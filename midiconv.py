"""MIDI -> ACML converter. Pure stdlib, no external deps."""

import os
import re

# ---------------------------------------------------------------------------
# Note / dynamic / duration helpers
# ---------------------------------------------------------------------------

_MIDI_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# (beats, letter) - sorted ascending; used for quantization
_DURATION_VALUES = [
    (0.25, "s"), (0.375, "s."), (0.5, "e"), (0.75, "e."),
    (1.0, "q"), (1.5, "q."), (2.0, "h"), (3.0, "h."),
    (4.0, "w"), (6.0, "w."),
]

_DYN_LEVELS = [
    (0.20, "ppp"), (0.25, "pp"), (0.35, "p"), (0.50, "mp"),
    (0.65, "mf"), (0.80, "f"), (0.90, "ff"), (1.00, "fff"),
]

# GM program (0-based) -> ACM instrument; range-based mapping
def _gm_to_instrument(program):
    p = program
    if p <= 7:
        return "piano"
    if p <= 15:
        return "bell"
    if p <= 23:
        return "organ"
    if p <= 31:
        return "guitar"
    if p <= 39:
        return "bass"
    if p <= 55:
        return "strings"
    if p == 56:
        return "trumpet"
    if p == 58:
        return "tuba"
    if p <= 63:
        return "brass"
    if p <= 71:
        return "brass"
    if p <= 79:
        return "lead"
    if p == 81:
        return "sawtooth"
    if p <= 87:
        return "lead"
    if p <= 95:
        return "pad"
    if p <= 103:
        return "pad"
    if p <= 111:
        return "guitar"
    if p <= 119:
        return "bell"
    # 120-127 GM sound effects: never map to "sample" (needs an explicit WAV path)
    return "wavetable"


def _midi_to_note_name(pitch):
    octave = pitch // 12 - 1
    name = _MIDI_TO_NOTE[pitch % 12]
    return f"{name}{octave}"


def _velocity_to_dynamic(velocity):
    v = velocity / 127.0
    return min(_DYN_LEVELS, key=lambda x: abs(x[0] - v))[1]


def _duration_value(letter):
    dotted = letter.endswith(".")
    base = letter[0].lower()
    m = {"w": 4.0, "h": 2.0, "q": 1.0, "e": 0.5, "s": 0.25}
    val = m.get(base, 1.0)
    return val * 1.5 if dotted else val


def _quantize_duration(beats):
    if beats <= 0:
        return "s"
    return min(_DURATION_VALUES, key=lambda x: abs(x[0] - beats))[1]


def _fit_duration(max_beats):
    """Largest standard duration that fits within max_beats."""
    for val, letter in sorted(_DURATION_VALUES, key=lambda x: -x[0]):
        if val <= max_beats + 1e-9:
            return letter
    return "s"


def _gap_to_rests(gap_beats):
    """Decompose a gap into rest tokens snapped to a sixteenth grid."""
    if gap_beats < 0.125:
        return []
    steps = int(round(gap_beats / 0.25))
    if steps <= 0:
        return []
    tokens = []
    for val, letter in [(16, "w"), (12, "h."), (8, "h"), (6, "q."),
                        (4, "q"), (3, "e."), (2, "e"), (1, "s")]:
        while steps >= val:
            tokens.append(f"R:{letter}")
            steps -= val
    return tokens


# ---------------------------------------------------------------------------
# Drum mapping (GM percussion note -> ACM drum letter)
# ---------------------------------------------------------------------------

_DRUM_MAP = {
    35: "K", 36: "K",
    37: "S", 38: "S", 39: "S", 40: "S",
    41: "T", 43: "T", 45: "T", 47: "T", 48: "T", 50: "T",
    42: "H", 44: "H",
    46: "O",
    49: "O", 51: "O", 53: "O", 55: "O", 57: "O", 59: "O",
}

_DRUM_TRACK_NAMES = {
    "K": "kick", "S": "snare", "H": "hats", "O": "cymbals", "T": "toms",
}


# ---------------------------------------------------------------------------
# MIDI parsing (SMF format 0/1/2)
# ---------------------------------------------------------------------------

def _read_vlq(data, pos):
    val = 0
    while True:
        if pos >= len(data):
            raise ValueError("Unexpected end of MIDI data while reading VLQ")
        byte = data[pos]
        pos += 1
        val = (val << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return val, pos


def parse_midi(filepath):
    """Parse a .mid file.

    Returns dict:
      {
        'ticks_per_beat': int,
        'bpm': float,
        'channels': {
            channel (int): {
                'program': int,
                'name': str or None,
                'notes': [{'pitch','start','end','velocity'}]  # ticks
            }
        }
      }
    """
    with open(filepath, "rb") as f:
        data = f.read()

    if data[0:4] != b"MThd":
        raise ValueError("Not a MIDI file (missing MThd header)")

    header_len = int.from_bytes(data[4:8], "big")
    division = int.from_bytes(data[12:14], "big")
    if division & 0x8000:
        raise ValueError("SMPTE time division is not supported")
    ticks_per_beat = division
    if ticks_per_beat <= 0:
        raise ValueError("Invalid time division")

    pos = 8 + header_len
    ntrks = int.from_bytes(data[10:12], "big")

    channels = {}       # channel -> {'program', 'name', 'notes'}
    tempo_events = []   # (abs_tick, bpm)
    open_notes = {}     # (channel, pitch) -> (start_tick, velocity, track_name)
    track_names = {}    # channel -> track name (first seen)

    for _ in range(ntrks):
        if pos + 8 > len(data):
            break
        if data[pos:pos + 4] != b"MTrk":
            chunk_len = int.from_bytes(data[pos + 4:pos + 8], "big")
            pos += 8 + chunk_len
            continue
        chunk_len = int.from_bytes(data[pos + 4:pos + 8], "big")
        chunk = data[pos + 8:pos + 8 + chunk_len]
        pos += 8 + chunk_len

        abs_tick = 0
        running_status = None
        cpos = 0
        track_name = None

        while cpos < len(chunk):
            delta, cpos = _read_vlq(chunk, cpos)
            abs_tick += delta

            if cpos >= len(chunk):
                break
            byte = chunk[cpos]

            if byte == 0xFF:  # meta event
                cpos += 1
                if cpos >= len(chunk):
                    break
                meta_type = chunk[cpos]
                cpos += 1
                meta_len, cpos = _read_vlq(chunk, cpos)
                meta_data = chunk[cpos:cpos + meta_len]
                cpos += meta_len

                if meta_type == 0x51 and len(meta_data) >= 3:
                    mpqn = int.from_bytes(meta_data[:3], "big")
                    if mpqn > 0:
                        bpm = round(60000000.0 / mpqn, 3)
                        tempo_events.append((abs_tick, bpm))
                elif meta_type == 0x03:
                    try:
                        track_name = meta_data.decode("utf-8", errors="replace").strip("\x00").strip()
                    except Exception:
                        track_name = None
                elif meta_type == 0x2F:
                    break  # end of track

            elif byte in (0xF0, 0xF7):  # sysex
                cpos += 1
                sysex_len, cpos = _read_vlq(chunk, cpos)
                cpos += sysex_len

            elif byte & 0x80:  # status byte
                running_status = byte
                cpos += 1
                cpos = _handle_channel_event(
                    chunk, cpos, byte, abs_tick,
                    channels, open_notes, track_names, track_name
                )

            else:  # running status
                if running_status is None:
                    cpos += 1
                    continue
                cpos = _handle_channel_event(
                    chunk, cpos, running_status, abs_tick,
                    channels, open_notes, track_names, track_name
                )

        # close any notes left open at end of this track (spec: note-on/off
        # always live in the same MTrk chunk, so clearing here is safe)
        end_tick = abs_tick
        for (ch, pitch), (start, vel, tname) in list(open_notes.items()):
            _add_note(channels, ch, pitch, start, end_tick, vel, tname)
        open_notes.clear()

    # close any remaining open notes at end of file
    max_tick = 0
    for ch_info in channels.values():
        for n in ch_info["notes"]:
            if n["end"] > max_tick:
                max_tick = n["end"]
    for (ch, pitch), (start, vel, tname) in list(open_notes.items()):
        _add_note(channels, ch, pitch, start, max_tick, vel, tname)
    open_notes.clear()

    tempo_events.sort(key=lambda x: x[0])
    bpm = tempo_events[0][1] if tempo_events else 120.0

    for ch_info in channels.values():
        ch_info["notes"].sort(key=lambda n: (n["start"], n["end"], n["pitch"]))

    return {
        "ticks_per_beat": ticks_per_beat,
        "bpm": bpm,
        "channels": channels,
    }


def _handle_channel_event(chunk, cpos, status, abs_tick,
                          channels, open_notes, track_names, track_name):
    """Handle one channel voice message. Returns new cpos."""
    msg_type = status & 0xF0
    channel = status & 0x0F

    if msg_type == 0x90:  # note on
        if cpos + 2 > len(chunk):
            return len(chunk)
        pitch = chunk[cpos]
        velocity = chunk[cpos + 1]
        cpos += 2
        if velocity > 0:
            open_notes[(channel, pitch)] = (abs_tick, velocity, track_name)
            if channel not in track_names and track_name:
                track_names[channel] = track_name
        else:
            _close_note(channels, open_notes, channel, pitch, abs_tick)
    elif msg_type == 0x80:  # note off
        if cpos + 2 > len(chunk):
            return len(chunk)
        pitch = chunk[cpos]
        cpos += 2
        _close_note(channels, open_notes, channel, pitch, abs_tick)
    elif msg_type == 0xC0:  # program change
        if cpos + 1 > len(chunk):
            return len(chunk)
        program = chunk[cpos]
        cpos += 1
        info = channels.setdefault(channel, {"program": 0, "name": None, "notes": []})
        info["program"] = program
    elif msg_type == 0xD0:  # channel aftertouch
        cpos += 1
    elif msg_type in (0xA0, 0xB0, 0xE0):  # poly AT, control change, pitch bend
        cpos += 2
    else:
        cpos += 1
    return cpos


def _close_note(channels, open_notes, channel, pitch, abs_tick):
    key = (channel, pitch)
    if key in open_notes:
        start, vel, tname = open_notes.pop(key)
        _add_note(channels, channel, pitch, start, abs_tick, vel, tname)


def _add_note(channels, channel, pitch, start, end, velocity, track_name):
    if end <= start:
        end = start + 1
    info = channels.setdefault(channel, {"program": 0, "name": None, "notes": []})
    if track_name and not info["name"]:
        info["name"] = track_name
    info["notes"].append({
        "pitch": pitch,
        "start": start,
        "end": end,
        "velocity": velocity,
    })


# ---------------------------------------------------------------------------
# Voice splitting (greedy interval partitioning, prefer most-recent voice)
# ---------------------------------------------------------------------------

def _split_voices(notes):
    if not notes:
        return []
    notes = sorted(notes, key=lambda n: (n["start"], n["end"], n["pitch"]))
    voices = []
    voice_ends = []
    for note in notes:
        best = -1
        best_end = -1
        for i, end in enumerate(voice_ends):
            if note["start"] >= end and end >= best_end:
                best = i
                best_end = end
        if best >= 0:
            voices[best].append(note)
            voice_ends[best] = note["end"]
        else:
            voices.append([note])
            voice_ends.append(note["end"])
    return voices


# ---------------------------------------------------------------------------
# Track naming
# ---------------------------------------------------------------------------

def _sanitize_track_name(name, fallback):
    if not name:
        return fallback
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", name).strip("_")
    if not cleaned:
        return fallback
    if cleaned[0].isdigit():
        cleaned = "t_" + cleaned
    return cleaned[:32]


def _unique_name(base, used):
    name = base
    n = 2
    while name in used:
        name = f"{base}_{n}"
        n += 1
    used.add(name)
    return name


# ---------------------------------------------------------------------------
# Voice -> ACML token stream
# ---------------------------------------------------------------------------

def _voice_to_events(voice, tpb):
    """Convert one monophonic voice into [(token, beats), ...]."""
    events = []
    current = 0.0

    for i, note in enumerate(voice):
        ns = note["start"] / tpb
        ne = note["end"] / tpb
        next_ns = voice[i + 1]["start"] / tpb if i + 1 < len(voice) else float("inf")

        # rests from current position up to this note's start
        gap = ns - current
        if gap > 0.125:
            for rt in _gap_to_rests(gap):
                d = _duration_value(rt.split(":")[1])
                events.append((rt, d))
                current += d
        # if gap < 0 (drift), skip - note plays immediately

        ideal = ne - ns
        dur_q = _quantize_duration(ideal)
        available = next_ns - current
        if available < _duration_value(dur_q) - 0.01:
            dur_q = _fit_duration(available)
            if _duration_value(dur_q) > available + 0.125 and available > 0.05:
                # even smallest duration overshoots significantly; accept it
                pass

        pitch_name = _midi_to_note_name(note["pitch"])
        dyn = _velocity_to_dynamic(note["velocity"])
        events.append((f"{pitch_name}:{dur_q}:{dyn}", _duration_value(dur_q)))
        current += _duration_value(dur_q)

    return events


def _drum_group_to_events(notes, tpb):
    """Convert a same-drum-type note list into [(token, beats), ...]."""
    notes = sorted(notes, key=lambda n: (n["start"], n["end"]))
    events = []
    current = 0.0

    for i, note in enumerate(notes):
        ns = note["start"] / tpb
        ne = note["end"] / tpb
        next_ns = notes[i + 1]["start"] / tpb if i + 1 < len(notes) else float("inf")

        gap = ns - current
        if gap > 0.125:
            for rt in _gap_to_rests(gap):
                d = _duration_value(rt.split(":")[1])
                events.append((rt, d))
                current += d

        ideal = ne - ns
        dur_q = _quantize_duration(ideal)
        available = next_ns - current
        if available < _duration_value(dur_q) - 0.01:
            dur_q = _fit_duration(available)

        drum = _DRUM_MAP.get(note["pitch"])
        if drum is None:
            continue  # unmapped percussion - skip (but time already advanced?)
        dyn = _velocity_to_dynamic(note["velocity"])
        events.append((f"{drum}:{dur_q}:{dyn}", _duration_value(dur_q)))
        current += _duration_value(dur_q)

    return events


# ---------------------------------------------------------------------------
# ACML emission
# ---------------------------------------------------------------------------

def _format_notes(events, beats_per_bar=4.0):
    """Group events into bar lines joined by ACML continuation '+'."""
    if not events:
        return "R:w:mf"

    # assign each event the absolute beat position where it starts
    pos = 0.0
    placed = []
    for token, dur in events:
        placed.append((token, dur, pos))
        pos += dur

    lines = []
    cur = []
    last_bar = 0
    for token, dur, start in placed:
        bar = int(start // beats_per_bar)
        if bar > last_bar and cur:
            lines.append(",".join(cur))
            cur = []
        cur.append(token)
        last_bar = bar
    if cur:
        lines.append(",".join(cur))

    if len(lines) == 1:
        return lines[0]
    return " +\n ".join(lines)


def midi_to_acml_text(midi_data, name="untitled"):
    """Convert parsed MIDI data to ACML text."""
    tpb = midi_data["ticks_per_beat"]
    bpm = int(round(midi_data["bpm"]))
    channels = midi_data["channels"]

    used_names = set()
    sections = []

    for channel in sorted(channels.keys()):
        info = channels[channel]
        notes = info["notes"]
        if not notes:
            continue

        if channel == 9:
            # drums: group by drum type
            groups = {}
            for n in notes:
                drum = _DRUM_MAP.get(n["pitch"])
                if drum is None:
                    continue
                groups.setdefault(drum, []).append(n)
            for drum in sorted(groups.keys(), key=lambda d: list(_DRUM_MAP.values()).index(d) if d in _DRUM_MAP.values() else 99):
                events = _drum_group_to_events(groups[drum], tpb)
                if not events:
                    continue
                base = _DRUM_TRACK_NAMES.get(drum, f"drum_{drum}")
                tname = _unique_name(base, used_names)
                notes_str = _format_notes(events)
                sections.append(
                    f"[track {tname}]\n"
                    f"instrument = drums\n"
                    f"notes = {notes_str}"
                )
            continue

        instrument = _gm_to_instrument(info.get("program", 0))
        voices = _split_voices(notes)
        if not voices:
            continue

        base = _sanitize_track_name(info.get("name"), f"ch{channel}")
        for vi, voice in enumerate(voices):
            events = _voice_to_events(voice, tpb)
            if not events:
                continue
            if len(voices) == 1:
                tname = _unique_name(base, used_names)
            else:
                tname = _unique_name(f"{base}_v{vi + 1}", used_names)
            notes_str = _format_notes(events)
            sections.append(
                f"[track {tname}]\n"
                f"instrument = {instrument}\n"
                f"notes = {notes_str}"
            )

    header = f"name = \"{name}\"\nbpm = {bpm}\n"
    return header + "\n" + "\n\n".join(sections) + "\n"


# ---------------------------------------------------------------------------
# Public entry
# ---------------------------------------------------------------------------

def convert(input_path, output_path=None):
    """Convert a MIDI file to ACML.

    Returns (acml_text, output_path).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"MIDI file not found: {input_path}")

    midi_data = parse_midi(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    acml_name = _sanitize_track_name(base_name, "converted")

    text = midi_to_acml_text(midi_data, name=acml_name)

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".acml"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text, output_path
