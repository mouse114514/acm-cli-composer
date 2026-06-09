# ACML v1 — ACM Composition Language 参考手册

ACML（ACM Composition Markup Language）是 ACM 编曲工具的声明式标记语言，
用一个 `.acml` 文件描述完整乐曲，通过 `compile` 命令一键生成项目文件和成品 WAV。

---

## 目录

1. [文件结构](#1-文件结构)
2. [全局设置](#2-全局设置)
3. [音轨定义](#3-音轨定义)
4. [音符标记法](#4-音符标记法)
5. [乐器列表](#5-乐器列表)
6. [鼓点](#6-鼓点)
7. [声场（Pan）](#7-声场pan)
8. [琶音器（Arpeggiator）](#8-琶音器arpeggiator)
9. [和弦标记法（Chord Notation）](#9-和弦标记法chord-notation)
10. [行续接（Line Continuation）](#10-行续接line-continuation)
11. [ACML 重复块](#11-acml-重复块)
12. [输出文件信息](#12-输出文件信息)
13. [完整示例](#13-完整示例)
14. [编译命令](#14-编译命令)
15. [CLI 子命令参考](#15-cli-子命令参考)
16. [FM 合成](#16-fm-合成frequency-modulation)
17. [波形表合成](#17-波形表合成wavetable)
18. [采样回放](#18-采样回放sample-playback)
19. [自动和声](#19-自动和声auto-harmony)
20. [和弦推荐](#20-和弦推荐chord-recommendation)

---

## 1. 文件结构

```
# 注释以 # 开头
全局参数

[track 音轨名称]
音轨属性

[track 另一个音轨]
音轨属性
```

- `#` 开头的行是注释，被忽略
- 全局参数写在所有音轨节之前
- `[track xxx]` 开始一个音轨节，`[xxx]` 也可（自动去掉 `track` 前缀）
- 属性用 `=` 或 `:` 分隔，空格可有可无

---

## 2. 全局设置

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | 字符串 | `"untitled"` | 项目名称，也是 JSON 文件名 |
| `bpm` | 整数 | `120` | 每分钟拍数 |
| `loop` | 整数 | `1` | 整曲循环次数（serial 轨重复次数，parallel 轨只播放一遍） |

```
name = "My Song"
bpm = 118
```

也允许冒号分隔：

```
name: "My Song"
bpm: 118
```

BPM 可通过 `--bpm` 命令行参数覆盖。

`loop` 可通过 `--loop` 命令行参数覆盖。值为 1 时只播放一遍；N > 1 时 serial 音轨依次重复 N 次，总时长 = max(parallel 时长, serial 总时长 × N)。parallel 音轨只渲染一次，不会因循环加倍。详见 [整曲循环](#-整曲循环)。

---

## 3. 音轨定义

```
[track 音轨名称]
属性 = 值
```

`[track 音轨名称]` 中的名称仅用于阅读标识，不影响输出。

### 通用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `instrument` | 字符串 | `piano` | 音色，参见乐器列表 |
| `scale` | 字符串 | `C` | 音阶根音 (C, D, G, A 等) |
| `pattern` | 字符串 | `pop` | 节奏模式 (pop, rock, jazz, latin, funk, shuffle, trap) |
| `octave` | 整数 | `4` | 默认八度 |
| `notes` | 字符串 | — | 音符序列，逗号分隔 |
| `volume` | 浮点数 | `1.0` | 音量 0.0–1.0 |
| `pan` | 浮点数 | `0.0` | 声场位置 -1.0(左) ~ 1.0(右) |
| `durations` | 字符串 | — | 不等长时值，逗号分隔，如 `2,1,1,2`（三快两慢） |
| `loops` | 整数 | `1` | 循环次数，重复音轨内容 N 次 |
| `arpeggio` | 字符串 | — | 琶音模式 (up, down, random, updown, downup) |
| `wavetable` | 字符串 | `saw` | 波形表类型 (saw, square, triangle, sine 或逗号分隔自定义值) |
| `sample` | 字符串 | — | 采样 WAV 文件路径 |
| `sample_pitch` | 字符串 | `C4` | 采样录制时的原始音高 |
| `harmony` | 字符串 | — | 自动和声间隔 (3, 5, 6, octave, 3below 等) |
| `fm_ratio` | 浮点数 | `2.0` | FM 合成调制比（载波频率倍数） |
| `fm_index` | 浮点数 | `3.0` | FM 合成调制指数（调制深度） |
| `mode` | 字符串 | `parallel` | 播放模式：`parallel`=同时播放，`serial`=串行播放 |

### 播放模式

`mode` 控制音轨在时间线上的播放方式：

| 值 | 说明 |
|----|------|
| `parallel` | **同时播放**（默认）。所有 parallel 音轨从 0 秒开始叠加混合，适合编配和声、节奏等多轨同时发声的场景 |
| `serial` | **串行播放**。serial 音轨按定义顺序依次播放，前一个播完后一个才开始。总时长 = max(parallel 时长, 所有 serial 轨时长之和)。支持与 parallel 轨混用 |

```acml
# serial 示例：两段旋律依次播放
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
# 混合模式：pad 铺底贯穿全程，旋律串行
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
# pad 播放全程，melody_a 播完后 melody_b 开始
```

### 整曲循环

全局 `loop` 控制整曲在时间线上重复的次数。

| 值 | 说明 |
|----|------|
| `1` | 只播放一遍（默认） |
| `N` | serial 音轨依次重复 N 次；parallel 音轨只渲染一次（不会因循环加倍） |

总时长 = max(所有 parallel 轨时长, 所有 serial 轨时长之和 × N)。

```acml
name = "Loops"
bpm = 120
loop = 3

[track pad]
instrument = pad
mode = parallel
notes = C3:w:mp
# pad 只播放 4 秒，loop 不影响它

[track melody]
instrument = lead
mode = serial
notes = C4:e:mf, E4:e:mf, G4:e:mf
# 3 遍循环：旋律播放 3 次，总时长 ≈ (0.5s × 6 个音) × 3 = 9s
# 总文件时长 = max(4s, 9s) = 9s
```

也可用 CLI 参数覆盖：`--loop 5`。

---

### 鼓点专用属性

当 `instrument = drums` 时，可通过下面属性指定鼓点节奏型。
若不指定，默认为：kick 每 4 拍第 1 拍，snare 每 4 拍第 3 拍，hihat 每拍都响。

| 属性 | 类型 | 说明 |
|------|------|------|
| `kick` | 字符串 | 底鼓节奏，如 `10001000`（1=响 0=不响） |
| `snare` | 字符串 | 军鼓节奏，如 `00100010` |
| `hihat` | 字符串 | 踩镲节奏，如 `11111111` |

也推荐直接使用鼓的扩展音符（见下节），更灵活。

---

## 4. 音符标记法

系统支持三种标记法，可按需混用（用逗号分隔）：

### 4.1 标准标记法（pattern + scale 模式）

只写音名（C, D, E...），使用 `scale` 和 `pattern` 驱动的音阶模式播放：

```
notes = C,D,E,F,G,A,B,C
```

`scale=C`, `octave=4` 时，上例播放 C4, D4, E4, F4, G4, A4, B4, C5。
使用 `R` 或 `_` 表示休止，休止不会消耗音符索引。

### 4.2 扩展标记法

每个音符独立指定时值、力度：`音名:时值:力度`。

```
notes = C4:q:mf,E4:q:mf,G4:q:mf,C5:h:f
```

**时值字母**：

| 字母 | 含义 | 拍数 |
|------|------|------|
| `w` | 全音符 whole | 4 拍 |
| `h` | 二分音符 half | 2 拍 |
| `q` | 四分音符 quarter | 1 拍 |
| `e` | 八分音符 eighth | 0.5 拍 |
| `s` | 十六分音符 sixteenth | 0.25 拍 |

加 `.` 表示附点，时值 ×1.5，如 `h.` = 3 拍。

**力度标记**：

| 标记 | 数值 | 说明 |
|------|------|------|
| `ppp` | 0.20 | 最弱 |
| `pp` | 0.25 | 很弱 |
| `p` | 0.35 | 弱 |
| `mp` | 0.50 | 中弱 |
| `mf` | 0.65 | 中强 |
| `f` | 0.80 | 强 |
| `ff` | 0.90 | 很强 |
| `fff` | 1.00 | 最强 |

力度也支持直接写数值：`C4:q:0.75`。

**休止**：`R:时值:力度` 或 `_:时值`，如 `R:h`（二分休止）、`R:q:mf`。

**升/降记号**：`C#`, `Db`, `F#`, `Bb` 等。

**移调**：音符后接数字可指定八度，如 `C#5` = 升C第5八度。

**扩展标记检测规则**：系统检测音符中是否包含 `:时值字母` 模式来决定是否使用扩展模式。
一旦检测到扩展标记，该音轨会忽略 `pattern` 和 `durations` 参数，
按音符列表从头到尾顺序播放。

### 4.3 紧凑标记法（快捷方式）

在 `.acml` 文件或 CLI 的 `--notes` 参数中，可以使用紧凑标记自动展开：

| 写法 | 展开结果 | 说明 |
|------|----------|------|
| `C5qf` | `C5:q:f` | 音名+八度+时值+力度 |
| `D5q(mf)` | `D5:q:mf` | 括号包裹力度 |
| `.` | `R:q` | 点号 = 四分休止 |
| `Kf` | `K:q:f` | 鼓点名称+力度 |
| `Hq(mf)` | `H:q:mf` | 鼓点名称+时值+括号力度 |
| `C5q` | `C5:q:mf` | 省略力度默认 mf |
| `Rh` | `R:h:mf` | 休止+时值 |

展开在输入时自动完成，存储在 JSON 中时已经是扩展格式。

---

## 5. 乐器列表

| 乐器名 | 音色描述 |
|--------|----------|
| `piano` | 纯正弦波，柔和干净 |
| `guitar` | 正弦波 + 三次谐波，温暖明亮 |
| `bass` | 锯齿波，厚实低沉 |
| `sawtooth` | 锯齿波，电子感 |
| `organ` | 4 层谐波混合，管风琴质感 |
| `bell` | 快衰减多谐波，钟声质感 |
| `strings` | 多层谐波混合（1-4次），弦乐合奏感 |
| `brass` | 方波 + 三次谐波带饱和，铜管感 |
| `pad` | 双失谐正弦波，铺垫音色 |
| `lead` | 增强型锯齿波+三次谐波，明亮电子主音 |
| `fm` | 2 算子 FM 合成（可调 ratio/index），金属/电子质感 |
| `wavetable` | 波形表合成（saw/square/triangle/sine 或自定义），复古数字感 |
| `sample` | 采样回放（加载 WAV，支持变调），真实乐器/人声 |
| `drums` | 鼓组，包含 K(底鼓), S(军鼓), H(闭镲), O(开镲), T(桶鼓) |
| `trumpet` | 多谐波混合（奇偶次谐波丰富），明亮铜管 |
| `tuba` | 强基频弱谐波，深沉低音铜管 |

鼓点乐器支持两种模式：
1. **扩展音符模式**：通过 `notes = K:q:mf,S:q:mf,H:q:mf` 等方式灵活排序
2. **传统模式**：使用 `kick`/`snare`/`hihat` 属性指定 0/1 字符串

同一音轨内两种模式不可混用。

---

## 7. 声场（Pan）

每个音轨可独立设置声场位置，使用恒功率声像定位（constant-power pan law），
确保中央声道不会比硬左/硬右响 +3dB。

```
pan = 0.0    # 居中（默认）
pan = -1.0   # 极左
pan = 1.0    # 极右
pan = -0.3   # 偏左
pan = 0.5    # 偏右
```

恒功率公式：`angle = (pan + 1) × π / 4`，左声道 = cos(angle)，右声道 = sin(angle)。

输出为立体声 16-bit WAV（44100Hz）。

---

## 6. 鼓点

### 6.1 扩展音符鼓点（推荐）

鼓音符使用 K/S/H/O/T 作为"音名"：

| 鼓类型 | 代码 | 说明 |
|--------|------|------|
| Kick | `K` | 底鼓，55Hz 正弦波 |
| Snare | `S` | 军鼓，噪声 + 180Hz 正弦 |
| Hi-hat(closed) | `H` | 闭镲，短噪声 |
| Hi-hat(open) | `O` | 开镲，长噪声 |
| Tom | `T` | 桶鼓，80Hz 正弦波 |

每个鼓点可独立设置力度和时值：

```
notes = K:q:f,S:q:mf,K:q:f,S:q:mf    # 底鼓军鼓交替
notes = H:e:mf,H:e:mf,H:e:mf,H:e:mf  # 八分踩镲
notes = T:q:f                         # 桶鼓
```

### 6.2 传统鼓点模式

通过 `kick`、`snare`、`hihat` 属性设置节奏字符串：

```
kick  = 1000100010001000
snare = 0010001000100010
hihat = 1111111111111111
```

1 = 响，0 = 不响。字符串长度不足时会重复。

---

## 13. 完整示例

### 示例 1 — 极简

```acml
name = "hello"
bpm = 120

[track piano]
instrument = piano
notes = C4:q:mf,E4:q:mf,G4:q:mf,C5:h:mf
```

### 示例 2 — Funk Machine (D Dorian, 118BPM)

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

### 示例 3 — Pop Demo

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

## 14. 编译命令

```
python cli.py compile <file.acml> [选项]
```

### 参数

| 参数 | 说明 |
|------|------|
| `file` | `.acml` 文件路径（必需） |
| `--duration <秒>` | 音频时长，默认 4 秒 |
| `--bpm <数值>` | 覆盖 ACML 中的 BPM |
| `--output <文件名>` | 自定义输出文件名，默认 `{项目名}.wav` |
| `--midi <文件名>` | 同时导出标准 MIDI 文件 |
| `--reverb <0.0-1.0>` | 混响强度 |
| `--delay <0.0-1.0>` | 延迟强度 |
| `--chorus <0.0-1.0>` | 合唱强度 |
| `--loop <次数>` | 整曲循环次数（serial 轨重复次数，覆盖 ACML 中的 `loop`） |
| `--prowav` | 编译后自动用 FluidSynth 渲染高质量 WAV（一步到位） |
| `--soundfont <路径>` | prowav 使用的 SoundFont `.sf2` 文件 |
| `--gain <倍率>` | prowav 增益倍率（默认 1.0） |
| `--json` | 以 JSON 格式输出结果信息 |

### 使用示例

```bash
# 基础编译
python cli.py compile samples/funk_machine.acml --duration 8

# 覆盖 BPM
python cli.py compile my_song.acml --bpm 140 --duration 30

# 自定义输出
python cli.py compile song.acml --output final.wav

# 同时导出 MIDI
python cli.py compile song.acml --output song.wav --midi song.mid

# 整曲循环（serial 轨重复 3 遍）
python cli.py compile song.acml --loop 3

# 加效果
python cli.py compile song.acml --reverb 0.3 --delay 0.2

# 一键高质量渲染（需要安装 FluidSynth 和 SoundFont）
python cli.py compile samples/acm.acml --prowav --loop 1

# 指定 SoundFont 和增益
python cli.py compile samples/acm.acml --prowav --soundfont "C:\sf2\FluidR3_GM.sf2" --gain 1.5

# JSON 输出（适合脚本处理）
python cli.py compile song.acml --json
```

### 编译流程

1. 解析 `.acml` 文件 → 提取全局参数和各音轨定义
2. 紧凑标记展开 → 将 `D5qf` 等快捷写法转为 `D5:q:f`
3. 写入 `projects/{name}.json` — 中间项目文件
4. 合成音频 → 写入 `output/{name}.wav` — 本引擎合成
5. （可选 `--midi`）导出 MIDI → `output/{name}.mid`
6. （可选 `--prowav`）调用 FluidSynth 渲染高质量 WAV → `output/{name}_prowav.wav`

### 输出文件

```
projects/
  └── {name}.json           # 中间项目文件（可用 track list / generate 操作）
output/
  ├── {name}.wav            # 本引擎合成的立体声音频 (44.1kHz, 16-bit)
  ├── {name}.mid            # （可选）MIDI 文件
  └── {name}_prowav.wav     # （可选，--prowav）FluidSynth 渲染的高质量 WAV
```

编译后仍可用原有命令操作项目：

```bash
python cli.py track list {name}
python cli.py generate {name} --output new.wav --bpm 200
```

---

## 15. CLI 子命令参考

### `init` — 初始化项目

```
python cli.py init <name> [--force] [--json]
```

### `track add` — 添加音轨

```
python cli.py track add <project> --instrument <乐器> [options]
```

常用选项：`--scale`, `--pattern`, `--octave`, `--notes`, `--volume`,
`--kick`, `--snare`, `--hihat`, `--pan`, `--durations`, `--loops`,
`--arpeggio`, `--wavetable`, `--sample`, `--sample-pitch`, `--harmony`,
`--fm-ratio`, `--fm-index`, `--mode`, `--json`

### `track list` — 列出音轨

```
python cli.py track list <project> [--json]
```

### `track remove` — 删除音轨

```
python cli.py track remove <project> <index>
```

### `track update` — 修改音轨

```
python cli.py track update <project> <index> [options]
```

### `generate` — 生成音频

```
python cli.py generate <project> --output <文件名> [--bpm] [--duration] [--midi] [--reverb] [--delay] [--chorus] [--loop] [--json]
```

### `compile` — 从 ACML 编译

```
python cli.py compile <file.acml> [--bpm] [--duration] [--output] [--midi] [--reverb] [--delay] [--chorus] [--loop] [--prowav] [--soundfont] [--gain] [--json]
```

### `analyze` — 和弦分析

```
python cli.py analyze <project> [--track N] [--beats-per-bar N] [--json]
```

分析指定音轨的旋律，按小节推荐和弦进行。

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `project` | — | 项目名称（必需） |
| `--track` | `1` | 要分析的音轨序号（从 1 开始） |
| `--beats-per-bar` | `4` | 每小节拍数（4 = 4/4 拍） |
| `--json` | — | JSON 格式输出 |

### `midi2wav` — MIDI 转 WAV

```
python cli.py midi2wav <input.mid> [--output] [--soundfont] [--gain] [--sample-rate]
```

使用外部 FluidSynth 将 MIDI 渲染为高质量 WAV。

| 参数 | 说明 |
|------|------|
| `input.mid` | MIDI 文件路径（必需） |
| `--output, -o <文件>` | 输出 WAV 路径（默认替换扩展名为 `.wav`） |
| `--soundfont, -s <路径>` | SoundFont `.sf2` 文件路径 |
| `--gain, -g <倍率>` | 增益倍率（默认 1.0） |
| `--sample-rate, -r <Hz>` | 采样率（默认 44100） |

前置要求：安装 [FluidSynth](https://www.fluidsynth.org) 并获取一个 SoundFont 文件（如 FluidR3_GM.sf2）。

### 全局选项

| 选项 | 说明 |
|------|------|
| `--version` | 输出版本号 |
| `--project-dir <目录>` | 项目文件目录 (默认: `projects/`, 环境变量: `ACM_PROJECT_DIR`) |
| `--output-dir <目录>` | 输出文件目录 (默认: `output/`, 环境变量: `ACM_OUTPUT_DIR`) |

---

---

## 8. 琶音器（Arpeggiator）

琶音模式替代简单的单音旋律生成，音轨的 `pattern` 控制节奏触发，
每个触发拍依次弹奏音阶中的不同音符。

### 支持模式

| 模式 | 说明 |
|------|------|
| `up` | 音阶上行循环 1-2-3-4-5-6-7-1-2-... |
| `down` | 音阶下行循环 7-6-5-4-3-2-1-7-6-... |
| `updown` | 上下交替 1-2-3-4-5-6-7-6-5-4-3-2-1-2-... |
| `downup` | 下上交替 7-6-5-4-3-2-1-2-3-4-5-6-7-6-... |
| `random` | 随机选取（种子固定保证确定） |

### 用法

**ACML 音轨属性**：

```acml
[track arp]
instrument = piano
scale = C
octave = 4
pattern = 1111
arpeggio = up
```

**CLI**：

```bash
python cli.py track add myproj --instrument piano --scale C --octave 4 --pattern 1111 --arpeggio up
```

**编译示例**：

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

### 工作原理

- 琶音从 `scale` 指定的音阶根音生成大调音阶音符（C 大调 = C, D, E, F, G, A, B）
- `octave` 控制起始八度
- `pattern` 的每个活动拍 (1) 推进琶音索引，非活动拍 (0) 跳过
- 琶音模式仅对标准 pattern 模式有效，不适用于扩展音符

---

## 9. 和弦标记法（Chord Notation）

ACML 支持和弦名称自动展开为组成音符，每个和弦音以相等时值排列生成快速琶音。

### 支持的和弦类型

| 写法 | 类型 | 组成音（半音间隔） |
|------|------|-------------------|
| `Cmaj` | 大三和弦 | 根音 + 大三度 + 纯五度 |
| `Cm` | 小三和弦 | 根音 + 小三度 + 纯五度 |
| `Cdim` | 减三和弦 | 根音 + 小三度 + 减五度 |
| `Caug` | 增三和弦 | 根音 + 大三度 + 增五度 |
| `C7` | 属七和弦 | 大三和弦 + 小七度 |
| `Cmaj7` | 大七和弦 | 大三和弦 + 大七度 |
| `Cm7` | 小七和弦 | 小三和弦 + 小七度 |
| `Cdim7` | 减七和弦 | 减三和弦 + 减七度 |
| `Cm7b5` | 半减七 | 减三和弦 + 小七度 |
| `Caug7` | 增七和弦 | 增三和弦 + 小七度 |
| `C6` | 六和弦 | 大三和弦 + 大六度 |
| `Cm6` | 小六和弦 | 小三和弦 + 大六度 |
| `C9` | 属九和弦 | 属七 + 大九度 |
| `Cmaj9` | 大九和弦 | 大七 + 大九度 |
| `Cm9` | 小九和弦 | 小七 + 大九度 |
| `Csus2` | 挂留二 | 根音 + 大二度 + 纯五度 |
| `Csus4` | 挂留四 | 根音 + 纯四度 + 纯五度 |
| `Cadd9` | 加九和弦 | 大三和弦 + 大九度 |

### 用法

**扩展格式（推荐）**：

```
notes = Cmaj7:q:mf,Fmaj7:q:mf,G7:q:mf,Cmaj7:q:mf
```

和弦 `Cmaj7` 扩展到 C4, E4, G4, B4，每个音获得 `q ÷ 4 = s`（十六分音符）的时值，
产生快速琶音效果。和弦总时长保持原指定时值（q = 1 拍）。

**指定八度**：

```
notes = C5maj7:q:mf    # C5, E5, G5, B5
notes = F4m:q:mf       # F4, Ab4, C5
```

**紧凑格式**：

```
notes = Cmaj7qf        # = Cmaj7:q:f → C4:s:f,E4:s:f,G4:s:f,B4:s:f
notes = G7h(mf)        # = G7:h:mf  → G4:e:mf,B4:e:mf,D5:e:mf,F5:e:mf
```

**与普通音符混合**：

```
notes = Cmaj7:q:mf,D4:q:mf,E4:q:mf
```

仅含有和弦后缀（`maj7`, `m`, `7` 等）的会被展开；
普通单音名（`C:q:mf`, `D4:q:mf`）保持不变，避免歧义。

**完整的和弦进行示例**：

```acml
name = "chord_progression"
bpm = 100

[track piano]
instrument = piano
notes = Cmaj7:q:mf,Fmaj7:q:mf,G7:q:mf,Cmaj7:q:mf
```

---

## 10. 行续接（Line Continuation）

长 `notes` 行可用 `+` 续接到下一行，提高可读性。

续接班规则：
- 行末的 `+` 表示下一行为续行
- 续行的前导空白被自动去除
- 续行内容直接拼接在前一行末尾（不加空格）

```
# 续行示例
notes = C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf, +
       C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf, +
       D4:q:mf,F4:q:mf,A4:q:mf,D5:q:mf

# 等价于一行：
# C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf,C4:q:mf,E4:q:mf,G4:q:mf,C5:q:mf,D4:q:mf,F4:q:mf,A4:q:mf,D5:q:mf
```

`+` 后的空格和续行的前导空格均被忽略，保证内容正确拼接。

---

## 11. ACML 重复块

`[repeat N]` 和 `[/repeat]` 标签可重复音轨定义，减少重复书写。

### 用法

```acml
name = "repeated_song"
bpm = 120

[repeat 4]
[track piano]
instrument = piano
notes = C4:q:mf
[/repeat]
```

以上等价于手动编写 4 个 `[track piano]` 节。

### 嵌套

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

外层的 `[repeat 2]` × 内层的 `[repeat 3]` = 6 个音轨。

**注意**：repeat 块仅支持结构上的重复，不会智能合并相同音轨。
解析时自动展开为重复行后再解析，不影响其他功能。

---

## 12. 输出文件信息

`generate` 和 `compile` 命令的人类模式输出现在包含文件详细信息：

```bash
> python cli.py generate my_song --output song.wav --duration 4
Generated: output/song.wav (86.2 KB, 0.5s, 44100Hz 16-bit stereo)

> python cli.py compile song.acml --duration 8
Project: projects/song.json
Output:  output/song.wav (1.2 MB, 4.0s, 44100Hz 16-bit stereo)
```

`--json` 模式不受影响，仍输出纯 JSON。

---

---

## 16. FM 合成（Frequency Modulation）

FM 合成使用两个正弦波振荡器：**载波**（产生声音）和**调制波**（改变载波频率）。
通过调整调制比和调制指数，可以产生从柔和到金属感的丰富音色。

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `fm_ratio` | `2.0` | 调制波频率 = 载波频率 × ratio。整数比（1,2,3...）产生谐波音色，非整数比（1.5,2.7...）产生非谐波/金属感 |
| `fm_index` | `3.0` | 调制深度。值越大谐波越多（明亮/刺耳），值越小越接近纯正弦 |

### ACML 用法

```acml
[track metallic]
instrument = fm
fm_ratio = 5.0     # 调制比 5:1
fm_index = 8.0     # 深度调制
notes = C4:q:mf,E4:q:mf,G4:q:mf

[track soft]
instrument = fm
fm_ratio = 1.0     # 调制比 1:1
fm_index = 0.5     # 浅调制
notes = C4:q:mf,E4:q:mf,G4:q:mf
```

### CLI 用法

```bash
acm track add project --instrument fm --fm-ratio 3.0 --fm-index 5.0 --notes "C4:q:mf"
```

---

## 17. 波形表合成（Wavetable）

波形表合成将预定义的周期波形存储为采样值表，通过相位查表 + 线性插值生成声音。
支持多种古典波形和自定义波形。

### 预制波形

| 形状 | 说明 |
|------|------|
| `saw` | 锯齿波，明亮厚实 |
| `square` | 方波，中空感（类似 8-bit 游戏音效） |
| `triangle` | 三角波，柔和介于正弦和锯齿之间 |
| `sine` | 纯正弦波，与 piano 相同但通过查表实现 |

### 自定义波形

以逗号分隔的浮点数列表，自动归一化到波形表长度。例如 8 点近似三角波：

```acml
wavetable = 0.0,0.5,1.0,0.5,0.0,-0.5,-1.0,-0.5
```

### 默认值

不指定 `wavetable` 时默认使用 `saw`（锯齿波）。

### 用法

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

## 18. 采样回放（Sample Playback）

支持加载外部 WAV 文件作为乐器。系统自动将采样变调到目标音符的音高。

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `sample` | — | WAV 文件路径（必填） |
| `sample_pitch` | `C4` | 采样录制时的原始音高。当弹奏 C4 时以原始速度播放，弹奏 G4 时升速变调 |

### 工作原理

- 加载 WAV 文件，自动将多声道混合为单声道
- 通过线性插值重采样实现变调：ratio = 目标频率 / 采样原始频率
- 每个音符带指数衰减包络

### 用法

```acml
[track vox]
instrument = sample
sample = vox_oh.wav
sample_pitch = C4       # 采样录制于 C4
notes = C4:q:mf,G4:q:mf,C5:q:mf
```

```bash
acm track add project --instrument sample --sample kick.wav --sample-pitch C4 --notes "C4:q:mf"
```

---

## 19. 自动和声（Auto-Harmony）

自动为旋律音符生成和声部，无需手动编写第二个声部。

### 支持间隔

| 参数值 | 半音数 | 说明 |
|--------|--------|------|
| `3` | +4 | 大三度上 |
| `3below` | -4 | 大三度下 |
| `5` | +7 | 纯五度上 |
| `6` | +9 | 大六度上 |
| `octave` | +12 | 八度上 |
| `octavebelow` | -12 | 八度下 |
| `4` | +5 | 纯四度上 |
| `2` | +2 | 大二度上 |
| `7` | +10 | 小七度上 |
| `unison` | 0 | 同度（测试用） |

### 工作原理

- 对音轨中每个音符，在相同位置叠加一个偏移指定半音的音符
- 和声音量 = 旋律音量 × 0.6
- 适用于扩展音符格式和 pattern 模式
- 不适用于鼓和采样音轨

### 用法

```acml
[track melody]
instrument = piano
harmony = 3           # 自动叠加三度上
notes = C4:q:mf,E4:q:mf,G4:q:mf
```

```bash
acm track add project --instrument piano --harmony 5 --notes "C4:q:mf,E4:q:mf"
```

---

## 20. 和弦推荐（Chord Recommendation）

通过 `analyze` 子命令分析已有音轨的旋律，自动推荐和弦进行。

### 工作原理

1. 将音轨的音符按小节分组（默认 4 拍一小节）
2. 对每小节提取音高类别（pitch class）
3. 遍历 18 种和弦类型，找出覆盖最多旋律音的和弦
4. 遍历 12 个根音，选择最佳匹配

### CLI 用法

```bash
# 分析和弦进行（默认分析音轨 1）
acm analyze myproject

# 指定音轨和小节长度
acm analyze myproject --track 2 --beats-per-bar 3

# JSON 输出
acm analyze myproject --json
```

### 示例输出

```bash
> acm analyze myproject
Track 1 (piano): Cmaj | Fmaj | G7 | Cmaj
```

### 注意事项

- 仅适用于使用扩展音符格式的音轨
- 和弦推荐基于音高匹配，不包含节奏/风格因素
- 无音符的小节输出 `N.C.`（无和弦）

---

## 附：常见问题

**Q: 音轨的 notes 很长，在 ACML 文件中怎么换行？**

A: 在行末添加 `+` 即可续行：

```acml
notes = C4:q:mf,E4:q:mf,G4:q:mf, +
       C4:q:mf,E4:q:mf,G4:q:mf, +
       D4:q:mf,F4:q:mf,A4:q:mf,D5:q:mf
```

`+` 后的空格和续行的前导空白会被自动去除，内容直接拼接。
详⻅ [第 10 章 行续接](#10-行续接line-continuation)。

**Q: 提示 "project xxx not found. Did you mean to run 'init' first?"**

A: 使用 `compile` 代替手动 `init` + `track add` + `generate`。
compile 会自动创建项目和生成音频。

**Q: 一个鼓音轨可以同时播放 kick 和 snare 吗？**

A: 可以。鼓的扩展音符用逗号分隔响应的鼓点：
`notes = K:q:mf,S:q:mf,K:q:mf,S:q:mf`
这是顺序播放。如需同时发声，创建两条鼓音轨。

**Q: 如何让音轨重复多次？**

A: 使用 `loops` 属性：在 ACML 中添加 `loops = 4`，或在 CLI 中使用 `--loops 4`。
音轨的内容（notes 或 pattern）会自动重复指定次数。

**Q: parallel 和 serial 模式有什么区别？**

A: `parallel`（默认）是所有音轨从 0 秒同时播放、叠加混合。`serial` 是音轨按顺序串联播放——前一个播完后一个才开始。两者可混用，详见[音轨定义-播放模式](#播放模式)。

**Q: 鼓点音符可以省略力度吗？**

A: 可以。省略力度时自动沿用上一个鼓点的力度值：
```
notes = K:q:f,S:q,K:q,S:q    # S 和第二个 K 的力度沿用 f (0.8)
```

**Q: 如何导出 MIDI 文件？**

A: 在 `compile` 或 `generate` 命令中使用 `--midi 文件名.mid` 选项。
MIDI 文件会输出到 `output/` 目录。鼓点自动映射到 GM 标准鼓通道（通道 10）。

使用 `--prowav` 可一步完成编译 + MIDI 导出 + FluidSynth 高质量 WAV 渲染。

**Q: 如何用 FluidSynth 渲染高质量 WAV？**

A: 两种方式：

1. 一键渲染：`python cli.py compile song.acml --prowav`
2. 分步渲染：先导出 MIDI（`--midi`），再用 `midi2wav` 命令

```bash
# 方式一：一步到位
python cli.py compile song.acml --prowav --loop 1

# 方式二：分步操作
python cli.py compile song.acml --midi song.mid
python cli.py midi2wav output/song.mid --output output/song_final.wav
```

前置要求：
- 安装 FluidSynth（`choco install fluidsynth` 或从官网下载）
- 下载 SoundFont 文件（如 FluidR3_GM.sf2），放置到 `~/.opencode/`

**Q: FM 合成器的 ratio 和 index 怎么调？**

A: ratio 控制调制波频率（整数=谐波，非整数=非谐波/金属感），index 控制调制深度（越大越亮/刺耳）。经典音色参考：
- 电钢：ratio=2, index=3（默认）
- 钟声：ratio=1, index=5
- 贝斯：ratio=0.5, index=2
- 金属擦片：ratio=1.4, index=8

**Q: Wavetable 支持哪些波形？**

A: 预制波形：`saw`、`square`、`triangle`、`sine`。也支持逗号分隔的自定义值。不指定时默认用 `saw`。

**Q: 采样支持立体声 WAV 吗？**

A: 支持。立体声或多声道 WAV 会自动混合为单声道后处理。

**Q: 如何让旋律自动生成和声？**

A: 在音轨上设置 `harmony = 3`（三度上）、`harmony = 5`（五度上）或 `harmony = octave`（八度上）。系统自动在每个旋律音上叠加和声。

**Q: 如何分析已有旋律的和弦进行？**

A: 使用 `analyze` 子命令：`acm analyze 项目名`。系统会按小节分析并推荐和弦。

**Q: 如何自定义项目和输出目录？**

A: 使用全局选项 `--project-dir` 和 `--output-dir`，或设置环境变量
`ACM_PROJECT_DIR` 和 `ACM_OUTPUT_DIR`。默认分别为 `projects/` 和 `output/`。
