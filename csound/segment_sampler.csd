<Cabbage>
form size(490, 330), caption("Segment Sampler"), pluginId("sgs2"), colour(20,35,35), guiMode("queue")
label bounds(10, 6, 64, 10), text("Rec_arm"), align("left")
checkbox bounds(10, 20, 50, 30), channel("rec_arm"), colour:0(0,142,0),  colour:1(142, 0, 0)
nslider bounds(90, 5, 55, 30), channel("segment_rec"), range(0, 9999, 0, 1, 1), text("current_rec")
checkbox bounds(90, 40, 55, 10), channel("recording"), colour:0(0,142,0),  colour:1(142, 0, 0)
nslider bounds(180, 5, 55, 30), channel("segment_play"), range(0, 9999, 0, 1, 1), text("curr_play")
button bounds(360, 5, 50, 30), channel("clear"), text("Clear"), colour:0(0,142,0),  colour:1(142, 0, 0), latched(0)
button bounds(360, 50, 50, 20), channel("debug"), text("print"), colour:0(0,142,0),  colour:1(142, 0, 0), latched(0)

;nslider bounds(10, 90, 50, 25), channel("noisefloor"), range(-60, 0, -50, 1)
;nslider bounds(80, 90, 50, 25), channel("low_transientThresh"), range(-60, 0, -35, 1)
;nslider bounds(150, 90, 50, 25), channel("amp_transientThresh"), range(0, 20, 7, 1)
;nslider bounds(220, 90, 50, 25), channel("amp_transientDoubleLimit"), range(0.01, 2, 0.1, 1, 0.01)
;nslider bounds(290, 90, 50, 25), channel("amp_transientDecThresh"), range(0, 20, 1, 1)
;nslider bounds(360, 90, 50, 25), channel("amp_transientDecTime"), range(0.1, 10, 1, 1)
;label bounds(10, 115, 64, 10), text("noisefloor"), align("left")
;label bounds(80, 115, 64, 10), text("low_level"), align("left")
;label bounds(150, 115, 64, 10), text("trans thresh"), align("left")
;label bounds(220, 115, 64, 10), text("double limit"), align("left")
;label bounds(290, 115, 64, 10), text("dec thresh"), align("left")
;label bounds(360, 115, 64, 10), text("dec time"), align("left")

nslider channel("predelay"), bounds(10, 55, 50, 25), text("Predelay"), range(0.0, 20, 12, 0.5)

nslider channel("noisefloor"), bounds(10, 90, 50, 25), text("Noise floor"), range(-90, 0, -40, 1, 1)
nslider channel("trans_thresh"), bounds(80, 90, 50, 25), text("T.thresh"), range(0, 30, 2.5)
nslider channel("retrig_thresh"), bounds(150, 90, 50, 25), text("T.retrig"), range(0, 30, 2)
nslider channel("low_trans"), bounds(220, 90, 50, 25), text("T.lowlimit"), range(-50, -5, -30, 1, 1)
nslider channel("double_limit"), bounds(290, 90, 50, 25), text("T.dbl.lim"), range(0.01, 0.5, 0.05, 0.35)
nslider channel("shape"), bounds(360, 90, 50, 25), text("Shape"), range(0.3, 3, 1, 0.35)
nslider channel("amp_trans"), bounds(430, 90, 50, 25), text("Amp_amt"), range(0.0, 1, 1, 0.35)

csoundoutput bounds(5, 125, 480, 200)
</Cabbage>
<CsoundSynthesizer>
<CsOptions>
-n -+rtmidi=null -Q0 -M0 
</CsOptions>
<CsInstruments>

ksmps = 32
nchnls = 2
0dbfs = 1
massign -1, 2

giLiveRecLen = 16777216    ; almost 6 minutes (349.5 secs) buffer at 48kHz
giLiveRecLenSec	= giLiveRecLen/sr
giLiveRec ftgen	1, 0, giLiveRecLen, 2, 0; table to hold live audio
giStartMarkers ftgen 0, 0, 1024, 2, 0 ; table to hold segment start markers
giEndMarkers ftgen 0, 0, 1024, 2, 0 ; table to hold segment end markers
giLiveRecEmpty ftgen	1, 0, giLiveRecLen, 2, 0; empty
giLiveMarkersEmpty ftgen 0, 0, 1024, 2, 0 ; empty

;***************************************************
; Transient detection udo

opcode TransientDetect, kk,kikkkk
  kin, iresponse, ktthresh, klowThresh, kdecThresh, kdoubleLimit xin 
  /*
  iresponse	= 10 		; response time in milliseconds
  ktthresh	= 6		; transient trig threshold 
  klowThresh	= -60		; lower threshold for transient detection
  kdoubleLimit	= 0.02		; minimum duration between events, (double trig limit)
  kdecThresh	= 6		; retrig threshold, how much must the level decay from its local max before allowing new transient trig
  */	
  kinDel	delayk	kin, iresponse/1000		; delay with response time for comparision of levels
  ktrig		= ((kin > kinDel + ktthresh) ? 1 : 0) 	; if current rms plus threshold is larger than previous rms, set trig signal to current rms
  klowGate	= (kin < klowThresh? 0 : 1)		; gate to remove transient of low level signals
  ktrig		= ktrig * klowGate			; activate gate on trig signal
  ktransLev	init 0
  ktransLev	samphold kin, 1-ktrig			; read amplitude at transient
  
  kreGate	init 1					; retrigger gate, to limit transient double trig before signal has decayed (decThresh) from its local max
  ktrig		= ktrig*kreGate				; activate gate
  kmaxAmp	init -99999
  kmaxAmp	max kmaxAmp, kin			; find local max amp
  kdiff		= kmaxAmp-kin				; how much the signal has decayed since its local max value
  kreGate	limit kreGate-ktrig, 0, 1		; mute when trig detected
  kreGate	= (kdiff > kdecThresh ? 1 : kreGate)	; re-enable gate when signal has decayed sufficiently
  kmaxAmp	= (kreGate == 1 ? -99999 : kmaxAmp)	; reset max amp gauge

  ; avoid closely spaced transient triggers (first trig priority)
  kdouble	init 1
  ktrig		= ktrig*kdouble
  if ktrig > 0 then
    reinit double
  endif
  double:
  idoubleLimit  = i(kdoubleLimit)	
  idoubleLimit  limit idoubleLimit, 1/kr, 5
  kdouble	linseg	0, idoubleLimit, 0, 0, 1, 1, 1
  rireturn

  xout ktrig, kdiff
endop

instr 1
  ; reset current segment record num, regardless of saved value in DAW project
  chnset 0, "segment_rec"
  ; gui handling
  krec chnget "rec_arm"
  ktrig_on trigger krec, 0.5, 0
  ktrig_off trigger krec, 0.5, 1
  if ktrig_on > 0 then
    event "i", 98, 0, -1 ; transient detection
    event "i", 99, 0, -1 ; recording audio
  endif
  if ktrig_off > 0 then
    event "i", -98, 0, 1
    event "i", -99, 0, 1
  endif
  
  kclear  chnget "clear"
  if trigger(kclear, 0.5, 0) > 0 then
    event, "i", 20, 0, 1
  endif

  kdebug chnget "debug"
  ktrig_debug trigger kdebug, 0.5, 0
  if ktrig_debug > 0 then
    event "i", 100, 0, .1
  endif
endin

instr 2
  ; midi trig
  inum notnum
  ;p1 = p1+inum*0.001
  iattacktime = 0.001
  ireleasetime = 0.1
  iseg_num = inum-47 ; segment 1 at 48
  ;print iseg_num
  cabbageSetValue "segment_play", iseg_num
  istart table iseg_num, giStartMarkers
  iend table iseg_num, giEndMarkers
  ;print istart, iend
  idur = ((iend-istart)/sr)-ireleasetime
  ;print inum, p1, p2, idur
  ktime timeinsts
  if ktime > idur then
    turnoff
  endif
  aphs line istart, 1, istart+sr
  a1 tablei aphs, giLiveRec
  aenv transegr 0, iattacktime, 2, 1, 1, 0, 1, ireleasetime, -2, 0
  a1 = a1*aenv
  outs a1, a1
endin

instr 3
  ; reset current segment record num, regardless of saved value in DAW project
  print p2
  chnset 0, "segment_rec"
endin

instr 20
  ; reset
  Smess = "Resetting record buffer and markers"
  puts Smess, 1
  cabbageSetValue  "segment_rec",  0
  tableicopy giLiveRec, giLiveRecEmpty
  tableicopy giStartMarkers, giLiveMarkersEmpty
  tableicopy giEndMarkers, giLiveMarkersEmpty
  chnset 0, "writepos"
endin

instr 98 ; transient detection
  knoiseFloor_dB chnget "noisefloor" ; (-40) noise floor of input signal, no transients detected below the noisefloor  
  iresponse = 10 ; transient detect response time in milliseconds (set and forget)
  ktthresh chnget "trans_thresh" ; (3) transient trig threshold (log scale but not dB, as it refers to variations in both flux and amplitude) 
  klowThresh chnget "low_trans"	; (-20) lower threshold for transient detection (log scale but not dB, as it refers to variations in both flux and amplitude) 
  kdoubleLimit chnget "double_limit" ; (0.02) minimum duration between events, (double trig limit)
  kdecThresh chnget "retrig_thresh"	; (2) retrig threshold, how much must the level decay from its local max before allowing new transient trig (log scale but not dB)
  kshape chnget "shape" ; > 1 makes it less sensitive to soft transients, < 1 makes it more sensitive to soft transients
  
  a1 inch 1
  a2 inch 2
  a1 = a1+a2*0.5
  krms rms a1
  krms_dB = dbfsamp(krms)
  kgate = (krms_dB < knoiseFloor_dB ? 0 : 1)
  chnset kgate, "noisefloor_gate"
  aenv follow2 a1, 0.01, 0.3
 
  ; ***************
  ; spectral analysis L2, low fft size, smoothing, custom window
  ifftsize = 512
  ioverlap = 16
  iwtype = 1
  iwin ftgen 0, 0, ifftsize, 20, 7, 1, 1.5 ;  KAISER
  fsin pvsanal a1, ifftsize, ifftsize/ioverlap, ifftsize, -iwin  
  ismoothing = 0.002
  fsmooth pvsmooth fsin, ismoothing, ismoothing
  
  iarrsize = ifftsize/2 + 1

  kAmps[] init iarrsize
  kFreqs[] init iarrsize
  kAmpsmooth[] init iarrsize
  kFreqsmooth[] init iarrsize
  kflag pvs2array kAmps, kFreqs, fsin
  kflag pvs2array kAmpsmooth, kFreqsmooth, fsmooth
  if changed(kflag) > 0 then
    kmaxAmp maxarray kAmps
    kFluxL2[] = limit(kAmps^2-kAmpsmooth^2, 0, 9999) ; L2 distance (limit, includes only positive changes)
    kfluxL2 = sumarray(kFluxL2) ; sum of all distances
  endif
  kfluxL2_norm divz kfluxL2, kmaxAmp^2, 0 ; normalized flux, independent of amplitude
  kfluxL2_norm *= 0.15
  aflux_env follow2 a(kfluxL2_norm), 0.01, 0.3
  aflux_env2 follow2 butterlp(limit(butterhp(a(kfluxL2_norm),2),0,1),25), 0.01, 0.3
    
  ktrans_in = (k(aflux_env2)^kshape)
  kamp_trans chnget "amp_trans"
  ktrans_in = ktrans_in*kamp_trans*k(aenv) + ktrans_in*(1-kamp_trans) ; mix in amp anvelope
  kttrans,ktdiff TransientDetect dbfsamp(ktrans_in), iresponse, ktthresh, klowThresh, kdecThresh, kdoubleLimit
  kttrans *= kgate
  
  chnset kttrans, "transient_trig"

endin

instr 99
  ; record segments
  a1 inch 1
  a2 inch 2
  a1 = a1+a2*0.5

  ; delay audio in to sync with the analysis envelopes
  kpre chnget "predelay" ; (5 ms) predelay for syncing audio with output trans envelopes
  adly vdelay a1, kpre, 50

  ksegment_num chnget "segment_rec"
  iwritepos chnget "writepos"
  kwritepos init iwritepos
  
  ktransient chnget "transient_trig" 

  kgate chnget "noisefloor_gate"
  
  kgate_off trigger kgate, 0.5, 1 ; trigger when signal drops below noisefloor
  
  krecording init 0
  cabbageSetValue "recording", krecording, changed(krecording)
  ; write markers, and send midi note out on recording
  if (kgate_off > 0) || ((krecording > 0) && (ktransient > 0)) then
    tablew kwritepos, ksegment_num, giEndMarkers
    event "i", -201, 0, .1
  endif
  if ktransient > 0 then
    ksegment_num += 1
    cabbageSetValue  "segment_rec",  ksegment_num
    tablew kwritepos, ksegment_num, giStartMarkers
    event "i", 201, 0, -1, 90, ksegment_num+48
  endif
  krecording = ktransient > 0 ? 1 : krecording
  krecording = kgate_off > 0 ? 0 : krecording
  if krecording > 0 then
    ; write audio to table
    andx line 0, 1, sr
    andx += iwritepos
    ixmode = 0
    ixoff = 0
    iwgmode = 0
    tablew adly, andx, giLiveRec, ixmode, ixoff, iwgmode
    kwritepos downsamp andx
    chnset kwritepos, "writepos"
  endif
endin

instr 100
; debug
  i1 = 1
  while i1 < 10 do
    istart = table(i1, giStartMarkers)/sr
    iend = table(i1, giEndMarkers)/sr
    print i1, istart, iend 
    i1 += 1
  od
endin

instr	201
  ; midi  output
  ivel = p4
  inote = p5
  ichan = 1
  idur = (p3 < 0.1 ? 0.1 : p3)	; avoid extremely short notes as they won't play
  idur = (p3 < 0 ? 999 : p3)	; use very long duration for realtime events, noteondur will create note off when instrument stops
  noteondur ichan, inote, ivel, idur
endin

</CsInstruments>  
<CsScore>
i1 0 86400
i3 1 1 ; reset counters
;i99 0 86400
</CsScore>
</CsoundSynthesizer>