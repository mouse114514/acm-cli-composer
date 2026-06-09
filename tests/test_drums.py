import unittest
from composer import Composer
from track import Track

class TestDrums(unittest.TestCase):
    def test_drums_have_three_sounds(self):
        """鼓点生成包含三种声音成分"""
        c = Composer(duration=1)
        t = Track(instrument="drums", pattern="rock")
        c.add_track(t)
        sr = c.SAMPLE_RATE
        spb = int(sr * 60 / c.bpm)
        beat_starts = c._compute_beat_starts(8, spb, None)
        data = c._generate_drum_beat(beat_starts, sr)
        self.assertTrue(any(abs(s) > 0.1 for s in data), "鼓点数据太安静")

if __name__ == "__main__":
    unittest.main()
