import os
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

from tools.isa.manual_golden_datatypes import (
    FLOATING,
    INTEGERS,
    datatype_assets,
    datatype_index,
    datatype_pages,
    datatype_review,
    validate_datatype_authority,
)


class GoldenDatatypeTest(unittest.TestCase):
    def test_pages_cover_every_assigned_type_once(self):
        pages = datatype_pages()
        self.assertEqual(len(pages), 28)
        codes = []
        for _, body in pages.values():
            codes.extend(int(value) for value in re.findall(r'data-code="(\d+)"', body))
        self.assertEqual(len(codes), 27)
        self.assertEqual(len(codes), len(set(codes)))
        self.assertEqual(
            set(codes),
            {item.code for item in FLOATING.values()}
            | {item[0] for item in INTEGERS.values()},
        )
        self.assertNotIn("22", {str(value) for value in codes})
        self.assertIn("22、23、29、30、31 保留", pages["arch-datatype-intro.html"][1])

    def test_packed_and_integer_definitions_are_exact(self):
        pages = datatype_pages()
        fp4 = pages["arch-datatype-fp4.html"][1]
        self.assertIn("E2M1X2", fp4)
        self.assertIn("E1M2X2", fp4)
        self.assertIn("1 位符号和 3 位幅值，没有独立指数域", fp4)
        self.assertIn("两个 4 位 lane", fp4)
        self.assertIn("[-2147483648, 2147483647]", pages["arch-datatype-int32.html"][1])
        self.assertIn("[0, 15]", pages["arch-datatype-uint4.html"][1])

    def test_matrix_mx_and_scale_boundaries_are_explicit(self):
        pages = datatype_pages()
        self.assertIn("不绑定缩放 Tile", pages["arch-datatype-fp16.html"][1])
        self.assertIn("每 32 个元素", pages["arch-datatype-mxfp4.html"][1])
        self.assertIn("E8M0", pages["arch-datatype-mxfp8.html"][1])
        self.assertIn("每 64 个元素", pages["arch-datatype-hif4.html"][1])
        scale = pages["arch-datatype-hif-scale.html"][1]
        self.assertIn("普通 <code>U32</code>", scale)
        self.assertIn("位 15:8", scale)
        self.assertIn("位 31:16", scale)
        self.assertIn("64 个逻辑 HiF4 lane", scale)

    def test_non_ieee_encodings_have_exact_special_value_rules(self):
        pages = datatype_pages()
        e8m0 = pages["arch-datatype-mx-scale.html"][1]
        self.assertIn("0x00 至 0xFE", e8m0)
        self.assertIn("2^(E−127)", e8m0)
        self.assertIn("0xFF 表示安静 NaN", e8m0)
        e6m2 = pages["arch-datatype-e6m2.html"][1]
        self.assertIn("(1+M/4)×2^(E−48)", e6m2)
        rcpe = pages["arch-datatype-rcpe6m2.html"][1]
        self.assertIn("E6M2 有限值的倒数", rcpe)
        e4m3 = pages["arch-datatype-fp8.html"][1]
        self.assertIn("不定义无穷或信号 NaN", e4m3)

    def test_review_disposes_every_old_page(self):
        review = datatype_review()
        self.assertEqual(len(review), 27)
        removed = {
            path: record
            for path, record in review.items()
            if record["disposition"] == "removed-unassigned-composite"
        }
        self.assertEqual(set(removed), {"docs/zh/isa/datatype/MXFP6.md"})
        pages = datatype_pages()
        for path, record in review.items():
            with self.subTest(path=path):
                self.assertTrue(record["authority"])
                if record["route"]:
                    self.assertIn(record["route"], pages)

    def test_index_and_assets_reference_only_current_pages(self):
        pages = datatype_pages()
        title, body = datatype_index()
        self.assertEqual(title, "数据类型")
        self.assertNotIn("MXFP6", body)
        self.assertIn("arch-datatype-rcpe6m2.html", body)
        assets = datatype_assets()
        self.assertEqual(len(assets), 28)
        self.assertTrue(all(name.startswith("figures/datatypes/") for name in assets))
        self.assertTrue(all(name.endswith(".svg") for name in assets))
        referenced = {
            source
            for _, body in pages.values()
            for source in re.findall(r'<img src="([^"]+)"', body)
        }
        self.assertEqual(referenced, set(assets))
        for name, data in assets.items():
            with self.subTest(asset=name):
                root = ET.fromstring(data)
                self.assertGreaterEqual(int(root.attrib["width"]), 800)
                self.assertGreaterEqual(int(root.attrib["height"]), 200)
                self.assertGreaterEqual(
                    len(root.findall("{http://www.w3.org/2000/svg}rect")), 2
                )
                self.assertGreater(len(data), 800)

    def test_generated_bitfields_show_constrained_and_dynamic_regions(self):
        assets = {name: data.decode() for name, data in datatype_assets().items()}
        self.assertIn("[12:0] 必须为 0 · 13 位", assets["figures/datatypes/tf32.svg"])
        self.assertIn("[7:6] 必须为 0 · 2 位", assets["figures/datatypes/e3m2.svg"])
        self.assertIn("lane1 M", assets["figures/datatypes/e1m2x2.svg"])
        self.assertNotIn("lane1 E", assets["figures/datatypes/e1m2x2.svg"])
        self.assertIn("lane1 E", assets["figures/datatypes/hif4x2.svg"])
        hif8 = assets["figures/datatypes/hif8.svg"]
        self.assertIn("D/E/M 动态区", hif8)
        self.assertNotIn("[6:3] E", hif8)
        self.assertIn(
            "001、01、10、11 分别选择 1、2、3、4 位指数",
            datatype_pages()["arch-datatype-hif8.html"][1],
        )
        scale = assets["figures/datatypes/hif4-scale.svg"]
        for literal in ("[31:16] E1_16", "[15:8] E1_8", "[7:0] E6M2"):
            self.assertIn(literal, scale)

    def test_locked_pto_sources_match_all_numeric_values(self):
        root = os.environ.get("PTO_SPEC_ROOT")
        if not root:
            self.skipTest("PTO_SPEC_ROOT is not set")
        errors = validate_datatype_authority(Path(root))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
