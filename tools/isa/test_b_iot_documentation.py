#!/usr/bin/env python3
"""Regression checks for the bilingual PTO ISA v0.58 B.IOT page."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class BIotDocumentationTests(unittest.TestCase):
    def test_catalog_and_bilingual_pages_publish_the_exact_five_forms(self) -> None:
        spec = json.loads(
            (ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8")
        )
        forms = [row for row in spec["instructions"] if row["mnemonic"] == "B.IOT"]
        self.assertEqual(len(forms), 5)
        expected_assembly = {row["asm"] for row in forms}
        for path in (
            ROOT / "docs/isa/header/B.IOT.md",
            ROOT / "docs/zh/isa/header/B.IOT.md",
        ):
            text = path.read_text(encoding="utf-8")
            for assembly in expected_assembly:
                self.assertIn(assembly, text)
            for token in (
                "SizeCode",
                "PEMode",
                "18:15",
                "11:9",
                "8:7",
                "1..10",
                "11..15",
                "0000",
                "1111",
                "256 KiB",
            ):
                self.assertIn(token, text)
            self.assertNotIn("SrcTile0<.reuse>", text)
            self.assertNotIn("SrcTile1<.reuse>", text)
            self.assertNotIn("S0R", text)
            self.assertNotIn("S1R", text)
            self.assertNotIn("DstTile=3b111", text)

    def test_navigation_uses_the_bilingual_special_page(self) -> None:
        self.assertIn(
            "isa/header/B.IOT.md",
            (ROOT / "mkdocs.zh.yml").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
