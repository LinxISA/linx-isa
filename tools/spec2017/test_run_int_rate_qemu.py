#!/usr/bin/env python3
from __future__ import annotations

import argparse
import inspect
import os
import tempfile
from pathlib import Path
import unittest
from unittest import mock

import run_int_rate_qemu as runner


class RunIntRateQemuTests(unittest.TestCase):
    def test_9p_append_enables_storage_init_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            append = runner._build_kernel_append("9p", "norandmaps")

        self.assertIn("norandmaps", append)
        self.assertIn("linx_storage_init=1", append)

    def test_9p_append_preserves_explicit_storage_init_override(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            append = runner._build_kernel_append("9p", "norandmaps linx_storage_init=0")

        self.assertIn("linx_storage_init=0", append)
        self.assertNotIn("linx_storage_init=1", append)

    def test_9p_force_virtio_mmio_preserves_custom_device_arg(self) -> None:
        with mock.patch.dict(os.environ, {"LINX_SPEC_9P_FORCE_VIRTIO_MMIO": "1"}, clear=True):
            append = runner._build_kernel_append(
                "9p", "virtio_mmio.device=0x100@0x30002000:2"
            )

        self.assertIn("virtio_mmio.device=0x100@0x30002000:2", append)
        self.assertNotIn("virtio_mmio.device=0x200@0x30001000:1", append)

    def test_default_qemu_prefers_build_linx_over_legacy_build(self) -> None:
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(
            os.environ, {}, clear=True
        ):
            root = Path(td)
            build_linx = root / "emulator" / "qemu" / "build-linx" / "qemu-system-linx64"
            legacy = root / "emulator" / "qemu" / "build" / "qemu-system-linx64"
            build_linx.parent.mkdir(parents=True)
            legacy.parent.mkdir(parents=True)
            build_linx.write_text("#!/bin/sh\n", encoding="utf-8")
            legacy.write_text("#!/bin/sh\n", encoding="utf-8")
            build_linx.chmod(0o755)
            legacy.chmod(0o755)

            self.assertEqual(runner._default_qemu(root), str(build_linx.resolve()))

    def test_default_qemu_honors_qemu_env_override(self) -> None:
        with tempfile.TemporaryDirectory() as td, mock.patch.dict(
            os.environ, {"QEMU": f"{td}/custom-qemu"}, clear=True
        ):
            self.assertEqual(
                runner._default_qemu(Path(td)),
                str((Path(td) / "custom-qemu").resolve()),
            )

    def test_child_exit_failure_evidence_includes_wait_status(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=0 "
                "fallback=0 status=0x0000000000000100 exited=1 code=1 "
                "signaled=0 sig=-1\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-wrapper-fail")
        self.assertIn("LINX_SPEC_FAIL child-exit", result["evidence"])
        self.assertIn("code=1", result["evidence"])
        self.assertIn("signaled=0", result["evidence"])

    def test_generated_wait_status_log_uses_single_helper_write(self) -> None:
        source = inspect.getsource(runner._build_init_for_run)

        self.assertIn("write_wait_status_log(wr, wait_errno", source)
        self.assertIn("static void write_wait_status_log", source)
        self.assertNotIn('LOG_LIT("LINX_SPEC_DBG wait wr=");', source)

    def test_terminal_failure_grace_is_opt_in(self) -> None:
        source = inspect.getsource(runner._run_qemu)

        self.assertIn("terminal_failure_grace_sec", source)
        self.assertIn("marker_now + terminal_failure_grace_sec", source)
        self.assertIn("max(1.0, terminal_failure_grace_sec)", source)

    def test_trap_delivery_trace_env_and_summary(self) -> None:
        qemu_env: dict[str, str] = {}

        runner._apply_qemu_debug_env(
            qemu_env,
            qemu_heartbeat_interval=0,
            qemu_fault_trace_regs=False,
            qemu_fault_trace_limit=1,
            qemu_trap_delivery_trace=True,
            qemu_trap_delivery_trace_limit=7,
            qemu_trap_delivery_trace_filters={
                "LINX_QEMU_TRAP_DELIVERY_TRACE_PC_LO": "0x1555825400",
                "LINX_QEMU_TRAP_DELIVERY_TRACE_PC_HI": "0x1555829900",
            },
        )

        self.assertEqual(qemu_env["LINX_QEMU_TRAP_DELIVERY_TRACE"], "1")
        self.assertEqual(qemu_env["LINX_QEMU_TRAP_DELIVERY_TRACE_LIMIT"], "7")
        self.assertEqual(
            qemu_env["LINX_QEMU_TRAP_DELIVERY_TRACE_PC_LO"],
            "0x1555825400",
        )

        summary = runner._trap_delivery_trace_summary(
            "LINX_TRAP_DELIVERY_TRACE seq=1 count=3159358776 trapnum=1 "
            "cause=0x5 argv=1 is_trap=1 bi=1 precise=0 src_acr=2 dst_acr=1 "
            "tpc=0x1555825572 tpc_next=0x1555825574 "
            "src_bpc=0x1555825566 report_bpc=0x1555825566 "
            "pending_arg0=0x155583c708 pending_cause=0x5 "
            "envpc=0x1555825572 body_tpc=0x1555825572 in_body=1 brtype=1 "
            "tgt=0x0 src_blocktype=1 src_tq0=0x0 src_tq1=0x1 "
            "src_tq2=0x2 src_tq3=0x3 src_uq0=0x4 src_uq1=0x5 "
            "src_uq2=0x6 src_uq3=0x7 src_lb=0x0:0x1:0x2 "
            "src_lc=0x3:0x4:0x5 dst_evbase=0xffffffff80000000 "
            "cstate=0x1 sp=0x3f7fff0000 ra=0x1555000000 "
            "a0=0x1 a1=0x2 a2=0x3 a3=0x4 a7=0xdd\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["count"], 1)
        self.assertEqual(summary["samples"][0]["pending_arg0"], "0x155583c708")
        self.assertEqual(summary["samples"][0]["tpc"], "0x1555825572")
        self.assertEqual(summary["samples"][0]["src_tq3"], "0x3")
        self.assertEqual(summary["samples"][0]["src_uq3"], "0x7")

    def test_linux_vm_trace_append_extra_and_summary(self) -> None:
        append = runner._linux_vm_trace_append_extra(
            "norandmaps",
            linux_vm_trace=False,
            linux_vm_trace_addr="0x155583c708",
        )

        self.assertEqual(
            append,
            "norandmaps linx_vm_trace=1 linx_vm_trace_addr=0x155583c708",
        )
        self.assertEqual(
            runner._linux_vm_trace_append_extra(
                append,
                linux_vm_trace=True,
                linux_vm_trace_addr="0x155583c708",
            ),
            append,
        )

        summary = runner._linux_vm_fault_trace_summary(
            "LINX_VM_FAULT stage=good-vma pid=0x2a comm=perlbench_r "
            "addr=0x155583c708 cause=0x5 flags=0x55 tpc=0x1555825572 "
            "bpc=0x1555825566 sp=0x3f7fff0000 vma_start=0x155583c000 "
            "vma_end=0x1555843000 vm_flags=0x75 page_prot=0x33 "
            "vm_pgoff=0x0 fault_pgoff=0x7\n"
            "LINX_VM_FAULT stage=handled pid=0x2a comm=perlbench_r "
            "addr=0x155583c708 cause=0x5 flags=0x55 tpc=0x1555825572 "
            "bpc=0x1555825566 sp=0x3f7fff0000 vma_start=0x155583c000 "
            "vma_end=0x1555843000 vm_flags=0x75 page_prot=0x33 "
            "vm_pgoff=0x0 fault_pgoff=0x7 fault=0x100\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["samples"][-1]["stage"], "handled")
        self.assertEqual(summary["samples"][-1]["pid"], 42)
        self.assertEqual(summary["samples"][-1]["addr"], "0x155583c708")
        self.assertEqual(summary["samples"][-1]["fault"], "0x100")

        interleaved = runner._linux_vm_fault_trace_summary(
            "3fefe4cLINX_VM_FAULT stage=vma-gap pid=0xd comm=perlbench_r_bas "
            "addr=0xc cause=0xc000000005000001 flags=0x255 "
            "tpc=0x1555672a00 bpc=0x15556729ea sp=0x3ffffff8d8\n"
        )
        self.assertTrue(interleaved["seen"])
        self.assertEqual(interleaved["samples"][0]["stage"], "vma-gap")
        self.assertEqual(interleaved["samples"][0]["addr"], "0xc")

    def test_child_exit_with_benchmark_internal_error_is_classified(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_SPEC_STDERR_BEGIN\n"
                "200.c: In function 'postpr_':\n"
                "200.c:63888:3: benchmark internal error: in ?, at tree-into-ssa.c:942\n"
                "The 502.gcc_r benchmark binary 'cpugcc_r' has encountered an internal error.\n"
                "LINX_SPEC_STDERR_END\n"
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=6 "
                "fallback=0 status=0x0000000000000400 exited=1 code=4 "
                "signaled=0 sig=-1\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-benchmark-internal-error")
        self.assertIn("benchmark internal error", result["evidence"])
        self.assertIn("code=4", result["evidence"])

    def test_child_exit_with_spec_mem_init_error_is_classified(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_SPEC_STDERR_BEGIN\n"
                "spec_mem_init: Error mallocing 267386880 bytes for fd 0@0x3f7feff240!\n"
                "LINX_SPEC_STDERR_END\n"
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=7 "
                "fallback=0 status=0x0000000000000100 exited=1 code=1 "
                "signaled=0 sig=-1\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-mem-init-fail")
        self.assertIn("spec_mem_init: Error mallocing", result["evidence"])
        self.assertIn("code=1", result["evidence"])

    def test_final_qemu_log_text_prefers_finished_log(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "qemu.log"
            log_path.write_bytes(
                b"LINX_SPEC_FAIL child-exit\r\n"
                b"LINX_SPEC_STDERR_BEGIN\r\n"
                b"benchmark internal error\r\n"
                b"LINX_SPEC_STDERR_END\r\n"
            )

            text = runner._final_qemu_log_text(
                log_path,
                [b"LINX_SPEC_FAIL child-exit\r\n"],
            )

        self.assertIn("LINX_SPEC_STDERR_BEGIN", text)
        self.assertIn("benchmark internal error", text)
        self.assertNotIn("\r", text)

    def test_spec_wrapper_failure_specializes_from_finished_log(self) -> None:
        qemu_info = {
            "failure_class": "spec-wrapper-fail",
            "failure_evidence": "LINX_SPEC_FAIL child-exit",
        }

        runner._specialize_spec_wrapper_failure(
            qemu_info,
            (
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=6 "
                "fallback=0 status=0x0000000000000400 exited=1 code=4 "
                "signaled=0 sig=-1\n"
                "LINX_SPEC_FAIL child-exit\r\n"
                "LINX_SPEC_STDERR_BEGIN\r\n"
                "200.c:63888:3: benchmark internal error: in ?, at tree-into-ssa.c:942\r\n"
                "LINX_SPEC_STDERR_END\r\n"
            ),
        )

        self.assertEqual(qemu_info["failure_class"], "spec-benchmark-internal-error")
        self.assertIn("benchmark internal error", qemu_info["failure_evidence"])
        self.assertIn("code=4", qemu_info["failure_evidence"])

    def test_child_sigkill_is_classified(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=7 "
                "fallback=0 status=0x0000000000000009 exited=0 code=-1 "
                "signaled=1 sig=9\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-child-sigkill")
        self.assertIn("sig=9", result["evidence"])

    def test_child_sigkill_with_oom_is_classified(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "oom_kill 0\n"
                "oom_kill 1\n"
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=7 "
                "fallback=0 status=0x0000000000000009 exited=0 code=-1 "
                "signaled=1 sig=9\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-child-sigkill-oom")
        self.assertIn("oom_kill=1", result["evidence"])

    def test_child_sigsegv_is_classified(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=7 "
                "fallback=0 status=0x000000000000000b exited=0 code=-1 "
                "signaled=1 sig=11\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-child-sigsegv")
        self.assertIn("sig=11", result["evidence"])

    def test_kernel_oops_preempts_child_sigsegv(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_DIE msg=Oops tpc=0xffffffff8012b58e "
                "bpc=0xffffffff8012b572 traparg0=0x8 trapno=0xc000000002000001\n"
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=7 "
                "fallback=0 status=0x000000000000000b exited=0 code=-1 "
                "signaled=1 sig=11\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "kernel-oops")
        self.assertIn("LINX_DIE msg=Oops", result["evidence"])
        self.assertIn("traparg0=0x8", result["evidence"])

    def test_guest_proc_diagnostics_block_dumps_memory_state(self) -> None:
        block = runner._guest_proc_diagnostics_block()

        self.assertIn("/proc/%lld/status", block)
        self.assertIn("LINX_SPEC_CHILD_STATUS_BEGIN", block)
        self.assertIn("LINX_SPEC_MEMINFO_BEGIN", block)
        self.assertIn("LINX_SPEC_VMSTAT_BEGIN", block)
        self.assertIn("LINX_SPEC_PRESSURE_MEMORY_OPEN_FAIL", block)

    def test_guest_proc_diagnostics_block_is_opt_in(self) -> None:
        self.assertEqual(runner._guest_proc_diagnostics_block_if_enabled(False), "")
        self.assertIn(
            "LINX_SPEC_PRESSURE_MEMORY_OPEN_FAIL",
            runner._guest_proc_diagnostics_block_if_enabled(True),
        )

    def test_qemu_fault_trace_regs_env_enables_trace(self) -> None:
        env: dict[str, str] = {}
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=100,
            qemu_heartbeat_regs=True,
            qemu_heartbeat_code_bytes=16,
            qemu_heartbeat_same_site_warn=4,
            qemu_frame_stats=True,
            qemu_frame_shape_hot=True,
            qemu_frame_single_reg_fast=True,
            qemu_frame_page_fast=True,
            qemu_frame_restore_host_load=True,
            qemu_frame_restore_host_verify=True,
            qemu_frame_restore_host_verify_limit=9,
            qemu_tlb_stats=True,
            qemu_tlb_inv_hot=True,
            qemu_tb_stats=True,
            template_chain=True,
            qemu_fault_trace_regs=True,
            qemu_fault_trace_limit=3,
        )

        self.assertEqual(env["LINX_HEARTBEAT_INTERVAL"], "100")
        self.assertEqual(env["LINX_QEMU_HEARTBEAT_REGS"], "1")
        self.assertEqual(env["LINX_QEMU_HEARTBEAT_CODE_BYTES"], "16")
        self.assertEqual(env["LINX_QEMU_HEARTBEAT_SAME_SITE_WARN"], "4")
        self.assertEqual(env["LINX_QEMU_FRAME_STATS"], "1")
        self.assertEqual(env["LINX_QEMU_FRAME_SHAPE_HOT"], "1")
        self.assertEqual(env["LINX_QEMU_FRAME_SINGLE_REG_FAST"], "1")
        self.assertEqual(env["LINX_QEMU_FRAME_PAGE_FAST"], "1")
        self.assertEqual(env["LINX_QEMU_FRAME_RESTORE_HOST_LOAD"], "1")
        self.assertEqual(env["LINX_QEMU_FRAME_RESTORE_HOST_VERIFY"], "1")
        self.assertEqual(env["LINX_QEMU_FRAME_RESTORE_HOST_VERIFY_LIMIT"], "9")
        self.assertEqual(env["LINX_QEMU_TLB_STATS"], "1")
        self.assertEqual(env["LINX_QEMU_TLB_INV_HOT"], "1")
        self.assertEqual(env["LINX_QEMU_TB_STATS"], "1")
        self.assertEqual(env["LINX_QEMU_TEMPLATE_CHAIN"], "1")
        self.assertEqual(env["LINX_QEMU_FAULT_TRACE"], "1")
        self.assertEqual(env["LINX_QEMU_FAULT_TRACE_REGS"], "1")
        self.assertEqual(env["LINX_QEMU_FAULT_TRACE_LIMIT"], "3")

    def test_qemu_fault_trace_filters_env_enable_trace(self) -> None:
        env: dict[str, str] = {}
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=0,
            qemu_fault_trace_regs=False,
            qemu_fault_trace_limit=7,
            qemu_fault_trace_filters={
                "LINX_QEMU_FAULT_TRACE_PC_LO": "0x15559efe00",
                "LINX_QEMU_FAULT_TRACE_PC_HI": "0x15559efe40",
                "LINX_QEMU_FAULT_TRACE_TRAPNUM": "5",
            },
        )

        self.assertEqual(env["LINX_QEMU_FAULT_TRACE"], "1")
        self.assertNotIn("LINX_QEMU_FAULT_TRACE_REGS", env)
        self.assertEqual(env["LINX_QEMU_FAULT_TRACE_LIMIT"], "7")
        self.assertEqual(env["LINX_QEMU_FAULT_TRACE_PC_LO"], "0x15559efe00")
        self.assertEqual(env["LINX_QEMU_FAULT_TRACE_PC_HI"], "0x15559efe40")
        self.assertEqual(env["LINX_QEMU_FAULT_TRACE_TRAPNUM"], "5")

    def test_child_maps_summary_matches_trap_addr(self) -> None:
        summary = runner._child_maps_summary(
            "LINX_SPEC_CHILD_MAPS_BEGIN path=/proc/13/maps\n"
            "0000001555824000-0000001555830000 r-xp 00000000 00:00 0 /spec-run/perlbench_r\n"
            "0000003f7ff00000-0000003f7ff02000 rw-p 00000000 00:00 0\n"
            "LINX_SPEC_CHILD_MAPS_END\n"
            "LINX_FAULT_TRACE mem_va=0x0000003f7ff00090 traparg0=0x0000003f7ff00090\n"
            "LINX_USER_TRAP addr=0x0000003f7ff0008c tpc=0x1555829a56\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["block_count"], 1)
        self.assertEqual(summary["trap_addr"], "0x3f7ff0008c")
        self.assertTrue(summary["trap_addr_mapped"])
        self.assertIn("3f7ff00000-0000003f7ff02000", summary["trap_addr_line"])
        self.assertEqual(summary["fault_addr"], "0x3f7ff00090")
        self.assertTrue(summary["fault_addr_mapped"])
        self.assertIn("3f7ff00000-0000003f7ff02000", summary["fault_addr_line"])

    def test_child_maps_summary_reports_unmapped_trap_addr(self) -> None:
        summary = runner._child_maps_summary(
            "LINX_SPEC_CHILD_MAPS_BEGIN\n"
            "0000001555824000-0000001555830000 r-xp 00000000 00:00 0 /spec-run/perlbench_r\n"
            "0000003f7fef0000-0000003f7fef1000 rw-p 00000000 00:00 0\n"
            "LINX_SPEC_CHILD_MAPS_END\n"
            "LINX_USER_TRAP addr=0x0000003f7ff0008c tpc=0x1555829a56\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["trap_addr"], "0x3f7ff0008c")
        self.assertFalse(summary["trap_addr_mapped"])
        self.assertEqual(summary["trap_addr_line"], "")

    def test_child_maps_summary_matches_fault_addr_when_terminal_trap_addr_is_zero(self) -> None:
        summary = runner._child_maps_summary(
            "LINX_SPEC_CHILD_MAPS_BEGIN\n"
            "0000003f7feec000-0000003f7feed000 rw-p 00000000 00:00 0\n"
            "LINX_SPEC_CHILD_MAPS_END\n"
            "LINX_FAULT_TRACE mem_va=0x0000003f7feec008 traparg0=0x0000003f7feec008\n"
            "LINX_USER_TRAP addr=0x0000000000000000 tpc=0x1555825572\n"
        )

        self.assertEqual(summary["trap_addr"], "")
        self.assertIsNone(summary["trap_addr_mapped"])
        self.assertEqual(summary["fault_addr"], "0x3f7feec008")
        self.assertTrue(summary["fault_addr_mapped"])

    def test_qemu_syscall_trace_args_auto_enable_trace(self) -> None:
        trace = runner._qemu_syscall_trace_from_args(
            argparse.Namespace(
                qemu_syscall_trace=False,
                qemu_syscall_trace_nr="56,63",
                qemu_syscall_trace_limit="64",
                qemu_syscall_trace_pc_lo="0x1555837f00",
                qemu_syscall_trace_pc_hi="0x1555838000",
                qemu_syscall_trace_regs=True,
                qemu_syscall_trace_strings=False,
            )
        )
        env: dict[str, str] = {}
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=0,
            qemu_fault_trace_regs=False,
            qemu_fault_trace_limit=0,
            qemu_syscall_trace=trace,
        )

        self.assertEqual(env["LINX_SYSCALL_TRACE"], "1")
        self.assertEqual(env["LINX_SYSCALL_TRACE_NR"], "56,63")
        self.assertEqual(env["LINX_SYSCALL_TRACE_LIMIT"], "64")
        self.assertEqual(env["LINX_SYSCALL_TRACE_PC_LO"], "0x1555837f00")
        self.assertEqual(env["LINX_SYSCALL_TRACE_PC_HI"], "0x1555838000")
        self.assertEqual(env["LINX_SYSCALL_TRACE_REGS"], "1")
        self.assertNotIn("LINX_SYSCALL_TRACE_STRINGS", env)
        self.assertIn("LINX_SYSCALL_TRACE_NR", runner._qemu_debug_env_summary(env))

    def test_qemu_mem_trace_args_auto_enable_trace(self) -> None:
        trace = runner._qemu_mem_trace_from_args(
            argparse.Namespace(
                qemu_mem_trace=False,
                qemu_mem_trace_addr="",
                qemu_mem_trace_size="",
                qemu_mem_trace_limit="32",
                qemu_mem_trace_access="loads",
                qemu_mem_trace_acr="2",
                qemu_mem_trace_pc="",
                qemu_mem_trace_pc_lo="0x15555c09d0",
                qemu_mem_trace_pc_hi="0x15555c09e8",
                qemu_mem_trace_count_lo="",
                qemu_mem_trace_count_hi="",
                qemu_mem_trace_fast="",
                qemu_mem_trace_context=True,
                qemu_mem_trace_pre=True,
                qemu_mem_trace_regs=True,
            )
        )
        env: dict[str, str] = {}
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=0,
            qemu_fault_trace_regs=False,
            qemu_fault_trace_limit=0,
            qemu_mem_trace=trace,
        )

        self.assertEqual(env["LINX_MEM_TRACE"], "1")
        self.assertEqual(env["LINX_MEM_TRACE_LIMIT"], "32")
        self.assertEqual(env["LINX_MEM_TRACE_ACCESS"], "loads")
        self.assertEqual(env["LINX_MEM_TRACE_ACR"], "2")
        self.assertEqual(env["LINX_MEM_TRACE_PC_LO"], "0x15555c09d0")
        self.assertEqual(env["LINX_MEM_TRACE_PC_HI"], "0x15555c09e8")
        self.assertEqual(env["LINX_MEM_TRACE_CONTEXT"], "1")
        self.assertEqual(env["LINX_MEM_TRACE_PRE"], "1")
        self.assertEqual(env["LINX_MEM_TRACE_REGS"], "1")
        self.assertIn("LINX_MEM_TRACE_PC_LO", runner._qemu_debug_env_summary(env))

    def test_qemu_frame_trace_args_auto_enable_trace(self) -> None:
        fret_trace = runner._qemu_fret_stk_trace_from_args(
            argparse.Namespace(
                qemu_fret_stk_trace=False,
                qemu_fret_stk_trace_pc="",
                qemu_fret_stk_trace_pc_lo="0x1555828d20",
                qemu_fret_stk_trace_pc_hi="0x1555828d40",
                qemu_fret_stk_trace_count_lo="",
                qemu_fret_stk_trace_count_hi="",
                qemu_fret_stk_trace_ra="0",
                qemu_fret_stk_trace_limit="64",
                qemu_fret_stk_trace_dump_words="16",
                qemu_fret_stk_trace_regs=True,
            )
        )
        fentry_trace = runner._qemu_fentry_trace_from_args(
            argparse.Namespace(
                qemu_fentry_trace=False,
                qemu_fentry_trace_pc="0x1555828c10",
                qemu_fentry_trace_pc_lo="",
                qemu_fentry_trace_pc_hi="",
                qemu_fentry_trace_count_lo="",
                qemu_fentry_trace_count_hi="",
                qemu_fentry_trace_ra="0x1555828d20",
                qemu_fentry_trace_sp="",
                qemu_fentry_trace_new_sp="",
                qemu_fentry_trace_limit="8",
                qemu_fentry_trace_dump_words="4",
                qemu_fentry_trace_regs=True,
            )
        )
        env: dict[str, str] = {}
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=0,
            qemu_fault_trace_regs=False,
            qemu_fault_trace_limit=0,
            qemu_fret_stk_trace=fret_trace,
            qemu_fentry_trace=fentry_trace,
        )

        self.assertEqual(env["LINX_QEMU_FRET_STK_TRACE"], "1")
        self.assertEqual(env["LINX_QEMU_FRET_STK_TRACE_PC_LO"], "0x1555828d20")
        self.assertEqual(env["LINX_QEMU_FRET_STK_TRACE_PC_HI"], "0x1555828d40")
        self.assertEqual(env["LINX_QEMU_FRET_STK_TRACE_RA"], "0")
        self.assertEqual(env["LINX_QEMU_FRET_STK_TRACE_LIMIT"], "64")
        self.assertEqual(env["LINX_QEMU_FRET_STK_TRACE_DUMP_WORDS"], "16")
        self.assertEqual(env["LINX_QEMU_FRET_STK_TRACE_REGS"], "1")
        self.assertEqual(env["LINX_QEMU_FENTRY_TRACE"], "1")
        self.assertEqual(env["LINX_QEMU_FENTRY_TRACE_PC"], "0x1555828c10")
        self.assertEqual(env["LINX_QEMU_FENTRY_TRACE_RA"], "0x1555828d20")
        self.assertEqual(env["LINX_QEMU_FENTRY_TRACE_LIMIT"], "8")
        self.assertEqual(env["LINX_QEMU_FENTRY_TRACE_DUMP_WORDS"], "4")
        self.assertEqual(env["LINX_QEMU_FENTRY_TRACE_REGS"], "1")
        self.assertIn("LINX_QEMU_FRET_STK_TRACE_RA", runner._qemu_debug_env_summary(env))
        self.assertIn("LINX_QEMU_FENTRY_TRACE_PC", runner._qemu_debug_env_summary(env))

    def test_qemu_frame_and_syscall_trace_summaries(self) -> None:
        text = (
            "LINX_FENTRY_TRACE count=3170704551 pc=0x1555837f18 "
            "next_pc=0x1555837f1c old_sp=0x3ffffff430 new_sp=0x3ffffff3f0 "
            "stacksize=64 callframe=0 begin=ra end=s5 save_count=7 "
            "incoming_ra=0x1555837f56 envpc=0x1555837f18 bpc=0x1555837f18 "
            "tpc=0x0 cstate=0x12 acr=2 mmu=1 brtype=1 tgt=0x0\n"
            "LINX_SYSCALL_TRACE nr=56 src_acr=2 dst_acr=1 count=3170704566 "
            "bpc=0x1555837f1c tpc=0x1555837f38 pc_next=0x1555837f3c "
            "a0=0xffffffffffffff9c a1=0x3fefeff180 a2=0x8000 a3=0x0 "
            "a4=0x0 a5=0x0 sp=0x3ffffff3f0 ra=0x1555837f56 cstate=0x12\n"
            "LINX_FRET_STK_TRACE count=3170709898 pc=0x1555837f46 "
            "next_pc=0x1555837f4a old_sp=0x3ffffff3f0 new_sp=0x3ffffff430 "
            "stacksize=64 callframe=0 restore_base=0 begin=ra end=s5 "
            "restore_count=7 incoming_ra=0x1555837f56 restored_ra=0x1555837f56 "
            "envpc=0x1555837f46 bpc=0x1555837f46 tpc=0x0 cstate=0x12 "
            "brtype=1 tgt=0x0\n"
        )

        fentry = runner._fentry_trace_summary(text)
        syscall = runner._syscall_trace_summary(text)
        fret = runner._fret_stk_trace_summary(text)

        self.assertTrue(fentry["seen"])
        self.assertEqual(fentry["count"], 1)
        self.assertEqual(fentry["samples"][0]["pc"], "0x1555837f18")
        self.assertEqual(fentry["samples"][0]["stacksize"], 64)
        self.assertTrue(syscall["seen"])
        self.assertEqual(syscall["samples"][0]["nr"], 56)
        self.assertEqual(syscall["samples"][0]["bpc"], "0x1555837f1c")
        self.assertTrue(fret["seen"])
        self.assertEqual(fret["samples"][0]["restored_ra"], "0x1555837f56")
        self.assertEqual(fret["samples"][0]["new_sp"], "0x3ffffff430")

    def test_qemu_acre_trace_env_and_summary(self) -> None:
        trace = runner._qemu_acre_trace_from_args(
            argparse.Namespace(
                qemu_acre_trace=False,
                qemu_acre_trace_pc="",
                qemu_acre_trace_pc_lo="0x1555837f18",
                qemu_acre_trace_pc_hi="0x1555837f48",
                qemu_acre_trace_bpc="",
                qemu_acre_trace_bpc_lo="",
                qemu_acre_trace_bpc_hi="",
                qemu_acre_trace_count_lo="3317000000",
                qemu_acre_trace_count_hi="3318000000",
                qemu_acre_trace_target="2",
                qemu_acre_trace_rra="1",
                qemu_acre_trace_trapnum="16",
                qemu_acre_trace_limit="8",
                qemu_acre_trace_code_bytes="16",
                qemu_acre_trace_regs=True,
            )
        )
        env: dict[str, str] = {}
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=0,
            qemu_fault_trace_regs=False,
            qemu_fault_trace_limit=0,
            qemu_acre_trace=trace,
        )

        self.assertEqual(env["LINX_QEMU_ACRE_TRACE"], "1")
        self.assertEqual(env["LINX_QEMU_ACRE_TRACE_PC_LO"], "0x1555837f18")
        self.assertEqual(env["LINX_QEMU_ACRE_TRACE_COUNT_LO"], "3317000000")
        self.assertEqual(env["LINX_QEMU_ACRE_TRACE_TARGET"], "2")
        self.assertEqual(env["LINX_QEMU_ACRE_TRACE_RRA"], "1")
        self.assertEqual(env["LINX_QEMU_ACRE_TRACE_TRAPNUM"], "16")
        self.assertEqual(env["LINX_QEMU_ACRE_TRACE_REGS"], "1")
        self.assertIn("LINX_QEMU_ACRE_TRACE_PC_LO", runner._qemu_debug_env_summary(env))

        summary = runner._acre_trace_summary(
            "LINX_ACRE_TRACE phase=staged count=3317420000 mgr=1 target=2 "
            "rra=1 bi=1 trapno=0x110 trapnum=16 resume=0x1555837f3c "
            "resume_bpc=0x1555837f1c saved_tq0=0x155557eb10 "
            "saved_tq1=0x1555841468 saved_uq0=0x2e saved_uq1=0x0 "
            "ebarg_tq0=0x155557eb10 ebarg_uq0=0x2e "
            "tq0=0x155557eb10 uq0=0x2e\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["count"], 1)
        self.assertEqual(summary["samples"][0]["phase"], "staged")
        self.assertEqual(summary["samples"][0]["target"], 2)
        self.assertEqual(summary["samples"][0]["saved_tq0"], "0x155557eb10")
        self.assertEqual(summary["samples"][0]["uq0"], "0x2e")

    def test_qemu_queue_trace_env_and_summary(self) -> None:
        trace = runner._qemu_queue_trace_from_args(
            argparse.Namespace(
                qemu_queue_trace=False,
                qemu_queue_trace_pc="",
                qemu_queue_trace_pc_lo="0x155582997c",
                qemu_queue_trace_pc_hi="0x155582998e",
                qemu_queue_trace_bpc="0x155582997c",
                qemu_queue_trace_bpc_lo="",
                qemu_queue_trace_bpc_hi="",
                qemu_queue_trace_count_lo="3282094328",
                qemu_queue_trace_count_hi="3282128183",
                qemu_queue_trace_limit="16",
                qemu_queue_trace_all=True,
            )
        )
        env: dict[str, str] = {}
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=0,
            qemu_fault_trace_regs=False,
            qemu_fault_trace_limit=0,
            qemu_queue_trace=trace,
        )

        self.assertEqual(env["LINX_QEMU_QUEUE_TRACE"], "1")
        self.assertEqual(env["LINX_QEMU_QUEUE_TRACE_PC_LO"], "0x155582997c")
        self.assertEqual(env["LINX_QEMU_QUEUE_TRACE_BPC"], "0x155582997c")
        self.assertEqual(env["LINX_QEMU_QUEUE_TRACE_COUNT_LO"], "3282094328")
        self.assertEqual(env["LINX_QEMU_QUEUE_TRACE_ALL"], "1")
        self.assertIn("LINX_QEMU_QUEUE_TRACE_PC_LO", runner._qemu_debug_env_summary(env))

        summary = runner._queue_trace_summary(
            "LINX_QUEUE_TRACE seq=1 count=3282094328 pc=0x155582998e "
            "bpc=0x155582997c tpc=0x155582998e acr=2 in_body=0 "
            "blocktype=0 brtype=1 call_ra_set=0 call_setret_pending=0 "
            "tq0=0x6 tq1=0x7 tq2=0x15555b5000 tq3=0x0 "
            "uq0=0x15555b5594 uq1=0x0 uq2=0x0 uq3=0x0\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["count"], 1)
        self.assertEqual(summary["samples"][0]["seq"], 1)
        self.assertEqual(summary["samples"][0]["pc"], "0x155582998e")
        self.assertEqual(summary["samples"][0]["tq2"], "0x15555b5000")
        self.assertEqual(summary["samples"][0]["uq0"], "0x15555b5594")

    def test_pc_watch_summary_captures_ring_fields(self) -> None:
        text = (
            "linx_pc_watch: pc=0x15555c09e6 hit=4 printed=4 "
            "count=3317352495 sp=0x3ffffff5f0 a0=0x3fefdfd3c0 "
            "a1=0x3fefe32a9a a2=0xb ra=0x15555c09c0 "
            "tq0=0x155557eb10 tq1=0x1555841468 uq0=0x2e uq1=0x0\n"
            "LINX_PC_WATCH_RING reason=fault fault_pc=0x15555c09e6 "
            "fault_count=3317352495 entries=1\n"
            "LINX_PC_WATCH_RING_ENTRY idx=0 age=0 watch=6 "
            "pc=0x15555c09e6 hit=4 printed=4 count=3317352495 "
            "envpc=0x15555c09e6 bpc=0x15555c09d4 tpc=0x0 acr=2 "
            "cstate=0x12 tq0=0x155557eb10 tq1=0x1555841468 "
            "uq0=0x2e uq1=0x0\n"
        )

        summary = runner._pc_watch_summary(text)

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["line_count"], 3)
        self.assertIn("pc=0x15555c09e6", summary["last"])
        self.assertTrue(summary["ring_seen"])
        self.assertEqual(summary["ring_entry_count"], 1)
        self.assertEqual(summary["last_ring_fields"]["fault_count"], 3317352495)
        self.assertEqual(
            summary["last_ring_entry_fields"]["tq0"],
            "0x155557eb10",
        )

    def test_qemu_debug_env_summary_is_sanitized(self) -> None:
        env: dict[str, str] = {
            "PATH": "/bin",
            "LINX_CALL_TRACE_RING": "1",
            "LINX_CALL_TRACE_RING_SIZE": "128",
            "LINX_SYSROOT": "/tmp/sysroot",
        }
        runner._apply_qemu_debug_env(
            env,
            qemu_heartbeat_interval=1000,
            qemu_fault_trace_regs=True,
            qemu_fault_trace_limit=3,
            qemu_pc_watch={
                "LINX_DEBUG_PC_WATCH": "0x1555827c8c",
                "LINX_DEBUG_PC_WATCH_RING": "1",
            },
        )

        self.assertEqual(
            runner._qemu_debug_env_summary(env),
            {
                "LINX_DEBUG_PC_WATCH": "0x1555827c8c",
                "LINX_DEBUG_PC_WATCH_RING": "1",
                "LINX_HEARTBEAT_INTERVAL": "1000",
                "LINX_CALL_TRACE_RING": "1",
                "LINX_CALL_TRACE_RING_SIZE": "128",
                "LINX_QEMU_FAULT_TRACE": "1",
                "LINX_QEMU_FAULT_TRACE_LIMIT": "3",
                "LINX_QEMU_FAULT_TRACE_REGS": "1",
            },
        )

    def test_pc_watch_call_ring_dump_enables_call_trace_ring(self) -> None:
        watch = runner._qemu_pc_watch_from_args(
            argparse.Namespace(
                qemu_pc_watch_dump_call_ring=True,
                qemu_call_trace_ring=False,
                qemu_call_trace_ring_size="128",
            )
        )

        self.assertEqual(watch["LINX_DEBUG_PC_WATCH_DUMP_CALL_RING"], "1")
        self.assertEqual(watch["LINX_CALL_TRACE_RING"], "1")
        self.assertEqual(watch["LINX_CALL_TRACE_RING_SIZE"], "128")

    def test_pc_watch_match_reg_maps_to_qemu_env(self) -> None:
        watch = runner._qemu_pc_watch_from_args(
            argparse.Namespace(
                qemu_pc_watch="0x155567e690",
                qemu_pc_watch_match_reg="tq0",
                qemu_pc_watch_match_value="0",
                qemu_pc_watch_hit_limit="1",
            )
        )

        self.assertEqual(watch["LINX_DEBUG_PC_WATCH"], "0x155567e690")
        self.assertEqual(watch["LINX_DEBUG_PC_WATCH_MATCH_REG"], "tq0")
        self.assertEqual(watch["LINX_DEBUG_PC_WATCH_MATCH_VALUE"], "0")
        self.assertEqual(watch["LINX_DEBUG_PC_WATCH_HIT_LIMIT"], "1")

    def test_heartbeat_tlb_fill_summary_includes_mmu_split(self) -> None:
        summary = runner._heartbeat_tlb_fill_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2 "
            "tlbf_total=10 tlbf_fetch=1 tlbf_load=6 tlbf_store=3 tlbf_probe=0 "
            "tlbf_ok=9 tlbf_fault=1 "
            "tlbf_user=7 tlbf_user_fetch=1 tlbf_user_load=4 tlbf_user_store=2 "
            "tlbf_kernel=2 tlbf_kernel_fetch=0 tlbf_kernel_load=1 tlbf_kernel_store=1 "
            "tlbf_other=1 "
            "tlbf_last_count=99 tlbf_last_pc=0x10 tlbf_last_bpc=0x20 "
            "tlbf_last_va=0x30 tlbf_last_pa=0x40 tlbf_last_access=1 "
            "tlbf_last_mmu=1 tlbf_last_prot=0x7 tlbf_last_cause=0x0 tlbf_last_acr=3"
        )

        self.assertEqual(summary["total"], 10)
        self.assertEqual(summary["user"], 7)
        self.assertEqual(summary["user_load"], 4)
        self.assertEqual(summary["kernel"], 2)
        self.assertEqual(summary["kernel_store"], 1)
        self.assertEqual(summary["other"], 1)
        self.assertEqual(summary["last_mmu"], 1)

    def test_heartbeat_summary_preserves_recent_site_window(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_HEARTBEAT count=100 pc=0x10 bpc=0x10 tpc=0x14 "
                "progress=first same_site=0\n"
                "LINX_HEARTBEAT count=200 pc=0x20 bpc=0x20 tpc=0x24 "
                "progress=site-change same_site=0\n"
                "LINX_HEARTBEAT count=300 pc=0x20 bpc=0x20 tpc=0x24 "
                "progress=same-site same_site=1\n"
            ),
            timed_out=True,
            stalled=False,
            panic_seen=False,
            fail_marker=False,
        )

        self.assertEqual(result["class"], "live-timeout")
        self.assertTrue(result["heartbeat_running"])
        self.assertTrue(result["heartbeat_site_progress"])
        self.assertEqual(result["heartbeat_recent_unique_sites"], 2)
        self.assertEqual(result["heartbeat_recent_count_delta"], 200)
        self.assertEqual(result["heartbeat_recent_sites"][-1]["count"], 300)
        self.assertEqual(result["heartbeat_recent_sites"][-1]["bpc"], "0x20")
        self.assertEqual(result["heartbeat_recent_sites"][-1]["progress"], "same-site")
        self.assertEqual(result["heartbeat_recent_sites"][-1]["same_site"], 1)

    def test_heartbeat_mmu_cache_summary_parses_cache_counts(self) -> None:
        summary = runner._heartbeat_mmu_cache_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2 "
            "mmuc_hit=11 mmuc_miss=22 mmuc_fill=33 "
            "mmuc_flush=4 mmuc_flush_page=5"
        )

        self.assertEqual(summary["hit"], 11)
        self.assertEqual(summary["miss"], 22)
        self.assertEqual(summary["fill"], 33)
        self.assertEqual(summary["flush"], 4)
        self.assertEqual(summary["flush_page"], 5)

    def test_heartbeat_frame_stats_summary_parses_template_counts(self) -> None:
        summary = runner._heartbeat_frame_stats_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2 "
            "fr_fentry=11 fr_save_probe=22 fr_save_slot=21 "
            "fr_save_host=19 fr_save_fallback=2 fr_fexit=3 "
            "fr_fret_stk=5 fr_fret_ra=7 fr_restore_slot=13 "
            "fr_restore_host=12 fr_restore_fallback=1 "
            "fr_restore_verify=15 fr_restore_mismatch=6 "
            "fr_ret_fast=17 fr_ret_check=4 "
            "fr_single_fast_fentry=8 fr_single_fast_fret_stk=9 "
            "fr_page_fast_fentry=10 fr_page_fast_restore=12"
        )

        self.assertEqual(summary["fentry"], 11)
        self.assertEqual(summary["save_probe"], 22)
        self.assertEqual(summary["save_slot"], 21)
        self.assertEqual(summary["save_host"], 19)
        self.assertEqual(summary["save_fallback"], 2)
        self.assertEqual(summary["fexit"], 3)
        self.assertEqual(summary["fret_stk"], 5)
        self.assertEqual(summary["fret_ra"], 7)
        self.assertEqual(summary["restore_slot"], 13)
        self.assertEqual(summary["restore_host"], 12)
        self.assertEqual(summary["restore_fallback"], 1)
        self.assertEqual(summary["restore_verify"], 15)
        self.assertEqual(summary["restore_mismatch"], 6)
        self.assertEqual(summary["ret_fast"], 17)
        self.assertEqual(summary["ret_check"], 4)
        self.assertEqual(summary["single_fast_fentry"], 8)
        self.assertEqual(summary["single_fast_fret_stk"], 9)
        self.assertEqual(summary["page_fast_fentry"], 10)
        self.assertEqual(summary["page_fast_restore"], 12)

    def test_frame_shape_hot_summary_parses_top_shapes(self) -> None:
        summary = runner._frame_shape_hot_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2\n"
            "LINX_FRAME_SHAPE_HOT count=100 evictions=2 slots=16 "
            "top0_count=80 top0_delta=20 top0_kind=fentry top0_kindid=0 "
            "top0_begin=10 top0_end=13 top0_stack=64 top0_regs=4 "
            "top0_frame_slots=320 "
            "top1_count=40 top1_delta=9 top1_kind=fret_stk top1_kindid=3 "
            "top1_begin=10 top1_end=13 top1_stack=64 top1_regs=4 "
            "top1_frame_slots=160\n"
            "LINX_FRAME_SHAPE_HOT count=200 evictions=2 slots=16 "
            "top0_count=95 top0_delta=15 top0_kind=fentry top0_kindid=0 "
            "top0_begin=10 top0_end=13 top0_stack=64 top0_regs=4 "
            "top0_frame_slots=380 "
            "top1_count=60 top1_delta=20 top1_kind=fret_stk top1_kindid=3 "
            "top1_begin=10 top1_end=13 top1_stack=64 top1_regs=4 "
            "top1_frame_slots=240\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["line_count"], 2)
        self.assertEqual(summary["heartbeat_count"], 200)
        self.assertEqual(summary["evictions"], 2)
        self.assertEqual(summary["top0_count"], 95)
        self.assertEqual(summary["top0_delta"], 15)
        self.assertEqual(summary["top0_kind"], "fentry")
        self.assertEqual(summary["top0_begin"], 10)
        self.assertEqual(summary["top0_end"], 13)
        self.assertEqual(summary["top0_stack"], 64)
        self.assertEqual(summary["top0_regs"], 4)
        self.assertEqual(summary["top1_kind"], "fret_stk")
        self.assertEqual(summary["max_delta"], 20)
        self.assertEqual(summary["max_delta_heartbeat_count"], 100)
        self.assertEqual(summary["max_delta_top0_kind"], "fentry")
        self.assertEqual(summary["max_delta_top0_frame_slots"], 320)

    def test_heartbeat_tlb_invalidation_summary_parses_counts(self) -> None:
        summary = runner._heartbeat_tlb_invalidation_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2 "
            "tlbi_iall=9 tlbi_ia=1 tlbi_iv=3849672 tlbi_iav=2 "
            "tlbi_last_count=19983095448 "
            "tlbi_last_pc=0xffffffff800db2b6 "
            "tlbi_last_bpc=0xffffffff800db2ac "
            "tlbi_last_operand=0x3ffffe2000 tlbi_last_acr=1"
        )

        self.assertEqual(summary["iall"], 9)
        self.assertEqual(summary["ia"], 1)
        self.assertEqual(summary["iv"], 3849672)
        self.assertEqual(summary["iav"], 2)
        self.assertEqual(summary["last_count"], 19983095448)
        self.assertEqual(summary["last_pc"], "0xffffffff800db2b6")
        self.assertEqual(summary["last_bpc"], "0xffffffff800db2ac")
        self.assertEqual(summary["last_operand"], "0x3ffffe2000")
        self.assertEqual(summary["last_acr"], 1)

    def test_heartbeat_tb_stats_summary_parses_tcg_counts(self) -> None:
        summary = runner._heartbeat_tb_stats_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2 "
            "tbs_exec=1000 tbs_lookup=900 tbs_jmp_hit=700 "
            "tbs_hash_hit=150 tbs_miss=50 tbs_gen=45 "
            "tbs_flush=2 tbs_phys_inv=3 "
            "tbs_code_used=4096 tbs_code_size=65536"
        )

        self.assertEqual(summary["exec"], 1000)
        self.assertEqual(summary["lookup"], 900)
        self.assertEqual(summary["jmp_hit"], 700)
        self.assertEqual(summary["hash_hit"], 150)
        self.assertEqual(summary["miss"], 50)
        self.assertEqual(summary["gen"], 45)
        self.assertEqual(summary["flush"], 2)
        self.assertEqual(summary["phys_inv"], 3)
        self.assertEqual(summary["code_used"], 4096)
        self.assertEqual(summary["code_size"], 65536)

    def test_pc_watch_summary_keeps_structured_ring_memory_fields(self) -> None:
        summary = runner._pc_watch_summary(
            "linx_pc_watch: pc=0x1555837f2e hit=8 printed=8 count=3185030925 "
            "sp=0x3fffffb690 bpc=0x1555837f1c\n"
            "LINX_PC_WATCH_RING reason=fault fault_pc=0x1555825572 "
            "fault_count=4181468642 entries=64\n"
            "LINX_PC_WATCH_RING_ENTRY idx=63 age=0 watch=2 "
            "pc=0x1555837f36 hit=876 printed=8 count=4181458218 "
            "bpc=0x1555837f1c sp=0x3fffffd3e0 a0=0x3 "
            "mem_src=sp mem_kind=0 mem_index=1 mem_offset=0xd60 "
            "mem_base=0x3fffffd3e0 mem_addr=0x3fffffe140 "
            "mem_ok=1 mem_value=0x0\n"
        )

        self.assertTrue(summary["seen"])
        self.assertTrue(summary["ring_seen"])
        self.assertEqual(summary["ring_entry_count"], 1)
        self.assertEqual(summary["last_ring_fields"]["fault_pc"], "0x1555825572")
        self.assertEqual(summary["last_ring_fields"]["fault_count"], 4181468642)
        last_entry = summary["last_ring_entry_fields"]
        self.assertEqual(last_entry["pc"], "0x1555837f36")
        self.assertEqual(last_entry["hit"], 876)
        self.assertEqual(last_entry["mem_src"], "sp")
        self.assertEqual(last_entry["mem_addr"], "0x3fffffe140")
        self.assertEqual(last_entry["mem_ok"], 1)
        self.assertEqual(last_entry["mem_value"], "0x0")

    def test_pc_watch_summary_keeps_call_trace_ring_fields(self) -> None:
        summary = runner._pc_watch_summary(
            "LINX_CALL_TRACE_RING reason=pc_watch fault_pc=0x1555837f3c "
            "fault_count=3340028859 entries=2\n"
            "LINX_CALL_TRACE_RING_ENTRY idx=0 age=1 event=call_commit "
            "pc=0x155583b6f6 target=0x1555837f4a extra1=0x1555837f4a "
            "count=3340028844 a0=0x40 a1=0x1 a2=0x3fefec9220\n"
            "LINX_CALL_TRACE_RING_ENTRY idx=1 age=0 event=fentry "
            "pc=0x1555837f18 count=3340028849 a0=0x40\n"
        )

        self.assertTrue(summary["seen"])
        self.assertTrue(summary["call_trace_ring_seen"])
        self.assertEqual(summary["call_trace_ring_count"], 1)
        self.assertEqual(summary["call_trace_ring_entry_count"], 2)
        self.assertEqual(
            summary["last_call_trace_ring_fields"]["fault_pc"], "0x1555837f3c"
        )
        self.assertEqual(
            summary["last_call_trace_ring_fields"]["fault_count"], 3340028859
        )
        last_entry = summary["last_call_trace_ring_entry_fields"]
        self.assertEqual(last_entry["idx"], 1)
        self.assertEqual(last_entry["event"], "fentry")
        self.assertEqual(last_entry["pc"], "0x1555837f18")
        self.assertEqual(last_entry["count"], 3340028849)

    def test_fault_trace_summary_keeps_recent_fault_fields(self) -> None:
        summary = runner._fault_trace_summary(
            "LINX_FAULT_TRACE count=3159403588 trapnum=1 src_acr=2 dst_acr=1 "
            "bi=1 precise=0 tpc=0x1555825572 tpc_next=0x1555825574 "
            "src_bpc=0x1555825566 report_bpc=0x1555825566 "
            "traparg0=0x155583c708 mem_va=0x155583c708 cause=0x5 "
            "store_ok=0 store_prot=0x0 store_cause=0x5 "
            "legacy_store=1:0:type0:4:0x868c1e0:0x0:0x0:0x0:0x0:0x5\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["count"], 1)
        sample = summary["samples"][0]
        self.assertEqual(sample["count"], 3159403588)
        self.assertEqual(sample["trapnum"], 1)
        self.assertEqual(sample["src_acr"], 2)
        self.assertEqual(sample["dst_acr"], 1)
        self.assertEqual(sample["bi"], 1)
        self.assertEqual(sample["precise"], 0)
        self.assertEqual(sample["tpc"], "0x1555825572")
        self.assertEqual(sample["report_bpc"], "0x1555825566")
        self.assertEqual(sample["traparg0"], "0x155583c708")
        self.assertEqual(sample["mem_va"], "0x155583c708")
        self.assertEqual(sample["store_ok"], 0)
        self.assertEqual(sample["store_cause"], "0x5")
        self.assertIn("type0", sample["legacy_store"])

    def test_fault_trace_summary_handles_serial_line_interleaving(self) -> None:
        text = (
            "3fefe7c000-3fefe7e000 rwLINX_FAULT_TRACE count=3347319869 "
            "trapnum=1 src_acr=2 dst_acr=1 bi=1 precise=0 "
            "tpc=0x1555672a00 report_bpc=0x15556729ea "
            "traparg0=0xc mem_va=0xc cause=0x5 store_ok=0 "
            "store_cause=0x5\n"
        )

        summary = runner._fault_trace_summary(text)

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["count"], 1)
        self.assertTrue(summary["last"].startswith("LINX_FAULT_TRACE "))
        sample = summary["samples"][0]
        self.assertEqual(sample["count"], 3347319869)
        self.assertEqual(sample["traparg0"], "0xc")
        self.assertEqual(sample["mem_va"], "0xc")
        self.assertEqual(sample["tpc"], "0x1555672a00")

    def test_mem_trace_summary_keeps_recent_queue_fields(self) -> None:
        summary = runner._mem_trace_summary(
            "LINX_MEM_TRACE access=store pc=0x1555672a00 addr=0x3fefe66724 "
            "size=4 value=0x4000000b count=3347503003 bpc=0x15556729ea "
            "tpc=0x0 envpc=0x15556729ea acr=2 cstate=0x12 "
            "tq0=0xfffffffffffbffff tq1=0x3fefe66718 tq2=0x0 tq3=0x0 "
            "uq0=0x4004000b uq1=0x0 uq2=0x0 uq3=0x0 "
            "ra=0x15556727ce sp=0x3ffffff8d8 a0=0x4000000b "
            "a1=0x3fefe55a88 a2=0x602\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["count"], 1)
        sample = summary["samples"][0]
        self.assertEqual(sample["access"], "store")
        self.assertEqual(sample["pc"], "0x1555672a00")
        self.assertEqual(sample["addr"], "0x3fefe66724")
        self.assertEqual(sample["size"], 4)
        self.assertEqual(sample["value"], "0x4000000b")
        self.assertEqual(sample["count"], 3347503003)
        self.assertEqual(sample["tq1"], "0x3fefe66718")
        self.assertEqual(sample["uq0"], "0x4004000b")
        self.assertEqual(sample["a0"], "0x4000000b")

    def test_tlb_fill_hot_summary_parses_top_slots(self) -> None:
        summary = runner._tlb_fill_hot_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2\n"
            "LINX_TLB_FILL_HOT count=100 evictions=7 inserts=19 "
            "last_hits=11 slot_hits=5 slots=16 "
            "top0_count=123 top0_page=0x3f7fa8d000 "
            "top0_last_va=0x3f7fa8d010 top0_last_pa=0x8d010 "
            "top0_access=1 top0_mmu=1 top0_probe=0 "
            "top0_prot=0x7 top0_cause=0x0 top0_acr=3 "
            "top0_pc=0x155555aa00 top0_bpc=0x155555aa02 "
            "top1_count=9 top1_page=0x1555550000 "
            "top1_last_va=0x1555550010 top1_last_pa=0x10010 "
            "top1_access=0 top1_mmu=1 top1_probe=0 "
            "top1_prot=0x5 top1_cause=0x0 top1_acr=3 "
            "top1_pc=0x155555bb00 top1_bpc=0x155555bb02\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["line_count"], 1)
        self.assertEqual(summary["heartbeat_count"], 100)
        self.assertEqual(summary["evictions"], 7)
        self.assertEqual(summary["inserts"], 19)
        self.assertEqual(summary["last_hits"], 11)
        self.assertEqual(summary["slot_hits"], 5)
        self.assertEqual(summary["top0_count"], 123)
        self.assertEqual(summary["top0_page"], "0x3f7fa8d000")
        self.assertEqual(summary["top0_access"], 1)
        self.assertEqual(summary["top0_mmu"], 1)
        self.assertEqual(summary["top1_count"], 9)
        self.assertEqual(summary["top1_prot"], 5)

    def test_tlb_inv_hot_summary_parses_top_slots(self) -> None:
        summary = runner._tlb_inv_hot_summary(
            "LINX_HEARTBEAT count=100 pc=0x1 bpc=0x2\n"
            "LINX_TLB_INV_HOT count=100 evictions=3 slots=16 "
            "top0_count=456 top0_delta=23 top0_op=iv top0_opid=2 "
            "top0_pc=0xffffffff800db2b6 top0_bpc=0xffffffff800db2ac "
            "top0_operand=0x3ffffe2abc top0_page=0x3ffffe2000 top0_acr=1 "
            "top1_count=12 top1_delta=4 top1_op=iav top1_opid=3 "
            "top1_pc=0xffffffff800aa100 top1_bpc=0xffffffff800aa0f0 "
            "top1_operand=0x100000001234 top1_page=0x1234 top1_acr=2\n"
            "LINX_TLB_INV_HOT count=200 evictions=3 slots=16 "
            "top0_count=500 top0_delta=0 top0_op=iall top0_opid=0 "
            "top0_pc=0xffffffff80001000 top0_bpc=0xffffffff80000ff0 "
            "top0_operand=0x0 top0_page=0x0 top0_acr=1 "
            "top1_count=12 top1_delta=0 top1_op=iav top1_opid=3 "
            "top1_pc=0xffffffff800aa100 top1_bpc=0xffffffff800aa0f0 "
            "top1_operand=0x100000001234 top1_page=0x1234 top1_acr=2\n"
        )

        self.assertTrue(summary["seen"])
        self.assertEqual(summary["line_count"], 2)
        self.assertEqual(summary["heartbeat_count"], 200)
        self.assertEqual(summary["evictions"], 3)
        self.assertEqual(summary["top0_count"], 500)
        self.assertEqual(summary["top0_delta"], 0)
        self.assertEqual(summary["top0_op"], "iall")
        self.assertEqual(summary["top0_opid"], 0)
        self.assertEqual(summary["top0_pc"], "0xffffffff80001000")
        self.assertEqual(summary["top0_acr"], 1)
        self.assertEqual(summary["top1_count"], 12)
        self.assertEqual(summary["top1_delta"], 0)
        self.assertEqual(summary["top1_op"], "iav")
        self.assertEqual(summary["top1_opid"], 3)
        self.assertEqual(summary["max_delta"], 23)
        self.assertEqual(summary["max_delta_heartbeat_count"], 100)
        self.assertEqual(summary["max_delta_top0_count"], 456)
        self.assertEqual(summary["max_delta_top0_delta"], 23)
        self.assertEqual(summary["max_delta_top0_op"], "iv")
        self.assertEqual(summary["max_delta_top0_pc"], "0xffffffff800db2b6")
        self.assertEqual(summary["max_delta_top0_page"], "0x3ffffe2000")

    def test_chdir_failure_evidence_includes_9p_errno(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_SPEC_START 525.x264_r\n"
                "LINX_SPEC_WARN 9p-mount-failed raw_rc=-71 neg_errno=71\n"
                "LINX_SPEC_FAIL chdir-rundir\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-wrapper-fail")
        self.assertIn("LINX_SPEC_FAIL chdir-rundir", result["evidence"])
        self.assertIn("neg_errno=71", result["evidence"])

    def test_pc_watch_exit_is_classified(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "LINX_HEARTBEAT count=1 pc=0x0 bpc=0x0\n"
                "linx_pc_watch: pc=0xffffffff80001574 hit=1 count=42 bpc=0xffffffff80402128\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=False,
        )

        self.assertEqual(result["class"], "pc-watch-exit")
        self.assertIn("0xffffffff80001574", result["evidence"])

    def test_pc_watch_does_not_mask_spec_child_exit(self) -> None:
        result = runner._classify_qemu_result(
            text=(
                "linx_pc_watch: pc=0x155604f424 hit=1 count=42 bpc=0x155604f414\n"
                "LINX_SPEC_DBG wait wr=13 errno=0 waitid_errno=0 method=6 "
                "fallback=0 status=0x0000000000000400 exited=1 code=4 "
                "signaled=0 sig=-1\n"
                "LINX_SPEC_FAIL child-exit\n"
            ),
            timed_out=False,
            stalled=False,
            panic_seen=False,
            fail_marker=True,
        )

        self.assertEqual(result["class"], "spec-wrapper-fail")
        self.assertIn("LINX_SPEC_FAIL child-exit", result["evidence"])
        self.assertIn("code=4", result["evidence"])

    def test_hash_mismatch_annotates_none_qemu_result(self) -> None:
        qemu_info = {"failure_class": "none", "failure_evidence": ""}
        runner._annotate_hash_mismatch(
            qemu_info,
            {
                "ok": False,
                "checks": [
                    {
                        "ok": False,
                        "output_name": "train.out",
                        "actual_hash": "0x1",
                        "expected_hash": "0x2",
                        "actual_size": 4,
                        "expected_size": 8,
                    }
                ],
            },
        )

        self.assertEqual(qemu_info["failure_class"], "hash-mismatch")
        self.assertIn("train.out", qemu_info["failure_evidence"])
        self.assertIn("0x1", qemu_info["failure_evidence"])
        self.assertIn("0x2", qemu_info["failure_evidence"])

    def test_hash_mismatch_preserves_runtime_failure_class(self) -> None:
        qemu_info = {"failure_class": "user-trap", "failure_evidence": "trap"}
        runner._annotate_hash_mismatch(qemu_info, {"ok": False, "checks": []})

        self.assertEqual(qemu_info["failure_class"], "user-trap")
        self.assertEqual(qemu_info["failure_evidence"], "trap")

    def test_strict_hash_pass_suppresses_specdiff_false_red(self) -> None:
        qemu_runs = [{"failure_class": "none", "failure_evidence": ""}]
        specdiff_info = {
            "ok": False,
            "strict_hash": True,
            "hash_checks": [{"ok": True, "output_name": "suns.out"}],
            "checks": [{"ok": False, "out": "suns.out", "returncode": 2}],
        }

        runner._annotate_specdiff_mismatch(qemu_runs, specdiff_info)

        self.assertTrue(runner._strict_hash_checks_ok(specdiff_info))
        self.assertEqual(qemu_runs[0]["failure_class"], "none")
        self.assertEqual(qemu_runs[0]["failure_evidence"], "")

    def test_hash_specdiff_result_preserves_partial_checks(self) -> None:
        checks = [{"ok": True, "output_name": "cpu2006docs.tar-4-0.out"}]

        result = runner._hash_specdiff_result(False, checks, strict_hash=True)

        self.assertFalse(result["ok"])
        self.assertTrue(result["strict_hash"])
        self.assertIs(result["checks"], checks)
        self.assertIs(result["hash_checks"], checks)

    def test_hash_marker_allows_heartbeat_interleaving(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ref = root / "ref.out"
            log = root / "qemu.log"
            ref.write_bytes(b"hash payload\n")
            ref_size, ref_hash = runner._fnv1a32(ref)
            ref_size_text = str(ref_size)
            log.write_text(
                f"LINX_SPEC_HASH rand.11.out {ref_size_text[:-1]}"
                "LINX_HEARTBEAT count=509000003 pc=0xffffffff8006c06a "
                f"bpc=0xffffffff8006c040 a0=0x{ref_hash:08x}\n"
                f"{ref_size_text[-1]} 0x{ref_hash:08x}\n"
                "LINX_SPEC_PASS 999.specrand_ir\n",
                encoding="utf-8",
            )

            result = runner._verify_hash_markers(
                root,
                log,
                "999.specrand_ir",
                {"compares": [{"out": "rand.11.out", "ref": "ref.out"}]},
                root,
            )

        self.assertTrue(result["ok"])
        self.assertEqual(result["checks"][0]["actual_hash"], f"0x{ref_hash:08x}")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ref = root / "ref.out"
            log = root / "qemu.log"
            ref.write_bytes(b"hash payload\n")
            ref_size, ref_hash = runner._fnv1a32(ref)
            ref_size_text = str(ref_size)
            log.write_text(
                f"LINX_SPEC_HASH rand.11.out {ref_size_text[:-1]}"
                "LINX_HEARTBEAT count=509000003 pc=0xffffffff8006c06a "
                f"bpc=0xffffffff8006c040 a0=0x{ref_hash:08x}\n"
                f"{ref_size_text[-1]} 0x00000000\n"
                "LINX_SPEC_PASS 999.specrand_ir\n",
                encoding="utf-8",
            )

            result = runner._verify_hash_markers(
                root,
                log,
                "999.specrand_ir",
                {"compares": [{"out": "rand.11.out", "ref": "ref.out"}]},
                root,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(result["checks"][0]["actual_hash"], "0x00000000")

    def test_indexed_argv_override_targets_requested_argument(self) -> None:
        with mock.patch.dict(os.environ, {"LINX_SPEC_ARGV1_OVERRIDE": "/spec-run/test.txt"}, clear=True):
            argv = runner._apply_argv_overrides(["./bench", "test.txt"])

        self.assertEqual(argv, ["./bench", "/spec-run/test.txt"])

    def test_indexed_argv_override_leaves_unset_arguments_unchanged(self) -> None:
        with mock.patch.dict(os.environ, {"LINX_SPEC_ARGV2_OVERRIDE": "patched"}, clear=True):
            argv = runner._apply_argv_overrides(["./bench", "input", "old"])

        self.assertEqual(argv, ["./bench", "input", "patched"])

    def test_effective_run_argv_reflects_indexed_overrides(self) -> None:
        run_cfg = {"argv": ["./bench", "input", "old"]}

        with mock.patch.dict(os.environ, {"LINX_SPEC_ARGV2_OVERRIDE": "patched"}, clear=True):
            argv = runner._effective_run_argv(run_cfg)

        self.assertEqual(argv, ["./bench", "input", "patched"])
        self.assertEqual(run_cfg["argv"], ["./bench", "input", "old"])

    def test_gcc_run_verifies_generated_assembly_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bench_root = Path(td)
            control = bench_root / "data" / "test" / "input" / "control"
            control.parent.mkdir(parents=True)
            control.write_text("t1.c -O3 -finline-limit=50000\n", encoding="utf-8")

            runs = runner._runs_gcc(bench_root, "test", "cpugcc_r_base.mytest-m64")

        self.assertEqual(len(runs), 1)
        self.assertEqual(
            runs[0]["argv"],
            [
                "./cpugcc_r_base.mytest-m64",
                "t1.c",
                "-O3",
                "-finline-limit=50000",
                "-o",
                "t1.opts-O3_-finline-limit_50000.s",
            ],
        )
        self.assertEqual(runs[0]["stdout"], "t1.opts-O3_-finline-limit_50000.out")
        self.assertEqual(runs[0]["verify_outputs"], ["t1.opts-O3_-finline-limit_50000.s"])

    def test_perlbench_train_uses_shared_scripts_and_side_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bench_root = Path(td)
            all_input = bench_root / "data" / "all" / "input"
            train_input = bench_root / "data" / "train" / "input"
            train_output = bench_root / "data" / "train" / "output"
            all_input.mkdir(parents=True)
            train_input.mkdir(parents=True)
            train_output.mkdir(parents=True)

            (all_input / "diffmail.pl").write_text("", encoding="utf-8")
            (all_input / "splitmail.pl").write_text("", encoding="utf-8")
            (train_input / "diffmail.in").write_text("2 550 15 24 23 100\n", encoding="utf-8")
            (train_input / "splitmail.in").write_text("535 13 25 24 1091 1\n", encoding="utf-8")
            (train_input / "perfect.pl").write_text("", encoding="utf-8")
            (train_input / "perfect.in").write_text("b 3\n", encoding="utf-8")
            (train_input / "scrabbl.pl").write_text("", encoding="utf-8")
            (train_input / "scrabbl.in").write_text("letters\n", encoding="utf-8")
            (train_input / "suns.pl").write_text("", encoding="utf-8")
            (train_output / "validate").write_text("", encoding="utf-8")

            runs = runner._runs_perlbench(bench_root, "train", "perlbench_r_base.mytest-m64")

        self.assertEqual([run["stdout"] for run in runs], [
            "diffmail.2.550.15.24.23.100.out",
            "perfect.b.3.out",
            "scrabbl.out",
            "splitmail.535.13.25.24.1091.1.out",
            "suns.out",
        ])
        self.assertEqual(runs[0]["argv"], [
            "./perlbench_r_base.mytest-m64",
            "-I./lib",
            "diffmail.pl",
            "2",
            "550",
            "15",
            "24",
            "23",
            "100",
        ])
        self.assertEqual(runs[3]["argv"][2], "splitmail.pl")
        self.assertEqual(runs[4]["verify_outputs"], ["suns.out", "validate"])

    def test_overlay_input_set_applies_shared_inputs_before_selected_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bench_root = Path(td) / "bench"
            dst_run = Path(td) / "run"
            all_input = bench_root / "data" / "all" / "input"
            train_input = bench_root / "data" / "train" / "input"
            all_input.mkdir(parents=True)
            train_input.mkdir(parents=True)
            dst_run.mkdir()

            (all_input / "shared.pl").write_text("all", encoding="utf-8")
            (all_input / "lib").mkdir()
            (all_input / "lib" / "helper.pm").write_text("lib", encoding="utf-8")
            (train_input / "shared.pl").write_text("train", encoding="utf-8")
            (train_input / "train.in").write_text("input", encoding="utf-8")

            runner._overlay_input_set(bench_root, dst_run, "train")

            self.assertEqual((dst_run / "shared.pl").read_text(encoding="utf-8"), "train")
            self.assertEqual((dst_run / "lib" / "helper.pm").read_text(encoding="utf-8"), "lib")
            self.assertEqual((dst_run / "train.in").read_text(encoding="utf-8"), "input")

    def test_select_run_indices_keeps_matching_compares(self) -> None:
        cfg = {
            "runs": [
                {"argv": ["./b", "a.c"], "verify_outputs": ["a.s"]},
                {"argv": ["./b", "b.c"], "verify_outputs": ["b.s"]},
                {"argv": ["./b", "c.c"], "verify_outputs": ["c.s"]},
            ],
            "compares": [
                {"out": "a.s"},
                {"out": "b.s"},
                {"out": "c.s"},
                {"out": "unrelated.s"},
            ],
        }

        selected = runner._select_run_indices(cfg, [2])

        self.assertEqual(len(selected["runs"]), 1)
        self.assertEqual(selected["runs"][0]["argv"], ["./b", "b.c"])
        self.assertEqual(selected["runs"][0]["source_run_index"], 2)
        self.assertEqual(selected["compares"], [{"out": "b.s"}])
        self.assertEqual(selected["selected_run_indices"], [2])

    def test_select_run_indices_rejects_out_of_range(self) -> None:
        cfg = {
            "runs": [{"argv": ["./b", "a.c"], "verify_outputs": ["a.s"]}],
            "compares": [{"out": "a.s"}],
        }

        with self.assertRaises(SystemExit):
            runner._select_run_indices(cfg, [2])

    def test_heartbeat_kernel_addresses_keep_recent_kernel_sites(self) -> None:
        text = "\n".join(
            [
                "LINX_HEARTBEAT count=1 pc=0x1555555000 bpc=0x1555554000 ra=0x0",
                (
                    "LINX_HEARTBEAT count=2 pc=0xffffffff803e88f6 "
                    "bpc=0xffffffff803e88b0 envpc=0xffffffff803e88aa "
                    "ra=0xffffffff800019bc tpc=0x0"
                ),
                (
                    "LINX_HEARTBEAT count=3 pc=0xffffffff803e88f6 "
                    "bpc=0xffffffff803e88b0 envpc=0xffffffff803e88aa "
                    "ra=0xffffffff800019bc tpc=0x0"
                ),
            ]
        )

        self.assertEqual(
            runner._heartbeat_kernel_addresses(text),
            [
                "0xffffffff803e88f6",
                "0xffffffff803e88b0",
                "0xffffffff803e88aa",
                "0xffffffff800019bc",
            ],
        )

    def test_tlb_inv_hot_kernel_addresses_keep_recent_sources(self) -> None:
        text = "\n".join(
            [
                (
                    "LINX_TLB_INV_HOT count=1 evictions=0 slots=16 "
                    "top0_pc=0x1555555000 top0_bpc=0x1555554000 "
                    "top1_pc=0xffffffff800d6c88 top1_bpc=0xffffffff800d6c54"
                ),
                (
                    "LINX_TLB_INV_HOT count=2 evictions=0 slots=16 "
                    "top0_pc=0xffffffff800db20c top0_bpc=0xffffffff800db202 "
                    "top1_pc=0xffffffff800d6c88 top1_bpc=0xffffffff800d6c54"
                ),
            ]
        )

        self.assertEqual(
            runner._tlb_inv_hot_kernel_addresses(text),
            [
                "0xffffffff800d6c88",
                "0xffffffff800d6c54",
                "0xffffffff800db20c",
                "0xffffffff800db202",
            ],
        )

    def test_kernel_symbols_suggest_panic_loop_from_panic_source(self) -> None:
        self.assertTrue(
            runner._kernel_symbols_suggest_panic_loop(
                [
                    {"address": "0xffffffff803e88f6", "function": "udelay", "source": "??:0"},
                    {"address": "0xffffffff800019bc", "function": ".LBB14_51", "source": "panic.c:0"},
                ]
            )
        )
        self.assertFalse(
            runner._kernel_symbols_suggest_panic_loop(
                [
                    {"address": "0xffffffff800fb6e2", "function": "kcsan_atomic_next", "source": "page_alloc.c:0"},
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()
