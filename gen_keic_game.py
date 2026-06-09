# KEIC BEMANI Game Track — BEMANI结构 + Touhou和声 + AW厚度
# BEMANI: 1:42 game edit, Intro→Verse→Build→Drop→A'→Build2→Final→Outro
# Touhou: bVI-bVII-i, 借位和弦Eb, 旋律模进, 硬切
# Key: Dm | BPM 150 | 64 bars | 无#号

bars = 64
bpm = 150

chord_seq = ['Dm','Dm','Bb','C','F','Eb','Am','C']
# Dm = D-F-A, Bb = Bb-D-F, C = C-E-G, F = F-A-C, Eb = Eb-G-Bb, Am = A-C-E

def sec(b):
    if b < 8:    return 'intro'
    if b < 16:   return 'verse'
    if b < 24:   return 'build'
    if b < 32:   return 'drop'
    if b < 40:   return 'verse2'
    if b < 48:   return 'build2'
    if b < 56:   return 'final'
    return 'outro'

def ch(b):
    return chord_seq[b % 8]

ROOT = {'Dm':'D2','Bb':'Bb1','C':'C2','F':'F1','Eb':'Eb1','Am':'A1'}
ROOT3 = {'Dm':'D3','Bb':'Bb2','C':'C3','F':'F2','Eb':'Eb2','Am':'A2'}
NOTES = {
    'Dm': ('D3','F3','A3','D4','F4','A4','D5','F5'),
    'Bb': ('Bb2','D3','F3','Bb3','D4','F4','Bb4','D5'),
    'C':  ('C3','E3','G3','C4','E4','G4','C5','E5'),
    'F':  ('F2','A2','C3','F3','A3','C4','F4','A4'),
    'Eb': ('Eb2','G3','Bb3','Eb4','G4','Bb4','Eb5','G5'),
    'Am': ('A2','C3','E3','A3','C4','E4','A5','C5'),
}

lines = []
lines.append('# KEIC BEMANI Game Track — 音游专用')
lines.append(f'name = "keic_game"')
lines.append(f'bpm = {bpm}')
lines.append('')

# ════════ KICK (BEMANI: 清晰click感) ════════
kick = []
for b in range(bars):
    s = sec(b)
    if s == 'outro' and b >= 60:
        kick.extend(['K:q:ff','R:q','K:q:ff','R:q']) if b < 62 else kick.extend(['R:q']*4)
    elif s in ('intro',):
        kick.extend(['K:q:mf','R:q','K:q:mf','R:q'])  # 4/floor click
    elif s in ('build','build2'):
        if b % 8 < 4:
            kick.extend(['K:q:mf','R:q','K:q:mf','R:q'])
        else:
            # snare roll overlap: kick on 1.5, 2.5, 3.5
            kick.extend(['K:q:mf','K:e:mf','R:e','K:q:mf','R:q'])
    elif s == 'outro':
        kick.extend(['K:q:mp','R:q','R:q','R:q'])
    else:
        kick.extend(['K:q:mf','R:q','K:q:mf','R:q'])

lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.75')
lines.append(f'notes = {",".join(kick)}\n')

# ════════ SNARE ════════
snare = []
for b in range(bars):
    s = sec(b)
    if s == 'intro' and b < 4:
        snare.extend(['R:q']*4)
    elif s in ('intro','verse','verse2'):
        snare.extend(['R:q','S:q:mp','R:q','S:q:mp'])
    elif s in ('build','build2'):
        if b % 8 < 4:
            snare.extend(['R:q','S:e:pp','R:e','R:q','S:e:pp','R:e'])
        else:
            snare.extend(['S:e:mf']*8)  # snare roll
    elif s in ('drop','final'):
        snare.extend(['R:q','S:q:mf','R:q','S:q:mf'])
    else:
        snare.extend(['R:q']*4)

lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.60')
lines.append(f'notes = {",".join(snare)}\n')

# ════════ HIHAT ════════
hihat = []
for b in range(bars):
    s = sec(b)
    if s == 'intro' and b < 4:
        hihat.extend(['R:e']*8)
    elif s in ('intro','verse','verse2','drop','final'):
        hihat.extend(['H:e:mp']*8)
    elif s in ('build','build2'):
        if b % 8 < 4:
            hihat.extend(['H:e:mp']*8)
        else:
            hihat.extend(['H:s:mf']*16)
    else:
        hihat.extend(['R:e']*8)

lines.append('[track hihat]\ninstrument = drums\nmode = parallel\nvolume = 0.30')
lines.append(f'notes = {",".join(hihat)}\n')

# ════════ BASS ════════
bass = []
for b in range(bars):
    s = sec(b)
    r = ROOT[ch(b)]
    if s == 'outro' and b >= 62:
        bass.append('R:w')
    elif s == 'outro':
        bass.append(f'{r}:h:mp,{r}:h:mp')
    else:
        bass.append(f'{r}:w:mf')

lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.70')
lines.append(f'notes = {",".join(bass)}\n')

# ════════ PIANO (BEMANI chord comping) ════════
piano = []
for b in range(bars):
    s = sec(b)
    n = NOTES[ch(b)]
    r, t3, t5, o, t3h, t5h, o2, t3hh = n

    if s == 'intro':
        p = f'{r}:h:mf,{o}:h:mf'
    elif s in ('verse','verse2'):
        if s == 'verse2':
            # different inversion for variation
            p = f'{o}:q:mf,{t5h}:e:mf,{o2}:e:mf,{r}:q:mf,{o}:e:mf,{t5h}:e:mf'
        else:
            p = f'{r}:q:mf,{t5}:e:mf,{t3h}:e:mf,{o}:q:mf,{o}:e:mf,{t5h}:e:mf'
    elif s in ('build','build2'):
        p = f'{r}:e:mf,{t3}:e:mf,{t5}:e:mf,{o}:e:mf,{t3h}:e:mf,{t5h}:e:mf,{o2}:e:mf,{t3hh}:e:mf'
    elif s in ('drop','final'):
        if s == 'final':
            p = f'{r}:q:ff,{o}:e:ff,{o2}:e:ff,{t3h}:q:ff,R:q'
        else:
            p = f'{r}:q:mf,{t3}:e:mf,{o}:e:mf,{o2}:q:mf,R:q'
    else:
        p = f'{r}:h:mp,{o}:q:mp,{o2}:q:mp'
    piano.extend(p.split(','))

lines.append('[track piano]\ninstrument = piano\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(piano)}\n')

# ════════ PAD (supersaw-like, always on) ════════
pad = []
for b in range(bars):
    s = sec(b)
    r = ROOT3[ch(b)]
    if s in ('intro','verse','verse2'):
        pad.append(f'{r}:w:pp')
    elif s in ('build','build2'):
        pad.append(f'{r}:w:mp')
    elif s in ('drop','final'):
        pad.append(f'{r}:w:mf')
    else:
        pad.append(f'{r}:w:pp')

lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.30\npan = 0.3')
lines.append(f'notes = {",".join(pad)}\n')

# ════════ LEAD (BEMANI main melody — motif driven) ════════
# Motif A: A4-D5-F5-G5-A5 (rising) [Dm-Dorian feel]
# Motif B: D5-F5-G5-A5-D6 (high climax)
# Motif C: A5-F5-D5-C5-Bb4-A4 (descending sequence)

lead = []
for b in range(bars):
    s = sec(b)
    idx = b % 8

    if s == 'intro':
        lead.append('R:w')
    elif s == 'verse':
        if idx == 0:
            lead.append('A4:e:mp,D5:e:mp,F5:e:mp,G5:e:mp,A5:e:mp,G5:e:mp,F5:e:mp,E5:e:mp')
        elif idx == 1:
            lead.append('D5:e:mp,F5:e:mp,A5:e:mp,D6:e:mp,A5:e:mp,F5:e:mp,D5:e:mp,R:e')
        elif idx == 2:
            lead.append('Bb4:e:mp,D5:e:mp,F5:e:mp,Bb5:e:mp,F5:e:mp,D5:e:mp,Bb4:e:mp,R:e')
        elif idx == 3:
            lead.append('C5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp,R:e')
        elif idx == 4:
            lead.append('F4:e:mp,A4:e:mp,C5:e:mp,F5:e:mp,C5:e:mp,A4:e:mp,F4:e:mp,A4:e:mp')
        elif idx == 5:
            lead.append('Eb4:e:mp,G4:e:mp,Bb4:e:mp,Eb5:e:mp,Bb4:e:mp,G4:e:mp,Eb4:e:mp,R:e')
        elif idx == 6:
            lead.append('A4:e:mp,C5:e:mp,E5:e:mp,A5:e:mp,E5:e:mp,C5:e:mp,A4:e:mp,R:e')
        else:
            lead.append('C5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp,B4:e:mp')
    elif s == 'build':
        if idx < 2:
            lead.append('R:w')
        elif idx < 4:
            lead.append('A4:e:mp,F4:e:mp,D4:e:mp,C4:e:mp,A4:e:mp,F4:e:mp,D4:e:mp,C4:e:mp')
        elif idx < 6:
            lead.append('D5:e:mp,F5:e:mp,A5:e:mp,D6:e:mp,A5:e:mp,F5:e:mp,D5:e:mp,A4:e:mp')
        else:
            lead.append('G5:e:mf,B5:e:mf,D6:e:mf,G6:e:mf,D6:e:mf,B5:e:mf,G5:e:mf,D5:e:mf')
    elif s == 'drop':
        if idx == 0:
            lead.append('D5:e:mf,F5:e:mf,A5:e:mf,D6:e:mf,A5:e:mf,F5:e:mf,D5:e:mf,A4:e:mf')
        elif idx == 1:
            lead.append('A5:e:mf,G5:e:mf,F5:e:mf,E5:e:mf,D5:e:mf,F5:e:mf,A5:e:mf,D6:e:mf')
        elif idx == 2:
            lead.append('Bb4:e:mf,D5:e:mf,F5:e:mf,Bb5:e:mf,F5:e:mf,D5:e:mf,Bb4:e:mf,F5:e:mf')
        elif idx == 3:
            lead.append('C5:e:mf,E5:e:mf,G5:e:mf,C6:e:mf,G5:e:mf,E5:e:mf,C5:e:mf,G5:e:mf')
        elif idx == 4:
            lead.append('F4:e:mf,A4:e:mf,C5:e:mf,F5:e:mf,A5:e:mf,C6:e:mf,A5:e:mf,F5:e:mf')
        elif idx == 5:
            lead.append('Eb4:e:mf,G4:e:mf,Bb4:e:mf,Eb5:e:mf,G5:e:mf,Bb5:e:mf,Eb6:e:mf,Bb5:e:mf')
        elif idx == 6:
            lead.append('A4:e:mf,C5:e:mf,E5:e:mf,A5:e:mf,E5:e:mf,C5:e:mf,A4:e:mf,E5:e:mf')
        else:
            lead.append('C5:e:mf,E5:e:mf,G5:e:mf,C6:e:mf,G5:e:mf,E5:e:mf,C5:e:mf,G5:e:mf')
    elif s == 'verse2':
        # Motif A with variations
        if idx == 0:
            lead.append('F5:e:mp,G5:e:mp,A5:e:mp,D6:e:mp,A5:e:mp,G5:e:mp,F5:e:mp,E5:e:mp')
        elif idx == 1:
            lead.append('D5:e:mp,F5:e:mp,A5:e:mp,D6:e:mp,C6:e:mp,Bb5:e:mp,A5:e:mp,G5:e:mp')
        elif idx in (2,3):
            lead.append('R:w')
        elif idx in (4,5):
            lead.append('R:w')
        elif idx == 6:
            lead.append('A4:e:mp,C5:e:mp,E5:e:mp,A5:e:mp,E5:e:mp,C5:e:mp,A4:e:mp,C5:e:mp')
        else:
            lead.append('C5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp,G5:e:mp')
    elif s == 'build2':
        if idx < 4:
            lead.append('A4:e:mp,F4:e:mp,D4:e:mp,C4:e:mp,R:e,R:e,R:e,R:e')
        else:
            lead.append('D5:e:mf,F5:e:mf,A5:e:mf,D6:e:mf,F5:e:mf,A5:e:mf,D6:e:mf,F6:e:mf')
    elif s == 'final':
        if idx == 0:
            lead.append('D5:e:ff,F5:e:ff,A5:e:ff,D6:e:ff,A5:e:ff,F5:e:ff,D5:e:ff,A5:e:ff')
        elif idx == 1:
            lead.append('D6:e:ff,C6:e:ff,Bb5:e:ff,A5:e:ff,G5:e:ff,F5:e:ff,E5:e:ff,D5:e:ff')
        elif idx == 2:
            lead.append('Bb4:e:ff,D5:e:ff,F5:e:ff,Bb5:e:ff,F5:e:ff,D5:e:ff,Bb4:e:ff,F5:e:ff')
        elif idx == 3:
            lead.append('C5:e:ff,E5:e:ff,G5:e:ff,C6:e:ff,G5:e:ff,E5:e:ff,C5:e:ff,G5:e:ff')
        elif idx == 4:
            lead.append('F4:e:ff,A4:e:ff,C5:e:ff,F5:e:ff,A5:e:ff,C6:e:ff,A5:e:ff,F5:e:ff')
        elif idx == 5:
            lead.append('Eb4:e:ff,G4:e:ff,Bb4:e:ff,Eb5:e:ff,G5:e:ff,Bb5:e:ff,Eb6:e:ff,Bb5:e:ff')
        elif idx == 6:
            lead.append('A4:e:ff,C5:e:ff,E5:e:ff,A5:e:ff,C6:e:ff,E6:e:ff,C6:e:ff,A5:e:ff')
        else:
            lead.append('C5:e:ff,E5:e:ff,G5:e:ff,C6:e:ff,E6:e:ff,G6:e:ff,E6:e:ff,C6:e:ff')
    else:
        if b < 60:
            lead.append('D5:e:pp,A4:e:pp,F4:e:pp,D4:e:pp,R:e,R:e,R:e,R:e')
        else:
            lead.append('R:w')

lines.append('[track lead]\ninstrument = sawtooth\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(lead)}\n')

# ════════ LEAD2 (BEMANI call-and-response, octave higher) ════════
lead2 = []
for b in range(bars):
    s = sec(b)
    idx = b % 8

    if s in ('drop','final'):
        if idx == 0:
            lead2.append('R:e,R:e,R:e,R:e,D6:e:ff,F6:e:ff,A6:e:ff,D7:e:ff')
        elif idx == 1:
            lead2.append('R:e,R:e,R:e,R:e,D6:e:ff,C6:e:ff,Bb5:e:ff,A5:e:ff')
        elif idx == 2:
            lead2.append('R:e,R:e,R:e,R:e,Bb5:e:ff,D6:e:ff,F6:e:ff,Bb6:e:ff')
        elif idx == 3:
            lead2.append('R:e,R:e,R:e,R:e,C6:e:ff,E6:e:ff,G6:e:ff,C7:e:ff')
        elif idx == 4:
            lead2.append('R:e,R:e,R:e,R:e,F5:e:ff,A5:e:ff,C6:e:ff,F6:e:ff')
        elif idx == 5:
            lead2.append('R:e,R:e,R:e,R:e,Eb5:e:ff,G5:e:ff,Bb5:e:ff,Eb6:e:ff')
        elif idx == 6:
            lead2.append('R:e,R:e,R:e,R:e,A5:e:ff,C6:e:ff,E6:e:ff,A6:e:ff')
        else:
            lead2.append('R:e,R:e,R:e,R:e,C6:e:ff,E6:e:ff,G6:e:ff,C7:e:ff')
    elif s == 'verse':
        if idx == 4:
            lead2.append('F5:e:mp,A5:e:mp,C6:e:mp,F6:e:mp,C6:e:mp,A5:e:mp,F5:e:mp,A5:e:mp')
        else:
            lead2.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
    elif s == 'verse2':
        if idx == 4:
            lead2.append('A5:e:mp,A5:e:mp,A5:e:mp,A5:e:mp,A5:e:mp,A5:e:mp,A5:e:mp,A5:e:mp')
        else:
            lead2.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
    elif s in ('build','build2'):
        lead2.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
    elif s == 'final':
        if idx == 0:
            lead2.append('R:e,R:e,R:e,R:e,F6:e:ff,D6:e:ff,F6:e:ff,A6:e:ff')
        elif idx == 1:
            lead2.append('R:e,R:e,R:e,R:e,F6:e:ff,E6:e:ff,D6:e:ff,C6:e:ff')
        elif idx == 2:
            lead2.append('R:e,R:e,R:e,R:e,Bb5:e:ff,D6:e:ff,F6:e:ff,Bb6:e:ff')
        elif idx == 3:
            lead2.append('R:e,R:e,R:e,R:e,C6:e:ff,E6:e:ff,G6:e:ff,C7:e:ff')
        elif idx == 4:
            lead2.append('R:e,R:e,R:e,R:e,F5:e:ff,A5:e:ff,C6:e:ff,F6:e:ff')
        elif idx == 5:
            lead2.append('R:e,R:e,R:e,R:e,Eb5:e:ff,G5:e:ff,Bb5:e:ff,Eb6:e:ff')
        elif idx == 6:
            lead2.append('R:e,R:e,R:e,R:e,A5:e:ff,C6:e:ff,E6:e:ff,A6:e:ff')
        else:
            lead2.append('R:e,R:e,R:e,R:e,C6:e:ff,E6:e:ff,G6:e:ff,C7:e:ff')
    else:
        lead2.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')

lead2_flat = []
for item in lead2:
    lead2_flat.extend(item.split(','))

lines.append('[track lead2]\ninstrument = sawtooth\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join(lead2_flat)}\n')

# ════════ CHORD STAB (BEMANI supersaw style) ════════
STAB = {
    'Dm': ('D3','F3','A3'),
    'Bb': ('Bb2','D3','F3'),
    'C':  ('C3','E3','G3'),
    'F':  ('F2','A2','C3'),
    'Eb': ('Eb2','G3','Bb3'),
    'Am': ('A2','C3','E3'),
}
stab = []
for b in range(bars):
    s = sec(b)
    r,t,f = STAB[ch(b)]
    if s in ('drop','final') and b % 2 == 0:
        stab.append(f'{r}:s:mf,{t}:s:mf,{f}:s:mf,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
    else:
        stab.append('R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
stab_flat = [x for g in stab for x in g.split(',')]
lines.append('[track stab]\ninstrument = wavetable\nwavetable = sawtooth\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join(stab_flat)}\n')

# ════════ FILL (crash cymbal accents at section boundaries) ════════
crash = []
crash_bars = {0,8,16,24,32,40,48,56}
for b in range(bars):
    if b in crash_bars:
        crash.extend(['C:q:mf','R:q','R:q','R:q'])
    else:
        crash.extend(['R:q']*4)

lines.append('[track crash]\ninstrument = drums\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(crash)}')

with open('samples/keic_game.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/keic_game.acml ({bars} bars, {bpm} BPM, {bars*4*60/bpm:.0f}s)')
