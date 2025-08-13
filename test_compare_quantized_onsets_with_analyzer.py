from mido import MidiFile
import main as m
import sys
import numpy as np
np.set_printoptions(legacy='1.25')
np.set_printoptions(threshold=sys.maxsize)


def get_onsets_from_quantized(testfile, numevents):
    midifile = MidiFile(testfile)
    print('midi file type', midifile.type)
    if numevents == -1:
        numevents = 0
        for msg in midifile:
            if msg.type == 'note_on' and msg.velocity > 0:
                numevents += 1
    print(f'get quantized onsets from {testfile} with {numevents} events')

    # get tempo changes
    tempi = []
    for track in midifile.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempi.append(msg.tempo)  # Tempo is in microseconds per beat
    if tempi == []: tempi.append(500000)
    if len(tempi) > 1:
        print('tempi', tempi)
        print('multiple tempo changes not handled, exiting')
        return []
    tempo_bpm = (60/(tempi[0]/1000000))

    # get onsets
    onsets = []
    i = 0
    delta = 0
    t = 0
    for msg in midifile:
        if msg.type == 'note_on' and msg.velocity > 0:
            msg.time += delta
            t += msg.time
            onsets.append(t*(tempo_bpm/60))
            delta = 0
            i += 1
        else:
            delta += msg.time
        if i > numevents:
            break
    #print('onsets', onsets)
    inter_onsets = []
    q_numevents = 0 # reset numevents to as many events as we find in the quantized file
    for i in range(len(onsets)-1):
        d = onsets[i+1] - onsets[i]
        if d > (m.server.minimum_delta_time/1000):
            inter_onsets.append(d)
            q_numevents += 1
    #print('inter onsets', inter_onsets)
    return np.array(inter_onsets), tempo_bpm, q_numevents

def get_onsets_from_analyzer(testfile, numevents):
    midifile = MidiFile(testfile)
    print('midi file type', midifile.type)
    if numevents == -1:
        numevents = 0
        for msg in midifile:
            if msg.type == 'note_on' and msg.velocity > 0:
                numevents += 1
    print(f'get analyzer onsets from {testfile} with {numevents} events')
    unused_addr = ''
    i = 0
    delta = 0
    t = 0
    t_prev = -1
    for msg in midifile:
        if msg.type == 'note_on' and msg.velocity > 0:
            msg.time += delta
            t += msg.time
            if t-t_prev > (m.server.minimum_delta_time/1000):
                osc_data = (t, 1, msg.note, msg.velocity)
                m.server.receive_eventdata(unused_addr, *osc_data) # on event
                osc_data = (t+0.05, 0, msg.note, msg.velocity)
                m.server.receive_eventdata(unused_addr, *osc_data) # off event
                delta = 0
                t_prev = t
            i += 1
        else:
            delta += msg.time
        if i > numevents:
            break
    # terminate last phrase
    osc_data = (-1, -1, 1, 1)
    m.server.receive_eventdata(unused_addr, *osc_data) # terminate last phrase
    tempo_bpm = m.dc.corpus[numevents-1,14]
    return m.dc.corpus[:numevents,4], tempo_bpm

#
# for testing, supply command line argument to specify data file for testing
if not len(sys.argv) == 4:
    print('need 3 arguments: midi file name quantized,  midi file performed, and num events (numevents = -1 use all events)')
    sys.exit()

analyze_file = sys.argv[1]
quantized_file = sys.argv[2]
numevents = int(sys.argv[3])

# get quantized onsets from file (must do first, as we will limit numevents to as many events we found here)
quantized_onsets, q_tempo_bpm, q_numevents = get_onsets_from_quantized(quantized_file, numevents)
# run midi file with analyzer
analyzer_onsets, a_tempo_bpm = get_onsets_from_analyzer(analyze_file, q_numevents)
# compare
print('\nCompare onsets from analyzer with quantized onsets in file:')
#print('analyzer_onsets', analyzer_onsets)
#print('quantized_onsets', quantized_onsets)

def compare_onsets(analyzer_onsets, quantized_onsets):
    # allow tempo mismatch with an integer factor of 2 in both directions
    n = np.sum(analyzer_onsets == quantized_onsets)
    n1 = np.sum(analyzer_onsets*2 == quantized_onsets) # analyzer has half tempo
    n2 = np.sum(analyzer_onsets == quantized_onsets*2) # analyzer has double tempo
    res = np.array([n,n1,n2])
    num_correct = np.max(res)
    tempo_error = np.argmax(res)
    tempo_errors = ['the same', 'half', 'double']
    print(f'Onset comparison gives {num_correct} out of {len(analyzer_onsets)} events. Correlation: {(num_correct/len(analyzer_onsets))*100:.2f} per cent')
    print(f'Analyzer interprets the beat as {tempo_errors[tempo_error]} tempo as the quantized file')

compare_onsets(analyzer_onsets, quantized_onsets)
