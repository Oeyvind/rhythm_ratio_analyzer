#!/usr/bin/python
# -*- coding: latin-1 -*-

# Rhythm ratio analyzer test scripts
# Oeyvind Brandtsegg 2024

import numpy as np
np.set_printoptions(suppress=True)
import ratio_analyzer as ra

def make_time_from_beats(beats,subdiv):
  timestamp = [0]
  for b in beats:
    t = timestamp[-1]
    timestamp.append(t+(b/subdiv))
  return np.array(timestamp)

def make_correct_answer(beats, subdiv):
  answer = []
  for b in beats:
     answer.append([b,subdiv])
  return answer

if __name__ == '__main__':
  beats = [3,3,2]
  subdiv = 4
  t = make_time_from_beats(beats, subdiv)
  print(f'{beats} \n{t}')
  answer = make_correct_answer(beats, subdiv)
  benni_weight = 1
  nd_sum_weight = 1
  ratio_dev_weight = 0.3
  ratio_dev_abs_max_weight = 1
  grid_dev_weight = 0.2
  evidence_weight = 0.3
  autocorr_weight = 1
  weights = [benni_weight, nd_sum_weight, ratio_dev_weight, ratio_dev_abs_max_weight, grid_dev_weight, evidence_weight, autocorr_weight]
  ra.set_weights(weights)
  rank = 1
  ratios_reduced, ranked_unique_representations, trigseq, ticktempo_bpm, tempo_tendency, pulseposition = ra.analyze(t, rank)
  best = ranked_unique_representations[0]
  ratios_list = ratios_reduced[best].tolist()
  print('best')
  for i in range(len(ratios_list)):
      print(f'{int(ratios_list[i][0])}/{int(ratios_list[i][1])}')
  next_best = ranked_unique_representations[1]
  ratios_list = ratios_reduced[best].tolist()
  print('second_best')
  for i in range(len(ratios_list)):
      print(f'{int(ratios_list[i][0])}/{int(ratios_list[i][1])}')
  print('answer')
  for a in answer:
     print(f'{a[0]}/{a[1]}')