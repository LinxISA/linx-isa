#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

from tools.isa.manual_current_prose import (
    gold_markdown,
    golden_constraints,
    golden_markdown,
)


class ManualCurrentProseTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[2]

    def test_compatibility_api(self) -> None:
        self.assertIs(gold_markdown, golden_markdown)

    def test_bior_rejects_reserved_selectors_before_reads_or_state(self) -> None:
        text = golden_markdown(
            "docs/zh/isa/header/B.IOR.md", "# B.IOR\n\nstale\n"
        )
        self.assertIn("编码 24 至 31 保留", text)
        self.assertIn("选择器编码 24 至 31 保留", text)
        self.assertIn("在读取或改变绑定状态之前", text)
        self.assertIn("也不读取任何 GPR", text)
        self.assertIn("同时需要范围与 GPR 掩码时使用连续两条记录", text)
        self.assertIn("Fault_IllegalInstruction", text)
        self.assertNotIn("stale", text)

        commands = json.loads(
            (self.ROOT / "isa/v0.59/state/pto_command_forms.json").read_text()
        )["forms"]
        bior = next(form for form in commands if form["mnemonic"] == "B.IOR")
        selectors = {
            item["field"]: item["values"]
            for item in bior["constraints"]
            if item["field"].startswith("Reg")
        }
        self.assertEqual(set(selectors), {"RegDst", "RegSrc0", "RegSrc1", "RegSrc2"})
        self.assertTrue(all(values == list(range(24)) for values in selectors.values()))

    def test_bior_alias_source_uses_the_same_current_body(self) -> None:
        actual = golden_markdown(
            "docs/zh/architecture/isa-manual/supplements/binder-alias.md",
            "# B.IOR\n\n旧导航。\n",
        )
        self.assertIn("在读取或改变绑定状态之前", actual)
        self.assertIn("也不读取任何 GPR", actual)
        self.assertNotIn("旧导航", actual)

    def test_bior_text_is_independently_bound_to_semantic_projection(self) -> None:
        forms = json.loads(
            (
                self.ROOT
                / "docs/architecture/isa-manual/reference/pto-v0591-semantics.json"
            ).read_text()
        )["forms"]
        projected = next(
            form for form in forms.values() if form.get("handler") == "BindBundleScalarIO"
        )
        authority = " ".join(
            statement
            for role in ("defaults", "exceptions", "legality")
            for statement in projected[role]
        )
        self.assertIn("selectors 24..31 are reserved", authority)
        self.assertIn("before binding state changes", authority)
        self.assertIn("Base/Min/Max first record", authority)
        self.assertIn("exactly two contiguous records", authority)

        rendered = golden_markdown("alias.md", "# B.IOR\n")
        self.assertIn("选择器编码 24 至 31 保留", rendered)
        self.assertIn("在读取或改变绑定状态之前", rendered)
        self.assertIn("也不读取任何 GPR", rendered)
        self.assertIn("同时需要范围与 GPR 掩码时使用连续两条记录", rendered)

    def test_iall_pages_drop_the_nonexistent_operand_and_examples(self) -> None:
        catalog = json.loads(
            (self.ROOT / "isa/v0.59/linxisa-v0.59.json").read_text()
        )["instructions"]
        for mnemonic in ("BC.IALL", "DC.IALL", "IC.IALL"):
            row = next(item for item in catalog if item["mnemonic"] == mnemonic)
            path = self.ROOT / f"docs/zh/isa/inst/misa_s/{mnemonic}.md"
            actual = golden_markdown(path.as_posix(), path.read_text())
            with self.subTest(mnemonic=mnemonic):
                self.assertIn(f"```asm\n{row['asm']}\n```", actual)
                self.assertNotIn("SrcL", actual)
                self.assertNotIn("单寄存器", actual)
                self.assertIn("仅允许在系统块内使用", actual)

        alias_source = (
            self.ROOT / "docs/zh/isa/inst/misa_s/DC.IALL.md"
        ).read_text()
        alias = golden_markdown("supplements/cache-maintenance-alias.md", alias_source)
        self.assertIn("```asm\ndc.iall\n```", alias)
        self.assertNotIn("SrcL", alias)

    def test_all_21_hl_immediate_stores_use_catalog_srcd_name(self) -> None:
        catalog = json.loads(
            (self.ROOT / "isa/v0.59/linxisa-v0.59.json").read_text()
        )["instructions"]
        rows = list({
            row["mnemonic"]: row
            for row in catalog
            if re.fullmatch(r"HL\.S[BDHW]I(?:\.(?:PO|PR|U|UPO|UPR))?", row["mnemonic"])
            and not row.get("pto_scope")
        }.values())
        self.assertEqual(len(rows), 21)
        for row in rows:
            path = self.ROOT / f"docs/zh/isa/inst/misa_h/{row['mnemonic']}.md"
            actual = golden_markdown(path.as_posix(), path.read_text())
            with self.subTest(mnemonic=row["mnemonic"]):
                self.assertIn(row["asm"], actual)
                self.assertIn("SrcD", actual)
                self.assertNotIn("SrcL", actual)

        alias_source = (
            self.ROOT / "docs/zh/isa/inst/misa_h/HL.SWI.md"
        ).read_text()
        alias = golden_markdown("supplements/store-word-alias.md", alias_source)
        self.assertIn("hl.swi SrcD, [SrcR, simm]", alias)
        self.assertNotIn("SrcL", alias)

    def test_integer_minmax_pages_do_not_claim_float_only_placement(self) -> None:
        for mnemonic in ("MIN", "MINU", "MAX", "MAXU"):
            path = self.ROOT / f"docs/zh/isa/inst/misa_f/{mnemonic}.md"
            actual = golden_markdown(path.as_posix(), path.read_text())
            with self.subTest(mnemonic=mnemonic):
                self.assertIn("标量整数比较指令", actual)
                self.assertIn("标准块的标量块体", actual)
                self.assertNotIn("只能用于浮点块", actual)

        source = (self.ROOT / "docs/zh/isa/inst/misa_f/MIN.md").read_text()
        alias = golden_markdown("supplements/signed-min-alias.md", source)
        self.assertIn("标量整数比较指令", alias)

    def test_all_46_indexed_pages_receive_descriptor_and_mask_contract(self) -> None:
        operations = json.loads(
            (self.ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )["operations"]
        indexed = [
            operation
            for operation in operations
            if operation["name"].startswith(("MGATHER", "MSCATTER"))
        ]
        self.assertEqual(len(indexed), 23)
        page_names = [operation["name"] for operation in indexed] + [
            operation["command_mnemonic"] for operation in indexed
        ]
        self.assertEqual(len(page_names), 46)
        for mnemonic in page_names:
            with self.subTest(mnemonic=mnemonic):
                actual = golden_constraints(
                    mnemonic, ("RegSrc1、RegSrc2 与 RegDst 必须为零。",)
                )
                prose = " ".join(actual)
                self.assertIn("MinIndex", prose)
                self.assertIn("MaxIndex", prose)
                self.assertIn("第二条记录", prose)
                self.assertIn("ExecMaskPresent", prose)
                self.assertNotIn("必须为零", prose)

    def test_indexed_projection_contains_range_fault_and_alias_folding_limits(self) -> None:
        projected = json.loads(
            (
                self.ROOT
                / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
            ).read_text()
        )["operations"]
        indexed = [
            operation
            for operation in projected
            if operation["mnemonic"].startswith(("MGATHER", "MSCATTER"))
        ]
        self.assertEqual(len(indexed), 23)
        for operation in indexed:
            contract = operation["contract"]
            prose = " ".join(
                statement
                for role in ("block_composition", "defaults", "legality", "ordering")
                for statement in contract.get(role, [])
            )
            with self.subTest(operation=operation["mnemonic"]):
                self.assertIn("MinIndex", prose)
                self.assertIn("MaxIndex", prose)
                self.assertIn("ExecMaskPresent", prose)
                self.assertIn("Fault_TileLegality", prose)
                self.assertIn("conflict edges", prose)
                self.assertIn("never weakens independent ordering constraints", prose)

    def test_fold_order_is_architectural_for_all_eight_reductions(self) -> None:
        names = (
            "TCOLMAX", "TCOLMIN", "TCOLPROD", "TCOLSUM",
            "TROWMAX", "TROWMIN", "TROWPROD", "TROWSUM",
        )
        for name in names:
            source = self.ROOT / f"docs/zh/isa/header/tileblock/{name}.md"
            actual = golden_markdown(source.as_posix(), source.read_text())
            constraints = " ".join(golden_constraints(name, ()))
            with self.subTest(name=name):
                self.assertIn("禁止树形重结合", actual)
                self.assertIn("不得扩大整数运算宽度", actual)
                self.assertIn("原子发布", actual)
                self.assertIn("禁止树形重结合", constraints)

    def test_c_movr_preserves_authored_explanation_and_examples(self) -> None:
        path = self.ROOT / "docs/zh/isa/inst/misa_c/C.MOVR.md"
        source = path.read_text()
        actual = golden_markdown(path.as_posix(), source)
        for snippet in (
            "将源寄存器值移动到目的寄存器中。",
            "integer d = UInt(RegDst);",
            "c.movr  a1,   ->t",
            "c.movr  u#1,  ->u",
            "c.movr  t#1,  ->a3",
            "允许源和目的寄存器为同一个寄存器。",
        ):
            self.assertIn(snippet, actual)
        self.assertEqual(source.count("```"), actual.count("```"))
        self.assertIn("16 位压缩编码", actual)

    def test_four_reserved_only_pages_retain_early_rejection(self) -> None:
        paths = (
            "docs/zh/isa/inst/misa_s/DMA.FREE.L.md",
            "docs/zh/isa/inst/misa_s/DMA.FREE.S.md",
            "docs/zh/isa/header/templateblock/MCOPY.DL.md",
            "docs/zh/isa/header/templateblock/MCOPY.DS.md",
        )
        for relative in paths:
            source = (self.ROOT / relative).read_text()
            actual = golden_markdown(relative, source)
            with self.subTest(path=relative):
                self.assertIn("仅保留编码", actual)
                self.assertIn("未实现", actual)
                self.assertIn("读取操作数或产生架构效果之前拒绝", actual)
                self.assertNotIn("0.59.2", actual)


if __name__ == "__main__":
    unittest.main()
