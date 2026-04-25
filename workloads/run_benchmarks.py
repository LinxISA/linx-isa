#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import json
import os
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


WORKLOADS_DIR = Path(__file__).resolve().parent
GENERATED_DIR = WORKLOADS_DIR / "generated"
DEFAULT_PUBLISH_ELF_DIR = GENERATED_DIR / "elf"


@dataclass(frozen=True)
class BuildResult:
    name: str
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


def _common_flags(*, target: str, sysroot: str | None, opt: str, extra_cflags: list[str]) -> list[str]:
    flags: list[str] = ["-target", target, opt]
    if sysroot:
        flags.append(f"--sysroot={sysroot}")
    flags.extend(extra_cflags)
    return flags


def _resolve_runtime_lib(*, sysroot: str | None, runtime_lib: str | None) -> Path:
    if runtime_lib:
        path = Path(os.path.expanduser(runtime_lib))
        if not path.exists():
            raise SystemExit(f"error: runtime lib not found: {path}")
        return path
    if not sysroot:
        raise SystemExit("error: --sysroot is required for musl-static link mode")
    sysroot_path = Path(os.path.expanduser(sysroot))
    for candidate in (
        sysroot_path / "lib" / "liblinx_builtin_rt.a",
        sysroot_path / "lib" / "libclang_rt.builtins-linx64.a",
    ):
        if candidate.exists():
            return candidate
    raise SystemExit(f"error: no runtime lib found under {sysroot_path / 'lib'}")


def _static_link_flags(*, sysroot: str | None, runtime_lib: str | None, image_base: str | None) -> list[str]:
    if not sysroot:
        raise SystemExit("error: --sysroot is required for musl-static link mode")
    sysroot_path = Path(os.path.expanduser(sysroot))
    lib_dir = sysroot_path / "lib"
    crt1 = lib_dir / "rcrt1.o"
    if not crt1.exists():
        crt1 = lib_dir / "crt1.o"
    if not crt1.exists():
        raise SystemExit(f"error: missing static startup object under {lib_dir}")
    crti = lib_dir / "crti.o"
    crtn = lib_dir / "crtn.o"
    libc = lib_dir / "libc.a"
    for required in (crti, crtn, libc):
        if not required.exists():
            raise SystemExit(f"error: missing musl static runtime object: {required}")
    rt_archive = _resolve_runtime_lib(sysroot=sysroot, runtime_lib=runtime_lib)
    flags = [
        "-fuse-ld=lld",
        "-static",
        "-Wl,-pie",
        "-nostdlib",
        str(crt1),
        str(crti),
        str(rt_archive),
        str(libc),
        str(crtn),
    ]
    if image_base:
        flags.append(f"-Wl,--image-base={image_base}")
    return flags


def _publish_executable(exe: Path, published_name: str, publish_dir: Path | None) -> Path | None:
    if publish_dir is None:
        return None
    publish_dir.mkdir(parents=True, exist_ok=True)
    dst = publish_dir / published_name
    shutil.copy2(exe, dst)
    dst.chmod(dst.stat().st_mode | 0o111)
    return dst


def _build_coremark(
    *,
    cc: Path,
    target: str,
    sysroot: str | None,
    opt: str,
    extra_cflags: list[str],
    out_dir: Path,
    port: str,
    iterations: int,
    link_mode: str,
    runtime_lib: str | None,
    image_base: str | None,
    verbose: bool,
) -> Path:
    core_up = WORKLOADS_DIR / "coremark" / "upstream"
    port_dir = core_up / port
    if not port_dir.exists():
        raise SystemExit(f"error: coremark port directory missing: {port_dir}")

    srcs = [
        core_up / "core_list_join.c",
        core_up / "core_main.c",
        core_up / "core_matrix.c",
        core_up / "core_state.c",
        core_up / "core_util.c",
        port_dir / "core_portme.c",
    ]

    core_out = out_dir / "coremark"
    core_out.mkdir(parents=True, exist_ok=True)
    exe = core_out / "coremark.elf"

    flags = _common_flags(target=target, sysroot=sysroot, opt=opt, extra_cflags=extra_cflags)
    link_flags = []
    if link_mode == "musl-static":
        link_flags = _static_link_flags(sysroot=sysroot, runtime_lib=runtime_lib, image_base=image_base)

    cmd = [
        str(cc),
        *flags,
        "-std=gnu99",
        f"-DITERATIONS={iterations}",
        '-DFLAGS_STR="external-runner"',
        "-DPERFORMANCE_RUN=1",
        f"-I{core_up}",
        f"-I{port_dir}",
        *[str(s) for s in srcs],
        *link_flags,
        "-o",
        str(exe),
    ]
    p = _run(cmd, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.buffer.write(p.stdout)
        sys.stderr.buffer.write(p.stderr)
        raise SystemExit("error: coremark build failed")
    return exe


def _build_dhrystone(
    *,
    cc: Path,
    target: str,
    sysroot: str | None,
    opt: str,
    extra_cflags: list[str],
    out_dir: Path,
    runs: int,
    link_mode: str,
    runtime_lib: str | None,
    image_base: str | None,
    verbose: bool,
) -> Path:
    dhry = WORKLOADS_DIR / "dhrystone" / "upstream"
    srcs = [dhry / "dhry_1.c", dhry / "dhry_2.c"]

    out = out_dir / "dhrystone"
    out.mkdir(parents=True, exist_ok=True)
    exe = out / "dhrystone.elf"

    flags = _common_flags(target=target, sysroot=sysroot, opt=opt, extra_cflags=extra_cflags)
    link_flags = []
    if link_mode == "musl-static":
        link_flags = _static_link_flags(sysroot=sysroot, runtime_lib=runtime_lib, image_base=image_base)

    cmd = [
        str(cc),
        *flags,
        "-std=gnu89",
        "-DTIME",
        "-Wno-implicit-int",
        "-Wno-return-type",
        "-Wno-implicit-function-declaration",
        f"-DDHRY_ITERS={runs}",
        *[str(s) for s in srcs],
        *link_flags,
        "-o",
        str(exe),
    ]
    p = _run(cmd, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.buffer.write(p.stdout)
        sys.stderr.buffer.write(p.stderr)
        raise SystemExit("error: dhrystone build failed")
    return exe


def _run_with_wrapper(
    *,
    name: str,
    exe: Path,
    run_command: str,
    timeout: float,
    out_dir: Path,
    verbose: bool,
) -> tuple[Path, Path, int]:
    # If {exe} is not present, append executable path.
    if "{exe}" in run_command:
        rendered = run_command.replace("{exe}", str(exe))
        cmd = shlex.split(rendered)
    else:
        cmd = [*shlex.split(run_command), str(exe)]

    stdout = out_dir / f"{name}.stdout.txt"
    stderr = out_dir / f"{name}.stderr.txt"

    p = _run(cmd, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    stdout.write_bytes(p.stdout or b"")
    stderr.write_bytes(p.stderr or b"")
    return stdout, stderr, p.returncode


def _write_report(path: Path, results: list[BuildResult], *, target: str, cc: Path, run_command: str | None) -> None:
    lines: list[str] = []
    lines.append("# Benchmark Report")
    lines.append("")
    lines.append(f"- Target: `{target}`")
    lines.append(f"- Compiler: `{cc}`")
    if run_command:
        lines.append(f"- Run command: `{run_command}`")
    else:
        lines.append("- Run command: _(not provided; build-only mode)_")
    lines.append("")
    lines.append("| Benchmark | Executable | Ran | Exit | Stdout | Stderr |")
    lines.append("|---|---|---:|---:|---|---|")
    for r in results:
        ran = "yes" if r.exit_code is not None else "no"
        exit_code = str(r.exit_code) if r.exit_code is not None else "N/A"
        stdout = f"`{r.stdout}`" if r.stdout else "N/A"
        stderr = f"`{r.stderr}`" if r.stderr else "N/A"
        lines.append(f"| `{r.name}` | `{r.exe}` | {ran} | {exit_code} | {stdout} | {stderr} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_json(path: Path, results: list[BuildResult], *, target: str, cc: Path, run_command: str | None) -> bool:
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
                "name": r.name,
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
            "Build upstream CoreMark + Dhrystone with an explicit cross target. "
            "Execution is optional via --run-command."
        )
    )
    ap.add_argument("--cc", default=None, help="Compiler path (or set CC)")
    ap.add_argument("--target", required=True, help="Target triple (required)")
    ap.add_argument("--sysroot", default=None, help="Optional sysroot path")
    ap.add_argument("--opt", default="-O2", help="Optimization flag (default: -O2)")
    ap.add_argument("--cflag", action="append", default=[], help="Extra C flag (repeatable)")
    ap.add_argument("--coremark-port", choices=["posix", "simple"], default="posix")
    ap.add_argument("--coremark-iterations", type=int, default=1)
    ap.add_argument("--dhrystone-runs", type=int, default=1000)
    ap.add_argument(
        "--link-mode",
        choices=["default", "musl-static"],
        default="default",
        help="Link mode for direct clang invocations (default: default)",
    )
    ap.add_argument("--runtime-lib", default=None, help="Optional builtins runtime archive for musl-static mode")
    ap.add_argument("--image-base", default=None, help="Optional image base passed to the linker")
    ap.add_argument(
        "--run-command",
        default=None,
        help="Optional execution wrapper command. Use {exe} placeholder or the executable is appended.",
    )
    ap.add_argument("--timeout", type=float, default=120.0, help="Execution timeout seconds")
    ap.add_argument("--out-dir", default=str(GENERATED_DIR / "benchmarks"), help="Output directory")
    ap.add_argument(
        "--publish-elf-dir",
        default=str(DEFAULT_PUBLISH_ELF_DIR),
        help="Optional canonical ELF publish directory (use none to disable)",
    )
    ap.add_argument("--json-out", default=None, help="Optional machine-readable summary path")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    cc = _resolve_cc(args.cc)
    out_dir = Path(os.path.expanduser(args.out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    publish_dir = None
    if str(args.publish_elf_dir).lower() not in ("", "none", "null"):
        publish_dir = Path(os.path.expanduser(args.publish_elf_dir))

    coremark_exe = _build_coremark(
        cc=cc,
        target=args.target,
        sysroot=args.sysroot,
        opt=args.opt,
        extra_cflags=args.cflag,
        out_dir=out_dir,
        port=args.coremark_port,
        iterations=args.coremark_iterations,
        link_mode=args.link_mode,
        runtime_lib=args.runtime_lib,
        image_base=args.image_base,
        verbose=args.verbose,
    )
    dhrystone_exe = _build_dhrystone(
        cc=cc,
        target=args.target,
        sysroot=args.sysroot,
        opt=args.opt,
        extra_cflags=args.cflag,
        out_dir=out_dir,
        runs=args.dhrystone_runs,
        link_mode=args.link_mode,
        runtime_lib=args.runtime_lib,
        image_base=args.image_base,
        verbose=args.verbose,
    )

    published_coremark = _publish_executable(coremark_exe, "coremark.elf", publish_dir)
    published_dhrystone = _publish_executable(dhrystone_exe, "dhrystone.elf", publish_dir)

    logs_dir = out_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    results: list[BuildResult] = [
        BuildResult(name="coremark", exe=coremark_exe, stdout=None, stderr=None, exit_code=None),
        BuildResult(name="dhrystone", exe=dhrystone_exe, stdout=None, stderr=None, exit_code=None),
    ]

    if args.run_command:
        ran_results: list[BuildResult] = []
        for r in results:
            try:
                stdout, stderr, rc = _run_with_wrapper(
                    name=r.name,
                    exe=r.exe,
                    run_command=args.run_command,
                    timeout=args.timeout,
                    out_dir=logs_dir,
                    verbose=args.verbose,
                )
            except subprocess.TimeoutExpired:
                raise SystemExit(f"error: timeout running {r.name}")
            ran_results.append(BuildResult(name=r.name, exe=r.exe, stdout=stdout, stderr=stderr, exit_code=rc))
        results = ran_results

    report = out_dir / "report.md"
    _write_report(report, results, target=args.target, cc=cc, run_command=args.run_command)
    json_out = Path(os.path.expanduser(args.json_out)) if args.json_out else (out_dir / "result.json")
    ok = _write_json(json_out, results, target=args.target, cc=cc, run_command=args.run_command)
    print(f"ok: wrote {report}")
    print(f"ok: wrote {json_out}")
    if published_coremark:
        print(f"ok: published {published_coremark}")
    if published_dhrystone:
        print(f"ok: published {published_dhrystone}")
    if not ok:
        print("error: one or more benchmark runs exited nonzero", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
