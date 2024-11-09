#!/usr/bin/python
# -*- coding: latin-1 -*-

#import markov_model as mm
import numpy as np
np.set_printoptions(suppress=True)

import json
# test
if __name__ == '__main__' :
    with open('testdata_rhythm3_clave.json', 'r') as filehandle:
      jsondict = json.load(filehandle)
    datasize = len(jsondict['0']['ratios'])
    data = np.empty((4,datasize),dtype='float')
    #print(jsondict['1'])
    for i in range(len(jsondict['0']['ratios'])):
       ratio_float1 = jsondict['0']['ratios'][i][0]/jsondict['0']['ratios'][i][1]
       ratio_float2 = jsondict['1']['ratios'][i][0]/jsondict['1']['ratios'][i][1]
       data[0,i] = ratio_float1
       data[1,i] = ratio_float2
    pulsepos1 = jsondict['0']['pulsepos']
    beat_weight1 = jsondict['0']['autocorr'][0::pulsepos1]
    pulsepos2 = jsondict['1']['pulsepos']
    beat_weight2 = jsondict['1']['autocorr'][0::pulsepos2]
    #data[2] = beat_weight1
    #data[3] = beat_weight2
    print(data)
    print(beat_weight1)
    #print(beat_weight2)
