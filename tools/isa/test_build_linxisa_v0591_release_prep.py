#!/usr/bin/env python3
"""Checks for inactive LinxISA v0.59.1 release preparation metadata."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from build_linxisa_v0591_release_prep import build, render
from build_golden import _profile_defaults


class LinxISAV0591ReleasePrepTest(unittest.TestCase):
    def test_manifest_is_deterministic_and_explicitly_unqualified(self):
        meta, manifest = build()
        self.assertEqual((meta, manifest), build())
        self.assertEqual(meta["status"], "inactive-prepublication")
        self.assertEqual(manifest["status"], "development-not-published")
        self.assertIsNone(manifest["publication"])
        self.assertNotIn("component_pins", manifest)
        self.assertNotIn("tag", manifest)
        self.assertFalse(manifest["policy"]["default_profile_changed"])
        self.assertTrue(
            all(
                value is False
                for key, value in manifest["qualification"].items()
                if key.endswith("_qualified")
            )
        )
        self.assertEqual(
            _profile_defaults(),
            ("isa/v0.58", "isa/v0.58/linxisa-v0.58.json"),
        )
        self.assertEqual(
            _profile_defaults("v0.59"),
            ("isa/v0.59", "isa/v0.59/linxisa-v0.59.json"),
        )

    def test_manifest_binds_exact_lock_catalog_and_counts(self):
        meta, manifest = build()
        lock = json.loads(
            (ROOT / "isa/v0.59/pto-spec.lock.json").read_text(encoding="utf-8")
        )
        catalog = json.loads(
            (ROOT / "isa/v0.59/linxisa-v0.59.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["identity"]["release"], lock["release"])
        self.assertEqual(manifest["identity"]["encoding_abi"], lock["encoding_abi"])
        self.assertEqual(
            meta["cardinality"]["instructions"], catalog["instruction_count"]
        )
        self.assertEqual(manifest["cardinality"]["instructions"], 1499)
        self.assertEqual(
            {
                key: manifest["cardinality"][key]
                for key in ("common_forms", "linx_only_forms", "scoped_forms")
            },
            {"common_forms": 578, "linx_only_forms": 216, "scoped_forms": 705},
        )

    def test_checked_files_match_builder(self):
        meta, manifest = build()
        self.assertEqual(
            (ROOT / "isa/v0.59/meta.json").read_text(encoding="utf-8"), render(meta)
        )
        self.assertEqual(
            (ROOT / "isa/v0.59/release_manifest.json").read_text(encoding="utf-8"),
            render(manifest),
        )

    def test_build_golden_v059_write_is_byte_exact(self):
        expected = (ROOT / "isa/v0.59/linxisa-v0.59.json").read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/isa/build_golden.py"),
                    "--profile",
                    "v0.59",
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            self.assertEqual(output.read_bytes(), expected)
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/isa/build_golden.py"),
                    "--profile",
                    "v0.59",
                    "--out",
                    str(output),
                    "--check",
                ],
                cwd=ROOT,
                check=True,
            )


if __name__ == "__main__":
    unittest.main()
