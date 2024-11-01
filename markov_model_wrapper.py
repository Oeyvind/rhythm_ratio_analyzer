#!/usr/bin/python
# -*- coding: latin-1 -*-

import markov_model as mm
import numpy as np
np.set_printoptions(suppress=True)

def analyze(data):
    datasize = np.shape(data)[1]
    m_1ord, m_1ord_2D = mm.analyze_vmo_vdim(data, datasize)
    models = (m_1ord, m_1ord_2D)
    return models

def generate(order, dimensions, models, indices, data, m_query=[0, None, None, None]):
    coefs = (order, dimensions)
    if not m_query[2]:
      start_index = np.random.choice(indices)
      next_item_1ord = data[0][start_index]
      m_query[1] = next_item_1ord
    m_query = mm.generate_vmo_vdim(models, m_query, coefs, indices, data) #query markov models for next event and update query for next iteration
    next_item_index = m_query[0]
    print(f'the next item is  {data[0][next_item_index]} at index {next_item_index}')
    return next_item_index, m_query
