#!/usr/bin/env python3
"""Checks for LinxISA v0.59.1 release preparation metadata."""

from __future__ import annotations

import hashlib
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
from linxisa_v0591_qualification import (
    COMPONENT_LOCK,
    PTO_LOCK,
    RECEIPT,
    REQUIRED_REPORTS,
    qualification_reference,
)


class LinxISAV0591ReleasePrepTest(unittest.TestCase):
    def test_manifest_is_deterministic_and_tracks_qualification(self):
        meta, manifest = build()
        self.assertEqual((meta, manifest), build())
        qualification = qualification_reference()
        qualified = qualification is not None
        self.assertEqual(meta["status"], "active-release" if qualified else "inactive-prepublication")
        self.assertEqual(manifest["status"], "release-qualified" if qualified else "development-not-published")
        if qualified:
            self.assertEqual(manifest["publication"]["tag"], "v0.59.1")
            self.assertEqual(manifest["qualification"]["evidence"], qualification)
        else:
            self.assertIsNone(manifest["publication"])
        self.assertNotIn("component_pins", manifest)
        self.assertNotIn("tag", manifest)
        self.assertEqual(manifest["policy"]["default_profile_changed"], qualified)
        self.assertTrue(
            all(
                value is qualified
                for key, value in manifest["qualification"].items()
                if key.endswith("_qualified")
            )
        )
        self.assertEqual(
            _profile_defaults(),
            ("isa/v0.59", "isa/v0.59/linxisa-v0.59.json")
            if qualified else ("isa/v0.58", "isa/v0.58/linxisa-v0.58.json"),
        )
        self.assertEqual(
            _profile_defaults("v0.59"),
            ("isa/v0.59", "isa/v0.59/linxisa-v0.59.json"),
        )

    def test_qualification_rejects_failed_gates_and_changed_component_pins(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(qualification_reference(root))
            for lock in (COMPONENT_LOCK, PTO_LOCK):
                (root / lock).parent.mkdir(parents=True, exist_ok=True)
                (root / lock).write_bytes(b"fixture")
            lock_hash = hashlib.sha256(b"fixture").hexdigest()
            path = root / RECEIPT
            receipt = {
                "schema_version": 1,
                "profile": "v0.59",
                "version": "0.59.1",
                "verification_commit": "c" * 40,
                "component_lock_sha256": lock_hash,
                "pto_lock_sha256": lock_hash,
                "reports": {
                    name: {"status": "pass", "sha256": "d" * 64}
                    for name in REQUIRED_REPORTS
                },
            }
            path.write_text(json.dumps(receipt), encoding="utf-8")
            self.assertEqual(qualification_reference(root)["path"], RECEIPT.as_posix())
            receipt["reports"]["strict_cross_repo"]["status"] = "fail"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not a verified pass"):
                qualification_reference(root)
            receipt["reports"]["strict_cross_repo"]["status"] = "pass"
            path.write_text(json.dumps(receipt), encoding="utf-8")
            (root / COMPONENT_LOCK).write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "does not match"):
                qualification_reference(root)

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
