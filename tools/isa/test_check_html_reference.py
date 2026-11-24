#!/usr/bin/env python3

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from check_html_reference import (
    Audit,
    Parser,
    SEMANTICS,
    TILE_MANUAL,
    english_visible_fragments,
    expected_fields,
    fixed_bits,
    informative_synopsis,
    hex_value,
    tile_predicate,
)
from manual_reader import operation_detail


class HtmlReferenceValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "isa/v0.59/linxisa-v0.59.json").read_text())

    def test_index_entries_explain_an_operation(self):
        for text in (
            "HL.CCAT 的中文增补说明与发布版编码。",
            "当前规范汇编：dc.iall",
            "目录名为 C.EBREAK。",
            "<br> 将两个源值相加。",
            "",
        ):
            with self.subTest(text=text):
                self.assertFalse(informative_synopsis(text))
        self.assertTrue(
            informative_synopsis("拼接两个源值后逻辑右移，低半部写入 Dst0。")
        )

    def test_parser_preserves_ids_links_and_text(self):
        parser = Parser()
        parser.feed(
            '<article class="form" id="x"><a href="y.html#z">A &amp; B</a></article>'
        )
        article = parser.root.find(tag="article", cls="form")
        self.assertEqual(len(article), 1)
        self.assertEqual(article[0].attrs["id"], "x")
        self.assertEqual(article[0].find(tag="a")[0].text(), "A & B")

    def test_default_language_scan_excludes_code_and_closed_evidence(self):
        parser = Parser()
        parser.feed(
            "<main><p>This visible English sentence must be reported here.</p>"
            "<pre><code>This source code sentence remains exact and hidden.</code></pre>"
            "<details><summary>规范证据</summary><p>Original English evidence stays folded.</p></details>"
            "<p>中文说明保留 Mode 与 Function 标识符。</p></main>"
        )
        self.assertEqual(
            english_visible_fragments(parser.root),
            ["This visible English sentence must be reported here."],
        )

    def test_catalog_encoding_expectations_are_exact(self):
        row = next(
            row
            for row in self.catalog["instructions"]
            if row["mnemonic"] == "ADD" and "pto_scope" not in row
        )
        self.assertEqual(expected_fields(row, 0)[-1], ("6:0", "0000101"))
        mask, match = fixed_bits(row)
        self.assertEqual(hex_value(mask, row["length_bits"]), "0x0000707f")
        self.assertEqual(hex_value(match, row["length_bits"]), "0x00000005")

    def test_missing_site_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = Audit(Path(tmp), self.catalog, {"operations": []}).run()
        self.assertTrue(errors)
        self.assertTrue(any("missing" in error for error in errors))

    def test_every_pto_form_resolves_an_exact_asl_owner(self):
        owners = json.loads(SEMANTICS.read_text(encoding="utf-8"))["forms"]
        missing = []
        for row in self.catalog["instructions"]:
            source_id = row.get("pto_base_form_id") or row.get("pto_source_form_id")
            if source_id and source_id not in owners:
                missing.append((row["id"], source_id))
        self.assertEqual(missing, [])

    def test_linx_forms_are_owned_by_the_positive_v059_source(self):
        source = json.loads(
            (ROOT / "isa/v0.59/state/linx_extension_forms.json").read_text()
        )
        rows = {
            row["id"]: row
            for row in self.catalog["instructions"]
            if not row.get("pto_source_form_id")
        }
        self.assertEqual(len(rows), 23)
        self.assertEqual(rows, {row["id"]: row for row in source["forms"]})

    def test_tile_predicates_and_blocks_are_nonempty(self):
        tiles = json.loads(
            (ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )["operations"]
        owners = {
            row["mnemonic"]: row
            for row in json.loads(TILE_MANUAL.read_text())["operations"]
        }
        by_mnemonic = {}
        for row in self.catalog["instructions"]:
            by_mnemonic.setdefault(row["mnemonic"], row)
        self.assertEqual(len(tiles), 119)
        for op in tiles:
            self.assertRegex(
                tile_predicate(op, by_mnemonic[op["command_mnemonic"]]),
                r"^\(word & 0x[0-9a-f]+\) == 0x[0-9a-f]+$",
            )
            self.assertTrue(owners[op["name"]]["block"])

    def test_archived_asl_markup_round_trips_exactly(self):
        tiles = json.loads(
            (ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )
        with tempfile.TemporaryDirectory() as tmp:
            audit = Audit(Path(tmp), self.catalog, tiles)
            for owner_path in (
                "asl/scalar/alu/ADD.asl",
                "asl/tile/elementwise-tile-tile/arithmetic/TADD.asl",
            ):
                parser = Parser()
                parser.feed(operation_detail(owner_path))
                audit.check_asl_excerpt(
                    owner_path,
                    parser.root.find(tag="details", cls="asl-operation"),
                    owner_path,
                )
            self.assertEqual(audit.errors, [])


if __name__ == "__main__":
    unittest.main()
