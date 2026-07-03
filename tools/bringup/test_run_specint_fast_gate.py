#!/usr/bin/env python3
from __future__ import annotations

import unittest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_specint_fast_gate as gate


class SpecintFastGateTests(unittest.TestCase):
    def test_all_suite_routes_large_payload_bench_to_9p(self) -> None:
        units = gate._suite_execution_units(gate.SUITES["test-all"], "")

        self.assertEqual([unit.name for unit in units], ["test-all", "test-all-large-9p"])
        self.assertEqual(units[0].transports, "initramfs")
        self.assertNotIn("525.x264_r", units[0].benches)
        self.assertEqual(units[1].transports, "9p")
        self.assertEqual(units[1].benches, ("525.x264_r",))

    def test_explicit_transport_override_keeps_suite_unsplit(self) -> None:
        units = gate._suite_execution_units(gate.SUITES["test-all"], "initramfs")

        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].name, "test-all")
        self.assertEqual(units[0].transports, "initramfs")
        self.assertIn("525.x264_r", units[0].benches)

    def test_9p_override_keeps_all_benches_together(self) -> None:
        units = gate._suite_execution_units(gate.SUITES["train-all"], "9p")

        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].name, "train-all")
        self.assertEqual(units[0].transports, "9p")
        self.assertEqual(units[0].benches, gate.SPECINT_STAGE_B_BENCHES)

    def test_large_auto_9p_shard_fails_fast_on_timeout(self) -> None:
        units = gate._suite_execution_units(gate.SUITES["train-all"], "")
        large = units[1]

        self.assertEqual(large.name, "train-all-large-9p")
        self.assertTrue(gate._auto_fail_9p_timeout(large, ""))
        self.assertFalse(gate._auto_fail_9p_timeout(large, "9p"))
        self.assertFalse(gate._auto_fail_9p_timeout(units[0], ""))

    def test_format_failure_details_includes_tlb_fill_stats(self) -> None:
        text = gate._format_failure_details(
            {
                "505.mcf_r": {
                    "heartbeat_running": True,
                    "heartbeat_site_progress": True,
                    "heartbeat_last_progress": "site-change",
                    "heartbeat_last_bpc": "0x155555c4be",
                    "heartbeat_tlb_fill": {
                        "total": 225069739,
                        "fetch": 1436090,
                        "load": 201417280,
                        "store": 22216369,
                        "probe": 138258,
                        "user": 224000000,
                        "kernel": 1069739,
                        "other": 0,
                    },
                }
            }
        )

        self.assertIn("tlbf=225069739/f1436090/l201417280/s22216369/p138258", text)
        self.assertIn("/u224000000/k1069739/o0", text)

    def test_markdown_records_qemu_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "summary.md"
            gate._write_md(
                path,
                {
                    "profile": "pr",
                    "ok": True,
                    "elapsed_sec": 1.0,
                    "qemu": "/tmp/qemu-system-linx64",
                    "qemu_provenance": {
                        "version": "QEMU emulator version 10.2.50",
                        "qemu_repo_head": "abc123",
                        "clean_build_for_head": True,
                    },
                    "qemu_machine_extra": "dumpdtb=/tmp/virt.dtb",
                    "qemu_extra_args": ["-accel", "tcg,split-wx=off"],
                    "spec_dir": "/spec",
                    "memory_mb": 2048,
                    "stack_limit": "2G",
                    "qemu_heartbeat_interval": 100,
                    "qemu_heartbeat_regs": False,
                    "qemu_heartbeat_code_bytes": 0,
                    "qemu_heartbeat_same_site_warn": 0,
                    "fail_9p_timeout": False,
                    "suites": [],
                },
            )

            text = path.read_text(encoding="utf-8")

        self.assertIn("qemu_version: `QEMU emulator version 10.2.50`", text)
        self.assertIn("qemu_repo_head: `abc123`", text)
        self.assertIn("qemu_clean_build_for_head: `true`", text)
        self.assertIn("qemu_machine_extra: `dumpdtb=/tmp/virt.dtb`", text)
        self.assertIn("qemu_extra_args: `-accel tcg,split-wx=off`", text)

    def test_suite_command_forwards_qemu_heartbeat_debug_switches(self) -> None:
        cmd = gate._suite_command(
            suite=gate.SUITES["train-smoke"],
            runner=Path("/runner.py"),
            spec_dir=Path("/spec"),
            qemu=Path("/qemu"),
            sysroot=Path("/sysroot"),
            out_dir=Path("/out"),
            append_extra="norandmaps",
            heartbeat_sec=30,
            memory_mb=2048,
            qemu_heartbeat_interval=1000000000,
            qemu_heartbeat_regs=True,
            qemu_heartbeat_code_bytes=16,
            qemu_heartbeat_same_site_warn=4,
            no_progress_timeout=120,
            forward_memory_mb=True,
            forward_qemu_heartbeat=True,
            forward_qemu_heartbeat_regs=True,
            forward_qemu_heartbeat_code_bytes=True,
            forward_qemu_heartbeat_same_site_warn=True,
            forward_no_progress=True,
            forward_stack_limit=True,
            forward_symbolize_heartbeat=True,
            stack_limit="2G",
            symbolize_heartbeat=True,
            guest_heartbeat_sec=0,
            dump_prefix_bytes=0,
            fail_9p_timeout=True,
        )

        self.assertIn("--qemu-heartbeat-regs", cmd)
        self.assertIn("--qemu-heartbeat-code-bytes", cmd)
        self.assertEqual(cmd[cmd.index("--qemu-heartbeat-code-bytes") + 1], "16")
        self.assertIn("--qemu-heartbeat-same-site-warn", cmd)
        self.assertEqual(cmd[cmd.index("--qemu-heartbeat-same-site-warn") + 1], "4")
        self.assertIn("--fail-9p-timeout", cmd)


if __name__ == "__main__":
    unittest.main()
