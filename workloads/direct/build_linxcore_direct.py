#!/usr/bin/env python3
"""Build and validate direct-boot LinxCore benchmark ELFs.

This lane is semantic bring-up evidence only. It deliberately builds fixed
ET_EXEC images for cycle-model and RTL direct execution instead of hosted PIEs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
OUT_ROOT = REPO_ROOT / "workloads" / "generated" / "linxcore-r678-direct"
ENTRY = 0x10000
UART = 0x10000000
FINISHER = 0x10009000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], *, cwd: Path = REPO_ROOT, env: dict[str, str] | None = None,
        timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def require_ok(result: subprocess.CompletedProcess[str], action: str) -> None:
    if result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(f"error: {action} failed with status {result.returncode}")


def default_tool(name: str) -> Path:
    candidate = REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / name
    if candidate.exists():
        return candidate
    found = shutil.which(name)
    if found:
        return Path(found)
    raise SystemExit(f"error: {name} not found")


def git_rev(path: Path) -> str | None:
    result = run(["git", "-C", str(path), "rev-parse", "HEAD"])
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_dirty(path: Path) -> bool:
    result = run(["git", "-C", str(path), "status", "--porcelain"])
    return bool(result.stdout.strip()) if result.returncode == 0 else True


def tool_version(path: Path) -> str:
    result = run([str(path), "--version"])
    if result.returncode != 0:
        return "unavailable"
    return result.stdout.splitlines()[0] if result.stdout else "unavailable"


def clang_resource_include(clang: Path) -> Path:
    result = run([str(clang), "-print-resource-dir"])
    require_ok(result, "query clang resource dir")
    include = Path(result.stdout.strip()) / "include"
    if not include.exists():
        raise SystemExit(f"error: clang resource include not found: {include}")
    return include


def source(path: str, *, defines: list[str] | None = None,
           cflags: list[str] | None = None) -> dict[str, object]:
    p = REPO_ROOT / path
    return {"path": path, "sha256": sha256(p), "defines": defines or [], "cflags": cflags or []}


def workloads() -> dict[str, dict[str, object]]:
    runtime = [
        "avs/runtime/freestanding/src/syscall.c",
        "avs/runtime/freestanding/src/stdio/stdio.c",
        "avs/runtime/freestanding/src/stdlib/stdlib.c",
        "avs/runtime/freestanding/src/string/mem.c",
        "avs/runtime/freestanding/src/string/str.c",
        "avs/runtime/freestanding/src/softfp/softfp.c",
    ]
    return {
        "coremark": {
            "iterations": 1,
            "oracle": [
                "Correct operation validated",
                "seedcrc          : 0xe9f5",
                "[0]crclist       : 0xe714",
                "[0]crcmatrix     : 0x1fd7",
                "[0]crcstate      : 0x8e3a",
            ],
            "sources": [
                source("workloads/coremark/upstream/core_list_join.c"),
                source("workloads/coremark/upstream/core_main.c"),
                source("workloads/coremark/upstream/core_matrix.c"),
                source("workloads/coremark/upstream/core_state.c"),
                source("workloads/coremark/upstream/core_util.c"),
                source("workloads/coremark/linx-direct/core_portme.c"),
                source("workloads/direct/startup.c"),
                *[source(p) for p in runtime],
            ],
            "cflags": [
                "-DPERFORMANCE_RUN=1",
                "-DITERATIONS=1",
                "-DMULTITHREAD=1",
                "-DMEM_METHOD=MEM_MALLOC",
                "-DMEM_LOCATION=\"HEAP\"",
                "-DMAIN_HAS_NOARGC=1",
                "-DFLAGS_STR=\"-O2 semantic direct-boot\"",
                "-DHAS_STDIO=1",
                "-DHAS_PRINTF=1",
                "-DHAS_FLOAT=0",
                "-DHAS_TIME_H=0",
                "-DUSE_CLOCK=0",
                "-Iworkloads/coremark/upstream",
                "-Iworkloads/coremark/linx-direct",
            ],
        },
        "dhrystone": {
            "iterations": 1,
            "oracle": [
                "Execution ends",
                "Int_Glob:            5",
                "Bool_Glob:           1",
                "Ch_1_Glob:           A",
                "Ch_2_Glob:           B",
                "Arr_1_Glob[8]:       7",
                "Int_1_Loc:           5",
                "Int_2_Loc:           13",
                "Int_3_Loc:           7",
                "DHRYSTONE PROGRAM, 1'ST STRING",
                "DHRYSTONE PROGRAM, 2'ND STRING",
            ],
            "sources": [
                source(
                    "workloads/dhrystone/upstream/dhry_1.c",
                    defines=["main=dhry_main"],
                    cflags=["-std=gnu89", "-Wno-implicit-int", "-Wno-implicit-function-declaration", "-Wno-deprecated-non-prototype"],
                ),
                source(
                    "workloads/dhrystone/upstream/dhry_2.c",
                    cflags=["-std=gnu89", "-Wno-implicit-int", "-Wno-implicit-function-declaration", "-Wno-deprecated-non-prototype"],
                ),
                source("workloads/direct/dhrystone_main.c"),
                source("workloads/direct/dhrystone_time.c"),
                source("workloads/direct/startup.c"),
                *[source(p) for p in runtime],
            ],
            "cflags": [
                "-DTIME",
                "-DDHRY_ITERS=1",
                "-Iworkloads/dhrystone/upstream",
            ],
        },
    }


def compile_source(clang: Path, out_dir: Path, src: dict[str, object], cflags: list[str],
                   common_flags: list[str]) -> Path:
    src_path = REPO_ROOT / str(src["path"])
    obj = out_dir / "obj" / (src_path.stem + "-" + hashlib.sha1(str(src_path).encode()).hexdigest()[:8] + ".o")
    obj.parent.mkdir(parents=True, exist_ok=True)
    per_source_defines = [f"-D{d}" for d in src.get("defines", [])]
    per_source_cflags = list(src.get("cflags", []))
    cmd = [
        str(clang),
        *common_flags,
        *cflags,
        *per_source_cflags,
        *per_source_defines,
        "-c",
        str(src_path),
        "-o",
        str(obj),
    ]
    require_ok(run(cmd), f"compile {src_path}")
    return obj


def parse_readelf(readelf: Path, elf: Path) -> dict[str, object]:
    header = run([str(readelf), "-h", str(elf)])
    phdrs = run([str(readelf), "-l", str(elf)])
    require_ok(header, "read ELF header")
    require_ok(phdrs, "read program headers")
    text = header.stdout
    if "Type:" not in text or "EXEC" not in text:
        raise SystemExit(f"error: {elf} is not ET_EXEC")
    if "Machine:" not in text or "Linx" not in text:
        raise SystemExit(f"error: {elf} is not a Linx ELF")
    entry_line = next((line for line in text.splitlines() if "Entry point address:" in line), "")
    entry = int(entry_line.rsplit(":", 1)[1].strip(), 16)
    if entry != ENTRY:
        raise SystemExit(f"error: {elf} entry is 0x{entry:x}, expected 0x{ENTRY:x}")

    loads: list[dict[str, int]] = []
    for line in phdrs.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[0] == "LOAD":
            loads.append({
                "offset": int(fields[1], 16),
                "vaddr": int(fields[2], 16),
                "paddr": int(fields[3], 16),
                "filesz": int(fields[4], 16),
                "memsz": int(fields[5], 16),
            })
    if not loads:
        raise SystemExit(f"error: {elf} has no PT_LOAD segments")
    for load in loads:
        end = load["vaddr"] + load["memsz"]
        if load["vaddr"] < ENTRY or end >= UART:
            raise SystemExit(f"error: {elf} load range 0x{load['vaddr']:x}-0x{end:x} overlaps platform MMIO")
    return {"type": "EXEC", "machine": "Linx", "entry": f"0x{entry:x}", "loads": loads}


def qemu_binary() -> Path | None:
    for candidate in (
        REPO_ROOT / "emulator" / "qemu" / "build-linx" / "qemu-system-linx64",
        REPO_ROOT / "emulator" / "qemu" / "build" / "qemu-system-linx64",
    ):
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    env_qemu = os.environ.get("QEMU")
    if env_qemu:
        p = Path(env_qemu)
        if p.exists():
            return p
    return None


def run_qemu_oracle(elf: Path, oracle: list[str], timeout: int) -> dict[str, object]:
    qemu = qemu_binary()
    if qemu is None:
        return {"status": "SKIPPED", "reason": "qemu-system-linx64 not found"}
    env = os.environ.copy()
    env["LINX_VIRT_TEST_FINISHER"] = "1"
    cmd = [str(qemu), "-machine", "virt", "-bios", "none", "-kernel", str(elf),
           "-nographic", "-monitor", "none"]
    try:
        result = run(cmd, env=env, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return {"status": "TIMEOUT", "command": cmd, "output_sha256": hashlib.sha256(output.encode()).hexdigest()}
    output = result.stdout + result.stderr
    missing = [marker for marker in oracle if marker not in output]
    status = "PASS" if result.returncode == 0 and not missing and "ERROR" not in output else "FAIL"
    return {
        "status": status,
        "returncode": result.returncode,
        "command": cmd,
        "missing_markers": missing,
        "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
        "output": output,
    }


def build(args: argparse.Namespace) -> int:
    clang = Path(args.clang) if args.clang else default_tool("clang")
    readelf = Path(args.readelf) if args.readelf else default_tool("llvm-readelf")
    linker = REPO_ROOT / "workloads" / "direct" / "linx-benchmark.ld"
    resource_include = clang_resource_include(clang)
    common_flags = [
        "--target=linx64-unknown-elf",
        "-O2",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-jump-tables",
        "-nostdinc",
        "-isystem" + str(resource_include),
        "-I" + str(REPO_ROOT / "avs" / "runtime" / "freestanding" / "include"),
        "-DLINX_HEAP_SIZE=65536",
    ]

    summary: dict[str, object] = {"benchmarks": {}}
    for name, cfg in workloads().items():
        out_dir = OUT_ROOT / name
        if args.clean and out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        objects = [
            compile_source(clang, out_dir, src, list(cfg["cflags"]), common_flags)
            for src in cfg["sources"]
        ]
        elf = out_dir / f"{name}.elf"
        link_cmd = [
            str(clang),
            "--target=linx64-unknown-elf",
            "-nostdlib",
            "-Wl,-T," + str(linker),
            "-Wl,--build-id=none",
            *[str(obj) for obj in objects],
            "-o",
            str(elf),
        ]
        require_ok(run(link_cmd), f"link {name}")
        elf_info = parse_readelf(readelf, elf)
        qemu = run_qemu_oracle(elf, list(cfg["oracle"]), args.qemu_timeout) if args.run_qemu else None
        manifest = {
            "schema": "linxcore.direct-benchmark.v1",
            "workload": name,
            "lane": "direct-freestanding-et-exec",
            "semantic_only": True,
            "score_claimed": False,
            "iterations": cfg["iterations"],
            "entry_contract": {"entry": f"0x{ENTRY:x}", "uart": f"0x{UART:x}", "finisher": f"0x{FINISHER:x}"},
            "elf": {"path": str(elf.relative_to(REPO_ROOT)), "sha256": sha256(elf), "size_bytes": elf.stat().st_size, **elf_info},
            "tools": {
                "clang": {"path": str(clang), "version": tool_version(clang), "sha256": sha256(clang)},
                "llvm_readelf": {"path": str(readelf), "version": tool_version(readelf), "sha256": sha256(readelf)},
            },
            "revisions": {
                "superproject": {"sha": git_rev(REPO_ROOT), "dirty": git_dirty(REPO_ROOT)},
                "llvm": {"sha": git_rev(REPO_ROOT / "compiler" / "llvm"), "dirty": git_dirty(REPO_ROOT / "compiler" / "llvm")},
                "qemu": {"sha": git_rev(REPO_ROOT / "emulator" / "qemu"), "dirty": git_dirty(REPO_ROOT / "emulator" / "qemu")},
                "linxcore_model": {"sha": git_rev(REPO_ROOT / "tools" / "LinxCoreModel"), "dirty": git_dirty(REPO_ROOT / "tools" / "LinxCoreModel")},
                "linxcore_rtl": {"sha": git_rev(REPO_ROOT / "rtl" / "LinxCore"), "dirty": git_dirty(REPO_ROOT / "rtl" / "LinxCore")},
            },
            "inputs": [source("workloads/direct/linx-benchmark.ld"), *cfg["sources"]],
            "commands": {"common_compile_flags": common_flags, "workload_cflags": cfg["cflags"], "link": link_cmd},
            "terminal_oracle": {"kind": "uart_markers_plus_finisher_pass", "markers": cfg["oracle"], "finisher_pass": "0x5555"},
            "qemu_semantic_check": qemu,
        }
        manifest_path = out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        summary["benchmarks"][name] = {
            "elf": manifest["elf"],
            "manifest": str(manifest_path.relative_to(REPO_ROOT)),
            "qemu_status": None if qemu is None else qemu["status"],
        }
        if qemu is not None and qemu["status"] != "PASS":
            raise SystemExit(f"error: QEMU semantic check failed for {name}: {qemu['status']}")
    (OUT_ROOT / "manifest-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def check(_: argparse.Namespace) -> int:
    ok = True
    for name, cfg in workloads().items():
        manifest_path = OUT_ROOT / name / "manifest.json"
        if not manifest_path.exists():
            print(f"missing manifest: {manifest_path}", file=sys.stderr)
            ok = False
            continue
        manifest = json.loads(manifest_path.read_text())
        elf = REPO_ROOT / manifest["elf"]["path"]
        if manifest["workload"] != name or manifest["lane"] != "direct-freestanding-et-exec":
            print(f"invalid manifest identity: {manifest_path}", file=sys.stderr)
            ok = False
        if manifest["semantic_only"] is not True or manifest["score_claimed"] is not False:
            print(f"invalid scoring contract: {manifest_path}", file=sys.stderr)
            ok = False
        if manifest["iterations"] != cfg["iterations"]:
            print(f"invalid iteration count: {manifest_path}", file=sys.stderr)
            ok = False
        if not elf.exists() or sha256(elf) != manifest["elf"]["sha256"]:
            print(f"invalid ELF hash: {elf}", file=sys.stderr)
            ok = False
        if manifest["elf"]["type"] != "EXEC" or manifest["elf"]["entry"] != f"0x{ENTRY:x}":
            print(f"invalid ELF shape: {elf}", file=sys.stderr)
            ok = False
        if manifest["terminal_oracle"]["finisher_pass"] != "0x5555":
            print(f"invalid terminal oracle: {manifest_path}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build ELFs and manifests")
    b.add_argument("--clean", action="store_true")
    b.add_argument("--clang")
    b.add_argument("--readelf")
    b.add_argument("--run-qemu", action="store_true")
    b.add_argument("--qemu-timeout", type=int, default=30)
    b.set_defaults(func=build)
    c = sub.add_parser("check", help="validate generated manifests and ELFs")
    c.set_defaults(func=check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
