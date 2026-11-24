#!/usr/bin/env python3

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

from tools.isa.check_manual_authored import (
    _ArticleFacts,
    _expected_pages,
    _normalize_local_targets,
    extract_authored,
)
from tools.isa.manual_authored import authored_for
from tools.isa.manual_markdown import render_article
from tools.isa.manual_tag import tagged_bytes, tagged_json


class CheckManualAuthoredTest(unittest.TestCase):
    def test_marker_extraction_is_exact_and_fails_closed(self):
        wrapped = '<section class="authored-reader" data-source-path="x.md"><p>来源</p><!-- authored:start --><p>正文</p><!-- authored:end --></section>'
        self.assertEqual(extract_authored(wrapped), ("x.md", "<p>正文</p>"))
        with self.assertRaises(ValueError):
            extract_authored("<p>no markers</p>")
        with self.assertRaises(ValueError):
            extract_authored(wrapped + wrapped)

    def test_internal_routing_normalization_preserves_external_links(self):
        one = '<a href="../op-add.html">A</a><img src="assets/a.svg"><a href="https://example.com/x">X</a>'
        two = '<a href="op-add.html">A</a><img src="../support-assets/a.svg"><a href="https://example.com/x">X</a>'
        self.assertEqual(_normalize_local_targets(one), _normalize_local_targets(two))

    def test_expected_coverage_includes_scopes_and_tiles(self):
        catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
        tiles = tagged_json("isa/v0.59/state/pto_tile_operations.json")
        expected = _expected_pages(catalog, tiles)
        self.assertEqual(len(expected), 1363)
        self.assertEqual(sum(name.startswith("op-") for name in expected), 1259)
        self.assertEqual(sum(name.startswith("tile-") for name in expected), 104)
        scoped = next(
            row
            for row in catalog["instructions"]
            if row.get("pto_scope") and row["mnemonic"] == "C.LDI"
        )
        base = next(
            row
            for row in catalog["instructions"]
            if not row.get("pto_scope") and row["mnemonic"] == "C.LDI"
        )
        self.assertEqual(
            expected[
                f"op-c-ldi-{ {'Private': 'private', 'IntraCore': 'intra', 'InterCore': 'inter'}[scoped['pto_scope']] }.html"
            ].source_path,
            authored_for(base).source_path,
        )

    def test_c_movr_render_retains_complete_original_content(self):
        catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
        row = next(
            row
            for row in catalog["instructions"]
            if row["mnemonic"] == "C.MOVR" and not row.get("pto_scope")
        )
        article = authored_for(row)
        fragment = render_article(
            article.source_path, current_page="op-c-movr.html"
        ).html
        facts = _ArticleFacts()
        facts.feed(fragment)
        self.assertEqual(
            facts.headings[:7],
            [
                "说明",
                "汇编语法",
                "汇编符号",
                "编码格式",
                "执行方式",
                "汇编索引模式",
                "备注",
            ],
        )
        example_blocks = [
            [line for line in block.splitlines() if line.strip().startswith("c.movr ")]
            for block in facts.code
        ]
        self.assertEqual(
            sum(len(lines) for lines in example_blocks if len(lines) > 1), 9
        )
        self.assertTrue(
            any(
                image.get("alt") == "c.movr" and image.get("src", "").endswith(".svg")
                for image in facts.images
            )
        )
        self.assertTrue(
            any(
                "info" in classes.split() and "注意" in text
                for classes, text in facts.admonitions
            )
        )
        self.assertEqual(
            sha256(tagged_bytes(article.source_path)).hexdigest(),
            "06bdfc0ac0f3aefbd1f5c0594ba9288a98bd718e2c8c30f50ad85ccbb9011432",
        )


if __name__ == "__main__":
    unittest.main()
