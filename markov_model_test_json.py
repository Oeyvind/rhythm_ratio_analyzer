#!/usr/bin/python
# -*- coding: latin-1 -*-

import markov_model as mm
import numpy as np
np.set_printoptions(suppress=True)

import json
# test
if __name__ == '__main__' :
    with open('testdata_rhythm.json', 'r') as filehandle:
      jsondict = json.load(filehandle)
    datasize = len(jsondict['0']['ratios'])
    data = np.empty((2,datasize),dtype='float')
    for i in range(len(jsondict['0']['ratios'])):
       ratio_float1 = jsondict['0']['ratios'][i][0]/jsondict['0']['ratios'][i][1]
       ratio_float2 = jsondict['1']['ratios'][i][0]/jsondict['1']['ratios'][i][1]
       data[0,i] = ratio_float1
       data[1,i] = ratio_float2
    print(data)
    #analyze variable markov order in 2 dimensions
    m_1ord, m_1ord_2D, m_2ord, m_2ord_2D = mm.analyze_vmo_vdim(data, datasize)
    models = (m_1ord, m_1ord_2D, m_2ord, m_2ord_2D)
    #generate
    indices = np.arange(datasize)
    order = 2
    dimensions = 2
    coefs = (order, dimensions)
    start_index = np.random.choice(indices)
    next_item_1ord = data[0][start_index]
    print(f'The first item is {next_item_1ord} at index {start_index}')
    next_item_1ord_2D = None
    next_item_2ord = None
    next_item_2ord_2D = None
    m_query = [0, next_item_1ord, next_item_1ord_2D, next_item_2ord, next_item_2ord_2D]
    i = 0
    while i < 50:
        m_query = mm.generate_vmo_vdim(models, m_query, coefs, indices, data) #query markov models for next event and update query for next iteration
        next_item_index = m_query[0]
        print(f'the next item is  {data[0][next_item_index]} at index {next_item_index}')
        i += 1
    print(f'generated {i} items')
