# ACML v1 — ACM Composition Language Reference Manual

ACML (ACM Composition Markup Language) is the declarative markup language of the ACM composition tool.
It describes a complete piece of music in a single `.acml` file, and generates project files and finished WAV with a single `compile` command.

---

## Table of Contents

1. [File Structure](#1-file-structure)
2. [Global Settings](#2-global-settings)
3. [Track Definition](#3-track-definition)
4. [Note Notation](#4-note-notation)
5. [Instrument List](#5-instrument-list)
6. [Drum Patterns](#6-drum-patterns)
7. [Pan](#7-pan)
8. [Arpeggiator](#8-arpeggiator)
9. [Chord Notation](#9-chord-notation)
10. [Line Continuation](#10-line-continuation)
11. [ACML Repeat Blocks](#11-acml-repeat-blocks)
12. [Output File Information](#12-output-file-information)
13. [Complete Examples](#13-complete-examples)
14. [Compile Command](#14-compile-command)
15. [CLI Subcommand Reference](#15-cli-subcommand-reference)
16. [FM Synthesis (Frequency Modulation)](#16-fm-synthesisfrequency-modulation)
17. [Wavetable Synthesis](#17-wavetable-synthesis)
18. [Sample Playback](#18-sample-playbacksample-playback)
19. [Auto Harmony](#19-auto-harmony)
20. [Chord Recommendation](#20-chord-recommendationchord-recommendation)

---

## 1. File Structure

```
# Comments start with #
Global parameters

[track track_name]
Track properties

[track another_track]
Track properties
```

- Lines starting with `#` are comments and are ignored
- Global parameters are written before all track sections
- `[track xxx]` starts a track section; `[xxx]` is also acceptable (the `track` prefix is automatically removed)
- Properties use `=` or `:` as separators, spaces are optional

---

## 2. Global Settings

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | string | `"untitled"` | Project name, also used as the JSON filename |
| `bpm` | integer | `120` | Beats per minute |
| `loop` | integer | `1` | Whole song loop count (serial tracks repeat, parallel tracks play only once) |

```
name = "My Song"
bpm = 118
```

Colon separator is also allowed:

```
name: "My Song"
bpm: 118
```

BPM can be overridden via the `--bpm` command-line argument.

`loop` can be overridden via the `--loop` command-line argument. When the value is 1, it plays only once; when N > 1, serial tracks repeat N times sequentially, total duration = max(parallel duration, serial total duration × N). Parallel tracks are rendered only once and are not doubled by looping. See [Whole Song Loop](#whole-song-loop) for details.

---

## 3. Track Definition

```
[track track_name]
property = value
```

The name in `[track track_name]` is for identification only and does not affect output.

### Common Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `instrument` | string | `piano` | Timbre, see instrument list |
| `scale` | string | `C` | Scale root (C, D, G, A, etc.) |
| `pattern` | string | `pop` | Rhythm pattern (pop, rock, jazz, latin, funk, shuffle, trap) |
| `octave` | integer | `4` | Default octave |
| `notes` | string | — | Note sequence, comma-separated |
| `volume` | float | `1.0` | Volume 0.0–1.0 |
| `pan` | float | `0.0` | Pan position -1.0(left) ~ 1.0(right) |
| `durations` | string | — | Unequal durations, comma-separated, e.g. `2,1,1,2` (three fast two slow) |
| `loops` | integer | `1` | Loop count, repeats track content N times |
| `arpeggio` | string | — | Arpeggio pattern (up, down, random, updown, downup) |
| `wavetable` | string | `saw` | Wavetable type (saw, square, triangle, sine or comma-separated custom values) |
| `sample` | string | — | Sample WAV file path |
| `sample_pitch` | string | `C4` | Original pitch of the recorded sample |
| `harmony` | string | — | Auto harmony interval (3, 5, 6, octave, 3below, etc.) |
| `fm_ratio` | float | `2.0` | FM synthesis modulation ratio (carrier frequency multiplier) |
| `fm_index` | float | `3.0` | FM synthesis modulation index (modulation depth) |
| `mode` | string | `parallel` | Playback mode: `parallel`=simultaneous, `serial`=sequential |

### Playback Mode

`mode` controls how tracks play on the timeline:

| Value | Description |
|-------|-------------|
| `parallel` | **Simultaneous playback** (default). All parallel tracks start at 0 seconds and mix together, suitable for chords, rhythm, and multi-track scenarios |
| `serial` | **Sequential playback**. Serial tracks play one after another in definition order; the next starts after the previous finishes. Total duration = max(parallel duration, sum of all serial track durations). Supports mixing with parallel tracks |

```acml
# serial example: two melodies playing in sequence
[track intro]
instrument = piano
mode = serial
notes = C4:q:mf,E4:q:mf,G4:q:mf

[track verse]
instrument = piano
mode = serial
notes = F4:q:mf,A4:q:mf,C5:q:mf
```

```acml
# Mixed mode: pad plays throughout, melody plays in sequence
[track pad]
instrument = pad
mode = parallel
notes = C3:w:mp

[track melody_a]
instrument = lead
mode = serial
notes = C5:e:mf,E5:e:mf,G5:e:mf

[track melody_b]
instrument = lead
mode = serial
notes = D5:e:mf,F5:e:mf,A5:e:mf
# pad plays throughout, melody_b starts after melody_a finishes
```

### Whole Song Loop

The global `loop` controls how many times the whole song repeats on the timeline.

| Value | Description |
|-------|-------------|
| `1` | Play only once (default) |
| `N` | Serial tracks repeat N times sequentially; parallel tracks are rendered only once (not doubled by looping) |

Total duration = max(all parallel track durations, sum of all serial track durations × N).

```acml
name = "Loops"
bpm = 120
loop = 3

[track pad]
instrument = pad
mode = parallel
notes = C3:w:mp
# pad only plays for 4 seconds, loop does not affect it

[track melody]
instrument = lead
mode = serial
notes = C4:e:mf, E4:e:mf, G4:e:mf
# 3 loops: melody plays 3 times, total duration ≈ (0.5s × 6 notes) × 3 = 9s
# Total file duration = max(4s, 9s) = 9s
```

Can also be overridden via CLI: `--loop 5`.

---

### Drum-Specific Properties

When `instrument = drums`, the following properties can be used to specify drum patterns.
If not specified, the default is: kick on beat 1 of every 4 beats, snare on beat 3 of every 4 beats, hihat on every beat.

| Property | Type | Description |
|----------|------|-------------|
| `kick` | string | Kick drum pattern, e.g. `10001000` (1=hit 0=rest) |
| `snare` | string | Snare drum pattern, e.g. `00100010` |
| `hihat` | string | Hi-hat pattern, e.g. `11111111` |

Using extended drum notes (see next section) is also recommended for greater flexibility.

---

## 4. Note Notation

The system supports three notation styles, which can be mixed as needed (separated by commas):

### 4.1 Standard Notation (pattern + scale mode)

Write only note names (C, D, E...), played using the scale mode driven by `scale` and `pattern`:

```
notes = C,D,E,F,G,A,B,C
```

With `scale=C`, `octave=4`, the example above plays C4, D4, E4, F4, G4, A4, B4, C5.
Use `R` or `_` for rest; rests do not consume the note index.

### 4.2 Extended Notation

Each note independently specifies duration and velocity: `pitch:duration:velocity`.

```
notes = C4:q:mf,E4:q:mf,G4:q:mf,C5:h:f
```

**Duration letters**:

| Letter | Meaning | Beats |
|--------|---------|-------|
| `w` | whole note | 4 beats |
| `h` | half note | 2 beats |
| `q` | quarter note | 1 beat |
| `e` | eighth note | 0.5 beats |
| `s` | sixteenth note | 0.25 beats |

Adding `.` indicates a dotted note, duration × 1.5, e.g. `h.` = 3 beats.

**Velocity markings**:

| Mark | Value | Description |
|------|-------|-------------|
| `ppp` | 0.20 | Pianississimo |
| `pp` | 0.25 | Pianissimo |
| `p` | 0.35 | Piano |
| `mp` | 0.50 | Mezzo-piano |
| `mf` | 0.65 | Mezzo-forte |
| `f` | 0.80 | Forte |
| `ff` | 0.90 | Fortissimo |
| `fff` | 1.00 | Fortississimo |

Velocity also supports direct numeric values: `C4:q:0.75`.

**Rest**: `R:duration:velocity` or `_:duration`, e.g. `R:h` (half rest), `R:q:mf`.

**Sharps/Flats**: `C#`, `Db`, `F#`, `Bb`, etc.

**Transposition**: A number after a note specifies the octave, e.g. `C#5` = C-sharp 5th octave.

**Extended notation detection rule**: The system detects whether a note contains a `:duration_letter` pattern to decide whether to use extended mode.
Once extended notation is detected, the track ignores the `pattern` and `durations` parameters
and plays the note list sequentially from beginning to end.

### 4.3 Compact Notation (shorthand)

In `.acml` files or the CLI `--notes` parameter, compact notation can be used for automatic expansion:

| Notation | Expansion Result | Description |
|----------|------------------|-------------|
| `C5qf` | `C5:q:f` | Pitch+octave+duration+velocity |
| `D5q(mf)` | `D5:q:mf` | Velocity in parentheses |
| `.` | `R:q` | Dot = quarter rest |
| `Kf` | `K:q:f` | Drum name + velocity |
| `Hq(mf)` | `H:q:mf` | Drum name + duration + parenthesized velocity |
| `C5q` | `C5:q:mf` | Omitted velocity defaults to mf |
| `Rh` | `R:h:mf` | Rest + duration |

Expansion happens automatically at input time; the stored JSON already uses the extended format.

---

## 5. Instrument List

| Instrument | Timbre Description |
|------------|--------------------|
| `piano` | Pure sine wave, soft and clean |
| `guitar` | Sine wave + 3rd harmonic, warm and bright |
| `bass` | Sawtooth wave, thick and deep |
| `sawtooth` | Sawtooth wave, electronic feel |
| `organ` | 4-layer harmonic mix, organ-like texture |
| `bell` | Fast-decay multi-harmonic, bell-like timbre |
| `strings` | Multi-layer harmonic mix (1st-4th), string ensemble feel |
| `brass` | Square wave + 3rd harmonic with saturation, brass-like feel |
| `pad` | Dual detuned sine waves, pad timbre |
| `lead` | Enhanced sawtooth + 3rd harmonic, bright electronic lead |
| `fm` | 2-operator FM synthesis (adjustable ratio/index), metallic/electronic texture |
| `wavetable` | Wavetable synthesis (saw/square/triangle/sine or custom), retro digital feel |
| `sample` | Sample playback (loads WAV, supports pitch shifting), realistic instruments/vocals |
| `drums` | Drum kit, includes K(kick), S(snare), H(closed hi-hat), O(open hi-hat), T(tom) |
| `trumpet` | Multi-harmonic mix (rich odd and even harmonics), bright brass |
| `tuba` | Strong fundamental with weak harmonics, deep low brass |

Drum instruments support two modes:
1. **Extended note mode**: flexible ordering via `notes = K:q:mf,S:q:mf,H:q:mf` etc.
2. **Traditional mode**: use `kick`/`snare`/`hihat` properties with 0/1 string patterns

The two modes cannot be mixed within the same track.

---

## 7. Pan

Each track can independently set its pan position, using constant-power pan law,
ensuring the center channel is not +3dB louder than hard left/right.

```
pan = 0.0    # Center (default)
pan = -1.0   # Hard left
pan = 1.0    # Hard right
pan = -0.3   # Slightly left
pan = 0.5    # Slightly right
```

Constant-power formula: `angle = (pan + 1) × π / 4`, left channel = cos(angle), right channel = sin(angle).

Output is stereo 16-bit WAV (44100Hz).

---

## 6. Drum Patterns

### 6.1 Extended Drum Notes (recommended)

Drum notes use K/S/H/O/T as "note names":

| Drum Type | Code | Description |
|-----------|------|-------------|
| Kick | `K` | Bass drum, 55Hz sine wave |
| Snare | `S` | Snare drum, noise + 180Hz sine |
| Hi-hat (closed) | `H` | Closed hi-hat, short noise |
| Hi-hat (open) | `O` | Open hi-hat, long noise |
| Tom | `T` | Tom drum, 80Hz sine wave |

Each drum hit can independently set velocity and duration:

```
notes = K:q:f,S:q:mf,K:q:f,S:q:mf    # Kick and snare alternating
notes = H:e:mf,H:e:mf,H:e:mf,H:e:mf  # Eighth-note hi-hat
notes = T:q:f                         # Tom drum
```

### 6.2 Traditional Drum Mode

Set rhythm strings via `kick`, `snare`, and `hihat` properties:

```
kick  = 1000100010001000
snare = 0010001000100010
hihat = 1111111111111111
```

1 = hit, 0 = rest. If the string is shorter than needed, it repeats.

---

## 13. Complete Examples

### Example 1 — Minimal

```acml
name = "hello"
bpm = 120

[track piano]
instrument = piano
notes = C4:q:mf,E4:q:mf,G4:q:mf,C5:h:mf
```

### Example 2 — Funk Machine (D Dorian, 118BPM)

```acml
# ACML v1 — Funk Machine
name = "funk_machine"
bpm = 118

[track guitar]
instrument = guitar
pan = -0.3
notes = D5qf,G5qf,A5qf,.,D5qf,G5qf,A5qf,.,D5qf,G5qf,A5qf,C5qf

[track drums]
instrument = drums
notes = H:q:mf,H:q:mf,H:q:mf,H:q:mf,K:q:mf,.,S:q:mf,.,K:q:mf,.,S:q:mf,.

[track bass]
instrument = bass
pan = 0.3
notes = D2:h:mf,D3:h:mf,D2:h:mf,D3:h:mf,G2:h:mf,G3:h:mf,G2:h:mf,G3:h:mf
```

### Example 3 — Pop Demo

```acml
name = "pop_demo"
bpm = 120

[track guitar]
instrument = guitar
notes = C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf,C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf

[track hihat]
instrument = drums
notes = H:q:mf,H:q:mf,H:q:mf,H:q:mf,H:q:mf,H:q:mf,H:q:mf,H:q:mf

[track kicksnare]
instrument = drums
notes = K:q:mf,.,S:q:mf,.,K:q:mf,.,S:q:mf,.

[track bass]
instrument = bass
notes = C2:h:mf,C3:h:mf,C2:h:mf,C3:h:mf
```

---

## 14. Compile Command

```
python cli.py compile <file.acml> [options]
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `file` | `.acml` file path (required) |
| `--duration <seconds>` | Audio duration, default 4 seconds |
| `--bpm <value>` | Override BPM in ACML |
| `--output <filename>` | Custom output filename, default `{project_name}.wav` |
| `--midi <filename>` | Also export a standard MIDI file |
| `--reverb <0.0-1.0>` | Reverb intensity |
| `--delay <0.0-1.0>` | Delay intensity |
| `--chorus <0.0-1.0>` | Chorus intensity |
| `--loop <count>` | Whole song loop count (serial track repeat count, overrides ACML `loop`) |
| `--prowav` | Automatically render high-quality WAV with FluidSynth after compilation (all-in-one) |
| `--soundfont <path>` | SoundFont `.sf2` file for prowav |
| `--gain <multiplier>` | Prowav gain multiplier (default 1.0) |
| `--json` | Output result information in JSON format |

### Usage Examples

```bash
# Basic compilation
python cli.py compile samples/funk_machine.acml --duration 8

# Override BPM
python cli.py compile my_song.acml --bpm 140 --duration 30

# Custom output
python cli.py compile song.acml --output final.wav

# Also export MIDI
python cli.py compile song.acml --output song.wav --midi song.mid

# Whole song loop (serial tracks repeat 3 times)
python cli.py compile song.acml --loop 3

# Add effects
python cli.py compile song.acml --reverb 0.3 --delay 0.2

# One-click high-quality rendering (requires FluidSynth and SoundFont)
python cli.py compile samples/acm.acml --prowav --loop 1

# Specify SoundFont and gain
python cli.py compile samples/acm.acml --prowav --soundfont "C:\sf2\FluidR3_GM.sf2" --gain 1.5

# JSON output (suitable for scripting)
python cli.py compile song.acml --json
```

### Compilation Flow

1. Parse `.acml` file → extract global parameters and track definitions
2. Compact notation expansion → convert `D5qf` shorthand to `D5:q:f`
3. Write `projects/{name}.json` — intermediate project file
4. Synthesize audio → write `output/{name}.wav` — engine-synthesized
5. (Optional `--midi`) Export MIDI → `output/{name}.mid`
6. (Optional `--prowav`) Call FluidSynth to render high-quality WAV → `output/{name}_prowav.wav`

### Output Files

```
projects/
  └── {name}.json           # Intermediate project file (usable with track list / generate)
output/
  ├── {name}.wav            # Engine-synthesized stereo audio (44.1kHz, 16-bit)
  ├── {name}.mid            # (Optional) MIDI file
  └── {name}_prowav.wav     # (Optional, --prowav) FluidSynth-rendered high-quality WAV
```

After compilation, existing commands can still operate on the project:

```bash
python cli.py track list {name}
python cli.py generate {name} --output new.wav --bpm 200
```

---

## 15. CLI Subcommand Reference

### `init` — Initialize Project

```
python cli.py init <name> [--force] [--json]
```

### `track add` — Add Track

```
python cli.py track add <project> --instrument <instrument> [options]
```

Common options: `--scale`, `--pattern`, `--octave`, `--notes`, `--volume`,
`--kick`, `--snare`, `--hihat`, `--pan`, `--durations`, `--loops`,
`--arpeggio`, `--wavetable`, `--sample`, `--sample-pitch`, `--harmony`,
`--fm-ratio`, `--fm-index`, `--mode`, `--json`

### `track list` — List Tracks

```
python cli.py track list <project> [--json]
```

### `track remove` — Delete Track

```
python cli.py track remove <project> <index>
```

### `track update` — Modify Track

```
python cli.py track update <project> <index> [options]
```

### `generate` — Generate Audio

```
python cli.py generate <project> --output <filename> [--bpm] [--duration] [--midi] [--reverb] [--delay] [--chorus] [--loop] [--json]
```

### `compile` — Compile from ACML

```
python cli.py compile <file.acml> [--bpm] [--duration] [--output] [--midi] [--reverb] [--delay] [--chorus] [--loop] [--prowav] [--soundfont] [--gain] [--json]
```

### `analyze` — Chord Analysis

```
python cli.py analyze <project> [--track N] [--beats-per-bar N] [--json]
```

Analyzes the melody of a specified track and recommends chord progressions by bar.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `project` | — | Project name (required) |
| `--track` | `1` | Track index to analyze (1-based) |
| `--beats-per-bar` | `4` | Beats per bar (4 = 4/4 time) |
| `--json` | — | JSON format output |

### `midi2wav` — MIDI to WAV

```
python cli.py midi2wav <input.mid> [--output] [--soundfont] [--gain] [--sample-rate]
```

Uses external FluidSynth to render MIDI into high-quality WAV.

| Parameter | Description |
|-----------|-------------|
| `input.mid` | MIDI file path (required) |
| `--output, -o <file>` | Output WAV path (default: replace extension with `.wav`) |
| `--soundfont, -s <path>` | SoundFont `.sf2` file path |
| `--gain, -g <multiplier>` | Gain multiplier (default 1.0) |
| `--sample-rate, -r <Hz>` | Sample rate (default 44100) |

Prerequisites: Install [FluidSynth](https://www.fluidsynth.org) and obtain a SoundFont file (e.g., FluidR3_GM.sf2).

### Global Options

| Option | Description |
|--------|-------------|
| `--version` | Print version number |
| `--project-dir <directory>` | Project file directory (default: `projects/`, env var: `ACM_PROJECT_DIR`) |
| `--output-dir <directory>` | Output file directory (default: `output/`, env var: `ACM_OUTPUT_DIR`) |

---

---

## 8. Arpeggiator

Arpeggio patterns replace simple single-note melody generation. The track's `pattern` controls rhythmic triggering,
and each trigger beat plays a different note from the scale in sequence.

### Supported Modes

| Mode | Description |
|------|-------------|
| `up` | Scale ascending cycle 1-2-3-4-5-6-7-1-2-... |
| `down` | Scale descending cycle 7-6-5-4-3-2-1-7-6-... |
| `updown` | Up-down alternating 1-2-3-4-5-6-7-6-5-4-3-2-1-2-... |
| `downup` | Down-up alternating 7-6-5-4-3-2-1-2-3-4-5-6-7-6-... |
| `random` | Random selection (fixed seed ensures determinism) |

### Usage

**ACML track property**:

```acml
[track arp]
instrument = piano
scale = C
octave = 4
pattern = 1111
arpeggio = up
```

**CLI**:

```bash
python cli.py track add myproj --instrument piano --scale C --octave 4 --pattern 1111 --arpeggio up
```

**Compile example**:

```acml
name = "arpeggio_demo"
bpm = 120

[track guitar]
instrument = guitar
scale = C
octave = 4
pattern = 11111111
arpeggio = updown
```

### How It Works

- Arpeggios generate major scale notes from the root specified by `scale` (C major = C, D, E, F, G, A, B)
- `octave` controls the starting octave
- Each active beat (1) in `pattern` advances the arpeggio index; inactive beats (0) are skipped
- Arpeggio mode only works with standard pattern mode, not with extended notes

---

## 9. Chord Notation

ACML supports automatic expansion of chord names into constituent notes, with each chord tone arranged at equal duration to create a fast arpeggio.

### Supported Chord Types

| Notation | Type | Intervals (semitones) |
|----------|------|----------------------|
| `Cmaj` | Major triad | Root + major 3rd + perfect 5th |
| `Cm` | Minor triad | Root + minor 3rd + perfect 5th |
| `Cdim` | Diminished triad | Root + minor 3rd + diminished 5th |
| `Caug` | Augmented triad | Root + major 3rd + augmented 5th |
| `C7` | Dominant 7th | Major triad + minor 7th |
| `Cmaj7` | Major 7th | Major triad + major 7th |
| `Cm7` | Minor 7th | Minor triad + minor 7th |
| `Cdim7` | Diminished 7th | Diminished triad + diminished 7th |
| `Cm7b5` | Half-diminished 7th | Diminished triad + minor 7th |
| `Caug7` | Augmented 7th | Augmented triad + minor 7th |
| `C6` | Sixth chord | Major triad + major 6th |
| `Cm6` | Minor sixth | Minor triad + major 6th |
| `C9` | Dominant 9th | Dominant 7th + major 9th |
| `Cmaj9` | Major 9th | Major 7th + major 9th |
| `Cm9` | Minor 9th | Minor 7th + major 9th |
| `Csus2` | Suspend 2 | Root + major 2nd + perfect 5th |
| `Csus4` | Suspend 4 | Root + perfect 4th + perfect 5th |
| `Cadd9` | Add 9 | Major triad + major 9th |

### Usage

**Extended format (recommended)**:

```
notes = Cmaj7:q:mf,Fmaj7:q:mf,G7:q:mf,Cmaj7:q:mf
```

Chord `Cmaj7` expands to C4, E4, G4, B4, each note gets a duration of `q ÷ 4 = s` (sixteenth note),
creating a fast arpeggio effect. The total chord duration maintains the originally specified value (q = 1 beat).

**Specifying octave**:

```
notes = C5maj7:q:mf    # C5, E5, G5, B5
notes = F4m:q:mf       # F4, Ab4, C5
```

**Compact format**:

```
notes = Cmaj7qf        # = Cmaj7:q:f → C4:s:f,E4:s:f,G4:s:f,B4:s:f
notes = G7h(mf)        # = G7:h:mf  → G4:e:mf,B4:e:mf,D5:e:mf,F5:e:mf
```

**Mixed with regular notes**:

```
notes = Cmaj7:q:mf,D4:q:mf,E4:q:mf
```

Only notes containing chord suffixes (`maj7`, `m`, `7`, etc.) are expanded;
ordinary single note names (`C:q:mf`, `D4:q:mf`) remain unchanged to avoid ambiguity.

**Complete chord progression example**:

```acml
name = "chord_progression"
bpm = 100

[track piano]
instrument = piano
notes = Cmaj7:q:mf,Fmaj7:q:mf,G7:q:mf,Cmaj7:q:mf
```

---

## 10. Line Continuation

Long `notes` lines can be continued to the next line using `+`, improving readability.

Continuation rules:
- A `+` at the end of a line indicates the next line is a continuation
- Leading whitespace on the continuation line is automatically removed
- The continuation content is directly concatenated to the end of the previous line (no space added)

```
# Continuation example
notes = C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf, +
       C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf, +
       D4:q:mf,F4:q:mf,A4:q:mf,D5:q:mf

# Equivalent to one line:
# C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf,C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf,D4:q:mf,F4:q:mf,A4:q:mf,D5:q:mf
```

Spaces after `+` and leading spaces on continuation lines are both ignored, ensuring correct concatenation.

---

## 11. ACML Repeat Blocks

`[repeat N]` and `[/repeat]` tags can repeat track definitions, reducing repetitive writing.

### Usage

```acml
name = "repeated_song"
bpm = 120

[repeat 4]
[track piano]
instrument = piano
notes = C4:q:mf
[/repeat]
```

The above is equivalent to manually writing 4 `[track piano]` sections.

### Nesting

```acml
name = "nested_repeat"
bpm = 120

[repeat 2]
[track guitar]
instrument = guitar
[repeat 3]
notes = C4:q:mf
[/repeat]
[/repeat]
```

Outer `[repeat 2]` × inner `[repeat 3]` = 6 tracks.

**Note**: Repeat blocks only support structural repetition; they do not intelligently merge identical tracks.
During parsing, they are automatically expanded into repeated lines before further processing, without affecting other functionality.

---

## 12. Output File Information

The human-readable output of `generate` and `compile` commands now includes file details:

```bash
> python cli.py generate my_song --output song.wav --duration 4
Generated: output/song.wav (86.2 KB, 0.5s, 44100Hz 16-bit stereo)

> python cli.py compile song.acml --duration 8
Project: projects/song.json
Output:  output/song.wav (1.2 MB, 4.0s, 44100Hz 16-bit stereo)
```

`--json` mode is unaffected and still outputs plain JSON.

---

---

## 16. FM Synthesis (Frequency Modulation)

FM synthesis uses two sine wave oscillators: a **carrier** (produces the sound) and a **modulator** (changes the carrier frequency).
By adjusting the modulation ratio and index, a wide range of timbres from soft to metallic can be produced.

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fm_ratio` | `2.0` | Modulator frequency = carrier frequency × ratio. Integer ratios (1,2,3...) produce harmonic timbres; non-integer ratios (1.5,2.7...) produce inharmonic/metallic sounds |
| `fm_index` | `3.0` | Modulation depth. Higher values produce more harmonics (brighter/harsher), lower values approach a pure sine wave |

### ACML Usage

```acml
[track metallic]
instrument = fm
fm_ratio = 5.0     # Modulation ratio 5:1
fm_index = 8.0     # Deep modulation
notes = C4:q:mf,E4:q:mf,G4:q:mf

[track soft]
instrument = fm
fm_ratio = 1.0     # Modulation ratio 1:1
fm_index = 0.5     # Shallow modulation
notes = C4:q:mf,E4:q:mf,G4:q:mf
```

### CLI Usage

```bash
acm track add project --instrument fm --fm-ratio 3.0 --fm-index 5.0 --notes "C4:q:mf"
```

---

## 17. Wavetable Synthesis

Wavetable synthesis stores predefined periodic waveforms as sampled value tables, generating sound through phase lookup + linear interpolation.
Supports multiple classic waveforms and custom waveforms.

### Preset Waveforms

| Shape | Description |
|-------|-------------|
| `saw` | Sawtooth wave, bright and thick |
| `square` | Square wave, hollow feel (similar to 8-bit game sound effects) |
| `triangle` | Triangle wave, soft, between sine and sawtooth |
| `sine` | Pure sine wave, same as piano but implemented via table lookup |

### Custom Waveforms

A comma-separated list of floating-point numbers, automatically normalized to the wavetable length. For example, an 8-point approximation of a triangle wave:

```acml
wavetable = 0.0,0.5,1.0,0.5,0.0,-0.5,-1.0,-0.5
```

### Default Value

When `wavetable` is not specified, it defaults to `saw` (sawtooth wave).

### Usage

```acml
[track bass_line]
instrument = wavetable
wavetable = square
notes = C3:q:mf,E3:q:mf,G3:q:mf

[track custom]
instrument = wavetable
wavetable = 0.0,0.3,1.0,0.3,-0.3,-1.0,-0.3
notes = C4:q:mf
```

```bash
acm track add project --instrument wavetable --wavetable triangle --notes "C4:q:mf"
```

---

## 18. Sample Playback (Sample Playback)

Supports loading external WAV files as instruments. The system automatically pitch-shifts the sample to the target note's pitch.

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `sample` | — | WAV file path (required) |
| `sample_pitch` | `C4` | Original pitch of the recorded sample. When playing C4, it plays at original speed; when playing G4, it pitch-shifts upward |

### How It Works

- Loads a WAV file, automatically mixes multi-channel audio to mono
- Pitch shifting via linear interpolation resampling: ratio = target frequency / sample original frequency
- Each note has an exponential decay envelope

### Usage

```acml
[track vox]
instrument = sample
sample = vox_oh.wav
sample_pitch = C4       # Sample recorded at C4
notes = C4:q:mf,G4:q:mf,C5:q:mf
```

```bash
acm track add project --instrument sample --sample kick.wav --sample-pitch C4 --notes "C4:q:mf"
```

---

## 19. Auto Harmony

Automatically generates harmony parts for melody notes without manually writing a second part.

### Supported Intervals

| Parameter Value | Semitones | Description |
|-----------------|-----------|-------------|
| `3` | +4 | Major 3rd above |
| `3below` | -4 | Major 3rd below |
| `5` | +7 | Perfect 5th above |
| `6` | +9 | Major 6th above |
| `octave` | +12 | Octave above |
| `octavebelow` | -12 | Octave below |
| `4` | +5 | Perfect 4th above |
| `2` | +2 | Major 2nd above |
| `7` | +10 | Minor 7th above |
| `unison` | 0 | Unison (testing purpose) |

### How It Works

- For each note in the track, a note offset by the specified semitones is added at the same position
- Harmony volume = melody volume × 0.6
- Works with extended note format and pattern mode
- Does not apply to drum and sample tracks

### Usage

```acml
[track melody]
instrument = piano
harmony = 3           # Automatically adds a 3rd above
notes = C4:q:mf,E4:q:mf,G4:q:mf
```

```bash
acm track add project --instrument piano --harmony 5 --notes "C4:q:mf,E4:q:mf"
```

---

## 20. Chord Recommendation (Chord Recommendation)

Use the `analyze` subcommand to analyze the melody of existing tracks and automatically recommend chord progressions.

### How It Works

1. Groups the track's notes by bar (default 4 beats per bar)
2. Extracts pitch classes for each bar
3. Iterates through 18 chord types to find the chord covering the most melody notes
4. Iterates through 12 root notes to select the best match

### CLI Usage

```bash
# Analyze chord progression (default analyzes track 1)
acm analyze myproject

# Specify track and bar length
acm analyze myproject --track 2 --beats-per-bar 3

# JSON output
acm analyze myproject --json
```

### Example Output

```bash
> acm analyze myproject
Track 1 (piano): Cmaj | Fmaj | G7 | Cmaj
```

### Notes

- Only works with tracks using the extended note format
- Chord recommendation is based on pitch matching and does not include rhythmic/stylistic factors
- Bars with no notes output `N.C.` (No Chord)

---

## Appendix: Frequently Asked Questions

**Q: The track notes are very long. How do I wrap lines in an ACML file?**

A: Add `+` at the end of the line to continue:

```acml
notes = C4:q:mf,E4:q:mf,G4:q:mf, +
       C4:q:mf,E4:q:mf,G4:q:mf, +
       D4:q:mf,F4:q:mf,A4:q:mf,D5:q:mf
```

Spaces after `+` and leading whitespace on continuation lines are automatically removed, and content is concatenated directly.
See [Chapter 10: Line Continuation](#10-line-continuationline-continuation).

**Q: I get "project xxx not found. Did you mean to run 'init' first?"**

A: Use `compile` instead of manually doing `init` + `track add` + `generate`.
`compile` automatically creates the project and generates audio.

**Q: Can a single drum track play kick and snare simultaneously?**

A: Yes. Extended drum notes use commas to separate drum hits in sequence:
`notes = K:q:mf,S:q:mf,K:q:mf,S:q:mf`
This plays sequentially. For simultaneous hits, create two drum tracks.

**Q: How do I repeat a track multiple times?**

A: Use the `loops` property: add `loops = 4` in ACML, or use `--loops 4` in CLI.
The track content (notes or pattern) will automatically repeat the specified number of times.

**Q: What is the difference between parallel and serial mode?**

A: `parallel` (default) means all tracks start at 0 seconds simultaneously and blend together. `serial` means tracks play sequentially—the next starts after the previous finishes. The two can be mixed. See [Track Definition - Playback Mode](#playback-mode) for details.

**Q: Can drum note velocity be omitted?**

A: Yes. When velocity is omitted, the previous drum note's velocity is automatically reused:
```
notes = K:q:f,S:q,K:q,S:q    # S and second K use f (0.8) velocity
```

**Q: How do I export a MIDI file?**

A: Use the `--midi filename.mid` option with the `compile` or `generate` command.
The MIDI file is output to the `output/` directory. Drums are automatically mapped to the GM standard drum channel (channel 10).

Using `--prowav` provides a one-step compilation + MIDI export + FluidSynth high-quality WAV rendering.

**Q: How do I render high-quality WAV with FluidSynth?**

A: Two methods:

1. One-click rendering: `python cli.py compile song.acml --prowav`
2. Step-by-step: First export MIDI (`--midi`), then use the `midi2wav` command

```bash
# Method 1: All-in-one
python cli.py compile song.acml --prowav --loop 1

# Method 2: Step-by-step
python cli.py compile song.acml --midi song.mid
python cli.py midi2wav output/song.mid --output output/song_final.wav
```

Prerequisites:
- Install FluidSynth (`choco install fluidsynth` or download from the official website)
- Download a SoundFont file (e.g., FluidR3_GM.sf2), place it in `~/.acm/` or specify via `--soundfont`

**Q: How do I adjust the FM synthesizer's ratio and index?**

A: ratio controls the modulator frequency (integer=harmonic, non-integer=inharmonic/metallic), index controls modulation depth (higher=brighter/harsher). Classic timbre references:
- Electric piano: ratio=2, index=3 (default)
- Bell: ratio=1, index=5
- Bass: ratio=0.5, index=2
- Metal cymbal: ratio=1.4, index=8

**Q: Which waveforms does Wavetable support?**

A: Preset waveforms: `saw`, `square`, `triangle`, `sine`. Also supports comma-separated custom values. When not specified, defaults to `saw`.

**Q: Does sample playback support stereo WAV?**

A: Yes. Stereo or multi-channel WAV files are automatically mixed to mono for processing.

**Q: How do I automatically generate harmony for a melody?**

A: Set `harmony = 3` (3rd above), `harmony = 5` (5th above), or `harmony = octave` (octave above) on the track. The system automatically adds harmony to each melody note.

**Q: How do I analyze the chord progression of an existing melody?**

A: Use the `analyze` subcommand: `acm analyze project_name`. The system analyzes by bar and recommends chords.

**Q: How do I customize the project and output directories?**

A: Use the global options `--project-dir` and `--output-dir`, or set the environment variables
`ACM_PROJECT_DIR` and `ACM_OUTPUT_DIR`. The defaults are `projects/` and `output/` respectively.
