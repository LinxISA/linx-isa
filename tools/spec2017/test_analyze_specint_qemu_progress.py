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
                        "top_qemu": [{"symbol": "linx_template_fentry_impl", "count": 10}],
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
        self.assertFalse(report["completion_status"]["spec_train_correctness_complete"])
        self.assertTrue(report["qemu"]["feature_compatibility"]["ok"])

    def test_build_analysis_reports_qemu_feature_mismatches(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gate = {
                "profile": "train",
                "qemu_frame_stats": True,
                "qemu_frame_single_reg_fast": False,
                "suites": [],
            }
            profile = {
                "input_set": "train",
                "stage": "b",
                "qemu_features": {
                    "qemu_frame_stats": False,
                    "qemu_frame_single_reg_fast": True,
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

    def test_feature_compatibility_infers_legacy_profile_command_flags(self) -> None:
        gate = {
            "template_chain": True,
            "qemu_frame_stats": True,
            "qemu_tlb_fill_hot": True,
        }
        profile = {
            "template_chain": True,
            "commands": [
                {
                    "command": [
                        "python3",
                        "run_stage_qemu_matrix.py",
                        "--qemu-frame-stats",
                        "--qemu-tlb-fill-hot",
                    ]
                }
            ],
        }

        compatibility = analyzer._feature_compatibility(gate, profile)

        self.assertTrue(compatibility["ok"])
        self.assertTrue(compatibility["profile"]["qemu_frame_stats"])
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
        self.assertIn("qemu_frame_stats", text)
        self.assertIn("template-tb-mmu-throughput", text)
        self.assertIn("tb_lookup=3", text)


if __name__ == "__main__":
    unittest.main()
