#!/usr/bin/env python3

from html import unescape
import json
from pathlib import Path
import re
import tempfile
import unittest

from tools.isa.manual_golden_registers import (
    register_evidence,
    register_review,
    register_routes,
    register_sections,
    validate_asl_evidence,
)


ROOT = Path(__file__).resolve().parents[2]


class GoldenRegisterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(
            (ROOT / "isa/v0.59/state/pto_system_registers.json").read_text()
        )
        cls.html, cls.records = register_sections(cls.document)

    def test_every_current_register_has_one_anchor_and_behavior_owner(self):
        self.assertEqual(len(self.records), 100)
        self.assertEqual(
            len(re.findall(r'class="system-register-detail"', self.html)), 100
        )
        self.assertEqual(len(re.findall(r'data-register-detail-key="', self.html)), 100)
        self.assertNotIn('data-register-key="', self.html)
        self.assertEqual(set(register_routes(self.document)), set(self.records))
        self.assertEqual(
            {record["behavior_status"] for record in self.records.values()},
            {
                behavior["behavior_status"]
                for behavior in self.document["behavior_classes"]
            },
        )

    def test_current_fields_and_formulas_are_visible(self):
        plain = unescape(re.sub(r"<[^>]+>", " ", self.html))
        for literal in (
            "CORE_STATE[3:0]",
            "36:32",
            "39:37",
            "(ACR << 12) | 0xF02",
            "TRAPNO_ACRn",
            "RX epoch",
            "claim sequence",
            "MSGBRXSTATE",
            "SSRSWAP",
        ):
            self.assertIn(literal, plain)

    def test_continuity_review_covers_all_old_ssr_sources(self):
        review = register_review(self.document)
        actual = {record["source"] for record in review}
        expected = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "docs/zh/isa/register/ssr").glob("*.md")
        }
        self.assertEqual(len(review), 41)
        self.assertEqual(actual, expected)
        self.assertTrue(all(len(record["source_sha256"]) == 64 for record in review))
        by_stem = {Path(record["source"]).stem: record for record in review}
        self.assertEqual(by_stem["CSTATE"]["current_registers"], ["CORE_STATE"])
        self.assertEqual(by_stem["CW"]["current_registers"], [])
        self.assertEqual(by_stem["LCFR"]["disposition"], "same-address-new-contract")
        self.assertEqual(by_stem["MMCONFIG"]["current_registers"], ["TTBR1_ACR1"])
        self.assertIn("MSGBACK", by_stem["MSGB"]["current_registers"])
        self.assertEqual(len(by_stem["per-acr"]["current_registers"]), 58)
        self.assertEqual(len(by_stem["ssrintro"]["current_registers"]), 100)

    def test_removed_field_names_do_not_enter_reader_sections(self):
        for stale in ("EBS_SZ", "canary", "GroupNum", "LaneNum", "FUTO", "EBSTATEP"):
            self.assertNotIn(stale, self.html)
        for current in ("CORE_FEATURE", "CORE_FEATURE_ENABLE", "THREAD_ID"):
            self.assertIn(current, self.html)

    def test_access_and_reset_values_come_from_current_behavior_classes(self):
        version = re.search(r'id="ssr-version"[\s\S]*?</section>', self.html).group(0)
        core_id = re.search(r'id="ssr-core-id"[\s\S]*?</section>', self.html).group(0)
        thread_ptr = re.search(
            r'id="ssr-thread-ptr"[\s\S]*?</section>', self.html
        ).group(0)
        self.assertIn("<code>RO</code>", version)
        self.assertIn("复位值为 1", version)
        self.assertIn("<code>RO</code>", core_id)
        self.assertIn("复位值为 0", core_id)
        self.assertIn("<code>RW</code>", thread_ptr)
        self.assertIn("复位值为 0", thread_ptr)

    def test_evidence_ledger_is_complete_and_reproducible(self):
        evidence = register_evidence(self.document)
        self.assertEqual(evidence["register_count"], 100)
        self.assertNotIn("continuity_review", evidence)
        self.assertEqual(set(evidence["registers"]), set(self.records))

    def test_asl_evidence_fails_closed_on_an_unpinned_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            errors = validate_asl_evidence(Path(directory))
        self.assertTrue(any("checkout unavailable" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
