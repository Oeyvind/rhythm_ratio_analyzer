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

    def __init__(self): # this method is called when the class is instantiated
        self.markov_stm = {}
        self.previous_item = None 
        self.wraparound = True

    def analyze(self, item, index):
        print('Markov analyze', item)
        if self.previous_item == None: # first item received is treated differently
            self.previous_item = item
            return
        else: # all next items are analyzed, stored as possible successors to the previous note
            self.markov_stm.setdefault(self.previous_item, []).append(index)
            self.previous_item = item

    def next_item(self, previous=None):
        print('next_item', previous)
        # as we are live recording items for analysis, dead ends are likely, and needs to be dealt with
        if previous and (previous not in self.markov_stm.keys()):
            print('Markov: dead end')
            if self.wraparound:
                print("Wrapping around to start of sequence")
                return 0
            return -1.0
        if len(self.markov_stm.keys()) == 0:
            print('Empty Markov sequence')
            return -1.0
        # for the very first item, if we do not have any previous note, so let's choose one randomly
        if not previous:
            previous = random.choice(list(self.markov_stm.keys()))
        alternatives = self.markov_stm[previous] # get a list of possible next items
        new_item_index = random.choice(alternatives) # and choose one of them
        return new_item_index
    
    def clear(self):
        self.markov_stm = {}
        self.previous_item = None 
        

# test
if __name__ == '__main__' :
    m = Markov()
    input_melody = ['C', 'D', 'E', 'F', 'G', 'E', 'F', 'D', 'C#']#, 'stop']
    #analyze
    i = 0
    for note in input_melody:
        m.analyze(note, i)
        i += 1
    print(m.markov_stm)
    print('**** **** done analyzing **** ****')
    #generate
    new_notes = []
    next_note = None
    i = 0
    while i < 15:
        if not next_note == 'stop':
            next_note_index = m.next_item(next_note)
            next_note = input_melody[next_note_index]
            print('the next note is ', next_note)
            new_notes.append(next_note)
        i += 1
    print('generated {} notes'.format(len(new_notes)-1))
    print('notes', new_notes)
          
    
