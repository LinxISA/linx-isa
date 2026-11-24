#!/usr/bin/env python3

from dataclasses import dataclass
import json
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

try:
    from manual_active_articles import (
        active_architecture_pages,
        active_markdown,
        active_rows,
        obsolete_mentions,
        obsolete_mnemonics,
        obsolete_source_paths,
        source_is_active,
        source_mentions_obsolete,
    )
except ModuleNotFoundError:
    from tools.isa.manual_active_articles import (
        active_architecture_pages,
        active_markdown,
        active_rows,
        obsolete_mentions,
        obsolete_mnemonics,
        obsolete_source_paths,
        source_is_active,
        source_mentions_obsolete,
    )


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Page:
    key: str
    source_path: str | None


class ManualActiveArticlesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(
            (ROOT / "isa/v0.59.2/linxisa-v0.59.2.json").read_text(encoding="utf-8")
        )
        cls.names = obsolete_mnemonics(cls.catalog)

    def test_catalog_filter_removes_exactly_the_adopted_inventory(self):
        active = active_rows(self.catalog)
        self.assertEqual(len(self.catalog["instructions"]), 1499)
        self.assertEqual(len(active), 1306)
        self.assertEqual(len(self.names), 193)
        self.assertIn("V.QPUSH", self.names)
        self.assertIn("B.TEXT", self.names)
        self.assertIn("C.BSTART.MPAR", self.names)
        self.assertNotIn("BSTART.TEPL", self.names)
        self.assertNotIn("HL.QPUSH", self.names)

    def test_exact_token_matching_does_not_hide_tile_vec_or_retained_names(self):
        self.assertTrue(source_mentions_obsolete("执行 V.ADD，然后 B.TEXT", self.names))
        self.assertFalse(
            source_mentions_obsolete(
                "Tile VEC 使用 BSTART.TEPL；HL.QPUSH 保留。", self.names
            )
        )
        self.assertFalse(source_mentions_obsolete("变量名是 V.ADDRESS", self.names))

    def test_source_policy_withholds_whole_legacy_articles(self):
        self.assertFalse(
            source_is_active(
                "docs/zh/isa/blockIntro/vec_block/intro.md",
                "本页没有列出具体指令。",
                self.names,
            )
        )
        self.assertTrue(
            source_is_active(
                "docs/zh/isa/arch/branch.md", "示例使用 BSTART.VPAR。", self.names
            )
        )
        self.assertTrue(
            source_is_active(
                "docs/zh/isa/blockIntro/cube_block/intro.md",
                "CUBE 通过 BSTART.TEPL 选择 Tile 操作。",
                self.names,
            )
        )
        self.assertTrue(
            source_is_active(
                "docs/zh/isa/register/common/intro.md",
                "形参寄存器用于分离块。",
                self.names,
            )
        )
        self.assertEqual(
            obsolete_mentions("B.TEXT 建立 Decoupled Block。", self.names),
            ("B.TEXT", "Decoupled Block"),
        )
        self.assertEqual(
            obsolete_mentions("进入MPAR并执行。", self.names),
            ("MPAR",),
        )
        self.assertEqual(
            obsolete_mentions("![旧块](figs/VSEQ-flow.svg)", self.names),
            ("VSEQ",),
        )

    def test_architecture_filter_keeps_indexes_and_current_chapters(self):
        pages = (
            Page("architecture", None),
            Page("branch", "docs/zh/isa/arch/branch.md"),
            Page("cube", "docs/zh/isa/blockIntro/cube_block/intro.md"),
        )
        sources = {
            "docs/zh/isa/arch/branch.md": "BSTART.VPAR 跳到 B.TEXT。",
            "docs/zh/isa/blockIntro/cube_block/intro.md": "矩阵 Tile 操作说明。",
        }
        self.assertEqual(
            tuple(
                page.key
                for page in active_architecture_pages(pages, sources, self.names)
            ),
            ("architecture", "branch", "cube"),
        )
        self.assertEqual(
            obsolete_source_paths(sources, sources, self.names),
            (),
        )

    def test_mixed_core_chapters_get_current_complete_replacements(self):
        for path in (
            "docs/zh/isa/arch/bisa.md",
            "docs/zh/isa/arch/branch.md",
            "docs/zh/isa/arch/execute.md",
            "docs/zh/isa/register/common/intro.md",
            "docs/zh/isa/blockIntro/tlsu_block/intro.md",
        ):
            revised = active_markdown(path, (ROOT / path).read_text(), self.names)
            self.assertIsNotNone(revised, path)
            self.assertEqual(obsolete_mentions(revised, self.names), (), path)
            self.assertGreater(len(revised), 180, path)

        try:
            from manual_markdown import render_markdown_text
        except ModuleNotFoundError:
            from tools.isa.manual_markdown import render_markdown_text
        branch = "docs/zh/isa/arch/branch.md"
        rendered = render_markdown_text(
            branch,
            active_markdown(branch, (ROOT / branch).read_text(), self.names),
            current_page="arch-branch.html",
        ).html
        self.assertIn('id="src-branch-29da7fb8--branch"', rendered)

    def test_common_reference_and_current_tile_text_are_retained(self):
        pseudo = "docs/zh/isa/inst/LibPseudoCode.md"
        self.assertEqual(
            active_markdown(pseudo, (ROOT / pseudo).read_text(), self.names),
            (ROOT / pseudo).read_text(),
        )
        cube = "docs/zh/isa/blockIntro/cube_block/intro.md"
        revised = active_markdown(cube, (ROOT / cube).read_text(), self.names)
        self.assertIn("TMATMUL", revised)
        self.assertIn("显式 Local 目的 Tile D", revised)
        self.assertEqual(obsolete_mentions(revised, self.names), ())

    def test_retained_instruction_drops_only_obsolete_cross_reference_blocks(self):
        source = """# L.ADD

## 说明

执行保留的标量加法。

## 旧向量对应形式

对应形式是 V.ADD。

## 结果

结果写入显式目的寄存器。
"""
        revised = active_markdown(
            "docs/zh/isa/inst/misa_l/L.ADD.md", source, self.names
        )
        self.assertIn("执行保留的标量加法", revised)
        self.assertIn("结果写入显式目的寄存器", revised)
        self.assertNotIn("旧向量对应形式", revised)
        self.assertEqual(obsolete_mentions(revised, self.names), ())

    def test_mixed_table_stays_a_single_markdown_table(self):
        source = """# 对照

| 名称 | 状态 |
| --- | --- |
| ADD | 保留 |
| V.ADD | 退役 |
| TADD | 保留 |
"""
        revised = active_markdown("docs/zh/isa/reference.md", source, self.names)
        self.assertIn("| ADD | 保留 |\n| TADD | 保留 |", revised)
        self.assertNotIn("\n\n| TADD", revised)

    def test_short_block_names_and_their_figures_are_removed_locally(self):
        source = """# 状态

当前块保存 BPC。

```asm
MPAR .Body
```

![VSEQ 旧流程](figs/vseq-flow.svg)

Tile 目的寄存器仍是显式状态。
"""
        revised = active_markdown("docs/zh/isa/arch/state.md", source, self.names)
        self.assertIn("当前块保存 BPC", revised)
        self.assertIn("Tile 目的寄存器", revised)
        self.assertNotIn(".Body", revised)
        self.assertNotIn("vseq-flow.svg", revised)
        self.assertEqual(obsolete_mentions(revised, self.names), ())


if __name__ == "__main__":
    unittest.main()
