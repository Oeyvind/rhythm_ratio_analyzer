#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer test scripts
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
import ratio_analyzer as ra
from fractions import Fraction
from itertools import product
# profiling tests
import cProfile


def make_time_from_beats(beats,subdiv):
  timestamp = [0]
  for b in beats:
    t = timestamp[-1]
    timestamp.append(t+(b/subdiv))
  return np.array(timestamp)

def make_correct_answer(beats, subdiv):
  answer = []
  for b in beats:
     f = Fraction(b,subdiv)
     answer.append([f.numerator,f.denominator])
  return np.array(answer, dtype='int')

def create_weight_combinations(num_weights, stepsize):
  # all combinations (length num_weights) of values within range, with step size N
  min = 0
  max = 1
  discrete_weights = []
  w = min
  while w <= max:
    discrete_weights.append(w)
    w += stepsize
  weight_combinations = product(discrete_weights, repeat=num_weights)
  return list(weight_combinations)

def create_and_compare(t, answer, weight_combinations, stepsize):
  good_weights = []
  for weights in weight_combinations:
    ra.set_weights(weights)
    rank = 1
    ratios_reduced, ranked_unique_representations, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
    best = ranked_unique_representations[0]
    #ratios_list = ratios_reduced[best].tolist()
    one = np.array(ratios_reduced[best][:,:2],dtype='int')
    '''
    print('best')
    for o in one:
      print(f'{o[0]}/{o[1]}')
    print('answer')
    for a in answer:
      print(f'{a[0]}/{a[1]}')
    '''
    e = np.array_equal(answer,one)
    #print('equal', e)
    
    if e:
      good_weights.append(weights)
  print(f'good {len(good_weights)}, out of {len(weight_combinations)}')
  return good_weights


test_weights = {
    'benni_weight' : 0.3,
    'nd_sum_weight' : 0.3,
    'ratio_dev_weight' : 0.3,
    'ratio_dev_abs_max_weight' : 0.2,
    'grid_dev_weight' : 0.2,
    'evidence_weight' : 0.1,
    'autocorr_weight' : 0.3
}


#if __name__ == '__main__':
#beats = [3,3,2]
#subdiv = 4
beats = [6,3,3,2,2,2,6]
subdiv = 6
t = make_time_from_beats(beats, subdiv)
print(f'{beats} \n{t}')
answer = make_correct_answer(beats, subdiv)
resolution = 1
print(len(create_weight_combinations(7, resolution)))
weight_combinations = create_weight_combinations(7, resolution)
good_weights = create_and_compare(t, answer, weight_combinations, resolution)
#cProfile.run('create_and_compare(t, answer, 7, resolution)')
#cProfile.run('test_r(0.01)')
#cProfile.run('test_f(0.01)')
ord_good =[]
for g in good_weights:
  ord_good.append([sum(g), g])
  #print(g, '    ', sum(g))
ord_good.sort()
for i in range(5):
  print(ord_good[i])
'''
weights = [test_weights['benni_weight'], 
           test_weights['nd_sum_weight'], 
           test_weights['ratio_dev_weight'],  
           test_weights['ratio_dev_abs_max_weight'],  
           test_weights['grid_dev_weight'], 
           test_weights['evidence_weight'], 
           test_weights['autocorr_weight']]
ra.set_weights(weights)
rank = 1
ratios_reduced, ranked_unique_representations, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
print('best')
best = ranked_unique_representations[0]
ratios_list = ratios_reduced[best].tolist()
one = np.array(ratios_reduced[best][:,:2],dtype='int')
for o in one:
  print(f'{o[0]}/{o[1]}')
print('second_best')
next_best = ranked_unique_representations[1]
two = np.array(ratios_reduced[next_best][:,:2],dtype='int')
for t in two:
  print(f'{t[0]}/{t[1]}')
print('answer')
for a in answer:
  print(f'{a[0]}/{a[1]}')

print('equal', np.array_equal(answer,one))
'''
