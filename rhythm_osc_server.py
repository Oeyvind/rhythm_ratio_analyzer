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
    t0 = time.perf_counter(), time.process_time()
    # trigger analysis and send result back to Csound
    rank = osc_data[0]
    t1 = time.perf_counter(), time.process_time()
    if len(timedata) < 2:
        print('WARNING: NOT ENOUGH DATA TO ANALYZE')
        return
    if rank > 0:
        logging.debug('timedata {} length {}'.format(timedata, len(timedata)))
        rat2 = r.ratio_to_each(timedata, div_limit=2)
        rat4 = r.ratio_to_each(timedata, div_limit=4)
        ratios = np.concatenate((rat2, rat4), axis=0)
        ratio_deviations, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, benedetti_height, nd_add = r.ratio_scores(ratios,timedata)
        if LOG_SIMPLE_RATIOS:
            for i in range(len(ratios)):
                logging.debug('\nINDX {}  ref_delta: {}'.format(i,round(ratios[i,0,-1],2)))
                logging.debug(' benni: {}  nd_add: {}  dev_abs {}  dev_abs_max {}  g_dev: {}'.format(int(benedetti_height[i]),
                                                                          round(nd_add[i],2),
                                                                          round(ratio_deviation_abs[i], 2),
                                                                          round(ratio_deviation_abs_max[i], 2),
                                                                          round(gridsize_deviations[i],2)))
                logging.debug('num, denom, dev, delta:')
                logging.debug(np.array_str(ratios[i,:,:-1], precision=3, suppress_small=True))
        ratios_commondiv = r.make_commondiv_ratios(ratios)
        norm_num_ratios = r.normalize_numerators(ratios_commondiv)
        evidence_scores = r.evidence(norm_num_ratios)
        logging.debug('evidence_scores {}'.format(evidence_scores))
        if LOG_PROFILING:
            t2 = time.perf_counter(), time.process_time()
            logging.info('Time spent on Python ratio analysis up to evidence scores with timeseries length {}:'.format(len(timedata)))
            logging.info('    RT: {} seconds'.format(t2[0]-t1[0]))
            logging.info('    CPU: {} seconds'.format(t2[1]-t1[1]))

        autocorr_scores = []
        for i in range(len(ratios)):
            trigseq = r.make_trigger_sequence(ratios_commondiv[i,:,:2])
            acorr = r.autocorr_bitwise(trigseq)
            autocorr_scores.append(np.max(acorr[1:])**2) #max autocorr, raised to give more difference
        if LOG_PROFILING:
            t3 = time.perf_counter(), time.process_time()    
            logging.info('Time spent on autocorr scores with timeseries length {}:'.format(len(timedata)))
            logging.info('    RT: {} seconds'.format(t3[0]-t2[0]))
            logging.info('    CPU: {} seconds'.format(t3[1]-t2[1]))

        scores = r.normalize_and_add_scores(
            [benedetti_height, nd_add, ratio_deviation_abs, ratio_deviation_abs_max, gridsize_deviations, evidence_scores, autocorr_scores], 
            [benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight],
            [0, 0, 0, 0, 0, 1, 1])
        if LOG_PROFILING:
            t4 = time.perf_counter(), time.process_time()
            logging.info('Time spent on normalize_add_scores with timeseries length {}:'.format(len(timedata)))
            logging.info('    RT: {} seconds'.format(t4[0]-t3[0]))
            logging.info('    CPU: {} seconds'.format(t4[1]-t3[1]))

        if LOG_COMMONDIV_RATIOS:
            for i in range(len(ratios_commondiv)):
                logging.debug('\nINDX {}  ref_delta: {}'.format(i,round(ratios[i,0,-1],2)))
                logging.debug(' benni: {}'.format(int(benedetti_height[i])))
                logging.debug(' nd_add: {}'.format(round(nd_add[i],2)))
                logging.debug(' dev_abs {}'.format(round(ratio_deviation_abs[i], 2)))
                logging.debug(' dev_abs_max {}'.format(round(ratio_deviation_abs_max[i], 2)))
                logging.debug(' g_dev: {}'.format(round(gridsize_deviations[i],2)))
                logging.debug(' evidence {}'.format(evidence_scores[i])) 
                logging.debug(' acorr_max {}'.format(autocorr_scores[i]))
                logging.debug('num, denom, dev, delta:')
                logging.debug(np.array_str(ratios_commondiv[i,:,:-1], precision=3, suppress_small=True))
        
        logging.debug('\nscores: \n {}'.format([round(d,2) for d in scores]))
        logging.debug('\nindices: \n {}'.format(np.argsort(scores)))
        logging.debug('rank: {}'.format(rank))

        # to use old, comment out the following paragraph
        # simplify ratios and remove duplicate ratio representations
        ratios_reduced = np.copy(ratios_commondiv)
        ratios_reduced = r.simplify_ratios(ratios_reduced)
        duplicates = r.find_duplicate_representations(ratios_reduced)
        ranked_unique_representations = r.get_ranked_unique_representations(duplicates, scores)
        if LOG_SIMPLE_REDUCED_RATIOS:
            logging.debug('\nduplicates \n {}'.format(duplicates))
            logging.debug('\nscores\n {}'.format(scores))
            logging.debug('\nranked unique\n {}'.format(ranked_unique_representations))
            logging.debug('\nbest unique\n {}'.format(ratios_reduced[ranked_unique_representations[0]]))
            logging.debug('+nsecond best unique\n {}'.format(ratios_reduced[ranked_unique_representations[1]]) )
        
        # new ranking
        i = ranked_unique_representations[rank-1] # select the unique representation ranked from the lowest score
        # old
        #i = np.argsort(scores)[int(rank)] # select the representation ranked from the lowest score

        logging.debug('using ratio-proposal: {}'.format(i))
        nums = ratios_reduced[i,:,0].astype(int).tolist()
        denoms = ratios_reduced[i,:,1].astype(int).tolist()
        deviations = ratios_reduced[i,:,2].astype(float).tolist()
        ticktempo_Hz = (1/ratios_commondiv[i,0,-1])*ratios_commondiv[i,0,1]
        ticktempo_bpm = ticktempo_Hz*60
        logging.debug('ticktempo: {} bpm'.format(ticktempo_bpm))
        trigseq = r.make_trigger_sequence(ratios_commondiv[i,:,:2])
        acorr = r.autocorr(trigseq)
        #logging.debug(acorr)
        pulseposition = np.argmax(acorr[1:])+1
        logging.debug('pulse: {} bpm'.format(ticktempo_bpm/pulseposition))
        tempo_tendency = ratio_deviations[i]*-1 # invert deviation to adjust tempo
        logging.debug('tempo tendency: {}'.format(round(tempo_tendency,3)))
        t5 = time.perf_counter(), time.process_time()
        for i in range(len(nums)):
            returnmsg = [nums[i], denoms[i], deviations[i]] #pack the values that we want to send back to Csound via OSC
            logging.debug('num, denom, deviation: {}'.format(returnmsg))
            osc_io.sendOSC("python_rhythmdata", returnmsg) # send OSC back to Csound
        returnmsg = [-1, 1, 0] #pack terminator
        osc_io.sendOSC("python_rhythmdata", returnmsg) # send OSC back to Csound
        for i in range(len(trigseq)):
            osc_io.sendOSC("python_triggerdata", [i, trigseq[i]]) # send OSC back to Csound
        returnmsg = [ticktempo_bpm,tempo_tendency,float(pulseposition)]
        logging.debug(returnmsg)
        osc_io.sendOSC("python_other", returnmsg) # send OSC back to Csound
        if LOG_PROFILING:
            t6 = time.perf_counter(), time.process_time()
            logging.info('\nTotal time at {}, \nincludinc OSC communications with timeseries length {}:'.format(
                datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f'),
                len(timedata)))
            logging.info('    RT: {} seconds'.format(t6[0]-t0[0]))
            logging.info('    CPU: {} seconds'.format(t6[1]-t0[1]))
            logging.info('\nTim spent on Python ratio analysis:')
            logging.info('    RT: {} seconds'.format(t5[0]-t1[0]))
            logging.info('    CPU: {} seconds'.format(t5[1]-t1[1]))
        
        # markov model training
        global mm_data, mm_datasize, mm_max_order, mh
        mm_datasize = len(ratios_reduced[0])
        #mm_indices = np.arange(mm_datasize)
        mm_dimensions = 2 # set max dimensions here for now
        mm_data = np.empty((mm_dimensions,mm_datasize),dtype='float')
        best = i = ranked_unique_representations[0]
        next_best = ranked_unique_representations[1]
        for i in range(mm_datasize):
            nums = ratios_reduced[i,:,0].astype(int).tolist()
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
        mh = mm.MarkovHelper(mm_data, max_size=100, max_order=mm_max_order)
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
    mm_query = mh.generate_vmo_vdim(mm_query, (order,dimension), temperature) #query markov models for next event and update query for next iteration
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

