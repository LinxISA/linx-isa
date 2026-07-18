#!/usr/bin/env python3
"""Regression tests for the clean BusyBox rootfs build wrapper."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("run_linux_busybox_rootfs_build_clean.sh")


class LinuxBusyboxRootfsBuildCleanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.base = Path(self.temp_dir.name)
        self.linux_root = self.base / "linux"
        self.llvm_build = self.base / "llvm"
        self.worktree = self.base / "worktree"
        self.out_dir = self.base / "out"
        self.obj_dir = self.base / "obj"
        self.build_count = self.base / "build-count"

        build_script = self.linux_root / "tools/linxisa/busybox_rootfs/build_rootfs.sh"
        build_script.parent.mkdir(parents=True)
        build_script.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
count=0
if [[ -f "$FAKE_BUILD_COUNT" ]]; then
  count="$(cat "$FAKE_BUILD_COUNT")"
fi
count="$((count + 1))"
printf '%s\\n' "$count" > "$FAKE_BUILD_COUNT"
mkdir -p "$O/linx-busybox-rootfs"
printf 'pristine-generation-%s\\n' "$count" > "$O/linx-busybox-rootfs/rootfs.ext2"
""",
            encoding="utf-8",
        )
        build_script.chmod(0o755)

        self._run_git("init", "-q")
        self._run_git("config", "user.email", "rootfs-test@example.invalid")
        self._run_git("config", "user.name", "Rootfs Test")
        self._run_git("add", ".")
        self._run_git("commit", "-qm", "fixture")

        tool_dir = self.llvm_build / "bin"
        tool_dir.mkdir(parents=True)
        for name in ("clang", "ld.lld"):
            tool = tool_dir / name
            tool.write_text(f"#!/bin/sh\n# fake {name} v1\n", encoding="utf-8")
            tool.chmod(0o755)

    def _run_git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.linux_root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _run_wrapper(
        self, *extra_args: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["FAKE_BUILD_COUNT"] = str(self.build_count)
        return subprocess.run(
            [
                "bash",
                str(SCRIPT),
                "--linux-root",
                str(self.linux_root),
                "--worktree",
                str(self.worktree),
                "--out-dir",
                str(self.out_dir),
                "--obj-dir",
                str(self.obj_dir),
                "--llvm-build",
                str(self.llvm_build),
                *extra_args,
            ],
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

    def test_pristine_cache_restores_working_image_and_tracks_toolchain(self) -> None:
        rootfs = self.out_dir / "rootfs.ext2"
        pristine = self.out_dir / "rootfs.pristine.ext2"
        marker = self.out_dir / ".linx_linux_rootfs_clean_head"

        first = self._run_wrapper()
        self.assertEqual(first.stdout.splitlines(), [str(rootfs)])
        self.assertEqual(self.build_count.read_text(encoding="utf-8"), "1\n")
        self.assertEqual(rootfs.read_bytes(), b"pristine-generation-1\n")
        self.assertEqual(pristine.read_bytes(), rootfs.read_bytes())
        first_marker = marker.read_text(encoding="utf-8")
        self.assertIn("format=2\n", first_marker)
        self.assertIn("linux_head=", first_marker)
        self.assertIn("clang_sha256=", first_marker)
        self.assertIn("ld_lld_sha256=", first_marker)

        rootfs.write_bytes(b"mutated-by-rw-boot\n")
        second = self._run_wrapper()
        self.assertEqual(second.stdout.splitlines(), [str(rootfs)])
        self.assertEqual(self.build_count.read_text(encoding="utf-8"), "1\n")
        self.assertEqual(rootfs.read_bytes(), b"pristine-generation-1\n")

        clang = self.llvm_build / "bin/clang"
        clang.write_text("#!/bin/sh\n# fake clang v2\n", encoding="utf-8")
        clang.chmod(0o755)
        third = self._run_wrapper()
        self.assertEqual(third.stdout.splitlines(), [str(rootfs)])
        self.assertEqual(self.build_count.read_text(encoding="utf-8"), "2\n")
        self.assertEqual(rootfs.read_bytes(), b"pristine-generation-2\n")
        self.assertNotEqual(marker.read_text(encoding="utf-8"), first_marker)

    def test_legacy_marker_and_missing_pristine_force_rebuild(self) -> None:
        self._run_wrapper()
        marker = self.out_dir / ".linx_linux_rootfs_clean_head"
        pristine = self.out_dir / "rootfs.pristine.ext2"

        head = subprocess.run(
            ["git", "-C", str(self.linux_root), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout
        marker.write_text(head, encoding="utf-8")
        self._run_wrapper()
        self.assertEqual(self.build_count.read_text(encoding="utf-8"), "2\n")

        pristine.unlink()
        self._run_wrapper()
        self.assertEqual(self.build_count.read_text(encoding="utf-8"), "3\n")

    def test_pristine_path_cannot_be_returned_as_work_image(self) -> None:
        pristine = self.out_dir / "rootfs.pristine.ext2"
        result = self._run_wrapper(
            "--rootfs-img", str(pristine), check=False
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("rootfs work image must differ from pristine cache", result.stderr)
        self.assertFalse(self.build_count.exists())


if __name__ == "__main__":
    unittest.main()
