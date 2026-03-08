#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LIBC_DIR = REPO_ROOT / "avs" / "runtime" / "freestanding"
LIBC_INCLUDE = LIBC_DIR / "include"
LIBC_SRC = LIBC_DIR / "src"

SCRIPT_DIR = Path(__file__).resolve().parent


def _check_exe(p: Path, what: str) -> None:
    if not p.exists():
        raise SystemExit(f"error: {what} not found: {p}")
    if not os.access(p, os.X_OK):
        raise SystemExit(f"error: {what} not executable: {p}")


def _run(cmd: list[str], *, verbose: bool, **kwargs) -> subprocess.CompletedProcess[bytes]:
    if verbose:
        print("+", " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd, check=False, **kwargs)


def _default_clang() -> Path | None:
    env = os.environ.get("CLANG")
    if env:
        return Path(os.path.expanduser(env))
    cand = Path.home() / "llvm-project" / "build-linxisa-clang" / "bin" / "clang"
    return cand if cand.exists() else None


def _default_lld(clang: Path | None) -> Path | None:
    env = os.environ.get("LLD")
    if env:
        return Path(os.path.expanduser(env))
    if clang:
        cand = clang.parent / "ld.lld"
        if cand.exists():
            return cand
    return None


def _default_qemu() -> Path | None:
    env = os.environ.get("QEMU")
    if env:
        return Path(os.path.expanduser(env))
    cand_tci = Path.home() / "qemu" / "build-tci" / "qemu-system-linx64"
    if cand_tci.exists():
        return cand_tci
    cand = Path.home() / "qemu" / "build" / "qemu-system-linx64"
    return cand if cand.exists() else None


def _default_llvm_tool(clang: Path, tool: str) -> Path | None:
    cand = clang.parent / tool
    return cand if cand.exists() else None


def _parse_linx_insn_count(stdout: bytes, stderr: bytes) -> int | None:
    text = (stderr or b"") + b"\n" + (stdout or b"")
    m = None
    for mm in re.finditer(rb"LINX_INSN_COUNT=(\d+)", text):
        m = mm
    if not m:
        return None
    return int(m.group(1), 10)


def _codelet_base_dir(ctuning_root: Path) -> Path | None:
    candidates = [
        ctuning_root / "program",
        ctuning_root / "out",
        ctuning_root,
    ]
    for candidate in candidates:
        if candidate.exists() and any(candidate.glob("milepost-codelet-*")):
            return candidate
    return None


def _collect_codelet_dirs(ctuning_root: Path) -> list[Path]:
    base_dir = _codelet_base_dir(ctuning_root)
    if base_dir is None:
        return []
    dirs = sorted(base_dir.glob("milepost-codelet-*"))
    return [d for d in dirs if d.is_dir()]


def _find_sources(codelet_dir: Path) -> tuple[list[Path], list[Path]]:
    wrappers = sorted(codelet_dir.glob("*.wrapper.c"))
    codelets = sorted(p for p in codelet_dir.glob("*.c") if p not in wrappers)
    return codelets, wrappers


def _build_runtime(
    clang: Path,
    target: str,
    out_dir: Path,
    *,
    verbose: bool,
) -> list[Path]:
    runtime_dir = out_dir / "_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    def cc(src: Path, obj_name: str, extra: list[str] | None = None) -> Path:
        obj = runtime_dir / obj_name
        cflags = [
            "-target",
            target,
            "-O2",
            "-ffreestanding",
            "-fno-builtin",
            "-fno-stack-protector",
            "-fno-asynchronous-unwind-tables",
            "-fno-unwind-tables",
            "-fno-exceptions",
            "-fno-jump-tables",
            "-nostdlib",
            f"-I{LIBC_INCLUDE}",
        ]
        if extra:
            cflags += extra
        cmd = [str(clang), *cflags, "-c", str(src), "-o", str(obj)]
        p = _run(cmd, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            sys.stderr.buffer.write(p.stderr)
            raise SystemExit(f"error: runtime compile failed: {src}")
        return obj

    startup = cc(SCRIPT_DIR / "startup.c", "startup.o")
    astex = cc(SCRIPT_DIR / "astex_runtime.c", "astex_runtime.o", extra=["-Wno-unknown-pragmas"])

    syscall = cc(LIBC_SRC / "syscall.c", "syscall.o")
    stdio = cc(LIBC_SRC / "stdio" / "stdio.c", "stdio.o")
    stdlib = cc(LIBC_SRC / "stdlib" / "stdlib.c", "stdlib.o")
    mem = cc(LIBC_SRC / "string" / "mem.c", "mem.o")
    string = cc(LIBC_SRC / "string" / "str.c", "str.o")
    math = cc(LIBC_SRC / "math" / "math.c", "math.o")

    # Soft-fp is large and the backend bring-up occasionally misses patterns at -O2;
    # keep it unoptimized like the existing qemu-tests runner.
    softfp = cc(LIBC_SRC / "softfp" / "softfp.c", "softfp.o", extra=["-O0"])

    return [startup, astex, syscall, stdio, stdlib, mem, string, math, softfp]


def _build_data_object(clang: Path, target: str, codelet_dir: Path, out_dir: Path, *, verbose: bool) -> Path:
    data_path = codelet_dir / "codelet.data"
    if not data_path.exists():
        raise SystemExit(f"error: missing codelet.data: {data_path}")

    asm = out_dir / "codelet_data.s"
    asm.write_text(
        "\n".join(
            [
                ".section .rodata",
                ".global __astex_codelet_data",
                ".global __astex_codelet_data_end",
                "__astex_codelet_data:",
                f'  .incbin "{data_path}"',
                "__astex_codelet_data_end:",
                "",
            ]
        )
        + "\n"
    )

    obj = out_dir / "codelet_data.o"
    cmd = [str(clang), "-target", target, "-c", str(asm), "-o", str(obj)]
    p = _run(cmd, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.buffer.write(p.stderr)
        raise SystemExit(f"error: failed to assemble {asm}")
    return obj


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build and optionally run ctuning Milepost codelets with explicit cross-target settings."
        )
    )
    parser.add_argument("--ctuning-root", default=str(REPO_ROOT / "workloads" / "ctuning"))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "workloads" / "ctuning" / "out"))
    parser.add_argument("--target", required=True)
    parser.add_argument("--clang", default=None)
    parser.add_argument("--lld", default=None)
    parser.add_argument("--qemu", default=None)
    parser.add_argument("--filter", help="Regex to select codelet directories by name.")
    parser.add_argument("--limit", type=int, default=0, help="Max number of codelets to build/run (0 = no limit).")
    parser.add_argument("--compile-only", action="store_true", help="Only build; do not run QEMU.")
    parser.add_argument("--run", action="store_true", help="Run under QEMU after building.")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--insn-counts-out",
        default=None,
        help="Write a CSV with LINX_INSN_COUNT per codelet (default: <out-dir>/insn_counts.csv when --run).",
    )
    parser.add_argument(
        "--objdump-dir",
        default=None,
        help="If set, write `llvm-objdump -d` outputs here (one file per codelet).",
    )
    parser.add_argument(
        "--insn-hist-plugin",
        default=None,
        help="Optional QEMU plugin `.so` to write a dynamic mnemonic histogram (expects `out=...` arg).",
    )
    parser.add_argument(
        "--insn-hist-out-dir",
        default=None,
        help="Directory to write per-codelet dynamic hist JSON (requires --insn-hist-plugin).",
    )
    parser.add_argument(
        "--summary-json",
        default=None,
        help="Write a machine-readable execution summary (default: <out-dir>/result.json).",
    )
    args = parser.parse_args(argv)

    ctuning_root = Path(os.path.expanduser(args.ctuning_root))
    if _codelet_base_dir(ctuning_root) is None:
        raise SystemExit(f"error: ctuning root does not look valid: {ctuning_root}")

    clang = Path(os.path.expanduser(args.clang)) if args.clang else (_default_clang() or None)
    if not clang:
        raise SystemExit("error: clang not found; set --clang or CLANG")
    lld = Path(os.path.expanduser(args.lld)) if args.lld else (_default_lld(clang) or None)
    if not lld:
        raise SystemExit("error: ld.lld not found; set --lld or LLD")
    qemu = Path(os.path.expanduser(args.qemu)) if args.qemu else (_default_qemu() or None)

    _check_exe(clang, "clang")
    _check_exe(lld, "ld.lld")
    if args.run and not args.compile_only:
        if not qemu:
            raise SystemExit("error: qemu-system-linx64 not found; set --qemu or QEMU")
        _check_exe(qemu, "qemu-system-linx64")

    do_run = args.run and (not args.compile_only)

    llvm_objdump = _default_llvm_tool(clang, "llvm-objdump")
    if args.objdump_dir:
        if not llvm_objdump:
            raise SystemExit("error: llvm-objdump not found next to clang; set CLANG to a full LLVM build")
        _check_exe(llvm_objdump, "llvm-objdump")
        Path(os.path.expanduser(args.objdump_dir)).mkdir(parents=True, exist_ok=True)

    insn_hist_plugin: Path | None = None
    insn_hist_out_dir: Path | None = None
    if args.insn_hist_plugin:
        insn_hist_plugin = Path(os.path.expanduser(args.insn_hist_plugin))
        _check_exe(insn_hist_plugin, "insn hist plugin")
        if not args.insn_hist_out_dir:
            raise SystemExit("error: --insn-hist-plugin requires --insn-hist-out-dir")
        insn_hist_out_dir = Path(os.path.expanduser(args.insn_hist_out_dir))
        insn_hist_out_dir.mkdir(parents=True, exist_ok=True)

    out_root = Path(os.path.expanduser(args.out_dir))
    out_root.mkdir(parents=True, exist_ok=True)

    counts_path: Path | None = None
    counts_fp = None
    if do_run:
        counts_path = Path(os.path.expanduser(args.insn_counts_out)) if args.insn_counts_out else (out_root / "insn_counts.csv")
        counts_fp = counts_path.open("w", encoding="utf-8")
        counts_fp.write("codelet,insn_count\n")

    runtime_objs = _build_runtime(clang, args.target, out_root, verbose=args.verbose)

    codelet_dirs = _collect_codelet_dirs(ctuning_root)
    if args.filter:
        rx = re.compile(args.filter)
        codelet_dirs = [d for d in codelet_dirs if rx.search(d.name)]

    if args.limit and args.limit > 0:
        codelet_dirs = codelet_dirs[: args.limit]

    if not codelet_dirs:
        raise SystemExit("error: no codelets selected")

    passed = 0
    failed = 0
    summary_rows: list[dict[str, object]] = []

    for d in codelet_dirs:
        codelets, wrappers = _find_sources(d)
        if not wrappers or not codelets:
            print(f"[skip] {d.name} (missing wrapper/codelet sources)", file=sys.stderr)
            summary_rows.append({"codelet": d.name, "status": "skipped_missing_sources"})
            continue

        out_dir = out_root / d.name
        out_dir.mkdir(parents=True, exist_ok=True)

        objs: list[Path] = []
        # Embed codelet.data
        objs.append(_build_data_object(clang, args.target, d, out_dir, verbose=args.verbose))

        common_cflags = [
            "-target",
            args.target,
            "-O2",
            "-ffreestanding",
            "-fno-builtin",
            "-fno-stack-protector",
            "-fno-asynchronous-unwind-tables",
            "-fno-unwind-tables",
            "-fno-exceptions",
            "-fno-jump-tables",
            "-nostdlib",
            f"-I{LIBC_INCLUDE}",
            f"-I{d}",
            "-include",
            "math.h",
            "-Wno-unknown-pragmas",
            "-Wno-incompatible-pointer-types",
        ]

        def compile_one(src: Path) -> Path:
            obj = out_dir / (src.stem + ".o")
            cmd = [str(clang), *common_cflags, "-c", str(src), "-o", str(obj)]
            p = _run(cmd, verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                sys.stderr.buffer.write(p.stderr)
                raise SystemExit(f"error: compile failed: {src}")
            return obj

        for src in codelets + wrappers:
            objs.append(compile_one(src))

        out_obj = out_dir / "codelet.o"
        link_cmd = [str(lld), "-r", "-o", str(out_obj), *[str(o) for o in (runtime_objs + objs)]]
        p = _run(link_cmd, verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            sys.stderr.buffer.write(p.stderr)
            print(f"[fail] {d.name} (link)", file=sys.stderr)
            failed += 1
            summary_rows.append({"codelet": d.name, "status": "link_failed", "return_code": p.returncode})
            continue

        print(f"[ok] build {d.name}")

        if args.objdump_dir:
            assert llvm_objdump is not None
            objdump_out = Path(os.path.expanduser(args.objdump_dir)) / f"{d.name}.objdump.txt"
            p_od = _run(
                [str(llvm_objdump), "-d", f"--triple={args.target}", str(out_obj)],
                verbose=args.verbose,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if p_od.returncode != 0:
                sys.stderr.buffer.write(p_od.stderr)
                raise SystemExit(f"error: llvm-objdump failed: {d.name}")
            objdump_out.write_bytes(p_od.stdout)

        if not do_run:
            passed += 1
            summary_rows.append({"codelet": d.name, "status": "built", "object": str(out_obj)})
            continue

        assert qemu is not None
        qemu_cmd = [
            str(qemu),
            "-machine",
            "virt",
            "-kernel",
            str(out_obj),
            "-nographic",
            "-monitor",
            "none",
        ]
        if insn_hist_plugin and insn_hist_out_dir:
            hist_out = insn_hist_out_dir / f"{d.name}.dyn_insn_hist.json"
            qemu_cmd += ["-plugin", f"{insn_hist_plugin},out={hist_out},top=200"]
        try:
            p = _run(
                qemu_cmd,
                verbose=args.verbose,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired as e:
            print(f"[fail] {d.name} (timeout {args.timeout:.1f}s)", file=sys.stderr)
            if e.stdout:
                sys.stderr.write("---- guest stdout (tail) ----\n")
                sys.stderr.buffer.write(e.stdout[-4000:])
                sys.stderr.write("\n")
            if e.stderr:
                sys.stderr.write("---- qemu stderr (tail) ----\n")
                sys.stderr.buffer.write(e.stderr[-4000:])
                sys.stderr.write("\n")
            failed += 1
            summary_rows.append({"codelet": d.name, "status": "timeout", "timeout_s": args.timeout})
            continue

        if p.returncode != 0:
            print(f"[fail] {d.name} (qemu exit={p.returncode})", file=sys.stderr)
            if p.stdout:
                sys.stderr.write("---- guest stdout (tail) ----\n")
                sys.stderr.buffer.write(p.stdout[-4000:])
                sys.stderr.write("\n")
            if p.stderr:
                sys.stderr.write("---- qemu stderr (tail) ----\n")
                sys.stderr.buffer.write(p.stderr[-4000:])
                sys.stderr.write("\n")
            failed += 1
            summary_rows.append({"codelet": d.name, "status": "run_failed", "return_code": p.returncode})
            continue

        insn_count = _parse_linx_insn_count(p.stdout or b"", p.stderr or b"")

        if insn_count is not None:
            print(f"[ok] run   {d.name} insns={insn_count}")
        else:
            print(f"[ok] run   {d.name} (no insn count)")

        if counts_fp:
            counts_fp.write(f"{d.name},{insn_count if insn_count is not None else ''}\n")

        passed += 1
        summary_rows.append(
            {
                "codelet": d.name,
                "status": "passed",
                "object": str(out_obj),
                "insn_count": insn_count,
            }
        )

    print(f"summary: passed={passed} failed={failed}")
    if counts_fp:
        counts_fp.close()
        print(f"wrote: {counts_path}")
    summary_path = Path(os.path.expanduser(args.summary_json)) if args.summary_json else (out_root / "result.json")
    summary_payload = {
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "ctuning_root": str(ctuning_root),
        "target": args.target,
        "compile_only": args.compile_only,
        "run": args.run,
        "selected_codelets": len(codelet_dirs),
        "passed": passed,
        "failed": failed,
        "results": summary_rows,
        "all_pass": failed == 0,
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote: {summary_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
