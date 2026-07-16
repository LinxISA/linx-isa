#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_qemu_executable_coverage as coverage


QEMU_SHA = "1" * 40
FORM_ID = "fret_stk_32_4fe246bd8241"
RAW_BYTES = "4130a504"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReportQemuExecutableCoverageTests(unittest.TestCase):
    def test_checked_in_memory_bundle_binds_pc_to_elf_symbol_and_disassembly(self) -> None:
        root = Path(__file__).resolve().parents[2]
        manifest = json.loads(
            (root / "avs/qemu/qemu_executable_coverage_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        entry = next(
            item
            for item in manifest["evidence"]
            if item["form_id"] == "hl_swip_u_48_e2dc917c8505"
        )
        instruction = entry["instruction"]
        binding = coverage._inspect_elf_instruction(
            root,
            root / entry["elf"],
            pc=int(instruction["pc"], 0),
            size=len(bytes.fromhex(instruction["raw_bytes_le"])),
            symbol=instruction["symbol"],
        )
        self.assertEqual(binding["elf_offset"], int(instruction["elf_offset"], 0))
        self.assertEqual(binding["raw_bytes"].hex(), instruction["raw_bytes_le"])
        self.assertEqual(
            coverage._normalize_disassembly(binding["disassembly"]),
            coverage._normalize_disassembly(instruction["disassembly"]),
        )

    def test_clean_gate_rejects_partial_ledgers(self) -> None:
        report = {
            "evidence": {"L2": {"form_count": 2}, "L3": {"form_count": 2}},
            "rejected": [{"form_id": "unproven"}],
        }
        self.assertFalse(
            coverage._gate_failed(report, require_nonzero=True, require_clean=False)
        )
        self.assertTrue(
            coverage._gate_failed(report, require_nonzero=True, require_clean=True)
        )

    def test_nonzero_gate_rejects_empty_ledgers(self) -> None:
        report = {
            "evidence": {"L2": {"form_count": 0}, "L3": {"form_count": 0}},
            "rejected": [],
        }
        self.assertTrue(
            coverage._gate_failed(report, require_nonzero=True, require_clean=True)
        )

    def _fixture(self, root: Path) -> tuple[Path, Path, dict[str, object], dict[str, object]]:
        spec = root / "isa.json"
        spec.write_text(
            json.dumps(
                {
                    "instructions": [
                        {
                            "id": FORM_ID,
                            "mnemonic": "FRET.STK",
                            "encoding": {
                                "length_bits": 32,
                                "parts": [{"mask": "0x0000707f", "match": "0x00003041"}],
                            },
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        bundle = root / "docs" / "bringup" / "gates" / "evidence" / "qemu-executable" / "test-run"
        obj = bundle / "14_callret_templates.o"
        elf = bundle / "linx-qemu-tests.elf"
        obj.parent.mkdir(parents=True)
        obj.write_bytes(b"OBJ" + bytes.fromhex(RAW_BYTES) + b"object-tail")
        elf.write_bytes(b"ELF" + bytes.fromhex(RAW_BYTES) + b"executable-tail")

        oracle = root / "avs" / "qemu" / "tests" / "14_callret.c"
        oracle.parent.mkdir(parents=True)
        oracle.write_text(
            "extern long callret_tpl_fret_stk_slot_redirect(long);\n"
            "static void test_fret_stk_uses_stack_ra(void) {\n"
            "  long r = callret_tpl_fret_stk_slot_redirect(0);\n"
            "  TEST_EQ64(r, 0x22, 0x140b);\n"
            "}\n",
            encoding="utf-8",
        )

        run_path = bundle / "run-evidence.json"
        uart = bundle / "run-evidence.uart.log"
        trace = bundle / "run-evidence.pc.log"
        qemu = root / "emulator" / "qemu" / "build-test" / "qemu-system-linx64"
        qemu.parent.mkdir(parents=True)
        qemu.write_bytes(b"test qemu binary")
        uart.write_text("Test 0x0000140B: PASS\n", encoding="utf-8")
        trace.write_text("0x0000000000010016: FRET.STK\n", encoding="utf-8")
        run = {
            "schema_version": 1,
            "status": "PASS",
            "oracle_verdict": "PASS",
            "suites": ["callret"],
            "required_test_ids_observed": ["0x0000140b"],
            "artifacts": {
                "elf": {"path": str(elf.relative_to(root)), "sha256": _sha256(elf)},
                "object": {"path": str(obj.relative_to(root)), "sha256": _sha256(obj)},
                "uart": {"path": str(uart.relative_to(root)), "sha256": _sha256(uart)},
                "pc_trace": {"path": str(trace.relative_to(root)), "sha256": _sha256(trace)},
            },
            "qemu": {
                "path": str(qemu.relative_to(root)),
                "binary_sha256": _sha256(qemu),
                "sha": QEMU_SHA,
                "version": f"QEMU emulator version test (g{QEMU_SHA[:12]})",
                "source_dirty": False,
                "patch_sha256": None,
            },
            "run": {
                "exit_code": 85,
                "timed_out": False,
                "stalled": False,
                "timeout_after_fail": False,
                "pass_marker": {"kind": "finisher_exit_low8", "value": "0x55"},
                "stdout": "Test 0x0000140B: PASS",
            },
            "test_events": [
                {"seq": 0, "kind": "START", "test_id": "0x0000140b"},
                {"seq": 1, "kind": "PASS", "test_id": "0x0000140b"},
            ],
            "pc_hits": [
                {
                    "pc": "0x00010016",
                    "elf_offset": 3,
                    "raw_bytes_le": RAW_BYTES,
                    "symbol": "callret_tpl_fret_stk_slot_redirect",
                }
            ],
        }
        run_path.write_text(json.dumps(run), encoding="utf-8")

        entry = {
            "form_id": FORM_ID,
            "mnemonic": "FRET.STK",
            "form_key": {
                "length_bits": 32,
                "mask": "0x0000707f",
                "match": "0x00003041",
            },
            "suite": "callret",
            "test_id": "0x0000140b",
            "elf": str(elf.relative_to(root)),
            "object": str(obj.relative_to(root)),
            "instruction": {
                "raw_bytes_le": RAW_BYTES,
                "disassembly": "FRET.STK [ra ~ ra], sp!, 16",
                "object_offset": 3,
                "elf_offset": 3,
                "pc": "0x00010016",
                "symbol": "callret_tpl_fret_stk_slot_redirect",
            },
            "reachability": {
                "source": str(oracle.relative_to(root)),
                "test_symbol": "test_fret_stk_uses_stack_ra",
                "target_symbol": "callret_tpl_fret_stk_slot_redirect",
            },
            "qemu_sha": QEMU_SHA,
            "run_evidence": str(run_path.relative_to(root)),
            "run_evidence_sha256": _sha256(run_path),
            "oracle": {
                "kind": "exact_value",
                "source": str(oracle.relative_to(root)),
                "locator": "test_fret_stk_uses_stack_ra",
                "expected": "0x22",
            },
            "max_level": "L3",
            "test_contract": "valid",
            "failure_attribution": "none",
        }
        manifest = {
            "schema_version": 1,
            "availability": {"L2": "available", "L3": "available"},
            "evidence": [entry],
        }
        return spec, run_path, manifest, run

    def _report(
        self,
        root: Path,
        spec: Path,
        manifest: dict[str, object],
    ) -> dict[str, object]:
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        def inspect_fixture(
            repo_root: Path,
            elf_path: Path,
            *,
            pc: int,
            size: int,
            symbol: str,
        ) -> dict[str, object]:
            if pc != 0x10016 or symbol != "callret_tpl_fret_stk_slot_redirect":
                raise ValueError("instruction PC is outside the claimed ELF symbol range")
            raw = elf_path.read_bytes()[3 : 3 + size]
            return {
                "elf_offset": 3,
                "raw_bytes": raw,
                "objdump_bytes": raw,
                "disassembly": "FRET.STK [ra ~ ra], sp!, 16",
                "symbol_start": 0x10010,
                "symbol_end": 0x10030,
            }

        with mock.patch.object(
            coverage, "_inspect_elf_instruction", side_effect=inspect_fixture
        ):
            return coverage.build_report(
                repo_root=root,
                spec_path=spec,
                manifest_path=manifest_path,
                current_qemu_sha=QEMU_SHA,
                qemu_root=root / "emulator" / "qemu",
            )

    def _set_two_part_form(
        self,
        root: Path,
        spec: Path,
        run_path: Path,
        manifest: dict[str, object],
        run: dict[str, object],
        *,
        low_word: int = 0x0000000F,
        high_word: int = 0x00002001,
    ) -> None:
        spec_data = json.loads(spec.read_text(encoding="utf-8"))
        spec_data["instructions"][0]["encoding"] = {
            "length_bits": 64,
            "parts": [
                {
                    "index": 0,
                    "width_bits": 32,
                    "mask": "0x0000007f",
                    "match": "0x0000000f",
                },
                {
                    "index": 1,
                    "width_bits": 32,
                    "mask": "0x00007fff",
                    "match": "0x00002001",
                },
            ],
        }
        spec.write_text(json.dumps(spec_data), encoding="utf-8")

        entry = manifest["evidence"][0]
        entry["form_key"] = {
            "length_bits": 64,
            "mask": "0x00007fff0000007f",
            "match": "0x000020010000000f",
        }
        raw_bytes = low_word.to_bytes(4, "little") + high_word.to_bytes(4, "little")
        raw_text = raw_bytes.hex()
        entry["instruction"]["raw_bytes_le"] = raw_text
        run["pc_hits"][0]["raw_bytes_le"] = raw_text

        obj = root / entry["object"]
        elf = root / entry["elf"]
        obj.write_bytes(b"OBJ" + raw_bytes + b"object-tail")
        elf.write_bytes(b"ELF" + raw_bytes + b"executable-tail")
        run["artifacts"]["object"]["sha256"] = _sha256(obj)
        run["artifacts"]["elf"]["sha256"] = _sha256(elf)
        run_path.write_text(json.dumps(run), encoding="utf-8")
        entry["run_evidence_sha256"] = _sha256(run_path)

    def _use_target_pc_watch(
        self,
        root: Path,
        run_path: Path,
        manifest: dict[str, object],
        run: dict[str, object],
    ) -> Path:
        pc_watch = run_path.with_suffix(".pc-watch.log")
        pc_watch.write_text(
            "linx_pc_watch: pc=0x10016 hit=1 printed=1 count=44 sp=0x0\n",
            encoding="utf-8",
        )
        run["artifacts"].pop("pc_trace", None)
        run["artifacts"]["pc_watch"] = {
            "path": str(pc_watch.relative_to(root)),
            "sha256": _sha256(pc_watch),
        }
        run["pc_evidence"] = {
            "kind": coverage.TARGET_PC_WATCH_KIND,
            "requested_pcs": ["0x0000000000010016"],
            "packet_prefix": "linx_pc_watch:",
        }
        run["qemu_debug_env"] = {
            "LINX_DEBUG_PC_WATCH": "0x10016",
            "LINX_DEBUG_PC_WATCH_HIT_LIMIT": "1",
            "LINX_DEBUG_PC_WATCH_PRINT": "1",
        }
        run["pc_hits"] = [
            {
                "pc": "0x0000000000010016",
                "hit": 1,
                "count": 44,
                "evidence_kind": coverage.TARGET_PC_WATCH_KIND,
            }
        ]
        run_path.write_text(json.dumps(run), encoding="utf-8")
        manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
        return pc_watch

    def test_complete_form_evidence_enters_l2_and_l3(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, _ = self._fixture(root)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["availability"], "available")
        self.assertEqual(report["evidence"]["L2"]["form_count"], 1)
        self.assertEqual(report["evidence"]["L3"]["form_count"], 1)
        self.assertEqual(report["admitted"][0]["form_id"], FORM_ID)
        self.assertEqual(report["rejected"], [])

    def test_target_scoped_pc_watch_packet_enters_l2_and_l3(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            self._use_target_pc_watch(root, run_path, manifest, run)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 1)
        self.assertEqual(report["evidence"]["L3"]["form_count"], 1)
        self.assertEqual(report["rejected"], [])

    def test_target_pc_watch_forgery_missing_packet_and_wrong_digest_are_rejected(self) -> None:
        mutations = {
            "forged-json": (
                lambda run, packet: packet.write_text(
                    "linx_pc_watch: pc=0x10018 hit=1 printed=1 count=44\n",
                    encoding="utf-8",
                ),
                "hashed target PC-watch packet",
            ),
            "missing-packet": (
                lambda run, packet: packet.write_text(
                    "IN: translation-only\n0x0000000000010016: FRET.STK\n",
                    encoding="utf-8",
                ),
                "hashed target PC-watch packet",
            ),
            "wrong-digest": (
                lambda run, packet: run["artifacts"]["pc_watch"].update(
                    {"sha256": "0" * 64}
                ),
                "SHA-256",
            ),
        }
        for label, (mutate, expected_reason) in mutations.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                spec, run_path, manifest, run = self._fixture(root)
                packet = self._use_target_pc_watch(root, run_path, manifest, run)
                mutate(run, packet)
                if label != "wrong-digest":
                    run["artifacts"]["pc_watch"]["sha256"] = _sha256(packet)
                run_path.write_text(json.dumps(run), encoding="utf-8")
                manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
                report = self._report(root, spec, manifest)

                self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
                self.assertEqual(report["evidence"]["L3"]["form_count"], 0)
                self.assertIn(
                    expected_reason, " ".join(report["rejected"][0]["reasons"])
                )

    def test_target_pc_watch_wrong_pc_and_wrong_qemu_sha_are_rejected(self) -> None:
        for label in ("wrong-pc", "wrong-qemu-sha"):
            with self.subTest(case=label), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                spec, run_path, manifest, run = self._fixture(root)
                packet = self._use_target_pc_watch(root, run_path, manifest, run)
                if label == "wrong-pc":
                    packet.write_text(
                        "linx_pc_watch: pc=0x10018 hit=1 printed=1 count=44\n",
                        encoding="utf-8",
                    )
                    run["artifacts"]["pc_watch"]["sha256"] = _sha256(packet)
                    run["pc_hits"][0]["pc"] = "0x0000000000010018"
                else:
                    run["qemu"]["sha"] = "2" * 40
                run_path.write_text(json.dumps(run), encoding="utf-8")
                manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
                report = self._report(root, spec, manifest)

                self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
                self.assertEqual(report["evidence"]["L3"]["form_count"], 0)
                expected_reason = (
                    "exact executed PC hit"
                    if label == "wrong-pc"
                    else "run QEMU SHA disagrees"
                )
                self.assertIn(
                    expected_reason, " ".join(report["rejected"][0]["reasons"])
                )

    def test_two_part_64_bit_form_evidence_is_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            self._set_two_part_form(root, spec, run_path, manifest, run)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 1)
        self.assertEqual(report["evidence"]["L3"]["form_count"], 1)
        self.assertEqual(
            report["admitted"][0]["form_key"],
            {
                "length_bits": 64,
                "mask": "0x7fff0000007f",
                "match": "0x20010000000f",
            },
        )

    def test_two_part_form_rejects_mismatch_in_either_half(self) -> None:
        mismatches = {
            "low": {"low_word": 0x0000000E},
            "high": {"high_word": 0x00002000},
        }
        for label, words in mismatches.items():
            with self.subTest(part=label), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                spec, run_path, manifest, run = self._fixture(root)
                self._set_two_part_form(root, spec, run_path, manifest, run, **words)
                report = self._report(root, spec, manifest)

                self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
                self.assertIn(
                    "raw bytes do not match golden form encoding",
                    report["rejected"][0]["reasons"],
                )

    def test_spec_forms_rejects_invalid_part_layouts(self) -> None:
        base_part = {
            "index": 0,
            "width_bits": 32,
            "mask": "0x0000007f",
            "match": "0x0000000f",
        }
        invalid_parts = {
            "duplicate index": [base_part, {**base_part}],
            "invalid width": [{**base_part, "width_bits": 33}],
            "part exceeds instruction": [{**base_part, "index": 1}],
            "mask exceeds part width": [{**base_part, "mask": "0x100000000"}],
            "match outside mask": [{**base_part, "match": "0x0000008f"}],
        }
        for label, parts in invalid_parts.items():
            with self.subTest(layout=label):
                spec = {
                    "instructions": [
                        {
                            "id": "test_form",
                            "mnemonic": "TEST",
                            "encoding": {"length_bits": 32, "parts": parts},
                        }
                    ]
                }
                with self.assertRaises(ValueError):
                    coverage._spec_forms(spec)

    def test_deleting_required_evidence_downgrades_form(self) -> None:
        mutations = {
            "PASS": lambda entry, run: run.pop("status"),
            "test_id": lambda entry, run: entry.pop("test_id"),
            "oracle": lambda entry, run: entry.pop("oracle"),
            "byte evidence": lambda entry, run: entry["instruction"].pop("raw_bytes_le"),
        }
        for label, mutate in mutations.items():
            with self.subTest(missing=label), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                spec, run_path, manifest, run = self._fixture(root)
                entry = manifest["evidence"][0]
                mutate(entry, run)
                run_path.write_text(json.dumps(run), encoding="utf-8")
                report = self._report(root, spec, manifest)

                self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
                self.assertEqual(report["evidence"]["L3"]["form_count"], 0)
                self.assertEqual(len(report["rejected"]), 1)

    def test_forged_stdout_and_exit_zero_do_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["status"] = "PASS"
            run["run"] = {
                "exit_code": 0,
                "timed_out": False,
                "stalled": False,
                "pass_marker": {"kind": "uart_success_marker", "value": "PASS"},
                "stdout": "PASS\nTEST SUITE COMPLETE\n",
            }
            run_path.write_text(json.dumps(run), encoding="utf-8")
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertEqual(report["evidence"]["L3"]["form_count"], 0)
        self.assertIn("finisher", " ".join(report["rejected"][0]["reasons"]))

    def test_verified_uart_suite_marker_is_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            uart = root / run["artifacts"]["uart"]["path"]
            uart.write_text(
                "Test 0x0000140B: PASS\nTEST SUITE COMPLETE\n",
                encoding="utf-8",
            )
            run["artifacts"]["uart"]["sha256"] = _sha256(uart)
            run["run"]["exit_code"] = 0
            run["run"]["pass_marker"] = {
                "kind": "uart_success_marker",
                "value": "TEST SUITE COMPLETE",
            }
            run["run"]["missing_required_test_ids"] = []
            run["run"]["missing_suite_completion_test_ids"] = []
            run["run"]["declared_suite_completion_test_ids"] = ["0x0000140b"]
            manifest["evidence"][0]["suite_completion_test_id"] = "0x0000140b"
            run_path.write_text(json.dumps(run), encoding="utf-8")
            manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 1)
        self.assertEqual(report["evidence"]["L3"]["form_count"], 1)

    def test_isolated_pass_cannot_forge_a_suite_uart_marker(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["run"]["exit_code"] = 0
            run["run"]["pass_marker"] = {
                "kind": "uart_success_marker",
                "value": "TEST SUITE COMPLETE",
            }
            run_path.write_text(json.dumps(run), encoding="utf-8")
            manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("final completion", " ".join(report["rejected"][0]["reasons"]))

    def test_uart_marker_rejects_missing_final_completion_event(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            uart = root / run["artifacts"]["uart"]["path"]
            uart.write_text(
                "Test 0x0000140B: PASS\nTEST SUITE COMPLETE\n",
                encoding="utf-8",
            )
            run["artifacts"]["uart"]["sha256"] = _sha256(uart)
            run["run"].update(
                {
                    "exit_code": 0,
                    "pass_marker": {
                        "kind": "uart_success_marker",
                        "value": "TEST SUITE COMPLETE",
                    },
                    "missing_required_test_ids": [],
                    "missing_suite_completion_test_ids": ["0x00001412"],
                    "declared_suite_completion_test_ids": ["0x00001412"],
                }
            )
            manifest["evidence"][0]["suite_completion_test_id"] = "0x00001412"
            run_path.write_text(json.dumps(run), encoding="utf-8")
            manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("final completion", " ".join(report["rejected"][0]["reasons"]))

    def test_missing_pc_trace_rejects_form_level_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["pc_hits"] = []
            run_path.write_text(json.dumps(run), encoding="utf-8")
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("PC hit", " ".join(report["rejected"][0]["reasons"]))

    def test_trace_hit_disconnected_from_claimed_elf_symbol_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            entry = manifest["evidence"][0]
            entry["instruction"]["pc"] = "0x00010030"
            run["pc_hits"] = [{"pc": "0x00010030", "elf_offset": 3, "raw_bytes_le": RAW_BYTES}]
            trace = root / run["artifacts"]["pc_trace"]["path"]
            trace.write_text("0x0000000000010030: unrelated\n", encoding="utf-8")
            run["artifacts"]["pc_trace"]["sha256"] = _sha256(trace)
            run_path.write_text(json.dumps(run), encoding="utf-8")
            entry["run_evidence_sha256"] = _sha256(run_path)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("symbol range", " ".join(report["rejected"][0]["reasons"]))

    def test_claimed_pc_absent_from_hashed_trace_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            trace = root / run["artifacts"]["pc_trace"]["path"]
            trace.write_text("0x0000000000019999: unrelated\n", encoding="utf-8")
            run["artifacts"]["pc_trace"]["sha256"] = _sha256(trace)
            run_path.write_text(json.dumps(run), encoding="utf-8")
            manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("hashed PC trace", " ".join(report["rejected"][0]["reasons"]))

    def test_unreachable_target_symbol_rejects_form_level_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, _ = self._fixture(root)
            source = root / manifest["evidence"][0]["reachability"]["source"]
            source.write_text(
                "static void test_fret_stk_uses_stack_ra(void) { TEST_EQ64(r, 0x22, 0x140b); }",
                encoding="utf-8",
            )
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("reachable", " ".join(report["rejected"][0]["reasons"]))

    def test_oracle_literals_must_be_in_locator_assertion(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, _ = self._fixture(root)
            source = root / manifest["evidence"][0]["oracle"]["source"]
            source.write_text(
                "extern long callret_tpl_fret_stk_slot_redirect(long);\n"
                "static void test_fret_stk_uses_stack_ra(void) {\n"
                "  long r = callret_tpl_fret_stk_slot_redirect(0);\n"
                "  TEST_EQ64(r, 0x99, 0x9999);\n"
                "}\n"
                "static void unrelated(void) { TEST_EQ64(r, 0x22, 0x140b); }\n",
                encoding="utf-8",
            )
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L3"]["form_count"], 0)
        self.assertIn("locator assertion", " ".join(report["rejected"][0]["reasons"]))

    def test_missing_local_binary_uses_audited_bundle_digest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, run = self._fixture(root)
            (root / run["qemu"]["path"]).unlink()
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 1)
        self.assertEqual(report["admitted"][0]["qemu_binary_verification"], "audited_recorded_digest")

    def test_missing_binary_without_audited_run_digest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, run = self._fixture(root)
            (root / run["qemu"]["path"]).unlink()
            manifest["evidence"][0].pop("run_evidence_sha256")
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("audited", " ".join(report["rejected"][0]["reasons"]))

    def test_foreign_qemu_path_is_rejected_even_when_digest_is_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["qemu"]["path"] = "tools/foreign/qemu-system-linx64"
            run_path.write_text(json.dumps(run), encoding="utf-8")
            manifest["evidence"][0]["run_evidence_sha256"] = _sha256(run_path)
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("selected QEMU root/build", " ".join(report["rejected"][0]["reasons"]))

    def test_anonymous_duplicate_and_out_of_order_pass_are_rejected(self) -> None:
        event_sets = {
            "anonymous": [
                {"seq": 0, "kind": "START", "test_id": "0x0000140b"},
                {"seq": 1, "kind": "PASS"},
            ],
            "duplicate": [
                {"seq": 0, "kind": "START", "test_id": "0x0000140b"},
                {"seq": 1, "kind": "PASS", "test_id": "0x0000140b"},
                {"seq": 2, "kind": "PASS", "test_id": "0x0000140b"},
            ],
            "out-of-order": [
                {"seq": 0, "kind": "PASS", "test_id": "0x0000140b"},
                {"seq": 1, "kind": "START", "test_id": "0x0000140b"},
            ],
        }
        for label, events in event_sets.items():
            with self.subTest(events=label), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                spec, run_path, manifest, run = self._fixture(root)
                run["test_events"] = events
                run_path.write_text(json.dumps(run), encoding="utf-8")
                report = self._report(root, spec, manifest)
                self.assertEqual(report["evidence"]["L2"]["form_count"], 0)

    def test_invalid_test_contract_is_observed_without_qemu_attribution(self) -> None:
        for contract in ("invalid", "under_review"):
            with self.subTest(contract=contract), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                spec, _, manifest, _ = self._fixture(root)
                manifest["evidence"][0]["test_contract"] = contract
                manifest["evidence"][0]["failure_attribution"] = "test_contract"
                report = self._report(root, spec, manifest)

                self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
                self.assertEqual(report["execution_observations"][0]["test_contract"], contract)
                self.assertEqual(report["execution_observations"][0]["failure_attribution"], "test_contract")

    def test_failing_execution_is_persisted_but_not_counted(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["status"] = "FAIL"
            run["oracle_verdict"] = "FAIL"
            run["run"] = {
                "exit_code": -9,
                "timed_out": True,
                "stalled": False,
                "timeout_after_fail": True,
                "pass_marker": None,
                "stdout": "FAIL\n    Test ID:  0x00001321\n"
                "    Expected: 0x0000000000000053\n"
                "    Actual:   0x0000000000000011\n",
            }
            run["failure"] = {
                "test_id": "0x00001321",
                "expected": "0x0000000000000053",
                "actual": "0x0000000000000011",
            }
            run_path.write_text(json.dumps(run), encoding="utf-8")
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertEqual(report["evidence"]["L3"]["form_count"], 0)
        observation = report["execution_observations"][0]
        self.assertEqual(observation["status"], "FAIL")
        self.assertEqual(observation["oracle_verdict"], "FAIL")
        self.assertEqual(observation["failure"]["test_id"], "0x00001321")
        self.assertEqual(observation["failure"]["expected"], "0x0000000000000053")
        self.assertEqual(observation["failure"]["actual"], "0x0000000000000011")
        self.assertTrue(observation["timeout_after_fail"])

    def test_unavailable_is_distinct_from_available_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, _ = self._fixture(root)

            unavailable = copy.deepcopy(manifest)
            unavailable["availability"] = {"L2": "unavailable", "L3": "unavailable"}
            unavailable["evidence"] = []
            unavailable_report = self._report(root, spec, unavailable)

            zero = copy.deepcopy(manifest)
            zero["evidence"] = []
            zero_report = self._report(root, spec, zero)

        for level in ("L2", "L3"):
            self.assertEqual(unavailable_report["evidence"][level]["availability"], "unavailable")
            self.assertIsNone(unavailable_report["evidence"][level]["form_count"])
            self.assertEqual(zero_report["evidence"][level]["availability"], "available")
            self.assertEqual(zero_report["evidence"][level]["form_count"], 0)

    def test_l2_admission_does_not_imply_l3(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, _ = self._fixture(root)
            manifest["evidence"][0]["max_level"] = "L2"
            manifest["evidence"][0]["oracle"]["kind"] = "runtime_invariant"
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 1)
        self.assertEqual(report["evidence"]["L3"]["form_count"], 0)

    def test_qemu_sha_mismatch_rejects_entry(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, _, manifest, _ = self._fixture(root)
            manifest["evidence"][0]["qemu_sha"] = "2" * 40
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("QEMU SHA", " ".join(report["rejected"][0]["reasons"]))

    def test_qemu_binary_version_must_identify_bound_source(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["qemu"]["version"] = "QEMU emulator version test (g222222222222)"
            run_path.write_text(json.dumps(run), encoding="utf-8")
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("version", " ".join(report["rejected"][0]["reasons"]))

    def test_dirty_qemu_requires_explicit_patch_digest_binding(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["qemu"]["source_dirty"] = True
            run["qemu"]["patch_sha256"] = "a" * 64
            run_path.write_text(json.dumps(run), encoding="utf-8")
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("dirty", " ".join(report["rejected"][0]["reasons"]))


if __name__ == "__main__":
    unittest.main()
