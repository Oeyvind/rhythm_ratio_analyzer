#!/usr/bin/python
# -*- coding: latin-1 -*-

"""
OSC server, communication between Client (e.g. Csound) and Python

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

    def __init__(self, dc, ratio_analyzer, pl_instance):
        self.dc = dc # data container
        self.corpus = dc.corpus # the main data container for events
        self.pnum_corpus = dc.pnum_corpus # dict for parameter_name:index in corpus
        self.pending_analysis = [] # indices for events not yet enelyzed
        self.last_analyzed_phrase = [] # indices for events in the last analyzed phrase
        self.minimum_delta_time = 50
        self.previous_timestamp = -1
        self.previous_notenum = -1
        self.previous_velocity = -1
        self.phrase_number = 0
        
        self.pl = pl_instance # probabilistic logic instance
        self.pl.weights[1] = 1 # first order for best ratio
        self.pl.weights[2] = 1 # 2nd order for best ratio
        self.pl.set_temperature(0.2) # < 1.0 is more deterministic
        self.ra = ratio_analyzer

        # temporary!
        self.query = [0, [None, 0, 0]] # initial probabilistic query. 

    def receive_eventdata(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        index, timenow, on_off, notenum, velocity = osc_data # unpack the OSC data, must have the same number of variables as we have items in the data
        index = int(index)
        logging.debug(f'received: {index}, {timenow:.2f}, {on_off}, {notenum}, {velocity}')
        if on_off == 0:
            self.corpus[index, self.pnum_corpus['time_off']] = timenow
        if on_off == 1:
            # put events in analysis queue
            if index == 0:
                self.corpus[index, self.pnum_corpus['timestamp']] = timenow
                self.corpus[index, self.pnum_corpus['notenum']] = notenum
                self.corpus[index, self.pnum_corpus['velocity']] = velocity
                self.pending_analysis.append(index)
            else:
                if timenow > (self.corpus[index-1, self.pnum_corpus['timestamp']] + (self.minimum_delta_time/1000)):
                    self.corpus[index,self.pnum_corpus['timestamp']] = timenow
                    self.corpus[index, self.pnum_corpus['notenum']] = notenum
                    self.corpus[index, self.pnum_corpus['velocity']] = velocity
                    # relative notenumber and velocity
                    if self.previous_notenum > -1:
                        self.corpus[index, self.pnum_corpus['notenum_relative']] = notenum-self.previous_notenum
                    if self.previous_velocity > -1:
                        self.corpus[index, self.pnum_corpus['velocity_relative']] = velocity-self.previous_velocity
                    self.previous_notenum = notenum
                    self.previous_velocity = velocity
                    self.pending_analysis.append(index)
                else:
                    logging.debug('skipped double trig event: {}, {}'.format(index, timenow))
                    osc_io.sendOSC("python_skipindex", index) # send OSC back to client

    def analyze(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        # trigger analysis and send result back to client
        not_used = osc_data[0]
        if len(self.pending_analysis) < 2:
            print('WARNING: NOT ENOUGH DATA TO ANALYZE')
            return
        self.last_analyzed_phrase = self.pending_analysis # keep it so we can delete it if clear_last_phrase is called
        start, end = self.pending_analysis[0], self.pending_analysis[-1]
        timedata = self.corpus[start:end+1,self.pnum_corpus['timestamp']]
        self.phrase_number += 1
        ratios_reduced, ranked_unique_representations, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = self.ra.analyze(timedata)
        for i in range(len(trigseq)):
            osc_io.sendOSC("python_triggerdata", [i, trigseq[i]]) # send OSC back to client
        returnmsg = [ticktempo_bpm, tempo_tendency, float(pulseposition), float(len(self.pending_analysis))]
        osc_io.sendOSC("python_other", returnmsg) # send OSC back to client
        
        # store the rhythm fractions as float for each event in the corpus
        best = ranked_unique_representations[0]
        print(f'ratios best: \n{ratios_reduced[best,range(len(self.pending_analysis)-1),0]/ratios_reduced[best,range(len(self.pending_analysis)-1),1]}')
        next_best = ranked_unique_representations[1]
        for i in range(len(self.pending_analysis)-1): 
            indx = self.pending_analysis[i]
            self.corpus[indx,self.pnum_corpus['index']] = indx
            self.corpus[indx,self.pnum_corpus['ratio_best']] = ratios_reduced[best,i,0]/ratios_reduced[best,i,1] # ratio as float
            self.corpus[indx,self.pnum_corpus['deviation_best']] = ratios_reduced[best,i,2] # deviation
            self.corpus[indx,self.pnum_corpus['ratio_2nd_best']] = ratios_reduced[next_best,i,0]/ratios_reduced[next_best,i,1] # ratio as float
            self.corpus[indx,self.pnum_corpus['phrase_num']] = self.phrase_number
            # event duration relative to time until next event
            self.corpus[indx,self.pnum_corpus['duration']] = \
                (self.corpus[indx,self.pnum_corpus['time_off']] \
                - self.corpus[indx,self.pnum_corpus['timestamp']]) \
                / (self.corpus[indx+1,self.pnum_corpus['timestamp']] \
                - self.corpus[indx,self.pnum_corpus['timestamp']])
            # probabilistic model encoding
            self.pl.analyze_single_event(indx)
        self.pending_analysis = [] # clear

    def pl_generate(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        voicenum, index, request_item, request_weight = osc_data
        voicenum = int(voicenum)
        if request_item < 0:
            request = [None, 0, 0]
        else:
            request = ['ratio_best', request_item, request_weight] # FIX/update
        self.query = [index, request]
        print('***pl_query', voicenum, self.query)

        self.query = self.pl.generate(self.query, voicenum) #query probabilistic models for next event and update query for next iteration
        next_item_index = self.query[0]
        returnmsg = [int(next_item_index), 
                     float(self.corpus[next_item_index, self.pnum_corpus['ratio_best']]),
                     float(self.corpus[next_item_index, self.pnum_corpus['deviation_best']]),
                     float(self.corpus[next_item_index, self.pnum_corpus['duration']]),
                     float(self.corpus[next_item_index, self.pnum_corpus['notenum']]),
                     float(self.corpus[next_item_index, self.pnum_corpus['notenum_relative']]),
                     float(self.corpus[next_item_index, self.pnum_corpus['velocity']])]
        #print('next item', next_item_index)
        #print(returnmsg)
        osc_io.sendOSC(f"python_prob_gen_voice{voicenum}", returnmsg) # send OSC back to client

    def printstuff(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        printcode = int(osc_data[0])
        if printcode == 1:
            for parm in self.pl.prob_parms.keys():
                pe = self.pl.prob_parms[parm][1]
                print(pe, pe.name)
                for key, value in pe.stm.items():
                    print(key, value[pe.max_order:pe.size+pe.max_order])
        elif printcode == 2:
            print('last_phrase: indx, ratio1, ratio2')
            print(self.pnum_corpus['index'], self.pnum_corpus['ratio_best'], self.pnum_corpus['ratio_2nd_best'], self.last_analyzed_phrase)
            parmindxs = [self.pnum_corpus['index'], self.pnum_corpus['ratio_best'], self.pnum_corpus['ratio_2nd_best']]
            for i in self.last_analyzed_phrase[:-1]:
                print(self.corpus[[i,i,i],parmindxs])
        else:
            print(f'unknown print code: {printcode}')

    def eventdata_admin(self, unused_addr, *osc_data):
        clear_last_phrase, clear_all, save_all = osc_data
        if clear_last_phrase > 0:
            print('Clear last recorded phrase')
            for i in self.last_analyzed_phrase:
                self.dc.clear_corpus_item(i)
            self.phrase_number -= 1
            if self.phrase_number < 0: 
                self.phrase_number = 0
            self.pl.clear_phrase(self.last_analyzed_phrase)
        if clear_all > 0:
            print('CLEAR CORPUS')
            self.dc.clear_corpus()
            self.pending_analysis = []
            self.phrase_number = 0
            self.pl.clear_all()
            self.previous_notenum = -1
            self.previous_velocity = -1
        if save_all > 0:
            self.dc.save_corpus()
            self.pl.save_all()

    def receive_parameter_controls(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        # set control parameters, like score weights etc
        kbenni_weight, knd_weight, kratio_dev_weight, \
            kratio_dev_abs_max_weight, kgrid_dev_weight, \
            kevidence_weight, kautocorr_weight, kratio1_order, \
            kratio2_order, knotenum_order, kinterval_order, ktemperature = osc_data
        
        ratio_analyzer_weights = [kbenni_weight, knd_weight, kratio_dev_weight, \
                                  kratio_dev_abs_max_weight, kgrid_dev_weight, \
                                  kevidence_weight, kautocorr_weight]
        self.ra.set_weights(ratio_analyzer_weights)
        
        self.pl.set_weights_pname('ratio_best', kratio1_order)         
        self.pl.set_weights_pname('ratio_2nd_best', kratio2_order) 
        self.pl.set_weights_pname('notenum', knotenum_order) 
        self.pl.set_weights_pname('notenum_relative', kinterval_order) 
        self.pl.set_temperature(ktemperature)        
        logging.debug('receive_parameter_controls {}'.format(osc_data))

    def start_server(self):
        osc_io.dispatcher.map("/client_eventdata", self.receive_eventdata) # here we assign the function to be called when we receive OSC on this address
        osc_io.dispatcher.map("/client_analyze_trig", self.analyze) # 
        osc_io.dispatcher.map("/client_parametercontrols", self.receive_parameter_controls) # 
        osc_io.dispatcher.map("/client_memory", self.eventdata_admin) # 
        osc_io.dispatcher.map("/client_prob_gen", self.pl_generate) # 
        osc_io.dispatcher.map("/client_print", self.printstuff) # 
        osc_io.asyncio.run(osc_io.run_osc_server()) # run the OSC server and client

