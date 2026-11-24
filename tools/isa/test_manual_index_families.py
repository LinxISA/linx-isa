#!/usr/bin/env python3
"""Regression tests for mnemonic-specific index synopses."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_index_families import family_index_synopsis, overridden_mnemonics
from manual_tag import SIGNED_TAG_COMMIT, tagged_bytes, verified_tag_commit


class IndexFamilySynopsisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            Path("isa/v0.59/linxisa-v0.59.json").read_text(encoding="utf-8")
        )

    def test_exact_reviewed_tag_and_coverage(self) -> None:
        self.assertEqual(verified_tag_commit(), SIGNED_TAG_COMMIT)
        catalogued = {row["mnemonic"] for row in self.catalog["instructions"]}
        self.assertEqual(len(overridden_mnemonics()), 2)
        self.assertLessEqual(overridden_mnemonics(), catalogued)

    def test_scalar_copy_paste_is_replaced_by_the_selected_operation(self) -> None:
        lti = family_index_synopsis("HL.SETC.LTI")
        ori = family_index_synopsis("HL.SETC.ORI")
        self.assertIn("有符号小于", lti)
        self.assertNotIn("大于等于", lti)
        self.assertIn("按位或", ori)
        self.assertNotIn("大于等于", ori)
        source = tagged_bytes("docs/zh/isa/inst/misa_h/HL.SETC.LTI.md").decode()
        self.assertIn("满足 `SrcL < (simm24 << shamt)`", source)

    def test_unknown_mnemonic_has_no_override(self) -> None:
        self.assertEqual(family_index_synopsis("V.ADD"), "")


if __name__ == "__main__":
    unittest.main()
