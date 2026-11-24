#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from check_html_reference import op_page
from check_v0592_html import (
    _check_no_obsolete_reader_material,
    _check_status_pages,
    _detail_record_has_removed_form,
    _exact_token_pattern,
    inventories,
    release_inputs,
)


class V0592HTMLCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.tiles = release_inputs()
        cls.active, cls.obsolete = inventories(cls.catalog)

    def test_signed_release_inventory_is_exact(self):
        self.assertEqual(len(self.catalog["instructions"]), 1499)
        self.assertEqual(len(self.active), 1306)
        self.assertEqual(len(self.obsolete), 193)
        self.assertEqual(
            sum(row["mnemonic"].startswith("V.") for row in self.obsolete), 184
        )
        self.assertEqual(len(self.tiles["operations"]), 119)

    def test_obsolete_page_and_link_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            obsolete = next(row for row in self.obsolete if row["mnemonic"] == "V.ADD")
            (site / op_page(obsolete)).write_text("<h1>V.ADD</h1>", encoding="utf-8")
            (site / "index.html").write_text(
                '<a href="op-v-add.html">V.ADD</a>', encoding="utf-8"
            )
            (site / "support-V.ADD.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"><title>V.ADD</title>'
                '<path d="M 0.592 1.2"/></svg>',
                encoding="utf-8",
            )
            errors: list[str] = []
            _check_no_obsolete_reader_material(site, [obsolete], errors)
        self.assertTrue(
            any("obsolete instruction page remains" in error for error in errors)
        )
        self.assertTrue(
            any("reader material still describes" in error for error in errors)
        )
        self.assertTrue(any("links to obsolete" in error for error in errors))
        self.assertTrue(
            any("packaged filename names obsolete" in error for error in errors)
        )
        self.assertTrue(
            any("SVG label still describes obsolete" in error for error in errors)
        )

    def test_exact_mnemonic_matching_does_not_confuse_version_or_longer_name(self):
        pattern = _exact_token_pattern({"V.ADD", "B.TEXT", "MPAR"})
        self.assertIsNone(pattern.search("LinxISA v0.59.2 and V.ADDI remain available"))
        self.assertIsNone(pattern.search("COMPARISON is not a block mnemonic"))
        self.assertIsNotNone(pattern.search("The old V.ADD example must be removed"))
        self.assertIsNotNone(pattern.search("B.TEXT <label>"))
        self.assertIsNotNone(pattern.search("MPAR并行分离块"))

    def test_tile_detail_operation_name_is_not_mistaken_for_a_form_id(self):
        active_ids = {row["id"] for row in self.active}
        obsolete_ids = {row["id"] for row in self.obsolete}
        self.assertFalse(
            _detail_record_has_removed_form(
                "tile-tadd.html",
                {"forms": ["TADD"]},
                tile_pages={"tile-tadd.html"},
                active_ids=active_ids,
                obsolete_ids=obsolete_ids,
            )
        )
        self.assertTrue(
            _detail_record_has_removed_form(
                "op-v-add.html",
                {"forms": [next(iter(obsolete_ids))]},
                tile_pages={"tile-tadd.html"},
                active_ids=active_ids,
                obsolete_ids=obsolete_ids,
            )
        )

    def test_architecture_status_sections_are_required(self):
        status_rows = [
            row
            for row in self.active
            if row.get("architecture_status", {}).get("state")
            in {"retained", "reserved-unimplemented"}
        ]
        grouped: dict[str, list[dict]] = {}
        for row in status_rows:
            grouped.setdefault(op_page(row), []).append(row)
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            for filename, rows in grouped.items():
                state = rows[0]["architecture_status"]["state"]
                text = (
                    "仅预留编码；执行须在读取操作数或产生架构效果之前拒绝。"
                    if state == "reserved-unimplemented"
                    else "本形式沿用现行定义。"
                )
                (site / filename).write_text(
                    f'<section class="architecture-status" data-state="{state}">{text}</section>',
                    encoding="utf-8",
                )
            errors: list[str] = []
            _check_status_pages(site, self.active, errors)
            self.assertEqual(errors, [])
            reserved_page = next(
                filename
                for filename, rows in grouped.items()
                if rows[0]["architecture_status"]["state"] == "reserved-unimplemented"
            )
            (site / reserved_page).write_text(
                '<section class="architecture-status" data-state="reserved-unimplemented">保留</section>',
                encoding="utf-8",
            )
            _check_status_pages(site, self.active, errors)
        self.assertTrue(
            any("reserved-unimplemented notice" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
