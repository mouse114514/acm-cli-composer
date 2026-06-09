# Alan Walker style ACML generator for KEIC
# Key: C#m | Progression: i-VI-III-VII = C#m-A-E-B | BPM 128 | 32 bars = 60s
# ACML parser treats # as comment, so use flat names (Db for C#, etc.)
# All tracks must have EXACTLY 4 beats per bar (128 beats total for 32 bars)

bars = 32
cycle = ['C#m', 'A', 'E', 'B']
chord_bars = [cycle[i % 4] for i in range(bars)]

# Flat note name (no # in output)
def f(n): return (n.replace('C#','Db').replace('D#','Eb')
                  .replace('F#','Gb').replace('G#','Ab').replace('A#','Bb'))

lines = []
lines.append('# KEIC Theme — Alan Walker Style')
lines.append('# Key: C#m | Progression: i-VI-III-VII = C#m-A-E-B')
lines.append('# BPM 128 (like Spectre) | 32 bars = 60s')
lines.append('# Melody: simple, stepwise, repetitive (like Faded)')
lines.append('name = "keic_theme_aw"')
lines.append('bpm = 128')
lines.append('')

# KICK: 4-on-the-floor (4 beats/bar)
kick = []
for b in range(bars):
    kick.extend(['K:q:mf', 'R:q', 'K:q:mf', 'R:q'])
lines.append('[track kick]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.8')
lines.append(f'notes = {",".join(kick)}')
lines.append('')

# SNARE with roll transitions (4 beats/bar)
snare = []
for b in range(bars):
    if b < 4:        # intro: no snare
        snare.extend(['R:q'] * 4)
    elif b < 6:      # build 5-6: normal
        snare.extend(['R:q', 'S:q:mf', 'R:q', 'S:q:mf'])
    elif b < 8:      # build 7-8: roll
        snare.extend(['S:e:mf'] * 8)
    elif b < 16:     # drop 9-16: normal
        snare.extend(['R:q', 'S:q:mf', 'R:q', 'S:q:mf'])
    elif b < 20:     # breakdown 17-20: no snare
        snare.extend(['R:q'] * 4)
    elif b < 22:     # build2 21-22: normal
        snare.extend(['R:q', 'S:q:mf', 'R:q', 'S:q:mf'])
    elif b < 24:     # build2 23-24: roll
        snare.extend(['S:e:mf'] * 8)
    elif b < 30:     # drop2 25-30: normal
        snare.extend(['R:q', 'S:q:mf', 'R:q', 'S:q:mf'])
    else:            # outro 31-32: no snare
        snare.extend(['R:q'] * 4)

lines.append('[track snare]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.65')
lines.append(f'notes = {",".join(snare)}')
lines.append('')

# HIHAT: eighth notes (4 beats/bar)
hihat = []
for b in range(bars):
    if b < 4:
        hihat.extend(['R:e'] * 8)
    else:
        hihat.extend(['H:e:mf'] * 8)
lines.append('[track hihat]')
lines.append('instrument = drums')
lines.append('mode = parallel')
lines.append('volume = 0.35')
lines.append(f'notes = {",".join(hihat)}')
lines.append('')

# BASS: chord root quarter notes (4 beats/bar)
chord_root = {'C#m': 'Db1', 'A': 'A0', 'E': 'E1', 'B': 'B0'}
bass = []
for b in range(bars):
    root = chord_root[chord_bars[b]]
    bass.extend([f'{root}:q:mf'] * 4)
lines.append('[track bass]')
lines.append('instrument = bass')
lines.append('mode = parallel')
lines.append('volume = 0.75')
lines.append('pan = -0.2')
lines.append(f'notes = {",".join(bass)}')
lines.append('')

# PAD: single root whole note per bar (4 beats)
chord_pad = {'C#m': 'Db2:w:mp', 'A': 'A2:w:mp', 'E': 'E2:w:mp', 'B': 'B2:w:mp'}
pad = [chord_pad[chord_bars[b]] for b in range(bars)]
lines.append('[track pad]')
lines.append('instrument = pad')
lines.append('mode = parallel')
lines.append('volume = 0.35')
lines.append('pan = 0.3')
lines.append(f'notes = {",".join(pad)}')
lines.append('')

# PIANO: arpeggiated broken chords (8 eighth notes/bar = 4 beats)
piano_arp = {
    'C#m': [f('Db4:e:mf'), 'E4:e:mf', f('Ab4:e:mf'), f('Db5:e:mf')] * 2,
    'A': ['A3:e:mf', f('Db4:e:mf'), 'E4:e:mf', 'A4:e:mf'] * 2,
    'E': ['E3:e:mf', f('Ab3:e:mf'), 'B3:e:mf', 'E4:e:mf'] * 2,
    'B': ['B2:e:mf', f('Eb3:e:mf'), f('Gb3:e:mf'), 'B3:e:mf'] * 2,
}
piano = []
for b in range(bars):
    piano.extend(piano_arp[chord_bars[b]])
lines.append('[track piano]')
lines.append('instrument = piano')
lines.append('mode = parallel')
lines.append('volume = 0.6')
lines.append('pan = -0.3')
lines.append(f'notes = {",".join(piano)}')
lines.append('')

# CRASH: bell at drop starts only (4 beats/bar with rests)
crash = ['R:q'] * (bars * 4)
crash[8*4] = f('Ab5:e:mf')
crash[24*4] = f('Ab5:e:mf')
lines.append('[track crash]')
lines.append('instrument = bell')
lines.append('mode = parallel')
lines.append('volume = 0.55')
lines.append('pan = 0.4')
lines.append(f'notes = {",".join(crash)}')
lines.append('')

# LEAD: simple pentatonic melody (4 beats/bar — exactly 6 eighth notes = 3 beats + 1 rest)
lead_melody = {
    'C#m': f('Db5:e:mf,Gb5:e:mf,Ab5:e:mf,Gb5:e:mf,Db5:e:mf,Ab4:e:mf,R:e,R:e'),
    'A': f('A4:e:mf,Db5:e:mf,E5:e:mf,Db5:e:mf,A4:e:mf,E4:e:mf,R:e,R:e'),
    'E': f('E4:e:mf,Ab4:e:mf,B4:e:mf,Ab4:e:mf,E5:e:mf,Ab4:e:mf,R:e,R:e'),
    'B': f('B4:e:mf,Eb5:e:mf,Gb5:e:mf,Eb5:e:mf,B4:e:mf,Gb4:e:mf,R:e,R:e'),
}
lead = []
for b in range(bars):
    if (8 <= b < 16) or (24 <= b < 30):
        lead.append(lead_melody[chord_bars[b]])
    else:
        lead.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
lead_flat = []
for item in lead:
    lead_flat.extend(item.split(','))
lines.append('[track lead]')
lines.append('instrument = sawtooth')
lines.append('mode = parallel')
lines.append('volume = 0.5')
lines.append('pan = -0.1')
lines.append(f'notes = {",".join(lead_flat)}')
lines.append('')

# ARP: sixteenth-note arpeggios (16 sixteenth notes/bar = 4 beats)
arp_notes = {
    'C#m': f('Db5:s,E5:s,Ab5:s,Db6:s'),
    'A': f('A4:s,Db5:s,E5:s,A5:s'),
    'E': f('E4:s,Ab4:s,B4:s,E5:s'),
    'B': f('B4:s,Eb5:s,Gb5:s,B5:s'),
}
arp = []
for b in range(bars):
    if (8 <= b < 16) or (24 <= b < 30):
        for _ in range(4):
            arp.append(arp_notes[chord_bars[b]])
    else:
        for _ in range(4):
            arp.append('R:s,R:s,R:s,R:s')
arp_flat = []
for item in arp:
    arp_flat.extend(item.split(','))
lines.append('[track arp]')
lines.append('instrument = wavetable')
lines.append('wavetable = square')
lines.append('mode = parallel')
lines.append('volume = 0.35')
lines.append('pan = 0.5')
lines.append(f'notes = {",".join(arp_flat)}')

with open('samples/keic_theme_aw.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated keic_theme_aw.acml ({bars} bars)')
