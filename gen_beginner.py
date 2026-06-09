# gen_beginner.py — KEIC Beginner关卡 (Lv2-3)
# 比gen_easy难一点点: 加军鼓2/4拍, 更高密度, 更多变奏
# D小调 (1个降号Bb), i-VII-VI-VII 进行
# 115 BPM, 48bars → 100s, 5层
# 完全新旋律: 下行级进+四度跳混合, 4小节乐句

bars = 48; bpm = 115

NOTES = {'Dm':('D2','F2','A2','D3','F3','A3','D4','F4','A4','D5','F5','A5'),
         'C': ('C2','E2','G2','C3','E3','G3','C4','E4','G4','C5','E5','G5'),
         'Bb':('Bb1','D2','F2','Bb2','D3','F3','Bb3','D4','F4','Bb4','D5','F5'),
         'Am':('A1','C2','E2','A2','C3','E3','A3','C4','E4','A4','C5','E5')}
ROOT = {'Dm':'D1','C':'C1','Bb':'Bb1','Am':'A1'}
CH = {'Dm':'Dm','C':'C','Bb':'Bb','Am':'Am'}

# 4小节一循环: Dm-C-Bb-C (i-VII-VI-VII)
# 12循环 = 48 bars
prog = []
for _ in range(12):
    prog.extend(['Dm','C','Bb','C'])

lines = ['# gen_beginner — D小调, 下行级进+四度跳, 5层', 'name = "beginner"', f'bpm = {bpm}', '']

# PAD
pad = []
for b in range(bars):
    ch = prog[b]; vol = 'pp' if b<16 or b>=40 else 'mp'
    pad.append(f'{NOTES[ch][6]}:w:{vol}')  # octave 3
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.25')
lines.append(f'notes = {",".join(pad)}\n')

# KICK — 4/floor
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(["K:q:mp"]*(bars*4))}\n')

# SNARE — 2/4 backbeat (这是比gen_easy多的一层)
snare = []
for b in range(bars):
    if b < 16:
        snare.append('R:q,R:q,R:q,R:q')
    else:
        snare.append('R:q,S:q:mp,R:q,S:q:mp')
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join([x for g in snare for x in g.split(",")])}\n')

# BASS
bass = []
for b in range(bars):
    ch = prog[b]; r = ROOT[ch]
    if b < 16:
        bass.append('R:w')
    else:
        vol = 'pp' if b>=40 else 'mp'
        bass.append(f'{r}:h:{vol},{r}:h:{vol}')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join([x for g in bass for x in g.split(",")])}\n')

# LEAD — 下行级进+四度跳, 2-2.5 nps
# 每4小节一个乐句, Dm-C-Bb-C循环
lead = []
for b in range(bars):
    ch = prog[b]; n = NOTES[ch]; vol = 'pp' if b>=40 else ('mf' if 24<=b<40 else 'mp')

    if b < 16:  # intro silence
        lead.append('R:q,R:q,R:q,R:q'); continue

    cycle = (b - 16) // 4  # 0-7 (32 bars active / 4 = 8 cycles)
    pos_in_cycle = (b - 16) % 4  # 0=Dm, 1=C, 2=Bb, 3=C

    if cycle < 4:  # Phase 1 (16-31): 八分下行级进, 8音/bar
        motifs = {
            'Dm': f'A4:e:{vol},G4:e:{vol},F4:e:{vol},E4:e:{vol},D4:e:{vol},E4:e:{vol},F4:e:{vol},G4:e:{vol}',
            'C':  f'G4:e:{vol},F4:e:{vol},E4:e:{vol},D4:e:{vol},C4:e:{vol},D4:e:{vol},E4:e:{vol},F4:e:{vol}',
            'Bb': f'F4:e:{vol},E4:e:{vol},D4:e:{vol},C4:e:{vol},Bb3:e:{vol},C4:e:{vol},D4:e:{vol},E4:e:{vol}',
        }
        lead.append(motifs[ch])

    elif cycle < 6:  # Phase 2 (32-39): 上行返回, 8音/bar
        motifs2 = {
            'Dm': f'D4:e:{vol},F4:e:{vol},A4:e:{vol},D5:e:{vol},A4:e:{vol},F4:e:{vol},D4:e:{vol},R:e',
            'C':  f'C4:e:{vol},E4:e:{vol},G4:e:{vol},C5:e:{vol},G4:e:{vol},E4:e:{vol},C4:e:{vol},R:e',
            'Bb': f'Bb3:e:{vol},D4:e:{vol},F4:e:{vol},Bb4:e:{vol},F4:e:{vol},D4:e:{vol},Bb3:e:{vol},R:e',
        }
        if ch == 'C' and pos_in_cycle == 3:  # C特殊: 回Dm过渡
            lead.append(f'C5:e:{vol},D5:e:{vol},E5:e:{vol},F5:e:{vol},E5:e:{vol},D5:e:{vol},C5:e:{vol},R:e')
        else:
            lead.append(motifs2[ch])

    else:  # Phase 3 (40-47): fade
        if pos_in_cycle == 0:
            lead.append(f'D5:q:{vol},A4:e:{vol},R:e,R:q,R:q')
        elif pos_in_cycle == 1:
            lead.append(f'C5:q:{vol},G4:e:{vol},R:e,R:q,R:q')
        elif pos_in_cycle == 2:
            lead.append(f'Bb4:q:{vol},F4:e:{vol},R:e,R:q,R:q')
        else:
            lead.append(f'C5:q:{vol},G4:e:{vol},R:e,R:q,R:q')

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = piano\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(lead_flat)}\n')

with open(r'D:\PYTHON\ACM\cli_composer\samples\beginner.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

dur = bars * 4 * 60 / bpm
total = sum(1 for g in lead_flat if g and g[0] not in ('R',''))
nps = total / dur
print(f'beginner.acml: {bars} bars, {bpm} BPM, {dur:.0f}s ({dur/60:.1f}m)')
print(f'Lead: {total} notes = {nps:.1f} nps')
print(f'Layers: 5 (pad+kick+snare+bass+lead)')
print(f'Progression: Dm-C-Bb-C (i-VII-VI-VII)')

nn = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}; ps = []
for n in lead_flat:
    c = n.strip()
    if not c or c[0] in ('R','K','S','H'): continue
    p = c.split(':')[0]
    try:
        if len(p)==2: ps.append(int(p[1])*12+nn[p[0]]+12)
        elif len(p)==3: ps.append(int(p[2])*12+nn[p[0]]+12-(1 if p[1]=='b' else 0))
    except: pass
print(f'Range: {min(ps)}-{max(ps)} = {max(ps)-min(ps)} st')

print(f'\n对比 gen_easy:')
print(f'  BPM: 110→115 (+5)')
print(f'  层数: 4→5 (+snare)')
print(f'  密度: 1.9→{nps:.1f} nps')
print(f'  时长: 105→{dur:.0f}s')
print(f'  调性: Am→Dm (加Bb)')
