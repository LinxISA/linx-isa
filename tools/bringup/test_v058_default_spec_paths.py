#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path


class V058DefaultSpecPathTests(unittest.TestCase):
    def test_current_bringup_entrypoints_do_not_default_to_v057(self) -> None:
        root = Path(__file__).resolve().parents[2]
        entrypoints = (
            "tools/bringup/check_tepl_encoding.py",
            "tools/bringup/refresh_qemu_executable_coverage.py",
            "tools/bringup/report_48bit_implementation.py",
            "tools/bringup/report_isa_llvm_qemu_coverage.py",
            "tools/bringup/report_llvm_c_codegen_coverage.py",
            "tools/bringup/report_qemu_executable_coverage.py",
            "tools/bringup/report_qemu_isa_coverage.py",
            "tools/bringup/report_qemu_translation_coverage.py",
            "tools/analysis/objdump_stats.py",
        )
        for relative in entrypoints:
            with self.subTest(path=relative):
                text = (root / relative).read_text(encoding="utf-8")
                self.assertNotIn("isa/v0.57/linxisa-v0.57.json", text)


if __name__ == "__main__":
    unittest.main()
