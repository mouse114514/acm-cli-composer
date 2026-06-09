class Track:
    def __init__(self, instrument, pattern=None, scale=None, octave=4, notes=None, volume=1.0, kick=None, snare=None, hihat=None, durations=None, pan=0.0, arpeggio=None, loops=1, wavetable=None, sample=None, sample_pitch=None, harmony=None, fm_ratio=None, fm_index=None, mode="parallel"):
        self.instrument = instrument
        self.pattern = pattern
        self.scale = scale
        self.octave = octave
        self.notes = notes
        self.volume = volume
        self.kick = kick
        self.snare = snare
        self.hihat = hihat
        self.durations = durations
        self.pan = pan
        self.arpeggio = arpeggio
        self.loops = loops
        self.wavetable = wavetable
        self.sample = sample
        self.sample_pitch = sample_pitch
        self.harmony = harmony
        self.fm_ratio = float(fm_ratio) if fm_ratio is not None else None
        self.fm_index = float(fm_index) if fm_index is not None else None
        self.mode = mode if mode in ("parallel", "serial") else "parallel"
