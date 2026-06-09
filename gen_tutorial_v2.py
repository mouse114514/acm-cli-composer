# gen_tutorial_v2.py — 真正的教学关卡 (教新手怎么玩)
# 16 bars, 100 BPM, 38s, 3层
# A小调, 四分音符only, 极稀疏, 问答结构
# 完全不同于之前的任何旋律/节奏

bars = 16; bpm = 100

NOTES = {'Am':('A2','C3','E3','A3','C4','E4','A4','C5','E5')}
ROOT = 'A1'

lines = ['# tut2 — 教学关卡', 'name = "tutorial_v2"', f'bpm = {bpm}', '']

# PAD — 全音符全程
pad = [f'{NOTES["Am"][3]}:w:mp' for _ in range(bars)]
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join(pad)}\n')

# KICK — 四分4/floor, 全程
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.40')
lines.append(f'notes = {",".join(["K:q:mp"]*(bars*4))}\n')

# BASS — 二分音符, 全程
bass_flat = [x for g in [f'{ROOT}:h:mp,{ROOT}:h:mp' for _ in range(bars)] for x in g.split(',')]
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(bass_flat)}\n')

# LEAD — 极简问答式旋律, 四分音符, A3-A4
# 前8bar无旋律 → 听到pad+bass+kick熟悉节奏
# 后8bar旋律: 2bar问+2bar答, 重复一次
lead = []
for b in range(bars):
    if b < 8:
        lead.append('R:q,R:q,R:q,R:q')
    elif b < 12:
        if b == 8:   # 问句上升
            lead.append('A4:q:mp,R:q,E4:q:mp,R:q')
        elif b == 9:
            lead.append('C4:q:mp,R:q,A4:q:mp,R:q')
        elif b == 10:
            lead.append('E4:q:mp,R:q,C4:q:mp,R:q')
        else:  # b==11
            lead.append('A4:q:mp,R:q,E4:q:mp,R:q')
    else:
        if b == 12:  # 答句下降
            lead.append('E4:q:mp,A4:q:mp,R:q,R:q')
        elif b == 13:
            lead.append('C4:q:mp,E4:q:mp,R:q,R:q')
        elif b == 14:
            lead.append('A3:q:mp,C4:q:mp,R:q,R:q')
        else:  # b==15
            lead.append('E4:q:mp,A4:q:mp,R:q,R:q')

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = piano\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(lead_flat)}\n')

with open(r'D:\PYTHON\ACM\cli_composer\samples\tutorial_v2.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

dur = bars * 4 * 60 / bpm
total = sum(1 for g in lead_flat if g and g[0] not in ('R',''))
print(f'tutorial_v2.acml: {bars} bars, {bpm} BPM, {dur:.0f}s ({dur/60:.1f}m)')
print(f'Lead: {total} notes = {total/dur:.1f} nps')

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
print('\nStructure:')
print('  Bars 0-7:  Intro (pad+kick+bass) — learn the beat')
print('  Bars 8-11: Question phrase (ascending) — hit on beat')
print('  Bars 12-15: Answer phrase (descending) — resolve')
