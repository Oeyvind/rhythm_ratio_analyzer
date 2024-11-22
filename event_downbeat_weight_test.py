#!/usr/bin/python
# -*- coding: latin-1 -*-

#import markov_model as mm
import numpy as np
np.set_printoptions(suppress=True)
import ratio_analyzer as r

if __name__ == '__main__' :
  # so far no luck, fails for many sequences, works for some very simple ones

  # things to try:
  # weight the autocorrealation over time
  # linear weight (linspace) seems to do something good, but select 12 length over 8 length (maybe reasonable with the test data)
  # mask the n first values of the autocorr, removing lengths that we cetrainly does not want
  # - here we assume that we are looking for something like a "bar" with length n subdivisions, usually at least 6 or 8 subdivisions long
  # Try to find the masking length from the length of the input data?
  #  - f.ex. mask length = half the length of the input data
  #  - we might also "fade in" (linspace) over this mask length **TRY THIS!**

  duration_list = [3,3,4,2,4,3,3,4,2,4,1] # fails, autocorr length 6 should be 4, and heavy n5 of the 6
  # it also fails if we force the pulsepos = 4, as we have more events on the beat 4

  duration_list = [4,2,2,4,1,1,1,1,2,2,1] # fails, too short autocorr: length:2
  # it also fails if we force the pulsepos = 4, as we have more events on the beat 3

  duration_list = [4,2,2,4,1,1,2,3,1,4] # works
  duration_list = [4,2,2,4,3,1,3,1,4] # works
  duration_list = [4,2,1,1,2,2,3,1,4] # works

  duration_list = [1,4,2,1,1,2,2,3,1,4] # fails to notice upbeat 
  duration_list = [1,4,4,2,2,4,4] # also fails to notice upbeat]
  duration_list = [2,4,4,4,2,4,4,] # upbeat removal test, sum every n (pulsepos) of autocorr
  #print(duration_list)
  duration_list = duration_list[1:]+duration_list[:1]
  print(duration_list)
  duration_list = [3,3,2,3,3,2,4] # tresillo, fails
  #duration_list = [1,1,1,1,2,2,1,1,1,1,2,2,4,4]
  
  seqlen = len(duration_list)
  ratios= np.ones(seqlen*2)
  ratios = np.reshape(ratios, (seqlen,2)) 
  ratios[:,0] = duration_list
  triggerseq = r.make_trigger_sequence(ratios)
  print(triggerseq)
  acorr = r.autocorr(triggerseq)
  print(acorr)
  acorr[0] = 0
  acorr_fadein_len = int(len(acorr)/2)
  acorr_fadein = np.linspace(0,1,num=acorr_fadein_len)
  acorr_weight = np.ones(len(acorr))
  acorr_weight[:acorr_fadein_len] = acorr_fadein
  acorr_weighted = acorr*acorr_weight
  pulsepos = np.argmax(acorr)
  pulseposes = np.where(acorr == acorr.max())
  aw_pulsepos = np.argmax(acorr_weighted) # this MIGHT be something, emphasizing correlations over longer time spans
  print(pulsepos, pulseposes, aw_pulsepos, np.sum(acorr_weighted)/np.sum(triggerseq))
  dweight = np.zeros(aw_pulsepos)
  i = 0
  while i < np.floor((len(acorr)/aw_pulsepos)):
    dweight += (acorr_weighted[i*aw_pulsepos:(i*aw_pulsepos)+aw_pulsepos])
    i += 1
  print(dweight)


