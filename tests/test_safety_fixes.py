"""补充测试：覆盖 v0.8.6 安全修复和健壮性修复。"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

sys.path.insert(0, str(ROOT / "scripts"))


class FillTemplateFallbackTests(unittest.TestCase):
    """P1-1: fill_template 仅在所有占位符缺失时才使用 fallback。"""

    def setUp(self):
        from build_prompts import fill_template
        self.fill_template = fill_template

    def test_all_missing_uses_fallback(self):
        """所有占位符都缺失时，整体替换为 fallback。"""
        result = self.fill_template("{a} and {b}", {}, fallback="default text")
        self.assertEqual(result, "default text")

    def test_partial_missing_keeps_filled_values(self):
        """部分占位符有值时，不使用 fallback，保留已有值。"""
        result = self.fill_template(
            "{game_name} featuring {main_character}",
            {"game_name": "TestGame", "main_character": ""},
            fallback="fallback text",
        )
        # game_name 有值，不应整体替换为 fallback
        self.assertIn("TestGame", result)
        self.assertNotEqual(result, "fallback text")

    def test_one_of_two_filled_no_fallback(self):
        """两个占位符中一个有值，不触发 fallback。"""
        result = self.fill_template(
            "{game_name} in {key_scene}",
            {"game_name": "MyGame", "key_scene": ""},
            fallback="generic scene",
        )
        self.assertIn("MyGame", result)
        self.assertNotEqual(result, "generic scene")

    def test_all_filled_no_fallback(self):
        """所有占位符都有值时，正常填充。"""
        result = self.fill_template(
            "{game_name} in {key_scene}",
            {"game_name": "MyGame", "key_scene": "forest"},
            fallback="generic scene",
        )
        self.assertEqual(result, "MyGame in forest")


class FetchUrlSafetyTests(unittest.TestCase):
    """P2-3: fetch_url.py URL scheme 白名单和内网过滤。"""

    def setUp(self):
        from fetch_url import validate_url
        self.validate_url = validate_url

    def test_reject_file_scheme(self):
        err = self.validate_url("file:///etc/passwd")
        self.assertIsNotNone(err)
        self.assertIn("scheme", err)

    def test_reject_ftp_scheme(self):
        err = self.validate_url("ftp://example.com/data.csv")
        self.assertIsNotNone(err)
        self.assertIn("scheme", err)

    def test_allow_https(self):
        err = self.validate_url("https://example.com/page")
        self.assertIsNone(err)

    def test_allow_http(self):
        err = self.validate_url("http://example.com/page")
        self.assertIsNone(err)

    def test_reject_localhost(self):
        err = self.validate_url("http://127.0.0.1/admin")
        self.assertIsNotNone(err)
        self.assertIn("内网", err)

    def test_reject_metadata_endpoint(self):
        err = self.validate_url("http://169.254.169.254/latest/meta-data/")
        self.assertIsNotNone(err)
        self.assertIn("内网", err)

    def test_reject_private_10(self):
        err = self.validate_url("http://10.0.0.1/internal")
        self.assertIsNotNone(err)
        self.assertIn("内网", err)


class BuildHtmlBriefEmptyFileTests(unittest.TestCase):
    """P2-4: build_html_brief.py 空 report.md 不崩溃。"""

    def test_empty_report_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "report").mkdir()
            (project / "images").mkdir()
            (project / "project_state.json").write_text(
                json.dumps({"project_id": "test_001", "inputs": {}, "direction_judgment": {}}),
                encoding="utf-8",
            )
            # 创建空的 report.md
            (project / "report" / "report.md").write_text("", encoding="utf-8")
            (project / "images" / "prompts.jsonl").write_text("", encoding="utf-8")
            result = subprocess.run(
                [PYTHON, "scripts/build_html_brief.py", str(project)],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            brief_path = Path(result.stdout.strip())
            self.assertTrue(brief_path.exists())
            brief = brief_path.read_text(encoding="utf-8")
            # 使用 project_id 兜底作为标题
            self.assertIn("test_001", brief)


class AssetIndexJsonProtectionTests(unittest.TestCase):
    """P3-8: asset_index.py 非法 JSON 不 traceback。"""

    def test_invalid_json_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "index.jsonl"
            result = subprocess.run(
                [PYTHON, "scripts/asset_index.py", "add", str(index_path), "--record", "not valid json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("不是合法 JSON", result.stderr)
            # 不应生成文件
            self.assertFalse(index_path.exists())

    def test_valid_json_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            index_path = Path(tmp) / "index.jsonl"
            result = subprocess.run(
                [PYTHON, "scripts/asset_index.py", "add", str(index_path),
                 "--record", json.dumps({"name": "test.png", "type": "image"})],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertTrue(index_path.exists())
            content = index_path.read_text(encoding="utf-8").strip()
            record = json.loads(content)
            self.assertEqual(record["name"], "test.png")
            self.assertIn("created_at", record)


class FfmpegConcatTests(unittest.TestCase):
    """P2-6 + P3-7: ffmpeg_concat.py 路径转义和临时文件清理。"""

    def test_dry_run_escapes_single_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            # 创建含单引号的文件名
            video = Path(tmp) / "it's_a_test.mp4"
            video.write_bytes(b"\x00")
            result = subprocess.run(
                [PYTHON, "scripts/ffmpeg_concat.py",
                 "--inputs", str(video),
                 "--output", str(Path(tmp) / "out.mp4"),
                 "--dry-run"],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            # 确认单引号被正确转义
            self.assertIn("'\\''", result.stdout)


class GenVideoProviderTests(unittest.TestCase):
    """P3-9: gen_video_seedance.py --provider 参数与降级逻辑一致。"""

    def test_explicit_provider_without_env_var(self):
        with tempfile.TemporaryDirectory() as tmp:
            storyboard = Path(tmp) / "storyboard.md"
            storyboard.write_text("# 分镜\n", encoding="utf-8")
            # 显式传 --provider seedance，不设置 VIDEO_PROVIDER 环境变量
            result = subprocess.run(
                [PYTHON, "scripts/gen_video_seedance.py",
                 "--storyboard", str(storyboard),
                 "--provider", "seedance"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                env={**__import__("os").environ, "VIDEO_PROVIDER": ""},
            )
            # 有 provider 时应该进入真实执行路径（报 adapter 未安装），而非降级
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("尚未安装 adapter", result.stderr)


class StateVersionTests(unittest.TestCase):
    """P1-2: state.py 版本号与 SKILL.md 一致。"""

    def test_skill_version_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [PYTHON, "scripts/state.py", "init", "--workspace", tmp, "--project-id", "ver_test"],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            state_path = Path(result.stdout.strip())
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["skill_version"], "0.8.5")


if __name__ == "__main__":
    unittest.main()
