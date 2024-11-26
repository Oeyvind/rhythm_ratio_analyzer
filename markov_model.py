#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
A multidimensional variable order markov chain generator.

@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import numpy as np 
np.set_printoptions(precision=2)

class Markov:
    # the basic core functionality of registering the order of which symbols appear

    def __init__(self, size=100, max_order=2, name='noname'): 
        self.markov_stm = {}
        self.max_order = max_order # we use this to pad the index_container, so we later can use array views for higher order lookup
        self.empty_index_container = np.zeros(size+max_order, dtype=np.float32) # float32 faster than int or float64
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
    # coordinate several queries (different orders, and different dimensions/parameters) to the Markov model

    def __init__(self, data=None, d_size2=2, max_size=100, max_order=2):
        self.maxsize = max_size # allocate more space than we need, we will add more data later
        self.max_order = max_order
        print('max order', self.max_order)
        # need to think about how to organize parameters, and variable order per parameter
        # what is called markov now should be called "ratio" and "ratio_alt", add data for velocity and downbeat
        #self.parms = ['markov1', 'markov2', 'markov1_2D', 'markov2_2D', 'request'] # just to start somewhere
        #self.parms = parms
        self.parms = ['markov1', 'markov2', 'markov1_2D', 'markov2_2D', 'request'] # just to start somewhere
        self.numparms = len(self.parms)
        self.weights = np.zeros(self.numparms)
        self.temperature = 1 # 1 is default (no temperature influence)

        # instantiate analyzer classes
        self.m_1ord = Markov(size=self.maxsize, max_order=self.max_order, name='1ord')
        self.m_1ord_2D = Markov(size=self.maxsize, max_order=self.max_order, name='1ord_2D')
        self.markov_history = [None, None]
        self.no_markov_history = [None, None]

        # set data and allocate data containers
        if type(data) == np.ndarray:
            self.data = data
            self.d_size2 = np.shape(data)[0]
        else:
            self.d_size2 = d_size2
            self.data = np.zeros(self.maxsize*self.d_size2)
            self.data = np.reshape(self.data, (self.d_size2, self.maxsize))
        
        self.current_datasize = 0
        self.indices = []
        self.indx_container = np.zeros(self.maxsize*self.numparms)
        self.indx_container = np.reshape(self.indx_container, (self.maxsize,self.numparms))
        # rewrite alternatives as views of indx_container
        #self.flat_probabilities = np.ones(self.current_datasize)
        self.alternatives_markov_temp = np.zeros(self.maxsize+self.max_order)
        self.prob = np.zeros(self.maxsize)
                
    def analyze_vmo_vdim(self):
        # analyze all data item by item
        for i in range(self.current_datasize):
            self.m_1ord.analyze(self.data[0][i], i)
            self.m_1ord_2D.analyze(self.data[1][i], i)
            self.indices.append(i)
        print('**** **** done analyzing **** ****')

    def add_and_analyze(self, item, i=None):
        # if we do not give an index, we build on after the last current item and increment the datasize counter
        # item must have the same size as self.numparms
        if not i:
            i = self.current_datasize
            self.indices.append(i)
            self.current_datasize += 1
        self.data[:,i] = item
        self.m_1ord.analyze(self.data[0][i], i)
        self.m_1ord_2D.analyze(self.data[1][i], i)

        #print(data[:,i])
        #mh.add_and_analyze(data[:,i])

    def set_data(self, data):
        self.data = data
        self.current_datasize = np.shape(data)[1]

    def set_weights(self, weights):
        self.weights = weights

    def set_temperature(self, temperature):
        if temperature < 0.01 : temperature = 0.01
        self.temperature = 1/temperature

    def generate_vmo_vdim(self, m_query, weights, temperature):
        next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D = m_query
        self.set_weights(weights)
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
        #print('q:', next_item_1ord, next_item_1ord_2D,next_item_2ord,next_item_2ord_2D)
        self.alternatives_markov_temp = self.m_1ord.next_items(next_item_1ord)[2:self.current_datasize+2]
        self.indx_container[:self.current_datasize, 0] = self.alternatives_markov_temp[:self.current_datasize]
        self.alternatives_markov_temp = self.m_1ord.next_items(next_item_2ord)[1:self.current_datasize+1]
        self.indx_container[:self.current_datasize, 1] = self.alternatives_markov_temp[:self.current_datasize]
        self.alternatives_markov_temp = self.m_1ord_2D.next_items(next_item_1ord_2D)[2:self.current_datasize+2]
        self.indx_container[:self.current_datasize, 2] = self.alternatives_markov_temp[:self.current_datasize]
        self.alternatives_markov_temp = self.m_1ord_2D.next_items(next_item_2ord_2D)[1:self.current_datasize+1]
        self.indx_container[:self.current_datasize, 3] = self.alternatives_markov_temp[:self.current_datasize]
        # if we request a specific item, handle this here 
        if request_next_item:
            # in case we request a value that is not exactly equal to a key in the stm, we first find the closest match
            keys = np.asarray(list(self.m_1ord.markov_stm.keys()))
            request_next_item_closest = keys[np.abs(request_next_item-keys).argmin()]
            print(f'* * * * * * requested value {request_next_item_closest} with weight {request_weight}')
            request = self.m_1ord.next_items(request_next_item_closest)[3:self.current_datasize+3]
            self.indx_container[:self.current_datasize, 4] = request
        
        # Scale by weights and sum: dot product indx_container and weight. Then adjust temnperature
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
            print('prob', self.prob, self.indices)
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

class MarkovManager:
    # manage Markov process registration and analysis

    def __init__(self, mh):
        
        self.mh = mh  
        self.mm_query = [0, None, 0, None, None] # initial markov query. 
        # query format: [next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D]      

    def add_data_chunk(self, newdata, best, next_best):
        datasize = len(newdata[0])
        dimensions = 2 # set max dimensions here for now
        data = np.empty((dimensions,datasize),dtype='float')
        for i in range(datasize):
            ratio_float1 = newdata[best][i][0]/newdata[best][i][1]
            ratio_float2 = newdata[next_best][i][0]/newdata[next_best][i][1]
            data[0,i] = ratio_float1
            data[1,i] = ratio_float2
        
        #analyze variable markov order in 2 dimensions
        #mh = mm.MarkovHelper(data=None, d_size2=2, max_size=100, max_order=mm_max_order)
        self.mh.set_data(data)
        self.mh.analyze_vmo_vdim()

# test
if __name__ == '__main__' :
    # example with 2D data
    #data = np.array([[1,2,3,4,1,2,3,4,1,2,3,1,2,3,1,2,3,4,5,1],
    #                 ['A','A','A','A','A','A','A','A','B','B','B','B','B','B','B','B','B','B','B','B']])
    data = np.array([[1,2,2,1,3,4,5, 3,4,5,1,2],
                     [1,1,1,1,1,1,1, 2,2,2,2,2]], dtype='float')
    datasize = np.shape(data)[1]
    d_size2 = np.shape(data)[0]
    max_order = 2
    #analyze variable markov order in 2 dimensions
    nodata = None
    mh = MarkovHelper(nodata, d_size2=d_size2, max_size=datasize, max_order=max_order)
    analyze_all = True
    if analyze_all:
        mh.set_data(data)
        print('data\n', mh.data)
        mh.analyze_vmo_vdim()
    else:
        for i in range(np.shape(data)[1]):
            mh.add_and_analyze(data[:,i])
        print('data\n', mh.data)
    print('done analyzing')
    
    #generate
    order = 2
    dimensions = 2
    #coefs = (order, dimensions)
    weights = [1,1,1,1,0] #1ord, 2ord, 1ord2D, 2ord2D, request
    '''
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
    '''
    temperature = 0.2 # low (<1.0) is deternimistic, high (>1.0) is more random
    start_index = 0#np.random.choice(indices)
    next_item_1ord = data[start_index][0]
    # for debug only
    print('stm 1ord')
    for key, value in mh.m_1ord.markov_stm.items():
        print(key, value[2:datasize+max_order])
    print('stm 2ord')
    for key, value in mh.m_1ord_2D.markov_stm.items():
        print(key, value[2:datasize+max_order])
    
    # query
    print(f'The first item is {next_item_1ord} at index {start_index}')
    next_item_1ord_2D = None
    m_query = [start_index, None, 0, next_item_1ord, next_item_1ord_2D]
    i = 0
    while i < 10:
        #print(f'query {m_query}')
        m_query = mh.generate_vmo_vdim(m_query, weights, temperature) #query markov models for next event and update query for next iteration
        next_item_index = m_query[0]
        print(f'        the next item is  {data[0][next_item_index]} at index {next_item_index}')
        i += 1
    print(f'generated {i} items')
