"""Regression tests for fidelity bugs found by MIDI round-trip comparison."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from acml import _split_key_value, parse_acml
from composer import Composer
from midiconv import _map_drum_pitch, _duration_value, _DURATION_VALUES
from track import Track


class TestSharpNoteParsing(unittest.TestCase):
    """acml._split_key_value must not truncate values at '#' (sharp notes)."""

    def test_unquoted_sharp_note(self):
        key, val = _split_key_value("notes = F#1:q:mf,C#4:q:mf")
        self.assertEqual(key, "notes")
        self.assertEqual(val, "F#1:q:mf,C#4:q:mf")

    def test_quoted_sharp_note(self):
        key, val = _split_key_value('notes = "F#4:e:ff,G#3:h:mf"')
        self.assertEqual(val, "F#4:e:ff,G#3:h:mf")

    def test_quoted_value_keeps_hash(self):
        key, val = _split_key_value('name = "test #1"')
        self.assertEqual(val, "test #1")

    def test_inline_comment_still_stripped(self):
        key, val = _split_key_value("instrument = piano # acoustic grand")
        self.assertEqual(val, "piano")

    def test_parse_acml_full_sharp_notes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".acml", delete=False,
                                         encoding="utf-8") as f:
            f.write('name = "t"\nbpm = 100\n\n'
                    '[track a]\n'
                    'instrument = piano\n'
                    'notes = F#1:e:ff,C#4:q:mf,G#3:h:p\n')
            path = f.name
        try:
            name, bpm, loop, tracks = parse_acml(path)
            self.assertEqual(tracks[0]["notes"], "F#1:e:ff,C#4:q:mf,G#3:h:p")
        finally:
            os.unlink(path)


class TestThirtySecondDuration(unittest.TestCase):
    """'x' = 0.125 beats (32nd note) must work end to end."""

    def test_parse_duration(self):
        self.assertAlmostEqual(Composer._parse_duration("x"), 0.125)
        self.assertAlmostEqual(Composer._parse_duration("x."), 0.1875)

    def test_is_extended_notes_accepts_x(self):
        self.assertTrue(Composer._is_extended_notes("A4:x:mf"))
        self.assertTrue(Composer._is_extended_notes("R:x"))

    def test_midiconv_duration_value(self):
        self.assertAlmostEqual(_duration_value("x"), 0.125)
        self.assertAlmostEqual(_duration_value("x."), 0.1875)

    def test_duration_values_include_x(self):
        vals = [v for v, _ in _DURATION_VALUES]
        self.assertIn(0.125, vals)
        self.assertIn(0.1875, vals)

    def test_compile_track_with_x(self):
        c = Composer(bpm=120)
        c.add_track(Track(instrument="piano", notes="A4:x:mf,A4:x:mf,A4:s:mf,R:x,A4:q:mf"))
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        try:
            c.generate(path, trim=False)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 44)
        finally:
            os.unlink(path)

    def test_write_midi_x_durations(self):
        c = Composer(bpm=120)
        c.add_track(Track(instrument="piano", notes="A4:x:mf,C5:x:mf,A4:q:mf"))
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = f.name
        try:
            c.write_midi(path)
            raw = open(path, "rb").read()
            self.assertTrue(raw.startswith(b"MThd"))
            self.assertGreater(len(raw), 30)
        finally:
            os.unlink(path)


class TestDrumLetters(unittest.TestCase):
    """C/Y/Z drum letters round-trip: converter output -> composer MIDI export."""

    def test_map_drum_pitch_never_drops(self):
        for pitch in range(35, 82):
            self.assertIsNotNone(_map_drum_pitch(pitch),
                                 "drum pitch %d not mapped" % pitch)

    def test_specific_mappings(self):
        self.assertEqual(_map_drum_pitch(39), "C")    # hand clap
        self.assertEqual(_map_drum_pitch(54), "Y")    # tambourine
        self.assertEqual(_map_drum_pitch(49), "Z")    # crash cymbal
        self.assertEqual(_map_drum_pitch(51), "Z")    # ride cymbal
        self.assertEqual(_map_drum_pitch(46), "O")    # open hi-hat
        self.assertEqual(_map_drum_pitch(36), "K")
        self.assertEqual(_map_drum_pitch(38), "S")

    def test_composer_midi_drum_map_covers_all_letters(self):
        for letter in ("K", "S", "C", "H", "O", "T", "Y", "Z"):
            self.assertIn(letter, Composer._MIDI_DRUM_MAP)

    def test_drum_midi_roundtrip_pitch(self):
        """Letter -> MIDI export must produce the GM pitch it came from."""
        expected = {"K": 36, "S": 38, "C": 39, "H": 42, "O": 46,
                    "T": 47, "Y": 54, "Z": 49}
        for letter, pitch in expected.items():
            self.assertEqual(Composer._MIDI_DRUM_MAP[letter], pitch)
            self.assertEqual(_map_drum_pitch(pitch), letter)

    def test_drum_letters_render_audio(self):
        """Synthesized output must be non-silent for every drum letter."""
        import math
        for letter in ("K", "S", "C", "H", "O", "T", "Y", "Z"):
            c = Composer(bpm=120)
            data = c._generate_drums_from_extended_notes(f"{letter}:w:ff", c.SAMPLE_RATE)
            rms = math.sqrt(sum(x * x for x in data[1000:50000]) / 49000)
            self.assertGreater(rms, 0.001, f"drum {letter} silent")


def _read_midi_tracks(path):
    """Return [(track_name, [pitch, ...]) for note-ons]."""
    raw = open(path, "rb").read()
    pos = 14
    ntracks = struct.unpack(">H", raw[10:12])[0]
    out = []

    def vlq(p):
        v = 0
        while True:
            b = raw[p]
            p += 1
            v = (v << 7) | (b & 0x7F)
            if not (b & 0x80):
                return v, p

    for _ in range(ntracks):
        length = struct.unpack(">I", raw[pos + 4:pos + 8])[0]
        end = pos + 8 + length
        p = pos + 8
        pos = end
        tick = 0
        status = 0
        name = None
        pitches = []
        while p < end:
            dt, p = vlq(p)
            tick += dt
            b = raw[p]
            if b == 0xFF:
                mtype = raw[p + 1]
                ln, p2 = vlq(p + 2)
                if mtype == 0x03:
                    name = raw[p2:p2 + ln].decode("utf-8", errors="replace")
                p = p2 + ln
                continue
            if b & 0x80:
                status = b
                p += 1
            ev = status & 0xF0
            if ev in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
                d1, d2 = raw[p], raw[p + 1]
                p += 2
                if ev == 0x90 and d2 > 0:
                    pitches.append((d1, status & 0x0F))
            elif ev in (0xC0, 0xD0):
                p += 1
        if pitches:
            out.append((name, pitches))
    return out


class TestMidiChannelAssignment(unittest.TestCase):
    """Melodic tracks must never land on channel 9 (percussion)."""

    def _make_project(self, n_melodic):
        c = Composer(bpm=120)
        for i in range(n_melodic):
            inst = ["piano", "bass", "lead", "bell", "sawtooth",
                    "guitar", "organ", "strings", "brass", "pad"][i % 10]
            t = Track(instrument=inst, notes="C4:q:mf,E4:q:mf,G4:q:mf,R:q")
            t.name = f"t{i}"
            c.add_track(t)
        d = Track(instrument="drums", notes="K:q:mf,S:q:mf,H:q:mf,O:q:mf")
        d.name = "dr"
        c.add_track(d)
        return c

    def test_no_melodic_on_channel_9(self):
        c = self._make_project(20)
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = f.name
        try:
            c.write_midi(path)
            for name, pitches in _read_midi_tracks(path):
                if name == "dr":
                    for pitch, ch in pitches:
                        self.assertEqual(ch, 9, "drum track not on ch9")
                else:
                    for pitch, ch in pitches:
                        self.assertNotEqual(ch, 9,
                                            f"track {name} on percussion ch9")
        finally:
            os.unlink(path)

    def test_same_instrument_shares_channel(self):
        c = self._make_project(16)
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = f.name
        try:
            c.write_midi(path)
            inst_channels = {}
            for name, pitches in _read_midi_tracks(path):
                if name == "dr":
                    continue
                chs = set(ch for _, ch in pitches)
                self.assertEqual(len(chs), 1, f"track {name} spans channels")
                ch = next(iter(chs))
                if name in inst_channels:
                    self.assertEqual(inst_channels[name], ch,
                                     f"instrument {name} split across channels")
                inst_channels[name] = ch
        finally:
            os.unlink(path)

    def test_different_instruments_dont_share_program_channel(self):
        """Two tracks with different instruments must land on different channels."""
        c = Composer(bpm=120)
        for inst in ("piano", "lead"):
            t = Track(instrument=inst, notes="C4:q:mf")
            t.name = inst
            c.add_track(t)
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as f:
            path = f.name
        try:
            c.write_midi(path)
            ch_by_name = {}
            for name, pitches in _read_midi_tracks(path):
                if not pitches:
                    continue
                chs = set(ch for _, ch in pitches)
                self.assertEqual(len(chs), 1)
                ch_by_name[name] = next(iter(chs))
            self.assertIn("piano", ch_by_name)
            self.assertIn("lead", ch_by_name)
            self.assertNotEqual(ch_by_name["piano"], ch_by_name["lead"],
                                "different instruments share a channel")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
