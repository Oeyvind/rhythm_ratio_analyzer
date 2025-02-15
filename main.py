#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Main program, runs the rhythm_osc_server and probabilistic logic modules

@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import data_containers
import ratio_analyzer 
import probabilistic_logic
import osc_server

# instantiate data containers
dc = data_containers.DataContainers()

# instantiate probabilistic logic
pl = probabilistic_logic.Probabilistic_logic(dc, max_size=100, max_order=4, max_voices=10)

# instantiate and start osc server
server = osc_server.Osc_server(dc, ratio_analyzer, pl)
server.start_server()