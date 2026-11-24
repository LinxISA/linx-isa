#!/usr/bin/env python3

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

from build_linxisa_v0592_catalog import build
from build_linxisa_v0592_release_prep import build as build_release


class LinxISAV0592CatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads((ROOT / "isa/v0.59/linxisa-v0.59.json").read_text())
        cls.new = build()

    def test_exact_status_inventory(self):
        states = {"obsolete": [], "retained": [], "reserved-unimplemented": []}
        for row in self.new["instructions"]:
            status = row.get("architecture_status")
            if status:
                states[status["state"]].append(row)
        self.assertEqual(
            {key: len(value) for key, value in states.items()},
            {"obsolete": 193, "retained": 19, "reserved-unimplemented": 4},
        )
        self.assertEqual(
            sum(row["mnemonic"].startswith("V.") for row in states["obsolete"]), 184
        )
        self.assertEqual(
            {row["mnemonic"] for row in states["reserved-unimplemented"]},
            {"DMA.FREE.L", "DMA.FREE.S", "MCOPY.DL", "MCOPY.DS"},
        )

    def test_only_version_release_status_and_linx_status_change(self):
        old = {row["id"]: row for row in self.old["instructions"]}
        new = {row["id"]: row for row in self.new["instructions"]}
        self.assertEqual(old.keys(), new.keys())
        for identity in old:
            actual = dict(new[identity])
            actual.pop("architecture_status", None)
            self.assertEqual(actual, old[identity], identity)
        other = dict(self.new)
        other["version"] = self.old["version"]
        other["release_status"] = self.old["release_status"]
        other["instructions"] = [
            {key: value for key, value in row.items() if key != "architecture_status"}
            for row in other["instructions"]
        ]
        self.assertEqual(other, self.old)

    def test_release_metadata_binds_catalog_lock_and_decision(self):
        meta, manifest = build_release()
        self.assertEqual(meta["version"], "0.59.2")
        self.assertEqual(manifest["version"], "0.59.2")
        self.assertEqual(manifest["identity"]["release"], "0.59.1")
        self.assertEqual(manifest["cardinality"]["linx_only_obsolete_forms"], 193)
        self.assertTrue(manifest["policy"]["obsolete_encodings_remain_reserved"])
        self.assertTrue(manifest["qualification"]["release_qualified"])
        self.assertTrue(manifest["qualification"]["sail_package_qualified"])
        self.assertFalse(manifest["qualification"]["linux_qualified"])
        self.assertEqual(
            manifest["authoritative_sources"]["tile_operations"]["count"], 119
        )
        self.assertEqual(
            manifest["authoritative_sources"]["system_registers"]["count"], 100
        )
        self.assertEqual(
            manifest["release_activation"]["sail_exporter"],
            "tools/isa/export_linxisa_v0592_sail.py",
        )


if __name__ == "__main__":
    unittest.main()
