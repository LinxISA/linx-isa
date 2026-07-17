#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "rtl" / "LinxCore" / "tools" / "generate"))

from opcode_catalog_lib import parse_decode_file  # noqa: E402


CASES = {
    "LR.W": {
        "qemu_mnemonic": "lr_w",
        "mask": 0xF000707F,
        "match": 0x2000000B,
        # RegDst=a0, SrcL=a0, SrcZero=31.
        "raw": 0x21F1010B,
    },
    "LR.D": {
        "qemu_mnemonic": "lr_d",
        "mask": 0xF000707F,
        "match": 0x3000000B,
        # RegDst=a0, SrcL=a0, SrcZero=17.
        "raw": 0x3111010B,
    },
}


class AtomicLrSrcZeroDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        golden = json.loads(
            (REPO_ROOT / "isa" / "v0.57" / "linxisa-v0.57.json").read_text(
                encoding="utf-8"
            )
        )
        cls.golden = {
            insn["mnemonic"]: insn["encoding"]["parts"][0]
            for insn in golden["instructions"]
            if insn["mnemonic"] in CASES
        }
        cls.qemu = {
            entry.mnemonic: entry
            for entry in parse_decode_file(
                REPO_ROOT / "emulator" / "qemu" / "target" / "linx" / "insn32.decode",
                32,
            )
            if entry.mnemonic in {case["qemu_mnemonic"] for case in CASES.values()}
        }

    def test_golden_and_qemu_accept_nonzero_srczero(self) -> None:
        self.assertEqual(set(self.golden), set(CASES))
        self.assertEqual(
            set(self.qemu), {case["qemu_mnemonic"] for case in CASES.values()}
        )

        for golden_name, case in CASES.items():
            with self.subTest(mnemonic=golden_name):
                golden_form = self.golden[golden_name]
                qemu_form = self.qemu[case["qemu_mnemonic"]]
                raw = case["raw"]

                self.assertNotEqual((raw >> 20) & 0x1F, 0)
                self.assertEqual(int(golden_form["mask"], 16), case["mask"])
                self.assertEqual(int(golden_form["match"], 16), case["match"])
                self.assertEqual(raw & case["mask"], case["match"])
                self.assertEqual(qemu_form.mask, case["mask"])
                self.assertEqual(qemu_form.match, case["match"])
                self.assertEqual(raw & qemu_form.mask, qemu_form.match)

    def test_directed_oracle_uses_the_checked_raw_words(self) -> None:
        source = (
            REPO_ROOT / "avs" / "qemu" / "tests" / "07_atomic_lr_srczero.S"
        ).read_text(encoding="utf-8")
        for golden_name, case in CASES.items():
            with self.subTest(mnemonic=golden_name):
                self.assertIn(f".4byte 0x{case['raw']:08x}", source)


if __name__ == "__main__":
    unittest.main()
