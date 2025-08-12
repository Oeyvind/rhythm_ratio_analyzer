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
from mido import MidiFile

# for testing, supply command line argument to specify data file for testing
if not len(sys.argv) == 3:
    print('need 2 arguments: midi file and num events')
    sys.exit()

testfile = './test_data/'+sys.argv[1]
midifile = MidiFile(testfile)
print('midi file type', midifile.type)
numevents = int(sys.argv[2])
if numevents == -1:
    numevents = len(testfile)
print(f'testing with midi read from {testfile} with {numevents} events')
unused_addr = ''
i = 0
delta = 0
t = 0
for msg in midifile:
    if msg.type == 'note_on' and msg.velocity > 0:
        msg.time += delta
        t += msg.time
        print(msg, t)
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
        
print(m.dc.pnum_corpus.keys())

# print corpus
with np.printoptions(precision=2, suppress=True):
    print(m.dc.corpus[:20])
