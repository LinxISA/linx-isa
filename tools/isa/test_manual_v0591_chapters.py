#!/usr/bin/env python3

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import unittest

from tools.isa.manual_v0591_chapters import (
    ACTIVE_REPLACEMENTS,
    active_markdown,
    obsolete_mentions,
)


class ManualV0591ChaptersTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[2]
    TEPL = "docs/zh/isa/blockIntro/tepl_block/intro.md"
    CUBE = "docs/zh/isa/blockIntro/cube_block/intro.md"
    EXCEPTION = "docs/zh/isa/exception/exception.md"

    def _render(self, path: str) -> str:
        source = (self.ROOT / path).read_text()
        rendered = active_markdown(path, source, ())
        self.assertIsNotNone(rendered)
        return str(rendered)

    def test_tepl_uses_exact_current_engine_inventory(self) -> None:
        operations = json.loads(
            (self.ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )["operations"]
        counts = Counter(operation["engine"] for operation in operations)
        self.assertEqual(counts, {"VEC": 32, "SFU": 47, "TLSU": 28, "CUBE": 12})

        text = self._render(self.TEPL)
        self.assertIn("VEC 有 32 个", text)
        self.assertIn("SFU 有 47 个", text)
        self.assertIn("四类合计 119 个", text)
        self.assertNotIn("VEC | Tile/Tile", text)
        self.assertNotIn("35", text)
        self.assertNotIn("52", text)
        self.assertNotIn("v0.58", text)
        for operation in operations:
            if operation["engine"] in {"VEC", "SFU"}:
                self.assertIn(f"`{operation['name']}`", text)

    def test_cube_chapter_matches_all_current_cube_contracts(self) -> None:
        operations = json.loads(
            (
                self.ROOT
                / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
            ).read_text()
        )["operations"]
        cube = [operation for operation in operations if operation["engine"] == "CUBE"]
        self.assertEqual(len(cube), 12)
        text = self._render(self.CUBE)
        for operation in cube:
            self.assertIn(operation["mnemonic"], text)

        acc = [operation for operation in cube if operation["mnemonic"].endswith("_ACC")]
        self.assertEqual(len(acc), 4)
        for operation in acc:
            authority = " ".join(
                statement
                for role in ("defaults", "legality", "state_effects")
                for statement in operation["contract"].get(role, [])
            )
            self.assertRegex(authority, r"(?:must differ|distinct)")
        self.assertIn("`C == D` 非法", text)
        self.assertIn("C 在乘法前取快照", text)
        self.assertIn("M、N、K 是", text)
        self.assertIn("TGEMV 固定 M=1", text)
        self.assertIn("`CUBE_M16` 或 `CUBE_M32`", text)
        self.assertIn("Local B 使用 `CUBE_N8`", text)
        self.assertIn("不得在操作前把所有输入一律转换为 FP32 或 INT32", text)
        self.assertNotIn("D == C", text)
        self.assertNotIn("512Byte", text)
        self.assertNotIn("1024Byte", text)

    def test_exception_chapter_matches_hardened_cube_first_use(self) -> None:
        state = (self.ROOT / "isa/v0.59/sail/model/state/state.sail").read_text()
        execute = (self.ROOT / "isa/v0.59/sail/model/execute/execute.sail").read_text()
        self.assertIn("ssr_econfig_acr1[33]", state)
        self.assertRegex(
            state,
            r"trap_cube_first_use\(\)[\s\S]*?raise_trap_full\([\s\S]*?0b1,[\s\S]*?0b1,[\s\S]*?trapnum_e_inst\(\),[\s\S]*?\(sail_zeros\(24\) \+ 4\),[\s\S]*?0x0000_0000_0000_0001,[\s\S]*?0b0",
        )
        self.assertIn("cube_first_use_enabled() then trap_cube_first_use()", execute)

        text = self._render(self.EXCEPTION)
        for fact in (
            "ACR2",
            "`ECONFIG_ACR1` 的 CUBE 位 33",
            "`TRAPNO.E=1`",
            "`TRAPNO.ARGV=1`",
            "`TRAPNO.TRAPNUM=E_INST (0)`",
            "`TRAPNO.CAUSE=EC_PERM (4)`",
            "`TRAPARG0=1`",
            "`ECSTATE.BI=0`",
            "TLSU 访存异常",
            "精确数据异常路径",
            "PTO 导入的标量、命令和 Tile 合同",
        ):
            self.assertIn(fact, text)
        for stale in (
            "v0.55",
            "v0.58",
            "ESAVE",
            "VECTOR",
            "ECONFIG.V",
            "TRAPARG0=0",
            "BSTART.MPAR",
            "BSTART.MSEQ",
        ):
            self.assertNotIn(stale, text)

    def test_new_chapter_links_resolve_to_current_sources(self) -> None:
        for source in (self.TEPL, self.CUBE, self.EXCEPTION):
            text = ACTIVE_REPLACEMENTS[source]
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (self.ROOT / source).parent.joinpath(target).resolve()
                with self.subTest(source=source, target=target):
                    self.assertTrue(resolved.is_file(), resolved)

    def test_unrelated_current_page_is_unchanged(self) -> None:
        source = "# Unrelated\n\nCurrent scalar explanation.\n"
        self.assertEqual(active_markdown("docs/zh/example.md", source, ()), source)
        for path in (self.TEPL, self.CUBE, self.EXCEPTION):
            self.assertEqual(obsolete_mentions(ACTIVE_REPLACEMENTS[path], ()), ())


if __name__ == "__main__":
    unittest.main()
