#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_tepl_encoding as checker


class TeplCarrierEncodingTests(unittest.TestCase):
    def test_active_consumer_is_linx_tileop_api_not_retired_pto_kernel(self) -> None:
        source = Path(checker.__file__).read_text(encoding="utf-8")
        self.assertIn('default="tools/Linx-TileOP-API"', source)
        self.assertNotIn('default="workloads/pto_kernels"', source)
        self.assertNotIn('PTO-Kernel(include/common/pto_tileop.hpp)', source)

    def test_uninitialized_gitlink_is_not_treated_as_a_materialized_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gitlink"
            path.mkdir()
            self.assertFalse(checker._is_materialized_repo(path))
            (path / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")
            self.assertTrue(checker._is_materialized_repo(path))

    def test_tileop_alias_parser_preserves_engine_classification(self) -> None:
        self.assertEqual(
            checker._parse_tileop_engine_aliases(
                '"BSTART.VEC TADD, %c1\\n"\n"BSTART.SFU TEXP, %c2\\n"'
            ),
            {"TADD": "VEC", "TEXP": "SFU"},
        )
        with self.assertRaises(RuntimeError):
            checker._parse_tileop_engine_aliases(
                '"BSTART.VEC TADD, %c1\\n"\n"BSTART.SFU TADD, %c2\\n"'
            )

    def test_v058_logical_selectors_are_loaded_from_the_carrier_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "engine_ops.json"
            path.write_text(
                json.dumps(
                    {
                        "tepl": {
                            "ops": [
                                {
                                    "name": "TADD",
                                    "engine": "VEC",
                                    "mode": 0,
                                    "function": 0,
                                    "logical_selector": 0,
                                },
                                {
                                    "name": "TEXP",
                                    "engine": "SFU",
                                    "mode": 2,
                                    "function": 0,
                                    "logical_selector": 64,
                                },
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(checker._load_engine_ops_map(path), {"TADD": 0, "TEXP": 64})

    def test_current_qemu_selector_switch_is_parsed(self) -> None:
        text = """
static uint32_t linx_tile_operation_impl_selector(uint32_t selector)
{
    switch (selector) {
    case 0x000u: /* TADD */ return 0x000u;
    case 0x01cu: /* TFMA */ return 0x10cu;
    default: return UINT32_MAX;
    }
}
"""
        self.assertEqual(
            checker._parse_qemu_selector_switch(text),
            {"TADD": 0x000, "TFMA": 0x01C},
        )

    def test_current_llvm_engine_table_is_parsed(self) -> None:
        text = """
#define LINXISA_V058_TILE_OPERATION_LIST(X) \\
  X(TADD, 0x000u, VEC) \\
  X(TEXP, 0x012u, SFU) \\
  X(TFMA, 0x01cu, VEC)
"""
        self.assertEqual(
            checker._parse_llvm_v058_engine_table(text),
            {"TADD": 0x000, "TEXP": 0x012, "TFMA": 0x01C},
        )


if __name__ == "__main__":
    unittest.main()
