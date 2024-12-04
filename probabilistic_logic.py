#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Probabilistic logic

Can be thought of as a "multidimensional variable order markov chain generator".

@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import numpy as np 
np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)
import json

class Probabilistic_encoder:
    # the basic core functionality of registering the order in which symbols appear

    def __init__(self, size=100, max_order=2, name='noname'): 
        self.stm = {} # state transition matrix in the form key:index_container, where the value contains an array of ones and zeros indicating presence
        self.size = size
        self.max_order = max_order # we use this to pad the index_container, so we later can use array views for higher order lookup
        self.empty_index_container = np.zeros(self.size+max_order, dtype=np.float32) 
        self.wraparound_index_container = np.copy(self.empty_index_container)
        self.wraparound_index_container[max_order] = 1 # to use for avoiding dead ends
        self.previous_item = None 
        self.name = name # just for debugging printing

    def analyze(self, item, index):
        if self.previous_item == None: # first item received is treated differently
            self.previous_item = item
            return
        else: # all next items are analyzed, stored as possible successors to the previous note
            print('Analyze:', self.name, self.previous_item, index, item)
            if self.previous_item not in self.stm.keys():
                index_container = np.copy(self.empty_index_container)
                index_container[index+self.max_order] = 1
                self.stm[self.previous_item] = index_container
            else:
                self.stm[self.previous_item][index+self.max_order] = 1
            self.previous_item = item

    def next_items(self, previous=None):
        # as we are live recording items for analysis, dead ends are likely, and needs to be dealt with
        #print(self.name, previous)
        if previous and (previous not in self.stm.keys()):
            print(f'Prob_encoder: {self.name} dead end at key {previous}, wrap around ')
            print(f'key: {previous}, allkeys: {self.stm.keys()}')
            return self.wraparound_index_container
        if len(self.stm.keys()) == 0:
            print('Empty Prob sequence')
            return [-1.0]
        # for the very first item, if we do not have any previous note, so let's choose one randomly
        if not previous:
            #print(f'{self.name}: Previous is None, returning zero probabilities')
            alternatives = self.empty_index_container
        else:
            alternatives = self.stm[previous] # get an index container of possible next items
        return alternatives
    
    def clear(self):
        self.stm = {}
        self.previous_item = None 
        
class Probabilistic_logic:
    # coordinate several queries (different orders, and different dimensions/parameters) to the Probabilistic encoder

    def __init__(self, corpus, pnum_corpus, prob_parms, d_size2=2, max_size=100, max_order=2, hack=1):
        self.maxsize = max_size # allocate more space than we need, we will add more data later
        self.max_order = max_order
        print('max order', self.max_order)
        
        # get number of parameters and instantiate analyzer classes
        self.prob_parms = prob_parms
        numparms = 0
        for parm in self.prob_parms.keys():
            numparms += (self.prob_parms[parm][0]+1) # 1 for each order, plus the "request value"
            pe = Probabilistic_encoder(size=self.maxsize, max_order=self.max_order, name=parm)
            self.prob_parms[parm][1] = pe
        self.numparms = numparms
        print('number of parameters in probabilistic logic:', self.numparms)
        
        self.prob_history = []
        for i in range(self.max_order): self.prob_history.append(None)
        self.no_prob_history = self.prob_history.copy()
        self.weights = np.zeros(self.numparms)
        self.temperature_coef = 1 # 1 is default (no temperature influence)

        # set data and allocate data containers
        self.current_datasize = 0
        self.corpus = corpus
        self.pnum_corpus = pnum_corpus
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]
        self.indx_container = np.zeros(self.maxsize*self.numparms)
        self.indx_container = np.reshape(self.indx_container, (self.maxsize,self.numparms))
        self.indices_prob_temp = np.zeros(self.maxsize+self.max_order)
        self.prob = np.zeros(self.maxsize)

    def analyze_single_event(self, i):
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            print(f'pe.analyze: {self.corpus[i, self.pnum_corpus[parm]]}')
            pe.analyze(self.corpus[i, self.pnum_corpus[parm]], i)
        self.current_datasize += 1
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]

    def set_weights(self, weights):
        self.weights = weights

    def set_weights_pname(self, pname, order):
        # set weights according to parameter name and desired order
        if pname in self.prob_parms.keys():
            max_order = self.prob_parms[pname][0]
            if order <= max_order:
                for i in range(1, max_order+1):
                    w_index = self.prob_parms[pname][2][0] + i
                    w = np.clip(1+order-i, 0, 1)
                    self.weights[w_index] = w
                print(f'prob weights set to {self.weights}')
            else: print(f'max order for {pname} exceeded: WARNING no change in weights applied')
        else: print(f'{pname} not in prob_parms: WARNING no change in weights applied')

    def set_temperature(self, temperature):
        if temperature < 0.001 : temperature = 0.001
        self.temperature_coef = 1/temperature
        print(f'PL temperature set to {temperature}')
       
    def update_history(self, history, new_item):
        history = history[1:]+history[:1] #rotate
        history[-1] = int(new_item) # add most recent INDEX last in list
        for i in range(len(history)-2): # not process the last (newest)
            if not history[i]:
                if history[i+1]:
                    history[i] = history[i+1]-1 # if there is a gap in the history, smooth out
        return history

    def generate(self, query):
        next_item_index, request_next_item = query
        
        # need to update and keep track of previous events for higher orders
        self.prob_history = self.update_history(self.prob_history, next_item_index)

        # get alternatives from Probabilistic encoder
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            for ord in range(1,self.prob_parms[parm][0]+1): # will skip for specific request (order 0)
                w_index = self.prob_parms[parm][2][ord] #prob weight index
                if self.weights[w_index] != 0:
                    offset = self.max_order+1-ord
                    if not self.prob_history[-ord]:
                        query_item = None
                    else:
                        query_item = self.corpus[self.prob_history[-ord], self.pnum_corpus[parm]]
                    #print(f'query item {query_item}, history {self.prob_history}, -ord {-ord}, pnum {self.pnum_corpus[parm]}')
                    self.indices_prob_temp = pe.next_items(query_item)[offset:self.current_datasize+offset]
                    self.indx_container[:self.current_datasize, w_index] = self.indices_prob_temp[:self.current_datasize]
                #else: print(f'skipping {parm} order {ord}')

        # if we request a specific item, handle this here 
        if request_next_item[0]:
            parm, value, weight = request_next_item
            w_index = self.prob_parms[parm][2][0] #prob weight index for "zero" order (value request)
            self.weights[w_index] = weight # might want to reset this to previous value?
            pe = self.prob_parms[parm][1]
            # in case we request a value that is not exactly equal to a key in the stm, we first find the closest match
            keys = np.asarray(list(pe.stm.keys()))
            request_next_item_closest = keys[np.abs(value-keys).argmin()]
            offset = self.max_order+1
            request = pe.next_items(request_next_item_closest)[offset:self.current_datasize+offset]
            #print(f'* * * * * * requested value {request_next_item_closest} with weight {self.weights[w_index]}')
            self.indx_container[:self.current_datasize, w_index] = request
        
        # Scale by weights and sum: dot product indx_container and weight. Then adjust temperature
        self.prob = np.dot(self.indx_container[:self.current_datasize, :self.numparms], self.weights)
        if np.amax(self.prob) > 0:
            self.prob /= np.amax(self.prob) # normalize
            self.prob = np.power(self.prob, self.temperature_coef) # temperature adjustment
            sumprob = np.sum(self.prob)
            self.prob = self.prob/sumprob #normalize sum to 1
            next_item_index = np.random.choice(self.indices,p=self.prob)
        else:
            print(f'Prob encoder zero probability from query {query}, choose one at random')
            next_item_index = np.random.choice(self.indices)
        next_item_index = int(next_item_index)
        return [next_item_index, [None,0]]

    def clear_all(self):
        # clear all prob encoder's stm
        print('clear all prob encoder stm')
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            pe.clear()
    
    def save_all(self):
        # save all prob encoders to file
        print('attempt prob encoder save to file')
        print('NOT IMPLEMENTED, need to convert stm keys to float')
        return
        data = []
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            data.append(pe.stm)
        with open("prob_encoders.json", "w") as fp:
            json.dump(data, fp)  
        
    def read_all(self):
        # read all prob encoders from file
        print('attempt prob encoder read from file')
        with open("prob_encoders.json", "r") as fp:
            data = json.load(fp)  
        i = 0
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            pe.stm = data[i]
            i += 1

# test
if __name__ == '__main__' :
    # example with 2D data
    pnum_corpus = {
        'index': 0, # register indices for data points currently in use
        'val1' : 1, 
        'val2': 2}
    # corpus is the main data container for events
    nparms_corpus = len(pnum_corpus.keys())
    # parameter names and max_order in the probabilistic logic module
    # zero order just means give us all indices where the value occurs
    # higher orders similar to markov order
    # the second item in the values is the analyzer instance for that parameter
    # the third is a list of indices used for probability calculation, corresponds to weight indices
    prob_parms = {'val1': [2, None, [0,1,2]],
                 'val2': [2, None, [3,4,5]]}

    max_events = 20
    corpus = np.zeros((max_events,nparms_corpus), dtype=np.float32) # float32 faster than int or float64
    list_val1 = [1,2,2,1,3,4,5, 3,4,5,1,2]
    list_val2 = [1,1,1,1,1,1,1, 2,2,2,2,2]
    for i in range(len(list_val1)):
        corpus[i,pnum_corpus['val1']] = list_val1[i]
        corpus[i,pnum_corpus['val2']] = list_val2[i]

    pl = Probabilistic_logic(corpus, pnum_corpus, prob_parms, d_size2=nparms_corpus, max_size=max_events, max_order=2, hack=1)
    for i in range(len(list_val1)):
        pl.corpus[i,pnum_corpus['index']] = i
        pl.analyze_single_event(i)
    print('done analyzing')
    
    #generate
    pl.set_weights_pname('val1', 1.5)
    pl.set_temperature(0.2) # low (<1.0) is deterministic, high (>1.0) is more random
    start_index = 0#np.random.choice(indices)
    next_item = corpus[start_index,pnum_corpus['val1']]
    # for debug only
    for parm in prob_parms.keys():
        pe = prob_parms[parm][1]
        # FIX HERE
        print(f'stm for {parm}')
        for key, value in pe.stm.items():
            print(key, value[2:pl.current_datasize+pl.max_order])
    
    # query
    print(f'The first item is {next_item} at index {start_index}')
    request_value = None
    if request_value: query = [start_index, ['val1', request_value, 1]]
    else: query = [start_index, [None, 0, 0]]

    i = 0
    while i < 10:
        query = pl.generate(query) #query probabilistic encoders for next event and update query for next iteration
        next_item_index = query[0]
        if request_value: query[1] = ['val1', request_value, 1]
        print(f"the next item is  {corpus[next_item_index,pnum_corpus['val1']]} at index {next_item_index}, prob {pl.prob}")
        i += 1
    print(f'generated {i} items')
