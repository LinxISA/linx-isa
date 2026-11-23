#!/usr/bin/env python3
"""Regression tests for mnemonic-specific index synopses."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_index_families import family_index_synopsis, overridden_mnemonics
from manual_tag import REVIEWED_COMMIT, tagged_bytes, verified_tag_commit


class IndexFamilySynopsisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(
            Path("isa/v0.59/linxisa-v0.59.json").read_text(encoding="utf-8")
        )

    def test_exact_reviewed_tag_and_coverage(self) -> None:
        self.assertEqual(verified_tag_commit(), REVIEWED_COMMIT)
        catalogued = {row["mnemonic"] for row in self.catalog["instructions"]}
        self.assertEqual(len(overridden_mnemonics()), 44)
        self.assertLessEqual(overridden_mnemonics(), catalogued)
        self.assertEqual(
            {name for name in catalogued if ".BRG" in name},
            {name for name in overridden_mnemonics() if ".BRG" in name},
        )

    def test_scalar_copy_paste_is_replaced_by_the_selected_operation(self) -> None:
        lti = family_index_synopsis("HL.SETC.LTI")
        ori = family_index_synopsis("HL.SETC.ORI")
        self.assertIn("有符号小于", lti)
        self.assertNotIn("大于等于", lti)
        self.assertIn("按位或", ori)
        self.assertNotIn("大于等于", ori)
        source = tagged_bytes("docs/zh/isa/inst/misa_h/HL.SETC.LTI.md").decode()
        self.assertIn("大于等于立即数", source)  # Demonstrates the tagged copied prose.

    def test_shuffle_variants_keep_their_source_selector(self) -> None:
        self.assertIn("SrcP 掩码", family_index_synopsis("V.SHFL.BFLY"))
        self.assertIn("加到当前通道 ID", family_index_synopsis("V.SHFL.DOWN"))
        self.assertIn("SrcP 索引值", family_index_synopsis("V.SHFL.IDX"))
        self.assertIn("减去立即数偏移量", family_index_synopsis("V.SHFLI.UP"))
        source = tagged_bytes("docs/zh/isa/inst/misa_v/V.SHFL.DOWN.md").decode()
        self.assertIn("当前通道ID加上偏移值", source)

    def test_brg_summaries_match_signed_tag_stage_handlers(self) -> None:
        load = family_index_synopsis("V.LW.BRG")
        store = family_index_synopsis("V.SW.BRG")
        immediate_store = family_index_synopsis("V.SWI.U.BRG")
        self.assertIn("第 0 通道的索引形成单一地址", load)
        self.assertIn("广播到活动通道", load)
        self.assertIn("第 0 通道的数据存储 32 位", store)
        self.assertIn("各活动通道依次向同一有效地址", immediate_store)
        self.assertIn(".U 当前复用", immediate_store)
        sail = tagged_bytes("isa/sail/model/execute/execute.sail").decode()
        self.assertIn("let idx0 : bits(32) = vec_get_lane32(idxv, 0);", sail)
        self.assertIn("mem_store32_le(ea0, vec_get_lane32(data, 0))", sail)
        self.assertIn("exec_v_swi(SrcL_k, SrcR, simm24, local)", sail)

    def test_atomic_min_is_not_the_copied_maximum(self) -> None:
        text = family_index_synopsis("V.LD.MIN")
        self.assertIn("最小值", text)
        self.assertNotIn("最大值", text)
        source = tagged_bytes("docs/zh/isa/inst/misa_v/V.LD.MIN.md").decode()
        self.assertIn("最大值比较", source)  # Tagged article contains the copy error.
        sail = tagged_bytes("isa/sail/model/execute/execute.sail").decode()
        self.assertIn("function exec_v_ld_min", sail)

    def test_unknown_mnemonic_has_no_override(self) -> None:
        self.assertEqual(family_index_synopsis("V.ADD"), "")


if __name__ == "__main__":
    unittest.main()
