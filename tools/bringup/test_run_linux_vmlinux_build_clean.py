#!/usr/bin/env python3
"""Regression tests for the clean Linux vmlinux build wrapper."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("run_linux_vmlinux_build_clean.sh")


class LinuxVmlinuxBuildCleanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.base = Path(self.temp_dir.name)
        self.linux_root = self.base / "linux"
        self.out_dir = self.base / "out"
        self.linux_root.mkdir()

        self.clang = self.base / "clang"
        self.clang.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.clang.chmod(0o755)

        self.gmake = self.base / "gmake"
        self.gmake.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
out=''
target=''
for arg in "$@"; do
  case "$arg" in
    O=*) out="${arg#O=}" ;;
    linx_v150_defconfig|olddefconfig|vmlinux) target="$arg" ;;
  esac
done
mkdir -p "$out"
if [[ "$target" == "linx_v150_defconfig" ]]; then
  printf 'CONFIG_FAKE=y\\n' > "$out/.config"
elif [[ "$target" == "vmlinux" ]]; then
  if [[ -e "$out/stale-object" ]]; then
    echo 'stale output survived fresh mode' >&2
    exit 9
  fi
  printf 'fresh-vmlinux\\n' > "$out/vmlinux"
fi
""",
            encoding="utf-8",
        )
        self.gmake.chmod(0o755)

    def _run(self, out_dir: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "bash",
                str(SCRIPT),
                "--linux-root",
                str(self.linux_root),
                "--out-dir",
                str(out_dir),
                "--clang",
                str(self.clang),
                "--gmake",
                str(self.gmake),
                "--jobs",
                "1",
                *extra,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def test_fresh_mode_removes_previous_output_before_build(self) -> None:
        first = self._run(self.out_dir, "--fresh")
        self.assertEqual(first.returncode, 0, first.stderr)
        (self.out_dir / "stale-object").write_text("stale\n", encoding="utf-8")

        result = self._run(self.out_dir, "--fresh")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.out_dir / "stale-object").exists())
        self.assertEqual(
            (self.out_dir / "vmlinux").read_text(encoding="utf-8"),
            "fresh-vmlinux\n",
        )

    def test_fresh_mode_refuses_unowned_nonempty_output(self) -> None:
        self.out_dir.mkdir()
        (self.out_dir / "unrelated").write_text("keep\n", encoding="utf-8")

        result = self._run(self.out_dir, "--fresh")

        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to remove unowned", result.stderr)
        self.assertTrue((self.out_dir / "unrelated").exists())

    def test_fresh_mode_refuses_output_inside_source_tree(self) -> None:
        result = self._run(self.linux_root / "build", "--fresh")

        self.assertEqual(result.returncode, 2)
        self.assertIn("fresh output directory must be outside", result.stderr)

    def test_fresh_mode_refuses_symlink_output(self) -> None:
        target = self.base / "target"
        target.mkdir()
        link = self.base / "out-link"
        link.symlink_to(target, target_is_directory=True)

        result = self._run(link, "--fresh")

        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be a symbolic link", result.stderr)


if __name__ == "__main__":
    unittest.main()
