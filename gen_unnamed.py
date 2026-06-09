# unnamed v5 — 借鉴Evans: 动机重复 + 非和弦音(25%) + 宽跳进 + 切分
# Hooktheory数据: Evans旋律只有72%和弦内音, 28%非和弦音
# 我之前的旋律: ~100%和弦内音 = 琶音感
# 本版: 每个phase都有一个2小节核心动机, 重复变奏

bars = 16
bpm = 95

# Bb自然小调: Bb-C-Db-Eb-F-Gb-Ab
chords_16 = [
    'Bbm','Bbm','Bbm','Bbm',
    'Gb','Gb','Ab','Ab',
    'Ebm','Ebm','F','F',
    'Bbm','Bbm','Gb','F'
]

ROOT = {'Bbm':'Bb1','Gb':'Gb1','Ab':'Ab1','Ebm':'Eb1','F':'F1'}
ROOT3 = {'Bbm':'Bb2','Gb':'Gb2','Ab':'Ab2','Ebm':'Eb2','F':'F2'}
NOTES = {
    'Bbm': ('Bb2','Db3','F3','Bb3','Db4','F4','Bb4','Db5','F5','Bb5'),
    'Gb':  ('Gb2','Bb2','Db3','Gb3','Bb3','Db4','Gb4','Bb4','Db5','Gb5'),
    'Ab':  ('Ab2','C3','Eb3','Ab3','C4','Eb4','Ab4','C5','Eb5','Ab5'),
    'Ebm': ('Eb2','Gb2','Bb2','Eb3','Gb3','Bb3','Eb4','Gb4','Bb4','Eb5'),
    'F':   ('F2','A2','C3','F3','A3','C4','F4','A4','C5','F5'),
}

def ph(b):
    if b < 4:   return 0
    if b < 8:   return 1
    if b < 12:  return 2
    return 3

lines = [f'# unnamed v5 — Evans-style motif + non-chord tones',
         f'name = "unnamed"', f'bpm = {bpm}', '']

# ═══ DRUMS (same as v4) ═══
kick = []
for b in range(bars):
    p = ph(b)
    if p == 0:
        kick.extend(['R:q']*4)
    elif p == 1:
        kick.extend(['R:q']*4)
    elif p == 2:
        kick.extend(['K:q:mp','R:q','R:q','R:q'])
    else:
        if b % 2 == 0:
            kick.extend(['R:q','K:q:mf','R:q','K:q:mf'])
        else:
            kick.extend(['K:q:ff','R:q','K:q:ff','R:q'])
lines.append('[track kick]\ninstrument = drums\nmode = parallel\nvolume = 0.75')
lines.append(f'notes = {",".join(kick)}\n')

snare = []
for b in range(bars):
    p = ph(b)
    if p == 0:
        snare.extend(['R:q']*4)
    elif p == 1:
        snare.extend(['R:q','S:q:pp','R:q','R:q'])
    elif p == 2:
        snare.extend(['S:q:mp','R:q','S:q:mp','R:q'])
    else:
        snare.extend(['R:q','S:q:ff','R:q','S:q:ff'])
lines.append('[track snare]\ninstrument = drums\nmode = parallel\nvolume = 0.60')
lines.append(f'notes = {",".join(snare)}\n')

hihat = []
for b in range(bars):
    p = ph(b)
    if p < 2:
        hihat.extend(['R:e']*8)
    elif p == 2:
        hihat.extend(['H:e:pp']*8)
    else:
        hihat.extend(['H:s:mf']*16)
lines.append('[track hihat]\ninstrument = drums\nmode = parallel\nvolume = 0.30')
lines.append(f'notes = {",".join(hihat)}\n')

# ═══ BASS (same as v4) ═══
bass = []
for b in range(bars):
    p = ph(b)
    r = ROOT[chords_16[b]]
    if p == 0:
        bass.append(f'{r}:w:pp')
    elif p == 1:
        bass.append(f'{r}:w:pp')
    elif p == 2:
        bass.append(f'{r}:h:mp,{r}:h:mp')
    else:
        bass.append(f'{r}:q:mf,{r}:q:mf,{r}:q:mf,{r}:q:mf')
bass_flat = [x for g in bass for x in g.split(',')]
lines.append('[track bass]\ninstrument = bass\nmode = parallel\nvolume = 0.65')
lines.append(f'notes = {",".join(bass_flat)}\n')

# ═══ PIANO (same as v4) ═══
piano = []
for b in range(bars):
    p = ph(b)
    if p == 0:
        piano.extend(['Bb2:h:pp','Bb3:h:pp'])
    elif p == 1:
        piano.extend(['Gb3:q:pp','Ab3:q:pp','R:q','R:q'])
    elif p == 2:
        piano.extend(['Eb3:e:mp','Ab3:e:mp','Db4:e:mp','Gb4:e:mp','R:e','R:e','R:e','R:e'])
    else:
        piano.extend(['Bb2:s:mf','Eb3:s:mf','Ab3:s:mf','R:s']*4)
lines.append('[track piano]\ninstrument = piano\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(piano)}\n')

# ═══ PAD (same as v4) ═══
pad = []
for b in range(bars):
    p = ph(b)
    r = ROOT3[chords_16[b]]
    vol = ['pp','pp','mp','mf'][p]
    pad.append(f'{r}:w:{vol}')
lines.append('[track pad]\ninstrument = pad\nmode = parallel\nvolume = 0.25\npan = 0.3')
lines.append(f'notes = {",".join(pad)}\n')

# ═══ LEAD (v5 — 完全重写: 动机重复 + 非和弦音 + 宽跳进) ═══
# 每个phase有一个2小节核心动机, 重复一次
# 标记: * = 非和弦音

lead = []
for b in range(bars):
    p = ph(b)

    # === PHASE 0 (Bbm): 忧郁动机 — 每个b=1小节(4拍) ===
    # 和弦: Bbm (Bb-Db-F)
    # 非和弦音: Gb4(b6), C4(2度), Eb4(4度) = 25%
    # 动机A (bars 0,2): 8-eighth motif (Evans风格)
    # 动机B (bars 1,3): syncopated variation
    if p == 0:
        if b in [0, 2]:
            lead.append('Bb3:e:pp,Db4:e:pp,F4:e:pp,Db4:e:pp,Gb4:e:pp,F4:e:pp,Bb3:e:pp,Gb4:e:pp')
        elif b in [1, 3]:
            lead.append('F4:e:pp,Db4:e:pp,C4:e:pp,F4:e:pp,Eb4:e:pp,Db4:e:pp,F4:e:pp,Bb4:e:pp')

    # === PHASE 1 (Gb-Ab): 不安 — C natural = #4 Lydian ===
    elif p == 1:
        if b == 4:
            lead.append('Gb4:e:pp,Bb4:e:pp,Db5:e:pp,C5:e:pp,Gb4:e:pp,Bb4:e:pp,Db5:e:pp,C5:e:pp')
        elif b == 5:
            lead.append('C5:e:pp,Db5:e:pp,Gb4:e:pp,R:e,C5:e:pp,Db5:e:pp,Gb5:e:pp,R:e')
        elif b == 6:
            lead.append('Ab4:e:pp,C5:e:pp,Eb5:e:pp,C5:e:pp,Ab4:e:pp,C5:e:pp,Eb5:e:pp,C5:e:pp')
        else:
            lead.append('Ab4:q:pp,Eb5:q:pp,R:e,C5:e:pp,Eb5:e:pp,Ab5:e:pp,R:e')

    # === PHASE 2 (Ebm-F): 上升 ===
    # Ebm: C5=非和弦(b6), Ab5=非和弦(b3上方)
    # F:   Eb5=非和弦(b7)
    elif p == 2:
        if b == 8:
            lead.append('Eb4:e:mp,Gb4:e:mp,Bb4:e:mp,Eb5:e:mp,Bb4:e:mp,Gb4:e:mp,C5:e:mp,R:e')
        elif b == 9:
            lead.append('R:e,Gb4:e:mp,Bb4:e:mp,Eb5:e:mp,Ab5:e:mp,Eb5:e:mp,Bb4:e:mp,R:e')
        elif b == 10:
            lead.append('F4:e:mp,A4:e:mp,C5:e:mp,F5:e:mp,Eb5:e:mp,A4:e:mp,F4:e:mp,R:e')
        else:
            lead.append('A4:q:mp,C5:q:mp,R:e,F5:e:mp,Eb5:e:mp,C5:e:mp,R:e')

    # === PHASE 3 (Bbm-Gb-F): 愤怒, 三全音 ===
    # Bbm: E自然=tritone, Gb: E=b6, F: E=7度
    else:
        if b == 12:
            lead.append('Db5:e:ff,E5:e:ff,Gb5:e:ff,Db5:e:ff,Bb4:e:ff,E5:e:ff,Gb5:e:ff,R:e')
        elif b == 13:
            lead.append('Gb4:e:ff,Bb4:e:ff,Db5:e:ff,E5:e:ff,Gb5:e:ff,E5:e:ff,Db5:e:ff,Bb4:e:ff')
        elif b == 14:
            lead.append('Bb3:e:ff,Db4:e:ff,E4:e:ff,Gb4:e:ff,Bb4:e:ff,Db5:e:ff,E5:e:ff,Gb5:e:ff')
        else:
            lead.append('F4:e:ff,A4:e:ff,C5:e:ff,F5:e:ff,C5:e:ff,A4:e:ff,F4:e:ff,R:e')

lines.append('[track lead]\ninstrument = sawtooth\nmode = parallel\nvolume = 0.50')
lines.append(f'notes = {",".join(lead)}\n')

# DRONE
drone = []
for b in range(bars):
    p = ph(b)
    r = ROOT[chords_16[b]]
    if p < 2:
        drone.append(f'{r}:w:pp')
    else:
        drone.append('R:w')
lines.append('[track drone]\ninstrument = string\nmode = parallel\nvolume = 0.18')
lines.append(f'notes = {",".join(drone)}\n')

# STAB (anger only)
stab = []
for b in range(bars):
    p = ph(b)
    chk = chords_16[b]
    r = {'Bbm':'Bb2','Gb':'Gb2','Ab':'Ab2','Ebm':'Eb2','F':'F2'}.get(chk,'C3')
    t = {'Bbm':'Db3','Gb':'Bb2','Ab':'C3','Ebm':'Gb2','F':'A2'}.get(chk,'C3')
    if p == 3:
        stab.append(f'{r}:s:mf,{t}:s:mf,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
    else:
        stab.append('R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s,R:s')
stab_flat = [x for g in stab for x in g.split(',')]
lines.append('[track stab]\ninstrument = wavetable\nwavetable = sawtooth\nmode = parallel\nvolume = 0.35')
lines.append(f'notes = {",".join(stab_flat)}')

with open('samples/unnamed.acml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Generated samples/unnamed.acml ({bars} bars, {bpm} BPM, {bars*4*60/bpm:.1f}s)')
