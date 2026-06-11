# ACM CLI Reference

ACM (Arrangement Composer) command-line interface. Supports compiling music from ACML files, managing projects, exporting MIDI, and rendering high-quality WAV via FluidSynth.

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Global Options](#2-global-options)
3. [compile — Compile from ACML](#3-compile--compile-from-acml)
4. [init — Initialize Project](#4-init--initialize-project)
5. [track — Track Management](#5-track--track-management)
6. [generate — Generate Audio from Project](#6-generate--generate-audio-from-project)
7. [analyze — Chord Analysis](#7-analyze--chord-analysis)
8. [midi2wav — MIDI to WAV](#8-midi2wav--midi-to-wav)
9. [Environment Variables](#9-environment-variables)

---

## 1. Quick Start

```bash
# One-step: compile ACML and render high-quality WAV
python cli.py compile samples/acm.acml --prowav --loop 1

# Three output files:
#   output/mouse.wav          — Normal WAV synthesized by the built-in engine
#   output/mouse.mid          — MIDI file
#   output/mouse_prowav.wav   — High-quality WAV rendered by FluidSynth
```

Common command quick reference:

| Purpose | Command |
|---------|---------|
| Compile ACML → WAV + MIDI | `python cli.py compile song.acml --midi song.mid` |
| Compile + FluidSynth output | `python cli.py compile song.acml --prowav` |
| View all subcommands | `python cli.py --help` |
| View subcommand details | `python cli.py compile --help` |
| Output JSON for scripts | `python cli.py status --json` |

---

## 2. Global Options

Available before all subcommands:

| Option | Description |
|--------|-------------|
| `--version` | Print version number |
| `--project-dir <directory>` | Project file directory (default `projects/`, env var `ACM_PROJECT_DIR`) |
| `--output-dir <directory>` | Output file directory (default `output/`, env var `ACM_OUTPUT_DIR`) |

---

## 3. compile — Compile from ACML

The most commonly used subcommand. Reads an `.acml` file, parses tracks, synthesizes audio, optionally exports MIDI and FluidSynth rendering.

```bash
python cli.py compile <file.acml> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `file` | `.acml` file path (required) |
| `--output <filename>` | Output WAV filename (default `{project_name}.wav`) |
| `--bpm <value>` | Override BPM in ACML |
| `--duration <seconds>` | Audio duration (default 4 seconds) |
| `--midi <filename>` | Also export standard MIDI file |
| `--reverb <0.0-1.0>` | Reverb intensity |
| `--delay <0.0-1.0>` | Delay intensity |
| `--chorus <0.0-1.0>` | Chorus intensity |
| `--loop <count>` | Whole song loop count (serial track repeat count, overrides `loop` in ACML) |
| `--prowav` | Auto-render high-quality WAV with FluidSynth after compilation |
| `--soundfont <path>` | SoundFont `.sf2` file for prowav |
| `--gain <ratio>` | Prowav gain multiplier (default 1.0) |
| `--json` | Output result in JSON format |

### Examples

```bash
# Basic compilation
python cli.py compose samples/pop_demo.acml --duration 8

# Override BPM + export MIDI
python cli.py compose song.acml --bpm 140 --midi song.mid

# Custom output filename
python cli.py compose song.acml --output final.wav

# One-click high-quality rendering (requires FluidSynth and SoundFont installed)
python cli.py compose samples/acm.acml --prowav --loop 2

# Specify SoundFont and gain
python cli.py compose samples/acm.acml --prowav --soundfont "C:\sf2\FluidR3_GM.sf2" --gain 1.5

# JSON output (suitable for script calls)
python cli.py compose song.acml --json
```

### Prowav Notes

`--prowav` is a three-in-one shortcut:

1. Compile ACML → WAV (built-in engine synthesis)
2. Also export MIDI
3. Call `fluidsynth` to convert MIDI → high-quality WAV (`*_prowav.wav`)

When `--midi` is not specified, the MIDI path is automatically derived from the output filename.
SoundFont lookup order: `--soundfont` argument → `~/.acm/FluidR3_GM.sf2` → default system path.

---

## 4. init — Initialize Project

Creates a new blank project JSON file.

```bash
python cli.py init <project_name> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `project_name` | Project name (required) |
| `--force` | Overwrite existing project |
| `--json` | Output in JSON format |

### Examples

```bash
python cli.py init mysong
python cli.py init mysong --force
python cli.py init mysong --json   # → {"name": "mysong", "status": "initialized"}
```

After initialization, `projects/mysong.json` is generated. Use `track add` to add tracks, or use `generate` to produce audio.

---

## 5. track — Track Management

CRUD operations on tracks in an initialized project.

```bash
python cli.py track <subcommand> <project_name> [options]
```

### 5.1 track add — Add Track

```bash
python cli.py track add <project_name> --instrument <instrument> [options]
```

| Option | Description |
|--------|-------------|
| `--instrument <instrument>` | Timbre (required): piano, guitar, bass, sawtooth, organ, bell, strings, brass, pad, lead, fm, wavetable, sample, trumpet, tuba, drums |
| `--scale <root>` | Scale root, e.g. C, D, G (default C) |
| `--pattern <pattern>` | Rhythm pattern: pop, rock, jazz, latin, funk, shuffle, trap |
| `--octave <value>` | Default octave (default 4) |
| `--notes <notes>` | Note sequence, comma-separated. Supports compact notation (`C5qf`) and extended notation (`C5:q:mf`) |
| `--volume <0.0-1.0>` | Volume (default 1.0) |
| `--pan <-1.0-1.0>` | Pan position (default 0.0) |
| `--durations <list>` | Unequal durations, e.g. `2,1,1,2` |
| `--loops <count>` | Track loop count (default 1) |
| `--mode <mode>` | Playback mode: parallel or serial |
| `--kick <string>` | Kick drum rhythm 0/1 string |
| `--snare <string>` | Snare drum rhythm 0/1 string |
| `--hihat <string>` | Hi-hat rhythm 0/1 string |
| `--arpeggio <pattern>` | Arpeggio: up, down, random, updown, downup |
| `--wavetable <shape>` | Wavetable: saw, square, triangle, sine or custom value |
| `--sample <path>` | Sample WAV file path |
| `--sample-pitch <note>` | Sample original pitch (default C4) |
| `--harmony <interval>` | Auto harmony: 3, 5, 6, octave, 3below, etc. |
| `--fm-ratio <value>` | FM modulation ratio (default 2.0) |
| `--fm-index <value>` | FM modulation index (default 3.0) |
| `--json` | Output in JSON format |

### 5.2 track list — List Tracks

```bash
python cli.py track list <project_name> [--json]
```

### 5.3 track remove — Remove Track

```bash
python cli.py track remove <project_name> <index>
```

### 5.4 track update — Update Track

```bash
python cli.py track update <project_name> <index> [options]
```

Options are the same as `track add`.

### Examples

```bash
# Add piano track
python cli.py track add mysong --instrument piano --notes "C4:q:mf,E4:q:mf,G4:q:mf"

# Add drum track
python cli.py track add mysong --instrument drums --notes "K:q:mf,S:q:mf,H:e:mf"

# View all tracks
python cli.py track list mysong

# Remove track 2
python cli.py track remove mysong 2

# Update track 1 instrument
python cli.py track update mysong 1 --instrument guitar
```

---

## 6. generate — Generate Audio from Project

Generate audio from an existing project JSON file.

```bash
python cli.py generate <project_name> --output <filename> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `project_name` | Project name (required) |
| `--output <filename>` | Output WAV filename (required) |
| `--bpm <value>` | Override project BPM |
| `--duration <seconds>` | Audio duration (default 4 seconds) |
| `--midi <filename>` | Also export MIDI |
| `--reverb <0.0-1.0>` | Reverb intensity |
| `--delay <0.0-1.0>` | Delay intensity |
| `--chorus <0.0-1.0>` | Chorus intensity |
| `--loop <count>` | Whole song loop count |
| `--json` | Output in JSON format |

### Examples

```bash
python cli.py generate mysong --output mysong.wav --bpm 120 --duration 60
python cli.py generate mysong --output mysong.wav --midi mysong.mid
```

---

## 7. analyze — Chord Analysis

Analyze the melody of a specified track and recommend chord progressions per bar.

```bash
python cli.py analyze <project_name> [options]
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `project_name` | — | Project name (required) |
| `--track <index>` | `1` | Track index to analyze (1-based) |
| `--beats-per-bar <beats>` | `4` | Beats per bar |
| `--json` | — | Output in JSON format |

### Examples

```bash
python cli.py analyze mysong
# → Track 1 (piano): Cmaj | Fmaj | G7 | Cmaj

python cli.py analyze mysong --track 2 --beats-per-bar 3
python cli.py analyze mysong --json
```

---

## 8. midi2wav — MIDI to WAV

Use external FluidSynth to render a MIDI file to WAV audio.

**Prerequisites**:
- Install [FluidSynth](https://www.fluidsynth.org)
- Obtain a SoundFont `.sf2` file (e.g. [FluidR3_GM.sf2](https://github.com/pianobooster/fluid-soundfont/releases))

```bash
python cli.py midi2wav <input.mid> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input` | Input `.mid` file path (required) |
| `--output, -o <filename>` | Output WAV file path (default replaces extension with `.wav`) |
| `--soundfont, -s <path>` | SoundFont `.sf2` file path |
| `--gain, -g <ratio>` | Gain multiplier (default 1.0) |
| `--sample-rate, -r <Hz>` | Sample rate (default 44100) |

### Examples

```bash
# Basic usage (auto-find SoundFont)
python cli.py midi2wav output/song.mid

# Specify SoundFont and gain
python cli.py midi2wav output/song.mid -s "C:\sf2\FluidR3_GM.sf2" -g 1.5

# Specify output path
python cli.py midi2wav output/song.mid -o output/final.wav
```

SoundFont lookup order:
1. Path specified by `--soundfont` argument
2. `~/.acm/default.sf2`
3. `~/.acm/FluidR3_GM.sf2`
4. Default system path

---

## 9. Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ACM_PROJECT_DIR` | Directory for project JSON files | `projects/` |
| `ACM_OUTPUT_DIR` | Directory for audio output files | `output/` |

Can be overridden via the CLI global options `--project-dir` and `--output-dir`.
