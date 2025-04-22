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
np.set_printoptions(linewidth=np.inf)

import logging 
#logging.basicConfig(filename="logging.log", filemode='w', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

import time
time_at_start = time.time()

class Osc_server():

    def __init__(self, dc, ratio_analyzer, pl_instance):
        self.dc = dc # data container
        self.pending_analysis = [] # indices for events not yet enelyzed
        self.last_analyzed_phrase = [] # indices for events in the last analyzed phrase
        self.minimum_delta_time = 50
        self.previous_timestamp = -1
        self.previous_notenum = -1
        self.previous_velocity = -1
        self.phrase_number = 0
        self.chord_on = 0

        self.pl = pl_instance # probabilistic logic instance
        self.pl.weights[1] = 1 # first order for best ratio
        self.pl.weights[2] = 1 # 2nd order for best ratio
        self.ra = ratio_analyzer

    def receive_eventdata(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        index, timenow, on_off, notenum, velocity = osc_data # unpack the OSC data, must have the same number of variables as we have items in the data
        index = int(index)
        logging.debug(f'received: {index}, {timenow:.2f}, {on_off}, {notenum}, {velocity}')
        if on_off == 0:
            self.dc.corpus[index, self.dc.pnum_corpus['time_off']] = timenow
        if on_off == 1:
            # put events in analysis queue
            if index == 0:
                self.dc.corpus[index, self.dc.pnum_corpus['timestamp']] = timenow
                self.dc.corpus[index, self.dc.pnum_corpus['notenum']] = notenum
                self.dc.corpus[index, self.dc.pnum_corpus['velocity']] = velocity
                self.pending_analysis.append(index)
            else:
                if timenow < (self.dc.corpus[index-1, self.dc.pnum_corpus['timestamp']] + (self.minimum_delta_time/1000)):
                    timenow += (self.minimum_delta_time/1000)
                self.dc.corpus[index,self.dc.pnum_corpus['timestamp']] = timenow
                self.dc.corpus[index, self.dc.pnum_corpus['notenum']] = notenum
                self.dc.corpus[index, self.dc.pnum_corpus['velocity']] = velocity
                # relative notenumber and velocity
                if self.previous_notenum > -1:
                    self.dc.corpus[index, self.dc.pnum_corpus['notenum_relative']] = notenum-self.previous_notenum
                if self.previous_velocity > -1:
                    self.dc.corpus[index, self.dc.pnum_corpus['velocity_relative']] = velocity-self.previous_velocity
                self.pending_analysis.append(index)
            self.previous_notenum = notenum
            self.previous_velocity = velocity
    
    def receive_eventchord(self, unused_addr, *osc_data):
        '''Receive chord data, i.e. when several notes occur simultaneously (within time window of i.e. 50 ms) in the input data'''
        index, chord_index, note, velocity, delta_time = osc_data
        index = int(index)
        chord_index = int(chord_index)
        self.dc.corpus[index, self.dc.pnum_corpus['chord_index']] = chord_index # 1-indexed, as zero means no chord
        base_note = self.dc.corpus[index, self.dc.pnum_corpus['notenum']] 
        base_velocity = self.dc.corpus[index, self.dc.pnum_corpus['velocity']]
        chord_note = [note-base_note, velocity/base_velocity, delta_time]
        if len(self.dc.chord_list) < chord_index:
            self.dc.chord_list.append([chord_note]) # the first note in a chord
        else:
            self.dc.chord_list[chord_index-1].append(chord_note) # next notes in previously existing chord
        
    def analyze(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        # trigger analysis and send result back to client
        not_used = osc_data[0]
        if len(self.pending_analysis) < 2:
            print('WARNING: NOT ENOUGH DATA TO ANALYZE')
            return
        self.last_analyzed_phrase = self.pending_analysis # keep it so we can delete it if clear_last_phrase is called
        start, end = self.pending_analysis[0], self.pending_analysis[-1]
        timedata = self.dc.corpus[start:end+1,self.dc.pnum_corpus['timestamp']]
        with np.printoptions(precision=5):
            print('timedata:', timedata-timedata[0], 'len:', len(self.pending_analysis))
        self.phrase_number += 1
        best, duration_patterns, deviations, scores, tempi = self.ra.analyze(timedata)
        print(f'dur pattern {duration_patterns[best]}')
        print(f'deviations {deviations[best]}')
        deviation_polarity = self.ra.get_deviation_polarity(deviations[best], 0.01)
        print(f'tempo {tempi[best]}')
        
        # return tempo to client
        returnmsg = tempi[best], len(duration_patterns[best]) # tempo and phrase length
        osc_io.sendOSC("python_other", returnmsg) # send OSC back to client
        
        # store the duration pattern as integer for each event in the corpus
        for i in range(len(self.pending_analysis)): 
            indx = self.pending_analysis[i]
            self.dc.corpus[indx,self.dc.pnum_corpus['index']] = indx
            self.dc.corpus[indx,self.dc.pnum_corpus['phrase_num']] = self.phrase_number
            if i < len(self.pending_analysis)-1:
                # DONE TO HERE
                # ok 1. store dur_pattern item as 'rhythm_subdiv' instead of ratio_best
                # ok 2. rename address in corpus accordingly
                # ok 3. check if that change propagates nicely into prob_logic
                # ok   - rename ratio_best and deviation_best fields here in this file, and check others
                # ok 4. calculate deviation per event (above)
                # ok 5. store deviation per event
                # ok 6. delete "next best" fields from corpus
                # 7. rewrite plugin to receive only tempo "python_tempo" OSC address
                #   - rewrite to only send complexity and deviation weight
                # ok 8. add prob_logic item for deviation
                # ok   - use 1, 0, and -1 to classify deviation (0 <= 1% ?)
                self.dc.corpus[indx,self.dc.pnum_corpus['rhythm_subdiv']] = duration_patterns[best][i]
                self.dc.corpus[indx,self.dc.pnum_corpus['deviation']] = deviations[best][i]
                self.dc.corpus[indx,self.dc.pnum_corpus['deviation_polarity']] = deviation_polarity[i]
                # event duration relative to time until next event
                self.dc.corpus[indx,self.dc.pnum_corpus['duration']] = \
                    ((self.dc.corpus[indx,self.dc.pnum_corpus['time_off']] \
                    - self.dc.corpus[indx,self.dc.pnum_corpus['timestamp']]) \
                    / (self.dc.corpus[indx+1,self.dc.pnum_corpus['timestamp']] \
                    - self.dc.corpus[indx,self.dc.pnum_corpus['timestamp']]))
            else:
                self.dc.corpus[indx,self.dc.pnum_corpus['rhythm_subdiv']] = 1
                # event duration for last event
                self.dc.corpus[indx,self.dc.pnum_corpus['duration']] = 0.9
            # probabilistic model encoding
            self.pl.analyze_single_event(indx)
        self.pending_analysis = [] # clear

    def pl_generate(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        voicenum, index, request_type, request_parm, request_value, request_weight, temperature = osc_data
        voicenum = int(voicenum)
        t = time.time()
        time_since_start = t-time_at_start
        if request_type in ['none', '-']: # no request
            request =  [None]
        else: 
            # translation of gui labels to data container labels
            if request_parm == 'rhythm': request_parm = 'rhythm_subdiv'
            if request_parm == 'pitch': request_parm = 'notenum'
            if request_parm == 'interval': request_parm = 'notenum_relative'
            if request_parm == 'phrase': request_parm = 'phrase_num'
            request = [request_parm, [request_type, [request_value]], request_weight]
        query = [index, request]
        print('***pl_query', voicenum, query)

        next_item_index = self.pl.generate(query, voicenum, temperature) #query probabilistic models for next event and update query for next iteration
        returnmsg = [int(next_item_index), 
                     float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['rhythm_subdiv']]),
                     float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['deviation']]),
                     float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['duration']]),
                     float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['notenum']]),
                     float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['notenum_relative']]),
                     float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['velocity']])]
        #print(f'gen returnmsg:{returnmsg}')
        osc_io.sendOSC(f"python_prob_gen_voice{voicenum}", returnmsg) # send OSC back to client
        chord_index = self.dc.corpus[next_item_index, self.dc.pnum_corpus['chord_index']]
        #print(f'debug: chord_index {chord_index}, chord_list {self.dc.chord_list}')
        if chord_index > 0:
            for event in self.dc.chord_list[int(chord_index-1)]:
                returnmsg = [int(next_item_index), 
                             0.0, # rhythm_subdiv
                             event[2], # deviation (...)
                             float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['duration']]),
                             event[0]+float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['notenum']]),
                             event[0],
                             event[1]*float(self.dc.corpus[next_item_index, self.dc.pnum_corpus['velocity']])]
                #print('chord event', returnmsg)
                if self.chord_on > 0:
                    osc_io.sendOSC(f"python_prob_gen_voice{voicenum}", returnmsg) # send OSC back to client
        

    def printstuff(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        printcode = int(osc_data[0])
        if printcode == 1:
            for parm in self.dc.prob_parms.keys():
                pe = self.dc.prob_parms[parm][1] # prob encoder instance
                print(pe, pe.name)
                for key, value in pe.stm.items():
                    #print(key, value[pe.max_order:pe.size+pe.max_order])
                    print(key, value[pe.max_order:pe.max_order+20])
            print('corpus')
            for i in range(20):
                print(i, self.dc.corpus[i])
            print('chord list: \n', self.dc.chord_list)

        elif printcode == 2:
            print('last_phrase: indx, rhythm_subdiv')
            print(self.dc.pnum_corpus['index'], self.dc.pnum_corpus['rhythm_subdiv'], self.last_analyzed_phrase)
            parmindxs = [self.dc.pnum_corpus['index'], self.dc.pnum_corpus['rhythm_subdiv']]
            for i in self.last_analyzed_phrase[:-1]:
                print(self.dc.corpus[[i,i,i],parmindxs])
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
        kcomplexity_weight, kdeviation_weight, krhythm_order, \
            kdeviation_order, knotenum_order, kinterval_order, kchord_on = osc_data
        
        self.ra.set_weights(kcomplexity_weight, kdeviation_weight)
        
        self.pl.set_weights_pname('rhythm_subdiv', krhythm_order)         
        self.pl.set_weights_pname('deviation_polarity', kdeviation_order) 
        self.pl.set_weights_pname('notenum', knotenum_order) 
        self.pl.set_weights_pname('notenum_relative', kinterval_order)
        self.chord_on = kchord_on 
        logging.debug('receive_parameter_controls {}'.format(osc_data))

    def start_server(self):
        osc_io.dispatcher.map("/client_eventdata", self.receive_eventdata) # here we assign the function to be called when we receive OSC on this address
        osc_io.dispatcher.map("/client_eventchord", self.receive_eventchord) 
        osc_io.dispatcher.map("/client_analyze_trig", self.analyze) # 
        osc_io.dispatcher.map("/client_parametercontrols", self.receive_parameter_controls) # 
        osc_io.dispatcher.map("/client_memory", self.eventdata_admin) # 
        osc_io.dispatcher.map("/client_prob_gen", self.pl_generate) # 
        osc_io.dispatcher.map("/client_print", self.printstuff) # 
        osc_io.asyncio.run(osc_io.run_osc_server()) # run the OSC server and client

