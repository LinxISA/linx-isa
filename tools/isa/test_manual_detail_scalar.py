import unittest

try:
    from manual_authored import authored_for
    from manual_detail_scalar import scalar_body
    from manual_tag import tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_authored import authored_for
    from tools.isa.manual_detail_scalar import scalar_body
    from tools.isa.manual_tag import tagged_json


class ScalarDetailBodyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = tagged_json("isa/v0.59/linxisa-v0.59.json")["instructions"]
        cls.sources = {
            form["form_id"]: form
            for path in (
                "isa/v0.59/state/pto_scalar_forms.json",
                "isa/v0.59/state/pto_command_forms.json",
            )
            for form in tagged_json(path)["forms"]
        }

    def body(self, mnemonic):
        row = next(
            row
            for row in self.rows
            if row["mnemonic"] == mnemonic and not row.get("pto_scope")
        )
        source = self.sources[row["pto_source_form_id"]]
        return scalar_body(row, source, authored_for(row))

    def test_every_conflicting_non_vector_article_has_a_replacement(self):
        replaced = []
        for row in self.rows:
            if row.get("pto_scope") or row["mnemonic"].startswith("V."):
                continue
            article = authored_for(row)
            if article is None or article.classification != "conflicting-current":
                continue
            source = self.sources[row["pto_source_form_id"]]
            body = scalar_body(row, source, article)
            self.assertTrue(body, row["id"])
            self.assertIn("## 说明", body)
            self.assertIn("## 架构效果", body)
            self.assertNotIn("当前规范汇编", body)
            replaced.append(row["id"])
        self.assertEqual(len(replaced), 28)

    def test_ccat_replaces_the_wrong_direction_and_destination_order(self):
        body = self.body("HL.CCAT")
        self.assertIn("逻辑右移", body)
        self.assertIn("先 Dst0", body)
        self.assertIn("再 Dst1", body)
        self.assertNotIn("循环左移", body)
        self.assertNotIn("先 Dst1", body)

    def test_ccatw_covers_word_selection_extension_and_large_shift(self):
        body = self.body("HL.CCATW")
        self.assertIn("SrcL 的低字", body)
        self.assertIn("SrcR 的低字", body)
        self.assertIn("符号扩展", body)
        self.assertIn("shamt 取 64..127 时，两个结果都为零", body)

    def test_operandless_maintenance_does_not_retain_old_register_operand(self):
        for mnemonic in ("BC.IALL", "DC.IALL", "IC.IALL"):
            with self.subTest(mnemonic=mnemonic):
                body = self.body(mnemonic)
                self.assertRegex(body, r"没有(?:任何)?(?:编码)?操作数(?:字段)?|全零")
                self.assertNotIn("SrcL", body)

    def test_immediate_stores_use_srcd_and_released_address_rules(self):
        expectations = {
            "HL.SBI": ("1 字节", "不缩放"),
            "HL.SHI": ("2 字节", "乘以 2"),
            "HL.SWI": ("4 字节", "乘以 4"),
            "HL.SDI": ("8 字节", "乘以 8"),
            "HL.SHI.U": ("2 字节", "不缩放"),
            "HL.SWI.U": ("4 字节", "不缩放"),
            "HL.SDI.U": ("8 字节", "不缩放"),
        }
        for mnemonic, phrases in expectations.items():
            with self.subTest(mnemonic=mnemonic):
                body = self.body(mnemonic)
                self.assertIn("SrcD", body)
                self.assertNotIn("SrcL", body)
                for phrase in phrases:
                    self.assertIn(phrase, body)

    def test_pre_and_post_index_store_updates_are_unambiguous(self):
        for mnemonic in ("HL.SDI.PR", "HL.SDI.UPR"):
            self.assertIn("新基址既作为有效地址", self.body(mnemonic))
        for mnemonic in ("HL.SDI.PO", "HL.SDI.UPO"):
            self.assertIn("本次存储使用原 SrcR", self.body(mnemonic))

    def test_setc_operations_do_not_retain_the_wrong_comparison(self):
        less = self.body("HL.SETC.LTI")
        bit_or = self.body("HL.SETC.ORI")
        self.assertIn("有符号小于", less)
        self.assertNotIn("大于等于", less)
        self.assertIn("按位或", bit_or)
        self.assertIn("非零", bit_or)
        self.assertNotIn("大于等于", bit_or)

    def test_changed_command_families_are_bound_to_each_specific_form(self):
        for mnemonic in ("B.DATR", "B.IOS", "B.IOT", "BSTART"):
            rows = [
                row
                for row in self.rows
                if row["mnemonic"] == mnemonic and not row.get("pto_scope")
            ]
            bodies = []
            for row in rows:
                source = self.sources[row["pto_source_form_id"]]
                body = scalar_body(row, source, authored_for(row))
                self.assertTrue(body, row["id"])
                bodies.append(body)
            self.assertEqual(len(set(bodies)), len(rows), mnemonic)

    def test_contextual_agu_bru_and_sys_pages_use_current_form_prose(self):
        for mnemonic in (
            "HL.LB.PCR",
            "HL.LDI.UPR",
            "CMP.AND",
            "SETC.OR",
            "TLB.IALL",
            "SSRSWAP",
        ):
            with self.subTest(mnemonic=mnemonic):
                self.assertTrue(self.body(mnemonic))

    def test_linx_register_mode_starts_do_not_reuse_the_generic_bstart_page(self):
        for row in self.rows:
            if row["mnemonic"] not in {
                "BSTART.MPAR",
                "BSTART.MSEQ",
                "BSTART.VPAR",
                "BSTART.VSEQ",
                "C.BSTART.MPAR",
                "C.BSTART.MSEQ",
                "C.BSTART.VPAR",
                "C.BSTART.VSEQ",
            }:
                continue
            body = scalar_body(row, {}, authored_for(row))
            self.assertIn("寄存器资源", body)
            if row["mnemonic"].startswith("C."):
                self.assertIn("固定的向量寄存器档位", body)
            else:
                self.assertIn("VS8 提供 2 组", body)
                self.assertNotIn("采用 FALL", body)
            if row["mnemonic"] in {"BSTART.VPAR", "BSTART.VSEQ"}:
                self.assertIn("B.TEXT", body)

    def test_audited_compatible_pages_use_their_exact_current_form(self):
        for mnemonic in ("HL.LDI", "CMP.EQ", "DC.CIVA"):
            row = next(
                row
                for row in self.rows
                if row["mnemonic"] == mnemonic and not row.get("pto_scope")
            )
            source = self.sources[row["pto_source_form_id"]]
            body = scalar_body(row, source, authored_for(row))
            self.assertIn(source["asm"], body)

    def test_every_current_agu_bru_and_sys_form_has_a_reviewed_body(self):
        covered = {"AGU": 0, "BRU": 0, "SYS": 0}
        for row in self.rows:
            if (
                row.get("pto_scope")
                or row.get("pto_source_form_id") not in self.sources
            ):
                continue
            source = self.sources[row["pto_source_form_id"]]
            family = source["semantic_family"]
            if family not in covered:
                continue
            article = authored_for(row)
            if article is None:
                continue
            body = scalar_body(row, source, article)
            self.assertTrue(body, row["id"])
            self.assertIn(source["asm"], body)
            self.assertNotIn("当前 ASL", body)
            self.assertNotIn("处理程序", body)
            covered[family] += 1
        self.assertEqual(covered, {"AGU": 183, "BRU": 58, "SYS": 33})

    def test_missing_sys_articles_are_current_release_supplements(self):
        paths = {
            "FENCE.D": "fence-d.md",
            "FENCE.I": "fence-i.md",
            "SYNC.CORE": "sync-core.md",
        }
        root = (
            __import__("pathlib").Path(__file__).resolve().parents[2]
            / "docs/zh/architecture/isa-manual/supplements"
        )
        for mnemonic, filename in paths.items():
            text = (root / filename).read_text(encoding="utf-8")
            self.assertIn('"version": "0.59.1"', text, mnemonic)
            self.assertIn(f"# {mnemonic}", text, mnemonic)

    def test_each_agu_body_states_transfer_width_addressing_and_update(self):
        for row in self.rows:
            source = self.sources.get(row.get("pto_source_form_id"))
            if row.get("pto_scope") or not source or source["semantic_family"] != "AGU":
                continue
            body = scalar_body(row, source, authored_for(row))
            agu = source["agu"]
            with self.subTest(form=row["id"]):
                if agu["action"] != "Prefetch":
                    self.assertIn(f"{agu['size_bytes']} 字节", body)
                if agu["action"].endswith("Pair"):
                    self.assertRegex(body, r"两个|相邻")
                if agu["action"].startswith("Load") and agu["size_bytes"] < 8:
                    extension = "符号扩展" if agu["signed_load"] else "零扩展"
                    self.assertIn(extension, body)
                if agu["address_kind"] == "PCRelative":
                    self.assertRegex(body, r"PC|TPC")
                if agu["address_kind"] == "Immediate":
                    scale = agu["offset_scale"]
                    if scale:
                        unit = 1 << scale
                        self.assertRegex(
                            body,
                            rf"乘以 {unit}|左移 {scale}|{unit} 字节单位|按 {unit} 缩放|单位为 {unit}",
                        )
                    else:
                        self.assertRegex(
                            body,
                            r"不缩放|不做缩放|不加比例|直接相加|字节位移|字节计数|以字节|任意字节|缩放因子(?:为)? 1|缩放为 1|缩放 1|按 1 缩放|位移是 [^。]+ 字节|1 字节对应一个编码单位",
                        )
                if agu["action"] != "Prefetch" and agu["size_bytes"] > 1:
                    self.assertRegex(
                        body, r"Fault_DataAlignment|地址必须是 [24816]+ 的倍数"
                    )
                if agu["update_mode"] == "PreIndex":
                    self.assertRegex(
                        body, r"前索引|前变址|前置|新基址|新指针|更新后的基址"
                    )
                if agu["update_mode"] == "PostIndex":
                    self.assertRegex(body, r"后索引|后变址|后置|原始基址|原 SrcR")

    def test_replacement_bodies_contain_no_historical_or_machine_notes(self):
        forbidden = (
            "历史",
            "旧文",
            "原文",
            "ASL",
            "处理程序",
            "目录记录",
            "机器记录",
        )
        for row in self.rows:
            if row.get("pto_scope"):
                continue
            source = self.sources.get(row.get("pto_source_form_id"), {})
            body = scalar_body(row, source, authored_for(row))
            if body is None:
                continue
            for term in forbidden:
                self.assertNotIn(term, body, row["id"])

    def test_linx_only_calling_bstarts_state_their_return_address_rules(self):
        fused = next(row for row in self.rows if row["mnemonic"] == "HL.BSTART CALL")
        body = scalar_body(fused, {}, authored_for(fused))
        self.assertIn("P + (SignExtend(simm25) << 1)", body)
        self.assertIn("(P + 4) + (ZeroExtend(uimm5) << 1)", body)
        for mnemonic in ("L.BSTART.FP", "L.BSTART.STD"):
            row = next(
                row
                for row in self.rows
                if row["mnemonic"] == mnemonic and " CALL" in row["asm"]
            )
            body = scalar_body(row, {}, authored_for(row))
            self.assertIn("不会改写 ra", body)
            self.assertIn("SETRET", body)

    def test_every_source_less_bbd_form_has_its_own_body(self):
        rows = [
            row
            for row in self.rows
            if not row.get("pto_scope")
            and row["uop_big_kind"] == "BBD"
            and not row.get("pto_source_form_id")
        ]
        self.assertEqual(len(rows), 23)
        for row in rows:
            body = scalar_body(row, {}, authored_for(row))
            self.assertTrue(body, row["id"])
            self.assertIn(row["asm"], body, row["id"])

    def test_every_multiform_non_tile_bstart_has_per_form_body(self):
        grouped = {}
        allowed = {
            "BSTART",
            "BSTART.FP",
            "BSTART.STD",
            "BSTART.SYS",
            "C.BSTART",
            "C.BSTART.FP",
            "C.BSTART.STD",
            "C.BSTART.SYS",
            "HL.BSTART.FP",
            "HL.BSTART.STD",
            "L.BSTART.FP",
            "L.BSTART.STD",
        }
        for row in self.rows:
            if not row.get("pto_scope") and row["mnemonic"] in allowed:
                grouped.setdefault(row["mnemonic"], []).append(row)
        for mnemonic, rows in grouped.items():
            if len(rows) == 1:
                continue
            bodies = []
            for row in rows:
                source = self.sources.get(row.get("pto_source_form_id"), {})
                body = scalar_body(row, source, authored_for(row))
                self.assertTrue(body, row["id"])
                self.assertIn(row["asm"], body, row["id"])
                bodies.append(body)
            self.assertEqual(len(set(bodies)), len(rows), mnemonic)


if __name__ == "__main__":
    unittest.main()
