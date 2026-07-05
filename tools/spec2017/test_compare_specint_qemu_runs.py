#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compare_specint_qemu_runs as compare


class CompareSpecintQemuRunsTests(unittest.TestCase):
    def _write(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def _summary(
        self,
        root: Path,
        name: str,
        *,
        counts: dict[str, int],
        ok_benches: set[str] | None = None,
        trap_benches: set[str] | None = None,
        features: dict[str, bool] | None = None,
        debug_env: dict[str, str] | None = None,
    ) -> Path:
        ok_benches = ok_benches or set()
        trap_benches = trap_benches or set()
        features = features or {}
        path = root / name / "specint_fast_gate_summary.json"
        stage_path = root / name / "train-all" / "initramfs" / "stage_b_summary.json"
        benches = sorted(set(counts) | ok_benches | trap_benches)
        summary = {
            "profile": "train",
            "qemu": f"/tmp/{name}/qemu-system-linx64",
            "qemu_provenance": {"qemu_repo_head": f"{name}-head"},
            **features,
            "suites": [
                {
                    "name": "train-all",
                    "input_set": "train",
                    "stage": "b",
                    "transports": ["initramfs"],
                    "timeout_sec": 100,
                    "benches": benches,
                    "stage_summary": str(stage_path),
                    "failure_classes": {
                        bench: ("user-trap" if bench in trap_benches else "live-timeout")
                        for bench in benches
                        if bench not in ok_benches
                    },
                    "failure_details": {
                        bench: {
                            "failure_class": "user-trap" if bench in trap_benches else "live-timeout",
                            "heartbeat_running": bench not in trap_benches,
                            "heartbeat_site_progress": bench not in trap_benches,
                            "heartbeat_last_count": counts.get(bench, 0),
                            "heartbeat_last_bpc": f"0x{bench[:3]}",
                            "trap_seen": bench in trap_benches,
                            "heartbeat_tb_stats": {"lookup": counts.get(bench, 0) * 2},
                            "heartbeat_tlb_fill": {"total": counts.get(bench, 0) * 3},
                            "heartbeat_frame_stats": {
                                "restore_fallback": counts.get(bench, 0) * 4,
                                "single_fast_fentry": counts.get(bench, 0) * 5,
                            },
                            "qemu_debug_env": debug_env or {},
                        }
                        for bench in benches
                        if bench not in ok_benches
                    },
                }
            ],
        }
        stage = {
            "stage": "b",
            "input_set": "train",
            "transport": "initramfs",
            "results": {
                bench: {
                    "ok": True,
                    "specdiff": {
                        "ok": True,
                        "strict_hash": True,
                        "hash_checks": [{"ok": True, "actual_hash": "0x1", "expected_hash": "0x1"}],
                    },
                }
                for bench in ok_benches
            },
        }
        self._write(path, summary)
        self._write(stage_path, stage)
        return path

    def test_build_comparison_reports_throughput_and_correctness_verdicts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            baseline_path = self._summary(
                root,
                "base",
                counts={"505.mcf_r": 100, "541.leela_r": 100, "557.xz_r": 100},
                ok_benches={"999.specrand_ir"},
                features={"qemu_frame_single_reg_fast": False},
            )
            candidate_path = self._summary(
                root,
                "cand",
                counts={"505.mcf_r": 90, "541.leela_r": 110, "557.xz_r": 0},
                ok_benches=set(),
                trap_benches={"557.xz_r", "999.specrand_ir"},
                features={"qemu_frame_single_reg_fast": True},
            )
            report = compare.build_comparison(
                json.loads(baseline_path.read_text(encoding="utf-8")),
                json.loads(candidate_path.read_text(encoding="utf-8")),
                baseline_path,
                candidate_path,
                threshold_pct=5,
            )

        rows = {row["bench"]: row for row in report["rows"]}
        self.assertEqual(rows["541.leela_r"]["verdict"], "throughput-improved")
        self.assertEqual(rows["505.mcf_r"]["verdict"], "throughput-regressed")
        self.assertEqual(rows["999.specrand_ir"]["verdict"], "correctness-regressed")
        self.assertEqual(rows["557.xz_r"]["verdict"], "correctness-regressed")
        self.assertAlmostEqual(rows["541.leela_r"]["count_delta_pct"], 10.0)
        self.assertAlmostEqual(rows["505.mcf_r"]["count_per_sec_delta_pct"], -10.0)
        self.assertEqual(
            rows["541.leela_r"]["diagnostic_deltas"]["tb_lookup"]["delta"],
            20,
        )
        self.assertEqual(
            report["summary"]["recommendation"],
            "reject-candidate-correctness-regression",
        )
        feature_changes = {
            item["feature"]: (item["baseline"], item["candidate"])
            for item in report["qemu_features"]["changed"]
        }
        self.assertEqual(feature_changes["qemu_frame_single_reg_fast"], (False, True))

    def test_feature_delta_infers_template_chain_from_row_debug_env(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            baseline_path = self._summary(
                root,
                "base",
                counts={"505.mcf_r": 100},
            )
            candidate_path = self._summary(
                root,
                "cand",
                counts={"505.mcf_r": 110},
                debug_env={"LINX_QEMU_TEMPLATE_CHAIN": "1"},
            )
            report = compare.build_comparison(
                json.loads(baseline_path.read_text(encoding="utf-8")),
                json.loads(candidate_path.read_text(encoding="utf-8")),
                baseline_path,
                candidate_path,
            )

        feature_changes = {
            item["feature"]: (item["baseline"], item["candidate"])
            for item in report["qemu_features"]["changed"]
        }
        self.assertEqual(feature_changes["template_chain"], (False, True))

    def test_write_markdown_contains_feature_and_row_table(self) -> None:
        report = {
            "generated_at_utc": "2026-07-05 00:00:00Z",
            "threshold_pct": 2.0,
            "baseline": {"label": "base", "summary": "/base.json", "qemu_head": "a"},
            "candidate": {"label": "cand", "summary": "/cand.json", "qemu_head": "b"},
            "qemu_features": {
                "changed": [
                    {
                        "feature": "qemu_mmu_cache",
                        "baseline": False,
                        "candidate": True,
                    }
                ]
            },
            "summary": {
                "recommendation": "mixed-candidate-row-regressions",
                "verdict_counts": {"throughput-improved": 1, "throughput-regressed": 1},
            },
            "rows": [
                {
                    "bench": "505.mcf_r",
                    "transport": "initramfs",
                    "verdict": "throughput-regressed",
                    "baseline_count": 100,
                    "candidate_count": 90,
                    "count_delta_pct": -10.0,
                    "count_per_sec_delta_pct": -10.0,
                    "baseline_bpc": "0x505",
                    "candidate_bpc": "0x506",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "report.md"
            compare.write_markdown(path, report)
            text = path.read_text(encoding="utf-8")

        self.assertIn("SPECint QEMU Run Comparison", text)
        self.assertIn("qemu_mmu_cache", text)
        self.assertIn("throughput-regressed", text)
        self.assertIn("-10.00%", text)


if __name__ == "__main__":
    unittest.main()
