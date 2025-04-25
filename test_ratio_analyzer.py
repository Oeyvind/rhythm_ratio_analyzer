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
    # 2. find deviation for each dur in dur pattern
    # SKIP 3. subtract average of all deviations from each deviaton
    # 4  use dur+deviation to try to reconstruct t from t_quantized
    step_size = 60/tempo
    t_quantized = [t[0]]
    for i in range(1, len(dur_pattern)+1):
        t_quantized.append(t_quantized[i-1]+(dur_pattern[i-1]*step_size))
    print('**fit_dur_pattern_deviations**')
    print('t:', t)
    print('d:', dur_pattern)
    print('tempo:', tempo, 'step_size', step_size)
    print('t_q:', t_quantized)
    t_dev = t-t_quantized
    print('t_dev:', t_dev)
    #dur_dev = ((t(n+1)-t(n)) / (tq(n+1)-tq(n))) * (dur/step_size)
    #!! must relate dur to quantizzed, not just to delta
    # only the dur landing on a deviation should have deviation
    print('diff(tq)', np.diff(t_quantized))
    dur_dev = (t_dev[1:]/np.diff(t_quantized)) #* (0.5/step_size)
    print('dur_dev', dur_dev)
    #avg = np.average(dur_dev)
    #print('avg', avg)
    #dur_dev = dur_dev-avg
    #print('dur_dev_avg', dur_dev)
    test = [0]
    for i in range(len(dur_pattern)):
        test.append((t_quantized[i+1])+(np.diff(t_quantized)[i]*dur_dev[i]))
    print('test', test)


    return dur_dev

#tempo: 239.47910888652055

t= np.array([0,1,1.45,2,3])
d= [2,1,1,2]
#t= np.array([0,0.51,1.989101876])
#d = [1,3]

t= np.array([0., 0.485, 0.735, 0.994, 1.496])
d = [2, 1, 1, 2]
tempo = fit_tempo_from_dur_pattern(d,t)
print('tempo', tempo)
dev = fit_dur_pattern_deviations(d,t,tempo)
#print(d)
#print(dev)
