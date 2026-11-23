#!/usr/bin/env python3

import json
from pathlib import Path
import unittest

try:
    from manual_authored import authored_for
    from manual_detail_vector import corrected_mnemonics, vector_body
    from manual_tag import tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_authored import authored_for
    from tools.isa.manual_detail_vector import corrected_mnemonics, vector_body
    from tools.isa.manual_tag import tagged_json


EXPECTED = {
    "HL.SETC.LTI",
    "HL.SETC.ORI",
    "V.CMP.AND",
    "V.CMP.ANDI",
    "V.FCVT",
    "V.FCVTI",
    "V.ICVT",
    "V.ICVTF",
    "V.LD.MIN",
    "V.REV",
    "V.SH.BRG",
    "V.SW.BRG",
    "V.SD.BRG",
}


class VectorDetailTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
        cls.rows = {
            row["mnemonic"]: row
            for row in cls.catalog["instructions"]
            if not row.get("pto_scope")
        }

    def body(self, mnemonic):
        row = self.rows[mnemonic]
        body = vector_body(row, None, authored_for(row))
        self.assertIsNotNone(body)
        return body

    def test_inventory_matches_audited_conflicts(self):
        self.assertEqual(corrected_mnemonics(), EXPECTED)
        for mnemonic in EXPECTED:
            body = self.body(mnemonic)
            self.assertIn("## 说明", body)
            self.assertNotIn("当前规范汇编", body)
            self.assertNotIn("历史", body)

    def test_boolean_and_is_not_bitwise_and(self):
        for mnemonic in ("V.CMP.AND", "V.CMP.ANDI"):
            body = self.body(mnemonic)
            self.assertIn("这不是先做按位与", body)
            self.assertIn("结果为 1", body)
            self.assertIn("结果未指定", body)

    def test_convert_forms_have_one_source_and_no_removed_operands(self):
        for mnemonic in ("V.FCVT", "V.FCVTI", "V.ICVT", "V.ICVTF"):
            body = self.body(mnemonic)
            self.assertIn("只有一个源寄存器", body)
            self.assertIn("不读取第二个源寄存器", body)
            self.assertIn("没有编码 `rm` 或 `sat`", body)
            fields = {
                field["name"]
                for part in self.rows[mnemonic]["encoding"]["parts"]
                for field in part["fields"]
            }
            self.assertIn("SrcL", fields)
            self.assertNotIn("SrcR", fields)
            self.assertNotIn("rm", fields)
            self.assertNotIn("sat", fields)

    def test_lti_ori_min_and_rev_state_correct_operation(self):
        self.assertIn("SrcL < (simm24 << shamt)", self.body("HL.SETC.LTI"))
        self.assertIn("按位或结果非零", self.body("HL.SETC.ORI"))
        self.assertIn("有符号最小值", self.body("V.LD.MIN"))
        self.assertIn("目的元素得到 7", self.body("V.LD.MIN"))
        self.assertIn("连续更新同一个内存单元", self.body("V.LD.MIN"))
        self.assertIn("不使用这三个值", self.body("V.LD.MIN"))
        self.assertIn("没有给出并发观察者之间的原子互斥规则", self.body("V.LD.MIN"))
        self.assertIn("0x44332211", self.body("V.REV"))
        self.assertIn("忽略编码中的 `immr` 和 `imml`", self.body("V.REV"))

    def test_every_brg_page_replaces_the_bridge_table_claim(self):
        brg = sorted(
            mnemonic
            for mnemonic in self.rows
            if mnemonic.startswith("V.") and mnemonic.endswith(".BRG")
        )
        self.assertEqual(len(brg), 33)
        for mnemonic in brg:
            body = self.body(mnemonic)
            self.assertIn("发布 Sail", body)
            self.assertIn("桥接表", body)
            self.assertIn("不使用它，也没有据此切换地址空间", body)
            if mnemonic.startswith(("V.L",)):
                self.assertIn("活动目的元素", body)
            elif not mnemonic.split(".")[1].endswith("I"):
                self.assertIn("lane 0", body)

    def test_brg_catalog_sail_shift_gap_is_visible(self):
        for mnemonic, scale in (
            ("V.SH.BRG", 1),
            ("V.SW.BRG", 2),
            ("V.SD.BRG", 3),
        ):
            body = self.body(mnemonic)
            self.assertIn("## 0.59.1 内部不一致", body)
            self.assertIn(f"SrcR << ({scale} + shamt)", body)
            self.assertIn("SrcR << shamt", body)
        self.assertNotIn("内部不一致", self.body("V.SD.U.BRG"))

    def test_brg_base_operand_follows_the_published_handler(self):
        self.assertIn("`SrcL`（标量基址）", self.body("V.LDI.BRG"))
        self.assertIn("`SrcL + (LC0 × 8)", self.body("V.SD.BRG"))
        self.assertIn("`SrcR`（标量基址）", self.body("V.SDI.BRG"))
        for mnemonic in ("V.LDI.BRG", "V.LDI.U.BRG", "V.SDI.BRG"):
            self.assertIn("直接把立即数作为字节偏移", self.body(mnemonic))

    def test_brg_lane_and_predicate_effects_follow_each_handler(self):
        self.assertIn("结果未指定", self.body("V.LW.BRG"))
        self.assertIn("保持原值", self.body("V.LD.BRG"))
        self.assertIn("不读取 P 掩码", self.body("V.SW.BRG"))
        immediate = self.body("V.SWI.BRG")
        self.assertIn("每个活动元素", immediate)
        self.assertIn("依次写到同一地址", immediate)
        self.assertIn("连续覆盖", immediate)
        self.assertNotIn("只使用 lane 0", immediate)

    def test_unrelated_vector_form_has_no_replacement(self):
        row = self.rows["V.ADD"]
        body = vector_body(row, None, authored_for(row))
        self.assertIn("左源寄存器", body)
        self.assertNotIn("无效lane中默认写0", body)
        self.assertIn("## 备注", body)
        self.assertIn(row["asm"], body)
        self.assertNotIn("## 汇编符号", body)
        self.assertNotIn("## 编码格式", body)
        self.assertNotIn("sat（saturation）", body)

    def test_every_vector_mnemonic_gets_a_clean_detail_body(self):
        vector_rows = {
            mnemonic: row
            for mnemonic, row in self.rows.items()
            if mnemonic.startswith("V.")
        }
        self.assertEqual(len(vector_rows), 184)
        for mnemonic, row in vector_rows.items():
            body = vector_body(row, None, authored_for(row))
            self.assertTrue(body and "## 说明\n" in body, mnemonic)
            self.assertNotIn("无效lane中默认写0", body, mnemonic)
            self.assertNotIn("中文原页", body, mnemonic)

    def test_lane_rules_match_published_sail_families(self):
        self.assertIn("结果未指定", self.body("V.CMP.OR"))
        self.assertIn("保持原值", self.body("V.FADD"))
        self.assertIn("不产生内存、队列或目的寄存器效果", self.body("V.SW"))
        self.assertIn("P 掩码为 0 的通道不参与", self.body("V.RDAND"))
        self.assertIn("全 1 恒等值", self.body("V.RDAND"))
        self.assertIn("不读取 P 掩码", self.body("V.PSEL"))

    def test_shuffle_reads_per_lane_operands_and_keeps_figure(self):
        body = self.body("V.SHFL.DOWN")
        self.assertIn("同一通道的 `SrcR`", body)
        self.assertIn("同一通道的 `SrcP`", body)
        self.assertIn("P 掩码为 0 的结果未指定", body)
        self.assertIn("shfl.down.png", body)
        immediate = self.body("V.SHFLI.IDX")
        self.assertIn("14 位无符号立即数", immediate)
        self.assertIn("同一通道的 `SrcR`", immediate)

    def test_compatible_examples_and_explanatory_figures_are_retained(self):
        self.assertIn("32 位载体", self.body("V.BCNT"))
        self.assertNotIn(
            "64 位位域语义", self.body("V.BCNT").split("没有 64 位位域语义")[0]
        )
        psel = self.body("V.PSEL")
        self.assertIn("## 优化场景", psel)
        self.assertIn("psel.png", psel)
        self.assertIn("psel1.png", psel)
        self.assertIn("psel2.png", psel)

    def test_source_owned_pages_are_the_single_reader_source(self):
        for mnemonic in EXPECTED:
            row = self.rows[mnemonic]
            article = authored_for(row)
            source = Path(article.source_path).read_text(encoding="utf-8")
            self.assertEqual(vector_body(row, None, article), source, mnemonic)

    def test_bitfield_family_is_bounded_to_the_32_bit_carrier(self):
        for mnemonic in (
            "V.BCNT",
            "V.BIC",
            "V.BIS",
            "V.BXS",
            "V.BXU",
            "V.CLZ",
            "V.CTZ",
        ):
            body = self.body(mnemonic)
            self.assertIn("32 位载体", body)
            self.assertIn("钳制到 32 位", body)
            self.assertIn("32 位环", body)
            self.assertIn("没有 64 位位域语义", body)
            self.assertNotIn("64 位循环移位", body.split("不对 64 位值执行循环移位")[0])

    def test_atomic_memory_family_states_the_actual_staged_order(self):
        for mnemonic in ("V.LW.ADD", "V.LD.XOR", "V.SW.MIN", "V.SD.MAX"):
            body = self.body(mnemonic)
            self.assertIn("同一个内存单元", body)
            self.assertIn("按通道递增顺序", body)
            self.assertIn("不使用这些位", body)
            self.assertIn("没有给出并发观察者之间的原子互斥规则", body)
            self.assertNotIn("执行结果不可知", body)

    def test_every_vector_form_is_bound_to_published_sail(self):
        sail = json.loads(
            Path(
                "docs/architecture/isa-manual/reference/data/manual-linx-sail.json"
            ).read_text()
        )
        vector_forms = {
            form_id: form
            for form_id, form in sail["forms"].items()
            if form["mnemonic"].startswith("V.")
        }
        self.assertEqual(len(vector_forms), 184)
        for form_id, form in vector_forms.items():
            self.assertEqual(form["disposition"], "calls-sail-helper", form_id)
            self.assertTrue(form["helpers"], form_id)
            for helper in form["helpers"]:
                self.assertIn(helper, sail["handlers"], form_id)


if __name__ == "__main__":
    unittest.main()
