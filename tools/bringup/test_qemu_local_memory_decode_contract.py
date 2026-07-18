#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_qemu_isa_coverage as coverage


TARGETS = {
    "V.LB": "v_lb",
    "V.LBU": "v_lbu",
    "V.LH": "v_lh",
    "V.LHU": "v_lhu",
    "V.SB": "v_sb",
    "V.SH": "v_sh",
}


class QemuLocalMemoryDecodeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.qemu_linx = cls.root / "emulator/qemu/target/linx"
        cls.spec = json.loads(
            (cls.root / "isa/v0.57/linxisa-v0.57.json").read_text(
                encoding="utf-8"
            )
        )

    @staticmethod
    def _combined_encoding(insn: dict[str, object]) -> tuple[int, int]:
        encoding = insn["encoding"]
        assert isinstance(encoding, dict)
        parts = encoding["parts"]
        assert isinstance(parts, list)
        mask = 0
        match = 0
        offset = 0
        for part in sorted(parts, key=lambda item: int(item["index"])):
            width = int(part["width_bits"])
            mask |= int(part["mask"], 0) << offset
            match |= int(part["match"], 0) << offset
            offset += width
        return mask, match

    @staticmethod
    def _function_body(text: str, signature: str) -> str:
        found = re.search(signature + r"\s*\{", text)
        if found is None:
            raise AssertionError(f"missing function matching {signature}")
        body = coverage._extract_c_block(text, found.end() - 1)
        if body is None:
            raise AssertionError(f"unbalanced function matching {signature}")
        return body

    def _target_spec_forms(self) -> dict[str, dict[str, object]]:
        result = {
            insn["mnemonic"]: insn
            for insn in self.spec["instructions"]
            if insn["mnemonic"] in TARGETS
        }
        self.assertEqual(set(result), set(TARGETS))
        return result

    def test_each_form_has_exact_decode_catalog_and_qemu_meta(self) -> None:
        decode_entries = {
            entry["mnemonic"]: entry
            for entry in coverage._parse_decode_entries(
                self.qemu_linx / "insn64.decode", 64
            )
        }
        meta_text = (self.qemu_linx / "linx_opcode_meta_gen.h").read_text(
            encoding="utf-8"
        )
        meta_entries = {
            match.group("mnemonic"): {
                "insn_len": int(match.group("insn_len")),
                "mask": int(match.group("mask"), 0),
                "match": int(match.group("match"), 0),
            }
            for match in coverage.QEMU_META_RE.finditer(meta_text)
        }
        catalog = json.loads(
            (self.root / "rtl/LinxCore/src/common/opcode_catalog.yaml").read_text(
                encoding="utf-8"
            )
        )
        catalog_entries = {
            record["mnemonic"]: record for record in catalog["records"]
        }

        for mnemonic, insn in self._target_spec_forms().items():
            token = TARGETS[mnemonic]
            expected_mask, expected_match = self._combined_encoding(insn)
            with self.subTest(mnemonic=mnemonic):
                self.assertNotEqual(expected_mask & (1 << 13), 0)
                self.assertEqual(expected_match & (1 << 13), 0)
                self.assertEqual(
                    decode_entries.get(token),
                    {
                        "mnemonic": token,
                        "insn_len": 64,
                        "mask": expected_mask,
                        "match": expected_match,
                    },
                )
                self.assertEqual(
                    meta_entries.get(token),
                    {
                        "insn_len": 64,
                        "mask": expected_mask,
                        "match": expected_match,
                    },
                )
                catalog_entry = catalog_entries.get(token)
                self.assertIsNotNone(catalog_entry)
                self.assertEqual(int(catalog_entry["mask"], 0), expected_mask)
                self.assertEqual(int(catalog_entry["match"], 0), expected_match)

    def test_translators_pass_runtime_l_to_existing_local_helpers(self) -> None:
        translate = (self.qemu_linx / "translate.c").read_text(encoding="utf-8")
        helper = (self.qemu_linx / "helper.c").read_text(encoding="utf-8")

        for token in TARGETS.values():
            with self.subTest(token=token):
                translator_body = self._function_body(
                    translate,
                    rf"static bool trans_{token}\([^)]*\)",
                )
                helper_call = rf"\bgen_helper_linx_{token}_local\s*\(.*?\);"
                call = re.search(helper_call, translator_body, re.DOTALL)
                self.assertIsNotNone(call)
                self.assertIn(
                    "tcg_constant_i32((int32_t)a->l)", call.group(0)
                )

                helper_body = self._function_body(
                    helper,
                    rf"void HELPER\(linx_{token}_local\)\([^)]*\)",
                )
                self.assertRegex(helper_body, r"if\s*\(local\s*==\s*0\)")
                self.assertRegex(
                    helper_body,
                    r"helper_raise_exception\(env,\s*LINX_EXCP_ILLEGAL_INST\)",
                )

    def test_new_l1_forms_are_not_claimed_as_executed(self) -> None:
        target_ids = {
            insn["id"] for insn in self._target_spec_forms().values()
        }
        executable = json.loads(
            (
                self.root
                / "docs/bringup/gates/qemu_executable_coverage_latest.json"
            ).read_text(encoding="utf-8")
        )
        claimed_ids = {item["form_id"] for item in executable["admitted"]}
        self.assertTrue(target_ids.isdisjoint(claimed_ids))


if __name__ == "__main__":
    unittest.main()
