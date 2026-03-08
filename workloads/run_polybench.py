#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


WORKLOADS_DIR = Path(__file__).resolve().parent
GENERATED_DIR = WORKLOADS_DIR / "generated"
POLYBENCH_DIR = WORKLOADS_DIR / "third_party" / "PolyBenchC"


KERNEL_PATHS: dict[str, Path] = {
    "gemm": Path("linear-algebra/blas/gemm/gemm.c"),
    "jacobi-2d": Path("stencils/jacobi-2d/jacobi-2d.c"),
}


@dataclass(frozen=True)
class KernelResult:
    kernel: str
    exe: Path
    stdout: Path | None
    stderr: Path | None
    exit_code: int | None


def _run(cmd: list[str], *, cwd: Path | None = None, verbose: bool = False, **kwargs) -> subprocess.CompletedProcess[bytes]:
    if verbose:
        print("+", " ".join(shlex.quote(c) for c in cmd), file=sys.stderr)
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=False, **kwargs)


def _check_exe(path: Path, name: str) -> None:
    if not path.exists():
        raise SystemExit(f"error: {name} not found: {path}")
    if not os.access(path, os.X_OK):
        raise SystemExit(f"error: {name} not executable: {path}")


def _resolve_cc(arg_cc: str | None) -> Path:
    raw = arg_cc or os.environ.get("CC")
    if not raw:
        raise SystemExit("error: compiler is required; set --cc or CC")
    cc = Path(os.path.expanduser(raw))
    _check_exe(cc, "cc")
    return cc


def _resolve_kernel_source(kernel: str) -> Path:
    if kernel not in KERNEL_PATHS:
        known = ", ".join(sorted(KERNEL_PATHS))
        raise SystemExit(f"error: unsupported kernel '{kernel}'; supported: {known}")
    src = POLYBENCH_DIR / KERNEL_PATHS[kernel]
    if not src.exists():
        raise SystemExit(
            "error: PolyBench kernel source not found: "
            f"{src}\n"
            "hint: run workloads/fetch_third_party.sh"
        )
    return src


def _build_kernel(
    *,
    cc: Path,
    target: str,
    sysroot: str | None,
    opt: str,
    extra_cflags: list[str],
    kernel: str,
    out_dir: Path,
    verbose: bool,
) -> Path:
    util_dir = POLYBENCH_DIR / "utilities"
    polybench_c = util_dir / "polybench.c"
    src = _resolve_kernel_source(kernel)
    src_dir = src.parent

    if not polybench_c.exists():
        raise SystemExit(
            "error: missing PolyBench utility source: "
            f"{polybench_c}\n"
            "hint: run workloads/fetch_third_party.sh"
        )

    out_kernel = out_dir / kernel
    out_kernel.mkdir(parents=True, exist_ok=True)
    exe = out_kernel / f"{kernel}.elf"

    cmd = [str(cc), "--target", target, opt]
    if sysroot:
        cmd.append(f"--sysroot={sysroot}")
    cmd += [
        "-DPOLYBENCH_TIME",
        "-I",
        str(util_dir),
        "-I",
        str(src_dir),
        *extra_cflags,
        str(polybench_c),
        str(src),
        "-o",
        str(exe),
    ]

    p = _run(cmd, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.buffer.write(p.stdout)
        sys.stderr.buffer.write(p.stderr)
        raise SystemExit(f"error: build failed for kernel {kernel}")
    return exe


def _run_with_wrapper(
    *,
    exe: Path,
    kernel: str,
    run_command: str,
    timeout: float,
    logs_dir: Path,
    verbose: bool,
) -> tuple[Path, Path, int]:
    if "{exe}" in run_command:
        rendered = run_command.replace("{exe}", str(exe))
        cmd = shlex.split(rendered)
    else:
        cmd = [*shlex.split(run_command), str(exe)]

    stdout = logs_dir / f"polybench_{kernel}.stdout.txt"
    stderr = logs_dir / f"polybench_{kernel}.stderr.txt"

    p = _run(cmd, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    stdout.write_bytes(p.stdout or b"")
    stderr.write_bytes(p.stderr or b"")
    return stdout, stderr, p.returncode


def _write_report(path: Path, results: list[KernelResult], *, target: str, cc: Path, run_command: str | None) -> None:
    lines: list[str] = []
    lines.append("# PolyBench Report")
    lines.append("")
    lines.append(f"- Target: `{target}`")
    lines.append(f"- Compiler: `{cc}`")
    if run_command:
        lines.append(f"- Run command: `{run_command}`")
    else:
        lines.append("- Run command: _(not provided; build-only mode)_")
    lines.append("")
    lines.append("| Kernel | Executable | Ran | Exit | Stdout | Stderr |")
    lines.append("|---|---|---:|---:|---|---|")
    for r in results:
        ran = "yes" if r.exit_code is not None else "no"
        exit_code = str(r.exit_code) if r.exit_code is not None else "N/A"
        stdout = f"`{r.stdout}`" if r.stdout else "N/A"
        stderr = f"`{r.stderr}`" if r.stderr else "N/A"
        lines.append(f"| `{r.kernel}` | `{r.exe}` | {ran} | {exit_code} | {stdout} | {stderr} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_json(path: Path, results: list[KernelResult], *, target: str, cc: Path, run_command: str | None) -> bool:
    payload = {
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "target": target,
        "compiler": str(cc),
        "run_command": run_command,
        "results": [
            {
                "kernel": r.kernel,
                "executable": str(r.exe),
                "ran": r.exit_code is not None,
                "exit_code": r.exit_code,
                "stdout": str(r.stdout) if r.stdout else None,
                "stderr": str(r.stderr) if r.stderr else None,
            }
            for r in results
        ],
    }
    ok = all(r.exit_code in (None, 0) for r in results)
    payload["all_pass"] = ok
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return ok


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Build PolyBench/C kernels with an explicit cross target. "
            "Execution is optional via --run-command."
        )
    )
    ap.add_argument("--cc", default=None, help="Compiler path (or set CC)")
    ap.add_argument("--target", required=True, help="Target triple (required)")
    ap.add_argument("--sysroot", default=None, help="Optional sysroot path")
    ap.add_argument("--kernels", default="gemm,jacobi-2d", help="Comma-separated kernels")
    ap.add_argument("--opt", default="-O2", help="Optimization flag (default: -O2)")
    ap.add_argument("--cflag", action="append", default=[], help="Extra C flag (repeatable)")
    ap.add_argument(
        "--run-command",
        default=None,
        help="Optional execution wrapper command. Use {exe} placeholder or executable is appended.",
    )
    ap.add_argument("--timeout", type=float, default=120.0, help="Execution timeout seconds")
    ap.add_argument("--out-dir", default=str(GENERATED_DIR / "polybench"), help="Output directory")
    ap.add_argument("--json-out", default=None, help="Optional machine-readable summary path")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    cc = _resolve_cc(args.cc)
    kernels = [k.strip() for k in args.kernels.split(",") if k.strip()]
    if not kernels:
        raise SystemExit("error: --kernels resolved to empty set")

    out_dir = Path(os.path.expanduser(args.out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    results: list[KernelResult] = []
    for kernel in kernels:
        exe = _build_kernel(
            cc=cc,
            target=args.target,
            sysroot=args.sysroot,
            opt=args.opt,
            extra_cflags=args.cflag,
            kernel=kernel,
            out_dir=out_dir,
            verbose=args.verbose,
        )

        stdout: Path | None = None
        stderr: Path | None = None
        exit_code: int | None = None
        if args.run_command:
            try:
                stdout, stderr, exit_code = _run_with_wrapper(
                    exe=exe,
                    kernel=kernel,
                    run_command=args.run_command,
                    timeout=args.timeout,
                    logs_dir=logs_dir,
                    verbose=args.verbose,
                )
            except subprocess.TimeoutExpired:
                raise SystemExit(f"error: timeout running kernel {kernel}")

        results.append(KernelResult(kernel=kernel, exe=exe, stdout=stdout, stderr=stderr, exit_code=exit_code))

    report = out_dir / "report.md"
    _write_report(report, results, target=args.target, cc=cc, run_command=args.run_command)
    json_out = Path(os.path.expanduser(args.json_out)) if args.json_out else (out_dir / "result.json")
    ok = _write_json(json_out, results, target=args.target, cc=cc, run_command=args.run_command)
    print(f"ok: wrote {report}")
    print(f"ok: wrote {json_out}")
    if not ok:
        print("error: one or more PolyBench kernels exited nonzero", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
