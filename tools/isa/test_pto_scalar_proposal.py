#!/usr/bin/env python3
"""Reject publication mutation and out-of-scope scalar proposal changes."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))
from pto_scalar_proposal import apply_proposal  # noqa: E402


class ScalarProposalTests(unittest.TestCase):
    def setUp(self):
        self.profile = ROOT / "isa/v0.58"
        self.baseline = json.loads((self.profile / "state/pto_scalar_forms.json").read_text())

    def test_baseline_is_preserved_and_effective_inventory_is_complete(self):
        original = copy.deepcopy(self.baseline)
        result = apply_proposal(self.profile, self.baseline)
        self.assertEqual(self.baseline, original)
        self.assertEqual(len(result["forms"]), 473)
        lr = next(form for form in result["forms"] if form["mnemonic"] == "LR.W")
        self.assertEqual(lr["encoding"][0]["match"], "0x1000000b")

    def test_modified_published_baseline_is_rejected(self):
        self.baseline["forms"][0]["semantic_summary"] = "modified"
        with self.assertRaisesRegex(ValueError, "baseline was modified"):
            apply_proposal(self.profile, self.baseline)

    def test_duplicate_or_out_of_scope_proposals_are_rejected(self):
        proposal = json.loads((self.profile / "state/pto_scalar_proposal.json").read_text())
        for mutation in ("duplicate", "scope", "additional"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                edited = copy.deepcopy(proposal)
                if mutation == "duplicate":
                    edited["forms"][0] = edited["forms"][1]
                elif mutation == "scope":
                    edited["forms"][0]["mnemonic"] = "ADD"
                else:
                    edited["additional_forms"].pop()
                profile = Path(directory)
                (profile / "state").mkdir()
                (profile / "state/pto_scalar_proposal.json").write_text(json.dumps(edited))
                (profile / "pto-scalar-proposal.lock.json").write_bytes(
                    (self.profile / "pto-scalar-proposal.lock.json").read_bytes()
                )
                with self.assertRaises(ValueError):
                    apply_proposal(profile, self.baseline)


if __name__ == "__main__":
    unittest.main()
