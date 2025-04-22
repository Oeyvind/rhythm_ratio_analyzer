#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer test scripts
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)
import ratio_analyzer as ra
# profiling tests
import cProfile



'''
# 14.April:
# ratios
# dur pattern
# stretch dur pattern
# purge duplicates
# compare deviation from all dur pattern suggestions
#t = np.array([0, 0.75, 1.06, 2.03])
t = np.array([0, 0.75, 1.03, 1.7, 2.03])
t = np.array([0, 0.7, 1.0, 1.75, 2.03])
ratios = ra.ratio_to_each(t)
duration_patterns = []
print('from ratio')
for i in range(len(ratios)):
    dur_pat = ra.make_duration_pattern(ratios[i])
    print(dur_pat, np.sum(np.abs(ratios[i,:,2])))
    duration_patterns.append(dur_pat)
#print(duration_patterns)
simplified_patterns = []
for i in range(len(duration_patterns)):
    d1,d2 = simplify_dur_pattern(duration_patterns[i])
    simplified_patterns.append(d1)
    simplified_patterns.append(d2)
#print(simplified_patterns)
duration_patterns.extend(simplified_patterns)
for i in range(len(duration_patterns)):
    duration_patterns[i] = duration_patterns[i].astype('int').tolist()
duration_patterns_no_dup = []
for d in duration_patterns:
    if d not in duration_patterns_no_dup: duration_patterns_no_dup.append(d)
#print(duration_patterns_no_dup)
deviations = []
dev_sum = []
#indigestabilities = [] # must find other measure of simplicity!
print('t', t)
for i in range(len(duration_patterns_no_dup)):
    t_q = fit_dur_pattern_to_time(t,duration_patterns_no_dup[i])
    deviations.append(t_q-t)
    dev_sum.append(np.sum(np.abs(t_q-t)))
    #indig = 0
    #for dur in duration_patterns_no_dup[i]:
    #    indig += ra.indigestability_n(dur)
    #indigestabilities.append(indig)
print('from dur pattern')
for i in range(len(duration_patterns_no_dup)):
    #print(duration_patterns_no_dup[i], dev_sum[i], indigestabilities[i])
    print(duration_patterns_no_dup[i], dev_sum[i])
print(np.argsort(dev_sum))
'''
'''
def indispensability_3_4(dur_pattern):
    trigger_seq = ra.make_trigger_sequence_dur_pattern(dur_pattern)
    indispensability_3 = np.array([0,2,1])
    indispensability_3 = indispensability_3/np.max(indispensability_3)
    indispensability_3 = np.tile(indispensability_3, int(np.ceil(len(trigger_seq)/len(indispensability_3))))
    indispensability_4 = np.array([0,3,1,2])
    indispensability_4 = indispensability_4/np.max(indispensability_4)
    indispensability_4 = np.tile(indispensability_4, int(np.ceil(len(trigger_seq)/len(indispensability_4))))
    indisp_3 = np.sum(trigger_seq*indispensability_3[:len(trigger_seq)])
    indisp_4 = np.sum(trigger_seq*indispensability_4[:len(trigger_seq)])
    # normalize sum to 1
    scale = indisp_3+indisp_4
    if indisp_3 < indisp_4: 
        pulse_div = 3
        certainty = 1-(indisp_3/scale)
    else:
        pulse_div = 4
        certainty = 1-(indisp_4/scale)
    return pulse_div, certainty

def indispensability_3_4_rotate(dur_pattern):
    trigger_seq = ra.make_trigger_sequence_dur_pattern(dur_pattern)
    # calc indisp, rotate all positions
    # large difference between min and max insdisp between rotations: good
    # compare best_4 and best_3 to determine 3 or 4
    indispensability_3 = np.array([0,2,1])
    indispensability_3 = indispensability_3/np.max(indispensability_3)
    indispensability_3 = np.tile(indispensability_3, int(np.ceil(len(trigger_seq)/len(indispensability_3))))
    indispensability_4 = np.array([0,3,1,2])
    indispensability_4 = indispensability_4/np.max(indispensability_4)
    indispensability_4 = np.tile(indispensability_4, int(np.ceil(len(trigger_seq)/len(indispensability_4))))
    indisp_3 = np.sum(trigger_seq*indispensability_3[:len(trigger_seq)])
    indisp_4 = np.sum(trigger_seq*indispensability_4[:len(trigger_seq)])
    # normalize sum to 1
    scale = indisp_3+indisp_4
    if indisp_3 < indisp_4: 
        pulse_div = 3
        certainty = 1-(indisp_3/scale)
    else:
        pulse_div = 4
        certainty = 1-(indisp_4/scale)
    return pulse_div, certainty

def tesselation(dur_pattern):
    # check all subsequences, 
    # test if subsequence sum is divisible by 3 or 4
    l = len(dur_pattern)
    tess_3 = 0
    tess_4 = 0
    subsize = 2
    while subsize <= l:
        for i in range(l-subsize+1):
            sub = dur_pattern[i:i+subsize]
            if np.sum(sub)%3 == 0:
                tess_3 += 1
            if np.sum(sub)%4 == 0:
                tess_4 += 1
        subsize += 1
    scale = tess_3+tess_4
    if tess_3 > tess_4: 
        pulse_div = 3
        certainty = tess_3/scale
    else:
        pulse_div = 4
        certainty = tess_4/scale
    return pulse_div, certainty

d_examples = [np.array([4,4,2,2,8,4]),
              np.array([2,1,2,1]),
              np.array([3,1,3,1]),
              np.array([2,2,1,1,4,4]),
              np.array([3,3,4,3,3]),
              np.array([3,3,4,3,3,3,3,4,3,3]),
              np.array([3,3,4,2,4]),
              np.array([3,3,4,2,4,3,3,4,2,4])]
for d in d_examples:
    print(d)
    tess_pulse_div, tess_c = tesselation(d)
    print(f'tess: {int(tess_pulse_div)}, {tess_c:.2f}')
    indisp_pulse_div, indisp_c = indispensability_3_4(d)
    print(f'indisp: {int(indisp_pulse_div)}, {indisp_c:.2f}')
    pulse_div,certainty = ra.find_pulse(d)
    print(f'findpulse: {int(pulse_div)}, {certainty:.2f}')
    pulse_div,certainty = ra.find_pulse2(d)
    print(f'findpulse2: {int(pulse_div)}, {certainty:.2f}')
'''    
    
'''
# autocorr complexity
# see if we can indicate that a duration pattern has combinations that does not align with whole beats
# the purpose is to avoid combinations like 2/3+1/4 or 3/4+1/3
# as examples 
# d1: 3/4+1/4,3/4+1/4
# d2: 2/3+1/4,3/4+1/4
# d1: 2/3+1/4,2/3+1/3
# d1: 2/3+1/3,2/3+1/3
# the _1 examples adds a whole beat 12/12 to all
  # seems to keep same complexity ordering
# the _3 examples adds a whole beat and 1/4 to all
  # d1_3 is then simple, while d4_3 is complex
# the _4 examples adds a whole beat and 1/3 to all
  # d1_4 is then complex, while d4_4 is simple
d1 = np.array([9,3,9,3])
d2 = np.array([8,3,9,3])
d3 = np.array([8,3,8,4])
d4 = np.array([8,4,8,4])
d1_1 = np.array([12,9,3,9,3])
d2_1 = np.array([12,8,3,9,3])
d3_1 = np.array([12,8,3,8,4])
d4_1 = np.array([12,8,4,8,4])
d1_3 = np.array([12,3,9,3,9,3])
d2_3 = np.array([12,3,8,3,9,3])
d3_3 = np.array([12,3,8,3,8,4])
d4_3 = np.array([12,3,8,4,8,4])
d1_4 = np.array([12,4,9,3,9,3])
d2_4 = np.array([12,4,8,3,9,3])
d3_4 = np.array([12,4,8,3,8,4])
d4_4 = np.array([12,4,8,4,8,4])
print('d1')
print(ra.autocorr_complexity(d1))
print(ra.autocorr_complexity(d2))
print(ra.autocorr_complexity(d3))
print(ra.autocorr_complexity(d4))
print('d1_1')
print(ra.autocorr_complexity(d1_1))
print(ra.autocorr_complexity(d2_1))
print(ra.autocorr_complexity(d3_1))
print(ra.autocorr_complexity(d4_1))
print('d1_3')
print(ra.autocorr_complexity(d1_3))
print(ra.autocorr_complexity(d2_3))
print(ra.autocorr_complexity(d3_3))
print(ra.autocorr_complexity(d4_3))
print('d1_4')
print(ra.autocorr_complexity(d1_4))
print(ra.autocorr_complexity(d2_4))
print(ra.autocorr_complexity(d3_4))
print(ra.autocorr_complexity(d4_4))
'''

def tesselation(dur_pattern):
    # check all subsequences, 
    # test if subsequence sum is divisible by 3 or 4
    l = len(dur_pattern)
    tess_3 = 0
    tess_4 = 0
    subsize = 2
    while subsize <= l:
        for i in range(l-subsize+1):
            sub = dur_pattern[i:i+subsize]
            if np.sum(sub)%3 == 0:
                tess_3 += 1
            if np.sum(sub)%4 == 0:
                tess_4 += 1
        subsize += 1
    scale = tess_3+tess_4
    if tess_3 > tess_4: 
        pulse_div = 3
        certainty = tess_3/scale
    else:
        pulse_div = 4
        certainty = tess_4/scale
    return pulse_div, certainty
