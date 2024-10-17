#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
A simple markov chain generator.

@author: Øyvind Brandtsegg 2018
@contact: obrandts@gmail.com
@license: GPL
"""

import random

class Markov:

    def __init__(self, size=100): # this method is called when the class is instantiated
        self.markov_stm = {}
        self.empty_index_container = np.zeros(size)
        self.previous_item = None 
        self.wraparound = True

    def analyze(self, item, index):
        print('Markov analyze', item)
        if self.previous_item == None: # first item received is treated differently
            self.previous_item = item
            return
        else: # all next items are analyzed, stored as possible successors to the previous note
            print(self.previous_item, index, item)
            if self.previous_item not in self.markov_stm.keys():
                index_container = self.empty_index_container.copy()
                index_container[index] = 1
                self.markov_stm[self.previous_item] = index_container
            else:
                self.markov_stm[self.previous_item][index] = 1
            self.previous_item = item

    def next_items(self, previous=None):
        print('previous_item', previous)
        # as we are live recording items for analysis, dead ends are likely, and needs to be dealt with
        if previous and (previous not in self.markov_stm.keys()):
            print('Markov: dead end')
            if self.wraparound:
                print("Wrapping around to start of sequence")
                return self.empty_index_container
            return [-1.0]
        if len(self.markov_stm.keys()) == 0:
            print('Empty Markov sequence')
            return [-1.0]
        # for the very first item, if we do not have any previous note, so let's choose one randomly
        if not previous:
            previous = random.choice(list(self.markov_stm.keys()))
        alternatives = self.markov_stm[previous] # get an index container of possible next items
        return alternatives
    
    def clear(self):
        self.markov_stm = {}
        self.previous_item = None 
        

# test
if __name__ == '__main__' :
    import numpy as np
    data = np.array([[1,2,3,4,1,2,3,4,1,2,3,1,2,3,1,2,3,4,5],
                     ['A','A','A','A','A','A','A','A','B','B','B','B','B','B','B','B','B','B','B']])
    #analyze
    datasize = np.shape(data)[1]
    indices = np.arange(datasize)
    m1 = Markov(datasize)
    m1_2D = Markov(datasize)
    for i in range(np.shape(data)[1]):
        m1.analyze(data[0][i], i)
        m1_2D.analyze((data[0][i],data[1][i]), i)
    for key, value in m1.markov_stm.items():
        print(key,value)
    for key,value in m1_2D.markov_stm.items():
        print(key,value)
    print('**** **** done analyzing **** ****')
    #generate
    next_item = None
    next_item_2D = None
    i = 0
    while i < 15:
        alternatives1 = m1.next_items(next_item)
        alternatives1_2D = m1_2D.next_items(next_item_2D)
        #print(alternatives1, '\n', alternatives1_2D)
        prob = alternatives1*alternatives1_2D
        sumprob = np.sum(prob)
        if sumprob > 0:
            prob = prob/sumprob
            next_item_index = np.random.choice(indices,p=prob)
        else:
            print('Markov zero probability, wrap around')
            next_item_index = 0 # wrap around
        next_item = data[0][next_item_index]
        next_item_2D = (data[0][next_item_index],data[1][next_item_index])
        print(f'the next item is  {next_item} at index {next_item_index}')
        i += 1
    print(f'generated {i} items')
