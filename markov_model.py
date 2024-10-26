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

    def __init__(self, size=100, name='noname'): # this method is called when the class is instantiated
        self.markov_stm = {}
        self.empty_index_container = np.zeros(size)
        self.previous_item = None 
        self.name = name # just for debugging printing

    def analyze(self, item, index):
        if self.previous_item == None: # first item received is treated differently
            self.previous_item = item
            return
        else: # all next items are analyzed, stored as possible successors to the previous note
            print('Analyze:', self.name, self.previous_item, index, item)
            if self.previous_item not in self.markov_stm.keys():
                index_container = self.empty_index_container.copy()
                index_container[index] = 1
                self.markov_stm[self.previous_item] = index_container
            else:
                self.markov_stm[self.previous_item][index] = 1
            self.previous_item = item

    def next_items(self, previous=None):
        # as we are live recording items for analysis, dead ends are likely, and needs to be dealt with
        if previous and (previous not in self.markov_stm.keys()):
            print(f'Markov: {self.name} dead end, returning zero probabilities')
            return self.empty_index_container
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
        
def analyze_vmo_vdim(data, datasize):
    #analyze
    m_1ord = Markov(size=datasize, name='1ord')
    m_1ord_2D = Markov(size=datasize, name='1ord_2D')
    m_2ord = Markov(size=datasize, name='2ord')
    m_2ord_2D = Markov(size=datasize, name='2ord_2D')
    for i in range(np.shape(data)[1]):
        m_1ord.analyze(data[0][i], i)
        m_1ord_2D.analyze((data[0][i],data[1][i]), i)
        if i > 0:
            m_2ord.analyze((data[0][i-1],data[0][i]), i)
            m_2ord_2D.analyze(((data[0][i-1],data[1][i-1]),(data[0][i],data[1][i])), i)
    print('**** **** done analyzing **** ****')
    return m_1ord, m_1ord_2D, m_2ord, m_2ord_2D

def generate_vmo_vdim(models, m_query, coefs, indices, data):
    m_1ord, m_1ord_2D, m_2ord, m_2ord_2D = models
    next_item_index, next_item_1ord, next_item_1ord_2D, next_item_2ord, next_item_2ord_2D = m_query
    order, dimension = coefs # the markov order and the number of dimensions to take into account
    alternatives_1ord = m_1ord.next_items(next_item_1ord)
    alternatives_1ord_2D = m_1ord_2D.next_items(next_item_1ord_2D)
    alternatives_2ord = m_2ord.next_items(next_item_2ord)
    alternatives_2ord_2D = m_2ord_2D.next_items(next_item_2ord_2D)
    # simplified for now, the fractional orders are sketchy but might just work for the purpose of musical sequence generation
    # remember that the alternatives for 2nd order only take into account transitions from the next to last event, so
    # they have to be multiplied with the 1st order alternatives to get a correct 2nd order markov chain
    # If the second order markov give zero probabilities, we fall bavck to first order
    if order == 0:
        prob = np.ones(len(alternatives_1ord)) # good
    
    elif (0 < order <= 1) and (dimension == 1):
        ones = np.ones(len(alternatives_1ord))
        prob = (alternatives_1ord*order)+(ones*(1-order)) # good
    elif (0 < order <= 1) and (dimension == 2):
        ones = np.ones(len(alternatives_1ord))
        prob = (alternatives_1ord*order)+(alternatives_1ord_2D*order)+(ones*(1-order)) #sketchy probabilities

    elif (order == 1.5) and (dimension == 1): 
        prob = alternatives_1ord+alternatives_2ord # sketchy probabilities
    elif (order == 1.5) and (dimension == 2): 
        prob = alternatives_1ord+alternatives_2ord+alternatives_1ord_2D+alternatives_2ord_2D # sketchy probabilities

    elif (order == 2) and (dimension == 1):
        if np.sum(alternatives_2ord) > 0:
            prob = alternatives_1ord*alternatives_2ord # good
        else:
            print(f'Fallback for order {order}, dimension {dimension}')
            prob = alternatives_1ord # fallback
    elif (order == 2) and (dimension == 2):
        if np.sum(alternatives_2ord_2D) > 0:
            prob = alternatives_1ord_2D*alternatives_2ord_2D # good
        else:
            if np.sum(alternatives_1ord_2D) > 0:
                print(f'Fallback for order {order}, dimension {dimension}')
                prob = alternatives_1ord_2D # fallback
            else:
                print(f'Last resort fallback for order {order}, dimension {dimension}')
                prob = alternatives_1ord # fallback

    # normalize probabilities, and choose next from probability distribution
    sumprob = np.sum(prob)
    if sumprob > 0:
        prob = prob/sumprob
        next_item_index = np.random.choice(indices,p=prob)
    else:
        print(f'Markov zero probability from query {m_query}, wrap around')
        next_item_index = 0 # wrap around
    next_item_1ord = data[0][next_item_index]
    next_item_1ord_2D = (data[0][next_item_index],data[1][next_item_index])
    if next_item_index > 0:
        next_item_2ord = (data[0][next_item_index-1],data[0][next_item_index])
        next_item_2ord_2D = ((data[0][next_item_index-1],data[1][next_item_index-1]),(data[0][next_item_index],data[1][next_item_index]))
    else: 
        next_item_2ord = None
        next_item_2ord_2D = None
    return (next_item_index, next_item_1ord, next_item_1ord_2D, next_item_2ord, next_item_2ord_2D)

# test
if __name__ == '__main__' :
    # example with 2D data
    data = np.array([[1,2,3,4,1,2,3,4,1,2,3,1,2,3,1,2,3,4,5,1],
                     ['A','A','A','A','A','A','A','A','B','B','B','B','B','B','B','B','B','B','B','A']])
    #analyze variable markov order in 2 dimensions
    datasize = np.shape(data)[1]
    m_1ord, m_1ord_2D, m_2ord, m_2ord_2D = analyze_vmo_vdim(data, datasize)
    models = (m_1ord, m_1ord_2D, m_2ord, m_2ord_2D)
    #generate
    indices = np.arange(datasize)
    order = 2
    dimensions = 2
    coefs = (order, dimensions)
    start_index = np.random.choice(indices)
    next_item_1ord = data[0][start_index]
    print(f'The first item is {next_item_1ord} at index {start_index}')
    next_item_1ord_2D = None
    next_item_2ord = None
    next_item_2ord_2D = None
    m_query = [0, next_item_1ord, next_item_1ord_2D, next_item_2ord, next_item_2ord_2D]
    i = 0
    while i < 50:
        m_query = generate_vmo_vdim(models, m_query, coefs, indices, data) #query markov models for next event and update query for next iteration
        next_item_index = m_query[0]
        print(f'the next item is  {data[0][next_item_index]} at index {next_item_index}')
        i += 1
    print(f'generated {i} items')
