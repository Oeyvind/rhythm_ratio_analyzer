<Cabbage>
form size(605, 410), caption("Rhythm Analyzer"), pluginId("rtm1"), guiMode("queue"), colour(46,45,52)

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

groupbox bounds(5, 135, 590, 65), text("generate events with prob logic"), colour(25,45,30){
button bounds(10, 25, 70, 30), text("generate"), channel("generate"), colour:0("green"), colour:1("red")
nslider bounds(95, 25, 40, 25), channel("gen_tempo_bpm"), range(1, 2999, 60), fontSize(14)
label bounds(95, 45, 60, 18), text("g_tempo"), fontSize(12), align("left")
nslider bounds(155, 25, 40, 25), channel("gen_r1_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(155, 45, 60, 18), text("g_r1_ord"), fontSize(12), align("left")
nslider bounds(220, 25, 40, 25), channel("gen_r2_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
label bounds(220, 45, 60, 18), text("g_r2_ord"), fontSize(12), align("left")
nslider bounds(285, 25, 40, 25), channel("gen_temperature"), range(0.01, 10, 0.2, 1, 0.01), fontSize(14)
label bounds(285, 45, 60, 18), text("g_temp"), fontSize(12), align("left")

button bounds(350, 25, 45, 30), text("metro"), channel("gen_metro_on"), colour:0("green"), colour:1("red"), latched(1)
button bounds(400, 25, 50, 30), text("dwnbeat sync"), channel("downbeat_sync"), colour:0("green"), colour:1("red"), latched(1)
nslider bounds(455, 25, 40, 25), channel("downbeat_sync_strength"), range(0, 1, 0.5), fontSize(14)
label bounds(455, 45, 60, 18), text("sync_w"), fontSize(12), align("left")
; debug
button bounds(520, 25, 50, 30), text("print stm"), channel("pl_print"), colour:0("green"), colour:1("red"), latched(0)
}
csoundoutput bounds(5, 205, 560, 200)
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
gkNote_index[] init 127 ; holds indices or each notenum (last time that notenum appeared, it had index N). For polyphny control in recordding.

gitrig_ftab ftgen 0, 0, 4096, 2, 0
gitrig_ftab_empty ftgen 0, 0, 4096, 2, 0
gihandle OSCinit 9999 ; set the network port number where we will receive OSC data from Python


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
    event "i", 109, 0, -1
  endif
  if ktrig_generate_stop > 0 then
    event "i", -109, 0, .1
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
  ivel veloc
  chnset k(inum), "notenum"
  chnset k(ivel), "velocity"
  ktrig_on init 1 ; do once
  ktrig_on = 0
  xtratim 2/kr
  krelease release
  krelease_trig trigger krelease, 0.5, 0
  kactive active p1
  if (kactive == 1) && (krelease > 0) then
    kactive -= 1
  endif
  k_prev init 0
  kchange = kactive-k_prev
  k_prev = kactive
  kevent_trig_on = kchange > 0 ? 1 : 0
  kevent_trig_off = kchange < 0 ? 1 : 0
  chnset kevent_trig_on, "event_trig_on"
  chnset kevent_trig_off, "event_trig_off"
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
  kevent_trig_on chnget "event_trig_on"
  kevent_trig_off chnget "event_trig_off"
  kevent_trig = (kevent_trig_on + kevent_trig_off) > 0 ? 1 : 0
  kevent_onoff = kevent_trig_on > 0 ? 1 : 0
  knotenum chnget "notenum"
  printk2 knotenum
  kvelocity chnget "velocity"

  krecord_enable chnget "record_enable"
  krec_trig_off trigger krecord_enable, 0.5, 1 ; stop recording, trigger the analysis process in Python 
  kclear_last_phrase chnget "clear_last_phrase"
  kclear_all chnget "clear_all"
  ksave_all chnget "save_all"

  ktime timeinsts  
  kindex init 0
  ;ktimenow init 0
  ; ktimenow = kevent_trig > 0 ? ktime : ktimenow
  

  ; send time data to Python
  if krecord_enable > 0 then
    kindex += kevent_trig_on
    if kevent_trig_on > 0 then ; polyphony management in reording, keep same index for note on and off
      gkNote_index[knotenum] = kindex
    endif
    if kevent_trig_off > 0 then
      kindex = gkNote_index[knotenum] ; will only be active for note offs
    endif
    if kevent_trig > 0 then
      OSCsend ktime, "127.0.0.1", 9901, "/client_eventdata", "fffff", kindex, ktime, kevent_onoff, knotenum, kvelocity
    endif
    ; if Python skips an index (due to invalid data), we update our index counter so it is equal to the index counter in Python
    skipindex:
      kskipindex OSClisten gihandle, "python_skipindex", "i", kindex  ; if Python skipped this index, update our index
      if kskipindex == 0 goto done_skipindex
      kgoto skipindex ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
    done_skipindex:
    if kevent_trig_on > 0 then
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
  ktemperature chnget "gen_temperature"
  kparm_update = changed(kbenni_weight, knd_weight, kratio_dev_weight, 
                      kratio_dev_abs_max_weight, kgrid_dev_weight, 
                      kevidence_weight, kautocorr_weight, kratio1_order, 
                      kratio2_order, ktemperature)
  OSCsend kparm_update, "127.0.0.1", 9901, "/client_parametercontrols", "ffffffffff", 
                      kbenni_weight, knd_weight, kratio_dev_weight, 
                      kratio_dev_abs_max_weight, kgrid_dev_weight, 
                      kevidence_weight, kautocorr_weight, kratio1_order, 
                      kratio2_order, ktemperature

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
  cabbageSetValue "gen_tempo_bpm", ktempo_bpm, changed(ktempo_bpm)
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
  kindex = changed(kclear_all) > 0 ? 0 : kindex
  kclear_phrase_trig trigger kclear_last_phrase, 0.5, 0
  kindex = kclear_phrase_trig > 0 ? kindex-kphraselen : kindex
  puts "reset index", changed(kclear_last_phrase, kclear_all)

endin

; *******************************
; generator

instr 109
  ktempo_bpm chnget "gen_tempo_bpm"
  korder chnget "gen_order" ; Markov-ish order, may be fractional, up to 2nd order
  kdimension chnget "gen_dimension"
  kdownbeat_sync chnget "downbeat_sync"
  kdownbeat_sync_strength chnget "downbeat_sync_strength"
  ktemperature chnget "gen_temperature"
  kmetro_on chnget "gen_metro_on"

  ; beat clock
  kclock_counter init 0
  kclock_counter += (ktempo_bpm/60)
  kbeat_clock = (kclock_counter/kr)
  iclock_resolution = 10000 ; 0.1 millisec

  ; downbeat trig
  knext_downbeat_time init 0
  kdownbeat = (kbeat_clock > knext_downbeat_time) ? 1 : 0 
  ktrig_downbeat trigger kdownbeat, 0.5, 0
  kzero = 0
  if ktrig_downbeat > 0 then
    cabbageSetValue "downbeat_sync", kzero
    knext_downbeat_time += 1
    idownbeat_instr = 119
    if kmetro_on > 0 then
      event "i", idownbeat_instr, 0, 0.3
    endif
  endif

  krequest_ratio init -1
  krequest_weight = kdownbeat_sync_strength ; may not necessary to rename/patch this, if it will only be used for that purpose
  igen_instr = 121
  ; event trig
  kgen_index init 0
  kgen_ratio init 1
  kgen_duration init 1
  kgen_notenum init 0
  kgen_velocity init 0
  knext_event_time init 0
  kget_event = (kbeat_clock > knext_event_time) ? 1 : 0 ; if current time is greater than the time for the next event, then activate
  kget_event_trig trigger kget_event, 0.5, 0
  kcount init 0
  kcount += kget_event_trig
  if kget_event_trig > 0 then
    knext_event_time += round(kgen_ratio*iclock_resolution)/iclock_resolution 
    kdur = kgen_duration*(60/ktempo_bpm)
    printk2 kgen_duration
    event "i", igen_instr, 0, kdur, kgen_notenum, kgen_velocity
    OSCsend kcount, "127.0.0.1", 9901, "/client_prob_gen", "fff", kgen_index, krequest_ratio, krequest_weight
  endif
  nextmsg:
    kmess OSClisten gihandle, "python_prob_gen", "fffff", kgen_index, kgen_ratio, kgen_duration, kgen_notenum, kgen_velocity ; receive OSC data from Python
    if kmess == 0 goto done
    kgoto nextmsg ; make sure we read all messages in the network buffer
  done:
  
  kratio_to_next_downbeat = knext_downbeat_time-knext_event_time
  krequest_ratio = kdownbeat_sync > 0 ? kratio_to_next_downbeat : -1 ; in case we want to request a ratio that will sync to next downbeat 
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
  aenv expon 1, p3, 0.0001
  a1 oscili ivel/127, cpsmidinn(inote)
  a1 *= aenv
  a1 *= iamp
  outs a1, a1
  ; midi out
  ichan = 1
  noteondur ichan, inote, ivel, p3

endin

</CsInstruments>
<CsScore>
i1 0 86400 ; Gui handling
i31 0 86400 ; OSC processing
</CsScore>
</CsoundSynthesizer>
