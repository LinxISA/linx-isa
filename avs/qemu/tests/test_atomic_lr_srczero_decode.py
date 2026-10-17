#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


CASES = {
    "LR.W": {
        "qemu_mnemonic": "lr_w",
        "mask": 0x7800707F,
        "match": 0x1000000B,
        # RegDst=a0, SrcL=a0, SrcZero=31.
        "raw": 0x11F1010B,
    },
    "LR.D": {
        "qemu_mnemonic": "lr_d",
        "mask": 0x7800707F,
        "match": 0x1800000B,
        # RegDst=a0, SrcL=a0, SrcZero=17.
        "raw": 0x1911010B,
    },
}


class AtomicLrSrcZeroDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        golden = json.loads((REPO_ROOT / "isa" / "v0.58" / "linxisa-v0.58.json").read_text(encoding="utf-8"))
        cls.golden = {
            insn["mnemonic"]: insn["encoding"]["parts"][0]
            for insn in golden["instructions"] if insn["mnemonic"] in CASES
        }
        cls.qemu = (REPO_ROOT / "emulator" / "qemu" / "target" / "linx" / "insn32.decode").read_text(encoding="utf-8")

    def test_golden_and_qemu_accept_nonzero_srczero(self) -> None:
        self.assertEqual(set(self.golden), set(CASES))
        for golden_name, case in CASES.items():
            with self.subTest(mnemonic=golden_name):
                golden_form = self.golden[golden_name]
                raw = case["raw"]

                self.assertNotEqual((raw >> 20) & 0x1F, 0)
                self.assertEqual(int(golden_form["mask"], 16), case["mask"])
                self.assertEqual(int(golden_form["match"], 16), case["match"])
                self.assertEqual(raw & case["mask"], case["match"])
                self.assertRegex(self.qemu, rf"(?m)^{case['qemu_mnemonic']}\s+")

    def test_directed_oracle_uses_the_checked_raw_words(self) -> None:
        source = (
            REPO_ROOT / "avs" / "qemu" / "tests" / "07_atomic_lr_srczero.S"
        ).read_text(encoding="utf-8")
        for golden_name, case in CASES.items():
            with self.subTest(mnemonic=golden_name):
                self.assertIn(f".4byte 0x{case['raw']:08x}", source)


if __name__ == "__main__":
    unittest.main()
