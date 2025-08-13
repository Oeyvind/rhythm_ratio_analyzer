from mido import MidiFile
#import pretty_midi
import sys
import numpy as np
np.set_printoptions(legacy='1.25')
np.set_printoptions(threshold=sys.maxsize)

# for testing, supply command line argument to specify data file for testing
if not len(sys.argv) == 3:
    print('need 2 arguments: midi file name and num events (numevents = -1 use all events)')
    sys.exit()

testfile = './test_data/'+sys.argv[1]
midifile = MidiFile(testfile)
print('midi file type', midifile.type)
numevents = int(sys.argv[2])
if numevents == -1:
    numevents = len(testfile)
print(f'testing with midi read from {testfile} with {numevents} events')

# get tempo changes
tempi = []
for track in midifile.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempi.append(msg.tempo)  # Tempo is in microseconds per beat
if tempi == []: tempi.append(500000)
print('tempi', tempi, (60/(tempi[0]/1000000)))
if len(tempi) > 1:
    print('multiple tempo changes not handled, exiting')
    sys.exit()

# get onsets
onsets = []
i = 0
delta = 0
t = 0
for msg in midifile:
    if msg.type == 'note_on' and msg.velocity > 0:
        msg.time += delta
        t += msg.time
        onsets.append(t*(1/(tempi[0]/1000000)))
        delta = 0
        i += 1
    else:
        delta += msg.time
    if i > numevents:
        break
print('onsets', onsets)
inter_onsets = []
for i in range(len(onsets)-1):
    d = onsets[i+1] - onsets[i]
    if d > 0:
        inter_onsets.append(d)
print('inter onsets', inter_onsets)
