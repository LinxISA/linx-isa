#!/usr/bin/env python3
from __future__ import annotations
import copy, json, unittest
from pathlib import Path
from manual_encoding import render_encoding, validate_catalog, validate_encoding
from check_html_reference import (
    Parser,
    actual_operand_rows,
    english_visible_fragments,
    expected_operand_rows,
)

ROOT = Path(__file__).resolve().parents[2]


class ManualEncodingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "isa/v0.59/linxisa-v0.59.json").read_text())
        cls.baseline = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text())

    def test_every_released_v0591_form_validates_and_renders(self):
        for row in self.catalog["instructions"]:
            with self.subTest(form=row["id"]):
                validate_encoding(row, self.catalog)
                html = render_encoding(row, self.catalog)
                self.assertIn(str(row["encoding"]["parts"][0]["mask"]), html)
                parser = Parser()
                parser.feed(html)
                self.assertEqual(english_visible_fragments(parser.root), [])
                tables = parser.root.find(tag="table", cls="encoding-operands")
                expected = expected_operand_rows(row)
                self.assertEqual(len(tables), 1 if expected else 0)
                if expected:
                    self.assertEqual(actual_operand_rows(tables[0]), expected)

    def test_full_catalog_source_and_baseline_audit(self):
        self.assertEqual(validate_catalog(self.catalog, self.baseline), [])

    def test_rejects_catalog_mask_divergence_from_exact_pto_source(self):
        row = copy.deepcopy(
            next(r for r in self.catalog["instructions"] if r.get("pto_source_form_id"))
        )
        row["encoding"]["parts"][0]["mask"] = "0x00000000"
        with self.assertRaises(ValueError):
            validate_encoding(row, self.catalog)

    def test_rejects_operand_bit_move_even_when_widths_are_preserved(self):
        row = copy.deepcopy(
            next(
                r
                for r in self.catalog["instructions"]
                if r["mnemonic"] == "CASB" and r["encoding_kind"] == "SCOPED64"
            )
        )
        fields = row["encoding"]["parts"][1]["fields"]
        srcd = next(field for field in fields if field["name"] == "SrcD")
        srcr = next(field for field in fields if field["name"] == "SrcR")
        srcd["name"], srcr["name"] = srcr["name"], srcd["name"]
        with self.assertRaisesRegex(ValueError, "operand bit mapping differs"):
            validate_encoding(row, self.catalog)

    def test_constraints_are_form_local_not_global_reserved_values(self):
        row = next(
            r for r in self.catalog["instructions"] if r["mnemonic"] == "B.FPATR"
        )
        html = render_encoding(row, self.catalog)
        self.assertIn("源定义固定字段", html)
        self.assertNotIn("保留编码值", html)

    def test_tepl_uses_published_composite_selector_domain(self):
        row = next(
            r for r in self.catalog["instructions"] if r["mnemonic"] == "BSTART.TEPL"
        )
        html = render_encoding(row, self.catalog)
        self.assertIn("128 个组合选择器中的 79 个", html)
        self.assertIn("其余 49 个未列出的 Mode / Function 组合均为保留编码", html)
        self.assertIn("TADD", html)
        self.assertIn("github.com/PTO-ISA/pto-spec/blob/a89a53d", html)

    def test_scoped_split_field_table_aggregates_all_parts(self):
        row = next(
            r
            for r in self.catalog["instructions"]
            if r["mnemonic"] == "CASB" and r["encoding_kind"] == "SCOPED64"
        )
        expected = {item["field"]: item for item in expected_operand_rows(row)}
        self.assertEqual(expected["SrcL"]["width"], 5)
        self.assertEqual(
            expected["SrcL"]["mapping"],
            "P0[31] / I[31] → 字段值[0], P1[3:0] / I[35:32] → 字段值[4:1]",
        )
        parser = Parser()
        parser.feed(render_encoding(row, self.catalog))
        actual = {
            item["field"]: item
            for item in actual_operand_rows(
                parser.root.find(tag="table", cls="encoding-operands")[0]
            )
        }
        self.assertEqual(actual["SrcL"], expected["SrcL"])

    def test_chinese_encoding_ui_across_instruction_families(self):
        for mnemonic in ("DC.IALL", "B.TEXT", "BSTART.TEPL", "CASB"):
            row = next(
                r
                for r in self.catalog["instructions"]
                if r["mnemonic"] == mnemonic and r.get("pto_scope") is None
            )
            with self.subTest(mnemonic=mnemonic):
                parser = Parser()
                parser.feed(render_encoding(row, self.catalog))
                headers = [node.text() for node in parser.root.find(tag="th")]
                if parser.root.find(tag="table", cls="encoding-operands"):
                    self.assertEqual(
                        headers[:4],
                        ["字段", "位宽", "指令位与字段值映射", "符号属性"],
                    )
                exact_labels = [node.text() for node in parser.root.find(tag="dt")]
                self.assertIn("掩码（Mask）", exact_labels)
                self.assertIn("匹配值（Match）", exact_labels)
                self.assertIn("位模式（Pattern）", exact_labels)
                self.assertNotIn("Instruction/value mapping", parser.root.text())
                self.assertNotIn(
                    "Published Mode/Function selectors", parser.root.text()
                )

    def test_dc_iall_groups_display_bits_but_preserves_raw_pattern(self):
        row = next(
            r for r in self.catalog["instructions"] if r["mnemonic"] == "DC.IALL"
        )
        html = render_encoding(row, self.catalog)
        self.assertIn("第 0 段（Part 0）", html)
        self.assertIn("0000 0000 0001 0000 0110 0000 0010 1011", html)
        self.assertIn("<dt>位模式（Pattern）</dt>", html)
        self.assertIn("<code>00000000000100000110000000101011</code>", html)


if __name__ == "__main__":
    unittest.main()
