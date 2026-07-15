#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_tests


class StructuredEvidenceParsingTests(unittest.TestCase):
    def test_test_events_preserve_test_specific_order(self) -> None:
        output = (
            b"  Test 0x0000140B: stack redirect PASS\r\n"
            b"  Test 0x0000140C: snapshot redirect PASS\r\n"
        )
        self.assertEqual(
            run_tests._parse_test_events(output),
            [
                {"seq": 0, "kind": "START", "test_id": "0x0000140b"},
                {"seq": 1, "kind": "PASS", "test_id": "0x0000140b"},
                {"seq": 2, "kind": "START", "test_id": "0x0000140c"},
                {"seq": 3, "kind": "PASS", "test_id": "0x0000140c"},
            ],
        )

    def test_failure_line_has_terminal_fail_event(self) -> None:
        output = b"  Test 0x00001321: vector sub oracle FAIL\r\n"
        self.assertEqual(
            run_tests._parse_test_events(output),
            [
                {"seq": 0, "kind": "START", "test_id": "0x00001321"},
                {"seq": 1, "kind": "FAIL", "test_id": "0x00001321"},
            ],
        )

    def test_any_fail_event_blocks_test_event_pass_marker(self) -> None:
        events = [
            {"seq": 0, "kind": "START", "test_id": "0x00001321"},
            {"seq": 1, "kind": "FAIL", "test_id": "0x00001321"},
            {"seq": 2, "kind": "START", "test_id": "0x00001322"},
            {"seq": 3, "kind": "PASS", "test_id": "0x00001322"},
        ]
        self.assertFalse(run_tests._test_events_are_clean_pass(events))
        self.assertTrue(
            run_tests._test_events_are_clean_pass(
                [
                    {"seq": 0, "kind": "START", "test_id": "0x0000140b"},
                    {"seq": 1, "kind": "PASS", "test_id": "0x0000140b"},
                ]
            )
        )

    def test_failure_record_and_timeout_after_fail_are_machine_readable(self) -> None:
        output = (
            b"  Test 0x00001321: FAIL\r\n"
            b"    Test ID:  0x00001321\r\n"
            b"    Expected: 0x0000000000000053\r\n"
            b"    Actual:   0x0000000000000011\r\n"
        )
        self.assertEqual(
            run_tests._parse_failure(output),
            {
                "test_id": "0x00001321",
                "expected": "0x0000000000000053",
                "actual": "0x0000000000000011",
            },
        )

    def test_qemu_trace_parser_extracts_executed_pcs(self) -> None:
        trace = """
IN: callret_tpl_fret_stk_slot_redirect
0x0000000000010016:  FRET.STK [ra ~ ra], sp!, 16
0x000000000001001a:  C.BSTART.STD RET
"""
        self.assertEqual(
            run_tests._parse_executed_pcs(trace),
            ["0x0000000000010016", "0x000000000001001a"],
        )


if __name__ == "__main__":
    unittest.main()
