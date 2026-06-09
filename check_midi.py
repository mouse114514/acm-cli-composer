import mido, os
path = 'output/keic_theme_aw.mid'
mid = mido.MidiFile(path)
sz = os.path.getsize(path)
print(f'File: {sz} bytes, {len(mid.tracks)} tracks')
total = 0
for i, t in enumerate(mid.tracks):
    n = sum(1 for m in t if m.type == 'note_on')
    if n > 0:
        total += n
        # find program  
        pgm = '?'
        for m in t:
            if m.type == 'program_change':
                pgm = str(m.program)
                break
        print(f'  Track {i}: {n} notes [pgm={pgm}]')
print(f'Total: {total} notes')
