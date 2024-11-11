#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
A multidimensional variable order markov chain generator.

@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import numpy as np 

class Markov:

    def __init__(self, size=100, max_order=2, name='noname'): # this method is called when the class is instantiated
        self.markov_stm = {}
        self.max_order = max_order # we use this to pad the index_container, so we later can use array views for higher order lookup
        self.empty_index_container = np.zeros(size+max_order)
        self.wraparound_index_container = np.copy(self.empty_index_container)
        self.wraparound_index_container[0+max_order] = 1 # to use for avoiding dead ends
        self.previous_item = None 
        self.name = name # just for debugging printing

    def analyze(self, item, index):
        if self.previous_item == None: # first item received is treated differently
            self.previous_item = item
            return
        else: # all next items are analyzed, stored as possible successors to the previous note
            print('Analyze:', self.name, self.previous_item, index, item)
            if self.previous_item not in self.markov_stm.keys():
                index_container = np.copy(self.empty_index_container)
                index_container[index+self.max_order] = 1
                self.markov_stm[self.previous_item] = index_container
            else:
                self.markov_stm[self.previous_item][index+self.max_order] = 1
            self.previous_item = item

    def next_items(self, previous=None):
        # as we are live recording items for analysis, dead ends are likely, and needs to be dealt with
        #print(self.name, previous)
        if previous and (previous not in self.markov_stm.keys()):
            print(f'Markov: {self.name} dead end at key {previous}, wrap around ')
            print(f'key: {previous}, allkeys: {self.markov_stm.keys()}')
            return self.wraparound_index_container
        if len(self.markov_stm.keys()) == 0:
            print('Empty Markov sequence')
            return [-1.0]
        # for the very first item, if we do not have any previous note, so let's choose one randomly
        if not previous:
            #print(f'{self.name}: Previous is None, returning zero probabilities')
            alternatives = self.empty_index_container
        else:
            alternatives = self.markov_stm[previous] # get an index container of possible next items
        return alternatives
    
    def clear(self):
        self.markov_stm = {}
        self.previous_item = None 
        
class MarkovHelper:
    def __init__(self, data, max_size=100, max_order=2):
        self.maxsize = max_size # allocate more space than we need, we will add more data later
        self.max_order = max_order
        self.parms = ['markov1', 'markov2', 'markov1_2D', 'markov2_2D', 'request'] # just to start somewhere
        self.current_numparms = len(self.parms)
        self.max_parms = len(self.parms)+5 # just to start somewhere
        self.weights = np.zeros(self.max_parms)
        self.temperature = 1 # 1 is default (no temperature influence)

        # instantiate analyzer classes
        self.m_1ord = Markov(size=self.maxsize, max_order=self.max_order, name='1ord')
        self.m_1ord_2D = Markov(size=self.maxsize, max_order=self.max_order, name='1ord_2D')
        self.markov_history = [None, None]
        self.no_markov_history = [None, None]

        # set data and allocate data containers
        self.data = data
        self.current_datasize = np.shape(self.data)[1]
        self.indices = np.arange(self.current_datasize)
        self.corpus = np.zeros(self.maxsize*self.max_parms)
        self.corpus = np.reshape(self.corpus, (self.maxsize,self.max_parms))
        # rewrite alternatives as views of corpus
        #self.flat_probabilities = np.ones(self.current_datasize)
        self.alternatives_markov_temp = np.zeros(self.maxsize+self.max_order)
        self.prob = np.zeros(self.maxsize)
                
    def analyze_vmo_vdim(self):
        # analyze item by item
        for i in range(self.current_datasize):
            self.m_1ord.analyze(self.data[0][i], i)
            self.m_1ord_2D.analyze(self.data[1][i], i)
        print('**** **** done analyzing **** ****')

    def set_weights(self, coefs, request_weight):
        # cumbersome hack for now
        order, dimension = coefs # the markov order and the number of dimensions to take into account
        if order == 0:
            self.weights[:3] = 0
        if order == 1:
            self.weights[0] = 1
        if order == 2:
            self.weights[:1] = 1
        if dimension == 2:
            self.weights[2:4] = 1
        self.weights[5] = request_weight

    def set_temperature(self, temperature):
        if temperature < 0.01 : temperature = 0.01
        self.temperature = 1/temperature

    def generate_vmo_vdim(self, m_query, coefs, temperature):
        next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D = m_query
        self.set_weights(coefs, request_weight)
        self.set_temperature(temperature)

        # need to update and keep track of previous events for higher orders
        self.markov_history[-1] = next_item_index
        if self.markov_history[-2]:
            i = self.markov_history[-2] # if we have recorded history
        else:
            i = next_item_index-1 # generate history from where we are
        next_item_2ord = self.data[0][i]
        next_item_2ord_2D = self.data[1][i]
            
        # get alternatives from Markov model
        self.alternatives_markov_temp = self.m_1ord.next_items(next_item_1ord)[2:self.current_datasize+2]
        self.corpus[:self.current_datasize, 0] = self.alternatives_markov_temp[:self.current_datasize]
        self.alternatives_markov_temp = self.m_1ord.next_items(next_item_2ord)[1:self.current_datasize+1]
        self.corpus[:self.current_datasize, 1] = self.alternatives_markov_temp[:self.current_datasize]
        self.alternatives_markov_temp = self.m_1ord_2D.next_items(next_item_1ord_2D)[2:self.current_datasize+2]
        self.corpus[:self.current_datasize, 2] = self.alternatives_markov_temp[:self.current_datasize]
        self.alternatives_markov_temp = self.m_1ord_2D.next_items(next_item_2ord_2D)[1:self.current_datasize+1]
        self.corpus[:self.current_datasize, 3] = self.alternatives_markov_temp[:self.current_datasize]
        # if we request a specific item, handle this here 
        if request_next_item:
            # in case we request a value that is not exactly equal to a key in the stm, we first find the closest match
            keys = np.asarray(list(self.m_1ord.markov_stm.keys()))
            request_next_item_closest = keys[np.abs(request_next_item-keys).argmin()]
            print(f'* * * * * * requested value {request_next_item_closest} with weight {request_weight}')
            request = self.m_1ord.next_items(request_next_item_closest)[3:self.current_datasize+3]
            self.corpus[:self.current_datasize, 4] = request
        
        # Scale by weights and sum: dot product corpus and weight. Then adjust temnperature
        self.prob = np.dot(self.corpus[:self.current_datasize, :self.current_numparms], self.weights[:self.current_numparms])
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
            print(f'Markov zero probability from query {m_query}, choose one at random')
            next_item_index = np.random.choice(self.indices)

        # update history
        next_item_1ord = self.data[0][next_item_index]
        next_item_1ord_2D = self.data[1][next_item_index]
        self.markov_history = self.markov_history[1:]+self.markov_history[:1] # roll the list one item back
        self.markov_history[-1] = next_item_index
        return [next_item_index, None, 0, next_item_1ord, next_item_1ord_2D]

# test
if __name__ == '__main__' :
    # example with 2D data
    data = np.array([[1,2,3,4,1,2,3,4,1,2,3,1,2,3,1,2,3,4,5,1],
                     ['A','A','A','A','A','A','A','A','B','B','B','B','B','B','B','B','B','B','B','B']])
    #data = np.array([[1,2,2,1,3,4,5],
    #                 [1,1,1,1,1,1,1]])
    datasize = np.shape(data[0])[0]
    max_order = 2
    #analyze variable markov order in 2 dimensions
    mh = MarkovHelper(data, max_size=100, max_order=max_order)
    mh.analyze_vmo_vdim()
    #generate
    order = 2
    dimensions = 2
    coefs = (order, dimensions)
    temperature = 0.2 # low (<1.0) is deternimistic, high (>1.0) is more random
    start_index = 1#np.random.choice(indices)
    next_item_1ord = data[0][start_index]
    # for debug only
    print('stm')
    if dimensions == 1:
        stm = mh.m_1ord.markov_stm
    else:
        stm = mh.m_1ord_2D.markov_stm
    for key, value in stm.items():
        print(key, value[2:datasize+max_order])
    # query
    print(f'The first item is {next_item_1ord} at index {start_index}')
    next_item_1ord_2D = None
    m_query = [start_index, None, 0, next_item_1ord, next_item_1ord_2D]
    i = 0
    while i < 10:
        #print(f'query {m_query}')
        m_query = mh.generate_vmo_vdim(m_query, coefs, temperature) #query markov models for next event and update query for next iteration
        next_item_index = m_query[0]
        print(f'the next item is  {data[0][next_item_index]} at index {next_item_index}')
        i += 1
    print(f'generated {i} items')

