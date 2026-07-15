#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_qemu_isa_coverage as coverage


class ReportQemuIsaCoverageTests(unittest.TestCase):
    def test_checked_in_l2_l3_counts_match_executable_ledger(self) -> None:
        root = Path(__file__).resolve().parents[2]
        executable = json.loads(
            (root / "docs/bringup/gates/qemu_executable_coverage_latest.json").read_text(
                encoding="utf-8"
            )
        )
        aggregate = json.loads(
            (root / "docs/bringup/gates/qemu_isa_coverage_latest.json").read_text(
                encoding="utf-8"
            )
        )
        for level in ("L2", "L3"):
            with self.subTest(level=level):
                self.assertEqual(aggregate["evidence"][level]["availability"], "available")
                self.assertEqual(
                    aggregate["evidence"][level]["form_count"],
                    executable["evidence"][level]["form_count"],
                )
                self.assertEqual(
                    aggregate["evidence"][level]["mnemonic_count"],
                    executable["evidence"][level]["mnemonic_count"],
                )
                self.assertEqual(
                    aggregate["evidence"][level]["qemu_sha"],
                    executable["inputs"]["qemu_sha"],
                )

    def _executable_report(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "claim": "per_form_qemu_executable_coverage",
            "inputs": {"qemu_sha": "abc123"},
            "rejected": [],
            "admitted": [
                {
                    "form_id": "foo_32_id",
                    "mnemonic": "FOO",
                    "max_level": "L3",
                    "qemu_sha": "abc123",
                },
                {
                    "form_id": "bar_32_id",
                    "mnemonic": "BAR",
                    "max_level": "L2",
                    "qemu_sha": "abc123",
                },
            ],
            "evidence": {
                "L2": {
                    "availability": "available",
                    "claim": "runtime_execution",
                    "form_count": 2,
                    "mnemonic_count": 2,
                },
                "L3": {
                    "availability": "available",
                    "claim": "semantic_oracle",
                    "form_count": 1,
                    "mnemonic_count": 1,
                },
            },
        }

    def test_executable_evidence_is_recounted_before_ingestion(self) -> None:
        evidence = coverage._validate_executable_evidence(
            self._executable_report(),
            {"foo_32_id": "FOO", "bar_32_id": "BAR"},
            "abc123",
        )
        self.assertEqual(evidence["L2"]["form_count"], 2)
        self.assertEqual(evidence["L2"]["mnemonic_count"], 2)
        self.assertEqual(evidence["L3"]["form_count"], 1)
        self.assertEqual(evidence["L3"]["mnemonic_count"], 1)

    def test_executable_evidence_rejects_stale_or_inconsistent_claims(self) -> None:
        cases: list[tuple[str, dict[str, object], str]] = []

        stale = self._executable_report()
        cases.append(("stale qemu", stale, "other-sha"))

        wrong_count = self._executable_report()
        wrong_count["evidence"]["L3"]["form_count"] = 2
        cases.append(("wrong count", wrong_count, "abc123"))

        unknown_form = self._executable_report()
        unknown_form["admitted"][0]["form_id"] = "unknown"
        cases.append(("unknown form", unknown_form, "abc123"))

        rejected = self._executable_report()
        rejected["rejected"] = [{"form_id": "bad"}]
        cases.append(("nonempty rejected list", rejected, "abc123"))

        duplicate = self._executable_report()
        duplicate["admitted"][1]["form_id"] = "foo_32_id"
        duplicate["admitted"][1]["mnemonic"] = "FOO"
        cases.append(("duplicate form", duplicate, "abc123"))

        wrong_mnemonic = self._executable_report()
        wrong_mnemonic["admitted"][0]["mnemonic"] = "BAR"
        cases.append(("wrong mnemonic", wrong_mnemonic, "abc123"))

        wrong_mnemonic_count = self._executable_report()
        wrong_mnemonic_count["evidence"]["L2"]["mnemonic_count"] = 1
        cases.append(("wrong mnemonic count", wrong_mnemonic_count, "abc123"))

        wrong_availability = self._executable_report()
        wrong_availability["evidence"]["L3"]["availability"] = "unavailable"
        cases.append(("wrong availability", wrong_availability, "abc123"))

        stale_entry = self._executable_report()
        stale_entry["admitted"][0]["qemu_sha"] = "other-sha"
        cases.append(("stale admitted entry", stale_entry, "abc123"))

        for name, report, qemu_sha in cases:
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    coverage._validate_executable_evidence(
                        report,
                        {"foo_32_id": "FOO", "bar_32_id": "BAR"},
                        qemu_sha,
                    )

    def test_b_dim_decode_tokens_map_to_architectural_mnemonic(self) -> None:
        spec_set = {"B.DIM"}

        for token in ("b_dim_lb0", "b_dim_lb1", "b_dim_lb2"):
            with self.subTest(token=token):
                self.assertEqual(
                    coverage._canonicalize_qemu_mnemonic(token, spec_set),
                    ["B.DIM"],
                )

    def test_c_setret_manual_translate_evidence_provides_exact_form(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            qemu_root = Path(td)
            linx_dir = qemu_root / "target" / "linx"
            linx_dir.mkdir(parents=True)
            (linx_dir / "translate.c").write_text(
                """
static bool linx_is_c_setret_hw(uint16_t hw)
{
    return (hw & 0xf83f) == 0x5016;
}

static void decode(uint16_t hw)
{
    if (false) {
    } else if (linx_is_c_setret_hw(hw)) {
        decoded = linx_setret_common(ctx, immediate);
    } else {
    }
}
""",
                encoding="utf-8",
            )

            self.assertEqual(
                coverage._load_manual_translate_entries(qemu_root),
                [
                    {
                        "mnemonic": "C.SETRET",
                        "insn_len": 16,
                        "mask": 0xF83F,
                        "match": 0x5016,
                        "source_file": "translate.c",
                    }
                ],
            )

    def test_c_setret_without_translation_call_is_not_covered(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            qemu_root = Path(td)
            linx_dir = qemu_root / "target" / "linx"
            linx_dir.mkdir(parents=True)
            (linx_dir / "translate.c").write_text(
                """
static bool linx_is_c_setret_hw(uint16_t hw)
{
    return (hw & 0xf83f) == 0x5016;
}

static void decode(uint16_t hw)
{
    if (false) {
    } else if (linx_is_c_setret_hw(hw)) {
        decoded = unrelated_translation(ctx);
    } else {
    }
}
""",
                encoding="utf-8",
            )

            self.assertEqual(coverage._load_manual_translate_entries(qemu_root), [])

    def test_metadata_fallback_includes_manual_translate_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu_root = root / "qemu"
            linx_dir = qemu_root / "target" / "linx"
            linx_dir.mkdir(parents=True)
            (linx_dir / "translate.c").write_text(
                """
static bool linx_is_c_setret_hw(uint16_t hw)
{
    return (hw & 0xf83f) == 0x5016;
}

static void decode(uint16_t hw)
{
    if (false) {
    } else if (linx_is_c_setret_hw(hw)) {
        decoded = linx_setret_common(ctx, immediate);
    } else {
    }
}
""",
                encoding="utf-8",
            )
            spec_path = root / "spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "instructions": [
                            {
                                "mnemonic": "C.SETRET",
                                "encoding": {
                                    "length_bits": 16,
                                    "parts": [{"mask": "0xf83f", "match": "0x5016"}],
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            meta_path = root / "linx_opcode_meta_gen.h"
            meta_path.write_text(
                '{.insn_len=16, .mask=UINT64_C(0x3f), '
                '.match=UINT64_C(0x16), .mnemonic="c_movi"},\n',
                encoding="utf-8",
            )
            report_path = root / "report.json"
            markdown_path = root / "report.md"

            rc = coverage.main(
                [
                    "--spec",
                    str(spec_path),
                    "--qemu-root",
                    str(qemu_root),
                    "--qemu-meta",
                    str(meta_path),
                    "--report-out",
                    str(report_path),
                    "--out-md",
                    str(markdown_path),
                    "--require-full",
                ]
            )
            report = json.loads(report_path.read_text(encoding="utf-8"))
            markdown = markdown_path.read_text(encoding="utf-8")

            self.assertEqual(rc, 0)
            self.assertEqual(report["qemu_source_kind"], "meta")
            self.assertEqual(report["coverage_count"], 1)
            self.assertEqual(report["form_coverage_count"], 1)
            self.assertEqual(report["qemu_manual_translate_mnemonics"], ["C.SETRET"])
            self.assertEqual(report["evidence_level"], "L1")
            self.assertEqual(report["claim"], "decoder_source_mapping")
            self.assertEqual(
                report["capabilities"],
                [
                    "decoder_source_to_isa_mnemonic_mapping",
                    "decoder_mask_to_isa_form_matching",
                ],
            )
            self.assertEqual(
                report["limitations"],
                [
                    "no_runtime_execution_evidence",
                    "no_semantic_oracle_evidence",
                ],
            )
            self.assertEqual(
                report["evidence"]["L1"],
                {
                    "availability": "available",
                    "claim": "decoder_source_mapping",
                    "form_count": 1,
                    "mnemonic_count": 1,
                },
            )
            self.assertEqual(
                report["coverage_count"],
                report["evidence"]["L1"]["mnemonic_count"],
            )
            self.assertEqual(
                report["form_coverage_count"],
                report["evidence"]["L1"]["form_count"],
            )
            for level, claim in (("L2", "runtime_execution"), ("L3", "semantic_oracle")):
                with self.subTest(level=level):
                    self.assertEqual(report["evidence"][level]["availability"], "unavailable")
                    self.assertEqual(report["evidence"][level]["claim"], claim)
                    self.assertIsNone(report["evidence"][level]["mnemonic_count"])
                    self.assertIsNone(report["evidence"][level]["form_count"])
            self.assertIn("Evidence level: `L1`", markdown)
            self.assertIn("Claim: `decoder_source_mapping`", markdown)
            self.assertIn("L2 runtime execution: `unavailable`", markdown)
            self.assertIn("L3 semantic oracle: `unavailable`", markdown)
            self.assertNotIn("executable coverage", markdown.lower())

    def test_l1_thresholds_do_not_imply_runtime_closure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu_root = root / "qemu"
            linx_dir = qemu_root / "target" / "linx"
            linx_dir.mkdir(parents=True)
            (linx_dir / "translate.c").write_text(
                """
static bool linx_is_c_setret_hw(uint16_t hw)
{
    return (hw & 0xf83f) == 0x5016;
}
static void decode(uint16_t hw)
{
    if (false) {
    } else if (linx_is_c_setret_hw(hw)) {
        decoded = linx_setret_common(ctx, immediate);
    }
}
""",
                encoding="utf-8",
            )
            spec_path = root / "spec.json"
            spec_path.write_text(
                json.dumps(
                    {
                        "instructions": [
                            {
                                "mnemonic": "C.SETRET",
                                "encoding": {
                                    "length_bits": 16,
                                    "parts": [{"mask": "0xf83f", "match": "0x5016"}],
                                },
                            },
                            {
                                "mnemonic": "FOO",
                                "encoding": {
                                    "length_bits": 16,
                                    "parts": [{"mask": "0xffff", "match": "0xabcd"}],
                                },
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            meta_path = root / "linx_opcode_meta_gen.h"
            meta_path.write_text(
                '{.insn_len=16, .mask=UINT64_C(0x3f), '
                '.match=UINT64_C(0x16), .mnemonic="c_movi"},\n',
                encoding="utf-8",
            )
            base_args = [
                "--spec",
                str(spec_path),
                "--qemu-root",
                str(qemu_root),
                "--qemu-meta",
                str(meta_path),
                "--report-out",
                str(root / "report.json"),
            ]

            self.assertEqual(coverage.main([*base_args, "--fail-under-count", "1"]), 0)
            self.assertEqual(coverage.main([*base_args, "--fail-under-count", "2"]), 1)
            self.assertEqual(coverage.main([*base_args, "--require-full"]), 1)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["evidence"]["L1"]["mnemonic_count"], 1)
            self.assertEqual(report["evidence"]["L2"]["availability"], "unavailable")
            self.assertEqual(report["evidence"]["L3"]["availability"], "unavailable")


if __name__ == "__main__":
    unittest.main()
