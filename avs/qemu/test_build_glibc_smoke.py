#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_glibc_smoke


class GlibcSmokeBuildInputTests(unittest.TestCase):
    def test_fallback_libs_follow_selected_glibc_build_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            glibc_build = root / "out" / "libc" / "glibc" / "v058-release" / "build"
            out_dir = root / "runtime"
            clang = root / "clang"
            clang.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            clang.chmod(0o755)

            tests_dir = root / "avs" / "qemu" / "tests"
            tests_dir.mkdir(parents=True)
            (tests_dir / "linux_glibc_hello_min.c").write_text("int main(void) { return 0; }\n")
            (tests_dir / "wrap_init_musl_staticpie_env.c").write_text("void _start(void) {}\n")

            for rel in (
                "csu/crt1.o",
                "csu/Scrt1.o",
                "csu/crti.o",
                "csu/crtn.o",
                "libc.a",
                "libc.so",
            ):
                path = glibc_build / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

            commands: list[list[str]] = []
            with (
                mock.patch.object(build_glibc_smoke, "REPO_ROOT", root),
                mock.patch.object(build_glibc_smoke, "_run", side_effect=lambda cmd, **_: commands.append(cmd)),
            ):
                self.assertEqual(
                    build_glibc_smoke.main(
                        [
                            "--clang",
                            str(clang),
                            "--glibc-build",
                            str(glibc_build),
                            "--out-dir",
                            str(out_dir),
                        ]
                    ),
                    0,
                )

            resolved_out = out_dir.resolve()
            resolved_build = glibc_build.resolve()
            static_command = next(
                cmd for cmd in commands if str(resolved_out / "hello_glibc_static") in cmd
            )
            self.assertIn(
                "-L" + str(resolved_build.parent / "fallback-libs"),
                static_command,
            )


if __name__ == "__main__":
    unittest.main()
