#!/usr/bin/env python3
"""PTO ISA v0.58 retired conditional branch closure."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RETIRED = {"B.EQ", "B.NE", "B.LT", "B.GE", "B.LTU", "B.GEU", "B.Z", "B.NZ"}


class RetiredBranchClosureTests(unittest.TestCase):
    def test_catalog_removes_and_reserves_all_eight_forms(self) -> None:
        spec = json.loads(
            (ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8")
        )
        self.assertTrue(RETIRED.isdisjoint({row["mnemonic"] for row in spec["instructions"]}))
        reservations = {
            row["mnemonic"]
            for row in spec["state"]["extension_encoding_reservations"]["reservations"]
        }
        self.assertTrue(RETIRED <= reservations)

    def test_sail_has_no_retired_execution_helpers(self) -> None:
        execute = (ROOT / "isa/sail/model/execute/execute.sail").read_text(
            encoding="utf-8"
        )
        for mnemonic in RETIRED:
            helper = "exec_" + mnemonic.lower().replace(".", "_")
            self.assertNotRegex(execute, rf"function\s+{re.escape(helper)}\b")
        directed = (ROOT / "isa/sail/tests/directed.sail").read_text(encoding="utf-8")
        for word in ("0x0000_0027", "0x0000_1027", "0x0000_2027", "0x0000_3027",
                     "0x0000_4027", "0x0000_5027", "0x0000_1037", "0x0000_2037"):
            self.assertIn(word, directed)

    def test_active_navigation_does_not_publish_retired_pages(self) -> None:
        navigation = (ROOT / "mkdocs.yml").read_text(encoding="utf-8") + (
            ROOT / "mkdocs.zh.yml"
        ).read_text(encoding="utf-8")
        for mnemonic in RETIRED:
            self.assertNotIn(f"- {mnemonic}:", navigation)
        for language_root in (ROOT / "docs/isa/inst/misa_g", ROOT / "docs/zh/isa/inst/misa_g"):
            for mnemonic in RETIRED:
                self.assertFalse((language_root / f"{mnemonic}.md").exists())


if __name__ == "__main__":
    unittest.main()
