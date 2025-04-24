#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)
import math
import random

weights = [0.5, 0.5]
# weights for the scoring of ratio alternatives, in this order:
# dur_pattern height (complexity)
# deviation

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
    if div_limit == 8 : 
      fact *= 2
      threshold /= 2
    if div_limit == 16 : 
      fact *= 4
      threshold /= 4
    dev = np.zeros(2)
    res = [0,0]
    while n < threshold:
      fact *= 2
      threshold /= 2
      if threshold < 0.011:
          break
    if n < (1/64):
      num = 1
      denom = 64
    else:
      res = n*fact
      dev = np.abs(np.round(res)-res)*(1/fact)# also adjust deviation according to the factor in question
      num = round(res[np.argmin(dev)])
      denom = fact[np.argmin(dev)]
    gcd = np.gcd(num, denom)
    num /= gcd
    denom /= gcd
    deviation = (n-(num/denom)) 
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
            ref_deltas.append(timeseries[i+2]-timeseries[i]) # then also include delta for next neighbour event
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

def fit_dur_pattern_to_time(t,dur_pattern):
    # Fit a dur pattern to the available time span from the first to the last event in a time sequence
    time_span = t[-1] - t[0]
    num_steps = np.sum(dur_pattern)
    step_size = time_span/num_steps
    t_quantized = [t[0]]
    for i in range(1, len(dur_pattern)+1):
        t_quantized.append(t_quantized[i-1]+(dur_pattern[i-1]*step_size))
    return np.array(t_quantized)

def dur_pattern_deviations(dur_pattern,t):
    time_span = t[-1] - t[0]
    num_steps = np.sum(dur_pattern)
    step_size = time_span/num_steps
    t_quantized = [t[0]]
    for i in range(1, len(dur_pattern)+1):
        t_quantized.append(t_quantized[i-1]+(dur_pattern[i-1]*step_size))
    deviation_diff = (np.diff(t)-np.diff(t_quantized))/np.diff(t_quantized)
    return deviation_diff

def get_deviation_polarity(deviations, threshold):
    # for each deviation, give a -1, 0, or 1 polarity
    # depending on the sign, but keep a range close to zero as 0 polarity
    pos = np.greater(deviations, threshold)*1
    neg = np.less(deviations, -threshold)*-1
    deviations_polarity = pos+neg
    return deviations_polarity

def simplify_dur_pattern(dur_pattern, deviation):
    # This can be used to correct for duration patterns containing odd combinations of durations
    # For example when triplets and 8th notes are mixed within the same sequence
    # divide by 2 and use deviation polarity for rounding
    dur_pattern_2 = np.copy(dur_pattern)
    if np.min(dur_pattern) > 1:
        dur_pattern_2 = dur_pattern_2 / 2
        pos = np.greater(deviation, 0.0001)*.1
        neg = np.less(deviation, -0.0001)*-.1
        deviations_polarity = pos+neg
        dur_pattern_2 += deviations_polarity
        dur_pattern_2 = np.round(dur_pattern_2)
    return np.round(dur_pattern_2).astype('int').tolist()

def make_box_notation(dur_pattern):
    # 1=transient, 0 = space
    # e.g. for rhythm 6/6, 3/6, 3/6, 2/6, 2/6, 2/6, the sequence will be
    # [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    box_notation = []
    for num in dur_pattern:
        box_notation.append(1)
        for i in range(num-1):
            box_notation.append(0)
    box_notation.append(1) # add a last 1 as terminator after last duration
    return box_notation

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

def indigestability(n):
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

def dur_pattern_height(d):
    # Complexity measure of the duration pattern
    # A simple sum of durations will give too much difference (e.g. 8 relative to 4)
    # Consider Euler suavitatis or Barlow indigestability
    # Might also consider tesselation (combination of durations)
    s = np.sum(d)
    suavit = 0
    indigest = 0
    for n in d:
        suavit += suavitatis(n)
        indigest += indigestability(n)
    test = suavit**0.3
    return suavit

def evaluate(duration_patterns, deviations, weights):
    # Evaluate the fitness of a set of suggested dur patterns,
    # considering dur pattern complexity and deviation
    # and the resulting deviations from the original time sequence
    heights = []
    for d in duration_patterns:
        height = dur_pattern_height(d)
        heights.append(height)
    scoresum = normalize_and_add_scores([deviations, heights], weights)
    return scoresum

def find_pulse_tempo(dur_pattern, t):
    # from dur_pattern, find pulse and tempo,
    # in relation to the available time span from the first to the last event in the original time sequence
    subdiv_tempo = (t[-1]-t[0])/np.sum(dur_pattern)
    subdiv_bpm = 60/subdiv_tempo
    return subdiv_bpm

def make_time_from_dur(dur_pattern,maxdev, subdiv_bpm=120, start_time=0):
    # make timestamp sequence from duration pattern
    # to reconstruct time sequence from proposed duration pattern,
    # or for generating time sequences for testing
    timestamp = [start_time]
    temposcaler = 60/subdiv_bpm
    t = start_time
    for d in dur_pattern:
        dev = (random.random()-0.5)*2*maxdev*temposcaler
        t += d*temposcaler
        timestamp.append(t+dev)
    return np.array(timestamp)

def dur_pattern_suggestions(t, div_limit=4, simplify=True):
    # Analysize time sequence, find possible duration patttern representations 
    timedata = t.tolist()
    ratios = ratio_to_each(timedata, div_limit=div_limit)
    duration_patterns = []
    for i in range(len(ratios)):
        dur_pattern = make_duration_pattern(ratios[i]).astype('int').tolist()
        if dur_pattern not in duration_patterns: 
            duration_patterns.append(dur_pattern)
            dev = dur_pattern_deviations(dur_pattern,t)
            if simplify:
                d2 = simplify_dur_pattern(dur_pattern,dev)
                if d2 not in duration_patterns: duration_patterns.append(d2)
    return duration_patterns

def indispensability_subdiv(trigger_seq):
    # Find pattern subdivision based on indispensability (Barlow)
    indis_2 = np.array([1,0])    
    indis_3 = np.array([2,0,1])
    indis_3 = (indis_3/np.max(indis_3))

    # all indispensabilities
    indis_all = [indis_3, indis_2] # list in increasing order of preference
    for i in range(len(indis_all)): # tile until long enough
        indis_all[i] = np.tile(indis_all[i], int(np.ceil(len(trigger_seq)/len(indis_all[i]))+1))

    # score table for the different indispensabilities
    indis_scores = np.array([[3, 0., 0., 0], # format: length, max_score, confidence (max/min score), rotation for best score
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
    #print(indis_scores)
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

def analyze(t, div_limit=4, simplify=True):
    """Analysis of time sequence, resulting in a duration pattern with tempo estimation"""
    duration_patterns = dur_pattern_suggestions(t, simplify=simplify)
    deviations = []
    devsums = []
    for d in duration_patterns:
        dev = dur_pattern_deviations(d,t)
        deviations.append(dev)
        devsum = np.sum(np.abs(dev))
        devsums.append(devsum)
    scores = evaluate(duration_patterns, devsums, weights)
    tempi = []
    for i in range(len(scores)):
        tempo = find_pulse_tempo(duration_patterns[i], t)
        tempi.append(tempo)
    best = np.argsort(scores)[0]
    return best, duration_patterns, deviations, scores, tempi

def test_timedata(t,simplify=True):
    print(f'\ntesting analysis of timedata. Simplify={simplify}')
    print('t:', t)
    best, duration_patterns, deviations, scores, tempi = analyze(t,simplify=simplify)
    for i in np.argsort(scores):
        print(f'{i}, dur_pat {duration_patterns[i]} score {scores[i]:.2f}, tempo: {tempi[i]:.2f} \n  dev: {deviations[i]} ')

def test_one_pattern(d, subdiv_bpm=120, r_deviation=0, simplify=True):
    # analyze one pattern
    print(f'\ntesting analysis of one pattern. Simplify={simplify}')
    print('dur pattern:', d)
    t = make_time_from_dur(d, r_deviation, subdiv_bpm)
    print('t:', t)
    best, duration_patterns, deviations, scores, tempi = analyze(t,simplify=simplify)
    for i in np.argsort(scores):
        print(f'{i}, dur_pat {duration_patterns[i]} score {scores[i]:.2f}, tempo: {tempi[i]:.2f} \n  dev: {deviations[i]} ')

def test_two_patterns(durs, subdiv_bpm=120, r_deviation=0, simplify=True):
    print(f'\ntesting analysis of two consecutive patterns. Simplify={simplify}')
    # analyze two consecutive rhythm patterns
    # try to reconcile the interpretation of the two patterns
    # allow re-interpretation of the first in light of evidence from the second
    # also allow interpretation of the second in light of eveidence from the first
    # Use tempo as a reconciliation measure, try to find an interpretation where the two tempi match within a threshold (e.g. 10%)
    # So:
    # Take the best tempo from the first phrase analysis, look for matching tempi in the analysis of the second phrase
    # Also take the first tempo from the second phrase analysis, and look for matching tempi in the analysis of the first phrase
    # Case to solve: if no match can be found (does it indicate a tempo change in the input?)
    #   - if this indicates a tempo change, we must break down the phrases to find the exact point of change
    # Case to solve: if several matches can be found (take the best sum of scores?)
    start_time = 0
    pattern_num = 0
    for d in durs:
        print('* dur pattern', pattern_num+1, durs[pattern_num])
        pattern_num += 1
        t = make_time_from_dur(d, r_deviation, subdiv_bpm, start_time=start_time)
        print('t:', t)
        start_time = t[-1]
        best, duration_patterns, deviations, scores, tempi = analyze(t,simplify=simplify)
        for i in np.argsort(scores):
            print(f'{i}, {duration_patterns[i]} {scores[i]:.2f}, tempo: {tempi[i]:.2f} \n  dev: {deviations[i]} ')


if __name__ == '__main__':
    set_weights([1,1]) # dev, height
    #d=[2,1,1,2]
    #d=[6,3,3,6,4,2,6,3,3,6]
    #d=[6,3,3,4,4,4]
    #test_one_pattern(subdiv_bpm=720)
    #durs = [[2,1,1,2],[1,1,2,2]]
    #durs = [[3,3,4,3,3],[1,1,2,2]]
    #test_two_patterns(durs)
    
    timedata = np.array([0, 1.,  1.5, 2, 2.7,  3])
    timedata = np.array([0, 1.,  2.05,  3, 4])
    #test_timedata(timedata, simplify=False)
