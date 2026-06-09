# gen_beginner_plus.py — Beginner+难度关卡
# 比easy(1.9nps)难一点, 但不过难
# D大调, I-vi-IV-V (D-Bm-G-A), 120BPM, 48bars=96s
# 5层: pad+kick+snare+bass+lead
# 旋律: 流动八分 (流れるような), 2.4-2.8 nps
# 音域: D4-D5 (62-74) = 12st
# 注: F#=Gb, C#=Db (ACML无#)

bars = 48; bpm = 120

NOTES = {'D': ('D2','Gb2','A2','D3','Gb3','A3','D4','Gb4','A4','D5'),
         'Bm':('B1','D2','Gb2','B2','D3','Gb3','B3','D4','Gb4','B4'),
         'G': ('G1','B1','D2','G2','B2','D3','G3','B3','D4','G4'),
         'A': ('A1','Db2','E2','A2','Db3','E3','A3','Db4','E4','A4')}
ROOT = {'D':'D1','Bm':'B1','G':'G1','A':'A1'}

# 2bar/和弦: D D Bm Bm G G A A = 8bars/cycle → 6 cycles = 48bars
prog = []
for _ in range(6):
    for ch, n in [('D',2),('Bm',2),('G',2),('A',2)]:
        prog.extend([ch]*n)

lines = ['# Beginner+ — D大调流动旋律', 'name = "beginner_plus"', f'bpm = {bpm}', '']

# PAD — 全音符, 全程
pad = []
for b in range(bars):
    ch = prog[b]; n = NOTES[ch]
    vol = 'pp' if b<8 or b>=40 else 'mp'
    pad.append(f'{n[6]}:w:{vol}')  # D4/B3/G3/A3
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.25')
lines.append(f'notes = {",".join(pad)}\n')

# KICK — 4/floor, bar 8+
kick = []
for b in range(bars):
    if b < 8:
        kick.append('R:q,R:q,R:q,R:q')
    else:
        kick.append('K:q:mp,K:q:mp,K:q:mp,K:q:mp')
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.40')
lines.append(f'notes = {",".join([x for g in kick for x in g.split(",")])}\n')

# SNARE — 2/4拍, bar 16+
snare = []
for b in range(bars):
    if b < 16:
        snare.append('R:q,R:q,R:q,R:q')
    else:
        snare.append('R:q,S:q:mp,R:q,S:q:mp')
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join([x for g in snare for x in g.split(",")])}\n')

# BASS — 二分
bass = []
for b in range(bars):
    ch = prog[b]; r = ROOT[ch]
    if b < 8:
        bass.append('R:w')
    else:
        bass.append(f'{r}:h:mp,{r}:h:mp') if b < 40 else bass.append(f'{r}:h:pp,{r}:h:pp')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join([x for g in bass for x in g.split(",")])}\n')

# LEAD — 流动八分, D4-D5, 2.5nps目标
lead = []
for b in range(bars):
    ch = prog[b]; n = NOTES[ch]
    vol = 'pp' if b>=40 else ('mf' if 24<=b<32 else 'mp')

    if b < 8:  # intro
        lead.append('R:q,R:q,R:q,R:q')
        continue

    # 每2个bar为一个乐句 (chord cycle)
    pos_in_cycle = b % 8  # 0-7, each chord gets 2 bars

    if pos_in_cycle < 2:  # D (2 bars)
        if pos_in_cycle == 0:
            lead.append(f'D4:e:{vol},Gb4:e:{vol},A4:e:{vol},D5:e:{vol},A4:e:{vol},Gb4:e:{vol},D4:e:{vol},R:e')
        else:  # bar 1 of D
            lead.append(f'E4:e:{vol},Gb4:e:{vol},A4:e:{vol},D5:e:{vol},A4:e:{vol},Gb4:e:{vol},E4:e:{vol},R:e')
    elif pos_in_cycle < 4:  # Bm (2 bars)
        if pos_in_cycle == 2:
            lead.append(f'B4:e:{vol},D4:e:{vol},Gb4:e:{vol},B4:e:{vol},Gb4:e:{vol},D4:e:{vol},B4:e:{vol},R:e')
        else:
            lead.append(f'D4:e:{vol},E4:e:{vol},Gb4:e:{vol},E4:e:{vol},D4:e:{vol},B4:e:{vol},R:e,R:e')
    elif pos_in_cycle < 6:  # G (2 bars)
        if pos_in_cycle == 4:
            lead.append(f'G4:e:{vol},B4:e:{vol},D4:e:{vol},G4:e:{vol},D4:e:{vol},B4:e:{vol},G4:e:{vol},R:e')
        else:
            lead.append(f'A4:e:{vol},B4:e:{vol},D5:e:{vol},G4:e:{vol},D4:e:{vol},B4:e:{vol},R:e,R:e')
    else:  # A (2 bars)
        if pos_in_cycle == 6:
            lead.append(f'A4:e:{vol},Gb4:e:{vol},E4:e:{vol},A4:e:{vol},E4:e:{vol},D4:e:{vol},A4:e:{vol},R:e')
        else:
            lead.append(f'B4:e:{vol},A4:e:{vol},Gb4:e:{vol},E4:e:{vol},D4:e:{vol},E4:e:{vol},A4:e:{vol},R:e')

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = piano\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(lead_flat)}\n')

with open(r'D:\PYTHON\ACM\cli_composer\samples\beginner_plus.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

dur = bars * 4 * 60 / bpm
total = sum(1 for g in lead_flat if g and g[0] not in ('R',''))
nps = total / dur
print(f'beginner_plus.acml: {bars} bars, {bpm} BPM, {dur:.0f}s ({dur/60:.1f}m)')
print(f'Lead: {total} notes = {nps:.1f} nps (target: 2.5)')

nn = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
note_names_rev = {v:k for k,v in nn.items()}
ps = []
for c in lead_flat:
    c = c.strip()
    if not c or c[0] in ('R','K','S','H'): continue
    p = c.split(':')[0]
    try:
        if len(p)==2: ps.append(int(p[1])*12+nn[p[0]]+12)
        elif len(p)==3:
            octave = int(p[2])
            if p[1]=='b': ps.append(octave*12+nn[p[0]]+12-1)
            elif p[1]=='#': ps.append(octave*12+nn[p[0]]+12+1)
            else: ps.append(octave*12+nn[p[0]]+12)
    except: pass
if ps:
    mn, mx = min(ps), max(ps)
    r = mx-mn
    print(f'Range: {mn}-{mx} = {r} st {"PASS" if r<=12 else "FAIL"}')
    # Print note names
    names = [f'{note_names_rev[(p-12)%12]}{p//12-1}' for p in [mn, mx]]
    print(f'  Lowest: {names[0]}({mn}), Highest: {names[1]}({mx})')

layers = ['pad','kick','snare','bass','lead']
print(f'Layers: {len(layers)} ({", ".join(layers)})')
print(f'Progression: D - Bm - G - A (I-vi-IV-V in D major)')
print(f'Drums: kick bar8+, snare bar16+ — builds gradually')
