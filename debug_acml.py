import sys; sys.path.insert(0,'.')
from acml import parse_acml
from composer import Composer
from track import Track

name, bpm, loop, trk_dicts = parse_acml('samples/keic_theme_aw.acml')
print(f'Song: {name}, BPM: {bpm}, Tracks: {len(trk_dicts)}')

for td in trk_dicts:
    trk_name = td.get('name','')
    t = Track(
        instrument=td.get('instrument','piano'),
        notes=td.get('notes',''),
        volume=float(td.get('volume',1.0)),
        pan=float(td.get('pan',0.0)),
        mode=td.get('mode','parallel'),
        wavetable=td.get('wavetable'),
    )
    # Set name attribute manually (not in __init__ but used by write_midi)
    t.name = trk_name
    nl = len(t.notes or '')
    print(f'  {t.name}: instr={t.instrument} mode={t.mode} notes_len={nl}')
    if t.notes:
        expanded = Composer.expand_compact_notes(t.notes)
        parts = [n.strip() for n in expanded.split(',') if n.strip()]
        ext = sum(1 for p in parts if ':' in p)
        print(f'    parts={len(parts)} extended={ext} first={parts[0] if parts else "?"} last={parts[-1] if parts else "?"}')

# Now compile and check MIDI
c = Composer(bpm=bpm)
for td in trk_dicts:
    trk_name = td.get('name','')
    t = Track(
        instrument=td.get('instrument','piano'),
        notes=td.get('notes',''),
        volume=float(td.get('volume',1.0)),
        pan=float(td.get('pan',0.0)),
        mode=td.get('mode','parallel'),
        wavetable=td.get('wavetable'),
        sample=td.get('sample'),
        sample_pitch=td.get('sample_pitch'),
        harmony=td.get('harmony'),
        fm_ratio=td.get('fm_ratio'),
        fm_index=td.get('fm_index'),
        kick=td.get('kick'),
        snare=td.get('snare'),
        hihat=td.get('hihat'),
        durations=td.get('durations'),
        arpeggio=td.get('arpeggio'),
        loops=int(td.get('loops',1)),
    )
    t.name = trk_name
    c.tracks.append(t)

c.write_midi('debug_from_acml.mid', max_secs=60.0)
import mido
mid = mido.MidiFile('debug_from_acml.mid')
print(f'\nMIDI result: {len(mid.tracks)} tracks')
for i,t in enumerate(mid.tracks):
    n=sum(1 for m in t if m.type=='note_on' and m.velocity>0)
    name='?'
    for m in t:
        if m.type=='track_name': name=m.name; break
    if n>0:
        print(f'  T{i}: {n} note_on [{name}]')
