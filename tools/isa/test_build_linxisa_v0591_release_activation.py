#!/usr/bin/env python3
"""Tests for LinxISA v0.59.1 release selection and packaging."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from build_linxisa_v0591_release_activation import build, render
from export_linxisa_v0591_sail import check as check_sail_export
from export_linxisa_v0591_sail import export as export_sail


class LinxISAV0591ReleaseActivationTest(unittest.TestCase):
    def test_package_is_deterministic_and_prepublication(self):
        selection, package = build()
        self.assertEqual((selection, package), build())
        self.assertEqual(selection["default_profile"], "v0.58")
        self.assertEqual(selection["profiles"]["v0.59"]["state"], "selectable-prepublication")
        self.assertFalse(selection["profiles"]["v0.59"]["release_qualified"])
        self.assertEqual(package["state"], "prepared-prepublication")
        self.assertFalse(package["publication_allowed"])
        self.assertTrue(package["activation_policy"]["explicit_profile_ready"])
        self.assertTrue(
            package["activation_policy"][
                "published_default_switch_requires_release_qualification"
            ]
        )
        self.assertFalse(package["qualification"]["release_qualified"])
        self.assertIsNone(package["qualification"]["evidence"])

    def test_package_binds_full_catalog_and_candidate_sail(self):
        _selection, package = build()
        self.assertEqual(package["catalog"]["instruction_count"], 1499)
        self.assertEqual(
            package["catalog"]["counts"],
            {"common": 578, "linx_only": 216, "scoped": 705},
        )
        self.assertEqual(
            package["sail"]["entry"],
            "model/linxisa_v0591.sail",
        )
        self.assertEqual(
            package["sail"]["exporter"],
            "tools/isa/export_linxisa_v0591_sail.py",
        )
        self.assertEqual(
            package["identity"]["encoding_abi"],
            "pto-isa-0.59.1-mode-function-v1",
        )
        self.assertIn("isa/sail/model/state/state.sail", package["inputs"])
        self.assertIn("isa/sail/model/linxisa.sail", package["inputs"])

    def test_checked_files_match_builder(self):
        selection, package = build()
        self.assertEqual(
            (ROOT / "isa/profile-selection.json").read_text(encoding="utf-8"),
            render(selection),
        )
        self.assertEqual(
            (ROOT / "isa/v0.59/release_package.json").read_text(encoding="utf-8"),
            render(package),
        )

    def test_sail_export_materializes_canonical_entry_and_decoder(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sail"
            package = export_sail(output)
            check_sail_export(output)
            self.assertEqual(package["entry"], "model/linxisa_v0591.sail")
            self.assertEqual(package["catalog"]["instruction_count"], 1499)
            self.assertIn("model/decode/decode.sail", package["files"])
            self.assertIn("model/linxisa_v0591.sail", package["files"])

    def test_selector_requires_explicit_prepublication_opt_in(self):
        command = [sys.executable, "tools/isa/select_linxisa_profile.py"]
        default = subprocess.run(
            command, cwd=ROOT, check=True, capture_output=True, text=True
        )
        self.assertEqual(json.loads(default.stdout)["profile"], "v0.58")
        blocked = subprocess.run(
            [*command, "--profile", "v0.59"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(blocked.returncode, 0)
        selected = subprocess.run(
            [*command, "--profile", "v0.59", "--allow-prepublication"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(selected.stdout)["state"], "selectable-prepublication")
        qualified = subprocess.run(
            [
                *command,
                "--profile",
                "v0.59",
                "--allow-prepublication",
                "--require-release-qualified",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(qualified.returncode, 0)


if __name__ == "__main__":
    unittest.main()
