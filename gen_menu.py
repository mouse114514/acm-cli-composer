# gen_menu.py — KEIC 主菜单BGM
# 洗脑循环曲: 16bars, 110BPM, C大调, 3层
# 核心hook: C4→G4→C5→E5 四度+三度跳进, 强记忆点
# 循环设计: bar15结束在F和弦(IV), bar0开始C和弦(I) → IV-I自然过渡

bars = 16; bpm = 110

NOTES = {'C':('C2','E2','G2','C3','E3','G3','C4','E4','G4','C5','E5','G5'),
         'G':('G1','B1','D2','G2','B2','D3','G3','B3','D4','G4','B4','D5'),
         'Am':('A1','C2','E2','A2','C3','E3','A3','C4','E4','A4','C5','E5'),
         'F':('F1','A1','C2','F2','A2','C3','F3','A3','C4','F4','A4','C5')}
ROOT = {'C':'C1','G':'G1','Am':'A1','F':'F1'}

# I-V-vi-IV, 每2小节换和弦
prog = []  # 16 bars
for _ in range(4):
    prog.extend(['C','C','G','G','Am','Am','F','F'])

lines = ['# KEIC 主菜单BGM — C大调洗脑循环', 'name = "menu"', f'bpm = {bpm}', '']

# PAD — 全音符, 温暖氛围
pad = []
for b in range(bars):
    ch = prog[b]; n = NOTES[ch]
    pad.append(f'{n[7]}:w:mp')  # E3/B3/C4/A3
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.28\npan = 0.2')
lines.append(f'notes = {",".join(pad)}\n')

# KICK — 极轻四地板 (只在1,3拍)
kick = []
for b in range(bars):
    kick.append('K:q:pp,R:q,K:q:pp,R:q')
kick_flat = [x for g in kick for x in g.split(',')]
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.20')
lines.append(f'notes = {",".join(kick_flat)}\n')

# BASS — 二分, 轻柔
bass = []
for b in range(bars):
    ch = prog[b]; r = ROOT[ch]
    bass.append(f'{r}:h:mp,{r}:h:mp')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join([x for g in bass for x in g.split(",")])}\n')

# LEAD — 洗脑hook
# Hook: C4-G4-C5-E5 (四度+三度跳进, 明亮)
# 每2小节: hook + 变奏
lead = []
for b in range(bars):
    ch = prog[b]; n = NOTES[ch]
    vol = 'mf' if b < 8 else 'mp'  # second half slightly softer for loop contrast

    if b % 8 < 2:  # C (bars 0,1,8,9) — 主hook
        if b % 2 == 0:
            lead.append(f'{n[6]}:q:{vol},{n[9]}:q:{vol},{n[10]}:q:{vol},{n[9]}:q:{vol}')  # C4 G4 C5 G4
        else:
            lead.append(f'{n[7]}:q:{vol},{n[9]}:q:{vol},{n[6]}:q:{vol},R:q')  # E4 G4 C4 R
    elif b % 8 < 4:  # G (bars 2,3,10,11) — hook转G
        if b % 2 == 0:
            lead.append(f'B3:q:{vol},D4:q:{vol},G4:q:{vol},D4:q:{vol}')
        else:
            lead.append(f'D4:q:{vol},G4:q:{vol},B3:q:{vol},R:q')
    elif b % 8 < 6:  # Am (bars 4,5,12,13) — hook转Am
        if b % 2 == 0:
            lead.append(f'A3:q:{vol},C4:q:{vol},E4:q:{vol},C4:q:{vol}')
        else:
            lead.append(f'C4:q:{vol},E4:q:{vol},A3:q:{vol},R:q')
    else:  # F (bars 6,7,14,15) — hook转F, bar15设计为循环过渡
        if b % 2 == 0:
            lead.append(f'F3:q:{vol},A3:q:{vol},C4:q:{vol},A3:q:{vol}')
        else:
            if b == 7 or b == 15:  # 过渡到C: F→C, 用E4引导
                lead.append(f'E4:e:{vol},C4:e:{vol},G4:q:{vol},R:q,R:q')
            else:
                lead.append(f'A3:q:{vol},C4:q:{vol},F3:q:{vol},R:q')

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = piano\nmode = parallel\nvolume = 0.45\npan = -0.15')
lines.append(f'notes = {",".join(lead_flat)}\n')

# Write
with open(r'D:\PYTHON\ACM\cli_composer\samples\menu.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

dur = bars * 4 * 60 / bpm
total = sum(1 for g in lead_flat if g and g[0] not in ('R',''))
print(f'menu.acml: {bars} bars, {bpm} BPM, {dur:.0f}s/loop')
print(f'Lead: {total} notes = {total/dur:.1f} nps')
print(f'Layers: 4 (pad+kick+bass+lead)')
print(f'\nHook: C4 → G4 → C5 → G4 (上升四度+四度, 明亮洗脑)')

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
print(f'\nLoop design: bar15 (F) → bar0 (C) = IV-I 自然过渡')
