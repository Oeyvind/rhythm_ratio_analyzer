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

    def __init__(self, corpus, pnum_corpus, ratio_analyzer, mm):
        self.corpus = corpus # the main data container for events
        self.pnum_corpus = pnum_corpus # dict for parameter_name:index in corpus
        self.pending_analysis = [] # indices for events not yet enelyzed
        self.minimum_delta_time = 50
        self.previous_timestamp = -1
        self.phrase_number = 0
        
        self.mh = mm.MarkovHelper(data=None, d_size2=2, max_size=100, max_order=2)
        self.mm = mm.MarkovManager(self.mh)
        self.ra = ratio_analyzer

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
            print(timedata)
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

            # markov model "training"
            best = ranked_unique_representations[0]
            next_best = ranked_unique_representations[1]
            self.mm.add_data_chunk(ratios_reduced, best, next_best)
            
            # store the rhythm fractions as float for each event in the corpus
            for i in range(len(self.pending_analysis)-1): 
                indx = self.pending_analysis[i]
                self.corpus[indx,self.pnum_corpus['index']] = indx
                self.corpus[indx,self.pnum_corpus['ratio_best']] = ratios_reduced[best,i,0]/ratios_reduced[best,i,1] # ratio as float
                self.corpus[indx,self.pnum_corpus['deviation_best']] = ratios_reduced[best,i,2] # deviation
                self.corpus[indx,self.pnum_corpus['ratio_2nd_best']] = ratios_reduced[next_best,i,0]/ratios_reduced[next_best,i,1] # ratio as float
                self.corpus[indx,self.pnum_corpus['deviation_2nd_best']] = ratios_reduced[next_best,i,2] # deviation
                self.corpus[indx,self.pnum_corpus['phrase_num']] = self.phrase_number
            self.corpus[indx+1,self.pnum_corpus['index']] = indx+1 # temporarily close the phrase...
            self.corpus[indx+1,self.pnum_corpus['ratio_best']] = 1 # ...rewrite data for this event later if we do streaming analysis ...
            self.corpus[indx+1,self.pnum_corpus['phrase_num']] = self.phrase_number # ... chunk by chunk over a larger contiguous phrase
            print(f'corpus \n{self.corpus[self.pending_analysis[0]:self.pending_analysis[-1]+1]}')
            self.pending_analysis = [] # clear

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

    def mm_generate(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        order, dimension, temperature, index, ratio, request_item, request_weight, update = osc_data
        if request_item < 0:
            request_item = None
        if update > 0:
            self.mm.mm_query[0] = int(index) 
            self.mm.mm_query[1] = request_item 
            self.mm.mm_query[2] = request_weight
            # query format: [next_item_index, request_next_item, request_weight, next_item_1ord, next_item_1ord_2D]
        print('***mm_query', self.mm.mm_query)

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

        self.mm.mm_query = self.mh.generate_vmo_vdim(self.mm.mm_query, weights, temperature) #query markov models for next event and update query for next iteration
        next_item_index = self.mm.mm_query[0]
        returnmsg = [int(next_item_index), float(self.mh.data[0][next_item_index])]
        #print('returnmsg', returnmsg)
        osc_io.sendOSC("python_markov_gen", returnmsg) # send OSC back to Csound

    def mm_print(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        print('mm_data', self.mm_data)
        for m in [self.mh.m_1ord, self.mh.m_1ord_2D]:
            print(m, m.name)
            for key, value in m.markov_stm.items():
                print(key, value[m.max_order:m.datasize+m.max_order])

    def start_server(self):
        osc_io.dispatcher.map("/csound_timevalues", self.receive_timevalues) # here we assign the function to be called when we receive OSC on this address
        osc_io.dispatcher.map("/csound_analyze_trig", self.analyze) # 
        osc_io.dispatcher.map("/csound_parametercontrols", self.receive_parameter_controls) # 
        osc_io.dispatcher.map("/csound_clear", self.clear_timedata) # 
        osc_io.dispatcher.map("/csound_markov_gen", self.mm_generate) # 
        osc_io.dispatcher.map("/csound_markov_print", self.mm_print) # 
        osc_io.asyncio.run(osc_io.run_osc_server()) # run the OSC server and client

