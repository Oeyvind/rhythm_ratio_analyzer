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

def make_box_notation(dur_pattern):
    # 1=transient, 0 = space
    # e.g. for rhythm 6/6, 3/6, 3/6, 2/6, 2/6, 2/6, the sequence will be
    # [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    box_notation = []
    for num in dur_pattern.astype(int):
        box_notation.append(1)
        for i in range(num-1):
            box_notation.append(0)
    return box_notation

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
    t1 = make_trigger_sequence_dur_pattern(testdata)
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
      t1 = make_trigger_sequence_dur_pattern(testdata)
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
        t1 = make_trigger_sequence_dur_pattern(data)
        a1 = autocorr(t1)
        p1 = np.argsort(-a1[1:])[:int(len(a1)/4)]+1
        for j in range(len(p1)):
            n = p1[j]
            sum_barlow += indigestability_n(n) # correlation position
        data = np.roll(data,1)
    return sum_barlow

