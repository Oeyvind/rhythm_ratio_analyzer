#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
import scipy.signal as signal
import math
from fractions import Fraction
import time # for profiling
#import logging 
#logging.basicConfig(filename="logging.log", filemode='w', level=logging.INFO)


def ratio_to_each(timeseries, mode='connect', div_limit=4):
    """Ratio of delta times to each other delta time in rhythm sequence. Also including combinations of two neighbouring delta times as reference"""
    # first make the list of deltas to compare to (all delta times, plus combination of 2 neighbouring delta times)
    # find the ratios to all delta times, from each delta time in list, with the best rational expression limited by div_limit
    t_series_len = len(timeseries)-1
    ref_deltas = []
    deltas = []
    for i in range(t_series_len):
        delta = timeseries[i+1]-timeseries[i]
        ref_deltas.append(delta)
        deltas.append(delta)
        if (mode == 'connect') and (i < (t_series_len-1)):
            ref_deltas.append(timeseries[i+2]-timeseries[i]) # then also include delta for next neighbour evet
    ref_deltas_len = len(ref_deltas)
    ratios = np.zeros((ref_deltas_len, t_series_len, 5))
    for i in range(ref_deltas_len):
        ref_delta = ref_deltas[i]
        for j in range(t_series_len):
            delta = deltas[j]
            ratio = delta/ref_delta
            f = Fraction(ratio).limit_denominator(div_limit)
            numerator, denom = f.numerator, f.denominator
            if numerator < 1: # if the subdivision is higher than 4
                print('***********WARNING***************: numerator less than 1', delta, ref_delta)
                for m in [2,4,8]: # try doubling it, then 4 then 8
                    ratio *= 2
                    f = Fraction(ratio).limit_denominator(div_limit)
                    numerator, denom = f.numerator, f.denominator
                    denom *= m # with this we compensate for the doubling, keeping the correct relationship to other ratios
                    deviation = (ratio-(numerator/denom))
                    if numerator > 0:
                        break
            deviation = (ratio-(numerator/denom)) # #difference between measured and quantized value, as fraction of the reference value
            ratios[i,j] = [numerator, denom, deviation, delta, ref_delta]
    return ratios

def ratio_scores(ratios, timeseries):
    "calculate scores for each set of ratios"
    ratio_deviations = []
    ratio_deviation_abs = []
    ratio_deviation_abs_max = []
    benedetti_height = []
    nd_add = []
    gridsize_deviations = [] #list of deviations from grid created on each delta value as rational approximation
    for i in range(len(ratios)):
        ratio_deviations.append(np.sum(ratios[i,:,2]))
        ratio_deviation_abs.append(np.sum(np.absolute(ratios[i,:,2])))
        ratio_deviation_abs_max.append(np.max(np.absolute(ratios[i,:,2])))
        grid_subdivs = np.unique(ratios[i,:,1]).astype(int) #list of all denoms in this set
        gridsize_deviation = test_gridsize_deviation(timeseries, ratios[i,0,4]/math.lcm(*grid_subdivs)) # TEST gridsize on least common multiple of the set
        gridsize_deviations.append(gridsize_deviation)
        benedetti_height.append(np.add.reduce(np.multiply(ratios[i,:,0], ratios[i,:,1]))) # sum of Benedetti heights across all ratios in each set
        nd_add.append(np.add.reduce(np.add(ratios[i,:,0], ratios[i,:,1]))) # sum of sums of numerators and denominators in each set
        '''for i in range(len(ratios)):
        print('ratio_set\n', ratios[i])
        print('ratio_deviations',ratio_deviations[i]) 
        print('ratio_deviation_abs',ratio_deviation_abs[i]) 
        print('ratio_deviation_abs_max',ratio_deviation_abs_max[i]) 
        print('gridsize_deviations', gridsize_deviations)
        print('benedetti_height',benedetti_height[i]) 
        print('nd_add',nd_add[i])'''
    return ratio_deviations, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, benedetti_height, nd_add 

def test_gridsize_deviation(timeseries, gridsize, offset=-1):
    """Test how well a ratio assumtion can be used as basis for a grid (for the whole time sequence)"""
    # for each item in rhythmlist, test how far it is from an integer multiple of the given ratio (gridsize)
    deviations = []
    if offset < 0:
        timeseries -= np.min(timeseries) # let it start from zero
    else:
        timeseries = np.subtract(timeseries,offset)# offset to the event in question
    for t in timeseries:
        deviation = abs(t)%gridsize
        if deviation > gridsize/2:
            deviation = gridsize-deviation
        deviations.append(deviation/gridsize) # using linear deviations but we could also square them
    return sum(deviations)

def make_commondiv_ratios(ratios, commondiv='auto'):
    """Set all ratios to a common denominator, in the case of rhythm analysis usually 12 is the denominator"""
    n = ratios[:,:,0].astype(int)
    d = ratios[:,:,1].astype(int)
    #dev = ratios[:,:,2]
    if commondiv == 'auto':
        d_ = np.unique(d)
        commondiv = math.lcm(*d_)
    for i in range(len(n)):
        for j in range(len(n[0])):
            f = commondiv/d[i,j]
            #print(commondiv, d[i,j], f)
            n[i,j] *= f
            d[i,j] *= f
            #dev[i,j] *= f
    ratios[:,:,0] = n
    ratios[:,:,1] = d
    #ratios[:,:,2] = dev
    return ratios

def simplify_ratios(ratios):
    """Reduce ratios to lowest terms"""
    n = ratios[:,:,0].astype(int)
    d = ratios[:,:,1].astype(int)
    for i in range(len(n)):
        for j in range(len(n[0])):
            f = Fraction(n[i,j],d[i,j])
            n[i,j] = f.numerator
            d[i,j] = f.denominator
    ratios[:,:,0] = n
    ratios[:,:,1] = d
    return ratios

def get_ranked_unique_representations(duplicates, scores):
    print(np.argsort(scores))
    ranked_unique_representations = []
    already_included = []
    for i in np.argsort(scores):
        #print('argsort score', i)
        if i not in already_included:
            for d in range(len(duplicates)):
                #print('d, already_included', d, already_included)
                if (i in duplicates[d]):
                    ranked_unique_representations.append(i)
                    #print('ranked so far:', ranked_unique_representations)
                    already_included.extend(duplicates[d])
                    duplicates.remove(duplicates[d])
                    break
    return ranked_unique_representations

def normalize_numerators(ratios):
    norm_num_ratios = np.copy(ratios)
    n = norm_num_ratios[:,:,0].astype(int)
    max_all = np.max(n)
    for i in range(len(n)):
        max_this = (np.max(n[i]))
        norm_num_ratios[i,:,0] *= (max_all/max_this) # normalize and write back
    return norm_num_ratios

def evidence(ratios):
    # check if any subarrays contain the same numerators (assuming we already have made common denominators)
    # give each subarray a score depending of how may other subarrays contain the same
    # usually run this with the output from normalize_numerators
    # invert the evidence scores when adding with other quality scores (as they rank low score as best)
    evidence_score = np.zeros((len(ratios)))
    for i in range(len(ratios)):
        n0 = ratios[i,:,0].astype(int)
        for j in range(len(ratios)):
            if i == j:
                continue
            n1 = ratios[j,:,0].astype(int)
            if np.array_equal(n0,n1):
                evidence_score[j] += 1
    return evidence_score

def normalize_and_add_scores(scores, weights, invert=None):
    # take several lists of scores, normalize them to max 1.0, 
    # set a weight for each scorelist, 
    # option to invert scores for each scorelist (1 to invert, 0 to keep as is)
    # and add them to produce a ranking (sum of scores)
    scoresum = np.zeros(len(scores[0]))
    if invert == None:
        invert = np.zeros(len(scores[0]))
    for i in range(len(scores)):
        smax = max(scores[i])
        smin = min(scores[i])
        if smax == smin:
            s = 1
        else:
            s = (scores[i]-smin)/(smax-smin)
        if invert[i] > 0:
            s = np.subtract(1,s)
        scoresum += s*weights[i]        
    return scoresum

def make_trigger_sequence(commondiv_ratios):
    # make the trigger sequence 
    # 1=transient, 0 = space
    # e.g. for rhythm 6/6, 3/6, 3/6, 2/6, 2/6, 2/6, the sequence will be
    # [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    trigger_seq = []
    for num in commondiv_ratios[:,0].astype(int):
        trigger_seq.append(1)
        for i in range(num-1):
            trigger_seq.append(0)
    return trigger_seq

def autocorr(data):
    """Autocorrelation (non normalized)"""
    return np.correlate(data, data, 'full')[len(data)-1:]

def autocorr_bitwise(data):
    """Autocorrelation by means of bitmasking, input is a list of ones and zeros"""
    acorr=[]
    b = 0b0
    for i in data:
        b = b << 1 | i
    for i in range(len(data)):
        b1 = b>>i&b
        acorr.append(b1.bit_count())
    return acorr                     

def find_duplicate_representations(ratios):
    """Find indices in the ratios array where the exact same rational approximations are used (not regarding deviations or other parameters)"""
    duplicate_list = []
    for i in range(len(ratios)):
        nd1 = ratios[i,:,:2] # numerator and denominator
        duplicate_list.append([])
        for j in range(i,len(ratios)):
            nd2 = ratios[j,:,:2]
            if np.array_equal(nd1,nd2):
                already_there = False
                for d in duplicate_list:
                    if j in d:
                        already_there = True
                if not already_there:
                    duplicate_list[i].append(j)
    empties = []
    for i in range(len(duplicate_list)):
        if len(duplicate_list[i]) == 0:
            empties.append(i)
    for i in empties:
        duplicate_list.remove([])
    return duplicate_list

def analyze(rhythm):
    """Do the full ratio analysis"""
    pass

                                               
# scratch pad


if __name__ == '__main__':
    t0 = time.perf_counter(), time.process_time()
    # example rhythms
    # rhythm is represented here by the time stamp of each event
    t = [0.0, 0.3467, 0.524, 1.02, 1.546, 1.8553, 2.088, 2.362, 2.6053, 2.8713, 3.1333, 3.62, 3.962, 4.176,]    
    # test 2 jazzphrase
    t = [0.    , 0.302 , 0.5406, 0.8426, 1.3613, 1.5746, 1.8673, 2.0813, 2.58  , 2.9286, 3.1213]
    # skalert for å matche til 3.0
    t = [0.    , 0.2903, 0.5196, 0.8099, 1.3084, 1.5134, 1.7947, 2.0004, 2.4797, 2.8148, 3.    ] 
    # ideell
    #t = [0,    0.25,     0.5,    0.75,   1.25,   1.5,    1.75,   2,      2.5,    2.75,   3]
    # manuell slark
    #t = [0,    0.3,      0.5,    0.8,    1.3,    1.5,    1.8,    2,      2.5,    2.8,   3]
    #t = [66.9, 67.2, 67.4, 67.9, 68.4, 68.7, 69.0, 69.2, 69.5, 69.7, 70.0, 70.5, 70.8, 71.0, 71.3, 71.6, 71.9, 72.4, 72.6, 72.9, 73.1, 73.6, 74.0, 74.2]
    example_rhythm = t
    #example_rhythm = [0, 1.0, 1.5, 2, 2.7, 3.1, 4.1]
    #example_rhythm = [0, 1.75, 2, 3.0]
    #example_rhythm = [0, 0.7, 1, 1.66, 2, 2.25, 3, 4]
    #for each in t:
    #    example_rhythm.append(each+4.5)
    #example_rhythm = [0, 0.7, 1, 1.5, 2]
    #example_rhythm = [0, 1, 1.51, 2.5, 3]

    #example_rhythm = [2*t for t in example_rhythm]
    rat2 = ratio_to_each(example_rhythm, div_limit=2)
    rat4 = ratio_to_each(example_rhythm, div_limit=4)
    ratios = np.concatenate((rat2, rat4), axis=0)

    rat4u,uniqindx, origindx = np.unique(rat4[:,:,:2], axis=0, return_index=True, return_inverse=True)
    for i in range(len(rat4)):
        print('\nINDX', i)
        print('num, denom, dev, delta ref_delta:')
        print(np.array_str(rat4[i], precision=3, suppress_small=True))
    for i in range(len(rat4u)):
        print('\nINDX', i, origindx[i])
        print('num, denom, dev, delta ref_delta:')
        print(np.array_str(rat4u[i], precision=3, suppress_small=True))


    for i in range(len(ratios)):
        print('\nINDX', i)
        print('num, denom, dev, delta ref_delta:')
        print(np.array_str(ratios[i], precision=3, suppress_small=True))
    
    
    ratio_deviations, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, benedetti_height, nd_add = ratio_scores(ratios,example_rhythm)
    '''
    for i in range(len(ratios)):
        print('\nINDX', i)
        print('ref_delta:', round(ratios[i,0,-1],2), 
              ' benni:',int(benedetti_height[i]), 
              ' nd_add:',round(nd_add[i],2), 
              ' dev_abs', round(ratio_deviation_abs[i], 2), 
              ' dev_abs_max', round(ratio_deviation_abs_max[i], 2), 
              ' g_dev:', round(gridsize_deviations[i],2))
        print('num, denom, dev, delta:')
        print(np.array_str(ratios[i,:,:-1], precision=3, suppress_small=True))
    '''
    ratios_commondiv = make_commondiv_ratios(ratios)
    norm_num_ratios = normalize_numerators(ratios_commondiv)
    evidence_scores = evidence(norm_num_ratios)
    print('evidence_scores', evidence_scores)
    t1 = time.perf_counter(), time.process_time()
    print('\nTime spent up to evidence with timeseries length {}:'.format(len(example_rhythm)))
    print('    RT: {} seconds'.format(t1[0]-t0[0]))
    print('    CPU: {} seconds'.format(t1[1]-t0[1]))

    benni_weight = 0.2
    nd_sum_weight = 0.5
    ratio_dev_weight = 1
    ratio_dev_abs_max_weight = 1
    grid_dev_weight = 0.0
    evidence_weight = 1
    scores = normalize_and_add_scores(
        [benedetti_height, nd_add, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, evidence_scores], 
        [benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight],
        [0, 0, 0, 0, 0, 1, 1])
    print('\nscores:: \n', [round(d,2) for d in scores])
    print('\nindices: \n', np.argsort(scores))

    #time.sleep(2)

    autocorr_scores = []
    print('len ratios', len(ratios))
    for i in range(len(ratios)):
        trigseq = make_trigger_sequence(ratios_commondiv[i,:,:2])
        acorr = autocorr_bitwise(trigseq)
        autocorr_scores.append(np.max(acorr)**2)
    t2 = time.perf_counter(), time.process_time()
    print('\nTime spent on autocorr with timeseries length {}:'.format(len(example_rhythm)))
    print('    RT: {} seconds'.format(t2[0]-t1[0]))
    print('    CPU: {} seconds'.format(t2[1]-t1[1]))

    benni_weight = 0.2
    nd_sum_weight = 0.5
    ratio_dev_weight = 1
    ratio_dev_abs_max_weight = 1
    grid_dev_weight = 0.0
    evidence_weight = 1
    autocorr_weight = 0.5
    scores = normalize_and_add_scores(
        [benedetti_height, nd_add, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, evidence_scores, autocorr_scores], 
        [benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight],
        [0, 0, 0, 0, 0, 1, 1])
    t3 = time.perf_counter(), time.process_time()
    print('\nTime spent on scores with timeseries length {}:'.format(len(example_rhythm)))
    print('    RT: {} seconds'.format(t3[0]-t2[0]))
    print('    CPU: {} seconds'.format(t3[1]-t2[1]))
    print('\n***\n')
    print('\nTime spent processing with timeseries length {}:'.format(len(example_rhythm)))
    print('    RT: {} seconds'.format(t3[0]-t0[0]))
    print('    CPU: {} seconds'.format(t3[1]-t0[1]))
        
    '''
    for i in range(len(ratios_commondiv)):
        print('INDX', i)
        print('ref_delta:', round(ratios_commondiv[i,0,-1],2), ' benni:',int(benedetti_height[i]), 
              ' nd:',round(nd_add[i],2), ' devsum', round(ratio_deviation_abs[i], 2), 
              ' devmax', round(ratio_deviation_abs_max[i], 2), ' g_dev:', round(gridsize_deviations[i],2),
              ' evidence', evidence_scores[i], 'acorr_max', autocorr_scores[i])
        print('num, denom, dev, delta:')
        print(np.array_str(ratios_commondiv[i,:,:-1], precision=3, suppress_small=True))
    '''
    print('\nscores:: \n', [round(d,2) for d in scores])
    print('\nindices: \n', np.argsort(scores))
    #print('example_rhythm', example_rhythm)
    '''
    for i in np.argsort(scores)[:4]:
        print('INDX', i)
        print('ref_delta:', round(ratios_commondiv[i,0,-1],2), ' benni:',int(benedetti_height[i]), 
              ' nd:',round(nd_add[i],2), ' devsum', round(ratio_deviation_abs[i], 2), 
              ' devmax', round(ratio_deviation_abs_max[i], 2), ' g_dev:', round(gridsize_deviations[i],2),
              ' evidence', evidence_scores[i], 'acorr_max', autocorr_scores[i])
        print('num, denom, dev, delta:')
        print(np.array_str(ratios_commondiv[i,:,:-1], precision=3, suppress_small=True))
    '''
    print('**************************************')
    '''print(ratios_commondiv[33])
    print(ratios_commondiv[34])
    print(ratios_commondiv[34,:,0].astype(int))'''
    ratios_reduced = simplify_ratios(ratios_commondiv)
    
    print(len(ratios))
    duplicates = find_duplicate_representations(ratios_reduced)
    print(duplicates)
    print(scores)
    ranked_unique_representations = get_ranked_unique_representations(duplicates, scores)
    print('ranked unique')
    print(ranked_unique_representations)   
    print('**** best unique')
    print(ratios_reduced[ranked_unique_representations[0]]) 
    print('**** second best unique')
    print(ratios_reduced[ranked_unique_representations[1]]) 
