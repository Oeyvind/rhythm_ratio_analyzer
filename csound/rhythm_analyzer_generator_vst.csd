<Cabbage>
form size(605, 460), caption("Rhythm Analyzer"), pluginId("rtm1"), guiMode("queue"), colour(46,45,52)

; recording and analysis
button bounds(5, 5, 70, 50), text("record","recording"), channel("record_enable"), colour:0("green"), colour:1("red")

groupbox bounds(85, 5, 160, 50), text("last recorded phrase"), colour(45,25,25){
  button bounds(8, 25, 45, 20), text("play"), channel("play_last_phrase"), colour:0("green"), colour:1("red")
  button bounds(57, 25, 45, 20), text("print"), channel("print_last_phrase"), colour:0("green"), colour:1("red"), latched(0)
  button bounds(106, 25, 45, 20), text("clear"), channel("clear_last_phrase"), colour:0("green"), colour:1("red"), latched(0)
}
groupbox bounds(248, 5, 215, 50), colour(45,25,25){ ; , text("phrase data")
label bounds(14, 2, 80, 18), text("tempo"), fontSize(12), align("left")
nslider bounds(10, 25, 50, 22), channel("tempo_bps_last_phrase"), range(1, 2999, 1), fontSize(14)
label bounds(70, 2, 80, 18), text("tendency"), fontSize(12), align("left")
nslider bounds(70, 25, 50, 22), channel("tempo_tendency"), range(-10, 10, 0), fontSize(14)
label bounds(138, 2, 80, 18), text("phrase_len"), fontSize(12), align("left")
nslider bounds(143, 25, 50, 22), channel("phrase_len"), range(0, 999, 0, 1, 1), fontSize(14)
}

button bounds(467, 5, 70, 23), text("clear_all","clearing"), channel("clear_all"), colour:0("green"), colour:1("red"), latched(0)
button bounds(467, 30, 70, 23), text("save_all","saving"), channel("save_all"), colour:0("green"), colour:1("red"), latched(0)

groupbox bounds(5, 60, 240, 65), text("last recorded event"), colour(20,30,45){
  nslider bounds(5,25,60,20), channel("timestamp_last_event"), fontSize(14), range(0,99999999, 0, 1, 0.1)
  label bounds(5,45,50,20), text("time"), fontSize(12)
  nslider bounds(70,25,50,20), channel("index_last_event"), fontSize(14), range(0,9999,0,1,1)
  label bounds(70,45,50,20), text("index_last_event"), fontSize(12)
  nslider bounds(125,25,50,20), channel("notenum_last_event"), fontSize(14), range(0,127,0,1,1)
  label bounds(125,45,50,20), text("num"), fontSize(12)
  nslider bounds(180,25,50,20), channel("velocity_last_event"), fontSize(14), range(0,127,0,1,1)
  label bounds(180,45,50,20), text("velocity"), fontSize(12)
}

groupbox bounds(250, 60, 350, 65), text("rhythm analysis weights"), colour(20,30,45){
nslider bounds(5, 25, 40, 20), channel("benni_weight"), range(0, 1, 1), fontSize(14)
label bounds(5, 45, 40, 20), text("benni"), fontSize(12)
nslider bounds(50, 25, 40, 20), channel("nd_weight"), range(0, 1, 1), fontSize(14)
label bounds(50, 45, 40, 20), text("n+d"), fontSize(12)
nslider bounds(100, 25, 40, 20), channel("ratio_dev_weight"), range(0, 1, 1), fontSize(14)
label bounds(100, 45, 40, 20), text("r_dev"), fontSize(12)
nslider bounds(150, 25, 40, 20), channel("ratio_dev_abs_max_weight"), range(0, 1, 1), fontSize(14)
label bounds(150, 45, 40, 20), text("r_maxdev"), fontSize(12)
nslider bounds(200, 25, 40, 20), channel("grid_dev_weight"), range(0, 1, 1), fontSize(14)
label bounds(200, 45, 40, 20), text("grid"), fontSize(12)
nslider bounds(250, 25, 40, 20), channel("evidence_weight"), range(0, 1, 1), fontSize(14)
label bounds(250, 45, 40, 20), text("evidence"), fontSize(12)
nslider bounds(300, 25, 40, 20), channel("autocorr_weight"), range(0, 1, 1), fontSize(14)
label bounds(300, 45, 40, 20), text("acorr"), fontSize(12)
}

groupbox bounds(5, 135, 590, 170), text("generate events with prob logic"), colour(25,45,30){
button bounds(10, 25, 70, 30), text("generate"), channel("generate"), colour:0("green"), colour:1("red")
nslider bounds(90, 25, 40, 25), channel("gen_r1_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(90, 45, 60, 18), text("r1_ord"), fontSize(12), align("left")
nslider bounds(155, 25, 40, 25), channel("gen_r2_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(155, 45, 60, 18), text("r2_ord"), fontSize(12), align("left")
nslider bounds(220, 25, 40, 25), channel("gen_pitch_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(220, 45, 60, 18), text("ptch_ord"), fontSize(12), align("left")
nslider bounds(285, 25, 40, 25), channel("gen_temperature"), range(0.01, 10, 0.2, 1, 0.01), fontSize(14)
label bounds(285, 45, 60, 18), text("temp"), fontSize(12), align("left")

button bounds(10, 65, 30, 23), text("at"), channel("auto_tempo"), colour:0("green"), colour:1("red"), value(1)
nslider bounds(40, 65, 40, 25), channel("gen_tempo_bpm"), range(1, 2999, 60), fontSize(14)
label bounds(40, 90, 60, 18), text("g_tpo"), fontSize(12), align("left")
nslider bounds(90, 65, 40, 25), channel("gen_duration_scale"), range(0.1, 2, 1), fontSize(14)
label bounds(90, 90, 60, 18), text("g_dur"), fontSize(12), align("left")
nslider bounds(155, 65, 40, 25), channel("gen_deviation_scale"), range(0, 3, 0), fontSize(14)
label bounds(155, 90, 60, 18), text("g_dev"), fontSize(12), align("left")
nslider bounds(220, 65, 40, 25), channel("gen_interval_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(220, 90, 60, 18), text("intv_ord"), fontSize(12), align("left")
button bounds(265, 65, 55, 25), text("rel pitch"), channel("gen_relative_pitch"), colour:0("green"), colour:1("red")

button bounds(350, 25, 45, 25), text("metro"), channel("gen_metro_on"), colour:0("green"), colour:1("red"), latched(1)
button bounds(350, 60, 45, 25), text("clock reset"), channel("beat_clock_reset"), colour:0("green"), colour:1("red"), latched(0)

groupbox bounds(430, 98, 160, 72), text("beat clock modulation") {
nslider bounds(10, 25, 40, 25), channel("beat_clock_mod_index"), range(0, 4, 0, 1), fontSize(14)
label bounds(13, 50, 40, 18), text("indx"), fontSize(12), align("left")
nslider bounds(60, 25, 40, 25), channel("beat_clock_mod_ratio"), range(0.5, 8, 1, 1, 0.5), fontSize(14)
label bounds(63, 50, 40, 18), text("ratio"), fontSize(12), align("left")
nslider bounds(110, 25, 40, 25), channel("beat_clock_mod_phase"), range(0, 1, 0, 1), fontSize(14)
label bounds(113, 50, 40, 18), text("phase"), fontSize(12), align("left")
}

button bounds(400, 25, 50, 25), text("beat sync"), channel("beat_sync"), colour:0("green"), colour:1("red"), latched(1)
; debug
button bounds(520, 25, 50, 25), text("print stm"), channel("pl_print"), colour:0("green"), colour:1("red"), latched(0)


; voice 2
button bounds(10, 115, 70, 23), text("voice 2"), channel("gen_voice2"), colour:0("green"), colour:1("red")
nslider bounds(90, 115, 40, 25), channel("gen_v2_pitch_offset"), range(-24, 24, 12, 1, 1), fontSize(14)
label bounds(90, 135, 60, 18), text("transp"), fontSize(12), align("left")


}
csoundoutput bounds(5, 315, 560, 140)
</Cabbage>

<CsoundSynthesizer>
<CsOptions>
-n -d -m0 -+rtmidi=NULL -M0 -Q0
</CsOptions>

<CsInstruments>

;sr = 48000 ; set by host
ksmps = 32
nchnls = 2
0dbfs = 1

massign -1, 2
pgmassign 0, -1 ; ignore program change
gkactivenote init 0; stores the note number of the active note, for polyphony control for rhythm analyzer

gitrig_ftab ftgen 0, 0, 4096, 2, 0
gitrig_ftab_empty ftgen 0, 0, 4096, 2, 0
gihandle OSCinit 9999 ; set the network port number where we will receive OSC data from Python
giSine ftgen 0, 0, 4096, 10, 1

; GUI handling
instr 1
  kplay chnget "play_last_phrase"
  ktrig_play trigger kplay, 0.5, 0
  ktrig_stop trigger kplay, 0.5, 1
  itriggerseq_instr = 5
  if ktrig_play > 0 then
    event "i", itriggerseq_instr, 0, -1
  endif
  if ktrig_stop > 0 then
    event "i", -itriggerseq_instr, 0, .1
  endif
  ; generator
  kgenerate chnget "generate"
  ktrig_generate trigger kgenerate, 0.5, 0
  ktrig_generate_stop trigger kgenerate, 0.5, 1
  if ktrig_generate > 0 then
    ivoice = 1
    event "i", 109+(ivoice*0.1), 0, -1, ivoice
  endif
  if ktrig_generate_stop > 0 then
    event "i", -(109+(ivoice*0.1)), 0, .1
  endif
  ; voice 2
  kgenerate2 chnget "gen_voice2"
  ktrig_generate2 trigger kgenerate2, 0.5, 0
  ktrig_generate2_stop trigger kgenerate2, 0.5, 1
  if ktrig_generate2 > 0 then
    ivoice2 = 2
    event "i", 109+(ivoice2*0.1), 0, -1, ivoice2
  endif
  if ktrig_generate2_stop > 0 then
    event "i", -(109+(ivoice2*0.1)), 0, .1
  endif
  ; start/stop master clock
  kactive active 109
  kanytrig_on = ktrig_generate+ktrig_generate2
  kanytrig_off trigger kactive, 0.5, 1
  if (kactive == 0) && (kanytrig_on > 0) then
    event "i", 108, 0, -1 ; master clock
  endif
  if kanytrig_off > 0 then
    event "i", -108, 0, .1 ; master clock
  endif

  kclock_reset chnget "beat_clock_reset"
  if kclock_reset > 0 then
    kzero = 0
    chnset kzero, "beat_clock"
  endif

  ; print probabilistic logic stm
  kprint_stm chnget "pl_print"
  kprint_last chnget "print_last_phrase"
  kprint_on trigger kprint_stm+kprint_last, 0.5, 0
  if kprint_on > 0 then
    event "i", 110, 0, .1, kprint_stm+(kprint_last*2) ; print code 1 or 2
  endif
endin

; rhythm recording instr, triggered by midi input
instr 2
  inum notnum
  chnset inum, "notenum"
  ivel veloc
  chnset ivel, "velocity"
  inst_num = 3+(inum*0.001)
  krelease lastcycle
  iactive active 3
  if iactive > 0 then
    ifrac = i(gkactivenote)*0.001
    event_i "i", -3-ifrac, 0, .1
    chnset 1, "event_force_off"
  endif
  event_i "i", inst_num, 0, -1, inum
  if (krelease > 0) && (inum == gkactivenote) then 
      event "i", -inst_num, 0, .1
      chnset krelease, "event_off"
  endif
  
endin

instr 3
  kon init 1
  chnset kon, "event_on"
  kon = 0
  gkactivenote = p4
  ;a1 oscil 0.1, cpsmidinn(p4)
  ;outs a1, a1
endin

; play trigger rhythm
instr 5
  ktempo chnget "tempo_triggerseq"
  itrig_length chnget "triggerseq_length"
  Striglength sprintf "triggerseq length %i", itrig_length
  puts Striglength, 1
  kmetro metro ktempo
  kindex init 0
  ktrig table kindex, gitrig_ftab
  kpulse = ktrig*kmetro
  kindex = (kindex+kmetro)
  if kindex > itrig_length+1 then
    Send = "Sequence end, turning off instr"
    puts Send, kindex
    turnoff
  endif
  inoise_instr = 120
  if kpulse > 0 then
    event "i", inoise_instr, 0, 0.1
  endif
endin

;*******************************
; Csound to Python communication, analyzer
instr 31
  ; event trig handling, making monophonic event on/off even if input has overlapping notes
  kevent_on chnget "event_on"
  kevent_off chnget "event_off"
  kevent_force_off chnget "event_force_off" ; force off when we have overlapping notes in input
  kzero = 0
  chnset kzero, "event_off"
  chnset kzero, "event_force_off"
  kevent_trig = (kevent_on + kevent_off + kevent_force_off) > 0 ? 1 : 0
  ksend_osc init 1
  ksend_osc += kevent_trig ; need this to activate osc send
  kevent_onoff = kevent_on ; if it is not on, it is an "off" event

  knotenum chnget "notenum"
  kvelocity chnget "velocity"
  ktime timeinsts  
  kindex init -1

  krecord_enable chnget "record_enable"
  krec_trig_off trigger krecord_enable, 0.5, 1 ; stop recording, trigger the analysis process in Python 
  kclear_last_phrase chnget "clear_last_phrase"
  kclear_all chnget "clear_all"
  ksave_all chnget "save_all"
  kauto_tempo_update chnget "auto_tempo"
    
  ; send time data to Python
  if krecord_enable > 0 then
    kindex += kevent_on
    if kevent_trig > 0 then
      OSCsend ksend_osc, "127.0.0.1", 9901, "/client_eventdata", "fffff", kindex, ktime, kevent_onoff, knotenum, kvelocity
    endif
    ; if Python skips an index (due to invalid data), we update our index counter so it is equal to the index counter in Python
    skipindex:
      kskipindex OSClisten gihandle, "python_skipindex", "i", kindex  ; if Python skipped this index, update our index
      if kskipindex == 0 goto done_skipindex
      kgoto skipindex ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
    done_skipindex:
    if kevent_on > 0 then
      cabbageSetValue "index_last_event", kindex
      cabbageSetValue "velocity_last_event", kvelocity
      cabbageSetValue "notenum_last_event", knotenum
      cabbageSetValue "timestamp_last_event", ktime
    endif
  endif

  ; send analyze trigger to Python
  kanalyzetrig init 0
  kanalyzetrig += krec_trig_off
  k_ = 1
  OSCsend kanalyzetrig, "127.0.0.1", 9901, "/client_analyze_trig", "i", k_
  
  ; send other parameter controls to Python
  kbenni_weight chnget "benni_weight"
  knd_weight chnget "nd_weight"
  kratio_dev_weight chnget "ratio_dev_weight"
  kratio_dev_abs_max_weight chnget "ratio_dev_abs_max_weight"
  kgrid_dev_weight chnget "grid_dev_weight"
  kevidence_weight chnget "evidence_weight"
  kautocorr_weight chnget "autocorr_weight"
  kratio1_order chnget "gen_r1_order"
  kratio2_order chnget "gen_r2_order"
  knotenum_order chnget "gen_pitch_order"
  kinterval_order chnget "gen_interval_order"
  ktemperature chnget "gen_temperature"
  kparm_update = changed(kbenni_weight, knd_weight, kratio_dev_weight, 
                      kratio_dev_abs_max_weight, kgrid_dev_weight, 
                      kevidence_weight, kautocorr_weight, kratio1_order, 
                      kratio2_order, knotenum_order, kinterval_order, ktemperature)
  OSCsend kparm_update, "127.0.0.1", 9901, "/client_parametercontrols", "ffffffffffff", 
                      kbenni_weight, knd_weight, kratio_dev_weight, 
                      kratio_dev_abs_max_weight, kgrid_dev_weight, 
                      kevidence_weight, kautocorr_weight, kratio1_order, 
                      kratio2_order, knotenum_order, kinterval_order, ktemperature

  ; receive trigger string from Python (only for playback of last recorded phrase)
  ktrig_sig init 0
  ktrig_index init 0
  if krec_trig_off+kclear_last_phrase+kclear_all > 0 then
    tablecopy gitrig_ftab, gitrig_ftab_empty  ; clear trig table
    ktrig_index = 0
    chnset ktrig_index, "triggerseq_length"
  endif
  nextmsg_trig:
  kmess_trig OSClisten gihandle, "python_triggerdata", "ii", ktrig_index, ktrig_sig  ; receive OSC data from Python
  if kmess_trig == 0 goto done_trig
  tablew ktrig_sig, ktrig_index, gitrig_ftab
  chnset ktrig_index+1, "triggerseq_length"
  kgoto nextmsg_trig ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done_trig:

  ; receive other data from Python
  kticktempo_bpm init 60
  ktempo_tendency init 0
  kpulseposition init 1
  kphraselen init 0
  nextmsg_other:
  kmess_other OSClisten gihandle, "python_other", "ffff", kticktempo_bpm,ktempo_tendency,kpulseposition,kphraselen ; receive OSC data from Python
  chnset kticktempo_bpm/60, "tempo_triggerseq"
  ktempo_bpm = kticktempo_bpm/kpulseposition
  cabbageSetValue "tempo_bps_last_phrase", ktempo_bpm, changed(ktempo_bpm)
  cabbageSetValue "gen_tempo_bpm", ktempo_bpm, changed(ktempo_bpm*kauto_tempo_update)
  cabbageSetValue "tempo_tendency", ktempo_tendency, changed(ktempo_tendency)
  cabbageSetValue "phrase_len", kphraselen, changed(kphraselen)
  if kmess_other == 0 goto done_other
  kgoto nextmsg_other ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done_other:

  ; clear timedata in Python
  kmem_trig = changed(kclear_last_phrase, kclear_all, ksave_all)
  kmem_trig_count init 0
  kmem_trig_count += kmem_trig
  OSCsend kmem_trig_count, "127.0.0.1", 9901, "/client_memory", "iii", kclear_last_phrase, kclear_all, ksave_all
  kindex = changed(kclear_all) > 0 ? -1 : kindex
  kclear_phrase_trig trigger kclear_last_phrase, 0.5, 0
  kindex = kclear_phrase_trig > 0 ? kindex-kphraselen : kindex
  puts "reset index", changed(kclear_last_phrase, kclear_all)

endin

; *******************************
; generator

; master clock
instr 108

  ; beat clock
  ktempo_bpm chnget "gen_tempo_bpm"
  ibeat_clock chnget "beat_clock"
  kclock_counter init ibeat_clock*kr
	kclock_counter += (ktempo_bpm/60)
  kbeat_clock = (kclock_counter/kr)
	chnset kbeat_clock, "beat_clock_dry" ; unmodulated clock
	kmod_index chnget "beat_clock_mod_index"
  kmod_ratio chnget "beat_clock_mod_ratio"
	kmod_freq = (ktempo_bpm/60)/kmod_ratio
	i2pi = 6.283186
	kmod_amp = (kmod_index/kmod_freq)*(ktempo_bpm/60)/i2pi
	;imodphase = 0.
	;kclock_modulator oscili kmod_amp, kmod_freq, -1, imodphase
	kmod_phase chnget "beat_clock_mod_phase"
  kmod_wave = giSine
  aclock_modulator osciliktp kmod_freq, kmod_wave, kmod_phase
  kclock_modulator downsamp aclock_modulator
  kclock_modulator *= kmod_amp
  kbeat_clock += kclock_modulator
	kprev init 0
	kdirection signum kbeat_clock-kprev ; indicate if time is moving forwards or backwards
	kprev = kbeat_clock
  chnset kbeat_clock, "beat_clock"
	chnset kdirection, "beat_clock_direction"
  ; metro sound
  kmetro_on chnget "gen_metro_on"
  if (kmetro_on > 0) && (changed(floor(kbeat_clock)) > 0) then
      event "i", 119, 0, 0.1
  endif
endin

; event generator
instr 109
  ivoice = p4
  ;print ivoice
  kinit_clock init 1 ; make sure a k-value from the master have come in
	if kinit_clock > 0 then
		reinit beat_clock_init
	endif
	beat_clock_init:
		ibeat_clock chnget "beat_clock"
    print ibeat_clock
    kinit_clock = 0
	rireturn

	; gen and play events
	ktempo_bpm chnget "gen_tempo_bpm"
  kbeat_clock chnget "beat_clock"  
	kbeat_clock_dry chnget "beat_clock_dry"
	kclock_direction chnget "beat_clock_direction"
	kEvent_queue[] init 10, 6 ; 30 events, 6 parameters each

  kbeat_sync chnget "beat_sync"
  ktemperature chnget "gen_temperature"
  kdur_scale chnget "gen_duration_scale"
  kdeviation_scale chnget "gen_deviation_scale"
  krelative_pitch chnget "gen_relative_pitch"
  iclock_resolution = 10000

  ; oddities
  krequest_ratio init -1
  krequest_weight = 0

  ; event trig
	kgen_once init 1 ; do only the first time
  kgen_index init 0
  kgen_ratio init 0 
  kgen_deviation init 0
  kgen_duration init 1
  kgen_notenum init 0
  kgen_interval init 0
  kgen_velocity init 0
  knext_event_time init -999 ; overwritten on first k-event
	kprevious_ratio init 0 ; means we will generate two events when starting
  kcount init 0
  igen_instr = 121
  ktime timeinsts ; for debug
  ;printk2 floor(kbeat_clock)
  kpython_data_ready init 0

  ; get event data from server
  if (kbeat_clock > knext_event_time) && (kpython_data_ready == 0) then
    OSCsend kcount, "127.0.0.1", 9901, "/client_prob_gen", "ffff", ivoice, kgen_index, krequest_ratio, krequest_weight
  nextmsg:
    Saddr sprintf "python_prob_gen_voice%i", ivoice
    kmess OSClisten gihandle, Saddr, "fffffff", kgen_index, kgen_ratio, kgen_deviation, kgen_duration, kgen_notenum, kgen_interval, kgen_velocity ; receive OSC data from Python
    if kmess > 0 then
        kpython_data_ready = 1
    endif
    if kmess == 0 goto done
    kgoto nextmsg ; make sure we read all messages in the network buffer
  done:
  endif

  ; store events in queue for playback
  if (kbeat_clock > knext_event_time) && (kpython_data_ready == 1) then
		;Sindex sprintfk "count %i, gen index %i, ratio %.2f, beat_clock %.2f, at time %.2f", kcount, kgen_index, kgen_ratio, kbeat_clock, ktime
		;puts Sindex, kcount+1
  	knext_event_time += round(kprevious_ratio*iclock_resolution)/iclock_resolution ; prevent accumulative rounding errors
		if kbeat_sync == 0 then
      knext_event_time = kgen_once > 0 ? ibeat_clock : knext_event_time ; sync to free beat clock the first time
    else
      knext_event_time = kgen_once > 0 ? ceil(ibeat_clock) : knext_event_time ; sync to whole beat clock the first time
    endif
	  kdeviation = kgen_deviation * kdeviation_scale 
		kprevious_ratio = kgen_ratio
    kEvent_queue[kcount % lenarray(kEvent_queue)][0] = knext_event_time + (kgen_ratio*kdeviation)*(60/ktempo_bpm); store this event time with deviation, for correct playback
    kEvent_queue[kcount % lenarray(kEvent_queue)][2] = kgen_duration*(60/ktempo_bpm)
    kEvent_queue[kcount % lenarray(kEvent_queue)][3] = kgen_notenum
    kEvent_queue[kcount % lenarray(kEvent_queue)][4] = kgen_interval
    kEvent_queue[kcount % lenarray(kEvent_queue)][5] = kgen_velocity
		;printarray kEvent_queue
		kgen_once = 0
    kcount += 1
    kpython_data_ready = 0
	endif

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
        klast_index wrap klast_index, 0, lenarray(kEvent_queue)
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
  kprev_notenum init 60
	if kplay_trig > 0 then
		if kclock_direction < 0 then 
			keventqueue_index wrap kplay_index-1, 0, lenarray(kEvent_queue)
		else
			keventqueue_index wrap kplay_index, 0, lenarray(kEvent_queue)
		endif
		;Sdebug sprintfk "play_index %i, e_queue_index %i, beat_clock %.2f, dir %i, time %.2f", kplay_index, keventqueue_index, kbeat_clock, kclock_direction, ktime
		;puts Sdebug, ktime+1
    ;kEvent[] fillarray kgen_ratio, kgen_deviation, kgen_duration, kgen_notenum, kgen_interval, kgen_velocity
    if krelative_pitch > 0 then
      kgen_notenum = kprev_notenum + kEvent_queue[keventqueue_index][4]
    else
      kgen_notenum = kEvent_queue[keventqueue_index][3]
    endif
    kprev_notenum = kgen_notenum
		kgen_velocity = kEvent_queue[keventqueue_index][5]
    kdur = kEvent_queue[keventqueue_index][2]*kdur_scale
  	event "i", igen_instr, 0, kdur, kgen_notenum, kgen_velocity, ivoice
		kplay_index += kclock_direction		
		kplay_trig = 0
	endif

endin

; print stuff on server
instr 110
    iprint = p4 ; 1= prob logic stm, 2=print last phrase ratios
    OSCsend 1, "127.0.0.1", 9901, "/client_print", "f", iprint
endin

; downbeat instr
instr 119
  iamp = ampdbfs(-5)
  aenv expon 1, p3, 0.0001
  a1 oscil 1, 440
  a1 *= aenv
  a1 *= iamp
  outs a1, a1*0
endin

; rhythm trig player
instr 120
  iamp = ampdbfs(-6)
  aenv expon 1, p3, 0.0001
  anoise rnd31 1, 1
  anoise *= aenv
  anoise *= iamp
  outs anoise*0, anoise
endin

; prob gen event player
instr 121
  iamp = ampdbfs(-6)
  inote = p4
  ivel = p5
  ichan = p6
  ktranspose_voice2 chnget "gen_v2_pitch_offset"
  if p6 == 2 then
    inote += i(ktranspose_voice2)
  endif
  aenv expon 1, p3, 0.0001
  a1 oscili ivel/127, cpsmidinn(inote)
  a1 *= (aenv*iamp)
  outs a1, a1
  ; midi out
  noteondur ichan, inote, ivel, p3

endin

</CsInstruments>
<CsScore>
i1 0 86400 ; Gui handling
i31 0 86400 ; OSC processing
</CsScore>
</CsoundSynthesizer>
