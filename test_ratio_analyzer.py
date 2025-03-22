#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer test scripts
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)
import ratio_analyzer as ra
from fractions import Fraction
from itertools import product
# profiling tests
import cProfile
import random


def make_time_from_beats(beats,subdiv, maxdev):
  timestamp = [0]
  t = 0
  for b in beats:
    delta = (b/subdiv)
    dev = (1/subdiv)*(random.random()-0.5)*maxdev
    #print('b/sub',b, subdiv, dev)
    t += delta
    timestamp.append(t+dev)
  return np.array(timestamp)


def test_ratio_analyzer(t, answer, weights, debug=False):
    ra.set_weights(weights)
    rank = 1
    ratios_reduced, ranked_unique_representations, rankscores, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
    # check if we found the right answer
    best = ranked_unique_representations[0]
    ratio_sequence = np.array(ratios_reduced[best])
    duration_pattern = ra.make_duration_pattern(ratio_sequence).astype('int')
    #print(f'answer: {answer} \nbest  : {duration_pattern.tolist()} \nbest_ID: {best}')
    good_answer = np.array_equal(answer,duration_pattern)
    #print('good:', good_answer)
    if (not good_answer) or debug:
      #print(ranked_unique_representations)
      #print(rankscores)
      for i in range(len(ranked_unique_representations)):
        print(f'ratio {i} \n{ratios_reduced[ranked_unique_representations[i]]} \nscore {i} \n{rankscores[i]}')
    return duration_pattern, np.array(ratios_reduced[best]), good_answer

def test_ratio_analyzer_on_beats(beats_subdivs, weights):
  good = 0
  num_attempts = 5
  for beats,subdiv in beats_subdivs:
    for i in range(num_attempts):
      maxdev = 0.2
      t = make_time_from_beats(beats, subdiv, maxdev)
      print(t)
      duration_pattern, suggestion, good_answer = test_ratio_analyzer(t, beats, weights)
      if good_answer:
        good += 1
  print(f'num good {good} out of {num_attempts*len(beats_subdivs)}')
  print(len(beats_subdivs))


beats_subdivs = [[[6,3,3,2,2,2,6],6], 
                 [[2,1,1,2],2],
                 [[3,1,4,4],4],
                 [[4,1,1,1,1,3,3,2,1],4], #!
                 [[3,3,2,3,3,2,4],4], #!
                 [[2,1,1,1,1,1,1,2,1,1,1,1,1,1,1],4], # !!
                 [[7,1,8,8],1],
                 [[7,1,1,7,3,2,3,8],1],
                 [[4,1,1,1,1,4,1,1,1,1,1],4], #!
                 [[3,1,1,1,3,1,1,1,1],3],
                 [[3,1,2,3,2,1,1],3], #!
                 [[3,1,1,2,1,1,2,1,1],3],
                 [[3,1,1,2,1,1,2,1,3],3],
                 [[3,1,1,1,2,1,3],3],
                 [[4,2,1,1,4],4], #!
                 [[4,2,1,1,4],4],
                 [[3,5,5,3],4],
                 [[3,5,3,3,2],4], 
                 [[2,1,2,1,3],3], 
                 [[3,3,4,2,2],4]]

weights = [0.2, 0.0, 0., 0., 0.0, 0.0, 0.0, 0.0]
# weights for the scoring of ratio alternatives, in this order:
#barlow_weight
#benni_weight
#nd_sum_weight
#ratio_dev_weight
#ratio_dev_abs_max_weight
#grid_dev_weight
#evidence_weight
#autocorr_weight

dur_pat = [2,2,1,1]
dev = 0.25
#t = make_time_from_beats(dur_pat, 4, dev)
#t = np.array([0, 0.51, 1.03, 1.26, 1.47])
dur_pat = [2,2,2,1]
t = np.array([0, 1.109, 1.9, 3.0, 3.5])

print(f't: {t}')
answer = dur_pat
ans_duration_pattern, ratios, good_answer = test_ratio_analyzer(t, answer, weights, debug=False)
print(f'{ans_duration_pattern} \n{ratios} \n{good_answer}')