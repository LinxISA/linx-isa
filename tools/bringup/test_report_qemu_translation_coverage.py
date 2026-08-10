#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_qemu_translation_coverage as coverage


class TranslationMnemonicParsingTests(unittest.TestCase):
    def test_v058_engine_aliases_map_to_the_tepl_encoding_carrier(self) -> None:
        spec_mnemonics = {"BSTART.TEPL"}
        self.assertEqual(
            coverage.map_emitted_to_spec("BSTART.VEC", spec_mnemonics),
            "BSTART.TEPL",
        )
        self.assertEqual(
            coverage.map_emitted_to_spec("BSTART.SFU", spec_mnemonics),
            "BSTART.TEPL",
        )

    def test_retired_tma_selector_does_not_synthesize_tlsu_coverage(self) -> None:
        self.assertEqual(
            coverage.derived_selector_mnemonics("BSTART.TMA", ["TLOAD"]),
            set(),
        )

    def test_retired_tepl_selector_spellings_do_not_transfer_coverage(self) -> None:
        for selector in ("ACCCVT", "ERCOV", "ESAVE"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    coverage.derived_selector_mnemonics("BSTART.TEPL", [selector]),
                    set(),
                )

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
