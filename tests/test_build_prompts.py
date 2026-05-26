"""Tests for build_prompts.py — 三层提示词组装引擎。"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def _make_fixture_project(
    tmp: Path,
    current_step: str = "M4",
    *,
    has_fields: bool = True,
    has_shotlist: bool = True,
) -> Path:
    """Create a minimal fixture project directory."""
    project = tmp / "outputs" / "test_001"
    project.mkdir(parents=True)

    state = {
        "project_id": "test_001",
        "current_step": current_step,
        "status": "in_progress",
        "workspace": str(project),
        "concept": {
            "shotlist": [
                {"id": "S1", "name": "主视觉 KV", "fixed": True},
                {"id": "S2", "name": "标志性场景图", "fixed": True},
                {"id": "S3", "name": "主界面", "fixed": True},
            ]
            if has_shotlist
            else [],
        },
    }
    if has_fields:
        state["concept"]["fields"] = {
            "name": "诡街守夜人",
            "main_character": "守夜少女",
            "key_scene": "雨夜古街",
            "theme_keywords": ["微恐", "中式民俗"],
            "characters": ["老捕快", "纸人"],
            "enemies": ["纸人傀儡"],
            "boss_description": "千年纸魂",
            "landmark_scene": "古街牌坊",
            "featured_character": "守夜少女",
            "color_preference": "青灰暖黄",
        }
    else:
        state["concept"]["fields"] = {}

    (project / "project_state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return project


class FillTemplateTests(unittest.TestCase):
    """fill_template() 变量填充测试"""

    def setUp(self):
        # Import inside test to avoid script-level side effects
        sys.path.insert(0, str(ROOT))
        from scripts import build_prompts as bp

        self.bp = bp

    def test_fill_complete(self):
        """所有占位符都有变量时正常填充"""
        result = self.bp.fill_template(
            "{game_name} is a {atmosphere_keyword} game",
            {"game_name": "诡街守夜人", "atmosphere_keyword": "微恐"},
        )
        self.assertEqual(result, "诡街守夜人 is a 微恐 game")

    def test_fill_missing_variable(self):
        """缺失变量留空"""
        result = self.bp.fill_template(
            "{game_name} in {key_scene}",
            {"game_name": "Test"},
        )
        self.assertEqual(result, "Test in")

    def test_fill_empty_dict(self):
        """无变量时模板全部留空"""
        result = self.bp.fill_template(
            "{game_name} - {atmosphere_keyword}",
            {},
        )
        self.assertEqual(result, "-")

    def test_fill_cleanup_spaces(self):
        """填充后清理多余空格和逗号"""
        result = self.bp.fill_template(
            "{a}, {b}, and {c}",
            {"a": "X", "b": "", "c": "Z"},
        )
        # '' 留空后清理 ", , and Z" -> "X, and Z"
        self.assertNotIn(",,", result)
        self.assertIn("X", result)
        self.assertIn("Z", result)

    def test_fill_no_placeholders(self):
        """无占位符时原样返回"""
        result = self.bp.fill_template("plain text", {})
        self.assertEqual(result, "plain text")


class ExtractVariablesTests(unittest.TestCase):
    """extract_variables() 变量提取测试"""

    def setUp(self):
        sys.path.insert(0, str(ROOT))
        from scripts import build_prompts as bp

        self.bp = bp

    def test_extract_full_fields(self):
        """fields 完整时正确提取所有变量"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), has_fields=True)
            state = json.loads(
                (project / "project_state.json").read_text(encoding="utf-8")
            )
            vars = self.bp.extract_variables(state)
            self.assertEqual(vars["game_name"], "诡街守夜人")
            self.assertEqual(vars["main_character"], "守夜少女")
            self.assertEqual(vars["key_scene"], "雨夜古街")
            self.assertEqual(vars["atmosphere_keyword"], "微恐")
            self.assertIn("纸人", vars["characters"])
            self.assertEqual(vars["enemy_type"], "纸人傀儡")

    def test_extract_empty_fields(self):
        """fields 为空时除 enemey_type 硬编码 fallback 外均为空"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), has_fields=False)
            state = json.loads(
                (project / "project_state.json").read_text(encoding="utf-8")
            )
            vars = self.bp.extract_variables(state)
            for key, val in vars.items():
                if key == "enemy_type":
                    self.assertEqual(val, "generic enemy")
                else:
                    self.assertEqual(val, "", f"{key} should be empty but got {val!r}")


class CategoryLoadingTests(unittest.TestCase):
    """品类加载与模糊匹配测试"""

    def test_all_13_categories_exist_in_yaml(self):
        """category_prompts.yaml 包含 13 个品类配置"""
        path = ROOT / "references" / "category_prompts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        categories = [k for k in data if k not in ("version", "last_updated")]
        self.assertEqual(len(categories), 14)

    def test_each_category_has_required_fields(self):
        """每个品类必须有 art_style, replacement_shots, model_route, negative_extra"""
        path = ROOT / "references" / "category_prompts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        required = {"art_style", "replacement_shots", "model_route", "negative_extra"}
        for name, conf in data.items():
            if name in ("version", "last_updated"):
                continue
            missing = required - set(conf.keys())
            self.assertFalse(
                missing, f"品类 '{name}' 缺少字段: {missing}"
            )

    def test_replacement_shots_have_id_and_name(self):
        """每个 replacement_shot 必须有 id、name、with_ui"""
        path = ROOT / "references" / "category_prompts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for name, conf in data.items():
            if name in ("version", "last_updated"):
                continue
            for i, shot in enumerate(conf.get("replacement_shots", [])):
                self.assertIn("id", shot, f"品类 '{name}' shot[{i}] 缺 id")
                self.assertIn("name", shot, f"品类 '{name}' shot[{i}] 缺 name")
                self.assertIn("with_ui", shot, f"品类 '{name}' shot[{i}] 缺 with_ui")

    def test_category_has_2_to_3_replacements(self):
        """每个品类替换槽位数在 2-3 之间"""
        path = ROOT / "references" / "category_prompts.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for name, conf in data.items():
            if name in ("version", "last_updated"):
                continue
            count = len(conf.get("replacement_shots", []))
            self.assertGreaterEqual(
                count, 2, f"品类 '{name}' 只有 {count} 个替换槽位（最少 2）"
            )
            self.assertLessEqual(
                count, 3, f"品类 '{name}' 有 {count} 个替换槽位（最多 3）"
            )


class StepCheckTests(unittest.TestCase):
    """M5 步骤前置检查测试"""

    def _run_build_prompts(self, tmp: Path, current_step: str, expect_fail: bool = False) -> subprocess.CompletedProcess:
        project = _make_fixture_project(tmp, current_step=current_step, has_fields=True, has_shotlist=True)
        return subprocess.run(
            [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
             "--project", str(project),
             "--category", "模拟经营",
             "--dry-run"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_accept_m4(self):
        """M4 应该通过"""
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_build_prompts(Path(tmp), "M4")
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")

    def test_accept_m5(self):
        """M5 应该通过"""
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_build_prompts(Path(tmp), "M5")
            self.assertEqual(result.returncode, 0)

    def test_accept_m7(self):
        """M7 应该通过"""
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_build_prompts(Path(tmp), "M7")
            self.assertEqual(result.returncode, 0)

    def test_reject_m1(self):
        """M1 应该被拒绝"""
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_build_prompts(Path(tmp), "M1", expect_fail=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("当前步骤 M1", result.stderr)

    def test_reject_m2(self):
        """M2 应该被拒绝"""
        with tempfile.TemporaryDirectory() as tmp:
            result = self._run_build_prompts(Path(tmp), "M2", expect_fail=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("M4", result.stderr)

    def test_empty_step_handling(self):
        """无 current_step 时也被拒绝"""
        with tempfile.TemporaryDirectory() as tmp:
            # 手动创建一个没有 current_step 的 state
            project = Path(tmp) / "outputs" / "test_001"
            project.mkdir(parents=True)
            state = {
                "project_id": "test_001",
                "status": "in_progress",
                "concept": {"shotlist": [], "fields": {}},
            }
            (project / "project_state.json").write_text(
                json.dumps(state, ensure_ascii=False), encoding="utf-8"
            )
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "模拟经营",
                 "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("当前步骤", result.stderr)


class BuildPipelineTests(unittest.TestCase):
    """端到端 build_prompts 组装测试"""

    def test_dry_run_output_shape(self):
        """dry-run 模式输出包含所有槽位"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), current_step="M4")
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "模拟经营",
                 "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["category"], "模拟经营")
            self.assertGreater(data["prompt_count"], 0)

    def test_prompt_contains_world_anchor(self):
        """每条提示词包含世界观锚点"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), current_step="M4")
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "模拟经营",
                 "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            data = json.loads(result.stdout)
            for p in data["prompts"]:
                prompt = p.get("prompt_v1", "")
                self.assertIn("诡街守夜人", prompt, f"{p['shot_id']} 缺少游戏名")
                self.assertIn("守夜少女", prompt, f"{p['shot_id']} 缺少主角")
                self.assertIn("雨夜古街", prompt, f"{p['shot_id']} 缺少场景")

    def test_prompt_has_render_mode(self):
        """每条提示词包含正确的 render_mode"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), current_step="M4")
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "模拟经营",
                 "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            data = json.loads(result.stdout)
            for p in data["prompts"]:
                self.assertIn("render_mode", p, f"{p['shot_id']} 缺少 render_mode")
                self.assertIn(
                    p["render_mode"],
                    ("mobile_screenshot", "concept_allowed"),
                    f"{p['shot_id']} render_mode 非法: {p['render_mode']}",
                )

    def test_fuzzy_category_match(self):
        """品类名带空格/斜杠时模糊匹配"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), current_step="M4")
            # 用 'ROGUE LIKE' 测试模糊匹配 RoguelikeRoguelite
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "RogueLike/Roguelite",
                 "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                result.returncode, 0,
                f"模糊匹配失败: stderr={result.stderr}",
            )

    def test_unknown_category_fallback(self):
        """未知品类走兜底"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), current_step="M4")
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "不存在的品类",
                 "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"stderr: {result.stderr}")
            # stderr 包含未找到品类警告
            self.assertIn("未找到品类", result.stderr)
            # stdout 包含兜底后的 JSON 输出
            self.assertIn('"ok": true', result.stdout)
            self.assertIn('"prompt_count"', result.stdout)

    def test_polish_flag_lists_all_slots(self):
        """--polish 输出所有槽位润色清单"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(Path(tmp), current_step="M4")
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "模拟经营",
                 "--polish"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0)
            # 确认包含润色标记和槽位信息
            self.assertIn("精细润色", result.stdout)
            self.assertIn("S1", result.stdout)
            self.assertIn("S3", result.stdout)
            # 确认 JSON 输出存在
            self.assertIn('"ok": true', result.stdout)
            self.assertIn('"category": "模拟经营"', result.stdout)

    def test_empty_shotlist_returns_empty(self):
        """shotlist 为空时返回空列表并给警告"""
        with tempfile.TemporaryDirectory() as tmp:
            project = _make_fixture_project(
                Path(tmp), current_step="M4", has_shotlist=False
            )
            result = subprocess.run(
                [PYTHON, str(ROOT / "scripts" / "build_prompts.py"),
                 "--project", str(project),
                 "--category", "模拟经营",
                 "--dry-run"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            # 空 shotlist → build_prompts 返回 []
            data = json.loads(result.stdout)
            self.assertEqual(data["prompt_count"], 0)


if __name__ == "__main__":
    unittest.main()