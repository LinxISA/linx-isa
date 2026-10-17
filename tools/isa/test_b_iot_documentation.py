#!/usr/bin/env python3
"""Regression checks for the bilingual PTO ISA v0.58 B.IOT page."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class BIotDocumentationTests(unittest.TestCase):
    def test_catalog_and_bilingual_pages_publish_the_exact_golden_forms(self) -> None:
        spec = json.loads(
            (ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8")
        )
        forms = [row for row in spec["instructions"] if row["mnemonic"] == "B.IOT"]
        self.assertEqual(len(forms), 13)
        expected_assembly = {row["asm"] for row in forms}
        for path in (
            ROOT / "docs/isa/header/B.IOT.md",
            ROOT / "docs/zh/isa/header/B.IOT.md",
        ):
            text = path.read_text(encoding="utf-8")
            for assembly in expected_assembly:
                self.assertIn(assembly, text)
            self.assertIn(".reuse", text)
            self.assertIn("PTO-SPEC golden", text)
            for form in forms:
                self.assertIn(form["pto_source_form_id"], text)
                self.assertIn(form["encoding"]["parts"][0]["mask"], text)
                self.assertIn(form["encoding"]["parts"][0]["match"], text)

    def test_navigation_uses_the_bilingual_special_page(self) -> None:
        self.assertIn(
            "isa/header/B.IOT.md",
            (ROOT / "mkdocs.zh.yml").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
