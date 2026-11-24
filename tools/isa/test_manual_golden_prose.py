import unittest
import json
from pathlib import Path

from tools.isa.manual_golden_prose import golden_constraints, golden_markdown


class ManualGoldenProseTest(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[2]

    def test_removes_only_obsolete_extension_classification(self):
        source = """# C.ADD

## 说明

执行加法，完整形式见 [ADD](../misa_g/ADD.md)。

## 约束

源不可用时引发 Fault_IllegalInstruction。

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能扩展时使用。
"""
        actual = golden_markdown("docs/zh/isa/inst/misa_c/C.ADD.md", source)
        self.assertIn("执行加法", actual)
        self.assertIn("Fault_IllegalInstruction", actual)
        self.assertNotIn("压缩指令扩展", actual)
        self.assertNotIn("instset", actual)
        self.assertNotIn("## 备注", actual)

    def test_keeps_useful_pseudocode_diagram_and_old_value(self):
        source = """# SWAPW

## 执行方式

```c
old = Memory[address];
Memory[address] = new_value;
```

![数据流](swap.svg)

原子交换把内存旧值写入目标。
"""
        actual = golden_markdown("SWAPW.md", source)
        self.assertIn("old = Memory", actual)
        self.assertIn("swap.svg", actual)
        self.assertIn("旧值", actual)

    def test_removes_specific_version_comparison_paragraph(self):
        source = """# TADD

## 说明

逐元素相加。

旧版使用另一种隐式累加器，这段历史说明不适用于本版。

## 示例

输入 1 与 2，输出 3。
"""
        actual = golden_markdown("TADD.md", source)
        self.assertIn("逐元素相加", actual)
        self.assertIn("输入 1 与 2", actual)
        self.assertNotIn("旧版", actual)

    def test_supplement_becomes_current_without_source_appendix(self):
        source = """<!-- LINXISA-SUPPLEMENT: {"version":"0.59.1"} -->
# B.ASSEMBLE

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

记录一个写入者范围。

## 0.59.1 来源

- PTO 源：asl/B.ASSEMBLE.asl
- PTO 提交：abc
"""
        actual = golden_markdown(
            "docs/zh/architecture/isa-manual/supplements/b-assemble.md", source
        )
        self.assertIn("记录一个写入者范围", actual)
        self.assertNotIn("增补", actual)
        self.assertNotIn("0.59.1 来源", actual)
        self.assertNotIn("PTO 提交", actual)

    def test_rewrites_model_terms_without_losing_architecture_rule(self):
        source = """# FENCE.D

## 执行结果

由于每个掩码都已分配，固定位仍在处理程序运行之前完成校验，因为该处理程序不写自己的 TPC。
"""
        actual = golden_markdown("supplements/fence-d.md", source)
        self.assertIn("读取操作数之前完成校验", actual)
        self.assertIn("随后 TPC 按指令长度前进", actual)
        self.assertNotIn("处理程序", actual)

    def test_rewrites_named_model_helpers_as_architecture_behavior(self):
        source = """# GMOV

## 合法性与异常

- GMOVDataTypeLegal 恰好接受 TileCarrierOrPackedBaselineDataTypeSupported 允许的类型：FP32。
- 与 atom/red、gather 和 scatter 分派器不同，ExecuteBundleGMOVOperation 没有零掩码提前返回，因此预检仍会执行。
"""
        actual = golden_markdown("supplements/gmov.md", source)
        self.assertIn("GMOV 接受的数据类型包括：FP32", actual)
        self.assertIn("零掩码不会跳过预检", actual)
        self.assertNotIn("GMOVDataTypeLegal", actual)
        self.assertNotIn("ExecuteBundle", actual)

    def test_all_release_supplements_drop_editorial_envelopes(self):
        folder = self.ROOT / "docs/zh/architecture/isa-manual/supplements"
        pages = sorted(folder.glob("*.md"))
        self.assertEqual(len(pages), 22)
        for page in pages:
            with self.subTest(page=page.name):
                actual = golden_markdown(
                    page.relative_to(self.ROOT).as_posix(), page.read_text()
                )
                for residue in (
                    "LINXISA-SUPPLEMENT",
                    "0.59.1 增补",
                    "0.59.1 来源",
                    "PTO 提交",
                    "处理程序",
                    "派发器",
                    "注入模型",
                ):
                    self.assertNotIn(residue, actual)

    def test_bior_uses_absolute_selectors_and_current_range_schema(self):
        actual = golden_markdown(
            "docs/zh/isa/header/B.IOR.md",
            "# B.IOR\n\nold text that must not survive\n",
        )
        self.assertIn("编码 24 至 31 保留", actual)
        self.assertIn("Fault_IllegalInstruction", actual)
        self.assertIn("S64 `MinIndex` 和 `MaxIndex`", actual)
        self.assertIn("B.IOR a0, a1, a2, ->zero", actual)
        self.assertIn("B.IOR a3, a4, zero, ->zero, ExecMaskPresent", actual)
        self.assertNotIn("old text", actual)

    def test_bior_generated_constraints_override_stale_reference_text(self):
        stale = (
            "选择器编码 24 至 31 会先保存，只在某些 schema 中拒绝。",
            "带索引的 TLSU 要求 RegSrc1、RegSrc2 与 RegDst 全为零。",
        )
        actual = golden_constraints("B.IOR", stale)
        self.assertTrue(
            any(
                "24 至 31" in item and "Fault_IllegalInstruction" in item
                for item in actual
            )
        )
        self.assertTrue(
            any("MinIndex" in item and "MaxIndex" in item for item in actual)
        )
        self.assertFalse(any("先保存" in item or "全为零" in item for item in actual))

    def test_indexed_tile_prose_distinguishes_absent_and_present_descriptor(self):
        stale = """# MGATHER_ADD

## 操作数

address 由 B.IOR.RegSrc0 给出。B.IOR 是必需的，RegSrc1、RegSrc2 与 RegDst 必须编码为零。
"""
        actual = golden_markdown("docs/zh/isa/header/tileblock/MGATHER_ADD.md", stale)
        self.assertIn("同为 zero 表示不声明范围", actual)
        self.assertIn("S64 MinIndex 和 MaxIndex", actual)
        self.assertIn("第二条记录", actual)
        self.assertNotIn("必须编码为零", actual)

        constraints = golden_constraints(
            "BSTART.MSCATTER.MASK",
            ("RegSrc1、RegSrc2 与 RegDst 必须为零。",),
        )
        self.assertEqual(len(constraints), 1)
        self.assertIn("MinIndex", constraints[0])

    def test_bior_claims_are_bound_to_release_projections(self):
        commands = json.loads(
            (self.ROOT / "isa/v0.59/state/pto_command_forms.json").read_text()
        )["forms"]
        bior = next(form for form in commands if form["mnemonic"] == "B.IOR")
        constraints = {
            item["field"]: item["values"]
            for item in bior["constraints"]
            if item["field"].startswith("Reg")
        }
        self.assertEqual(set(constraints), {"RegDst", "RegSrc0", "RegSrc1", "RegSrc2"})
        self.assertTrue(all(values == list(range(24)) for values in constraints.values()))

        operations = json.loads(
            (
                self.ROOT
                / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
            ).read_text()
        )["operations"]
        indexed = [
            operation
            for operation in operations
            if operation["mnemonic"].startswith(("MGATHER", "MSCATTER"))
        ]
        self.assertEqual(len(indexed), 23)
        for operation in indexed:
            with self.subTest(operation=operation["mnemonic"]):
                contract = operation["contract"]
                prose = " ".join(
                    statement
                    for role in ("block_composition", "defaults", "legality")
                    for statement in contract[role]
                )
                self.assertIn("MinIndex", prose)
                self.assertIn("MaxIndex", prose)
                self.assertIn("ExecMaskPresent", prose)


if __name__ == "__main__":
    unittest.main()
