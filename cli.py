import argparse, json, os, wave
from track import Track
from composer import Composer

__version__ = "0.6.0"

def _file_info_str(path):
    size = os.path.getsize(path)
    size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024 * 1024 else f"{size / 1024:.1f} KB"
    with wave.open(path) as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        dur = frames / rate
    return f"({size_str}, {dur:.1f}s, {rate}Hz 16-bit stereo)"

def _truncate_notes(notes_str, max_len=60):
    if len(notes_str) <= max_len:
        return notes_str
    truncated = notes_str[:max_len]
    last_comma = truncated.rfind(",")
    if last_comma > 0:
        truncated = truncated[:last_comma]
    return truncated + "..."

def _resolve_dirs(args):
    proj_dir = getattr(args, "project_dir", None) or os.environ.get("ACM_PROJECT_DIR", "projects")
    out_dir = getattr(args, "output_dir", None) or os.environ.get("ACM_OUTPUT_DIR", "output")
    os.makedirs(proj_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    return proj_dir, out_dir

def main(argv=None):
    parser = argparse.ArgumentParser(description="CLI编曲软件 - 多步骤编曲工具")
    parser.add_argument("--version", action="version", version=f"acm {__version__}")
    parser.add_argument("--project-dir", default=None, help="项目目录 (默认: projects/, 环境变量: ACM_PROJECT_DIR)")
    parser.add_argument("--output-dir", default=None, help="输出目录 (默认: output/, 环境变量: ACM_OUTPUT_DIR)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="初始化新项目")
    init_parser.add_argument("name", help="项目名称")
    init_parser.add_argument("--force", action="store_true", help="覆盖已有项目")
    init_parser.add_argument("--json", action="store_true", help="JSON格式输出")

    track_parser = subparsers.add_parser("track", help="音轨管理")
    track_sub = track_parser.add_subparsers(dest="track_command", required=True)

    track_add = track_sub.add_parser("add", help="添加音轨")
    track_add.add_argument("project", help="项目名称")
    track_add.add_argument("--instrument", required=True, help="乐器音色")
    track_add.add_argument("--scale", default="C", help="音阶")
    track_add.add_argument("--pattern", default="pop", help="节奏模式")
    track_add.add_argument("--octave", type=int, default=4, help="八度")
    track_add.add_argument("--notes", default=None, help="音符序列: C4,D4,E4,F4 或紧凑标记 C5qf,D5qf(.=R:q); 扩展: C4:q:mf")
    track_add.add_argument("--volume", type=float, default=1.0, help="音量 0.0-1.0")
    track_add.add_argument("--kick", default=None, help="鼓点kick节奏型，如 10001000")
    track_add.add_argument("--snare", default=None, help="鼓点snare节奏型，如 00100010")
    track_add.add_argument("--hihat", default=None, help="鼓点hihat节奏型，如 11111111")
    track_add.add_argument("--durations", default=None, help="不等长时值，如 2,1,1,2 (三快两慢)")
    track_add.add_argument("--pan", type=float, default=0.0, help="声场位置 -1.0(左) ~ 1.0(右)")
    track_add.add_argument("--arpeggio", default=None, help="琶音模式: up/down/random/updown/downup")
    track_add.add_argument("--loops", type=int, default=1, help="循环次数 (默认: 1)")
    track_add.add_argument("--wavetable", default=None, help="波形表类型: saw/square/triangle/sine 或自定义值")
    track_add.add_argument("--sample", default=None, help="采样文件路径")
    track_add.add_argument("--sample-pitch", default=None, help="采样原始音高 (默认C4)")
    track_add.add_argument("--harmony", default=None, help="自动和声间隔: 3/5/6/octave/3below等")
    track_add.add_argument("--fm-ratio", type=float, default=None, help="FM调制比 (默认2.0)")
    track_add.add_argument("--fm-index", type=float, default=None, help="FM调制指数 (默认3.0)")
    track_add.add_argument("--mode", default="parallel", choices=["parallel", "serial"], help="播放模式: parallel=同时, serial=串行 (默认 parallel)")
    track_add.add_argument("--json", action="store_true", help="JSON格式输出")

    track_list = track_sub.add_parser("list", help="列出音轨")
    track_list.add_argument("project", help="项目名称")
    track_list.add_argument("--json", action="store_true", help="以JSON格式输出")

    track_remove = track_sub.add_parser("remove", help="删除音轨")
    track_remove.add_argument("project", help="项目名称")
    track_remove.add_argument("index", type=int, help="音轨序号（从1开始）")

    track_update = track_sub.add_parser("update", help="修改音轨")
    track_update.add_argument("project", help="项目名称")
    track_update.add_argument("index", type=int, help="音轨序号（从1开始）")
    track_update.add_argument("--instrument", default=None, help="乐器音色")
    track_update.add_argument("--scale", default=None, help="音阶")
    track_update.add_argument("--pattern", default=None, help="节奏模式")
    track_update.add_argument("--octave", type=int, default=None, help="八度")
    track_update.add_argument("--notes", default=None, help="音符序列: C4,E4,G4 或紧凑标记 C5qf,D5qf(.=R:q)")
    track_update.add_argument("--volume", type=float, default=None, help="音量")
    track_update.add_argument("--kick", default=None, help="鼓点kick")
    track_update.add_argument("--snare", default=None, help="鼓点snare")
    track_update.add_argument("--hihat", default=None, help="鼓点hihat")
    track_update.add_argument("--durations", default=None, help="不等长时值")
    track_update.add_argument("--pan", type=float, default=None, help="声场位置 -1.0(左) ~ 1.0(右)")
    track_update.add_argument("--arpeggio", default=None, help="琶音模式: up/down/random/updown/downup")
    track_update.add_argument("--loops", type=int, default=None, help="循环次数")
    track_update.add_argument("--wavetable", default=None, help="波形表类型")
    track_update.add_argument("--sample", default=None, help="采样文件路径")
    track_update.add_argument("--sample-pitch", default=None, help="采样原始音高")
    track_update.add_argument("--harmony", default=None, help="自动和声间隔")
    track_update.add_argument("--fm-ratio", type=float, default=None, help="FM调制比")
    track_update.add_argument("--fm-index", type=float, default=None, help="FM调制指数")

    gen_parser = subparsers.add_parser("generate", help="生成音频")
    gen_parser.add_argument("project", help="项目名称")
    gen_parser.add_argument("--output", required=True, help="输出音频文件名")
    gen_parser.add_argument("--bpm", type=int, default=120, help="BPM速度")
    gen_parser.add_argument("--duration", type=int, default=4, help="音乐时长（秒）")
    gen_parser.add_argument("--midi", default=None, help="导出MIDI文件路径（可选）")
    gen_parser.add_argument("--reverb", type=float, default=0.0, help="混响强度 0.0-1.0")
    gen_parser.add_argument("--delay", type=float, default=0.0, help="延迟强度 0.0-1.0")
    gen_parser.add_argument("--chorus", type=float, default=0.0, help="合唱强度 0.0-1.0")
    gen_parser.add_argument("--loop", type=int, default=None, help="整曲循环次数（serial 轨重复次数，默认 1）")
    gen_parser.add_argument("--json", action="store_true", help="JSON格式输出")
    gen_parser.add_argument("--trim", action=argparse.BooleanOptionalAction, default=True, help="裁剪末尾静音（默认开启）")

    compile_parser = subparsers.add_parser("compile", help="从ACML文件编译生成音乐")
    compile_parser.add_argument("file", help=".acml 文件路径")
    compile_parser.add_argument("--output", default=None, help="输出音频文件名")
    compile_parser.add_argument("--bpm", type=int, default=None, help="覆盖BPM")
    compile_parser.add_argument("--duration", type=int, default=None, help="音乐时长（秒），不指定则自动从音符计算")
    compile_parser.add_argument("--midi", default=None, help="导出MIDI文件路径（可选）")
    compile_parser.add_argument("--reverb", type=float, default=0.0, help="混响强度 0.0-1.0")
    compile_parser.add_argument("--delay", type=float, default=0.0, help="延迟强度 0.0-1.0")
    compile_parser.add_argument("--chorus", type=float, default=0.0, help="合唱强度 0.0-1.0")
    compile_parser.add_argument("--loop", type=int, default=None, help="整曲循环次数（serial 轨重复次数，默认 1）")
    compile_parser.add_argument("--json", action="store_true", help="JSON格式输出")
    compile_parser.add_argument("--prowav", action="store_true", help="编译后自动用 FluidSynth 将 MIDI 渲染为 WAV（高质量成品）")
    compile_parser.add_argument("--soundfont", default=None, help="prowav 使用的 SoundFont .sf2 文件路径")
    compile_parser.add_argument("--gain", type=float, default=1.0, help="prowav 增益倍率（默认 1.0）")
    compile_parser.add_argument("--trim", action=argparse.BooleanOptionalAction, default=True, help="裁剪末尾静音（默认开启）")

    analyze_parser = subparsers.add_parser("analyze", help="分析音轨并推荐和弦进行")
    analyze_parser.add_argument("project", help="项目名称")
    analyze_parser.add_argument("--track", type=int, default=1, help="音轨序号（从1开始，默认1）")
    analyze_parser.add_argument("--beats-per-bar", type=int, default=4, help="每小节拍数（默认4）")
    analyze_parser.add_argument("--json", action="store_true", help="JSON格式输出")

    midi_parser = subparsers.add_parser("midi2wav", help="用 FluidSynth 将 MIDI 渲染为 WAV（需安装 fluidsynth 和 SoundFont）")
    midi_parser.add_argument("input", help="输入的 .mid 文件路径")
    midi_parser.add_argument("--output", "-o", default=None, help="输出 .wav 文件路径（默认替换扩展名）")
    midi_parser.add_argument("--soundfont", "-s", default=None, help="SoundFont .sf2 文件路径")
    midi_parser.add_argument("--gain", "-g", type=float, default=1.0, help="增益倍率（默认 1.0）")
    midi_parser.add_argument("--sample-rate", "-r", type=int, default=44100, help="采样率（默认 44100）")

    args = parser.parse_args(argv)
    proj_dir, out_dir = _resolve_dirs(args)

    if args.command == "init":
        project_path = f"{proj_dir}/{args.name}.json"
        if os.path.exists(project_path) and not args.force:
            print(f"Error: project '{args.name}' already exists. Use --force to overwrite.")
            return
        project = {"name": args.name, "tracks": [], "bpm": 120}
        with open(project_path, "w") as f:
            json.dump(project, f, indent=2)
        if getattr(args, "json", False):
            print(json.dumps({"name": args.name, "status": "initialized"}))
        else:
            print(f"Project '{args.name}' initialized")

    elif args.command == "track":
        project_file = f"{proj_dir}/{args.project}.json"
        if not os.path.exists(project_file):
            print(f"Error: project '{args.project}' not found. Did you mean to run 'init' first?")
            return
        with open(project_file) as f:
            project = json.load(f)

        if args.track_command == "add":
            track = {
                "instrument": args.instrument,
                "scale": args.scale,
                "pattern": args.pattern,
                "octave": args.octave,
                "volume": args.volume,
            }
            if args.notes:
                track["notes"] = Composer.expand_compact_notes(args.notes)
            track["pan"] = args.pan
            track["loops"] = args.loops
            track["mode"] = getattr(args, "mode", "parallel")
            if args.arpeggio:
                track["arpeggio"] = args.arpeggio
            for dk in ("kick", "snare", "hihat", "durations", "wavetable", "sample", "sample_pitch", "harmony"):
                val = getattr(args, dk, None)
                if val:
                    track[dk] = val
            if args.fm_ratio is not None:
                track["fm_ratio"] = args.fm_ratio
            if args.fm_index is not None:
                track["fm_index"] = args.fm_index
            project["tracks"].append(track)
            idx = len(project["tracks"])
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
            if getattr(args, "json", False):
                print(json.dumps({"index": idx, "instrument": args.instrument, "status": "added"}))
            else:
                print(f"Track added: {args.instrument} ({args.scale}, {args.pattern}, pan={args.pan})")

        elif args.track_command == "list":
            if getattr(args, "json", False):
                print(json.dumps(project["tracks"], indent=2))
            elif not project["tracks"]:
                print("No tracks")
            else:
                for i, t in enumerate(project["tracks"], 1):
                    extra = ""
                    if t.get("notes"):
                        extra += f" notes={_truncate_notes(t['notes'])}"
                    if t.get("kick") or t.get("snare") or t.get("hihat"):
                        extra += f" drum_kick={t.get('kick','')} drum_snare={t.get('snare','')} drum_hihat={t.get('hihat','')}"
                    pan = t.get("pan", 0.0)
                    loops = t.get("loops", 1)
                    print(f"{i}. {t['instrument']} | scale={t['scale']} | pattern={t['pattern']} | octave={t['octave']} | volume={t['volume']} | pan={pan} | loops={loops}{extra}")

        elif args.track_command == "remove":
            idx = args.index - 1
            if 0 <= idx < len(project["tracks"]):
                removed = project["tracks"].pop(idx)
                with open(project_file, "w") as f:
                    json.dump(project, f, indent=2)
                print(f"Track {args.index} removed: {removed['instrument']}")
            else:
                print(f"Error: invalid track index {args.index}")

        elif args.track_command == "update":
            idx = args.index - 1
            if 0 <= idx < len(project["tracks"]):
                updates = {}
                for key in ("instrument", "scale", "pattern", "kick", "snare", "hihat", "durations", "pan", "arpeggio", "wavetable", "sample", "sample_pitch", "harmony", "fm_ratio", "fm_index"):
                    val = getattr(args, key, None)
                    if val is not None:
                        updates[key] = val
                notes_val = getattr(args, "notes", None)
                if notes_val is not None:
                    updates["notes"] = Composer.expand_compact_notes(notes_val)
                for key in ("octave", "volume"):
                    val = getattr(args, key, None)
                    if val is not None:
                        updates[key] = val
                loops_val = getattr(args, "loops", None)
                if loops_val is not None:
                    updates["loops"] = loops_val
                project["tracks"][idx].update(updates)
                with open(project_file, "w") as f:
                    json.dump(project, f, indent=2)
                print(f"Track {args.index} updated")
            else:
                print(f"Error: invalid track index {args.index}")

    elif args.command == "generate":
        project_file = f"{proj_dir}/{args.project}.json"
        if not os.path.exists(project_file):
            print(f"Error: project '{args.project}' not found. Did you mean to run 'init' first?")
            return
        with open(project_file) as f:
            project = json.load(f)
        if not project["tracks"]:
            print("Error: no tracks in project")
            return
        if args.bpm != project.get("bpm"):
            project["bpm"] = args.bpm
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)
        composer = Composer(bpm=args.bpm, duration=args.duration)
        for t in project["tracks"]:
            track = Track(
                instrument=t["instrument"],
                scale=t.get("scale", "C"),
                pattern=t.get("pattern", "pop"),
                octave=t.get("octave", 4),
                notes=t.get("notes"),
                volume=t.get("volume", 1.0),
                kick=t.get("kick"),
                snare=t.get("snare"),
                hihat=t.get("hihat"),
                durations=t.get("durations"),
                pan=t.get("pan", 0.0),
                arpeggio=t.get("arpeggio"),
                loops=t.get("loops", 1),
                wavetable=t.get("wavetable"),
                sample=t.get("sample"),
                sample_pitch=t.get("sample_pitch"),
                harmony=t.get("harmony"),
                fm_ratio=t.get("fm_ratio"),
                fm_index=t.get("fm_index"),
                mode=t.get("mode", "parallel"),
            )
            composer.add_track(track)
        output_path = args.output if ("/" in args.output or "\\" in args.output) else f"{out_dir}/{args.output}"
        midi_path = args.midi if args.midi and ("/" in args.midi or "\\" in args.midi) else (f"{out_dir}/{args.midi}" if args.midi else None)
        composer.generate(output_path, midi_path, args.reverb, args.delay, args.chorus, loop=args.loop or 1, trim=args.trim)
        if getattr(args, "json", False):
            result = {"output": args.output, "tracks": len(project["tracks"]), "status": "generated"}
            if midi_path:
                result["midi"] = args.midi
            print(json.dumps(result))
        else:
            info = _file_info_str(output_path)
            parts = [f"Generated: {output_path} {info}"]
            if midi_path:
                parts.append(f"MIDI:     {midi_path}")
            print("\n".join(parts))

    elif args.command == "compile":
        from acml import parse_acml

        if not os.path.exists(args.file):
            print(f"Error: file '{args.file}' not found")
            return

        name, bpm, acml_loop, tracks_data = parse_acml(args.file)
        if args.bpm is not None:
            bpm = args.bpm
        loop = args.loop if args.loop is not None else acml_loop

        project = {"name": name, "tracks": [], "bpm": bpm}

        for t in tracks_data:
            track = {}
            track["instrument"] = t.get("instrument", "piano")
            track["scale"] = t.get("scale", "C")
            track["pattern"] = t.get("pattern", "pop")
            track["octave"] = int(t.get("octave", 4))
            track["volume"] = float(t.get("volume", 1.0))
            track["pan"] = float(t.get("pan", 0.0))
            track["loops"] = int(t.get("loops", 1))
            track["mode"] = t.get("mode", "parallel")

            notes = t.get("notes")
            if notes:
                track["notes"] = Composer.expand_compact_notes(notes)

            for dk in ("kick", "snare", "hihat", "durations", "arpeggio", "wavetable", "sample", "sample_pitch", "harmony", "fm_ratio", "fm_index"):
                val = t.get(dk)
                if val:
                    track[dk] = val

            project["tracks"].append(track)

        project_path = f"{proj_dir}/{name}.json"
        with open(project_path, "w") as f:
            json.dump(project, f, indent=2)

        if not project["tracks"]:
            print("Error: no tracks defined in ACML file")
            return

        # 自动计算所需时长（基于扩展音符的拍数总和），仅当 --duration 未指定时
        if args.duration is not None:
            auto_duration = args.duration
        else:
            auto_duration = 4
            has_extended = False
            total_beats = 0.0
            serial_beats = 0.0
            for t in project["tracks"]:
                notes = t.get("notes")
                mode = t.get("mode", "parallel")
                loops = int(t.get("loops", 1))
                if notes and Composer._is_extended_notes(notes):
                    has_extended = True
                    track_beats = 0.0
                    note_str = ",".join([notes] * loops)
                    for expr in note_str.split(","):
                        expr = expr.strip()
                        if expr and ":" in expr:
                            parts = expr.split(":")
                            if len(parts) >= 2 and parts[1] and parts[1][0] in "whqesWHQES":
                                track_beats += Composer._parse_duration(parts[1])
                            else:
                                track_beats += 1.0
                        elif expr:
                            track_beats += 1.0
                    if mode == "serial":
                        serial_beats += track_beats
                    elif track_beats > total_beats:
                        total_beats = track_beats
            if has_extended:
                spb = 44100 * 60 / bpm
                parallel_secs = total_beats * spb / 44100
                serial_secs = serial_beats * loop * spb / 44100
                needed = max(parallel_secs, serial_secs) + 2
                auto_duration = int(needed) + 1

        composer = Composer(bpm=bpm, duration=auto_duration)
        for t in project["tracks"]:
            track_obj = Track(
                instrument=t["instrument"],
                scale=t.get("scale", "C"),
                pattern=t.get("pattern", "pop"),
                octave=t.get("octave", 4),
                notes=t.get("notes"),
                volume=t.get("volume", 1.0),
                kick=t.get("kick"),
                snare=t.get("snare"),
                hihat=t.get("hihat"),
                durations=t.get("durations"),
                pan=t.get("pan", 0.0),
                arpeggio=t.get("arpeggio"),
                loops=t.get("loops", 1),
                wavetable=t.get("wavetable"),
                sample=t.get("sample"),
                sample_pitch=t.get("sample_pitch"),
                harmony=t.get("harmony"),
                fm_ratio=t.get("fm_ratio"),
                fm_index=t.get("fm_index"),
                mode=t.get("mode", "parallel"),
            )
            composer.add_track(track_obj)

        output_name = args.output or f"{name}.wav"
        output_path = output_name if ("/" in output_name or "\\" in output_name) else f"{out_dir}/{output_name}"

        midi_path = None
        if args.midi:
            midi_path = args.midi if ("/" in args.midi or "\\" in args.midi) else f"{out_dir}/{args.midi}"
        elif getattr(args, "prowav", False):
            midi_name = os.path.splitext(output_name)[0] + ".mid"
            midi_path = midi_name if ("/" in midi_name or "\\" in midi_name) else f"{out_dir}/{midi_name}"

        composer.generate(output_path, midi_path, args.reverb, args.delay, args.chorus, loop=loop, trim=args.trim)

        if getattr(args, "prowav", False):
            import subprocess, shutil
            fluidsynth_path = shutil.which("fluidsynth")
            if not fluidsynth_path:
                print("Error: fluidsynth not found. Install it and try again.")
                return
            sf_path = args.soundfont
            if not sf_path:
                candidates = [
                    os.path.expanduser("~/.acm/default.sf2"),
                    os.path.expanduser("~/.acm/FluidR3_GM.sf2"),
                    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
                ]
                sf_path = next((p for p in candidates if os.path.exists(p)), None)
            if not sf_path or not os.path.exists(sf_path):
                print("Error: SoundFont not found. Use --soundfont or place one at ~/.acm/FluidR3_GM.sf2")
                return
            wav_output = os.path.splitext(midi_path)[0] + "_prowav.wav"
            cmd = [
                fluidsynth_path,
                "-F", wav_output,
                "-T", "wav",
                "-r", "44100",
                "-g", str(args.gain),
                sf_path,
                midi_path,
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                print(f"fluidsynth failed:\n{r.stderr}")
                return
            # Truncate prowav WAV to match requested duration
            if args.duration:
                import wave
                try:
                    wf = wave.open(wav_output, "rb")
                    nframes = wf.getnframes()
                    sr = wf.getframerate()
                    target_frames = int(args.duration * sr)
                    if target_frames < nframes:
                        frames = wf.readframes(target_frames)
                        wf.close()
                        wf = wave.open(wav_output, "wb")
                        wf.setnchannels(2)
                        wf.setsampwidth(2)
                        wf.setframerate(sr)
                        wf.writeframes(frames)
                    wf.close()
                except Exception:
                    pass
            size = os.path.getsize(wav_output)
            size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024 * 1024 else f"{size / 1024:.1f} KB"
            print(f"ProWAV:  {wav_output} ({size_str})")

        if getattr(args, "json", False):
            result = {
                "project": f"{name}.json",
                "output": output_name,
                "tracks": len(project["tracks"]),
                "bpm": bpm,
                "status": "compiled",
            }
            if midi_path:
                result["midi"] = args.midi
            print(json.dumps(result))
        else:
            info = _file_info_str(output_path)
            parts = [f"Project: {proj_dir}/{name}.json"]
            parts.append(f"Output:  {output_path} {info}")
            if midi_path:
                parts.append(f"MIDI:    {midi_path}")
            print("\n".join(parts))

    elif args.command == "analyze":
        project_file = f"{proj_dir}/{args.project}.json"
        if not os.path.exists(project_file):
            print(f"Error: project '{args.project}' not found. Did you mean to run 'init' first?")
            return
        with open(project_file) as f:
            project = json.load(f)
        if not project["tracks"]:
            print("Error: no tracks in project")
            return
        track_idx = args.track - 1
        if track_idx < 0 or track_idx >= len(project["tracks"]):
            print(f"Error: invalid track index {args.track}")
            return
        composer = Composer(bpm=project.get("bpm", 120))
        t = project["tracks"][track_idx]
        track_obj = Track(
            instrument=t["instrument"],
            scale=t.get("scale", "C"),
            pattern=t.get("pattern", "pop"),
            octave=t.get("octave", 4),
            notes=t.get("notes"),
            volume=t.get("volume", 1.0),
            pan=t.get("pan", 0.0),
            mode=t.get("mode", "parallel"),
        )
        composer.add_track(track_obj)
        chords = composer.analyze_chords(0, beats_per_bar=args.beats_per_bar)
        if getattr(args, "json", False):
            print(json.dumps({"track": args.track, "chords": chords, "status": "analyzed"}))
        else:
            print(f"Track {args.track} ({t['instrument']}): {' | '.join(chords)}")

    elif args.command == "midi2wav":
        import subprocess, shutil

        if not os.path.exists(args.input):
            print(f"Error: MIDI file '{args.input}' not found")
            return

        fluidsynth_path = shutil.which("fluidsynth")
        if not fluidsynth_path:
            print("Error: fluidsynth not found. Install it:\n"
                  "  macOS: brew install fluid-synth\n"
                  "  Ubuntu: sudo apt install fluidsynth\n"
                  "  Windows: 从 https://www.fluidsynth.org 下载，或装 TinySoundFont/VSamp 等替代方案\n"
                  "  也可在 Python 中: pip install pyfluidsynth")
            return

        sf_path = args.soundfont
        if not sf_path:
            # 查找常见 SoundFont 路径
            candidates = [
                os.path.expanduser("~/.acm/default.sf2"),
                "/usr/share/sounds/sf2/FluidR3_GM.sf2",
                "/usr/share/sounds/sf2/default.sf2",
                "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.sf2",
            ]
            sf_path = next((p for p in candidates if os.path.exists(p)), None)
        if not sf_path or not os.path.exists(sf_path):
            print(f"Error: SoundFont not found. Specify it with --soundfont or place one at ~/.acm/default.sf2")
            return

        output = args.output
        if not output:
            output = os.path.splitext(args.input)[0] + ".wav"

        cmd = [
            fluidsynth_path,
            "-F", output,
            "-T", "wav",
            "-r", str(args.sample_rate),
            "-g", str(args.gain),
            sf_path,
            args.input,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"fluidsynth failed:\n{r.stderr}")
            return
        size = os.path.getsize(output)
        size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024 * 1024 else f"{size / 1024:.1f} KB"
        print(f"Rendered: {output} ({size_str})")

if __name__ == "__main__":
    main()
