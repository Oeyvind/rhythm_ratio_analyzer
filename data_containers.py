#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Data containers for event corpus and probabilistic logic
"""

import numpy as np 
np.set_printoptions(precision=2)
import sys

class DataContainers:
  """ 
  Data containers for event corpus and probabilistic logic
  """
  def __init__(self): 
    self.max_events = 10000 # 100 for test, 10.000 for small scale production

    # parameter names and their indices in the corpus
    self.pnum_corpus = {
      'index': 0, # register indices for data points currently in use
      'timestamp' : 1, # time of note on 
      'time_off' : 2, # time of note off
      'duration' : 3, # relative duration (time_off - timestamp) / (timestamp next event/timestamp this event)
      'ratio_best': 4, # best unique rational approx, as float
      'deviation_best' : 5,
      'ratio_2nd_best': 6,
      'phrase_num': 7, 
      'downbeat_trig': 8, # to be implemented
      'velocity': 9,
      'velocity_relative': 10, 
      'notenum': 11,
      'notenum_relative': 12,
      'chord_index': 13
    }
    print('pnum_corpus keys', self.pnum_corpus.keys())
    # corpus is the main data container for events
    self.nparms_corpus = len(self.pnum_corpus.keys())
    self.corpus = np.zeros((self.max_events, self.nparms_corpus), dtype=np.float32) # float32 faster than int or float64

    # parameter names and max_order in the probabilistic logic module
    # zero order just means give us all indices where the value occurs
    # higher orders similar to markov order
    self.prob_parms_description = {
      'ratio_best': 4,
      'ratio_2nd_best': 4,
      'notenum': 4, 
      'notenum_relative': 4,
      'phrase_num': 1}

    # set up prob_parms as dict with format: [order, prob_encoder instance, [list of prob logic indices]]
    # prob_encoder instance will be updated when the encoder is instantiated
    # prob_logic indices corresponds to weights for each dimension in probabilistic logic
    i = 0
    self.prob_parms = {}
    for key,value in self.prob_parms_description.items():
      if key in self.pnum_corpus.keys():
        indices = []
        for j in range(value+1):
          indices.append(i)
          i += 1
        self.prob_parms[key] = [value, None, indices]
      else:
        print(f'ERROR: parameter name {key} not in corpus, check datacontainers.py ...terminating program')
        sys.exit()

    print('* prob parms and weight indices:')
    for key,value in self.prob_parms.items():
      print(f'{key}: {value}')

    # chord list, an appendix to the corpus, for events that contain several simultaneous notes
    # as the size of the chord may vary, we only store a chord index in the corpus, pointing to an index in the chord list
    # format for entries:
    # [[relative_note, relative_velocity, relative_time],[same for next notes in chord]]
    self.chord_list = []
    
  def clear_corpus_item(self, index):
    # clear one event from corpus 
    self.corpus[index] = np.zeros(self.nparms_corpus)
    print(f'corpus clear item {self.corpus[index]}')
  
  def clear_corpus(self):
    # reset the whole corpus to zeros
    print('before clear corpus')
    print(self.corpus[1])
    self.corpus = np.zeros((self.max_events, self.nparms_corpus), dtype=np.float32) # float32 faster than int or float64
    print('after clear corpus')
    print(self.corpus[1])
  
  def save_corpus(self):
    # save corpus to file
    np.save('saved_corpus.npy', self.corpus)
  
  def load_corpus(self):
    # load corpus from file
    self.corpus = np.load('saved_corpus.npy')

