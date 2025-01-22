#!/usr/bin/python
# -*- coding: latin-1 -*-

import numpy as np
np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)

def autocorr(data, offset):
    """Autocorrelation (non normalized), options to offset"""
    if offset == 'm':
      mean = np.mean(data)
      data = data-mean
    elif offset < 0:
      mean = np.mean(data)
      mean *= abs(offset)
      data = data-mean
    else:
      data = data*(1+offset)
      data -= offset
    mean = np.mean(data)
    print(mean)
    acorr = np.correlate(data, data, 'full')[len(data)-1:]
    sorted = np.argsort(acorr[1:])
    best = sorted[-1]+1
    second_best = sorted[-2]+1
    print(f'max corr at {best} and {second_best}')
    return acorr

def make_trigger_sequence(ratios):
    # make the trigger sequence 
    # 1=transient, 0 = space
    # e.g. for rhythm 6, 3, 3, 2, 2, 2, the sequence will be
    # [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    trigger_seq = []
    for num in ratios:
        trigger_seq.append(1)
        for i in range(num-1):
            trigger_seq.append(0)
    return np.array(trigger_seq)

autocorr(a1,0.7)

def indigestability2(n,e):
    "Barlow's indigestability measure"
    d = prime_factorization(n)
    b = 0
    for p in d.keys():
        b += (d[p]*((p-1)**e)/p)
    return b*2


'''def rational_approx(n):
    # faster rational approx
    fact = np.array([3,4])
    dev = np.zeros(2)
    res = [0,0]
    threshold = 0.208333
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
'''
'''
def rational_approx(n):
  # faster rational approx
  fact = np.array([3,4])
  dev = np.zeros(2)
  res = np.zeros(2)
  if n < 0.25:
    fact *= 2
  if n < 0.1:
    fact *= 2
  if n < 0.04:
    fact *= 2
  if n < 0.02:
    fact *= 2
  if n < 0.01:
    nom = 1
    denom = 64
  print(fact)
  else:
    for i in range(2):
      f = fact[i]
      r = n*f
      res[i] = r
      dev[i] = abs(round(r)-r)
    print(res, '\n', dev)
    nom = round(res[np.argmin(dev)])
    denom = fact[np.argmin(dev)] 
  return nom, denom

'''
rational_approx(0.2)

'''def fraction_approx(n):
  div_limit = 4
  f = Fraction(n).limit_denominator(div_limit)
  numerator, denom = f.numerator, f.denominator
  deviation = (n-(numerator/denom))
  return numerator, denom, deviation
  
def rational_approx(n):
  # faster rational approx
  fact = [3,4]#np.array([3,4])
  dev = np.zeros(2)
  res = [0,0]#np.zeros(2)
  if n < 0.25:
    fact *= 2
  if n < 0.1:
    fact *= 2
  if n < 0.04:
    fact *= 2
  if n < 0.02:
    fact *= 2
  if n < 0.01:
    num = 1
    denom = 64
  else:
    for i in range(2):
      f = fact[i]
      r = n*f
      res[i] = r
      dev[i] = abs(round(r)-r)
  num = round(res[np.argmin(dev)])
  denom = fact[np.argmin(dev)] 
  deviation = (n-(num/denom))
  gcd = np.gcd(num, denom)
  num /= gcd
  denom /= gcd
  return int(num), int(denom), deviation

def test_f(n):
  for i in range(10000):
    fraction_approx(n)

def test_r(n):
  for i in range(10000):
    rational_approx(n)

'''
'''
def rational_approx_old(n, maxdev):
  fact = np.array([3,4])
  dev = np.zeros(2)
  res = np.zeros(2)
  for i in range(2):
    f = fact[i]
    r = n*f
    res[i] = r
    dev[i] = abs(round(r)-r)
  print(res, '\n', dev)
  if np.min(dev) > maxdev:
    fact *= 2
    for i in range(2):
      f = fact[i]
      r = n*f
      res[i] = r
      dev[i] = abs(round(r)-r)
    print('div2', res, '\n', dev)
  denom = fact[np.argmin(dev)]
  nom = round(res[np.argmin(dev)])
  print(nom, denom)

history = [0,0,0,0]
def update_history(history,new_item):
  history = history[1:]+history[:1] #rotate
  history[-1] = new_item
  for i in range(len(history)-2): # not process the last (newest)
    if not history[i]:
      if history[i+1] > 0:
        history[i] = history[i+1]-1
  return history

for i in range(5):
  history = update_history(history,i)
  print(history)
history[2] = None
print(history)
for i in range(2):
  history = update_history(history,i+10)
  print(history)
'''

'''
# profiling tests
import cProfile

# rotate list vs array
l = [0,0,0,0]
a = np.zeros(4)

# fastest and simplest
def rotate_list(l, new):
  l[-1] = new
  return l[1:]+l[:1]

def insert_pop_list(l, new):
  l.insert(new,l.pop())
  return l

def roll_array(a, new):
  a[-1] = new
  return np.roll(a,-1)

num = 100000

def test_list():
  l = [0,0,0,0]
  for i in range(num):
    l=rotate_list(l,i)
  print(l)
  
def test_list_pop():
  l = [0,0,0,0]
  for i in range(num):
    l=insert_pop_list(l,i)
  print(l)

def test_array():
  a = np.zeros(4)
  for i in range(num):
    a=roll_array(a,i)
  print(a)

cProfile.run('test_list()')
cProfile.run('test_list_pop()')

'''
'''maxweights = 100
datasize = 100000
weights = np.ones(maxweights)
data = np.random.rand(datasize*maxweights)
data = np.reshape(data, (datasize, maxweights))
print(data[0][0])
current_datasize = 10000
current_weightsize = 10
d = data[:current_datasize,:current_weightsize]
print(data[0][0])
print(d[0][0])
w = weights[:current_weightsize]
def dot(a1, a2):
  p = np.dot(a1, a2)
  #print(p)
#cProfile.run('dot(data,weights)')
def allocate(datasize, maxweights):
  data = np.zeros(datasize*maxweights)
  data += 0.5
  data *= 3
  #data = np.reshape(data, (datasize, maxweights))
cProfile.run('allocate(datasize, maxweights)')
cProfile.run('dot(d,w)')
print(data[0][0])
print(d[0][0])
'''
'''
def multiply_array(a,scale):
  test = a*scale
def multiply_arrays(a):
  test = np.multiply(a,a)
def sum_arrays(a):
  test = np.add(a,a)
def array_normalize(a):
  test = a/np.sum(a)

cProfile.run('multiply_array(data,0.5)')
cProfile.run('multiply_arrays(data)')
cProfile.run('sum_arrays(data)')
cProfile.run('array_normalize(data)')
'''