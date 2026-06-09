import mido, os
path = 'output/keic_theme_aw.mid'
mid = mido.MidiFile(path)
sz = os.path.getsize(path)
print(f'File: {sz} bytes, {len(mid.tracks)} tracks, length={mid.length:.1f}s')
total_on = 0
for i, t in enumerate(mid.tracks):
    n_on = sum(1 for m in t if m.type == 'note_on' and m.velocity > 0)
    n_off = sum(1 for m in t if m.type == 'note_off')
    n_on0 = sum(1 for m in t if m.type == 'note_on' and m.velocity == 0)
    msgs = len(t)
    pgm = '?'
    for m in t:
        if m.type == 'program_change':
            pgm = str(m.program)
            break
    if n_on > 0 or n_off > 0:
        total_on += n_on
        print(f'  Track {i}: {n_on} note_on + {n_off} note_off + {n_on0} note_on(v=0) = {msgs} msgs [pgm={pgm}]')
print(f'Total note_on(vel>0): {total_on}')
