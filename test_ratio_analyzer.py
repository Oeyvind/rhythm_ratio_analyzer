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

def make_weight_combinations(num_weights, discrete_weights):
  # all combinations (length num_weights) of values within range, with step size N
  weight_combinations = product(discrete_weights, repeat=num_weights)
  return list(weight_combinations)

def make_variation_on_each_weight(weights, adjust_up=True, adjust_down=True):
  # Take 1 weight variations in, make 16 variations (or 8 if only adjusting up or down)
  # for each variation, adjust one of the 8 weights, by bisect method up or down from current value
  # Output list of 8 variations
  new_weights = []  
  if adjust_down:
    for i in range(len(weights)):
      new_w = np.copy(weights).astype('float')
      if (new_w[i] == 1) or (new_w[i] == 0):
        new_w[i] = 0.5
      else:
        new_w[i] *= 0.5
      new_weights.append(tuple(new_w))
  if adjust_up:
    for i in range(len(weights)):
      new_w = np.copy(weights).astype('float')
      if (new_w[i] == 1) or (new_w[i] == 0):
        new_w[i] = 0.5
      else:
        new_w[i] += (1-new_w[i])*0.5
      new_weights.append(tuple(new_w))
  return new_weights
  

def make_adjusted_weights_variations_low(weights):
  # If this weight works, but can be improved,
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

def test_ratio_analyzer(t, answer, weights, debug=False):
    ra.set_weights(weights)
    rank = 1
    ratios_reduced, ranked_unique_representations, rankscores, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
    # check if we found the right answer
    best = ranked_unique_representations[0]
    ratio_sequence = np.array(ratios_reduced[best])
    duration_pattern = ra.make_duration_pattern(ratio_sequence).astype('int')
    print(f'answer: {answer} \nbest  : {duration_pattern.tolist()} \nbest_ID: {best}')
    good_answer = np.array_equal(answer,duration_pattern)
    print('good:', good_answer)
    if (not good_answer) or debug:
      #print(ranked_unique_representations)
      #print(rankscores)
      for i in range(len(ranked_unique_representations)):
        print(f'ratio {i} \n{ratios_reduced[ranked_unique_representations[i]]} \nscore {i} \n{rankscores[i]}')
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

def auto_adjust_weights(init_weight_combinations, beats_subdivs, maxdev=0, num_attempts=3, training_rounds=3, outputfile ='weights_adjusted.txt'):
  print(f'testing the {len(init_weight_combinations)} initial weights, {training_rounds} training rounds')
  print(f'maxdev: {maxdev}, num_attempts: {num_attempts}, outputfile: {outputfile}')
  w_c_dict = {} # master dictionary of weights, with confidence values for that weight
  all_tested_weights = set() # keep track of weights that have been tested 
  for w in init_weight_combinations:
    all_tested_weights.add(tuple(w))
  for beats,subdiv in beats_subdivs:
    
    # need to make several attempts when using random deviations from time
    # keep the weight, confidence only for weights that are successful in all attempts
    good_weights_in_attempt = []
    good_confidences_in_attempt = []
    for i in range(num_attempts):
      t = make_time_from_beats(beats, subdiv, maxdev)
      good_weights, confidences = test_and_compare_weights(t, beats, init_weight_combinations)
      good_weights_in_attempt.append(good_weights)
      good_confidences_in_attempt.append(confidences)
    good_weights_set_intersection = find_intersection_good_weights(good_weights_in_attempt)
    good_weights = []
    confidences = []
    for i in range(len(good_weights_in_attempt)):
      for j in range(len(good_weights_in_attempt[i])):
        if tuple(good_weights_in_attempt[i][j]) in good_weights_set_intersection:
          good_weights.append(good_weights_in_attempt[i][j])
          confidences.append(good_confidences_in_attempt[i][j])
        
    # working alternative without several attempts:
    #t = make_time_from_beats(beats, subdiv, maxdev)
    #good_weights, confidences = test_and_compare_weights(t, beats, init_weight_combinations)
    
    for w,c in zip(good_weights, confidences):
      w_c_dict.setdefault(tuple(w), []).append(c)
  print('*****')
  for i in range(training_rounds):
    print(f'training round {i}, exploring {len(list(w_c_dict.keys()))} weights with {len(beats_subdivs)} duration patterns')
    w_c_dict3 = {}
    purge_list = []
    #i = 0
    if (i>2) and ((i%2)==0):
      adjust_up = False
    else:
      adjust_up = True
    print(f'adjust up: {adjust_up}')
    for k,v in w_c_dict.items():
      #if i%100 == 0:
      #  print(f'explore {int(i/100)*100}')
      #i += 1
      #print(f'{k}, avg:{(sum(v)/len(v)):.2f}, min:{min(v):.2f}')
      w_c_dict_temp, all_tested_weights = explore_test_weight_variations(k, w_c_dict, beats_subdivs, all_tested_weights, maxdev, num_attempts)
      if len(list(w_c_dict_temp.keys())) > 0: # if we found a weight with better confidence
        purge_list.append(k) # mark parent weight for removal  
      for k2,v2 in w_c_dict_temp.items():
        w_c_dict3.setdefault(tuple(k2), []).extend(v2) # store to new dict
    #print('*** *** length of weight dict:', len(list(w_c_dict.keys())))
    for k in purge_list: # remove less good weights
      del w_c_dict[k]
    #print('*** *** length of weight dict:', len(list(w_c_dict.keys())))
    for k,v in w_c_dict3.items():
        w_c_dict.setdefault(tuple(k), []).extend(v) # store to parent dict
    # HERE, we can also remove the weights lowest confidence from the full set of evaluated weights
    avg_list = []
    min_list = []
    for k,v in w_c_dict.items():
      avg_list.append(sum(v)/len(v))
      min_list.append(min(v))
    cut_amount = 0.5
    avg_cutoff = max(avg_list) - (max(avg_list)-min(avg_list))*cut_amount
    min_cutoff = max(min_list) - (max(min_list)-min(min_list))*cut_amount
    purge_list = []
    for k,v in w_c_dict.items():
      if ((sum(v)/len(v)) < avg_cutoff) and (min(v) < min_cutoff):
        purge_list.append(k)
    print(f'purge {len(purge_list)} weights by confidence cutoff')
    for k in purge_list: # remove less good weights
      del w_c_dict[k]    
  print('weights, average confidence, minimum confidence')
  with open(outputfile, 'w') as w_file: 
    for k,v in w_c_dict.items():
      s = f'{k}, avg:{(sum(v)/len(v)):.2f}, min:{min(v):.2f}'
      print(s)
      w_file.write(s+'\n')
  print(f'keeping {len(list(w_c_dict.keys()))} weights after training. Output written to {outputfile}')
  

def explore_test_weight_variations(weights, weights_confidence_dict, beats_subdivs, all_tested_weights, maxdev, num_attempts, adjust_up=True, adjust_down=True):
  w_confidence_avg = sum(weights_confidence_dict[weights])/len(weights_confidence_dict[weights])
  w_confidence_min = min(weights_confidence_dict[weights])
  #print('***', weights, w_confidence_avg, w_confidence_min)
  weights_var = make_variation_on_each_weight(weights, adjust_up, adjust_down)
  len_before_purge = len(weights_var)
  purge = []
  for w in weights_var: # check if we have tested this weight before
    if tuple(w) in all_tested_weights: purge.append(w)
  for p in purge:
    weights_var.remove(p)
  #print(f'num variations: {len(weights_var)} from {len_before_purge} before purge')
  
  weights_confidence_dict2 = {}
  for beats,subdiv in beats_subdivs:
    
    # need to make several attempts when using random deviations from time
    # keep the weight, confidence only for weights that are successful in all attempts
    good_weights_in_attempt = []
    good_confidences_in_attempt = []
    num_attempts = 3
    for i in range(num_attempts):
      t = make_time_from_beats(beats, subdiv, maxdev)
      good_weights, confidences = test_and_compare_weights(t, beats, weights_var)
      good_weights_in_attempt.append(good_weights)
      good_confidences_in_attempt.append(confidences)
    good_weights_set_intersection = find_intersection_good_weights(good_weights_in_attempt)
    good_weights = []
    confidences = []
    for i in range(len(good_weights_in_attempt)):
      for j in range(len(good_weights_in_attempt[i])):
        if tuple(good_weights_in_attempt[i][j]) in good_weights_set_intersection:
          good_weights.append(good_weights_in_attempt[i][j])
          confidences.append(good_confidences_in_attempt[i][j])

    #t = make_time_from_beats(beats, subdiv, maxdev)
    #good_weights, confidences = test_and_compare_weights(t, beats, weights_var)
    for w,c in zip(good_weights, confidences):
      weights_confidence_dict2.setdefault(tuple(w), []).append(c)
  #print('** len before purge', weights, len(weights_confidence_dict2.keys()))
  purge_list = []
  for k,v in weights_confidence_dict2.items():
    all_tested_weights.add(k)
    if (sum(v)/len(v) < w_confidence_avg) or (min(v) < w_confidence_min):
      purge_list.append(k)
  for k in purge_list:
    del weights_confidence_dict2[k]
  #print('** len after purge', weights, len(weights_confidence_dict2.keys()))
  #for k,v in weights_confidence_dict2.items():
  #  print(f'{k}, avg:{(sum(v)/len(v)):.2f}, min:{min(v):.2f}')
  return weights_confidence_dict2, all_tested_weights


# test for each beat with all weight combinations
discrete_weights = [1,0]
num_weights = 8
weight_combinations_from_discrete = make_weight_combinations(num_weights, discrete_weights)
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
#barlow_weight
#benni_weight
#nd_sum_weight
#ratio_dev_weight
#ratio_dev_abs_max_weight
#grid_dev_weight
#evidence_weight
#autocorr_weight

#weights = [0, 0, 0, 1, 0., 1, 0, 0]
weights = [1.0, 0.0, 1.0, 0.0, 0.0, 0.0625, 0.5, 0.75]
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
#beats_subdivs = beats_subdivs[1:2]
#test_ratio_analyzer_on_beats(beats_subdivs, weights)

def autocorr(data):
    """Autocorrelation (non normalized)"""
    mean = np.mean(data)
    data = data-mean
    return np.correlate(data, data, 'full')[len(data)-1:]

def find_pulse(data, mode='coef'):
  print(type(data))
  # reduce 
  data = data/np.gcd.reduce(data)
  pulse_2 = 0
  pulse_3 = 0
  for i in range(4):
    testdata = data*(2**i)
    print(2**i, 'data', testdata)
    t1 = make_trigger_sequence(testdata)
    a1 = autocorr(t1)
    p1 = np.argsort(-a1[1:])[:5]+1
    print(p1)
    print(a1[p1])
    for j in range(len(p1)):
      n = p1[j]
      if mode == 'coef': coef = a1[p1[j]] # correlation coefficient
      else: coef = 1/(j+1) # gradually decreasing with order
      if n <= 32:
        if n%3==0: pulse_3 += coef
        elif n%2==0: pulse_2 += coef
  certainty = pulse_2/(pulse_2+pulse_3)
  if certainty > 0.5: 
    pulse_div = 2
  else: 
    pulse_div = 3
    certainty = 1-certainty 
  #print(f'pulse div is {pulse_div} with certainty: {certainty} ')
  return pulse_div, certainty

def make_trigger_sequence(dur_pattern):
    # make the trigger sequence 
    # 1=transient, 0 = space
    # e.g. for rhythm 6/6, 3/6, 3/6, 2/6, 2/6, 2/6, the sequence will be
    # [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    trigger_seq = []
    for num in dur_pattern.astype(int):
        trigger_seq.append(1)
        for i in range(num-1):
            trigger_seq.append(0)
    return trigger_seq

'''dur_pattern = np.array([4,2,2,3,1,4])
#dur_pattern = np.array([4,2,4,2,4,3,3,3])
#dur_pattern = np.array([2,1,2,1,3,1,1,1])
#dur_pattern = np.array([2,2,1,2,2,2,1,2,2,1,2,2,2,1])
print(dur_pattern)
find_pulse(dur_pattern, mode='')
'''


#beats_subdivs = beats_subdivs[:3]
#init_weight_combinations = [[0,1,1,1,1,1,1,0],[0,1,0,1,1,0,1,0],[0,0,0,0,0,0,1,0]]
init_weight_combinations = weight_combinations_from_discrete # all 256 init weights
#init_weight_combinations = init_weight_combinations[:10]
#auto_adjust_weights(init_weight_combinations, beats_subdivs, maxdev= 0.17, num_attempts=15, training_rounds=6, outputfile='weights_adjusted1.txt')
maxdev = 0.15 
num_attempts = 10
training_rounds = 7
outputfile = f'weights_adjusted_dev{int(maxdev*1000)}_att{num_attempts}_tr{training_rounds}.txt'
#auto_adjust_weights(init_weight_combinations, beats_subdivs, maxdev, num_attempts, training_rounds, outputfile)

'''
# test time sequence  
t = np.array([0.,   0.5,  0.75, 1.25, 1.5,  2.,   2.67, 3.33, 4.  ])
t = np.array([0.,   0.5,  0.75, 1.25, 1.5,  2.,   2.33, 2.67, 3.  ])
beats=(4,2,2,4,1,1,1,1,4)
t = make_time_from_beats(beats, 1, 0)
'''

'''
# odd problem sequence
# delta 3 and 4 should be same ratio
# manual evaluation:
dur_pat = [2,2,1,1,2,1,2,1,2,2,1,1,3,1,1,4]#,1,1,4,1,1
t = [0.,   0.37, 0.74, 0.89, 1.08, 1.41, 1.61, 1.95, 2.14, 2.47, 2.86, 3.02, 3.19, 3.77, 3.92, 4.09]

# print from test with osc_server
ratios best:
[0.5  0.5  0.17 0.25 0.5  0.25 0.5  0.25 0.5  0.5  0.25 0.25 0.75 0.25
 0.25]
pulse_div, certainty 3 1.0
tempo_sanitized, tempo_factor 109.3200442044246 1.3333333333333333
sanitized ratios best:
[0.67 0.67 0.22 0.33 0.67 0.33 0.67 0.33 0.67 0.67 0.33 0.33 1.   0.33
 0.33]
 '''
# odd problem sequence
# delta 3 and 4 should be same ratio
# manual evaluation:
dur_pat = [2,2,1,1,2,1,2,1,2,2,1,1,3,1,1]#,4]#,1,1,4,1,1
t = np.array([0.,   0.37, 0.74, 0.89, 1.08, 1.41, 1.61, 1.95, 2.14, 2.47, 2.86, 3.02, 3.19, 3.77, 3.92, 4.09])

'''ratios_reduced, ranked_unique_representations, rankscores, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, 1)
score_confidence = confidence(rankscores)
# check if we found the right answer
best = ranked_unique_representations[0]
ratio_sequence = np.array(ratios_reduced[best])
duration_pattern = ra.make_duration_pattern(ratio_sequence).astype('int')
print(duration_pattern, np.equal(duration_pattern, dur_pat))
print(ra.weights)
'''
weights = [0, 1, 1, 0.3, 1, 0.2, 0.3, 1]
answer = dur_pat
ans_duration_pattern, ratios, good_answer = test_ratio_analyzer(t, answer, weights, debug=True)