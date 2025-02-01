#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Data containers for event corpus and probabilistic logic
"""

import numpy as np 
np.set_printoptions(precision=2)
import sys

max_events = 10000 # 100 for test, 10.000 for small scale production

# parameter names and their indices in the corpus
pnum_corpus = {
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
  'notenum_relative': 12 
}
print('pnum_corpus keys', pnum_corpus.keys())
# corpus is the main data container for events
nparms_corpus = len(pnum_corpus.keys())
corpus = np.zeros((max_events,nparms_corpus), dtype=np.float32) # float32 faster than int or float64

def clear_corpus_item(index):
  # clear one event from corpus 
  global corpus
  corpus[index] = np.zeros(nparms_corpus)
  print(f'corpus clear item {corpus[index]}')

def clear_corpus():
  # reset the whole corpus to zeros
  global corpus
  corpus = np.zeros((max_events,nparms_corpus), dtype=np.float32) # float32 faster than int or float64

def save_corpus():
  # save corpus to file
  global corpus
  np.save('saved_corpus.npy', corpus)

def load_corpus():
  # save corpus to file
  global corpus
  corpus = np.load('saved_corpus.npy')

# parameter names and max_order in the probabilistic logic module
# zero order just means give us all indices where the value occurs
# higher orders similar to markov order
prob_parms_description = {
  'ratio_best': 4,
  'ratio_2nd_best': 4,
  'notenum': 4, 
  'notenum_relative': 4,
  'phrase_num': 1}

# set up prob_parms as dict with format: [order, prob_encoder instance, [list of prob logic indices]]
# prob_encoder instance will be updated when the encoder is instantiated
# prob_logic indices corresponds to weights for each dimension in probabilistic logic
i = 0
prob_parms = {}
for key,value in prob_parms_description.items():
  if key in pnum_corpus.keys():
    indices = []
    for j in range(value+1):
      indices.append(i)
      i += 1
    prob_parms[key] = [value, None, indices]
  else:
    print(f'ERROR: parameter name {key} not in corpus, check datacontainers.py ...terminating program')
    sys.exit()

print('* prob parms and weight indices:')
for key,value in prob_parms.items():
  print(f'{key}: {value}')

