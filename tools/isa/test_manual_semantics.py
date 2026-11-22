#!/usr/bin/env python3

import json
from pathlib import Path
import subprocess
import sys
import unittest
import re


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.isa.manual_semantics import (
    _concise_chinese,
    _logical_compare_result,
    _natural_chinese,
    describe_form,
    detail,
    summary,
    validate_catalog_coverage,
)
from tools.isa.manual_prose_zh import polish, scalar_synopsis


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
        chinese = json.loads(
            (
                ROOT
                / "docs/architecture/isa-manual/reference/data/manual-semantics-zh.json"
            ).read_text(encoding="utf-8")
        )["forms"]
        self.assertEqual(len(chinese), 578)
        for form_id, record in chinese.items():
            for role in (
                "purpose",
                "mechanism",
                "inputs-outputs",
                "effects",
                "constraints",
            ):
                statements = record["roles"][role]["statements"]
                self.assertTrue(statements, f"{form_id}:{role}")
                visible = " ".join(statements)
                self.assertNotIn("其记录的摘要为", visible)
                self.assertNotRegex(visible, r"asl/[^ )：]+:\d+")
                self.assertNotIn("设计要点：", visible)
        missing = []
        for row in common:
            semantic = describe_form(row, "v0.59")
            record = chinese[row["pto_source_form_id"]]
            if row["mnemonic"] == "DC.IALL":
                continue
            fallback = _natural_chinese(
                _concise_chinese(record["roles"]["purpose"]["statements"][0])
            )
            expected_summary = scalar_synopsis(row, fallback)
            if semantic.short != expected_summary:
                missing.append(f"{row['id']}:summary")
            rendered = " ".join((semantic.description, *semantic.details))
            for role in ("mechanism", "inputs-outputs", "effects", "constraints"):
                for statement in record["roles"][role]["statements"]:
                    if polish(_natural_chinese(statement)) not in rendered:
                        missing.append(f"{row['id']}:{role}")
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
        self.assertIn(
            '<section class="semantic-section"><h4>操作数</h4>',
            detail(row59, self.catalogs["v0.59"]),
        )
        self.assertEqual(
            summary(row59, self.catalogs["v0.59"]),
            "将 SrcL 与零扩展后的 12 位立即数相加。结果写入 RegDst 指定的目标。",
        )
        self.assertIn(
            "按小端序读取一个 4 字节值",
            summary(self.row("v0.59", "LWI"), self.catalogs["v0.59"]),
        )

    def test_all_non_scoped_synopses_are_concise_chinese(self) -> None:
        rows = [
            row
            for row in self.catalogs["v0.59"]["instructions"]
            if not row.get("pto_scope")
        ]
        failures = []
        for row in rows:
            text = summary(row, self.catalogs["v0.59"])
            if not re.search(r"[\u4e00-\u9fff]", text) or len(text) > 180:
                failures.append((row["id"], text))
        self.assertEqual(failures, [])
        dc = describe_form(self.row("v0.59", "DC.IALL"), "v0.59")
        self.assertEqual(
            dc.short,
            "在系统块内同步完成数据缓存全部条目的失效维护。该形式没有显式操作数。",
        )
        dc_text = " ".join((dc.description, *dc.details))
        self.assertIn("无显式操作数", dc_text)
        self.assertNotIn("SrcL", dc_text)
        note_rows = [
            row for row in rows if row.get("note") and not row.get("pto_source_form_id")
        ]
        self.assertEqual(len(note_rows), 30)
        self.assertTrue(
            all(
                re.search(r"[\u4e00-\u9fff]", describe_form(row, "v0.59").short)
                for row in note_rows
            )
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
        self.assertTrue(any("通道 0" in item for item in brg.details))
        self.assertFalse(any("TSO ordering domain" in item for item in brg.details))
        immediate = describe_form(self.row("v0.59", "V.LWI"), "v0.59")
        self.assertTrue(
            any(
                "同一地址" in item or "一个有效地址" in item
                for item in immediate.details
            )
        )
        self.assertTrue(any("谓词位 2*i" in item for item in immediate.details))
        for mnemonic in ("C.BSTART.VPAR", "C.BSTART.VSEQ"):
            semantic = describe_form(self.row("v0.59", mnemonic), "v0.59")
            self.assertNotIn("FALL 字段", semantic.description)
            self.assertTrue(
                any("没有独立的 FALL 物理字段" in item for item in semantic.details)
            )

    def test_vector_logical_compare_booleanizes_each_operand(self) -> None:
        # (1 & 2) is zero, while both operands are nonzero. This distinguishes
        # the tagged Sail boolean rule from the former bitwise interpretation.
        self.assertEqual(1 & 2, 0)
        self.assertEqual(_logical_compare_result("AND", 1, 2), 1)
        self.assertEqual(_logical_compare_result("ANDI", 1, 2), 1)
        self.assertEqual(_logical_compare_result("OR", 0, 2), 1)
        self.assertEqual(_logical_compare_result("ORI", 0, 0), 0)
        tagged_sail = subprocess.check_output(
            ["git", "show", "refs/tags/v0.59.1:isa/sail/model/execute/execute.sail"],
            cwd=ROOT,
            text=True,
        )
        self.assertIn("let a = vec_get_lane32(lhs, i) != 0x0000_0000;", tagged_sail)
        self.assertIn("let b = imm != 0x0000_0000;", tagged_sail)
        self.assertIn("vec_bool32(a & b)", tagged_sail)
        self.assertIn("vec_bool32(a | b)", tagged_sail)
        for mnemonic in ("V.CMP.AND", "V.CMP.ANDI", "V.CMP.OR", "V.CMP.ORI"):
            semantic = describe_form(self.row("v0.59", mnemonic), "v0.59")
            self.assertIn("分别判非零", semantic.short)
            self.assertNotIn("按位", semantic.short)
            self.assertTrue(
                any("(1, 2) 的结果是 1" in item for item in semantic.details)
            )
            self.assertTrue(
                any(
                    "execute.sail#L3899-L3964" in source
                    for source in semantic.provenance
                )
            )
        self.assertTrue(
            any(
                "simm12 符号扩展" in item
                for item in describe_form(
                    self.row("v0.59", "V.CMP.ANDI"), "v0.59"
                ).details
            )
        )

    def test_other_derived_vector_details_match_tagged_sail(self) -> None:
        for mnemonic in ("V.SLL", "V.SRLI", "V.SRAI"):
            self.assertTrue(
                any(
                    "有效整数位宽取模" in item
                    for item in describe_form(
                        self.row("v0.59", mnemonic), "v0.59"
                    ).details
                )
            )
        for mnemonic in ("V.MUL", "V.MADD"):
            semantic = describe_form(self.row("v0.59", mnemonic), "v0.59")
            self.assertIn("无符号整数", semantic.short)
            self.assertTrue(any("无符号整数" in item for item in semantic.details))
        psel = describe_form(self.row("v0.59", "V.PSEL"), "v0.59")
        self.assertTrue(any("不读取执行掩码 p" in item for item in psel.details))
        for mnemonic in ("V.LD.MAX", "V.SW.MIN"):
            atomic = describe_form(self.row("v0.59", mnemonic), "v0.59")
            self.assertIn("有符号", atomic.short)
            self.assertTrue(any("有符号整数顺序" in item for item in atomic.details))

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
