#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_tests


class StructuredEvidenceParsingTests(unittest.TestCase):
    def test_every_declared_suite_source_exists(self) -> None:
        missing = {
            name: meta["src"]
            for name, meta in run_tests.SUITES.items()
            if not (run_tests.SCRIPT_DIR / meta["src"]).is_file()
        }
        self.assertEqual(missing, {})

    def test_terminal_system_suite_is_invoked_last(self) -> None:
        main_source = (run_tests.SCRIPT_DIR / "tests" / "main.c").read_text(
            encoding="utf-8"
        )
        system_index = main_source.index("run_system_tests();")
        for invocation in (
            "run_v03_vector_tile_tests();",
            "run_v03_vector_ops_matrix_tests();",
            "run_callret_tests();",
            "run_freestanding_runtime_tests();",
        ):
            with self.subTest(invocation=invocation):
                self.assertLess(main_source.index(invocation), system_index)

    def test_evidence_paths_remain_relative_in_repo_and_absolute_outside(self) -> None:
        in_repo = Path(__file__).resolve()
        self.assertEqual(
            run_tests._repo_relative(in_repo),
            str(in_repo.relative_to(run_tests.REPO_ROOT.resolve())),
        )

        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "artifact.elf"
            self.assertEqual(run_tests._repo_relative(outside), str(outside.resolve()))

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

    def test_runtime_verdict_accepts_only_a_terminal_oracle(self) -> None:
        quiet = run_tests._runtime_verdict(b"LINX TESTS PASS\r\n", 0)
        self.assertEqual(quiet["status"], "PASS")
        self.assertEqual(quiet["oracle_verdict"], "PASS")

        incomplete = run_tests._runtime_verdict(b"Test 0x10: PASS\r\n", 0)
        self.assertEqual(incomplete["status"], "FAIL")
        self.assertEqual(incomplete["reason"], "missing_terminal_oracle")

        declared_terminal = run_tests._runtime_verdict(
            b"Test 0x110d: PASS\r\n",
            0,
            terminal_test_ids=[0x110D],
        )
        self.assertEqual(declared_terminal["status"], "PASS")
        self.assertEqual(
            declared_terminal["pass_marker"],
            {"kind": "terminal_test_id", "value": "0x0000110d"},
        )

    def test_declared_terminal_must_be_the_last_pass_event(self) -> None:
        verdict = run_tests._runtime_verdict(
            b"Test 0x110d: PASS\r\nTest 0x1110: PASS\r\n",
            0,
            terminal_test_ids=[0x110D],
        )
        self.assertEqual(verdict["status"], "FAIL")
        self.assertEqual(verdict["reason"], "missing_terminal_oracle")

    def test_explicit_failure_dominates_finisher_and_later_success_marker(self) -> None:
        output = (
            b"Test 0x10: FAIL\r\n"
            b"Test ID: 0x10\r\nExpected: 0x1\r\nActual: 0x2\r\n"
            b"TEST SUITE COMPLETE\r\n"
        )
        for returncode in (0, run_tests.FINISHER_PASS_LOW8):
            with self.subTest(returncode=returncode):
                verdict = run_tests._runtime_verdict(output, returncode)
                self.assertEqual(verdict["status"], "FAIL")
                self.assertEqual(verdict["oracle_verdict"], "FAIL")
                self.assertEqual(verdict["reason"], "guest_failure")
                self.assertIsNone(verdict["pass_marker"])

    def test_required_ids_are_part_of_the_shared_verdict(self) -> None:
        verdict = run_tests._runtime_verdict(
            b"Test 0x10: PASS\r\nLINX TESTS PASS\r\n",
            0,
            required_test_ids=[0x10, 0x11],
        )
        self.assertEqual(verdict["status"], "FAIL")
        self.assertEqual(verdict["oracle_verdict"], "FAIL")
        self.assertEqual(verdict["reason"], "missing_required_test_ids")
        self.assertEqual(verdict["missing_required_test_ids"], ["0x00000011"])

    def test_selected_suite_completion_ids_are_part_of_the_shared_verdict(self) -> None:
        verdict = run_tests._runtime_verdict(
            b"Test 0x110d: PASS\r\n",
            0,
            terminal_test_ids=[0x110D],
            suite_completion_test_ids=[0x1412, 0x110D],
        )
        self.assertEqual(verdict["status"], "FAIL")
        self.assertEqual(verdict["oracle_verdict"], "FAIL")
        self.assertEqual(verdict["reason"], "missing_suite_completion_test_ids")
        self.assertEqual(
            verdict["missing_suite_completion_test_ids"],
            ["0x00001412"],
        )

    def test_timeout_and_stall_do_not_publish_pass(self) -> None:
        for kwargs, expected in (({"timed_out": True}, "TIMEOUT"), ({"stalled": True}, "STALLED")):
            with self.subTest(expected=expected):
                verdict = run_tests._runtime_verdict(
                    b"LINX TESTS PASS\r\n", 0, **kwargs
                )
                self.assertEqual(verdict["status"], expected)
                self.assertIsNone(verdict["pass_marker"])

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
        verdict = run_tests._runtime_verdict(output, -9, timed_out=True)
        self.assertEqual(verdict["status"], "FAIL")
        self.assertEqual(verdict["oracle_verdict"], "FAIL")
        self.assertEqual(verdict["reason"], "guest_failure")
        self.assertTrue(verdict["timed_out"])

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
