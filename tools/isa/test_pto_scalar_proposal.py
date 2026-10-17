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

    def test_golden_is_preserved_and_inventory_is_complete(self):
        original = copy.deepcopy(self.baseline)
        result = apply_proposal(self.profile, self.baseline)
        self.assertEqual(self.baseline, original)
        self.assertEqual(len(result["forms"]), 473)
        lr = next(form for form in result["forms"] if form["mnemonic"] == "LR.W")
        self.assertEqual(lr["encoding"][0]["match"], "0x1000000b")

    def test_modified_published_baseline_is_rejected(self):
        self.baseline["forms"][0]["semantic_summary"] = "modified"
        with self.assertRaisesRegex(ValueError, "differs from PTO golden"):
            apply_proposal(self.profile, self.baseline)

    def test_duplicate_form_and_published_identity_are_rejected(self):
        malformed = copy.deepcopy(self.baseline)
        malformed["forms"][0] = malformed["forms"][1]
        with self.assertRaisesRegex(ValueError, "differs from PTO golden"):
            apply_proposal(self.profile, malformed)
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory)
            lock = json.loads((self.profile / "pto-scalar-proposal.lock.json").read_text())
            lock["published_identity_compatible"] = True
            (profile / "pto-scalar-proposal.lock.json").write_text(json.dumps(lock))
            with self.assertRaisesRegex(ValueError, "published compatible identity"):
                apply_proposal(profile, self.baseline)


if __name__ == "__main__":
    unittest.main()
