#!/usr/bin/env python3
"""Bilingual and generated first-use exception documentation closure."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EN_EXCEPTION = ROOT / "docs/isa/exception/exception.md"
ZH_EXCEPTION = ROOT / "docs/zh/isa/exception/exception.md"
EN_TRAPNO = ROOT / "docs/isa/register/ssr/TRAPNO.md"
ZH_TRAPNO = ROOT / "docs/zh/isa/register/ssr/TRAPNO.md"
EN_ECONFIG = ROOT / "docs/isa/register/ssr/ECONFIG.md"
ZH_ECONFIG = ROOT / "docs/zh/isa/register/ssr/ECONFIG.md"
MANUAL = ROOT / "docs/architecture/isa-manual/src/chapters/10_system_and_privilege.adoc"
GENERATED_TRAP = ROOT / "docs/architecture/isa-manual/src/generated/trapno_encoding.adoc"
GENERATED_SSR = ROOT / "docs/architecture/isa-manual/src/generated/system_registers_ssr.adoc"


class FirstUseExceptionDocumentationTest(unittest.TestCase):
    def test_active_exception_pages_use_exact_first_use_encoding(self) -> None:
        for path in (EN_EXCEPTION, ZH_EXCEPTION, EN_TRAPNO, ZH_TRAPNO):
            text = path.read_text(encoding="utf-8")
            self.assertIn("E_INST", text, path)
            self.assertIn("EC_PERM", text, path)
            self.assertNotIn("E_PEREM", text, path)
        self.assertIn("TRAPARG0 = 0", EN_EXCEPTION.read_text(encoding="utf-8"))
        self.assertIn("TRAPARG0 = 1", EN_EXCEPTION.read_text(encoding="utf-8"))
        self.assertIn("TRAPARG0 = 0", ZH_EXCEPTION.read_text(encoding="utf-8"))
        self.assertIn("TRAPARG0 = 1", ZH_EXCEPTION.read_text(encoding="utf-8"))

    def test_econfig_pages_replace_placeholder_with_exact_table(self) -> None:
        en = EN_ECONFIG.read_text(encoding="utf-8")
        zh = ZH_ECONFIG.read_text(encoding="utf-8")
        for text, path in ((en, EN_ECONFIG), (zh, ZH_ECONFIG)):
            self.assertNotIn("figs/bitfield/svg/Sysregs/ECONFIG.svg", text, path)
            self.assertIn("0x0000000300000008", text, path)
            self.assertIn("32", text, path)
            self.assertIn("33", text, path)
            self.assertIn("VECTOR", text, path)
            self.assertIn("CUBE", text, path)
        self.assertIn("bit 32", en)
        self.assertIn("位 32", zh)

    def test_generated_manual_matches_machine_contract(self) -> None:
        trap = GENERATED_TRAP.read_text(encoding="utf-8")
        ssr = GENERATED_SSR.read_text(encoding="utf-8")
        manual = MANUAL.read_text(encoding="utf-8")
        self.assertIn("VECTOR/CUBE first-use exception", trap)
        self.assertIn("|`trapnum` |`E_INST`", trap)
        self.assertIn("|`trapnum_value` |`0`", trap)
        self.assertIn("|`cause` |`EC_PERM`", trap)
        self.assertIn("|`cause_value` |`4`", trap)
        self.assertIn("|`TRAPARG0.VECTOR` |`0`", trap)
        self.assertIn("|`TRAPARG0.CUBE` |`1`", trap)
        self.assertIn("`0x0000000300000008`", ssr)
        self.assertIn("|`V` |`32`", ssr)
        self.assertIn("|`C` |`33`", ssr)
        self.assertIn("VECTOR/CUBE first-use exception", manual)
        self.assertNotIn(
            "For a SYNC_SERVICE_REQUEST: set `TRAPNO_ACRm.E = 0`", manual
        )

if __name__ == "__main__":
    unittest.main()
