#!/usr/bin/env python3
"""Mutation regressions for the catalog-derived scalar PCR wiring gate."""

import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))
from check_scalar_pcr_contract import check_wiring, function_parts, pcr_forms  # noqa: E402


class ScalarPCRContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forms = pcr_forms(ROOT)
        cls.execution = (ROOT / "isa/sail/model/execute/execute.sail").read_text()
        cls.decoder = (ROOT / "isa/sail/model/decode/decode.sail").read_text()

    def check(self, execution, forms=None, decoder=None):
        return check_wiring(self.forms if forms is None else forms, execution,
                            self.decoder if decoder is None else decoder)

    def mutate_body(self, function, old, new):
        _, body = function_parts(self.execution, function)
        self.assertIn(old, body)
        return self.execution.replace(body, body.replace(old, new), 1)

    def test_current_golden_inventory_and_bindings(self):
        self.assertEqual(len(self.forms), 22)
        self.assertEqual(sum(form["length_bits"] == 32 for form in self.forms), 11)
        self.assertEqual({form["agu"]["offset_scale"] for form in self.forms}, {2})
        self.assertEqual(self.check(self.execution), [])

    def test_every_form_rejects_unscaled_displacement(self):
        for form in self.forms:
            with self.subTest(form=form["form_id"]):
                function = "exec_" + form["mnemonic"].lower().replace(".", "_")
                mutated = self.mutate_body(function, ", 2);", ", 0);")
                self.assertTrue(any(form["mnemonic"] in error and "scale" in error
                                    for error in self.check(mutated)))

    def test_scales_are_derived_from_catalog_not_access_size(self):
        forms = copy.deepcopy(self.forms)
        form = next(form for form in forms if form["mnemonic"] == "LD.PCR")
        form["agu"]["offset_scale"] = 3
        self.assertTrue(any("LD.PCR" in error and "scale" in error
                            for error in self.check(self.execution, forms=forms)))

    def test_wrong_pc_and_wrong_sign_extension_are_rejected(self):
        for helper, width in (("ea_pcr17", 17), ("hl_ea_pcr", 29)):
            for old, new in (("read_pc_or_tpc()", "0x0000_0000_0000_0000"),
                             (f"sext{width}_to64", "zero_extend")):
                with self.subTest(helper=helper, mutation=new):
                    mutated = self.mutate_body(helper, old, new)
                    self.assertTrue(any(helper in error for error in self.check(mutated)))

    def test_missing_form_is_rejected(self):
        mutated = self.execution.replace("function exec_hl_sd_pcr(", "function removed_hl_sd_pcr(")
        self.assertTrue(any("inventory mismatch" in error for error in self.check(mutated)))

    def test_memory_width_and_load_extension_are_checked(self):
        for old, new in (("read_mem8(ea)", "mem_load16_le(ea)"),
                         ("sext8_from8(b)", "zext8_from8(b)")):
            with self.subTest(mutation=new):
                mutated = self.mutate_body("exec_lb_pcr", old, new)
                self.assertTrue(any("LB.PCR" in error for error in self.check(mutated)))

    def test_corrupt_store_source_or_payload_is_rejected(self):
        for old, new in (("read_reg5(SrcD)[31..0]", "read_reg5(0b00001)[31..0]"),
                         ("mem_store32_le(ea, v)", "mem_store32_le(ea, sail_zeros(32))")):
            with self.subTest(mutation=new):
                mutated = self.mutate_body("exec_sw_pcr", old, new)
                self.assertTrue(any("SW.PCR: store" in error for error in self.check(mutated)))

    def test_corrupt_64_bit_load_publication_is_rejected(self):
        for replacement in ("()", "write_scalar_gpr_or_discard(RegDst, sail_zeros(64))",
                            "write_scalar_gpr_or_discard(0b00001, d)"):
            with self.subTest(mutation=replacement):
                mutated = self.mutate_body("exec_ld_pcr", "write_scalar_gpr_or_discard(RegDst, d)", replacement)
                self.assertTrue(any("LD.PCR: loaded" in error for error in self.check(mutated)))

    def test_wrong_decoded_source_is_rejected(self):
        decoder = self.decoder.replace("exec_sw_pcr(srcl, simm)", "exec_sw_pcr(0b00001, simm)")
        self.assertTrue(any("SW.PCR: decoded" in error
                            for error in self.check(self.execution, decoder=decoder)))

    def test_missing_queue_guard_is_rejected(self):
        mutated = self.mutate_body("exec_ld_pcr",
                                   "not_bool(scalar_gpr_or_discard_destination_supported(RegDst))",
                                   "false")
        self.assertTrue(any("LD.PCR: unsupported queue" in error for error in self.check(mutated)))


if __name__ == "__main__":
    unittest.main()
