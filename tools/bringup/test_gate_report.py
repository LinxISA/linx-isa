#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
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
                "linx-tileop-api",
                "model",
                "pycircuit",
                "glibc",
                "mesa3d",
                "musl",
                "pto-kernels",
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

    def test_retain_run_keeps_all_lanes_for_one_run_id(self) -> None:
        report = {
            "schema_version": gate_report.SCHEMA_VERSION,
            "generated_at_utc": "2026-07-15 00:00:00Z",
            "runs": [
                {"run_id": "old", "lane": "pin", "profile": "dev", "gates": []},
                {"run_id": "release", "lane": "pin", "profile": "release-strict", "gates": []},
                {"run_id": "release", "lane": "external", "profile": "release-strict", "gates": []},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "latest.json"
            gate_report._save_report(report_path, report)
            gate_report.cmd_retain_run(
                argparse.Namespace(report=str(report_path), run_id="release")
            )
            retained = json.loads(report_path.read_text())["runs"]
            self.assertEqual(
                [(run["lane"], run["run_id"]) for run in retained],
                [("external", "release"), ("pin", "release")],
            )


if __name__ == "__main__":
    unittest.main()
