#!/usr/bin/env python3
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import run_stage_qemu_matrix as matrix


class StageQemuMatrixTests(unittest.TestCase):
    def test_template_chain_is_forwarded_to_child_env(self) -> None:
        captured_envs: list[dict[str, str]] = []

        def fake_run(cmd, **kwargs):  # type: ignore[no-untyped-def]
            env = kwargs.get("env")
            if env is None:
                return SimpleNamespace(returncode=0, stdout="")
            captured_envs.append(dict(env))
            out_dir = Path(cmd[cmd.index("--out-dir") + 1])
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "stage_b_summary.json").write_text(
                '{"ok": true, "results": {}}\n',
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=0)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec_dir = root / "spec"
            (spec_dir / "benchspec" / "CPU").mkdir(parents=True)
            (spec_dir / "bin" / "harness").mkdir(parents=True)
            (spec_dir / "bin" / "harness" / "specdiff").write_text("")
            out_dir = root / "out"

            with mock.patch.dict(os.environ, {"QEMU": "/bin/true"}), mock.patch.object(
                matrix.subprocess, "run", side_effect=fake_run
            ):
                rc = matrix.main(
                    [
                        "--spec-dir",
                        str(spec_dir),
                        "--qemu",
                        "/bin/true",
                        "--stage",
                        "b",
                        "--input-set",
                        "train",
                        "--transports",
                        "initramfs",
                        "--sysroot",
                        str(root / "sysroot"),
                        "--out-dir",
                        str(out_dir),
                        "--template-chain",
                    ]
                )

            summary = (out_dir / "qemu_matrix_summary.json").read_text()

        self.assertEqual(rc, 0)
        self.assertEqual(captured_envs[0]["LINX_QEMU_TEMPLATE_CHAIN"], "1")
        self.assertIn('"template_chain": true', summary)

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
                            "heartbeat_recent_unique_sites": 3,
                            "heartbeat_recent_count_delta": 2000000024,
                            "heartbeat_kernel_panic_loop": True,
                            "heartbeat_kernel_symbol_evidence": "heartbeat kernel symbols: 0xffffffff800019bc=.LBB14_51 panic.c:0",
                            "tlb_inv_hot_kernel_symbolized": True,
                            "tlb_inv_hot_kernel_symbol_evidence": "tlb-inv-hot kernel symbols: 0xffffffff800db20c=local_flush_tlb_page arch/linx/include/asm/tlbflush.h:23",
                            "tlb_inv_hot_kernel_symbols": [
                                {
                                    "address": "0xffffffff800db20c",
                                    "function": "local_flush_tlb_page",
                                    "source": "arch/linx/include/asm/tlbflush.h:23",
                                }
                            ],
                            "heartbeat_tlb_fill_hot": {
                                "seen": True,
                                "top0_count": 12345,
                                "top0_page": "0x3f7fa8d000",
                                "top0_access": 1,
                                "top0_mmu": 1,
                                "evictions": 17,
                            },
                            "heartbeat_frame_shape_hot": {
                                "seen": True,
                                "top0_count": 80,
                                "top0_delta": 20,
                                "top0_kind": "fentry",
                                "top0_begin": 10,
                                "top0_end": 13,
                                "top0_stack": 64,
                                "top0_regs": 4,
                                "evictions": 2,
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
        self.assertEqual(
            matrix._transport_failure_details(summary)["500.perlbench_r"][
                "heartbeat_frame_shape_hot"
            ]["top0_kind"],
            "fentry",
        )
        self.assertIn(
            "kernel-panic-loop",
            matrix._format_failure_details(
                matrix._transport_failure_details(summary)
            ),
        )
        self.assertIn(
            "recent-sites=3 count-delta=2000000024",
            matrix._format_failure_details(
                matrix._transport_failure_details(summary)
            ),
        )
        self.assertIn(
            "tlbi-hot-symbolized",
            matrix._format_failure_details(
                matrix._transport_failure_details(summary)
            ),
        )
        self.assertIn(
            "frame-hot=fentry:80/d20/r10-13/n4/s64 evict=2",
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
            "qemu_frame_single_reg_fast": True,
            "qemu_frame_page_fast": True,
            "template_chain": True,
            "qemu_frame_restore_host_verify": True,
            "qemu_frame_restore_host_verify_limit": 9,
            "qemu_fault_trace": True,
            "qemu_fault_trace_regs": True,
            "qemu_fault_trace_limit": 1,
            "qemu_fault_trace_filters": {
                "LINX_QEMU_FAULT_TRACE_PC_LO": "0x15559efe00",
                "LINX_QEMU_FAULT_TRACE_PC_HI": "0x15559efe40",
            },
            "qemu_trap_delivery_trace": True,
            "qemu_trap_delivery_trace_limit": 64,
            "qemu_trap_delivery_trace_filters": {
                "LINX_QEMU_TRAP_DELIVERY_TRACE_PC_LO": "0x1555825400",
                "LINX_QEMU_TRAP_DELIVERY_TRACE_PC_HI": "0x1555829900",
            },
            "qemu_syscall_trace": {
                "LINX_SYSCALL_TRACE": "1",
                "LINX_SYSCALL_TRACE_PC_LO": "0x1555837f00",
                "LINX_SYSCALL_TRACE_PC_HI": "0x1555838000",
            },
            "qemu_mem_trace": {
                "LINX_MEM_TRACE": "1",
                "LINX_MEM_TRACE_PC_LO": "0x15555c09d0",
                "LINX_MEM_TRACE_PC_HI": "0x15555c09e8",
                "LINX_MEM_TRACE_ACCESS": "loads",
                "LINX_MEM_TRACE_PRE": "1",
                "LINX_MEM_TRACE_REGS": "1",
            },
            "qemu_fret_stk_trace": {
                "LINX_QEMU_FRET_STK_TRACE": "1",
                "LINX_QEMU_FRET_STK_TRACE_RA": "0",
                "LINX_QEMU_FRET_STK_TRACE_LIMIT": "64",
            },
            "qemu_fentry_trace": {
                "LINX_QEMU_FENTRY_TRACE": "1",
                "LINX_QEMU_FENTRY_TRACE_PC": "0x1555828c10",
                "LINX_QEMU_FENTRY_TRACE_REGS": "1",
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
        self.assertIn("qemu_trap_delivery_trace: `true`", text)
        self.assertIn("qemu_trap_delivery_trace_limit: `64`", text)
        self.assertIn("LINX_QEMU_TRAP_DELIVERY_TRACE_PC_LO=0x1555825400", text)
        self.assertIn("qemu_heartbeat_regs: `true`", text)
        self.assertIn("qemu_version: `QEMU emulator version 10.2.50`", text)
        self.assertIn("qemu_repo_head: `abc123`", text)
        self.assertIn("qemu_clean_build_for_head: `true`", text)
        self.assertIn("qemu_machine_extra: `dumpdtb=/tmp/virt.dtb`", text)
        self.assertIn("qemu_extra_args: `-accel tcg,split-wx=off`", text)
        self.assertIn("qemu_heartbeat_code_bytes: `16`", text)
        self.assertIn("qemu_heartbeat_same_site_warn: `4`", text)
        self.assertIn("qemu_frame_single_reg_fast: `true`", text)
        self.assertIn("qemu_frame_page_fast: `true`", text)
        self.assertIn("template_chain: `true`", text)
        self.assertIn("qemu_frame_restore_host_verify: `true`", text)
        self.assertIn("qemu_frame_restore_host_verify_limit: `9`", text)
        self.assertIn("guest_proc_diagnostics: `true`", text)
        self.assertIn("LINX_QEMU_FAULT_TRACE_PC_LO=0x15559efe00", text)
        self.assertIn("LINX_QEMU_FAULT_TRACE_PC_HI=0x15559efe40", text)
        self.assertIn("qemu_syscall_trace:", text)
        self.assertIn("LINX_SYSCALL_TRACE_PC_LO=0x1555837f00", text)
        self.assertIn("qemu_mem_trace:", text)
        self.assertIn("LINX_MEM_TRACE_PC_LO=0x15555c09d0", text)
        self.assertIn("LINX_MEM_TRACE_PRE=1", text)
        self.assertIn("LINX_MEM_TRACE_REGS=1", text)
        self.assertIn("qemu_fret_stk_trace:", text)
        self.assertIn("LINX_QEMU_FRET_STK_TRACE_RA=0", text)
        self.assertIn("qemu_fentry_trace:", text)
        self.assertIn("LINX_QEMU_FENTRY_TRACE_PC=0x1555828c10", text)


if __name__ == "__main__":
    unittest.main()
