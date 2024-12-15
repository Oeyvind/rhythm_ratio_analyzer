<CsoundSynthesizer>
<CsOptions>
</CsOptions>
<CsInstruments>

	sr = 48000  
	ksmps = 10
	nchnls = 2	
	0dbfs = 1

gkTest_data[] init 6, 4 ; 6 events with 4 parameters

instr 1
	p3 = 1/kr
	; make test data
	; event format: index, delta_time (ratio), note, velocity
	kEvent1[] fillarray 0, 0.5, 60, 90
	kEvent2[] fillarray 1, 0.5, 62, 90
	kEvent3[] fillarray 2, 0.5, 63, 90
	kEvent4[] fillarray 3, 0.5, 65, 90
	kEvent5[] fillarray 4, 0.5, 67, 90
	kEvent6[] fillarray 5, 0.5, 70, 90
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
	kmod_index = 6;0.9
	kmod_freq = 0.5
	i2pi = 6.283186
	kmod_amp = (kmod_index/kmod_freq)*(ktempo_bpm/60)/i2pi
	kclock_modulator oscili kmod_amp, kmod_freq
	kbeat_clock += kclock_modulator
	kprev init 0
	kdirection signum kbeat_clock-kprev ; indicate if time is moving forwards or backwards
	kprev = kbeat_clock
  chnset kbeat_clock, "beat_clock"
	chnset kdirection, "beat_clock_direction"
  ;printk2 floor(kbeat_clock)
	outch 1, -1+a(kbeat_clock)*0.1
endin	

instr 3
; queue
  kbeat_clock chnget "beat_clock"
  ibeat_clock chnget "beat_clock"
	kprev_beat_clock init ibeat_clock
	iclock_resolution = 10000
	kclock_direction chnget "beat_clock_direction"
  igen_instr = 4
	kEvent_queue[] init 10, 4 ; 10 events, 4 parameters each
	ktime timeinsts

  ; get event trig
  kget_index init 0
	;Sgetindex sprintfk "get_index %i time %.2f", kget_index, ktime
	;puts Sgetindex, kget_index+1
  kgen_ratio init 0 
  kgen_notenum init 0
  kgen_velocity init 0
  knext_event_time init ibeat_clock
  kget_event = (kbeat_clock >= knext_event_time) ? 1 : 0 
  kget_event_trig trigger kget_event, 0.5, 0

  if kget_event_trig > 0 then
		; get event
		kEvent[] getrow gkTest_data, kget_index % lenarray(gkTest_data)
		kgen_ratio = kEvent[1]
		kEvent_queue setrow kEvent, kget_index % lenarray(kEvent_queue)
		kEvent_queue[kget_index % lenarray(kEvent_queue)][1] = knext_event_time ; (this event time)
		;Sget sprintfk "  get: index %i event_beat %.2f at time %.2f", kget_index % lenarray(kEvent_queue), knext_event_time, ktime
		;puts Sget, kget_index+1
		;printarray kEvent_queue
    knext_event_time += round(kgen_ratio*iclock_resolution)/iclock_resolution 
		kget_index += 1
	endif

	; play event trig
	kplay_index init 0
	kplay_index = kplay_index % lenarray(kEvent_queue)
	;Splayindex sprintfk "    play_index %i time %.2f, note %i", kplay_index, ktime, kEvent_queue[kplay_index][2]
	;puts Splayindex, kplay_index+1
	;kevent_time_debug = kEvent_queue[kplay_index][1]
	;Splay_event sprintfk "      play: index %i, beat %.2f at time %.2f", kplay_index, kevent_time_debug, ktime
	;puts Splay_event, kevent_time_debug+1

	if kclock_direction > 0 then
		kplay_event_trig trigger kbeat_clock,  kEvent_queue[kplay_index % lenarray(kEvent_queue)][1], 0
	else
		;printk2 floor(kbeat_clock*100)/100
		kplay_event_trig trigger kbeat_clock,  kEvent_queue[kplay_index-2 % lenarray(kEvent_queue)][1], 1
	endif
	printk2 kclock_direction, 10
	;printk2 kplay_event_trig, 30
	;kplay_event_trig trigger kplay_event, 0.5, 0
	if kplay_event_trig > 0 then
		; play event
		printk2 kplay_index
		if kclock_direction < 0 then
			kpindex = kplay_index-2
		else
			kpindex = kplay_index
		endif
  	kgen_notenum = kEvent_queue[kpindex][2]
 	 	kgen_velocity = kEvent_queue[kpindex][3]
    kdur = 0.5
		ivoice = 1
    event "i", igen_instr, 0, kdur, kgen_notenum, kgen_velocity, ivoice
		kplay_index += kclock_direction
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

</CsInstruments>
<CsScore>
i1 0 1  ; test data
i2 0 10 ; beat clock
i3 0 10 ; event queue


</CsScore>
</CsoundSynthesizer>