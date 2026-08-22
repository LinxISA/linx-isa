#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_BUILD_SCRIPT = ROOT / "tools" / "build_linx_llvm_cpp_runtimes.sh"


class RuntimeBuildScriptTest(unittest.TestCase):
    def test_linux_uapi_helper_rename_is_complete(self) -> None:
        script = RUNTIME_BUILD_SCRIPT.read_text(encoding="utf-8")

        legacy_calls = re.findall(r"(?m)^\s*ensure_linux_compat_headers\s*$", script)
        current_calls = re.findall(r"(?m)^\s*install_linux_uapi_headers\s*$", script)

        self.assertEqual(legacy_calls, [], "legacy helper call survived the rename")
        self.assertEqual(
            len(current_calls),
            2,
            "Linux UAPI headers must be installed before configure and after sysroot merge",
        )

    def test_no_merge_empty_copied_libs_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            llvm_root = temp / "llvm-project"
            host_build = temp / "host-build"
            sysroot = temp / "sysroot"
            out_root = temp / "out"
            fake_bin = temp / "bin"
            linux_root = temp / "linux"
            cache_file = llvm_root / "runtime-cache.cmake"

            (llvm_root / "llvm").mkdir(parents=True)
            (llvm_root / "runtimes").mkdir()
            cache_file.write_text("# test cache\n", encoding="utf-8")
            (host_build / "lib/cmake/llvm").mkdir(parents=True)
            (host_build / "lib/cmake/clang").mkdir(parents=True)
            (host_build / "lib/cmake/llvm/LLVMConfig.cmake").write_text(
                "# test config\n", encoding="utf-8"
            )
            (host_build / "lib/cmake/clang/ClangConfig.cmake").write_text(
                "# test config\n", encoding="utf-8"
            )
            (sysroot / "lib").mkdir(parents=True)
            (sysroot / "include").mkdir()
            (linux_root / "include/uapi/linux").mkdir(parents=True)
            for header in ("limits.h", "futex.h"):
                (linux_root / "include/uapi/linux" / header).write_text(
                    f"/* test {header} */\n", encoding="utf-8"
                )
            fake_bin.mkdir()

            tool = fake_bin / "tool"
            tool.write_text(
                "#!/usr/bin/env bash\n"
                "if [[ ${1:-} == -print-resource-dir ]]; then\n"
                "  echo \"${FAKE_RESOURCE_DIR:?}\"\n"
                "fi\n",
                encoding="utf-8",
            )
            tool.chmod(0o755)
            for name in (
                "clang", "clang++", "ld.lld", "llvm-ar", "llvm-ranlib",
                "llvm-nm", "llvm-strip", "cmake",
            ):
                os.symlink(tool, fake_bin / name)

            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{fake_bin}:{env['PATH']}",
                    "CLANG": str(fake_bin / "clang"),
                    "CLANGXX": str(fake_bin / "clang++"),
                    "LLD": str(fake_bin / "ld.lld"),
                    "AR": str(fake_bin / "llvm-ar"),
                    "RANLIB": str(fake_bin / "llvm-ranlib"),
                    "NM": str(fake_bin / "llvm-nm"),
                    "STRIP": str(fake_bin / "llvm-strip"),
                    "LLVM_HOST_BUILD_ROOT": str(host_build),
                    "LINUX_UAPI_ROOT": str(linux_root),
                    "FAKE_RESOURCE_DIR": str(temp / "resource"),
                    "JOBS": "1",
                }
            )
            result = subprocess.run(
                [
                    "bash", str(RUNTIME_BUILD_SCRIPT),
                    "--llvm-root", str(llvm_root),
                    "--out-root", str(out_root),
                    "--musl-sysroot", str(sysroot),
                    "--cache-file", str(cache_file),
                    "--no-merge-sysroot",
                ],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(
                (out_root / "summary_phase-b.json").read_text(encoding="utf-8")
            )
            self.assertFalse(summary["merge_sysroot"])
            self.assertEqual(summary["copied_runtime_libs"], [])


if __name__ == "__main__":
    unittest.main()
