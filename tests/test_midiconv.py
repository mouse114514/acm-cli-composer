import os
import tempfile
import unittest

from midiconv import (
    parse_midi, midi_to_acml_text, convert,
    _midi_to_note_name, _velocity_to_dynamic, _gm_to_instrument,
    _quantize_duration, _gap_to_rests, _split_voices, _duration_value,
)
from composer import Composer
from track import Track
from acml import parse_acml


# ---------------------------------------------------------------------------
# Minimal MIDI file builder (SMF bytes, pure stdlib)
# ---------------------------------------------------------------------------

def _vlq(value):
    buf = bytearray([value & 0x7F])
    value >>= 7
    while value:
        buf.append(0x80 | (value & 0x7F))
        value >>= 7
    buf.reverse()
    return bytes(buf)


def _track_bytes(events):
    data = bytearray()
    for delta, ev in events:
        data += _vlq(delta)
        data += ev
    return b"MTrk" + len(data).to_bytes(4, "big") + bytes(data)


def build_midi(tracks, division=480, fmt=1):
    header = (b"MThd" + (6).to_bytes(4, "big")
              + fmt.to_bytes(2, "big")
              + len(tracks).to_bytes(2, "big")
              + division.to_bytes(2, "big"))
    out = header
    for evs in tracks:
        out += _track_bytes(evs)
    return out


def meta_tempo(bpm):
    mpqn = int(round(60000000 / bpm))
    return bytes([0xFF, 0x51, 0x03]) + mpqn.to_bytes(3, "big")


def meta_name(text):
    raw = text.encode("utf-8")
    return bytes([0xFF, 0x03, len(raw)]) + raw


def note_on(ch, pitch, vel):
    return bytes([0x90 | ch, pitch, vel])


def note_off(ch, pitch, vel=0):
    return bytes([0x80 | ch, pitch, vel])


def write_midi_file(path, tracks, division=480, fmt=1):
    with open(path, "wb") as f:
        f.write(build_midi(tracks, division=division, fmt=fmt))


class TestMidiParse(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="acm_midiconv_")

    def _path(self, name="t.mid"):
        return os.path.join(self.dir, name)

    def test_parse_header_and_note(self):
        """解析 MIDI 头与单个音符"""
        p = self._path()
        write_midi_file(p, [[
            (0, meta_tempo(120)),
            (0, note_on(0, 60, 100)),
            (480, note_off(0, 60)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        data = parse_midi(p)
        self.assertEqual(data["ticks_per_beat"], 480)
        self.assertAlmostEqual(data["bpm"], 120.0, places=2)
        notes = data["channels"][0]["notes"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["pitch"], 60)
        self.assertEqual(notes[0]["start"], 0)
        self.assertEqual(notes[0]["end"], 480)
        self.assertEqual(notes[0]["velocity"], 100)

    def test_parse_tempo_bpm(self):
        """不同 BPM 速度元事件被正确解析"""
        p = self._path()
        write_midi_file(p, [[
            (0, meta_tempo(175)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]])
        data = parse_midi(p)
        self.assertAlmostEqual(data["bpm"], 175.0, places=1)

    def test_parse_track_name(self):
        """解析轨名元事件"""
        p = self._path()
        write_midi_file(p, [[
            (0, meta_name("Melody Line")),
            (0, note_on(0, 64, 80)),
            (240, note_off(0, 64)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]])
        data = parse_midi(p)
        self.assertEqual(data["channels"][0]["name"], "Melody Line")

    def test_note_on_velocity_zero_is_note_off(self):
        """velocity=0 的 note-on 等同于 note-off"""
        p = self._path()
        write_midi_file(p, [[
            (0, note_on(0, 62, 90)),
            (480, note_on(0, 62, 0)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]])
        data = parse_midi(p)
        notes = data["channels"][0]["notes"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["end"], 480)

    def test_running_status(self):
        """运行状态（省略重复状态字节）被正确处理"""
        p = self._path()
        # 手工构造：0x90 后跟 running status 省略
        events = [
            (0, bytes([0x90, 60, 100])),    # note on C4 @ tick 0
            (480, bytes([61, 100])),         # running status note on C#4 @ tick 480
            (480, bytes([0x80, 60, 0])),     # explicit note off C4 @ tick 960
            (0, bytes([61, 0])),             # running status (0x80) note off C#4 @ tick 960
        ]
        write_midi_file(p, [events + [(0, bytes([0xFF, 0x2F, 0x00]))]])
        data = parse_midi(p)
        notes = data["channels"][0]["notes"]
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0]["pitch"], 60)
        self.assertEqual(notes[0]["start"], 0)
        self.assertEqual(notes[0]["end"], 960)
        self.assertEqual(notes[1]["pitch"], 61)
        self.assertEqual(notes[1]["start"], 480)
        self.assertEqual(notes[1]["end"], 960)

    def test_program_change(self):
        """program change 被记录到对应通道"""
        p = self._path()
        write_midi_file(p, [[
            (0, bytes([0xC0, 26])),   # program change: electric guitar
            (0, note_on(0, 40, 80)),
            (480, note_off(0, 40)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]])
        data = parse_midi(p)
        self.assertEqual(data["channels"][0]["program"], 26)

    def test_not_a_midi_file_raises(self):
        """非 MIDI 文件抛出 ValueError"""
        p = self._path()
        with open(p, "wb") as f:
            f.write(b"RIFFxxxxWAVE")
        with self.assertRaises(ValueError):
            parse_midi(p)


class TestHelpers(unittest.TestCase):
    def test_midi_to_note_name(self):
        """MIDI 音高 -> 音名（C4=60 为中央C）"""
        self.assertEqual(_midi_to_note_name(60), "C4")
        self.assertEqual(_midi_to_note_name(61), "C#4")
        self.assertEqual(_midi_to_note_name(59), "B3")
        self.assertEqual(_midi_to_note_name(69), "A4")
        self.assertEqual(_midi_to_note_name(0), "C-1")
        self.assertEqual(_midi_to_note_name(127), "G9")

    def test_note_name_roundtrip_with_composer(self):
        """音名 -> MIDI -> 音名 往返一致"""
        from composer import Composer
        for pitch in range(128):
            name = _midi_to_note_name(pitch)
            back = Composer._note_name_to_midi(name)
            self.assertEqual(back, pitch, f"pitch {pitch} -> {name} -> {back}")

    def test_velocity_dynamic_roundtrip(self):
        """ACML 力度 -> MIDI velocity -> ACML 力度 往返一致"""
        from composer import Composer
        for name in ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]:
            v0 = Composer._parse_dynamic(name)
            vel = max(1, min(127, round(v0 * 127)))
            self.assertEqual(_velocity_to_dynamic(vel), name,
                             f"{name} (vel={vel}) roundtrip failed")

    def test_gm_instrument_never_sample(self):
        """GM program 映射绝不返回 sample（缺少 WAV 路径会崩溃）"""
        for prog in range(128):
            self.assertNotEqual(_gm_to_instrument(prog), "sample",
                                f"program {prog} mapped to sample")

    def test_quantize_duration_values(self):
        """时值量化到标准 ACML 字母"""
        self.assertEqual(_quantize_duration(0.25), "s")
        self.assertEqual(_quantize_duration(0.5), "e")
        self.assertEqual(_quantize_duration(1.0), "q")
        self.assertEqual(_quantize_duration(2.0), "h")
        self.assertEqual(_quantize_duration(4.0), "w")
        self.assertEqual(_quantize_duration(3.0), "h.")
        self.assertEqual(_quantize_duration(6.0), "w.")

    def test_duration_value_inverse(self):
        """_duration_value 与量化互逆"""
        for beats, letter in [(0.25, "s"), (0.375, "s."), (0.5, "e"),
                              (0.75, "e."), (1.0, "q"), (1.5, "q."),
                              (2.0, "h"), (3.0, "h."), (4.0, "w"), (6.0, "w.")]:
            self.assertEqual(_quantize_duration(beats), letter)
            self.assertAlmostEqual(_duration_value(letter), beats, places=6)

    def test_gap_to_rests_covers_gap(self):
        """休止符分解覆盖间隔拍数"""
        for gap in [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 8.0]:
            tokens = _gap_to_rests(gap)
            total = sum(_duration_value(t.split(":")[1]) for t in tokens)
            self.assertAlmostEqual(total, gap, places=6,
                                   msg=f"gap {gap} -> {tokens} = {total}")

    def test_gap_to_rests_ignores_tiny_gap(self):
        """极小间隔不产生休止符"""
        self.assertEqual(_gap_to_rests(0.05), [])
        self.assertEqual(_gap_to_rests(0.0), [])


class TestVoiceSplit(unittest.TestCase):
    def test_sequence_single_voice(self):
        """不重叠音符归入同一声部"""
        notes = [
            {"pitch": 60, "start": 0, "end": 100, "velocity": 80},
            {"pitch": 62, "start": 100, "end": 200, "velocity": 80},
            {"pitch": 64, "start": 200, "end": 300, "velocity": 80},
        ]
        self.assertEqual(len(_split_voices(notes)), 1)

    def test_chord_creates_multiple_voices(self):
        """同时发声的和弦拆成多个声部"""
        notes = [
            {"pitch": 60, "start": 0, "end": 100, "velocity": 80},
            {"pitch": 64, "start": 0, "end": 100, "velocity": 80},
            {"pitch": 67, "start": 0, "end": 100, "velocity": 80},
        ]
        voices = _split_voices(notes)
        self.assertEqual(len(voices), 3)

    def test_no_voice_overlaps(self):
        """每个声部内部没有重叠"""
        notes = [
            {"pitch": 60, "start": 0, "end": 200, "velocity": 80},
            {"pitch": 64, "start": 0, "end": 200, "velocity": 80},
            {"pitch": 67, "start": 100, "end": 300, "velocity": 80},
        ]
        for voice in _split_voices(notes):
            for a, b in zip(voice, voice[1:]):
                self.assertLessEqual(a["end"], b["start"])


class TestConvert(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="acm_conv_")

    def _path(self, name="t.mid"):
        return os.path.join(self.dir, name)

    def test_convert_monophonic(self):
        """单声部旋律转换出正确的扩展音符"""
        p = self._path()
        write_midi_file(p, [[
            (0, meta_tempo(120)),
            (0, note_on(0, 60, 83)),    # C4, vel 83 -> mf
            (480, note_off(0, 60)),
            (0, note_on(0, 62, 83)),
            (480, note_off(0, 62)),
            (0, note_on(0, 64, 83)),
            (480, note_off(0, 64)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        data = parse_midi(p)
        text = midi_to_acml_text(data, name="melody")
        self.assertIn('name = "melody"', text)
        self.assertIn("bpm = 120", text)
        self.assertIn("C4:q:mf", text)
        self.assertIn("D4:q:mf", text)
        self.assertIn("E4:q:mf", text)

    def test_convert_gap_produces_rest(self):
        """音符之间的时间空隙产生休止符"""
        p = self._path()
        write_midi_file(p, [[
            (0, note_on(0, 60, 83)),
            (480, note_off(0, 60)),
            (480, note_on(0, 62, 83)),   # 空 1 拍
            (480, note_off(0, 62)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        data = parse_midi(p)
        text = midi_to_acml_text(data, name="gap")
        self.assertIn("C4:q:mf", text)
        self.assertIn("R:q", text)
        self.assertIn("D4:q:mf", text)

    def test_convert_chord_creates_multiple_tracks(self):
        """同时和弦生成多个平行 track"""
        p = self._path()
        write_midi_file(p, [[
            (0, note_on(0, 60, 83)),
            (0, note_on(0, 64, 83)),
            (0, note_on(0, 67, 83)),
            (480, note_off(0, 60)),
            (0, note_off(0, 64)),
            (0, note_off(0, 67)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        data = parse_midi(p)
        text = midi_to_acml_text(data, name="chord")
        track_count = text.count("[track ")
        self.assertEqual(track_count, 3)

    def test_convert_drums(self):
        """鼓通道 (ch9) 映射为 K/S/H/O/T 独立轨"""
        p = self._path()
        write_midi_file(p, [[
            (0, note_on(9, 36, 100)),   # kick
            (0, note_on(9, 38, 100)),   # snare (同时)
            (480, note_off(9, 36)),
            (0, note_off(9, 38)),
            (0, note_on(9, 42, 100)),   # hi-hat
            (240, note_off(9, 42)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        data = parse_midi(p)
        text = midi_to_acml_text(data, name="drums")
        self.assertIn("instrument = drums", text)
        self.assertIn("[track kick]", text)
        self.assertIn("[track snare]", text)
        self.assertIn("[track hats]", text)
        self.assertIn("K:q:f", text)   # vel 100 -> 100/127=0.787 -> nearest f(0.8)
        self.assertIn("S:", text)
        self.assertIn("H:", text)

    def test_convert_instrument_mapping(self):
        """GM program 映射到 ACM 乐器名"""
        p = self._path()
        write_midi_file(p, [[
            (0, bytes([0xC0, 34])),   # electric bass finger
            (0, note_on(0, 40, 83)),
            (480, note_off(0, 40)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        data = parse_midi(p)
        text = midi_to_acml_text(data, name="bass")
        self.assertIn("instrument = bass", text)

    def test_convert_track_name_sanitized(self):
        """轨名被清理为合法 ACML 标识符"""
        p = self._path()
        write_midi_file(p, [[
            (0, meta_name("My Cool Track!")),
            (0, note_on(0, 60, 83)),
            (480, note_off(0, 60)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        data = parse_midi(p)
        text = midi_to_acml_text(data, name="x")
        self.assertIn("[track My_Cool_Track]", text)

    def test_convert_writes_file(self):
        """convert() 写出 .acml 文件"""
        p = self._path("in.mid")
        out = self._path("out.acml")
        write_midi_file(p, [[
            (0, note_on(0, 60, 83)),
            (480, note_off(0, 60)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        text, path = convert(p, out)
        self.assertEqual(path, out)
        self.assertTrue(os.path.exists(out))
        with open(out, encoding="utf-8") as f:
            self.assertEqual(f.read(), text)

    def test_convert_default_output_path(self):
        """未指定输出时默认替换扩展名为 .acml"""
        p = self._path("song.mid")
        write_midi_file(p, [[
            (0, note_on(0, 60, 83)),
            (480, note_off(0, 60)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        text, path = convert(p)
        self.assertEqual(path, os.path.join(self.dir, "song.acml"))
        self.assertTrue(os.path.exists(path))
        os.remove(path)

    def test_convert_missing_file_raises(self):
        """缺失文件抛出 FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            convert(os.path.join(self.dir, "nope.mid"))


class TestRoundTrip(unittest.TestCase):
    """ACML -> MIDI (composer) -> ACML (midiconv) 往返"""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="acm_rt_")

    def test_roundtrip_notes_preserved(self):
        """往返后音高与时值保持"""
        composer = Composer(bpm=120, duration=2)
        composer.add_track(Track(
            instrument="piano", scale="C", pattern="pop",
            notes="C4:q:mf,D4:q:mf,E4:q:mf,F4:q:mf",
        ))
        wav = os.path.join(self.dir, "rt.wav")
        mid = os.path.join(self.dir, "rt.mid")
        composer.generate(wav, mid)

        data = parse_midi(mid)
        self.assertAlmostEqual(data["bpm"], 120.0, delta=0.5)
        notes = data["channels"][0]["notes"]
        pitches = [n["pitch"] for n in notes]
        self.assertEqual(pitches, [60, 62, 64, 65])
        # 每个音符应持续 1 拍 (480 ticks @ 480 tpb)
        self.assertEqual(data["ticks_per_beat"], 480)
        for n in notes:
            self.assertEqual(n["end"] - n["start"], 480)

        text = midi_to_acml_text(data, name="rt")
        self.assertIn("C4:q:mf", text)
        self.assertIn("D4:q:mf", text)
        self.assertIn("E4:q:mf", text)
        self.assertIn("F4:q:mf", text)

    def test_roundtrip_acml_recompiles(self):
        """往返生成的 ACML 可以被 acml.parse_acml 解析"""
        composer = Composer(bpm=100, duration=2)
        composer.add_track(Track(
            instrument="guitar", scale="C", pattern="pop",
            notes="G3:q:mf,B3:q:mf,D4:q:mf,G4:h:mf",
        ))
        wav = os.path.join(self.dir, "rt2.wav")
        mid = os.path.join(self.dir, "rt2.mid")
        composer.generate(wav, mid)

        data = parse_midi(mid)
        text = midi_to_acml_text(data, name="rt2")
        acml_path = os.path.join(self.dir, "rt2.acml")
        with open(acml_path, "w", encoding="utf-8") as f:
            f.write(text)

        name, bpm, loop, tracks = parse_acml(acml_path)
        self.assertEqual(name, "rt2")
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]["instrument"], "guitar")
        self.assertIn("G3:q:mf", tracks[0]["notes"])

    def test_roundtrip_drums(self):
        """鼓 pattern 往返保留 K/S/H 字母"""
        composer = Composer(bpm=120, duration=2)
        composer.add_track(Track(
            instrument="drums", scale="C", pattern="pop",
            notes="K:q:mf,S:q:mf,K:q:mf,S:q:mf",
        ))
        wav = os.path.join(self.dir, "dr.wav")
        mid = os.path.join(self.dir, "dr.mid")
        composer.generate(wav, mid)

        data = parse_midi(mid)
        self.assertIn(9, data["channels"])
        text = midi_to_acml_text(data, name="dr")
        self.assertIn("instrument = drums", text)
        self.assertIn("[track kick]", text)
        self.assertIn("[track snare]", text)


class TestCliMidiconv(unittest.TestCase):
    def test_cli_midiconv_runs(self):
        """CLI midiconv 子命令可以执行"""
        from cli import main
        import io
        import contextlib
        d = tempfile.mkdtemp(prefix="acm_cli_")
        mid = os.path.join(d, "c.mid")
        write_midi_file(mid, [[
            (0, note_on(0, 60, 83)),
            (480, note_off(0, 60)),
            (0, bytes([0xFF, 0x2F, 0x00])),
        ]], division=480)
        out = os.path.join(d, "c.acml")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["midiconv", mid, "-o", out])
        self.assertTrue(os.path.exists(out))
        self.assertIn("Converted:", buf.getvalue())

    def test_cli_midiconv_missing_file(self):
        """CLI midiconv 缺失文件输出错误"""
        from cli import main
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["midiconv", "definitely_missing_xyz.mid"])
        self.assertIn("Error:", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
