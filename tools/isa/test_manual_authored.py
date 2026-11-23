#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

from tools.isa.manual_authored import (
    authored_for,
    authored_tile,
    coverage_report,
    source_inventory,
    tile_source_inventory,
)


class ManualAuthoredTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "isa/v0.59/linxisa-v0.59.json").read_text())

    def row(self, mnemonic):
        return next(
            row
            for row in self.catalog["instructions"]
            if row["mnemonic"] == mnemonic and not row.get("pto_scope")
        )

    def test_tagged_instruction_inventory_and_mapping(self):
        inventory = source_inventory()
        self.assertEqual(len(inventory), 811)
        self.assertEqual(sum(mapped for _, _, mapped in inventory), 642)
        mapped_forms = [
            row
            for row in self.catalog["instructions"]
            if not row.get("pto_scope") and authored_for(row)
        ]
        self.assertEqual(len(mapped_forms), 787)
        missing = {
            row["mnemonic"]
            for row in self.catalog["instructions"]
            if not row.get("pto_scope") and authored_for(row) is None
        }
        self.assertEqual(
            missing,
            {
                "B.ASSEMBLE",
                "B.FPATR",
                "B.SUBVIEW",
                "BSTART.TIMG2COL",
                "FENCE.D",
                "FENCE.I",
                "SYNC.CORE",
            },
        )

    def test_c_movr_preserves_full_original_sections_and_cursor_examples(self):
        article = authored_for(self.row("C.MOVR"))
        self.assertIsNotNone(article)
        self.assertEqual(article.classification, "syntax-compatible-original")
        self.assertEqual(article.source_path, "docs/zh/isa/inst/misa_c/C.MOVR.md")
        self.assertEqual(
            [section.heading for section in article.sections],
            [
                "说明",
                "汇编语法",
                "汇编符号",
                "编码格式",
                "执行方式",
                "汇编索引模式",
                "备注",
            ],
        )
        self.assertIn("将源寄存器值移动到目的寄存器中", article.intro)
        self.assertEqual(len(article.examples), 3)
        self.assertTrue(
            any("t#1" in example and "u#1" in example for example in article.examples)
        )
        self.assertIn("汇编索引模式", article.headings)

    def test_dc_iall_drift_is_blocked_and_current_view_is_explicit(self):
        article = authored_for(self.row("DC.IALL"))
        self.assertIsNotNone(article)
        self.assertEqual(article.classification, "conflicting-current")
        self.assertTrue(any("SrcL" in reason for reason in article.reasons))
        current = " ".join(article.current_view)
        self.assertIn("0x0010602b", current)
        self.assertIn("没有 SrcL", current)
        self.assertIn("Maintenance_DC_IALL", current)
        self.assertIn("TPC 前进 4 字节", current)

    def test_ccat_authored_preamble_and_release_difference(self):
        for name in ("HL.CCAT", "HL.CCATW"):
            article = authored_for(self.row(name))
            self.assertIn("拼接", article.intro)
            self.assertEqual(article.classification, "conflicting-current")
            self.assertIn("逻辑右移", " ".join(article.current_view))
            self.assertIn("循环左移", " ".join(article.reasons))
        self.assertNotIn("<br", authored_for(self.row("V.ADD")).intro.lower())

    def test_known_vector_semantic_conflicts_are_scoped(self):
        for mnemonic in ("V.CMP.AND", "V.CMP.ANDI"):
            article = authored_for(self.row(mnemonic))
            self.assertEqual(article.classification, "conflicting-current")
            self.assertTrue(
                any(
                    "按位 AND" in reason and "布尔 AND" in reason
                    for reason in article.reasons
                )
            )
            self.assertIn("SrcL=1", " ".join(article.current_view))
            self.assertIn("未指定", " ".join(article.current_view))
            self.assertIn(
                "按位与运算", " ".join(section.markdown for section in article.sections)
            )
        reverse = authored_for(self.row("V.REV"))
        self.assertEqual(reverse.classification, "conflicting-current")
        self.assertIn("bswap32", " ".join(reverse.current_view))
        self.assertIn("忽略编码中的 immr/imml", " ".join(reverse.current_view))
        self.assertIn("M/N 位域翻转", " ".join(reverse.current_view))

    def test_scalar_cmp_and_remains_bitwise_and_c_movr_primary(self):
        scalar = authored_for(self.row("CMP.AND"))
        self.assertNotEqual(scalar.classification, "conflicting-current")
        chinese = json.loads(
            (
                ROOT
                / "docs/architecture/isa-manual/reference/data/manual-semantics-zh.json"
            ).read_text()
        )["forms"]
        record = chinese[self.row("CMP.AND")["pto_source_form_id"]]
        mechanism = " ".join(record["roles"]["mechanism"]["statements"])
        self.assertIn("left AND right", mechanism)
        self.assertIn("逻辑结果非零", mechanism)
        cmovr = authored_for(self.row("C.MOVR"))
        self.assertEqual(cmovr.source_path, "docs/zh/isa/inst/misa_c/C.MOVR.md")
        self.assertEqual(cmovr.classification, "syntax-compatible-original")

    def test_bad_h1_and_historical_unmapped_docs_do_not_alias(self):
        article = authored_for(self.row("HL.DIVU"))
        self.assertEqual(article.source_path, "docs/zh/isa/inst/misa_h/HL.DIVU.md")
        self.assertEqual(article.title, "DIVU")
        self.assertEqual(article.classification, "contextual-original")
        historical = next(
            item for item in source_inventory() if item[0].endswith("/misa_l/L.ADD.md")
        )
        self.assertFalse(historical[2])
        grouped = authored_for(self.row("C.BSTART.FP"))
        self.assertEqual(grouped.source_path, "docs/zh/isa/header/C.BSTART.md")
        self.assertEqual(grouped.classification, "contextual-original")
        self.assertTrue(any("分组或替代拼写" in reason for reason in grouped.reasons))
        carrier = authored_for(self.row("BSTART.TLOAD"))
        self.assertEqual(carrier.source_path, "docs/zh/isa/header/tileblock/TLOAD.md")
        self.assertEqual(carrier.classification, "contextual-original")
        self.assertTrue(any("关联到原文分组" in reason for reason in carrier.reasons))

    def test_tile_articles_are_contextual_and_cover_alias_groups(self):
        direct = authored_tile("TADD")
        self.assertEqual(direct.source_path, "docs/zh/isa/header/tileblock/TADD.md")
        self.assertEqual(direct.classification, "contextual-original")
        self.assertTrue(direct.sections)
        self.assertIn("TADD", direct.title)
        alias = authored_tile("TMATMUL_MX_ACC")
        self.assertEqual(
            alias.source_path, "docs/zh/isa/header/tileblock/TMATMULMX.ACC.md"
        )
        self.assertTrue(any("历史分组页面" in reason for reason in alias.reasons))
        gather = authored_tile("MGATHER_ADD")
        self.assertEqual(gather.source_path, "docs/zh/isa/header/tileblock/MGATHER.md")
        self.assertIsNone(authored_tile("TFMA"))
        operations = json.loads(
            (ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )["operations"]
        missing = {op["name"] for op in operations if authored_tile(op["name"]) is None}
        self.assertEqual(
            missing,
            {
                "TFMA",
                "TROWARGMAX",
                "TROWARGMIN",
                "TCOLARGMAX",
                "TCOLARGMIN",
                "TCI",
                "TTRI",
                "GMOV",
                "TPERMUTE",
                "TSHUF",
                "TPACK",
                "TUNPACK",
                "TGPR2T",
                "TEXPDIF",
                "TLEA",
            },
        )

    def test_all_sources_are_exact_reviewed_tag_links(self):
        for mnemonic in ("C.MOVR", "DC.IALL", "HL.DIVU"):
            article = authored_for(self.row(mnemonic))
            self.assertIn(
                "/blob/d262515b55c727073997c8f4c95261909f2fe8d3/", article.source_url
            )
        self.assertIn(
            "/blob/d262515b55c727073997c8f4c95261909f2fe8d3/",
            authored_tile("TLOAD").source_url,
        )

    def test_coverage_report_counts_every_source_family(self):
        report = coverage_report()
        self.assertEqual(report["instruction_source_articles"], 811)
        self.assertEqual(report["instruction_forms"], 794)
        self.assertEqual(report["mapped_instruction_forms"], 787)
        self.assertEqual(report["mapped_instruction_mnemonics"], 747)
        self.assertEqual(sum(report["classification_counts"].values()), 787)
        self.assertEqual(
            report["classification_counts"],
            {
                "conflicting-current": 36,
                "contextual-original": 414,
                "syntax-compatible-original": 337,
            },
        )
        self.assertEqual(report["tile_source_articles"], 89)
        self.assertEqual(report["tile_operations"], 119)
        self.assertEqual(report["mapped_tile_operations"], 104)
        self.assertEqual(len(tile_source_inventory()), 89)

    def test_inventory_is_independent_of_process_working_directory(self):
        script = (
            "import json; from tools.isa.manual_authored import coverage_report; "
            "print(json.dumps(coverage_report(), sort_keys=True))"
        )
        output = subprocess.check_output(
            [sys.executable, "-c", script],
            cwd=ROOT / "docs/architecture/isa-manual",
            env={"PYTHONPATH": str(ROOT)},
            text=True,
        )
        report = json.loads(output)
        self.assertEqual(report["mapped_instruction_forms"], 787)
        self.assertEqual(report["mapped_tile_operations"], 104)
        self.assertEqual(report["instruction_source_articles"], 811)


if __name__ == "__main__":
    unittest.main()
