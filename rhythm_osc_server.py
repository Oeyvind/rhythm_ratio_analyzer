#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
OSC server, communication between Csound and Python

@author: Oyvind Brandtsegg
@contact: obrandts@gmail.com
@license: GPL
"""

import osc_io # osc server and client 
import numpy as np
np.set_printoptions(precision=2)

import logging 
#logging.basicConfig(filename="logging.log", filemode='w', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

class Osc_server():

    def __init__(self, corpus, pnum_corpus, ratio_analyzer, pl_instance):
        self.corpus = corpus # the main data container for events
        self.pnum_corpus = pnum_corpus # dict for parameter_name:index in corpus
        self.pending_analysis = [] # indices for events not yet enelyzed
        self.minimum_delta_time = 50
        self.previous_timestamp = -1
        self.phrase_number = 0
        
        self.pl = pl_instance
        self.pl.weights[1] = 1 # first order for best ratio
        self.pl.weights[2] = 1 # 2nd order for best ratio
        self.pl.set_temperature(0.2) # < 1.0 is more deterministic
        self.ra = ratio_analyzer

        # temporary!
        self.query = [0, [None, 0, 0]] # initial probabilistic query. 

    def receive_timevalues(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        index, timenow = osc_data # unpack the OSC data, must have the same number of variables as we have items in the data
        index = int(index)
        logging.debug('received: {}, {}'.format(index, timenow))
        # put events in analysis queue
        if index == 0:
            self.corpus[index, self.pnum_corpus['timestamp']] = timenow
            self.pending_analysis.append(index)
        else:
            if timenow > (self.corpus[index-1, self.pnum_corpus['timestamp']] + (self.minimum_delta_time/1000)):
                self.corpus[index,self.pnum_corpus['timestamp']] = timenow
                self.pending_analysis.append(index)
            else:
                logging.debug('skipped double trig event: {}, {}'.format(index, timenow))
                osc_io.sendOSC("python_skipindex", index) # send OSC back to Csound

    def analyze(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        # trigger analysis and send result back to Csound
        rank = osc_data[0]
        if len(self.pending_analysis) < 2:
            print('WARNING: NOT ENOUGH DATA TO ANALYZE')
            return
        if rank > 0:
            start, end = self.pending_analysis[0], self.pending_analysis[-1]
            timedata = self.corpus[start:end+1,self.pnum_corpus['timestamp']]
            self.phrase_number += 1
            ratios_reduced, ranked_unique_representations, selected, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = self.ra.analyze(timedata, rank)
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
            
            # store the rhythm fractions as float for each event in the corpus
            best = ranked_unique_representations[0]
            next_best = ranked_unique_representations[1]
            for i in range(len(self.pending_analysis)-1): 
                indx = self.pending_analysis[i]
                self.corpus[indx,self.pnum_corpus['index']] = indx
                self.corpus[indx,self.pnum_corpus['ratio_best']] = ratios_reduced[best,i,0]/ratios_reduced[best,i,1] # ratio as float
                self.corpus[indx,self.pnum_corpus['deviation_best']] = ratios_reduced[best,i,2] # deviation
                self.corpus[indx,self.pnum_corpus['ratio_2nd_best']] = ratios_reduced[next_best,i,0]/ratios_reduced[next_best,i,1] # ratio as float
                self.corpus[indx,self.pnum_corpus['deviation_2nd_best']] = ratios_reduced[next_best,i,2] # deviation
                self.corpus[indx,self.pnum_corpus['phrase_num']] = self.phrase_number
                # probabilistic model encoding
                self.pl.analyze_single_event(i)
            self.pending_analysis = [] # clear

    def pl_generate(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        #order, dimension, temperature, index, ratio, request_item, request_weight, update = osc_data
        index, request_item, request_weight = osc_data
        if request_item < 0:
            request = [None, 0, 0]
        else:
            request = ['ratio_best', request_item, request_weight] # FIX/update
        self.query = [index, request]
        print('***pl_query', self.query)

        self.query = self.pl.generate(self.query) #query probabilistic models for next event and update query for next iteration
        next_item_index = self.query[0]
        returnmsg = [int(next_item_index), float(self.corpus[next_item_index, self.pnum_corpus['ratio_best']])]
        #print('returnmsg', returnmsg)
        osc_io.sendOSC("python_prob_gen", returnmsg) # send OSC back to Csound

    def pl_print(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        print('pl_data', self.corpus)
        for p in [self.pl.m_1ord, self.pl.m_1ord_2D]:
            print(p, p.name)
            for key, value in p.stm.items():
                print(key, value[p.max_order:p.datasize+m.max_order])

    def clear_timedata(self, unused_addr, *osc_data):
        print('CLEAR DATA NOT IMPLEMENTED YET, but resetting phrase number')
        self.phrase_number = 0
        # clear the whole corpus? clear a range of indices?
        # clear probabilistic encoder for the indices we want to clear
        '''
        self.timedata = []
        for m in [self.mh.m_1ord, self.mh.m_1ord_2D]:
            m.clear()
        print('clear timeseries and probabilistic encoder')
        '''

    def receive_parameter_controls(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        # set control parameters, like score weights etc
        self.ra.set_weights(osc_data)
        logging.debug('receive_parameter_controls {}'.format(osc_data))

    def start_server(self):
        osc_io.dispatcher.map("/csound_timevalues", self.receive_timevalues) # here we assign the function to be called when we receive OSC on this address
        osc_io.dispatcher.map("/csound_analyze_trig", self.analyze) # 
        osc_io.dispatcher.map("/csound_parametercontrols", self.receive_parameter_controls) # 
        osc_io.dispatcher.map("/csound_clear", self.clear_timedata) # 
        osc_io.dispatcher.map("/csound_prob_gen", self.pl_generate) # 
        osc_io.dispatcher.map("/csound_prob_print", self.pl_print) # 
        osc_io.asyncio.run(osc_io.run_osc_server()) # run the OSC server and client

