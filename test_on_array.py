#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Test the rhythm analyzer on an array of onset times
@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import main as m
import sys
import numpy as np

# for testing, supply command line argument to specify data file for testing
if len(sys.argv) > 1:
    testfile = './test_data/'+sys.argv[1]
    test_arr = np.load(testfile)
    numevents = int(sys.argv[2])
    if numevents == -1:
        numevents = len(testfile)
    print(f'testing with array read from {testfile} with {numevents} events')
    for i in range(numevents):
        unused_addr = ''
        osc_data = (test_arr[i], 1, 60, 90)
        m.server.receive_eventdata(unused_addr, *osc_data) # on event
        osc_data = (test_arr[i]+0.05, 0, 60, 90)
        m.server.receive_eventdata(unused_addr, *osc_data) # off event
    # terminate last phrase
    osc_data = (-1, -1, 60, 90)
    m.server.receive_eventdata(unused_addr, *osc_data) # terminate last phrase
    print(m.dc.pnum_corpus.keys())
    
    # print corpus
    with np.printoptions(precision=2, suppress=True):
        print(m.dc.corpus[:20])
