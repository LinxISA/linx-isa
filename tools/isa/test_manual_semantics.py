#!/usr/bin/env python3

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.isa.manual_semantics import (
    describe_form,
    detail,
    summary,
    validate_catalog_coverage,
)


class ManualSemanticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalogs = {
            profile: json.loads(
                (ROOT / "isa" / profile / f"linxisa-{profile}.json").read_text(
                    encoding="utf-8"
                )
            )
            for profile in ("v0.58", "v0.59")
        }

    def row(self, profile: str, mnemonic: str):
        return next(
            row
            for row in self.catalogs[profile]["instructions"]
            if row["mnemonic"] == mnemonic
        )

    def test_all_forms_have_specific_semantics(self) -> None:
        self.assertEqual(validate_catalog_coverage(ROOT, "v0.58"), [])
        self.assertEqual(validate_catalog_coverage(ROOT, "v0.59"), [])

    def test_all_non_scoped_v0591_forms_are_covered_by_form_id(self) -> None:
        rows = [
            row
            for row in self.catalogs["v0.59"]["instructions"]
            if not row.get("pto_scope")
        ]
        self.assertEqual(len(rows), 794)
        self.assertEqual(len({row["id"] for row in rows}), 794)
        common = [row for row in rows if row.get("pto_source_form_id")]
        self.assertEqual(len(common), 578)
        self.assertEqual(
            [row["id"] for row in common if not describe_form(row, "v0.59").details],
            [],
        )
        self.assertEqual(
            [
                row["id"]
                for row in common
                if not any(
                    "github.com/PTO-ISA/pto-spec/blob/a89a53d" in source
                    for source in describe_form(row, "v0.59").provenance
                )
            ],
            [],
        )
        reference = json.loads(
            (
                ROOT / "docs/architecture/isa-manual/reference/pto-v0591-semantics.json"
            ).read_text(encoding="utf-8")
        )["forms"]
        self.assertEqual(len(reference), 578)
        self.assertEqual(
            [
                form_id
                for form_id, record in reference.items()
                if (record.get("review") or {}).get("outcome") != "FORMAL-COMPLETE"
            ],
            [],
        )
        labels = {
            "operands": "操作数：",
            "state_effects": "状态结果：",
            "memory_effects": "内存效果：",
            "ordering": "顺序：",
            "exceptions": "异常与 fault 边界：",
            "legality": "合法性：",
        }
        missing = []
        for row in common:
            semantic = describe_form(row, "v0.59")
            record = reference[row["pto_source_form_id"]]
            for key, label in labels.items():
                values = [
                    str(value)
                    for value in record.get(key, [])
                    if str(value) and str(value) != "none"
                ]
                if values and not any(
                    item.startswith(label) for item in semantic.details
                ):
                    missing.append(f"{row['id']}:{key}")
        self.assertEqual(missing, [])

    def test_catalog_note_is_preserved_exactly(self) -> None:
        row = self.row("v0.58", "ADDI")
        self.assertEqual(summary(row, self.catalogs["v0.58"]), row["note"])
        self.assertIn(row["note"], detail(row, self.catalogs["v0.58"]))
        row59 = self.row("v0.59", "ADDI")
        self.assertIn(
            "github.com/PTO-ISA/pto-spec/blob/a89a53d",
            detail(row59, self.catalogs["v0.59"]),
        )
        self.assertIn("标量二元运算", summary(row59, self.catalogs["v0.59"]))
        self.assertIn(
            "加载 4 byte", summary(self.row("v0.59", "LWI"), self.catalogs["v0.59"])
        )

    def test_vector_fallback_is_mnemonic_specific(self) -> None:
        catalog = self.catalogs["v0.59"]
        self.assertIn("整数加法", summary(self.row("v0.59", "V.ADD"), catalog))
        self.assertIn(
            "无符号32-bit", summary(self.row("v0.59", "V.LWUI.U.BRG"), catalog)
        )
        self.assertIn("原子加法", summary(self.row("v0.59", "V.LD.ADD"), catalog))
        self.assertIn("归约", summary(self.row("v0.59", "V.RDADD"), catalog))
        issue_expectations = {
            "V.LW": "issues/141",
            "V.LD.ADD": "issues/149",
            "V.QPUSH": "issues/150",
            "V.SHFL.DOWN": "issues/151",
        }
        for mnemonic, issue in issue_expectations.items():
            semantic = describe_form(self.row("v0.59", mnemonic), "v0.59")
            self.assertTrue(any(issue in source for source in semantic.provenance))

    def test_risky_vector_and_fall_claims_remain_bounded(self) -> None:
        catalog = self.catalogs["v0.59"]
        self.assertIn("有符号整数除法", summary(self.row("v0.59", "V.DIV"), catalog))
        brg = describe_form(self.row("v0.59", "V.LW.BRG"), "v0.59")
        self.assertTrue(any("lane 0" in item for item in brg.details))
        self.assertFalse(any("TSO ordering domain" in item for item in brg.details))
        immediate = describe_form(self.row("v0.59", "V.LWI"), "v0.59")
        self.assertTrue(
            any(
                "同一地址" in item or "一个有效地址" in item
                for item in immediate.details
            )
        )
        self.assertTrue(any("predicate bit 2*i" in item for item in immediate.details))
        for mnemonic in ("C.BSTART.VPAR", "C.BSTART.VSEQ"):
            semantic = describe_form(self.row("v0.59", mnemonic), "v0.59")
            self.assertNotIn("FALL 字段", semantic.description)
            self.assertTrue(
                any("没有独立的 FALL 物理字段" in item for item in semantic.details)
            )

    def test_detail_is_html_escaped(self) -> None:
        catalog = {"version": "0.58.7"}
        row = {
            "mnemonic": "X",
            "note": "a < b & c > d",
            "source": {"file": "x", "line": 1},
        }
        rendered = detail(row, catalog)
        self.assertIn("a &lt; b &amp; c &gt; d", rendered)
        self.assertNotIn("a < b", rendered)


if __name__ == "__main__":
    unittest.main()
