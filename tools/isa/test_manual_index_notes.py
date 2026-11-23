#!/usr/bin/env python3

import unittest

try:
    from manual_index_notes import INDEX_NOTES, covered_mnemonics, index_note
except ModuleNotFoundError:
    from tools.isa.manual_index_notes import INDEX_NOTES, covered_mnemonics, index_note


class ManualIndexNotesTest(unittest.TestCase):
    def test_inventory_is_specific_chinese_prose(self):
        self.assertEqual(len(INDEX_NOTES), 53)
        self.assertEqual(set(covered_mnemonics()), set(INDEX_NOTES))
        for mnemonic, note in INDEX_NOTES.items():
            with self.subTest(mnemonic=mnemonic):
                self.assertRegex(note, r"[\u4e00-\u9fff]")
                self.assertTrue(note.endswith("。"))
                self.assertNotIn("中文增补说明", note)
                self.assertNotIn("当前规范汇编", note)

    def test_ccat_order_and_width_are_release_specific(self):
        self.assertIn("逻辑右移", index_note("HL.CCAT"))
        self.assertIn("低 64 位先写 Dst0", index_note("HL.CCAT"))
        self.assertIn("低、高 32 位分别符号扩展", index_note("HL.CCATW"))
        self.assertEqual(index_note({"mnemonic": "HL.CCATW"}), INDEX_NOTES["HL.CCATW"])

    def test_immediate_store_scaling_is_visible(self):
        from tools.isa.manual_prose_zh import memory_synopsis
        from tools.isa.manual_tag import tagged_json

        forms = {
            f["mnemonic"]: f
            for f in tagged_json("isa/v0.59/state/pto_scalar_forms.json")["forms"]
        }
        for name, factor in (("HL.SDI", 8), ("HL.SWI", 4), ("HL.SHI", 2)):
            for suffix, unscaled in (("", ".U"), (".PR", ".UPR"), (".PO", ".UPO")):
                scaled_note = memory_synopsis(
                    forms[name + suffix]["agu"], explain_displacement=True
                )
                raw_note = memory_synopsis(
                    forms[name + unscaled]["agu"], explain_displacement=True
                )
                self.assertIn(f"立即数乘 {factor}", scaled_note)
                self.assertIn("不缩放", raw_note)
        for name in ("BSTART.MPAR", "BSTART.MSEQ", "BSTART.VPAR", "BSTART.VSEQ"):
            self.assertIn("寄存器档位", index_note(name))

    def test_noncovered_mnemonic_has_no_override(self):
        self.assertIsNone(index_note("ADD"))


if __name__ == "__main__":
    unittest.main()
