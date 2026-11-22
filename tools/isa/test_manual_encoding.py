#!/usr/bin/env python3
from __future__ import annotations
import copy, json, unittest
from pathlib import Path
from manual_encoding import render_encoding, validate_catalog, validate_encoding

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
        self.assertIn("assigns 79 of 128 composite selectors", html)
        self.assertIn("remaining 49 unlisted Mode/Function pairs are reserved", html)
        self.assertIn("TADD", html)
        self.assertIn("github.com/PTO-ISA/pto-spec/blob/a89a53d", html)


if __name__ == "__main__":
    unittest.main()
