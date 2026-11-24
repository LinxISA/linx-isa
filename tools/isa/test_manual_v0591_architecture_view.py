from __future__ import annotations

import json
from pathlib import Path
import unittest

from tools.isa.manual_v0591_architecture_view import assets
from tools.isa.manual_v0591_architecture_view import audit
from tools.isa.manual_v0591_architecture_view import pages
from tools.isa.manual_v0591_architecture_view import routes


ROOT = Path(__file__).resolve().parents[2]


class ManualV0591ArchitectureViewTest(unittest.TestCase):
    def test_api_is_current_only_and_complete(self):
        rendered = pages()
        route_map = routes()
        self.assertEqual(len(rendered), 34)
        self.assertEqual(len(route_map), 134)
        self.assertTrue(set(rendered) <= set(route_map))
        body = "\n".join(html for _title, html in rendered.values())
        for stale in (
            "0.59.2",
            "VGPR",
            "BSTART.MPAR",
            "BSTART.MSEQ",
            "BSTART.VPAR",
            "BSTART.VSEQ",
            "B.TEXT",
        ):
            self.assertNotIn(stale, body)
        self.assertIn("HL.BSTART.FP FALL", body)
        self.assertIn("L.BSTART.STD FALL", body)
        self.assertIn("T#1", body)
        self.assertIn("LB0", body)
        self.assertIn("MGATHER_MASK", body)

    def test_ssr_page_renders_every_locked_definition_and_behavior(self):
        document = json.loads(
            (ROOT / "isa/v0.59/state/pto_system_registers.json").read_text(
                encoding="utf-8"
            )
        )
        body = pages()["arch-ssr.html"][1]
        self.assertEqual(document["register_definition_count"], 100)
        for row in document["registers"]:
            self.assertIn(f'id="ssr-{row["name"].lower().replace("_", "-")}"', body)
        self.assertIn("读取", body)
        self.assertIn("写入", body)
        self.assertIn("复位值", body)
        self.assertIn("当前含义", body)

    def test_datatype_assets_are_real_svg_diagrams(self):
        diagrams = assets()
        self.assertEqual(len(diagrams), 28)
        for name, data in diagrams.items():
            self.assertTrue(name.endswith(".svg"), name)
            self.assertTrue(data.lstrip().startswith(b"<svg"), name)
            self.assertGreater(len(data), 500, name)
            self.assertNotIn(b'width="1"', data, name)
            self.assertNotIn(b'height="1"', data, name)

    def test_audit_binds_catalog_lock_ssr_tile_and_fall_forms(self):
        report = audit()
        self.assertEqual(report["version"], "0.59.1")
        self.assertEqual(report["catalog_forms"], 1306)
        self.assertEqual(report["ssr_count"], 100)
        self.assertEqual(report["tile_operation_count"], 119)
        self.assertEqual(len(report["fall_forms"]), 6)
        self.assertEqual(report["page_count"], 34)
        self.assertEqual(report["asset_count"], 28)
        serialized = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("LCFR", serialized)
        self.assertNotIn("LCFR_EN", serialized)
        self.assertNotIn("docs/zh/isa/register/ssr/", serialized)


if __name__ == "__main__":
    unittest.main()
