#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from check_manual_structure import (
    Audit,
    CLASS_FILES,
    Parser,
    class_page_mnemonics,
    expected_class_inventory,
)
from manual_tag import RELEASE_TAG, tagged_bytes, tagged_json, verified_tag_commit


class ManualStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")

    def test_class_inventory_is_exact_and_disjoint(self) -> None:
        inventory = expected_class_inventory(self.catalog)
        self.assertEqual(
            {name: len(inventory[path]) for name, path in CLASS_FILES.items()},
            {
                "ALU": 107,
                "BBD": 11,
                "BRU": 58,
                "AGU": 183,
                "AMO": 61,
                "CMD": 75,
                "FSU": 30,
                "SYS": 36,
            },
        )
        flattened = [name for names in inventory.values() for name in names]
        self.assertEqual(len(flattened), 561)
        self.assertEqual(len(set(flattened)), 561)

    def test_alphabet_list_reads_first_mnemonic_link(self) -> None:
        parser = Parser()
        parser.feed(
            '<ul class="alphabet-list">'
            '<li><span class="mnemonic"><a href="op-add.html">ADD</a></span><span>说明</span></li>'
            '<li><span class="mnemonic"><a href="op-sub.html">SUB</a></span></li>'
            "</ul>"
        )
        self.assertEqual(class_page_mnemonics(parser.root), (["ADD", "SUB"], []))

    def test_alphabet_list_fails_ambiguous_rows(self) -> None:
        parser = Parser()
        parser.feed(
            '<ul class="alphabet-list"><li><span class="mnemonic">ADD</span></li></ul>'
        )
        names, errors = class_page_mnemonics(parser.root)
        self.assertEqual(names, [])
        self.assertTrue(errors)

    def test_sectioned_alphabet_lists_are_combined(self) -> None:
        parser = Parser()
        parser.feed(
            '<section class="alphabet"><ul class="index-list">'
            '<li><span class="mnemonic"><a href="a">ADD</a></span></li></ul></section>'
            '<section class="alphabet"><ul class="index-list">'
            '<li><span class="mnemonic"><a href="s">SUB</a></span></li></ul></section>'
        )
        self.assertEqual(class_page_mnemonics(parser.root), (["ADD", "SUB"], []))

    def test_missing_site_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            errors = Audit(Path(directory), self.catalog).run()
        self.assertTrue(errors)
        self.assertTrue(any("diagram-audit.json: missing" in error for error in errors))
        for filename in CLASS_FILES.values():
            self.assertTrue(any(error.startswith(filename + ":") for error in errors))

    def test_diagram_audit_rejects_wrong_catalog_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "diagram-audit.json").write_text(
                json.dumps(
                    {
                        "schema": "linxisa.manual.encoding-diagrams.v1",
                        "release_tag": RELEASE_TAG,
                        "source_commit": verified_tag_commit(),
                        "catalog_sha256": "0" * 64,
                        "forms": {},
                    }
                ),
                encoding="utf-8",
            )
            audit = Audit(root, self.catalog)
            audit.diagram_audit()
        self.assertIn("diagram-audit.json: wrong catalog digest", audit.errors)
        self.assertNotEqual(
            "0" * 64,
            hashlib.sha256(tagged_bytes("isa/v0.59/linxisa-v0.59.json")).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
