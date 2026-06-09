# KEIC Intermediate — 中级曲目, Lv6-9
# 135 BPM, Am (Touhou bVI-bVII-i), 6层, 56bars, ~1:40
# 特点: 短intro, 八分常规, 1.5 octave, 有build/drop对比

bars = 56
bpm = 135

# Am: A-C-E, F: F-A-C, G: G-B-D, C: C-E-G, Dm: D-F-A, E: E-Ab-B (E major, Ab=G# 无#)
chord_seq = ['Am','Am','F','G','C','C','Dm','E']
NOTES = {
    'Am': ('A2','C3','E3','A3','C4','E4','A4','C5'),
    'F':  ('F2','A2','C3','F3','A3','C4','F4','A4'),
    'G':  ('G2','B3','D4','G4','B4','D5','G5','B5'),
    'C':  ('C3','E3','G3','C4','E4','G4','C5','E5'),
    'Dm': ('D3','F3','A3','D4','F4','A4','D5','F5'),
    'E':  ('E2','Ab2','B2','E3','Ab3','B3','E4','Ab4'),  # E = E-Ab-B (Gb=Ab)
}
ROOT = {'Am':'A1','F':'F1','G':'G1','C':'C2','Dm':'D2','E':'E1'}
ROOT3 = {'Am':'A2','F':'F2','G':'G2','C':'C3','Dm':'D3','E':'E2'}

def sec(b):
    if b < 4:    return 'intro'
    if b < 20:   return 'verse'
    if b < 28:   return 'build'
    if b < 44:   return 'drop'
    return 'outro'

def ch(b):
    return chord_seq[b % 8]

lines = [f'# KEIC Intermediate — 中级曲目', f'name = "keic_med"', f'bpm = {bpm}', '']

# KICK
kick = []
for b in range(bars):
    s = sec(b)
    if s == 'intro':
        kick.extend(['K:q:mf','R:q','K:q:mf','R:q'])
    elif s == 'build':
        if b % 8 < 4:
            kick.extend(['K:q:mf','R:q','K:q:mf','R:q'])
        else:
            kick.extend(['K:q:mf','K:e:mp','R:e','K:q:mf','R:q'])
    elif s == 'outro':
        if b < 52:
            kick.extend(['K:q:mp','R:q','R:q','R:q'])
        else:
            kick.extend(['R:q']*4)
    else:
        kick.extend(['K:q:mf','R:q','K:q:mf','R:q'])
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.72')
lines.append(f'notes = {",".join(kick)}\n')

# SNARE
snare = []
for b in range(bars):
    s = sec(b)
    if s == 'intro':
        snare.extend(['R:q','S:q:mp','R:q','S:q:mp'])
    elif s == 'build':
        if b % 8 < 4:
            snare.extend(['R:q','S:e:pp','R:e','R:q','S:e:pp','R:e'])
        else:
            snare.extend(['S:e:mf']*8)
    elif s == 'outro':
        snare.extend(['R:q']*4)
    else:
        snare.extend(['R:q','S:q:mf','R:q','S:q:mf'])
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.58')
lines.append(f'notes = {",".join(snare)}\n')

# HIHAT (八分常规, 中级标志)
hihat = []
for b in range(bars):
    s = sec(b)
    if s == 'build' and b % 8 >= 4:
        hihat.extend(['H:s:mp']*16)
    elif s == 'outro':
        hihat.extend(['R:e']*8)
    else:
        hihat.extend(['H:e:mp']*8)
lines.append('[track hihat]\ninstrument = drums\nmode = parallel\nvolume = 0.28')
lines.append(f'notes = {",".join(hihat)}\n')

# BASS
bass = []
for b in range(bars):
    s = sec(b)
    r = ROOT[ch(b)]
    if s == 'outro' and b >= 52:
        bass.append('R:w')
    elif s == 'outro':
        bass.append(f'{r}:h:mp,{r}:h:mp')
    else:
        bass.append(f'{r}:w:mf')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.67')
lines.append(f'notes = {",".join(bass)}\n')

# PIANO
piano = []
for b in range(bars):
    s = sec(b)
    n = NOTES[ch(b)]
    r, t3, t5, o, t3h, t5h, o2, t3hh = n
    if s == 'intro':
        p = f'{r}:h:mp,{o}:h:mp'
    elif s == 'verse':
        if b % 2 == 0:
            p = f'{r}:q:mp,{t5}:e:mp,{t3h}:e:mp,{o}:q:mp,{o}:e:mp,{t5h}:e:mp'
        else:
            p = f'{o}:q:mp,{t5h}:e:mp,{t3hh}:e:mp,{o2}:q:mp,{t5h}:e:mp,{o2}:e:mp'
    elif s == 'build':
        p = f'{r}:e:mf,{t3}:e:mf,{t5}:e:mf,{o}:e:mf,{t3h}:e:mf,{t5h}:e:mf,{o2}:e:mf,{t3hh}:e:mf'
    elif s == 'drop':
        p = f'{r}:q:mf,{t3}:e:mf,{o}:e:mf,{o2}:q:mf,R:q'
    else:
        if b < 52:
            p = f'{r}:h:mp,{o}:q:mp,{o2}:q:mp'
        else:
            p = f'{r}:w:pp'
    piano.extend(p.split(','))
lines.append('[track piano]\ninstrument = piano\nmode = parallel\nvolume = 0.52')
lines.append(f'notes = {",".join(piano)}\n')

# PAD
pad = []
for b in range(bars):
    s = sec(b)
    r = ROOT3[ch(b)]
    if s in ('intro','outro'):
        pad.append(f'{r}:w:pp')
    elif s == 'verse':
        pad.append(f'{r}:w:mp')
    else:
        pad.append(f'{r}:w:mf')
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.25\npan = 0.3')
lines.append(f'notes = {",".join(pad)}\n')

# LEAD (Am motif, 1.5 octave range, Touhou bVI-bVII-i flavor)
lead = []
for b in range(bars):
    s = sec(b)
    idx = b % 8
    if s == 'intro':
        lead.append('R:w')
    elif s == 'verse':
        if idx == 0: lead.append('A4:e:mp,C5:e:mp,E5:e:mp,A5:e:mp,E5:e:mp,C5:e:mp,A4:e:mp,E4:e:mp')
        elif idx == 1: lead.append('A4:e:mp,E5:e:mp,A5:e:mp,E6:e:mp,A5:e:mp,E5:e:mp,A4:e:mp,R:e')
        elif idx == 2: lead.append('F4:e:mp,A4:e:mp,C5:e:mp,F5:e:mp,C5:e:mp,A4:e:mp,F4:e:mp,A4:e:mp')
        elif idx == 3: lead.append('G4:e:mp,B4:e:mp,D5:e:mp,G5:e:mp,D5:e:mp,B4:e:mp,G4:e:mp,D5:e:mp')
        elif idx == 4: lead.append('C5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp,E5:e:mp')
        elif idx == 5: lead.append('C5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp,R:e')
        elif idx == 6: lead.append('D5:e:mp,F5:e:mp,A5:e:mp,D6:e:mp,A5:e:mp,F5:e:mp,D5:e:mp,F5:e:mp')
        else: lead.append('E4:e:mp,Ab4:e:mp,B4:e:mp,E5:e:mp,B4:e:mp,Ab4:e:mp,E4:e:mp,R:e')
    elif s == 'build':
        if idx < 4:
            lead.append('A4:e:mp,E4:e:mp,C4:e:mp,A3:e:mp,R:e,R:e,R:e,R:e')
        elif idx < 6:
            lead.append('A5:e:mp,C5:e:mp,E5:e:mp,A5:e:mp,R:e,R:e,R:e,R:e')
        else:
            lead.append('E5:e:mf,G5:e:mf,B5:e:mf,E6:e:mf,B5:e:mf,G5:e:mf,E5:e:mf,B4:e:mf')
    elif s == 'drop':
        if idx == 0: lead.append('A5:e:mf,C6:e:mf,E6:e:mf,A6:e:mf,E6:e:mf,C6:e:mf,A5:e:mf,E5:e:mf')
        elif idx == 1: lead.append('A5:e:mf,E6:e:mf,A6:e:mf,E7:e:mf,A6:e:mf,E6:e:mf,A5:e:mf,R:e')
        elif idx == 2: lead.append('F4:e:mf,A4:e:mf,C5:e:mf,F5:e:mf,A5:e:mf,C6:e:mf,F6:e:mf,A5:e:mf')
        elif idx == 3: lead.append('G4:e:mf,B4:e:mf,D5:e:mf,G5:e:mf,B5:e:mf,D6:e:mf,G6:e:mf,D6:e:mf')
        elif idx == 4: lead.append('C5:e:mf,E5:e:mf,G5:e:mf,C6:e:mf,E6:e:mf,G6:e:mf,C7:e:mf,G6:e:mf')
        elif idx == 5: lead.append('C5:e:mf,E5:e:mf,G5:e:mf,C6:e:mf,E6:e:mf,G6:e:mf,C7:e:mf,R:e')
        elif idx == 6: lead.append('D5:e:mf,F5:e:mf,A5:e:mf,D6:e:mf,F6:e:mf,A6:e:mf,D7:e:mf,A6:e:mf')
        else: lead.append('E4:e:mf,Ab4:e:mf,B4:e:mf,E5:e:mf,Ab5:e:mf,B5:e:mf,E6:e:mf,Ab5:e:mf')
    else:
        if b < 52:
            lead.append('A4:e:pp,E4:e:pp,C4:e:pp,A3:e:pp,R:e,R:e,R:e,R:e')
        else:
            lead.append('R:w')

lines.append('[track lead]\ninstrument = sawtooth\nmode = parallel\nvolume = 0.48')
lines.append(f'notes = {",".join(lead)}\n')

# CHORD STAB (Marshmello/BEMANI, only in drop)
STAB_RTF = {
    'Am': ('A2','C3','E3'), 'F': ('F2','A2','C3'),
    'G':  ('G2','B3','D4'), 'C': ('C3','E3','G3'),
    'Dm': ('D3','F3','A3'), 'E': ('E2','Ab2','B2'),
}
stab = []
for b in range(bars):
    s = sec(b)
    r,t,f = STAB_RTF[ch(b)]
    if s == 'drop' and b % 2 == 0:
        stab.append(f'{r}:s:mf,{t}:s:mf,{f}:s:mf,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
    else:
        stab.append('R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
stab_flat = [x for g in stab for x in g.split(',')]
lines.append('[track stab]\ninstrument = wavetable\nwavetable = sawtooth\nmode = parallel\nvolume = 0.32')
lines.append(f'notes = {",".join(stab_flat)}')

with open('samples/keic_med.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/keic_med.acml ({bars} bars, {bpm} BPM, {bars*4*60/bpm:.0f}s)')
