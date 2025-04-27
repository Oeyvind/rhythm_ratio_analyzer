#!/usr/bin/python
# -*- coding: latin-1 -*-

from midiutil import MIDIFile
import numpy as np

pitch = 60
velocity = 100
channel = 0
time = 0  # In beats
duration = 0.5 # relative duration  
track = 0
tempo    = 120   # In BPM
MyMIDI = MIDIFile(1)
MyMIDI.addTempo(track, time, tempo)

timeseries = np.array([0., 0.734, 1.512, 2.497, 3.256, 4.025, 4.252, 4.5, 5.009, 5.54 ])
timeseries = np.array([0.0, 0.7249959482178304, 1.4939843381306637, 2.4576872877355918, 3.292096246752668, 3.988235826245749, 4.20001517849765, 4.44348514735324, 4.969086229162556, 5.483582228526372])
#timeseries = np.array([0,1,2,3,4,5])
deltas = np.diff(timeseries)
    
for d in deltas:
    MyMIDI.addNote(track, channel, pitch, time, d*duration, velocity)
    time += d
MyMIDI.addNote(track, channel, pitch, time, d*duration, velocity) # last event

with open("midi_timeseries.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
print('midi file written')