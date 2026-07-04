#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import run_stage_qemu_matrix as matrix


class StageQemuMatrixTests(unittest.TestCase):
    def test_multi_run_benchmark_reports_failing_subrun(self) -> None:
        summary = {
            "results": {
                "500.perlbench_r": {
                    "ok": False,
                    "qemu": [
                        {
                            "failure_class": "none",
                            "heartbeat_last_bpc": "0x15555d66f2",
                            "heartbeat_last_count": 34000000001,
                            "heartbeat_last_progress": "site-change",
                            "heartbeat_running": True,
                            "heartbeat_site_progress": True,
                            "log": "run_001/qemu.log",
                        },
                        {
                            "failure_class": "user-trap",
                            "failure_evidence": "LINX_USER_TRAP addr=0x3f7fee56880000",
                            "qemu_machine": "virt,accel=tcg",
                            "qemu_machine_extra": "dumpdtb=/tmp/virt.dtb",
                            "qemu_extra_args": ["-accel", "tcg,split-wx=off"],
                            "heartbeat_last_bpc": "0x1555677c50",
                            "heartbeat_last_count": 4000000025,
                            "heartbeat_last_progress": "site-change",
                            "heartbeat_running": True,
                            "heartbeat_site_progress": True,
                            "heartbeat_kernel_panic_loop": True,
                            "heartbeat_kernel_symbol_evidence": "heartbeat kernel symbols: 0xffffffff800019bc=.LBB14_51 panic.c:0",
                            "heartbeat_tlb_fill_hot": {
                                "seen": True,
                                "top0_count": 12345,
                                "top0_page": "0x3f7fa8d000",
                                "top0_access": 1,
                                "top0_mmu": 1,
                                "evictions": 17,
                            },
                            "log": "run_002/qemu.log",
                        },
                    ],
                },
                "999.specrand_ir": {
                    "ok": True,
                    "qemu": [{"failure_class": "none"}],
                },
            }
        }

        self.assertEqual(
            matrix._transport_failure_classes(summary),
            {"500.perlbench_r": "user-trap"},
        )
        self.assertEqual(
            matrix._transport_failure_details(summary)["500.perlbench_r"]["log"],
            "run_002/qemu.log",
        )
        self.assertEqual(
            matrix._transport_failure_details(summary)["500.perlbench_r"][
                "heartbeat_last_bpc"
            ],
            "0x1555677c50",
        )
        self.assertEqual(
            matrix._transport_failure_details(summary)["500.perlbench_r"][
                "qemu_extra_args"
            ],
            ["-accel", "tcg,split-wx=off"],
        )
        self.assertTrue(
            matrix._transport_failure_details(summary)["500.perlbench_r"][
                "heartbeat_kernel_panic_loop"
            ]
        )
        self.assertEqual(
            matrix._transport_failure_details(summary)["500.perlbench_r"][
                "heartbeat_tlb_fill_hot"
            ]["top0_page"],
            "0x3f7fa8d000",
        )
        self.assertIn(
            "kernel-panic-loop",
            matrix._format_failure_details(
                matrix._transport_failure_details(summary)
            ),
        )
        self.assertIn(
            "tlbf-hot=12345@0x3f7fa8d000/a1/m1 evict=17",
            matrix._format_failure_details(
                matrix._transport_failure_details(summary)
            ),
        )

    def test_markdown_records_qemu_fault_filters(self) -> None:
        summary = {
            "stage": "b",
            "input_set": "test",
            "strict": True,
            "transports": ["initramfs"],
            "qemu_provenance": {
                "path": "/tmp/qemu-system-linx64",
                "version": "QEMU emulator version 10.2.50",
                "qemu_repo_head": "abc123",
                "clean_build_for_head": True,
            },
            "qemu_machine_extra": "dumpdtb=/tmp/virt.dtb",
            "qemu_extra_args": ["-accel", "tcg,split-wx=off"],
            "timeout_sec": 180,
            "memory_mb": 2048,
            "stack_limit": "2G",
            "append_extra": "norandmaps",
            "qemu_heartbeat_interval": 1000000000,
            "qemu_heartbeat_regs": True,
            "qemu_heartbeat_code_bytes": 16,
            "qemu_heartbeat_same_site_warn": 4,
            "qemu_fault_trace": True,
            "qemu_fault_trace_regs": True,
            "qemu_fault_trace_limit": 1,
            "qemu_fault_trace_filters": {
                "LINX_QEMU_FAULT_TRACE_PC_LO": "0x15559efe00",
                "LINX_QEMU_FAULT_TRACE_PC_HI": "0x15559efe40",
            },
            "qemu_syscall_trace": {
                "LINX_SYSCALL_TRACE": "1",
                "LINX_SYSCALL_TRACE_PC_LO": "0x1555837f00",
                "LINX_SYSCALL_TRACE_PC_HI": "0x1555838000",
            },
            "guest_heartbeat_sec": 10,
            "guest_proc_diagnostics": True,
            "bench_override": ["523.xalancbmk_r"],
            "ok": False,
            "elapsed_sec": 1.0,
            "results": [],
            "failed_transports": [],
        }

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "summary.md"
            matrix._write_md(path, summary)
            text = path.read_text()

        self.assertIn("qemu_fault_trace: `true`", text)
        self.assertIn("qemu_heartbeat_regs: `true`", text)
        self.assertIn("qemu_version: `QEMU emulator version 10.2.50`", text)
        self.assertIn("qemu_repo_head: `abc123`", text)
        self.assertIn("qemu_clean_build_for_head: `true`", text)
        self.assertIn("qemu_machine_extra: `dumpdtb=/tmp/virt.dtb`", text)
        self.assertIn("qemu_extra_args: `-accel tcg,split-wx=off`", text)
        self.assertIn("qemu_heartbeat_code_bytes: `16`", text)
        self.assertIn("qemu_heartbeat_same_site_warn: `4`", text)
        self.assertIn("guest_proc_diagnostics: `true`", text)
        self.assertIn("LINX_QEMU_FAULT_TRACE_PC_LO=0x15559efe00", text)
        self.assertIn("LINX_QEMU_FAULT_TRACE_PC_HI=0x15559efe40", text)
        self.assertIn("qemu_syscall_trace:", text)
        self.assertIn("LINX_SYSCALL_TRACE_PC_LO=0x1555837f00", text)


if __name__ == "__main__":
    unittest.main()
