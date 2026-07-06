#!/usr/bin/env python3
from __future__ import annotations

import unittest
import sys
import tempfile
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_specint_fast_gate as gate


def _stack_args(**overrides: bool) -> SimpleNamespace:
    values = {
        "qemu_debug_stack": False,
        "qemu_speed_stack": False,
        "qemu_frame_stats": False,
        "qemu_frame_shape_hot": False,
        "qemu_frame_single_reg_fast": False,
        "qemu_frame_page_fast": False,
        "qemu_frame_restore_host_load": False,
        "qemu_tlb_stats": False,
        "qemu_tlb_inv_hot": False,
        "qemu_tlb_fill_stats": False,
        "qemu_tlb_fill_hot": False,
        "qemu_mmu_cache": False,
        "qemu_mmu_cache_stats": False,
        "qemu_mmu_cache_assoc2": False,
        "template_chain": False,
        "qemu_heartbeat_extended": False,
        "qemu_tb_stats": False,
        "qemu_tb_hot": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


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

    def test_out_dir_space_check_records_free_space(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            info = gate._check_out_dir_free_space(Path(td) / "nested" / "out", 0)

        self.assertGreaterEqual(info["free_bytes"], 0)
        self.assertEqual(info["min_free_gb"], 0)
        self.assertEqual(info["required_bytes"], 0)
        self.assertIn("free_human", info)

    def test_out_dir_space_check_fails_before_qemu_when_too_small(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(SystemExit, "insufficient free space"):
                gate._check_out_dir_free_space(Path(td), 1024 * 1024)

    def test_qemu_speed_stack_preset_enables_speed_features_only(self) -> None:
        args = _stack_args(qemu_speed_stack=True)

        gate._apply_qemu_stack_presets(args)

        self.assertTrue(args.qemu_frame_single_reg_fast)
        self.assertTrue(args.qemu_mmu_cache)
        self.assertTrue(args.template_chain)
        self.assertTrue(args.qemu_heartbeat_extended)
        self.assertFalse(args.qemu_frame_stats)
        self.assertFalse(args.qemu_tlb_stats)
        self.assertFalse(args.qemu_tlb_fill_stats)
        self.assertFalse(args.qemu_mmu_cache_stats)
        self.assertFalse(args.qemu_tb_stats)
        self.assertFalse(args.qemu_frame_page_fast)
        self.assertFalse(args.qemu_frame_restore_host_load)
        self.assertFalse(args.qemu_mmu_cache_assoc2)

    def test_qemu_debug_stack_preset_extends_speed_stack_with_attribution(self) -> None:
        args = _stack_args(qemu_debug_stack=True)

        gate._apply_qemu_stack_presets(args)

        self.assertTrue(args.qemu_speed_stack)
        self.assertTrue(args.qemu_frame_single_reg_fast)
        self.assertTrue(args.qemu_mmu_cache)
        self.assertTrue(args.template_chain)
        self.assertTrue(args.qemu_heartbeat_extended)
        self.assertTrue(args.qemu_frame_stats)
        self.assertTrue(args.qemu_frame_shape_hot)
        self.assertTrue(args.qemu_tlb_stats)
        self.assertTrue(args.qemu_tlb_inv_hot)
        self.assertTrue(args.qemu_tlb_fill_stats)
        self.assertTrue(args.qemu_tlb_fill_hot)
        self.assertTrue(args.qemu_mmu_cache_stats)
        self.assertTrue(args.qemu_tb_stats)
        self.assertTrue(args.qemu_tb_hot)
        self.assertFalse(args.qemu_frame_page_fast)
        self.assertFalse(args.qemu_frame_restore_host_load)
        self.assertFalse(args.qemu_mmu_cache_assoc2)

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
                    "heartbeat_tlb_fill_hot": {
                        "seen": True,
                        "top0_count": 991,
                        "top0_page": "0x3f7fa8d000",
                        "top0_access": 1,
                        "top0_mmu": 1,
                        "evictions": 4,
                    },
                }
            }
        )

        self.assertIn("tlbf=225069739/f1436090/l201417280/s22216369/p138258", text)
        self.assertIn("/u224000000/k1069739/o0", text)
        self.assertIn("tlbf-hot=991@0x3f7fa8d000/a1/m1 evict=4", text)

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
                    "qemu_speed_stack": True,
                    "qemu_debug_stack": False,
                    "fail_9p_timeout": False,
                    "qemu_mmu_cache_assoc2": True,
                    "template_chain": True,
                    "suites": [],
                },
            )

            text = path.read_text(encoding="utf-8")

        self.assertIn("qemu_version: `QEMU emulator version 10.2.50`", text)
        self.assertIn("qemu_repo_head: `abc123`", text)
        self.assertIn("qemu_clean_build_for_head: `true`", text)
        self.assertIn("qemu_machine_extra: `dumpdtb=/tmp/virt.dtb`", text)
        self.assertIn("qemu_extra_args: `-accel tcg,split-wx=off`", text)
        self.assertIn("qemu_speed_stack: `true`", text)
        self.assertIn("qemu_debug_stack: `false`", text)
        self.assertIn("qemu_mmu_cache_assoc2: `true`", text)
        self.assertIn("template_chain: `true`", text)

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
            qemu_heartbeat_extended=True,
            qemu_frame_stats=True,
            qemu_frame_shape_hot=True,
            qemu_frame_single_reg_fast=True,
            qemu_frame_page_fast=True,
            qemu_frame_restore_host_load=False,
            qemu_tlb_stats=False,
            qemu_tlb_inv_hot=False,
            qemu_tlb_fill_stats=False,
            qemu_tlb_fill_hot=False,
            qemu_mmu_cache=True,
            qemu_mmu_cache_stats=True,
            qemu_mmu_cache_assoc2=True,
            template_chain=True,
            qemu_tlb_fault_trace=True,
            qemu_tlb_fault_trace_limit=64,
            qemu_tlb_fault_trace_addr="",
            qemu_tlb_fault_trace_addr_lo="0x3f7feec000",
            qemu_tlb_fault_trace_addr_hi="0x3f7feeefff",
            qemu_tlb_fault_trace_count_lo="",
            qemu_tlb_fault_trace_count_hi="",
            qemu_tb_stats=False,
            qemu_tb_hot=False,
            no_progress_timeout=120,
            forward_memory_mb=True,
            forward_qemu_heartbeat=True,
            forward_qemu_heartbeat_regs=True,
            forward_qemu_heartbeat_code_bytes=True,
            forward_qemu_heartbeat_same_site_warn=True,
            forward_qemu_heartbeat_extended=True,
            forward_qemu_frame_stats=True,
            forward_qemu_frame_shape_hot=True,
            forward_qemu_frame_single_reg_fast=True,
            forward_qemu_frame_page_fast=True,
            forward_qemu_frame_restore_host_load=True,
            forward_qemu_tlb_stats=True,
            forward_qemu_tlb_inv_hot=True,
            forward_qemu_tlb_fill_stats=True,
            forward_qemu_tlb_fill_hot=True,
            forward_qemu_mmu_cache=True,
            forward_qemu_mmu_cache_stats=True,
            forward_qemu_mmu_cache_assoc2=True,
            forward_template_chain=True,
            forward_qemu_tlb_fault_trace=True,
            forward_qemu_tb_stats=True,
            forward_qemu_tb_hot=True,
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
        self.assertIn("--qemu-heartbeat-extended", cmd)
        self.assertIn("--qemu-frame-stats", cmd)
        self.assertIn("--qemu-frame-shape-hot", cmd)
        self.assertIn("--qemu-frame-single-reg-fast", cmd)
        self.assertIn("--qemu-frame-page-fast", cmd)
        self.assertIn("--qemu-tlb-fault-trace", cmd)
        self.assertIn("--qemu-tlb-fault-trace-limit", cmd)
        self.assertEqual(cmd[cmd.index("--qemu-tlb-fault-trace-limit") + 1], "64")
        self.assertIn("--qemu-mmu-cache", cmd)
        self.assertIn("--qemu-mmu-cache-stats", cmd)
        self.assertIn("--qemu-mmu-cache-assoc2", cmd)
        self.assertIn("--template-chain", cmd)
        self.assertIn("--qemu-tlb-fault-trace-addr-lo", cmd)
        self.assertEqual(cmd[cmd.index("--qemu-tlb-fault-trace-addr-lo") + 1], "0x3f7feec000")
        self.assertIn("--fail-9p-timeout", cmd)


if __name__ == "__main__":
    unittest.main()
