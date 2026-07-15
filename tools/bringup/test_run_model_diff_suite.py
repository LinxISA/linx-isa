#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_model_diff_suite


class RunModelDiffSuiteTests(unittest.TestCase):
    def test_wrapper_selects_direct_boot_qemu(self) -> None:
        completed = subprocess.CompletedProcess([], 0, stdout='{"cases": []}\n')
        with (
            mock.patch.object(run_model_diff_suite.subprocess, "run", return_value=completed) as run,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            rc = run_model_diff_suite.main(["--root", "/repo"])

        self.assertEqual(rc, 0)
        cmd = run.call_args.args[0]
        self.assertIn("--qemu", cmd)
        self.assertEqual(
            cmd[cmd.index("--qemu") + 1],
            "/repo/emulator/qemu/build-linx/qemu-system-linx64",
        )
        self.assertIn("--qemu-bios", cmd)
        self.assertEqual(cmd[cmd.index("--qemu-bios") + 1], "none")
        self.assertEqual(run.call_args.kwargs["env"]["LINX_VIRT_TEST_FINISHER"], "1")


if __name__ == "__main__":
    unittest.main()
