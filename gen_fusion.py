# "Fusion" — Alan Walker × Tobu × Marshmello 三合一
# AW: 忧郁段4层厚度 + i-VI-III-VII | Tobu: 明亮vi-IV-I-V + 高跳进旋律
# Marshmello: 7和弦 + halftime律动 + chord stab + Chord-Bass平滑
# Key: Cm → C → Cm | BPM 128 | 40 bars | 无#号

bars = 40
bpm = 128

# 和弦定义: (label, root, third, fifth, seventh)
chords = [
    # Bars 0-3: Intro — AW melancholy (Cm7-Abmaj7-Ebmaj7-Bb7)
    ('Cm7','C3','Eb3','G3','Bb3'), ('Abmaj7','Ab2','C3','Eb3','G3'),
    ('Ebmaj7','Eb2','G2','Bb2','D3'), ('Bb7','Bb2','D3','F3','Ab3'),
    # Bars 4-7: Verse — AW+Marshmello (重复加7和弦)
    ('Cm7','C3','Eb3','G3','Bb3'), ('Abmaj7','Ab2','C3','Eb3','G3'),
    ('Ebmaj7','Eb2','G2','Bb2','D3'), ('Bb7','Bb2','D3','F3','Ab3'),
    # Bars 8-9: Build
    ('Cm7','C3','Eb3','G3','Bb3'), ('G7','G2','B2','D3','F3'),
    # Bars 10-17: Drop — C大调, Tobu+halftime (vi-IV-I-V)
    ('Am7','A2','C3','E3','G3'), ('Fmaj7','F2','A2','C3','E3'),
    ('Cmaj7','C3','E3','G3','B3'), ('G','G2','B2','D3','G3'),
    ('Am7','A2','C3','E3','G3'), ('Fmaj7','F2','A2','C3','E3'),
    ('Cmaj7','C3','E3','G3','B3'), ('G','G2','B2','D3','G3'),
    # Bars 18-19: Bridge — Marshmello复杂转调
    ('G7sus4','G2','C3','D3','F3'), ('G7','G2','B2','D3','F3'),
    # Bars 20-23: Verse' — Cm回归
    ('Cm7','C3','Eb3','G3','Bb3'), ('Abmaj7','Ab2','C3','Eb3','G3'),
    ('Ebmaj7','Eb2','G2','Bb2','D3'), ('Bb7','Bb2','D3','F3','Ab3'),
    # Bars 24-25: Build 2
    ('Cm7','C3','Eb3','G3','Bb3'), ('G7','G2','B2','D3','F3'),
    # Bars 26-33: Drop 2 — 全融合
    ('Am7','A2','C3','E3','G3'), ('Fmaj7','F2','A2','C3','E3'),
    ('Cmaj7','C3','E3','G3','B3'), ('G','G2','B2','D3','G3'),
    ('Am7','A2','C3','E3','G3'), ('Fmaj7','F2','A2','C3','E3'),
    ('Cmaj7','C3','E3','G3','B3'), ('G','G2','B2','D3','G3'),
    # Bars 34-37: Outro — fading Cm
    ('Cm7','C3','Eb3','G3','Bb3'), ('Abmaj7','Ab2','C3','Eb3','G3'),
    ('Ebmaj7','Eb2','G2','Bb2','D3'), ('R','R','R','R','R'),
    # Bars 38-39: Silence
    ('R','R','R','R','R'), ('R','R','R','R','R'),
]

def s(b):  # section helper
    if b < 4: return 'intro'
    if b < 8: return 'verse'
    if b < 10: return 'build'
    if b < 18: return 'drop'
    if b < 20: return 'bridge'
    if b < 24: return 'verse_return'
    if b < 26: return 'build2'
    if b < 34: return 'drop2'
    if b < 38: return 'outro'
    return 'silence'

lines = []
lines.append('# Fusion — Alan Walker × Tobu × Marshmello')
lines.append('# Key: Cm(maj7) → C(maj7) → Cm(maj7) | BPM 128 | 40 bars')
lines.append(f'name = "fusion"')
lines.append(f'bpm = {bpm}')
lines.append('')

# ── 1. KICK ──
kick = []
for b in range(bars):
    sec = s(b)
    if sec == 'silence':
        kick.extend(['R:q']*4)
    elif sec in ('drop','drop2'):  # Marshmello halftime: kick on 1
        kick.extend(['K:q:ff','R:q','R:q','R:q'])
    elif sec in ('build','build2'):
        if b in (8,24):
            kick.extend(['K:e:mf']*8)      # eighth build
        else:
            kick.extend(['K:s:mf']*16)     # sixteenth roll
    else:  # AW 4-on-the-floor
        kick.extend(['K:q:mp','R:q','K:q:mp','R:q'])

lines.append('[track kick]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.75')
lines.append(f'notes = {",".join(kick)}')
lines.append('')

# ── 2. SNARE ──
snare = []
for b in range(bars):
    sec = s(b)
    if sec == 'silence':
        snare.extend(['R:q']*4)
    elif sec in ('drop','drop2'):  # Marshmello halftime: snare on 3
        snare.extend(['R:q','R:q','S:q:ff','R:q'])
    elif sec in ('build','build2'):
        if b in (8,24):
            snare.extend(['S:e:mf']*8)
        else:
            snare.extend(['S:s:mf']*16)
    elif sec in ('intro','outro'):
        snare.extend(['R:q']*4)              # no snare
    else:
        snare.extend(['R:q','S:q:mp','R:q','S:q:mp'])

lines.append('[track snare]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.60')
lines.append(f'notes = {",".join(snare)}')
lines.append('')

# ── 3. HIHAT ──
hihat = []
for b in range(bars):
    sec = s(b)
    if sec == 'silence':
        hihat.extend(['R:e']*8)
    elif sec in ('drop','drop2'):  # halftime: eighth notes
        hihat.extend(['H:e:mf']*8)
    elif sec in ('build','build2'):
        hihat.extend(['H:s:mf']*16)
    else:
        hihat.extend(['H:e:pp']*8)

lines.append('[track hihat]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.30')
lines.append(f'notes = {",".join(hihat)}')
lines.append('')

# ── 4. BASS (always present — AW层数法则) ──
bass = []
for b in range(bars):
    c = chords[b]
    sec = s(b)
    root = c[1]
    if sec == 'silence':
        bass.extend(['R:q']*4)
    elif sec in ('drop','drop2'):  # Marshmello smooth bass (root-fifth walking)
        fifth = {'A2':'E2','F2':'C3','C3':'G2','G2':'D2','R':'R'}.get(root,root)
        if c[0] == 'G':
            bass.extend([f'{root}:q:mf',f'{root}:q:mf',f'{root}:q:mf',f'{root}:q:mf'])
        else:
            bass.extend([f'{root}:q:mf',f'{fifth}:q:mf',f'{root}:q:mf',f'{fifth}:q:mf'])
    else:  # AW style: root quarter notes always
        bass.extend([f'{root}:q:mp']*4)

lines.append('[track bass]')
lines.append('instrument = bass')
lines.append('mode = parallel')
lines.append('volume = 0.70')
lines.append('pan = -0.2')
lines.append(f'notes = {",".join(bass)}')
lines.append('')

# ── 5. PIANO (arpeggio anchor — AW signature, never stops) ──
# Build arpeggio patterns for each chord type
# 8 eighth notes per bar = root, third, fifth, seventh, root, third, fifth, seventh
piano_pat = {
    'Cm7':     ['C3:e','Eb3:e','G3:e','Bb3:e','C4:e','Eb4:e','G4:e','Bb4:e'],
    'Abmaj7':  ['Ab2:e','C3:e','Eb3:e','G3:e','Ab3:e','C4:e','Eb4:e','G4:e'],
    'Ebmaj7':  ['Eb2:e','G2:e','Bb2:e','D3:e','Eb3:e','G3:e','Bb3:e','D4:e'],
    'Bb7':     ['Bb2:e','D3:e','F3:e','Ab3:e','Bb3:e','D4:e','F4:e','Ab4:e'],
    'G7':      ['G2:e','B2:e','D3:e','F3:e','G3:e','B3:e','D4:e','F4:e'],
    'Am7':     ['A2:e','C3:e','E3:e','G3:e','A3:e','C4:e','E4:e','G4:e'],
    'Fmaj7':   ['F2:e','A2:e','C3:e','E3:e','F3:e','A3:e','C4:e','E4:e'],
    'Cmaj7':   ['C3:e','E3:e','G3:e','B3:e','C4:e','E4:e','G4:e','B4:e'],
    'G':       ['G2:e','B2:e','D3:e','G3:e','G2:e','B2:e','D3:e','G3:e'],
    'G7sus4':  ['G2:e','C3:e','D3:e','F3:e','G2:e','C3:e','D3:e','F3:e'],
    'R':       ['R:e']*8,
}

piano = []
for b in range(bars):
    label = chords[b][0]
    sec = s(b)
    pat = piano_pat.get(label, ['R:e']*8)
    if sec == 'silence':
        piano.extend(['R:e']*8)
    elif sec in ('build','build2'):
        if b in (8,24):
            piano.extend([f'{chords[b][1]}:s:pp']*8 + [f'{chords[b][3]}:s:pp']*8)
        else:
            piano.extend([f'{chords[b][1]}:s:mp']*16)
    elif sec in ('drop','drop2'):
        piano.extend([f'{n}:mf' for n in pat])
    else:
        piano.extend([f'{n}:pp' for n in pat])

piano_flat = []
for item in piano:
    piano_flat.extend(item.split(','))
lines.append('[track piano]')
lines.append('instrument = piano')
lines.append('mode = parallel')
lines.append('volume = 0.60')
lines.append('pan = -0.3')
lines.append(f'notes = {",".join(piano_flat)}')
lines.append('')

# ── 6. PAD (sustained chords — always on) ──
pad = []
for b in range(bars):
    c = chords[b]
    sec = s(b)
    root = c[1]
    third = c[2]
    seventh = c[4]
    if sec == 'silence':
        pad.append('R:w')
    elif sec in ('drop','drop2'):
        pad.append(f'{root}:h:mp,{seventh}:h:mp')
    else:
        pad.append(f'{root}:w:pp')

lines.append('[track pad]')
lines.append('instrument = pad')
lines.append('mode = parallel')
lines.append('volume = 0.30')
lines.append('pan = 0.3')
lines.append(f'notes = {",".join(pad)}')
lines.append('')

# ── 7. STRING DRONE (warmth layer — AW厚度关键) ──
drone = []
for b in range(bars):
    c = chords[b]
    sec = s(b)
    root = c[1]
    if sec == 'silence':
        drone.append('R:w')
    else:
        drone.append(f'{root}:w:pp')

lines.append('[track drone]')
lines.append('instrument = string')
lines.append('mode = parallel')
lines.append('volume = 0.20')
lines.append('pan = 0.2')
lines.append(f'notes = {",".join(drone)}')
lines.append('')

# ── 8. LEAD (Tobu style — bright, jumpy, high register) ──
lead_pat = {
    'Cm7': ['Eb5:e:mp','G5:e:mp','Bb5:e:mp','C6:e:mp','G5:e:mp','Eb5:e:mp','C5:e:mp','Bb4:e:mp'],
    'Abmaj7': ['C5:e:mp','Eb5:e:mp','G5:e:mp','Ab5:e:mp','G5:e:mp','Eb5:e:mp','C5:e:mp','Ab4:e:mp'],
    'Ebmaj7': ['Eb5:e:mp','G5:e:mp','Bb5:e:mp','Eb6:e:mp','Bb5:e:mp','G5:e:mp','Eb5:e:mp','G5:e:mp'],
    'Bb7': ['D5:e:mp','F5:e:mp','Ab5:e:mp','Bb5:e:mp','Ab5:e:mp','F5:e:mp','D5:e:mp','Bb4:e:mp'],
    'G7': ['B4:e:mp','D5:e:mp','F5:e:mp','G5:e:mp','F5:e:mp','D5:e:mp','B4:e:mp','G4:e:mp'],
    'Am7': ['E5:e:mf','G5:e:mf','C6:e:mf','E6:e:mf','C6:e:mf','G5:e:mf','E5:e:mf','C5:e:mf'],
    'Fmaj7': ['C5:e:mf','F5:e:mf','A5:e:mf','C6:e:mf','A5:e:mf','F5:e:mf','C5:e:mf','A4:e:mf'],
    'Cmaj7': ['E5:e:mf','G5:e:mf','C6:e:mf','E6:e:mf','C6:e:mf','G5:e:mf','E5:e:mf','C5:e:mf'],
    'G': ['D5:e:mf','G5:e:mf','B5:e:mf','D6:e:mf','B5:e:mf','G5:e:mf','D5:e:mf','G4:e:mf'],
    'G7sus4': ['C5:e:mf','D5:e:mf','F5:e:mf','G5:e:mf','F5:e:mf','D5:e:mf','C5:e:mf','G4:e:mf'],
    'R': ['R:e']*8,
}

lead = []
for b in range(bars):
    label = chords[b][0]
    sec = s(b)
    if sec == 'silence':
        lead.append(','.join(['R:e']*8))
    elif sec in ('drop','drop2'):
        pat = lead_pat.get(label, ['R:e']*8)
        lead.append(','.join(pat))
    elif sec == 'bridge':
        pat = lead_pat.get(label, ['R:e']*8)
        lead.append(','.join([f'{n}' for n in pat]))
    else:
        lead.append(','.join(['R:e']*8))

lead_flat = []
for item in lead:
    lead_flat.extend(item.split(','))
lines.append('[track lead]')
lines.append('instrument = sawtooth')
lines.append('mode = parallel')
lines.append('volume = 0.45')
lines.append('pan = -0.1')
lines.append(f'notes = {",".join(lead_flat)}')
lines.append('')

# ── 9. ARP (sixteenth-note, in drops + builds) ──
arp_pat = {
    'Am7': ['E4:s','A4:s','C5:s','E5:s'],
    'Fmaj7': ['C4:s','F4:s','A4:s','C5:s'],
    'Cmaj7': ['E4:s','G4:s','C5:s','E5:s'],
    'G': ['D4:s','G4:s','B4:s','D5:s'],
}
arp = []
for b in range(bars):
    label = chords[b][0]
    sec = s(b)
    if sec in ('drop','drop2'):
        pat = arp_pat.get(label, ['R:s']*4)
        arp.extend([','.join(pat)] * 4)
    elif sec in ('build','build2'):
        arp.extend(['R:s,R:s,R:s,R:s']*4)
    else:
        arp.extend(['R:s,R:s,R:s,R:s']*4)
arp_flat = []
for item in arp:
    arp_flat.extend(item.split(','))
lines.append('[track arp]')
lines.append('instrument = wavetable')
lines.append('wavetable = square')
lines.append('mode = parallel')
lines.append('volume = 0.25')
lines.append('pan = 0.5')
lines.append(f'notes = {",".join(arp_flat)}')
lines.append('')

# ── 10. CHORD STAB (Marshmello style — quarter note stabs in drop) ──
stab = []
for b in range(bars):
    c = chords[b]
    sec = s(b)
    root = c[1]
    third = c[2]
    fifth = c[3]
    if sec in ('drop','drop2'):
        # 3快速十六分 = chord stab效果, 然后休息填满4拍
        stab.extend([f'{root}:s:mf,{third}:s:mf,{fifth}:s:mf,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s'])
    else:
        stab.extend(['R:q']*4)
stab_flat = []
for item in stab:
    stab_flat.extend(item.split(','))
lines.append('[track stab]')
lines.append('instrument = wavetable')
lines.append('wavetable = sawtooth')
lines.append('mode = parallel')
lines.append('volume = 0.35')
lines.append('pan = 0.0')
lines.append(f'notes = {",".join(stab_flat)}')
lines.append('')

# ── 11. BELL (playful accents) ──
bell = []
for b in range(bars):
    sec = s(b)
    if sec in ('drop','drop2'):
        bell.append('G5:s:mf,G6:s:mf,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
    else:
        bell.append('R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
bell_flat = []
for item in bell:
    bell_flat.extend(item.split(','))
lines.append('[track bell]')
lines.append('instrument = bell')
lines.append('mode = parallel')
lines.append('volume = 0.45')
lines.append('pan = 0.4')
lines.append(f'notes = {",".join(bell_flat)}')

with open('samples/fusion.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/fusion.acml ({bars} bars, {bpm} BPM)')
