#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
Rhythm ratio analyzer in Python, getting time values from Csound

@author: Oyvind Brandtsegg
@contact: obrandts@gmail.com
@license: GPL
"""

import osc_io # osc server and client 
import ratio_analyzer as r
import numpy as np
import markov_model as mm
import time # for profiling
from datetime import datetime
import logging 
import json
#logging.basicConfig(filename="logging.log", filemode='w', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

timedata = []

weights = {
    'benni_weight': 1,
    'nd_sum_weight': 1
    'ratio_dev_weight': 0.3
    'ratio_dev_abs_max_weight': 1
    'grid_dev_weight': 0.2
    'evidence_weight': 0.3
    'autocorr_weight': 1,
    'minimum_delta_time': 50 #milliseconds
}

mh = mm.MarkovHelper(data=None, d_size2=2, max_size=100, max_order=2)
mm = mm.MarkovManager(mh)

def receive_timevalues(unused_addr, *osc_data):
    '''Message handler. This is called when we receive an OSC message'''
    index, timenow = osc_data # unpack the OSC data, must have the same number of variables as we have items in the data
    logging.debug('received: {}, {}'.format(index, timenow))
    # update analysis data here
    if len(timedata) == 0:
        timedata.append(timenow)
    else:
        if timenow > (timedata[-1] + (minimum_delta_time/1000)):
            timedata.append(timenow)
        else:
            logging.debug('skipped double trig event: {}, {}'.format(index, timenow))

def analyze(unused_addr, *osc_data):
    '''Message handler. This is called when we receive an OSC message'''
    # trigger analysis and send result back to Csound
    rank = osc_data[0]
    if len(timedata) < 2:
        print('WARNING: NOT ENOUGH DATA TO ANALYZE')
        return
    if rank > 0:
        ratios_reduced, ranked_unique_representations, selected, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = r.analyze(timedata, rank, weights)
        ratios_list = ratios_reduced[selected].tolist()
        for i in range(len(ratios_list)):
            returnmsg = [ratios_list[i][0], ratios_list[i][1], ratios_list[i][2]] #pack the values that we want to send back to Csound via OSC
            osc_io.sendOSC("python_rhythmdata", returnmsg) # send OSC back to Csound
            returnmsg = [-1, 1, 0] #pack terminator
            osc_io.sendOSC("python_rhythmdata", returnmsg) # send OSC back to Csound
        for i in range(len(trigseq)):
            osc_io.sendOSC("python_triggerdata", [i, trigseq[i]]) # send OSC back to Csound
        returnmsg = [ticktempo_bpm,tempo_tendency,float(pulseposition)]
        osc_io.sendOSC("python_other", returnmsg) # send OSC back to Csound

        # markov model "training"
        best = ranked_unique_representations[0]
        next_best = ranked_unique_representations[1]
        mm.add_data_chunk(ratios_reduced, best, next_best)
        
def clear_timedata(unused_addr, *osc_data):
    global timedata
    timedata = []
    for m in [mh.m_1ord, mh.m_1ord_2D]:
        m.clear()
    print('clear timeseries and Markov data')

def receive_parameter_controls(unused_addr, *osc_data):
    '''Message handler. This is called when we receive an OSC message'''
    # set control parameters, like score weights etc
    global weights
    benni, nd_sum, ratio_dev, ratio_dev_abs_max, grid_dev, evidence, autocorr, minimum_delta_time = osc_data
    weights['benni_weight'] = benni
    weights['nd_sum_weight'] = nd_sum
    weights['ratio_dev_weight'] = ratio_dev
    weights['ratio_dev_abs_max_weight'] = ratio_dev_abs_max
    weights['grid_dev_weight'] = grid_dev
    weights['evidence_weight'] = evidence
    weights['autocorr_weight'] = autocorr
    weights['minimum_delta_time'] = minimum_delta_time

    logging.debug('receive_parameter_controls {}'.format(osc_data))

def mm_generate(unused_addr, *osc_data):
    '''Message handler. This is called when we receive an OSC message'''
    order, dimension, temperature, index, ratio, request_item, request_weight, update = osc_data
    if request_item < 0:
        request_item = None
    if update > 0:
        mm.mm_query[0] = int(index) 
        mm.mm_query[1] = request_item 
        mm.mm_query[2] = request_weight
        # query format: [next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D]
    print('***mm_query', mm.mm_query)

    weights = np.zeros(5) # TEMPORARY, was order, dimension
    # cumbersome hack for now
    if order == 0:
        weights[:3] = 0
    if order == 1:
        weights[0] = 1
    if order == 2:
        weights[:2] = 1
    if dimension == 2:
        weights[2:4] = 1
    weights[4] = request_weight
    
    mm.mm_query = mh.generate_vmo_vdim(mm.mm_query, weights, temperature) #query markov models for next event and update query for next iteration
    next_item_index = mm.mm_query[0]
    returnmsg = [int(next_item_index), float(mh.data[0][next_item_index])]
    #print('returnmsg', returnmsg)
    osc_io.sendOSC("python_markov_gen", returnmsg) # send OSC back to Csound

def mm_print(unused_addr, *osc_data):
    '''Message handler. This is called when we receive an OSC message'''
    _unused = osc_data
    print('mm_data', mm_data)
    #print('mm_models', mm_models)
    for m in [mh.m_1ord, mh.m_1ord_2D]:
        print(m, m.name)
        for key, value in m.markov_stm.items():
            print(key, value[mm_max_order:mm_datasize+mm_max_order])

def start_server():
    osc_io.dispatcher.map("/csound_timevalues", receive_timevalues) # here we assign the function to be called when we receive OSC on this address
    osc_io.dispatcher.map("/csound_analyze_trig", analyze) # 
    osc_io.dispatcher.map("/csound_parametercontrols", receive_parameter_controls) # 
    osc_io.dispatcher.map("/csound_clear", clear_timedata) # 
    osc_io.dispatcher.map("/csound_markov_gen", mm_generate) # 
    osc_io.dispatcher.map("/csound_markov_print", mm_print) # 
    osc_io.asyncio.run(osc_io.run_osc_server()) # run the OSC server and client

if __name__ == "__main__": # if we run this module as main we will start the server
    start_server()
