#!/usr/bin/env python3

import json
from pathlib import Path
import unittest

from tools.isa.manual_navigation import category_links, index_pages


def alpha(entries, intro, prompt):
    return intro + prompt + " ".join(item[0] for item in entries)


class ManualNavigationTest(unittest.TestCase):
    def test_default_navigation_retains_v0591_classes(self):
        self.assertIn("class-vec.html", category_links())

    def test_active_navigation_omits_obsolete_vector_class(self):
        keys = {"ALU", "BBD", "BRU", "AGU", "AMO", "CMD", "FSU", "SYS"}
        links = category_links("../", active_keys=keys)
        self.assertNotIn("class-vec.html", links)
        self.assertIn("../class-lsu.html", links)

        rows = [
            {"uop_big_kind": key, "mnemonic": "M" + str(index)}
            for index, key in enumerate(sorted(keys))
        ]
        entries = [(row["mnemonic"], "x", "说明", row["uop_big_kind"]) for row in rows]
        pages = index_pages(rows, entries, alpha, 119, active_keys=keys)
        self.assertNotIn("class-vec.html", pages)
        self.assertIn("class-lsu.html", pages)
        self.assertIn("VEC、SFU、TLSU 和 CUBE", pages["index.html"][1])

    def test_active_mapping_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "functional class mapping"):
            index_pages([], [], alpha, 119, active_keys={"ALU"})

    def test_v0592_active_catalog_has_exactly_eight_classes(self):
        root = Path(__file__).resolve().parents[2]
        catalog = json.loads((root / "isa/v0.59.2/linxisa-v0.59.2.json").read_text())
        active = [
            row
            for row in catalog["instructions"]
            if row.get("architecture_status", {}).get("state") != "obsolete"
        ]
        self.assertEqual(len(active), 1306)
        self.assertEqual(
            {row["uop_big_kind"] for row in active},
            {"ALU", "BBD", "BRU", "AGU", "AMO", "CMD", "FSU", "SYS"},
        )


if __name__ == "__main__":
    unittest.main()
