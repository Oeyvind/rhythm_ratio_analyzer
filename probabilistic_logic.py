#!/usr/bin/python
# -*- coding: latin-1 -*-

""" 
Probabilistic logic

Can be thought of as a "multidimensional variable order markov chain generator".

@author: Øyvind Brandtsegg 2024
@contact: obrandts@gmail.com
@license: GPL
"""

import numpy as np 
np.set_printoptions(suppress=True)
np.set_printoptions(precision=2)
import json

class Probabilistic_encoder:
    # the basic core functionality of registering the order in which symbols appear

    def __init__(self, size=100, max_order=2, name='noname'): 
        self.stm = {} # state transition matrix in the form key:index_container, where the value contains an array of ones and zeros indicating presence
        self.size = size
        self.max_order = max_order # we use this to pad the index_container, so we later can use array views for higher order lookup
        self.empty_index_container = np.zeros(self.size+max_order, dtype=np.float32) 
        self.wraparound = 1 # wraparound or random choice on dead end
        self.wraparound_index_container = np.copy(self.empty_index_container)
        self.wraparound_index_container[max_order] = 1 # to use for avoiding dead ends
        self.previous_item = None 
        self.name = name # just for debugging printing

    def analyze(self, item, index):
        if self.previous_item == None: # first item received is treated differently
            self.previous_item = item
            return
        else: # all next items are analyzed, stored as possible successors to the previous note
            if self.previous_item not in self.stm.keys():
                index_container = np.copy(self.empty_index_container)
                index_container[index+self.max_order] = 1
                self.stm[self.previous_item] = index_container
            else:
                self.stm[self.previous_item][index+self.max_order] = 1
            self.previous_item = item

    def next_items(self, previous=None):
        # as we are live recording items for analysis, dead ends are likely, and needs to be dealt with
        if previous and (previous not in self.stm.keys()):
            if self.wraparound == 1:
                #print(f'Prob_encoder: {self.name} dead end at key {previous}, wrap around ')
                #print(f'key: {previous}, allkeys: {self.stm.keys()}')
                return self.wraparound_index_container
            else:
                #print(f'Prob_encoder: {self.name} dead end at key {previous}, choose randomly')
                #print(f'key: {previous}, allkeys: {self.stm.keys()}')
                return self.empty_index_container
        
        if len(self.stm.keys()) == 0:
            print('Empty Prob sequence')
            return [-1.0]
        # for the very first item, if we do not have any previous note, so let's choose one randomly
        # same applies if we ask for a nonexisting key
        if (previous == None) or (previous not in self.stm.keys()):
            #print(f'Prob_encoder: {self.name} previous {previous} not in stm.keys')
            alternatives = self.empty_index_container
        else:
            alternatives = self.stm[previous] # get an index container of possible next items
        return alternatives
    
    def clear(self):
        self.stm = {}
        self.previous_item = None 
    
    def clear_phrase(self, indices):
        # clear last recorded phrase
        for key in self.stm.keys():
            for i in indices:
                self.stm[key][i+self.max_order] 
        self.previous_item == None

        
class Probabilistic_logic:
    # coordinate several queries (different orders, and different dimensions/parameters) to the Probabilistic encoder

    def __init__(self, dc, max_size=100, max_order=2, max_voices=10):
        self.maxsize = max_size # allocate more space than we need, we will add more data later
        self.max_order = max_order
        self.dc = dc #pointer to data containers
        
        # get number of parameters and instantiate analyzer classes
        numparms = 0
        for parm in self.dc.prob_parms.keys():
            numparms += (self.dc.prob_parms[parm][0]+1) # 1 for each order, plus the "request value"
            pe = Probabilistic_encoder(size=self.maxsize, max_order=self.max_order, name=parm)
            self.dc.prob_parms[parm][1] = pe
        self.numparms = numparms
        print('number of parameters in probabilistic logic:', self.numparms)
        
        prob_history = []
        for i in range(self.max_order): prob_history.append(None)
        self.no_prob_history = prob_history.copy()
        self.prob_history = []
        for i in range(max_voices):
            self.prob_history.append(self.no_prob_history) #make separate history for each voice
        self.weights = np.zeros(self.numparms)
        # set default weights to first order for all parameters
        for pname in self.dc.prob_parms.keys():
            self.set_weights_pname(pname, 1, printit=False)
        print(f'prob weights set to {self.weights}')

        # set data and allocate data containers
        self.current_datasize = 0 
        self.indices = self.dc.corpus[:self.current_datasize, self.dc.pnum_corpus['index']]
        self.indx_container = np.zeros(self.maxsize*self.numparms)
        self.indx_container = np.reshape(self.indx_container, (self.maxsize,self.numparms))
        self.indices_prob_temp = np.zeros(self.maxsize+self.max_order)
        self.request_mask = np.zeros(self.maxsize+self.max_order)
        self.prob = np.zeros(self.maxsize)
        
    def analyze_single_event(self, i):
        #print(f'analyze: {self.dc.corpus[i]}')
        for parm in self.dc.prob_parms.keys():
            pe = self.dc.prob_parms[parm][1]
            #print(f'pe.analyze: {pe.name}, {self.dc.corpus[i, self.dc.pnum_corpus[parm]]}')
            pe.analyze(self.dc.corpus[i, self.dc.pnum_corpus[parm]], i)
        self.current_datasize += 1
        self.indices = self.dc.corpus[:self.current_datasize, self.dc.pnum_corpus['index']]

    def set_weights(self, weights):
        self.weights = weights

    def set_weights_pname(self, pname, order, printit=True):
        # set weights according to parameter name and desired order
        if pname in self.dc.prob_parms.keys():
            max_order = self.dc.prob_parms[pname][0]
            if order <= max_order:
                for i in range(1, max_order+1):
                    w_index = self.dc.prob_parms[pname][2][0] + i
                    w = np.clip(1+order-i, 0, 1)
                    self.weights[w_index] = w
                if printit:
                    print(f'prob weights set to {self.weights}')
            else: print(f'max order for {pname} exceeded: WARNING no change in weights applied')
        else: print(f'{pname} not in prob_parms: WARNING no change in weights applied')

    def set_temperature(self, temperature):
        if temperature < 0.001 : temperature = 0.001
        temperature_coef = 1/temperature
        return temperature_coef
       
    def update_history(self, history, new_item):
        history = history[1:]+history[:1] #rotate
        history[-1] = int(new_item) # add most recent INDEX last in list
        for i in range(len(history)-2): # not process the last (newest)
            if not history[i]:
                if history[i+1]:
                    history[i] = history[i+1]-1 # if there is a gap in the history, smooth out
        return history

    def generate(self, query, voice=1, temperature=0.2):
        next_item_index, request_next_item = query
        #print('query', query)
        temperature_coef = self.set_temperature(temperature)
        
        # need to update and keep track of previous events for higher orders
        self.prob_history[voice-1] = self.update_history(self.prob_history[voice-1], next_item_index)

        # get alternatives from Probabilistic encoder
        for parm in self.dc.prob_parms.keys():
            pe = self.dc.prob_parms[parm][1]
            for ord in range(1,self.dc.prob_parms[parm][0]+1): # will skip for specific request (order 0)
                w_index = self.dc.prob_parms[parm][2][ord] #prob weight index
                if self.weights[w_index] != 0:
                    offset = self.max_order+1-ord
                    if not self.prob_history[voice-1][-ord]:
                        query_item = None
                    else:
                        query_item = self.dc.corpus[self.prob_history[voice-1][-ord], self.dc.pnum_corpus[parm]]
                    self.indices_prob_temp = pe.next_items(query_item)[offset:self.current_datasize+offset]
                    self.indx_container[:self.current_datasize, w_index] = self.indices_prob_temp[:self.current_datasize]

        # Scale by weights for each prob dimension and sum: dot product indx_container and weight. Then adjust temperature
        self.prob = np.dot(self.indx_container[:self.current_datasize, :self.numparms], self.weights)
        if np.amax(self.prob) > 0:
            self.prob /= np.amax(self.prob) # normalize
            self.prob = np.power(self.prob, temperature_coef) # temperature adjustment
        else:
            print(f'Prob encoder zero probability from query {query}, choose one at random')
            self.prob = np.ones(self.current_datasize)

        #print('prob and mask:')
        #print(self.prob)
        # if we request a specific item, handle this here 
        if request_next_item[0] != None:
            request_parm, request_code, request_weight = request_next_item
            self.set_request_mask(request_parm, request_code)
            #print(self.request_mask[:self.current_datasize])
            if request_weight == 1:
                self.prob *= self.request_mask[:self.current_datasize]
            else:        
                self.prob = (self.request_mask[:self.current_datasize]*request_weight) + self.prob*(1-request_weight)
            if np.amax(self.prob) == 0: # check to find if no values are available after masking
                print('no prob!')
                self.prob += self.request_mask[:self.current_datasize] # just use mask
        sumprob = np.sum(self.prob)
        self.prob = self.prob/sumprob #normalize sum to 1
        #print('prob again\n', self.prob)
        next_item_index = int(np.random.choice(self.indices,p=self.prob))
        return next_item_index

    def set_request_mask(self, request_parm, request_code):
        # request_parm = parameter name
        # request code = type of request and the value(s) requested
        # type of request (can be exact value, < or > a threshold value, OR a gradient)
        request_type = request_code[0]
        val = request_code[1][0]
        self.request_mask[:self.current_datasize] = 0*self.request_mask[:self.current_datasize]
        if request_parm == 'index':
            keys = self.indices
        else:
            pe = self.dc.prob_parms[request_parm][1]
            keys = np.asarray(list(pe.stm.keys()))
        if request_type == '==':
            if request_parm == 'index':
                val = val%self.current_datasize # wrap index request to available range
                self.request_mask[int(val)] = 1
            else:
                # in case we request a value that is not exactly equal to a key in the stm, we first find the closest match
                # THIS SHOULD BE OPTIONAL, make argument selector to enable (if no exact values found, return flat probability)
                request_next_item_closest = keys[np.abs(val-keys).argmin()]
                print(f'closest val: {request_next_item_closest}')
                offset = self.max_order+1
                request = pe.next_items(request_next_item_closest)[offset:self.current_datasize+offset]
                self.request_mask[:self.current_datasize] += request[:self.current_datasize]
        elif request_type == 'next':
            if request_parm == 'index':
                val = (val+1)%self.current_datasize # wrap index request to available range
                self.request_mask[int(val)] = 1
        elif request_type == 'prev':
            if request_parm == 'index':
                val = (val-1)%self.current_datasize # wrap index request to available range
                self.request_mask[int(val)] = 1
        else: # request type is 'gradient', or > or <
            # For request code 'gradient', '>' or '<', we need to look at the values in the corpus rather than the index containers
            #   A gradient can be aligned to prefer low values or high values, with increasing probability along the gradient
            #   The request mask in this case is not a simple mask, but a floating point probability. Still using the same size and format as the request mask.
            #   Special treatment of relative pitch, where we might want to request large (or small) intervals, regardless of sign (up or down intervals)
            #   In that case, use absolute values of interval (request code = 'gr_abs').
            # Request code < or > works similarly, but gives a binary mask (over/under threshold)
            pvalues = self.dc.corpus[:, self.dc.pnum_corpus[request_parm]][:self.current_datasize]
            if (request_type == '>') or (request_type == '<'):
                if request_type == '>':
                    pvalues = np.ma.masked_greater_equal(pvalues,val).mask
                else:
                    pvalues = np.ma.masked_less_equal(pvalues,val).mask
            else: # if gradient
                gradient_shape = request_code[1][0] # request value in gui
                if request_type == 'gr_abs':
                    pvalues = np.abs(pvalues)
                amin = np.amin(pvalues)
                pvalues = (pvalues-amin)/np.amax(pvalues-amin)
                if gradient_shape < 0:
                    pvalues = 1-pvalues # invert, we use the shape parameter both to determine gradient direction
                pvalues = np.power(pvalues, abs(gradient_shape)) # ... and powershape
            self.request_mask[:self.current_datasize] = pvalues
        if np.amax(self.request_mask[:self.current_datasize]) == 0: # if all masks are zero
            self.request_mask[:self.current_datasize] += 1 # disable masks
        

    def clear_all(self):
        # clear all prob encoder's stm
        print('clear all prob encoder stm')
        for parm in self.dc.prob_parms.keys():
            pe = self.dc.prob_parms[parm][1]
            pe.clear()
        self.current_datasize = 0
        self.indices = self.dc.corpus[:self.current_datasize, self.dc.pnum_corpus['index']]
    
    def clear_phrase(self, indices):
        # clear last recorded phrase
        for parm in self.dc.prob_parms.keys():
            pe = self.dc.prob_parms[parm][1]
            pe.clear_phrase(indices)
        self.current_datasize -= len(indices)
        self.indices = self.dc.corpus[:self.current_datasize, self.dc.pnum_corpus['index']]
    
    def save_all(self):
        # save all prob encoders to file
        print('attempt prob encoder save to file')
        print('NOT IMPLEMENTED, need to convert stm keys to float')
        return
        data = []
        for parm in self.dc.prob_parms.keys():
            pe = self.dc.prob_parms[parm][1]
            data.append(pe.stm)
        with open("prob_encoders.json", "w") as fp:
            json.dump(data, fp)  
        
    def read_all(self):
        # read all prob encoders from file
        print('attempt prob encoder read from file')
        with open("prob_encoders.json", "r") as fp:
            data = json.load(fp)  
        i = 0
        for parm in self.dc.prob_parms.keys():
            pe = self.dc.prob_parms[parm][1]
            pe.stm = data[i]
            i += 1

#####################################################
# Tests
#####################################################

class Datacontainer_test():
    def __init__(self, max_events, random_population=0): 
        # example with 2D data
        self.pnum_corpus = {
            'index': 0, # register indices for data points currently in use
            'val1' : 1, 
            'val2': 2}
        # corpus is the main data container for events
        self.nparms_corpus = len(self.pnum_corpus.keys())
        # parameter names and max_order in the probabilistic logic module
        # zero order just means give us all indices where the value occurs
        # higher orders similar to markov order
        # the second item in the values is the analyzer instance for that parameter
        # the third is a list of indices used for probability calculation, corresponds to weight indices
        self.prob_parms = {'val1': [2, None, [0,1,2]],
                     'val2': [2, None, [3,4,5]]}

        self.max_events = max_events
        self.corpus = np.zeros((self.max_events, self.nparms_corpus), dtype=np.float32) # float32 faster than int or float64
        
        if random_population == 0:
            self.list_val1 = [1,2,2,1,3,4,5, 3,4,5,-1,-2] 
            self.list_val2 = [1,1,1,1,1,1,1, 2,2,2,2,2] 
        else:
            self.list_val1 = np.random.randint(-10,10,random_population)
            self.list_val2 = np.random.randint(0,10,random_population)

        for i in range(len(self.list_val1)):
            self.corpus[i, self.pnum_corpus['val1']] = self.list_val1[i]
            self.corpus[i, self.pnum_corpus['val2']] = self.list_val2[i]

def encoder_test():
    datasize = 10
    max_order = 2
    pe = Probabilistic_encoder(size=datasize, max_order=max_order)
    data = ('A','B','C','C','B','A')
    indices = np.zeros(datasize+max_order)
    current_datasize = 0
    for i in range(len(data)):
        pe.analyze(data[i],i)
        indices[i+max_order] = i
        current_datasize += 1
    v = ('A')
    temperature_coef = 1
    for i in range(10):
        prob = pe.next_items(v)
        prob /= np.amax(prob) # normalize
        prob = np.power(prob, temperature_coef) # temperature adjustment
        sumprob = np.sum(prob)
        prob = prob/sumprob #normalize sum to 1
        print('prob \n', prob)
        print('indices \n', indices)
        next_item_index = int(np.random.choice(indices,p=prob))
        v = data[next_item_index]
        print(v)

def basic_test():
    max_events = 1000
    dc = Datacontainer_test(max_events)
    pl = Probabilistic_logic(dc, max_size=max_events, max_order=2, max_voices=2)
    for i in range(len(dc.list_val1)):
        dc.corpus[i, dc.pnum_corpus['index']] = i
        pl.analyze_single_event(i)
    print('done analyzing')
    
    #generate
    pl.set_weights_pname('val1', 1.5)
    temperature = 0.2 # low (<1.0) is deterministic, high (>1.0) is more random
    start_index = 0#np.random.choice(indices)
    next_item = dc.corpus[start_index, dc.pnum_corpus['val1']]
    # for debug only
    for parm in dc.prob_parms.keys():
        pe = dc.prob_parms[parm][1]
        # FIX HERE
        print(f'stm for {parm}')
        for key, value in pe.stm.items():
            print(key, value[2:pl.current_datasize+pl.max_order])
    
    # query
    print(f'The first item is {next_item} at index {start_index}')
    query = [start_index, [None]]
                          
    i = 0
    voice = 1
    while i < 10:
        next_item_index = pl.generate(query, voice, temperature) #query probabilistic encoders for next event and update query for next iteration
        query[0] = next_item_index
        print(f"the next item is  {dc.corpus[next_item_index,dc.pnum_corpus['val1']]} at index {next_item_index}, prob {pl.prob}")
        i += 1
    print(f'generated {i} items')
    
    # test voice 2, with request specific value
    print('** Voice2**')
    start_index = 1
    next_item = dc.corpus[start_index, dc.pnum_corpus['val1']]
    print(f'The first item is {next_item} at index {start_index}')
    request_item = 'index'
    request_type = 'values'
    request_value = 1
    request_weight = 0.5
    if request_item: 
        query = [start_index, [request_item, [request_type, [request_value]], request_weight]]
    else: 
        query = [start_index, [None, [0, [0]], 0]]
    i = 0
    voice = 2
    while i < 10:
        next_item_index = pl.generate(query, voice) #query probabilistic encoders for next event and update query for next iteration
        if request_item: 
            request_value = next_item_index+1
            query = [next_item_index, [request_item, [request_type, [request_value]], request_weight]] #request index, and use next_item_index as the value to ask for
        else: query = [next_item_index, [None, [0, [0]], 0]]
        print(f"the next item is  {dc.corpus[next_item_index, dc.pnum_corpus['val1']]} at index {next_item_index}, prob {pl.prob}")
        i += 1
    print(f'generated {i} items')

        
    print(pl.current_datasize)
    #request_next_item = ['index', 1, 0.5]
    #request_next_item = ['val1', ['values', [2.3]], 1] # list of one value
    request_next_item = ['val1', ['values' ,[1,3]], 1] # list of values
    #request_next_item = ['val1', ['>', [2]], 1] #mask high values, e.g. all x > zero
    mask = pl.get_request_mask(request_next_item)
    print('mask of values 1 and 3:\n', mask)

def request_dev():
    max_events = 10
    dc = Datacontainer_test(max_events, random_population=8)
    pl = Probabilistic_logic(dc, max_size=max_events, max_order=2, max_voices=2)
    for i in range(len(dc.list_val1)):
        dc.corpus[i,dc.pnum_corpus['index']] = i
        pl.analyze_single_event(i)
    print('done analyzing')
    print(f'corpus:\n{dc.corpus}')

    request_next_item = ['index', ['==' ,[1]], 1]
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')
    
    request_next_item = ['val1', ['==', [2.3]], 1] # list of one value
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

    request_next_item = ['val1', ['==' ,[1]], 1] # list of values
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

    request_next_item = ['val1', ['>', [2]], 1] #mask high values, e.g. all x > zero
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

    request_next_item = ['val1', ['gradient', [1]], 1] 
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

    request_next_item = ['val1', ['gradient', [2]], 1] 
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

    request_next_item = ['val1', ['gradient', [-2]], 1] 
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

    request_next_item = ['val1', ['gr_abs', [2]], 1] 
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

    request_next_item = ['val1', ['gr_abs', [-2]], 1] 
    print(f'request mask for {request_next_item}:')
    mask = pl.get_request_mask(request_next_item)
    print(f'mask: {mask}')

# test
if __name__ == '__main__' :
    encoder_test()
    #basic_test()
    #request_dev()
    # profiling tests
    #import cProfile
    #cProfile.run('pl.get_request_mask(request_next_item)')

    #        if previous == None:
