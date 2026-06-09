# "hihi" — Emotional arc: melancholy → joyful → melancholy
# Key: Cm → C → Cm | BPM 120 | 32 bars × 4 beats = 128 beats ≈ 64s
# No sharp notes used (all naturals/flats in Cm/C major)

bars = 32
bpm = 120

# Chord per bar: (label, root, third, fifth, seventh/octave)
# Using only natural/flat notes (no #) for ACML compatibility
C = lambda: None  # silence sentinel

chords = [
    # Bars 0-3: Intro — melancholy (Cm: i-VI-III-VII)
    ('Cm','C3','Eb3','G3','C4'), ('Ab','Ab2','C3','Eb3','Ab3'),
    ('Eb','Eb2','G2','Bb2','Eb3'), ('Bb','Bb2','D3','F3','Bb3'),
    # Bars 4-7: Verse — melancholy
    ('Cm','C3','Eb3','G3','C4'), ('Ab','Ab2','C3','Eb3','Ab3'),
    ('Eb','Eb2','G2','Bb2','Eb3'), ('Bb','Bb2','D3','F3','Bb3'),
    # Bars 8-9: Build — rising tension
    ('Cm','C3','Eb3','G3','C4'), ('G','G2','B2','D3','G3'),
    # Bars 10-13: Chorus — joyful (C: I-IV-V-vi)
    ('C','C3','E3','G3','C4'), ('F','F2','A2','C3','F3'),
    ('G','G2','B2','D3','G3'), ('Am','A2','C3','E3','A3'),
    # Bars 14-17: Chorus' — playful
    ('F','F2','A2','C3','F3'), ('G','G2','B2','D3','G3'),
    ('C','C3','E3','G3','C4'), ('Am','A2','C3','E3','A3'),
    # Bars 18-19: Break — falling back
    ('G','G2','B2','D3','G3'), ('G7','G2','B2','D3','F3'),
    # Bars 20-21: Verse return — melancholy
    ('Cm','C3','Eb3','G3','C4'), ('Ab','Ab2','C3','Eb3','Ab3'),
    # Bars 22-23: Sinking
    ('Eb','Eb2','G2','Bb2','Eb3'), ('Bb','Bb2','D3','F3','Bb3'),
    # Bars 24-27: Outro — fading
    ('Cm','C3','Eb3','G3','C4'), ('Ab','Ab2','C3','Eb3','Ab3'),
    ('Eb','Eb2','G2','Bb2','Eb3'), ('Bb','Bb2','D3','F3','Bb3'),
    # Bars 28-29: Coda — final
    ('Cm','C3','Eb3','G3','C4'), ('Cm','C3','Eb3','G3','C4'),
    # Bars 30-31: Silence
    (None,)*5, (None,)*5,
]

# Helper to check bar index ranges
def in_range(b, lo, hi): return lo <= b < hi
def section(b):
    if b < 4: return 'intro'
    if b < 8: return 'verse'
    if b < 10: return 'build'
    if b < 18: return 'chorus'
    if b < 20: return 'break'
    if b < 24: return 'verse_return'
    if b < 28: return 'outro'
    if b < 30: return 'coda'
    return 'silence'

lines = []
lines.append('# hihi — Emotional arc: melancholy → joyful → melancholy')
lines.append('# Key: Cm → C → Cm | BPM 120 | 32 bars')
lines.append(f'name = "hihi"')
lines.append(f'bpm = {bpm}')
lines.append('')

# Internal note: build a note string with optional velocity
def nv(note, vel='mf'):
    return f'{note}:e:{vel}'

# ── KICK ──
kick_notes = []
for b in range(bars):
    s = section(b)
    if s == 'silence':
        kick_notes.extend(['R:q']*4)
    elif s in ('intro', 'verse'):
        kick_notes.extend(['K:q:mp','R:q','K:q:mp','R:q'])
    elif s == 'build':
        if b == 8:
            kick_notes.extend(['K:e:mf']*8)       # eighth note build
        else:
            kick_notes.extend(['K:s:mf']*16)       # sixteenth note roll
    elif s == 'chorus':
        kick_notes.extend(['K:q:ff','R:q','K:q:ff','R:q'])
    elif s == 'break':
        kick_notes.extend(['K:q:mf','R:q','K:q:mf','R:q'])
    elif s in ('verse_return', 'outro', 'coda'):
        kick_notes.extend(['K:q:mp','R:q','K:q:mp','R:q'])

lines.append('[track kick]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.75')
lines.append(f'notes = {",".join(kick_notes)}')
lines.append('')

# ── SNARE ──
snare_notes = []
for b in range(bars):
    s = section(b)
    if s == 'silence':
        snare_notes.extend(['R:q']*4)
    elif s in ('intro', 'coda'):
        snare_notes.extend(['R:q']*4)              # no snare in intro/coda
    elif s == 'verse':
        snare_notes.extend(['R:q','S:q:mp','R:q','S:q:mp'])  # soft on 2&4
    elif s == 'build':
        if b == 8:
            snare_notes.extend(['S:e:mf']*8)
        else:
            snare_notes.extend(['S:s:mf']*16)
    elif s == 'chorus':
        snare_notes.extend(['R:q','S:q:ff','R:q','S:q:ff'])
    elif s == 'break':
        snare_notes.extend(['R:q']*4)              # silent break
    elif s in ('verse_return', 'outro'):
        snare_notes.extend(['R:q','S:q:pp','R:q','S:q:pp'])

lines.append('[track snare]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.6')
lines.append(f'notes = {",".join(snare_notes)}')
lines.append('')

# ── HIHAT ──
hihat_notes = []
for b in range(bars):
    s = section(b)
    if s == 'silence':
        hihat_notes.extend(['R:e']*8)
    elif s in ('intro', 'verse', 'break', 'verse_return', 'outro', 'coda'):
        hihat_notes.extend(['H:e:pp']*8)           # gentle closed hat
    elif s == 'build':
        if b == 8:
            hihat_notes.extend(['H:e:mf']*8)       # open up
        else:
            hihat_notes.extend(['H:s:mf']*16)      # tight sixteenth
    elif s == 'chorus':
        hihat_notes.extend(['H:s:mf']*16)          # crisp sixteenth

lines.append('[track hihat]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.3')
lines.append(f'notes = {",".join(hihat_notes)}')
lines.append('')

# ── BASS ──
bass_notes = []
for b in range(bars):
    c = chords[b]
    s = section(b)
    if s == 'silence':
        bass_notes.extend(['R:q']*4)
    elif s in ('intro', 'verse', 'break', 'verse_return', 'outro', 'coda'):
        root = c[1]
        bass_notes.extend([f'{root}:q:mp']*4)
    elif s == 'build':
        root = c[1]
        bass_notes.extend([f'{root}:q:mf']*4)
    elif s == 'chorus':
        root = c[1]
        # Walking root-fifth pattern
        fifth_map = {'C3':'G2','F2':'C3','G2':'D2','A2':'E2'}
        fifth = fifth_map.get(root, root)
        bass_notes.extend([f'{root}:q:mf', f'{fifth}:q:mf', f'{root}:q:mf', f'{fifth}:q:mf'])

lines.append('[track bass]')
lines.append('instrument = bass')
lines.append('mode = parallel')
lines.append('volume = 0.70')
lines.append('pan = -0.2')
lines.append(f'notes = {",".join(bass_notes)}')
lines.append('')

# ── PAD ──
pad_notes = []
for b in range(bars):
    c = chords[b]
    s = section(b)
    root = c[1]
    third = c[2]
    if s == 'silence':
        pad_notes.append('R:w')
    elif s in ('intro', 'coda'):
        # Soft sustained chord
        pad_notes.append(f'{root}:w:pp')
    elif s == 'verse':
        pad_notes.append(f'{root}:h:pp,R:h')        # half notes + rest
    elif s == 'build':
        pad_notes.append(f'{root}:h:mp,R:h')        # slightly louder
    elif s == 'chorus':
        pad_notes.append(f'{root}:h:mp,R:h')        # pulsing
    elif s in ('break', 'verse_return', 'outro'):
        pad_notes.append(f'{root}:h:pp,R:h')        # fade back

lines.append('[track pad]')
lines.append('instrument = pad')
lines.append('mode = parallel')
lines.append('volume = 0.30')
lines.append('pan = 0.3')
lines.append(f'notes = {",".join(pad_notes)}')
lines.append('')

# ── PIANO (arpeggiated broken chords, 8 eighth notes per bar) ──
piano_pat = {}
for label, root, third, fifth, octave in chords:
    pat = [f'{root}:e','{third}:e','{fifth}:e','{octave}:e'] * 2
    piano_pat[label] = [s.format(root=root, third=third, fifth=fifth, octave=octave) for s in pat]

piano_notes = []
for b in range(bars):
    c = chords[b]
    s = section(b)
    label = c[0]
    if s == 'silence':
        piano_notes.extend(['R:e']*8)
    elif s in ('intro',):
        ppat = piano_pat.get(label, ['R:e']*8)
        piano_notes.extend([f'{n}:pp' for n in ppat])
    elif s in ('verse',):
        ppat = piano_pat.get(label, ['R:e']*8)
        piano_notes.extend([f'{n}:pp' for n in ppat])
    elif s == 'build':
        if b == 8:
            piano_notes.extend([f'{c[1]}:s:pp']*16)  # root rising
        else:
            piano_notes.extend([f'{c[1]}:s:mf']*16)
    elif s == 'chorus':
        ppat = piano_pat.get(label, ['R:e']*8)
        piano_notes.extend([f'{n}:mf' for n in ppat])
    elif s == 'break':
        piano_notes.extend(['R:e']*8)
    elif s in ('verse_return', 'outro', 'coda'):
        ppat = piano_pat.get(label, ['R:e']*8)
        piano_notes.extend([f'{n}:pp' for n in ppat])

lines.append('[track piano]')
lines.append('instrument = piano')
lines.append('mode = parallel')
lines.append('volume = 0.65')
lines.append('pan = -0.3')
lines.append(f'notes = {",".join(piano_notes)}')
lines.append('')

# ── DRONE (warm string pad, sustained throughout) ──
drone_notes = []
for b in range(bars):
    c = chords[b]
    s = section(b)
    root = c[1]
    fifth = {'C3':'G3','Eb2':'Bb2','G2':'D3','Bb2':'F3','Ab2':'Eb3','A2':'E3','D3':'A3','F2':'C3','G2':'D3'}.get(root, root)
    if s == 'silence':
        drone_notes.append('R:w')
    elif s in ('intro', 'verse', 'verse_return', 'outro', 'coda'):
        drone_notes.append(f'{root}:w:pp')
    elif s in ('build', 'break'):
        drone_notes.append(f'{root}:w:pp')
    elif s == 'chorus':
        drone_notes.append(f'{root}:h:pp,{fifth}:h:pp')

lines.append('[track drone]')
lines.append('instrument = string')
lines.append('mode = parallel')
lines.append('volume = 0.20')
lines.append('pan = 0.2')
lines.append(f'notes = {",".join(drone_notes)}')
lines.append('')

# ── LEAD (melody) ──
# Melancholy motif: descending, stepwise, centered on root
# Joyful motif: ascending, brighter, "hihi" playful leaps
lead_melodies = {
    'intro_verse': {
        'Cm': ['G4:e:mp','C5:e:mp','Eb5:e:mp','C5:e:mp','G4:e:mp','C5:e:mp','Bb4:e:mp','G4:e:mp'],
        'Ab': ['Ab4:e:mp','C5:e:mp','Eb5:e:mp','C5:e:mp','Ab4:e:mp','C5:e:mp','Eb5:e:mp','C5:e:mp'],
        'Eb': ['Eb4:e:mp','G4:e:mp','Bb4:e:mp','G4:e:mp','Eb4:e:mp','G4:e:mp','Bb4:e:mp','G4:e:mp'],
        'Bb': ['Bb3:e:mp','D4:e:mp','F4:e:mp','D4:e:mp','Bb3:e:mp','D4:e:mp','F4:e:mp','D4:e:mp'],
    },
    'chorus': {
        'C':  ['C5:e:mf','G4:e:mf','E5:e:mf','G4:e:mf','C5:e:mf','G4:e:mf','E5:e:mf','G4:e:mf'],
        'F':  ['F5:e:mf','C5:e:mf','A5:e:mf','C5:e:mf','F5:e:mf','C5:e:mf','A5:e:mf','C5:e:mf'],
        'G':  ['G5:e:mf','D5:e:mf','B5:e:mf','D5:e:mf','G5:e:mf','D5:e:mf','B5:e:mf','D5:e:mf'],
        'Am': ['A5:e:mf','E5:e:mf','C6:e:mf','E5:e:mf','A5:e:mf','E5:e:mf','C6:e:mf','E5:e:mf'],
    },
    'break': {
        'G':  ['G4:e:mf','B4:e:mf','D5:e:mf','B4:e:mf','F4:e:mf','B4:e:mf','D5:e:mf','B4:e:mf'],
        'G7': ['G4:e:mf','B4:e:mf','F5:e:mf','D5:e:mf','G4:e:mf','B4:e:mf','D5:e:mf','F5:e:mf'],
    },
}

lead_notes = []
for b in range(bars):
    c = chords[b]
    s = section(b)
    label = c[0]
    if s == 'silence':
        lead_notes.extend(['R:e']*8)
    elif s == 'build':
        # Rests during build (percussion focus)
        lead_notes.extend(['R:e']*8)
    elif s in ('intro', 'verse'):
        pat = lead_melodies.get('intro_verse', {}).get(label)
        if pat:
            lead_notes.extend(pat)
        else:
            lead_notes.extend(['R:e']*8)
    elif s == 'chorus':
        pat = lead_melodies.get('chorus', {}).get(label)
        if pat:
            lead_notes.extend(pat)
        else:
            lead_notes.extend(['R:e']*8)
    elif s == 'break':
        pat = lead_melodies.get('break', {}).get(label)
        if pat:
            lead_notes.extend(pat)
        else:
            lead_notes.extend(['R:e']*8)
    elif s in ('verse_return', 'outro', 'coda'):
        pat = lead_melodies.get('intro_verse', {}).get(label)
        if pat:
            lead_notes.extend(pat)
        else:
            lead_notes.extend(['R:e']*8)

lead_flat = []
for item in lead_notes:
    lead_flat.extend(item.split(','))
lines.append('[track lead]')
lines.append('instrument = sawtooth')
lines.append('mode = parallel')
lines.append('volume = 0.45')
lines.append('pan = -0.1')
lines.append(f'notes = {",".join(lead_flat)}')
lines.append('')

# ── ARP (sixteenth-note arpeggios in chorus only) ──
arp_pat = {
    'C':  ['G4:s','C5:s','E5:s','G5:s'],
    'F':  ['A4:s','C5:s','F5:s','A5:s'],
    'G':  ['B4:s','D5:s','G5:s','B5:s'],
    'Am': ['A4:s','C5:s','E5:s','A5:s'],
}
arp_notes = []
for b in range(bars):
    c = chords[b]
    s = section(b)
    label = c[0]
    if s == 'chorus':
        pat = arp_pat.get(label, ['R:s']*4)
        arp_notes.extend([','.join(pat)] * 4)
    else:
        arp_notes.extend(['R:s,R:s,R:s,R:s'] * 4)
arp_flat = []
for item in arp_notes:
    arp_flat.extend(item.split(','))
lines.append('[track arp]')
lines.append('instrument = wavetable')
lines.append('wavetable = square')
lines.append('mode = parallel')
lines.append('volume = 0.25')
lines.append('pan = 0.5')
lines.append(f'notes = {",".join(arp_flat)}')
lines.append('')

# ── BELL ("hihi" playful accent in chorus only) ──
# Two quick high notes at start of each chorus bar: "hi-hi!"
bell_notes = []
for b in range(bars):
    s = section(b)
    if s == 'chorus':
        # "hi-hi!" — two quick G5 stabs at beat 0, then quarter-note rests
        bell_notes.append('G5:s:mf,G6:s:mf,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
    else:
        bell_notes.append('R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
bell_flat = []
for item in bell_notes:
    bell_flat.extend(item.split(','))
lines.append('[track bell]')
lines.append('instrument = bell')
lines.append('mode = parallel')
lines.append('volume = 0.50')
lines.append('pan = 0.4')
lines.append(f'notes = {",".join(bell_flat)}')

with open('samples/hihi.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/hihi.acml ({bars} bars, {bpm} BPM)')
