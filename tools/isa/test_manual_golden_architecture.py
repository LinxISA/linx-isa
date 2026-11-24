#!/usr/bin/env python3

from html import unescape
import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from manual_golden_architecture import (  # noqa: E402
    CATALOG_SOURCE,
    REGISTER_SOURCE,
    TILE_SOURCE,
    golden_architecture_bodies,
    golden_architecture_routes,
)


class GoldenArchitectureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = {
            path: (ROOT / path).read_bytes()
            for path in (CATALOG_SOURCE, REGISTER_SOURCE, TILE_SOURCE)
        }
        cls.catalog = json.loads(cls.raw[CATALOG_SOURCE])
        cls.registers = json.loads(cls.raw[REGISTER_SOURCE])
        cls.tiles = json.loads(cls.raw[TILE_SOURCE])
        cls.pages, cls.audit = golden_architecture_bodies(
            "830fbdb53bccec889414b5673ffba31b0a08606d",
            cls.catalog,
            cls.registers,
            cls.tiles,
            cls.raw,
        )

    def test_route_inventory_contains_only_current_golden_pages(self):
        self.assertEqual(set(self.pages), golden_architecture_routes())
        self.assertEqual(set(self.audit), golden_architecture_routes())
        forbidden = {
            "arch-execution-mode.html",
            "arch-vgpr.html",
            "arch-predicate.html",
            "arch-core-state.html",
            "arch-model-notes.html",
        }
        self.assertTrue(forbidden.isdisjoint(self.pages))

    def test_system_register_table_is_exact_and_behavior_complete(self):
        body = self.pages["arch-ssr.html"][1]
        keys = re.findall(r'data-register-key="([^"]+)"', body)
        expected = [
            f"{row['scope']}:{row['name']}:{row.get('address', row.get('low_index'))}"
            for row in self.registers["registers"]
        ]
        self.assertEqual(keys, expected)
        self.assertEqual(len(keys), 100)
        for literal in (
            "CORE_STATE",
            "当前架构行为",
            "写入值同时选择当前 ACR",
            "读取架构时间",
            "只写，读取会被拒绝",
        ):
            self.assertIn(literal, body)
        self.assertNotIn("历史", body)

    def test_pages_preserve_reviewed_current_explanations(self):
        plain = unescape(
            re.sub(r"<[^>]+>", " ", "\n".join(body for _, body in self.pages.values()))
        )
        for literal in (
            "带累加的矩阵操作读取显式 Local 输入 C",
            "Tile 块可以先登记",
            "第一条普通标量指令使块进入块体阶段",
            "程序序描述一条执行流中指令的先后关系",
            "本版定义 13 个异常编号",
            "Tile VEC 有 32 个操作",
        ):
            self.assertIn(literal, plain)
        for stale in (
            "v0.58",
            "v0.55",
            "历史说明",
            "旧中文",
            "Janus Core",
            "旧模型",
            "旧路径",
        ):
            self.assertNotIn(stale, plain)

    def test_audit_binds_release_commit_and_exact_machine_sources(self):
        for record in self.audit.values():
            self.assertEqual(
                record["source_commit"], "830fbdb53bccec889414b5673ffba31b0a08606d"
            )
            self.assertEqual(set(record["sources"]), set(self.raw))
            self.assertEqual(record["origin"], "v0.59.2-machine-projection")

    def test_rejects_missing_behavior_ownership(self):
        modified = json.loads(json.dumps(self.registers))
        modified["behavior_classes"][0]["registers"].remove("THREAD_PTR")
        with self.assertRaisesRegex(ValueError, "behavior coverage"):
            golden_architecture_bodies("x", self.catalog, modified, self.tiles)


if __name__ == "__main__":
    unittest.main()
