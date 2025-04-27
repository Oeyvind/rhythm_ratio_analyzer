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
simplify = True

def set_precision(precision):
    global weights
    complexity = precision
    deviation = 1-precision
    weights = [complexity, deviation]

def set_simplify(truefalse):
    global simplify
    simplify = truefalse

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

def get_dur_pattern_deviations(dur_pattern, t, tempo):
    # Find the deviations by
    # 1. construct quantized time from tempo and dur pattern
    # 2. find deviation for each dur in dur pattern (as fraction of the delta time)
    # OPT: use dur+deviation to try to reconstruct t from t_quantized
    step_size = 60/tempo
    t_quantized = [t[0]]
    for i in range(1, len(dur_pattern)+1):
        t_quantized.append(t_quantized[i-1]+(dur_pattern[i-1]*step_size))
    t_dev = t-t_quantized
    dur_dev = (t_dev[1:]/np.diff(t_quantized)) #* (0.5/step_size)
    #test = [0]
    #for i in range(len(dur_pattern)):
    #    test.append((t_quantized[i+1])+(np.diff(t_quantized)[i]*dur_dev[i]))
    #print('test', test)
    return dur_dev

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
    #indigest = 0
    for n in d:
        suavit += suavitatis(n)
        #indigest += indigestability(n)
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

def dur_pattern_suggestions(t, div_limit=4):
    # Analyze time sequence, find possible duration patttern representations 
    # Calculate tempo and deviations for each dur pattern
    timedata = t.tolist()
    ratios = ratio_to_each(timedata, div_limit=div_limit)
    duration_patterns = []
    deviations = []
    tempi = []
    for i in range(len(ratios)):
        dur_pattern = make_duration_pattern(ratios[i]).astype('int').tolist()
        if dur_pattern not in duration_patterns: 
            tempo = fit_tempo_from_dur_pattern(dur_pattern,t)
            #if tempo < 1000: # pulse tempo over this threshold is probably an error
            duration_patterns.append(dur_pattern)
            tempi.append(tempo)
            dev = get_dur_pattern_deviations(dur_pattern,t,tempo)
            deviations.append(dev)
            if simplify:
                d2 = simplify_dur_pattern(dur_pattern,dev)
                if (d2 not in duration_patterns) and ((np.array(d2)/2).astype('int').tolist() not in duration_patterns): 
                    tempo = fit_tempo_from_dur_pattern(d2,t)
                    #if tempo < 1000: # pulse tempo over this threshold is probably an error
                    duration_patterns.append(d2)
                    tempi.append(tempo)
                    dev = fit_dur_pattern_deviations(d2,t,tempo)
                    deviations.append(dev)
    return duration_patterns, deviations, tempi

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

def analyze(t, div_limit=4):
    """Analysis of time sequence, resulting in a duration pattern with tempo estimation"""
    duration_patterns, deviations, tempi = dur_pattern_suggestions(t)
    devsums = []
    for dev in deviations:
        devsum = np.sum(np.abs(dev))
        devsums.append(devsum)
    scores = evaluate(duration_patterns, devsums, weights)
    best = np.argsort(scores)[0]
    best_dur_pattern = duration_patterns[best]
    trigger_seq = make_box_notation(best_dur_pattern)
    pulse, pulsepos = indispensability_subdiv(trigger_seq)
    return best, pulse, pulsepos, duration_patterns, deviations, scores, tempi

# testing functions

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

def print_analysis(analysis):
    best, pulse, pulsepos, duration_patterns, deviations, scores, tempi = analysis
    print('pulse, pulsepos', pulse, pulsepos)
    for i in np.argsort(scores):
        print(f'{i}, dur_pat {duration_patterns[i]} score {scores[i]:.2f}, tempo: {tempi[i]:.2f} \n  dev: {deviations[i]} ')

def test_timedata(t, printit=True):
    print(f'\ntesting analysis of timedata. Simplify={simplify}')
    analysis = analyze(t)
    if printit: 
        print('t:', t)
        print_analysis(analysis)
    return analysis
    
def test_timedatas(t, printit=True):
    numpatterns = len(t)
    print(f'\ntesting analysis of {numpatterns} timedata series. Simplify={simplify}')
    analyses = []
    for i in range(numpatterns):
        analysis = analyze(t[i])
        if printit:
            print(f'timedata {i} \n{t[i]}') 
            print_analysis(analysis)
        analyses.append(analysis)
    return analyses
        
def test_pattern(d, subdiv_bpm=120, r_deviation=0, printit=True):
    # analyze one pattern
    print(f'\ntesting analysis of one pattern. Simplify={simplify}')
    t = make_time_from_dur(d, r_deviation, subdiv_bpm)
    analysis = analyze(t)
    if printit: 
        print('dur pattern:', d)
        print('t:', t)
        print_analysis(analysis)
    return analysis

def test_patterns(durs, subdiv_bpm=120, r_deviation=0, printit=True):
    # analyze several patterns
    numpatterns = len(durs)
    print(f'\ntesting analysis of {numpatterns} patterns. Simplify={simplify}')
    start_time = 0
    analyses = []
    for i in range(numpatterns):
        t = make_time_from_dur(durs[i], r_deviation, subdiv_bpm, start_time=start_time)
        start_time = t[-1]
        analysis = analyze(t)
        analyses.append(analysis)
        if printit: 
            print(f'dur pattern {i} \n{durs[i]}') 
            print('t:', t)
            print_analysis(analysis)
    return analyses

def reconcile_tempi(tempi1,tempi2, tolerance=0.1):
    # Compare arrays of tempi, try to find compatible tempo combinations
    # Compatible means they are almost equal (within tolerance limit)
    # If they can become compatible by integer multiplication (e.g. 120bpm and 240bpm),
    # save the factor needed to reconcile them.
    # Allow only multipliers [2,3], as these can represent reconcilable tempo ratios
    # The non-redundant tempo factors are then [1,1],[1,2],[1,3],[2,1],[2,3],[3,1],[3,2]
    tempo_factors = [[1,1],[1,2],[1,3],[2,1],[2,3],[3,1],[3,2]]
    reconcile_combos = []
    for tf in tempo_factors:
        for i in range(len(tempi1)):
            tmp = tempi1[i]*tf[0]
            near_match = np.isclose(tempi2*tf[1], tmp, tolerance) 
            for j in range(len(near_match)):
                if near_match[j]:
                    reconcile_combos.append([[i,j],tf])
    # return indices for reconcilable tempi, and the factors needed for reconciliation
    return reconcile_combos

#tempi1 = np.array([236,884])
#tempi2 = np.array([237,920,3107])
tempi1 = np.array([60,180])
tempi2 = np.array([120,240])
print(reconcile_tempi(tempi1,tempi2))

def reconciliation(analyses):
    # When analyzing two or more consecutive rhythm patterns
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
    print('analysis reconciliation')
    best1 = analyses[0][0]
    best2 = analyses[1][0]
    tempi1 = analyses[0][6]
    tempi2 = analyses[1][6]
    tempo_tolerance = 0.1
    reconciled = False
    if (tempi1[best1] < tempi2[best2]*(1-tempo_tolerance)) \
        or (tempi1[best1] > tempi2[best2]*(1+tempo_tolerance)):
        print('not matching:', tempi1[best1], tempi2[best2])
    else:
        print('reconciled')
        reconciled = True
        #print(analyses[i])
        print('durations:', analyses[0][3][best1], analyses[1][3][best2])
    alternative_bests = []
    if not reconciled:
        for i in range(len(tempi1)):
            tmp = tempi1[i]
            near_match = np.isclose(tempi2,tmp, tempo_tolerance) 
            if np.sum(near_match) > 0:
                for j in range(len(near_match)):
                    if near_match[j]:
                        alternative_bests.append([i,j])
        for i in range(len(tempi2)):
            tmp = tempi2[i]
            near_match = np.isclose(tempi1,tmp, tempo_tolerance) 
            if np.sum(near_match) > 0:
                for j in range(len(near_match)):
                    if near_match[j]:
                        if [j,i] not in alternative_bests:
                            alternative_bests.append([j,i])
        print('alternative_bests', alternative_bests)
        alt_best_score = 99
        for combo in alternative_bests:
            score_sum = analyses[0][5][combo[0]]+analyses[1][5][combo[1]]
            print('alt combo scores', combo, score_sum)
            if score_sum < alt_best_score:
                alt_best = combo
                alt_best_score = score_sum
    if len(alternative_bests) == 0:
        print('** ** CAN NOT BE RECONCILED')
    else:
        print('reconciled combo:', combo)
        selected_durations = [analyses[0][3][combo[0]], analyses[1][3][combo[1]]]
        print('reconciled durations:', selected_durations)
        print('input durations', durs)
        if np.array_equal(durs[0],selected_durations[0]) and np.array_equal(durs[1],selected_durations[1]):
            reconciled = True
    print('match found =', reconciled)
    return reconciled


if __name__ == '__main__':
    set_precision(0.5) # balance betwseen deviation and complexity
    set_simplify(False)
    d=[2,1,1,2]
    #d=[6,3,3,6,4,2,6,3,3,6]
    #d=[6,3,3,4,4,4]
    #test_pattern(d, r_deviation=0.1, subdiv_bpm=240)
    
    durs = [[2,1,1,2],[1,1,2,2]]
    durs = [[3,3,4,3,3],[1,1,2,2]]
    #analyses = test_patterns(durs, r_deviation=0.1, subdiv_bpm=240)
    #reconciliation(analyses)
    
    #num_test = 1
    #num_success = 0
    #for i in range(num_test):
    #    success = test_two_patterns(durs, r_deviation=0.1, subdiv_bpm=240)
    #    num_success += success
    #print('num test', num_test, 'num_success', num_success)

    #timedata = np.array([0. , 0.485, 0.735, 0.994, 1.496])
    #test_timedata(timedata)

    # analyze two time series (consecutive, where the last in the first timeseries = the first in the second)
    #timedata1 = np.array([0., 0.734, 1.512, 2.497, 3.256, 4.025])
    #timedata2 = np.array([4.025, 4.252, 4.5, 5.009, 5.54 ])
    #t = [timedata1,timedata2]
    #test_timedatas(t,2)

