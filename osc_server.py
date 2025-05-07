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
        #self.pending_analysis = [] # indices for events not yet analyzed
        self.last_analyzed_phrase = [] # NOT USED indices for events in the last analyzed phrase
        self.index = 0
        self.analysis_chunk = []
        self.recent_analyses = []
        self.prev_tempo = 0
        self.minimum_delta_time = 50
        self.previous_timenow = -1
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
        timenow, on_off, notenum, velocity = osc_data # unpack the OSC data, must have the same number of variables as we have items in the data
        #index = int(index)
        if on_off > 0:
            logging.debug(f'received: {self.index}, {timenow:.2f}, {on_off}, {notenum}, {velocity}')
        else:
            logging.debug(f'received: {self.index-1}, {timenow:.2f}, {on_off}, {notenum}, {velocity}')
        
        # timenow == -1 is a phrase termination event, skip storing event data, just trigger chunk_analysis_event()
        # And: if delta time > threshold (2 sec), terminate previous chunk and start a new one
        phrase_division_time = 2
        if ((timenow-self.previous_timenow) > phrase_division_time) and (self.index > 0) and (on_off > 0):
            # terminate previous phrase
            analysis_event = self.chunk_analysis_event(-1)
            self.update_corpus(analysis_event, self.index-1)
            self.set_corpus_last_event(self.index-1)
            self.phrase_number += 1
            self.analysis_chunk = [] # no reconciliation across phrase terminations
            self.recent_analyses =[] # as above
            # then go on with the timestamp, creating a new phrase
        self.previous_timenow = timenow
        if timenow >= 0:
            if on_off == 0:
                self.dc.corpus[self.index-1, self.dc.pnum_corpus['time_off']] = timenow
            elif on_off == 1:
                if self.index == 0:
                    self.dc.corpus[self.index, self.dc.pnum_corpus['timestamp']] = timenow
                    self.dc.corpus[self.index, self.dc.pnum_corpus['notenum']] = notenum
                    self.dc.corpus[self.index, self.dc.pnum_corpus['velocity']] = velocity
                else:
                    if timenow < (self.dc.corpus[self.index-1, self.dc.pnum_corpus['timestamp']] + (self.minimum_delta_time/1000)):
                        timenow += (self.minimum_delta_time/1000) # set minimum delta time
                    self.dc.corpus[self.index,self.dc.pnum_corpus['timestamp']] = timenow
                    self.dc.corpus[self.index,self.dc.pnum_corpus['index']] = self.index
                    self.dc.corpus[self.index, self.dc.pnum_corpus['notenum']] = notenum
                    self.dc.corpus[self.index, self.dc.pnum_corpus['velocity']] = velocity
                    # relative notenumber and velocity
                    if self.previous_notenum > -1:
                        self.dc.corpus[self.index, self.dc.pnum_corpus['notenum_relative']] = notenum-self.previous_notenum
                    if self.previous_velocity > -1:
                        self.dc.corpus[self.index, self.dc.pnum_corpus['velocity_relative']] = velocity-self.previous_velocity
                self.previous_notenum = notenum
                self.previous_velocity = velocity
                analysis_event = self.chunk_analysis_event(timenow)
                self.update_corpus(analysis_event, self.index)
        else:
            # when terminating phrase:
            analysis_event = self.chunk_analysis_event(-1)
            self.update_corpus(analysis_event, self.index-1)
            self.set_corpus_last_event(self.index-1)
            self.phrase_number += 1
            self.analysis_chunk = [] # no reconciliation across phrase terminations
            self.recent_analyses =[] # as above
        if (timenow >= 0) and (on_off > 0):
            self.index += 1 # only increment for on events
    
    def receive_eventchord(self, unused_addr, *osc_data):
        '''Receive chord data, i.e. when several notes occur simultaneously (within time window of i.e. 50 ms) in the input data'''
        index, chord_index, note, velocity, delta_time = osc_data
        index = int(index)
        chord_index = int(chord_index)
        self.dc.corpus[index, self.dc.pnum_corpus['chord_index']] = chord_index # 1-indexed, as zero means no chord
        base_note = self.dc.corpus[index, self.dc.pnum_corpus['notenum']] 
        base_velocity = self.dc.corpus[index, self.dc.pnum_corpus['velocity']]
        if base_velocity == 0: base_velocity=90
        chord_note = [note-base_note, velocity/base_velocity, delta_time]
        if len(self.dc.chord_list) < chord_index:
            self.dc.chord_list.append([chord_note]) # the first note in a chord
        else:
            self.dc.chord_list[chord_index-1].append(chord_note) # next notes in previously existing chord

    def chunk_analysis_event(self, t_event, chunk_size=5):
        # Receive time events one by one, split it into chunks and analyze each chunk.
        # Return duration pattern, deviation, and tempo for the analyzed chunks
        # If we make more than one chunk: Reconcile chunks and return common dur_pattern, deviation, tempo

        # The chunks will be overlapping by one event ([1,2,3,4],[4,5,6,7])
        # When we have a full chunk size of events: analyze
        # On last event: 
        #   - if we have already analyzed: pass
        #   - if there are any events not yet analyzed: analyze the last chunk again, including these events
        #   - if too few events altogether, print warning and exit
        # If more than one phrase since chunk closed: Reconcile phrases
 
        new_analysis = False
        if t_event >= 0:
            print(f'appending {t_event} to analysis chunk')
            self.analysis_chunk.append(t_event)
            print('analysis chunk', self.analysis_chunk)
            if (len(self.analysis_chunk) == (chunk_size*2)-1): #if we have enough for two chunks...
                self.analysis_chunk = self.analysis_chunk[chunk_size-1:] # the first one have already been analyzed
            if (len(self.analysis_chunk) == chunk_size):
                print('*\nanalyze', np.array(self.analysis_chunk), '\n at index', self.index)
                analysis = self.ra.analyze(np.array(self.analysis_chunk))
                self.recent_analyses.append(analysis)
                new_analysis = True
                if (len(self.recent_analyses) > 2):
                    self.recent_analyses = self.recent_analyses[-2:] # keep only two last phrases
        if t_event < 0: # on sequence termination
            if len(self.analysis_chunk) == chunk_size:
                pass # already analyzed
            elif len(self.analysis_chunk) > chunk_size:
                print('*\nanalyze2', np.array(self.analysis_chunk), '\n at index', self.index)
                analysis = self.ra.analyze(np.array(self.analysis_chunk))
                new_analysis = True
                self.recent_analyses[-1] = analysis # replace the last analysis
            else: 
                print(f'Not enough time data to analyze {self.analysis_chunk}')
            self.analysis_chunk = []
        if new_analysis:
            #best1 = self.recent_analyses[0][0]
            #dur_pat1 = self.recent_analyses[0][3][best1]
            if len(self.recent_analyses) == 2:
                #best2 = self.recent_analyses[1][0]
                #dur_pat2 = self.recent_analyses[1][3][best2]
                #print(f'**reconciling 2 phrases: \n{dur_pat1} \n{dur_pat2}')
                durs_devs_tpo = self.ra.analysis_reconcile(self.recent_analyses, prev_tempo=self.prev_tempo)
                self.prev_tempo = durs_devs_tpo[2]
                #print('reconciled:', durs_devs_tpo)
                return analysis, durs_devs_tpo
            else: return analysis
        else: return None
    
    def update_corpus(self, analysis_event, index):
        print('update_corpus()', analysis_event, index)
        if not analysis_event:
            pass
        else: 
            if len(analysis_event) == 7: # single analysis
                self.update_corpus_single_analysis(analysis_event, index)
            if len(analysis_event) == 2: # reconciled analysis
                print('***reconciled analysis***', analysis_event)
                self.update_corpus_single_analysis(analysis_event[0], index)
                dur_pattern = analysis_event[1][0]
                tempo = analysis_event[1][2]
                print('reconciled dur pattern', dur_pattern)
                print('reconciled tempo', tempo)
                corp_indx = index-(len(dur_pattern))
                for d in dur_pattern:
                    print(f'rewrite corpus with reconciled dur {d} at index{corp_indx}')
                    self.dc.corpus[corp_indx,self.dc.pnum_corpus['rhythm_subdiv']] = d
                    self.dc.corpus[corp_indx,self.dc.pnum_corpus['tempo']] = tempo
                    # REWRITE probabilistic model encoding for the new interpretation
                    # self.pl.reanalyze_single_event(indx)
                    corp_indx += 1
                # rewrite tempo and duration pattern for previous events in corpus
                # for each event, check tempo factor and tolerance
                # if tolerance ok, multiply dur with tempo_factor, then write new dur and tempo
                # if tolerance not ok, stop
                tmpo_rewrite_index = index-(len(dur_pattern))
                tmpo_tolerance = 0.33
                while tmpo_rewrite_index > 0:
                    prev_tempo = self.dc.corpus[tmpo_rewrite_index-1,self.dc.pnum_corpus['tempo']]
                    if prev_tempo == 0: prev_tempo = 1
                    tempo_factor = self.dc.corpus[tmpo_rewrite_index,self.dc.pnum_corpus['tempo']] / prev_tempo
                    tempo_dev = round(tempo_factor)-tempo_factor
                    if tempo_dev < tmpo_tolerance:
                        self.dc.corpus[tmpo_rewrite_index-1,self.dc.pnum_corpus['rhythm_subdiv']] *= round(tempo_factor) # rewrite dur
                        self.dc.corpus[tmpo_rewrite_index-1,self.dc.pnum_corpus['tempo']] *= round(tempo_factor) # rewrite tempo
                        # REWRITE probabilistic model encoding for the new interpretation
                        # self.pl.reanalyze_single_event(indx)
                    else:
                        break # stop rewriting if we encounter incompatible tempi
                    tmpo_rewrite_index -= 1                

    def update_corpus_single_analysis(self, analysis, index):
        # Update corpus with analyzed data
        best, pulse, pulsepos, duration_patterns, deviations_, scores, tempi = analysis
        duration_pattern = duration_patterns[best]
        deviations = deviations_[best]
        print(f'dur pattern {duration_pattern}')
        print(f'deviations {deviations}')
        deviation_polarity = self.ra.get_deviation_polarity(deviations, 0.01)
        tempo = tempi[best]
        print(f'subdiv tempo {tempo}')
        print(f'pulse subdiv {pulse}, start position {pulsepos}')
        # return tempo to client
        returnmsg = tempo, pulse, len(duration_pattern) # tempo and phrase length
        osc_io.sendOSC("python_other", returnmsg) # send OSC back to client
        
        # store the data for each event in the corpus
        for i in range(len(duration_pattern)): 
            indx = index - len(duration_pattern) + i
            print('update_corpus_single: index:', indx)
            self.dc.corpus[indx,self.dc.pnum_corpus['index_test']] = indx
            self.dc.corpus[indx,self.dc.pnum_corpus['phrase_num']] = self.phrase_number
            self.dc.corpus[indx,self.dc.pnum_corpus['rhythm_subdiv']] = duration_pattern[i]
            self.dc.corpus[indx,self.dc.pnum_corpus['deviation']] = deviations[i]
            self.dc.corpus[indx,self.dc.pnum_corpus['deviation_polarity']] = deviation_polarity[i]
            self.dc.corpus[indx,self.dc.pnum_corpus['tempo']] = tempo
            # event duration relative to time until next event
            self.dc.corpus[indx,self.dc.pnum_corpus['duration']] = \
                ((self.dc.corpus[indx,self.dc.pnum_corpus['time_off']] \
                - self.dc.corpus[indx,self.dc.pnum_corpus['timestamp']]) \
                / (self.dc.corpus[indx+1,self.dc.pnum_corpus['timestamp']] \
                - self.dc.corpus[indx,self.dc.pnum_corpus['timestamp']]))
            # probabilistic model encoding
            self.pl.analyze_single_event(indx)
        
    def set_corpus_last_event(self, indx):
        # set data for last event
        print('set_corpus_last_event()', indx)
        tempo = self.dc.corpus[indx-1,self.dc.pnum_corpus['tempo']] # take tempo from second last event
        self.dc.corpus[indx,self.dc.pnum_corpus['tempo']] = tempo
        seconds_per_beat = 60/tempo
        print(f"last event tempo {tempo}, spb {seconds_per_beat}, timestamp {self.dc.corpus[indx,self.dc.pnum_corpus['timestamp']]} time_off {self.dc.corpus[indx,self.dc.pnum_corpus['time_off']]}")
        duration_last = ((self.dc.corpus[indx,self.dc.pnum_corpus['time_off']] \
                    - self.dc.corpus[indx,self.dc.pnum_corpus['timestamp']]) \
                    / seconds_per_beat)    
        self.dc.corpus[indx,self.dc.pnum_corpus['duration']] = duration_last
        subdiv = round(duration_last)
        if subdiv < 1: subdiv = 1
        self.dc.corpus[indx,self.dc.pnum_corpus['rhythm_subdiv']] = subdiv

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
            print('Clear last recorded phrase: NOT IMPLEMENTED')
            #for i in self.last_analyzed_phrase:
            #    self.dc.clear_corpus_item(i)
            #self.phrase_number -= 1
            #if self.phrase_number < 0: 
            #    self.phrase_number = 0
            #self.pl.clear_phrase(self.last_analyzed_phrase)
        if clear_all > 0:
            print('CLEAR CORPUS')
            self.dc.clear_corpus()
            #self.pending_analysis = []
            self.phrase_number = 0
            self.pl.clear_all()
            self.previous_notenum = -1
            self.previous_velocity = -1
            self.index = 0
        if save_all > 0:
            self.dc.save_corpus()
            self.pl.save_all()

    def receive_parameter_controls(self, unused_addr, *osc_data):
        '''Message handler. This is called when we receive an OSC message'''
        # set control parameters, like score weights etc
        kdev_vs_complexity, ksimplify, krhythm_order, \
            kdeviation_order, knotenum_order, kinterval_order, kchord_on = osc_data
        
        self.ra.set_precision(kdev_vs_complexity)
        self.ra.set_simplify(ksimplify)

        self.pl.set_weights_pname('rhythm_subdiv', krhythm_order)         
        self.pl.set_weights_pname('deviation_polarity', kdeviation_order) 
        self.pl.set_weights_pname('notenum', knotenum_order) 
        self.pl.set_weights_pname('notenum_relative', kinterval_order)
        self.chord_on = kchord_on 
        logging.debug('receive_parameter_controls {}'.format(osc_data))

    def start_server(self):
        osc_io.dispatcher.map("/client_eventdata", self.receive_eventdata) # here we assign the function to be called when we receive OSC on this address
        osc_io.dispatcher.map("/client_eventchord", self.receive_eventchord) 
        #osc_io.dispatcher.map("/client_analyze_trig", self.analyze) # 
        osc_io.dispatcher.map("/client_parametercontrols", self.receive_parameter_controls) # 
        osc_io.dispatcher.map("/client_memory", self.eventdata_admin) # 
        osc_io.dispatcher.map("/client_prob_gen", self.pl_generate) # 
        osc_io.dispatcher.map("/client_print", self.printstuff) # 
        osc_io.asyncio.run(osc_io.run_osc_server()) # run the OSC server and client

