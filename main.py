#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Main program, runs the rhythm_osc_server and probabilistic logic modules

@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import data_containers as dc 
import ratio_analyzer 
import probabilistic_logic
import rhythm_osc_server

# instantiate probabilistic logic
pl = probabilistic_logic.Probabilistic_logic(dc.corpus, dc.pnum_corpus, dc.pnum_prob, d_size2=2, max_size=100, max_order=4, hack=2)

# instantiate and start osc server
server = rhythm_osc_server.Osc_server(dc.corpus, dc.pnum_corpus, ratio_analyzer, pl)
server.start_server()