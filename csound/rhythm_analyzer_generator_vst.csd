<Cabbage>
form size(770, 660), caption("Rhythm Analyzer"), pluginId("rtm1"), guiMode("queue"), colour(46,45,52)

; recording and analysis
button bounds(5, 5, 70, 50), text("record","recording"), channel("record_enable"), colour:0("green"), colour:1("red")

groupbox bounds(85, 5, 110, 50), text("last rec phrase"), colour(45,25,25){
  button bounds(8, 25, 45, 20), text("print"), channel("print_last_phrase"), colour:0("green"), colour:1("red"), latched(0)
  button bounds(57, 25, 45, 20), text("clear"), channel("clear_last_phrase"), colour:0("green"), colour:1("red"), latched(0)
}
groupbox bounds(198, 5, 215, 50), colour(45,25,25){ ; , text("phrase data")
label bounds(10, 2, 80, 18), text("an_tempo"), fontSize(11), align("left")
nslider bounds(10, 25, 50, 22), channel("tempo_bpm_last_phrase"), range(1, 2999, 1), fontSize(14)
label bounds(70, 2, 80, 18), text("pulse"), fontSize(11), align("left")
nslider bounds(70, 25, 50, 22), channel("pulse_subdiv"), range(1, 3, 1, 1, 1), fontSize(14)
label bounds(138, 2, 80, 18), text("phrase_len"), fontSize(11), align("left")
nslider bounds(143, 25, 50, 22), channel("phrase_len"), range(0, 99, 0, 1, 1), fontSize(14)
}

button bounds(467, 5, 70, 23), text("clear_all","clearing"), channel("clear_all"), colour:0("green"), colour:1("red"), latched(0)
button bounds(467, 30, 70, 23), text("save_all","saving"), channel("save_all"), colour:0("green"), colour:1("red"), latched(0)

checkbox bounds(545, 5, 50, 11), text(" "," "), channel("print_event_time"), colour:0("green"), colour:1("red"), latched(1)
label bounds(545, 18, 50, 11), text("pr.evt.t")

groupbox bounds(5, 60, 240, 65), text("last recorded event"), colour(20,30,45){
  nslider bounds(5,25,60,20), channel("timestamp_last_event"), fontSize(14), range(0,99999999, 0, 1, 0.1)
  label bounds(5,45,50,20), text("time"), fontSize(12)
  nslider bounds(70,25,50,20), channel("index_this_event"), fontSize(14), range(-1,9999,-1,1,1)
  label bounds(70,45,50,20), text("index_this_event"), fontSize(12)
  nslider bounds(125,25,50,20), channel("notenum_last_event"), fontSize(14), range(0,127,0,1,1)
  label bounds(125,45,50,20), text("num"), fontSize(12)
  nslider bounds(180,25,50,20), channel("velocity_last_event"), fontSize(14), range(0,127,0,1,1)
  label bounds(180,45,50,20), text("velocity"), fontSize(12)
}

groupbox bounds(250, 60, 400, 65), text("rhythm analysis settings"), colour(20,30,45){
hslider bounds(5, 27, 100, 20), channel("dev_vs_complexity"), range(0, 1, 0.5), fontSize(14)
label bounds(5, 45, 100, 20), text("precision"), fontSize(12)
checkbox bounds(125, 27, 18, 18), channel("simplify")
label bounds(115, 45, 40, 20), text("simplify"), fontSize(12)

checkbox bounds(190, 27, 18, 18), channel("phrase_reconciliation")
label bounds(185, 45, 40, 20), text("reconcile"), fontSize(12)

nslider bounds(290, 27, 40, 18), channel("phrase_length"), range(4, 20, 5, 1, 1), fontSize(14)
label bounds(290, 45, 40, 20), text("phr.len"), fontSize(12)
}

groupbox bounds(5, 135, 760, 170), text("generate events with prob logic"), colour(25,45,30){
; Voice 1
label bounds(5, 25, 50, 18), text("Voice 1"), fontSize(12), align("left")
button bounds(50, 25, 40, 20), text("on"), channel("gen_voice1"), colour:0("green"), colour:1("red")
nslider bounds(100, 25, 40, 20), channel("gen_v1_duration_scale"), range(0.1, 2, 1), fontSize(14)
label bounds(104, 45, 40, 18), text("dur"), fontSize(12), align("left")
nslider bounds(145, 25, 40, 20), channel("gen_v1_deviation_scale"), range(0, 3, 0), fontSize(14)
label bounds(140, 45, 65, 18), text("dviation"), fontSize(12), align("left")

nslider bounds(190, 25, 40, 20), channel("gen_v1_pitch_offset"), range(-24, 24, 0, 1, 1), fontSize(14)
label bounds(192, 45, 50, 18), text("transp"), fontSize(12), align("left")
button bounds(235, 25, 55, 20), text("rel pitch"), channel("gen_v1_relative_pitch"), colour:0("green"), colour:1("red")

button bounds(300, 25, 35, 20), text("trig"), channel("beat_sync_v1"), colour:0("green"), colour:1("red"), latched(1)
label bounds(300, 45, 70, 18), text("sync -------"), fontSize(12), align("left")
button bounds(340, 25, 35, 20), text("auto"), channel("beat_sync_auto_v1"), colour:0("green"), colour:1("red"), latched(1)

nslider bounds(380, 25, 25, 20), channel("sync_min_v1"), range(0, 10, 1, 1, 1), fontSize(14)
label bounds(380, 45, 30, 18), text("min"), fontSize(12), align("left")
nslider bounds(410, 25, 25, 20), channel("sync_range_v1"), range(0, 10, 1, 1, 1), fontSize(14)
label bounds(409, 45, 35, 18), text("range"), fontSize(12), align("left")

combobox bounds(450, 26, 58, 18), channel("request_parm_v1"), items("index", "rhythm", "pitch", "interval", "phrase")
label bounds(450, 45, 60, 18), text("req_parm"), fontSize(12), align("left")
combobox bounds(510, 26, 58, 18), channel("request_type_v1"), items("none", "next", "prev", "==", ">", "<", "gradient", "gr_abs")
label bounds(510, 45, 60, 18), text("req_type"), fontSize(12), align("left")
nslider bounds(570, 25, 37, 20), channel("request_value_v1"), range(-999, 999, 0, 1, 0.1), fontSize(14)
label bounds(575, 45, 37, 18), text("val"), fontSize(12), align("left")
nslider bounds(610, 25, 40, 20), channel("request_weight_v1"), range(0, 1, 0), fontSize(14)
label bounds(610, 45, 40, 18), text("weight"), fontSize(12), align("left")

;nslider bounds(665, 25, 40, 20), channel("clock_multiplier_v1"), range(-1.0, 1, 1, 1, 0.01), fontSize(14)
;label bounds(665, 45, 65, 18), text("clkdev"), fontSize(12), align("left")

nslider bounds(715, 25, 40, 20), channel("gen_v1_temperature"), range(0.01, 10, 0.2, 1, 0.01), fontSize(14)
label bounds(710, 45, 65, 18), text("tmprature"), fontSize(12), align("left")

; Voice 2
label bounds(5, 65, 50, 18), text("Voice 2"), fontSize(12), align("left")
button bounds(50, 65, 40, 20), text("on"), channel("gen_voice2"), colour:0("green"), colour:1("red")
nslider bounds(100, 65, 40, 20), channel("gen_v2_duration_scale"), range(0.1, 2, 1), fontSize(14)
nslider bounds(145, 65, 40, 20), channel("gen_v2_deviation_scale"), range(0, 3, 0), fontSize(14)
nslider bounds(190, 65, 40, 20), channel("gen_v2_pitch_offset"), range(-24, 24, 12, 1, 1), fontSize(14)
button bounds(235, 65, 55, 20), text("rel pitch"), channel("gen_v2_relative_pitch"), colour:0("green"), colour:1("red")

button bounds(300, 65, 35, 20), text("trig"), channel("beat_sync_v2"), colour:0("green"), colour:1("red"), latched(1)
button bounds(340, 65, 35, 20), text("auto"), channel("beat_sync_auto_v2"), colour:0("green"), colour:1("red"), latched(1)

nslider bounds(380, 65, 25, 20), channel("sync_min_v2"), range(0, 10, 1, 1, 1), fontSize(14)
nslider bounds(410, 65, 25, 20), channel("sync_range_v2"), range(0, 10, 1, 1, 1), fontSize(14)

combobox bounds(450, 66, 58, 18), channel("request_parm_v2"), items("index", "rhythm", "pitch", "interval", "phrase")
combobox bounds(510, 66, 58, 18), channel("request_type_v2"), items("none", "next", "prev", "==", ">", "<", "gradient", "gr_abs")
nslider bounds(570, 65, 37, 20), channel("request_value_v2"), range(-999, 999, 0, 1, 0.1), fontSize(14)
nslider bounds(610, 65, 40, 20), channel("request_weight_v2"), range(0, 1, 0), fontSize(14)
nslider bounds(715, 65, 40, 20), channel("gen_v2_temperature"), range(0.01, 10, 0.2, 1, 0.01), fontSize(14)

button bounds(390, 125, 45, 18), text("chord"), channel("chords_on"), colour:0("green"), colour:1("red"), latched(1)

nslider bounds(460, 125, 40, 22), channel("gen_rhythm_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(460, 147, 60, 18), text("rytm_ord"), fontSize(12), align("left")
nslider bounds(525, 125, 40, 25), channel("gen_deviation_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(525, 147, 60, 18), text("dev_ord"), fontSize(12), align("left")
nslider bounds(590, 125, 40, 22), channel("gen_pitch_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(590, 147, 60, 18), text("ptch_ord"), fontSize(12), align("left")
nslider bounds(655, 125, 40, 22), channel("gen_interval_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(655, 147, 60, 18), text("intv_ord"), fontSize(12), align("left")


groupbox bounds(0, 98, 160, 72), text("gen tempo") {
button bounds(10, 25, 45, 18), text("metro"), channel("gen_metro_on"), colour:0("green"), colour:1("red"), latched(1)
button bounds(10, 47, 20, 20), text(" "), channel("daw_sync"), colour:0("green"), colour:1("red")
label bounds(30, 45, 60, 15), text("DAW"), fontSize(12), align("left")
label bounds(30, 55, 60, 15), text("play sync"), fontSize(12), align("left")
combobox bounds(95, 25, 60, 17), items("analyze", "host", "host_x2", "free"), channel("gen_tempo_mode"), value(2), fontSize(15)
nslider bounds(95, 47, 60, 20), channel("gen_tempo_bpm"), range(1, 2999, 60), fontSize(14)
}

groupbox bounds(160, 98, 160, 72), text("beat clock modulation") {
nslider bounds(10, 25, 40, 25), channel("beat_clock_mod_index"), range(0, 4, 0, 1), fontSize(14)
label bounds(13, 50, 40, 18), text("indx"), fontSize(12), align("left")
nslider bounds(60, 25, 40, 25), channel("beat_clock_mod_ratio"), range(0.5, 32, 1, 1, 0.5), fontSize(14)
label bounds(63, 50, 40, 18), text("ratio"), fontSize(12), align("left")
nslider bounds(110, 25, 40, 25), channel("beat_clock_mod_phase"), range(0, 1, 0, 1), fontSize(14)
label bounds(113, 50, 40, 18), text("phase"), fontSize(12), align("left")
}

; debug
button bounds(560, 3, 75, 15), text("print stm"), channel("pl_print"), colour:0("green"), colour:1("red"), latched(0)
button bounds(480, 3, 75, 15), text("clock reset"), channel("beat_clock_reset"), colour:0("green"), colour:1("red"), latched(0)
}

csoundoutput bounds(5, 315, 760, 340)
</Cabbage>

<CsoundSynthesizer>
<CsOptions>
-n -d -m0 -+rtmidi=NULL -M0 -Q0
</CsOptions>

<CsInstruments>

;sr = 48000 ; set by host
ksmps = 16
nchnls = 2
0dbfs = 1

massign -1, 2
pgmassign 0, -1 ; ignore program change
gkactivenote init 0; stores the note number of the active note, for polyphony control for rhythm analyzer
giChord[] init 6 ; hold chord notes

gihandle OSCinit 9999 ; set the network port number where we will receive OSC data from Python
giSine ftgen 0, 0, 4096, 10, 1

; GUI handling
instr 1
  ; generator
  kgenerate chnget "gen_voice1"
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
  krecord_enable = 1;chnget "record_enable"
  inum notnum
  ivel veloc
  inst_num = 3+(inum*0.001)
  krelease lastcycle
  if krecord_enable > 0 then
    index chnget "index_this_event"
    ;thresh function
    ithresh = 0.050 ; thresh time in seconds
    chnset ithresh, "chord_timethresh"
    itime times
    iprev_time chnget "previous_time"
    idelta = itime-iprev_time
    chnset itime, "previous_time"
    if idelta > ithresh then
      chnset inum, "notenum"
      chnset ivel, "velocity"
      index += 1
      cabbageSetValue "index_this_event", index
      ichord_note_index = 0 ; new chord, or no chord
      chnset ichord_note_index, "chord_note_index"
      iactive active floor(inst_num)
      if iactive > 0 then
        ifrac = i(gkactivenote)*0.001
        event_i "i", -floor(inst_num)-ifrac, 0, .1
        chnset 1, "event_force_off"
      endif
      event_i "i", inst_num, 0, -1, inum
    else
      ichord_note_index chnget "chord_note_index"
      chnset ichord_note_index+1, "chord_note_index"
      ichord_index chnget "chord_index"
      if ichord_note_index == 0 then
        ichord_index += 1
        chnset ichord_index, "chord_index"
      endif
      ichord_send_instr = 4
      isend_delay = ithresh ; delay chord note send so we are sure the base note have arrived before it
      event_i "i", ichord_send_instr, isend_delay, 0.1, index, ichord_index, inum, ivel, idelta
      ;print index, ichord_index, ichord_note_index, inum
    endif

    if (krelease > 0) && (inum == gkactivenote) then 
        event "i", -inst_num, 0, .1
        chnset krelease, "event_off"
    endif
  endif
  krecord_off trigger krecord_enable, 0.5, 1
  if krecord_off > 0 then
    event "i", -inst_num, 0, .1
    chnset krelease, "event_off"
  endif
endin

instr 3
  kon init 1
  chnset kon, "event_on"
  kon = 0
  gkactivenote = p4
endin

instr 4
  ; send chord note event to Python
  index = p4
  ichord_index = p5
  inum = p6
  ivel = p7
  idelta = p8
  OSCsend 1, "127.0.0.1", 9901, "/client_eventchord", "fffff", index, ichord_index, inum, ivel, idelta  
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
  ktempo_mode chnget "gen_tempo_mode"
  khost_bpm chnget "HOST_BPM"
  khost_bpm_update = changed(khost_bpm, ktempo_mode)
  if ktempo_mode == 1 then
    kauto_tempo_update = 1
  else
    kauto_tempo_update = 0
    if ktempo_mode == 2 then
      cabbageSetValue "gen_tempo_bpm", khost_bpm, khost_bpm_update
    elseif ktempo_mode == 3 then
      cabbageSetValue "gen_tempo_bpm", khost_bpm*2, khost_bpm_update
    endif
  endif
  ; if mode is "free", do nothing

    
  ; send time data to Python
  if krecord_enable > 0 then
    kindex chnget "index_this_event"
    if kevent_trig > 0 then
      if kevent_force_off == 1 then
        kindex_send = kindex-1
      else
        kindex_send = kindex
      endif
      ;Sdebug sprintfk "rec: %i, %.2f, %i, %i, %i", kindex_send, ktime, kevent_onoff, knotenum, kvelocity
      ;puts Sdebug, ksend_osc
      OSCsend ksend_osc, "127.0.0.1", 9901, "/client_eventdata", "ffff", ktime, kevent_onoff, knotenum, kvelocity
    endif
    if kevent_on > 0 then
      cabbageSetValue "velocity_last_event", kvelocity
      cabbageSetValue "notenum_last_event", knotenum
      cabbageSetValue "timestamp_last_event", ktime
    endif
  endif

  ; send analyze trigger to Python on record off, and auto trig after n seconds silence
  ktime_this_event init 0 ; for timeout phrase end trigger
  ktime_this_event = kevent_trig > 0 ? ktime : ktime_this_event
  kphrase_auto_terminate = 2
  ktimeout_phrase_trig trigger ktime-ktime_this_event, kphrase_auto_terminate, 0
  ktimeout_phrase_trig *= krecord_enable
  kanalyzetrig init 0 
  kanalyzetrig += (krec_trig_off + ktimeout_phrase_trig)
  OSCsend kanalyzetrig, "127.0.0.1", 9901, "/client_eventdata", "ffff", -1, -1, -1, -1

  ; send other parameter controls to Python
  kdev_vs_complexity chnget "dev_vs_complexity"
  ksimplify chnget "simplify"
  krhythm_order chnget "gen_rhythm_order"
  kdeviation_order chnget "gen_deviation_order"
  knotenum_order chnget "gen_pitch_order"
  kinterval_order chnget "gen_interval_order"
  kchords_on chnget "chords_on"
  kphrase_reconciliation chnget "phrase_reconciliation"
  kphrase_length chnget "phrase_length"
  kparm_update = changed(kdev_vs_complexity, ksimplify, krhythm_order, 
                      kdeviation_order, knotenum_order, kinterval_order, 
                      kchords_on, kphrase_reconciliation, kphrase_length)
  OSCsend kparm_update, "127.0.0.1", 9901, "/client_parametercontrols", "fffffffff", 
                      kdev_vs_complexity, ksimplify, krhythm_order, 
                      kdeviation_order, knotenum_order, kinterval_order, 
                      kchords_on, kphrase_reconciliation, kphrase_length

  ; receive other data from Python
  ktempo_bpm init 60
  kpulse_subdiv init 1
  kphraselen init 0
  nextmsg_other:
  kmess_other OSClisten gihandle, "python_other", "fff", ktempo_bpm, kpulse_subdiv, kphraselen ; receive OSC data from Python
  cabbageSetValue "tempo_bpm_last_phrase", ktempo_bpm, changed(ktempo_bpm)
  kplay_event_triggered chnget "play_event_triggered"
  cabbageSetValue "gen_tempo_bpm", ktempo_bpm, changed(ktempo_bpm*kauto_tempo_update*kplay_event_triggered)
  cabbageSetValue "pulse_subdiv", kpulse_subdiv, changed(kpulse_subdiv)
  cabbageSetValue "phrase_len", kphraselen, changed(kphraselen)
  if kmess_other == 0 goto done_other
  kgoto nextmsg_other ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done_other:

  ; clear timedata in Python
  kmem_trig = changed(kclear_last_phrase, kclear_all, ksave_all)
  kmem_trig_count init 0
  kmem_trig_count += kmem_trig
  OSCsend kmem_trig_count, "127.0.0.1", 9901, "/client_memory", "iii", kclear_last_phrase, kclear_all, ksave_all
  kinit_clear_index = 1 ; clear index when starting
  kindex = changed(kclear_all, kinit_clear_index) > 0 ? -1 : kindex
  kclear_phrase_trig trigger kclear_last_phrase, 0.5, 0
  kindex = kclear_phrase_trig > 0 ? kindex-kphraselen : kindex
  
  cabbageSetValue "index_this_event", kindex, changed(kclear_last_phrase, kclear_all, kinit_clear_index)+1
  puts "reset index", changed(kclear_last_phrase, kclear_all)+1
  ; clear chord index
  kchord_index chnget "chord_index"
  kchord_index = changed(kclear_all) > 0 ? 0 : kchord_index
  chnset kchord_index, "chord_index"

endin

; *******************************
; generator

; master clock
instr 108

  ; beat clock
  ktempo_bpm chnget "gen_tempo_bpm"
reinit_clock:
  ibeat_clock chnget "beat_clock"
  ;print ibeat_clock, ceil(ibeat_clock)
  kclock_counter init ceil(ibeat_clock)*kr ; when pausing clock, restart form the next whole beat
 rireturn
	kdaw_sync chnget "daw_sync"
  khost_is_playing chnget "IS_PLAYING"
  if (kdaw_sync > 0) then
    kstart_playing trigger khost_is_playing, 0.5, 0
    if kstart_playing > 0 then
      reinit reinit_clock
    endif
    if (khost_is_playing > 0) then
      kclock_counter += (ktempo_bpm/60) ; if daw sync enabled, only run clock if daw is playing
    endif
  else
    kclock_counter += (ktempo_bpm/60) ; if no daw sync just play
  endif
  
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
      event "i", 119, 0, 0.1, kbeat_clock
  endif
endin

; event generator
instr 109
  ivoice = p4
 
	; gen and play events
	ktempo_bpm chnget "gen_tempo_bpm"
  kbeat_clock chnget "beat_clock"  
  kbeat_clock_dry chnget "beat_clock_dry"

	kclock_direction chnget "beat_clock_direction"
	kEvent_queue[] init 10, 7 ; 30 events, 6 parameters each
  kChord_queue[] init 30, 4 ; 30 events, 4 parameters each
  kChord_event[] getrow kChord_queue, 0

  Sbeat_sync sprintf "beat_sync_v%i", ivoice
  kbeat_sync chnget Sbeat_sync
  ibeat_sync = 1
  cabbageSetValue Sbeat_sync, ibeat_sync

  Sbeat_sync_auto sprintf "beat_sync_auto_v%i", ivoice
  kbeat_sync_auto chnget Sbeat_sync_auto
  Sbeat_sync_auto_min sprintf "sync_min_v%i", ivoice
  kbeat_sync_auto_min chnget Sbeat_sync_auto_min
  Sbeat_sync_auto_range sprintf "sync_range_v%i", ivoice
  kbeat_sync_auto_range chnget Sbeat_sync_auto_range
  knext_sync_beat init 0
  if kbeat_sync_auto > 0 then
    kbeat_trig = changed(floor(kbeat_clock))
    if (kbeat_trig > 0) && (kbeat_clock >= knext_sync_beat) then
      knext_sync_beat random kbeat_sync_auto_min, kbeat_sync_auto_min+kbeat_sync_auto_range
      knext_sync_beat = int(knext_sync_beat)+floor(kbeat_clock)
      kbeat_sync = 1
    endif
  endif

  Srequest_type_ sprintf "request_type_v%i", ivoice
  krequest_type chnget Srequest_type_
  Srequest_types[] fillarray "none", "none", "next", "prev", "==", ">", "<", "gradient", "gr_abs" ; pad (copy) item at index zero, as combobox init to 0 but uses 1-indexing thereafter
  Srequest_type = Srequest_types[krequest_type]
  
  Srequest_parm_ sprintf "request_parm_v%i", ivoice
  krequest_parm chnget Srequest_parm_
  Srequest_parms[] fillarray "index", "index", "rhythm", "pitch", "interval", "phrase"
  Srequest_parm = Srequest_parms[krequest_parm]

  Srequest_value sprintf "request_value_v%i", ivoice
  krequest_value chnget Srequest_value
  Srequest_weight sprintf "request_weight_v%i", ivoice
  krequest_weight chnget Srequest_weight

  Stemperature sprintf "gen_v%i_temperature", ivoice
  ktemperature chnget Stemperature
  Sdur_scale sprintf "gen_v%i_duration_scale", ivoice
  kdur_scale chnget Sdur_scale
  Sdeviation_scale sprintf "gen_v%i_deviation_scale", ivoice
  kdeviation_scale chnget Sdeviation_scale
  Srelative_pitch sprintf "gen_v%i_relative_pitch", ivoice
  krelative_pitch chnget Srelative_pitch
  krelative_pitch_range = 19 ; octave and fifth
  krelative_pitch_trig trigger krelative_pitch, 0.5, 0
  krelative_middle_note init 60
  kgen_notenum init 0
  krelative_middle_note = krelative_pitch_trig > 0 ? kgen_notenum : krelative_middle_note
  krelative_pitch_inverter init 1
  iclock_resolution = 10000

  ; event trig
	kgen_once init 1 ; do only the first time
  kgen_index init 0
  kgen_rhythm_subdiv init 0 
  kgen_deviation init 0
  kgen_duration init 1
  kgen_notenum init 0
  kgen_interval init 0
  kgen_velocity init 0
  knext_event_time init -999 ; overwritten on first k-event
	kprevious_rhythm init 0 ; means we will generate two events when starting
  kcount init 0
  kchord_count init 0
  igen_instr = 121
  ktime timeinsts ; for debug
  kprint_time chnget "print_event_time"
  if kprint_time > 0 then
    ;Sevent_time sprintfk "next event %f, beat clock %f", knext_event_time, kbeat_clock
    ;puts Sevent_time, changed(knext_event_time, kbeat_clock)
    printk2 floor(kbeat_clock)
    printk2 knext_event_time, 10
  endif
  ; get event data from server
  if (kbeat_clock > knext_event_time) then
    kplay_event_triggered changed kcount ; trig on any new event
    kplay_event_triggered += 	kgen_once
    chnset kplay_event_triggered, "play_event_triggered"
    if strcmpk(Srequest_parm, "index") == 0 then 
      if (strcmpk(Srequest_type, "next") == 0) || (strcmpk(Srequest_type, "prev") == 0) then
        krequest_value = kgen_index ; request next/previous index
        cabbageSetValue Srequest_value, krequest_value, changed(krequest_value)
      endif
    endif
    OSCsend kcount, "127.0.0.1", 9901, "/client_prob_gen", "ffssfff", ivoice, kgen_index, Srequest_type, Srequest_parm, krequest_value, krequest_weight, ktemperature
  nextmsg:
    Saddr sprintf "python_prob_gen_voice%i", ivoice
    kmess OSClisten gihandle, Saddr, "fffffff", kgen_index, kgen_rhythm_subdiv, kgen_deviation, kgen_duration, kgen_notenum, kgen_interval, kgen_velocity ; receive OSC data from Python
    ;Sdebug sprintfk "received i:%i, rhythm:%f, dev:%f, dur:%f, note:%i", kgen_index, kgen_rhythm_subdiv, kgen_deviation, kgen_duration, kgen_notenum
    ;kdebug_print init 1
    ;kdebug_print += kmess
    ;puts Sdebug, kdebug_print
    if kmess == 0 goto done
      ; store events in queue for playback
      if kgen_rhythm_subdiv > 0 then ; if it is not a chord event
        knext_event_time += round(kprevious_rhythm*iclock_resolution)/iclock_resolution ; prevent accumulative rounding errors
	      if kbeat_sync == 1 then
           knext_event_time = ceil(kbeat_clock) ; sync to whole beat clock if enabled
           kzero = 0
           cabbageSetValue Sbeat_sync, kzero, changed(knext_event_time)
        endif
        ;Sdebug sprintfk "receive: voice %i, ndx %i, beat clock %.2f, next event %.2f, ratio %.2f, note %i vel %.2f dur %.2f", ivoice, kgen_index, kbeat_clock, knext_event_time, kgen_rhythm_subdiv, kgen_notenum, kgen_velocity, kgen_duration
        ;puts Sdebug, knext_event_time+kgen_rhythm_subdiv+kgen_deviation+kgen_notenum
        
	      kdeviation = kgen_deviation * kdeviation_scale 
        kEvent_queue[kcount % lenarray(kEvent_queue)][0] = knext_event_time
        kEvent_queue[(kcount+1) % lenarray(kEvent_queue)][0] = knext_event_time + kgen_rhythm_subdiv + kdeviation; store this event time with deviation, for correct playback
        kEvent_queue[kcount % lenarray(kEvent_queue)][2] = kgen_duration*kgen_rhythm_subdiv
        kEvent_queue[kcount % lenarray(kEvent_queue)][3] = kgen_notenum
        kEvent_queue[kcount % lenarray(kEvent_queue)][4] = kgen_interval
        kEvent_queue[kcount % lenarray(kEvent_queue)][5] = kgen_velocity
        kEvent_queue[kcount % lenarray(kEvent_queue)][6] = -1 ; is not a chord
        kprevious_rhythm = kgen_rhythm_subdiv
        kcount += 1
        ;printarray kEvent_queue
      else
        kdeviation = kgen_deviation * kdeviation_scale 
        kChord_event[0] = (kcount-1) % lenarray(kEvent_queue) ; we use the kcount event counter to synchronize base events and chord events on playback
        kChord_event[1] = kdeviation
        kChord_event[2] = kgen_interval
        kChord_event[3] = kgen_velocity
        kChord_queue setrow kChord_event, kchord_count
        if changed(kcount) > 0 then
          kEvent_queue[(kcount-1) % lenarray(kEvent_queue)][6] = kchord_count ; store chord event index with base event
        endif
        kchord_count = (kchord_count+1)%lenarray(kChord_queue)
      endif
	    kgen_once = 0
      kgoto nextmsg ; make sure we read all messages in the network buffer
  done:
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
    ;printk2 keventqueue_index
    if krelative_pitch > 0 then
        kgen_notenum = kprev_notenum + (kEvent_queue[keventqueue_index][4]*krelative_pitch_inverter)
      if (kgen_notenum > (krelative_middle_note+krelative_pitch_range)) then
        krelative_pitch_inverter *= -1
        kgen_notenum -= 12
      elseif (kgen_notenum < (krelative_middle_note-krelative_pitch_range)) then
        krelative_pitch_inverter *= -1
        kgen_notenum += 12
      endif
    else
      kgen_notenum = kEvent_queue[keventqueue_index][3]
    endif
    
    ;kDebug_play[] getrow kEvent_queue, keventqueue_index
    ;printarray kDebug_play
    
    kprev_notenum = kgen_notenum
		kgen_velocity = kEvent_queue[keventqueue_index][5]
    kdur = kEvent_queue[keventqueue_index][2]*kdur_scale*(60/ktempo_bpm)
  	event "i", igen_instr, 0, kdur, kgen_notenum, kgen_velocity, ivoice
    kchords_on chnget "chords_on"
    if kchords_on > 0 then
      ; play chord events here
      ; if event is not a chord, it will have -1 in the chord flag of the event data
      kchord_index = kEvent_queue[keventqueue_index][6]
      if kchord_index > -1 then
        ; check Chord queue for events where the first value [0] in the array equals keventqueue_index
        ; play all of those with matching value
        imax_chordnotes = 10
        knum_chordnotes = 0
        play_chord:
        if kChord_queue[kchord_index][0] == keventqueue_index then
          kchordnote_timedev = kChord_queue[kchord_index][1]
          kchordnote_notenum = kChord_queue[kchord_index][2]+kgen_notenum
          kchordnote_velocity = kChord_queue[kchord_index][3]
          event "i", igen_instr, kchordnote_timedev, kdur, kchordnote_notenum, kchordnote_velocity, ivoice
          kchord_index = (kchord_index+1)%lenarray(kChord_queue)
          knum_chordnotes += 1
          if knum_chordnotes < imax_chordnotes then ; just make sure we are not stuck here on accidental garbage data (probably never needed)
            kgoto play_chord
          endif
        endif
      endif
    endif
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
  iamp = ampdbfs(-1)
  aenv expon 1, p3, 0.0001
  ibeat = p4
  imodbeat_ratio chnget "beat_clock_mod_ratio"
  inote = floor(ibeat)%imodbeat_ratio == 0 ? 69 : 57
  icps = cpsmidinn(inote)
  a1 oscil 1, 440
  a1 *= aenv
  a1 *= iamp
  outs a1, a1
  ; midi out
  ichan = 16
  ivel = 100
  noteondur ichan, inote, ivel, p3
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
  ;print p2, inote
  if inote == 0 then
    turnoff
    igoto skip
  endif
  ivel = p5
  ichan = p6
  Sgen_pitch_offset sprintf "gen_v%i_pitch_offset", ichan
  itranspose_voice chnget Sgen_pitch_offset
  inote += itranspose_voice
  aenv expon 1, p3, 0.0001
  a1 oscili ivel/127, cpsmidinn(inote)
  a1 *= (aenv*iamp)
  outs a1, a1
  ; midi out
  noteondur ichan, inote, ivel, p3
  skip:
endin

</CsInstruments>
<CsScore>
i1 0 86400 ; Gui handling
i31 0 86400 ; OSC processing
</CsScore>
</CsoundSynthesizer>
