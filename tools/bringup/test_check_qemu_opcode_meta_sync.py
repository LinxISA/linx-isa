#!/usr/bin/env python3
"""Regression tests for QEMU decode/meta signature synchronization."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_qemu_opcode_meta_sync.py")


class QemuOpcodeMetaSyncTests(unittest.TestCase):
    def make_tree(self, root: Path, *, meta_match: str = "0x40602b") -> tuple[Path, Path]:
        linx = root / "target" / "linx"
        linx.mkdir(parents=True)
        (linx / "insn16.decode").write_text("# empty\n", encoding="utf-8")
        (linx / "insn32.decode").write_text(
            "dc_isw 0000 0000 0100 .... .110 0000 0010 1011 %SrcL\n",
            encoding="utf-8",
        )
        (linx / "insn48.decode").write_text("# empty\n", encoding="utf-8")
        (linx / "insn64.decode").write_text("# empty\n", encoding="utf-8")
        (linx / "linx_opcode_ids_gen.h").write_text(
            "    LINX_OP_DC_ISW = 7,\n", encoding="utf-8"
        )
        (linx / "linx_opcode_meta_gen.h").write_text(
            "    {.op_id=7, .major_cat=LINX_CAT_MISC, .insn_len=32, "
            f".mask=UINT64_C(0xfff07fff), .match=UINT64_C({meta_match}), "
            '.mnemonic="dc_isw", .minor_cat="misc", .rd_kind="NONE", '
            '.source_file="insn32.decode"},\n',
            encoding="utf-8",
        )
        allowlist = root / "allowlist.json"
        allowlist.write_text(
            json.dumps({"decode_only_allow": [], "meta_only_allow": []}),
            encoding="utf-8",
        )
        return root, allowlist

    def run_check(self, qemu_root: Path, allowlist: Path, report: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--qemu-root",
                str(qemu_root),
                "--allowlist",
                str(allowlist),
                "--report-out",
                str(report),
                "--strict",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_exact_decode_meta_signature_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, allowlist = self.make_tree(Path(td))
            report = root / "report.json"
            proc = self.run_check(root, allowlist, report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["signature_mismatch_count"], 0)
            self.assertTrue(payload["result"]["ok"])

    def test_same_mnemonic_with_stale_match_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, allowlist = self.make_tree(Path(td), meta_match="0x70602b")
            report = root / "report.json"
            proc = self.run_check(root, allowlist, report)
            self.assertEqual(proc.returncode, 1)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["decode_only_unexpected_count"], 0)
            self.assertEqual(payload["meta_only_unexpected_count"], 0)
            self.assertEqual(payload["signature_mismatch_count"], 1)
            mismatch = payload["signature_mismatches"][0]
            self.assertEqual(mismatch["mnemonic"], "dc_isw")
            self.assertEqual(mismatch["decode_only"][0]["match"], "0x40602b")
            self.assertEqual(mismatch["meta_only"][0]["match"], "0x70602b")
            self.assertFalse(payload["result"]["ok"])

    def test_repeated_decoder_form_requires_repeated_metadata_form(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, allowlist = self.make_tree(Path(td))
            decode = root / "target" / "linx" / "insn32.decode"
            decode.write_text(
                decode.read_text(encoding="utf-8")
                + "dc_isw 0000 0000 0101 .... .110 0000 0010 1011 %SrcL\n",
                encoding="utf-8",
            )
            report = root / "report.json"
            proc = self.run_check(root, allowlist, report)
            self.assertEqual(proc.returncode, 1)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["signature_mismatch_count"], 1)
            mismatch = payload["signature_mismatches"][0]
            self.assertEqual(mismatch["mnemonic"], "dc_isw")
            self.assertEqual(len(mismatch["decode_only"]), 1)
            self.assertEqual(mismatch["decode_only"][0]["match"], "0x50602b")
            self.assertEqual(mismatch["meta_only"], [])


if __name__ == "__main__":
    unittest.main()
