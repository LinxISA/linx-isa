#!/usr/bin/env python3
"""Tests for the LinxISA v0.59.2 Sail and release packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from export_linxisa_v0592_sail import (  # noqa: E402
    check,
    export,
    release_package,
    render,
)
from export_linxisa_v0591_sail import export as export_v0591  # noqa: E402


class LinxISAV0592SailExportTest(unittest.TestCase):
    def test_export_binds_catalog_status_and_preserves_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sail"
            package = export(output)
            check(output)
            self.assertEqual(package["version"], "0.59.2")
            self.assertEqual(package["catalog"]["obsolete_form_count"], 193)
            self.assertEqual(
                package["identity"]["encoding_abi"],
                "pto-isa-0.59.1-mode-function-v1",
            )
            self.assertEqual(package["entry"], "model/linxisa_v0592.sail")
            self.assertTrue(
                package["execution_compatibility"][
                    "obsolete_forms_execute_with_v0591_semantics"
                ]
            )
            self.assertFalse(
                package["execution_compatibility"]["obsolete_trap_policy_decided"]
            )
            self.assertIn("model/decode/decode.sail", package["files"])

    def test_catalog_status_does_not_change_decode_or_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "v0592"
            baseline = Path(directory) / "v0591"
            export(output)
            export_v0591(baseline)
            current_decode = (output / "model/decode/decode.sail").read_text(
                encoding="utf-8"
            )
            baseline_decode = (baseline / "model/decode/decode.sail").read_text(
                encoding="utf-8"
            )
            self.assertEqual(
                current_decode.splitlines()[2:], baseline_decode.splitlines()[2:]
            )
            entry = (output / "model/linxisa_v0592.sail").read_text(encoding="utf-8")
            self.assertIn('$include "execute/v0591_candidate_dispatch.sail"', entry)

    def test_release_package_is_checked_in_and_binds_exact_inputs(self):
        expected = release_package()
        actual = json.loads(
            (ROOT / "isa/v0.59.2/release_package.json").read_text(encoding="utf-8")
        )
        self.assertEqual(actual, expected)
        self.assertEqual(render(expected), render(release_package()))
        self.assertEqual(expected["identity"]["linxisa_release"], "0.59.2")
        self.assertEqual(expected["identity"]["pto_release"], "0.59.1")
        self.assertEqual(expected["obsolete_policy"]["form_count"], 193)
        self.assertEqual(
            expected["obsolete_policy"]["binary_trap_policy"], "not-decided"
        )
        self.assertIn("isa/v0.59.2/linxisa-v0.59.2.json", expected["inputs"])
        self.assertIn("isa/sail/model/execute/execute.sail", expected["inputs"])
        self.assertTrue(expected["qualification"]["release_qualified"])
        self.assertTrue(expected["qualification"]["sail_package_qualified"])
        self.assertFalse(expected["qualification"]["platform_qualified"])
        self.assertEqual(
            expected["qualification"]["evidence"]["sail_validator"],
            "tools/isa/check_v0592_sail.py",
        )

    def test_check_rejects_manifest_metadata_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sail"
            export(output)
            manifest_path = output / "linxisa-v0592-sail-package.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for field, value in (
                ("version", "0.59.1"),
                ("catalog.sha256", "0" * 64),
                ("catalog.obsolete_form_count", 192),
            ):
                modified = json.loads(json.dumps(manifest))
                target = modified
                parts = field.split(".")
                for part in parts[:-1]:
                    target = target[part]
                target[parts[-1]] = value
                manifest_path.write_text(render(modified), encoding="utf-8")
                with self.subTest(field=field), self.assertRaises(ValueError):
                    check(output)
            manifest_path.write_text(render(manifest), encoding="utf-8")
            check(output)


if __name__ == "__main__":
    unittest.main()
