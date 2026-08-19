#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_tests
import run_elf_identity_contract as elf_identity


class StructuredEvidenceParsingTests(unittest.TestCase):
    def test_v058_runner_does_not_publish_retired_pto_kernel_suites(self) -> None:
        retired = {
            "tile", "pto_parity", "deepseek_tilekernels",
            "v057_vector", "v057_vector_ops", "v057_vector_body_fault",
        }
        self.assertTrue(retired.isdisjoint(run_tests.SUITES), run_tests.SUITES)
        self.assertTrue(retired.isdisjoint(run_tests.EXPERIMENTAL_SUITES))

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
            "run_callret_tests();",
            "run_freestanding_runtime_tests();",
        ):
            with self.subTest(invocation=invocation):
                self.assertLess(main_source.index(invocation), system_index)

    def test_legacy_system_matrix_disables_first_use_explicitly(self) -> None:
        system_source = (run_tests.SCRIPT_DIR / "tests" / "11_system.c").read_text(
            encoding="utf-8"
        )
        self.assertIn("SSR_ECONFIG_ACR1 = 0x1F07", system_source)
        self.assertIn(
            "hl_ssrset_uimm24(SSR_ECONFIG_ACR1, UINT64_C(0x8));",
            system_source,
        )

    def test_active_catalog_is_the_exact_v0581_catalog(self) -> None:
        self.assertEqual(run_tests.LLVM_AVS_SPEC, run_tests.REPO_ROOT / "isa/v0.58/linxisa-v0.58.json")
        catalog = json.loads(run_tests.LLVM_AVS_SPEC.read_text())
        self.assertEqual(catalog["version"], "0.58.1")
        self.assertEqual(catalog["instruction_count"], 765)

    def test_v0571_executable_evidence_is_explicitly_archived(self) -> None:
        manifest = json.loads(
            (run_tests.SCRIPT_DIR / "qemu_executable_coverage_manifest.json").read_text()
        )
        self.assertEqual(manifest["release"], "0.57.1")
        self.assertFalse(manifest["active_release"])
        self.assertEqual(manifest["superseded_by"], "0.58.1")

    def test_elf_identity_fixture_matrix_is_exact(self) -> None:
        self.assertEqual(len(elf_identity.IDENTITY), 165)
        self.assertTrue(elf_identity._note(elf_identity.IDENTITY).startswith(
            b"\x04\x00\x00\x00\xa5\x00\x00\x00\x01\x00\x00\x00PTO\0"
        ))
        self.assertNotEqual(elf_identity.IDENTITY, elf_identity.OLD_IDENTITY)

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

    def test_target_pc_watch_parser_accepts_only_requested_runtime_packets(self) -> None:
        stderr = (
            b"IN: translated-only\n"
            b"0x0000000000010016: V.ADD\n"
            b"linx_pc_watch: pc=0x10016 hit=1 printed=1 count=44 sp=0x0\n"
            b"linx_pc_watch: pc=0x10018 hit=1 printed=1 count=45 sp=0x0\n"
        )
        self.assertEqual(
            run_tests._parse_target_pc_watch_packets(stderr, [0x10016]),
            [
                {
                    "pc": "0x0000000000010016",
                    "hit": 1,
                    "count": 44,
                    "evidence_kind": "qemu_target_pc_watch_v1",
                }
            ],
        )

    def test_target_pc_watch_parser_rejects_malformed_or_unprinted_hits(self) -> None:
        stderr = (
            b"prefix linx_pc_watch: pc=0x10016 hit=1 printed=1 count=44\n"
            b"linx_pc_watch: pc=0x10016 hit=0 printed=1 count=44\n"
            b"linx_pc_watch: pc=0x10016 hit=1 printed=0 count=44\n"
        )
        self.assertEqual(
            run_tests._parse_target_pc_watch_packets(stderr, [0x10016]), []
        )

    def test_target_pc_watch_env_is_bounded_and_reproducible(self) -> None:
        self.assertEqual(
            run_tests._target_pc_watch_env([0x10016, 0x1001A]),
            {
                "LINX_DEBUG_PC_WATCH": "0x10016,0x1001a",
                "LINX_DEBUG_PC_WATCH_HIT_LIMIT": "1",
                "LINX_DEBUG_PC_WATCH_PRINT": "1",
            },
        )
        self.assertEqual(run_tests._parse_evidence_pcs(["0x10", "16"]), [16])
        with self.assertRaises(SystemExit):
            run_tests._parse_evidence_pcs([str(value) for value in range(17)])

        inherited = {
            "PATH": "/bin",
            "LINX_DEBUG_PC_WATCH": "0xdead",
            "LINX_DEBUG_PC_WATCH_COUNT_LO": "999",
            "LINX_DEBUG_PC_WATCH_RING": "1",
        }
        recorded = run_tests._configure_target_pc_watch_env(inherited, [0x10016])
        self.assertEqual(
            inherited,
            {
                "PATH": "/bin",
                "LINX_DEBUG_PC_WATCH": "0x10016",
                "LINX_DEBUG_PC_WATCH_HIT_LIMIT": "1",
                "LINX_DEBUG_PC_WATCH_PRINT": "1",
            },
        )
        self.assertEqual(recorded, {key: inherited[key] for key in recorded})


if __name__ == "__main__":
    unittest.main()
