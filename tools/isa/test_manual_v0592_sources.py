#!/usr/bin/env python3

import json
from pathlib import Path
import re
import unittest

from tools.isa.manual_v0592_sources import sources_v0592


ROOT = Path(__file__).resolve().parents[2]


class ManualV0592SourcesTest(unittest.TestCase):
    def test_source_page_states_the_active_and_compatibility_boundaries(self):
        manifest = json.loads((ROOT / "isa/v0.59.2/release_manifest.json").read_text())
        lock = json.loads((ROOT / "isa/v0.59/pto-spec.lock.json").read_text())
        html = sources_v0592(
            "830fbdb53bccec889414b5673ffba31b0a08606d",
            {"instruction-forms.json": b"catalog"},
            manifest,
            lock,
        )
        for literal in ("1306", "561", "119", "v0.59.1", "DMA.FREE.L", "PTO"):
            self.assertIn(literal, html)
        self.assertIn("Tile VEC", html)
        self.assertNotIn("V.SH.BRG", html)
        self.assertNotIn("旧机器字", html)
        self.assertNotIn("obsolete", html)
        self.assertRegex(html, re.compile(r"spec/instruction-forms\.json"))

    def test_source_page_rejects_the_old_manifest(self):
        manifest = json.loads((ROOT / "isa/v0.59/release_manifest.json").read_text())
        lock = json.loads((ROOT / "isa/v0.59/pto-spec.lock.json").read_text())
        with self.assertRaisesRegex(ValueError, "requires the v0.59.2"):
            sources_v0592("deadbeef", {}, manifest, lock)

    def test_source_page_rejects_a_full_catalog_with_obsolete_rows(self):
        manifest = json.loads((ROOT / "isa/v0.59.2/release_manifest.json").read_text())
        lock = json.loads((ROOT / "isa/v0.59/pto-spec.lock.json").read_text())
        with self.assertRaisesRegex(ValueError, "must not package"):
            sources_v0592(
                "deadbeef",
                {"isa/v0.59.2/linxisa-v0.59.2.json": b"full"},
                manifest,
                lock,
            )


if __name__ == "__main__":
    unittest.main()
