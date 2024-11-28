#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Data containers for rhythm analysis and probabilistic logic
"""

import numpy as np 
np.set_printoptions(precision=2)

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
prob_parms = {
  'ratio_best': [2, None, [0,1,2]],
  'ratio_2nd_best': [2, None, [3,4,5]]}

'''# test set
pnum_prob = {
  'ratio_best': 0, # 'zeroeth order' just means give us all indices where the value occurs
  'ratio_best_1order': 1, # first order markovian lookup
  'ratio_best_2order': 2,
  'ratio_2nd_best': 3,
  'ratio_2nd_best_1order': 4,
  'ratio_2nd_best_2order': 5,
  'phrase_num': 6} # the rest is placeholders, to be implemented
'''

# full set
'''
pnum_prob = {
  'ratio_best': 0, # 'zeroeth order' just means give us all indices where the value occurs
  'ratio_best_1order': 1, # first order markovian lookup
  'ratio_best_2order': 2,
  'ratio_best_3order': 3,
  'ratio_best_4order': 4,
  'ratio_2nd_best': 5,
  'ratio_2nd_best_1order': 6,
  'ratio_2nd_best_2order': 7,
  'ratio_2nd_best_3order': 8,
  'ratio_2nd_best_4order': 9,
  'phrase_num': 10, # the rest is placeholders, to be implemented
  'downbeat': 11,
  'amp_relative': 12,
  'pitch_relative': 13,
}
'''