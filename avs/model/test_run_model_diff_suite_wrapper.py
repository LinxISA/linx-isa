#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


RUNNER_PATH = Path(__file__).resolve().parents[2] / "tools/bringup/run_model_diff_suite.py"
SPEC = importlib.util.spec_from_file_location("root_model_diff_runner", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
root_model_diff_runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(root_model_diff_runner)


class ModelDiffWrapperTests(unittest.TestCase):
    def test_explicit_qemu_path_is_forwarded_to_model_suite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu = root / "exact-qemu-system-linx64"
            qemu.write_bytes(b"exact merged qemu")
            completed = subprocess.CompletedProcess(
                args=[], returncode=0, stdout='{"cases": []}\n'
            )
            with mock.patch.object(
                root_model_diff_runner.subprocess,
                "run",
                return_value=completed,
            ) as run:
                with redirect_stdout(io.StringIO()):
                    result = root_model_diff_runner.main(
                        ["--root", str(root), "--qemu", str(qemu)]
                    )

        self.assertEqual(result, 0)
        command = run.call_args.args[0]
        qemu_index = command.index("--qemu")
        self.assertEqual(command[qemu_index + 1], str(qemu.resolve()))


if __name__ == "__main__":
    unittest.main()
