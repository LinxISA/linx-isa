#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate_report


class GateReportTests(unittest.TestCase):
    def test_pin_manifest_covers_every_declared_leaf(self) -> None:
        paths = gate_report._pin_paths(Path("/repo"))
        self.assertEqual(
            set(paths),
            {
                "linx-isa",
                "llvm",
                "ptoas",
                "qemu",
                "linux",
                "linxcore",
                "linx-skills",
                "linxcore-model",
                "model",
                "pycircuit",
                "glibc",
                "mesa3d",
                "musl",
                "pto-kernels",
                "supernpu-bench",
            },
        )

    def test_atomic_report_and_render_round_trip(self) -> None:
        report = {
            "schema_version": gate_report.SCHEMA_VERSION,
            "generated_at_utc": "2026-07-15 00:00:00Z",
            "runs": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report_path = root / "latest.json"
            markdown_path = root / "GATE_STATUS.md"
            gate_report._save_report(report_path, report)
            loaded = gate_report._load_report(report_path)
            expected = gate_report._render_markdown(loaded)
            gate_report._atomic_write_text(markdown_path, expected)
            self.assertEqual(json.loads(report_path.read_text()), report)
            self.assertEqual(markdown_path.read_text(), expected)
            self.assertEqual(list(root.glob(".latest.json.*")), [])
            self.assertEqual(list(root.glob(".GATE_STATUS.md.*")), [])


if __name__ == "__main__":
    unittest.main()
