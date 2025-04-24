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

def indispensability_subdiv(trigger_seq):
    # Find pattern subdivision based on indispensability (Barlow)
    indis_2 = np.array([1,0])    
    indis_3 = np.array([2,0,1])
    indis_3 = (indis_3/np.max(indis_3))
    indis_4 = np.array([3,0,2,1])
    indis_4 = (indis_4/np.max(indis_4))
    #indis_5 = np.array([4,0,3,1,2])
    #indis_5 = (indis_5/(np.max(indis_5)+1)) # normalize to lower than regular
    indis_6 = np.array([5,0,3,1,4,2])
    indis_6 = (indis_6/np.max(indis_6))
    #indis_7 = np.array([6,0,4,1,5,2,3])
    #indis_7 = (indis_7/(np.max(indis_7)+1)) # normalize to lower than regular
    indis_9 = np.array([8,0,3,6,1,4,7,2,5])
    indis_9 = (indis_9/np.max(indis_9))

    # all indispensabilities
    #indis_all = [indis_7, indis_5, indis_9, indis_6, indis_4, indis_3, indis_2] # list in increasing order of preference
    indis_all = [indis_9, indis_6, indis_4, indis_3, indis_2] # list in increasing order of preference
    for i in range(len(indis_all)): # tile until long enough
        indis_all[i] = np.tile(indis_all[i], int(np.ceil(len(trigger_seq)/len(indis_all[i]))+1))

    # score table for the different indispensabilities
    indis_scores = np.array([[9, 0., 0., 0], # format: length, max_score, confidence (max/min score), rotation for best score
                             [6, 0., 0., 0],
                             [4, 0., 0., 0],
                             [3, 0., 0., 0],
                             [2, 0., 0., 0]])

    for i in range(len(indis_all)):
        subscores = np.zeros(int(indis_scores[i][0]))
        for j in range(int(indis_scores[i][0])):
            subscore = np.sum(trigger_seq*indis_all[i][j:len(trigger_seq)+j])
            subscores[j] = subscore
        indis_scores[i,1] = np.max(subscores)
        minimum = np.min(subscores)
        if minimum == 0: minimum = 1
        indis_scores[i,2] = np.max(subscores)/minimum
        #print(i,'subscores', subscores)
        found_max = False
        for j in np.argsort(subscores):    
            if (subscores[j] == np.max(subscores)) and not found_max: # we want to find the least rotation needed for max score
                indis_scores[i,3] = j
                found_max = True
    print(indis_scores)
    ranked = np.argsort(indis_scores[:,1])
    subdiv = indis_scores[ranked[-1],0]
    position = indis_scores[ranked[-1],3]
    test_best = 2
    while indis_scores[ranked[-test_best],1] == indis_scores[ranked[-1],1]: # if we have two equal max scores
        if indis_scores[ranked[-test_best],2] > indis_scores[ranked[-1],2]: # if the second alternative has better confidence
            subdiv = indis_scores[ranked[-test_best]][0] # use the second
            position = indis_scores[ranked[-test_best]][3]
        print(f'indispensability confidence used to decide a tie between {int(indis_scores[ranked[-1]][0])} and {int(indis_scores[ranked[-test_best]][0])}')
        test_best += 1
        if test_best > len(indis_scores):
            break
    return int(subdiv), int(position)

d = [1,4,1,1,2,2]
#d = [2,1,1,2,1,1]
d = [3,3,4,3,3]
#d = [3,3,2,4,2]
#d = [1,3,3,2,4,4]#,3,3,2,4,4]
#d = [6,6,3,3,2,2,2,6]
#d = [3,1,1,1,3]
#d = [4,2,1,1,4]
#d = [2,1,2,1,2,1,3]
#d = [1,4,2,1,1,4,2,1,1]
#d = [2,2,1,2,2,2,1,2,2,1,2,2,2,1]
#d = [3,2,1,2,1,3]
#d = [1,2,1,2,1,2,1,3]
#d = [4,4,4,3,1,4]
#d = [3,3,3]
print(d)
trigger_seq = ra.make_box_notation(d)
subdiv, position = indispensability_subdiv(trigger_seq)
print('subdiv', subdiv, 'position', position)