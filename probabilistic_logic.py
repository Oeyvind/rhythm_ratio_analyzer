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

class Probabilistic_encoder:
    # the basic core functionality of registering the order in which symbols appear

    def __init__(self, size=100, max_order=2, name='noname'): 
        self.stm = {} # state transition matrix in the form key:index_container, where the value contains an array of ones and zeros indicating presence
        self.max_order = max_order # we use this to pad the index_container, so we later can use array views for higher order lookup
        self.empty_index_container = np.zeros(size+max_order, dtype=np.float32) 
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

    def __init__(self, corpus, pnum_corpus, pnum_prob, d_size2=2, max_size=100, max_order=2, hack=1):
        self.maxsize = max_size # allocate more space than we need, we will add more data later
        self.max_order = max_order
        print('max order', self.max_order)
        self.pnum_prob = pnum_prob # dict of (parameter name : index) of dimensions in the prob logic
        self.numparms = len(self.pnum_prob.keys())
        self.weights = np.zeros(self.numparms)
        self.temperature = 1 # 1 is default (no temperature influence)

        # set data and allocate data containers
        self.current_datasize = 0
        self.corpus = corpus
        self.pnum_corpus = pnum_corpus
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]
        self.indx_container = np.zeros(self.maxsize*self.numparms)
        self.indx_container = np.reshape(self.indx_container, (self.maxsize,self.numparms))
        self.indices_prob_temp = np.zeros(self.maxsize+self.max_order)
        self.prob = np.zeros(self.maxsize)

        '''
        pnum_prob = {
          'ratio_best': 0, # 'zeroeth order' just means give us all indices where the value occurs
          'ratio_best_1order': 1, # first order markovian lookup
          'ratio_best_2order': 2,
          'ratio_2nd_best': 5,
          'ratio_2nd_best_1order': 6,
          'ratio_2nd_best_2order': 7,
          'phrase_num': 10} # the rest is placeholders, to be implemented
        '''

        # instantiate analyzer classes
        self.m_1ord = Probabilistic_encoder(size=self.maxsize, max_order=self.max_order, name='1ord')
        self.m_1ord_2D = Probabilistic_encoder(size=self.maxsize, max_order=self.max_order, name='1ord_2D')
        self.prob_history = [None, None]
        self.no_prob_history = [None, None]

        # ugly, temporary
        if hack == 1:
            self.hacknames = ['index', 'val1', 'val2']
        else:
            self.hacknames = ['index', 'ratio_best', 'ratio_2nd_best']


    
    def analyze_single_event(self, i):
        self.m_1ord.analyze(self.corpus[i, self.pnum_corpus[self.hacknames[1]]], i)
        self.m_1ord_2D.analyze(self.corpus[i, self.pnum_corpus[self.hacknames[2]]], i)
        self.current_datasize += 1
        self.indices = self.corpus[:self.current_datasize, self.pnum_corpus['index']]

    def set_weights(self, weights):
        self.weights = weights

    def set_temperature(self, temperature):
        if temperature < 0.01 : temperature = 0.01
        self.temperature = 1/temperature

    def generate(self, query, weights, temperature):
        next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D = query
        self.set_weights(weights)
        self.set_temperature(temperature)

        # need to update and keep track of previous events for higher orders
        self.prob_history[-1] = next_item_index
        if self.prob_history[-2]:
            i = self.prob_history[-2] # if we have recorded history
        else:
            i = next_item_index-1 # generate history from where we are
        next_item_2ord = self.corpus[i, self.pnum_corpus[self.hacknames[1]]]
        next_item_2ord_2D = self.corpus[i, self.pnum_corpus[self.hacknames[2]]]

        # get alternatives from Probabilistic encoder
        #print('q:', next_item_1ord, next_item_1ord_2D,next_item_2ord,next_item_2ord_2D)
        self.indices_prob_temp = self.m_1ord.next_items(next_item_1ord)[2:self.current_datasize+2]
        self.indx_container[:self.current_datasize, 0] = self.indices_prob_temp[:self.current_datasize]
        self.indices_prob_temp = self.m_1ord.next_items(next_item_2ord)[1:self.current_datasize+1]
        self.indx_container[:self.current_datasize, 1] = self.indices_prob_temp[:self.current_datasize]
        self.indices_prob_temp = self.m_1ord_2D.next_items(next_item_1ord_2D)[2:self.current_datasize+2]
        self.indx_container[:self.current_datasize, 2] = self.indices_prob_temp[:self.current_datasize]
        self.indices_prob_temp = self.m_1ord_2D.next_items(next_item_2ord_2D)[1:self.current_datasize+1]
        self.indx_container[:self.current_datasize, 3] = self.indices_prob_temp[:self.current_datasize]
        # if we request a specific item, handle this here 
        if request_next_item:
            # in case we request a value that is not exactly equal to a key in the stm, we first find the closest match
            keys = np.asarray(list(self.m_1ord.stm.keys()))
            request_next_item_closest = keys[np.abs(request_next_item-keys).argmin()]
            print(f'* * * * * * requested value {request_next_item_closest} with weight {request_weight}')
            request = self.m_1ord.next_items(request_next_item_closest)[3:self.current_datasize+3]
            self.indx_container[:self.current_datasize, 4] = request
        
        # Scale by weights and sum: dot product indx_container and weight. Then adjust temperature
        #print(f'prob \n {self.indx_container[:self.current_datasize, :self.numparms]}')
        self.prob = np.dot(self.indx_container[:self.current_datasize, :self.numparms], self.weights)
        if np.amax(self.prob) > 0:
            self.prob /= np.amax(self.prob) # normalize
            self.prob = np.power(self.prob, self.temperature) # temperature adjustment
            sumprob = np.sum(self.prob)
        else:
            sumprob = 0
        if sumprob > 0:
            self.prob = self.prob/sumprob #normalize sum to 1
            next_item_index = np.random.choice(self.indices,p=self.prob)
        else:
            print(f'Prob encoder zero probability from query {query}, choose one at random')
            next_item_index = np.random.choice(self.indices)
        next_item_index = int(next_item_index)

        # update history
        next_item_1ord = self.corpus[next_item_index, self.pnum_corpus[self.hacknames[1]]]
        next_item_1ord_2D = self.corpus[next_item_index, self.pnum_corpus[self.hacknames[2]]]
        self.prob_history = self.prob_history[1:] + self.prob_history[:1] # roll the list one item back
        self.prob_history[-1] = next_item_index
        return [next_item_index, None, 0, next_item_1ord, next_item_1ord_2D]

# test
if __name__ == '__main__' :
    # example with 2D data
    pnum_corpus = {
        'index': 0, # register indices for data points currently in use
        'val1' : 1, 
        'val2': 2}
    # corpus is the main data container for events
    nparms_corpus = len(pnum_corpus.keys())
    pnum_prob = {'val1_1order': 0, 
                 'val1_2order': 1, 
                 'val2_1order': 2, 
                 'val2_2order': 3}

    max_events = 20
    corpus = np.zeros((max_events,nparms_corpus), dtype=np.float32) # float32 faster than int or float64
    list_val1 = [1,2,2,1,3,4,5, 3,4,5,1,2]
    list_val2 = [1,1,1,1,1,1,1, 2,2,2,2,2]
    for i in range(len(list_val1)):
        corpus[i,pnum_corpus['val1']] = list_val1[i]
        corpus[i,pnum_corpus['val2']] = list_val2[i]

    pl = Probabilistic_logic(corpus, pnum_corpus, pnum_prob, d_size2=nparms_corpus, max_size=max_events, max_order=2, hack=1)
    for i in range(len(list_val1)):
        pl.corpus[i,pnum_corpus['index']] = i
        pl.analyze_single_event(i)
    print('done analyzing')
    
    #generate
    weights = [1,1,1,0.5] #1ord, 2ord, 1ord2D, 2ord2D
    temperature = 0.2 # low (<1.0) is deternimistic, high (>1.0) is more random
    start_index = 0#np.random.choice(indices)
    next_item_1ord = corpus[start_index,pnum_corpus[pl.hacknames[1]]]
    # for debug only
    print('stm 1ord')
    for key, value in pl.m_1ord.stm.items():
        print(key, value[2:pl.current_datasize+pl.max_order])
    print('stm 2ord')
    for key, value in pl.m_1ord_2D.stm.items():
        print(key, value[2:pl.current_datasize+pl.max_order])
    
    # query
    print(f'The first item is {next_item_1ord} at index {start_index}')
    next_item_1ord_2D = None
    query = [start_index, None, 0, next_item_1ord, next_item_1ord_2D]
    i = 0
    while i < 10:
        query = pl.generate(query, weights, temperature) #query probabilistic encoders for next event and update query for next iteration
        next_item_index = query[0]
        print(f"the next item is  {corpus[next_item_index,pnum_corpus[pl.hacknames[1]]]} at index {next_item_index}, prob {pl.prob}")
        i += 1
    print(f'generated {i} items')
