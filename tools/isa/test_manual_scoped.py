#!/usr/bin/env python3
from __future__ import annotations
import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))
from build_manual_scoped_data import build
from manual_scoped import (
    scoped_detail,
    scoped_summary,
    tile_detail,
    tile_summary,
    validate_coverage,
)
from manual_scoped_zh import role_zh

PTO_ROOT = Path("/Users/zhoubot/.codex/worktrees/pto-spec/published-0591-source")


class ManualScopedTest(unittest.TestCase):
    def test_all_normative_rows_resolve(self):
        self.assertEqual(validate_coverage(), [])

    def test_tile_manual_data_is_exact_published_asl_projection(self):
        if not PTO_ROOT.is_dir():
            self.skipTest("published PTO source checkout unavailable")
        expected = json.loads(
            (
                ROOT
                / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
            ).read_text()
        )
        self.assertEqual(build(PTO_ROOT), expected)

    def test_scoped_contract_does_not_overstate_scope(self):
        rows = json.loads((ROOT / "isa/v0.59/state/pto_scalar_forms.json").read_text())[
            "scoped_forms"
        ]
        for row in rows:
            summary = scoped_summary(row)
            detail = scoped_detail(row)
            self.assertRegex(summary, r"[\u4e00-\u9fff]")
            self.assertIn("这是共享请求，不是单独的可见性禁止规则", detail)
            self.assertIn("源 TPC + 8", detail)
            self.assertIn("只快照、不消费", detail)
        self.assertEqual(len({scoped_summary(row) for row in rows}), 705)
        signed = next(row for row in rows if row["mnemonic"] == "C.LWI")
        self.assertIn("符号扩展", scoped_detail(signed))

    def test_all_tile_pages_have_specific_source_and_contract(self):
        ops = json.loads(
            (ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )["operations"]
        for op in ops:
            self.assertRegex(tile_summary(op), r"[\u4e00-\u9fff]")
            detail = tile_detail(op)
            self.assertIn("github.com/PTO-ISA/pto-spec/blob/a89a53d", detail)
            self.assertIn('class="tile-zh-mechanism"', detail)
            self.assertIn('class="tile-zh-inputs-outputs"', detail)
            self.assertIn('class="tile-zh-effects"', detail)
            self.assertIn('class="tile-zh-constraints"', detail)
            self.assertIn("英文规范原文", detail)
        self.assertEqual(len({tile_summary(op) for op in ops}), 119)
        roles = {
            operand["role"]
            for record in json.loads(
                (
                    ROOT
                    / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
                ).read_text()
            )["operations"]
            for operand in record["contract"].get("operands", [])
        }
        for role in roles:
            self.assertRegex(role_zh(role), r"[\u4e00-\u9fff]", role)
        by_name = {op["name"]: op for op in ops}
        self.assertIn("left + right", tile_detail(by_name["TADD"]))
        self.assertIn("M x N", tile_detail(by_name["TMATMUL"]))
        self.assertIn("row_stride_bytes", tile_detail(by_name["TLOAD"]))
        self.assertIn("TLOADDataTypeLegal", tile_detail(by_name["TLOAD"]))
        self.assertIn("TSTOREDataTypeLegal", tile_detail(by_name["TSTORE"]))
        self.assertIn("RMode 与 Sat", tile_detail(by_name["TCVT"]))
        self.assertIn("谓词为 1", tile_detail(by_name["TSEL"]))
        self.assertIn("不转换数值", tile_detail(by_name["TMOV"]))
        self.assertNotEqual(
            tile_summary(by_name["TLOAD"]), tile_summary(by_name["TSTORE"])
        )


if __name__ == "__main__":
    unittest.main()
