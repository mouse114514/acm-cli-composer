import unittest
from track import Track

class TestTrack(unittest.TestCase):
    def test_create_track_with_instrument(self):
        """音轨可以被创建并设置音色"""
        track = Track(instrument="piano")
        self.assertEqual(track.instrument, "piano")

    def test_track_with_pattern(self):
        """音轨可以设置节奏模式"""
        track = Track(instrument="piano", pattern="pop")
        self.assertEqual(track.pattern, "pop")

    def test_track_with_scale(self):
        """音轨可以设置音阶"""
        track = Track(instrument="piano", scale="C")
        self.assertEqual(track.scale, "C")

    def test_track_with_octave(self):
        """音轨可以设置八度"""
        track = Track(instrument="piano", scale="C", octave=4)
        self.assertEqual(track.octave, 4)

    def test_track_with_notes(self):
        """音轨可以设置音符序列"""
        track = Track(instrument="piano", notes="C4,D4,E4,F4")
        self.assertEqual(track.notes, "C4,D4,E4,F4")

    def test_track_with_volume(self):
        """音轨可以设置音量"""
        track = Track(instrument="piano", volume=0.5)
        self.assertEqual(track.volume, 0.5)

    def test_track_custom_pattern_string(self):
        """音轨支持自定义二进制pattern字符串"""
        track = Track(instrument="piano", pattern="10100101")
        self.assertEqual(track.pattern, "10100101")

    def test_track_drum_independent_patterns(self):
        """鼓点音轨支持独立的kick/snare/hihat节奏"""
        track = Track(instrument="drums", kick="10001000", snare="00100010", hihat="11111111")
        self.assertEqual(track.kick, "10001000")
        self.assertEqual(track.snare, "00100010")
        self.assertEqual(track.hihat, "11111111")

    def test_track_with_durations(self):
        """音轨支持不等长时值参数"""
        track = Track(instrument="piano", durations="2,1,1,2")
        self.assertEqual(track.durations, "2,1,1,2")

    def test_track_with_arpeggio(self):
        """音轨支持琶音模式"""
        for mode in ("up", "down", "random", "updown", "downup"):
            track = Track(instrument="piano", arpeggio=mode)
            self.assertEqual(track.arpeggio, mode)

    def test_track_with_loops(self):
        """音轨支持循环次数"""
        track = Track(instrument="piano", loops=4)
        self.assertEqual(track.loops, 4)

    def test_track_loops_defaults_to_one(self):
        """loops默认为1"""
        track = Track(instrument="piano")
        self.assertEqual(track.loops, 1)

    def test_track_with_fm_ratio(self):
        """音轨支持FM调制比"""
        track = Track(instrument="fm", fm_ratio=4.0)
        self.assertEqual(track.fm_ratio, 4.0)

    def test_track_with_fm_index(self):
        """音轨支持FM调制指数"""
        track = Track(instrument="fm", fm_index=5.0)
        self.assertEqual(track.fm_index, 5.0)

    def test_track_fm_defaults_to_none(self):
        """fm_ratio/fm_index默认为None"""
        track = Track(instrument="fm")
        self.assertIsNone(track.fm_ratio)
        self.assertIsNone(track.fm_index)

if __name__ == "__main__":
    unittest.main()
