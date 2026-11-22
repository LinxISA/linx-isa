#!/usr/bin/env python3
from __future__ import annotations
import unittest
from manual_tag import REVIEWED_COMMIT, tagged_bytes, tagged_json, verified_tag_commit


class ManualTagTest(unittest.TestCase):
    def test_release_tag_resolves_to_reviewed_commit(self):
        self.assertEqual(verified_tag_commit(), REVIEWED_COMMIT)

    def test_tagged_readers_return_release_objects(self):
        catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
        self.assertEqual(catalog["version"], "0.59.1")
        self.assertEqual(catalog["instruction_count"], 1499)
        raw = tagged_bytes("isa/v0.59/pto-spec.lock.json")
        self.assertEqual(raw, tagged_bytes("isa/v0.59/pto-spec.lock.json"))
        self.assertIn(b'"release": "0.59.1"', raw)


if __name__ == "__main__":
    unittest.main()
