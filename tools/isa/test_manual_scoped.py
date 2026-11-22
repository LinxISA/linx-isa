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
            self.assertIn("shareability request", summary)
            self.assertIn("not a standalone visibility prohibition", detail)
            self.assertIn("source TPC + 8", detail)
            self.assertIn("without consuming an entry", detail)
        signed = next(row for row in rows if row["mnemonic"] == "C.LWI")
        self.assertIn("sign-extends", scoped_detail(signed))

    def test_all_tile_pages_have_specific_source_and_contract(self):
        ops = json.loads(
            (ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )["operations"]
        for op in ops:
            self.assertNotIn("semantic handler", tile_summary(op).lower())
            detail = tile_detail(op)
            self.assertIn("github.com/PTO-ISA/pto-spec/blob/a89a53d", detail)
            self.assertIn("Legality", detail)
            self.assertIn("State effects", detail)


if __name__ == "__main__":
    unittest.main()
