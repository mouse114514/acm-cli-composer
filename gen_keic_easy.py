# KEIC Beginner — 初学者曲目, Lv1-5
# 120 BPM, C大调, 4层, 48bars, 1:36
# 特点: 长intro, 全八分以下, 1 octave音域, 鼓不变, 简单I-IV-V

bars = 48
bpm = 120

chord_seq = ['C','G','Am','F','C','G','F','C']
NOTES = {
    'C':  ('C3','E3','G3','C4','E4','G4','C5','E5'),
    'G':  ('G2','B3','D4','G4','B4','D5','G5','B5'),
    'Am': ('A2','C3','E3','A3','C4','E4','A4','C5'),
    'F':  ('F2','A2','C3','F3','A3','C4','F4','A4'),
}
ROOT = {'C':'C2','G':'G1','Am':'A1','F':'F1'}
ROOT3 = {'C':'C3','G':'G2','Am':'A2','F':'F2'}

def sec(b):
    if b < 8:   return 'intro'
    if b < 24:  return 'verse'
    if b < 40:  return 'verse2'
    return 'outro'

def ch(b):
    return chord_seq[b % 8]

lines = [f'# KEIC Beginner — 初学者曲目', f'name = "keic_easy"', f'bpm = {bpm}', '']

# KICK — 全程4/floor不变
kick = ['K:q:mf,R:q,K:q:mf,R:q' for _ in range(bars)]
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.70')
lines.append(f'notes = {",".join(kick)}\n')

# SNARE — 全程2&4
snare = []
for b in range(bars):
    if b < 4:
        snare.extend(['R:q']*4)
    else:
        snare.extend(['R:q','S:q:mp','R:q','S:q:mp'])
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.55')
lines.append(f'notes = {",".join(snare)}\n')

# HIHAT — 全程四分 (初学者只有四分!)
hihat = []
for b in range(bars):
    if b < 4:
        hihat.extend(['R:q']*4)
    else:
        hihat.extend(['H:q:pp']*4)  # quarters only!
lines.append('[track hihat]\ninstrument = drums\nmode = parallel\nvolume = 0.25')
lines.append(f'notes = {",".join(hihat)}\n')

# BASS — 全音符root, 全程
bass = []
for b in range(bars):
    bass.append(f'{ROOT[ch(b)]}:w:mp')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.65')
lines.append(f'notes = {",".join(bass)}\n')

# PIANO — 简单分解和弦, 每bar4拍
piano = []
for b in range(bars):
    s = sec(b)
    n = NOTES[ch(b)]
    r, t3, t5, o = n[0], n[1], n[2], n[3]
    if s == 'intro':
        p = f'{r}:h:pp,{o}:h:pp'  # sustained intro
    elif s == 'outro':
        p = f'{r}:w:pp'
    else:
        # simple root-5th-octave pattern, quarter notes only
        p = f'{r}:q:mp,{t5}:q:mp,{o}:q:mp,{t5}:q:mp'
    piano.extend(p.split(',') if isinstance(p, str) else p)
lines.append('[track piano]\ninstrument = piano\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(piano)}\n')

# PAD — 一层薄pad, 全程
pad = []
for b in range(bars):
    r = ROOT3[ch(b)]
    s = sec(b)
    v = 'pp' if s == 'intro' else 'mp'
    pad.append(f'{r}:w:{v}')
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.20\npan = 0.3')
lines.append(f'notes = {",".join(pad)}\n')

# LEAD — 简单motif, 1 octave范围内, 全八分以下
lead = []
for b in range(bars):
    s = sec(b)
    idx = b % 8
    if s == 'intro':
        lead.append('R:w')
    elif s == 'verse':
        if idx == 0: lead.append('C4:e:mp,D4:e:mp,E4:e:mp,G4:e:mp,A4:e:mp,G4:e:mp,E4:e:mp,D4:e:mp')
        elif idx == 1: lead.append('C4:e:mp,D4:e:mp,E4:e:mp,G4:e:mp,C5:e:mp,G4:e:mp,E4:e:mp,C4:e:mp')
        elif idx == 2: lead.append('G4:e:mp,B4:e:mp,D5:e:mp,G5:e:mp,D5:e:mp,B4:e:mp,G4:e:mp,R:e')
        elif idx == 3: lead.append('F4:e:mp,A4:e:mp,C5:e:mp,F5:e:mp,C5:e:mp,A4:e:mp,F4:e:mp,R:e')
        elif idx == 4: lead.append('C4:e:mp,E4:e:mp,G4:e:mp,C5:e:mp,G4:e:mp,E4:e:mp,C4:e:mp,E4:e:mp')
        elif idx == 5: lead.append('G4:e:mp,B4:e:mp,D5:e:mp,G5:e:mp,D5:e:mp,B4:e:mp,G4:e:mp,B4:e:mp')
        elif idx == 6: lead.append('F4:e:mp,A4:e:mp,C5:e:mp,F5:e:mp,C5:e:mp,A4:e:mp,F4:e:mp,A4:e:mp')
        else: lead.append('C4:e:mp,E4:e:mp,G4:e:mp,C5:e:mp,G4:e:mp,E4:e:mp,C4:e:mp,R:e')
    elif s == 'verse2':
        # same melody, higher octave for variation
        if idx == 0: lead.append('C5:e:mp,D5:e:mp,E5:e:mp,G5:e:mp,A5:e:mp,G5:e:mp,E5:e:mp,D5:e:mp')
        elif idx == 1: lead.append('C5:e:mp,D5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp')
        elif idx == 2: lead.append('G4:e:mp,B4:e:mp,D5:e:mp,G5:e:mp,D5:e:mp,B4:e:mp,G4:e:mp,R:e')
        elif idx == 3: lead.append('F4:e:mp,A4:e:mp,C5:e:mp,F5:e:mp,C5:e:mp,A4:e:mp,F4:e:mp,R:e')
        elif idx == 4: lead.append('C5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp,E5:e:mp')
        elif idx == 5: lead.append('G4:e:mp,B4:e:mp,D5:e:mp,G5:e:mp,D5:e:mp,B4:e:mp,G4:e:mp,B4:e:mp')
        elif idx == 6: lead.append('F4:e:mp,A4:e:mp,C5:e:mp,F5:e:mp,C5:e:mp,A4:e:mp,F4:e:mp,A4:e:mp')
        else: lead.append('C5:e:mp,E5:e:mp,G5:e:mp,C6:e:mp,G5:e:mp,E5:e:mp,C5:e:mp,R:e')
    else:
        if b < 44:
            lead.append('C4:e:pp,G3:e:pp,E3:e:pp,C3:e:pp,R:e,R:e,R:e,R:e')
        else:
            lead.append('R:w')

lines.append('[track lead]\ninstrument = sawtooth\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(lead)}')

with open('samples/keic_easy.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/keic_easy.acml ({bars} bars, {bpm} BPM, {bars*4*60/bpm:.0f}s)')
