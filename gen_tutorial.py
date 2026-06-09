# gen_tutorial.py — 新手教学关卡音乐
# 设计原则:
#   - C大调, 120 BPM, 48 bars (1:36)
#   - I-V-vi-IV 万能和弦 (C-G-Am-F)
#   - 3层引入: 前16bar无鼓, 逐步加层
#   - 五声旋律 (C-D-E-G-A), ≤1 octave
#   - 鼓: 全程4/floor不变 (四分)
#   - 新手友好: 下拍为主, 无切分

bars = 48
bpm = 120

# 6组 × 8bars, 每组: C*2 + G*2 + Am*2 + F*2
chords = []
for phase in range(6):
    chords.extend(['C','C','G','G','Am','Am','F','F'])
chords_48 = chords[:48]

NOTES = {
    'C':  ('C2','E2','G2','C3','E3','G3','C4','E4','G4','C5'),
    'G':  ('G1','B1','D2','G2','B2','D3','G3','B3','D4','G4'),
    'Am': ('A1','C2','E2','A2','C3','E3','A3','C4','E4','A4'),
    'F':  ('F1','A1','C2','F2','A2','C3','F3','A3','C4','F4'),
}
ROOT = {'C':'C1','G':'G1','Am':'A1','F':'F1'}
THIRD = {'C':'E2','G':'B2','Am':'C2','F':'A2'}

lines = [f'# 新手教学关卡 — C大调, 120BPM, 48bars, 3-4层',
         f'name = "tutorial"', f'bpm = {bpm}', '']

# ═══ PAD (全程, 全音符, pp→mp→mf→mp→pp) ═══
pad = []
for b in range(bars):
    ch = chords_48[b]
    n = NOTES[ch]
    if b < 16:
        pad.append(f'{n[4]}:w:pp')    # C3/E3/G3 etc.
    elif b < 32:
        pad.append(f'{n[4]}:w:mp')
    elif b < 40:
        pad.append(f'{n[4]}:w:mf')
    else:
        pad.append(f'{n[4]}:w:mp')
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.30')
lines.append(f'notes = {",".join(pad)}\n')

# ═══ BASS (bar 16+, 二分音符) ═══
bass = []
for b in range(bars):
    ch = chords_48[b]
    r = ROOT[ch]
    if b < 16:
        bass.append('R:w')
    elif b < 40:
        bass.append(f'{r}:h:mp,{r}:h:mp')
    else:
        bass.append(f'{r}:h:pp,{r}:h:pp')
bass_flat = [x for g in bass for x in g.split(',')]
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(bass_flat)}\n')

# ═══ KICK (bar 24+, 四分4/floor) ═══
kick = []
for b in range(bars):
    if b < 24:
        kick.append('R:q,R:q,R:q,R:q')
    else:
        kick.append('K:q:mp,K:q:mp,K:q:mp,K:q:mp')
kick_flat = [x for g in kick for x in g.split(',')]
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.55')
lines.append(f'notes = {",".join(kick_flat)}\n')

# ═══ SNARE (bar 24+, 四分2/4拍) ═══
snare = []
for b in range(bars):
    if b < 24:
        snare.append('R:q,R:q,R:q,R:q')
    else:
        snare.append('R:q,S:q:mp,R:q,S:q:mp')
snare_flat = [x for g in snare for x in g.split(',')]
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.45')
lines.append(f'notes = {",".join(snare_flat)}\n')

# ═══ PIANO (bar 8+, 琶音C→G→Am→F) ═══
piano = []
for b in range(bars):
    ch = chords_48[b]
    # 不同和弦用不同级数, 保持整体≤10st
    off = 3 if ch in ('C','Am') else 4
    n3 = NOTES[ch][off]
    n5 = NOTES[ch][off+1]
    n7 = NOTES[ch][off+2]
    if b < 8:
        piano.append('R:q,R:q,R:q,R:q')
    elif b < 24:
        # 分解: root-5th-root-3rd
        piano.append(f'{n3}:e:pp,{n5}:e:pp,{n3}:e:pp,{n7}:e:pp')
    elif b < 40:
        piano.append(f'{n3}:e:mp,{n5}:e:mp,{n3}:e:mp,{n7}:e:mp')
    else:
        piano.append(f'{n3}:e:pp,{n5}:e:pp,{n3}:e:pp,{n7}:e:pp')
piano_flat = [x for g in piano for x in g.split(',')]
lines.append('[track piano]\ninstrument = piano\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join(piano_flat)}\n')

# ═══ LEAD MELODY — C五声, ≤1 octave, 下拍 ═══
# 旋律设计: 4-bar乐句, 呼-应
# C五声音阶: C4(60) D4(62) E4(64) G4(67) A4(69)
# 音域: C4(60) - C5(72) = 12半音, 但主要用C4-A4(60-69)=9半音

lead = []
for b in range(bars):
    p = b // 8  # phase (0-5)
    ch = chords_48[b]

    # Phase 0-1 (bars 0-15): no melody (pad + piano only)
    if b < 16:
        lead.append('R:w')

    # 音域限制: C4(60) - C5(72) = 12st (≤1 octave)
    # 核心五声音阶: C4 D4 E4 G4 A4 C5 (最多C5最高点)
    # Phase 2 (bars 16-23): melody first entry
    elif b == 16:   # C — 上行动机
        lead.append('C4:e:mp,E4:e:mp,G4:e:mp,E4:e:mp,C4:e:mp,D4:e:mp,E4:e:mp,R:e')
    elif b == 17:   # C — 落
        lead.append('D4:e:mp,C4:e:mp,R:e,R:e,G4:e:mp,E4:e:mp,D4:e:mp,R:e')
    elif b == 18:   # G — 呼应
        lead.append('D4:e:mp,G4:e:mp,B4:e:mp,G4:e:mp,D4:e:mp,E4:e:mp,D4:e:mp,R:e')
    elif b == 19:   # G
        lead.append('D4:e:mp,R:e,G4:e:mp,E4:e:mp,D4:e:mp,C4:e:mp,D4:e:mp,R:e')
    elif b == 20:   # Am
        lead.append('C4:e:mp,E4:e:mp,A4:e:mp,E4:e:mp,C4:e:mp,E4:e:mp,A4:e:mp,R:e')
    elif b == 21:   # Am
        lead.append('G4:e:mp,E4:e:mp,C4:e:mp,R:e,G4:e:mp,A4:e:mp,G4:e:mp,R:e')
    elif b == 22:   # F
        lead.append('C4:e:mp,C4:e:mp,F4:e:mp,C4:e:mp,C4:e:mp,C4:e:mp,F4:e:mp,R:e')
    elif b == 23:   # F — 乐句结束
        lead.append('E4:e:mp,D4:e:mp,C4:e:mp,R:e,E4:e:mp,G4:e:mp,C4:e:mp,R:e')

    # Phase 3 (bars 24-31): repeat, stronger
    elif b == 24:   # C
        lead.append('C4:e:mf,E4:e:mf,G4:e:mf,E4:e:mf,C4:e:mf,D4:e:mf,E4:e:mf,R:e')
    elif b == 25:   # C — 高点
        lead.append('D4:e:mf,C4:e:mf,R:e,R:e,A4:e:mf,G4:e:mf,E4:e:mf,R:e')
    elif b == 26:   # G
        lead.append('D4:e:mf,G4:e:mf,B4:e:mf,G4:e:mf,D4:e:mf,E4:e:mf,D4:e:mf,R:e')
    elif b == 27:   # G
        lead.append('D4:e:mf,R:e,G4:e:mf,E4:e:mf,D4:e:mf,C4:e:mf,D4:e:mf,R:e')
    elif b == 28:   # Am — 更高
        lead.append('E4:e:mf,G4:e:mf,C5:e:mf,G4:e:mf,E4:e:mf,G4:e:mf,C5:e:mf,R:e')
    elif b == 29:   # Am
        lead.append('A4:e:mf,G4:e:mf,E4:e:mf,R:e,A4:e:mf,G4:e:mf,E4:e:mf,R:e')
    elif b == 30:   # F
        lead.append('F4:e:mf,A4:e:mf,C5:e:mf,A4:e:mf,F4:e:mf,E4:e:mf,D4:e:mf,R:e')
    elif b == 31:   # F
        lead.append('C4:e:mf,D4:e:mf,E4:e:mf,R:e,G4:e:mf,A4:e:mf,G4:e:mf,R:e')

    # Phase 4 (bars 32-39): variation
    elif b == 32:   # C
        lead.append('G4:e:mf,E4:e:mf,C4:e:mf,R:e,E4:e:mf,G4:e:mf,C5:e:mf,R:e')
    elif b == 33:   # C
        lead.append('A4:e:mf,G4:e:mf,E4:e:mf,R:e,G4:e:mf,E4:e:mf,D4:e:mf,R:e')
    elif b == 34:   # G
        lead.append('G4:e:mf,D4:e:mf,C4:e:mf,R:e,G4:e:mf,D4:e:mf,C4:e:mf,R:e')
    elif b == 35:   # G
        lead.append('D4:e:mf,E4:e:mf,G4:e:mf,E4:e:mf,D4:e:mf,C4:e:mf,D4:e:mf,R:e')
    elif b == 36:   # Am — climax (still ≤C5)
        lead.append('A4:e:mf,C5:e:mf,G4:e:mf,C5:e:mf,A4:e:mf,G4:e:mf,E4:e:mf,R:e')
    elif b == 37:   # Am — 回落
        lead.append('A4:e:mf,E4:e:mf,C4:e:mf,R:e,A4:e:mf,E4:e:mf,C4:e:mf,R:e')
    elif b == 38:   # F
        lead.append('F4:e:mf,A4:e:mf,C5:e:mf,A4:e:mf,G4:e:mf,F4:e:mf,E4:e:mf,R:e')
    elif b == 39:   # F
        lead.append('E4:e:mf,D4:e:mf,C4:e:mf,D4:e:mf,E4:e:mf,G4:e:mf,C4:e:mf,R:e')

    # Phase 5 (bars 40-47): wind down
    elif b == 40:   # C
        lead.append('C4:e:mp,E4:e:mp,G4:e:mp,E4:e:mp,C4:e:mp,D4:e:mp,E4:e:mp,R:e')
    elif b == 41:   # C
        lead.append('D4:e:mp,C4:e:mp,R:e,R:e,G4:e:mp,E4:e:mp,C4:e:mp,R:e')
    elif b == 42:   # G
        lead.append('D4:e:mp,G4:e:mp,B4:e:mp,G4:e:mp,D4:e:mp,C4:e:mp,D4:e:mp,R:e')
    elif b == 43:   # G
        lead.append('D4:e:mp,R:e,G4:e:mp,E4:e:mp,D4:e:mp,C4:e:mp,D4:e:mp,R:e')
    elif b == 44:   # Am — 渐低
        lead.append('C4:e:mp,E4:e:mp,A4:e:mp,R:e,C4:e:mp,E4:e:mp,A4:e:mp,R:e')
    elif b == 45:   # Am
        lead.append('G4:e:mp,E4:e:mp,C4:e:mp,R:e,G4:e:mp,E4:e:mp,D4:e:mp,R:e')
    elif b == 46:   # F — fade
        lead.append('C4:e:pp,C4:e:pp,F4:e:pp,C4:e:pp,C4:e:pp,C4:e:pp,E4:e:pp,R:e')
    else:           # b==47 — final C chord resolve
        lead.append('D4:e:pp,C4:e:pp,R:e,R:e,D4:e:pp,C4:e:pp,R:e,R:e')

lead_flat = [x for g in lead for x in g.split(',')]
lines.append('[track lead]\ninstrument = piano\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(lead_flat)}\n')

# ═══ BELL (bar 32+, 点缀高音) ═══
bell = []
for b in range(bars):
    if b < 32:
        bell.append('R:q,R:q,R:q,R:q')
    elif b == 32:
        bell.append('G4:e:mf,C5:e:mf,R:e,R:e,R:e,R:e,R:e,R:e')
    elif b == 33:
        bell.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
    elif b == 34:
        bell.append('G4:e:mf,D4:e:mf,R:e,R:e,R:e,R:e,R:e,R:e')
    elif b == 35:
        bell.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
    elif b == 36:
        bell.append('A4:e:mf,C5:e:mf,R:e,R:e,R:e,R:e,R:e,R:e')
    elif b == 37:
        bell.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
    elif b == 38:
        bell.append('F4:e:mp,A4:e:mp,R:e,R:e,R:e,R:e,R:e,R:e')
    elif b == 39:
        bell.append('R:e,R:e,R:e,R:e,R:e,R:e,R:e,R:e')
    else:
        bell.append('R:q,R:q,R:q,R:q')

bell_flat = [x for g in bell for x in g.split(',')]
lines.append('[track bell]\ninstrument = piano\nmode = parallel\nvolume = 0.25')
lines.append(f'notes = {",".join(bell_flat)}\n')

with open(r'D:\PYTHON\ACM\cli_composer\samples\tutorial.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/tutorial.acml ({bars} bars, {bpm} BPM, {bars*4*60/bpm:.1f}s)')

# Verify note density
total_notes = sum(1 for g in lead_flat if g and g[0] != 'R')
dur_sec = bars * 4 * 60 / bpm
print(f'Lead melody: {total_notes} notes in {dur_sec:.0f}s = {total_notes/dur_sec:.1f} notes/sec')
print(f'Melody range check needed: ≤1 octave for beginner')
