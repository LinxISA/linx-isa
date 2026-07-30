#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import run_frame_template_semantics as runner


class FrameTemplateSemanticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _artifact(self, name: str, data: bytes) -> dict:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {"path": str(path), "sha256": runner._sha256(path)}

    def _fentry_line(self, case: runner.Case, *, old_sp: int = 0x7FEFFF0) -> str:
        decoded = runner._case_fentry_decode(case)
        stacksize = decoded["stacksize"]
        new_sp = (old_sp - stacksize) & runner.U64_MASK
        return (
            "LINX_FENTRY_TRACE count=1 pc=0x10000 next_pc=0x10004 "
            f"old_sp=0x{old_sp:x} new_sp=0x{new_sp:x} stacksize={stacksize} "
            f"callframe=0 begin={decoded['begin']} end={decoded['end']} "
            f"save_count={decoded['save_count']} incoming_ra=0x7fffff0"
        )

    def _slot_lines(
        self,
        case: runner.Case,
        *,
        old_sp: int = 0x7FEFFF0,
        pc: int = 0x10000,
    ) -> str:
        decoded = runner._case_fentry_decode(case)
        values = [0x4400000000000000 + index for index in range(decoded["save_count"])]
        if case.case_id == "valid_singleton_ra_terminal":
            values[0] = 0x7FFFFF0
        slots = list(zip(decoded["registers"], values, strict=True))
        return "\n".join(
            (
                f"LINX_FENTRY_SLOT count=1 pc=0x{pc:x} reg={reg} "
                f"addr=0x{old_sp - 8 * (index + 1):x} value=0x{value:x} "
                f"mmu=0 mmu_readback=0x{value:x} host=(nil) host_readback=0x0 "
                f"debug_read_ok=1 debug_readback=0x{value:x}"
            )
            for index, (reg, value) in enumerate(slots)
        )

    def _run_text(self, case: runner.Case) -> str:
        if case.case_id == runner.FRET_RA_CASE_ID:
            return "\n".join(
                [
                    runner.FRET_RA_PRE_MARKER,
                    runner.FRET_RA_RESTORED_MARKER,
                    runner._terminal_token(case),
                    runner._terminal_trace_line(),
                ]
            ) + "\n"
        if case.case_id == runner.FRET_STK_CASE_ID:
            return self._fret_stk_text(case, runner.FRET_STK_DYNAMIC_CONFIGS[0])
        return "\n".join(
            [
                self._fentry_line(case),
                self._slot_lines(case),
                runner._terminal_token(case),
                runner._terminal_trace_line(),
            ]
        ) + "\n"

    def _fret_stk_text(
        self,
        case: runner.Case,
        config: dict,
        *,
        old_sp: int = 0x7FEFFE0,
        pc: int = 0x10100,
        slot0_value: int = 0x10200,
    ) -> str:
        new_sp = old_sp + 16
        expected = config["expected"]
        trace = (
            "LINX_FRET_STK_TRACE "
            f"count=7 pc=0x{pc:x} next_pc=0x{pc + 4:x} "
            f"old_sp=0x{old_sp:x} new_sp=0x{new_sp:x} "
            "stacksize=16 callframe=0 restore_base=0 begin=ra end=ra restore_count=1 "
            f"restore_host_loads={expected['restore_host_loads']} "
            f"restore_fallback_loads={expected['restore_fallback_loads']} "
            f"host_verify_loads={expected['host_verify_loads']} "
            "executed_restore_loads=1 "
            f"physical_restore_reads={expected['physical_restore_reads']} "
            f"slot0_addr=0x{new_sp - 8:x} slot0_value=0x{slot0_value:x} "
            f"slot0_loads=1 slot0_physical_reads={expected['slot0_physical_reads']} "
            f"slot0_physical_reads_proven={expected['slot0_physical_reads_proven']} "
            f"retained_target=0x{slot0_value:x} incoming_ra=0xdead restored_ra=0x{slot0_value:x} "
            "envpc=0x0 bpc=0x0 tpc=0x0 cstate=0x0 brtype=0 tgt=0x0"
        )
        slot = (
            "LINX_FRET_STK_SLOT "
            f"count=7 pc=0x{pc:x} reg=ra addr=0x{new_sp - 8:x} value=0x{slot0_value:x}"
        )
        publish = (
            "LINX_FRET_STK_PUBLISH "
            f"count=7 pc=0x{pc:x} slot0_addr=0x{new_sp - 8:x} slot0_value=0x{slot0_value:x} "
            "slot0_loads=1 additional_slot0_loads=0 "
            f"slot0_physical_reads={expected['slot0_physical_reads']} "
            f"slot0_physical_reads_proven={expected['slot0_physical_reads_proven']} "
            "additional_slot0_physical_reads=0 executed_restore_loads=1 "
            f"host_verify_loads={expected['host_verify_loads']} "
            f"retained_target=0x{slot0_value:x} committed_r10=0x{slot0_value:x} "
            f"published_target=0x{slot0_value:x}"
        )
        return "\n".join(
            [
                trace,
                slot,
                publish,
                runner.FRET_STK_RETAINED_MARKER,
                runner._terminal_token(case),
                runner._terminal_trace_line(),
            ]
        ) + "\n"

    def base_report(self) -> dict:
        observations = []
        for case in runner.MANIFEST:
            if case.kind != "dynamic":
                continue
            kernel = self._artifact(f"{case.case_id}/kernel.o", f"kernel-{case.case_id}".encode())
            compile_log = self._artifact(
                f"{case.case_id}/compile.log", f"compile-{case.case_id}".encode()
            )
            runs = []
            run_configs = (
                [
                    {
                        "label": "unset" if env_value is None else env_value,
                        "env_value": env_value,
                        "fret_stk_config": None,
                    }
                    for env_value in runner.EXPECTED_DYNAMIC_ENVS
                ]
                if case.case_id != runner.FRET_STK_CASE_ID
                else [
                    {
                        "label": config["label"],
                        "env_value": None,
                        "fret_stk_config": config,
                    }
                    for config in runner.FRET_STK_DYNAMIC_CONFIGS
                ]
            )
            for run_config in run_configs:
                label = run_config["label"]
                env_value = run_config["env_value"]
                token = runner._terminal_token(case)
                output = (
                    self._fret_stk_text(case, run_config["fret_stk_config"])
                    if run_config["fret_stk_config"]
                    else self._run_text(case)
                )
                qemu_log = self._artifact(
                    f"{case.case_id}/qemu-{label}.log",
                    output.encode(),
                )
                terminal_trace = self._artifact(
                    f"{case.case_id}/terminal-{label}.log",
                    output.encode(),
                )
                runs.append(
                    {
                        "env": (
                            {"LINX_CALLFRAME_SIZE": env_value}
                            if not run_config["fret_stk_config"]
                            else copy.deepcopy(run_config["fret_stk_config"]["env"])
                        ),
                        **(
                            {"configuration": run_config["fret_stk_config"]["label"]}
                            if run_config["fret_stk_config"]
                            else {}
                        ),
                        "status": (
                            "pass"
                            if not run_config["fret_stk_config"]
                            else run_config["fret_stk_config"]["expected"]["status"]
                        ),
                        "returncode": 0,
                        "timed_out": False,
                        "terminal_observed": True,
                        "premature_exit": False,
                        "collector_termination": {
                            "status": "exited_after_terminal",
                            "requested": False,
                            "returncode": 0,
                        },
                        "generic_fault_seen": False,
                        "terminal": {
                            "case_id": case.case_id,
                            "case_number": case.case_number,
                            "token": token,
                            "terminal_pass_low8": True,
                            "terminal_case_id": case.case_number,
                            "finisher_addr": runner.FINISHER_ADDR,
                            "finisher_value": runner.PASS_VALUE,
                            "qemu_trace_event": "linx_virt_exit_write",
                        },
                        "qemu_log": qemu_log["path"],
                        "qemu_log_sha256": qemu_log["sha256"],
                        "terminal_trace": terminal_trace["path"],
                        "terminal_trace_sha256": terminal_trace["sha256"],
                    }
                )
                if case.case_id == runner.FRET_RA_CASE_ID:
                    runs[-1]["fret_ra"] = runner._parse_fret_ra_evidence(output, case, env_value)
                elif case.case_id == runner.FRET_STK_CASE_ID:
                    fret_stk = runner._parse_fret_stk_evidence(output, case, run_config["fret_stk_config"])
                    runs[-1]["fret_stk"] = fret_stk
                    if "product_blocker" in fret_stk:
                        runs[-1]["product_blocker"] = fret_stk["product_blocker"]
                else:
                    runs[-1]["fentry_trace"] = runner._parse_fentry_trace_evidence(output, case, env_value)
                    runs[-1]["fentry_slots"] = runner._parse_fentry_evidence(output, case, env_value)[1]
            observations.append(
                {
                    "id": case.case_id,
                    "kind": "dynamic",
                    "compile": {
                        "status": "compiled",
                        "compile_log": compile_log["path"],
                        "compile_log_sha256": compile_log["sha256"],
                        "kernel": kernel["path"],
                        "kernel_sha256": kernel["sha256"],
                    },
                    "runs": runs,
                }
            )
        observations.extend(runner._semantic_rows_for_current_red(observations))
        return {
            "schema": runner.SCHEMA,
            "mode": "current-red",
            "source": str(runner.SRC),
            "source_sha256": runner._sha256(runner.SRC),
            "manifest": runner._manifest_dict(),
            "observations": observations,
            "current_blockers": copy.deepcopy(runner.EXPECTED_CURRENT_BLOCKER_ROWS),
        }

    def _future_semantic_rows(self, dynamic_observations: list[dict]) -> list[dict]:
        return runner._semantic_rows_for_future_green(dynamic_observations)

    def future_green_report(self) -> dict:
        report = self.base_report()
        report["mode"] = "future-green"
        report["current_blockers"] = []
        report["observations"] = [
            item for item in report["observations"] if item["kind"] == "dynamic"
        ]
        report["observations"].extend(self._future_semantic_rows(report["observations"]))
        return report

    def assert_report_error(self, report: dict, mode: str, needle: str) -> None:
        errors = runner._validate_report(report, mode=mode)
        self.assertTrue(errors, "expected report validation to fail")
        self.assertTrue(any(needle in item for item in errors), errors)

    def test_manifest_has_required_semantic_rows(self) -> None:
        rows = {item["id"]: item for item in runner._manifest_dict()}
        for case in runner.MANIFEST:
            self.assertIn(case.case_id, rows)

    def test_guest_uses_raw_template_encodings(self) -> None:
        source = runner.SRC.read_text(encoding="utf-8")
        self.assertNotIn("\tFENTRY", source)
        self.assertNotIn("\tFEXIT", source)
        for mapping in runner.RAW_GUEST_ENCODINGS.values():
            if "fentry_word" in mapping:
                self.assertIn(f".word {mapping['fentry_word']}", source)
            if "fexit_word" in mapping:
                self.assertIn(f".word {mapping['fexit_word']}", source)
            if "fret_ra_word" in mapping:
                self.assertIn(f".word {mapping['fret_ra_word']}", source)
            if "fret_stk_word" in mapping:
                self.assertIn(f".word {mapping['fret_stk_word']}", source)
        malformed = runner.EXPECTED_SEMANTIC_OBSERVATIONS["malformed_admission_zero_effect"]
        malformed_words = {record["raw_word"] for record in malformed["records"]}
        self.assertIn("0x08ab0041", malformed_words)
        self.assertNotIn(".word 0x08ab0041", source)

    def test_raw_decoder_derives_exact_legal_rings(self) -> None:
        expected = {
            "valid_singleton_ra_terminal": (10, 10, 16, ["ra"]),
            "valid_wrap_r22_ra_terminal": (
                22,
                10,
                88,
                ["x2", "x3", "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "ra"],
            ),
            "valid_full_r2_s12_terminal": (2, 23, 176, list(runner.GPR_NAMES[2:24])),
        }
        for case in runner.MANIFEST:
            if case.case_id not in runner.FENTRY_DYNAMIC_CASES:
                continue
            decoded = runner._case_fentry_decode(case)
            begin, end, stacksize, registers = expected[case.case_id]
            with self.subTest(case=case.case_id):
                self.assertEqual(decoded["begin_index"], begin)
                self.assertEqual(decoded["end_index"], end)
                self.assertEqual(decoded["stacksize"], stacksize)
                self.assertEqual(decoded["registers"], registers)
                self.assertEqual(decoded["save_count"], len(registers))
                self.assertGreaterEqual(stacksize, decoded["legal_min_frame"])

    def test_raw_decoder_marks_old_wrap_insufficient(self) -> None:
        decoded = runner._decode_fentry_word("0x08ab0041")
        self.assertEqual(decoded["save_count"], 11)
        self.assertEqual(decoded["stacksize"], 32)
        self.assertEqual(decoded["legal_min_frame"], 88)
        self.assertFalse(decoded["legal"])

    def test_current_red_accepts_exact_required_rows(self) -> None:
        self.assertEqual(runner._validate_report(self.base_report(), mode="current-red"), [])

    def test_current_red_rejects_missing_semantic_rows(self) -> None:
        report = self.base_report()
        report["observations"] = [item for item in report["observations"] if item["kind"] != "semantic"]
        self.assert_report_error(report, "current-red", "semantic observation ID set")

    def test_manifest_mutation_rejects(self) -> None:
        report = self.base_report()
        report["manifest"][0]["raw_encoding"]["fentry_word"] = "0xdeadbeef"
        self.assert_report_error(report, "current-red", "manifest must match")

    def test_duplicate_blocker_rejects(self) -> None:
        report = self.base_report()
        report["current_blockers"].append(copy.deepcopy(report["current_blockers"][0]))
        self.assert_report_error(report, "current-red", "duplicate current blocker")

    def test_nonexistent_artifact_rejects(self) -> None:
        report = self.base_report()
        report["observations"][0]["runs"][0]["qemu_log"] = str(self.root / "missing.log")
        self.assert_report_error(report, "current-red", "artifact does not exist")

    def test_mismatched_artifact_digest_rejects(self) -> None:
        report = self.base_report()
        report["observations"][0]["runs"][0]["qemu_log_sha256"] = "0" * 64
        self.assert_report_error(report, "current-red", "artifact digest mismatch")

    def test_swapped_case_artifact_rejects(self) -> None:
        report = self.base_report()
        first = report["observations"][0]["runs"][0]
        second = report["observations"][1]["runs"][0]
        first["qemu_log"] = second["qemu_log"]
        first["qemu_log_sha256"] = second["qemu_log_sha256"]
        self.assert_report_error(report, "current-red", "terminal case id mismatch")

    def test_fentry_parser_rejects_missing_trace(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = runner._terminal_token(case) + "\n" + runner._terminal_trace_line() + "\n"
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_trace_evidence(text, case, None)

    def test_fentry_parser_rejects_duplicate_trace(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = self._fentry_line(case) + "\n" + self._fentry_line(case) + "\n"
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_trace_evidence(text, case, None)

    def test_fentry_parser_rejects_wrong_delta(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = self._fentry_line(case).replace("new_sp=0x7feffe0", "new_sp=0x7feffe1")
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_trace_evidence(text, case, None)

    def test_fentry_parser_rejects_nonzero_callframe(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = self._fentry_line(case).replace("callframe=0", "callframe=64")
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_trace_evidence(text, case, None)

    def test_fentry_parser_rejects_wrong_save_count(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 2)
        text = self._fentry_line(case).replace("save_count=11", "save_count=10")
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "save_count mismatch"):
            runner._parse_fentry_trace_evidence(text, case, None)

    def test_fentry_parser_rejects_wrong_begin(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 2)
        text = self._fentry_line(case).replace("begin=x2", "begin=x1")
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "begin/end mismatch"):
            runner._parse_fentry_trace_evidence(text, case, None)

    def test_fentry_parser_rejects_wrong_end(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 2)
        text = self._fentry_line(case).replace("end=ra", "end=a7")
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "begin/end mismatch"):
            runner._parse_fentry_trace_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_missing_slot_trace(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        trace = runner._parse_fentry_trace_evidence(self._fentry_line(case), case, None)
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_slot_evidence(self._fentry_line(case), case, trace)

    def test_fentry_slot_parser_rejects_shifted_slot_address(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 1)
        text = self._fentry_line(case) + "\n" + self._slot_lines(case).replace(
            "addr=0x7feffe8", "addr=0x7feffe0"
        )
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_duplicate_slot_record(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 1)
        text = self._fentry_line(case) + "\n" + self._slot_lines(case) + "\n" + self._slot_lines(case)
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_truncated_wrap(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 2)
        lines = self._slot_lines(case).splitlines()
        text = self._fentry_line(case) + "\n" + "\n".join(lines[:-1])
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "exactly 11"):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_truncated_full_ring(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 3)
        lines = self._slot_lines(case).splitlines()
        text = self._fentry_line(case) + "\n" + "\n".join(lines[:-1])
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "exactly 22"):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_missing_middle(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 2)
        lines = self._slot_lines(case).splitlines()
        text = self._fentry_line(case) + "\n" + "\n".join(lines[:5] + lines[6:])
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "exactly 11"):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_wrong_register(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 2)
        slots = self._slot_lines(case).replace("reg=x2 ", "reg=ra ", 1)
        text = self._fentry_line(case) + "\n" + slots
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "register/order mismatch"):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_reordered_log_rows(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 2)
        lines = self._slot_lines(case).splitlines()
        lines[4], lines[5] = lines[5], lines[4]
        text = self._fentry_line(case) + "\n" + "\n".join(lines)
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_slot_parser_rejects_wrong_value_readback(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 1)
        text = self._fentry_line(case) + "\n" + self._slot_lines(case).replace(
            "debug_readback=0x7fffff0", "debug_readback=0x7fffff1"
        )
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_fentry_evidence(text, case, None)

    def test_fentry_report_rejects_cross_case_swapped_slots(self) -> None:
        report = self.base_report()
        first = report["observations"][0]["runs"][0]
        second = report["observations"][1]["runs"][0]
        first["fentry_slots"] = copy.deepcopy(second["fentry_slots"])
        self.assert_report_error(report, "current-red", "FENTRY slot trace mismatch in qemu log")

    def test_fentry_report_rejects_reordered_slots(self) -> None:
        report = self.base_report()
        run = report["observations"][1]["runs"][0]
        run["fentry_slots"] = list(reversed(run["fentry_slots"]))
        self.assert_report_error(report, "current-red", "FENTRY slot trace mismatch in qemu log")

    def test_fentry_report_rejects_report_log_disagreement(self) -> None:
        report = self.base_report()
        run = report["observations"][1]["runs"][0]
        run["fentry_slots"][4]["value"] ^= 1
        self.assert_report_error(report, "current-red", "FENTRY slot trace mismatch in qemu log")

    def test_fentry_report_rejects_swapped_state_record(self) -> None:
        report = self.base_report()
        first = report["observations"][0]["runs"][0]
        second = report["observations"][1]["runs"][0]
        first["fentry_trace"] = copy.deepcopy(second["fentry_trace"])
        self.assert_report_error(report, "current-red", "FENTRY trace case id mismatch")

    def test_fentry_report_rejects_unset_vs_malicious_state_divergence(self) -> None:
        report = self.base_report()
        run = report["observations"][0]["runs"][1]
        trace = copy.deepcopy(run["fentry_trace"])
        trace["old_sp"] += 8
        trace["new_sp"] += 8
        run["fentry_trace"] = trace
        self.assert_report_error(report, "current-red", "FENTRY state tuple must be identical")

    def _fret_run(self, report: dict, *, env_index: int = 0) -> dict:
        item = next(item for item in report["observations"] if item["id"] == runner.FRET_RA_CASE_ID)
        return item["runs"][env_index]

    def _fret_stk_run(self, report: dict, *, env_index: int = 0) -> dict:
        item = next(item for item in report["observations"] if item["id"] == runner.FRET_STK_CASE_ID)
        return item["runs"][env_index]

    def test_fret_ra_parser_rejects_swapped_pre_and_slot_targets(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_RA_CASE_ID)
        text = "\n".join(
            [
                runner.FRET_RA_RESTORED_MARKER,
                runner.FRET_RA_PRE_MARKER,
                runner._terminal_token(case),
                runner._terminal_trace_line(),
            ]
        )
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "restored target reached before"):
            runner._parse_fret_ra_evidence(text, case, None)

    def test_fret_ra_parser_rejects_wrong_reached_marker(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_RA_CASE_ID)
        text = self._run_text(case).replace(runner.FRET_RA_PRE_MARKER, "LINX_FRET_RA_PRE_TARGET case=3")
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "pre-restore marker case mismatch"):
            runner._parse_fret_ra_evidence(text, case, None)

    def test_fret_ra_parser_rejects_post_ra_not_restored(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_RA_CASE_ID)
        text = self._run_text(case).replace(runner.FRET_RA_RESTORED_MARKER + "\n", "")
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "restored-target marker"):
            runner._parse_fret_ra_evidence(text, case, None)

    def test_fret_ra_parser_rejects_duplicate_evidence(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_RA_CASE_ID)
        text = self._run_text(case).replace(
            runner.FRET_RA_PRE_MARKER,
            runner.FRET_RA_PRE_MARKER + "\n" + runner.FRET_RA_PRE_MARKER,
        )
        with self.assertRaisesRegex(runner.TerminalEvidenceError, "exactly one pre-restore"):
            runner._parse_fret_ra_evidence(text, case, None)

    def test_fret_ra_report_rejects_wrong_sp_delta(self) -> None:
        report = self.base_report()
        run = self._fret_run(report)
        run["fret_ra"]["sp_delta"] = 8
        self.assert_report_error(report, "current-red", "FRET.RA evidence mismatch")

    def test_fret_ra_report_rejects_missing_record(self) -> None:
        report = self.base_report()
        run = self._fret_run(report)
        run.pop("fret_ra")
        self.assert_report_error(report, "current-red", "FRET.RA evidence mismatch")

    def test_fret_ra_report_rejects_report_log_disagreement(self) -> None:
        report = self.base_report()
        run = self._fret_run(report)
        run["fret_ra"]["restored_marker"] = "LINX_FRET_RA_RESTORED_TARGET case=0"
        self.assert_report_error(report, "current-red", "FRET.RA evidence mismatch")

    def test_current_red_keeps_only_required_semantic_blockers(self) -> None:
        report = self.base_report()
        blocker_ids = [item["id"] for item in report["current_blockers"]]
        self.assertEqual(
            blocker_ids,
            [
                "bad_target_zero_effect_oracle_missing",
                "phase_one_resume_oracle_missing",
                "device_mmio_vload_zero_read_oracle_missing",
            ],
        )
        self.assertNotIn("fret_stk_host_verify_double_read", blocker_ids)
        self.assertNotIn("fret_stk_no_second_read_oracle_missing", blocker_ids)
        self.assertEqual(self._fret_stk_run(report, env_index=2)["status"], "pass")
        self.assertNotIn("product_blocker", self._fret_stk_run(report, env_index=2))

    def test_fret_stk_parser_rejects_missing_duplicate_and_swapped_rows(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_STK_CASE_ID)
        config = runner.FRET_STK_DYNAMIC_CONFIGS[0]
        text = self._fret_stk_text(case, config)
        with self.subTest("missing_pre"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "pre-commit"):
                runner._parse_fret_stk_evidence(
                    "\n".join(line for line in text.splitlines() if not line.startswith("LINX_FRET_STK_TRACE ")) + "\n",
                    case,
                    config,
                )
        with self.subTest("duplicate_publish"):
            publish = next(line for line in text.splitlines() if line.startswith("LINX_FRET_STK_PUBLISH "))
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "publish"):
                runner._parse_fret_stk_evidence(text.replace(publish, publish + "\n" + publish), case, config)
        with self.subTest("swapped_key"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "publish row key"):
                runner._parse_fret_stk_evidence(text.replace("LINX_FRET_STK_PUBLISH count=7", "LINX_FRET_STK_PUBLISH count=8"), case, config)

    def test_fret_stk_parser_rejects_mismatched_address_value_target(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_STK_CASE_ID)
        config = runner.FRET_STK_DYNAMIC_CONFIGS[0]
        mutations = {
            "slot address": ("slot0_addr=0x7feffe8", "slot0_addr=0x7feffe0", "slot0 address"),
            "slot value": ("slot0_value=0x10200", "slot0_value=0x10208", "retained/restored"),
            "retained target": ("retained_target=0x10200", "retained_target=0x10208", "retained/restored"),
            "committed r10": ("committed_r10=0x10200", "committed_r10=0x10208", "committed R10"),
            "published target": ("published_target=0x10200", "published_target=0x10208", "published target"),
        }
        for name, (old, new, needle) in mutations.items():
            with self.subTest(name):
                with self.assertRaisesRegex(runner.TerminalEvidenceError, needle):
                    runner._parse_fret_stk_evidence(self._fret_stk_text(case, config).replace(old, new, 1), case, config)

    def test_fret_stk_parser_rejects_fabricated_proven_and_read_counts(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_STK_CASE_ID)
        default = runner.FRET_STK_DYNAMIC_CONFIGS[0]
        host_verify = runner.FRET_STK_DYNAMIC_CONFIGS[2]
        with self.subTest("read_count_zero"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "physical_restore_reads"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, default).replace("physical_restore_reads=1", "physical_restore_reads=0"),
                    case,
                    default,
                )
        with self.subTest("read_count_two_green"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "physical_restore_reads"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, default).replace("physical_restore_reads=1", "physical_restore_reads=2"),
                    case,
                    default,
                )
        with self.subTest("host_verify_two_read_regression"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "FRET.STK physical_restore_reads"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, host_verify).replace("physical_restore_reads=1", "physical_restore_reads=2"),
                    case,
                    host_verify,
                )
        with self.subTest("host_verify_unproven_regression"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "slot0_physical_reads"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, host_verify).replace(
                        "slot0_physical_reads=1",
                        "slot0_physical_reads=-1",
                    ).replace("slot0_physical_reads_proven=1", "slot0_physical_reads_proven=0"),
                    case,
                    host_verify,
                )
        with self.subTest("host_verify_fabricated_proven_two_read"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "slot0_physical_reads"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, host_verify).replace(
                        "slot0_physical_reads=1",
                        "slot0_physical_reads=-1",
                    ).replace("physical_restore_reads=1", "physical_restore_reads=2"),
                    case,
                    host_verify,
                )

    def test_fret_stk_parser_rejects_extra_reads_wrong_marker_terminal_and_env(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_id == runner.FRET_STK_CASE_ID)
        config = runner.FRET_STK_DYNAMIC_CONFIGS[0]
        with self.subTest("extra_logical"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "additional logical"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, config).replace("additional_slot0_loads=0", "additional_slot0_loads=1"),
                    case,
                    config,
                )
        with self.subTest("extra_physical"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "additional physical"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, config).replace("additional_slot0_physical_reads=0", "additional_slot0_physical_reads=1"),
                    case,
                    config,
                )
        with self.subTest("wrong_sp"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "SP delta"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, config).replace("new_sp=0x7fefff0", "new_sp=0x7feffe8"),
                    case,
                    config,
                )
        with self.subTest("wrong_marker"):
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "marker case"):
                runner._parse_fret_stk_evidence(
                    self._fret_stk_text(case, config).replace(runner.FRET_STK_RETAINED_MARKER, "LINX_FRET_STK_RETAINED_TARGET case=4"),
                    case,
                    config,
                )
        with self.subTest("terminal_before_marker"):
            text = self._fret_stk_text(case, config).replace(
                runner.FRET_STK_RETAINED_MARKER + "\n" + runner._terminal_token(case),
                runner._terminal_token(case) + "\n" + runner.FRET_STK_RETAINED_MARKER,
            )
            with self.assertRaisesRegex(runner.TerminalEvidenceError, "terminal appeared before"):
                runner._parse_fret_stk_evidence(text, case, config)
        with self.subTest("environment_disagreement"):
            report = self.base_report()
            self._fret_stk_run(report)["env"] = {"LINX_FRET_STK_TRACE": "1", "LINX_QEMU_FRAME_RESTORE_HOST_LOAD": "1"}
            self.assert_report_error(report, "current-red", "environment values")

    def test_fret_stk_report_rejects_report_log_disagreement(self) -> None:
        report = self.base_report()
        run = self._fret_stk_run(report)
        run["fret_stk"]["published_target"] ^= 8
        self.assert_report_error(report, "current-red", "FRET.STK trace mismatch in qemu log")

    def test_terminal_parser_rejects_empty_output(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_terminal_evidence("", case)

    def test_terminal_parser_rejects_duplicate_terminal_records(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = runner._terminal_token(case) + "\n" + runner._terminal_token(case) + "\n"
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_terminal_evidence(text + runner._terminal_trace_line(), case)

    def test_terminal_parser_rejects_partial_terminal_record(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = runner._terminal_token(case).split(" finisher_value=")[0]
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_terminal_evidence(text + "\n" + runner._terminal_trace_line(), case)

    def test_terminal_parser_rejects_wrong_case(self) -> None:
        case = next(case for case in runner.MANIFEST if case.case_number == 1)
        text = runner._terminal_token(case).replace("case=1", "case=2")
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_terminal_evidence(text + "\n" + runner._terminal_trace_line(), case)

    def test_terminal_parser_rejects_wrong_finisher_address(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = runner._terminal_token(case).replace("finisher_addr=0x10009000", "finisher_addr=0x10009004")
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_terminal_evidence(text + "\n" + runner._terminal_trace_line(), case)

    def test_terminal_parser_rejects_wrong_finisher_value(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        text = runner._terminal_token(case).replace("finisher_value=0x00005555", "finisher_value=0x00005554")
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_terminal_evidence(text + "\n" + runner._terminal_trace_line(), case)

    def test_terminal_parser_rejects_wrong_trace_value(self) -> None:
        case = next(case for case in runner.MANIFEST if case.kind == "dynamic")
        with self.assertRaises(runner.TerminalEvidenceError):
            runner._parse_terminal_evidence(
                runner._terminal_token(case) + "\nlinx_virt_exit_write value=0x5554",
                case,
            )

    def test_dynamic_validation_rejects_generic_fault(self) -> None:
        report = self.base_report()
        report["observations"][0]["runs"][0]["generic_fault_seen"] = True
        self.assert_report_error(report, "current-red", "generic fault is not conformance")

    def test_dynamic_validation_rejects_premature_exit(self) -> None:
        report = self.base_report()
        report["observations"][0]["runs"][0]["terminal_observed"] = False
        report["observations"][0]["runs"][0]["premature_exit"] = True
        report["observations"][0]["runs"][0]["collector_termination"] = {
            "status": "premature_exit",
            "requested": False,
            "returncode": 0,
        }
        self.assert_report_error(report, "current-red", "process exited before terminal evidence")

    def test_dynamic_validation_rejects_timeout_before_terminal(self) -> None:
        report = self.base_report()
        report["observations"][0]["runs"][0]["status"] = "timeout"
        report["observations"][0]["runs"][0]["timed_out"] = True
        report["observations"][0]["runs"][0]["terminal_observed"] = False
        report["observations"][0]["runs"][0]["collector_termination"] = {
            "status": "timeout_before_terminal",
            "requested": False,
            "returncode": None,
        }
        self.assert_report_error(report, "current-red", "timeout is not evidence")

    def test_dynamic_validation_rejects_termination_failure(self) -> None:
        report = self.base_report()
        report["observations"][0]["runs"][0]["collector_termination"] = {
            "status": "failed",
            "requested": True,
            "returncode": None,
        }
        self.assert_report_error(report, "current-red", "collector termination did not complete after evidence")

    def test_future_green_rejects_each_semantic_field_mutation(self) -> None:
        for case in runner.MANIFEST:
            if case.kind != "required-red":
                continue
            report = self.future_green_report()
            for item in report["observations"]:
                if item["id"] == case.case_id:
                    item["observed"] = copy.deepcopy(item["observed"])
                    item["observed"]["schema"] = "linx.qemu.frame_template_semantics.weakened"
                    break
            with self.subTest(case=case.case_id):
                self.assert_report_error(report, "future-green", "semantic observation mismatch")

    def _remove_fentry_trace_from_ingested_logs(self, report: dict, *, add_fallback_marker: bool = False) -> dict:
        report = copy.deepcopy(report)
        for item in report["observations"]:
            if item.get("kind") != "dynamic":
                continue
            if item["id"] not in runner.FENTRY_DYNAMIC_CASES:
                continue
            case = next(case for case in runner.MANIFEST if case.case_id == item["id"])
            for index, run in enumerate(item["runs"]):
                env_value = run["env"]["LINX_CALLFRAME_SIZE"]
                terminal_only = runner._terminal_token(case) + "\n" + runner._terminal_trace_line() + "\n"
                qemu_log = self._artifact(
                    f"missing-fentry/{case.case_id}/qemu-{index}.log",
                    terminal_only.encode(),
                )
                terminal_trace = self._artifact(
                    f"missing-fentry/{case.case_id}/terminal-{index}.log",
                    terminal_only.encode(),
                )
                run["qemu_log"] = qemu_log["path"]
                run["qemu_log_sha256"] = qemu_log["sha256"]
                run["terminal_trace"] = terminal_trace["path"]
                run["terminal_trace_sha256"] = terminal_trace["sha256"]
                if add_fallback_marker:
                    run["legacy_fixture_fentry_trace_source"] = "ingested_semantic_record"
                    run["fentry_trace"] = {
                        "case_id": case.case_id,
                        "raw_fentry_word": runner.RAW_GUEST_ENCODINGS[case.case_id]["fentry_word"],
                        "env": {"LINX_CALLFRAME_SIZE": env_value},
                        "pc": 0,
                        "old_sp": 0x800000,
                        "new_sp": 0x800000 - runner.EXPECTED_FENTRY_STACKSIZE[case.case_id],
                        "stacksize": runner.EXPECTED_FENTRY_STACKSIZE[case.case_id],
                        "delta": runner.EXPECTED_FENTRY_STACKSIZE[case.case_id],
                        "callframe": 0,
                        "begin": "?",
                        "end": "?",
                    }
                    run["fentry_slots"] = [
                        {
                            "index": 0,
                            "case_id": case.case_id,
                            "pc": 0,
                            "pre_sp": 0x800000,
                            "register": "ra",
                            "address": 0x7FFFF8,
                            "value": 0,
                            "memory_effect": {
                                "mmu": 0,
                                "mmu_readback": 0,
                                "host": "(nil)",
                                "host_readback": 0,
                                "debug_read_ok": True,
                                "debug_readback": 0,
                            },
                        }
                    ]
                else:
                    run.pop("fentry_trace", None)
                    run.pop("fentry_slots", None)
        return report

    def test_future_green_ingest_rejects_missing_fentry_trace(self) -> None:
        report = self._remove_fentry_trace_from_ingested_logs(self.future_green_report())
        normalized = runner._normalize_ingested_report(report)
        errors = runner._validate_report(normalized, mode="future-green")
        self.assertTrue(any("FENTRY trace evidence missing" in error for error in errors), errors)
        self.assertTrue(any("expected exactly one FENTRY trace record" in error for error in errors), errors)

    def test_future_green_ingest_rejects_fallback_marker_without_product_trace(self) -> None:
        report = self._remove_fentry_trace_from_ingested_logs(
            self.future_green_report(),
            add_fallback_marker=True,
        )
        normalized = runner._normalize_ingested_report(report)
        errors = runner._validate_report(normalized, mode="future-green")
        self.assertTrue(any("expected exactly one FENTRY trace record" in error for error in errors), errors)

    def test_future_green_cli_ingests_concrete_report_fixture(self) -> None:
        report_path = self.root / "future-report.json"
        report_path.write_text(
            json.dumps(self.future_green_report(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        out_dir = self.root / "out"
        self.assertEqual(
            runner.run(["--future-green", "--ingest-report", str(report_path), "--out-dir", str(out_dir)]),
            0,
        )
        copied = out_dir / "frame-template-semantics-report.json"
        self.assertTrue(copied.exists())


if __name__ == "__main__":
    unittest.main()
