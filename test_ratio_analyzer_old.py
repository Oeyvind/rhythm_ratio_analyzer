#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer test scripts
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)
import ratio_analyzer as ra_new
import ratio_analyzer_old as ra
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
    dev = (delta*(random.random()-0.5))*2*maxdev
    #print('b/sub',b, subdiv, dev)
    t += delta
    timestamp.append(t+dev)
  return np.array(timestamp)

def make_weight_combinations(num_weights, discrete_weights):
  # all combinations (length num_weights) of values within range, with step size N
  weight_combinations = product(discrete_weights, repeat=num_weights)
  return list(weight_combinations)

def make_adjusted_weights_variations_low(weights):
  # If this weight works for some rhythm patterns but not for all,
  # we try to adjust each weight by half the available range,
  # and produce all combinations of such adjusted weights.
  # If the weight is at 1.0 or 0.0, adjust to 0.5
  # For this version of the function, we always adjust down (not exploring the upper half of the range),
  weights = list(weights)
  new_weights_values = []  
  for i in range(len(weights)):
    if (weights[i] == 1) or (weights[i] == 0):
      new_weights_values.append([weights[i],0.5])
    else:
      new_weights_values.append([weights[i],weights[i]*0.5])
  # create all combinations of the new values
  indices = list(product([0,1], repeat=len(weights)))
  new_weights = []
  for i in range(len(indices)):
    w_ = []
    for j in range(len(indices[i])):
      w_.append(new_weights_values[j][indices[i][j]])
    new_weights.append(w_)
  # remove the initial weights
  new_weights.remove(weights)
  # if any weight suggestion consist of only the same value repeated, remove it
  for w in new_weights:
    if len(set(w)) == 1:
      new_weights.remove(w)
  return new_weights

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

def test_and_compare_weights(t, answer, weight_combinations):
  good_weights = []
  confidences = []
  for weights in weight_combinations:
    ra.set_weights(weights)
    rank = 1
    ratios_reduced, ranked_unique_representations, rankscores, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
    score_confidence = confidence(rankscores)

    # check if we found the right answer
    best = ranked_unique_representations[0]
    ratio_sequence = np.array(ratios_reduced[best])
    duration_pattern = ra.make_duration_pattern(ratio_sequence).astype('int')
    #print(f'answer: {answer} \nbest  : {duration_pattern.tolist()} \nbest_ID: {best}')
    good_answer = np.array_equal(answer, duration_pattern)
    if good_answer:
      good_weights.append(weights)
      confidences.append(score_confidence)

    any_good = False
    good_not_selected = []
    for i in ranked_unique_representations:
      #print(f'answer:{answer}, \ncompare{np.array(ratios_reduced[i][:,:2],dtype="int")}')
      alternative_answer = np.array(ratios_reduced[i])
      alt_dur_pattern = ra.make_duration_pattern(alternative_answer)
      if np.array_equal(answer, alt_dur_pattern):
        any_good = True
        good_not_selected.append([i, alt_dur_pattern.tolist()])
  '''
  if len(confidences) > 0:
    confidences_avg = sum(confidences)/len(confidences)
  else:
    confidences_avg = -1
  print(f'confidences avg {confidences_avg:.{2}f}, sum {sum(confidences):.{2}f}')
  if any_good and confidences_avg < 0:
    print(f'any good alternatives:{any_good} \ngood_not_selected:{good_not_selected}')
  '''
  return good_weights, confidences

def find_intersection_good_weights(all_weights_good):
  # intersection of good weights, find those who exist with all beats
  weight_sets = []
  for i in range(len(all_weights_good)):
    t = tuple(map(tuple, all_weights_good[i]))
    s = set(t)
    weight_sets.append(s)
  weight_set_intersection = set(weight_sets[0]) # just start somewhere
  for s in weight_sets:
    weight_set_intersection.intersection_update(s)
  #print(f' *** num intersecting good weights {len(weight_set_intersection)} \n')
  return weight_set_intersection

def purge_duplicate_weights(weights):
  # make set of the list of weights to get rid of duplicates
  # duplicates will occur when the same weight is good for several beats suggestions
  weight_sets = []
  t = tuple(map(tuple, weights))
  s = set(t)
  return s

def sum_confidence_each_weight(all_weights, all_confidences, weight_set_intersection):
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
  return confidence_for_weights

def test_ratio_analyzer(t, answer, weights):
    ra.set_weights(weights)
    rank = 1
    ratios_reduced, ranked_unique_representations, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
    # check if we found the right answer
    best = ranked_unique_representations[0]
    ratio_sequence = np.array(ratios_reduced[best])
    duration_pattern = ra_new.make_duration_pattern(ratio_sequence).astype('int')
    print(f'answer: {answer} \nbest  : {duration_pattern.tolist()} \nbest_ID: {best}')
    good_answer = np.array_equal(answer,duration_pattern)
    print('good:', good_answer)
    if not good_answer:
      print(ratio_sequence)
    return duration_pattern, np.array(ratios_reduced[best]), good_answer


def test_ratio_analyze_scoring(beats_subdivs):
  # test ratio approximation and scoring
  for beats,subdiv in beats_subdivs:
    t = make_time_from_beats(beats, subdiv)
    print(t)
    ratios = ra.ratio_to_each(t, div_limit=4)
    ratios_copy = np.copy(ratios)
    ratio_scores = np.array(ra.ratio_scores(ratios,t))
    
    commondiv = ra.make_commondiv_ratios(ratios)
    commondiv = ra.recalculate_deviation(commondiv)
    commondiv_copy = np.copy(commondiv)
    commondiv_copy2 = np.copy(commondiv)
    commondiv_scores = np.array(ra.ratio_scores(commondiv,t))
    
    norm_num_ratios = ra.normalize_numerators(commondiv)
    norm_num_ratios = ra.recalculate_deviation(norm_num_ratios)
    evidence = ra.evidence(norm_num_ratios)
    norm_num_copy = np.copy(norm_num_ratios)
    norm_num_scores = np.array(ra.ratio_scores(norm_num_ratios,t))

    simplify = ra.simplify_ratios(commondiv_copy2)
    simplify_scores = np.array(ra.ratio_scores(simplify,t))

    for i in range(len(norm_num_ratios)):
      print(f'{i} ratios \n{ratios_copy[i]}, \nscores {ratio_scores[:,i]}')
      print(f'{i} commondiv \n{commondiv_copy[i]}, \nscores {commondiv_scores[:,i]}')
      print(f'{i} norm_num_ratios, evidence: {evidence[i]} \n{norm_num_copy[i]}, \nscores {norm_num_scores[:,i]}')
      print(f'{i} simplify \n{simplify[i]}, \nscores {simplify_scores[:,i]}')


def compare_indigestabilities(duration_pattern, suggestion):
  # testing different uses of the indigestability
  print(duration_pattern)  
  print(suggestion)
  indigest_dur = []
  for n in duration_pattern:
    indigest_dur.append(ra.indigestability_n(n))
  indigest_n = []
  indigest_d = []
  for r in suggestion:
    indigest_n.append(ra.indigestability_n(r[0]))
    indigest_d.append(ra.indigestability_n(r[1]))
  print('dur', indigest_dur, sum(indigest_dur))
  print('num', indigest_n, sum(indigest_n))
  print('den', indigest_d, sum(indigest_d))

def flatten(xss):
    return [x for xs in xss for x in xs]

# test for each beat with all weight combinations
discrete_weights = [1,0]
num_weights = 8
weight_combinations = make_weight_combinations(num_weights, discrete_weights)
#weight_combinations = [[1,1,1,1,1,1],[1,0,1,1,0,1],[0,0,0,0,0,1]]
# the weights are (in order):
#barlow_weight
#benni_weight
#nd_sum_weight
#ratio_dev_weight
#ratio_dev_abs_max_weight
#grid_dev_weight
#evidence_weight
#autocorr_weight
#weights = [0,0,0,0,1,0,0]

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


# the weights are (in order):
#benni_weight
#nd_sum_weight
#ratio_dev_weight
#ratio_dev_abs_max_weight
#grid_dev_weight
#evidence_weight
#autocorr_weight
weights = [0, 0, 1, 0., 1, 0, 0]
beats_subdivs = beats_subdivs[0:5] #test subset
good = 0
num_attempts = 1
for beats,subdiv in beats_subdivs:
  for i in range(num_attempts):
    maxdev = 0.1
    t = make_time_from_beats(beats, subdiv, maxdev)
    duration_pattern, suggestion, good_answer = test_ratio_analyzer(t, beats, weights)
    if good_answer:
      good += 1
print(f'num good {good} out of {num_attempts*len(beats_subdivs)}')

'''
for i in range(10):
  for beats,subdiv in beats_subdivs:
    maxdev = 0.1
    t = make_time_from_beats(beats, subdiv, maxdev)
    print(f'****************\nbeat {beats} \ntime {t}')
''' 
beats_subdivs = beats_subdivs[1:5] #test subset

def auto_adjust_weights(beats_subdivs, weight_combinations):
  # auto adjust weights
  all_good_weights = []
  #all_confidences = []
  for beats,subdiv in beats_subdivs:
    maxdev = 0.1
    t = make_time_from_beats(beats, subdiv, maxdev)
    print(f'****************\nbeat {beats} \ntime {t}')
    good_weights, confidences = test_and_compare_weights(t, beats, weight_combinations)
    print(f'good {len(good_weights)}, out of {len(weight_combinations)}')
    all_good_weights.append(good_weights)
    #all_confidences.append(confidences)

  all_weights_bad = []
  all_weights_good_flat = purge_duplicate_weights(flatten(all_good_weights))
  for w in weight_combinations:
    if w not in all_weights_good_flat:
      all_weights_bad.append(w)
  
  weight_set_intersection = find_intersection_good_weights(all_good_weights)
  print(f' *** num good weights {len(all_weights_good_flat)}')
  print(f' *** num bad weights {len(all_weights_bad)}')
  print(f' *** num weights good for all rhythms {len(weight_set_intersection)}')
  print(f' *** num all weights {len(weight_combinations)}')
  #sum_confidence_each_weight(all_weights_good, all_confidences, weight_set_intersection)

#auto_adjust_weights(beats_subdivs, weight_combinations)


# THEN
# select N best (highest confidence) for each beat
# adjust weights [0.8, 0.2] 
# intersection of good weights, append to previous good weights
# adjust weights [0.6, 0.4]
# intersection of good weights, append to previous good weights
# select N best from confidence
# print and inspect
#print(weight_combinations)