#!/usr/bin/env python3

from __future__ import annotations

import copy
from html.parser import HTMLParser
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from manual_diagrams import (
    _catalog_segments,
    _legacy_segments,
    _svg_matches_json,
    make_diagrams,
)
from manual_tag import tagged_bytes, tagged_json


class FigureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.figures = 0
        self.images: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "figure" and "encoding-diagram" in values.get("class", "").split():
            self.figures += 1
        if tag == "img":
            self.images.append(values.get("src", ""))


class ManualDiagramsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
        cls.by_id = {row["id"]: row for row in cls.catalog["instructions"]}
        cls.html, cls.assets, cls.audit = make_diagrams(cls.catalog)

    def test_every_form_and_part_has_one_offline_asset(self) -> None:
        self.assertEqual(len(self.html), 1306)
        self.assertEqual(len(self.assets), 2021)
        self.assertEqual(self.audit["form_count"], 1306)
        self.assertEqual(self.audit["asset_count"], 2021)
        for form_id, row in self.by_id.items():
            with self.subTest(form=form_id):
                parser = FigureParser()
                parser.feed(self.html[form_id])
                self.assertEqual(parser.figures, len(row["parts"]))
                self.assertEqual(len(parser.images), len(row["parts"]))
                self.assertTrue(all(path in self.assets for path in parser.images))
                self.assertEqual(
                    [part["part"] for part in self.audit["forms"][form_id]["parts"]],
                    list(range(len(row["parts"]))),
                )

    def test_original_wavedrom_assets_are_only_used_after_exact_bit_match(self) -> None:
        self.assertEqual(sum(self.audit["source_counts"].values()), 2021)
        for form_id, record in self.audit["forms"].items():
            row = self.by_id[form_id]
            for part in record["parts"]:
                if part["source"] != "tagged-original-wavedrom-svg":
                    continue
                with self.subTest(form=form_id):
                    source_json = tagged_bytes(part["json_path"])
                    self.assertEqual(
                        _legacy_segments(source_json, row["mnemonic"]),
                        _catalog_segments(row, part["part"]),
                    )
                    self.assertEqual(
                        self.assets[part["asset"]], tagged_bytes(part["svg_path"])
                    )

    def test_c_movr_reuses_exact_original_chinese_svg(self) -> None:
        form_id = "c_movr_16_12f1ae6e940f"
        part = self.audit["forms"][form_id]["parts"][0]
        self.assertEqual(part["source"], "tagged-original-wavedrom-svg")
        self.assertEqual(
            part["svg_path"], "docs/zh/figs/bitfield/svg/Instruction_16bit/C.MOVR.svg"
        )
        self.assertEqual(
            part["svg_sha256"],
            "6ad97a3e486198d19869f78a46874acd7b25a5069255fba183ecab1bb12af12c",
        )
        self.assertEqual(part["padded_blank_bits"], 16)
        self.assertIn("原图上半部留白，指令实际为 16 位", self.html[form_id])
        self.assertEqual(self.assets[part["asset"]], tagged_bytes(part["svg_path"]))

    def test_corrupted_original_svg_is_rejected(self) -> None:
        form_id = "c_movr_16_12f1ae6e940f"
        part = self.audit["forms"][form_id]["parts"][0]
        svg = tagged_bytes(part["svg_path"])
        source_json = tagged_bytes(part["json_path"])
        self.assertTrue(_svg_matches_json(svg, source_json, "C.MOVR"))
        self.assertFalse(
            _svg_matches_json(svg.replace(b"SrcL", b"BadL"), source_json, "C.MOVR")
        )

    def test_scoped_fallback_is_grouped_per_part_and_valid_svg(self) -> None:
        row = next(
            row
            for row in self.catalog["instructions"]
            if row["mnemonic"] == "CASB" and row.get("pto_scope") == "Private"
        )
        parts = self.audit["forms"][row["id"]]["parts"]
        self.assertEqual(len(parts), 2)
        self.assertTrue(
            all(part["source"] == "tagged-catalog-svg-generator" for part in parts)
        )
        for part in parts:
            svg = self.assets[part["asset"]]
            ET.fromstring(svg)
            self.assertIn(b"32 \xe4\xbd\x8d\xe7\xbc\x96\xe7\xa0\x81", svg)

    def test_all_svg_assets_are_well_formed_and_script_free(self) -> None:
        for path, data in self.assets.items():
            with self.subTest(path=path):
                root = ET.fromstring(data)
                self.assertTrue(root.tag.endswith("svg"))
                self.assertFalse(
                    any(node.tag.endswith("script") for node in root.iter())
                )

    def test_catalog_drift_fails_closed(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["instructions"][0]["asm"] += " corrupt"
        with self.assertRaisesRegex(ValueError, "differs from reviewed release tag"):
            make_diagrams(catalog)


if __name__ == "__main__":
    unittest.main()
