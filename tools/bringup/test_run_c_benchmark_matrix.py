#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from run_c_benchmark_matrix import _classify, _initramfs_lines


class CBenchmarkLauncherTests(unittest.TestCase):
    def test_success_requires_exit_zero_and_clean_shutdown(self) -> None:
        result = _classify(
            "LINX_BENCH_START\nLINX_BENCH_EXIT rc=0\nLINX_REBOOT lisc_shutdown\n",
            qemu_rc=0,
            timed_out=False,
        )
        self.assertTrue(result["ok"])

    def test_timeout_never_passes_even_after_markers(self) -> None:
        result = _classify(
            "LINX_BENCH_START\nLINX_BENCH_EXIT rc=0\nLINX_REBOOT lisc_shutdown\n",
            qemu_rc=None,
            timed_out=True,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["classification"], "timeout")

    def test_nonzero_workload_exit_is_missing_success_marker(self) -> None:
        result = _classify(
            "LINX_BENCH_START\nLINX_BENCH_EXIT rc=9\nLINX_REBOOT lisc_shutdown\n",
            qemu_rc=0,
            timed_out=False,
        )
        self.assertFalse(result["ok"])
        self.assertIn("LINX_BENCH_EXIT rc=0", result["missing_markers"])

    def test_initramfs_places_supervisor_and_workload_separately(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            lines = _initramfs_lines(root / "init", root / "coremark.elf")
        self.assertIn(f"file /init {root / 'init'} 0755 0 0", lines)
        self.assertIn(f"file /bench {root / 'coremark.elf'} 0755 0 0", lines)


if __name__ == "__main__":
    unittest.main()
