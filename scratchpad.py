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


# use an array of values as the probability distribution for random.choice
data = np.asarray([0.25,0.25,0.5,1,2,3,4])
indexmask = np.asarray([0,0,1,0,1,0,0])
indexmask_norm = indexmask/np.sum(indexmask)
next = np.random.choice(data,p=indexmask_norm)
print(next)

mask_1 = np.ma.masked_equal(data, 0.5)
mask_2 = np.ma.masked_equal(data, 3)
mask = np.ma.getmask(mask_1)+np.ma.getmask(mask_2)
masked = data * mask
print(mask, np.ma.array(data, mask=mask))
#mask_bool = np.ma.make_mask(mask_eq)
#print(mask_bool)

# profiling tests
import cProfile
datasize = 10000000
data = np.random.rand(datasize)
def mask_array(a,v1,v2):
  mask = np.ma.masked_values(a, v1, rtol=0.000001, atol=0.000001)
  masked = np.ma.array(data, mask=mask)
  #masked = a * mask
  #print(np.sum(a), np.sum(masked))
cProfile.run('mask_array(data,0.5,0.6)')

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