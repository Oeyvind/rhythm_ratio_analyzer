#!/usr/bin/python
# -*- coding: latin-1 -*-

from mido import MidiFile
import numpy as np

mid = MidiFile('./test_data/Shi05M.mid')
print('midi file type', mid.type)
i = 0
delta = 0
t = 0
for msg in mid:
    if msg.type == 'note_on' and msg.velocity > 0:
        msg.time += delta
        t += msg.time
        print(msg, t)
        delta = 0
        i += 1
    else:
        delta += msg.time
    if i > 15:
        break
