#!/usr/bin/env python3
from __future__ import annotations
import unittest
from manual_tile_index_notes import (
    command_index_notes,
    tile_index_note,
    validate_tile_index_notes,
)


class TileIndexNotesTest(unittest.TestCase):
    def test_all_operations_have_specific_chinese_note(self):
        self.assertEqual(validate_tile_index_notes(), [])

    def test_gather_scatter_discriminators_are_explicit(self):
        self.assertIn("将旧值写入本地目标 Tile", tile_index_note("MGATHER_ADD"))
        self.assertIn("不返回旧值", tile_index_note("MSCATTER_ADD"))
        self.assertIn("不生成地址", tile_index_note("MGATHER_MASK"))
        self.assertIn("比较交换", tile_index_note("MGATHER_CAS"))
        self.assertIn("U32", tile_index_note("MSCATTER_POPC"))

    def test_typed_command_notes_do_not_repeat_family_intro(self):
        notes = command_index_notes()
        self.assertNotEqual(notes["BSTART.MGATHER.ADD"], notes["BSTART.MGATHER.AND"])
        self.assertNotEqual(notes["BSTART.MSCATTER.ADD"], notes["BSTART.MSCATTER.XOR"])
        self.assertIn("原子加法", notes["BSTART.MGATHER.ADD"])


if __name__ == "__main__":
    unittest.main()
