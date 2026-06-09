# ACM 编曲工具 v0.5.0

CLI 编曲软件 — 从 ACML 标记文件编译音乐，支持 MIDI 导出和 FluidSynth 高质量 WAV 渲染。

```bash
# 一步到位
python cli.py compile samples/acm.acml --prowav --loop 1
```

## 安装

```bash
pip install -e .

# 可选加速（numpy）
pip install -e ".[accelerate]"

# 可选 GPU 加速（cupy，需 CUDA 12.x）
pip install -e ".[cuda]"
```

Python >= 3.10，无硬性依赖（numpy/cupy 可选）。

## 快速开始

```bash
# 编译 ACML 并渲染高质量 WAV（一步到位）
python cli.py compile samples/acm.acml --prowav --loop 1

# 只导出 WAV + MIDI
python cli.py compile samples/acm.acml --midi output/song.mid

# 查看所有子命令
python cli.py --help
```

也可通过安装后的入口使用：
```bash
pip install -e .
acm compile samples/acm.acml --prowav
```

## FluidSynth 设置（可选，用于 prowav / midi2wav）

```bash
# Windows
choco install fluidsynth

# macOS
brew install fluid-synth

# Linux
sudo apt install fluidsynth
```

下载 SoundFont（如 FluidR3_GM.sf2）放置到 `~/.opencode/`。

## 文档

| 文档 | 说明 |
|------|------|
| `docs/acml-format.md` | ACML 标记语言完整参考 |
| `docs/cli-reference.md` | CLI 命令参考手册 |

## 功能

| 功能 | 说明 |
|------|------|
| ACML 编译 | 声明式标记语言 → 一键生成 WAV |
| MIDI 导出 | GM 标准，含鼓映射、程序变更、串行/并行模式 |
| `--prowav` | 编译 + MIDI + FluidSynth 高质量 WAV 一条龙 |
| `midi2wav` | 单独将 MIDI 渲染为 WAV |
| 乐器 | piano, guitar, bass, sawtooth, organ, bell, strings, brass, pad, lead, fm, wavetable, sample, trumpet, tuba, drums |
| 鼓点 | K(底鼓), S(军鼓), H(闭镲), O(开镲), T(桶鼓) |
| 和弦 | 17 种类型 + 自动和声 + 和弦推荐 |
| FM 合成 | 可调 ratio/index |
| 波形表 | saw / square / triangle / sine / 自定义 |
| 采样回放 | WAV 加载 + 变调 |
| 模式 | parallel（同时）/ serial（串行）+ 全局循环 |
| 效果 | 混响 / 延迟 / 合唱 |
| 紧凑标记 | `D5qf` → `D5:q:f`，节省 token |
| GPU 加速 | 可选 cupy 支持 |

## 项目结构

```
├── cli.py          CLI 入口
├── composer.py     核心合成引擎
├── acml.py         ACML 解析器
├── track.py        音轨数据类
├── pyproject.toml
├── README.md
├── docs/
│   ├── acml-format.md    ACML 语言参考
│   └── cli-reference.md  CLI 命令参考
├── samples/
│   └── acm.acml          示例乐曲
├── tests/                 162 项测试
├── projects/              项目 JSON 文件
└── output/                成品音频
```

## 测试

```bash
python -m pytest tests/ -v
```
