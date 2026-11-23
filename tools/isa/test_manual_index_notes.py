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

    def test_noncovered_mnemonic_has_no_override(self):
        self.assertIsNone(index_note("ADD"))


if __name__ == "__main__":
    unittest.main()
