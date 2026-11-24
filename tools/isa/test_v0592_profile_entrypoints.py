#!/usr/bin/env python3
"""Checks for the published, explicit LinxISA v0.59.2 profile entrypoints."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LinxISAV0592ProfileEntrypointsTest(unittest.TestCase):
    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_default_and_historical_profiles_are_unchanged(self):
        default = json.loads(
            self.run_tool("tools/isa/select_linxisa_profile.py").stdout
        )
        self.assertEqual(default["profile"], "v0.58")
        published = json.loads(
            self.run_tool(
                "tools/isa/select_linxisa_profile.py", "--profile", "v0.59"
            ).stdout
        )
        self.assertEqual(published["version"], "0.59.1")

    def test_v0592_is_published_explicit_and_release_qualified(self):
        selected = json.loads(
            self.run_tool(
                "tools/isa/select_linxisa_profile.py",
                "--profile",
                "v0.59.2",
                "--require-release-qualified",
            ).stdout
        )
        self.assertEqual(selected["state"], "published-explicit-profile")
        self.assertEqual(selected["version"], "0.59.2")
        self.assertEqual(
            selected["catalog"], "isa/v0.59.2/linxisa-v0.59.2.json"
        )
        self.assertTrue(selected["release_qualified"])
        self.assertFalse(selected["platform_qualified"])

    def test_normal_build_and_validation_entrypoints(self):
        self.assertEqual(
            self.run_tool(
                "tools/isa/build_golden.py", "--profile", "v0.59.2", "--check"
            ).stdout.strip(),
            "OK",
        )
        self.assertEqual(
            self.run_tool(
                "tools/isa/validate_spec.py", "--profile", "v0.59.2"
            ).stdout.strip(),
            "OK",
        )

    def test_v0592_profile_rejects_a_v0591_catalog(self):
        result = subprocess.run(
            [
                sys.executable,
                "tools/isa/validate_spec.py",
                "--profile",
                "v0.59.2",
                "--spec",
                "isa/v0.59/linxisa-v0.59.json",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires a catalog with version 0.59.2", result.stderr)

    def test_v0592_profile_rejects_a_missing_obsolete_marker(self):
        catalog = json.loads(
            (ROOT / "isa/v0.59.2/linxisa-v0.59.2.json").read_text(
                encoding="utf-8"
            )
        )
        row = next(
            row
            for row in catalog["instructions"]
            if row["mnemonic"] == "V.ADD"
        )
        row.pop("architecture_status")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "linxisa-v0.59.2.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/isa/validate_spec.py",
                    "--profile",
                    "v0.59.2",
                    "--spec",
                    str(path),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("architecture_status", result.stderr)


if __name__ == "__main__":
    unittest.main()
