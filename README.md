# rhythm_ratio_analyzer
Analyze a time series in terms of rational relationships between delta times. Generate new rhythms based on analysis.
The program runs as a server, and we can use a VST plugin or other external program as a client.
Communication between client and server over OSC.

Øyvind Brandtsegg & Daniel Formo, NTNU. 
Developed 2016-2024

The files:  
**main.py** - the main python file, run this to start everything
**data_containers.py** - data containers for event corpus and probabilistic logic
**ratio_analyzer.py** - the ratio analyzer methods  
**rhythm_osc_server.py** - osc communication (with e.g. a vst plugin), forward calls to ratio_analyzer and probabilistic logic
**osc_io.py** - loaded by rhythm_osc_server.py to handle osc communication  
**rhythm_analyzer_vst.csd** - a simple test VST plugin, taking midi note inputs, communicates with rhythm_osc_server.py for the analysis. Export this as a plugin from Cabbage.  
**rhythm_ratio_analyzer_test.rpp** - Test project for Reaper, with midi sequences and the rhythm_analyzer_vst vst plugin (OSX users might need to delete and add the plugin for Reaper to find it)  

To use:  
python main.py  
Then load the plugin "rhythm_analyzer_vst" in a DAW, hit "record" and send midi notes to it. When you stop recording, analysis will be initiated. hit "play" to hear the best analysis suggestion. The "rank" dropdown will give access to next best suggestions.  Hit "generate" to use the probabilistic logic to generate a steram of events based on analysis of recorded events.

Description of the rhythm ratio analyzer process:
The basic idea is to analyze a time series in terms of rational relationships between delta times. Rational expressions (ratios) are found by comparing one delta time to all other delta times in the sequence, representing the whole sequence as a series of ratios. Each of the delta times can be used as the reference delta, against which all other deltas are compared to form ratios. Thus, a number of competing theories/suggestions co-exist as possible rational representations of the sequence. The competing suggestions are then evaluated according to criteria for suitability. The score value thus attained for each suggestion is used to rank them. From the rational representation of the time series, one can deduce pulse and meter, which represent larger scale patterns in the series.

Process overview:
1.	Input of the time series. Each event in the series is stored as a time stamp when the even occurred. This can be written as t1, t2, t3, etc.
2.	The delta time between each event is obtained by subtracting the previous time stamp from the current one. For example d1 = t2-t1. 
3.	Rational representations of the delta times are calculated as a simplest rational approximation within a given resolution. For example, if the resolution is 1/4 and the ratio is 0.8:1, it is approximated as 3/4. A rational approximation of the whole series is calculated using each of the delta times in the series. This results in N-1 suggestions for a rational approximation for a time series of length N.
4.	Evaluation of the suitability of each suggestion is done by giving each suggestion a score based on the following criteria:
a.	Deviation: the approximation error, which is the difference between the unquantized ratio and the rational approximation. Deviation is calculated both as sum of all deviations, sum of absolute deviations, and the maximum absolute deviation.
b.	Gridsize deviation: A time grid is constructed from the reference delta of each suggestion. This reference delta may be subdivided by the least common denominator found in the ratio suggestion. Gridsize deviation is then calculated as the sum of absolute deviations from this grid, over all delta times in the sequence.
c.	Complexity: Some reference deltas will lead to high complexity rational approximations (where e.g. 7/8 is more complex than 3/4). The calculation of complexity for an integer ratio is not straightforward. We use Benedetti height as one such measure (multiply the nominator and denominator). Another, perhaps better measure is simply adding the nominator and denominator. These complexity measurements are then summed across all ratios in the sequence.
d.	Evidence: if several of the ratio approximation suggestions are equal, this might indicate that the suggestion is more valid. Equality is calculated by first converting the suggestion to use a common denominator, then normalize the numerators, giving a representation suitable for comparison.
e.	Autocorrelation: If a suggestion of a rational approximation sequence has high autocorrelation it might indicate that there are rhythmical patterns with recurring emphasis. This can indicate that a suggestion is well suited, as there are repeating subsequences within the suggestion. Repetition (or partly/incomplete repetition) suggests rhythmical consistency. Autocorrelation is calculated by first converting the rational expressions to a binary "trigger sequence" (e.g. 3/6, 2/6, 2/6, 2/6 becomes 100101010). This trigger sequence is then autocorrelated, and we use the max value as our autocorrelation score (exepting the first value, which is correlation with itself with no delay). To further differentiate the autocorrelation scores of different suggestions, we raise this max value to a power of two.
5.	All evaluation methods (scores) are normalized and then given an empirically adjustable weight. This allows a straightforward sum of all evaluation methods for each suggestion.
6.	Based on the evaluation scores, all suggestions are ranked, and we select the suggestion with the best score.
7.	The best suggestion for rational approximation is returned, with the form os a ratio sequence with a common denominator.
8.	The tick tempo in Hz (the tempo of a metronome reading the trigger sequence) is calculated from the (1/reference delta time) multiplied with the common denominator
9.	A suggested pulse for the rhythmic sequence is suggested by taking the index of the maximum autocorrelation value
10.	Tempo tendency (increasing or decreasing over the length of the sequence) is calculated by taking the inverse of the sum of all ratio deviations in sequence (the best suggestion for rational approximation of the sequence)

Description of daata containers:
The main data container is the corpus (in data_containers.py). This numpy array contains index, timestamp, rhythm ratio, and other parameters associated with each event. A pointer to this corpus is passed to the modules that need access to it. 
A dictionary (pnum_corpus) is used to associate parameter names with indices in the corpus.  
Beware that if any module then changes the data for an event, it will have effect globally, as the central corpus will be modified. Any module that need to process and modify the data from the corpus must consider if it needs to make a copy of the relevant data to prevent such global effects.  
There is also a similar dictionary for the dimensions (the different event parameters considered) of the probabilistic logic modules. This dictionary (prob_parms) has the format   
parameter_name: [order, prob_encoder instance, [list of prob logic indices]]
The prob_parms dictionary is created automatically from user data given in prob_parms_description


Description of the probabilistic logic:
The probabilistic logic depends on classification/quantization of event values to produce a small set of symbols (quantized event values) for probabilistic encoding. The encoder simply records the index at which each symbol appear. It uses and index container with size=max_events and records a 1 for each index where the symbol occurs. To generate e.g. first order markovian sequences, we query the encoder with a symbol, and offset the index container by one. For hogher order markov lookups, query with the appropriate symbol from history and offset the index container acording to the markov order. We can ask for a specific symbol in the same manner, using an offset of zero. All queries result in an index container, these are then scaled according to a weight vector and summed using an effective dot matrix operation. This results in a probability distribution, which can be additionally shaped with a temperature coefficient (low temperature is more deterministic, similar to other machine learning and neural network techniques). The probability distribution is then used to select the next event for generation.

OSC communication:
The server receives OSC messages on port 9901 and sends OSC messages to the client on port 9999.
This can be edited in osc_io.py, at the top of the script (approx line 20)

The client uses these OSC channels:
"/client_timevalues" - for recording event time stamps
"/client_analyze_trig" - trigger analysis of recorded events
"/client_parametercontrols" - set various parameters
"/client_clear" - clear recorded data
"/client_prob_gen" - query to generate one new event with the probabilistic logic
"/client_prob_print" - print state transition matrices for the probabilistic logic module

The message format might change during development. Look at the relevant methods in rhythm_osc_server to find how many values each method expects.

