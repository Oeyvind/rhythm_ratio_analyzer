<Cabbage>
form size(800, 500), caption("Rhythm Analyzer"), pluginId("rtm1"), guiMode("queue"), colour(30,40,40)

button bounds(5, 5, 70, 20), text("record","recording"), channel("record_enable"), colour:0("green"), colour:1("red")
button bounds(90, 5, 60, 20), text("clear"), channel("clear"), colour:0("green"), colour:1("red"), latched(0)
button bounds(170, 5, 70, 20), text("play"), channel("play"), colour:0("green"), colour:1("red")
nslider bounds(245, 5, 40, 25), text("tempo"), channel("tempo_bps"), range(0.1, 100, 1), fontSize(14)

nslider bounds(300, 5, 40, 25), text("benni"), channel("benni_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(350, 5, 40, 25), text("n+d"), channel("nd_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(400, 5, 40, 25), text("r_dev"), channel("ratio_dev_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(450, 5, 40, 25), text("r_maxdev"), channel("ratio_dev_abs_max_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(500, 5, 40, 25), text("grid"), channel("grid_dev_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(550, 5, 40, 25), text("evidence"), channel("evidence_weight"), range(0, 1, 1), fontSize(14)
nslider bounds(600, 5, 40, 25), text("acorr"), channel("autocorr_weight"), range(0, 1, 1), fontSize(14)
button bounds(650, 5, 40, 20), text("calc"), channel("calc"), colour:0("green"), colour:1("red"), latched(0)
combobox channel("rank"), bounds(700, 5, 60, 20), text("1", "2", "3", "4", "5", "6", "7", "8"), value(1)
label bounds(760, 5, 60, 20), text("Rank"), fontSize(12), align("left")

label bounds(690, 125, 60, 20), text("min_delta"), fontSize(12), align("left")
nslider bounds(750, 125, 40, 25), channel("minimum_delta_time"), range(0, 100, 50), fontSize(14)


label bounds(5, 40, 80, 20), text("Time Series"), fontSize(12), align("left")
texteditor bounds(85, 40, 710, 20), channel("time_series"), fontSize(15), colour("black"), fontColour("white"), caretColour("white")
label bounds(5, 70, 80, 20), text("Rhythm Ratios"), fontSize(12), align("left")
texteditor bounds(85, 70, 710, 20), channel("rhythm_ratios"), fontSize(15), colour("black"), fontColour("white"), caretColour("white")
label bounds(5, 100, 80, 20), text("Deviations"), fontSize(12), align("left")
texteditor bounds(85, 100, 710, 20), channel("deviations"), fontSize(15), colour("black"), fontColour("white"), caretColour("white")

nslider bounds(5, 150, 50, 22), channel("ticktempo_bpm"), range(10, 5000, 100), fontSize(14)
nslider bounds(110, 150, 50, 22), channel("tempo_tendency"), range(-10, 10, 0), fontSize(14)
nslider bounds(220, 150, 50, 22), channel("pulseposition"), range(0, 20, 0, 1, 1), fontSize(14)
label bounds(5, 175, 100, 18), text("ticktempo_bpm"), fontSize(12), align("left")
label bounds(110, 175, 100, 18), text("tempo_tendency"), fontSize(12), align("left")
label bounds(220, 175, 100, 18), text("pulseposition"), fontSize(12), align("left")

button bounds(400, 150, 70, 20), text("generate"), channel("generate"), colour:0("green"), colour:1("red")
nslider bounds(480, 150, 40, 25), channel("gen_tempo_bpm"), range(1, 3000, 60), fontSize(14)
nslider bounds(540, 150, 40, 25), channel("gen_order"), range(0, 2, 2, 1, 0.5), fontSize(14)
nslider bounds(600, 150, 40, 25), channel("gen_dimension"), range(1, 2, 2, 1, 1), fontSize(14)
label bounds(480, 175, 70, 18), text("g_tempo"), fontSize(12), align("left")
label bounds(540, 175, 70, 18), text("g_order"), fontSize(12), align("left")
label bounds(600, 175, 70, 18), text("g_dim"), fontSize(12), align("left")
button bounds(650, 150, 40, 20), text("print stm"), channel("mm_print"), colour:0("green"), colour:1("red"), latched(0)

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
  kplay chnget "play"
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
  ; print markov stm
  kprint chnget "mm_print"
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
    chnset ktrig, "trig"
    ktrig = 0
  endif
endin

; play trigger rhythm
instr 3
  ktempo chnget "tempo_bps"
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

  ktrig chnget "trig"
  krecord_enable chnget "record_enable"
  kclear chnget "clear"
  krank chnget "rank"
  kcalc chnget "calc" ; force calculation without record or rank

  ktime timeinsts
  ; initialize variables that will be used in the communication with Python
  kindex init 0
  ktimenow init 0
  ktimenow = ktrig > 0 ? ktime : ktimenow
  
  krec_trig_on trigger krecord_enable, 0.5, 0 
  krec_trig_off trigger krecord_enable, 0.5, 1 ; we use this as a "string termination", to trigger the analysis process in Python 

  if krec_trig_on > 0 then
    cabbageSet changed(kindex+1), "time_series", "text", ""
  endif
  
  ; send time data to Python
  if ktrig > 0 then
    OSCsend kindex+1, "127.0.0.1", 9901, "/csound_timevalues", "ff", kindex, ktimenow
    Stimevalues cabbageGetValue "time_series"
    kstrlen strlenk Stimevalues
    if kstrlen < 1 then
      Stimevalues1 sprintfk "%.1f", ktimenow
    else
      Stimevalues1 sprintfk "%s, %.1f", Stimevalues, ktimenow
    endif
    cabbageSet changed(kindex+1), "time_series", "text", Stimevalues1
    kindex += 1
  endif

  ; send analyze trigger to Python
  kanalyzetrig init 0
  kanalyzetrig += (changed(krank,kcalc)+krec_trig_off)
  OSCsend kanalyzetrig, "127.0.0.1", 9901, "/csound_analyze_trig", "i", krank
  ; clear timedata in Python
  OSCsend changed(kclear), "127.0.0.1", 9901, "/csound_clear", "i", kclear
  
  ; send other parameter controls to Python
  kbenni_weight chnget "benni_weight"
  knd_weight chnget "nd_weight"
  kratio_dev_weight chnget "ratio_dev_weight"
  kratio_dev_abs_max_weight chnget "ratio_dev_abs_max_weight"
  kgrid_dev_weight chnget "grid_dev_weight"
  kevidence_weight chnget "evidence_weight"
  kautocorr_weight chnget "autocorr_weight"
  kminimum_delta_time chnget "minimum_delta_time"
  
  OSCsend changed(kbenni_weight, knd_weight, kratio_dev_weight, 
                  kratio_dev_abs_max_weight, kgrid_dev_weight, 
                  kevidence_weight, kautocorr_weight, kminimum_delta_time), 
                  "127.0.0.1", 9901, "/csound_parametercontrols", "ffffffff", 
                  kbenni_weight, knd_weight, kratio_dev_weight, 
                  kratio_dev_abs_max_weight, kgrid_dev_weight, 
                  kevidence_weight, kautocorr_weight, kminimum_delta_time

  ; receive and process rhythm ratio data from Python
  knum init 1
  kdenom init 1
  kdeviation init 0
  kreceive_counter init 0
  Srhythmstring = "" ; just init, we reset them after updating the gui
  Sdevstring = "" 
  nextmsg_rhythm: 
  kmess_rhythm OSClisten gihandle, "python_rhythmdata", "iif", knum, kdenom, kdeviation ; receive OSC data from Python
  if kmess_rhythm == 0 goto done_rhythm
  kreceive_counter += 1
  if knum != -1 then
    Srhythmstring strcatk Srhythmstring, sprintfk("%i/%i, ", knum, kdenom)
    Sdevstring strcatk Sdevstring, sprintfk("%.2f, ", kdeviation)    
  else  
    kstrlen_r strlenk Srhythmstring
    Srhythmstring strsubk Srhythmstring, 0, kstrlen_r-2
    kstrlen_d strlenk Sdevstring
    Sdevstring strsubk Sdevstring, 0, kstrlen_d-2
    cabbageSet changed(Srhythmstring), "rhythm_ratios", "text", Srhythmstring
    cabbageSet changed(Sdevstring), "deviations", "text", Sdevstring
    Srhythmstring strcpyk ""
    Sdevstring strcpyk ""
  endif
  kgoto nextmsg_rhythm ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done_rhythm:

  ; receive trigger string from Python
  ktrig_sig init 0
  ktrig_index init 0
  if krec_trig_off+changed(krank)+kclear > 0 then
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
  cabbageSetValue "ticktempo_bpm", kticktempo_bpm, changed(kmess_other)
  cabbageSetValue "tempo_bps", kticktempo_bpm/60, changed(kmess_other)
  cabbageSetValue "gen_tempo_bpm", kticktempo_bpm/kpulseposition, changed(kmess_other)
  cabbageSetValue "tempo_tendency", ktempo_tendency, changed(kmess_other)
  cabbageSetValue "pulseposition", kpulseposition, changed(kmess_other)
  if kmess_other == 0 goto done_other
  kgoto nextmsg_other ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done_other:

endin

; *******************************
; generator

instr 109
  ktempo_bpm chnget "gen_tempo_bpm"
  ktempo = ktempo_bpm/60
  kbeat_duration = 60/ktempo_bpm
  korder chnget "gen_order" ; Markov-ish order, may be fractional, up to 2nd order
  kdimension chnget "gen_dimension"
  ; play it
  ;kmetrotempo init 1
  ;ktrig metro kmetrotempo

  ; alternative clock based on delta time to next event
  ktime timeinsts
  knext_event_time init 0
  kget_event = (ktime > knext_event_time) ? 1 : 0 ; if current time is greater than the time for the next event, then activate
  ktrig trigger kget_event, 0.5, 0
  ;kratio_set chnget "ratio_set"
  ;kindex_set chnget "index_set"
  ;kupdate changed kratio_set, kindex_set
  kupdate init 0
  kratio init 1
  kindex init 0
  krequest_item init -1
  kcount init 0
  kcount += ktrig
  inoise_instr = 120
  if ktrig > 0 then
    ktime_then = ktime
    event "i", inoise_instr, 0, 0.1
    OSCsend kcount, "127.0.0.1", 9901, "/csound_markov_gen", "ffffff", korder, kdimension, kindex, kratio, krequest_item, kupdate
  endif
  nextmsg:
    kmess OSClisten gihandle, "python_markov_gen", "ff", kindex, kratio ; receive OSC data from Python
    if kmess == 0 goto done
    kgoto nextmsg ; jump back to the OSC listen line, to see if there are more messages waiting in the network buffer
  done:
  ;kmetrotempo = ktempo/kratio
  knext_event_time = ktime_then + (kratio*kbeat_duration)

endin

; print markov stm
instr 110
    OSCsend 1, "127.0.0.1", 9901, "/csound_markov_print", "f", 1
endin

; rhythm trig player
instr 120
  aenv expon 1, p3, 0.0001
  anoise rnd31 1, 1
  anoise *= aenv
  outs anoise, anoise
endin

</CsInstruments>
<CsScore>
i1 0 86400 ; Gui handling
i31 0 86400 ; OSC processing
</CsScore>
</CsoundSynthesizer>
