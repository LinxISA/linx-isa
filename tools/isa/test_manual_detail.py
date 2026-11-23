"""Regression checks for published results which differ from the older Chinese pages."""

import json
from pathlib import Path
import unittest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_authored import authored_for
from manual_detail import instruction_body, revised_intro
from manual_tag import REPO_ROOT, tagged_json


class DetailRevisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = {
            row["mnemonic"]: row
            for row in tagged_json("isa/v0.59/linxisa-v0.59.json")["instructions"]
            if not row.get("pto_scope")
        }
        cls.owners = json.loads(
            (
                REPO_ROOT
                / "docs/architecture/isa-manual/reference/pto-v0591-semantics.json"
            ).read_text()
        )["forms"]

    def manuscript(self, name):
        return (REPO_ROOT / authored_for(self.rows[name]).source_path).read_text()

    def test_zero_divisor_and_word_extension(self):
        for prefix in ("", "HL."):
            for op in ("DIV", "REM"):
                for suffix in ("", "W", "U", "UW"):
                    self.assertIn(
                        "商为零，余数为被除数", self.manuscript(prefix + op + suffix)
                    )
        self.assertIn("0xffffffff80000000", self.manuscript("MULUW"))

    def test_concatenation_uses_an_asymmetric_example(self):
        for name, expected in (
            ("HL.CCAT", "0x8000000000000001"),
            ("HL.CCATW", "0xffffffff80000001"),
        ):
            text = self.manuscript(name)
            self.assertIn(expected, text)
            self.assertIn("逻辑右移", text)
            self.assertNotIn("循环左移", text)
            self.assertNotIn("不可知", text)

    def test_modifier_codes(self):
        for name in (
            "ADD",
            "ADDW",
            "SUB",
            "SUBW",
            "AND",
            "ANDW",
            "OR",
            "ORW",
            "XOR",
            "XORW",
        ):
            body = self.manuscript(name)
            self.assertIn("2b00 then operand2 = SignExtend", body)
            self.assertIn("2b11 then No operation", body)
            self.assertIn("| 00 | .sw |", body)
            self.assertIn("| 11 | 省略 |", body)
            owner = self.owners[self.rows[name]["pto_source_form_id"]]
            self.assertIn(
                "SrcRType=11 selects no modifier", " ".join(owner["defaults"])
            )

    def test_scalar_fp_type_table(self):
        for name, row in self.rows.items():
            if row["uop_big_kind"] != "FSU":
                continue
            owner = self.owners[row["pto_source_form_id"]]
            text = self.manuscript(name)
            if any(
                "SrcType codes 0 and 1 are assigned" in line
                for line in owner["legality"]
            ):
                self.assertIn("编码 2 和 3 保留", text, name)
                self.assertNotIn("FP16", text, name)
            else:
                self.assertIn("E4M3", text, name)
            self.assertIn("## 数据类型", text, name)

    def test_index_and_body_use_same_definition(self):
        row = self.rows["MULUW"]
        body = instruction_body([row], {}, authored_for(row), [])
        self.assertIn("符号扩展", revised_intro(body))
        self.assertNotIn("无符号扩展", revised_intro(body))

    def test_matrix_mx_width_and_explicit_accumulator(self):
        folder = REPO_ROOT / "docs/zh/isa/header/tileblock"
        for path in folder.glob("T*MX*.md"):
            if path.name.startswith(("TGEMV", "TMATMUL")):
                self.assertIn("64 个元素一组的 U32", path.read_text(), path)
        for name in ("TGEMV.ACC", "TMATMUL.ACC", "TGEMVMX.ACC", "TMATMULMX.ACC"):
            body = (folder / (name + ".md")).read_text()
            self.assertIn("C 是本地累加源", body)
            self.assertNotIn("ACC寄存器", body)
