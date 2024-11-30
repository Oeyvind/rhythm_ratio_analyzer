#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Data containers for event corpus and probabilistic logic
"""

import numpy as np 
np.set_printoptions(precision=2)
import sys

max_events = 100 # 100 for test, 10.000 for small scale production

# parameter names and their indices in the corpus
pnum_corpus = {
  'index': 0, # register indices for data points currently in use
  'timestamp' : 1,
  'ratio_best': 2, # best unique rational approx, as float
  'deviation_best' : 3,
  'ratio_2nd_best': 4,
  'deviation_2nd_best' : 5,
  'phrase_num': 6, # the rest is placeholders, to be implemented
  'downbeat_trig': 7,
  'amp': 8,
  'amp_relative': 9,
  'pitch': 10,
  'pitch_relative': 11
}
# corpus is the main data container for events
nparms_corpus = len(pnum_corpus.keys())
corpus = np.zeros((max_events,nparms_corpus), dtype=np.float32) # float32 faster than int or float64

# parameter names and max_order in the probabilistic logic module
# zero order just means give us all indices where the value occurs
# higher orders similar to markov order
prob_parms_description = {
  'ratio_best': 2,
  'ratio_2nd_best': 2}

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

'''
# test set
prob_parms_description = {
  'ratio_best': 2, 
  'ratio_2nd_best': 2,
  'phrase_num': 1} 
'''

'''
# full set example
prob_parms_description = {
  'ratio_best': 4, 
  'ratio_2nd_best': 4,
  'phrase_num': 1,
  'downbeat': 0,
  'amp_relative': 2,
  'pitch_relative': 2,
}
'''