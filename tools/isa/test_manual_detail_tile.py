#!/usr/bin/env python3

import unittest
from pathlib import Path

try:
    from manual_authored import authored_tile
    from manual_detail_tile import (
        tile_body,
        tile_command_body,
        validate_tile_bodies,
    )
    from manual_tag import tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_authored import authored_tile
    from tools.isa.manual_detail_tile import (
        tile_body,
        tile_command_body,
        validate_tile_bodies,
    )
    from tools.isa.manual_tag import tagged_json


class ManualDetailTileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.operations = {
            row["name"]: row
            for row in tagged_json("isa/v0.59/state/pto_tile_operations.json")[
                "operations"
            ]
        }

    def test_all_published_operations_have_current_chinese_body(self):
        self.assertEqual(119, len(self.operations))
        self.assertEqual([], validate_tile_bodies())
        replacements = 0
        for operation in self.operations.values():
            body = tile_body(operation)
            if body is None:
                continue
            replacements += 1
            self.assertIn(operation["name"], body)
            self.assertIn("## ", body)
        self.assertEqual(104, replacements)

    def test_indexed_memory_families_do_not_reuse_plain_gather_text(self):
        gather = tile_body(self.operations["MGATHER"])
        add = tile_body(self.operations["MGATHER_ADD"])
        masked = tile_body(self.operations["MGATHER_MASK"])
        popc = tile_body(self.operations["MSCATTER_POPC"])
        self.assertIn("字节位移", gather)
        self.assertIn("原子读-改-写", add)
        self.assertIn("旧值返回", add)
        self.assertIn("谓词为 0", masked)
        self.assertIn("不会产生翻译后地址", masked)
        self.assertIn("不读取值 Tile", popc)
        self.assertIn("U32 增量", popc)
        for body in (gather, add, masked, popc):
            self.assertNotIn("不替代规范操作", body)
            self.assertNotIn("下方 owner", body)

    def test_arg_reduce_body_uses_dimensions_not_example_constants(self):
        root = Path(__file__).resolve().parents[2]
        supplements = root / "docs/zh/architecture/isa-manual/supplements"
        row = (supplements / "trowargmax.md").read_text(encoding="utf-8")
        col = (supplements / "tcolargmin.md").read_text(encoding="utf-8")
        self.assertIn("`ValidRow × 1`", row)
        self.assertIn("`1 × ValidCol`", col)
        # The checked worked example intentionally remains concrete.
        self.assertIn("有效区域为 7 x 60", row)
        self.assertIn("有效区域为 7 x 60", col)

    def test_value_reductions_do_not_leak_worked_example_shape(self):
        row = tile_body(self.operations["TROWSUM"])
        col = tile_body(self.operations["TCOLMAX"])
        self.assertIn("ValidRow 个有效行乘一个有效列", row)
        self.assertIn("ValidRow x 1 有效区域之外", row)
        self.assertNotIn("逻辑形状为 7 个有效行", row)
        self.assertIn("一个有效行乘 ValidCol 个有效列", col)
        self.assertIn("1 x ValidCol 有效区域之外", col)
        self.assertNotIn("逻辑形状为 一个有效行乘 60 个有效列", col)

    def test_typed_command_is_bound_to_exact_operation(self):
        add = tile_command_body({"mnemonic": "BSTART.MGATHER.ADD"})
        scatter = tile_command_body({"mnemonic": "BSTART.MSCATTER"})
        self.assertIn("`MGATHER_ADD`", add)
        self.assertIn("原子读-改-写", add)
        self.assertIn("`MSCATTER`", scatter)
        self.assertIn("没有目标", scatter)
        self.assertIsNone(tile_command_body({"mnemonic": "BSTART.TEPL"}))

    def test_exact_operation_figure_is_preserved(self):
        body = tile_body(self.operations["TADD"], authored_tile("TADD"))
        self.assertIn("**数据块加法(Tile Add)**", body)
        self.assertIn("逐元素加法操作", body)
        self.assertIn("../../../figs/isa/tileop/TADD.png", body)
        # Atomic variants share a historical family page and must not inherit
        # its ordinary MGATHER illustration or prose.
        atomic = tile_body(self.operations["MGATHER_ADD"], authored_tile("MGATHER_ADD"))
        self.assertNotIn("## 数据流示意", atomic)

    def test_mgather_keeps_human_explanation_and_replaces_old_contract(self):
        body = tile_body(self.operations["MGATHER"], authored_tile("MGATHER"))
        self.assertIn("内存聚集（Gather from Memory to Tile）", body)
        self.assertIn("DstTile[r][c] = Memory[BaseGPR + byte_offset]", body)
        self.assertIn("S32、U32、S64 或 U64", body)
        self.assertIn("不会乘以传输元素的字节数", body)
        self.assertIn("伪代码描述普通非打包类型", body)
        self.assertIn("一个索引指向一个字节", body)
        self.assertIn("两个相邻的逻辑半字节", body)
        self.assertNotIn("支持 `u16`、`u32` 和 `u64`", body)

    def test_typed_atomic_command_does_not_reuse_plain_gather_page(self):
        command = tile_command_body({"mnemonic": "BSTART.MGATHER.ADD"})
        variant = tile_body(
            self.operations["MGATHER_ADD"], authored_tile("MGATHER_ADD")
        )
        for body in (command, variant):
            self.assertIn("原子读-改-写", body)
            self.assertNotIn("普通读取伪代码", body)
            self.assertNotIn("内存聚集（Gather from Memory to Tile）", body)

    def test_cube_pages_do_not_restore_old_accumulator_register_claim(self):
        body = tile_body(self.operations["TMATMUL_ACC"], authored_tile("TMATMUL_ACC"))
        self.assertIn("TMATMUL_ACC", body)
        self.assertNotIn("累加到ACC寄存器", body)
        self.assertNotIn("Matrix_C +=", body)

    def test_unknown_operation_is_not_invented(self):
        self.assertIsNone(tile_body({"name": "TDOESNOTEXIST"}))
        self.assertIsNone(tile_command_body({"mnemonic": "BSTART.UNKNOWN"}))


if __name__ == "__main__":
    unittest.main()
