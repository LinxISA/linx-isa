#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RUNNER = Path(__file__).with_name("run_tsvc.py")


def _load_runner_module():
    spec = importlib.util.spec_from_file_location("linx_tsvc_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SourcePolicyTests(unittest.TestCase):
    def test_removed_v03_policy_is_rejected(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(RUNNER), "--source-policy", "linx-v03-parity"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("invalid choice", proc.stderr)
        self.assertNotIn("clang not found", proc.stderr)


class QemuFinisherTests(unittest.TestCase):
    def test_qemu_runner_enables_and_accepts_canonical_pass_finisher(self) -> None:
        runner = _load_runner_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake_qemu = root / "qemu-system-linx64"
            fake_qemu.write_text(
                "#!/bin/sh\n"
                "test \"$LINX_VIRT_TEST_FINISHER\" = 1 || exit 42\n"
                "printf 'Loop \\tTime(sec) \\tChecksum\\n s000\\t1\\t0x474b2000\\n'\n"
                "exit 85\n",
                encoding="utf-8",
            )
            fake_qemu.chmod(0o755)
            elf = root / "tsvc.off.elf"
            elf.write_bytes(b"ELF")
            stdout_log = root / "stdout.txt"
            stderr_log = root / "stderr.txt"

            old = os.environ.pop("LINX_VIRT_TEST_FINISHER", None)
            try:
                returncode, stdout = runner._run_qemu(
                    qemu=fake_qemu,
                    elf=elf,
                    stdout_log=stdout_log,
                    stderr_log=stderr_log,
                    timeout_s=2.0,
                    verbose=False,
                )
            finally:
                if old is not None:
                    os.environ["LINX_VIRT_TEST_FINISHER"] = old

            self.assertEqual(returncode, 85)
            self.assertIn("s000", stdout)
            self.assertEqual(stderr_log.read_bytes(), b"")

    def test_qemu_runner_rejects_canonical_fail_finisher(self) -> None:
        runner = _load_runner_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake_qemu = root / "qemu-system-linx64"
            fake_qemu.write_text("#!/bin/sh\nexit 51\n", encoding="utf-8")
            fake_qemu.chmod(0o755)
            elf = root / "tsvc.off.elf"
            elf.write_bytes(b"ELF")

            with self.assertRaisesRegex(SystemExit, "QEMU failed \\(exit=51\\)"):
                runner._run_qemu(
                    qemu=fake_qemu,
                    elf=elf,
                    stdout_log=root / "stdout.txt",
                    stderr_log=root / "stderr.txt",
                    timeout_s=2.0,
                    verbose=False,
                )


if __name__ == "__main__":
    unittest.main()
