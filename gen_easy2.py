# gen_easy2.py — KEIC Beginner Lv2 (略难于easy)
# G大调, I-V-vi-IV (G-D-Em-C), 115 BPM
# 5层 (pad+kick+snare+bass+lead), ~2.2 nps
# 旋律: 跳进+级进混合 (不同于easy的重复音/琶音)
# 音域: D4-D5 (12st)
# 48bars × 4 × 60/115 = 100s

bars = 48; bpm = 115

NOTES = {'G': ('G1','B1','D2','G2','B2','D3','G3','B3','D4','G4','B4','D5'),
         'D': ('D2','F#2','A2','D3','F#3','A3','D4','F#4','A4','D5','F#5','A5'),
         'Em':('E2','G2','B2','E3','G3','B3','E4','G4','B4','E5','G5','B5'),
         'C': ('C2','E2','G2','C3','E3','G3','C4','E4','G4','C5','E5','G5')}
ROOT = {'G':'G1','D':'D1','Em':'E1','C':'C1'}

# I-V-vi-IV, 每2小节换
prog = []
for _ in range(6):
    prog.extend(['G','G','D','D','Em','Em','C','C'])

lines = ['# gen_easy2 — G大调, 略难于easy', 'name = "easy2"', f'bpm = {bpm}', '']

# PAD — 全音符
pad = []
for b in range(bars):
    ch = prog[b]; n = NOTES[ch]
    vol = 'pp' if b<16 or b>=40 else 'mp'
    pad.append(f'{n[7]}:w:{vol}')
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.28')
lines.append(f'notes = {",".join(pad)}\n')

# KICK — 4/floor
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.40')
lines.append(f'notes = {",".join(["K:q:mp"]*(bars*4))}\n')

# SNARE — 2/4拍 (新增! easy没有snare)
snare = []
for b in range(bars):
    if b < 16: snare.append('R:q,R:q,R:q,R:q')
    else: snare.append('R:q,S:q:mp,R:q,S:q:mp')
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.30')
lines.append(f'notes = {",".join([x for g in snare for x in g.split(",")])}\n')

# BASS — 二分
bass = []
for b in range(bars):
    ch = prog[b]; r = ROOT[ch]
    if b < 16: bass.append('R:w')
    else: bass.append(f'{r}:h:mp,{r}:h:mp' if b<40 else f'{r}:h:pp,{r}:h:pp')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join([x for g in bass for x in g.split(",")])}\n')

# LEAD — 跳进+级进混合, 八分+四分下拍
# 4段: intro(0-15) / entry(16-27) / active(28-39) / fade(40-47)
lead = []
for b in range(bars):
    if b < 16:
        lead.append('R:q,R:q,R:q,R:q'); continue

    ch = prog[b]; vol = 'pp' if b>=40 else ('mf' if 28<=b<40 else 'mp')
    s8 = f':e:{vol}'  # eighth note suffix
    s4 = f':q:{vol}'  # quarter note suffix

    # Phase 1 (16-27): 跳进动机, 每bar 8音
    if b < 28:
        if ch == 'G':
            if b % 4 == 0: lead.append(f'B4{s8},G4{s8},D4{s8},G4{s8},B4{s8},G4{s8},D4{s8},G4{s8}')
            else: lead.append(f'G4{s8},D4{s8},B4{s8},D4{s8},G4{s8},D4{s8},B4{s8},R{s8}')
        elif ch == 'D':
            if b % 4 == 0: lead.append(f'F#4{s8},D4{s8},A4{s8},D4{s8},F#4{s8},D4{s8},A4{s8},D4{s8}')
            else: lead.append(f'D4{s8},A4{s8},F#4{s8},A4{s8},D4{s8},A4{s8},F#4{s8},R{s8}')
        elif ch == 'Em':
            if b % 4 == 0: lead.append(f'G4{s8},E4{s8},B4{s8},E4{s8},G4{s8},E4{s8},B4{s8},E4{s8}')
            else: lead.append(f'E4{s8},B4{s8},G4{s8},B4{s8},E4{s8},B4{s8},G4{s8},R{s8}')
        else:  # C
            if b % 4 == 0: lead.append(f'E4{s8},C4{s8},G4{s8},C4{s8},E4{s8},C4{s8},G4{s8},C4{s8}')
            else: lead.append(f'C4{s8},G4{s8},E4{s8},G4{s8},C4{s8},G4{s8},E4{s8},R{s8}')

    # Phase 2 (28-39): 更密, 8音/bar, 级进
    elif b < 40:
        if ch == 'G':
            if b % 4 == 0: lead.append(f'B4{s8},G4{s8},D4{s8},G4{s8},B4{s8},G4{s8},D4{s8},G4{s8}')
            elif b % 4 == 1: lead.append(f'G4{s8},A4{s8},B4{s8},A4{s8},G4{s8},D4{s8},G4{s8},B4{s8}')
            elif b % 4 == 2: lead.append(f'B4{s8},A4{s8},G4{s8},A4{s8},B4{s8},G4{s8},D4{s8},G4{s8}')
            else: lead.append(f'G4{s8},B4{s8},D5{s8},B4{s8},G4{s8},D4{s8},B4{s8},D5{s8}')  # 8 notes
        elif ch == 'D':
            if b % 4 == 0: lead.append(f'F#4{s8},D4{s8},A4{s8},D4{s8},F#4{s8},D4{s8},A4{s8},D4{s8}')
            elif b % 4 == 1: lead.append(f'D4{s8},E4{s8},F#4{s8},E4{s8},D4{s8},A4{s8},D4{s8},F#4{s8}')
            elif b % 4 == 2: lead.append(f'F#4{s8},E4{s8},D4{s8},E4{s8},F#4{s8},D4{s8},A4{s8},D4{s8}')
            else: lead.append(f'D4{s8},F#4{s8},A4{s8},F#4{s8},D4{s8},A4{s8},D4{s8},F#4{s8}')  # 8 notes
        elif ch == 'Em':
            if b % 4 == 0: lead.append(f'B4{s8},G4{s8},E4{s8},G4{s8},B4{s8},G4{s8},E4{s8},G4{s8}')
            elif b % 4 == 1: lead.append(f'E4{s8},F#4{s8},G4{s8},F#4{s8},E4{s8},B4{s8},E4{s8},G4{s8}')
            elif b % 4 == 2: lead.append(f'B4{s8},G4{s8},E4{s8},G4{s8},B4{s8},G4{s8},E4{s8},G4{s8}')
            else: lead.append(f'E4{s8},G4{s8},B4{s8},G4{s8},E4{s8},B4{s8},E4{s8},G4{s8}')
        else:  # C
            if b % 4 == 0: lead.append(f'G4{s8},E4{s8},C4{s8},E4{s8},G4{s8},E4{s8},C4{s8},E4{s8}')
            elif b % 4 == 1: lead.append(f'C4{s8},D4{s8},E4{s8},D4{s8},C4{s8},G4{s8},C4{s8},E4{s8}')
            elif b % 4 == 2: lead.append(f'G4{s8},E4{s8},C4{s8},E4{s8},G4{s8},E4{s8},C4{s8},E4{s8}')
            else: lead.append(f'E4{s8},G4{s8},C5{s8},G4{s8},E4{s8},C4{s8},E4{s8},C5{s8}')

    else:  # Phase 3 (40-47): fade
        if b == 40: lead.append('G4:q:pp,B4:q:pp,R:q,R:q')
        elif b == 41: lead.append('D4:q:pp,G4:q:pp,R:q,R:q')
        elif b == 42: lead.append('B4:q:pp,D4:q:pp,R:q,R:q')
        elif b == 43: lead.append('R:w')
        elif b == 44: lead.append('G4:q:pp,B4:q:pp,R:q,R:q')
        elif b == 45: lead.append('E4:q:pp,G4:q:pp,R:q,R:q')
        elif b == 46: lead.append('R:w')
        else: lead.append('G4:q:pp,R:q,R:q,R:q')

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = piano\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(lead_flat)}\n')

with open(r'D:\PYTHON\ACM\cli_composer\samples\easy2.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

dur = bars * 4 * 60 / bpm
total = sum(1 for g in lead_flat if g and g[0] not in ('R',''))
print(f'easy2.acml: {bars} bars, {bpm} BPM, {dur:.0f}s')
print(f'Lead: {total} notes = {total/dur:.1f} nps')
print(f'Layers: 5 (pad+kick+snare+bass+lead) — easy只有4层')

nn = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}; ps = []
for n in lead_flat:
    c = n.strip()
    if not c or c[0] in ('R','K','S','H'): continue
    p = c.split(':')[0]
    try:
        if len(p)==2: ps.append(int(p[1])*12+nn[p[0]]+12)
        elif len(p)==3: ps.append(int(p[2])*12+nn[p[0]]+12-(1 if p[1]=='b' else 0))
    except: pass
r = max(ps)-min(ps)
print(f'Range: {min(ps)}-{max(ps)} = {r} st')
print()
# Compare with easy
print('=== 与 easy 对比 ===')
print(f'easy:   110 BPM, 105s, 4层, 1.9 nps, Am, 重复音琶音')
print(f'easy2:  115 BPM, {dur:.0f}s, 5层(+snare!), {total/dur:.1f} nps, G, 跳进+级进')
