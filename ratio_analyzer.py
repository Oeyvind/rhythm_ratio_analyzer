#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)
import math
#import time # for profiling
#import logging 
#logging.basicConfig(level=logging.DEBUG)

weights = [0, 1, 1, 0.3, 1, 0.2, 0.3, 1]
# weights for the scoring of ratio alternatives, in this order:
#barlow_weight
#benni_weight
#nd_sum_weight
#ratio_dev_weight
#ratio_dev_abs_max_weight
#grid_dev_weight
#evidence_weight
#autocorr_weight

def set_weights(w):
    global weights
    weights = w

def rational_approx(n, div_limit=4):
    # faster rational approx for 2 and 3 divisions
    if div_limit == 2:
        fact = np.array([2])
        threshold = 0.2501 # finer resolution with small n
    else:
        fact = np.array([3,4])
        threshold = 0.208333 # finer resolution with small n
    dev = np.zeros(2)
    res = [0,0]
    while n < threshold:
      fact *= 2
      threshold /= 2
      if threshold < 0.011:
          break
    if n < 0.01:
      num = 1
      denom = 64
    else:
      res = n*fact
      dev = np.abs(np.round(res)-res)
    num = round(res[np.argmin(dev)])
    denom = fact[np.argmin(dev)] 
    deviation = (n-(num/denom))
    gcd = np.gcd(num, denom)
    num /= gcd
    denom /= gcd
    return int(num), int(denom), deviation

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
            numerator, denom, deviation = rational_approx(ratio, div_limit)
            ratios[i,j] = [numerator, denom, deviation, delta, ref_delta]
    return ratios

def recalculate_deviation(ratios):
    ratios[:,:,2] = (ratios[:,:,3]/ratios[:,:,4])-(ratios[:,:,0]/ratios[:,:,1]) 
    return ratios

def ratio_scores(ratios, timeseries):
    "calculate scores for each set of ratios"
    ratio_deviations = []
    ratio_deviation_abs = []
    ratio_deviation_abs_max = []
    indigestabilities = []
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
        indig = 0
        for denom in ratios[i,:,1]:
            indig += indigestability_n(denom)
        indigestabilities.append(indig)
    return ratio_deviations, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, indigestabilities, benedetti_height, nd_add 


def prime_factorization(n):
    "prime factorization of `n` as a dictionary with p:multiplicity for each p."
    # nudged from https://scientific-python-101.readthedocs.io/python/exercises/prime_factorization.html
    prime_factors = {}
    i = 2
    while i**2 <= n:
        if n % i:
            i += 1
        else:
            n /= i
            try:
                prime_factors[i] += 1
            except KeyError:
                prime_factors[i] = 1
    if n > 1:
        try:
            prime_factors[n] += 1
        except KeyError:
            prime_factors[n] = 1
    return prime_factors

def indigestability_n(n):
    "Barlow's indigestability measure"
    d = prime_factorization(n)
    b = 0
    for p in d.keys():
        b += (d[p]*((p-1)**2)/p)
    return b*2

def suavitatis(n):
    "Euler's gradus suavitatis"
    d = prime_factorization(n)
    s = 0
    for p in d.keys():
        s += d[p]*(p-1)
    return s

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
    """Set all ratio suggestions to a common denominator, in the case of rhythm analysis usually 12 is the denominator"""
    d = ratios[:,:,1].astype(int)
    if commondiv == 'auto':
        d_ = np.unique(d)
        commondiv = math.lcm(*d_)
    f = commondiv/d[:,:]
    ratios[:,:,0] *= f
    ratios[:,:,1] *= f
    return ratios

def make_commondiv_ratios_single(ratio_sequence, commondiv='auto'):
    """Set all ratios in a suggestion to a common denominator"""
    d = ratio_sequence[:,1].astype(int)
    if commondiv == 'auto':
        d_ = np.unique(d)
        commondiv = math.lcm(*d_)
    f = commondiv/d[:]
    ratio_sequence[:,0] *= f
    ratio_sequence[:,1] *= f
    return ratio_sequence

def make_duration_pattern(ratio_sequence):
    """Duration pattern, counts how many of a common rhythmic subdiv"""
    ratio_sequence = make_commondiv_ratios_single(ratio_sequence)
    n = ratio_sequence[:,0]
    return n

def simplify_ratios(ratios):
    """Reduce ratios to lowest terms"""
    n = ratios[:,:,0].astype(int)
    d = ratios[:,:,1].astype(int)
    for i in range(len(n)):
        for j in range(len(n[0])):
            gcd = np.gcd(n[i,j],d[i,j])
            n[i,j] /= gcd
            d[i,j] /= gcd
    ratios[:,:,0] = n
    ratios[:,:,1] = d
    return ratios

def get_ranked_unique_representations(duplicates, scores):
    ranked_unique_representations = []
    already_included = []
    rankscores = []
    for i in np.argsort(scores):
        if i not in already_included:
            for d in range(len(duplicates)):
                if (i in duplicates[d]):
                    ranked_unique_representations.append(i)
                    already_included.extend(duplicates[d])
                    rankscores.append(scores[i])
                    duplicates.remove(duplicates[d])
                    break
    return ranked_unique_representations, rankscores

def normalize_numerators(ratios):
    n = ratios[:,:,0].astype(int)
    max_all = np.max(n)
    for i in range(len(n)):
        max_this = (np.max(n[i]))
        ratios[i,:,0] *= (max_all/max_this) # normalize and write back
        ratios[i,:,1] *= (max_all/max_this) # also normalize denominators 
    return ratios

def evidence(ratios):
    # check if any subarrays contain the same numerators (assuming we already have made common denominators)
    # give each subarray a score depending of how may other subarrays contain the same
    # usually run this with the output from normalize_numerators
    # invert the evidence scores when adding with other quality scores (as they rank low score as best)
    evidence_score = np.zeros((len(ratios)))
    for i in range(len(ratios)):
        n0 = ratios[i,:,0]#.astype(int)
        for j in range(len(ratios)):
            if i == j:
                continue
            n1 = ratios[j,:,0]#.astype(int)
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
        invert = np.zeros(len(weights))
    for i in range(len(scores)):
        smax = max(scores[i])
        smin = min(scores[i])
        if smax == smin:
            s = 1
        else:
            s = (np.array(scores[i])-smin)/(smax-smin)
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

def make_trigger_sequence_dur_pattern(dur_pattern):
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

def autocorr(data):
    """Autocorrelation (non normalized)"""
    mean = np.mean(data)
    data = data-mean
    return np.correlate(data, data, 'full')[len(data)-1:]

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

def tempo_sanitize(tempo, assumption=120, pulse_div=1):
    # Adjust tempo to be in sanitized range
    # Using 120 bpm as the mother of all tempos, the range must be from 2/3 to 4/3: 80-160
    mintempo = assumption*(2/3)
    maxtempo = assumption*(4/3)
    tempo_factor = pulse_div
    while (tempo*tempo_factor) > maxtempo:
        tempo_factor /= 2        
    while (tempo*tempo_factor) < mintempo:
        tempo_factor *= 2
    tempo *= tempo_factor
    return tempo, tempo_factor

def find_pulse(data, mode='coef'):
  # reduce 
  data = data/np.gcd.reduce(data)
  pulse_2 = 0
  pulse_3 = 0
  for i in range(4):
    testdata = data*(2**i)
    t1 = make_trigger_sequence_dur_pattern(testdata)
    a1 = autocorr(t1)
    p1 = np.argsort(-a1[1:])[:5]+1
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
  return pulse_div, certainty


def analyze(t, rank=1):
    """Do the full ratio analysis"""
    timedata = t.tolist()
    barlow_weight, benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight = weights # global weights
    #rat2 = ratio_to_each(timedata, div_limit=2)
    #rat4 = ratio_to_each(timedata, div_limit=4)
    #ratios = np.concatenate((rat2, rat4), axis=0)
    ratios = ratio_to_each(timedata, div_limit=4)
    ratio_deviations, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, barlow_indigest,benedetti_height, nd_add = ratio_scores(ratios,timedata)
    ratios_commondiv = make_commondiv_ratios(ratios)
    ratios_commondiv_copy = np.copy(ratios_commondiv)
    norm_num_ratios = normalize_numerators(ratios_commondiv_copy)
    evidence_scores = evidence(norm_num_ratios)
    autocorr_scores = []
    for i in range(len(ratios)):
        trigseq = make_trigger_sequence(ratios_commondiv[i,:,:2])
        acorr = autocorr(trigseq)
        autocorr_scores.append(np.max(acorr[1:])) # max of autocorr
    scores = normalize_and_add_scores(
        [barlow_indigest, benedetti_height, nd_add, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, evidence_scores, autocorr_scores], 
        [barlow_weight, benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight],
        [0, 0, 0, 0, 0, 0, 1, 1])
    
    # simplify ratios and remove duplicate ratio representations
    ratios_reduced = np.copy(ratios_commondiv)
    ratios_reduced = simplify_ratios(ratios_reduced)
    duplicates = find_duplicate_representations(ratios_reduced)
    ranked_unique_representations, rankscores = get_ranked_unique_representations(duplicates, scores)
    # isolate the selected (best) representation
    selected = ranked_unique_representations[rank-1] # select the unique representation ranked from the lowest score
    ticktempo_Hz = (1/ratios_commondiv[selected,0,-1])*ratios_commondiv[selected,0,1]
    #print('analyze: commondiv', ratios_commondiv[selected,0,1])
    #print(f'ticktempo \n{ratios_commondiv[selected]} \n {ticktempo_Hz}')
    #print((1/ratios_commondiv[selected,0,-1]), ratios_commondiv[selected,0,1])
    ticktempo_bpm = ticktempo_Hz*60
    trigseq = make_trigger_sequence(ratios_commondiv[selected,:,:2])
    acorr = autocorr(trigseq)
    pulseposition = np.argmax(acorr[1:])+1
    tempo_tendency = ratio_deviations[selected]*-1 # invert deviation to adjust tempo
    
    # return
    return ratios_reduced, ranked_unique_representations, rankscores, trigseq, ticktempo_bpm, tempo_tendency, pulseposition
        
if __name__ == '__main__':
    # example rhythms
    # rhythm is represented here by the time stamp of each event
    #t = [0.0, 0.3467, 0.524, 1.02, 1.546, 1.8553, 2.088, 2.362, 2.6053, 2.8713, 3.1333, 3.62, 3.962, 4.176,]    
    # test 2 jazzphrase
    #t = [0.    , 0.302 , 0.5406, 0.8426, 1.3613, 1.5746, 1.8673, 2.0813, 2.58  , 2.9286, 3.1213]
    # skalert for å matche til 3.0
    #t = [0.    , 0.2903, 0.5196, 0.8099, 1.3084, 1.5134, 1.7947, 2.0004, 2.4797, 2.8148, 3.    ] 
    # ideell
    t = [0,    0.25,     0.5,    0.75,   1.25,   1.5,    1.75,   2,      2.5,    2.75,   3]
    # manuell slark
    #t = [0,    0.3,      0.5,    0.8,    1.3,    1.5,    1.8,    2,      2.5,    2.8,   3]
    #t = [ 6.69,  7.19,  7.44,  7.69,  8.19,  8.52,  8.69,  9.19,  9.44,  9.69, 10.19]
    t = np.array(t,dtype=np.float32)
    barlow_weight = 1
    benni_weight = 1
    nd_sum_weight = 1
    ratio_dev_weight = 0.3
    ratio_dev_abs_max_weight = 1
    grid_dev_weight = 0.2
    evidence_weight = 0.3
    autocorr_weight = 1
    weights = [barlow_weight, benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight]
    set_weights(weights)
    rank = 1
    ratios_reduced, ranked_unique_representations, rankscores, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = analyze(t, rank)
    best = ranked_unique_representations[0]
    ratios_list = ratios_reduced[best].tolist()
    for i in range(len(ratios_list)):
        print(ratios_list[i])
    #print(ratios_reduced[selected,:,:3]) #nom, denom, deviation
    #print(ratios_reduced[selected,0,0], type(ratios_reduced[selected,0,0]))
   