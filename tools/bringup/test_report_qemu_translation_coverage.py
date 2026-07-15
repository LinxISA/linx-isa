#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_qemu_translation_coverage as coverage


class TranslationMnemonicParsingTests(unittest.TestCase):
    def test_hex_prefixed_real_mnemonic_is_not_mangled(self) -> None:
        self.assertEqual(coverage.canonicalize_mnemonic("FENCE.D"), "FENCE.D")
        self.assertEqual(coverage.canonicalize_mnemonic("FENCE.I"), "FENCE.I")

    def test_known_glued_byte_spelling_remains_supported(self) -> None:
        self.assertEqual(
            coverage.canonicalize_mnemonic("00HL.BSTART.STD"),
            "HL.BSTART.STD",
        )
        self.assertEqual(
            coverage.canonicalize_mnemonic("ffBSTART.STD"),
            "BSTART.STD",
        )

    def test_objdump_parser_keeps_fence_mnemonics(self) -> None:
        emitted, _ = coverage.extract_mnemonics_from_objdump(
            "     242: 2b 20 10 01  fence.d\n"
            "     246: 2b 20 00 10  fence.i\n"
        )
        self.assertEqual(emitted, {"FENCE.D", "FENCE.I"})


if __name__ == "__main__":
    unittest.main()
