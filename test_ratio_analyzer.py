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

def make_weight_combinations(num_weights, discrete_weights):
  # all combinations (length num_weights) of values within range, with step size N
  weight_combinations = product(discrete_weights, repeat=num_weights)
  return list(weight_combinations)

def confidence(a):
  # the confidence is calculated as 
  # the difference between the two best alternatives divided by the range of all alternatives
  # plus half the difference between the second and third best divided by the range of all alternatives
  if len(a) < 2:
    print(f'too few alternatives in {a} to caclulate confidence')
    return 0
  else:
    max_diff = (a[-1]-a[0])
    if max_diff != 0:
      first = (a[1]-a[0])/max_diff
      second = ((a[2]-a[1])/max_diff)/2
      return first+second 
    else:
      return 0

def commondiv_ratios(a,b):
  # take two rational representations, make them use a common denominator
  # ... to compare different equal representations
  c = a[:,1].tolist()
  c.extend(b[:,1].tolist())
  common = np.lcm.reduce(c)
  afact = common / np.max(a[:,1])
  bfact = common / np.max(b[:,1])
  a *= afact
  b *= bfact
  # NOT DONE

def test_and_compare_weights(t, answer, weight_combinations):
  good_weights = []
  confidences = []
  for weights in weight_combinations:
    #print(f'**** weights {weights} ****')
    ra.set_weights(weights)
    rank = 1
    ratios_reduced, ranked_unique_representations, rankscores, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
    # !! also check ranked unique for uniqueness !!
    '''
    print('ranked_unique_representations', ranked_unique_representations)
    print(f'rankscores {rankscores}')
    for i in range((len(ranked_unique_representations))):
      print(f'{i} score {rankscores[i]} \n{np.asarray(ratios_reduced[ranked_unique_representations[i]])[:,:3]}')
    '''
    
    score_confidence = confidence(rankscores)
    #print(f'confidence {score_confidence}')

    # check if we found the right answer
    best = ranked_unique_representations[0]
    one = np.array(ratios_reduced[best][:,:2],dtype='int')
    print(f'answer: {answer.tolist()} \nbest  : {one.tolist()} \nbest_ID: {best}')
    good_answer = np.array_equal(answer,one)
    if good_answer:
      good_weights.append(weights)
      confidences.append(score_confidence)

    any_good = False
    good_not_selected = []
    for i in ranked_unique_representations:
      #print(f'answer:{answer}, \ncompare{np.array(ratios_reduced[i][:,:2],dtype="int")}')
      alternative_answer = np.array(ratios_reduced[i][:,:2],dtype='int')
      if np.array_equal(answer, alternative_answer):
        any_good = True
        good_not_selected.append([i, alternative_answer.tolist()])

  print(f'good {len(good_weights)}, out of {len(weight_combinations)}')
  print(f'rankscores:\n{rankscores} \nranked_unique:\n{ranked_unique_representations}')
  if len(confidences) > 0:
    confidences_avg = sum(confidences)/len(confidences)
  else:
    confidences_avg = -1
  print(f'confidences avg {confidences_avg:.{2}f}, sum {sum(confidences):.{2}f}')
  if any_good and confidences_avg < 0:
    print(f'any good alternatives:{any_good} \ngood_not_selected:{good_not_selected}')
  return good_weights, confidences



# test for each beat with all weight combinations
discrete_weights = [1,0]
num_weights = 7
weight_combinations = make_weight_combinations(num_weights, discrete_weights)
#weight_combinations = weight_combinations[:67]
#weight_combinations = [[1,1,1,1,1,1,1],[1,0,1,0,1,0,1],[0,0,0,0,0,0,1]]
#weight_combinations = [[1,1,1,1,1,1,1]]
#weight_combinations = [[1,0,1,0,1,0,1]]
#weight_combinations = [[0,0,0,0,0,0,1]]
#weight_combinations = [[0,0,0,0,0,0,1]]
#weight_combinations = [[0,0.4,0,0,0,1,0]]
# the weights are (in order):
#benni_weight
#nd_sum_weight
#ratio_dev_weight
#ratio_dev_abs_max_weight
#grid_dev_weight
#evidence_weight
#autocorr_weight


# set test rhythms as numbeats of a subdivision
# adjust subdivision to expected correct answer, set manually for each rhythm 
# THERE MIGHT BE SEVERAL EQUIVALENT GOOD ANSWERS, NEED TO REDO THIS
# f.ex. 3/4 1/4 = 3/1 1/1 both can be found
# f.ex 7/1 1/1 ... but 7/8 1/8 can not be found
'''
beats_subdivs = [[[6,3,3,2,2,2,6],6], 
                 [[2,1,1,2],2],
                 [[3,1,4,4],4],
                 [[3,1,4,4],1], # !!
                 [[7,1,8,8],1]]
'''
beats_subdivs = [[[4,1,1,1,1,3,3,2,1],4]] #!
#beats_subdivs = [[[4,1,1,1,1,3,3,2,4],4]] #!
#beats_subdivs = [[[3,3,2,3,3,2,4],4]] #!
#beats_subdivs = [[[2,1,1,1,1,1,1,2,1,1,1,1,1,1,1],4]] # !!
#beats_subdivs = [[[4,1,1,1,1,4,1,1,1,1,1],4]] #!
#beats_subdivs = [[[3,1,1,1,3,1,1,1,1],3]]
#beats_subdivs = [[[3,1,2,3,2,1,1],3]] #!
#beats_subdivs = [[[3,1,1,2,1,1,2,1,1],3]]
#beats_subdivs = [[[3,1,1,2,1,1,2,1,3],3]]
#beats_subdivs = [[[3,1,1,1,2,1,3],3]]

#beats_subdivs = [[[4,2,1,1,4],4]] #!
#beats_subdivs = [[[4,2,2,4],4]]

#beats_subdivs = [[[6,3,3,2,2,2,6],6]]
#beats_subdivs = [[[2,1,1,2],2]]
beats_subdivs = [[[3,1,4,4],4]]
beats_subdivs = [[[2,1,2,1,3],3]]
#beats_subdivs = [[[7,1,8,8],1]]
for beats,subdiv in beats_subdivs:
  t = make_time_from_beats(beats, subdiv)
  print(t)
  ratios = ra.ratio_to_each(t, div_limit=4)
  ratio_scores = ra.ratio_scores(ratios,t)
  ratio_scores = np.array(ratio_scores)
  print(len(ratios), len(ratio_scores), type(ratio_scores))
  for i in range(len(ratios)):
    print(f'ratios \n{ratios[i]}, \nratio_scores {ratio_scores[:,i]}')
'''
all_weights = []
all_confidences = []
for beats,subdiv in beats_subdivs:
  print(f'**************** beat {beats} ****************')
  t = make_time_from_beats(beats, subdiv)
  answer = make_correct_answer(beats, subdiv)
  #print(f'answer {answer.tolist()}')
  good_weights, confidences = test_and_compare_weights(t, answer, weight_combinations)
  all_weights.append(good_weights)
  all_confidences.append(confidences)
'''
'''
# intersection of good weights, find those who exist with both/all beats
weight_sets = []
for i in range(len(all_weights)):
  t = tuple(map(tuple, all_weights[i]))
  s = set(t)
  weight_sets.append(s)
weight_set_intersection = set(weight_sets[0]) # just start somewhere
for s in weight_sets:
  weight_set_intersection.intersection_update(s)

# sum all confidence values for each weight
confidence_for_weights = {}
for w,c in zip(all_weights, all_confidences):
  for i in range(len(w)):
    if w[i] in weight_set_intersection:
      if w[i] in confidence_for_weights:
        confidence_for_weights[w[i]] += c[i]
      else:
        confidence_for_weights[w[i]] = c[i]

print('confidence_for_weights')
for key, value in confidence_for_weights.items():
  print(key, value)
'''
# THEN
# select N best (highest confidence) for each beat
# adjust weights [0.8, 0.2] 
# intersection of good weights, append to previous good weights
# adjust weights [0.6, 0.4]
# intersection of good weights, append to previous good weights
# select N best from confidence
# print and inspect
