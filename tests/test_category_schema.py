"""Schema 校验测试 — 验证 YAML 配置的完整性和一致性。"""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class CategorySchemaTests(unittest.TestCase):
    """category_prompts.yaml 14 品类 schema 校验"""

    @classmethod
    def setUpClass(cls):
        path = ROOT / "references" / "category_prompts.yaml"
        cls.data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cls.categories = [
            (k, v) for k, v in cls.data.items()
            if k not in ("version", "last_updated")
        ]

    def test_14_categories_defined(self):
        """品类数量必须是 14"""
        self.assertEqual(len(self.categories), 14)

    def test_each_has_required_string_fields(self):
        """每个品类必须有 6 个字符串字段"""
        string_fields = {"art_style", "default_camera", "color_palette",
                         "ui_aesthetic", "negative_extra", "default_subject"}
        for name, conf in self.categories:
            missing = string_fields - set(conf.keys())
            self.assertFalse(missing, f"品类 '{name}' 缺少字符串字段: {missing}")
            for field in string_fields:
                val = conf.get(field, "")
                self.assertIsInstance(val, str,
                    f"品类 '{name}' 的 {field} 应为 str，实际为 {type(val).__name__}")
                self.assertGreater(len(val), 5,
                    f"品类 '{name}' 的 {field} 太短: '{val}'")

    def test_each_has_model_route(self):
        """每个品类必须有 model_route（含 primary, fallback, cfg_scale, denoising_strength）"""
        required_keys = {"primary", "fallback", "cfg_scale", "denoising_strength"}
        for name, conf in self.categories:
            self.assertIn("model_route", conf, f"品类 '{name}' 缺少 model_route")
            mr = conf["model_route"]
            missing = required_keys - set(mr.keys())
            self.assertFalse(missing, f"品类 '{name}' model_route 缺少: {missing}")
            self.assertIsInstance(mr["primary"], str)
            self.assertIsInstance(mr["cfg_scale"], (int, float))
            cfg = mr["cfg_scale"]
            self.assertGreaterEqual(cfg, 5.0)
            self.assertLessEqual(cfg, 12.0)

    def test_social_slot_is_bool(self):
        """social_slot_enabled 必须是 bool"""
        for name, conf in self.categories:
            self.assertIn("social_slot_enabled", conf,
                          f"品类 '{name}' 缺少 social_slot_enabled")
            self.assertIsInstance(conf["social_slot_enabled"], bool)

    def test_replacement_shots_have_all_fields(self):
        """每个 replacement_shot 必须包含 id, name, with_ui, composition, subject_template"""
        required = {"id", "name", "with_ui", "composition", "subject_template"}
        for name, conf in self.categories:
            shots = conf.get("replacement_shots", [])
            self.assertGreaterEqual(len(shots), 2,
                f"品类 '{name}' 只有 {len(shots)} 个替换槽位")
            for i, shot in enumerate(shots):
                missing = required - set(shot.keys())
                self.assertFalse(missing,
                    f"品类 '{name}' shot[{i}] 缺少: {missing}")
                self.assertIsInstance(shot["with_ui"], bool)
                self.assertIn(shot["id"], (f"S{7+i}" for i in range(3)),
                    f"品类 '{name}' shot[{i}] id '{shot['id']}' 格式错误")

    def test_shot_id_unique_within_category(self):
        """同一品类内 replacement_shot 的 id 唯一"""
        for name, conf in self.categories:
            ids = [s["id"] for s in conf.get("replacement_shots", [])]
            self.assertEqual(len(ids), len(set(ids)),
                f"品类 '{name}' 有重复 shot id: {ids}")

    def test_category_name_normalizable(self):
        """品类名不能包含空格或斜杠（模糊匹配需要）"""
        for name, _ in self.categories:
            self.assertNotIn(" ", name,
                f"品类名 '{name}' 含空格，模糊匹配会出问题")
            self.assertNotIn("/", name,
                f"品类名 '{name}' 含斜杠，模糊匹配会出问题")

    def test_negative_extra_includes_keywords(self):
        """negative_extra 至少包含 3 个关键词"""
        for name, conf in self.categories:
            extra = conf.get("negative_extra", "")
            keywords = [k.strip() for k in extra.split(",")]
            self.assertGreaterEqual(len(keywords), 3,
                f"品类 '{name}' negative_extra 只有 {len(keywords)} 个关键词")


class SlotSchemaTests(unittest.TestCase):
    """slot_prompts.yaml 槽位配置校验"""

    @classmethod
    def setUpClass(cls):
        path = ROOT / "references" / "slot_prompts.yaml"
        cls.data = yaml.safe_load(path.read_text(encoding="utf-8"))
        cls.slots = {k: v for k, v in cls.data.items()
                     if k not in ("version", "last_updated")}

    def test_slots_count(self):
        """固定槽位 6 个 + 可选 1 个 = 7 个"""
        self.assertEqual(len(self.slots), 7)

    def test_slots_s1_to_s6_present(self):
        """S1-S6 固定槽位都存在"""
        for i in range(1, 7):
            key = f"S{i}"
            self.assertIn(key, self.slots, f"缺少槽位 {key}")

    def test_s10_optional_present(self):
        """S10 可选槽位存在"""
        self.assertIn("S10", self.slots)

    def test_each_slot_has_required_fields(self):
        """每个槽位必须有 name, slot_type, with_ui, composition, subject_template"""
        required = {"name", "slot_type", "with_ui", "composition", "subject_template"}
        for sid, conf in self.slots.items():
            missing = required - set(conf.keys())
            self.assertFalse(missing, f"槽位 {sid} 缺少: {missing}")
            self.assertIsInstance(conf["with_ui"], bool)
            self.assertIn(conf["slot_type"], ("fixed", "optional"))

    def test_llm_polish_consistency(self):
        """S1/S2/S5 的 llm_polish 为 True"""
        for sid in ("S1", "S2", "S5"):
            self.assertTrue(self.slots[sid].get("llm_polish"),
                            f"{sid} 的 llm_polish 应为 True")
        for sid in ("S3", "S4", "S6", "S10"):
            self.assertFalse(self.slots[sid].get("llm_polish"),
                             f"{sid} 的 llm_polish 应为 False")

    def test_with_ui_consistency(self):
        """S1/S2 的 with_ui=False"""
        for sid in ("S1", "S2"):
            self.assertFalse(self.slots[sid]["with_ui"],
                             f"{sid} 的 with_ui 应为 False")
        for sid in ("S3", "S4", "S5", "S6", "S10"):
            self.assertTrue(self.slots[sid]["with_ui"],
                            f"{sid} 的 with_ui 应为 True")


class BaseSchemaTests(unittest.TestCase):
    """prompt_base.yaml 基础配置校验"""

    @classmethod
    def setUpClass(cls):
        path = ROOT / "references" / "prompt_base.yaml"
        cls.data = yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_world_context_present(self):
        """world_context 块必须存在且有 template, style, note"""
        wc = self.data.get("world_context", {})
        self.assertIn("template", wc)
        self.assertIn("style", wc)
        self.assertIn("note", wc)
        # template 至少包含一个占位符
        self.assertIn("{", wc["template"])

    def test_anchors_present(self):
        """anchors 必须有 with_ui_true 和 with_ui_false"""
        anchors = self.data.get("anchors", {})
        self.assertIn("with_ui_true", anchors)
        self.assertIn("with_ui_false", anchors)

    def test_negative_global_present(self):
        """negative_global 必须存在且非空"""
        ng = self.data.get("negative_global", "")
        self.assertGreater(len(ng), 50)

    def test_variable_schema_matches_extract_variables(self):
        """variable_schema 必须包含 extract_variables 返回的所有键"""
        expected = {
            "game_name", "main_character", "characters", "key_scene",
            "atmosphere_keyword", "enemy_type", "boss_description",
            "landmark_scene", "featured_character", "color_preference",
        }
        vs = set(self.data.get("variable_schema", {}).keys())
        missing = expected - vs
        extra = vs - expected
        self.assertFalse(missing, f"variable_schema 缺少: {missing}")
        self.assertFalse(extra, f"variable_schema 多余: {extra}")

    def test_fallback_config_present(self):
        """fallback 块必须存在"""
        fb = self.data.get("fallback", {})
        self.assertIn("missing_variable", fb)
        self.assertIn("missing_category", fb)
        self.assertIn("missing_reference", fb)


if __name__ == "__main__":
    unittest.main()