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
            if self.previous_item not in self.stm.keys():
                index_container = np.copy(self.empty_index_container)
                index_container[index+self.max_order] = 1
                self.stm[self.previous_item] = index_container
            else:
                self.stm[self.previous_item][index+self.max_order] = 1
            self.previous_item = item

    def next_items(self, previous=None):
        # as we are live recording items for analysis, dead ends are likely, and needs to be dealt with
        if previous and (previous not in self.stm.keys()):
            print(f'Prob_encoder: {self.name} dead end at key {previous}, wrap around ')
            print(f'key: {previous}, allkeys: {self.stm.keys()}')
            return self.wraparound_index_container
        if len(self.stm.keys()) == 0:
            print('Empty Prob sequence')
            return [-1.0]
        # for the very first item, if we do not have any previous note, so let's choose one randomly
        if not previous:
            alternatives = self.empty_index_container
        else:
            alternatives = self.stm[previous] # get an index container of possible next items
        return alternatives
    
    def clear(self):
        self.stm = {}
        self.previous_item = None 
    
    def clear_phrase(self, indices):
        # clear last recorded phrase
        for key in self.stm.keys():
            for i in indices:
                self.stm[key][i+self.max_order] 
        self.previous_item == None

        
class Probabilistic_logic:
    # coordinate several queries (different orders, and different dimensions/parameters) to the Probabilistic encoder

    def __init__(self, corpus, pnum_corpus, prob_parms, max_size=100, max_order=2, max_voices=10):
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
        
        prob_history = []
        for i in range(self.max_order): prob_history.append(None)
        self.no_prob_history = prob_history.copy()
        self.prob_history = []
        for i in range(max_voices):
            self.prob_history.append(self.no_prob_history) #make separate history for each voice
        self.weights = np.zeros(self.numparms)
        # set default weights to first order for all parameters
        for pname in self.prob_parms.keys():
            self.set_weights_pname(pname, 1, printit=False)
        print(f'prob weights set to {self.weights}')

        # set data and allocate data containers
        self.current_datasize = 0
        self.corpus = corpus
        self.pnum_corpus = pnum_corpus
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]
        self.indx_container = np.zeros(self.maxsize*self.numparms)
        self.indx_container = np.reshape(self.indx_container, (self.maxsize,self.numparms))
        self.indices_prob_temp = np.zeros(self.maxsize+self.max_order)
        self.request_mask = np.zeros(self.maxsize+self.max_order)
        self.prob = np.zeros(self.maxsize)
        
    def analyze_single_event(self, i):
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            #print(f'pe.analyze: {pe.name}, {self.corpus[i, self.pnum_corpus[parm]]}')
            pe.analyze(self.corpus[i, self.pnum_corpus[parm]], i)
        self.current_datasize += 1
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]

    def set_weights(self, weights):
        self.weights = weights

    def set_weights_pname(self, pname, order, printit=True):
        # set weights according to parameter name and desired order
        if pname in self.prob_parms.keys():
            max_order = self.prob_parms[pname][0]
            if order <= max_order:
                for i in range(1, max_order+1):
                    w_index = self.prob_parms[pname][2][0] + i
                    w = np.clip(1+order-i, 0, 1)
                    self.weights[w_index] = w
                if printit:
                    print(f'prob weights set to {self.weights}')
            else: print(f'max order for {pname} exceeded: WARNING no change in weights applied')
        else: print(f'{pname} not in prob_parms: WARNING no change in weights applied')

    def set_temperature(self, temperature):
        if temperature < 0.001 : temperature = 0.001
        temperature_coef = 1/temperature
        return temperature_coef
       
    def update_history(self, history, new_item):
        history = history[1:]+history[:1] #rotate
        history[-1] = int(new_item) # add most recent INDEX last in list
        for i in range(len(history)-2): # not process the last (newest)
            if not history[i]:
                if history[i+1]:
                    history[i] = history[i+1]-1 # if there is a gap in the history, smooth out
        return history

    def generate(self, query, voice=1, temperature=0.2):
        next_item_index, request_next_item = query
        print('query', query)
        temperature_coef = self.set_temperature(temperature)
        
        # need to update and keep track of previous events for higher orders
        self.prob_history[voice-1] = self.update_history(self.prob_history[voice-1], next_item_index)

        # get alternatives from Probabilistic encoder
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            for ord in range(1,self.prob_parms[parm][0]+1): # will skip for specific request (order 0)
                w_index = self.prob_parms[parm][2][ord] #prob weight index
                if self.weights[w_index] != 0:
                    offset = self.max_order+1-ord
                    if not self.prob_history[voice-1][-ord]:
                        query_item = None
                    else:
                        query_item = self.corpus[self.prob_history[voice-1][-ord], self.pnum_corpus[parm]]
                    self.indices_prob_temp = pe.next_items(query_item)[offset:self.current_datasize+offset]
                    self.indx_container[:self.current_datasize, w_index] = self.indices_prob_temp[:self.current_datasize]

        # if we request a specific item, handle this here 
        if request_next_item[0]:
            self.get_request_mask(request_next_item)

        # Scale by weights and sum: dot product indx_container and weight. Then adjust temperature
        self.prob = np.dot(self.indx_container[:self.current_datasize, :self.numparms], self.weights)
        if np.amax(self.prob) > 0:
            self.prob /= np.amax(self.prob) # normalize
            self.prob = np.power(self.prob, temperature_coef) # temperature adjustment
            if request_next_item[0]:
                self.prob *= self.request_mask[:self.current_datasize]
            if np.amax(self.prob) == 0: # check to find if no values are available after masking
                self.prob = self.request_mask[:self.current_datasize] # just give us one of the unmasked values
            sumprob = np.sum(self.prob)
            self.prob = self.prob/sumprob #normalize sum to 1
            next_item_index = np.random.choice(self.indices,p=self.prob)
        else:
            print(f'Prob encoder zero probability from query {query}, choose one at random')
            print('indices', self.indices)
            next_item_index = np.random.choice(self.indices)
            print('selected', next_item_index)
        next_item_index = int(next_item_index)
        return next_item_index

    def get_request_mask(self, request_next_item):
        request_parm, request_code, request_weight = request_next_item
        request_type = request_code[0]
        self.request_mask[:self.current_datasize] = 0*self.request_mask[:self.current_datasize]
        if request_parm == 'index':
            keys = self.indices
        else:
            pe = self.prob_parms[request_parm][1]
            keys = np.asarray(list(pe.stm.keys()))
        if (request_type == '>') or (request_type == '<'):
            val = request_code[1]
            values = []
            print('val', val)
            if request_type == '>':
                for k in keys:
                    if k > val:
                        values.append(k)
            else:
                for k in keys:
                    print(k)
                    if k < val:
                        values.append(k)
        if request_type == 'values':
            values = request_code[1]
        for val in values:
            if request_parm == 'index':
                print(val, self.current_datasize)
                val = val%self.current_datasize # wrap index request to available range
                self.request_mask[int(val)] = 1
            else:
                # in case we request a value that is not exactly equal to a key in the stm, we first find the closest match
                request_next_item_closest = keys[np.abs(val-keys).argmin()]
                offset = self.max_order+1
                request = pe.next_items(request_next_item_closest)[offset:self.current_datasize+offset]
                self.request_mask[:self.current_datasize] += request[:self.current_datasize]
        self.request_mask[:self.current_datasize] *= request_weight
        self.request_mask[:self.current_datasize] += 1-request_weight
        if np.amax(self.request_mask[:self.current_datasize]) == 0: # if all masks are zero
            self.request_mask[:self.current_datasize] += 1 # disable masks
        return self.request_mask

    def clear_all(self):
        # clear all prob encoder's stm
        print('clear all prob encoder stm')
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            pe.clear()
        self.current_datasize = 0
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]
    
    def clear_phrase(self, indices):
        # clear last recorded phrase
        for parm in self.prob_parms.keys():
            pe = self.prob_parms[parm][1]
            pe.clear_phrase(indices)
        self.current_datasize -= len(indices)
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]
    
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

    max_events = 1010
    corpus = np.zeros((max_events,nparms_corpus), dtype=np.float32) # float32 faster than int or float64
    list_val1 = [1,2,2,1,3,4,5, 3,4,5,-1,-2] #np.random.randint(0,10,1000)#
    list_val2 = [1,1,1,1,1,1,1, 2,2,2,2,2] # np.random.randint(0,10,1000)#
    for i in range(len(list_val1)):
        corpus[i,pnum_corpus['val1']] = list_val1[i]
        corpus[i,pnum_corpus['val2']] = list_val2[i]

    pl = Probabilistic_logic(corpus, pnum_corpus, prob_parms, max_size=max_events, max_order=2, max_voices=2)
    for i in range(len(list_val1)):
        pl.corpus[i,pnum_corpus['index']] = i
        pl.analyze_single_event(i)
    print('done analyzing')
    
    #generate
    pl.set_weights_pname('val1', 1.5)
    temperature = 0.2 # low (<1.0) is deterministic, high (>1.0) is more random
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
    query = [start_index, [None, [0], 0]]
                          
    i = 0
    voice = 1
    while i < 10:
        next_item_index = pl.generate(query, voice, temperature) #query probabilistic encoders for next event and update query for next iteration
        query[0] = next_item_index
        print(f"the next item is  {corpus[next_item_index,pnum_corpus['val1']]} at index {next_item_index}, prob {pl.prob}")
        i += 1
    print(f'generated {i} items')
    
    # test voice 2, with request specific value
    print('** Voice2**')
    start_index = 1
    next_item = corpus[start_index,pnum_corpus['val1']]
    print(f'The first item is {next_item} at index {start_index}')
    request_item = 'index'
    request_type = 'values'
    request_value = 1
    request_weight = 0.5
    if request_item: 
        query = [start_index, [request_item, [request_type, [request_value]], request_weight]]
    else: 
        query = [start_index, [None, [0, [0]], 0]]
    i = 0
    voice = 2
    while i < 10:
        next_item_index = pl.generate(query, voice) #query probabilistic encoders for next event and update query for next iteration
        if request_item: 
            request_value = next_item_index+1
            query = [next_item_index, [request_item, [request_type, [request_value]], request_weight]] #request index, and use next_item_index as the value to ask for
        else: query = [next_item_index, [None, [0, [0]], 0]]
        print(f"the next item is  {corpus[next_item_index,pnum_corpus['val1']]} at index {next_item_index}, prob {pl.prob}")
        i += 1
    print(f'generated {i} items')

        
    print(pl.current_datasize)
    #request_next_item = ['index', 1, 0.5]
    #request_next_item = ['val1', ['values', [2.3]], 1] # list of one value
    request_next_item = ['val1', ['values' ,[1,3]], 1] # list of values
    #request_next_item = ['val1', ['>', [2]], 1] #mask high values, e.g. all x > zero
    mask = pl.get_request_mask(request_next_item)
    print('mask of values 1 and 3:\n', mask)

    # profiling tests
    #import cProfile
    #cProfile.run('pl.get_request_mask(request_next_item)')
    