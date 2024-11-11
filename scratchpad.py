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

# profiling tests
import cProfile
maxweights = 100
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