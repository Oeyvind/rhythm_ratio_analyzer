#!/usr/bin/python
# -*- coding: latin-1 -*-

# Backup of some possibly useful functions taken out of ratio analyzer during simplification
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)

def deviation_scaler(n, num,denom):
    # scale the deviation from the rational approx according to available deviation range between ratios
    nf, ni = np.modf(n)
    if denom == 1: dev_range = [1/4, 1/4]
    if denom == 2: dev_range = [1/6, 1/6]
    if nf >= 0.5:
        if denom == 3: dev_range = [1/6, 1/12]
        if denom == 4: dev_range = [1/12, 1/4]
    if nf < 0.5:
        if denom == 3: dev_range = [1/12, 1/6]
        if ni == 0:
            if denom == 4: dev_range = [1/12, 1/12]
        else:
            if denom == 4: dev_range = [1/4, 1/12]
        if denom == 6: dev_range = [1/24, 1/12]
        if denom == 8: dev_range = [1/24, 1/24]
        if denom == 12: dev_range = [1/48, 1/24]
        if denom == 16: dev_range = [1/48, 1/48]
        if denom == 24: dev_range = [1/96, 1/48]
        if denom > 24: dev_range = [1/96, 1/96]
    dev = (n-(num/denom)) 
    if dev < 0:
        dev /= dev_range[0]
    else: 
        dev /= dev_range[1]
    return dev 

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


def autocorr(data):
    """Autocorrelation (non normalized)"""
    mean = np.mean(data) #HERE BE DRAGONS, mean will make a trigger seq for the same rhythm in twice the tempo different(!)
    data = data-mean
    return np.correlate(data, data, 'full')[len(data)-1:]

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

def find_pulse(data, mode='coef', oversample=1):
  # reduce 
  data = data/np.gcd.reduce(data)
  pulse_2 = 0
  pulse_3 = 0
  for i in range(oversample):
    testdata = data*(2**i)
    t1 = make_box_notation(testdata)
    a1 = autocorr(t1)
    #p1 = np.argsort(-a1[1:])[:6]+1
    p1 = np.argsort(-a1[1:])[:int(len(a1)/4)]+1
    #print(p1)
    for j in range(len(p1)):
      n = p1[j]
      if a1[p1[j]] > 0:
        if mode == 'coef': 
            coef = a1[p1[j]] # correlation coefficient
            #print(n,coef)
        else: 
            coef = 1/(j+1) # gradually decreasing with order
            #print(n,coef)
        if n <= 32:
          if n%3==0: pulse_3 += coef
          elif n%2==0: pulse_2 += coef
    #print('pulse 2, 3:', pulse_2, pulse_3)
  if pulse_2+pulse_3 > 0:
      certainty = pulse_2/(pulse_2+pulse_3)
  else: certainty = 0.5
  if certainty >= 0.5: 
    pulse_div = 2
  else: 
    pulse_div = 3
    certainty = 1-certainty 
  return pulse_div, certainty

def find_pulse2(data, mode='coef', oversample=1, rotate=True):
  # reduce 
  data = data/np.gcd.reduce(data)
  pulse_2 = 0
  pulse_3 = 0
  if rotate: rotations = len(data)
  else: rotations = 1 
  for k in range(rotations):
    for i in range(oversample):
      testdata = data*(2**i)
      t1 = make_box_notation(testdata)
      a1 = autocorr(t1)
      #print(a1)
      p1 = np.argsort(-a1[1:])[:6]+1
      #p1 = np.argsort(-a1[1:])[:int(len(a1)/4)]+1
      #print('p1', p1)
      for j in range(len(p1)):
        n = p1[j]
        if mode == 'coef': 
          if a1[p1[j]] > 0:
            coef = a1[p1[j]] # correlation coefficient
            #print(n,coef)
        else: 
          coef = 1/(j+1) # gradually decreasing with order
        if n <= 32:
          if n%3==0: pulse_3 += coef
          elif n%2==0: pulse_2 += coef
      #print('k, data', k, data)
      #print('pulse 2, 3:', pulse_2, pulse_3)
      data = np.roll(data,1)
  if pulse_2+pulse_3 > 0:
      certainty = pulse_2/(pulse_2+pulse_3)
  else: certainty = 0.5
  if certainty >= 0.5: 
    pulse_div = 2
  else: 
    pulse_div = 3
    certainty = 1-certainty 
  return pulse_div, certainty

def autocorr_complexity(data):
    # sort the correlation coefficients, take only the best 1/4 of them, 
    # look at the digestability for the correlation indices
    data = data/np.gcd.reduce(data) # reduce to lowest terms
    sum_barlow = 0
    for i in range(len(data)):
        t1 = make_box_notation(data)
        a1 = autocorr(t1)
        p1 = np.argsort(-a1[1:])[:int(len(a1)/4)]+1
        for j in range(len(p1)):
            n = p1[j]
            sum_barlow += indigestability_n(n) # correlation position
        data = np.roll(data,1)
    return sum_barlow

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
#print(d)
#trigger_seq = make_box_notation(d)
#subdiv, position = indispensability_subdiv(trigger_seq)
#print('subdiv', subdiv, 'position', position)

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
