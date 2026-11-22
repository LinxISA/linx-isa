#!/usr/bin/env python3

import json
from pathlib import Path
import re
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

from tools.isa.manual_supplements import (
    INSTRUCTION_PATHS,
    TILE_PATHS,
    instruction_supplement,
    supplement_mapping,
    tile_supplement,
    validate_supplements,
)
import tools.isa.manual_supplements as SUPPLEMENTS


class ManualSupplementsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "isa/v0.59/linxisa-v0.59.json").read_text())
        cls.tiles = json.loads(
            (ROOT / "isa/v0.59/state/pto_tile_operations.json").read_text()
        )["operations"]

    def test_exact_missing_sets_and_identity_mapping(self):
        self.assertEqual(
            set(INSTRUCTION_PATHS),
            {
                "B.ASSEMBLE",
                "B.FPATR",
                "B.SUBVIEW",
                "BSTART.TIMG2COL",
                "FENCE.D",
                "FENCE.I",
                "SYNC.CORE",
            },
        )
        self.assertEqual(
            set(TILE_PATHS),
            {
                "TFMA",
                "TROWARGMAX",
                "TROWARGMIN",
                "TCOLARGMAX",
                "TCOLARGMIN",
                "TCI",
                "TTRI",
                "GMOV",
                "TPERMUTE",
                "TSHUF",
                "TPACK",
                "TUNPACK",
                "TGPR2T",
                "TEXPDIF",
                "TLEA",
            },
        )
        mapping = supplement_mapping()
        self.assertEqual(len(mapping), 22)
        for row in self.catalog["instructions"]:
            if row["mnemonic"] in INSTRUCTION_PATHS and not row.get("pto_scope"):
                self.assertIn(row["id"], mapping)
                self.assertEqual(mapping[row["id"]], instruction_supplement(row))
        for op in self.tiles:
            if op["name"] in TILE_PATHS:
                identity = f"tile:{op['engine']}:{op.get('mode', '-')}:{op['function']}:{op['name']}"
                self.assertIn(identity, mapping)
                self.assertEqual(mapping[identity], tile_supplement(op))

    def test_all_supplements_are_source_valid_and_readable(self):
        self.assertEqual(validate_supplements(), [])
        for path in map(Path, supplement_mapping().values()):
            text = path.read_text(encoding="utf-8")
            self.assertIn("> **0.59.1 增补**", text)
            self.assertRegex(text, r"[\u4e00-\u9fff]")
            self.assertNotIn("DOC-BEGIN", text)
            self.assertNotIn("以下为非规范示例，仅用于说明当前所有者", text)
            marker = json.loads(
                re.match(r"<!-- LINXISA-SUPPLEMENT: (\{.*\}) -->", text).group(1)
            )
            self.assertRegex(marker["reader_source_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(marker["pto_source_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(marker["pto_instruction_sha256"], r"^[0-9a-f]{64}$")

    def test_strict_pinned_source_validation_and_wrong_digest_rejection(self):
        pto_root = Path(
            "/Users/zhoubot/.codex/worktrees/pto-spec/published-0591-source"
        )
        if not pto_root.is_dir():
            self.skipTest("published PTO 0.59.1 source checkout is unavailable")
        self.assertEqual(validate_supplements(pto_root), [])
        original = SUPPLEMENTS._metadata

        def wrong_digest(path):
            value = original(path)
            if path.name == "b-assemble.md":
                value = dict(value)
                value["reader_source_sha256"] = "0" * 64
            return value

        with mock.patch.object(SUPPLEMENTS, "_metadata", side_effect=wrong_digest):
            errors = validate_supplements(pto_root)
        self.assertTrue(
            any(
                "b-assemble.md: Chinese reader source digest differs" in error
                for error in errors
            )
        )

    def test_representative_facts_and_examples_are_preserved(self):
        fence = Path(
            instruction_supplement(
                next(
                    row
                    for row in self.catalog["instructions"]
                    if row["mnemonic"] == "FENCE.D"
                )
            )
        ).read_text()
        self.assertIn("PRED_IMM", fence)
        self.assertIn("fence.d 8, 1", fence)
        self.assertIn("Fault_BundleControl", fence)
        assemble = Path(
            next(
                path
                for identity, path in supplement_mapping().items()
                if identity.startswith("b_assemble_")
            )
        ).read_text()
        self.assertIn("B.ASSEMBLE 1, 0, zero, 0, 5", assemble)
        self.assertIn("WriterSizeCode", assemble)
        self.assertIn("对正常参与的绑定组，指令读取 GPR[RegSrc]", assemble)
        self.assertIn("只有前置绑定的 PEMode=000", assemble)
        self.assertNotIn("在该组中，每条原始字段合法", assemble)
        tfma = Path(tile_supplement("TFMA")).read_text()
        self.assertIn("tile:VEC:0:28:TFMA", tfma)
        self.assertIn("0x01C", tfma)
        self.assertIn("left * right + addend", tfma)
        lea = Path(tile_supplement("TLEA")).read_text()
        self.assertIn("[0, 4, 8]", lea)
        self.assertIn("0x02E", lea)

    def test_no_dangling_context_or_repeated_wrapper_prose(self):
        forbidden = (
            "在该组中",
            "该图",
            "上述位映射",
            "参见范围修饰符",
            "当前所有者",
            "该写法示例只用于说明",
        )
        for path in map(Path, supplement_mapping().values()):
            text = path.read_text(encoding="utf-8")
            for phrase in forbidden:
                self.assertNotIn(phrase, text, f"{path.name}: {phrase}")
            self.assertEqual(text.count("> **0.59.1 增补**"), 1)
            self.assertNotIn("本页补足 0.59.1 芯片开发手册中缺少的中文说明。", text)


if __name__ == "__main__":
    unittest.main()
