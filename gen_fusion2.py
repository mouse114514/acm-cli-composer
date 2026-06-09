# Fusion v2 — 手工作曲，motif驱动
# 修复v1: 单调、机械重复、无旋律感、和弦太快
# Key: Cm | 128 BPM | 32 bars | 10 tracks

bars = 32
bpm = 128

# 8-bar loop: 慢和弦节奏 (每个和弦2bar)
chord_seq = ['Cm','Cm','Ab','Bb','Eb','Eb','Bb','G']
two_beat  = [True, True, True, True, True, True, True, True]

def sec_of(b):
    if b < 4:    return 'intro'
    if b < 8:    return 'verse'
    if b < 12:   return 'prechorus'
    if b < 20:   return 'chorus'
    if b < 24:   return 'break'
    if b < 28:   return 'outro'
    return 'silence'

def ch_of(b):
    return chord_seq[b % 8]

# 音高映射（全flat/natural，无#）
ROOT = {'Cm':'C2','Ab':'Ab1','Bb':'Bb1','Eb':'Eb2','G':'G1'}
ROOT3 = {'Cm':'C3','Ab':'Ab2','Bb':'Bb2','Eb':'Eb3','G':'G2'}
NOTES = {
    'Cm': ('C3','Eb3','G3','C4','Eb4','G4','C5','Eb5'),
    'Ab': ('Ab2','C3','Eb3','Ab3','C4','Eb4','Ab4','C5'),
    'Bb': ('Bb2','D3','F3','Bb3','D4','F4','Bb4','D5'),
    'Eb': ('Eb2','G3','Bb3','Eb4','G4','Bb4','Eb5','G5'),
    'G':  ('G2','B3','D4','G4','B4','D5','G5','B5'),
}

lines = []
lines.append('# Fusion v2 — melody-driven arrangement')
lines.append(f'name = "fusion2"')
lines.append(f'bpm = {bpm}')
lines.append('')

# ════════ DRUMS ════════
kick = []
for b in range(bars):
    sec = sec_of(b)
    if sec in ('intro','break','outro','silence'):
        kick.extend(['R:q']*4)
    elif sec == 'verse':
        kick.extend(['K:q:mp','R:q','K:q:pp','R:q'])
    elif sec == 'prechorus':
        kick.extend(['K:q:mf','R:q','K:q:mf','R:q'])
    else:  # chorus
        if b % 2 == 0:
            kick.extend(['K:q:mf','K:e:mp','R:e','K:q:mf','R:q'])
        else:
            kick.extend(['K:q:mf','R:q','K:e:mp','K:e:mp','R:q'])
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.70')
lines.append(f'notes = {",".join(kick)}\n')

snare = []
for b in range(bars):
    sec = sec_of(b)
    if sec in ('intro','outro','silence','break'):
        snare.extend(['R:q']*4)
    elif sec == 'verse':
        snare.extend(['R:q','S:q:pp','R:q','S:q:pp'])
    elif sec == 'prechorus':
        snare.extend(['S:e:pp','R:e','S:e:mp','R:e']*2)
    else:
        snare.extend(['R:q','S:q:mf','R:q','S:q:mf'])
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.55')
lines.append(f'notes = {",".join(snare)}\n')

hihat = []
for b in range(bars):
    sec = sec_of(b)
    if sec in ('intro','outro','silence','break'):
        hihat.extend(['R:e']*8)
    elif sec == 'verse':
        hihat.extend(['H:e:pp']*8)
    elif sec == 'prechorus':
        hihat.extend(['H:e:mp','H:e:pp']*4)
    else:
        hihat.extend(['H:s:mf']*16)
lines.append('[track hihat]\ninstrument = drums\nmode = parallel\nvolume = 0.25')
lines.append(f'notes = {",".join(hihat)}\n')

# ════════ BASS (whole note, root) ════════
bass = []
for b in range(bars):
    sec = sec_of(b)
    r = ROOT[ch_of(b)]
    if sec == 'silence':
        bass.append('R:w')
    elif sec in ('intro','verse','break'):
        bass.append(f'{r}:w:pp')
    elif sec == 'prechorus':
        bass.append(f'{r}:w:mp')
    else:
        bass.append(f'{r}:w:mf')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.65')
lines.append(f'notes = {",".join(bass)}\n')

# ════════ PIANO (4 patterns, section-dependent) ════════
piano = []
for b in range(bars):
    n = NOTES[ch_of(b)]
    r, t3, t5, o, t3h, t5h, o2, t3hh = n
    sec = sec_of(b)

    if sec == 'intro':
        p = f'{r}:h:pp,{o}:q:pp,{o2}:q:pp'
    elif sec in ('verse','break'):
        if b % 2 == 0:
            p = f'{r}:q:mp,{t5}:e:mp,{t3h}:e:mp,{o}:q:mp,{o}:e:mp,{t5h}:e:mp'
        else:
            p = f'{o}:q:mp,{t5h}:e:mp,{t3hh}:e:mp,{o2}:q:mp,{t5h}:e:mp,{o2}:e:mp'
    elif sec == 'prechorus':
        p = f'{r}:e:mf,{t3}:e:mf,{t5}:e:mf,{o}:e:mf,{t3h}:e:mf,{t5h}:e:mf,{o2}:e:mf,{t3hh}:e:mf'
    elif sec == 'chorus':
        p = f'{r}:q:mf,{t3}:e:mf,{o}:e:mf,{o2}:q:mf,R:q'
    else:  # outro/silence
        p = f'{r}:h:pp,{o}:h:pp'

    piano.extend(p.split(','))

lines.append('[track piano]\ninstrument = piano\nmode = parallel\nvolume = 0.55\npan = -0.3')
lines.append(f'notes = {",".join(piano)}\n')

# ════════ PAD ════════
pad = []
for b in range(bars):
    r = ROOT3[ch_of(b)]
    sec = sec_of(b)
    if sec == 'silence':
        pad.append('R:w')
    else:
        vol = {'intro':'pp','verse':'pp','prechorus':'mp','chorus':'mf','break':'pp','outro':'pp'}.get(sec,'pp')
        pad.append(f'{r}:w:{vol}')
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.25\npan = 0.4')
lines.append(f'notes = {",".join(pad)}\n')

# ════════ STRING DRONE (always on, AW厚度) ════════
drone = []
for b in range(bars):
    r = ROOT[ch_of(b)]
    sec = sec_of(b)
    if sec == 'silence':
        drone.append('R:w')
    else:
        drone.append(f'{r}:w:pp')
lines.append('[track drone]\ninstrument = string\nmode = parallel\nvolume = 0.18\npan = 0.3')
lines.append(f'notes = {",".join(drone)}\n')

# ════════ LEAD (motif-based composed melody) ════════
# Motif: C5-Eb5-G5-Ab5-G5 (rising leap, half-step resolution)
# Developed across sections
lead = []
for b in range(bars):
    sec = sec_of(b)
    idx = b % 8

    if sec == 'silence':
        lead.append('R:w')
    elif sec == 'intro':
        lead.append('R:w')
    elif sec == 'verse':
        if idx == 0:
            lead.append('G4:e:pp,Eb4:e:pp,C4:e:pp,R:e,G4:e:pp,Eb4:e:pp,C4:e:pp,R:e')
        elif idx == 1:
            lead.append('Bb4:e:pp,G4:e:pp,F4:e:pp,Eb4:e:pp,C5:e:pp,G4:e:pp,Eb4:e:pp,C4:e:pp')
        elif idx == 2:
            lead.append('R:w')
        elif idx == 3:
            lead.append('G4:e:mp,Eb4:e:mp,Bb4:e:mp,G4:e:mp,F4:e:mp,D4:e:mp,R:e,R:e')
        elif idx in (4,5):
            lead.append('R:w')
        elif idx == 6:
            lead.append('Bb4:e:pp,G4:e:pp,Eb5:e:pp,C5:e:pp,Bb4:e:pp,G4:e:pp,Eb4:e:pp,C4:e:pp')
        else:
            lead.append('R:w')
    elif sec == 'prechorus':
        if idx % 2 == 0:
            lead.append('Eb5:e:mp,G5:e:mp,Bb5:e:mp,C6:e:mp,Bb5:e:mp,G5:e:mp,Eb5:e:mp,C5:e:mp')
        else:
            lead.append('D5:e:mp,F5:e:mp,Ab5:e:mp,Bb5:e:mp,Ab5:e:mp,F5:e:mp,D5:e:mp,R:e')
    elif sec == 'chorus':
        if idx == 0:
            lead.append('C5:e:mf,G4:e:mf,Eb5:e:mf,G4:e:mf,C5:e:mf,Eb5:e:mf,G5:e:mf,Ab5:e:mf')
        elif idx == 1:
            lead.append('G5:e:mf,Eb5:e:mf,C5:e:mf,G4:e:mf,Eb5:e:mf,C5:e:mf,G4:e:mf,Eb4:e:mf')
        elif idx == 2:
            lead.append('Ab4:e:mf,C5:e:mf,Eb5:e:mf,G5:e:mf,C6:e:mf,G5:e:mf,Eb5:e:mf,C5:e:mf')
        elif idx == 3:
            lead.append('Bb4:e:mf,D5:e:mf,F5:e:mf,Ab5:e:mf,F5:e:mf,D5:e:mf,Bb4:e:mf,G4:e:mf')
        elif idx == 4:
            lead.append('Eb5:e:mf,G5:e:mf,Bb5:e:mf,Eb6:e:mf,Bb5:e:mf,G5:e:mf,Eb5:e:mf,Bb5:e:mf')
        elif idx == 5:
            lead.append('G5:e:mf,Eb5:e:mf,Bb4:e:mf,G4:e:mf,Eb5:e:mf,C5:e:mf,Bb4:e:mf,G4:e:mf')
        elif idx == 6:
            lead.append('Bb4:e:mf,D5:e:mf,F5:e:mf,G5:e:mf,F5:e:mf,D5:e:mf,Bb4:e:mf,G4:e:mf')
        else:
            lead.append('D5:e:ff,F5:e:ff,G5:e:ff,B5:e:ff,D6:e:ff,B5:e:ff,G5:e:ff,D5:e:mf')
    elif sec == 'break':
        lead.append('C5:e:pp,G4:e:pp,Eb4:e:pp,C4:e:pp,C5:e:pp,G4:e:pp,Eb4:e:pp,C4:e:pp')
    else:  # outro
        if b % 2 == 0:
            lead.append('C5:e:pp,G4:e:pp,Eb4:e:pp,C4:e:pp,R:e,R:e,R:e,R:e')
        else:
            lead.append('R:w')

lines.append('[track lead]\ninstrument = sawtooth\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(lead)}\n')

# ════════ ARP (sixteenth, only prechorus+chorus) ════════
arp = []
for b in range(bars):
    sec = sec_of(b)
    n = NOTES[ch_of(b)]
    p = n[:4] if b % 2 == 0 else tuple(reversed(n[:4]))
    if sec in ('prechorus','chorus'):
        group = ','.join([f'{x}:s:mp' for x in p])
        arp.extend([group]*4)
    else:
        arp.append(','.join(['R:s']*4))
arp_flat = [x for g in arp for x in g.split(',')]
lines.append('[track arp]\ninstrument = wavetable\nwavetable = square\nmode = parallel\nvolume = 0.20')
lines.append(f'notes = {",".join(arp_flat)}\n')

# ════════ CHORD STAB (Marshmello, chorus only) ════════
STAB_RTF = {
    'Cm': ('C3','Eb3','G3'), 'Ab': ('Ab2','C3','Eb3'),
    'Bb': ('Bb2','D3','F3'), 'Eb': ('Eb2','G3','Bb3'),
    'G':  ('G2','B3','D4'),
}
stab = []
for b in range(bars):
    sec = sec_of(b)
    r,t,f = STAB_RTF.get(ch_of(b), ('R','R','R'))
    if sec == 'chorus' and b % 2 == 0:
        stab.append(f'{r}:s:mf,{t}:s:mf,{f}:s:mf,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
    else:
        stab.append('R:s,'*16)
stab_flat = [x for g in stab for x in g.strip(',').split(',')]
lines.append('[track stab]\ninstrument = wavetable\nwavetable = sawtooth\nmode = parallel\nvolume = 0.30')
lines.append(f'notes = {",".join(stab_flat)}')

with open('samples/fusion2.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/fusion2.acml ({bars} bars, {bpm} BPM)')
