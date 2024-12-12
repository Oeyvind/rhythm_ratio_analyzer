#!/usr/bin/python
# -*- coding: latin-1 -*-

# Test using arrays to hold collections of alternatives for next event.
# e.g. for a markov lookup, we might use the previous event *data value* as the *key*,
# ... and then get an array of indices as the *value* for that *key*.
# The array would hold a 1 for each index that is a possible data point for the next event.
# This would allow several markov lookups to be efficiently collated, e.g. summing two such arrays.

# Thing to test:
# - use an array of values as the probability distribution for numpy.random.choice
# - how expensive is it (profiling) to multiply a large 1D array with a scalar? (in order to weigh the different sets of possibilities)
#    - 0.02 secs (20 millisecs) to multiply an array of size 10 million
# - should we instead just sum several times (e.g. only have integer weights possible)
#    - same as multiplication, no gain
# - can we efficiently create a "mask" from data values? e.g. put a '1' for each time we have a specific value in the data?
#    - for example, find all occurences of 0.25 (in the case we need that value to synchronize the rhythm to the next downbeat)
# - profiling of masking an array of size 10 million, extracting matching values (within tolerance)
#    - 0.1 seconds to mask an array and output result, 0.07 for just the masking operation (0.02 for the multiplication)
#    - using np.ma.array(data, mask=mask) seems much faster than multiplication (maybe twice as fast)
# - if we have such "index-masks" and "value-masks" it would be quite efficient to collate severel different "probability-sets" into one probability distribution

import numpy as np

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