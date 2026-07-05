#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analyze_specint_qemu_progress as analyzer


class AnalyzeSpecintQemuProgressTests(unittest.TestCase):
    def _write(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_extract_gate_rows_follows_matrix_and_stage_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gate_path = root / "specint_fast_gate_summary.json"
            matrix_path = root / "train-all" / "qemu_matrix_summary.json"
            stage_path = root / "train-all" / "initramfs" / "stage_b_summary.json"

            gate = {
                "suites": [
                    {
                        "name": "train-all",
                        "input_set": "train",
                        "stage": "b",
                        "transports": ["initramfs"],
                        "benches": ["531.deepsjeng_r", "999.specrand_ir"],
                        "matrix_summary": str(matrix_path),
                        "failure_classes": {"531.deepsjeng_r": "live-timeout"},
                        "failure_details": {
                            "531.deepsjeng_r": {
                                "failure_class": "live-timeout",
                                "heartbeat_running": True,
                                "heartbeat_site_progress": True,
                                "heartbeat_last_count": 12,
                                "heartbeat_last_bpc": "0x531",
                                "heartbeat_frame_stats": {
                                    "restore_fallback": 7,
                                    "single_fast_fentry": 5,
                                    "single_fast_fret_stk": 4,
                                    "page_fast_fentry": 3,
                                    "page_fast_restore": 2,
                                },
                                "heartbeat_frame_shape_hot": {
                                    "seen": True,
                                    "top0_kind": "fentry",
                                    "top0_count": 80,
                                },
                                "heartbeat_tb_stats": {"lookup": 100, "miss": 3},
                            }
                        },
                    }
                ]
            }
            matrix = {
                "results": [
                    {
                        "transport": "initramfs",
                        "summary_json": str(stage_path),
                        "failure_classes": {"531.deepsjeng_r": "live-timeout"},
                    }
                ]
            }
            stage = {
                "stage": "b",
                "input_set": "train",
                "transport": "initramfs",
                "results": {
                    "531.deepsjeng_r": {
                        "bench": "531.deepsjeng_r",
                        "ok": False,
                        "specdiff": {"ok": False, "strict_hash": True, "hash_checks": []},
                    },
                    "999.specrand_ir": {
                        "bench": "999.specrand_ir",
                        "ok": True,
                        "specdiff": {
                            "ok": True,
                            "strict_hash": True,
                            "hash_checks": [
                                {
                                    "output_name": "rand.11.out",
                                    "actual_hash": "0x973dcfc2",
                                    "expected_hash": "0x973dcfc2",
                                    "ok": True,
                                }
                            ],
                        },
                    },
                },
            }
            self._write(gate_path, gate)
            self._write(matrix_path, matrix)
            self._write(stage_path, stage)

            rows = analyzer.extract_gate_rows(gate, gate_path)

        self.assertEqual(rows["531.deepsjeng_r"]["failure_class"], "live-timeout")
        self.assertEqual(rows["531.deepsjeng_r"]["heartbeat_last_bpc"], "0x531")
        self.assertEqual(rows["531.deepsjeng_r"]["frame_shape_hot"]["top0_kind"], "fentry")
        self.assertEqual(rows["531.deepsjeng_r"]["frame_single_fast_fentry"], 5)
        self.assertEqual(rows["531.deepsjeng_r"]["frame_single_fast_fret_stk"], 4)
        self.assertEqual(rows["531.deepsjeng_r"]["frame_page_fast_fentry"], 3)
        self.assertEqual(rows["531.deepsjeng_r"]["frame_page_fast_restore"], 2)
        self.assertEqual(rows["531.deepsjeng_r"]["tb_lookup"], 100)
        self.assertFalse(rows["531.deepsjeng_r"]["ok"])
        self.assertTrue(rows["999.specrand_ir"]["ok"])
        self.assertTrue(rows["999.specrand_ir"]["strict_hash_ok"])

    def test_build_analysis_classifies_sentinel_tlbi_9p_and_template_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gate_path = root / "specint_fast_gate_summary.json"
            profile_path = root / "profile_suite_summary.json"
            stage_path = root / "stage_b_summary.json"
            gate = {
                "profile": "train",
                "qemu": "/tmp/qemu",
                "qemu_provenance": {"qemu_repo_head": "gate-head"},
                "qemu_frame_stats": True,
                "suites": [
                    {
                        "name": "train-all",
                        "input_set": "train",
                        "stage": "b",
                        "transports": ["initramfs"],
                        "matrix_summary": str(stage_path),
                        "benches": ["505.mcf_r", "531.deepsjeng_r", "999.specrand_ir"],
                        "failure_classes": {
                            "505.mcf_r": "live-timeout",
                            "531.deepsjeng_r": "live-timeout",
                        },
                        "failure_details": {
                            "505.mcf_r": {
                                "failure_class": "live-timeout",
                                "heartbeat_running": True,
                                "heartbeat_site_progress": True,
                                "heartbeat_last_count": 50,
                                "heartbeat_last_bpc": "0x505",
                                "heartbeat_last_progress": "site-change",
                                "heartbeat_recent_unique_sites": 4,
                                "heartbeat_recent_count_delta": 3000000000,
                                "heartbeat_recent_sites": [
                                    {
                                        "count": 20,
                                        "pc": "0x5010",
                                        "bpc": "0x5000",
                                        "tpc": "0x5014",
                                        "progress": "first",
                                        "same_site": 0,
                                    },
                                    {
                                        "count": 50,
                                        "pc": "0x5050",
                                        "bpc": "0x505",
                                        "tpc": "0x5054",
                                        "progress": "site-change",
                                        "same_site": 0,
                                    },
                                ],
                                "tlb_inv_hot_kernel_symbolized": True,
                                "tlb_inv_hot_kernel_symbol_evidence": "tlb-inv-hot kernel symbols: 0xffffffff800db20c=local_flush_tlb_page arch/linx/include/asm/tlbflush.h:23",
                                "tlb_inv_hot_kernel_symbols": [
                                    {
                                        "address": "0xffffffff800db20c",
                                        "function": "local_flush_tlb_page",
                                        "source": "arch/linx/include/asm/tlbflush.h:23",
                                    }
                                ],
                            },
                            "531.deepsjeng_r": {
                                "failure_class": "live-timeout",
                                "heartbeat_running": True,
                                "heartbeat_site_progress": True,
                                "heartbeat_last_count": 53,
                                "heartbeat_last_bpc": "0x531",
                            },
                        },
                    },
                    {
                        "name": "train-all-large-9p",
                        "input_set": "train",
                        "stage": "b",
                        "transports": ["9p"],
                        "benches": ["525.x264_r"],
                        "failure_classes": {"525.x264_r": "live-timeout"},
                        "failure_details": {
                            "525.x264_r": {
                                "failure_class": "live-timeout",
                                "heartbeat_running": True,
                                "heartbeat_site_progress": True,
                                "heartbeat_last_count": 52,
                                "heartbeat_last_bpc": "0x525",
                            }
                        },
                    },
                ],
            }
            stage = {
                "stage": "b",
                "input_set": "train",
                "transport": "initramfs",
                "results": {
                    "999.specrand_ir": {
                        "ok": True,
                        "specdiff": {
                            "ok": True,
                            "strict_hash": True,
                            "hash_checks": [{"ok": True, "actual_hash": "0x1", "expected_hash": "0x1"}],
                        },
                    }
                },
            }
            profile = {
                "input_set": "train",
                "stage": "b",
                "qemu": "/tmp/qemu",
                "qemu_provenance": {"qemu_repo_head": "profile-head"},
                "qemu_features": {"qemu_frame_stats": True},
                "rows": [
                    {
                        "bench": "505.mcf_r",
                        "transport": "initramfs",
                        "sample_ok": True,
                        "top_qemu": [
                            {"symbol": "cpu_exec_setjmp", "count": 99},
                            {"symbol": "linx_template_fentry_impl", "count": 10},
                        ],
                    },
                    {
                        "bench": "531.deepsjeng_r",
                        "transport": "initramfs",
                        "sample_ok": True,
                        "top_qemu": [{"symbol": "helper_linx_tlb_iv", "count": 12}],
                    },
                    {
                        "bench": "525.x264_r",
                        "transport": "9p",
                        "sample_ok": True,
                        "top_qemu": [{"symbol": "linx_template_fentry_impl", "count": 14}],
                    },
                ],
            }
            self._write(gate_path, gate)
            self._write(stage_path, stage)
            self._write(profile_path, profile)

            report = analyzer.build_analysis(gate, profile, gate_path, profile_path)

        lanes = {row["bench"]: row["lane"] for row in report["benchmarks"]}
        self.assertEqual(lanes["999.specrand_ir"], "correctness-sentinel-pass")
        self.assertEqual(lanes["531.deepsjeng_r"], "linux-tlbi-attribution")
        self.assertEqual(lanes["525.x264_r"], "transport-9p-throughput")
        self.assertEqual(lanes["505.mcf_r"], "template-tb-mmu-throughput")
        rows = {row["bench"]: row for row in report["benchmarks"]}
        self.assertEqual(
            rows["505.mcf_r"]["top_qemu"],
            [{"symbol": "linx_template_fentry_impl", "count": 10}],
        )
        self.assertEqual(rows["505.mcf_r"]["heartbeat_last_progress"], "site-change")
        self.assertEqual(rows["505.mcf_r"]["heartbeat_recent_unique_sites"], 4)
        self.assertEqual(rows["505.mcf_r"]["heartbeat_recent_count_delta"], 3000000000)
        self.assertEqual(rows["505.mcf_r"]["heartbeat_recent_sites"][-1]["bpc"], "0x505")
        self.assertTrue(rows["505.mcf_r"]["tlb_inv_hot_kernel_symbolized"])
        self.assertIn(
            "local_flush_tlb_page",
            rows["505.mcf_r"]["tlb_inv_hot_kernel_symbol_evidence"],
        )
        self.assertEqual(
            rows["505.mcf_r"]["tlb_inv_hot_kernel_symbols"][0]["function"],
            "local_flush_tlb_page",
        )
        self.assertEqual(
            rows["505.mcf_r"]["profile_wrapper_qemu"],
            [{"symbol": "cpu_exec_setjmp", "count": 99}],
        )
        self.assertEqual(
            rows["505.mcf_r"]["raw_top_qemu"][0],
            {"symbol": "cpu_exec_setjmp", "count": 99},
        )
        lane_summary = {
            row["lane"]: row["top_qemu_symbols"] for row in report["lanes"]
        }
        self.assertNotIn(
            "cpu_exec_setjmp",
            {item["symbol"] for item in lane_summary["template-tb-mmu-throughput"]},
        )
        self.assertFalse(report["completion_status"]["spec_train_correctness_complete"])
        self.assertTrue(report["qemu"]["feature_compatibility"]["ok"])

    def test_build_analysis_reports_qemu_feature_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gate = {
                "profile": "train",
                "qemu_frame_stats": True,
                "qemu_frame_single_reg_fast": False,
                "qemu_frame_page_fast": True,
                "qemu_mmu_cache": True,
                "qemu_mmu_cache_stats": True,
                "suites": [],
            }
            profile = {
                "input_set": "train",
                "stage": "b",
                "qemu_features": {
                    "qemu_frame_stats": False,
                    "qemu_frame_single_reg_fast": True,
                    "qemu_frame_page_fast": False,
                    "qemu_mmu_cache": False,
                    "qemu_mmu_cache_stats": False,
                },
                "rows": [],
            }

            report = analyzer.build_analysis(
                gate,
                profile,
                root / "gate.json",
                root / "profile.json",
            )

        self.assertFalse(report["qemu"]["feature_compatibility"]["ok"])
        mismatches = {
            item["feature"]: (item["gate"], item["profile"])
            for item in report["qemu"]["feature_compatibility"]["mismatches"]
        }
        self.assertEqual(mismatches["qemu_frame_stats"], (True, False))
        self.assertEqual(mismatches["qemu_frame_single_reg_fast"], (False, True))
        self.assertEqual(mismatches["qemu_frame_page_fast"], (True, False))
        self.assertEqual(mismatches["qemu_mmu_cache"], (True, False))
        self.assertEqual(mismatches["qemu_mmu_cache_stats"], (True, False))
        self.assertFalse(report["qemu"]["profile_used_for_classification"])
        self.assertEqual(report["qemu"]["profile_use_reason"], "suppressed-feature-mismatch")

    def test_mismatched_profile_is_suppressed_unless_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gate_path = root / "specint_fast_gate_summary.json"
            profile_path = root / "profile_suite_summary.json"
            gate = {
                "profile": "train",
                "qemu_mmu_cache": True,
                "suites": [
                    {
                        "name": "train-all",
                        "input_set": "train",
                        "stage": "b",
                        "transports": ["initramfs"],
                        "benches": ["531.deepsjeng_r"],
                        "failure_classes": {"531.deepsjeng_r": "live-timeout"},
                        "failure_details": {
                            "531.deepsjeng_r": {
                                "failure_class": "live-timeout",
                                "heartbeat_running": True,
                                "heartbeat_site_progress": True,
                                "heartbeat_last_count": 53,
                                "heartbeat_last_bpc": "0x531",
                            },
                        },
                    }
                ],
            }
            profile = {
                "input_set": "train",
                "stage": "b",
                "qemu_features": {"qemu_mmu_cache": False},
                "rows": [
                    {
                        "bench": "531.deepsjeng_r",
                        "transport": "initramfs",
                        "sample_ok": True,
                        "top_qemu": [{"symbol": "helper_linx_tlb_iv", "count": 120}],
                    }
                ],
            }

            suppressed = analyzer.build_analysis(gate, profile, gate_path, profile_path)
            allowed = analyzer.build_analysis(
                gate,
                profile,
                gate_path,
                profile_path,
                allow_feature_mismatch=True,
            )

        self.assertFalse(suppressed["qemu"]["feature_compatibility"]["ok"])
        self.assertFalse(suppressed["qemu"]["profile_used_for_classification"])
        self.assertEqual(suppressed["benchmarks"][0]["lane"], "live-throughput-unattributed")
        self.assertEqual(suppressed["benchmarks"][0]["top_qemu"], [])
        self.assertTrue(allowed["qemu"]["profile_used_for_classification"])
        self.assertEqual(allowed["qemu"]["profile_use_reason"], "allowed-feature-mismatch")
        self.assertEqual(allowed["benchmarks"][0]["lane"], "linux-tlbi-attribution")

    def test_stage_qemu_detail_carries_fault_trace_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gate_path = root / "specint_fast_gate_summary.json"
            profile_path = root / "profile_suite_summary.json"
            stage_path = root / "stage_b_summary.json"
            gate = {
                "profile": "test",
                "suites": [
                    {
                        "name": "test-all",
                        "input_set": "test",
                        "stage": "b",
                        "transports": ["initramfs"],
                        "stage_summary": str(stage_path),
                        "benches": ["500.perlbench_r"],
                    }
                ],
            }
            stage = {
                "stage": "b",
                "input_set": "test",
                "transport": "initramfs",
                "results": {
                    "500.perlbench_r": {
                        "ok": False,
                        "specdiff": {"ok": False, "strict_hash": True, "hash_checks": []},
                        "qemu": [
                            {
                                "failure_class": "user-trap",
                                "failure_evidence": "LINX_USER_TRAP addr=0x0",
                                "trap_seen": True,
                                "qemu_debug_env": {"LINX_QEMU_FAULT_TRACE": "1"},
                                "fault_trace_seen": True,
                                "fault_trace_count": 2,
                                "fault_trace_last": "LINX_FAULT_TRACE traparg0=0x1234",
                                "fault_trace_samples": [{"traparg0": "0x1234"}],
                                "mem_trace_seen": True,
                                "mem_trace_count": 3,
                                "mem_trace_last": "LINX_MEM_TRACE pc=0x1555672a00 addr=0x3fefe66724",
                                "mem_trace_samples": [{"pc": "0x1555672a00"}],
                                "syscall_trace_seen": True,
                                "syscall_trace_count": 4,
                                "syscall_trace_last": "LINX_SYSCALL_TRACE nr=56 bpc=0x1555837f1c",
                                "syscall_trace_samples": [{"nr": 56}],
                                "fentry_trace_seen": True,
                                "fentry_trace_count": 5,
                                "fentry_trace_last": "LINX_FENTRY_TRACE pc=0x1555837f18",
                                "fentry_trace_samples": [{"pc": "0x1555837f18"}],
                                "fret_stk_trace_seen": True,
                                "fret_stk_trace_count": 6,
                                "fret_stk_trace_last": "LINX_FRET_STK_TRACE pc=0x1555837f46",
                                "fret_stk_trace_samples": [{"pc": "0x1555837f46"}],
                                "pc_watch_seen": True,
                                "pc_watch_line_count": 7,
                                "pc_watch_last": "LINX_PC_WATCH_REGS pc=0x15555c09e6",
                                "pc_watch_samples": [{"pc": "0x15555c09e6"}],
                                "pc_watch_ring_seen": True,
                                "pc_watch_ring_entry_count": 4,
                                "pc_watch_last_ring_entry": (
                                    "LINX_PC_WATCH_RING_ENTRY pc=0x15555c09e6"
                                ),
                                "pc_watch_ring_entry_samples": [
                                    {"pc": "0x15555c09e6"}
                                ],
                                "child_maps": {
                                    "seen": True,
                                    "block_count": 3,
                                    "trap_addr": "0x3f7ff0008c",
                                    "trap_addr_mapped": False,
                                    "trap_addr_line": "",
                                    "fault_addr": "0x3f7feec008",
                                    "fault_addr_mapped": True,
                                    "fault_addr_line": "3f7feec000-3f7feed000 rw-p 00000000 00:00 0",
                                },
                                "pc_watch": {"seen": True, "last": "linx_pc_watch: pc=0x1"},
                                "log": "/tmp/qemu.log",
                            }
                        ],
                    }
                },
            }
            profile = {"input_set": "test", "stage": "b", "rows": []}
            self._write(gate_path, gate)
            self._write(stage_path, stage)
            self._write(profile_path, profile)

            report = analyzer.build_analysis(gate, profile, gate_path, profile_path)
            direct_report = analyzer.build_analysis(stage, profile, stage_path, profile_path)

        row = report["benchmarks"][0]
        self.assertEqual(row["lane"], "correctness-fault-trace-debug")
        self.assertEqual(row["failure_class"], "user-trap")
        self.assertTrue(row["fault_trace_seen"])
        self.assertEqual(row["fault_trace_count"], 2)
        self.assertTrue(row["mem_trace_seen"])
        self.assertEqual(row["mem_trace_count"], 3)
        self.assertTrue(row["syscall_trace_seen"])
        self.assertEqual(row["syscall_trace_count"], 4)
        self.assertTrue(row["fentry_trace_seen"])
        self.assertEqual(row["fentry_trace_count"], 5)
        self.assertTrue(row["fret_stk_trace_seen"])
        self.assertEqual(row["fret_stk_trace_count"], 6)
        self.assertTrue(row["pc_watch_seen"])
        self.assertEqual(row["pc_watch_line_count"], 7)
        self.assertTrue(row["pc_watch_ring_seen"])
        self.assertEqual(row["pc_watch_ring_entry_count"], 4)
        self.assertTrue(row["child_maps_seen"])
        self.assertEqual(row["child_maps_block_count"], 3)
        self.assertEqual(row["child_maps_trap_addr"], "0x3f7ff0008c")
        self.assertFalse(row["child_maps_trap_addr_mapped"])
        self.assertEqual(row["child_maps_fault_addr"], "0x3f7feec008")
        self.assertTrue(row["child_maps_fault_addr_mapped"])
        self.assertEqual(row["qemu_debug_env"], {"LINX_QEMU_FAULT_TRACE": "1"})
        self.assertTrue(row["pc_watch_seen"])
        self.assertEqual(
            direct_report["benchmarks"][0]["lane"],
            "correctness-fault-trace-debug",
        )
        self.assertEqual(direct_report["input_set"], "test")

    def test_feature_compatibility_infers_legacy_profile_command_flags(self) -> None:
        gate = {
            "template_chain": True,
            "qemu_frame_stats": True,
            "qemu_mmu_cache": True,
            "qemu_mmu_cache_stats": True,
            "qemu_tlb_fill_hot": True,
        }
        profile = {
            "template_chain": True,
            "commands": [
                {
                    "command": [
                        "python3",
                        "run_stage_qemu_matrix.py",
                        "--template-chain",
                        "--qemu-frame-stats",
                        "--qemu-mmu-cache",
                        "--qemu-mmu-cache-stats",
                        "--qemu-tlb-fill-hot",
                    ]
                }
            ],
        }

        compatibility = analyzer._feature_compatibility(gate, profile)

        self.assertTrue(compatibility["ok"])
        self.assertTrue(compatibility["profile"]["template_chain"])
        self.assertTrue(compatibility["profile"]["qemu_frame_stats"])
        self.assertTrue(compatibility["profile"]["qemu_mmu_cache"])
        self.assertTrue(compatibility["profile"]["qemu_mmu_cache_stats"])
        self.assertTrue(compatibility["profile"]["qemu_tlb_fill_hot"])

    def test_write_markdown_includes_lane_summary(self) -> None:
        report = {
            "generated_at_utc": "2026-07-05 00:00:00Z",
            "input_set": "train",
            "gate_summary": "/gate.json",
            "profile_summary": "/profile.json",
            "qemu": {
                "gate_provenance": {"qemu_repo_head": "abc"},
                "profile_provenance": {"qemu_repo_head": "def"},
                "feature_compatibility": {
                    "ok": False,
                    "mismatches": [
                        {
                            "feature": "qemu_frame_stats",
                            "gate": True,
                            "profile": False,
                        }
                    ],
                },
                "profile_used_for_classification": False,
                "profile_use_reason": "suppressed-feature-mismatch",
            },
            "completion_status": {
                "spec_train_correctness_complete": False,
                "passing_benches": ["999.specrand_ir"],
                "failing_benches": ["505.mcf_r"],
            },
            "benchmarks": [
                {
                    "bench": "505.mcf_r",
                    "transport": "initramfs",
                    "gate_ok": False,
                    "failure_class": "live-timeout",
                    "heartbeat_last_count": 5,
                    "heartbeat_last_bpc": "0x505",
                    "profile_sample_ok": True,
                    "lane": "template-tb-mmu-throughput",
                    "top_qemu": [{"symbol": "tb_lookup", "count": 3}],
                    "proposed_action": "Target TB lookup.",
                    "trap_seen": True,
                    "fault_trace_seen": True,
                    "fault_trace_count": 1,
                    "fault_trace_last": "LINX_FAULT_TRACE traparg0=0x1234",
                    "syscall_trace_seen": True,
                    "syscall_trace_count": 2,
                    "syscall_trace_last": "LINX_SYSCALL_TRACE nr=63 bpc=0x1555837f1c",
                    "fentry_trace_seen": True,
                    "fentry_trace_count": 2,
                    "fentry_trace_last": "LINX_FENTRY_TRACE pc=0x1555837f18",
                    "fret_stk_trace_seen": True,
                    "fret_stk_trace_count": 2,
                    "fret_stk_trace_last": "LINX_FRET_STK_TRACE pc=0x1555837f46",
                    "pc_watch_seen": True,
                    "pc_watch_line_count": 3,
                    "pc_watch_last": "LINX_PC_WATCH_REGS pc=0x15555c09e6",
                    "pc_watch_ring_seen": True,
                    "pc_watch_ring_entry_count": 1,
                    "pc_watch_last_ring_entry": (
                        "LINX_PC_WATCH_RING_ENTRY pc=0x15555c09e6"
                    ),
                    "child_maps_seen": True,
                    "child_maps_trap_addr": "0x3f7ff0008c",
                    "child_maps_trap_addr_mapped": False,
                    "child_maps_fault_addr": "0x3f7feec008",
                    "child_maps_fault_addr_mapped": True,
                    "child_maps_fault_addr_line": "3f7feec000-3f7feed000 rw-p 00000000 00:00 0",
                    "failure_evidence": "LINX_USER_TRAP addr=0x0",
                }
            ],
            "lanes": [
                {
                    "lane": "template-tb-mmu-throughput",
                    "bench_count": 1,
                    "benches": ["505.mcf_r"],
                    "top_qemu_symbols": [{"symbol": "tb_lookup", "count": 3}],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "report.md"
            analyzer._write_markdown(path, report)
            text = path.read_text(encoding="utf-8")

        self.assertIn("SPECint QEMU Progress Analysis", text)
        self.assertIn("qemu_feature_compatible: `false`", text)
        self.assertIn("profile_used_for_classification: `false`", text)
        self.assertIn("profile_use_reason: `suppressed-feature-mismatch`", text)
        self.assertIn("qemu_frame_stats", text)
        self.assertIn("template-tb-mmu-throughput", text)
        self.assertIn("tb_lookup=3", text)
        self.assertIn("Fault And Trap Evidence", text)
        self.assertIn("LINX_FAULT_TRACE", text)
        self.assertIn("syscall-trace count=`2`", text)
        self.assertIn("fentry-trace count=`2`", text)
        self.assertIn("fret-stk-trace count=`2`", text)
        self.assertIn("pc-watch lines=`3`", text)
        self.assertIn("pc-watch-ring entries=`1`", text)
        self.assertIn("child-maps trap_addr=`0x3f7ff0008c` mapped=`false`", text)
        self.assertIn("child-maps fault_addr=`0x3f7feec008` mapped=`true`", text)


if __name__ == "__main__":
    unittest.main()
