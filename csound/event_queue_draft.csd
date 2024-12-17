<CsoundSynthesizer>
<CsOptions>
</CsOptions>
<CsInstruments>

	sr = 48000  
	ksmps = 10
	nchnls = 2	
	0dbfs = 1

gkTest_data[] init 6, 4 ; 6 events with 4 parameters
giSine ftgen 0, 0, 4096, 10, 1


instr 1
	p3 = 1/kr
	; make test data
	; event format: delta_time (ratio), deviation, note, velocity
	kEvent1[] fillarray 1, 0.0, 60, 90
	kEvent2[] fillarray 0.5, 0.0, 61, 90
	kEvent3[] fillarray 0.25, 0.1, 62, 90
	kEvent4[] fillarray 0.25, 0.0, 63, 90
	kEvent5[] fillarray 0.5, -0.1, 64, 90
	kEvent6[] fillarray 0.5, 0.0, 65, 90
	gkTest_data setrow kEvent1, 0
	gkTest_data setrow kEvent2, 1
	gkTest_data setrow kEvent3, 2
	gkTest_data setrow kEvent4, 3
	gkTest_data setrow kEvent5, 4
	gkTest_data setrow kEvent6, 5
	;printarray(gkTest_data)
endin	

instr 2
  ; beat clock
  ktempo_bpm = 120
  chnset ktempo_bpm, "gen_tempo_bpm"
  ibeat_clock chnget "beat_clock"
  kclock_counter init ibeat_clock*kr
	kclock_counter += (ktempo_bpm/60)
  kbeat_clock = (kclock_counter/kr)
	chnset kbeat_clock, "beat_clock_dry" ; unmodulated clock
	kmod_index linseg 0, 4, 0, 16, 2.6
	kmod_freq = (ktempo_bpm/60)/4
	i2pi = 6.283186
	kmod_amp = (kmod_index/kmod_freq)*(ktempo_bpm/60)/i2pi
	imodphase = 0.
	kclock_modulator oscili kmod_amp, kmod_freq, -1, imodphase
	kbeat_clock += kclock_modulator
	kprev init 0
	kdirection signum kbeat_clock-kprev ; indicate if time is moving forwards or backwards
	kprev = kbeat_clock
  chnset kbeat_clock, "beat_clock"
	chnset kdirection, "beat_clock_direction"
	outch 1, -0.9+a(kbeat_clock)*0.02
endin	

instr 3
	kgen_once init 1 ; do only the first time
	if kgen_once > 0 then
		reinit beat_clock_init
	endif
	beat_clock_init:
		ibeat_clock chnget "beat_clock"
		;print ibeat_clock
	rireturn

	; gen and play events
	ktempo_bpm chnget "gen_tempo_bpm"
  kbeat_clock chnget "beat_clock"  
	kbeat_clock_dry chnget "beat_clock_dry"
	iclock_resolution = 10000
	kclock_direction chnget "beat_clock_direction"
  igen_instr = 4
	kEvent_queue[] init 30, 4 ; 20 events, 4 parameters each
	ktime timeinsts ; just for debug

  ; get event trig
  kgen_index init 0
	kdeviation_scale = 0.2
  knext_event_time init -999 ; overwritten on first k-event
	kprevious_ratio init 0 ; means we will generate two events when starting
	
  if kbeat_clock > knext_event_time then
		; get event
		kEvent[] getrow gkTest_data, kgen_index % lenarray(gkTest_data) ; get external/new data
		kgen_ratio = kEvent[0]
		;Sindex sprintfk "gen index %i, ratio %.2f, beat_clock %.2f, at time %.2f", kgen_index, kgen_ratio, kbeat_clock, ktime
		;puts Sindex, kgen_index+1
		knext_event_time += round(kprevious_ratio*iclock_resolution)/iclock_resolution ; prevent accumulative rounding errors
		knext_event_time = kgen_once > 0 ? ibeat_clock : knext_event_time ; sync to beat clock the first time
		kdeviation = kEvent[1] * kdeviation_scale 
		kEvent[0] = knext_event_time + (kgen_ratio*kdeviation)*(60/ktempo_bpm); store this event time with deviation, for correct playback
		kprevious_ratio = kgen_ratio
		kEvent_queue setrow kEvent, kgen_index % lenarray(kEvent_queue)
		;printarray kEvent_queue
		kgen_once = 0
		kgen_index += 1
	endif
	; TO HERE
	; event playback
  kplay_index init 0
	kplay_event_time = kEvent_queue[wrap(kplay_index, 0, lenarray(kEvent_queue))][0]
	kclock_switch trigger kclock_direction, 0, 1 ; trigger on change to negative
	kbacklog_clock_point init 0
	kbacklog_clock_point = kclock_switch > 0 ? kbeat_clock : kbacklog_clock_point ; the beat time when we started playing backwards
	kclock_behind = kbeat_clock < kbacklog_clock_point ? 1 : 0
	
	; regular play trig
	kplaytrig_flag init 1
	kplay_trig init 0
	if kbeat_clock > kplay_event_time && kplaytrig_flag > 0 then
		kplaytrig_flag = 0
		kplay_trig = 1
	endif
	if kbeat_clock < kplay_event_time then
		kplaytrig_flag = 1
	endif

	; playtrig when we are playing backlog (previous) events due to time modulation
	if kclock_behind > 0 then
		if kclock_direction < 0 then
			if kplay_index >= 0 then
				kbacklog_time = kEvent_queue[(kplay_index-1) % lenarray(kEvent_queue)][0]
			else
				klast_index = lenarray(kEvent_queue)+(kplay_index+1)
				kbacklog_time = kEvent_queue[klast_index-1][0]-kEvent_queue[klast_index][0]
			endif
			if kbeat_clock < kbacklog_time && kplaytrig_flag > 0 then
				kplaytrig_flag = 0
				kplay_trig = 1
			endif
			if kbeat_clock > kbacklog_time then
				kplaytrig_flag = 1
			endif
		endif
	endif

	; play event and update
	if kplay_trig > 0 then
		kdur = 0.5
		if kclock_direction < 0 then 
			keventqueue_index wrap kplay_index-1, 0, lenarray(kEvent_queue)
		else
			keventqueue_index wrap kplay_index, 0, lenarray(kEvent_queue)
		endif
		Sdebug sprintfk "play_index %i, e_queue_index %i, beat_clock %.2f, dir %i, time %.2f", kplay_index, keventqueue_index, kbeat_clock, kclock_direction, ktime
		puts Sdebug, ktime+1
  	kgen_notenum = kEvent_queue[keventqueue_index][2]
		kgen_velocity = kEvent_queue[keventqueue_index][3]
		ivoice = 1
  	event "i", igen_instr, 0, kdur, kgen_notenum, kgen_velocity, ivoice
		
		kplay_index += kclock_direction		
		kplay_trig = 0
	endif
endin	


instr 4
; play event
	;print p2, p4
  iamp = ampdbfs(-6)
  inote = p4
  ivel = p5
  ichan = p6
  aenv expon 1, p3, 0.0001
  a1 oscili ivel/127, cpsmidinn(inote)
  a1 *= (aenv*iamp)
  outch 2, a1
endin	

instr 5
	kmod_freq = 0.001
	kmod_wave = giSine
	kmod_phase = 0
  aclock_modulator osciliktp kmod_freq, kmod_wave, kmod_phase
  kclock_modulator downsamp aclock_modulator
	kclock_modulator *= 0.1
	kdiff diff kclock_modulator
	outs a(kclock_modulator), a(kdiff)*10000 
endin	

</CsInstruments>
<CsScore>
i1 0 1  ; test data
i2 0 20 ; beat clock
i3 0 20 ; event queue
;i5 0 10

</CsScore>
</CsoundSynthesizer>