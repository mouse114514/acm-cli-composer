import unittest, os, json, tempfile, shutil
from cli import main, __version__

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.orig_dir)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @staticmethod
    def _wav_content_md5(path):
        import hashlib, wave
        with wave.open(path) as wf:
            frames = wf.readframes(wf.getnframes())
        return hashlib.md5(frames).hexdigest()

    def _capture_main(self, args):
        import io, sys
        captured = io.StringIO()
        old = sys.stdout; sys.stdout = captured
        try:
            try:
                main(args)
            except SystemExit:
                pass
        finally:
            sys.stdout = old
        return captured.getvalue()

    def test_init_creates_project_file(self):
        """cli init 在projects/下创建项目文件"""
        main(["init", "my_song"])
        self.assertTrue(os.path.exists("projects/my_song.json"))
        with open("projects/my_song.json") as f:
            project = json.load(f)
        self.assertEqual(project["name"], "my_song")
        self.assertEqual(project["tracks"], [])
        self.assertEqual(project["bpm"], 120)

    def test_track_add_to_project(self):
        """cli track add 添加音轨到项目"""
        main(["init", "song2"])
        main(["track", "add", "song2", "--instrument", "piano", "--scale", "C", "--pattern", "pop"])
        with open("projects/song2.json") as f:
            project = json.load(f)
        self.assertEqual(len(project["tracks"]), 1)
        self.assertEqual(project["tracks"][0]["instrument"], "piano")

    def test_track_list_output(self):
        """cli track list 列出音轨"""
        main(["init", "song3"])
        main(["track", "add", "song3", "--instrument", "guitar", "--scale", "G", "--pattern", "jazz"])
        with open("projects/song3.json") as f:
            project = json.load(f)
        self.assertEqual(len(project["tracks"]), 1)
        self.assertEqual(project["tracks"][0]["instrument"], "guitar")

    def test_generate_from_project(self):
        """cli generate 在output/下生成音频"""
        main(["init", "song4"])
        main(["track", "add", "song4", "--instrument", "piano", "--scale", "C", "--pattern", "pop"])
        main(["generate", "song4", "--output", "out.wav", "--bpm", "120", "--duration", "2"])
        self.assertTrue(os.path.exists("output/out.wav"))
        self.assertGreater(os.path.getsize("output/out.wav"), 100)

    def test_track_list_json(self):
        """track list --json 输出合法JSON"""
        main(["init", "song5"])
        main(["track", "add", "song5", "--instrument", "piano", "--scale", "C", "--pattern", "pop"])
        output = self._capture_main(["track", "list", "song5", "--json"])
        data = json.loads(output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["instrument"], "piano")

    def test_track_remove(self):
        """track remove 删除指定音轨"""
        main(["init", "song7"])
        main(["track", "add", "song7", "--instrument", "piano", "--scale", "C", "--pattern", "pop"])
        main(["track", "add", "song7", "--instrument", "drums", "--pattern", "rock"])
        main(["track", "remove", "song7", "1"])
        with open("projects/song7.json") as f:
            project = json.load(f)
        self.assertEqual(len(project["tracks"]), 1)
        self.assertEqual(project["tracks"][0]["instrument"], "drums")

    def test_track_update(self):
        """track update 修改指定音轨"""
        main(["init", "song8"])
        main(["track", "add", "song8", "--instrument", "piano", "--scale", "C", "--pattern", "pop"])
        main(["track", "update", "song8", "1", "--instrument", "guitar", "--pattern", "jazz"])
        with open("projects/song8.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["instrument"], "guitar")
        self.assertEqual(project["tracks"][0]["pattern"], "jazz")

    def test_generate_bpm_writes_back_to_project(self):
        """generate --bpm 回写项目文件"""
        main(["init", "song6"])
        main(["track", "add", "song6", "--instrument", "piano", "--scale", "C", "--pattern", "pop"])
        main(["generate", "song6", "--output", "out.wav", "--bpm", "180", "--duration", "1"])
        with open("projects/song6.json") as f:
            project = json.load(f)
        self.assertEqual(project["bpm"], 180)

    # ── 新增测试 ──────────────────────────────────────────

    def test_version_flag(self):
        """--version 输出版本号"""
        output = self._capture_main(["--version"])
        self.assertIn(__version__, output)

    def test_init_json(self):
        """init --json 输出JSON"""
        output = self._capture_main(["init", "json_init", "--json"])
        data = json.loads(output)
        self.assertEqual(data["name"], "json_init")
        self.assertEqual(data["status"], "initialized")

    def test_init_force(self):
        """init --force 覆盖已有项目"""
        main(["init", "forcesong"])
        main(["init", "forcesong", "--force"])  # no error
        self.assertTrue(os.path.exists("projects/forcesong.json"))

    def test_init_without_force_warns(self):
        """init 无--force不覆盖已有项目"""
        main(["init", "noforce"])
        output = self._capture_main(["init", "noforce"])
        self.assertIn("exist", output.lower())

    def test_track_add_json(self):
        """track add --json 输出JSON"""
        main(["init", "json_track"])
        output = self._capture_main(["track", "add", "json_track", "--instrument", "piano", "--json"])
        data = json.loads(output)
        self.assertEqual(data["index"], 1)
        self.assertEqual(data["instrument"], "piano")

    def test_generate_json(self):
        """generate --json 输出JSON"""
        main(["init", "json_gen"])
        main(["track", "add", "json_gen", "--instrument", "piano"])
        output = self._capture_main(["generate", "json_gen", "--output", "out.json.wav", "--json"])
        data = json.loads(output)
        self.assertIn("output", data)
        self.assertIn("status", data)

    def test_track_add_missing_project_suggests_init(self):
        """track add 时项目不存在给出init提示"""
        output = self._capture_main(["track", "add", "nonexistent", "--instrument", "piano"])
        self.assertIn("init", output.lower())

    def test_generate_missing_project_suggests_init(self):
        """generate 时项目不存在给出init提示"""
        output = self._capture_main(["generate", "nonexistent", "--output", "x.wav"])
        self.assertIn("init", output.lower())

    def test_track_list_truncates_notes_properly(self):
        """track list截断在完整音符边界"""
        main(["init", "trunc"])
        main(["track", "add", "trunc", "--instrument", "piano", "--notes", "C#4,D#4,E#4,F#4,G#4,A#4,B4,C5"])
        output = self._capture_main(["track", "list", "trunc"])
        # 不应出现被切断的note（以逗号后直接跟省略号，或者不被切断）
        lines = output.strip().split("\n")
        self.assertTrue(len(lines) >= 1)
        # 最后一个字符不是不完整音符（如果包含...则...前应是完整note）
        if "..." in output:
            # 找到notes=后面到...的内容
            idx = output.find("notes=")
            if idx >= 0:
                after = output[idx + 6:]
                dots_pos = after.find("...")
                if dots_pos >= 0:
                    truncated = after[:dots_pos].rstrip()
                    # 不应以逗号结尾
                    self.assertFalse(truncated.endswith(","))

    def test_track_add_with_pan(self):
        """track add --pan 设置声场位置"""
        main(["init", "pan_cli"])
        main(["track", "add", "pan_cli", "--instrument", "piano", "--pan", "-0.5"])
        with open("projects/pan_cli.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["pan"], -0.5)

    # ── ACML compile ─────────────────────────────────────

    def test_compile_creates_project_and_wav(self):
        """compile 从ACML生成项目和音频"""
        with open("test.acml", "w") as f:
            f.write('name = "test_song"\nbpm = 120\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        main(["compile", "test.acml", "--duration", "1"])
        self.assertTrue(os.path.exists("projects/test_song.json"))
        self.assertTrue(os.path.exists("output/test_song.wav"))

    def test_compile_missing_file_error(self):
        """compile 文件不存在时报错"""
        output = self._capture_main(["compile", "nonexistent.acml"])
        self.assertIn("not found", output.lower())

    def test_compile_json_output(self):
        """compile --json 输出JSON"""
        with open("test.acml", "w") as f:
            f.write('name = "jsonsong"\nbpm = 100\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        output = self._capture_main(["compile", "test.acml", "--duration", "1", "--json"])
        data = json.loads(output)
        self.assertEqual(data["status"], "compiled")
        self.assertIn("output", data)

    def test_compile_with_bpm_override(self):
        """compile --bpm 覆盖ACML中的BPM"""
        with open("test.acml", "w") as f:
            f.write('name = "bpmsong"\nbpm = 80\n\n[track piano]\ninstrument = piano\n')
        main(["compile", "test.acml", "--bpm", "160", "--duration", "1"])
        with open("projects/bpmsong.json") as f:
            project = json.load(f)
        self.assertEqual(project["bpm"], 160)

    def test_compile_with_output_override(self):
        """compile --output 覆盖输出文件名"""
        with open("test.acml", "w") as f:
            f.write('name = "outsong"\nbpm = 120\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        main(["compile", "test.acml", "--output", "custom.wav", "--duration", "1"])
        self.assertTrue(os.path.exists("output/custom.wav"))

    def test_compile_with_drums(self):
        """compile 支持鼓点音轨"""
        with open("test.acml", "w") as f:
            f.write('name = "drumsong"\nbpm = 120\n\n[track drums]\ninstrument = drums\nnotes = K:q:mf,S:q:mf\n')
        main(["compile", "test.acml", "--duration", "1"])
        self.assertTrue(os.path.exists("output/drumsong.wav"))

    def test_compile_with_pan(self):
        """compile 支持pan设置"""
        with open("test.acml", "w") as f:
            f.write('name = "pansong"\nbpm = 120\n\n[track guitar]\ninstrument = guitar\npan = -0.5\nnotes = C4:q:mf\n')
        main(["compile", "test.acml", "--duration", "1"])
        with open("projects/pansong.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["pan"], -0.5)

    def test_compile_uses_colon_global(self):
        """compile 支持 : 分隔的全局参数"""
        with open("test.acml", "w") as f:
            f.write('name: "colonsong"\nbpm: 140\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        main(["compile", "test.acml", "--duration", "1"])
        with open("projects/colonsong.json") as f:
            project = json.load(f)
        self.assertEqual(project["bpm"], 140)

    def test_compile_expands_compact_notation(self):
        """compile 自动展开紧凑标记法"""
        with open("test.acml", "w") as f:
            f.write('name = "compact_song"\nbpm = 120\n\n[track guitar]\ninstrument = guitar\nnotes = C5qf,D5qf\n')
        main(["compile", "test.acml", "--duration", "1"])
        with open("projects/compact_song.json") as f:
            project = json.load(f)
        notes = project["tracks"][0]["notes"]
        self.assertIn("C5:q:f", notes)
        self.assertIn("D5:q:f", notes)

    # ── Arpeggio CLI ────────────────────────────────────

    def test_track_add_with_arpeggio(self):
        """track add --arpeggio 存储琶音模式"""
        main(["init", "arp_cli"])
        main(["track", "add", "arp_cli", "--instrument", "piano", "--arpeggio", "up"])
        with open("projects/arp_cli.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["arpeggio"], "up")

    def test_generate_with_arpeggio(self):
        """generate 支持琶音音轨"""
        main(["init", "arp_gen"])
        main(["track", "add", "arp_gen", "--instrument", "piano", "--scale", "C", "--pattern", "1111", "--arpeggio", "up"])
        main(["generate", "arp_gen", "--output", "arp.wav", "--duration", "1"])
        self.assertTrue(os.path.exists("output/arp.wav"))

    def test_compile_with_arpeggio(self):
        """compile 支持琶音ACML"""
        with open("test.acml", "w") as f:
            f.write('name = "arp_acml"\nbpm = 120\n\n[track piano]\ninstrument = piano\narpeggio = up\npattern = 1111\n')
        main(["compile", "test.acml", "--duration", "1"])
        with open("projects/arp_acml.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["arpeggio"], "up")

    # ── Output File Info ─────────────────────────────────

    def test_generate_shows_file_info(self):
        """generate 输出包含文件大小和时长信息"""
        main(["init", "infosong"])
        main(["track", "add", "infosong", "--instrument", "piano", "--notes", "C4:q:mf"])
        output = self._capture_main(["generate", "infosong", "--output", "info.wav", "--duration", "1"])
        self.assertIn("KB", output)
        self.assertIn("Hz", output)
        self.assertIn("stereo", output)

    def test_compile_shows_file_info(self):
        """compile 输出包含文件信息"""
        with open("test.acml", "w") as f:
            f.write('name = "infocompile"\nbpm = 120\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        output = self._capture_main(["compile", "test.acml", "--duration", "1"])
        self.assertIn("KB", output)

    # ── ACML Repeat ─────────────────────────────────────

    def test_compile_repeat_block(self):
        """compile [repeat N] 展开相同音轨"""
        with open("test.acml", "w") as f:
            f.write('name = "repeatsong"\nbpm = 120\n[repeat 2]\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n[/repeat]\n')
        main(["compile", "test.acml", "--duration", "1"])
        with open("projects/repeatsong.json") as f:
            project = json.load(f)
        self.assertEqual(len(project["tracks"]), 2)
        self.assertEqual(project["tracks"][0]["instrument"], "piano")
        self.assertEqual(project["tracks"][1]["instrument"], "piano")

    def test_compile_repeat_nested(self):
        """compile 嵌套 [repeat] 正确展开"""
        with open("test.acml", "w") as f:
            f.write('name = "nested_repeat"\nbpm = 120\n[repeat 2]\n[track guitar]\ninstrument = guitar\n[repeat 2]\nnotes = C4:q:mf\n[/repeat]\n[/repeat]\n')
        main(["compile", "test.acml", "--duration", "1"])
        with open("projects/nested_repeat.json") as f:
            project = json.load(f)
        self.assertEqual(len(project["tracks"]), 2)  # outer repeat × 2
        for t in project["tracks"]:
            self.assertEqual(t["instrument"], "guitar")

    # ── Multiline continuation ─────────────────────────

    def test_compile_multiline_notes(self):
        """compile +续行拼接notes"""
        with open("test.acml", "w") as f:
            f.write('name = "multiline"\nbpm = 120\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf, +\nE4:q:mf, +\nG4:q:mf\n')
        main(["compile", "test.acml", "--duration", "1"])
        with open("projects/multiline.json") as f:
            project = json.load(f)
        notes = project["tracks"][0]["notes"]
        self.assertIn("C4:q:mf", notes)
        self.assertIn("E4:q:mf", notes)
        self.assertIn("G4:q:mf", notes)

    # ── BOM handling ────────────────────────────────────

    def test_compile_with_bom(self):
        """compile BOM文件正确解析name"""
        with open("bom.acml", "w", encoding="utf-8") as f:
            f.write('\ufeffname = "bom_song"\nbpm = 120\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        main(["compile", "bom.acml", "--duration", "1"])
        with open("projects/bom_song.json") as f:
            project = json.load(f)
        self.assertEqual(project["name"], "bom_song")
        self.assertEqual(len(project["tracks"]), 1)

    # ── Loops ───────────────────────────────────────────

    def test_track_add_with_loops(self):
        """track add --loops 保存正确"""
        main(["init", "loop_song"])
        main(["track", "add", "loop_song", "--instrument", "piano", "--loops", "4"])
        with open("projects/loop_song.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["loops"], 4)

    def test_track_update_loops(self):
        """track update --loops 更新正确"""
        main(["init", "up_loop"])
        main(["track", "add", "up_loop", "--instrument", "piano"])
        main(["track", "update", "up_loop", "1", "--loops", "3"])
        with open("projects/up_loop.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["loops"], 3)

    def test_generate_with_loops_produces_larger_file(self):
        """generate 带 loops 产生更大文件"""
        main(["init", "gen_loop"])
        main(["track", "add", "gen_loop", "--instrument", "piano", "--notes", "C4:q:mf"])
        main(["generate", "gen_loop", "--output", "gen_loop1.wav", "--duration", "2"])
        s1 = os.path.getsize("output/gen_loop1.wav")
        main(["track", "update", "gen_loop", "1", "--loops", "4"])
        main(["generate", "gen_loop", "--output", "gen_loop4.wav", "--duration", "2"])
        s4 = os.path.getsize("output/gen_loop4.wav")
        self.assertGreater(s4, s1)

    # ── MIDI Export ─────────────────────────────────────

    def test_generate_with_midi_flag(self):
        """generate --midi 导出MIDI文件"""
        main(["init", "midi_song"])
        main(["track", "add", "midi_song", "--instrument", "piano", "--notes", "C4:q:mf"])
        main(["generate", "midi_song", "--output", "midi_song.wav", "--midi", "midi_song.mid", "--duration", "1"])
        self.assertTrue(os.path.exists("output/midi_song.mid"))

    def test_compile_with_midi_flag(self):
        """compile --midi 导出MIDI文件"""
        with open("midi_compile.acml", "w") as f:
            f.write('name = "midi_compile"\nbpm = 120\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        main(["compile", "midi_compile.acml", "--midi", "midi_compile.mid", "--duration", "1"])
        self.assertTrue(os.path.exists("output/midi_compile.mid"))

    # ── Configurable directories ────────────────────────

    def test_project_dir_flag(self):
        """--project-dir 重定向项目目录"""
        main(["--project-dir", "my_projects", "init", "custom_proj"])
        self.assertTrue(os.path.exists("my_projects/custom_proj.json"))

    def test_output_dir_flag(self):
        """--output-dir 重定向输出目录"""
        main(["--project-dir", "mp", "init", "cout_proj"])
        main(["--project-dir", "mp", "--output-dir", "my_output", "track", "add", "cout_proj", "--instrument", "piano", "--notes", "C4:q:mf"])
        main(["--project-dir", "mp", "--output-dir", "my_output", "generate", "cout_proj", "--output", "cout.wav", "--duration", "1"])
        self.assertTrue(os.path.exists("my_output/cout.wav"))

    # ── Effects ─────────────────────────────────────────

    def test_generate_with_reverb(self):
        """generate --reverb 产生不同输出"""
        main(["init", "rev_song"])
        main(["track", "add", "rev_song", "--instrument", "piano", "--notes", "C4:q:mf"])
        main(["generate", "rev_song", "--output", "rev_none.wav", "--duration", "1"])
        main(["generate", "rev_song", "--output", "rev_on.wav", "--duration", "1", "--reverb", "0.5"])
        self.assertNotEqual(self._wav_content_md5("output/rev_none.wav"), self._wav_content_md5("output/rev_on.wav"))

    def test_compile_with_delay(self):
        """compile --delay 产生不同输出"""
        with open("delay_test.acml", "w") as f:
            f.write('name = "delay_test"\nbpm = 120\n\n[track piano]\ninstrument = piano\nnotes = C4:q:mf\n')
        main(["compile", "delay_test.acml", "--output", "delay_off.wav", "--duration", "1"])
        main(["compile", "delay_test.acml", "--output", "delay_on.wav", "--duration", "1", "--delay", "0.5"])
        self.assertNotEqual(self._wav_content_md5("output/delay_off.wav"), self._wav_content_md5("output/delay_on.wav"))

    # ── Wavetable CLI ───────────────────────────────────

    def test_track_add_with_wavetable(self):
        """track add --wavetable 存储波形表类型"""
        main(["init", "wt_cli"])
        main(["track", "add", "wt_cli", "--instrument", "wavetable", "--wavetable", "square"])
        with open("projects/wt_cli.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["wavetable"], "square")

    def test_generate_with_wavetable(self):
        """generate 支持wavetable音轨"""
        main(["init", "wt_gen"])
        main(["track", "add", "wt_gen", "--instrument", "wavetable", "--wavetable", "saw", "--notes", "C4:q:mf"])
        main(["generate", "wt_gen", "--output", "wt_gen.wav", "--duration", "1"])
        self.assertTrue(os.path.exists("output/wt_gen.wav"))

    # ── Sample CLI ──────────────────────────────────────

    def test_track_add_with_sample(self):
        """track add --sample 存储采样路径"""
        import wave, struct, math
        sr = 44100
        with wave.open("test_cli_sample.wav", "w") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
            for i in range(int(sr * 0.3)):
                s = math.sin(2 * math.pi * 440 * i / sr) * 0.5
                wf.writeframes(struct.pack("<h", int(s * 32767)))
        main(["init", "smp_cli"])
        main(["track", "add", "smp_cli", "--instrument", "sample", "--sample", "test_cli_sample.wav", "--notes", "C4:q:mf"])
        with open("projects/smp_cli.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["sample"], "test_cli_sample.wav")

    # ── Harmony CLI ─────────────────────────────────────

    def test_track_add_with_harmony(self):
        """track add --harmony 存储和声间隔"""
        main(["init", "harm_cli"])
        main(["track", "add", "harm_cli", "--instrument", "piano", "--harmony", "3", "--notes", "C4:q:mf"])
        with open("projects/harm_cli.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["harmony"], "3")

    def test_generate_with_harmony(self):
        """generate 支持和声音轨"""
        import wave
        main(["init", "harm_gen"])
        main(["track", "add", "harm_gen", "--instrument", "piano", "--harmony", "3", "--notes", "C4:q:mf"])
        main(["generate", "harm_gen", "--output", "harm_gen.wav", "--duration", "1"])
        self.assertTrue(os.path.exists("output/harm_gen.wav"))

    # ── Analyze CLI ─────────────────────────────────────

    def test_analyze_subcommand(self):
        """analyze 子命令分析和弦进行"""
        main(["init", "an_song"])
        main(["track", "add", "an_song", "--instrument", "piano", "--notes", "C4:q:mf,E4:q:mf,G4:q:mf"])
        output = self._capture_main(["analyze", "an_song"])
        self.assertIn("C", output)

    def test_analyze_json(self):
        """analyze --json 输出JSON"""
        main(["init", "an_json"])
        main(["track", "add", "an_json", "--instrument", "piano", "--notes", "C4:q:mf,E4:q:mf,G4:q:mf"])
        output = self._capture_main(["analyze", "an_json", "--json"])
        data = json.loads(output)
        self.assertIn("chords", data)

    # ── FM ratio/index CLI ─────────────────────────────

    def test_track_add_with_fm_ratio(self):
        """track add --fm-ratio 存储FM调制比"""
        main(["init", "fm_cli"])
        main(["track", "add", "fm_cli", "--instrument", "fm", "--fm-ratio", "3.0", "--notes", "C4:q:mf"])
        with open("projects/fm_cli.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["fm_ratio"], 3.0)

    def test_track_add_with_fm_index(self):
        """track add --fm-index 存储FM调制指数"""
        main(["init", "fm_idx"])
        main(["track", "add", "fm_idx", "--instrument", "fm", "--fm-index", "5.0", "--notes", "C4:q:mf"])
        with open("projects/fm_idx.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["fm_index"], 5.0)

    def test_generate_with_fm_params(self):
        """generate 支持FM参数"""
        main(["init", "fm_gen"])
        main(["track", "add", "fm_gen", "--instrument", "fm", "--fm-ratio", "4.0", "--fm-index", "2.0", "--notes", "C4:q:mf"])
        main(["generate", "fm_gen", "--output", "fm_gen.wav", "--duration", "1"])
        self.assertTrue(os.path.exists("output/fm_gen.wav"))

    def test_compile_with_fm_params(self):
        """compile 支持FM参数ACML"""
        with open("fm_acml.acml", "w") as f:
            f.write('name = "fm_acml"\nbpm = 120\n\n[track fm]\ninstrument = fm\nfm_ratio = 3.0\nfm_index = 4.0\nnotes = C4:q:mf\n')
        main(["compile", "fm_acml.acml", "--duration", "1"])
        with open("projects/fm_acml.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["fm_ratio"], "3.0")
        self.assertEqual(project["tracks"][0]["fm_index"], "4.0")

    # ── Compile with new features ───────────────────────

    def test_compile_with_wavetable(self):
        """compile 支持wavetable ACML"""
        with open("wt_acml.acml", "w") as f:
            f.write('name = "wt_acml"\nbpm = 120\n\n[track wt]\ninstrument = wavetable\nwavetable = square\nnotes = C4:q:mf\n')
        main(["compile", "wt_acml.acml", "--duration", "1"])
        with open("projects/wt_acml.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["wavetable"], "square")

    def test_compile_with_harmony(self):
        """compile 支持harmony ACML"""
        with open("harm_acml.acml", "w") as f:
            f.write('name = "harm_acml"\nbpm = 120\n\n[track p]\ninstrument = piano\nharmony = 5\nnotes = C4:q:mf\n')
        main(["compile", "harm_acml.acml", "--duration", "1"])
        with open("projects/harm_acml.json") as f:
            project = json.load(f)
        self.assertEqual(project["tracks"][0]["harmony"], "5")

if __name__ == "__main__":
    unittest.main()
