#!/usr/bin/env python3
from __future__ import annotations
import unittest
from manual_tag import (
    SIGNED_TAG_COMMIT,
    revision_commit,
    tagged_bytes,
    tagged_json,
    verified_tag_commit,
)


class ManualTagTest(unittest.TestCase):
    def test_release_tag_resolves_to_reviewed_commit(self):
        self.assertEqual(verified_tag_commit(), SIGNED_TAG_COMMIT)
        self.assertTrue(revision_commit())

    def test_tagged_readers_return_release_objects(self):
        catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
        self.assertEqual(catalog["version"], "0.59.1")
        self.assertEqual(catalog["instruction_count"], 1306)
        self.assertFalse(any(row["mnemonic"].startswith("V.") for row in catalog["instructions"]))
        raw = tagged_bytes("isa/v0.59/pto-spec.lock.json")
        self.assertEqual(raw, tagged_bytes("isa/v0.59/pto-spec.lock.json"))
        self.assertIn(b'"release": "0.59.1"', raw)

    def test_missing_revision_source_never_falls_back_to_tag(self):
        with self.assertRaises(FileNotFoundError):
            tagged_bytes("docs/zh/isa/removed-from-working-revision.md")


if __name__ == "__main__":
    unittest.main()
