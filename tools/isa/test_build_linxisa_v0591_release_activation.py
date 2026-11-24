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

from build_linxisa_v0591_release_activation import build
from export_linxisa_v0591_sail import check as check_sail_export
from export_linxisa_v0591_sail import export as export_sail
from check_linxisa_v0591_release_compat import check as check_release_compat


class LinxISAV0591ReleaseActivationTest(unittest.TestCase):
    def test_package_is_deterministic_and_published_for_specification(self):
        selection, package = build()
        self.assertEqual((selection, package), build())
        self.assertEqual(selection["default_profile"], "v0.58")
        self.assertEqual(selection["profiles"]["v0.59"]["state"], "published-explicit-profile")
        self.assertTrue(selection["profiles"]["v0.59"]["release_qualified"])
        self.assertFalse(selection["profiles"]["v0.59"]["platform_qualified"])
        self.assertEqual(package["state"], "published-specification")
        self.assertTrue(package["publication_allowed"])
        self.assertTrue(package["activation_policy"]["explicit_profile_ready"])
        self.assertTrue(
            package["activation_policy"][
                "published_default_switch_requires_platform_qualification"
            ]
        )
        self.assertTrue(package["qualification"]["release_qualified"])
        self.assertTrue(package["qualification"]["specification_qualified"])
        self.assertFalse(package["qualification"]["platform_qualified"])
        self.assertIsNotNone(package["qualification"]["evidence"])

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
        self.assertIn("isa/v0.59/state/pto_tile_operations.json", package["inputs"])
        lock = json.loads(
            (ROOT / "isa/v0.59/pto-spec.lock.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            package["upstream_source_hashes"]["tile_operations"]["sha256"],
            lock["catalogs"]["tile_operations"]["sha256"],
        )
        self.assertNotEqual(
            package["inputs"]["isa/v0.59/state/pto_tile_operations.json"],
            package["upstream_source_hashes"]["tile_operations"]["sha256"],
        )

    def test_checked_files_match_builder(self):
        self.assertEqual(check_release_compat(), [])

    def test_sail_export_materializes_canonical_entry_and_decoder(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sail"
            package = export_sail(output)
            check_sail_export(output)
            self.assertEqual(package["entry"], "model/linxisa_v0591.sail")
            self.assertEqual(package["catalog"]["instruction_count"], 1499)
            self.assertIn("model/decode/decode.sail", package["files"])
            self.assertIn("model/linxisa_v0591.sail", package["files"])

    def test_selector_keeps_published_profile_explicit_but_selectable(self):
        command = [sys.executable, "tools/isa/select_linxisa_profile.py"]
        default = subprocess.run(
            command, cwd=ROOT, check=True, capture_output=True, text=True
        )
        self.assertEqual(json.loads(default.stdout)["profile"], "v0.58")
        selected = subprocess.run(
            [*command, "--profile", "v0.59"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(selected.stdout)["state"], "published-explicit-profile")
        qualified = subprocess.run(
            [
                *command,
                "--profile",
                "v0.59",
                "--require-release-qualified",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertTrue(json.loads(qualified.stdout)["release_qualified"])

    def test_legacy_activation_cli_preserves_extended_registry_and_package(self):
        command = [
            sys.executable,
            "tools/isa/build_linxisa_v0591_release_activation.py",
        ]
        before_selection = (ROOT / "isa/profile-selection.json").read_bytes()
        before_package = (ROOT / "isa/v0.59/release_package.json").read_bytes()
        checked = subprocess.run(
            [*command, "--check"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("immutable release", checked.stdout)
        preserved = subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("preserved immutable v0.59.1 package", preserved.stdout)
        self.assertEqual(
            (ROOT / "isa/profile-selection.json").read_bytes(), before_selection
        )
        self.assertEqual(
            (ROOT / "isa/v0.59/release_package.json").read_bytes(), before_package
        )


if __name__ == "__main__":
    unittest.main()
