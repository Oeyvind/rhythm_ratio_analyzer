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



def fit_tempo_from_dur_pattern(dur_pattern, t):
    # Check all subsequences of dur pattern against the deltatimes from the time series,
    # to find a tempo estimation for each subsequence
    # Take the average of all subsequence tempo estimations
    length = len(dur_pattern)
    t_diff = np.diff(t)
    tempi = 0
    num_iterations = 0
    subsize = 1
    while subsize <= length:
        for i in range(length-subsize+1):
            num_iterations += 1
            sub_dur = dur_pattern[i:i+subsize]
            sub_time = t_diff[i:i+subsize]
            #print('dur', sub_dur, 't_diff', sub_time)
            temp = (np.sum(sub_dur)/np.sum(sub_time))
            #print('temp', temp)
            tempi += temp #??? multiply with sum(sub_dur) ???
        subsize += 1
    tempo = 60*(tempi/num_iterations) #??? and divide by sum of all dur
    #print('tempo', tempo)    
    return tempo

def fit_dur_pattern_deviations(dur_pattern, t, tempo):
    # Find the best fit of deviations by
    # 1. construct quantized time from tempo and dur pattern
    # 2. initial deviation estimate (align first event with start time)
    # 3. slide time series according to average deviation (to minimize average deviation)
    # 4  repeat step 3 a few times to come closer to average zero
    num_steps = np.sum(dur_pattern)
    step_size = 60/tempo
    t_quantized = [t[0]]
    for i in range(1, len(dur_pattern)+1):
        t_quantized.append(t_quantized[i-1]+(dur_pattern[i-1]*step_size))
    print('**fit_dur_pattern_deviations**')
    print('t:', t)
    print('d:', dur_pattern)
    print('tempo:', tempo)
    print('t_q:', t_quantized)
    for i in range(4):
        print('')
        t_diff = t-t_quantized
        print('t_diff', t_diff)
        dev = t_diff[1:]/np.diff(t_quantized)
        t = t-(np.average(dev))
        print(i, dev, np.average(dev), dev-np.average(dev))
    print('****')
    return dev

#tempo: 239.47910888652055

#t= np.array([0,1,1.5,2,3.3])
#d= [2,1,1,2]
t= np.array([0.1,0.7,2.2])
d = [1,1]
t= np.array([0., 0.485, 0.735, 0.994, 1.496])
d = [2, 1, 1, 2]
tempo = fit_tempo_from_dur_pattern(d,t)
print('tempo', tempo)
dev = fit_dur_pattern_deviations(d,t,tempo)
print(d)
print(dev)
