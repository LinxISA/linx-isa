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
                    "--require-full",
                ]
            )
            report = json.loads(report_path.read_text(encoding="utf-8"))

            self.assertEqual(rc, 0)
            self.assertEqual(report["qemu_source_kind"], "meta")
            self.assertEqual(report["coverage_count"], 1)
            self.assertEqual(report["form_coverage_count"], 1)
            self.assertEqual(report["qemu_manual_translate_mnemonics"], ["C.SETRET"])


if __name__ == "__main__":
    unittest.main()
