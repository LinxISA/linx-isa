#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_48bit_implementation as report48
import report_isa_llvm_qemu_coverage as coherence


def _valid_l1_report() -> dict[str, object]:
    return {
        "schema_version": "qemu-isa-coverage-v3",
        "evidence_level": "L1",
        "claim": "decoder_source_mapping",
        "coverage_count": 1,
        "form_coverage_count": 1,
        "evidence": {
            "L1": {
                "availability": "available",
                "mnemonic_count": 1,
                "form_count": 1,
            },
            "L2": {"availability": "unavailable"},
            "L3": {"availability": "unavailable"},
        },
    }


class CoverageEvidenceConsumerTests(unittest.TestCase):
    def test_consumers_require_explicit_l1_claim(self) -> None:
        valid = _valid_l1_report()
        self.assertIsNone(coherence._validate_qemu_l1_report(valid))
        self.assertIsNone(report48._validate_qemu_l1_report(valid))

        for field, value in (
            ("schema_version", "qemu-isa-coverage-v2"),
            ("evidence_level", "L2"),
            ("claim", "executable_semantics"),
        ):
            with self.subTest(field=field):
                invalid = _valid_l1_report()
                invalid[field] = value
                self.assertIsNotNone(coherence._validate_qemu_l1_report(invalid))
                self.assertIsNotNone(report48._validate_qemu_l1_report(invalid))

    def test_downstream_markdown_keeps_l1_scope(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            coherence_path = root / "coherence.md"
            coherence._render_markdown(
                {
                    "generated_at_utc": "now",
                    "spec_unique_mnemonics": 1,
                    "qemu_evidence": _valid_l1_report()["evidence"],
                    "llvm": {"coverage_count": 1, "coverage_ratio_percent": 100.0},
                    "qemu_l1_mapping": {"coverage_count": 1, "coverage_ratio_percent": 100.0},
                    "qemu_translation": {"coverage_count": 1, "coverage_ratio_percent": 100.0},
                    "inconsistencies": {
                        "compiler_only_vs_qemu_l1_mapping_count": 0,
                        "qemu_l1_mapping_only_vs_translation_count": 0,
                        "translation_without_qemu_l1_mapping_count": 0,
                        "compiler_only_vs_translation_count": 0,
                        "compiler_only_vs_qemu_l1_mapping_by_prefix": [],
                        "qemu_l1_mapping_only_vs_translation_by_prefix": [],
                        "compiler_only_vs_translation_by_prefix": [],
                        "compiler_only_vs_qemu_l1_mapping": [],
                        "compiler_only_vs_translation": [],
                    },
                },
                coherence_path,
            )
            text = coherence_path.read_text(encoding="utf-8")
            self.assertIn("QEMU L1 decoder/source mapping", text)
            self.assertIn("does not claim runtime or semantic completeness", text)
            self.assertNotIn("mapped implementation", text.lower())

            report48_path = root / "48bit.md"
            report48._render_markdown(
                {
                    "generated_at_utc": "now",
                    "spec": {"form_count": 1, "mnemonic_count": 1},
                    "qemu_evidence": _valid_l1_report()["evidence"],
                    "llvm": {
                        "mnemonic_coverage_count": 1,
                        "mnemonic_coverage_ratio_percent": 100.0,
                        "roundtrip_stable_form_count": 1,
                        "roundtrip_stable_ratio_percent": 100.0,
                        "missing_mnemonics": [],
                        "roundtrip_skipped_forms": [],
                    },
                    "qemu": {
                        "mapped_form_count": 1,
                        "mapped_form_ratio_percent": 100.0,
                        "translation_mnemonic_coverage_count": 1,
                        "translation_mnemonic_coverage_ratio_percent": 100.0,
                        "missing_forms": [],
                        "translation_missing_mnemonics": [],
                    },
                },
                report48_path,
            )
            text48 = report48_path.read_text(encoding="utf-8")
            self.assertIn("QEMU L1 mapped forms", text48)
            self.assertIn("does not claim runtime or semantic completeness", text48)

    def test_canonical_gate_uses_l1_wording(self) -> None:
        root = Path(__file__).resolve().parents[2]
        report = json.loads((root / "docs/bringup/gates/latest.json").read_text(encoding="utf-8"))
        gates = [gate for run in report["runs"] for gate in run["gates"]]
        gate = next(
            item
            for item in gates
            if item["gate"] == "Canonical ISA L1 decoder/source mapping breadth"
        )
        evidence = " ".join(gate["evidence"]).lower()
        self.assertIn("l1 decoder/source mapping", evidence)
        self.assertIn("l2 runtime execution", evidence)
        self.assertNotIn("implementation evidence", evidence)
        status = (root / "docs/bringup/GATE_STATUS.md").read_text(encoding="utf-8")
        self.assertNotIn("Canonical ISA executable semantic breadth", status)


if __name__ == "__main__":
    unittest.main()
