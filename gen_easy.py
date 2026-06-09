# gen_easy.py — KEIC Beginner关卡 (Lv1-3)
# A小调, 重复音+琶音, 完全不同于tutorial的级进五声
# 110 BPM 48bars=105s, 4层, ~2 nps
# 音域: A3-A4 = 12st

bars = 48; bpm = 110

NOTES = {'Am':('A1','C2','E2','A2','C3','E3','A3','C4','E4','A4'),
         'F': ('F1','A1','C2','F2','A2','C3','F3','A3','C4','F4'),
         'C': ('C2','E2','G2','C3','E3','G3','C4','E4','G4','C5'),
         'G': ('G1','B1','D2','G2','B2','D3','G3','B3','D4','G4')}
ROOT = {'Am':'A1','F':'F1','C':'C1','G':'G1'}

chords = []
for _ in range(12): chords.extend(['Am','F','C','G'])

lines = ['# gen_easy', 'name = "easy"', f'bpm = {bpm}', '']

# PAD
pad = [f'{NOTES[chords[b]][6]}:w:{"pp" if b<16 or b>=40 else "mp"}' for b in range(bars)]
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.30')
lines.append(f'notes = {",".join(pad)}\n')

# KICK
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(["K:q:mp"]*(bars*4))}\n')

# BASS
bass = []
for b in range(bars):
    if b < 16: bass.append('R:w')
    else: bass.append(f'{ROOT[chords[b]]}:h:{"pp" if b>=40 else "mp"},{ROOT[chords[b]]}:h:{"pp" if b>=40 else "mp"}')
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join([x for g in bass for x in g.split(",")])}\n')

# LEAD — 重复音动机 (0-15) / 8八分 (16-39) / fade (40-47)
lead = []
for b in range(bars):
    if b < 16: lead.append('R:q,R:q,R:q,R:q'); continue
    ch = chords[b]; vol = 'pp' if b>=40 else ('mf' if 28<=b<36 else 'mp')

    if b < 24:  # 重复音 8八分
        p = {'Am':('A4','E4'),'F':('A4','C4'),'C':('G4','E4'),'G':('G4','B3')}[ch]
        lead.append((f'{p[0]}:e:{vol},{p[1]}:e:{vol},'*4)[:-1])  # 8 notes
    elif b < 32:  # 琶音 8八分
        p = {'Am':('A4','G4','E4','C4'),'F':('A4','G4','F4','C4'),
             'C':('G4','E4','C4','E4'),'G':('G4','D4','B3','D4')}[ch]
        lead.append((f'{p[0]}:e:{vol},{p[1]}:e:{vol},{p[2]}:e:{vol},{p[3]}:e:{vol},'*2)[:-1])
    elif b < 40:  # 回落 8八分/bar
        p = {'Am':('A4','E4','A4','C4'),'F':('A4','C4','F4','A4'),
             'C':('G4','E4','G4','C4'),'G':('G4','B3','D4','G4')}[ch]
        lead.append((f'{p[0]}:e:{vol},{p[1]}:e:{vol},{p[2]}:e:{vol},{p[3]}:e:{vol},'*2)[:-1])
    else:  # fade
        if b == 40: lead.append('A4:h:pp,R:q,R:q')
        elif b == 41: lead.append('E4:h:pp,R:q,R:q')
        elif b == 42: lead.append('A4:e:pp,E4:e:pp,R:q,R:q')
        elif b == 43: lead.append('R:w')
        elif b == 44: lead.append('C4:h:pp,R:q,R:q')
        elif b == 45: lead.append('R:w')
        elif b == 46: lead.append('A3:h:pp,R:q,R:q')
        else: lead.append('R:w')

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = piano\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(lead_flat)}\n')

with open(r'D:\PYTHON\ACM\cli_composer\samples\easy.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

total = sum(1 for g in lead_flat if g and g[0] not in ('R',''))
dur = bars * 4 * 60 / bpm
print(f'easy.acml: {dur:.0f}s, lead={total} notes = {total/dur:.1f} nps')

nn = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}; ps = []
for n in lead_flat:
    c = n.strip()
    if not c or c[0] in ('R','K','S','H','C','O'): continue
    p = c.split(':')[0]
    try:
        if len(p) == 2: ps.append(int(p[1])*12+nn[p[0]]+12)
        elif len(p)==3: ps.append(int(p[2])*12+nn[p[0]]+12-(1 if p[1]=='b' else 0))
    except: pass
r = max(ps)-min(ps)
print(f'Range: {min(ps)}-{max(ps)} = {r} st {"PASS" if r<=12 else "FAIL"}')

# Section breakdown
print(f'Phases: intro 0-15 | rep 16-23 | arp 24-31 | ret 32-39 | fade 40-47')
