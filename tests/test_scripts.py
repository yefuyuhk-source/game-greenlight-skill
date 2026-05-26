import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class ScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [PYTHON, *args],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )

    def test_state_init_validate_summary_and_patch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_script("scripts/state.py", "init", "--workspace", tmp, "--project-id", "demo_001")
            state_path = Path(result.stdout.strip())
            self.assertTrue(state_path.exists())

            validate = self.run_script("scripts/state.py", "validate", str(state_path))
            self.assertEqual(validate.stdout.strip(), "OK")

            self.run_script(
                "scripts/state.py",
                "patch",
                str(state_path),
                "--step",
                "M1",
                "--patch",
                json.dumps({"inputs": {"theme": "赛博朋克"}, "current_step": "M2"}, ensure_ascii=False),
            )
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["inputs"]["theme"], "赛博朋克")
            self.assertEqual(state["current_step"], "M2")
            self.assertTrue(state_path.with_suffix(".json.bak").exists())

            summary = self.run_script("scripts/state.py", "summary", str(state_path))
            self.assertIn("当前步骤: M2", summary.stdout)

    def test_md_to_html_marks_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.md"
            target = Path(tmp) / "report.html"
            source.write_text("# 标题\n\n🟢【已证据支持】结论\n", encoding="utf-8")
            self.run_script("scripts/md_to_html.py", str(source), str(target))
            html = target.read_text(encoding="utf-8")
            self.assertIn("title-main", html)
            self.assertIn("标题", html)
            self.assertIn("tag tt", html)

    def test_md_to_html_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "scores.md"
            target = Path(tmp) / "scores.html"
            source.write_text("# 标题\n\n## 评分\n\n|候选|折算分|\n|---|---:|\n|A|8.2|\n|B|6.5|\n", encoding="utf-8")
            self.run_script("scripts/md_to_html.py", str(source), str(target))
            html = target.read_text(encoding="utf-8")
            self.assertIn("table-card", html)
            self.assertNotIn("chart-card", html)
            self.assertNotIn("bar-fill", html)

    def test_md_to_html_shot_cards_injection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "report.md"
            target = Path(tmp) / "report.html"
            prompts_file = Path(tmp) / "prompts.jsonl"
            source.write_text("# 标题\n\n## 关键画面\n\n{{SHOT_CARDS}}\n", encoding="utf-8")
            prompts_file.write_text(
                json.dumps({
                    "shot_id": "S1",
                    "name": "主界面",
                    "prompt_v1": "actual mobile game screenshot, test prompt",
                }, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self.run_script("scripts/md_to_html.py", str(source), str(target),
                            "--prompts", str(prompts_file))
            html = target.read_text(encoding="utf-8")
            self.assertIn("shot-card", html)
            self.assertIn("复制提示词", html)
            self.assertIn("actual mobile game screenshot, test prompt", html)

    def test_provider_scripts_degrade_without_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prompts = Path(tmp) / "prompts.jsonl"
            prompts.write_text(json.dumps({"shot_id": "S1", "prompt_v1": "test"}) + "\n", encoding="utf-8")
            image = self.run_script("scripts/gen_image.py", "--prompts", str(prompts), "--dry-run")
            self.assertIn("dry_run", image.stdout)

            # 不带 --dry-run 时降级
            image2 = self.run_script("scripts/gen_image.py", "--prompts", str(prompts))
            self.assertIn("未配置图像 provider", image2.stdout)

            storyboard = Path(tmp) / "storyboard.md"
            storyboard.write_text("# 分镜\n", encoding="utf-8")
            video = self.run_script("scripts/gen_video_seedance.py", "--storyboard", str(storyboard), "--dry-run")
            self.assertIn("未配置视频 provider", video.stdout)

    def test_list_outputs_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "outputs" / "demo_001"
            (project / "report").mkdir(parents=True)
            (project / "report" / "report.md").write_text("# report\n", encoding="utf-8")
            (project / "report" / "html_design_brief.md").write_text("# brief\n", encoding="utf-8")
            (project / "project_state.json").write_text("{}", encoding="utf-8")
            result = self.run_script("scripts/list_outputs.py", str(project), "--step", "M7", "--markdown")
            self.assertIn("report.md", result.stdout)
            self.assertIn("html_design_brief.md", result.stdout)
            self.assertIn("project_state.json", result.stdout)

    def test_build_html_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "outputs" / "demo_001"
            (project / "report").mkdir(parents=True)
            (project / "images").mkdir()
            (project / "project_state.json").write_text(
                json.dumps(
                    {
                        "project_id": "demo_001",
                        "inputs": {"theme": "微恐", "gameplay": "塔防", "art_style": "Q版"},
                        "direction_judgment": {"light": "yellow", "evidence_strength": "medium"},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (project / "report" / "report.md").write_text("# 诡街守夜人\n\n内容\n", encoding="utf-8")
            (project / "images" / "prompts.jsonl").write_text(
                json.dumps({"shot_id": "S1", "name": "主界面", "prompt_v1": "prompt"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            result = self.run_script("scripts/build_html_brief.py", str(project))
            brief_path = Path(result.stdout.strip())
            brief = brief_path.read_text(encoding="utf-8")
            self.assertIn("Modern Minimal Design Brief", brief)
            self.assertIn("只保留项目名称", brief)
            self.assertIn("诡街守夜人", brief)

    def test_check_design_backend_fallback_with_empty_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [PYTHON, "scripts/check_design_backend.py", "--json"],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
                env={"HOME": tmp},
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["backend"], "modern-minimal-html")
            self.assertTrue(data["modern_minimal_available"])
            self.assertIn("vendor", data["skill_path"])

    def test_check_design_backend_extra_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            skill = root / "modern-minimal-html"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: modern-minimal-html\n---\n", encoding="utf-8")
            result = self.run_script("scripts/check_design_backend.py", "--json", "--root", str(root))
            data = json.loads(result.stdout)
            self.assertEqual(data["backend"], "modern-minimal-html")
            self.assertTrue(data["skill_path"].endswith("modern-minimal-html/SKILL.md"))


if __name__ == "__main__":
    unittest.main()
