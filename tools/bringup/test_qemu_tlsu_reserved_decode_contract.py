#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_qemu_isa_coverage as coverage


EXPECTED = {
    "bstart_tload": (0x07FFFFFF, 0x00011181, 0),
    "bstart_tstore": (0x07FFFFFF, 0x00111181, 1),
    "bstart_tmov": (0x07FFFFFF, 0x00211181, 2),
    "bstart_tprefetch": (0x07FFFFFF, 0x00311181, 3),
    "bstart_mgather": (0x07FFFFFF, 0x00411181, 4),
    "bstart_mscatter": (0x07FFFFFF, 0x00511181, 5),
    "bstart_mgather_mask": (0x07FFFFFF, 0x00611181, 6),
    "bstart_mscatter_mask": (0x07FFFFFF, 0x00711181, 7),
    "bstart_mgather_cas": (0x07FFFFFF, 0x00811181, 8),
}
META_WITH_ID_RE = re.compile(
    r"\.op_id=(?P<op_id>\d+),.*?"
    r"\.insn_len=(?P<insn_len>\d+),\s*"
    r"\.mask=UINT64_C\((?P<mask>0x[0-9a-fA-F]+)\),\s*"
    r"\.match=UINT64_C\((?P<match>0x[0-9a-fA-F]+)\),.*?"
    r"\.mnemonic=\"(?P<mnemonic>[^\"]+)\""
)


class QemuTlsuReservedDecodeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.linx = cls.root / "emulator/qemu/target/linx"
        cls.decode_entries = coverage._parse_decode_entries(cls.linx / "insn32.decode", 32)
        meta_text = (cls.linx / "linx_opcode_meta_gen.h").read_text(encoding="utf-8")
        cls.meta_entries = [
            {
                "op_id": int(match.group("op_id")),
                "mnemonic": match.group("mnemonic"),
                "insn_len": int(match.group("insn_len")),
                "mask": int(match.group("mask"), 0),
                "match": int(match.group("match"), 0),
            }
            for match in META_WITH_ID_RE.finditer(meta_text)
        ]

    def test_current_qemu_exact_tlsu_subset_is_decoded_and_cataloged(self) -> None:
        decoded = {
            entry["mnemonic"]: (entry["mask"], entry["match"])
            for entry in self.decode_entries
            if entry["mnemonic"] in EXPECTED
        }
        for token, (mask, match, _) in EXPECTED.items():
            with self.subTest(token=token):
                self.assertEqual(decoded.get(token), (mask, match))

        meta = {
            entry["mnemonic"]: entry
            for entry in self.meta_entries
            if entry["mnemonic"] in EXPECTED
        }
        shared_op_ids = {meta[token]["op_id"] for token in EXPECTED}
        self.assertEqual(len(shared_op_ids), 1)
        for token, (mask, match, _) in EXPECTED.items():
            with self.subTest(token=token):
                self.assertEqual(meta[token]["insn_len"], 32)
                self.assertEqual(meta[token]["mask"], mask)
                self.assertEqual(meta[token]["match"], match)

    def test_current_qemu_subset_and_architecturally_reserved_words_partition_the_family(self) -> None:
        for token, (_, _, function) in EXPECTED.items():
            word = (1 << 27) | (function << 20) | 0x00011181
            matches = [
                entry["mnemonic"]
                for entry in self.decode_entries
                if word & entry["mask"] == entry["match"]
            ]
            self.assertEqual(matches, [token])

        for function, word in ((15, 0x08F11181), (31, 0x09F11181)):
            with self.subTest(function=function):
                decode_matches = [
                    entry["mnemonic"]
                    for entry in self.decode_entries
                    if word & entry["mask"] == entry["match"]
                ]
                meta_matches = [
                    entry["mnemonic"]
                    for entry in self.meta_entries
                    if entry["insn_len"] == 32
                    and word & entry["mask"] == entry["match"]
                ]
                self.assertEqual(decode_matches, [])
                self.assertEqual(meta_matches, [])

    def test_translators_freeze_the_nine_legal_function_values(self) -> None:
        translate = (self.linx / "translate.c").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"\btrans_bstart_(?:tma|tlsu)\s*\(", translate))
        for token, (_, _, function) in EXPECTED.items():
            with self.subTest(token=token):
                found = re.search(rf"static bool trans_{token}\([^)]*\)\s*\{{", translate)
                self.assertIsNotNone(found)
                body = coverage._extract_c_block(translate, found.end() - 1)
                self.assertIsNotNone(body)
                self.assertIn(
                    f"trans_bstart_tile_func_common(ctx, a->dtype, 2, {function})",
                    body,
                )

    def test_reserved_decode_miss_routes_to_illegal_instruction(self) -> None:
        translate = (self.linx / "translate.c").read_text(encoding="utf-8")
        decode32 = re.search(
            r"decoded\s*=\s*decode_insn32\(ctx,\s*insn_val\);\s*"
            r"if\s*\(!decoded\)\s*\{(?P<body>.*?)\n\s*\}",
            translate,
            re.DOTALL,
        )
        self.assertIsNotNone(decode32)
        self.assertIn("linx_illegal(ctx)", decode32.group("body"))

        illegal = re.search(r"static bool linx_illegal\([^)]*\)\s*\{", translate)
        self.assertIsNotNone(illegal)
        body = coverage._extract_c_block(translate, illegal.end() - 1)
        self.assertIsNotNone(body)
        self.assertIn("gen_helper_raise_exception", body)
        self.assertIn("LINX_EXCP_ILLEGAL_INST", body)

if __name__ == "__main__":
    unittest.main()
