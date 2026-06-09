import mido
path = 'output/keic_theme_aw.mid'
mid = mido.MidiFile(path)
# Debug bass track (index 3)
t = mid.tracks[3]
print(f"Bass track ({len(t)} msgs):")
for m in t:
    print(f"  {m}")
print()
# Debug pad track (index 4)
t = mid.tracks[4]
print(f"Pad track ({len(t)} msgs):")
for m in t:
    print(f"  {m}")
print()
# Debug lead track (index 7)
t = mid.tracks[7]
print(f"Lead track ({len(t)} msgs):")
for m in t[:20]:
    print(f"  {m}")
if len(t) > 20:
    print(f"  ... ({len(t)} total)")
