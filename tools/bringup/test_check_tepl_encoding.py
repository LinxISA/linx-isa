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


if __name__ == "__main__":
    unittest.main()
