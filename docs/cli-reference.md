# ACM CLI 参考手册

ACM（编曲工具）的命令行界面。支持从 ACML 文件编译音乐、管理项目、导出 MIDI、以及通过 FluidSynth 渲染高质量 WAV。

---

## 目录

1. [快速入门](#1-快速入门)
2. [全局选项](#2-全局选项)
3. [compile — 从 ACML 编译](#3-compile--从-acml-编译)
4. [init — 初始化项目](#4-init--初始化项目)
5. [track — 音轨管理](#5-track--音轨管理)
6. [generate — 从项目生成音频](#6-generate--从项目生成音频)
7. [analyze — 和弦分析](#7-analyze--和弦分析)
8. [midi2wav — MIDI 转 WAV](#8-midi2wav--midi-转-wav)
9. [环境变量](#9-环境变量)

---

## 1. 快速入门

```bash
# 一步到位：编译 ACML 并渲染高质量 WAV
python cli.py compile samples/acm.acml --prowav --loop 1

# 三个输出文件：
#   output/mouse.wav          — 本引擎合成的普通 WAV
#   output/mouse.mid          — MIDI 文件
#   output/mouse_prowav.wav   — FluidSynth 渲染的高质量 WAV
```

常用命令速查：

| 用途 | 命令 |
|------|------|
| 编译 ACML → WAV + MIDI | `python cli.py compile song.acml --midi song.mid` |
| 编译 + FluidSynth 成品 | `python cli.py compile song.acml --prowav` |
| 查看所有子命令 | `python cli.py --help` |
| 查看子命令详情 | `python cli.py compile --help` |
| 输出 JSON 给脚本 | `python cli.py status --json` |

---

## 2. 全局选项

所有子命令前均可使用：

| 选项 | 说明 |
|------|------|
| `--version` | 输出版本号 |
| `--project-dir <目录>` | 项目文件目录（默认 `projects/`，环境变量 `ACM_PROJECT_DIR`） |
| `--output-dir <目录>` | 输出文件目录（默认 `output/`，环境变量 `ACM_OUTPUT_DIR`） |

---

## 3. compile — 从 ACML 编译

最常用的子命令。读取 `.acml` 文件，解析音轨、合成音频、可选导出 MIDI 和 FluidSynth 渲染。

```bash
python cli.py compile <file.acml> [选项]
```

### 参数

| 参数 | 说明 |
|------|------|
| `file` | `.acml` 文件路径（必需） |
| `--output <文件名>` | 输出 WAV 文件名（默认 `{项目名}.wav`） |
| `--bpm <数值>` | 覆盖 ACML 中的 BPM |
| `--duration <秒>` | 音频时长（默认 4 秒） |
| `--midi <文件名>` | 同时导出标准 MIDI 文件 |
| `--reverb <0.0-1.0>` | 混响强度 |
| `--delay <0.0-1.0>` | 延迟强度 |
| `--chorus <0.0-1.0>` | 合唱强度 |
| `--loop <次数>` | 整曲循环次数（serial 轨重复次数，覆盖 ACML 中的 `loop`） |
| `--prowav` | 编译后自动用 FluidSynth 渲染高质量 WAV |
| `--soundfont <路径>` | prowav 使用的 SoundFont `.sf2` 文件 |
| `--gain <倍率>` | prowav 增益倍率（默认 1.0） |
| `--json` | JSON 格式输出结果 |

### 示例

```bash
# 基础编译
python cli.py compose samples/pop_demo.acml --duration 8

# 覆盖 BPM + 导出 MIDI
python cli.py compose song.acml --bpm 140 --midi song.mid

# 自定义输出文件名
python cli.py compose song.acml --output final.wav

# 一键高质量渲染（需要已安装 FluidSynth 和 SoundFont）
python cli.py compose samples/acm.acml --prowav --loop 2

# 指定 SoundFont 和增益
python cli.py compose samples/acm.acml --prowav --soundfont "C:\sf2\FluidR3_GM.sf2" --gain 1.5

# JSON 输出（适合脚本调用）
python cli.py compose song.acml --json
```

### prowav 说明

`--prowav` 是三步合一的快捷方式：

1. 编译 ACML → WAV（本引擎合成）
2. 同时导出 MIDI
3. 调用 `fluidsynth` 将 MIDI → 高质量 WAV（`*_prowav.wav`）

不指定 `--midi` 时自动从输出文件名派生 MIDI 路径。
SoundFont 查找顺序：`--soundfont` 参数 → `~/.acm/FluidR3_GM.sf2` → 环境默认路径。

---

## 4. init — 初始化项目

创建一个新的空白项目 JSON 文件。

```bash
python cli.py init <项目名> [选项]
```

### 参数

| 参数 | 说明 |
|------|------|
| `项目名` | 项目名称（必需） |
| `--force` | 覆盖已有项目 |
| `--json` | JSON 格式输出 |

### 示例

```bash
python cli.py init mysong
python cli.py init mysong --force
python cli.py init mysong --json   # → {"name": "mysong", "status": "initialized"}
```

初始化后生成 `projects/mysong.json`，可用 `track add` 添加音轨，或用 `generate` 生成音频。

---

## 5. track — 音轨管理

对已初始化的项目进行音轨增删改查。

```bash
python cli.py track <子命令> <项目名> [选项]
```

### 5.1 track add — 添加音轨

```bash
python cli.py track add <项目名> --instrument <乐器> [选项]
```

| 选项 | 说明 |
|------|------|
| `--instrument <乐器>` | 音色（必需）：piano, guitar, bass, sawtooth, organ, bell, strings, brass, pad, lead, fm, wavetable, sample, trumpet, tuba, drums |
| `--scale <根音>` | 音阶根音，如 C, D, G（默认 C） |
| `--pattern <模式>` | 节奏模式：pop, rock, jazz, latin, funk, shuffle, trap |
| `--octave <数值>` | 默认八度（默认 4） |
| `--notes <音符>` | 音符序列，逗号分隔。支持紧凑标记（`C5qf`）和扩展标记（`C5:q:mf`） |
| `--volume <0.0-1.0>` | 音量（默认 1.0） |
| `--pan <-1.0-1.0>` | 声场位置（默认 0.0） |
| `--durations <列表>` | 不等长时值，如 `2,1,1,2` |
| `--loops <次数>` | 音轨循环次数（默认 1） |
| `--mode <模式>` | 播放模式：parallel（同时）或 serial（串行） |
| `--kick <字符串>` | 底鼓节奏 0/1 字符串 |
| `--snare <字符串>` | 军鼓节奏 0/1 字符串 |
| `--hihat <字符串>` | 踩镲节奏 0/1 字符串 |
| `--arpeggio <模式>` | 琶音：up, down, random, updown, downup |
| `--wavetable <形状>` | 波形表：saw, square, triangle, sine 或自定义值 |
| `--sample <路径>` | 采样 WAV 文件路径 |
| `--sample-pitch <音名>` | 采样原始音高（默认 C4） |
| `--harmony <间隔>` | 自动和声：3, 5, 6, octave, 3below 等 |
| `--fm-ratio <数值>` | FM 调制比（默认 2.0） |
| `--fm-index <数值>` | FM 调制指数（默认 3.0） |
| `--json` | JSON 格式输出 |

### 5.2 track list — 列出音轨

```bash
python cli.py track list <项目名> [--json]
```

### 5.3 track remove — 删除音轨

```bash
python cli.py track remove <项目名> <序号>
```

### 5.4 track update — 修改音轨

```bash
python cli.py track update <项目名> <序号> [选项]
```

选项同 `track add`。

### 示例

```bash
# 添加钢琴音轨
python cli.py track add mysong --instrument piano --notes "C4:q:mf,E4:q:mf,G4:q:mf"

# 添加鼓音轨
python cli.py track add mysong --instrument drums --notes "K:q:mf,S:q:mf,H:e:mf"

# 查看所有音轨
python cli.py track list mysong

# 删除第 2 个音轨
python cli.py track remove mysong 2

# 修改第 1 个音轨的乐器
python cli.py track update mysong 1 --instrument guitar
```

---

## 6. generate — 从项目生成音频

从已存在的项目 JSON 文件生成音频。

```bash
python cli.py generate <项目名> --output <文件名> [选项]
```

### 参数

| 参数 | 说明 |
|------|------|
| `项目名` | 项目名称（必需） |
| `--output <文件名>` | 输出 WAV 文件名（必需） |
| `--bpm <数值>` | 覆盖项目 BPM |
| `--duration <秒>` | 音频时长（默认 4 秒） |
| `--midi <文件名>` | 同时导出 MIDI |
| `--reverb <0.0-1.0>` | 混响强度 |
| `--delay <0.0-1.0>` | 延迟强度 |
| `--chorus <0.0-1.0>` | 合唱强度 |
| `--loop <次数>` | 整曲循环次数 |
| `--json` | JSON 格式输出 |

### 示例

```bash
python cli.py generate mysong --output mysong.wav --bpm 120 --duration 60
python cli.py generate mysong --output mysong.wav --midi mysong.mid
```

---

## 7. analyze — 和弦分析

分析指定音轨的旋律，按小节推荐和弦进行。

```bash
python cli.py analyze <项目名> [选项]
```

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `项目名` | — | 项目名称（必需） |
| `--track <序号>` | `1` | 要分析的音轨序号（从 1 开始） |
| `--beats-per-bar <拍数>` | `4` | 每小节拍数 |
| `--json` | — | JSON 格式输出 |

### 示例

```bash
python cli.py analyze mysong
# → Track 1 (piano): Cmaj | Fmaj | G7 | Cmaj

python cli.py analyze mysong --track 2 --beats-per-bar 3
python cli.py analyze mysong --json
```

---

## 8. midi2wav — MIDI 转 WAV

使用外部 FluidSynth 将 MIDI 文件渲染为 WAV 音频。

**前置要求**：
- 安装 [FluidSynth](https://www.fluidsynth.org)
- 获取一个 SoundFont `.sf2` 文件（如 [FluidR3_GM.sf2](https://github.com/pianobooster/fluid-soundfont/releases)）

```bash
python cli.py midi2wav <input.mid> [选项]
```

### 参数

| 参数 | 说明 |
|------|------|
| `input` | 输入的 `.mid` 文件路径（必需） |
| `--output, -o <文件名>` | 输出 WAV 文件路径（默认替换扩展名为 `.wav`） |
| `--soundfont, -s <路径>` | SoundFont `.sf2` 文件路径 |
| `--gain, -g <倍率>` | 增益倍率（默认 1.0） |
| `--sample-rate, -r <Hz>` | 采样率（默认 44100） |

### 示例

```bash
# 基本用法（自动查找 SoundFont）
python cli.py midi2wav output/song.mid

# 指定 SoundFont 和增益
python cli.py midi2wav output/song.mid -s "C:\sf2\FluidR3_GM.sf2" -g 1.5

# 指定输出路径
python cli.py midi2wav output/song.mid -o output/final.wav
```

SoundFont 查找顺序：
1. `--soundfont` 参数指定的路径
2. `~/.acm/default.sf2`
3. `~/.acm/FluidR3_GM.sf2`
4. 系统默认路径

---

## 9. 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ACM_PROJECT_DIR` | 项目 JSON 文件的存放目录 | `projects/` |
| `ACM_OUTPUT_DIR` | 音频输出文件的存放目录 | `output/` |

可通过 CLI 全局选项 `--project-dir` 和 `--output-dir` 覆盖。
