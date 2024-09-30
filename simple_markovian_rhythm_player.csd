<Cabbage>
form size(400, 300), caption("Rhythm Player"), pluginId("rtp1"), guiMode("queue"), colour(30,40,40)

button bounds(5, 5, 70, 20), text("play"), channel("play"), colour:0("green"), colour:1("red")
nslider bounds(100, 5, 40, 25), text("tempo"), channel("tempo_bpm"), range(30, 300, 60), fontSize(14)
nslider bounds(150, 5, 40, 25), text("order"), channel("order"), range(0, 2, 2), fontSize(14)

label bounds(5, 70, 80, 20), text("Rhythm Ratios"), fontSize(12), align("left")
texteditor bounds(85, 70, 300, 20), channel("rhythm_ratios"), fontSize(15), colour("black"), fontColour("white"), caretColour("white")


csoundoutput bounds(5, 100, 390, 195)
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
;massign -1, 2
;pgmassign 0, -1 ; ignore program change

giRatios[] fillarray 1, 0.5, 0.25, 0.25, 1;, 0.33, 0.33, 0.33, 1
ginumitems = 2 ; initial assumption on how many unique ratios we will see, updated later
giUniqueRatiosItems[] init ginumitems

; The transition matrix holds transition probabilities from one ratio to all others,
; similar to an STM in a Markov model, but it is not normalized, we just add 1 to each observed transition.
; The indices into the STM are not the ratio items themselves, 
; but the index into giUniqueRatiosItems where the ratio (item) can be found.
; The STM has twice as many rows as the max number of items, as we also keep track of second order transitions.
; This is done in the loosest possible manner, where we think a tuplet of [second_last_item, unknown], 
; but we actually just store the second_last_item as the lookup key. 
; Combined with the probabilities of the usual case (last item, first order Markov transition), 
; it allows something similar to a second order Markov chain, but with some more flexibility.
; We may need this flexibility when we combine the Markov transitions with other preference rules,
; allowing output sequences not observed in the input (leading to possible dead ends in the STM).
giTransitionMatrix[][] init ginumitems*2, ginumitems

; GUI handling
instr 1
  kplay chnget "play"
  ktrig_play trigger kplay, 0.5, 0
  ktrig_stop trigger kplay, 0.5, 1
  if ktrig_play > 0 then
    event "i", 9, 0, -1
  endif
  if ktrig_stop > 0 then
    event "i", -9, 0, .1
  endif
  Sratios chnget "rhythm_ratios"
  if changed:k(Sratios) == 1 then
    Scoreline sprintfk {{i 2 0 1 "%s"}}, Sratios
    scoreline Scoreline, 1
  endif
endin

; set rhythm from gui
instr 2
  p3 = 1/kr
  Sratios strget p4
  puts Sratios, 1
  Sparts[] strsplit Sratios, ","
  giRatios[] init lenarray(Sparts)
  index = 0
  while index < lenarray(Sparts) do
    Sratio sprintf "return %s", Sparts[index]
    iratio evalstr Sratio
    giRatios[index] = iratio
    index += 1
  od
  printarray giRatios
  event_i "i", 4, 0, 1
endin

; analyze rhythm series: collect unique ratios, record the indices where each ratio occurs
instr 4
  puts "All ratios in order of appearance:", 1
  printarray giRatios
  ; first find how many unique ratios and index them in order of appearance
  giUniqueRatiosItems init lenarray(giRatios) ; generous assumption of size
  index = 0
  iunique_index = 0
  while index < lenarray(giRatios) do
    iratio = giRatios[index]
    iunique_id findarray giUniqueRatiosItems, iratio, 0.01
    if iunique_id == -1 then
      giUniqueRatiosItems[iunique_index] = iratio
      iunique_index += 1
    endif
    index += 1
  od
  ginumitems = iunique_index
  giUniqueRatiosItems slicearray giUniqueRatiosItems, 0, ginumitems-1

  ; now we know how large the STM needs to be, and can proceed filling it
  giTransitionMatrix[][] init ginumitems*2, ginumitems
  index = 0
  iprev_ratio = -1
  i2prev_ratio = -1
  iprev_unique_id = -1
  i2prev_unique_id = -1
  while index < lenarray(giRatios) do
    iratio = giRatios[index]
    iunique_id findarray giUniqueRatiosItems, iratio, 0.01
    ; increment in STM for each observation
    ;print index, iratio, iprev_ratio, i2prev_ratio
    ;print iunique_id, iprev_unique_id, i2prev_unique_id
    if iprev_ratio > -1 then
      giTransitionMatrix[iprev_unique_id][iunique_id] = giTransitionMatrix[iprev_unique_id][iunique_id]+1
      if i2prev_ratio > -1 then
        giTransitionMatrix[i2prev_unique_id+ginumitems][iunique_id] = giTransitionMatrix[i2prev_unique_id+ginumitems][iunique_id]+1
      endif
    endif
    ; bookeeping
    i2prev_ratio = iprev_ratio
    i2prev_unique_id = iprev_unique_id
    iprev_ratio = iratio
    iprev_unique_id = iunique_id
    index += 1
  od
  puts "Unique ratios in order of appearance:", 1
  printarray(giUniqueRatiosItems)
  puts "STM:", 1
  printarray(giTransitionMatrix)
  ktrig init 1
  chnset ktrig, "reinit_rhythm"
  ktrig = 0
endin


instr 9
  ktempo_bpm chnget "tempo_bpm"
  ktempo = ktempo_bpm/60
  korder chnget "order" ; Markov-ish order, may be fractional, up to 2nd order
  iorder chnget "order"
  korder init iorder
  iord1tab ftgen 0, 0, 4, 2, 0, 1, 1, 1; first order weight lookup
  iord2tab ftgen 0, 0, 4, 2, 0, 0, 1, 1; second order weight lookup
  iratio = giUniqueRatiosItems[0] ; gotta start somewhere, to be updated
  ;iprev_ratio = -1 ; not known at start
  iprev_unique_ratio = -1 ; not known at start

  ; play it
  kmetrotempo init 1
  ktrig metro kmetrotempo
  if ktrig > 0 then
    event "i", 20, 0, 0.1
    reinit thething
  endif

  thething:    
  iord1 tablei i(korder), iord1tab
  iord2 tablei i(korder), iord2tab

  iunique_ratio findarray giUniqueRatiosItems, iratio, 0.01
  print iunique_ratio, iprev_unique_ratio

  ; get probabilities from STM
  giProb_prev[] getrow giTransitionMatrix, iunique_ratio ; 1st order Markov (according to previous item)
  if iprev_unique_ratio < 0 then; attempt to get around init of both, but fails
    iprev_lookup = iunique_ratio
  else
    iprev_lookup = iprev_unique_ratio+ginumitems 
  endif
  print iprev_lookup
  giProb_2prev[] getrow giTransitionMatrix, iprev_lookup ; probability according to 2nd previous item (independent of previous item)
  printarray giProb_2prev
  ; normalize
  imax_prob_prev maxarray giProb_prev
  inorm_prev divz 1, imax_prob_prev, 1
  giProb_prev = giProb_prev*inorm_prev
  imax_prob_2prev maxarray giProb_2prev
  inorm_2prev divz 1, imax_prob_2prev, 1
  giProb_2prev = giProb_2prev*inorm_2prev

  print iord1, iord2
  
  giProb_prev = giProb_prev*iord1+(1-iord1); first order, also covers zeroeth order when iord1=0
  giProb_2prev = giProb_2prev*iord2+(1-iord2) ; second order
  giProb[] = giProb_prev*giProb_2prev
  
  ; normalize and safeguard against dead ends
  imax_prob maxarray giProb
  if imax_prob == 0 then ; if we have no combined probabilities
    giProb = giProb_prev+giProb_2prev ; use OR probability instead of AND probability, so we don't get stuck
    puts "Fall back to OR probability for one event", 1
    imax_prob maxarray giProb 
    if imax_prob == 0 then ; in the unlikely case there are still no options
      giProb = giProb+1 ; set all equal
      puts "Fall back to random selection for one event", 1
    endif
  endif
  inorm divz 1, imax_prob, 1
  giProb = giProb*inorm

  ; select: fill an array with random variables, multiply with probabilities, select max
  giSelect[] init ginumitems
  index = 0
  while index < lenarray(giSelect) do
    giSelect[index] = random(0, 1)
    index += 1
  od
  printarray giProb_prev
  printarray giProb_2prev
  printarray giProb
  giSelect1[] = giSelect*giProb
  i_, iselect maxarray giSelect1
  ; iselect is now an index into the unique ratios 
  iratio = giUniqueRatiosItems[iselect]
  iprev_unique_ratio = iunique_ratio

  print iratio
  puts "\n", 1
  rireturn
  kmetrotempo = ktempo/iratio

endin

; rhythm trig player
instr 20
  aenv expon 1, p3, 0.0001
  anoise rnd31 1, 1
  anoise *= aenv
  outs anoise, anoise
endin

</CsInstruments>
<CsScore>
i1 0 86400 ; Gui handling
i4 0 1
</CsScore>
</CsoundSynthesizer>
