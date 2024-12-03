<Cabbage>
form size(800, 500), caption("Rhythm Analyzer"), pluginId("rtm1"), guiMode("queue"), colour(30,40,40)

; recording and analysis
button bounds(5, 5, 70, 20), text("record","recording"), channel("record_enable"), colour:0("green"), colour:1("red")
button bounds(90, 5, 60, 20), text("clear"), channel("clear"), colour:0("green"), colour:1("red"), latched(0)
button bounds(170, 5, 70, 20), text("play_last_prase"), channel("play_last_phrase"), colour:0("green"), colour:1("red")
nslider bounds(245, 35, 40, 25), text("tempo_last_phrase"), channel("tempo_bps_last_phrase"), range(0.1, 100, 1), fontSize(14)
nslider bounds(90, 35, 50, 22), channel("tempo_tendency"), range(-10, 10, 0), fontSize(14)
label bounds(90, 60, 100, 18), text("tpo_tendency"), fontSize(12), align("left")

nslider bounds(300, 5, 40, 25), text("benni"), channel("benni_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(350, 5, 40, 25), text("n+d"), channel("nd_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(400, 5, 40, 25), text("r_dev"), channel("ratio_dev_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(450, 5, 40, 25), text("r_maxdev"), channel("ratio_dev_abs_max_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(500, 5, 40, 25), text("grid"), channel("grid_dev_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(550, 5, 40, 25), text("evidence"), channel("evidence_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(600, 5, 40, 25), text("acorr"), channel("autocorr_weight"), range(0, 1, 1), fontSize(14)

; generate events with prob logic
button bounds(300, 150, 70, 20), text("generate"), channel("generate"), colour:0("green"), colour:1("red")
nslider bounds(380, 150, 40, 25), channel("gen_tempo_bpm"), range(1, 3000, 60), fontSize(14)
nslider bounds(440, 150, 40, 25), channel("gen_r1_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
nslider bounds(500, 150, 40, 25), channel("gen_r2_order"), range(0, 4, 2, 1, 0.5), fontSize(14)
nslider bounds(560, 150, 40, 25), channel("gen_temperature"), range(0.01, 10, 0.2, 1, 0.01), fontSize(14)
label bounds(380, 175, 70, 18), text("g_tempo"), fontSize(12), align("left")
label bounds(440, 175, 70, 18), text("g_r1_ord"), fontSize(12), align("left")
label bounds(500, 175, 70, 18), text("g_r2_ord"), fontSize(12), align("left")
label bounds(560, 175, 70, 18), text("g_temp"), fontSize(12), align("left")

button bounds(610, 150, 40, 20), text("dwnbeat sync"), channel("downbeat_sync"), colour:0("green"), colour:1("red"), latched(1)
nslider bounds(655, 150, 40, 25), channel("downbeat_sync_strength"), range(0, 1, 0.5), fontSize(14)
label bounds(655, 175, 70, 18), text("sync_w"), fontSize(12), align("left")
; debug
button bounds(710, 150, 40, 20), text("print stm"), channel("pl_print"), colour:0("green"), colour:1("red"), latched(0)

csoundoutput bounds(5, 200, 690, 295)
</Cabbage>

<CsoundSynthesizer>
<CsOptions>
-n -d -m0 -+rtmidi=NULL -M0 -Q0
;-n -+rtmidi=NULL -M0 -Q0
</CsOptions>

<CsInstruments>

;sr = 48000 ; set by host
ksmps = 32
nchnls = 2
0dbfs = 1

massign -1, 2
pgmassign 0, -1 ; ignore program change

gitrig_ftab ftgen 0, 0, 4096, 2, 0
gitrig_ftab_empty ftgen 0, 0, 4096, 2, 0
gihandle OSCinit 9999 ; set the network port number where we will receive OSC data from Python


; GUI handling
instr 1
  kplay chnget "play_last_phrase"
  ktrig_play trigger kplay, 0.5, 0
  ktrig_stop trigger kplay, 0.5, 1
  if ktrig_play > 0 then
    event "i", 3, 0, -1
  endif
  if ktrig_stop > 0 then
    event "i", -3, 0, .1
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
  kprint chnget "pl_print"
  kprint_on trigger kprint, 0.5, 0
  if kprint_on > 0 then
    event "i", 110, 0, .1
  endif
endin

; rhythm recording instr, triggered by midi input
instr 2
  print p1, p2, p3
  iprevious_event_time chnget "previous_event_time"
  chnset p2, "previous_event_time"
  imin_delta_time chnget "minimum_delta_time"
  if p2 > iprevious_event_time + (imin_delta_time/1000) then
    ktrig init 1
    chnset ktrig, "new_event_trig"
    ktrig = 0
  endif
endin

; play trigger rhythm
instr 3
  ktempo chnget "tempo_bps_last_phrase"
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

  knew_event_trig chnget "new_event_trig"
  krecord_enable chnget "record_enable"
  krec_trig_on trigger krecord_enable, 0.5, 0 
  krec_trig_off trigger krecord_enable, 0.5, 1 ; stop recording, trigger the analysis process in Python 
  kclear chnget "clear"

  ktime timeinsts
  ; initialize variables that will be used in the communication with Python
  kindex init 0
  ktimenow init 0
  ktimenow = knew_event_trig > 0 ? ktime : ktimenow
  
  
  ; send time data to Python
  if knew_event_trig > 0 then
    OSCsend kindex+1, "127.0.0.1", 9901, "/client_timevalues", "ff", kindex, ktimenow
    kindex += 1
  endif
  ; if Python skips an index (due to invalid data), we update our index counter so it is equal to the index counter in Python
  skipindex:
    kskipindex OSClisten gihandle, "python_skipindex", "i", kindex  ; if Python skipped this index, update our index
    if kskipindex == 0 goto done_skipindex
    kgoto skipindex ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done_skipindex:

  ; send analyze trigger to Python
  kanalyzetrig init 0
  kanalyzetrig += krec_trig_off
  k_unused = 1
  OSCsend kanalyzetrig, "127.0.0.1", 9901, "/client_analyze_trig", "i", k_unused
  ; clear timedata in Python
  OSCsend changed(kclear), "127.0.0.1", 9901, "/client_clear", "i", kclear
  kindex = changed(kclear) > 0 ? 0 : kindex
  puts "reset index", changed(kclear)

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
  if krec_trig_off+kclear > 0 then
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
  nextmsg_other:
  kmess_other OSClisten gihandle, "python_other", "fff", kticktempo_bpm,ktempo_tendency,kpulseposition ; receive OSC data from Python
  cabbageSetValue "tempo_bps_last_phrase", kticktempo_bpm/60, changed(kmess_other)
  cabbageSetValue "gen_tempo_bpm", kticktempo_bpm/kpulseposition, changed(kmess_other)
  cabbageSetValue "tempo_tendency", ktempo_tendency, changed(kmess_other)
  if kmess_other == 0 goto done_other
  kgoto nextmsg_other ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done_other:

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
    event "i", idownbeat_instr, 0, 0.3
  endif

  ;kratio_set chnget "ratio_set"
  ;kindex_set chnget "index_set"
  ;kupdate changed kratio_set, kindex_set
  kindex init 0
  krequest_ratio init -1
  krequest_weight = kdownbeat_sync_strength ; may not necessary to rename/patch this, if it will only be used for that purpose
  inoise_instr = 120
  ; event trig
  kratio init 1
  knext_event_time init 0
  kget_event = (kbeat_clock > knext_event_time) ? 1 : 0 ; if current time is greater than the time for the next event, then activate
  kget_event_trig trigger kget_event, 0.5, 0
  kcount init 0
  kcount += kget_event_trig
  if kget_event_trig > 0 then
    knext_event_time += round(kratio*iclock_resolution)/iclock_resolution 
    event "i", inoise_instr, 0, 0.1
    OSCsend kcount, "127.0.0.1", 9901, "/client_prob_gen", "fff", kindex, krequest_ratio, krequest_weight
  endif
  nextmsg:
    kmess OSClisten gihandle, "python_prob_gen", "ff", kindex, kratio ; receive OSC data from Python
    if kmess == 0 goto done
    kgoto nextmsg ; make sure we read all messages in the network buffer
  done:
  
  kratio_to_next_downbeat = knext_downbeat_time-knext_event_time
  krequest_ratio = kdownbeat_sync > 0 ? kratio_to_next_downbeat : -1 ; in case we want to request a ratio that will sync to next downbeat 
endin

; print prob logic stm
instr 110
    OSCsend 1, "127.0.0.1", 9901, "/client_prob_print", "f", 1
endin

; downbeat instr
instr 119
  iamp = ampdbfs(-15)
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

</CsInstruments>
<CsScore>
i1 0 86400 ; Gui handling
i31 0 86400 ; OSC processing
</CsScore>
</CsoundSynthesizer>
