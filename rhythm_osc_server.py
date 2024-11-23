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
LOG_SIMPLE_RATIOS = False
LOG_COMMONDIV_RATIOS = False
LOG_PROFILING = False
LOG_SIMPLE_REDUCED_RATIOS = False
LOG_MARKOV_INPUT = True

timedata = []
minimum_delta_time = 50 #milliseconds
benni_weight = 1
nd_sum_weight = 1
ratio_dev_weight = 0.3
ratio_dev_abs_max_weight = 1
grid_dev_weight = 0.2
evidence_weight = 0.3
autocorr_weight = 1
savedata = False

mh = None # Markov helper object
mm_data = None # to hold markov model data
mm_datasize = -1
mm_max_order = 2
mm_query = [0, None, 0, None, None] # initial markov query. 
# query format: [next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D]

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
        weights = [benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight]
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

        # REFACTORED TO HERE, NOW DO THE PROBABLISTIC PROCESSING IN A SEPARATE MODULE        
        # markov model training
        global mm_data, mm_datasize, mm_max_order, mh
        mm_datasize = len(ratios_reduced[0])
        #mm_indices = np.arange(mm_datasize)
        mm_dimensions = 2 # set max dimensions here for now
        mm_data = np.empty((mm_dimensions,mm_datasize),dtype='float')
        best = ranked_unique_representations[0]
        next_best = ranked_unique_representations[1]
        for i in range(mm_datasize):
            #nums = ratios_reduced[i,:,0].astype(int).tolist()
            ratio_float1 = ratios_reduced[best][i][0]/ratios_reduced[best][i][1]
            ratio_float2 = ratios_reduced[next_best][i][0]/ratios_reduced[next_best][i][1]
            mm_data[0,i] = ratio_float1
            mm_data[1,i] = ratio_float2
            if LOG_MARKOV_INPUT:
                logging.debug(f'mm ratio1: {ratios_reduced[best][i][0]},{ratios_reduced[best][i][1]}')
                logging.debug(f'mm as float {ratio_float1}')
        if LOG_MARKOV_INPUT:
            logging.debug(f'mm_data: {mm_data}')
        #analyze variable markov order in 2 dimensions
        mh = mm.MarkovHelper(data=None, d_size2=2, max_size=100, max_order=mm_max_order)
        mh.set_data(mm_data)
        mh.analyze_vmo_vdim()

        if savedata:
            # make a dict with all the data to be exported
            jsondict = {}
            #selection = np.argsort(scores)[:4] # select the 4 best representations
            ranked_unique_representations[rank]
            for i in range(4):
                sub_dict = {}
                j = ranked_unique_representations[i]
                sub_dict['ratios'] = ratios_reduced[j].tolist()
                trigseq = r.make_trigger_sequence(ratios_commondiv[j,:,:2])
                sub_dict['trigseq'] = trigseq
                acorr = r.autocorr(trigseq).tolist()
                sub_dict['autocorr'] = acorr
                sub_dict['pulsepos'] = (np.argmax(acorr[1:])+1).tolist()
                jsondict[int(i)] = sub_dict
            with open('testdata_rhythm.json', 'w') as filehandle:
                json.dump(jsondict, filehandle)
        
def clear_timedata(unused_addr, *osc_data):
    global timedata
    timedata = []
    for m in [mh.m_1ord, mh.m_1ord_2D]:
        m.clear()
    print('clear timeseries and Markov data')

def receive_parameter_controls(unused_addr, *osc_data):
    '''Message handler. This is called when we receive an OSC message'''
    # set control parameters, like score weights etc
    global benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight, minimum_delta_time
    benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight, minimum_delta_time = osc_data
    logging.debug('receive_parameter_controls {}'.format(osc_data))

def mm_generate(unused_addr, *osc_data):
    '''Message handler. This is called when we receive an OSC message'''
    global mm_query
    order, dimension, temperature, index, ratio, request_item, request_weight, update = osc_data
    if request_item < 0:
        request_item = None
    if update > 0:
        mm_query[0] = int(index) 
        mm_query[1] = request_item 
        mm_query[2] = request_weight
        # query format: [next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D]
    print('***mm_query', mm_query)

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
    
    mm_query = mh.generate_vmo_vdim(mm_query, weights, temperature) #query markov models for next event and update query for next iteration
    next_item_index = mm_query[0]
    returnmsg = [int(next_item_index), float(mm_data[0][next_item_index])]
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

if __name__ == "__main__": # if we run this module as main we will start the server
    osc_io.dispatcher.map("/csound_timevalues", receive_timevalues) # here we assign the function to be called when we receive OSC on this address
    osc_io.dispatcher.map("/csound_analyze_trig", analyze) # 
    osc_io.dispatcher.map("/csound_parametercontrols", receive_parameter_controls) # 
    osc_io.dispatcher.map("/csound_clear", clear_timedata) # 
    osc_io.dispatcher.map("/csound_markov_gen", mm_generate) # 
    osc_io.dispatcher.map("/csound_markov_print", mm_print) # 
    osc_io.asyncio.run(osc_io.run_osc_server()) # run the OSC server and client

