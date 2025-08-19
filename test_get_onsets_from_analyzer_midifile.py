#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Test the rhythm analyzer on a midi file
@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import main as m
import sys
import numpy as np
np.set_printoptions(threshold=np.inf) 
from mido import MidiFile

def get_onsets_from_analyzer(testfile, numevents, force_tempo):
    midifile = MidiFile(testfile)
    print('midi file type', midifile.type)
    if numevents == -1:
        numevents = len(testfile)
    print(f'get analyzer onsets from {testfile} with {numevents} events')
    m.server.force_tempo = force_tempo
    unused_addr = ''
    i = 0
    delta = 0
    t = 0
    for msg in midifile:
        if msg.type == 'note_on' and msg.velocity > 0:
            msg.time += delta
            t += msg.time
            osc_data = (t, 1, msg.note, msg.velocity)
            m.server.receive_eventdata(unused_addr, *osc_data) # on event
            osc_data = (t+0.05, 0, msg.note, msg.velocity)
            m.server.receive_eventdata(unused_addr, *osc_data) # off event
            delta = 0
            i += 1
        else:
            delta += msg.time
        if i > numevents:
            # terminate last phrase
            osc_data = (-1, -1, 1, 1)
            m.server.receive_eventdata(unused_addr, *osc_data) # terminate last phrase
            break
    print(m.dc.corpus[:numevents])
    return m.dc.corpus[:numevents+1,4]

#
# for testing, supply command line argument to specify data file for testing
if not len(sys.argv) == 4:
    print('need 3 arguments: midi file name, num events (numevents = -1 use all events), and force_tempo')
    sys.exit()

testfile = sys.argv[1]
numevents = int(sys.argv[2])
force_tempo = int(sys.argv[3])
analyzer_onsets = get_onsets_from_analyzer(testfile, numevents, force_tempo)
print('analyzer_onsets \n', analyzer_onsets)


