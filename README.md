# ACM Composer

[![CI](https://github.com/mouse114514/acm-cli-composer/actions/workflows/ci.yml/badge.svg)](https://github.com/mouse114514/acm-cli-composer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![GitHub release](https://img.shields.io/github/v/release/mouse114514/acm-cli-composer)](https://github.com/mouse114514/acm-cli-composer/releases)

A CLI-based non-interactive music composition tool. Compose music from ACML notation files, with MIDI export and FluidSynth high-quality WAV rendering.

```bash
python cli.py compile samples/acm.acml --prowav --loop 1
```

## Installation

```bash
pip install -e .

# Optional: numpy acceleration
pip install -e ".[accelerate]"

# Optional: GPU acceleration (requires CUDA 12.x)
pip install -e ".[cuda]"
```

Python >= 3.10, no hard dependencies (numpy/cupy optional).

## Quick Start

```bash
# Compile ACML and render high-quality WAV in one step
python cli.py compile samples/acm.acml --prowav --loop 1

# Export WAV + MIDI
python cli.py compile samples/acm.acml --midi output/song.mid

# View all subcommands
python cli.py --help
```

Or via the installed entry point:
```bash
pip install -e .
acm compile samples/acm.acml --prowav
```

## FluidSynth Setup (optional, for prowav / midi2wav)

```bash
# Windows
choco install fluidsynth

# macOS
brew install fluid-synth

# Linux
sudo apt install fluidsynth
```

Place a SoundFont (e.g. FluidR3_GM.sf2) at `~/.acm/` or specify with `--soundfont`.

## Documentation

| Document | Description |
|----------|-------------|
| `docs/acml-format.md` | ACML notation language reference |
| `docs/cli-reference.md` | CLI command reference |

## Features

| Feature | Description |
|---------|-------------|
| ACML Compile | Declarative notation -> one-step WAV generation |
| MIDI Export | GM standard with drum mapping, program change, serial/parallel modes |
| `--prowav` | Compile + MIDI + FluidSynth WAV in one command |
| `midi2wav` | Standalone MIDI to WAV rendering |
| Instruments | piano, guitar, bass, sawtooth, organ, bell, strings, brass, pad, lead, fm, wavetable, sample, trumpet, tuba, drums |
| Drums | K(kick), S(snare), H(hi-hat closed), O(hi-hat open), T(tom) |
| Chords | 17 types + auto-harmony + chord recommendation |
| FM Synthesis | Adjustable ratio/index |
| Wavetable | saw / square / triangle / sine / custom |
| Sample Playback | WAV loading with pitch shifting |
| Modes | parallel / serial + global loop |
| Effects | reverb / delay / chorus |
| Compact Notation | `D5qf` -> `D5:q:f`, token-efficient |
| GPU Acceleration | Optional cupy support |

## Project Structure

```
├── cli.py              CLI entry point
├── composer.py         Core synthesis engine
├── acml.py             ACML parser
├── track.py            Track data class
├── pyproject.toml
├── README.md
├── LICENSE
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
├── docs/
│   ├── acml-format.md
│   └── cli-reference.md
├── samples/
│   └── acm.acml        Example composition
├── tests/              91 tests
└── .github/
    ├── workflows/ci.yml
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

## Tests

```bash
python -m pytest tests/ -v
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE)
