#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import profile_qemu_spec_suite as suite


class ProfileQemuSpecSuiteTests(unittest.TestCase):
    def test_bench_slug_is_path_safe(self) -> None:
        self.assertEqual(suite._bench_slug("500.perlbench_r"), "500_perlbench_r")
        self.assertEqual(suite._bench_slug("525.x264_r"), "525_x264_r")

    def test_transport_auto_splits_large_payload(self) -> None:
        self.assertEqual(suite._transport_for_bench("505.mcf_r", "auto"), "initramfs")
        self.assertEqual(suite._transport_for_bench("525.x264_r", "auto"), "9p")
        self.assertEqual(suite._transport_for_bench("525.x264_r", "initramfs"), "initramfs")

    def test_parse_env_assignment_requires_key_value(self) -> None:
        self.assertEqual(suite._parse_env_assignment("A=B=C"), ("A", "B=C"))
        with self.assertRaises(SystemExit):
            suite._parse_env_assignment("NO_VALUE")
        with self.assertRaises(SystemExit):
            suite._parse_env_assignment("=no_key")

    def test_parse_args_defaults_to_train_workload_benches(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            args = suite._parse_args(["--out-root", td, "--qemu", "/tmp/qemu"])

        self.assertEqual(args.input_set, "train")
        self.assertEqual(args.stage, "b")
        self.assertEqual(args.bench, suite.DEFAULT_PROFILE_BENCHES)
        self.assertNotIn("999.specrand_ir", args.bench)
        self.assertTrue(args.terminate_after_sample)
        self.assertTrue(args.terminate_on_wait_timeout)

    def test_parse_args_can_profile_sentinel_when_named(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            args = suite._parse_args(
                [
                    "--out-root",
                    td,
                    "--qemu",
                    "/tmp/qemu",
                    "--bench",
                    "999.specrand_ir",
                ]
            )

        self.assertEqual(args.bench, ("999.specrand_ir",))

    def test_profile_command_uses_bench_root_and_transport_policy(self) -> None:
        args = argparse.Namespace(
            spec_dir=Path("/spec"),
            qemu=Path("/qemu"),
            sysroot=Path("/sysroot"),
            sample_sec=7,
            sample_delay_sec=3.5,
            wait_timeout=90.0,
            terminate_grace_sec=2.0,
            terminate_after_sample=True,
            terminate_on_wait_timeout=True,
            stage="b",
            input_set="train",
            transports="auto",
            row_timeout=120,
            heartbeat_sec=0.0,
            guest_heartbeat_sec=0,
            qemu_heartbeat_interval=0,
            no_progress_timeout=0.0,
            stack_limit="2G",
            memory_mb=2048,
            append_extra="norandmaps",
            dump_prefix_bytes=0,
            qemu_frame_stats=True,
            qemu_frame_shape_hot=True,
            qemu_frame_single_reg_fast=True,
            qemu_frame_page_fast=True,
            qemu_mmu_cache=True,
            qemu_mmu_cache_stats=True,
            qemu_mmu_cache_assoc2=True,
            qemu_tb_stats=True,
            qemu_tlb_stats=False,
            qemu_tlb_inv_hot=False,
            qemu_tlb_fill_stats=False,
            qemu_tlb_fill_hot=False,
        )

        cmd = suite._profile_command(args, "525.x264_r", Path("/out/525_x264_r"))

        self.assertIn("--terminate-after-sample", cmd)
        self.assertIn("--terminate-on-wait-timeout", cmd)
        self.assertIn("--sample-delay-sec", cmd)
        self.assertIn("3.5", cmd)
        self.assertIn("--transports", cmd)
        self.assertEqual(cmd[cmd.index("--transports") + 1], "9p")
        self.assertIn("--qemu-frame-stats", cmd)
        self.assertIn("--qemu-frame-shape-hot", cmd)
        self.assertIn("--qemu-frame-single-reg-fast", cmd)
        self.assertIn("--qemu-frame-page-fast", cmd)
        self.assertIn("--qemu-mmu-cache", cmd)
        self.assertIn("--qemu-mmu-cache-stats", cmd)
        self.assertIn("--qemu-tb-stats", cmd)
        self.assertEqual(cmd[cmd.index("--bench") + 1], "525.x264_r")

    def test_aggregate_top_qemu_counts_reports_once_per_row(self) -> None:
        rows = [
            {
                "top_qemu": [
                    {"symbol": "tb_lookup", "count": 5},
                    {"symbol": "tb_lookup", "count": 2},
                    {"symbol": "mmu_lookup1", "count": 3},
                ]
            },
            {"top_qemu": [{"symbol": "tb_lookup", "count": 7}]},
        ]

        out = suite._aggregate_top(rows)

        self.assertEqual(out[0], {"symbol": "tb_lookup", "count": 14, "reports": 2})
        self.assertEqual(out[1], {"symbol": "mmu_lookup1", "count": 3, "reports": 1})

    def test_qemu_features_records_all_profile_knobs(self) -> None:
        args = argparse.Namespace(
            template_chain=True,
            qemu_frame_stats=True,
            qemu_frame_shape_hot=False,
            qemu_frame_single_reg_fast=True,
            qemu_frame_page_fast=True,
            qemu_mmu_cache=True,
            qemu_mmu_cache_stats=True,
            qemu_mmu_cache_assoc2=True,
            qemu_tb_stats=True,
            qemu_tlb_stats=True,
            qemu_tlb_inv_hot=False,
            qemu_tlb_fill_stats=True,
            qemu_tlb_fill_hot=False,
        )

        features = suite._qemu_features(args)

        self.assertTrue(features["template_chain"])
        self.assertTrue(features["qemu_frame_stats"])
        self.assertFalse(features["qemu_frame_shape_hot"])
        self.assertTrue(features["qemu_frame_single_reg_fast"])
        self.assertTrue(features["qemu_frame_page_fast"])
        self.assertTrue(features["qemu_mmu_cache"])
        self.assertTrue(features["qemu_mmu_cache_stats"])
        self.assertTrue(features["qemu_mmu_cache_assoc2"])
        self.assertTrue(features["qemu_tb_stats"])
        self.assertTrue(features["qemu_tlb_stats"])
        self.assertFalse(features["qemu_tlb_inv_hot"])
        self.assertTrue(features["qemu_tlb_fill_stats"])
        self.assertFalse(features["qemu_tlb_fill_hot"])

    def test_write_markdown_uses_qemu_repo_head(self) -> None:
        summary = {
            "started_at_utc": "2026-07-05 00:00:00Z",
            "finished_at_utc": "2026-07-05 00:00:01Z",
            "input_set": "train",
            "qemu": "/tmp/qemu",
            "qemu_provenance": {"qemu_repo_head": "abc123"},
            "rows": [],
            "aggregate_top_qemu": [],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "summary.md"
            suite._write_markdown(path, summary)
            text = path.read_text()

        self.assertIn("- qemu_head: `abc123`", text)


if __name__ == "__main__":
    unittest.main()
