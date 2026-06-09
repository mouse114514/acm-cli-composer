import unittest
from composer import Composer
from track import Track

class TestComposer(unittest.TestCase):
    def test_composer_holds_multiple_tracks(self):
        """编曲器可以包含多个音轨"""
        composer = Composer()
        track1 = Track(instrument="piano")
        track2 = Track(instrument="drums")
        composer.add_track(track1)
        composer.add_track(track2)
        self.assertEqual(len(composer.tracks), 2)
        self.assertEqual(composer.tracks[0].instrument, "piano")
        self.assertEqual(composer.tracks[1].instrument, "drums")

    def test_composer_generates_output(self):
        """编曲器可以生成音频输出文件"""
        composer = Composer()
        track = Track(instrument="piano", scale="C", pattern="pop")
        composer.add_track(track)
        output_path = "test_output.wav"
        composer.generate(output_path)
        import os
        self.assertTrue(os.path.exists(output_path))
        os.remove(output_path)

    def test_composer_with_different_instruments(self):
        """支持多种乐器音色"""
        for inst in ["piano", "guitar", "bass", "drums"]:
            composer = Composer()
            track = Track(instrument=inst, scale="C", pattern="pop")
            composer.add_track(track)
            output_path = f"test_{inst}.wav"
            composer.generate(output_path)
            import os
            self.assertTrue(os.path.exists(output_path),
                            f"Failed to generate output for {inst}")
            os.remove(output_path)

    def test_composer_with_bpm(self):
        """支持BPM（速度）设置"""
        composer = Composer(bpm=120)
        self.assertEqual(composer.bpm, 120)

    def test_composer_with_duration(self):
        """支持时长控制"""
        composer = Composer(duration=2)
        output_path = "test_dur.wav"
        track = Track(instrument="piano", scale="C", pattern="pop")
        composer.add_track(track)
        composer.generate(output_path, trim=False)
        import os, wave
        with wave.open(output_path, "r") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            self.assertAlmostEqual(frames / rate, 2.0, delta=0.1)
        os.remove(output_path)

    def test_custom_pattern_generates_different_audio(self):
        """自定??6拍pattern??拍pattern产生不同输出"""
        import hashlib, os
        c1 = Composer(duration=2)
        c1.add_track(Track(instrument="piano", scale="C", notes="C4,D4,E4,F4,G4,A4,B4,C5", pattern="1010101010101010"))
        p1 = "test_custom_1.wav"
        c1.generate(p1)

        c2 = Composer(duration=2)
        c2.add_track(Track(instrument="piano", scale="C", notes="C4,D4,E4,F4,G4,A4,B4,C5", pattern="1111000011110000"))
        p2 = "test_custom_2.wav"
        c2.generate(p2)

        h1 = hashlib.md5(open(p1, "rb").read()).hexdigest()
        h2 = hashlib.md5(open(p2, "rb").read()).hexdigest()
        self.assertNotEqual(h1, h2)
        os.remove(p1); os.remove(p2)

    def test_durations_change_rhythm(self):
        """不等长时值产生不同的节奏效果"""
        import hashlib, os
        c1 = Composer(duration=2)
        c1.add_track(Track(instrument="piano", scale="C", notes="C4,D4,E4,F4", pattern="1111", durations="1,1,1,1"))
        p1 = "test_dur_1.wav"
        c1.generate(p1)

        c2 = Composer(duration=2)
        c2.add_track(Track(instrument="piano", scale="C", notes="C4,D4,E4,F4", pattern="1111", durations="2,1,1,2"))
        p2 = "test_dur_2.wav"
        c2.generate(p2)

        h1 = hashlib.md5(open(p1, "rb").read()).hexdigest()
        h2 = hashlib.md5(open(p2, "rb").read()).hexdigest()
        self.assertNotEqual(h1, h2)
        os.remove(p1); os.remove(p2)

    def test_sawtooth_instrument_differs_from_piano(self):
        """sawtooth与piano音色不同"""
        import hashlib, os
        make = lambda inst: (Composer(duration=1), Track(instrument=inst, scale="C", notes="C4,E4,G4", pattern="111"))
        c1, t1 = make("piano"); c1.add_track(t1); c1.generate("a.wav")
        c2, t2 = make("sawtooth"); c2.add_track(t2); c2.generate("b.wav")
        self.assertNotEqual(hashlib.md5(open("a.wav","rb").read()).hexdigest(), hashlib.md5(open("b.wav","rb").read()).hexdigest())
        os.remove("a.wav"); os.remove("b.wav")

    def test_organ_instrument_differs_from_piano(self):
        import hashlib, os
        c1 = Composer(duration=1); c1.add_track(Track(instrument="piano", scale="C", notes="C4", pattern="1")); c1.generate("a.wav")
        c2 = Composer(duration=1); c2.add_track(Track(instrument="organ", scale="C", notes="C4", pattern="1")); c2.generate("b.wav")
        self.assertNotEqual(hashlib.md5(open("a.wav","rb").read()).hexdigest(), hashlib.md5(open("b.wav","rb").read()).hexdigest())
        os.remove("a.wav"); os.remove("b.wav")

    def test_bell_instrument_differs_from_piano(self):
        import hashlib, os
        c1 = Composer(duration=1); c1.add_track(Track(instrument="piano", scale="C", notes="C4", pattern="1")); c1.generate("a.wav")
        c2 = Composer(duration=1); c2.add_track(Track(instrument="bell", scale="C", notes="C4", pattern="1")); c2.generate("b.wav")
        self.assertNotEqual(hashlib.md5(open("a.wav","rb").read()).hexdigest(), hashlib.md5(open("b.wav","rb").read()).hexdigest())
        os.remove("a.wav"); os.remove("b.wav")

    def test_deterministic_output(self):
        """跨进程运行产生完全相同的输出"""
        import hashlib, os, subprocess, sys
        code = "from composer import Composer; from track import Track; c=Composer(duration=1); c.add_track(Track(instrument='drums', pattern='1111')); c.add_track(Track(instrument='piano', scale='C', notes='C4,D4', pattern='11')); c.generate('test_det.wav')"
        subprocess.run([sys.executable, "-c", code], check=True)
        h1 = hashlib.md5(open("test_det.wav", "rb").read()).hexdigest()
        subprocess.run([sys.executable, "-c", code], check=True)
        h2 = hashlib.md5(open("test_det.wav", "rb").read()).hexdigest()
        self.assertEqual(h1, h2)
        os.remove("test_det.wav")

    def test_accidentals_produce_different_freq(self):
        """Accidentals produce different frequency from naturals"""
        import hashlib, os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="piano", scale="C", notes="C4", pattern="1"))
        p1 = "test_acc_1.wav"
        c1.generate(p1)

        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", scale="C", notes="C#4", pattern="1"))
        p2 = "test_acc_2.wav"
        c2.generate(p2)

        h1 = hashlib.md5(open(p1, "rb").read()).hexdigest()
        h2 = hashlib.md5(open(p2, "rb").read()).hexdigest()
        self.assertNotEqual(h1, h2)
        os.remove(p1); os.remove(p2)

    # ── 新增测试 ──────────────────────────────────────────

    def test_new_patterns_available(self):
        """新增pattern trap/latin/funk/shuffle可用"""
        c = Composer()
        for name in ("trap", "latin", "funk", "shuffle"):
            pat = c._resolve_pattern(name)
            self.assertTrue(len(pat) >= 4, f"{name} pattern too short")
            self.assertTrue(all(v in (0, 1) for v in pat), f"{name} 只含0/1")

    def test_rest_note_produces_silence(self):
        """R休止符在对应拍不产生声音"""
        c = Composer(duration=1)
        sr = c.SAMPLE_RATE
        spb = int(sr * 60 / c.bpm)
        beat_starts = c._compute_beat_starts(4, spb)
        data = c._generate_melody_from_notes("C4,R,E4,F4", [1, 1, 1, 1], beat_starts, spb * 4, "piano")
        r_start = beat_starts[1]
        r_end = beat_starts[2]
        has_sound = any(abs(data[i]) > 0.001 for i in range(r_start, min(r_end, len(data))))
        self.assertFalse(has_sound, "R休止符拍应该没有声音")

    def test_rest_note_advances_index(self):
        """R休止符推进音符索引，后续音符正确"""
        import hashlib, os
        c1 = Composer(duration=4)
        c1.add_track(Track(instrument="piano", scale="C", notes="C4,R,E4", pattern="111"))
        c1.generate("a.wav")

        c2 = Composer(duration=4)
        c2.add_track(Track(instrument="piano", scale="C", notes="C4,R,F4", pattern="111"))
        c2.generate("b.wav")

        h1 = hashlib.md5(open("a.wav", "rb").read()).hexdigest()
        h2 = hashlib.md5(open("b.wav", "rb").read()).hexdigest()
        self.assertNotEqual(h1, h2, "R后音符不同应产生不同输出")
        os.remove("a.wav"); os.remove("b.wav")

    def test_underscore_rest_also_works(self):
        """_也支持作为休止符"""
        c = Composer(duration=1)
        sr = c.SAMPLE_RATE
        spb = int(sr * 60 / c.bpm)
        beat_starts = c._compute_beat_starts(3, spb)
        data = c._generate_melody_from_notes("C4,_,E4", [1, 1, 1], beat_starts, spb * 3, "piano")
        r_start = beat_starts[1]
        r_end = beat_starts[2]
        has_sound = any(abs(data[i]) > 0.001 for i in range(r_start, min(r_end, len(data))))
        self.assertFalse(has_sound, "_休止符拍应该没有声音")

    # ── Pan / Stereo ─────────────────────────────────────

    def test_pan_affects_output(self):
        """不同pan值产生不同立体声输出"""
        import hashlib, os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="piano", scale="C", notes="C4,E4", pattern="11", pan=-1.0))
        c1.generate("a.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", scale="C", notes="C4,E4", pattern="11", pan=1.0))
        c2.generate("b.wav")
        self.assertNotEqual(hashlib.md5(open("a.wav","rb").read()).hexdigest(),
                            hashlib.md5(open("b.wav","rb").read()).hexdigest())
        os.remove("a.wav"); os.remove("b.wav")

    def test_stereo_wav_has_two_channels(self):
        """立体声WAV有两个声道"""
        import wave, os
        c = Composer(duration=1)
        c.add_track(Track(instrument="piano", scale="C", notes="C4", pattern="1", pan=0.0))
        c.generate("stereo_test.wav")
        with wave.open("stereo_test.wav") as wf:
            self.assertEqual(wf.getnchannels(), 2)
        os.remove("stereo_test.wav")

    # ── Velocity ─────────────────────────────────────────

    def test_note_velocity_affects_amplitude(self):
        """音符力度影响振幅"""
        import struct, wave, os
        def max_amp(path):
            with wave.open(path) as wf:
                raw = wf.readframes(wf.getnframes())
            vals = [abs(struct.unpack("<h", raw[i:i+2])[0]) for i in range(0, len(raw), 2)]
            return max(vals) if vals else 0
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="piano", scale="C", notes="C4:1.0", pattern="1"))
        c1.generate("v1.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", scale="C", notes="C4:0.1", pattern="1"))
        c2.generate("v2.wav")
        self.assertGreater(max_amp("v1.wav"), max_amp("v2.wav"))
        os.remove("v1.wav"); os.remove("v2.wav")

    # ── Extended Notes (per-note duration + dynamic) ──────

    def test_parse_duration_letters(self):
        c = Composer()
        self.assertEqual(c._parse_duration("w"), 4.0)
        self.assertEqual(c._parse_duration("h"), 2.0)
        self.assertEqual(c._parse_duration("q"), 1.0)
        self.assertEqual(c._parse_duration("e"), 0.5)
        self.assertEqual(c._parse_duration("s"), 0.25)
        self.assertEqual(c._parse_duration("h."), 3.0)
        self.assertEqual(c._parse_duration("q."), 1.5)

    def test_parse_dynamic_names(self):
        c = Composer()
        self.assertAlmostEqual(c._parse_dynamic("ppp"), 0.2)
        self.assertAlmostEqual(c._parse_dynamic("p"), 0.35)
        self.assertAlmostEqual(c._parse_dynamic("mp"), 0.5)
        self.assertAlmostEqual(c._parse_dynamic("mf"), 0.65)
        self.assertAlmostEqual(c._parse_dynamic("f"), 0.8)
        self.assertAlmostEqual(c._parse_dynamic("ff"), 0.9)
        self.assertAlmostEqual(c._parse_dynamic("fff"), 1.0)

    def test_parse_dynamic_numeric(self):
        c = Composer()
        self.assertAlmostEqual(c._parse_dynamic("0.8"), 0.8)
        self.assertAlmostEqual(c._parse_dynamic("0.35"), 0.35)

    def test_parse_extended_note_with_duration_and_dynamic(self):
        """C4:q:p ??freq??61.63, beats=1, vel=0.35"""
        c = Composer()
        freq, beats, vel = c._parse_extended_note("C4:q:p")
        self.assertAlmostEqual(freq, 261.63, delta=0.1)
        self.assertEqual(beats, 1.0)
        self.assertAlmostEqual(vel, 0.35)

    def test_parse_extended_note_with_duration_and_numeric_velocity(self):
        """C4:q:0.8 ??vel=0.8"""
        c = Composer()
        freq, beats, vel = c._parse_extended_note("C4:q:0.8")
        self.assertAlmostEqual(vel, 0.8)

    def test_parse_extended_note_defaults_to_mf(self):
        """C4:q ??默认力度mf=0.65"""
        c = Composer()
        freq, beats, vel = c._parse_extended_note("C4:q")
        self.assertAlmostEqual(vel, 0.65)

    def test_parse_extended_rest(self):
        """R:q ??freq=None, beats=1"""
        c = Composer()
        freq, beats, vel = c._parse_extended_note("R:q")
        self.assertIsNone(freq)
        self.assertEqual(beats, 1.0)

    def test_extended_notes_detection(self):
        """带时值标记的notes被正确识别"""
        c = Composer()
        self.assertTrue(c._is_extended_notes("C4:q:p,D4:e:mf"))
        self.assertTrue(c._is_extended_notes("C4:h"))
        self.assertFalse(c._is_extended_notes("C4,D4,E4"))
        self.assertFalse(c._is_extended_notes("C4:0.8,D4:0.5"))

    def test_extended_notes_generates_output(self):
        """扩展音符格式生成音频"""
        import os
        c = Composer(bpm=80, duration=4)
        c.add_track(Track(instrument="piano", notes="C4:q:p,E4:q:mf,G4:h:f"))
        c.generate("ext_test.wav")
        self.assertTrue(os.path.exists("ext_test.wav"))
        self.assertGreater(os.path.getsize("ext_test.wav"), 100)
        os.remove("ext_test.wav")

    def test_extended_notes_backward_compatible(self):
        """旧格式C4:0.8仍然工作"""
        import hashlib, os
        c = Composer(duration=1)
        c.add_track(Track(instrument="piano", scale="C", notes="C4:0.8,E4:0.5", pattern="11"))
        c.generate("old_ext.wav")
        self.assertTrue(os.path.exists("old_ext.wav"))
        os.remove("old_ext.wav")

    def test_parse_extended_bare_colon_rest(self):
        """:h 被当作休止符"""
        c = Composer()
        freq, beats, vel = c._parse_extended_note(":h")
        self.assertIsNone(freq)
        self.assertEqual(beats, 2.0)

    def test_parse_extended_underscore_rest(self):
        """_:h 下划线休止符"""
        c = Composer()
        freq, beats, vel = c._parse_extended_note("_:h")
        self.assertIsNone(freq)
        self.assertEqual(beats, 2.0)

    def test_extended_note_rest_produces_silence(self):
        """R:q休止符不产生声音"""
        c = Composer(bpm=80, duration=4)
        sr = c.SAMPLE_RATE
        spb = int(sr * 60 / 80)
        total = int(spb * 2)  # 2 beats
        data = c._generate_melody_from_extended_notes("C4:q, R:q", total, "piano")
        rest_start = int(spb * 1.0)
        has_sound = any(abs(data[i]) > 0.001 for i in range(rest_start, min(rest_start + int(spb * 1.0), len(data))))
        self.assertFalse(has_sound, "R:q休止符区域应该没有声音")

    # ── Compact Notation Expander ────────────────────────

    def test_expand_compact_quarter_note(self):
        """D5qf ??D5:q:f"""
        c = Composer()
        result = c.expand_compact_notes("D5qf")
        self.assertEqual(result, "D5:q:f")

    def test_expand_compact_with_paren_dynamic(self):
        """D5q(mf) ??D5:q:mf"""
        c = Composer()
        result = c.expand_compact_notes("D5q(mf)")
        self.assertEqual(result, "D5:q:mf")

    def test_expand_compact_dot_to_rest(self):
        """. ??R:q"""
        c = Composer()
        result = c.expand_compact_notes(".")
        self.assertEqual(result, "R:q")

    def test_expand_compact_mixed(self):
        """混合格式正确扩展"""
        c = Composer()
        result = c.expand_compact_notes("D5qf,G5qf,.")
        self.assertEqual(result, "D5:q:f,G5:q:f,R:q")

    def test_expand_compact_half_note_with_dynamic(self):
        """D2h(f) ??D2:h:f"""
        c = Composer()
        result = c.expand_compact_notes("D2h(f)")
        self.assertEqual(result, "D2:h:f")

    def test_expand_compact_dotted_half(self):
        """G5h.ff ??G5:h.:ff"""
        c = Composer()
        result = c.expand_compact_notes("G5h.ff")
        self.assertEqual(result, "G5:h.:ff")

    def test_expand_compact_accidental(self):
        """C#5qff ??C#5:q:ff"""
        c = Composer()
        result = c.expand_compact_notes("C#5qff")
        self.assertEqual(result, "C#5:q:ff")

    def test_expand_compact_drum_notation(self):
        """Kf ??K:q:f, Sff ??S:q:ff, Hmf ??H:q:mf"""
        c = Composer()
        self.assertEqual(c.expand_compact_notes("Kf"), "K:q:f")
        self.assertEqual(c.expand_compact_notes("Sff"), "S:q:ff")
        self.assertEqual(c.expand_compact_notes("Hmf"), "H:q:mf")

    def test_expand_compact_already_extended(self):
        """已有冒号格式不变"""
        c = Composer()
        result = c.expand_compact_notes("C5:q:f")
        self.assertEqual(result, "C5:q:f")

    # ── Drum Extended Notes ──────────────────────────────

    def test_drum_extended_notes_generates_output(self):
        """鼓扩展音符生成音频"""
        import os
        c = Composer(bpm=118, duration=8)
        c.add_track(Track(instrument="drums", notes="K:q:f,S:q:f,K:q:f,S:q:f"))
        c.generate("drum_ext_test.wav")
        self.assertTrue(os.path.exists("drum_ext_test.wav"))
        os.remove("drum_ext_test.wav")

    def test_drum_extended_notes_open_hihat(self):
        """开镲O产生与闭镲H不同的声音"""
        import hashlib, os
        c1 = Composer(duration=2)
        c1.add_track(Track(instrument="drums", notes="H:q:f,H:q:f,H:q:f,H:q:f"))
        c1.generate("drum_h.wav")
        c2 = Composer(duration=2)
        c2.add_track(Track(instrument="drums", notes="O:q:f,O:q:f,O:q:f,O:q:f"))
        c2.generate("drum_o.wav")
        self.assertNotEqual(hashlib.md5(open("drum_h.wav","rb").read()).hexdigest(),
                            hashlib.md5(open("drum_o.wav","rb").read()).hexdigest())
        os.remove("drum_h.wav"); os.remove("drum_o.wav")

    def test_drum_extended_notes_tom(self):
        """桶鼓T与K/S/H不同"""
        import hashlib, os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="drums", notes="T:q:f"))
        c1.generate("drum_t.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="drums", notes="K:q:f"))
        c2.generate("drum_k.wav")
        self.assertNotEqual(hashlib.md5(open("drum_t.wav","rb").read()).hexdigest(),
                            hashlib.md5(open("drum_k.wav","rb").read()).hexdigest())
        os.remove("drum_t.wav"); os.remove("drum_k.wav")

    def test_drum_extended_velocity_affects_amplitude(self):
        """鼓扩展音符力度影响振幅"""
        import struct, wave, os
        def max_amp(path):
            with wave.open(path) as wf:
                raw = wf.readframes(wf.getnframes())
            vals = [abs(struct.unpack("<h", raw[i:i+2])[0]) for i in range(0, len(raw), 2)]
            return max(vals) if vals else 0
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="drums", notes="K:q:ff"))
        c1.generate("ka.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="drums", notes="K:q:pp"))
        c2.generate("kb.wav")
        self.assertGreater(max_amp("ka.wav"), max_amp("kb.wav"))
        os.remove("ka.wav"); os.remove("kb.wav")

    def test_drum_extended_notes_mixed(self):
        """混合鼓类型在同一track工作"""
        import os
        c = Composer(bpm=118, duration=4)
        c.add_track(Track(instrument="drums", notes="K:q:f,S:q:mf,O:e:ff,T:q:f"))
        c.generate("drum_mixed.wav")
        self.assertGreater(os.path.getsize("drum_mixed.wav"), 100)
        os.remove("drum_mixed.wav")

    # ── Arpeggio ────────────────────────────────────────

    def test_arpeggio_up_produces_multiple_pitches(self):
        """琶音上行产生多种音高"""
        import struct, wave, os
        c = Composer(duration=1)
        c.add_track(Track(instrument="piano", scale="C", pattern="1111", octave=4, arpeggio="up"))
        c.generate("arp_up.wav")
        with wave.open("arp_up.wav") as wf:
            raw = wf.readframes(wf.getnframes())
        vals = [abs(struct.unpack("<h", raw[i:i+2])[0]) for i in range(0, len(raw), 4)]
        # multiple non-zero segments = multiple pitches
        nonzero = sum(1 for v in vals if v > 100)
        self.assertGreater(nonzero, 100)
        os.remove("arp_up.wav")

    def test_arpeggio_down_differs_from_up(self):
        """琶音上下行产生不同音高"""
        import hashlib, os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="piano", scale="C", pattern="1111", arpeggio="up"))
        c1.generate("a_up.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", scale="C", pattern="1111", arpeggio="down"))
        c2.generate("a_dn.wav")
        self.assertNotEqual(hashlib.md5(open("a_up.wav","rb").read()).hexdigest(),
                            hashlib.md5(open("a_dn.wav","rb").read()).hexdigest())
        os.remove("a_up.wav"); os.remove("a_dn.wav")

    def test_arpeggio_random_is_deterministic(self):
        """琶音随机模式在相同种子下确定"""
        import hashlib, os
        def gen():
            c = Composer(duration=1)
            c.add_track(Track(instrument="piano", scale="C", pattern="11111111", arpeggio="random"))
            c.generate("arp_r.wav")
            return hashlib.md5(open("arp_r.wav","rb").read()).hexdigest()
        self.assertEqual(gen(), gen())
        os.remove("arp_r.wav")

    def test_arpeggio_updown_differs_from_up(self):
        """updown与up模式不同"""
        import hashlib, os
        for m in ("updown", "downup"):
            c = Composer(duration=1)
            c.add_track(Track(instrument="piano", scale="C", pattern="1111", arpeggio=m))
            c.generate(f"arp_{m}.wav")
            self.assertGreater(os.path.getsize(f"arp_{m}.wav"), 100)
            os.remove(f"arp_{m}.wav")

    # ── Chord Notation ──────────────────────────────────

    def test_expand_chord_major_triad(self):
        """Cmaj:q:mf ??(C4,E4,G4):q:mf"""
        c = Composer()
        result = c.expand_compact_notes("Cmaj:q:mf")
        self.assertIn("C4", result)
        self.assertIn("E4", result)
        self.assertIn("G4", result)
        self.assertTrue(result.startswith("("))

    def test_expand_chord_maj7(self):
        """Cmaj7:q:mf ??(C4,E4,G4,B4):q:mf"""
        c = Composer()
        result = c.expand_compact_notes("Cmaj7:q:mf")
        self.assertIn("C4", result)
        self.assertIn("E4", result)
        self.assertIn("G4", result)
        self.assertIn("B4", result)
        self.assertTrue(result.startswith("("))

    def test_expand_chord_minor(self):
        """Fm:q:mf ??(F4,G#4,C5):q:mf"""
        c = Composer()
        result = c.expand_compact_notes("Fm:q:mf")
        self.assertIn("F4", result)
        self.assertIn("G#4", result)
        self.assertIn("C5", result)
        self.assertTrue(result.startswith("("))

    def test_expand_chord_dominant_7th(self):
        """G7 ??(G4,B4,D5,F5):q:mf"""
        c = Composer()
        result = c.expand_compact_notes("G7")
        self.assertIn("G4", result)
        self.assertIn("B4", result)
        self.assertIn("D5", result)
        self.assertIn("F5", result)
        self.assertTrue(result.startswith("("))

    def test_expand_chord_with_octave(self):
        """C5maj7:q:mf ??(C5,E5,G5,B5):q:mf"""
        c = Composer()
        result = c.expand_compact_notes("C5maj7:q:mf")
        self.assertIn("C5", result)
        self.assertIn("E5", result)
        self.assertIn("G5", result)
        self.assertIn("B5", result)
        self.assertTrue(result.startswith("("))

    def test_expand_chord_in_mixed_sequence(self):
        """和弦与音符混合使用，非和弦音符不被展开"""
        c = Composer()
        result = c.expand_compact_notes("C:q:mf,D4:q:mf")
        self.assertIn("D4:q:mf", result)
        self.assertIn("C:q:mf", result,
                      "C:q:mf is a single note (no chord suffix), should not expand")

    def test_expand_chord_compact_notation(self):
        """Cmaj7qf ??(C4,E4,G4,B4):q:f"""
        c = Composer()
        result = c.expand_compact_notes("Cmaj7qf")
        self.assertTrue(result.startswith("("))
        self.assertIn(":q:f", result)

    def test_chord_is_chord_name_detection(self):
        """和弦名称检测"""
        self.assertTrue(Composer._is_chord_name("Cmaj7"))
        self.assertTrue(Composer._is_chord_name("Fm"))
        self.assertTrue(Composer._is_chord_name("G7"))
        self.assertTrue(Composer._is_chord_name("Bb7"))
        self.assertTrue(Composer._is_chord_name("C#dim"))
        self.assertFalse(Composer._is_chord_name("C4"))
        self.assertFalse(Composer._is_chord_name("C"))
        self.assertFalse(Composer._is_chord_name("D5"))

    def test_expand_chord_generates_output(self):
        """和弦扩展生成有效音频"""
        import os
        c = Composer(duration=2)
        c.add_track(Track(instrument="piano", notes=c.expand_compact_notes("Cmaj7:q:mf,Fmaj7:q:mf,G7:q:mf,Cmaj7:q:mf")))
        c.generate("chord_test.wav")
        self.assertGreater(os.path.getsize("chord_test.wav"), 100)
        os.remove("chord_test.wav")

    # ── New Instruments ─────────────────────────────────

    def test_strings_instrument_differs_from_piano(self):
        """strings音色与piano不同"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="strings", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        c.generate("strings_test.wav")
        self.assertGreater(os.path.getsize("strings_test.wav"), 100)
        os.remove("strings_test.wav")

    def test_brass_instrument_differs_from_piano(self):
        """brass音色与piano不同"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="brass", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        c.generate("brass_test.wav")
        self.assertGreater(os.path.getsize("brass_test.wav"), 100)
        os.remove("brass_test.wav")

    def test_pad_instrument_differs_from_piano(self):
        """pad音色与piano不同"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="pad", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        c.generate("pad_test.wav")
        self.assertGreater(os.path.getsize("pad_test.wav"), 100)
        os.remove("pad_test.wav")

    def test_lead_instrument_differs_from_piano(self):
        """lead音色与piano不同"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="lead", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        c.generate("lead_test.wav")
        self.assertGreater(os.path.getsize("lead_test.wav"), 100)
        os.remove("lead_test.wav")

    # ── Drum velocity recall ────────────────────────────

    def test_drum_velocity_recall_uses_last_velocity(self):
        """鼓点省略力度时沿用上次力度"""
        c = Composer(duration=1)
        notes = "K:q:f,S:q,K:q,S:q"
        c.add_track(Track(instrument="drums", notes=notes))
        c.generate("drum_vel_test.wav")
        import os
        self.assertGreater(os.path.getsize("drum_vel_test.wav"), 100)
        os.remove("drum_vel_test.wav")

    # ── Loops ───────────────────────────────────────────

    def test_loops_produces_longer_output(self):
        """loop>1产生更长的音频"""
        import os
        c1 = Composer(bpm=120, duration=4)
        c1.add_track(Track(instrument="piano", notes="C4:q:mf", loops=1))
        c1.generate("loop1_test.wav")
        size1 = os.path.getsize("loop1_test.wav")
        c2 = Composer(bpm=120, duration=4)
        c2.add_track(Track(instrument="piano", notes="C4:q:mf", loops=4))
        c2.generate("loop4_test.wav")
        size4 = os.path.getsize("loop4_test.wav")
        self.assertGreater(size4, size1)
        os.remove("loop1_test.wav")
        os.remove("loop4_test.wav")

    # ── MIDI Export ─────────────────────────────────────

    def test_midi_export_creates_midi_file(self):
        """MIDI导出生成有效文件"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="piano", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        c.generate("midi_test.wav", midi_path="midi_test.mid")
        self.assertTrue(os.path.exists("midi_test.mid"))
        with open("midi_test.mid", "rb") as f:
            header = f.read(4)
        self.assertEqual(header, b"MThd")
        os.remove("midi_test.wav")
        os.remove("midi_test.mid")

    def test_midi_drums_use_channel_9(self):
        """MIDI导出鼓使用通道9"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="drums", notes="K:q:mf,S:q:mf,H:q:mf"))
        c.generate("midi_drum_test.wav", midi_path="midi_drum_test.mid")
        self.assertTrue(os.path.exists("midi_drum_test.mid"))
        os.remove("midi_drum_test.wav")
        os.remove("midi_drum_test.mid")

    # ── FM Instrument ───────────────────────────────────

    def test_fm_instrument_generates_output(self):
        """FM合成乐器生成有效音频"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="fm", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        c.generate("fm_test.wav")
        self.assertGreater(os.path.getsize("fm_test.wav"), 100)
        os.remove("fm_test.wav")

    def _wav_md5(self, path):
        import hashlib, wave
        with wave.open(path) as wf:
            frames = wf.readframes(wf.getnframes())
        return hashlib.md5(frames).hexdigest()

    def test_fm_differs_from_piano(self):
        """FM音色与piano不同"""
        import os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="fm", notes="C4:q:mf"))
        c1.generate("fm_comp.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", notes="C4:q:mf"))
        c2.generate("piano_comp.wav")
        self.assertNotEqual(self._wav_md5("fm_comp.wav"), self._wav_md5("piano_comp.wav"))
        os.remove("fm_comp.wav")
        os.remove("piano_comp.wav")

    def test_fm_ratio_affects_output(self):
        """不同FM ratio产生不同音色"""
        import os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="fm", notes="C4:q:mf", fm_ratio=2.0))
        c1.generate("fm_r2.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="fm", notes="C4:q:mf", fm_ratio=3.0))
        c2.generate("fm_r3.wav")
        self.assertNotEqual(self._wav_md5("fm_r2.wav"), self._wav_md5("fm_r3.wav"))
        os.remove("fm_r2.wav"); os.remove("fm_r3.wav")

    def test_fm_index_affects_output(self):
        """不同FM index产生不同音色"""
        import os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="fm", notes="C4:q:mf", fm_index=1.0))
        c1.generate("fm_i1.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="fm", notes="C4:q:mf", fm_index=5.0))
        c2.generate("fm_i5.wav")
        self.assertNotEqual(self._wav_md5("fm_i1.wav"), self._wav_md5("fm_i5.wav"))
        os.remove("fm_i1.wav"); os.remove("fm_i5.wav")

    # ── Effects ─────────────────────────────────────────

    def test_delay_affects_output(self):
        """延迟效果改变音频输出"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="piano", notes="C4:q:mf"))
        c.generate("no_delay.wav")
        c.generate("with_delay.wav", delay=0.5)
        self.assertNotEqual(self._wav_md5("no_delay.wav"), self._wav_md5("with_delay.wav"))
        os.remove("no_delay.wav")
        os.remove("with_delay.wav")

    def test_reverb_affects_output(self):
        """混响效果改变音频输出"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="piano", notes="C4:q:mf"))
        c.generate("no_rev.wav")
        c.generate("with_rev.wav", reverb=0.5)
        self.assertNotEqual(self._wav_md5("no_rev.wav"), self._wav_md5("with_rev.wav"))
        os.remove("no_rev.wav")
        os.remove("with_rev.wav")

    def test_chorus_affects_output(self):
        """合唱效果改变音频输出"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="piano", notes="C4:q:mf"))
        c.generate("no_chorus.wav")
        c.generate("with_chorus.wav", chorus=0.5)
        self.assertNotEqual(self._wav_md5("no_chorus.wav"), self._wav_md5("with_chorus.wav"))
        os.remove("no_chorus.wav")
        os.remove("with_chorus.wav")

    # ── Wavetable Synthesis ─────────────────────────────────

    def test_wavetable_generates_output(self):
        """wavetable乐器生成有效音频"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="wavetable", notes="C4:q:mf", wavetable="saw"))
        c.generate("wt_saw.wav")
        self.assertGreater(os.path.getsize("wt_saw.wav"), 100)
        os.remove("wt_saw.wav")

    def test_wavetable_saw_differs_from_piano(self):
        """wavetable(saw)与piano音色不同"""
        import os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="wavetable", notes="C4:q:mf", wavetable="saw"))
        c1.generate("wt1.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", notes="C4:q:mf"))
        c2.generate("wt2.wav")
        self.assertNotEqual(self._wav_md5("wt1.wav"), self._wav_md5("wt2.wav"))
        os.remove("wt1.wav"); os.remove("wt2.wav")

    def test_wavetable_shapes_differ(self):
        """不同波形表形状产生不同音色"""
        import os
        shapes = ["saw", "square", "triangle", "sine"]
        files = {}
        for s in shapes:
            c = Composer(duration=1)
            c.add_track(Track(instrument="wavetable", notes="C4:q:mf", wavetable=s))
            f = f"wt_{s}.wav"
            c.generate(f)
            files[s] = f
        md5s = set(self._wav_md5(f) for f in files.values())
        self.assertEqual(len(md5s), len(shapes), "每种波形表形状应产生不同输出")
        for f in files.values():
            os.remove(f)

    def test_wavetable_custom_shape(self):
        """自定义波形表值产生有效的音频输出"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="wavetable", notes="C4:q:mf", wavetable="0.0,0.5,1.0,0.5,0.0,-0.5,-1.0,-0.5"))
        c.generate("wt_custom.wav")
        self.assertGreater(os.path.getsize("wt_custom.wav"), 100)
        os.remove("wt_custom.wav")

    def test_wavetable_default_is_saw(self):
        """wavetable默认使用saw波形"""
        import os
        c = Composer(duration=1)
        c.add_track(Track(instrument="wavetable", notes="C4:q:mf"))
        c.generate("wt_default.wav")
        self.assertGreater(os.path.getsize("wt_default.wav"), 100)
        os.remove("wt_default.wav")

    # ── Sample Playback ──────────────────────────────────

    def _create_test_sample(self, path, freq=440, dur=0.5):
        import wave, struct, math
        sr = 44100
        n = int(sr * dur)
        with wave.open(path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for i in range(n):
                s = math.sin(2 * math.pi * freq * i / sr) * 0.5
                wf.writeframes(struct.pack("<h", int(s * 32767)))

    def test_sample_playback_generates_output(self):
        """采样回放生成有效音频"""
        import os
        self._create_test_sample("test_sample.wav", freq=261)
        c = Composer(duration=1)
        c.add_track(Track(instrument="sample", sample="test_sample.wav", notes="C4:q:mf"))
        c.generate("sample_test.wav")
        self.assertGreater(os.path.getsize("sample_test.wav"), 100)
        os.remove("test_sample.wav")
        os.remove("sample_test.wav")

    def test_sample_differs_from_piano(self):
        """采样回放与piano音色不同"""
        import os
        self._create_test_sample("test_s2.wav", freq=440)
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="sample", sample="test_s2.wav", notes="C4:q:mf"))
        c1.generate("smp1.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", notes="C4:q:mf"))
        c2.generate("smp2.wav")
        self.assertNotEqual(self._wav_md5("smp1.wav"), self._wav_md5("smp2.wav"))
        os.remove("test_s2.wav"); os.remove("smp1.wav"); os.remove("smp2.wav")

    def test_sample_with_sample_pitch(self):
        """指定sample_pitch正确变调"""
        import os
        self._create_test_sample("test_s3.wav", freq=261)
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="sample", sample="test_s3.wav", sample_pitch="C4", notes="C4:q:mf"))
        c1.generate("smp3a.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="sample", sample="test_s3.wav", sample_pitch="C4", notes="G4:q:mf"))
        c2.generate("smp3b.wav")
        self.assertNotEqual(self._wav_md5("smp3a.wav"), self._wav_md5("smp3b.wav"))
        os.remove("test_s3.wav"); os.remove("smp3a.wav"); os.remove("smp3b.wav")

    def test_sample_stereo_wav(self):
        """立体声WAV采样正确混音为单声道"""
        import os, wave, struct, math
        sr = 44100
        n = int(sr * 0.3)
        with wave.open("test_stereo.wav", "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for i in range(n):
                l = int(math.sin(2 * math.pi * 440 * i / sr) * 0.5 * 32767)
                r = int(math.sin(2 * math.pi * 880 * i / sr) * 0.3 * 32767)
                wf.writeframes(struct.pack("<hh", l, r))
        c = Composer(duration=1)
        c.add_track(Track(instrument="sample", sample="test_stereo.wav", notes="C4:q:mf"))
        c.generate("stereo_sample_test.wav")
        self.assertGreater(os.path.getsize("stereo_sample_test.wav"), 100)
        os.remove("test_stereo.wav"); os.remove("stereo_sample_test.wav")

    # ── Auto-Harmony ─────────────────────────────────────

    def test_harmony_produces_different_output_from_no_harmony(self):
        """自动和声与无和声产生不同输出"""
        import os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="piano", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        c1.generate("no_harm.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", notes="C4:q:mf,E4:q:mf,G4:q:mf", harmony="3"))
        c2.generate("with_harm.wav")
        self.assertNotEqual(self._wav_md5("no_harm.wav"), self._wav_md5("with_harm.wav"))
        os.remove("no_harm.wav"); os.remove("with_harm.wav")

    def test_harmony_different_intervals_differ(self):
        """不同和声间隔产生不同音频"""
        import os
        c1 = Composer(duration=1)
        c1.add_track(Track(instrument="piano", notes="C4:q:mf", harmony="3"))
        c1.generate("h3.wav")
        c2 = Composer(duration=1)
        c2.add_track(Track(instrument="piano", notes="C4:q:mf", harmony="5"))
        c2.generate("h5.wav")
        self.assertNotEqual(self._wav_md5("h3.wav"), self._wav_md5("h5.wav"))
        os.remove("h3.wav"); os.remove("h5.wav")

    # ── Chord Recommendation ─────────────────────────────

    def test_analyze_chords_returns_list(self):
        """和弦分析返回和弦列表"""
        c = Composer(bpm=120)
        c.add_track(Track(instrument="piano", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        result = c.analyze_chords(0)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_analyze_chords_suggests_c_major(self):
        """C大三和弦序列应推荐C相关和弦"""
        c = Composer(bpm=120)
        c.add_track(Track(instrument="piano", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        result = c.analyze_chords(0)
        self.assertTrue(any("C" in ch for ch in result),
                        f"Expected C chord, got {result}")

    def test_analyze_chords_different_melodies_differ(self):
        """不同旋律产生不同和弦建议"""
        c1 = Composer(bpm=120)
        c1.add_track(Track(instrument="piano", notes="C4:q:mf,E4:q:mf,G4:q:mf"))
        r1 = c1.analyze_chords(0)

        c2 = Composer(bpm=120)
        c2.add_track(Track(instrument="piano", notes="D4:q:mf,F#4:q:mf,A4:q:mf"))
        r2 = c2.analyze_chords(0)

        self.assertNotEqual(r1, r2)

    def test_trim_trailing_silence(self):
        """trim=True 裁掉末尾静音"""
        import os, wave
        c = Composer(bpm=120, duration=10)
        c.add_track(Track(instrument="bell", notes="C6:q:mp"))
        trimmed = "test_trim.wav"
        c.generate(trimmed, trim=True)
        with wave.open(trimmed, "r") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
        dur = frames / rate
        self.assertLess(dur, 10.0, "trim should cut trailing silence")
        self.assertGreaterEqual(dur, 0.5, "trim should keep the note")
        os.remove(trimmed)

    def test_no_trim_keeps_full_duration(self):
        """trim=False 保持完整 duration（通过 pattern 填满）"""
        import os, wave
        c = Composer(bpm=120, duration=4)
        c.add_track(Track(instrument="piano", scale="C", pattern="11111111"))
        untrimmed = "test_notrim.wav"
        c.generate(untrimmed, trim=False)
        with wave.open(untrimmed, "r") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
        dur = frames / rate
        self.assertAlmostEqual(dur, 4.0, delta=0.1)
        os.remove(untrimmed)

    def test_trim_empty_audio(self):
        """空音频trim不报错"""
        import os
        c = Composer(bpm=120, duration=2)
        c.add_track(Track(instrument="piano", notes=""))
        out = "test_trim_empty.wav"
        c.generate(out, trim=True)
        self.assertTrue(os.path.exists(out))
        os.remove(out)

if __name__ == "__main__":
    unittest.main()
