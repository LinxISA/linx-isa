#!/usr/bin/env python3

import unittest

try:
    from manual_authored import authored_for
    from manual_detail_atomic import atomic_body, validate_atomic_bodies
    from manual_tag import tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_authored import authored_for
    from tools.isa.manual_detail_atomic import atomic_body, validate_atomic_bodies
    from tools.isa.manual_tag import tagged_json


class ManualDetailAtomicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = tagged_json("isa/v0.59/linxisa-v0.59.json")["instructions"]
        cls.amo = {
            row["mnemonic"]: row
            for row in cls.rows
            if row["uop_big_kind"] == "AMO" and not row.get("pto_scope")
        }

    def body(self, name):
        row = self.amo[name]
        return atomic_body(row, article=authored_for(row))

    def test_all_61_base_amo_forms_have_current_body(self):
        self.assertEqual(61, len(self.amo))
        self.assertEqual([], validate_atomic_bodies(self.rows))

    def test_lr_sc_reservation_and_failure_contract(self):
        lr = self.body("LR.B")
        sc = self.body("SC.B")
        self.assertIn("64 字节粒度", lr)
        self.assertIn("零扩展后的字节", lr)
        self.assertIn("未命中路径", sc)
        self.assertIn("从不调用 ProbeDataAccess", sc)
        self.assertIn("成功、未命中以及命中同行的访问故障", sc)

    def test_cas_and_swap_return_normalization(self):
        casb = self.body("CASB")
        swapw = self.body("SWAPW")
        self.assertIn("0x0000000000000080", casb)
        self.assertIn("不是 0xffffffffffffff80", casb)
        self.assertIn("符号扩展到 64 位", swapw)
        self.assertNotIn("32位`数据无符号扩展", swapw)
        hl_casw = self.body("HL.CASW")
        self.assertIn("两种无故障结果都会把原来的字", hl_casw)
        self.assertIn("符号扩展到 64 位", hl_casw)
        self.assertNotIn("无符号扩展后写入目的寄存器", hl_casw)

    def test_dma_is_exactly_64_bytes_and_preflighted(self):
        dma = self.body("DMA")
        self.assertIn("恰好 64 字节", dma)
        self.assertIn("两个完整范围都必须通过预检", dma)
        self.assertIn("8 个 8 字节的载入事件", dma)
        self.assertIn("8 个 8 字节的存储事件", dma)

    def test_dma_free_encodings_are_explicitly_unsupported(self):
        for name in ("DMA.FREE.L", "DMA.FREE.S"):
            body = self.body(name)
            self.assertIn("只保留编码", body)
            self.assertIn("非法指令", body)
            self.assertIn("读取 `SrcL`", body)
            self.assertIn("不会复制或释放 DMA 资源", body)

    def test_scoped_forms_are_owned_by_base_semantics(self):
        scoped = next(
            row
            for row in self.rows
            if row.get("pto_scope") and row.get("uop_big_kind") == "AMO"
        )
        self.assertIsNone(atomic_body(scoped))


if __name__ == "__main__":
    unittest.main()
