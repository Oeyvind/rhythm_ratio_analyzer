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
        self.markov_history = [None, None]
        self.no_markov_history = [None, None]
        # instantiate analyzer classes
        self.m_1ord = Markov(size=self.maxsize, max_order=self.max_order, name='1ord')
        self.m_1ord_2D = Markov(size=self.maxsize, max_order=self.max_order, name='1ord_2D')
        # set data and allocate data containers
        self.data = data
        self.current_datasize = np.shape(self.data)[1]
        self.indices = np.arange(self.current_datasize)
        self.alternatives_all = np.ones(self.current_datasize)
        self.alternatives_1ord = np.zeros(self.maxsize+self.max_order)
        self.alternatives_1ord_2D = np.zeros(self.maxsize+self.max_order)
        self.alternatives_2ord = np.zeros(self.maxsize+self.max_order)
        self.alternatives_2ord_2D = np.zeros(self.maxsize+self.max_order)
        self.request = np.zeros(self.maxsize+self.max_order)
        self.prob = np.zeros(self.maxsize+self.max_order)
        
    def analyze_vmo_vdim(self):
        # analyze item by item
        for i in range(self.current_datasize):
            self.m_1ord.analyze(self.data[0][i], i)
            self.m_1ord_2D.analyze((self.data[0][i],self.data[1][i]), i)
        print('**** **** done analyzing **** ****')

    def generate_vmo_vdim(self, m_query, coefs):
        next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D = m_query
        order, dimension = coefs # the markov order and the number of dimensions to take into account
        
        # need to update and keep track of previous events for higher orders
        self.markov_history[-1] = next_item_index
        if self.markov_history[-2]:
            i = self.markov_history[-2] # if we have recorded history
        else:
            i = next_item_index-1 # generate history from where we are
        print(f'*** *** ***  {self.markov_history}, {m_query}, index: {i}')
        next_item_2ord = self.data[0][i]
        next_item_2ord_2D = (self.data[0][i],self.data[1][i])
            
        # get alternatives from Markov model
        self.alternatives_1ord = self.m_1ord.next_items(next_item_1ord)[2:self.current_datasize+2]
        self.alternatives_1ord_2D = self.m_1ord_2D.next_items(next_item_1ord_2D)[2:self.current_datasize+2]
        self.alternatives_2ord = self.m_1ord.next_items(next_item_2ord)[1:self.current_datasize+1]
        self.alternatives_2ord_2D = self.m_1ord_2D.next_items(next_item_2ord_2D)[1:self.current_datasize+1]

        # Collate probabilities from the different ways to query out models
        # ...simplified for now, the fractional orders are sketchy but might just work for the purpose of musical sequence generation
        # remember that the alternatives for 2nd order only take into account transitions from the next to last event, so
        # they have to be multiplied with the 1st order alternatives to get a correct 2nd order markov chain
        # If the second order markov give zero probabilities, we fall back to first order,
        # We might add other fallback strategies, for example "second order with unknown" (our current 2nd order lookup result on its own)
        if order == 0:
            prob = np.copy(self.alternatives_all) # good
        
        elif (0 < order <= 1) and (dimension == 1):
            ones = np.copy(self.alternatives_all)
            prob = (self.alternatives_1ord*order)+(ones*(1-order)) # good
        elif (0 < order <= 1) and (dimension == 2):
            ones = np.copy(self.alternatives_all)
            prob = (self.alternatives_1ord*order)+(self.alternatives_1ord_2D*order)+(ones*(1-order)) #sketchy probabilities

        elif (order == 1.5) and (dimension == 1): 
            prob = self.alternatives_1ord+self.alternatives_2ord # sketchy probabilities
        elif (order == 1.5) and (dimension == 2): 
            prob = self.alternatives_1ord+self.alternatives_2ord+self.alternatives_1ord_2D+self.alternatives_2ord_2D # sketchy probabilities

        elif (order == 2) and (dimension == 1):
            prob = self.alternatives_1ord*self.alternatives_2ord # good, if 2nd order is possible
            if np.sum(prob) == 0:
                print(f'Fallback for order {order}, dimension {dimension}')
                #print(f'history {[self.data[0][i] for i in self.markov_history]}')
                #print(f'alternatives \n {self.alternatives_1ord} \n {self.alternatives_2ord}')
                prob = self.alternatives_1ord # fallback
                self.markov_history = self.no_markov_history.copy() # and erase history
        elif (order == 2) and (dimension == 2):
            prob = self.alternatives_1ord_2D*self.alternatives_2ord_2D # good, if 2nd order is possible
            if np.sum(prob) == 0:
                print(f'Fallback for order {order}, dimension {dimension}')
                #print(f'history {[(self.data[0][i],self.data[1][i]) for i in self.markov_history]}')
                #print(f'alternatives \n {self.alternatives_1ord_2D} \n {self.alternatives_2ord_2D}')
                prob = self.alternatives_1ord_2D # fallback
                self.markov_history = self.no_markov_history.copy() # and erase history
                if np.sum(self.prob) == 0:
                    print(f'Last resort fallback for order {order}, dimension {dimension}')
                    prob = self.alternatives_1ord # fallback

        # if we request a specific item, handle this here 
        if request_next_item:
            # in case we request a value that is not exactly equal to a key in the stm, we first find the closest match
            keys = np.asarray(list(self.m_1ord.markov_stm.keys()))
            #print(request_next_item, keys)
            request_next_item_closest = keys[np.abs(request_next_item-keys).argmin()]
            print(f'* * * * * * requested value {request_next_item_closest} with weight {request_weight}')
            request = self.m_1ord.next_items(request_next_item_closest)[3:self.current_datasize+3]
            print(f'r {request} type {type(request)}')
            request *= request_weight
            prob *= (1-request_weight)
            print(f'r {request}')
            print(f'p {prob}')
            prob += request
            print(f'p {prob}')

        # normalize probabilities, and choose next from probability distribution
        sumprob = np.sum(prob)
        if sumprob > 0:
            prob = prob/sumprob
            next_item_index = np.random.choice(self.indices,p=prob)
        else:
            print(f'Markov zero probability from query {m_query}, choose one at random')
            next_item_index = np.random.choice(self.indices)

        next_item_1ord = self.data[0][next_item_index]
        next_item_1ord_2D = (self.data[0][next_item_index],self.data[1][next_item_index])

        self.markov_history = self.markov_history[1:]+self.markov_history[:1] # roll the list one item back
        self.markov_history[-1] = next_item_index
        return [next_item_index, None, 0, next_item_1ord, next_item_1ord_2D]

# test
if __name__ == '__main__' :
    # example with 2D data
    #data = np.array([[1,2,3,4,1,2,3,4,1,2,3,1,2,3,1,2,3,4,5,1],
    #                 ['A','A','A','A','A','A','A','A','B','B','B','B','B','B','B','B','B','B','B','B']])
    data = np.array([[1,2,2,1,3,4,5],
                     [1,1,1,1,1,1,1]])
    datasize = np.shape(data[0])[0]
    max_order = 2
    #analyze variable markov order in 2 dimensions
    mh = MarkovHelper(data, max_size=100, max_order=max_order)
    mh.analyze_vmo_vdim()
    #generate
    order = 2
    dimensions = 1
    coefs = (order, dimensions)
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
        m_query = mh.generate_vmo_vdim(m_query, coefs) #query markov models for next event and update query for next iteration
        next_item_index = m_query[0]
        print(f'the next item is  {data[0][next_item_index]} at index {next_item_index}')
        i += 1
    print(f'generated {i} items')
    m_query[0] = int(2) # index
    m_query[1] = 3.01 # request
    m_query[2] = 1 # request weight
    m_query = mh.generate_vmo_vdim(m_query, coefs) #query markov models for next event and update query for next iteration
    next_item_index = m_query[0]
    print(f'the next item is  {data[0][next_item_index]} at index {next_item_index}')
'''    i = 0
    while i < 3:
        m_query = mh.generate_vmo_vdim(m_query, coefs) #query markov models for next event and update query for next iteration
        next_item_index = m_query[0]
        print(f'the next item is  {data[0][next_item_index]} at index {next_item_index}')
        i += 1
    print(f'generated {i} items')

'''