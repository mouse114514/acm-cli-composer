# gen_awalker.py — Alan Walker style composition
# Key characteristics from analysis:
#   - 75-80% stepwise motion
#   - 1.3-1.4 notes/sec (sparse, lots of space)
#   - 0.23-0.25 contour changes/note (smooth lines)
#   - Pentatonic-leaning pitch content
#   - Call-and-response 4-bar phrases
#   - i-VI-III-VII chord pattern (Faded/Alone formula)
#
# Key: Cm (ACML-safe: no sharp note names)
# Chords: Cm - Ab - Eb - Bb (i - VI - III - VII)
# BPM: 95

bars = 16
bpm = 95

# Chord progression (4 phases of 4 bars)
chords_16 = [
    'Cm','Cm','Cm','Cm',      # Phase 0: intro
    'Ab','Ab','Eb','Eb',      # Phase 1: build
    'Bb','Bb','Cm','Cm',      # Phase 2: tension
    'Ab','Ab','Bb','Bb',      # Phase 3: climax + resolution
]

ROOT = {'Cm':'C1','Ab':'Ab1','Eb':'Eb1','Bb':'Bb1'}
ROOT3 = {'Cm':'C2','Ab':'Ab2','Eb':'Eb2','Bb':'Bb2'}
NOTES = {
    'Cm': ('C2','Eb2','G2','C3','Eb3','G3','C4','Eb4','G4','C5'),
    'Ab': ('Ab1','C2','Eb2','Ab2','C3','Eb3','Ab3','C4','Eb4','Ab4'),
    'Eb': ('Eb1','G1','Bb1','Eb2','G2','Bb2','Eb3','G3','Bb3','Eb4'),
    'Bb': ('Bb1','D2','F2','Bb2','D3','F3','Bb3','D4','F4','Bb4'),
}

def ph(b):
    return b // 4

lines = [f'# gen_awalker — Alan Walker style (sparse, pentatonic, stepwise)',
         f'name = "awalker"', f'bpm = {bpm}', '']

# ═══ DRUMS — minimal, Faded-style ═══
kick = []
snare = []
hihat = []
for b in range(bars):
    p = ph(b)
    if p == 0:
        kick.extend(['K:q:pp','R:q','R:q','R:q'])
        snare.extend(['R:q']*4)
        hihat.extend(['R:e']*8)
    elif p == 1:
        kick.extend(['K:q:mp','R:q','R:q','R:q'])
        snare.extend(['R:q','S:q:pp','R:q','R:q'])
        hihat.extend(['R:e']*8)
    elif p == 2:
        kick.extend(['K:q:mf','R:q','R:q','R:q'])
        snare.extend(['R:q','S:q:mp','R:q','R:q'])
        hihat.extend(['H:e:pp']*8)
    else:
        kick.extend(['K:q','R:q','K:q','R:q'])
        snare.extend(['R:q','S:q:mf','R:q','S:q:mf'])
        hihat.extend(['H:e:mp']*16)

lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.70')
lines.append(f'notes = {",".join(kick)}\n')
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.55')
lines.append(f'notes = {",".join(snare)}\n')
lines.append('[track hihat]\ninstrument = drums\nmode = parallel\nvolume = 0.25')
lines.append(f'notes = {",".join(hihat)}\n')

# ═══ BASS — simple root notes, whole notes → quarter notes ═══
bass = []
for b in range(bars):
    p = ph(b)
    r = ROOT[chords_16[b]]
    if p == 0:
        bass.append(f'{r}:w:pp')
    elif p == 1:
        bass.append(f'{r}:h:pp,{r}:h:pp')
    elif p == 2:
        bass.append(f'{r}:h:mp,{r}:h:mp')
    else:
        bass.append(f'{r}:q:mf,{r}:q:mf,{r}:q:mf,{r}:q:mf')
bass_flat = [x for g in bass for x in g.split(',')]
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.60')
lines.append(f'notes = {",".join(bass_flat)}\n')

# ═══ PAD — sustained strings ═══
pad = []
for b in range(bars):
    p = ph(b)
    r3 = ROOT3[chords_16[b]]
    vol = ['pp','pp','mp','mf'][p]
    pad.append(f'{r3}:w:{vol}')
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.30')
lines.append(f'notes = {",".join(pad)}\n')

# ═══ PIANO — chord stabs (Alan Walker style supersaw stabs) ═══
piano = []
for b in range(bars):
    p = ph(b)
    ch = chords_16[b]
    # Chord voicing: root + 3rd + 5th in middle register
    r3 = {'Cm':'C2','Ab':'Ab2','Eb':'Eb2','Bb':'Bb2'}[ch]
    t3 = {'Cm':'Eb2','Ab':'C3','Eb':'G2','Bb':'D3'}[ch]
    f3 = {'Cm':'G2','Ab':'Eb3','Eb':'Bb2','Bb':'F3'}[ch]
    if p < 2:
        piano.append(f'{r3}:h:pp,{t3}:h:pp')
        piano.append(f'{r3}:h:pp,{t3}:h:pp')
    else:
        piano.append(f'{r3}:q:mp,{t3}:q:mp,{f3}:q:mp,R:q')
piano_flat = [x for g in piano for x in g.split(',')]
lines.append('[track piano]\ninstrument = piano\nmode = parallel\nvolume = 0.40')
lines.append(f'notes = {",".join(piano_flat)}\n')

# ═══ LEAD MELODY — Alan Walker style ═══
# Sparse (1.3 notes/sec), stepwise (75-80%), pentatonic, lots of space
# Cm pentatonic core: C, Eb, F, G, Bb
# Non-chord tones added for flavor (target 20-30%)

lead = []
for b in range(bars):
    p = ph(b)
    ch = chords_16[b]

    if p == 0:
        # Phase 0: Cm — sparse intro, pentatonic descent
        # Bars: notes every 1-2 beats, mostly half and quarter notes
        if b == 0:
            lead.append('G4:h:pp,Bb4:q:pp')  # G4(2beats) Bb4(1beat) then rest
        elif b == 1:
            lead.append('G4:q:pp,F4:q:pp,Eb4:h:pp')  # G4 F4 Eb4
        elif b == 2:
            lead.append('F4:h:pp,G4:q:pp')  # F4 G4
        else:
            lead.append('Eb4:w:pp')  # held Eb4

    elif p == 1:
        # Phase 1: Ab x2, Eb x2 — build, slightly more active
        if b == 4:  # Ab
            lead.append('Eb4:h:pp,G4:q:pp,Ab4:q:pp')  # Eb4 G4 Ab4 (Ab4=non-chord over Ab? No, it's the root)
        elif b == 5:  # Ab
            lead.append('G4:q:pp,F4:q:pp,Eb4:h:pp')  # G4 F4 Eb4
        elif b == 6:  # Eb
            lead.append('Bb4:h:pp,G4:q:pp,F4:q:pp')  # Bb4 G4 F4
        else:  # b == 7, Eb
            lead.append('Eb4:q:pp,F4:q:pp,G4:h:pp')  # Eb4 F4 G4

    elif p == 2:
        # Phase 2: Bb x2, Cm x2 — higher register, tension
        if b == 8:  # Bb (Bb-D-F)
            lead.append('D5:q:mp,F5:q:mp,Eb5:q:mp,D5:q:mp')  # D5 F5 Eb5 D5 (Eb5=non-chord!)
        elif b == 9:  # Bb
            lead.append('C5:h:mp,Bb4:q:mp,G4:q:mp')  # C5 Bb4 G4
        elif b == 10:  # Cm
            lead.append('Ab4:q:mp,G4:h:mp,F4:q:mp')  # Ab4 G4 F4 (Ab=non-chord over Cm!)
        else:  # b == 11, Cm
            lead.append('G4:q:mp,Eb4:q:mp,F4:q:mp,G4:q:mp')  # G4 Eb4 F4 G4

    else:
        # Phase 3: Ab x2, Bb x2 — climax
        if b == 12:  # Ab
            lead.append('C5:q:mf,D5:q:mf,Eb5:q:mf,C5:q:mf')  # C5 D5 Eb5 C5
        elif b == 13:  # Ab — octave jump (Alan Walker signature)
            lead.append('C5:q:mf,Eb5:q:mf,Ab5:q:mf,G5:q:mf')  # C5 Eb5 Ab5 G5
        elif b == 14:  # Bb — high point
            lead.append('G5:q:mf,F5:q:mf,Eb5:h:mf')  # G5 F5 Eb5
        else:  # b == 15, Bb — resolve down to Cm
            lead.append('D5:q:mf,C5:q:mf,Bb4:h:mf')  # D5 C5 Bb4

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = sawtooth\nmode = parallel\nvolume = 0.55')
lines.append(f'notes = {",".join(lead_flat)}\n')

# ═══ ARP — gentle arpeggio pad (Alan Walker style) ═══
arp = []
for b in range(bars):
    p = ph(b)
    ch = chords_16[b]
    notes = NOTES[ch]
    if p < 2:
        arp.append(f'{notes[2]}:q:pp,{notes[4]}:q:pp,{notes[6]}:q:pp,{notes[4]}:q:pp')
    else:
        arp.append(f'{notes[2]}:q:mp,{notes[4]}:q:mp,{notes[6]}:q:mp,{notes[4]}:q:mp')
arp_flat = [x for g in arp for x in g.split(',')]
lines.append('[track arp]\ninstrument = string\nmode = parallel\nvolume = 0.20\npan = -0.3')
lines.append(f'notes = {",".join(arp_flat)}\n')

with open(r'D:\PYTHON\ACM\cli_composer\samples\awalker.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/awalker.acml ({bars} bars, {bpm} BPM, {bars*4*60/bpm:.1f}s)')

# Non-chord analysis
print('\n=== Non-chord Tone Check ===')
chord_sets = {'Cm': {0,3,7}, 'Ab': {8,0,3}, 'Eb': {3,7,10}, 'Bb': {10,2,5}}
note_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
total = 0
non_ct = 0
for b in range(bars):
    ch = chords_16[b]
    ct_set = chord_sets[ch]
    bar_notes = lead[b]
    for note_str in bar_notes.split(','):
        note_str = note_str.strip()
        if not note_str or note_str == 'R' or note_str.startswith('R:'):
            continue
        # Parse note name like "G4", "Eb4", "F#4"
        name = note_str.split(':')[0]
        if name == 'R':
            continue
        # Extract pitch class
        if len(name) == 2:
            pc = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}.get(name[0], -1)
        else:
            pc = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}.get(name[0], -1)
            if name[1] == 'b':
                pc -= 1
            elif name[1] == '#':
                pc += 1
        pc %= 12
        is_ct = pc in ct_set
        total += 1
        if not is_ct:
            non_ct += 1
            if b < 4:
                note_full = note_str.split(':')[0]
                expected = [note_names[p] for p in sorted(ct_set)]
                print(f'  Bar {b} ({ch}): {note_full} (pc={pc}={note_names[pc]}) non-chord! chord={expected}')

print(f'\nTotal: {non_ct}/{total} = {100*non_ct/total:.0f}% non-chord tones')
