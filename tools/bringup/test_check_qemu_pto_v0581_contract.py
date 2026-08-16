#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_qemu_pto_v0581_contract as checker


ROOT = Path(__file__).resolve().parents[2]


class QemuPtoV0581ContractTests(unittest.TestCase):
    def test_checked_in_qemu_matches_the_exact_release_contract(self) -> None:
        result = checker.check_contract(ROOT)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.mnemonics, 731)
        self.assertEqual(result.forms, 765)
        self.assertEqual(result.engine_counts, {"VEC": 31, "SFU": 56, "TLSU": 10, "CUBE": 12})
        self.assertEqual(result.operation_count, 109)
        self.assertEqual(result.numeric_reference_vector_count, 104)

    def test_catalog_release_mutation_is_rejected(self) -> None:
        catalog = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text())
        mutated = copy.deepcopy(catalog)
        mutated["version"] = "0.58.0"
        with self.assertRaisesRegex(ValueError, "release"):
            checker.validate_catalog(mutated)

    def test_elf_identity_validation_must_precede_every_loader(self) -> None:
        source = (ROOT / "emulator/qemu/hw/linx/virt.c").read_text()
        checker.validate_elf_loader_order(source)


if __name__ == "__main__":
    unittest.main()
