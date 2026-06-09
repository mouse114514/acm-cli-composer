import wave
import struct
import math
import re
import random

try:
    import cupy as _cupy_mod
    _HAS_CUPY = True
except ImportError:
    _HAS_CUPY = False
    _cupy_mod = None

try:
    import numpy as _numpy_mod
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False
    _numpy_mod = None

if _HAS_CUPY:
    _xp = _cupy_mod
elif _HAS_NUMPY:
    _xp = _numpy_mod
else:
    _xp = None

if _xp is not None:
    _sin = _xp.sin
    _exp = _xp.exp
    _sqrt = _xp.sqrt
else:
    _sin = math.sin
    _exp = math.exp
    _sqrt = math.sqrt

class Composer:
    SAMPLE_RATE = 44100
    NOTE_FREQUENCIES = {
        "C": 261.63, "C#": 277.18, "Db": 277.18,
        "D": 293.66, "D#": 311.13, "Eb": 311.13,
        "E": 329.63,
        "F": 349.23, "F#": 369.99, "Gb": 369.99,
        "G": 392.00, "G#": 415.30, "Ab": 415.30,
        "A": 440.00, "A#": 466.16, "Bb": 466.16,
        "B": 493.88,
    }
    PATTERNS = {
        "pop": [1, 0, 1, 0, 1, 0, 1, 0],
        "rock": [1, 0, 0, 1, 1, 0, 0, 1],
        "jazz": [1, 0, 1, 0, 0, 1, 0, 1],
        "trap": [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1],
        "latin": [1, 0, 1, 1, 0, 1, 0, 1],
        "funk": [1, 0, 1, 1, 0, 0, 1, 1],
        "shuffle": [1, 0, 1, 0, 1, 1, 0, 1],
    }

    _SEMITONE_TO_NOTE = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    _NOTE_TO_SEMITONE = {n: i for i, n in enumerate(_SEMITONE_TO_NOTE)}
    _SCALE_SEMITONES = {  # intervals from root
        "major": [0, 2, 4, 5, 7, 9, 11],
        "minor": [0, 2, 3, 5, 7, 8, 10],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    }

    _CHORD_SEMITONES = {  # intervals from root
        "maj": [0, 4, 7],
        "m": [0, 3, 7],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8],
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
        "6": [0, 4, 7, 9],
        "m6": [0, 3, 7, 9],
        "7": [0, 4, 7, 10],
        "maj7": [0, 4, 7, 11],
        "m7": [0, 3, 7, 10],
        "dim7": [0, 3, 6, 9],
        "m7b5": [0, 3, 6, 10],
        "aug7": [0, 4, 8, 10],
        "9": [0, 4, 7, 10, 14],
        "maj9": [0, 4, 7, 11, 14],
        "m9": [0, 3, 7, 10, 14],
        "add9": [0, 4, 7, 14],
    }

    _GM_INSTRUMENTS = {
        "piano": 0, "guitar": 26, "bass": 34, "sawtooth": 81,
        "organ": 16, "bell": 14, "strings": 48, "brass": 61,
        "pad": 88, "lead": 82, "fm": 81, "wavetable": 89,
        "trumpet": 56, "tuba": 58, "sample": 0,
    }

    _CHORD_TYPE_NAMES = sorted(_CHORD_SEMITONES.keys(), key=lambda k: -len(k))

    _HARMONY_INTERVALS = {
        "3": 4, "3below": -4, "5": 7, "6": 9,
        "octave": 12, "octavebelow": -12,
        "4": 5, "2": 2, "7": 10,
        "unison": 0,
    }

    _WAVETABLE_SIZE = 2048

    @staticmethod
    def _build_wavetable(shape):
        if shape in ("saw", "square", "triangle", "sine"):
            n = Composer._WAVETABLE_SIZE
            wt = [0.0] * n
            if shape == "saw":
                for i in range(n):
                    wt[i] = 2.0 * i / n - 1.0
            elif shape == "square":
                half = n // 2
                for i in range(n):
                    wt[i] = 1.0 if i < half else -1.0
            elif shape == "triangle":
                half = n // 2
                for i in range(n):
                    wt[i] = 2.0 * i / half - 1.0 if i < half else 2.0 - 2.0 * i / half
            elif shape == "sine":
                for i in range(n):
                    wt[i] = _sin(2 * math.pi * i / n)
            return wt
        try:
            vals = [float(x) for x in shape.split(",")]
            return vals
        except (ValueError, TypeError):
            return Composer._build_wavetable("saw")

    @staticmethod
    def _wavetable_lookup(table, phase):
        if _xp is not None and hasattr(phase, '__len__'):
            idx = phase * (len(table) - 1)
            i0 = _xp.clip(_xp.floor(idx).astype(_xp.intp), 0, len(table) - 2)
            i1 = i0 + 1
            frac = idx - i0
            t = _xp.array(table)
            return t[i0] + frac * (t[i1] - t[i0])
        idx = phase * (len(table) - 1)
        i0 = int(idx)
        i1 = min(i0 + 1, len(table) - 1)
        frac = idx - i0
        return table[i0] + frac * (table[i1] - table[i0])

    def __init__(self, bpm=120, duration=4):
        self.tracks = []
        self.bpm = bpm
        self.duration = duration

    def add_track(self, track):
        self.tracks.append(track)

    def _resolve_pattern(self, pattern_str):
        if pattern_str in self.PATTERNS:
            return self.PATTERNS[pattern_str]
        return [int(c) for c in pattern_str if c in "01"]

    def _get_waveform(self, instrument, t, freq, wavetable_type=None, fm_ratio=None, fm_index=None):
        if instrument == "bass":
            phase = (freq * t) % 1.0
            return 2.0 * phase - 1.0
        if instrument == "guitar":
            s = _sin(2 * math.pi * freq * t)
            h3 = _sin(2 * math.pi * freq * 3 * t)
            return 0.5 * s + 0.25 * h3
        if instrument == "sawtooth":
            phase = (freq * t) % 1.0
            return 2.0 * phase - 1.0
        if instrument == "organ":
            s = _sin(2 * math.pi * freq * t)
            h2 = _sin(2 * math.pi * freq * 2 * t)
            h3 = _sin(2 * math.pi * freq * 3 * t)
            h4 = _sin(2 * math.pi * freq * 4 * t)
            return 0.3 * s + 0.25 * h2 + 0.2 * h3 + 0.15 * h4
        if instrument == "bell":
            s = _sin(2 * math.pi * freq * t)
            h3 = _sin(2 * math.pi * freq * 3 * t)
            h5 = _sin(2 * math.pi * freq * 5 * t)
            if _xp is not None:
                env = _xp.maximum(0, 1 - t * 2)
            else:
                env = max(0, 1 - t * 2)
            return (0.4 * s + 0.3 * h3 + 0.2 * h5) * env
        if instrument == "strings":
            s = _sin(2 * math.pi * freq * t)
            h2 = _sin(2 * math.pi * freq * 2 * t)
            h3 = _sin(2 * math.pi * freq * 3 * t)
            h4 = _sin(2 * math.pi * freq * 4 * t)
            return 0.4 * s + 0.3 * h2 + 0.2 * h3 + 0.1 * h4
        if instrument == "brass":
            phase = (freq * t) % 1.0
            if _xp is not None:
                sq = _xp.where(phase < 0.5, 1.0, -1.0)
            else:
                sq = 1.0 if phase < 0.5 else -1.0
            h3 = _sin(2 * math.pi * freq * 3 * t)
            return 0.5 * sq + 0.3 * h3
        if instrument == "trumpet":
            s = _sin(2 * math.pi * freq * t)
            h2 = _sin(2 * math.pi * freq * 2 * t)
            h3 = _sin(2 * math.pi * freq * 3 * t)
            h4 = _sin(2 * math.pi * freq * 4 * t)
            h5 = _sin(2 * math.pi * freq * 5 * t)
            h6 = _sin(2 * math.pi * freq * 6 * t)
            return 0.35 * s + 0.30 * h2 + 0.50 * h3 + 0.25 * h4 + 0.15 * h5 + 0.08 * h6
        if instrument == "tuba":
            s = _sin(2 * math.pi * freq * t)
            h2 = _sin(2 * math.pi * freq * 2 * t)
            h3 = _sin(2 * math.pi * freq * 3 * t)
            h4 = _sin(2 * math.pi * freq * 4 * t)
            return 1.0 * s + 0.45 * h2 + 0.20 * h3 + 0.08 * h4
        if instrument == "pad":
            d1 = _sin(2 * math.pi * freq * t)
            d2 = _sin(2 * math.pi * freq * 1.01 * t)
            return 0.5 * d1 + 0.3 * d2
        if instrument == "lead":
            phase = (freq * t) % 1.0
            s = 2.0 * phase - 1.0
            h3 = _sin(2 * math.pi * freq * 3 * t)
            return 0.6 * s + 0.3 * h3
        if instrument == "fm":
            ratio = fm_ratio if fm_ratio is not None else (getattr(self, "_active_fm_ratio", None) or 2.0)
            idx = fm_index if fm_index is not None else (getattr(self, "_active_fm_index", None) or 3.0)
            mod = _sin(2 * math.pi * freq * ratio * t)
            return _sin(2 * math.pi * freq * t + idx * mod)
        if instrument == "wavetable":
            phase = (freq * t) % 1.0
            wt = wavetable_type or getattr(self, "_active_wavetable", "saw")
            table = self._build_wavetable(wt)
            return self._wavetable_lookup(table, phase)
        return _sin(2 * math.pi * freq * t)

    @staticmethod
    def _pan_gains(pan):
        angle = (pan + 1.0) * math.pi / 4.0
        return math.cos(angle), _sin(angle)

    @staticmethod
    def _soft_clip(samples):
        if _xp is not None and not isinstance(samples, list):
            return _xp.tanh(samples)
        return [math.tanh(s) for s in samples]

    def _compute_beat_starts(self, beats, samples_per_beat, durations_str=None):
        if durations_str:
            ratios = [max(float(d), 0.01) for d in durations_str.split(",")]
            total_ratio = sum(ratios)
            starts = []
            pos = 0
            for r in ratios:
                starts.append(pos)
                pos += int(samples_per_beat * r / total_ratio)
            starts.append(pos)
            return starts
        return [i * samples_per_beat for i in range(beats + 1)]

    @staticmethod
    def _parse_duration(dur_str):
        base = dur_str[0].lower()
        dotted = len(dur_str) > 1 and dur_str[1] == "."
        m = {"w": 4.0, "h": 2.0, "q": 1.0, "e": 0.5, "s": 0.25}
        val = m.get(base, 1.0)
        return val * 1.5 if dotted else val

    @staticmethod
    def _parse_dynamic(dyn_str):
        try:
            return float(dyn_str)
        except ValueError:
            pass
        m = {"ppp": 0.2, "pp": 0.25, "p": 0.35, "mp": 0.5, "mf": 0.65, "f": 0.8, "ff": 0.9, "fff": 1.0}
        return m.get(dyn_str.lower(), 0.65)

    @staticmethod
    def _is_extended_notes(notes_str):
        for part in notes_str.split(","):
            part = part.strip()
            if ":" in part:
                parts = part.split(":")
                if len(parts) >= 2 and parts[1] and parts[1][0] in "whqesWHQES":
                    return True
        return False

    # ---- Arpeggio --------------------------------------------------------------------------------

    def _get_scale_freqs(self, root_name, scale_type="major", octave=4):
        root_semi = self._NOTE_TO_SEMITONE.get(root_name.upper(), 0)
        intervals = self._SCALE_SEMITONES.get(scale_type, self._SCALE_SEMITONES["major"])
        freqs = []
        for interval in intervals:
            semi = root_semi + interval
            note_name = self._SEMITONE_TO_NOTE[semi % 12]
            note_oct = octave + semi // 12
            base = self.NOTE_FREQUENCIES[note_name]
            freqs.append(base * (2 ** (note_oct - 4)))
        return freqs

    def _generate_arpeggio(self, freqs, mode, pattern, beat_starts, total_samples, instrument="piano"):
        data = [0.0] * total_samples
        sr = self.SAMPLE_RATE
        n_beats = min(len(pattern), len(beat_starts) - 1)
        n = len(freqs)
        if n == 0:
            return data
        # build sequence
        if mode == "up":
            seq = list(range(n))
        elif mode == "down":
            seq = list(range(n - 1, -1, -1))
        elif mode == "updown":
            seq = list(range(n)) + list(range(n - 2, 0, -1))
        elif mode == "downup":
            seq = list(range(n - 1, -1, -1)) + list(range(1, n - 1))
        elif mode == "random":
            rng = random.Random(42)
            seq = [rng.randint(0, n - 1) for _ in range(200)]
        else:
            seq = list(range(n))
        arp_idx = 0
        for beat in range(n_beats):
            if pattern[beat]:
                freq = freqs[seq[arp_idx % len(seq)]]
                arp_idx += 1
                start = beat_starts[beat]
                end = beat_starts[beat + 1]
                length = end - start
                for i in range(length):
                    t = (start + i) / sr
                    env = _exp(-i / (length * 0.3))
                    data[start + i] = self._get_waveform(instrument, t, freq) * env
        return data

    # ---- Chord Notation --------------------------------------------------------------------

    @staticmethod
    def _is_chord_name(name):
        if not name or name[0] not in "ABCDEFG":
            return False
        i = 1
        if len(name) > 1 and name[1] in "#b":
            i = 2
        suffix = name[i:]
        if not suffix:
            return False
        if suffix in Composer._CHORD_SEMITONES:
            return True
        # Try greedy: consume all leading digits as octave
        j = 0
        while j < len(suffix) and suffix[j].isdigit():
            j += 1
        rest = suffix[j:]
        if rest and rest in Composer._CHORD_SEMITONES:
            return True
        # Try non-greedy: first 1-2 digits as octave, rest as chord type
        for k in range(1, min(3, len(suffix))):
            if suffix[:k].isdigit():
                rest = suffix[k:]
                if rest and rest in Composer._CHORD_SEMITONES:
                    return True
        # Try chord-type-first: consume leading alpha as chord type, rest as octave
        j = 0
        while j < len(suffix) and suffix[j].isalpha():
            j += 1
        if j > 0:
            ctype = suffix[:j]
            rest = suffix[j:]
            if ctype in Composer._CHORD_SEMITONES:
                return True
        return False

    @staticmethod
    def _parse_chord_name(chord_str):
        i = 1
        if len(chord_str) > 1 and chord_str[1] in "#b":
            i = 2
        root = chord_str[:i]
        suffix = chord_str[i:]
        if suffix in Composer._CHORD_SEMITONES:
            return root, 4, suffix
        # Greedy: consume all leading digits as octave
        j = 0
        while j < len(suffix) and suffix[j].isdigit():
            j += 1
        rest = suffix[j:]
        if rest and rest in Composer._CHORD_SEMITONES:
            return root, int(suffix[:j]) if j > 0 else 4, rest
        # Non-greedy: first digit as octave, rest as chord type
        for k in range(1, min(3, len(suffix))):
            if suffix[:k].isdigit():
                rest = suffix[k:]
                if rest and rest in Composer._CHORD_SEMITONES:
                    return root, int(suffix[:k]), rest
        # Chord-type-first: leading alpha as chord type, rest as octave
        j = 0
        while j < len(suffix) and suffix[j].isalpha():
            j += 1
        if j > 0:
            ctype = suffix[:j]
            rest = suffix[j:]
            if ctype in Composer._CHORD_SEMITONES:
                octv = int(rest) if rest and rest.isdigit() else 4
                return root, octv, ctype
        return root, 4, suffix

    @staticmethod
    def _chord_intervals_to_names(root, intervals, root_octave=4):
        root_semi = Composer._NOTE_TO_SEMITONE.get(root, 0)
        result = []
        for interval in intervals:
            semi = root_semi + interval
            note = Composer._SEMITONE_TO_NOTE[semi % 12]
            octv = root_octave + semi // 12
            result.append(f"{note}{octv}")
        return result

    @staticmethod
    def _subdivide_duration(dur_str, n):
        base = dur_str[0].lower()
        dotted = len(dur_str) > 1 and dur_str[1] == "."
        m = {"w": 4.0, "h": 2.0, "q": 1.0, "e": 0.5, "s": 0.25}
        total = m.get(base, 1.0) * (1.5 if dotted else 1.0)
        each = total / n
        rev = {}
        for k, v in m.items():
            rev[v] = k
        for k, v in m.items():
            rev[v * 1.5] = k + "."
        best = "s"
        best_diff = float("inf")
        for val, ds in rev.items():
            diff = abs(each - val)
            if diff < best_diff:
                best_diff = diff
                best = ds
        return best

    def analyze_chords(self, track_index, beats_per_bar=4):
        track = self.tracks[track_index]
        if not track.notes or not self._is_extended_notes(track.notes):
            return []
        notes = [n.strip() for n in track.notes.split(",") if n.strip()]
        parsed = []
        pos_beats = 0.0
        for expr in notes:
            parts = expr.split(":")
            note_part = parts[0]
            dur_str = parts[1] if len(parts) >= 2 else "q"
            dur = self._parse_duration(dur_str) if dur_str and dur_str[0] in "whqesWHQES" else 1.0
            if note_part not in ("R", "_"):
                midi = self._note_name_to_midi(note_part)
                pc = midi % 12
                parsed.append((pc, pos_beats, dur))
            pos_beats += dur
        if not parsed:
            return []
        total_beats = pos_beats
        num_bars = max(1, int(total_beats / beats_per_bar))
        chords = []
        for bar in range(num_bars):
            bar_start = bar * beats_per_bar
            bar_end = (bar + 1) * beats_per_bar
            pcs_in_bar = set()
            for pc, pos, dur in parsed:
                if pos < bar_end and pos + dur > bar_start:
                    pcs_in_bar.add(pc)
            if not pcs_in_bar:
                chords.append("N.C.")
                continue
            best_chord = "maj"
            best_score = -1
            for chord_name, intervals in self._CHORD_SEMITONES.items():
                chord_pcs = set(i % 12 for i in intervals)
                score = len(pcs_in_bar & chord_pcs)
                if score > best_score:
                    best_score = score
                    best_chord = chord_name
            best_root = "C"
            best_root_score = -1
            for root_pc in range(12):
                root_name = self._SEMITONE_TO_NOTE[root_pc]
                chord_intervals = self._CHORD_SEMITONES.get(best_chord, [0, 4, 7])
                chord_pcs = set((root_pc + i) % 12 for i in chord_intervals)
                score = len(pcs_in_bar & chord_pcs)
                if score > best_root_score:
                    best_root_score = score
                    best_root = root_name
            chords.append(f"{best_root}{best_chord}")
        return chords

    @staticmethod
    def _expand_chord(expr):
        parts = expr.split(":")
        chord_name = parts[0]
        dur = parts[1] if len(parts) > 1 else "q"
        dyn = parts[2] if len(parts) > 2 else "mf"
        root, octave, chord_type = Composer._parse_chord_name(chord_name)
        intervals = Composer._CHORD_SEMITONES.get(chord_type)
        if intervals is None:
            intervals = [0, 4, 7]
        note_names = Composer._chord_intervals_to_names(root, intervals, octave)
        inner = ",".join(note_names)
        return f"({inner}):{dur}:{dyn}"

    _COMPACT_RE = re.compile(
        r"^([A-Ga-g][#b]?)"     # note (C, C#, Bb)
        r"([a-z]*)"              # chord type (m, maj7, dim, etc.)
        r"(\d*)"                  # octave
        r"([whqes]\.?)"          # duration + optional dot
        r"(?:\(([^)]+)\)|([a-z]*))?$"  # dynamic: (mf) or f
    )

    _DRUM_TYPES = set("KSHOT")

    @staticmethod
    def expand_compact_notes(notes_str):
        """Convert 'D5qf' -> 'D5:q:f', 'Kf' -> 'K:q:f', '.' -> 'R:q'.
        Chord 'Gm3' -> '(G3,Bb3,D4):q:mf'.  Trailing notes with same
        duration/dynamics in the same bar merge into the chord group.
        Bars are separated by ',,' (inserted by ACML continuation lines).
        """
        # Split by bar boundaries (,,), then by note boundaries (,)
        bars = notes_str.split(",,")

        expanded = []
        for bar in bars:
            raw_groups = [g.strip() for g in bar.split(",") if g.strip()]
            bar_items = []
            for group in raw_groups:
                items = Composer._expand_one_group(group)
                bar_items.extend(items)

            # Merge: chord absorbs trailing notes with same dur+dyn within bar
            merged_bar = []
            i = 0
            while i < len(bar_items):
                item = bar_items[i]
                if item.startswith("(") and ":" in item:
                    paren_end = item.index(")")
                    inner = item[1:paren_end]
                    rest_str = item[paren_end + 1:]
                    parts_r = rest_str.split(":")
                    dur = parts_r[1] if len(parts_r) > 1 else "q"
                    dyn = parts_r[2] if len(parts_r) > 2 else "mf"
                    notes = inner.split(",")
                    j = i + 1
                    while j < len(bar_items):
                        nxt = bar_items[j]
                        if nxt.startswith("(") or nxt.startswith("R:") or (len(nxt) > 1 and nxt[0] in "KSHOT"):
                            break
                        n_parts = nxt.split(":")
                        if len(n_parts) >= 3 and n_parts[1] == dur and n_parts[2] == dyn:
                            notes.append(n_parts[0])
                            j += 1
                        else:
                            break
                    merged_bar.append(f"({','.join(notes)}):{dur}:{dyn}")
                    i = j
                else:
                    merged_bar.append(item)
                    i += 1
            expanded.extend(merged_bar)
        return ",".join(expanded)

    @staticmethod
    def _expand_one_group(part):
        """Expand a single comma-group (may be a chord with trailing notes)."""
        if part == ".":
            return ["R:q"]
        if ":" in part:
            chord_candidate = part.split(":")[0]
            _i = 1
            if len(chord_candidate) > 1 and chord_candidate[1] in "#b":
                _i = 2
            _suffix = chord_candidate[_i:]
            if _suffix.isdigit() and len(_suffix) <= 2 and int(_suffix) <= 9:
                rest = ":".join(part.split(":")[1:])
                if rest and rest[0] in "whqesWHQES":
                    return [part]
            if Composer._is_chord_name(chord_candidate):
                return [Composer._expand_chord(part)]
            return [part]
        if part[0] in Composer._DRUM_TYPES:
            note = part[0]
            suffix = part[1:]
            dur_char = suffix[0] if suffix and suffix[0] in "whqes" else "q"
            dur = dur_char
            rest = suffix[1:] if suffix.startswith(dur_char) else suffix
            if rest and rest[0] == ".":
                dur += "."
                rest = rest[1:]
            dyn = rest if rest else "mf"
            return [f"{note}:{dur}:{dyn}"]
        if part[0].upper() == "R":
            suffix = part[1:]
            dur_char = suffix[0] if suffix and suffix[0] in "whqes" else "q"
            dur = dur_char
            rest = suffix[1:] if suffix.startswith(dur_char) else suffix
            if rest and rest[0] == ".":
                dur += "."
                rest = rest[1:]
            return [f"R:{dur}:mf"]
        m = Composer._COMPACT_RE.match(part)
        if m:
            note = m.group(1)
            ctype = m.group(2)
            octave = m.group(3) or "4"
            dur = m.group(4)
            dyn = m.group(5) or m.group(6) or "mf"
            if ctype and ctype in Composer._CHORD_SEMITONES:
                return [Composer._expand_chord(f"{note}{ctype}{octave}:{dur}:{dyn}")]
            return [f"{note}{octave}:{dur}:{dyn}"]
        m2 = re.match(r"^([A-G][#b]?[a-z0-9]*?)([whqes]\.?)([a-z]*)$", part)
        if m2 and Composer._is_chord_name(m2.group(1)):
            chord_n = m2.group(1)
            dur = m2.group(2)
            dyn = m2.group(3) or "mf"
            return [Composer._expand_chord(f"{chord_n}:{dur}:{dyn}")]
        if Composer._is_chord_name(part):
            return [Composer._expand_chord(f"{part}:q:mf")]
        return [part]

    def _parse_extended_note(self, expr):
        expr = expr.strip()
        parts = expr.split(":")
        note_part = parts[0]
        if not note_part or note_part in ("R", "_"):
            dur = self._parse_duration(parts[1]) if len(parts) >= 2 else 1.0
            return None, dur, 0
        if len(parts) == 1:
            return self._note_name_to_freq(note_part), 1.0, 1.0
        if parts[1] and parts[1][0] in "whqesWHQES":
            dur = self._parse_duration(parts[1])
            vel = self._parse_dynamic(parts[2]) if len(parts) > 2 else 0.65
            return self._note_name_to_freq(note_part), dur, vel
        return self._note_name_to_freq(note_part), 1.0, float(parts[1])

    def _generate_melody_from_extended_notes(self, notes_str, total_samples, instrument="piano"):
        notes = [n.strip() for n in notes_str.split(",") if n.strip()]
        if _xp is not None:
            data = _xp.zeros(total_samples)
        else:
            data = [0.0] * total_samples
        sr = self.SAMPLE_RATE
        spb = int(sr * 60 / self.bpm)
        pos = 0
        for expr in notes:
            if not expr:
                continue
            freq, beat_frac, velocity = self._parse_extended_note(expr)
            nsamples = int(beat_frac * spb)
            if pos + nsamples > total_samples:
                nsamples = total_samples - pos
            if nsamples <= 0:
                break
            if freq is not None:
                if _xp is not None:
                    i = _xp.arange(nsamples)
                    t = (pos + i) / sr
                    env = _exp(-i / (nsamples * 0.3))
                    data[pos:pos + nsamples] = self._get_waveform(instrument, t, freq) * env * velocity
                else:
                    for i in range(nsamples):
                        t = (pos + i) / sr
                        envelope = _exp(-i / (nsamples * 0.3))
                        data[pos + i] = self._get_waveform(instrument, t, freq) * envelope * velocity
            pos += nsamples
        if _xp is not None and _HAS_CUPY:
            data = data.get()
        return data

    @staticmethod
    def _load_sample(path):
        import struct
        with wave.open(path) as wf:
            n = wf.getnframes()
            nch = wf.getnchannels()
            sw = wf.getsampwidth()
            raw = wf.readframes(n)
            total_samples = n * nch
            if sw == 2:
                fmt = "<" + "h" * total_samples
                interleaved = [v / 32768.0 for v in struct.unpack(fmt, raw)]
            else:
                fmt = "<" + "B" * total_samples
                interleaved = [(v - 128) / 128.0 for v in struct.unpack(fmt, raw)]
        if nch == 1:
            return interleaved
        # mix down multi-channel to mono
        mono = [0.0] * n
        for i in range(n):
            s = 0.0
            for ch in range(nch):
                s += interleaved[i * nch + ch]
            mono[i] = s / nch
        return mono

    @staticmethod
    def _resample(samples, ratio):
        if abs(ratio - 1.0) < 1e-6:
            return samples[:]
        out_len = max(1, int(len(samples) / ratio))
        result = [0.0] * out_len
        for i in range(out_len):
            src_idx = i * ratio
            i0 = int(src_idx)
            i1 = min(i0 + 1, len(samples) - 1)
            frac = src_idx - i0
            result[i] = samples[i0] + frac * (samples[i1] - samples[i0])
        return result

    def _generate_harmony_from_extended_notes(self, notes_str, total_samples, instrument, semitones):
        notes = [n.strip() for n in notes_str.split(",") if n.strip()]
        if _xp is not None:
            data = _xp.zeros(total_samples)
        else:
            data = [0.0] * total_samples
        sr = self.SAMPLE_RATE
        spb = int(sr * 60 / self.bpm)
        pos = 0
        for expr in notes:
            if not expr:
                continue
            freq, beat_frac, velocity = self._parse_extended_note(expr)
            nsamples = int(beat_frac * spb)
            if pos + nsamples > total_samples:
                nsamples = total_samples - pos
            if nsamples <= 0:
                break
            if freq is not None:
                harm_freq = freq * (2 ** (semitones / 12.0))
                if _xp is not None:
                    i = _xp.arange(nsamples)
                    t = (pos + i) / sr
                    env = _exp(-i / (nsamples * 0.3))
                    data[pos:pos + nsamples] = self._get_waveform(instrument, t, harm_freq) * env * velocity
                else:
                    for i in range(nsamples):
                        t = (pos + i) / sr
                        envelope = _exp(-i / (nsamples * 0.3))
                        data[pos + i] = self._get_waveform(instrument, t, harm_freq) * envelope * velocity
            pos += nsamples
        if _xp is not None and _HAS_CUPY:
            data = data.get()
        return data

    def _generate_sample_from_extended_notes(self, notes_str, total_samples, sample_path, sample_pitch="C4"):
        sample_audio = self._load_sample(sample_path)
        base_freq = self._note_name_to_freq(sample_pitch)
        notes = [n.strip() for n in notes_str.split(",") if n.strip()]
        if _xp is not None:
            data = _xp.zeros(total_samples)
        else:
            data = [0.0] * total_samples
        sr = self.SAMPLE_RATE
        spb = int(sr * 60 / self.bpm)
        pos = 0
        for expr in notes:
            freq, beat_frac, velocity = self._parse_extended_note(expr)
            nsamples = int(beat_frac * spb)
            if pos + nsamples > total_samples:
                nsamples = total_samples - pos
            if nsamples <= 0:
                break
            if freq is not None:
                ratio = freq / base_freq
                resampled = self._resample(sample_audio, ratio)
                copy_len = min(nsamples, len(resampled))
                if _xp is not None:
                    env = _exp(-_xp.arange(copy_len, dtype=_xp.float64) / (nsamples * 0.3))
                    data[pos:pos + copy_len] = _xp.array(resampled[:copy_len]) * env * velocity
                else:
                    for i in range(copy_len):
                        env = _exp(-i / (nsamples * 0.3))
                        data[pos + i] = resampled[i] * env * velocity
            pos += nsamples
        if _xp is not None and _HAS_CUPY:
            data = data.get()
        return data

    def _repeat_notes(self, notes_str, loops):
        if loops <= 1 or not notes_str:
            return notes_str
        return ",".join([notes_str] * loops)

    def _repeat_pattern(self, pattern, loops):
        if loops <= 1:
            return pattern
        return pattern * loops

    def generate(self, output_path, midi_path=None, reverb=0.0, delay=0.0, chorus=0.0, loop=1, trim=True):
        spb = int(self.SAMPLE_RATE * 60 / self.bpm)
        max_beats = 1
        total_ext_beats = 0.0
        has_extended = False
        serial_total_samples = 0
        for track in self.tracks:
            loops = getattr(track, "loops", 1) or 1
            mode = getattr(track, "mode", "parallel")
            self._active_wavetable = getattr(track, "wavetable", None) or "saw"
            self._active_fm_ratio = getattr(track, "fm_ratio", None)
            self._active_fm_index = getattr(track, "fm_index", None)
            if track.notes and self._is_extended_notes(track.notes):
                has_extended = True
                track_beats = 0.0
                note_str = self._repeat_notes(track.notes, loops)
                for expr in note_str.split(","):
                    expr = expr.strip()
                    if expr and ":" in expr:
                        parts = expr.split(":")
                        if len(parts) >= 2 and parts[1] and parts[1][0] in "whqesWHQES":
                            track_beats += self._parse_duration(parts[1])
                        else:
                            track_beats += 1.0
                    elif expr:
                        track_beats += 1.0
                if mode == "serial":
                    serial_total_samples += int(spb * track_beats)
                elif track_beats > total_ext_beats:
                    total_ext_beats = track_beats
            else:
                pat = self._resolve_pattern(track.pattern if track.pattern else "pop")
                pat = self._repeat_pattern(pat, loops)
                if mode == "serial":
                    serial_total_samples += spb * len(pat)
                elif len(pat) > max_beats:
                    max_beats = len(pat)
        serial_total_samples *= loop
        if has_extended:
            parallel_samples = min(int(spb * total_ext_beats), self.SAMPLE_RATE * self.duration)
        else:
            parallel_samples = min(spb * max_beats, self.SAMPLE_RATE * self.duration)
        total_samples = max(parallel_samples, serial_total_samples)
        if _xp is not None:
            left = _xp.zeros(total_samples)
            right = _xp.zeros(total_samples)
        else:
            left = [0.0] * total_samples
            right = [0.0] * total_samples

        serial_offset = 0
        for loop_idx in range(loop):
            for track in self.tracks:
                mode = getattr(track, "mode", "parallel")
                if mode == "parallel" and loop_idx > 0:
                    continue
                loops = getattr(track, "loops", 1) or 1
                notes_str = self._repeat_notes(track.notes, loops) if track.notes else None
                if notes_str and self._is_extended_notes(notes_str) and track.instrument == "sample":
                    beat_data = self._generate_sample_from_extended_notes(
                        notes_str, total_samples, track.sample,
                        getattr(track, "sample_pitch", None) or "C4"
                    )
                elif notes_str and self._is_extended_notes(notes_str) and track.instrument == "drums":
                    beat_data = self._generate_drums_from_extended_notes(notes_str, total_samples)
                elif track.instrument == "drums":
                    pattern = self._resolve_pattern(track.pattern if track.pattern else "pop")
                    pattern = self._repeat_pattern(pattern, loops)
                    beats = len(pattern)
                    beat_starts = self._compute_beat_starts(beats, spb, track.durations)
                    beat_starts = [s for s in beat_starts if s < total_samples]
                    beat_starts.append(total_samples)
                    beat_data = self._generate_drum_beat(beat_starts, total_samples, track.kick, track.snare, track.hihat)
                elif notes_str and self._is_extended_notes(notes_str):
                    beat_data = self._generate_melody_from_extended_notes(notes_str, total_samples, track.instrument)
                else:
                    pattern = self._resolve_pattern(track.pattern if track.pattern else "pop")
                    pattern = self._repeat_pattern(pattern, loops)
                    beats = len(pattern)
                    beat_starts = self._compute_beat_starts(beats, spb, track.durations)
                    beat_starts = [s for s in beat_starts if s < total_samples]
                    beat_starts.append(total_samples)
                    if getattr(track, "arpeggio", None) and track.arpeggio in ("up", "down", "random", "updown", "downup"):
                        scale_freqs = self._get_scale_freqs(track.scale or "C", "major", track.octave or 4)
                        beat_data = self._generate_arpeggio(scale_freqs, track.arpeggio, pattern, beat_starts, total_samples, track.instrument)
                    elif track.notes:
                        beat_data = self._generate_melody_from_notes(notes_str if notes_str else track.notes, pattern, beat_starts, total_samples, track.instrument)
                    else:
                        base_freq = self.NOTE_FREQUENCIES.get(track.scale, 440.0)
                        freq = base_freq * (2 ** (track.octave - 4))
                        beat_data = self._generate_melody(freq, pattern, beat_starts, total_samples, track.instrument)

                harm_interval = getattr(track, "harmony", None)
                if harm_interval and track.instrument not in ("drums", "sample"):
                    semitones = self._HARMONY_INTERVALS.get(harm_interval, 4)
                    if notes_str and self._is_extended_notes(notes_str):
                        harm_data = self._generate_harmony_from_extended_notes(
                            notes_str, total_samples, track.instrument, semitones
                        )
                    elif not getattr(track, "arpeggio", None):
                        harm_freq = freq * (2 ** (semitones / 12.0))
                        harm_data = self._generate_melody(harm_freq, pattern, beat_starts, total_samples, track.instrument)
                    else:
                        harm_data = None
                    if harm_data is not None:
                        limit_h = min(len(beat_data), len(harm_data))
                        if _xp is not None and not isinstance(beat_data, list):
                            beat_data[:limit_h] += harm_data[:limit_h] * 0.6
                        else:
                            for i in range(limit_h):
                                beat_data[i] += harm_data[i] * 0.6

                vol = getattr(track, "volume", 1.0)
                pan = getattr(track, "pan", 0.0)
                lg, rg = self._pan_gains(pan)
                offset = serial_offset if mode == "serial" else 0
                if mode == "serial":
                    serial_offset += len(beat_data)
                limit = min(total_samples - offset, len(beat_data))
                if _xp is not None and not isinstance(beat_data, list):
                    left[offset:offset + limit] += beat_data[:limit] * vol * lg
                    right[offset:offset + limit] += beat_data[:limit] * vol * rg
                else:
                    for i in range(limit):
                        s = beat_data[i] * vol
                        left[offset + i] += s * lg
                        right[offset + i] += s * rg

        if reverb > 0:
            left, right = self._apply_reverb(left, right, reverb)
        if delay > 0:
            left, right = self._apply_delay(left, right, delay)
        if chorus > 0:
            left, right = self._apply_chorus(left, right, chorus)

        if trim:
            left, right = self._trim_trailing_silence(left, right)

        self._write_stereo_wav(output_path, self._soft_clip(left), self._soft_clip(right))

        if midi_path:
            self.write_midi(midi_path, loop=loop, max_secs=total_samples / self.SAMPLE_RATE)
    def _trim_trailing_silence(self, left, right, threshold=0.003, padding_sec=0.12):
        """Trim trailing silence from both channels.
        threshold: amplitude below which is considered silence (default 0.003 ≈ -50 dBFS).
        padding_sec: audio to keep after last detected sound for decay tails.
        """
        n = len(left)
        if n == 0:
            return left, right
        padding = int(self.SAMPLE_RATE * padding_sec)
        last_sound = 0
        if _xp is not None and not isinstance(left, list):
            abs_max = _xp.maximum(_xp.abs(left), _xp.abs(right))
            indices = _xp.where(abs_max > threshold)[0]
            if len(indices) > 0:
                last_sound = int(indices[-1]) + padding
        else:
            for i in range(n - 1, -1, -1):
                if abs(left[i]) > threshold or abs(right[i]) > threshold:
                    last_sound = i + padding
                    break
        trim_to = min(last_sound, n)
        if trim_to < n:
            return left[:trim_to], right[:trim_to]
        return left, right
        trim_to = min(last_sound, n)
        if trim_to < n:
            return left[:trim_to], right[:trim_to]
        return left, right

    def _write_stereo_wav(self, output_path, left, right):
        with wave.open(output_path, "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(self.SAMPLE_RATE)
            if _xp is not None and not isinstance(left, list):
                frames = _xp.column_stack((
                    _xp.clip(_xp.round(left * 32767), -32768, 32767).astype(_xp.int16),
                    _xp.clip(_xp.round(right * 32767), -32768, 32767).astype(_xp.int16),
                ))
                wf.writeframes(frames.tobytes())
            else:
                for l, r in zip(left, right):
                    wf.writeframes(struct.pack("<hh", int(l * 32767), int(r * 32767)))

    # ---- Effects ------------------------------------------------

    @staticmethod
    def _apply_delay(left, right, wet=0.3, delay_time=0.3, feedback=0.4):
        sr = 44100
        delay_samples = int(sr * delay_time)
        out_l, out_r = left[:], right[:]
        for i in range(delay_samples, len(left)):
            out_l[i] += out_l[i - delay_samples] * feedback
            out_r[i] += out_r[i - delay_samples] * feedback
        dry = 1.0 - wet
        return ([left[i] * dry + out_l[i] * wet for i in range(len(left))],
                [right[i] * dry + out_r[i] * wet for i in range(len(right))])

    @staticmethod
    def _apply_reverb(left, right, wet=0.3, decay=0.5):
        sr = 44100
        delays = [int(sr * d) for d in [0.03, 0.037, 0.041, 0.047]]
        out_l, out_r = [0.0] * len(left), [0.0] * len(right)
        for delay in delays:
            for ch in [(left, out_l), (right, out_r)]:
                src, dst = ch
                buf = [0.0] * delay
                for i in range(len(src)):
                    temp = src[i] + buf[i % delay] * decay
                    dst[i] += temp
                    buf[i % delay] = temp
        gain = 1.0 / len(delays)
        dry = 1.0 - wet
        return ([left[i] * dry + out_l[i] * gain * wet for i in range(len(left))],
                [right[i] * dry + out_r[i] * gain * wet for i in range(len(right))])

    @staticmethod
    def _apply_chorus(left, right, wet=0.4, depth=0.003, rate=1.5):
        sr = 44100
        delay_base = int(sr * 0.02)
        out_l, out_r = [0.0] * len(left), [0.0] * len(right)
        for voice in range(3):
            phase = voice * 2 * math.pi / 3
            for ch_i, (src, dst) in enumerate([(left, out_l), (right, out_r)]):
                for i in range(len(src)):
                    mod = depth * _sin(2 * math.pi * rate * i / sr + phase)
                    read_idx = i - delay_base - int(mod * sr)
                    if 0 <= read_idx < len(src):
                        dst[i] += src[read_idx] * 0.3
        dry = 1.0 - wet
        return ([left[i] * dry + out_l[i] * wet for i in range(len(left))],
                [right[i] * dry + out_r[i] * wet for i in range(len(right))])

    # ---- MIDI Export ----------------------------------------------------------------------------

    _MIDI_DRUM_MAP = {"K": 36, "S": 38, "H": 42, "O": 46, "T": 47}

    @staticmethod
    def _note_name_to_midi(note_str):
        mapping = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
                   "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
                   "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
        note_str = note_str.strip()
        i = 1
        if len(note_str) > 1 and note_str[1] in "#b":
            i = 2
        name = note_str[:i]
        rest = note_str[i:]
        octave = 4
        if rest:
            try:
                octave = int(rest)
            except ValueError:
                octave = 4
        return (octave + 1) * 12 + mapping.get(name, 0)

    @staticmethod
    def _midi_varlen(value):
        buf = bytearray()
        buf.append(value & 0x7F)
        value >>= 7
        while value > 0:
            buf.append(0x80 | (value & 0x7F))
            value >>= 7
        buf.reverse()
        return bytes(buf)

    @staticmethod
    def _midi_write_track(events):
        data = bytearray()
        for delta, event in events:
            data.extend(Composer._midi_varlen(delta))
            data.extend(event)
        return bytes(data)

    def _build_midi_events_from_notes(self, notes_str, channel=0, instrument="", harmony_semitones=None, max_ticks=0):
        sr = self.SAMPLE_RATE
        spb = int(sr * 60 / self.bpm)
        notes = [n.strip() for n in notes_str.split(",") if n.strip()]
        events = []
        ticks_per_beat = 480
        pending_ticks = 0
        pos_ticks = 0
        last_vel = 0.65
        for expr in notes:
            parts = expr.split(":")
            note_part = parts[0]
            dur_str = parts[1] if len(parts) >= 2 else "q"
            vel_str = parts[2] if len(parts) > 2 else None
            if vel_str is not None:
                last_vel = self._parse_dynamic(vel_str)
            beat_frac = self._parse_duration(dur_str) if dur_str and dur_str[0] in "whqesWHQES" else 1.0
            delta_ticks = int(beat_frac * ticks_per_beat)
            if note_part in ("R", "_"):
                pending_ticks += delta_ticks
                continue
            pos_ticks += pending_ticks
            if max_ticks and pos_ticks >= max_ticks:
                break
            if instrument == "drums":
                if note_part in self._MIDI_DRUM_MAP:
                    note = self._MIDI_DRUM_MAP[note_part]
                    vel = int(last_vel * 127)
                    note_len = min(delta_ticks, max_ticks - pos_ticks) if max_ticks else delta_ticks
                    events.append((pending_ticks, bytes([0x99, note, vel])))
                    pending_ticks = 0
                    events.append((note_len, bytes([0x89, note, 0])))
                    pos_ticks += note_len
                    if max_ticks and note_len < delta_ticks:
                        pending_ticks = delta_ticks - note_len
            else:
                midi_note = self._note_name_to_midi(note_part)
                vel = int(last_vel * 127)
                note_len = min(delta_ticks, max_ticks - pos_ticks) if max_ticks else delta_ticks
                events.append((pending_ticks, bytes([0x90 | channel, midi_note, vel])))
                pending_ticks = 0
                if harmony_semitones:
                    for st in harmony_semitones:
                        harm_note = midi_note + st
                        if 0 <= harm_note <= 127:
                            events.append((0, bytes([0x90 | channel, harm_note, vel])))
                events.append((note_len, bytes([0x80 | channel, midi_note, 0])))
                if harmony_semitones:
                    for st in harmony_semitones:
                        harm_note = midi_note + st
                        if 0 <= harm_note <= 127:
                            events.append((0, bytes([0x80 | channel, harm_note, 0])))
                pos_ticks += note_len
                if max_ticks and note_len < delta_ticks:
                    pending_ticks = delta_ticks - note_len
        return events

    def _build_midi_drum_pattern(self, track, ticks_per_beat):
        events = []
        kick_pat = getattr(track, "kick", None) or "1000100010001000"
        snare_pat = getattr(track, "snare", None) or "0010001000100010"
        hihat_pat = getattr(track, "hihat", None) or "1111111111111111"
        max_len = max(len(kick_pat), len(snare_pat), len(hihat_pat))
        pending = 0
        for beat in range(max_len):
            hits = []
            if beat < len(kick_pat) and kick_pat[beat] in ("1", "X"):
                hits.append((36, 100))
            if beat < len(snare_pat) and snare_pat[beat] in ("1", "X"):
                hits.append((38, 100))
            if beat < len(hihat_pat) and hihat_pat[beat] in ("1", "X"):
                hits.append((42, 80))
            if hits:
                for note, vel in hits:
                    events.append((pending, bytes([0x99, note, vel])))
                    pending = 0
                for note, vel in hits:
                    events.append((ticks_per_beat, bytes([0x89, note, 0])))
            else:
                pending += ticks_per_beat
        return events

    def _build_midi_pattern(self, track, ticks_per_beat, channel):
        events = []
        pat = self._resolve_pattern(getattr(track, "pattern", "pop"))
        pat = self._repeat_pattern(pat, getattr(track, "loops", 1) or 1)
        root_note = self._note_name_to_midi(f"{getattr(track, 'scale', 'C')}{getattr(track, 'octave', 4)}")
        harm_str = getattr(track, "harmony", None)
        harm_st = self._HARMONY_INTERVALS.get(harm_str) if harm_str else None
        pending = 0
        for beat in range(len(pat)):
            if pat[beat]:
                vel = min(int(getattr(track, "volume", 1.0) * 100), 127)
                if vel < 1:
                    vel = 80
                events.append((pending, bytes([0x90 | channel, root_note, vel])))
                if harm_st is not None:
                    harm_note = root_note + harm_st
                    if 0 <= harm_note <= 127:
                        events.append((0, bytes([0x90 | channel, harm_note, vel])))
                events.append((ticks_per_beat, bytes([0x80 | channel, root_note, 0])))
                if harm_st is not None:
                    harm_note = root_note + harm_st
                    if 0 <= harm_note <= 127:
                        events.append((0, bytes([0x80 | channel, harm_note, 0])))
                pending = 0
            else:
                pending += ticks_per_beat
        return events

    def write_midi(self, output_path, loop=1, max_secs=0):
        ticks_per_beat = 480
        tempo_us = int(60_000_000 / self.bpm)
        max_ticks = int(max_secs * self.bpm * ticks_per_beat / 60) if max_secs else 0

        # Track 0: tempo + time signature
        tempo_events = [
            (0, bytes([0xFF, 0x51, 0x03, (tempo_us >> 16) & 0xFF, (tempo_us >> 8) & 0xFF, tempo_us & 0xFF])),
            (0, bytes([0xFF, 0x58, 0x04, 4, 2, 24, 8])),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]
        all_tracks = [tempo_events]

        parallel_entries = []
        serial_entries = []
        channel = 0

        for track in self.tracks:
            notes_str = track.notes
            if notes_str:
                notes_str = Composer.expand_compact_notes(notes_str)
                notes_str = self._repeat_notes(notes_str, getattr(track, "loops", 1) or 1)

            is_drums = track.instrument == "drums"
            mode = getattr(track, "mode", "parallel")
            trk_name = getattr(track, "name", "") or track.instrument
            name_bytes = trk_name.encode()

            harm_str = getattr(track, "harmony", None)
            harm_semitones = []
            if harm_str and not is_drums:
                st = self._HARMONY_INTERVALS.get(harm_str)
                if st is not None:
                    harm_semitones = [st]

            events = None
            ch = 9 if is_drums else channel

            if notes_str and self._is_extended_notes(notes_str):
                events = self._build_midi_events_from_notes(notes_str, ch, track.instrument, harm_semitones, max_ticks)
                if not is_drums:
                    channel += 1
            elif is_drums:
                events = self._build_midi_drum_pattern(track, ticks_per_beat)
            else:
                events = self._build_midi_pattern(track, ticks_per_beat, ch)
                channel += 1

            if not events:
                continue

            events.insert(0, (0, bytes([0xFF, 0x03, len(name_bytes)]) + name_bytes))
            if not is_drums:
                prog = self._GM_INSTRUMENTS.get(track.instrument, 0)
                events.insert(0, (0, bytes([0xC0 | ch, prog])))

            entry = (events, ch, is_drums)
            if mode == "serial":
                serial_entries.append(entry)
            else:
                parallel_entries.append(entry)

        # Parallel tracks (render once)
        for evts, ch, is_drums in parallel_entries:
            copy = list(evts)
            copy.append((0, bytes([0xFF, 0x2F, 0x00])))
            all_tracks.append(copy)

        # Serial tracks: precompute per-track durations
        serial_durs = [sum(d for d, _ in evts) for evts, _, _ in serial_entries]
        serial_block = sum(serial_durs)

        for loop_n in range(loop):
            serial_offset = 0
            for idx, (evts, ch, is_drums) in enumerate(serial_entries):
                copy = []
                for i, (d, e) in enumerate(evts):
                    offset = serial_offset + loop_n * serial_block
                    new_d = (d + offset) if i == 0 else d
                    copy.append((new_d, e))
                copy.append((0, bytes([0xFF, 0x2F, 0x00])))
                all_tracks.append(copy)
                serial_offset += serial_durs[idx]

        # Write MIDI file
        with open(output_path, "wb") as f:
            ntracks = len(all_tracks)
            f.write(b"MThd")
            f.write(struct.pack(">I", 6))
            f.write(struct.pack(">HHH", 1, ntracks, ticks_per_beat))
            for track_events in all_tracks:
                track_data = self._midi_write_track(track_events)
                f.write(b"MTrk")
                f.write(struct.pack(">I", len(track_data)))
                f.write(track_data)

    def _generate_melody(self, freq, pattern, beat_starts, total_samples, instrument="piano"):
        if _xp is not None:
            data = _xp.zeros(total_samples)
        else:
            data = [0.0] * total_samples
        sr = self.SAMPLE_RATE
        n_beats = min(len(pattern), len(beat_starts) - 1)
        for beat in range(n_beats):
            if pattern[beat]:
                start = beat_starts[beat]
                end = beat_starts[beat + 1]
                length = end - start
                if _xp is not None:
                    i = _xp.arange(length)
                    t = (start + i) / sr
                    env = _exp(-i / (length * 0.3))
                    data[start:end] = self._get_waveform(instrument, t, freq) * env
                else:
                    for i in range(length):
                        t = (start + i) / sr
                        envelope = _exp(-i / (length * 0.3))
                        data[start + i] = self._get_waveform(instrument, t, freq) * envelope
        return data

    @staticmethod
    def _parse_note_expr(expr):
        expr = expr.strip()
        if expr in ("R", "_"):
            return expr, 0
        parts = expr.split(":")
        note = parts[0]
        velocity = float(parts[1]) if len(parts) > 1 else 1.0
        return note, velocity

    def _note_name_to_freq(self, note_str):
        note_str = note_str.strip()
        octave = int(note_str[-1]) if note_str[-1].isdigit() else 4
        raw = note_str[:-1] if note_str[-1].isdigit() else note_str
        name = raw[0].upper()
        if len(raw) > 1 and raw[1] in "#b":
            name = raw[0].upper() + raw[1:]
        base = self.NOTE_FREQUENCIES.get(name, 440.0)
        return base * (2 ** (octave - 4))

    def _generate_melody_from_notes(self, notes_str, pattern, beat_starts, total_samples, instrument="piano"):
        notes = [n.strip() for n in notes_str.split(",") if n.strip()]
        if _xp is not None:
            data = _xp.zeros(total_samples)
        else:
            data = [0.0] * total_samples
        note_idx = 0
        sr = self.SAMPLE_RATE
        n_beats = min(len(pattern), len(beat_starts) - 1)
        for beat in range(n_beats):
            if pattern[beat] and notes:
                current = notes[note_idx % len(notes)]
                note_idx += 1
                if current in ("R", "_"):
                    continue
                name, velocity = self._parse_note_expr(current)
                freq = self._note_name_to_freq(name)
                start = beat_starts[beat]
                end = beat_starts[beat + 1]
                length = end - start
                if _xp is not None:
                    i = _xp.arange(length)
                    t = (start + i) / sr
                    env = _exp(-i / (length * 0.3))
                    data[start:end] = self._get_waveform(instrument, t, freq) * env * velocity
                else:
                    for i in range(length):
                        t = (start + i) / sr
                        envelope = _exp(-i / (length * 0.3))
                        data[start + i] = self._get_waveform(instrument, t, freq) * envelope * velocity
        return data

    def _resolve_drum_pattern(self, pat_str, beats):
        if pat_str is None:
            return None
        lst = [int(c) for c in pat_str if c in "01"]
        if len(lst) < beats:
            lst = lst * (beats // len(lst) + 1)
        return lst[:beats]

    def _generate_drum_beat(self, beat_starts, total_samples, kick_str=None, snare_str=None, hihat_str=None):
        beats = len(beat_starts) - 1
        data = [0.0] * total_samples
        if beats == 0:
            return data
        sr = self.SAMPLE_RATE

        kick_pat = self._resolve_drum_pattern(kick_str, beats)
        snare_pat = self._resolve_drum_pattern(snare_str, beats)
        hihat_pat = self._resolve_drum_pattern(hihat_str, beats)

        for beat in range(beats):
            start = beat_starts[beat]
            end = beat_starts[beat + 1]
            length = end - start
            kick_on = kick_pat[beat] if kick_pat is not None else (beat % 4 == 0)
            snare_on = snare_pat[beat] if snare_pat is not None else (beat % 4 == 2)
            hihat_on = hihat_pat[beat] if hihat_pat is not None else True

            if kick_on:
                for i in range(length // 2):
                    if start + i < total_samples:
                        t = (start + i) / sr
                        env = _exp(-i / (length * 0.08))
                        data[start + i] += _sin(2 * math.pi * 55 * t) * env * 0.6

            if snare_on:
                for i in range(length // 2):
                    if start + i < total_samples:
                        t = (start + i) / sr
                        env = _exp(-i / (length * 0.12))
                        noise = (((beat * 999 + i) * 113) % 200) / 200 * 2 - 1
                        tone = _sin(2 * math.pi * 180 * t)
                        data[start + i] += (noise * 0.3 + tone * 0.3) * env * 0.7

            if hihat_on:
                for i in range(length // 4):
                    if start + i < total_samples:
                        env = _exp(-i / (length * 0.03))
                        noise = (((beat * 5555 + i) * 113) % 200) / 200 * 2 - 1
                        data[start + i] += noise * env * 0.3
        return data

    def _generate_drums_from_extended_notes(self, notes_str, total_samples):
        notes = [n.strip() for n in notes_str.split(",") if n.strip()]
        data = [0.0] * total_samples
        sr = self.SAMPLE_RATE
        spb = int(sr * 60 / self.bpm)
        pos = 0
        last_vel = 0.65
        for expr in notes:
            if not expr:
                continue
            parts = expr.split(":")
            dtype = parts[0]
            beat_frac = self._parse_duration(parts[1]) if len(parts) >= 2 and parts[1] and parts[1][0] in "whqesWHQES" else 1.0
            vel = self._parse_dynamic(parts[2]) if len(parts) > 2 else last_vel
            last_vel = vel
            nsamples = int(beat_frac * spb)
            if pos + nsamples > total_samples:
                nsamples = total_samples - pos
            if nsamples <= 0:
                break
            if dtype == "K":
                for i in range(nsamples):
                    t = i / sr
                    env = _exp(-i / (nsamples * 0.08))
                    data[pos + i] += _sin(2 * math.pi * 55 * t) * env * 0.6 * vel
            elif dtype == "S":
                for i in range(nsamples):
                    t = i / sr
                    env = _exp(-i / (nsamples * 0.12))
                    noise = ((i * 113) % 200) / 200 * 2 - 1
                    tone = _sin(2 * math.pi * 180 * t)
                    data[pos + i] += (noise * 0.3 + tone * 0.3) * env * 0.7 * vel
            elif dtype == "H":
                prev = 0.0
                for i in range(nsamples // 2):
                    env = _exp(-i / (nsamples * 0.03))
                    noise_raw = ((i * 113) % 200) / 200 * 2 - 1
                    noise = noise_raw - prev
                    prev = noise_raw
                    data[pos + i] += noise * env * 0.3 * vel
            elif dtype == "O":
                prev = 0.0
                for i in range(nsamples):
                    env = _exp(-i / (nsamples * 0.1))
                    noise_raw = ((i * 113) % 200) / 200 * 2 - 1
                    noise = noise_raw - prev
                    prev = noise_raw
                    data[pos + i] += noise * env * 0.35 * vel
            elif dtype == "T":
                for i in range(nsamples):
                    t = i / sr
                    env = _exp(-i / (nsamples * 0.15))
                    data[pos + i] += _sin(2 * math.pi * 80 * t) * env * 0.5 * vel
            pos += nsamples
        return data
