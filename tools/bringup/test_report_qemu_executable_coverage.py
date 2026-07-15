#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_qemu_executable_coverage as coverage


QEMU_SHA = "1" * 40
FORM_ID = "fret_stk_32_4fe246bd8241"
RAW_BYTES = "4130a504"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReportQemuExecutableCoverageTests(unittest.TestCase):
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
        return coverage.build_report(
            repo_root=root,
            spec_path=spec,
            manifest_path=manifest_path,
            current_qemu_sha=QEMU_SHA,
            qemu_root=root / "emulator" / "qemu",
        )

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

    def test_missing_pc_trace_rejects_form_level_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec, run_path, manifest, run = self._fixture(root)
            run["pc_hits"] = []
            run_path.write_text(json.dumps(run), encoding="utf-8")
            report = self._report(root, spec, manifest)

        self.assertEqual(report["evidence"]["L2"]["form_count"], 0)
        self.assertIn("PC hit", " ".join(report["rejected"][0]["reasons"]))

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
