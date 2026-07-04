#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import select
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
BRINGUP_DIR = REPO_ROOT / "tools" / "bringup"
if str(BRINGUP_DIR) not in sys.path:
    sys.path.insert(0, str(BRINGUP_DIR))

from qemu_build_paths import default_qemu_binary, qemu_binary_provenance

STAGE_A_BENCHES = [
    "999.specrand_ir",
    "505.mcf_r",
    "531.deepsjeng_r",
]

STAGE_B_BENCHES = [
    "500.perlbench_r",
    "502.gcc_r",
    "505.mcf_r",
    "520.omnetpp_r",
    "523.xalancbmk_r",
    "525.x264_r",
    "531.deepsjeng_r",
    "541.leela_r",
    "557.xz_r",
    "999.specrand_ir",
]

ALL_BENCHES = STAGE_B_BENCHES

EXE_MAP: dict[str, list[str]] = {
    "500.perlbench_r": ["perlbench_r_base.mytest-m64"],
    "502.gcc_r": ["cpugcc_r_base.mytest-m64"],
    "505.mcf_r": ["mcf_r_base.mytest-m64"],
    "520.omnetpp_r": ["omnetpp_r_base.mytest-m64"],
    "523.xalancbmk_r": ["cpuxalan_r_base.mytest-m64"],
    "525.x264_r": ["x264_r_base.mytest-m64", "imagevalidate_525_base.mytest-m64"],
    "531.deepsjeng_r": ["deepsjeng_r_base.mytest-m64"],
    "541.leela_r": ["leela_r_base.mytest-m64"],
    "557.xz_r": ["xz_r_base.mytest-m64"],
    "999.specrand_ir": ["specrand_ir_base.mytest-m64"],
}

COMPARE_ARGS: dict[str, list[str]] = {
    "500.perlbench_r": ["-m", "-l", "10", "--floatcompare", "--nonansupport"],
    "502.gcc_r": ["-m", "-l", "10", "--floatcompare", "--nonansupport"],
    "505.mcf_r": ["-m", "-l", "10"],
    "520.omnetpp_r": ["-m", "-l", "10", "--abstol", "1e-06", "--reltol", "1e-05"],
    "523.xalancbmk_r": ["-m", "-l", "10"],
    "525.x264_r": ["-m", "-l", "10", "--reltol", "0.085"],
    "531.deepsjeng_r": ["-m", "-l", "10", "--obiwan"],
    "541.leela_r": ["-m", "-l", "10"],
    "557.xz_r": ["-m", "-l", "10"],
    "999.specrand_ir": ["-m", "-l", "10", "--floatcompare", "--nonansupport"],
}

SRC_RUN_DIR = "run_base_refrate_mytest-m64.0000"
EMPTY_STDIN_NAME = ".linx_empty_stdin"


def _kernel_cmdline_has_arg(cmdline: str, name: str) -> bool:
    prefix = f"{name}="
    try:
        parts = shlex.split(cmdline)
    except ValueError:
        parts = cmdline.split()
    return any(part == name or part.startswith(prefix) for part in parts)


def _append_kernel_arg_if_absent(cmdline: str, name: str, value: str) -> str:
    if _kernel_cmdline_has_arg(cmdline, name):
        return cmdline
    extra = f"{name}={value}"
    return f"{cmdline} {extra}".strip()


def _build_kernel_append(transport: str, append_extra: str) -> str:
    append = "lpj=1000000 loglevel=8 console=ttyS0 kfence.sample_interval=0"
    disable_timer_irq = os.environ.get("LINX_DISABLE_TIMER_IRQ", "").lower() in {
        "1",
        "true",
        "yes",
    }
    if disable_timer_irq:
        append = _append_kernel_arg_if_absent(append, "linx_disable_timer_irq", "1")
    if append_extra.strip():
        append += " " + append_extra.strip()

    if transport == "9p":
        append = _append_kernel_arg_if_absent(append, "linx_storage_init", "1")
        force_virtio_mmio = os.environ.get(
            "LINX_SPEC_9P_FORCE_VIRTIO_MMIO", ""
        ).lower() in {"1", "true", "yes"}
        if force_virtio_mmio:
            append = _append_kernel_arg_if_absent(
                append, "virtio_mmio.device", "0x200@0x30001000:1"
            )
    return append


def _default_musl_sysroot() -> str:
    env = os.environ.get("LINX_SYSROOT", "").strip()
    if env:
        return str(Path(os.path.expanduser(env)).resolve())
    phase_c = REPO_ROOT / "out" / "libc" / "musl" / "install" / "phase-c"
    if _usable_static_sysroot(phase_c):
        return str(phase_c.resolve())
    return str((REPO_ROOT / "out" / "libc" / "musl" / "install" / "phase-b").resolve())


def _default_qemu(root: Path = REPO_ROOT) -> str:
    env = os.environ.get("QEMU", "").strip()
    if env:
        return str(Path(os.path.expanduser(env)).resolve())
    return str(default_qemu_binary(root).resolve())


def _usable_static_sysroot(path: Path) -> bool:
    return (
        (path / "usr" / "include" / "errno.h").is_file()
        and (path / "lib" / "libc.a").is_file()
        and (
            (path / "lib" / "rcrt1.o").is_file()
            or (path / "lib" / "crt1.o").is_file()
        )
    )


def _sysroot_provenance(sysroot: Path) -> dict[str, Any]:
    info: dict[str, Any] = {"path": str(sysroot)}
    summary_path: Path | None = None
    if sysroot.parent.name == "install":
        summary_path = sysroot.parent.parent / "logs" / f"{sysroot.name}-summary.txt"
    if summary_path is None:
        return info

    info["summary_path"] = str(summary_path)
    info["summary_exists"] = summary_path.is_file()
    if not summary_path.is_file():
        return info

    parsed: dict[str, str] = {}
    for raw in summary_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()

    for key in (
        "mode",
        "target",
        "malloc_impl",
        "musl_root",
        "llvm_bin",
        "build_dir",
        "install_dir",
        "m1",
        "m2",
        "m3",
        "shared_install",
    ):
        if key in parsed:
            info[key] = parsed[key]
    if parsed.get("install_dir"):
        info["install_dir_matches_sysroot"] = parsed["install_dir"] == str(sysroot)
    return info


def _read_control_rows(path: Path) -> list[list[str]]:
    if not path.exists():
        raise SystemExit(f"error: missing control file: {path}")
    rows: list[list[str]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rows.append(line.split())
    return rows


def _list_output_files(bench_root: Path, input_set: str) -> list[str]:
    output_dir = bench_root / "data" / input_set / "output"
    if not output_dir.exists():
        raise SystemExit(f"error: missing output dir for {input_set}: {output_dir}")
    outputs = [p.relative_to(output_dir).as_posix() for p in sorted(output_dir.rglob("*")) if p.is_file()]
    if not outputs:
        raise SystemExit(f"error: no output files found under {output_dir}")
    return outputs


def _mk_run(
    argv: list[str],
    stdout: str,
    stderr: str,
    *,
    stdin: str | None = None,
    verify_outputs: list[str] | None = None,
) -> dict[str, Any]:
    run: dict[str, Any] = {
        "argv": argv,
        "stdout": stdout,
        "stderr": stderr,
        "verify_outputs": list(verify_outputs) if verify_outputs is not None else [stdout],
    }
    if stdin:
        run["stdin"] = stdin
    return run


def _apply_argv_overrides(argv: list[str]) -> list[str]:
    out = list(argv)
    for idx in range(len(out)):
        val = os.environ.get(f"LINX_SPEC_ARGV{idx}_OVERRIDE", "").strip()
        if val:
            out[idx] = val
    return out


def _effective_run_argv(run_cfg: dict[str, Any]) -> list[str]:
    return _apply_argv_overrides(list(run_cfg["argv"]))


def _runs_perlbench(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    input_dir = bench_root / "data" / input_set / "input"
    if not input_dir.exists():
        raise SystemExit(f"error: missing input dir: {input_dir}")

    output_dir = bench_root / "data" / input_set / "output"
    script_by_name: dict[str, Path] = {}
    for script_dir in (bench_root / "data" / "all" / "input", input_dir):
        if not script_dir.exists():
            continue
        for path in sorted(script_dir.iterdir()):
            if path.is_file() and path.suffix in {".t", ".pl"}:
                script_by_name[path.name] = path

    runs: list[dict[str, Any]] = []
    special = {"splitmail", "perfect", "diffmail", "checkspam"}
    for path in sorted(script_by_name.values(), key=lambda p: p.name):
        name = path.stem
        if name in special:
            params_file = input_dir / f"{name}.in"
            if not params_file.exists():
                continue
            for raw in params_file.read_text(encoding="utf-8", errors="replace").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                params = line.split()
                tag = ".".join(params)
                runs.append(
                    _mk_run(
                        [f"./{exe}", "-I./lib", path.name, *params],
                        f"{name}.{tag}.out",
                        f"{name}.{tag}.err",
                    )
                )
            continue

        stdin = f"{name}.in" if (input_dir / f"{name}.in").exists() else None
        verify_outputs = [f"{name}.out"]
        if name == "suns" and (output_dir / "validate").exists():
            verify_outputs.append("validate")
        run = _mk_run(
            [f"./{exe}", "-I.", "-I./lib", path.name],
            f"{name}.out",
            f"{name}.err",
            stdin=stdin,
            verify_outputs=verify_outputs,
        )
        runs.append(run)

    if not runs:
        raise SystemExit(f"error: failed to derive runs for 500.perlbench_r ({input_set})")
    return runs


def _runs_gcc(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    rows = _read_control_rows(bench_root / "data" / input_set / "input" / "control")
    runs: list[dict[str, Any]] = []
    for cols in rows:
        src, *opts = cols
        out = Path(src).stem + ".opts" + "_".join(opts)
        out = out.replace("=", "_")
        runs.append(
            _mk_run(
                [f"./{exe}", src, *opts, "-o", f"{out}.s"],
                f"{out}.out",
                f"{out}.err",
                verify_outputs=[f"{out}.s"],
            )
        )
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 502.gcc_r ({input_set})")
    return runs


def _runs_mcf(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    rows = _read_control_rows(bench_root / "data" / input_set / "input" / "control")
    runs: list[dict[str, Any]] = []
    for cols in rows:
        input_name = cols[0]
        name = input_name[:-3] if input_name.endswith(".in") else input_name
        m = re.match(r".*\.(\d)$", name)
        argv = [f"./{exe}", input_name]
        if m:
            argv.append(m.group(1))
        verify_outputs = [f"{name}.out", "mcf.out"] if name == "inp" else [f"{name}.out"]
        runs.append(_mk_run(argv, f"{name}.out", f"{name}.err", verify_outputs=verify_outputs))
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 505.mcf_r ({input_set})")
    return runs


def _runs_omnetpp(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    rows = _read_control_rows(bench_root / "data" / input_set / "input" / "control")
    runs: list[dict[str, Any]] = []
    for cols in rows:
        if len(cols) < 2:
            continue
        conf, runnum = cols[0], cols[1]
        runs.append(_mk_run([f"./{exe}", "-c", conf, "-r", runnum], f"omnetpp.{conf}-{runnum}.out", f"omnetpp.{conf}-{runnum}.err"))
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 520.omnetpp_r ({input_set})")
    return runs


def _runs_xalanc(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    input_dir = bench_root / "data" / input_set / "input"
    if not input_dir.exists():
        raise SystemExit(f"error: missing input dir: {input_dir}")
    runs: list[dict[str, Any]] = []
    for lst in sorted(input_dir.glob("*.lst")):
        name = lst.stem
        for raw in lst.read_text(encoding="utf-8", errors="replace").splitlines():
            xml = raw.strip()
            if not xml:
                continue
            out_base = f"{name}-{Path(xml).stem}"
            runs.append(_mk_run([f"./{exe}", "-v", xml, "xalanc.xsl"], f"{out_base}.out", f"{out_base}.err"))
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 523.xalancbmk_r ({input_set})")
    return runs


def _runs_x264(bench_root: Path, input_set: str, x264_exe: str, imagevalidate_exe: str) -> list[dict[str, Any]]:
    rows = _read_control_rows(bench_root / "data" / input_set / "input" / "control")
    if not rows:
        raise SystemExit(f"error: failed to derive runs for 525.x264_r ({input_set})")
    cols = rows[0]
    if len(cols) < 9:
        raise SystemExit(f"error: malformed x264 control line for {input_set}: {' '.join(cols)}")

    (
        _org_x264,
        yuv_output,
        _yuv_md5,
        new_x24,
        size,
        seek_val,
        frames,
        frames2,
        yuvdump,
        *validframes,
    ) = cols

    def _basename_no_exe(name: str) -> str:
        return name[:-4] if name.endswith(".exe") else name

    x264_base = _basename_no_exe(x264_exe)
    dumpyuv = ["--dumpyuv", yuvdump] if yuvdump else []
    io = ["-o", new_x24, yuv_output, size]
    runs: list[dict[str, Any]] = []

    frames2_i = int(frames2)
    if frames2_i:
        width = len(str(int(frames)))
        pass_base = f"run_{0:0{width}d}-{frames}_{x264_base}_x264"
        runs.append(
            _mk_run(
                [f"./{x264_exe}", "--pass", "1", "--stats", "x264_stats.log", "--bitrate", "1000", "--frames", frames, *io],
                f"{pass_base}_pass1.out",
                f"{pass_base}_pass1.err",
                verify_outputs=[],
            )
        )
        runs.append(
            _mk_run(
                [
                    f"./{x264_exe}",
                    "--pass",
                    "2",
                    "--stats",
                    "x264_stats.log",
                    "--bitrate",
                    "1000",
                    *dumpyuv,
                    "--frames",
                    frames,
                    *io,
                ],
                f"{pass_base}_pass2.out",
                f"{pass_base}_pass2.err",
                verify_outputs=[],
            )
        )

        width2 = len(str(frames2_i))
        seek_i = int(seek_val)
        run_base = f"run_{seek_i:0{width2}d}-{frames2}_{x264_base}_x264"
        runs.append(_mk_run([f"./{x264_exe}", "--seek", seek_val, *dumpyuv, "--frames", frames2, *io], f"{run_base}.out", f"{run_base}.err", verify_outputs=[]))
    else:
        width = len(str(int(frames)))
        run_base = f"run_{0:0{width}d}-{frames}_{x264_base}_x264"
        runs.append(_mk_run([f"./{x264_exe}", *dumpyuv, "--frames", frames, *io], f"{run_base}.out", f"{run_base}.err", verify_outputs=[]))

    for frame in validframes:
        frame = frame.strip()
        if not frame:
            continue
        runs.append(
            _mk_run(
                [
                    f"./{imagevalidate_exe}",
                    "-avg",
                    "-threshold",
                    "0.5",
                    "-maxthreshold",
                    "20",
                    f"frame_{frame}.yuv",
                    f"/spec/benchspec/CPU/525.x264_r/data/{input_set}/compare/frame_{frame}.org.tga",
                ],
                f"imagevalidate_frame_{frame}.out",
                f"imagevalidate_frame_{frame}.err",
            )
        )

    if not runs:
        raise SystemExit(f"error: failed to derive runs for 525.x264_r ({input_set})")
    return runs


def _runs_deepsjeng(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    input_dir = bench_root / "data" / input_set / "input"
    runs = [_mk_run([f"./{exe}", p.name], f"{p.stem}.out", f"{p.stem}.err") for p in sorted(input_dir.glob("*.txt")) if p.is_file()]
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 531.deepsjeng_r ({input_set})")
    return runs


def _runs_leela(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    input_dir = bench_root / "data" / input_set / "input"
    runs = [_mk_run([f"./{exe}", p.name], f"{p.stem}.out", f"{p.stem}.err") for p in sorted(input_dir.glob("*.sgf")) if p.is_file()]
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 541.leela_r ({input_set})")
    return runs


def _runs_xz(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    rows = _read_control_rows(bench_root / "data" / input_set / "input" / "control")
    runs: list[dict[str, Any]] = []
    for cols in rows:
        if len(cols) < 6:
            continue
        name, size, sumv, minv, maxv, *levels = cols
        levels = [lvl for lvl in levels if re.match(r"^\de?$", lvl)]
        if int(size) <= 0 or not sumv or not levels:
            continue
        leveltext = "_".join(levels)
        runs.append(_mk_run([f"./{exe}", f"{name}.xz", size, sumv, minv, maxv, *levels], f"{name}-{size}-{leveltext}.out", f"{name}-{size}-{leveltext}.err"))
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 557.xz_r ({input_set})")
    return runs


def _runs_specrand(bench_root: Path, input_set: str, exe: str) -> list[dict[str, Any]]:
    rows = _read_control_rows(bench_root / "data" / input_set / "input" / "control")
    runs: list[dict[str, Any]] = []
    for cols in rows:
        if len(cols) < 2:
            continue
        seed, count = cols[0], cols[1]
        runs.append(_mk_run([f"./{exe}", seed, count], f"rand.{count}.out", f"rand.{count}.err"))
    if not runs:
        raise SystemExit(f"error: failed to derive runs for 999.specrand_ir ({input_set})")
    return runs


def _resolve_cfg(spec_dir: Path, bench: str, input_set: str) -> dict[str, Any]:
    bench_root = spec_dir / "benchspec" / "CPU" / bench
    exes = EXE_MAP[bench]

    if bench == "500.perlbench_r":
        runs = _runs_perlbench(bench_root, input_set, exes[0])
    elif bench == "502.gcc_r":
        runs = _runs_gcc(bench_root, input_set, exes[0])
    elif bench == "505.mcf_r":
        runs = _runs_mcf(bench_root, input_set, exes[0])
    elif bench == "520.omnetpp_r":
        runs = _runs_omnetpp(bench_root, input_set, exes[0])
    elif bench == "523.xalancbmk_r":
        runs = _runs_xalanc(bench_root, input_set, exes[0])
    elif bench == "525.x264_r":
        runs = _runs_x264(bench_root, input_set, exes[0], exes[1])
    elif bench == "531.deepsjeng_r":
        runs = _runs_deepsjeng(bench_root, input_set, exes[0])
    elif bench == "541.leela_r":
        runs = _runs_leela(bench_root, input_set, exes[0])
    elif bench == "557.xz_r":
        runs = _runs_xz(bench_root, input_set, exes[0])
    elif bench == "999.specrand_ir":
        runs = _runs_specrand(bench_root, input_set, exes[0])
    else:
        raise SystemExit(f"error: unsupported benchmark: {bench}")

    compares = [
        {
            "args": COMPARE_ARGS[bench],
            "ref": f"benchspec/CPU/{bench}/data/{input_set}/output/{out_name}",
            "out": out_name,
        }
        for out_name in _list_output_files(bench_root, input_set)
    ]

    return {
        "exes": exes,
        "src_run": SRC_RUN_DIR,
        "linx_run": f"run_base_{input_set}_linx-m64.0000",
        "runs": runs,
        "compares": compares,
    }


def _select_run_indices(cfg: dict[str, Any], selected_indices: list[int]) -> dict[str, Any]:
    if not selected_indices:
        return cfg

    runs = list(cfg.get("runs", []))
    unique_indices = list(dict.fromkeys(selected_indices))
    invalid = [idx for idx in unique_indices if idx < 1 or idx > len(runs)]
    if invalid:
        raise SystemExit(
            "error: --run-index out of range: "
            + ", ".join(str(idx) for idx in invalid)
            + f" (available: 1..{len(runs)})"
        )

    selected_runs: list[dict[str, Any]] = []
    selected_outputs: set[str] = set()
    for idx in unique_indices:
        run_cfg = dict(runs[idx - 1])
        run_cfg["source_run_index"] = idx
        selected_runs.append(run_cfg)
        selected_outputs.update(str(name) for name in run_cfg.get("verify_outputs", []))

    selected_compares = [
        cmp_cfg for cmp_cfg in cfg.get("compares", []) if cmp_cfg.get("out") in selected_outputs
    ]
    out = dict(cfg)
    out["runs"] = selected_runs
    out["compares"] = selected_compares
    out["selected_run_indices"] = unique_indices
    return out


def _check_exe(path: Path, what: str) -> Path:
    if path.exists():
        if not os.access(path, os.X_OK):
            raise SystemExit(f"error: {what} is not executable: {path}")
        return path
    resolved = shutil.which(str(path))
    if not resolved:
        raise SystemExit(f"error: {what} not found: {path}")
    rp = Path(resolved)
    if not os.access(rp, os.X_OK):
        raise SystemExit(f"error: {what} is not executable: {rp}")
    return rp


def _choose_init_static(transport: str, sysroot: Path) -> bool:
    init_static_env = os.environ.get("LINX_SPEC_INIT_STATIC", "").strip().lower()
    if init_static_env:
        return init_static_env not in {"0", "false", "no"}
    # Default initramfs runs to static PIE so Linux can exec /init without
    # relying on dynamic-loader FDPIC behavior in early bring-up kernels.
    if transport == "initramfs":
        return True
    # If the sysroot has no shared musl, prefer a static /init so static-only
    # workloads can still exercise the QEMU/runtime path.
    return not (sysroot / "lib" / "libc.so").exists()


def _spec_stack_limit_raw() -> str:
    return (
        os.environ.get("LINX_SPEC_STACK_LIMIT_BYTES")
        or os.environ.get("LINX_SPEC_STACK_LIMIT")
        or ""
    ).strip()


def _parse_stack_limit_bytes(raw: str) -> int:
    value = raw.strip().replace("_", "")
    match = re.fullmatch(r"(0[xX][0-9a-fA-F]+|[0-9]+)([a-zA-Z]*)", value)
    if not match:
        raise SystemExit(
            "error: LINX_SPEC_STACK_LIMIT_BYTES must be an integer byte count, "
            f"a K/M/G/T byte size, or 'unlimited' (got {raw!r})"
        )

    number = int(match.group(1), 0)
    suffix = match.group(2).lower()
    multipliers = {
        "": 1,
        "b": 1,
        "k": 1024,
        "kb": 1024,
        "kib": 1024,
        "m": 1024**2,
        "mb": 1024**2,
        "mib": 1024**2,
        "g": 1024**3,
        "gb": 1024**3,
        "gib": 1024**3,
        "t": 1024**4,
        "tb": 1024**4,
        "tib": 1024**4,
    }
    if suffix not in multipliers:
        raise SystemExit(
            "error: LINX_SPEC_STACK_LIMIT_BYTES suffix must be one of "
            "K, M, G, T, KiB, MiB, GiB, or TiB "
            f"(got {raw!r})"
        )

    return number * multipliers[suffix]


def _spec_stack_limit_defines() -> list[str]:
    raw = _spec_stack_limit_raw()
    if not raw:
        return []

    lowered = raw.lower()
    if lowered in {"unlimited", "infinity", "inf", "rlim_infinity"}:
        return ["-DLINX_SPEC_STACK_LIMIT_UNLIMITED=1"]
    if lowered in {"default", "finite"}:
        return []

    limit = _parse_stack_limit_bytes(raw)
    if limit <= 0:
        raise SystemExit(
            "error: LINX_SPEC_STACK_LIMIT_BYTES must be positive or 'unlimited'"
        )
    return [f"-DLINX_SPEC_STACK_LIMIT_BYTES={limit}ULL"]


def _run_dir_requires_guest_shared_runtime(run_dir: Path, exe_names: list[str]) -> bool:
    for exe_name in exe_names:
        exe_path = run_dir / exe_name
        if not exe_path.exists():
            raise SystemExit(f"error: missing staged executable: {exe_path}")
        data = exe_path.read_bytes()
        if b"/lib/ld-musl-linx64.so.1" in data:
            return True
    return False


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def _c_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _guest_proc_diagnostics_block() -> str:
    return """
        char proc_status_path[64];
        int proc_status_len = snprintf(proc_status_path, sizeof(proc_status_path),
                                       "/proc/%lld/status", (long long)child);
        if (proc_status_len > 0 && proc_status_len < (int)sizeof(proc_status_path)) {
          dump_log_file_with_markers("LINX_SPEC_CHILD_STATUS_BEGIN",
                                     "LINX_SPEC_CHILD_STATUS_END",
                                     "LINX_SPEC_CHILD_STATUS_OPEN_FAIL",
                                     "LINX_SPEC_CHILD_STATUS_READ_FAIL",
                                     proc_status_path, 4096);
        }

        dump_log_file_with_markers("LINX_SPEC_MEMINFO_BEGIN",
                                   "LINX_SPEC_MEMINFO_END",
                                   "LINX_SPEC_MEMINFO_OPEN_FAIL",
                                   "LINX_SPEC_MEMINFO_READ_FAIL",
                                   "/proc/meminfo", 4096);
        dump_log_file_with_markers("LINX_SPEC_VMSTAT_BEGIN",
                                   "LINX_SPEC_VMSTAT_END",
                                   "LINX_SPEC_VMSTAT_OPEN_FAIL",
                                   "LINX_SPEC_VMSTAT_READ_FAIL",
                                   "/proc/vmstat", 4096);
        dump_log_file_with_markers("LINX_SPEC_PRESSURE_MEMORY_BEGIN",
                                   "LINX_SPEC_PRESSURE_MEMORY_END",
                                   "LINX_SPEC_PRESSURE_MEMORY_OPEN_FAIL",
                                   "LINX_SPEC_PRESSURE_MEMORY_READ_FAIL",
                                   "/proc/pressure/memory", 1024);
"""


def _guest_proc_diagnostics_block_if_enabled(enabled: bool) -> str:
    return _guest_proc_diagnostics_block() if enabled else ""


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name, "").strip().lower()
    if not value:
        return default
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise SystemExit(f"error: {name} must be a boolean, got {value!r}")


def _apply_qemu_debug_env(
    qemu_env: dict[str, str],
    *,
    qemu_heartbeat_interval: int,
    qemu_heartbeat_regs: bool = False,
    qemu_heartbeat_code_bytes: int = 0,
    qemu_heartbeat_same_site_warn: int = 0,
    qemu_frame_stats: bool = False,
    qemu_frame_restore_host_load: bool = False,
    qemu_frame_restore_host_verify: bool = False,
    qemu_frame_restore_host_verify_limit: int = 0,
    qemu_tlb_stats: bool = False,
    qemu_tlb_inv_hot: bool = False,
    qemu_tlb_fill_stats: bool = False,
    qemu_tlb_fill_hot: bool = False,
    qemu_tb_stats: bool = False,
    qemu_fret_stk_trace: dict[str, str] | None = None,
    qemu_fentry_trace: dict[str, str] | None = None,
    qemu_fault_trace: bool = False,
    qemu_fault_trace_regs: bool,
    qemu_fault_trace_limit: int,
    qemu_fault_trace_filters: dict[str, str] | None = None,
    qemu_pc_watch: dict[str, str] | None = None,
    qemu_syscall_trace: dict[str, str] | None = None,
    qemu_mem_trace: dict[str, str] | None = None,
) -> None:
    if qemu_heartbeat_interval > 0:
        qemu_env["LINX_HEARTBEAT_INTERVAL"] = str(qemu_heartbeat_interval)
    if qemu_heartbeat_regs:
        qemu_env["LINX_QEMU_HEARTBEAT_REGS"] = "1"
    if qemu_heartbeat_code_bytes > 0:
        qemu_env["LINX_QEMU_HEARTBEAT_CODE_BYTES"] = str(qemu_heartbeat_code_bytes)
    if qemu_heartbeat_same_site_warn > 0:
        qemu_env["LINX_QEMU_HEARTBEAT_SAME_SITE_WARN"] = str(qemu_heartbeat_same_site_warn)
    if qemu_frame_stats:
        qemu_env["LINX_QEMU_FRAME_STATS"] = "1"
    if qemu_frame_restore_host_load:
        qemu_env["LINX_QEMU_FRAME_RESTORE_HOST_LOAD"] = "1"
    if qemu_frame_restore_host_verify or qemu_frame_restore_host_verify_limit > 0:
        qemu_env["LINX_QEMU_FRAME_RESTORE_HOST_VERIFY"] = "1"
    if qemu_frame_restore_host_verify_limit > 0:
        qemu_env["LINX_QEMU_FRAME_RESTORE_HOST_VERIFY_LIMIT"] = str(
            qemu_frame_restore_host_verify_limit
        )
    if qemu_tlb_stats:
        qemu_env["LINX_QEMU_TLB_STATS"] = "1"
    if qemu_tlb_inv_hot:
        qemu_env["LINX_QEMU_TLB_INV_HOT"] = "1"
    if qemu_tlb_fill_stats:
        qemu_env["LINX_QEMU_TLB_FILL_STATS"] = "1"
    if qemu_tlb_fill_hot:
        qemu_env["LINX_QEMU_TLB_FILL_HOT"] = "1"
    if qemu_tb_stats:
        qemu_env["LINX_QEMU_TB_STATS"] = "1"
    for name, value in (qemu_fret_stk_trace or {}).items():
        if str(value).strip():
            qemu_env[name] = str(value).strip()
    for name, value in (qemu_fentry_trace or {}).items():
        if str(value).strip():
            qemu_env[name] = str(value).strip()
    filters = {k: v for k, v in (qemu_fault_trace_filters or {}).items() if str(v).strip()}
    if qemu_fault_trace or qemu_fault_trace_regs or filters:
        qemu_env["LINX_QEMU_FAULT_TRACE"] = "1"
        for name, value in filters.items():
            qemu_env[name] = str(value).strip()
        if qemu_fault_trace_limit > 0:
            qemu_env["LINX_QEMU_FAULT_TRACE_LIMIT"] = str(qemu_fault_trace_limit)
    if qemu_fault_trace_regs:
        qemu_env["LINX_QEMU_FAULT_TRACE_REGS"] = "1"
    for name, value in (qemu_pc_watch or {}).items():
        if str(value).strip():
            qemu_env[name] = str(value).strip()
    for name, value in (qemu_syscall_trace or {}).items():
        if str(value).strip():
            qemu_env[name] = str(value).strip()
    for name, value in (qemu_mem_trace or {}).items():
        if str(value).strip():
            qemu_env[name] = str(value).strip()


def _qemu_debug_env_summary(qemu_env: dict[str, str]) -> dict[str, str]:
    prefixes = (
        "LINX_CALL_TRACE",
        "LINX_DEBUG_PC_WATCH",
        "LINX_HEARTBEAT_INTERVAL",
        "LINX_MEM_TRACE",
        "LINX_QEMU_",
        "LINX_SYSCALL_TRACE",
    )
    return {
        name: qemu_env[name]
        for name in sorted(qemu_env)
        if any(name.startswith(prefix) for prefix in prefixes)
    }


QEMU_FAULT_TRACE_FILTER_ARGS = {
    "qemu_fault_trace_pc": "LINX_QEMU_FAULT_TRACE_PC",
    "qemu_fault_trace_pc_lo": "LINX_QEMU_FAULT_TRACE_PC_LO",
    "qemu_fault_trace_pc_hi": "LINX_QEMU_FAULT_TRACE_PC_HI",
    "qemu_fault_trace_addr": "LINX_QEMU_FAULT_TRACE_ADDR",
    "qemu_fault_trace_addr_lo": "LINX_QEMU_FAULT_TRACE_ADDR_LO",
    "qemu_fault_trace_addr_hi": "LINX_QEMU_FAULT_TRACE_ADDR_HI",
    "qemu_fault_trace_count_lo": "LINX_QEMU_FAULT_TRACE_COUNT_LO",
    "qemu_fault_trace_count_hi": "LINX_QEMU_FAULT_TRACE_COUNT_HI",
    "qemu_fault_trace_trapnum": "LINX_QEMU_FAULT_TRACE_TRAPNUM",
}

QEMU_PC_WATCH_ARGS = {
    "qemu_pc_watch": "LINX_DEBUG_PC_WATCH",
    "qemu_pc_watch_count_lo": "LINX_DEBUG_PC_WATCH_COUNT_LO",
    "qemu_pc_watch_count_hi": "LINX_DEBUG_PC_WATCH_COUNT_HI",
    "qemu_pc_watch_hit_limit": "LINX_DEBUG_PC_WATCH_HIT_LIMIT",
    "qemu_pc_watch_hit_lo": "LINX_DEBUG_PC_WATCH_HIT_LO",
    "qemu_pc_watch_hit_hi": "LINX_DEBUG_PC_WATCH_HIT_HI",
    "qemu_pc_watch_match_gpr": "LINX_DEBUG_PC_WATCH_MATCH_GPR",
    "qemu_pc_watch_match_value": "LINX_DEBUG_PC_WATCH_MATCH_VALUE",
    "qemu_pc_watch_match_mask": "LINX_DEBUG_PC_WATCH_MATCH_MASK",
    "qemu_pc_watch_dump_reg": "LINX_DEBUG_PC_WATCH_DUMP_REG",
    "qemu_pc_watch_dump_regs": "LINX_DEBUG_PC_WATCH_DUMP_REGS",
    "qemu_pc_watch_dump_offsets": "LINX_DEBUG_PC_WATCH_DUMP_OFFSETS",
    "qemu_pc_watch_dump_ptr_offsets": "LINX_DEBUG_PC_WATCH_DUMP_PTR_OFFSETS",
    "qemu_pc_watch_dump_words": "LINX_DEBUG_PC_WATCH_DUMP_WORDS",
    "qemu_pc_watch_dump_width": "LINX_DEBUG_PC_WATCH_DUMP_WIDTH",
    "qemu_pc_watch_dump_code_bytes": "LINX_DEBUG_PC_WATCH_DUMP_CODE_BYTES",
    "qemu_pc_watch_ring_size": "LINX_DEBUG_PC_WATCH_RING_SIZE",
    "qemu_pc_watch_ring_mem_reg": "LINX_DEBUG_PC_WATCH_RING_MEM_REG",
    "qemu_pc_watch_ring_mem_offset": "LINX_DEBUG_PC_WATCH_RING_MEM_OFFSET",
}

QEMU_PC_WATCH_BOOL_ARGS = {
    "qemu_pc_watch_regs": "LINX_DEBUG_PC_WATCH_REGS",
    "qemu_pc_watch_ring": "LINX_DEBUG_PC_WATCH_RING",
    "qemu_pc_watch_dump_call_ring": "LINX_DEBUG_PC_WATCH_DUMP_CALL_RING",
    "qemu_pc_watch_dump_phys": "LINX_DEBUG_PC_WATCH_DUMP_PHYS",
}

QEMU_SYSCALL_TRACE_ARGS = {
    "qemu_syscall_trace_nr": "LINX_SYSCALL_TRACE_NR",
    "qemu_syscall_trace_limit": "LINX_SYSCALL_TRACE_LIMIT",
    "qemu_syscall_trace_pc_lo": "LINX_SYSCALL_TRACE_PC_LO",
    "qemu_syscall_trace_pc_hi": "LINX_SYSCALL_TRACE_PC_HI",
    "qemu_syscall_trace_string_max": "LINX_SYSCALL_TRACE_STRING_MAX",
    "qemu_syscall_trace_dump_args": "LINX_SYSCALL_TRACE_DUMP_ARGS",
    "qemu_syscall_trace_dump_arg": "LINX_SYSCALL_TRACE_DUMP_ARG",
    "qemu_syscall_trace_dump_bytes": "LINX_SYSCALL_TRACE_DUMP_BYTES",
}

QEMU_SYSCALL_TRACE_BOOL_ARGS = {
    "qemu_syscall_trace_regs": "LINX_SYSCALL_TRACE_REGS",
    "qemu_syscall_trace_strings": "LINX_SYSCALL_TRACE_STRINGS",
}

QEMU_MEM_TRACE_ARGS = {
    "qemu_mem_trace_addr": "LINX_MEM_TRACE_ADDR",
    "qemu_mem_trace_size": "LINX_MEM_TRACE_SIZE",
    "qemu_mem_trace_limit": "LINX_MEM_TRACE_LIMIT",
    "qemu_mem_trace_access": "LINX_MEM_TRACE_ACCESS",
    "qemu_mem_trace_acr": "LINX_MEM_TRACE_ACR",
    "qemu_mem_trace_pc": "LINX_MEM_TRACE_PC",
    "qemu_mem_trace_pc_lo": "LINX_MEM_TRACE_PC_LO",
    "qemu_mem_trace_pc_hi": "LINX_MEM_TRACE_PC_HI",
    "qemu_mem_trace_count_lo": "LINX_MEM_TRACE_COUNT_LO",
    "qemu_mem_trace_count_hi": "LINX_MEM_TRACE_COUNT_HI",
    "qemu_mem_trace_fast": "LINX_MEM_TRACE_FAST",
}

QEMU_MEM_TRACE_BOOL_ARGS = {
    "qemu_mem_trace_context": "LINX_MEM_TRACE_CONTEXT",
    "qemu_mem_trace_pre": "LINX_MEM_TRACE_PRE",
    "qemu_mem_trace_regs": "LINX_MEM_TRACE_REGS",
}

QEMU_FRET_STK_TRACE_ARGS = {
    "qemu_fret_stk_trace_pc": "LINX_QEMU_FRET_STK_TRACE_PC",
    "qemu_fret_stk_trace_pc_lo": "LINX_QEMU_FRET_STK_TRACE_PC_LO",
    "qemu_fret_stk_trace_pc_hi": "LINX_QEMU_FRET_STK_TRACE_PC_HI",
    "qemu_fret_stk_trace_count_lo": "LINX_QEMU_FRET_STK_TRACE_COUNT_LO",
    "qemu_fret_stk_trace_count_hi": "LINX_QEMU_FRET_STK_TRACE_COUNT_HI",
    "qemu_fret_stk_trace_ra": "LINX_QEMU_FRET_STK_TRACE_RA",
    "qemu_fret_stk_trace_limit": "LINX_QEMU_FRET_STK_TRACE_LIMIT",
    "qemu_fret_stk_trace_dump_words": "LINX_QEMU_FRET_STK_TRACE_DUMP_WORDS",
}

QEMU_FRET_STK_TRACE_BOOL_ARGS = {
    "qemu_fret_stk_trace_regs": "LINX_QEMU_FRET_STK_TRACE_REGS",
}

QEMU_FENTRY_TRACE_ARGS = {
    "qemu_fentry_trace_pc": "LINX_QEMU_FENTRY_TRACE_PC",
    "qemu_fentry_trace_pc_lo": "LINX_QEMU_FENTRY_TRACE_PC_LO",
    "qemu_fentry_trace_pc_hi": "LINX_QEMU_FENTRY_TRACE_PC_HI",
    "qemu_fentry_trace_count_lo": "LINX_QEMU_FENTRY_TRACE_COUNT_LO",
    "qemu_fentry_trace_count_hi": "LINX_QEMU_FENTRY_TRACE_COUNT_HI",
    "qemu_fentry_trace_ra": "LINX_QEMU_FENTRY_TRACE_RA",
    "qemu_fentry_trace_sp": "LINX_QEMU_FENTRY_TRACE_SP",
    "qemu_fentry_trace_new_sp": "LINX_QEMU_FENTRY_TRACE_NEW_SP",
    "qemu_fentry_trace_limit": "LINX_QEMU_FENTRY_TRACE_LIMIT",
    "qemu_fentry_trace_dump_words": "LINX_QEMU_FENTRY_TRACE_DUMP_WORDS",
}

QEMU_FENTRY_TRACE_BOOL_ARGS = {
    "qemu_fentry_trace_regs": "LINX_QEMU_FENTRY_TRACE_REGS",
}


def _qemu_fault_trace_filters_from_args(args: argparse.Namespace) -> dict[str, str]:
    filters: dict[str, str] = {}
    for attr, env_name in QEMU_FAULT_TRACE_FILTER_ARGS.items():
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            filters[env_name] = value
    return filters


def _qemu_pc_watch_from_args(args: argparse.Namespace) -> dict[str, str]:
    watch: dict[str, str] = {}
    for attr, env_name in QEMU_PC_WATCH_ARGS.items():
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            watch[env_name] = value
    for attr, env_name in QEMU_PC_WATCH_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            watch[env_name] = "1"
    if bool(getattr(args, "qemu_call_trace_ring", False)) or bool(
        getattr(args, "qemu_pc_watch_dump_call_ring", False)
    ):
        watch.setdefault("LINX_CALL_TRACE_RING", "1")
    call_trace_ring_size = str(
        getattr(args, "qemu_call_trace_ring_size", "") or ""
    ).strip()
    if call_trace_ring_size:
        watch["LINX_CALL_TRACE_RING_SIZE"] = call_trace_ring_size
    return watch


def _qemu_syscall_trace_from_args(args: argparse.Namespace) -> dict[str, str]:
    trace: dict[str, str] = {}
    for attr, env_name in QEMU_SYSCALL_TRACE_ARGS.items():
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            trace[env_name] = value
    for attr, env_name in QEMU_SYSCALL_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            trace[env_name] = "1"
    if bool(getattr(args, "qemu_syscall_trace", False)) or trace:
        trace["LINX_SYSCALL_TRACE"] = "1"
    return trace


def _qemu_mem_trace_from_args(args: argparse.Namespace) -> dict[str, str]:
    trace: dict[str, str] = {}
    for attr, env_name in QEMU_MEM_TRACE_ARGS.items():
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            trace[env_name] = value
    for attr, env_name in QEMU_MEM_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            trace[env_name] = "1"
    if bool(getattr(args, "qemu_mem_trace", False)) or trace:
        trace["LINX_MEM_TRACE"] = "1"
    return trace


def _qemu_fret_stk_trace_from_args(args: argparse.Namespace) -> dict[str, str]:
    trace: dict[str, str] = {}
    for attr, env_name in QEMU_FRET_STK_TRACE_ARGS.items():
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            trace[env_name] = value
    for attr, env_name in QEMU_FRET_STK_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            trace[env_name] = "1"
    if bool(getattr(args, "qemu_fret_stk_trace", False)) or trace:
        trace["LINX_QEMU_FRET_STK_TRACE"] = "1"
    return trace


def _qemu_fentry_trace_from_args(args: argparse.Namespace) -> dict[str, str]:
    trace: dict[str, str] = {}
    for attr, env_name in QEMU_FENTRY_TRACE_ARGS.items():
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            trace[env_name] = value
    for attr, env_name in QEMU_FENTRY_TRACE_BOOL_ARGS.items():
        if bool(getattr(args, attr, False)):
            trace[env_name] = "1"
    if bool(getattr(args, "qemu_fentry_trace", False)) or trace:
        trace["LINX_QEMU_FENTRY_TRACE"] = "1"
    return trace


def _find_gen_init_cpio(linux_root: Path, out_dir: Path) -> Path:
    cands = [
        linux_root / "build-linx-fixed" / "usr" / "gen_init_cpio",
        linux_root / "usr" / "gen_init_cpio",
    ]
    for c in cands:
        if c.exists():
            return c

    src = linux_root / "usr" / "gen_init_cpio.c"
    if not src.exists():
        raise SystemExit(f"error: missing gen_init_cpio source: {src}")
    out = out_dir / "gen_init_cpio"
    cc = _check_exe(Path("clang"), "host clang")
    proc = _run([str(cc), "-O2", "-Wall", "-Wextra", "-o", str(out), str(src)])
    if proc.returncode != 0:
        raise SystemExit(
            "error: failed to build gen_init_cpio:\n" + proc.stdout.decode("utf-8", errors="replace")
        )
    return out


def _copy_input_overlay(input_dir: Path, dst_run: Path) -> None:
    for src in sorted(input_dir.rglob("*")):
        rel = src.relative_to(input_dir)
        dst = dst_run / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        if src.is_symlink():
            os.symlink(os.readlink(src), dst)
        else:
            shutil.copy2(src, dst)


def _overlay_input_set(bench_root: Path, dst_run: Path, input_set: str) -> None:
    if input_set == "refrate":
        return

    for input_dir in (bench_root / "data" / "all" / "input", bench_root / "data" / input_set / "input"):
        if input_dir.exists():
            _copy_input_overlay(input_dir, dst_run)


def _prepare_run_dir(
    spec_dir: Path,
    bench: str,
    cfg: dict[str, Any],
    *,
    preserve_symlinks: bool,
    input_set: str,
) -> Path:
    bench_root = spec_dir / "benchspec" / "CPU" / bench
    src_run = bench_root / "run" / cfg["src_run"]
    dst_run = bench_root / "run" / cfg["linx_run"]

    if not src_run.exists():
        raise SystemExit(f"error: missing source run dir: {src_run}")

    if dst_run.exists():
        shutil.rmtree(dst_run)
    shutil.copytree(src_run, dst_run, symlinks=preserve_symlinks)
    _overlay_input_set(bench_root, dst_run, input_set)

    for exe_name in cfg["exes"]:
        exe_src = bench_root / "exe" / exe_name
        exe_dst = dst_run / exe_name
        if not exe_src.exists():
            raise SystemExit(f"error: missing Linx executable: {exe_src}")
        shutil.copy2(exe_src, exe_dst)
        os.chmod(exe_dst, 0o755)

    cleanup_files = {
        rel
        for run_cfg in cfg.get("runs", [])
        for rel in (run_cfg.get("stdout"), run_cfg.get("stderr"))
        if rel
    }
    cleanup_files.update(c["out"] for c in cfg.get("compares", []))
    # Drop stale harness/output artifacts copied from source run dirs (often huge for refrate).
    stale_suffixes = {".out", ".err", ".stdout", ".cmp"}
    for p in dst_run.iterdir():
        if p.is_file() and p.suffix in stale_suffixes:
            cleanup_files.add(p.name)
    for rel in cleanup_files:
        p = dst_run / rel
        if p.exists() or p.is_symlink():
            p.unlink()

    (dst_run / EMPTY_STDIN_NAME).write_bytes(b"")

    return dst_run


def _build_init_for_run(
    bench: str,
    cfg: dict[str, Any],
    run_cfg: dict[str, Any],
    dst_run: Path,
    out_dir: Path,
    clang: Path,
    sysroot: Path,
    transport: str,
    dump_prefix_bytes: int,
    guest_heartbeat_sec: int,
    guest_proc_diagnostics: bool,
    *,
    emit_hashes: bool = False,
) -> Path:
    if transport not in {"9p", "initramfs"}:
        raise SystemExit(f"error: unsupported transport: {transport}")
    if dump_prefix_bytes < 0:
        raise SystemExit("error: dump_prefix_bytes must be >= 0")
    if guest_heartbeat_sec < 0:
        raise SystemExit("error: guest_heartbeat_sec must be >= 0")

    argv = _effective_run_argv(run_cfg)
    argv_items = "\n".join(f'    "{_c_escape(arg)}",' for arg in argv)
    stdout_rel = str(run_cfg["stdout"])
    stderr_rel = str(run_cfg["stderr"])
    stdin_rel = str(run_cfg.get("stdin") or EMPTY_STDIN_NAME)
    dump_items = "\n".join(f'    "{_c_escape(name)}",' for name in run_cfg.get("verify_outputs", []))
    if not emit_hashes:
        dump_items = ""
    if not dump_items:
        dump_items = "    NULL,"
    mirror_log_default = "0" if transport == "initramfs" else "1"
    mirror_log_stdout = os.environ.get("LINX_SPEC_MIRROR_LOG_STDOUT", mirror_log_default).lower() in {
        "1",
        "true",
        "yes",
    }
    setup_console_env = os.environ.get("LINX_SPEC_SETUP_CONSOLE", "").lower()
    if setup_console_env:
        setup_console = setup_console_env in {"1", "true", "yes"}
    else:
        setup_console = True
    use_kmsg_log = os.environ.get("LINX_SPEC_LOG_KMSG", "").lower() in {
        "1",
        "true",
        "yes",
    }
    use_vfork_default = "0" if transport == "initramfs" else "0"
    use_vfork = os.environ.get("LINX_SPEC_USE_VFORK", use_vfork_default).lower() in {"1", "true", "yes"}
    trace_cwd = os.environ.get("LINX_SPEC_CWD_TRACE", "").lower() in {"1", "true", "yes"}
    direct_initramfs = transport == "initramfs" and os.environ.get(
        "LINX_SPEC_DIRECT_INITRAMFS", ""
    ).lower() in {"1", "true", "yes"}
    stdout_console = os.environ.get("LINX_SPEC_STDOUT_CONSOLE", "").lower() in {"1", "true", "yes"}
    if transport == "9p":
        mount_opts = os.environ.get("LINX_SPEC_9P_MOUNT_OPTS", "trans=virtio,version=9p2000.L")
        guest_run = f"/spec/benchspec/CPU/{bench}/run/{cfg['linx_run']}"
        transport_block = f"""
  (void)mkdir("/spec", 0755);
  long spec_mnt_rc = linx_spec_mount_raw("spec2017", "/spec", "9p", 0, "{_c_escape(mount_opts)}");
  if (spec_mnt_rc < 0) {{
    char spec_mnt_line[96];
    int spec_mnt_n = snprintf(
        spec_mnt_line, sizeof(spec_mnt_line),
        "LINX_SPEC_WARN 9p-mount-failed raw_rc=%lld neg_errno=%lld\\n",
        (long long)spec_mnt_rc, (long long)-spec_mnt_rc);
    if (spec_mnt_n > 0 && spec_mnt_n < (int)sizeof(spec_mnt_line))
      write_log_all(spec_mnt_line, (unsigned long)spec_mnt_n);
  }}
"""
    else:
        guest_run = "/spec-run"
        transport_block = ""
    exec_path = str(argv[0])
    if transport == "initramfs" and exec_path.startswith("./"):
        exec_path = f"{guest_run}/{exec_path[2:]}"
    guest_proc_diagnostics_block = _guest_proc_diagnostics_block_if_enabled(
        guest_proc_diagnostics
    )
    stdin_open_block = f"""
  LOG_LIT("LINX_SPEC_DBG step=open-in\\n");
  int fd_in = raw_openat("{_c_escape(stdin_rel)}", O_RDONLY, 0);
  if (fd_in < 0) {{
    LOG_LIT("LINX_SPEC_FAIL open-in\\n");
    poweroff_now();
  }}
"""
    if transport == "initramfs" and not direct_initramfs:
        debug_console_io = os.environ.get("LINX_SPEC_DEBUG_CONSOLE_IO", "").lower() in {"1", "true", "yes"}
        if debug_console_io:
            child_stdio_setup = """
    if (g_log_fd >= 0)
      write_fd_all(g_log_fd, "LINX_SPEC_DBG child-console-io\\n",
                   sizeof("LINX_SPEC_DBG child-console-io\\n") - 1);
"""
        else:
            child_stdio_setup = ""
        if stdout_console:
            stdout_open_block = """
  LOG_LIT("LINX_SPEC_DBG step=open-out-inherited\\n");
  int fd_out = STDOUT_FILENO;
"""
        else:
            stdout_open_block = f"""
  LOG_LIT("LINX_SPEC_DBG step=open-out\\n");
  int fd_out = raw_openat("{_c_escape(stdout_rel)}", O_WRONLY | O_CREAT | O_TRUNC, 0644);
  if (fd_out < 0) {{
    LOG_LIT("LINX_SPEC_FAIL open-out\\n");
    poweroff_now();
  }}
"""
        run_block = f"""
  static const char *hash_files[] = {{
{dump_items}
    NULL,
  }};
  int child_success = 0;

{stdout_open_block}
  LOG_LIT("LINX_SPEC_DBG step=open-err\\n");
  int fd_err = raw_openat("{_c_escape(stderr_rel)}", O_WRONLY | O_CREAT | O_APPEND, 0644);
  if (fd_err < 0) {{
    LOG_LIT("LINX_SPEC_FAIL open-err\\n");
    poweroff_now();
  }}

{stdin_open_block}
  LOG_LIT("LINX_SPEC_DBG step=fds-ready\\n");
  int state_pipe[2] = {{-1, -1}};
  int state_pipe_nonblock = 0;
  LOG_LIT("LINX_SPEC_DBG step=state-pipe-skip\\n");
  LOG_LIT("LINX_SPEC_DBG step=sigaction-skip\\n");

  LOG_LIT("LINX_SPEC_DBG step=predup-stdio\\n");
  if (fd_in != STDIN_FILENO && dup2(fd_in, STDIN_FILENO) < 0) {{
    LOG_LIT("LINX_SPEC_FAIL predup-in\\n");
    poweroff_now();
  }}
  if (fd_out != STDOUT_FILENO && dup2(fd_out, STDOUT_FILENO) < 0) {{
    LOG_LIT("LINX_SPEC_FAIL predup-out\\n");
    poweroff_now();
  }}
  if (fd_err != STDERR_FILENO && dup2(fd_err, STDERR_FILENO) < 0) {{
    LOG_LIT("LINX_SPEC_FAIL predup-err\\n");
    poweroff_now();
  }}

  LOG_LIT("LINX_SPEC_DBG step=spawn\\n");
  errno = 0;
  pid_t child = spawn_child_process();
  static const char kSpawnRaw[] = "LINX_SPEC_DBG step=spawn-raw\\n";
  write_log_all(kSpawnRaw, sizeof(kSpawnRaw) - 1);

  if (child > 0)
    LOG_LIT("LINX_SPEC_DBG step=parent-after-spawn\\n");
  if (child == 0) {{
    if (state_pipe[0] >= 0)
      close(state_pipe[0]);
    if (state_pipe[1] >= 0) {{
      (void)write(state_pipe[1], "S", 1);
      close(state_pipe[1]);
      state_pipe[1] = -1;
    }}
    if (!kUseVfork)
      LOG_LIT("LINX_SPEC_DBG step=child-enter\\n");
{child_stdio_setup}
    LOG_LIT("LINX_SPEC_DBG step=child-before-exec\\n");
    log_cwd_probe("child-before-exec");
    log_preexec_probe(argv[0]);
    log_preexec_probe(kExecPath);
    /*
     * Child-side close after fork is not part of SPEC semantics, and early
     * Linx fork/exec bring-up has exposed hangs there. Keep the extra run-file
     * descriptors open across exec; stdout/stderr still point at the intended
     * files after dup2.
     */
    char *empty_envp[] = {{ NULL }};
    int exec_rc = linx_spec_execve(kExecPath, argv, empty_envp);
    int exec_errno = errno;
    if (!kUseVfork)
    {{
      LOG_LIT("LINX_SPEC_FAIL execve rc=");
      write_log_u64_dec((unsigned long long)(exec_rc < 0 ? -exec_rc : exec_rc));
      LOG_LIT(" errno=");
      write_log_u64_dec((unsigned long long)exec_errno);
      LOG_LIT("\\n");
      LOG_LIT("LINX_SPEC_FAIL execve\\n");
    }}
    _exit(124);
  }}

  LOG_LIT("LINX_SPEC_DBG step=spawn-ret\\n");
  if (child < 0) {{
    LOG_LIT("LINX_SPEC_FAIL spawn\\n");
    poweroff_now();
  }}

  if (fd_in > STDERR_FILENO)
    close(fd_in);
  if (fd_out > STDERR_FILENO && fd_out != fd_in)
    close(fd_out);
  if (fd_err > STDERR_FILENO && fd_err != fd_in && fd_err != fd_out)
    close(fd_err);
  if (state_pipe[1] >= 0) {{
    close(state_pipe[1]);
    state_pipe[1] = -1;
  }}
  LOG_LIT("LINX_SPEC_DBG step=parent-waitpid\\n");
  {{
    int status = -1;
    pid_t wr = -2;
    int wait_errno = 0;
    int waitid_errno = 0;
    int wait_fallback = 0;
    int wait_method = 0;
    int child_started = 1;
    int child_pipe_eof = 0;

    wait_method = 6;
    if (kGuestHeartbeatSec > 0) {{
      wait_method = 7;
      for (;;) {{
        siginfo_t si;
        memset(&si, 0, sizeof(si));
        errno = 0;
        int waitid_ret = waitid(P_PID, child, &si, WEXITED | WNOHANG);
        if (waitid_ret == 0 && si.si_pid == child) {{
          status = wait_status_from_siginfo(&si);
          wr = child;
          wait_errno = 0;
          waitid_errno = 0;
          break;
        }}
        if (waitid_ret < 0) {{
          waitid_errno = errno;
          break;
        }}

        struct stat st_out;
        struct stat st_err;
        long long out_size = -1;
        long long err_size = -1;
        if (stat("{_c_escape(stdout_rel)}", &st_out) == 0)
          out_size = (long long)st_out.st_size;
        if (stat("{_c_escape(stderr_rel)}", &st_err) == 0)
          err_size = (long long)st_err.st_size;
        errno = 0;
        int kr = probe_child_alive(child);
        int kerr = errno;

        char child_hb_line[192];
        int child_hb_len = snprintf(
            child_hb_line, sizeof(child_hb_line),
            "LINX_SPEC_CHILD_HEARTBEAT child=%lld alive=%lld "
            "kill_errno=%lld out_size=%lld err_size=%lld\\n",
            (long long)child, (long long)(kr == 0 || kerr != ESRCH),
            (long long)kerr, out_size, err_size);
        if (child_hb_len > 0 && child_hb_len < (int)sizeof(child_hb_line))
          write_log_all(child_hb_line, (unsigned long)child_hb_len);

        if (kDumpPrefixBytes > 0 && out_size > 0) {{
          LOG_LIT("LINX_SPEC_CHILD_STDOUT_PREFIX_BEGIN\\n");
          (void)dump_file_prefix("{_c_escape(stdout_rel)}", kDumpPrefixBytes);
          LOG_LIT("\\nLINX_SPEC_CHILD_STDOUT_PREFIX_END\\n");
        }}
        if (kDumpPrefixBytes > 0 && err_size > 0) {{
          LOG_LIT("LINX_SPEC_CHILD_STDERR_PREFIX_BEGIN\\n");
          (void)dump_file_prefix("{_c_escape(stderr_rel)}", kDumpPrefixBytes);
          LOG_LIT("\\nLINX_SPEC_CHILD_STDERR_PREFIX_END\\n");
        }}

        char proc_stat_path[64];
        int proc_stat_len = snprintf(proc_stat_path, sizeof(proc_stat_path),
                                     "/proc/%lld/stat", (long long)child);
        if (proc_stat_len > 0 && proc_stat_len < (int)sizeof(proc_stat_path)) {{
          errno = 0;
          int proc_fd = raw_openat(proc_stat_path, O_RDONLY, 0);
          if (proc_fd >= 0) {{
            char proc_buf[256];
            errno = 0;
            ssize_t proc_rd = read(proc_fd, proc_buf, sizeof(proc_buf) - 1);
            int proc_read_errno = errno;
            close(proc_fd);
            if (proc_rd > 0) {{
              proc_buf[proc_rd] = '\\0';
              LOG_LIT("LINX_SPEC_CHILD_STAT ");
              write_log_all(proc_buf, (unsigned long)proc_rd);
              if (proc_buf[proc_rd - 1] != '\\n')
                LOG_LIT("\\n");
            }} else {{
              LOG_LIT("LINX_SPEC_CHILD_STAT_READ_FAIL rd=");
              write_log_s64_dec((long long)proc_rd);
              LOG_LIT(" errno=");
              write_log_s64_dec((long long)proc_read_errno);
              LOG_LIT("\\n");
            }}
          }} else {{
            int proc_open_errno = errno;
            LOG_LIT("LINX_SPEC_CHILD_STAT_OPEN_FAIL errno=");
            write_log_s64_dec((long long)proc_open_errno);
            LOG_LIT("\\n");
          }}
        }}

        char proc_maps_path[64];
        int proc_maps_len = snprintf(proc_maps_path, sizeof(proc_maps_path),
                                     "/proc/%lld/maps", (long long)child);
        if (proc_maps_len > 0 && proc_maps_len < (int)sizeof(proc_maps_path)) {{
          errno = 0;
          int maps_fd = raw_openat(proc_maps_path, O_RDONLY, 0);
          if (maps_fd >= 0) {{
            char maps_buf[2048];
            errno = 0;
            ssize_t maps_rd = read(maps_fd, maps_buf, sizeof(maps_buf) - 1);
            int maps_read_errno = errno;
            close(maps_fd);
            if (maps_rd > 0) {{
              maps_buf[maps_rd] = '\\0';
              LOG_LIT("LINX_SPEC_CHILD_MAPS_BEGIN\\n");
              write_log_all(maps_buf, (unsigned long)maps_rd);
              if (maps_buf[maps_rd - 1] != '\\n')
                LOG_LIT("\\n");
              LOG_LIT("LINX_SPEC_CHILD_MAPS_END\\n");
            }} else {{
              LOG_LIT("LINX_SPEC_CHILD_MAPS_READ_FAIL rd=");
              write_log_s64_dec((long long)maps_rd);
              LOG_LIT(" errno=");
              write_log_s64_dec((long long)maps_read_errno);
              LOG_LIT("\\n");
            }}
          }} else {{
            int maps_open_errno = errno;
            LOG_LIT("LINX_SPEC_CHILD_MAPS_OPEN_FAIL errno=");
            write_log_s64_dec((long long)maps_open_errno);
            LOG_LIT("\\n");
          }}
        }}

{guest_proc_diagnostics_block}
        sleep(kGuestHeartbeatSec);
      }}
    }} else if (wait_child_waitid_blocking(child, &status, &waitid_errno) == 0) {{
      wr = child;
      wait_errno = 0;
    }}
    if (wr != child) {{
      wait_method = 1;
      errno = 0;
      wr = wait_child_blocking(child, &status);
      wait_errno = errno;
    }}
    if (wr < 0 && wait_errno == ENOSYS) {{
      errno = 0;
      wr = wait_child_blocking(child, &status);
      wait_errno = errno;
    }}
    if (wr < 0 && wait_errno == ECHILD) {{
      errno = 0;
      wr = wait_child_blocking((pid_t)-1, &status);
      wait_errno = errno;
      if (wr >= 0) {{
        wait_method = 5;
        LOG_LIT("LINX_SPEC_WARN wait-any-child\\n");
      }}
    }}
    if (wr < 0 && wait_errno == ECHILD) {{
      unsigned int spins = 0;
      long long last_out_size = -1;
      unsigned int stable_count = 0;
      wait_fallback = 1;
      wait_method = 3;
      LOG_LIT("LINX_SPEC_WARN wait-echild-fallback\\n");
      for (;;) {{
        struct stat st_out;
        long long out_size = -1;
        if (stat("{_c_escape(stdout_rel)}", &st_out) == 0)
          out_size = (long long)st_out.st_size;
        if (out_size == last_out_size)
          stable_count++;
        else
          stable_count = 0;
        last_out_size = out_size;

        errno = 0;
        int kr = probe_child_alive(child);
        int kerr = errno;
        if (kr < 0 && kerr == ESRCH)
          break;
        if (stable_count > 20000u) {{
          LOG_LIT("LINX_SPEC_WARN wait-stable-break\\n");
          break;
        }}
        if (spins > 20000000u) {{
          LOG_LIT("LINX_SPEC_WARN wait-fallback-timeout\\n");
          break;
        }}
        (void)sched_yield();
        spins++;
      }}
    }} else if (wr < 0) {{
      LOG_LIT("LINX_SPEC_FAIL waitpid-block wr=");
      write_log_s64_dec((long long)wr);
      LOG_LIT(" errno=");
      write_log_s64_dec((long long)wait_errno);
      LOG_LIT(" child=");
      write_log_s64_dec((long long)child);
      LOG_LIT("\\n");
      poweroff_now();
    }}
    if (wr > 0 && wr != child)
      LOG_LIT("LINX_SPEC_WARN wait-unexpected-child\\n");

    if (state_pipe[1] >= 0)
      close(state_pipe[1]);
    if (state_pipe[0] >= 0)
      close(state_pipe[0]);
    if (!child_started && child_pipe_eof)
      child_started = 1;
    if (!child_started)
      LOG_LIT("LINX_SPEC_WARN child-start-unknown\\n");
    if (child_pipe_eof)
      LOG_LIT("LINX_SPEC_DBG child-pipe-eof\\n");

    write_wait_status_log(wr, wait_errno, waitid_errno, wait_method, wait_fallback, status);
    child_success = wait_fallback || (WIFEXITED(status) && WEXITSTATUS(status) == 0);
    if (!child_success) {{
      LOG_LIT("LINX_SPEC_FAIL child-exit\\n");
    }}
  }}
  LOG_LIT("LINX_SPEC_DBG step=parent-hash\\n");

  {{
    int fd_dbg = raw_openat("{_c_escape(stderr_rel)}", O_RDONLY, 0);
    if (fd_dbg >= 0) {{
      char dbg_buf[512];
      ssize_t dbg_n = read(fd_dbg, dbg_buf, sizeof(dbg_buf));
      if (dbg_n > 0) {{
        LOG_LIT("LINX_SPEC_STDERR_BEGIN\\n");
        write_log_all(dbg_buf, (unsigned long)dbg_n);
        LOG_LIT("\\nLINX_SPEC_STDERR_END\\n");
      }}
      close(fd_dbg);
    }}
  }}

  for (int i = 0; hash_files[i]; ++i) {{
    unsigned long long fsize = 0;
    unsigned long long fhash = 0;

    if (hash_file_fnv1a64(hash_files[i], &fsize, &fhash) < 0) {{
      LOG_LIT("LINX_SPEC_FAIL hash\\n");
      poweroff_now();
    }}

    /*
     * The initramfs parent keeps the benchmark stdout fd after dup2 so the
     * child inherits it across exec.  Emit host-visible verification markers
     * through the log channel, not through guest stdout.
     */
    LOG_LIT("LINX_SPEC_HASH ");
    write_log_cstr(hash_files[i]);
    LOG_LIT(" ");
    write_log_u64_dec(fsize);
    LOG_LIT(" 0x");
    write_log_hex_u64(fhash);
    LOG_LIT("\\n");

    if (kDumpPrefixBytes > 0) {{
      LOG_LIT("LINX_SPEC_FILE_BEGIN ");
      write_log_cstr(hash_files[i]);
      LOG_LIT("\\n");

      if (dump_file_prefix(hash_files[i], kDumpPrefixBytes) < 0) {{
        LOG_LIT("LINX_SPEC_FAIL dump-prefix\\n");
        poweroff_now();
      }}

      LOG_LIT("\\nLINX_SPEC_FILE_END ");
      write_log_cstr(hash_files[i]);
      LOG_LIT("\\n");
    }}
  }}

  if (!child_success) {{
    LOG_LIT("LINX_SPEC_FAIL child-exit-no-pass\\n");
    poweroff_now();
  }}
  LOG_LIT("LINX_SPEC_PASS {_c_escape(bench)}\\n");
  poweroff_now();
"""
    else:
        if stdout_console:
            stdout_open_block = """
  LOG_LIT("LINX_SPEC_DBG step=open-out-inherited\\n");
  int fd_out = STDOUT_FILENO;
"""
        else:
            stdout_open_block = f"""
  LOG_LIT("LINX_SPEC_DBG step=open-out\\n");
  int fd_out = raw_openat("{_c_escape(stdout_rel)}", O_WRONLY | O_CREAT | O_TRUNC, 0644);
  if (fd_out < 0) {{
    LOG_LIT("LINX_SPEC_FAIL open-out\\n");
    poweroff_now();
  }}
"""
        run_block = f"""
{stdout_open_block}
  LOG_LIT("LINX_SPEC_DBG step=open-err\\n");
  int fd_err = raw_openat("{_c_escape(stderr_rel)}", O_WRONLY | O_CREAT | O_APPEND, 0644);
  if (fd_err < 0) {{
    LOG_LIT("LINX_SPEC_FAIL open-err\\n");
    poweroff_now();
  }}

{stdin_open_block}

  LOG_LIT("LINX_SPEC_DBG step=dup2-in\\n");
  if (fd_in != STDIN_FILENO && dup2(fd_in, STDIN_FILENO) < 0) {{
    LOG_LIT("LINX_SPEC_FAIL dup2-in\\n");
    poweroff_now();
  }}

  LOG_LIT("LINX_SPEC_DBG step=dup2-out\\n");
  if (fd_out != STDOUT_FILENO && dup2(fd_out, STDOUT_FILENO) < 0) {{
    LOG_LIT("LINX_SPEC_FAIL dup2-out\\n");
    poweroff_now();
  }}
  LOG_LIT("LINX_SPEC_DBG step=dup2-err\\n");
  if (fd_err != STDERR_FILENO && dup2(fd_err, STDERR_FILENO) < 0) {{
    LOG_LIT("LINX_SPEC_FAIL dup2-err\\n");
    poweroff_now();
  }}
  LOG_LIT("LINX_SPEC_DBG step=close-in\\n");
  if (fd_in > STDERR_FILENO)
    close(fd_in);
  LOG_LIT("LINX_SPEC_DBG step=close-out\\n");
  if (fd_out > STDERR_FILENO && fd_out != fd_in)
    close(fd_out);
  LOG_LIT("LINX_SPEC_DBG step=close-err\\n");
  if (fd_err > STDERR_FILENO && fd_err != fd_in && fd_err != fd_out)
    close(fd_err);

  LOG_LIT("LINX_SPEC_DBG step=direct-before-exec\\n");
  char *empty_envp[] = {{ NULL }};
  log_preexec_probe(argv[0]);
  log_preexec_probe(kExecPath);
  linx_spec_execve(kExecPath, argv, empty_envp);
  LOG_LIT("LINX_SPEC_FAIL execve\\n");
  poweroff_now();
"""

    c_src = out_dir / f"init_{bench.replace('.', '_')}.c"
    c_bin = out_dir / f"init_{bench.replace('.', '_')}"

    src = f"""#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <signal.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>

#ifndef LINX_SPEC_SELFTEST_WRITEV
#define LINX_SPEC_SELFTEST_WRITEV 0
#endif

#ifndef LINX_SPEC_SELFTEST_FP
#define LINX_SPEC_SELFTEST_FP 0
#endif

#ifndef LINX_SPEC_SELFTEST_PRINTF
#define LINX_SPEC_SELFTEST_PRINTF 0
#endif

#ifndef LINX_SPEC_STACK_LIMIT_BYTES
#define LINX_SPEC_STACK_LIMIT_BYTES (256ULL * 1024ULL * 1024ULL)
#endif

#ifndef LINX_SPEC_STACK_LIMIT_UNLIMITED
#define LINX_SPEC_STACK_LIMIT_UNLIMITED 0
#endif

#ifndef LINX_SPEC_IOBUF_SIZE
#define LINX_SPEC_IOBUF_SIZE 512
#endif

#ifndef LINUX_REBOOT_MAGIC1
#define LINUX_REBOOT_MAGIC1 0xfee1dead
#endif
#ifndef LINUX_REBOOT_MAGIC2
#define LINUX_REBOOT_MAGIC2 672274793
#endif
#ifndef LINUX_REBOOT_CMD_POWER_OFF
#define LINUX_REBOOT_CMD_POWER_OFF 0x4321fedc
#endif

static int raw_openat(const char *path, int flags, int mode) {{
  return open(path, flags, mode);
}}

static long linx_spec_raw_syscall3(long n, long a0, long a1, long a2) {{
  long ret;

  __asm__ volatile(
      "c.movr %1, ->a0\\n"
      "c.movr %2, ->a1\\n"
      "c.movr %3, ->a2\\n"
      "c.movr %4, ->a7\\n"
      "acrc 1\\n"
      "c.bstop\\n"
      "C.BSTART\\n"
      "c.movr a0, ->%0\\n"
      : "=r"(ret)
      : "r"(a0), "r"(a1), "r"(a2), "r"(n)
      : "a0", "a1", "a2", "a7",
        "x0", "x1", "x2", "x3", "memory");

  return ret;
}}

static long linx_spec_raw_syscall4(long n, long a0, long a1, long a2, long a3) {{
  long ret;

  __asm__ volatile(
      "c.movr %1, ->a0\\n"
      "c.movr %2, ->a1\\n"
      "c.movr %3, ->a2\\n"
      "c.movr %4, ->a3\\n"
      "c.movr %5, ->a7\\n"
      "acrc 1\\n"
      "c.bstop\\n"
      "C.BSTART\\n"
      "c.movr a0, ->%0\\n"
      : "=r"(ret)
      : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(n)
      : "a0", "a1", "a2", "a3", "a7",
        "x0", "x1", "x2", "x3", "memory");

  return ret;
}}

static long linx_spec_raw_syscall5(long n, long a0, long a1, long a2, long a3, long a4) {{
  long ret;

  __asm__ volatile(
      "c.movr %1, ->a0\\n"
      "c.movr %2, ->a1\\n"
      "c.movr %3, ->a2\\n"
      "c.movr %4, ->a3\\n"
      "c.movr %5, ->a4\\n"
      "c.movr %6, ->a7\\n"
      "acrc 1\\n"
      "c.bstop\\n"
      "C.BSTART\\n"
      "c.movr a0, ->%0\\n"
      : "=r"(ret)
      : "r"(a0), "r"(a1), "r"(a2), "r"(a3), "r"(a4), "r"(n)
      : "a0", "a1", "a2", "a3", "a4", "a7",
        "x0", "x1", "x2", "x3", "memory");

  return ret;
}}

static int linx_spec_execve(const char *path, char *const argv[], char *const envp[]) {{
  long ret = linx_spec_raw_syscall3(SYS_execve, (long)path, (long)argv, (long)envp);
  if (ret < 0 && ret >= -4095) {{
    errno = (int)-ret;
    return -1;
  }}
  return (int)ret;
}}

static long linx_spec_mount_raw(const char *src, const char *target, const char *fstype,
                                unsigned long flags, const void *data) {{
  return linx_spec_raw_syscall5(SYS_mount, (long)src, (long)target,
                                (long)fstype, (long)flags, (long)data);
}}

static int g_log_fd = -1;
static const unsigned long kDumpPrefixBytes = {dump_prefix_bytes}ul;
static const int kMirrorLogToStdout = {1 if mirror_log_stdout else 0};
static const int kSetupConsole = {1 if setup_console else 0};
static const int kUseVfork = {1 if use_vfork else 0};
static const int kUseKmsgLog = {1 if use_kmsg_log else 0};
static const int kTraceCwd = {1 if trace_cwd else 0};
static const unsigned int kGuestHeartbeatSec = {guest_heartbeat_sec}u;

__attribute__((noinline, returns_twice)) static pid_t spawn_child_process(void) {{
  if (!kUseVfork) {{
#ifdef SYS_fork
    return (pid_t)syscall(SYS_fork);
#endif
    return (pid_t)syscall(SYS_clone, (long)SIGCHLD, 0L, 0L, 0L, 0L);
  }}
  return kUseVfork ? vfork() : fork();
}}

static int wait_status_from_siginfo(const siginfo_t *si) {{
  switch (si->si_code) {{
  case CLD_EXITED:
    return ((si->si_status & 0xff) << 8);
  case CLD_KILLED:
    return (si->si_status & 0x7f);
  case CLD_DUMPED:
    return (si->si_status & 0x7f) | 0x80;
  case CLD_STOPPED:
    return ((si->si_status & 0xff) << 8) | 0x7f;
  case CLD_CONTINUED:
    return 0xffff;
  default:
    return -1;
  }}
}}

static int wait_child_waitid_blocking(pid_t child, int *status, int *wait_errno) {{
  siginfo_t si;
  memset(&si, 0, sizeof(si));
  errno = 0;
  int ret = waitid(P_PID, child, &si, WEXITED);
  if (ret == 0) {{
    *status = wait_status_from_siginfo(&si);
    *wait_errno = 0;
    return 0;
  }}
  *wait_errno = errno;
  return -1;
}}

static pid_t wait_child_blocking(pid_t child, int *status) {{
  pid_t ret = waitpid(child, status, 0);
  if (ret < 0 && errno == ECHILD) {{
    errno = 0;
    ret = waitpid(-1, status, 0);
  }}
  return ret;
}}

static int probe_child_alive(pid_t child) {{
  return kill(child, 0);
}}

static void write_fd_all(int fd, const char *p, unsigned long n) {{
  while (n > 0) {{
    ssize_t wr = write(fd, p, n);
    if (wr <= 0)
      return;
    p += (unsigned long)wr;
    n -= (unsigned long)wr;
  }}
}}

static void write_all(const char *p, unsigned long n) {{
  write_fd_all(STDOUT_FILENO, p, n);
}}

static void write_log_all(const char *p, unsigned long n) {{
  if (g_log_fd < 0 || kMirrorLogToStdout)
    write_fd_all(STDOUT_FILENO, p, n);
  if (g_log_fd >= 0)
    write_fd_all(g_log_fd, p, n);
}}

static void try_open_kmsg_log(void) {{
  if (kUseKmsgLog)
    g_log_fd = raw_openat("/dev/kmsg", O_WRONLY | O_CLOEXEC, 0);
  if (g_log_fd < 0 && kSetupConsole)
    g_log_fd = raw_openat("/dev/console", O_WRONLY | O_CLOEXEC, 0);
  if (g_log_fd < 0 && kSetupConsole)
    g_log_fd = raw_openat("/dev/ttyS0", O_WRONLY | O_CLOEXEC, 0);
  if (g_log_fd < 0)
    g_log_fd = -1;
}}

static void write_cstr(const char *s) {{
  const char *p = s;
  while (*p)
    p++;
  write_all(s, (unsigned long)(p - s));
}}

static void write_hex_u32(unsigned int v) {{
  static const char kHex[] = "0123456789abcdef";
  char out[8];
  int i;
  for (i = 7; i >= 0; --i) {{
    out[i] = kHex[v & 0xfu];
    v >>= 4;
  }}
  write_all(out, sizeof(out));
}}

static void write_log_cstr(const char *s) {{
  const char *p = s;
  while (*p)
    p++;
  write_log_all(s, (unsigned long)(p - s));
}}

static void write_log_hex_u64(unsigned long long v) {{
  static const char kHex[] = "0123456789abcdef";
  char out[16];
  int i;
  for (i = 15; i >= 0; --i) {{
    out[i] = kHex[(unsigned int)(v & 0xfu)];
    v >>= 4;
  }}
  write_log_all(out, sizeof(out));
}}

static void write_log_u64_dec(unsigned long long v) {{
  char out[32];
  int i = 0;

  if (v == 0) {{
    write_log_all("0", 1);
    return;
  }}

  while (v && i < (int)sizeof(out)) {{
    out[i++] = (char)('0' + (v % 10));
    v /= 10;
  }}

  while (i > 0)
    write_log_all(&out[--i], 1);
}}

static void write_log_s64_dec(long long v) {{
  if (v < 0) {{
    write_log_all("-", 1);
    write_log_u64_dec((unsigned long long)(-v));
  }} else {{
    write_log_u64_dec((unsigned long long)v);
  }}
}}

static void write_wait_status_log(pid_t wr, int wait_errno, int waitid_errno,
                                  int wait_method, int wait_fallback,
                                  int status) {{
  char line[192];
  int n = snprintf(
      line, sizeof(line),
      "LINX_SPEC_DBG wait wr=%lld errno=%lld waitid_errno=%lld "
      "method=%lld fallback=%lld status=0x%016llx exited=%lld "
      "code=%lld signaled=%lld sig=%lld\\n",
      (long long)wr, (long long)wait_errno, (long long)waitid_errno,
      (long long)wait_method, (long long)wait_fallback,
      (unsigned long long)(unsigned int)status, (long long)WIFEXITED(status),
      (long long)(WIFEXITED(status) ? WEXITSTATUS(status) : -1),
      (long long)WIFSIGNALED(status),
      (long long)(WIFSIGNALED(status) ? WTERMSIG(status) : -1));
  if (n > 0) {{
    if (n >= (int)sizeof(line))
      n = (int)sizeof(line) - 1;
    write_log_all(line, (unsigned long)n);
  }}
}}

static void log_cwd_probe(const char *tag) {{
  if (!kTraceCwd)
    return;

  char cwd[256];
  errno = 0;
  char *p = getcwd(cwd, sizeof(cwd));
  int err = errno;
  write_log_cstr("LINX_SPEC_CWD tag=");
  write_log_cstr(tag);
  write_log_cstr(" path=");
  if (p) {{
    write_log_cstr(cwd);
  }} else {{
    write_log_cstr("<error> errno=");
    write_log_s64_dec((long long)err);
  }}
  write_log_cstr("\\n");
}}

static void set_spec_stack_limit(void) {{
  struct rlimit rl;
#if LINX_SPEC_STACK_LIMIT_UNLIMITED
  rl.rlim_cur = RLIM_INFINITY;
  rl.rlim_max = RLIM_INFINITY;
#else
  rl.rlim_cur = (rlim_t)LINX_SPEC_STACK_LIMIT_BYTES;
  rl.rlim_max = (rlim_t)LINX_SPEC_STACK_LIMIT_BYTES;
#endif
#ifdef SYS_prlimit64
  long prlimit_ret = linx_spec_raw_syscall4(
      SYS_prlimit64, 0, RLIMIT_STACK, (long)&rl, 0);
  if (prlimit_ret == 0) {{
#if LINX_SPEC_STACK_LIMIT_UNLIMITED
    write_log_cstr("LINX_SPEC_DBG stack-limit=unlimited\\n");
#else
    write_log_cstr("LINX_SPEC_DBG stack-limit=");
    write_log_u64_dec((unsigned long long)LINX_SPEC_STACK_LIMIT_BYTES);
    write_log_cstr("\\n");
#endif
    return;
  }}
  if (prlimit_ret < 0 && prlimit_ret >= -4095) {{
    write_log_cstr("LINX_SPEC_WARN raw-prlimit-stack errno=");
    write_log_s64_dec((long long)-prlimit_ret);
    write_log_cstr("\\n");
  }} else {{
    write_log_cstr("LINX_SPEC_WARN raw-prlimit-stack ret=");
    write_log_s64_dec((long long)prlimit_ret);
    write_log_cstr("\\n");
  }}
#endif
  errno = 0;
  if (setrlimit(RLIMIT_STACK, &rl) < 0) {{
    int err = errno;
    write_log_cstr("LINX_SPEC_WARN setrlimit-stack errno=");
    write_log_s64_dec((long long)err);
    write_log_cstr("\\n");
  }} else {{
#if LINX_SPEC_STACK_LIMIT_UNLIMITED
    write_log_cstr("LINX_SPEC_DBG stack-limit=unlimited\\n");
#else
    write_log_cstr("LINX_SPEC_DBG stack-limit=");
    write_log_u64_dec((unsigned long long)LINX_SPEC_STACK_LIMIT_BYTES);
    write_log_cstr("\\n");
#endif
  }}
}}

static void log_preexec_probe(const char *path) {{
  struct stat st;
  errno = 0;
  int sr = stat(path, &st);
  int serr = errno;
  write_log_cstr("LINX_SPEC_PREEXEC path=");
  write_log_cstr(path);
  write_log_cstr(" stat=");
  write_log_s64_dec((long long)sr);
  write_log_cstr(" errno=");
  write_log_s64_dec((long long)serr);
  if (sr == 0) {{
    write_log_cstr(" mode=0x");
    write_log_hex_u64((unsigned long long)st.st_mode);
    write_log_cstr(" size=");
    write_log_u64_dec((unsigned long long)st.st_size);
  }}
  errno = 0;
  int fd = raw_openat(path, O_RDONLY, 0);
  int oerr = errno;
  write_log_cstr(" open=");
  write_log_s64_dec((long long)fd);
  write_log_cstr(" open_errno=");
  write_log_s64_dec((long long)oerr);
  if (fd >= 0) {{
    unsigned char hdr[4] = {{0, 0, 0, 0}};
    ssize_t rd = read(fd, hdr, sizeof(hdr));
    int rerr = errno;
    write_log_cstr(" read4=");
    write_log_s64_dec((long long)rd);
    write_log_cstr(" read_errno=");
    write_log_s64_dec((long long)rerr);
    if (rd == (ssize_t)sizeof(hdr)) {{
      unsigned int magic = ((unsigned int)hdr[0] << 24) |
                           ((unsigned int)hdr[1] << 16) |
                           ((unsigned int)hdr[2] << 8) |
                           (unsigned int)hdr[3];
      write_log_cstr(" magic=0x");
      write_log_hex_u64((unsigned long long)magic);
    }}
    close(fd);
  }}
  write_log_cstr("\\n");
}}

static unsigned long long va_arg_double_bits(int tag, ...) {{
  va_list ap;
  va_start(ap, tag);
  double d = va_arg(ap, double);
  va_end(ap);
  unsigned long long out = 0;
  memcpy(&out, (const void *)&d, sizeof(out));
  return out;
}}

static int hash_file_fnv1a64(const char *path,
                             unsigned long long *out_size,
                             unsigned long long *out_hash) {{
  int fd = raw_openat(path, O_RDONLY, 0);
  unsigned int hash = 2166136261u;
  unsigned long long size = 0;
  unsigned char buf[LINX_SPEC_IOBUF_SIZE];

  if (fd < 0)
    return -1;

  for (;;) {{
    ssize_t n = read(fd, buf, sizeof(buf));
    if (n == 0)
      break;
    if (n < 0) {{
      close(fd);
      return -1;
    }}
    for (ssize_t i = 0; i < n; ++i) {{
      hash ^= (unsigned int)buf[i];
      hash = hash
           + (hash << 1)
           + (hash << 4)
           + (hash << 7)
           + (hash << 8)
           + (hash << 24);
    }}
    size += (unsigned long long)n;
  }}

  close(fd);
  *out_size = size;
  *out_hash = (unsigned long long)hash;
  return 0;
}}

static int dump_file(const char *path) {{
  int fd = raw_openat(path, O_RDONLY, 0);
  char buf[LINX_SPEC_IOBUF_SIZE];
  if (fd < 0)
    return -1;

  for (;;) {{
    ssize_t n = read(fd, buf, sizeof(buf));
    if (n == 0) {{
      close(fd);
      return 0;
    }}
    if (n < 0) {{
      close(fd);
      return -1;
    }}
    write_log_all(buf, (unsigned long)n);
  }}
}}

static int dump_file_prefix(const char *path, unsigned long max_bytes) {{
  int fd = raw_openat(path, O_RDONLY, 0);
  char buf[LINX_SPEC_IOBUF_SIZE];
  if (fd < 0)
    return -1;

  unsigned long remaining = max_bytes;
  while (remaining > 0) {{
    unsigned long want = remaining < sizeof(buf) ? remaining : (unsigned long)sizeof(buf);
    ssize_t n = read(fd, buf, want);
    if (n == 0) {{
      close(fd);
      return 0;
    }}
    if (n < 0) {{
      close(fd);
      return -1;
    }}
    write_log_all(buf, (unsigned long)n);
    remaining -= (unsigned long)n;
  }}

  close(fd);
  return 0;
}}

static void write_log_marker_path_line(const char *marker, const char *path) {{
  char line[512];
  int n = snprintf(line, sizeof(line), "%s path=%s\\n", marker, path);
  if (n > 0 && n < (int)sizeof(line)) {{
    write_log_all(line, (unsigned long)n);
    return;
  }}
  write_log_cstr(marker);
  write_log_cstr(" path=");
  write_log_cstr(path);
  write_log_cstr("\\n");
}}

static void write_log_marker_errno_line(const char *marker, const char *path, int err) {{
  char line[512];
  int n = snprintf(line, sizeof(line), "%s path=%s errno=%lld\\n",
                   marker, path, (long long)err);
  if (n > 0 && n < (int)sizeof(line)) {{
    write_log_all(line, (unsigned long)n);
    return;
  }}
  write_log_cstr(marker);
  write_log_cstr(" path=");
  write_log_cstr(path);
  write_log_cstr(" errno=");
  write_log_s64_dec((long long)err);
  write_log_cstr("\\n");
}}

static void dump_log_file_with_markers(const char *begin_marker,
                                       const char *end_marker,
                                       const char *open_fail_marker,
                                       const char *read_fail_marker,
                                       const char *path,
                                       unsigned long max_bytes) {{
  int fd = raw_openat(path, O_RDONLY, 0);
  char buf[LINX_SPEC_IOBUF_SIZE];
  int wrote = 0;
  char last = '\\n';

  if (fd < 0) {{
    int open_errno = errno;
    write_log_marker_errno_line(open_fail_marker, path, open_errno);
    return;
  }}

  write_log_marker_path_line(begin_marker, path);

  unsigned long remaining = max_bytes;
  while (remaining > 0) {{
    unsigned long want = remaining < sizeof(buf) ? remaining : (unsigned long)sizeof(buf);
    errno = 0;
    ssize_t n = read(fd, buf, want);
    int read_errno = errno;
    if (n == 0)
      break;
    if (n < 0) {{
      close(fd);
      if (wrote && last != '\\n')
        write_log_cstr("\\n");
      write_log_marker_errno_line(read_fail_marker, path, read_errno);
      return;
    }}
    write_log_all(buf, (unsigned long)n);
    wrote = 1;
    last = buf[n - 1];
    remaining -= (unsigned long)n;
  }}

  close(fd);
  if (wrote && last != '\\n')
    write_log_cstr("\\n");
  write_log_cstr(end_marker);
  write_log_cstr("\\n");
}}

static int dump_run_file(const char *run_root, const char *name) {{
  char path[512];
  unsigned long i = 0;
  unsigned long j = 0;

  while (run_root[i] && i + 1 < sizeof(path)) {{
    path[i] = run_root[i];
    i++;
  }}

  if (i == 0 || path[i - 1] != '/') {{
    if (i + 1 >= sizeof(path))
      return -1;
    path[i++] = '/';
  }}

  while (name[j] && i + 1 < sizeof(path)) {{
    path[i++] = name[j++];
  }}
  path[i] = '\\0';

  return dump_file(path);
}}

static void setup_console(void) {{
  int fd_out = raw_openat("/dev/console", O_WRONLY, 0);
  if (fd_out < 0)
    fd_out = raw_openat("/dev/console", O_RDWR, 0);
  if (fd_out < 0)
    fd_out = raw_openat("/dev/ttyS0", O_WRONLY, 0);
  if (fd_out < 0)
    fd_out = raw_openat("/dev/ttyS0", O_RDWR, 0);
  if (fd_out < 0)
    fd_out = raw_openat("/dev/kmsg", O_WRONLY, 0);
  if (fd_out < 0)
    fd_out = raw_openat("/dev/null", O_WRONLY, 0);

  if (fd_out >= 0) {{
    /*
     * Duplicate output fds before touching stdin. In early init the first open
     * can return fd 0, so this ordering avoids aliasing stdout/stderr onto a
     * read-only stdin fd.
     */
    (void)dup2(fd_out, STDOUT_FILENO);
    (void)dup2(fd_out, STDERR_FILENO);
  }}

  {{
    int fd_in = raw_openat("/dev/null", O_RDONLY, 0);
    if (fd_in < 0)
      fd_in = raw_openat("/dev/console", O_RDONLY, 0);
    if (fd_in >= 0) {{
      (void)dup2(fd_in, STDIN_FILENO);
      if (fd_in > STDERR_FILENO && fd_in != fd_out)
        close(fd_in);
    }} else if (fd_out >= 0) {{
      (void)dup2(fd_out, STDIN_FILENO);
    }}
  }}

  if (fd_out > STDERR_FILENO)
    close(fd_out);
}}

__attribute__((noreturn)) static void spin_forever(void) {{
  for (;;) {{
    __asm__ __volatile__("" ::: "memory");
  }}
}}

__attribute__((noreturn)) static void poweroff_now(void) {{
  sync();
  (void)reboot(LINUX_REBOOT_CMD_POWER_OFF);
  spin_forever();
}}

static void selftest_writev(void) {{
#if LINX_SPEC_SELFTEST_WRITEV
  struct iovec iov[2];
  iov[0].iov_base = (void *)"AAA";
  iov[0].iov_len = 3;
  iov[1].iov_base = (void *)"BBB";
  iov[1].iov_len = 3;

  int fd = raw_openat("/tmp/linx_spec_writev_test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
  if (fd < 0) {{
    write_cstr("LINX_SPEC_FAIL writev-selftest-open\\n");
    poweroff_now();
  }}

  ssize_t wr = writev(fd, iov, 2);
  close(fd);
  if (wr != 6) {{
    write_cstr("LINX_SPEC_FAIL writev-selftest-wr\\n");
    poweroff_now();
  }}

  fd = raw_openat("/tmp/linx_spec_writev_test.txt", O_RDONLY, 0);
  if (fd < 0) {{
    write_cstr("LINX_SPEC_FAIL writev-selftest-reopen\\n");
    poweroff_now();
  }}

  char buf[6];
  ssize_t rd = read(fd, buf, sizeof(buf));
  close(fd);
  if (rd != (ssize_t)sizeof(buf) || memcmp(buf, "AAABBB", sizeof(buf)) != 0) {{
    write_cstr("LINX_SPEC_FAIL writev-selftest-rd\\n");
    poweroff_now();
  }}
#endif
}}

static void selftest_fp_bits(void) {{
#if LINX_SPEC_SELFTEST_FP
  unsigned long long bits = 0;
  char line[160];

  /*
   * Keep these inputs volatile so the compiler cannot constant-fold the
   * conversions/ops away. SPECINT failures have historically been "looks fine
   * in bits" when we were only printing constants.
   */
  volatile unsigned long long vi = 123ull;
  volatile double d3 = 3.0;
  volatile double d05 = 0.5;
  volatile double denom = 4294967296.0;
  volatile double fmtv = 0.819302;

  unsigned long long vabits = va_arg_double_bits(0, (double)fmtv);
  write_cstr("LINX_SPEC_DBG va_arg(double) bits=0x");
  write_log_hex_u64(vabits);
  write_cstr("\\n");
  if (vabits != 0x3fea37b8d3f1843cull) {{
    write_cstr("LINX_SPEC_FAIL fp-selftest-vaarg-double\\n");
    poweroff_now();
  }}

  /* Integer -> double conversion (forces UC/VTCVT execution). */
  volatile double fp_cvt = (double)vi;
  memcpy(&bits, (const void *)&fp_cvt, sizeof(bits));
  int n1 = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG fpcvt123 bits=0x%016llx\\n",
                    bits);
  if (n1 > 0 && n1 < (int)sizeof(line))
    write_all(line, (unsigned long)n1);
  if (bits != 0x405ec00000000000ull) {{
    write_cstr("LINX_SPEC_FAIL fp-selftest-fpcvt123\\n");
    poweroff_now();
  }}

  /* 1.0 / 2^32 runtime division. */
  volatile double fp_k = 1.0 / denom;
  memcpy(&bits, (const void *)&fp_k, sizeof(bits));
  int n2 = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG fpk bits=0x%016llx\\n",
                    bits);
  if (n2 > 0 && n2 < (int)sizeof(line))
    write_all(line, (unsigned long)n2);
  if (bits != 0x3df0000000000000ull) {{
    write_cstr("LINX_SPEC_FAIL fp-selftest-fpk\\n");
    poweroff_now();
  }}

  /* Runtime multiply (forces __muldf3 or FMUL path). */
  volatile double fp_mul = d3 * d05;
  memcpy(&bits, (const void *)&fp_mul, sizeof(bits));
  int n3 = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG fpmul bits=0x%016llx\\n",
                    bits);
  if (n3 > 0 && n3 < (int)sizeof(line))
    write_all(line, (unsigned long)n3);
  if (bits != 0x3ff8000000000000ull) {{
    write_cstr("LINX_SPEC_FAIL fp-selftest-fpmul\\n");
    poweroff_now();
  }}

  /* Float -> integer conversions used by musl printf floating formatting. */
  volatile double dscale = fmtv * 1000000.0;
  volatile unsigned int u32_scale = (unsigned int)dscale;
  int n4 = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG fptoui32_scale=%u\\n",
                    (unsigned)u32_scale);
  if (n4 > 0 && n4 < (int)sizeof(line))
    write_all(line, (unsigned long)n4);
  if (u32_scale != 819302u) {{
    write_cstr("LINX_SPEC_FAIL fp-selftest-fptoui32_scale\\n");
    poweroff_now();
  }}

  /* Sanity: show raw bits for the formatting probe value. */
  memcpy(&bits, (const void *)&fmtv, sizeof(bits));
  int nb = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG fmtv bits=0x%016llx\\n",
                    bits);
  if (nb > 0 && nb < (int)sizeof(line))
    write_all(line, (unsigned long)nb);

  /* libc puts() behavior (banner regression triage). */
  int outfd = fileno(stdout);
  int errfd = fileno(stderr);
  int nfds = snprintf(line, sizeof(line),
                      "LINX_SPEC_DBG stdio fds stdout=%d stderr=%d\\n",
                      outfd, errfd);
  if (nfds > 0 && nfds < (int)sizeof(line))
    write_all(line, (unsigned long)nfds);

  /* libc float formatting sanity: should not print all zeros. */
  char fmtbuf[32];
  int fn = snprintf(fmtbuf, sizeof(fmtbuf), "%.6f", (double)fmtv);
  int nf = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG snprintf(0.819302)=<%s> n=%d\\n",
                    fmtbuf, fn);
  if (nf > 0 && nf < (int)sizeof(line))
    write_all(line, (unsigned long)nf);
  if (fn != 8 || memcmp(fmtbuf, "0.819302", 8) != 0) {{
    write_cstr("LINX_SPEC_WARN fp-selftest-snprintf\\n");
  }}

  /* Hex-float formatting (%a) helps distinguish dtoa vs value issues. */
  char fmtabuf[64];
  int fan = snprintf(fmtabuf, sizeof(fmtabuf), "%a", (double)fmtv);
  int fa = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG snprintf(%%a)=<%s> n=%d\\n",
                    fmtabuf, fan);
  if (fa > 0 && fa < (int)sizeof(line))
    write_all(line, (unsigned long)fa);

  /* Direct writev() probe (puts/fwrite use writev internally on musl). */
  struct iovec wiov[2];
  wiov[0].iov_base = (void *)"WV";
  wiov[0].iov_len = 2;
  wiov[1].iov_base = (void *)"\\n";
  wiov[1].iov_len = 1;
  write_cstr("LINX_SPEC_DBG before_direct_writev\\n");
  errno = 0;
  ssize_t wvr = writev(STDOUT_FILENO, wiov, 2);
  int wve = errno;
  write_cstr("LINX_SPEC_DBG after_direct_writev\\n");
  int nwv = snprintf(line, sizeof(line),
                     "LINX_SPEC_DBG direct_writev ret=%lld errno=%d\\n",
                     (long long)wvr, wve);
  if (nwv > 0 && nwv < (int)sizeof(line))
    write_all(line, (unsigned long)nwv);

  errno = 0;
  int pr = puts("LINX_SPEC_DBG puts_selftest");
  int pe = errno;
  int np = snprintf(line, sizeof(line),
                    "LINX_SPEC_DBG puts ret=%d errno=%d\\n", pr, pe);
  if (np > 0 && np < (int)sizeof(line))
    write_all(line, (unsigned long)np);
#endif
}}

static void selftest_printf_stdio(void) {{
#if LINX_SPEC_SELFTEST_PRINTF
  int pr = printf("LINX_SPEC_DBG printf_int seed=%d count=%d\\n",
                  324342, 24239);
  (void)fflush(stdout);
  if (pr < 0) {{
    write_cstr("LINX_SPEC_FAIL printf-selftest-ret\\n");
    poweroff_now();
  }}
#endif
}}

#define WRITE_LIT(s) write_all((s), (unsigned long)(sizeof(s) - 1))
#define LOG_LIT(s) write_log_all((s), (unsigned long)(sizeof(s) - 1))

int main(void) {{
  if (kSetupConsole)
    setup_console();
  char *argv[] = {{
{argv_items}
    NULL,
  }};
  static const char kExecPath[] = "{_c_escape(exec_path)}";

  (void)mkdir("/proc", 0755);
  (void)mkdir("/sys", 0755);
  (void)mkdir("/dev", 0755);
  /* Keep static device nodes from initramfs (/dev/console, /dev/ttyS0). */
  (void)linx_spec_mount_raw("proc", "/proc", "proc", 0, "");
  (void)linx_spec_mount_raw("sysfs", "/sys", "sysfs", 0, "");
  selftest_fp_bits();
  selftest_printf_stdio();
  selftest_writev();
  try_open_kmsg_log();
  set_spec_stack_limit();
  /* Use inherited init stdio from the kernel console wiring. */
  LOG_LIT("LINX_SPEC_START {_c_escape(bench)}\\n");
  LOG_LIT("LINX_SPEC_ARGV_BEGIN\\n");
  for (int i = 0; argv[i]; ++i) {{
    LOG_LIT("LINX_SPEC_ARGV index=");
    write_log_u64_dec((unsigned long long)i);
    LOG_LIT(" value=");
    write_log_cstr(argv[i]);
    LOG_LIT("\\n");
  }}
  LOG_LIT("LINX_SPEC_ARGV_END\\n");
{transport_block}

  LOG_LIT("LINX_SPEC_DBG step=chdir\\n");
  if (chdir("{_c_escape(guest_run)}") < 0) {{
    LOG_LIT("LINX_SPEC_FAIL chdir-rundir\\n");
    poweroff_now();
  }}
  LOG_LIT("LINX_SPEC_DBG step=chdir-ok\\n");
  log_cwd_probe("parent-after-chdir");

{run_block}
}}
"""

    c_src.write_text(src, encoding="utf-8")

    c_obj = out_dir / f"init_{bench.replace('.', '_')}.o"
    init_static = _choose_init_static(transport, sysroot)

    compile_cmd = [
        str(clang),
        "--target=linx64-unknown-linux-musl",
        f"--sysroot={sysroot}",
        "-O1",
        "-c",
        "-o",
        str(c_obj),
        str(c_src),
    ]
    if os.environ.get("LINX_SPEC_SELFTEST_WRITEV", "").lower() in {"1", "true", "yes"}:
        compile_cmd.insert(4, "-DLINX_SPEC_SELFTEST_WRITEV=1")
    if os.environ.get("LINX_SPEC_SELFTEST_FP", "").lower() in {"1", "true", "yes"}:
        compile_cmd.insert(4, "-DLINX_SPEC_SELFTEST_FP=1")
    if os.environ.get("LINX_SPEC_SELFTEST_PRINTF", "").lower() in {"1", "true", "yes"}:
        compile_cmd.insert(4, "-DLINX_SPEC_SELFTEST_PRINTF=1")
    for define in _spec_stack_limit_defines():
        compile_cmd.insert(4, define)
    if init_static:
        compile_cmd.insert(4, "-fPIE")
    proc = _run(compile_cmd)
    if proc.returncode != 0:
        raise SystemExit(
            f"error: failed to compile init source for {bench}:\n"
            + proc.stdout.decode("utf-8", errors="replace")
        )

    libdir = sysroot / "lib"
    crt1 = libdir / ("rcrt1.o" if init_static else "Scrt1.o")
    crti = libdir / "crti.o"
    crtn = libdir / "crtn.o"
    runtime_rt = libdir / "liblinx_builtin_rt.a"
    builtins_rt = libdir / "libclang_rt.builtins-linx64.a"
    libc_a = libdir / "libc.a"
    libc_so = libdir / "libc.so"
    required = [crt1, crti, crtn, runtime_rt]
    if init_static:
        required.extend([libc_a, builtins_rt])
    else:
        required.append(libc_so)
    for req in required:
        if not req.exists():
            raise SystemExit(f"error: missing required sysroot artifact: {req}")

    link_cmd = [str(clang), "--target=linx64-unknown-linux-musl", f"--sysroot={sysroot}", "-fuse-ld=lld", "-nostdlib"]
    if init_static:
        link_cmd.extend(
            [
                "-static",
                "-Wl,-pie",
                "-Wl,-z,now",
                str(crt1),
                str(crti),
                str(c_obj),
                str(runtime_rt),
                str(builtins_rt),
                "-L" + str(libdir),
                "-L" + str(sysroot / "usr" / "lib"),
                "-lc",
                str(crtn),
                "-Wl,--build-id=none",
                "-Wl,--image-base=0x40000000",
                "-o",
                str(c_bin),
            ]
        )
    else:
        link_cmd.extend(
            [
                "-Wl,-pie",
                "-Wl,-z,now",
                str(crt1),
                str(crti),
                str(c_obj),
                str(runtime_rt),
                "-L" + str(libdir),
                "-L" + str(sysroot / "usr" / "lib"),
                "-lc",
                str(crtn),
                "-Wl,--dynamic-linker=/lib/ld-musl-linx64.so.1",
                "-Wl,--image-base=0x40000000",
                "-o",
                str(c_bin),
            ]
        )
    proc = _run(link_cmd)
    if proc.returncode != 0:
        raise SystemExit(
            f"error: failed to link init for {bench}:\n"
            + proc.stdout.decode("utf-8", errors="replace")
        )

    return c_bin


def _build_initramfs(
    bench: str,
    out_dir: Path,
    gen_init_cpio: Path,
    init_bin: Path,
    sysroot: Path,
    run_dir: Path | None,
    transport: str,
    include_shared_runtime: bool,
) -> tuple[Path, Path]:
    init_list = out_dir / f"initramfs_{bench.replace('.', '_')}.list"
    init_cpio = out_dir / f"initramfs_{bench.replace('.', '_')}.cpio"
    init_log = out_dir / f"initramfs_{bench.replace('.', '_')}.log"

    lines = [
        "dir /dev 0755 0 0",
        "nod /dev/console 0600 0 0 c 5 1",
        "nod /dev/null 0666 0 0 c 1 3",
        "nod /dev/kmsg 0600 0 0 c 1 11",
        "nod /dev/ttyS0 0600 0 0 c 4 64",
        "dir /proc 0755 0 0",
        "dir /sys 0755 0 0",
        "dir /tmp 1777 0 0",
        "dir /lib 0755 0 0",
        f"file /init {init_bin} 0755 0 0",
    ]
    if include_shared_runtime:
        libc_so = sysroot / "lib" / "libc.so"
        if not libc_so.exists():
            raise SystemExit(f"error: missing libc.so in sysroot: {libc_so}")
        lines.extend(
            [
                f"file /lib/libc.so {libc_so} 0755 0 0",
                f"file /lib/ld-musl-linx64.so.1 {libc_so} 0755 0 0",
                f"file /lib/libm.so {libc_so} 0755 0 0",
            ]
        )

    if transport == "9p":
        lines.append("dir /spec 0755 0 0")
    elif transport == "initramfs":
        if run_dir is None:
            raise SystemExit("error: run_dir is required for initramfs transport")
        lines.append("dir /spec-run 0755 0 0")
        for host in sorted(run_dir.rglob("*")):
            rel = host.relative_to(run_dir).as_posix()
            guest = f"/spec-run/{rel}"
            if host.is_symlink():
                lines.append(f"slink {guest} {os.readlink(host)} 0777 0 0")
            elif host.is_dir():
                lines.append(f"dir {guest} 0755 0 0")
            elif host.is_file():
                mode = 0o755 if os.access(host, os.X_OK) else 0o644
                lines.append(f"file {guest} {host} {mode:o} 0 0")
    else:
        raise SystemExit(f"error: unsupported transport: {transport}")

    lines.append("")
    init_list.write_text("\n".join(lines), encoding="utf-8")

    cmd = [str(gen_init_cpio), "-o", str(init_cpio), str(init_list)]
    proc = _run(cmd)
    init_log.write_bytes(proc.stdout)
    if proc.returncode != 0:
        raise SystemExit(f"error: failed to build initramfs for {bench} (see {init_log})")

    return init_cpio, init_log


def _run_qemu(
    bench: str,
    qemu: Path,
    kernel: Path,
    initramfs: Path,
    spec_dir: Path,
    timeout: int,
    out_log: Path,
    transport: str,
    memory_mb: int,
    heartbeat_sec: float,
    qemu_heartbeat_interval: int,
    qemu_heartbeat_regs: bool,
    qemu_heartbeat_code_bytes: int,
    qemu_heartbeat_same_site_warn: int,
    qemu_frame_stats: bool,
    qemu_frame_restore_host_load: bool,
    qemu_frame_restore_host_verify: bool,
    qemu_frame_restore_host_verify_limit: int,
    qemu_tlb_stats: bool,
    qemu_tlb_inv_hot: bool,
    qemu_tlb_fill_stats: bool,
    qemu_tlb_fill_hot: bool,
    qemu_tb_stats: bool,
    qemu_fret_stk_trace: dict[str, str],
    qemu_fentry_trace: dict[str, str],
    no_progress_timeout: float,
    append_extra: str,
    symbolize_heartbeat: bool,
    qemu_fault_trace: bool,
    qemu_fault_trace_regs: bool,
    qemu_fault_trace_limit: int,
    qemu_fault_trace_filters: dict[str, str],
    qemu_pc_watch: dict[str, str],
    qemu_syscall_trace: dict[str, str],
    qemu_mem_trace: dict[str, str],
) -> dict[str, Any]:
    append = _build_kernel_append(transport, append_extra)

    machine = "virt"
    machine_extra = os.environ.get("LINX_SPEC_QEMU_MACHINE_EXTRA", "").strip()
    if machine_extra:
        if not machine_extra.startswith(","):
            machine += ","
        machine += machine_extra

    qemu_extra = shlex.split(os.environ.get("LINX_SPEC_QEMU_EXTRA_ARGS", ""))

    cmd = [
        str(qemu),
        "-machine",
        machine,
        "-nographic",
        "-monitor",
        "none",
        "-no-reboot",
        "-m",
        str(memory_mb),
        "-kernel",
        str(kernel),
        "-initrd",
        str(initramfs),
        "-append",
        append,
    ]
    if "-bios" not in cmd and "qemu-system-linx64-bios-none" not in qemu.name:
        cmd += ["-bios", "none"]
    cmd += qemu_extra
    if transport == "9p":
        cmd += [
            "-fsdev",
            f"local,id=specfs,path={spec_dir},security_model=none",
            "-device",
            "virtio-9p-device,fsdev=specfs,mount_tag=spec2017",
        ]

    qemu_env = os.environ.copy()
    _apply_qemu_debug_env(
        qemu_env,
        qemu_heartbeat_interval=qemu_heartbeat_interval,
        qemu_heartbeat_regs=qemu_heartbeat_regs,
        qemu_heartbeat_code_bytes=qemu_heartbeat_code_bytes,
        qemu_heartbeat_same_site_warn=qemu_heartbeat_same_site_warn,
        qemu_frame_stats=qemu_frame_stats,
        qemu_frame_restore_host_load=qemu_frame_restore_host_load,
        qemu_frame_restore_host_verify=qemu_frame_restore_host_verify,
        qemu_frame_restore_host_verify_limit=qemu_frame_restore_host_verify_limit,
        qemu_tlb_stats=qemu_tlb_stats,
        qemu_tlb_inv_hot=qemu_tlb_inv_hot,
        qemu_tlb_fill_stats=qemu_tlb_fill_stats,
        qemu_tlb_fill_hot=qemu_tlb_fill_hot,
        qemu_tb_stats=qemu_tb_stats,
        qemu_fret_stk_trace=qemu_fret_stk_trace,
        qemu_fentry_trace=qemu_fentry_trace,
        qemu_fault_trace=qemu_fault_trace,
        qemu_fault_trace_regs=qemu_fault_trace_regs,
        qemu_fault_trace_limit=qemu_fault_trace_limit,
        qemu_fault_trace_filters=qemu_fault_trace_filters,
        qemu_pc_watch=qemu_pc_watch,
        qemu_syscall_trace=qemu_syscall_trace,
        qemu_mem_trace=qemu_mem_trace,
    )
    qemu_debug_env = _qemu_debug_env_summary(qemu_env)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=qemu_env,
    )
    heartbeat_counts_progress = os.environ.get("LINX_SPEC_HEARTBEAT_COUNTS_PROGRESS", "").lower()
    if heartbeat_counts_progress in {"1", "true", "yes"}:
        heartbeat_progress_enabled = True
    elif heartbeat_counts_progress in {"0", "false", "no"}:
        heartbeat_progress_enabled = False
    else:
        # Initramfs lane redirects benchmark output to guest files, so stdout
        # can remain quiet for long stretches while work is still progressing.
        # Once QEMU's own BPC heartbeat is enabled, only QEMU output should
        # reset no-progress accounting; host heartbeat lines are just liveness
        # breadcrumbs from the wrapper.
        heartbeat_progress_enabled = (transport == "initramfs" and qemu_heartbeat_interval <= 0)
    fd = proc.stdout.fileno() if proc.stdout is not None else -1
    chunks: list[bytes] = []
    bytes_seen = 0
    timed_out = False
    stalled = False
    terminal_failure_seen = False
    recent_output = b""
    terminal_failure_markers = (
        b"Kernel panic - not syncing",
        b"LINX_PANIC",
        b"LINX_EXIT_INIT",
        b"LINX_DIE",
        b"LINX_USER_TRAP",
        b"[linx trap]",
    )
    start = time.monotonic()
    last_activity = start
    terminal_failure_deadline: float | None = None
    next_heartbeat = start + heartbeat_sec if heartbeat_sec > 0 else float("inf")

    out_log.parent.mkdir(parents=True, exist_ok=True)
    log_fp = out_log.open("wb")

    while fd >= 0:
        now = time.monotonic()
        elapsed = now - start
        if terminal_failure_deadline is not None and now >= terminal_failure_deadline:
            break
        if elapsed >= timeout:
            timed_out = True
            break

        idle = now - last_activity
        if no_progress_timeout > 0 and idle >= no_progress_timeout:
            stalled = True
            break

        wait_for = min(0.5, timeout - elapsed)
        if heartbeat_sec > 0:
            wait_for = min(wait_for, max(0.0, next_heartbeat - now))
        if no_progress_timeout > 0:
            wait_for = min(wait_for, max(0.0, no_progress_timeout - idle))
        if terminal_failure_deadline is not None:
            wait_for = min(wait_for, max(0.0, terminal_failure_deadline - now))

        readable, _, _ = select.select([fd], [], [], wait_for)
        if readable:
            try:
                data = os.read(fd, 8192)
            except OSError:
                data = b""
            if not data:
                fd = -1
            else:
                chunks.append(data)
                log_fp.write(data)
                log_fp.flush()
                bytes_seen += len(data)
                last_activity = time.monotonic()
                recent_output = (recent_output + data)[-4096:]
                for marker in terminal_failure_markers:
                    marker_pos = recent_output.find(marker)
                    if marker_pos < 0:
                        continue
                    terminal_failure_seen = True
                    if b"\n" in recent_output[marker_pos:]:
                        terminal_failure_deadline = time.monotonic()
                    elif terminal_failure_deadline is None:
                        terminal_failure_deadline = time.monotonic() + 1.0
                    break
                if terminal_failure_deadline is not None and terminal_failure_deadline <= time.monotonic():
                    break

        now = time.monotonic()
        if heartbeat_sec > 0 and now >= next_heartbeat:
            hb_line = (
                "LINX_SPEC_HEARTBEAT "
                f"bench={bench} "
                f"elapsed={now - start:.1f}s "
                f"idle={now - last_activity:.1f}s "
                f"bytes={bytes_seen}"
            )
            print(hb_line, file=sys.stderr, flush=True)
            hb_data = (hb_line + "\n").encode("utf-8")
            chunks.append(hb_data)
            log_fp.write(hb_data)
            log_fp.flush()
            if heartbeat_progress_enabled:
                last_activity = now
            while next_heartbeat <= now:
                next_heartbeat += heartbeat_sec

    if timed_out or stalled or terminal_failure_seen:
        proc.kill()

    extra = b""
    try:
        out_extra, _ = proc.communicate(timeout=1.0)
        if out_extra:
            extra = out_extra
    except subprocess.TimeoutExpired:
        proc.kill()
        out_extra, _ = proc.communicate()
        if out_extra:
            extra = out_extra
    if extra:
        chunks.append(extra)
        log_fp.write(extra)
        log_fp.flush()
    log_fp.close()

    text = _final_qemu_log_text(out_log, chunks)
    qemu_rc = proc.returncode if proc.returncode is not None else -1
    panic_seen = (
        "Kernel panic - not syncing" in text
        or "LINX_PANIC" in text
        or "LINX_EXIT_INIT" in text
    )
    fail_marker = f"LINX_SPEC_FAIL {bench}" in text or "LINX_SPEC_FAIL" in text
    classification = _classify_qemu_result(
        text=text,
        timed_out=timed_out,
        stalled=stalled,
        panic_seen=panic_seen,
        fail_marker=fail_marker,
    )
    if symbolize_heartbeat:
        heartbeat_kernel_symbols = _symbolize_heartbeat_kernel_sites(text, kernel)
    else:
        heartbeat_kernel_symbols = {
            "enabled": False,
            "ok": False,
            "tool": "",
            "kernel": str(kernel),
            "sites": [],
            "panic_loop": False,
            "evidence": "",
        }
    if (
        classification["class"]
        in {"live-timeout", "same-site-live-timeout", "timeout-no-bpc-progress"}
        and heartbeat_kernel_symbols.get("panic_loop")
    ):
        classification["class"] = "kernel-panic-loop-timeout"
        classification["evidence"] = str(
            heartbeat_kernel_symbols.get("evidence") or classification["evidence"]
        )[:512]
    fcmp_trace = _fcmp_trace_summary(text)
    tlb_fill_trace = _tlb_fill_trace_summary(text)
    mprotect_trace = _mprotect_trace_summary(text)
    heartbeat_stall = classification["heartbeat_stall"]
    heartbeat_tlb_fill = _heartbeat_tlb_fill_summary(classification["last_heartbeat"])
    heartbeat_mmu_cache = _heartbeat_mmu_cache_summary(classification["last_heartbeat"])
    heartbeat_frame_stats = _heartbeat_frame_stats_summary(classification["last_heartbeat"])
    heartbeat_tlb_invalidation = _heartbeat_tlb_invalidation_summary(classification["last_heartbeat"])
    heartbeat_tb_stats = _heartbeat_tb_stats_summary(classification["last_heartbeat"])
    heartbeat_tlb_fill_hot = _tlb_fill_hot_summary(text)
    heartbeat_tlb_inv_hot = _tlb_inv_hot_summary(text)
    bstart_cache_stats = _bstart_cache_stats_summary(text)
    pc_watch = _pc_watch_summary(text)

    qemu_info = {
        "command": cmd,
        "qemu_machine": machine,
        "qemu_machine_extra": machine_extra,
        "qemu_extra_args": qemu_extra,
        "qemu_debug_env": qemu_debug_env,
        "qemu_frame_stats": bool(qemu_frame_stats),
        "qemu_frame_restore_host_load": bool(qemu_frame_restore_host_load),
        "qemu_tlb_stats": bool(qemu_tlb_stats),
        "qemu_tlb_inv_hot": bool(qemu_tlb_inv_hot),
        "qemu_tlb_fill_stats": bool(qemu_tlb_fill_stats),
        "qemu_tlb_fill_hot": bool(qemu_tlb_fill_hot),
        "qemu_tb_stats": bool(qemu_tb_stats),
        "qemu_rc": qemu_rc,
        "timed_out": timed_out,
        "stalled": stalled,
        "panic_seen": panic_seen,
        "die_seen": "LINX_DIE" in text,
        "trap_seen": "LINX_USER_TRAP" in text or "[linx trap]" in text.lower(),
        "pass_marker": f"LINX_SPEC_PASS {bench}" in text,
        "fail_marker": fail_marker,
        "failure_class": classification["class"],
        "failure_evidence": classification["evidence"],
        "last_heartbeat": classification["last_heartbeat"],
        "heartbeat_progress": classification["heartbeat_progress"],
        "heartbeat_running": classification["heartbeat_running"],
        "heartbeat_site_progress": classification["heartbeat_site_progress"],
        "heartbeat_last_count": classification["heartbeat_last_count"],
        "heartbeat_last_bpc": classification["heartbeat_last_bpc"],
        "heartbeat_last_progress": classification["heartbeat_last_progress"],
        "heartbeat_last_same_site": classification["heartbeat_last_same_site"],
        "heartbeat_recent_unique_sites": classification["heartbeat_recent_unique_sites"],
        "heartbeat_recent_count_delta": classification["heartbeat_recent_count_delta"],
        "heartbeat_stall_seen": heartbeat_stall["seen"],
        "heartbeat_stall_count": heartbeat_stall["count"],
        "heartbeat_stall_last": heartbeat_stall["last"],
        "heartbeat_stall_repeats": heartbeat_stall["repeats"],
        "heartbeat_stall_threshold": heartbeat_stall["threshold"],
        "heartbeat_stall_bpc": heartbeat_stall["bpc"],
        "heartbeat_stall_status": heartbeat_stall["status"],
        "heartbeat_tlb_fill": heartbeat_tlb_fill,
        "heartbeat_mmu_cache": heartbeat_mmu_cache,
        "heartbeat_frame_stats": heartbeat_frame_stats,
        "heartbeat_tlb_invalidation": heartbeat_tlb_invalidation,
        "heartbeat_tb_stats": heartbeat_tb_stats,
        "heartbeat_tlb_fill_hot": heartbeat_tlb_fill_hot,
        "heartbeat_tlb_inv_hot": heartbeat_tlb_inv_hot,
        "bstart_cache_stats": bstart_cache_stats,
        "pc_watch": pc_watch,
        "heartbeat_kernel_symbols": heartbeat_kernel_symbols.get("sites", []),
        "heartbeat_kernel_symbolized": bool(heartbeat_kernel_symbols.get("ok", False)),
        "heartbeat_kernel_panic_loop": bool(heartbeat_kernel_symbols.get("panic_loop", False)),
        "heartbeat_kernel_symbol_evidence": str(heartbeat_kernel_symbols.get("evidence") or "")[:512],
        "fcmp_trace_seen": fcmp_trace["seen"],
        "fcmp_trace_count": fcmp_trace["count"],
        "fcmp_trace_last": fcmp_trace["last"],
        "fcmp_trace_samples": fcmp_trace["samples"],
        "tlb_fill_trace_seen": tlb_fill_trace["seen"],
        "tlb_fill_trace_count": tlb_fill_trace["count"],
        "tlb_fill_trace_last": tlb_fill_trace["last"],
        "tlb_fill_trace_samples": tlb_fill_trace["samples"],
        "mprotect_trace_seen": mprotect_trace["seen"],
        "mprotect_trace_count": mprotect_trace["count"],
        "mprotect_trace_last": mprotect_trace["last"],
        "mprotect_trace_samples": mprotect_trace["samples"],
        "log": str(out_log),
    }
    _specialize_spec_wrapper_failure(qemu_info, text)
    return qemu_info


def _classify_qemu_result(
    *,
    text: str,
    timed_out: bool,
    stalled: bool,
    panic_seen: bool,
    fail_marker: bool,
) -> dict[str, Any]:
    heartbeats = re.findall(r"^LINX_HEARTBEAT .*$", text, flags=re.MULTILINE)
    heartbeat = _heartbeat_summary(heartbeats)
    heartbeat_stall = _heartbeat_stall_summary(text)
    last_heartbeat = str(heartbeat["last"])
    base = {
        "last_heartbeat": last_heartbeat,
        "heartbeat_progress": heartbeat["running"],
        **_heartbeat_classification_fields(heartbeat),
        "heartbeat_stall": heartbeat_stall,
    }

    if panic_seen:
        line = _first_matching_line(text, ("LINX_PANIC", "Kernel panic - not syncing", "LINX_EXIT_INIT"))
        return {
            "class": "kernel-panic",
            "evidence": line,
            **base,
        }

    die = _first_matching_line(text, ("LINX_DIE",))
    if die:
        return {
            "class": "kernel-oops" if "Oops" in die else "kernel-die",
            "evidence": die,
            **base,
        }

    trap = _first_matching_line(text, ("LINX_USER_TRAP", "[linx trap]"))
    if trap:
        return {
            "class": "user-trap",
            "evidence": trap,
            **base,
        }

    if stalled:
        return {
            "class": "no-progress-timeout",
            "evidence": "no QEMU output before no-progress timeout",
            **base,
        }
    if timed_out:
        if heartbeat["site_progress"]:
            cls = "live-timeout"
        elif heartbeat["running"]:
            cls = "same-site-live-timeout"
        elif heartbeat["seen"]:
            cls = "timeout-no-bpc-progress"
        else:
            cls = "timeout-no-heartbeat"
        evidence = last_heartbeat or "timeout without LINX_HEARTBEAT evidence"
        return {
            "class": cls,
            "evidence": evidence,
            **base,
        }

    if "Bad file number" in text:
        return {
            "class": "fd-io-bad-file-number",
            "evidence": _first_matching_line(text, ("Bad file number",)),
            **base,
        }
    if "Bad file descriptor" in text:
        return {
            "class": "fd-io-bad-file-descriptor",
            "evidence": _first_matching_line(text, ("Bad file descriptor",)),
            **base,
        }
    if "Range iterator outside integer range" in text:
        return {
            "class": "user-arithmetic-range",
            "evidence": _first_matching_line(text, ("Range iterator outside integer range",)),
            **base,
        }

    execve = _first_matching_line(text, ("LINX_SPEC_FAIL execve",))
    if execve:
        return {
            "class": "execve-failure",
            "evidence": execve,
            **base,
        }

    if fail_marker:
        signal = _spec_child_signal(text)
        if signal is not None:
            oom = _spec_oom_evidence(text)
            if signal == 9 and oom:
                cls = "spec-child-sigkill-oom"
            elif signal == 9:
                cls = "spec-child-sigkill"
            elif signal == 11:
                cls = "spec-child-sigsegv"
            else:
                cls = "spec-child-signal"
            evidence = _spec_wrapper_failure_evidence(text)
            if oom:
                evidence = f"{evidence}; {oom}"[:512]
            return {
                "class": cls,
                "evidence": evidence,
                **base,
            }
        internal_error = _spec_stderr_internal_error(text)
        if internal_error:
            evidence = f"{internal_error}; {_spec_wrapper_failure_evidence(text)}"[:512]
            return {
                "class": "spec-benchmark-internal-error",
                "evidence": evidence,
                **base,
            }
        mem_init = _spec_mem_init_error(text)
        if mem_init:
            evidence = f"{mem_init}; {_spec_wrapper_failure_evidence(text)}"[:512]
            return {
                "class": "spec-mem-init-fail",
                "evidence": evidence,
                **base,
            }
        return {
            "class": "spec-wrapper-fail",
            "evidence": _spec_wrapper_failure_evidence(text),
            **base,
        }

    pc_watch = _first_matching_line(text, ("linx_pc_watch:", "LINX_CALL_TRACE_RING reason=pc_watch"))
    if pc_watch:
        return {
            "class": "pc-watch-exit",
            "evidence": pc_watch,
            **base,
        }

    return {
        "class": "none",
        "evidence": "",
        **base,
    }


def _final_qemu_log_text(out_log: Path, chunks: list[bytes]) -> str:
    chunk_data = b"".join(chunks)
    chunk_text = _decode_qemu_log_bytes(chunk_data)
    try:
        final_data = out_log.read_bytes()
    except OSError:
        return chunk_text
    if len(final_data) >= len(chunk_data):
        return _decode_qemu_log_bytes(final_data)
    return chunk_text


def _decode_qemu_log_bytes(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def _specialize_spec_wrapper_failure(qemu_info: dict[str, Any], text: str) -> None:
    if qemu_info.get("failure_class") != "spec-wrapper-fail":
        return
    mem_init = _spec_mem_init_error(text)
    if mem_init:
        evidence = f"{mem_init}; {_spec_wrapper_failure_evidence(text)}"[:512]
        qemu_info["failure_class"] = "spec-mem-init-fail"
        qemu_info["failure_evidence"] = evidence
        return
    internal_error = _spec_stderr_internal_error(text)
    if not internal_error:
        return
    evidence = f"{internal_error}; {_spec_wrapper_failure_evidence(text)}"[:512]
    qemu_info["failure_class"] = "spec-benchmark-internal-error"
    qemu_info["failure_evidence"] = evidence


def _first_matching_line(text: str, needles: tuple[str, ...]) -> str:
    for line in text.splitlines():
        if any(needle in line for needle in needles):
            return line[:512]
    return ""


def _spec_wrapper_failure_evidence(text: str) -> str:
    fail = _first_matching_line(text, ("LINX_SPEC_FAIL",)) or "LINX_SPEC_FAIL"
    if "chdir-rundir" in fail:
        mount = _first_matching_line(text, ("LINX_SPEC_WARN 9p-mount-failed",))
        if mount:
            return f"{fail}; {mount}"[:512]
    if "child-exit" not in fail:
        return fail
    wait = _first_matching_line(text, ("LINX_SPEC_DBG wait",))
    if not wait:
        return fail
    return f"{fail}; {wait}"[:512]


def _spec_stderr_internal_error(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    match = re.search(
        r"LINX_SPEC_STDERR_BEGIN\n(?P<body>.*?)\nLINX_SPEC_STDERR_END",
        text,
        flags=re.DOTALL,
    )
    if not match:
        return ""
    needles = (
        "benchmark internal error",
        "internal compiler error",
        "has encountered an internal error",
    )
    for raw in match.group("body").splitlines():
        line = raw.strip()
        if not line:
            continue
        lowered = line.lower()
        if any(needle in lowered for needle in needles):
            return line[:512]
    return ""


def _spec_mem_init_error(text: str) -> str:
    return _first_matching_line(text, ("spec_mem_init: Error mallocing",))


def _spec_child_signal(text: str) -> int | None:
    wait = _first_matching_line(text, ("LINX_SPEC_DBG wait",))
    if "signaled=1" not in wait:
        return None
    match = re.search(r"\bsig=([0-9]+)\b", wait)
    if not match:
        return None
    return int(match.group(1))


def _spec_oom_evidence(text: str) -> str:
    values = [int(value) for value in re.findall(r"^oom_kill\s+([0-9]+)\s*$", text, flags=re.MULTILINE)]
    if values and max(values) > 0:
        return f"oom_kill={values[-1]}"
    line = _first_matching_line(text, ("Out of memory", "Killed process"))
    return line


def _set_output_failure_class(qemu_info: dict[str, Any], cls: str, evidence: str) -> None:
    if qemu_info.get("failure_class") != "none":
        return
    qemu_info["failure_class"] = cls
    qemu_info["failure_evidence"] = evidence[:512]


def _annotate_hash_mismatch(qemu_info: dict[str, Any], hash_info: dict[str, Any]) -> None:
    if hash_info.get("ok", True):
        return
    checks = hash_info.get("checks", [])
    first_failed = next(
        (check for check in checks if isinstance(check, dict) and not check.get("ok", False)),
        None,
    )
    if not isinstance(first_failed, dict):
        _set_output_failure_class(qemu_info, "hash-mismatch", "host hash check failed")
        return

    output = first_failed.get("output_name", "<unknown>")
    actual_hash = first_failed.get("actual_hash", "<none>")
    expected_hash = first_failed.get("expected_hash", "<none>")
    actual_size = first_failed.get("actual_size", "<none>")
    expected_size = first_failed.get("expected_size", "<none>")
    _set_output_failure_class(
        qemu_info,
        "hash-mismatch",
        (
            f"{output}: actual hash {actual_hash} size {actual_size} "
            f"!= expected hash {expected_hash} size {expected_size}"
        ),
    )


def _annotate_specdiff_mismatch(
    qemu_runs: list[dict[str, Any]], specdiff_info: dict[str, Any]
) -> None:
    if specdiff_info.get("ok", True) or not qemu_runs:
        return
    if _strict_hash_checks_ok(specdiff_info):
        return
    checks = specdiff_info.get("checks", [])
    first_failed = next(
        (check for check in checks if isinstance(check, dict) and not check.get("ok", False)),
        None,
    )
    if isinstance(first_failed, dict):
        evidence = (
            f"{first_failed.get('out', '<unknown>')}: specdiff rc="
            f"{first_failed.get('returncode', '<none>')}"
        )
    else:
        evidence = "host specdiff failed"
    _set_output_failure_class(qemu_runs[-1], "specdiff-mismatch", evidence)


def _strict_hash_checks_ok(specdiff_info: dict[str, Any]) -> bool:
    if not specdiff_info.get("strict_hash", False):
        return False
    checks = specdiff_info.get("hash_checks", [])
    return bool(checks) and all(isinstance(check, dict) and check.get("ok", False) for check in checks)


def _hash_specdiff_result(ok: bool, hash_checks: list[dict[str, Any]], strict_hash: bool) -> dict[str, Any]:
    return {
        "ok": bool(ok),
        "checks": hash_checks,
        "hash_checks": hash_checks,
        "strict_hash": strict_hash,
    }


def _heartbeat_progress(heartbeats: list[str]) -> bool:
    return bool(_heartbeat_summary(heartbeats)["running"])


def _heartbeat_classification_fields(heartbeat: dict[str, Any]) -> dict[str, Any]:
    return {
        "heartbeat_running": bool(heartbeat["running"]),
        "heartbeat_site_progress": bool(heartbeat["site_progress"]),
        "heartbeat_last_count": heartbeat["last_count"],
        "heartbeat_last_bpc": heartbeat["last_bpc"],
        "heartbeat_last_progress": heartbeat["last_progress"],
        "heartbeat_last_same_site": heartbeat["last_same_site"],
        "heartbeat_recent_unique_sites": heartbeat["recent_unique_sites"],
        "heartbeat_recent_count_delta": heartbeat["recent_count_delta"],
    }


def _heartbeat_summary(heartbeats: list[str]) -> dict[str, Any]:
    if not heartbeats:
        return {
            "seen": False,
            "running": False,
            "site_progress": False,
            "last": "",
            "last_count": None,
            "last_bpc": "",
            "last_progress": "",
            "last_same_site": None,
            "recent_unique_sites": 0,
            "recent_count_delta": 0,
        }

    counts: list[int] = []
    sites: list[tuple[str, str, str]] = []
    entries: list[dict[str, str]] = []
    for line in heartbeats[-8:]:
        fields = _heartbeat_fields(line)
        entries.append(fields)
        count = fields.get("count", "")
        if count.isdecimal():
            counts.append(int(count))
        site = (
            fields.get("pc", "").lower(),
            fields.get("bpc", "").lower(),
            fields.get("tpc", "").lower(),
        )
        if any(site):
            sites.append(site)

    last = entries[-1] if entries else {}
    recent_count_delta = counts[-1] - counts[0] if len(counts) >= 2 else 0
    return {
        "seen": True,
        "running": len(counts) >= 2 and recent_count_delta > 0,
        "site_progress": len(set(sites)) > 1,
        "last": heartbeats[-1],
        "last_count": int(last["count"]) if last.get("count", "").isdecimal() else None,
        "last_bpc": last.get("bpc", "").lower(),
        "last_progress": last.get("progress", ""),
        "last_same_site": int(last["same_site"]) if last.get("same_site", "").isdecimal() else None,
        "recent_unique_sites": len(set(sites)),
        "recent_count_delta": recent_count_delta,
    }


def _heartbeat_stall_summary(text: str) -> dict[str, Any]:
    lines = re.findall(r"^LINX_HEARTBEAT_STALL .*$", text, flags=re.MULTILINE)
    if not lines:
        return {
            "seen": False,
            "count": 0,
            "last": "",
            "repeats": None,
            "threshold": None,
            "bpc": "",
            "status": "",
        }
    fields = _heartbeat_fields(lines[-1])
    return {
        "seen": True,
        "count": len(lines),
        "last": lines[-1][:512],
        "repeats": _decimal_or_none(fields.get("repeats")),
        "threshold": _decimal_or_none(fields.get("threshold")),
        "bpc": fields.get("bpc", "").lower(),
        "status": fields.get("status", ""),
    }


def _heartbeat_fields(line: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)=([^ \n]+)", line):
        fields[match.group(1)] = match.group(2)
    return fields


def _heartbeat_kernel_addresses(text: str, *, limit: int = 16) -> list[str]:
    heartbeats = re.findall(r"^LINX_HEARTBEAT .*$", text, flags=re.MULTILINE)
    addresses: list[str] = []
    seen: set[str] = set()
    for line in heartbeats[-limit:]:
        fields = _heartbeat_fields(line)
        for name in ("pc", "bpc", "envpc", "ra", "tpc"):
            value = fields.get(name, "").lower()
            if not value.startswith("0xffffffff"):
                continue
            if value in seen:
                continue
            seen.add(value)
            addresses.append(value)
    return addresses


def _find_llvm_addr2line() -> Path | None:
    env = os.environ.get("LINX_LLVM_ADDR2LINE", "").strip()
    if env:
        candidate = Path(os.path.expanduser(env)).resolve()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        return None

    bundled = (
        REPO_ROOT
        / "compiler"
        / "llvm"
        / "build-linxisa-clang"
        / "bin"
        / "llvm-addr2line"
    )
    if bundled.is_file() and os.access(bundled, os.X_OK):
        return bundled

    found = shutil.which("llvm-addr2line")
    return Path(found).resolve() if found else None


def _kernel_symbols_suggest_panic_loop(sites: list[dict[str, str]]) -> bool:
    if not sites:
        return False
    for site in sites:
        function = site.get("function", "").lower()
        source = site.get("source", "").lower()
        if "panic" in function or "panic.c" in source:
            return True
    return False


def _symbolize_heartbeat_kernel_sites(text: str, kernel: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "enabled": True,
        "ok": False,
        "tool": "",
        "kernel": str(kernel),
        "sites": [],
        "panic_loop": False,
        "evidence": "",
    }
    addresses = _heartbeat_kernel_addresses(text)
    if not addresses:
        return result

    tool = _find_llvm_addr2line()
    if tool is None:
        result["evidence"] = "heartbeat kernel symbolization unavailable: llvm-addr2line not found"
        return result

    proc = subprocess.run(
        [str(tool), "-e", str(kernel), "-f", "-C", *addresses],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    result["tool"] = str(tool)
    if proc.returncode != 0:
        result["evidence"] = proc.stdout.decode("utf-8", errors="replace").strip()[:512]
        return result

    lines = proc.stdout.decode("utf-8", errors="replace").splitlines()
    sites: list[dict[str, str]] = []
    for idx, address in enumerate(addresses):
        function = lines[2 * idx].strip() if 2 * idx < len(lines) else ""
        source = lines[2 * idx + 1].strip() if 2 * idx + 1 < len(lines) else ""
        sites.append({"address": address, "function": function, "source": source})

    result["ok"] = True
    result["sites"] = sites
    result["panic_loop"] = _kernel_symbols_suggest_panic_loop(sites)
    interesting = [
        f"{site['address']}={site['function']} {site['source']}".strip()
        for site in sites
        if site.get("function") and site.get("function") != "??"
    ]
    if not interesting:
        interesting = [site["address"] for site in sites]
    result["evidence"] = "heartbeat kernel symbols: " + "; ".join(interesting[:8])
    return result


def _decimal_or_none(value: str | None) -> int | None:
    if value and value.isdecimal():
        return int(value)
    return None


def _int_or_none(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value, 0)
    except ValueError:
        return None


def _heartbeat_tlb_fill_summary(line: str) -> dict[str, Any]:
    fields = _heartbeat_fields(line)
    return {
        "total": _decimal_or_none(fields.get("tlbf_total")),
        "fetch": _decimal_or_none(fields.get("tlbf_fetch")),
        "load": _decimal_or_none(fields.get("tlbf_load")),
        "store": _decimal_or_none(fields.get("tlbf_store")),
        "probe": _decimal_or_none(fields.get("tlbf_probe")),
        "ok": _decimal_or_none(fields.get("tlbf_ok")),
        "fault": _decimal_or_none(fields.get("tlbf_fault")),
        "user": _decimal_or_none(fields.get("tlbf_user")),
        "user_fetch": _decimal_or_none(fields.get("tlbf_user_fetch")),
        "user_load": _decimal_or_none(fields.get("tlbf_user_load")),
        "user_store": _decimal_or_none(fields.get("tlbf_user_store")),
        "kernel": _decimal_or_none(fields.get("tlbf_kernel")),
        "kernel_fetch": _decimal_or_none(fields.get("tlbf_kernel_fetch")),
        "kernel_load": _decimal_or_none(fields.get("tlbf_kernel_load")),
        "kernel_store": _decimal_or_none(fields.get("tlbf_kernel_store")),
        "other": _decimal_or_none(fields.get("tlbf_other")),
        "last_count": _decimal_or_none(fields.get("tlbf_last_count")),
        "last_pc": fields.get("tlbf_last_pc", "").lower(),
        "last_bpc": fields.get("tlbf_last_bpc", "").lower(),
        "last_va": fields.get("tlbf_last_va", "").lower(),
        "last_pa": fields.get("tlbf_last_pa", "").lower(),
        "last_access": _int_or_none(fields.get("tlbf_last_access")),
        "last_mmu": _int_or_none(fields.get("tlbf_last_mmu")),
        "last_prot": _int_or_none(fields.get("tlbf_last_prot")),
        "last_cause": _int_or_none(fields.get("tlbf_last_cause")),
        "last_acr": _int_or_none(fields.get("tlbf_last_acr")),
    }


def _heartbeat_mmu_cache_summary(line: str) -> dict[str, Any]:
    fields = _heartbeat_fields(line)
    return {
        "hit": _decimal_or_none(fields.get("mmuc_hit")),
        "miss": _decimal_or_none(fields.get("mmuc_miss")),
        "fill": _decimal_or_none(fields.get("mmuc_fill")),
        "flush": _decimal_or_none(fields.get("mmuc_flush")),
        "flush_page": _decimal_or_none(fields.get("mmuc_flush_page")),
    }


def _heartbeat_frame_stats_summary(line: str) -> dict[str, Any]:
    fields = _heartbeat_fields(line)
    return {
        "fentry": _decimal_or_none(fields.get("fr_fentry")),
        "save_probe": _decimal_or_none(fields.get("fr_save_probe")),
        "save_slot": _decimal_or_none(fields.get("fr_save_slot")),
        "save_host": _decimal_or_none(fields.get("fr_save_host")),
        "save_fallback": _decimal_or_none(fields.get("fr_save_fallback")),
        "fexit": _decimal_or_none(fields.get("fr_fexit")),
        "fret_stk": _decimal_or_none(fields.get("fr_fret_stk")),
        "fret_ra": _decimal_or_none(fields.get("fr_fret_ra")),
        "restore_slot": _decimal_or_none(fields.get("fr_restore_slot")),
        "restore_host": _decimal_or_none(fields.get("fr_restore_host")),
        "restore_fallback": _decimal_or_none(fields.get("fr_restore_fallback")),
        "restore_verify": _decimal_or_none(fields.get("fr_restore_verify")),
        "restore_mismatch": _decimal_or_none(fields.get("fr_restore_mismatch")),
        "ret_fast": _decimal_or_none(fields.get("fr_ret_fast")),
        "ret_check": _decimal_or_none(fields.get("fr_ret_check")),
    }


def _heartbeat_tlb_invalidation_summary(line: str) -> dict[str, Any]:
    fields = _heartbeat_fields(line)
    return {
        "iall": _decimal_or_none(fields.get("tlbi_iall")),
        "ia": _decimal_or_none(fields.get("tlbi_ia")),
        "iv": _decimal_or_none(fields.get("tlbi_iv")),
        "iav": _decimal_or_none(fields.get("tlbi_iav")),
        "last_count": _decimal_or_none(fields.get("tlbi_last_count")),
        "last_pc": fields.get("tlbi_last_pc", "").lower(),
        "last_bpc": fields.get("tlbi_last_bpc", "").lower(),
        "last_operand": fields.get("tlbi_last_operand", "").lower(),
        "last_acr": _int_or_none(fields.get("tlbi_last_acr")),
    }


def _heartbeat_tb_stats_summary(line: str) -> dict[str, Any]:
    fields = _heartbeat_fields(line)
    return {
        "exec": _decimal_or_none(fields.get("tbs_exec")),
        "lookup": _decimal_or_none(fields.get("tbs_lookup")),
        "jmp_hit": _decimal_or_none(fields.get("tbs_jmp_hit")),
        "hash_hit": _decimal_or_none(fields.get("tbs_hash_hit")),
        "miss": _decimal_or_none(fields.get("tbs_miss")),
        "gen": _decimal_or_none(fields.get("tbs_gen")),
        "flush": _decimal_or_none(fields.get("tbs_flush")),
        "phys_inv": _decimal_or_none(fields.get("tbs_phys_inv")),
        "code_used": _decimal_or_none(fields.get("tbs_code_used")),
        "code_size": _decimal_or_none(fields.get("tbs_code_size")),
    }


def _tlb_fill_hot_summary(text: str) -> dict[str, Any]:
    lines = re.findall(r"^LINX_TLB_FILL_HOT .*$", text, flags=re.MULTILINE)
    if not lines:
        return {
            "seen": False,
            "line_count": 0,
            "last": "",
        }

    fields = _heartbeat_fields(lines[-1])
    return {
        "seen": True,
        "line_count": len(lines),
        "last": lines[-1][:512],
        "heartbeat_count": _decimal_or_none(fields.get("count")),
        "evictions": _decimal_or_none(fields.get("evictions")),
        "slots": _decimal_or_none(fields.get("slots")),
        "top0_count": _decimal_or_none(fields.get("top0_count")),
        "top0_page": fields.get("top0_page", "").lower(),
        "top0_last_va": fields.get("top0_last_va", "").lower(),
        "top0_last_pa": fields.get("top0_last_pa", "").lower(),
        "top0_access": _int_or_none(fields.get("top0_access")),
        "top0_mmu": _int_or_none(fields.get("top0_mmu")),
        "top0_probe": _int_or_none(fields.get("top0_probe")),
        "top0_prot": _int_or_none(fields.get("top0_prot")),
        "top0_cause": _int_or_none(fields.get("top0_cause")),
        "top0_acr": _int_or_none(fields.get("top0_acr")),
        "top0_pc": fields.get("top0_pc", "").lower(),
        "top0_bpc": fields.get("top0_bpc", "").lower(),
        "top1_count": _decimal_or_none(fields.get("top1_count")),
        "top1_page": fields.get("top1_page", "").lower(),
        "top1_last_va": fields.get("top1_last_va", "").lower(),
        "top1_last_pa": fields.get("top1_last_pa", "").lower(),
        "top1_access": _int_or_none(fields.get("top1_access")),
        "top1_mmu": _int_or_none(fields.get("top1_mmu")),
        "top1_probe": _int_or_none(fields.get("top1_probe")),
        "top1_prot": _int_or_none(fields.get("top1_prot")),
        "top1_cause": _int_or_none(fields.get("top1_cause")),
        "top1_acr": _int_or_none(fields.get("top1_acr")),
        "top1_pc": fields.get("top1_pc", "").lower(),
        "top1_bpc": fields.get("top1_bpc", "").lower(),
    }


def _tlb_inv_hot_summary(text: str) -> dict[str, Any]:
    lines = re.findall(r"^LINX_TLB_INV_HOT .*$", text, flags=re.MULTILINE)
    if not lines:
        return {
            "seen": False,
            "line_count": 0,
            "last": "",
        }

    fields = _heartbeat_fields(lines[-1])
    max_delta_fields = fields
    max_delta_line = lines[-1]
    max_delta = _decimal_or_none(fields.get("top0_delta"))
    for line in lines:
        candidate_fields = _heartbeat_fields(line)
        candidate_delta = _decimal_or_none(candidate_fields.get("top0_delta"))
        if candidate_delta is not None and (max_delta is None or candidate_delta >= max_delta):
            max_delta = candidate_delta
            max_delta_fields = candidate_fields
            max_delta_line = line

    return {
        "seen": True,
        "line_count": len(lines),
        "last": lines[-1][:512],
        "heartbeat_count": _decimal_or_none(fields.get("count")),
        "evictions": _decimal_or_none(fields.get("evictions")),
        "slots": _decimal_or_none(fields.get("slots")),
        "top0_count": _decimal_or_none(fields.get("top0_count")),
        "top0_delta": _decimal_or_none(fields.get("top0_delta")),
        "top0_op": fields.get("top0_op", "").lower(),
        "top0_opid": _int_or_none(fields.get("top0_opid")),
        "top0_pc": fields.get("top0_pc", "").lower(),
        "top0_bpc": fields.get("top0_bpc", "").lower(),
        "top0_operand": fields.get("top0_operand", "").lower(),
        "top0_page": fields.get("top0_page", "").lower(),
        "top0_acr": _int_or_none(fields.get("top0_acr")),
        "top1_count": _decimal_or_none(fields.get("top1_count")),
        "top1_delta": _decimal_or_none(fields.get("top1_delta")),
        "top1_op": fields.get("top1_op", "").lower(),
        "top1_opid": _int_or_none(fields.get("top1_opid")),
        "top1_pc": fields.get("top1_pc", "").lower(),
        "top1_bpc": fields.get("top1_bpc", "").lower(),
        "top1_operand": fields.get("top1_operand", "").lower(),
        "top1_page": fields.get("top1_page", "").lower(),
        "top1_acr": _int_or_none(fields.get("top1_acr")),
        "max_delta": max_delta,
        "max_delta_line": max_delta_line[:512],
        "max_delta_heartbeat_count": _decimal_or_none(max_delta_fields.get("count")),
        "max_delta_top0_count": _decimal_or_none(max_delta_fields.get("top0_count")),
        "max_delta_top0_delta": _decimal_or_none(max_delta_fields.get("top0_delta")),
        "max_delta_top0_op": max_delta_fields.get("top0_op", "").lower(),
        "max_delta_top0_opid": _int_or_none(max_delta_fields.get("top0_opid")),
        "max_delta_top0_pc": max_delta_fields.get("top0_pc", "").lower(),
        "max_delta_top0_bpc": max_delta_fields.get("top0_bpc", "").lower(),
        "max_delta_top0_operand": max_delta_fields.get("top0_operand", "").lower(),
        "max_delta_top0_page": max_delta_fields.get("top0_page", "").lower(),
        "max_delta_top0_acr": _int_or_none(max_delta_fields.get("top0_acr")),
    }


def _bstart_cache_stats_summary(text: str) -> dict[str, Any]:
    lines = [
        line.strip()
        for line in re.findall(r"LINX_BSTART_CACHE_STATS [^\n]*(?:\n|$)", text)
    ]
    if not lines:
        return {
            "seen": False,
            "line_count": 0,
            "last": "",
        }

    fields = _heartbeat_fields(lines[-1])
    checks = _decimal_or_none(fields.get("checks")) or 0
    hits = _decimal_or_none(fields.get("hits")) or 0
    hit_pct = round((hits * 100.0 / checks), 3) if checks else None
    return {
        "seen": True,
        "line_count": len(lines),
        "last": lines[-1][:512],
        "count": _decimal_or_none(fields.get("count")),
        "pc": fields.get("pc", "").lower(),
        "bpc": fields.get("bpc", "").lower(),
        "tpc": fields.get("tpc", "").lower(),
        "checks": checks,
        "hits": hits,
        "hit_pct": hit_pct,
        "revalidations": _decimal_or_none(fields.get("revalidations")),
        "continuations": _decimal_or_none(fields.get("continuations")),
        "fallthroughs": _decimal_or_none(fields.get("fallthroughs")),
        "bstarts": _decimal_or_none(fields.get("bstarts")),
        "defers": _decimal_or_none(fields.get("defers")),
        "bad": _decimal_or_none(fields.get("bad")),
        "inserts": _decimal_or_none(fields.get("inserts")),
        "resets": _decimal_or_none(fields.get("resets")),
        "page_resets": _decimal_or_none(fields.get("page_resets")),
        "page_reset_entries": _decimal_or_none(fields.get("page_reset_entries")),
        "size": _decimal_or_none(fields.get("size")),
    }


def _pc_watch_summary(text: str) -> dict[str, Any]:
    lines = re.findall(
        (
            r"^(?:linx_pc_watch:|LINX_PC_WATCH_[A-Z_]+|"
            r"LINX_CALL_TRACE_RING(?:_ENTRY)?).*$"
        ),
        text,
        flags=re.MULTILINE,
    )
    ring_headers = [
        line for line in lines if line.startswith("LINX_PC_WATCH_RING ")
    ]
    ring_entries = [
        line for line in lines if line.startswith("LINX_PC_WATCH_RING_ENTRY ")
    ]
    call_trace_ring_headers = [
        line for line in lines if line.startswith("LINX_CALL_TRACE_RING ")
    ]
    call_trace_ring_entries = [
        line for line in lines if line.startswith("LINX_CALL_TRACE_RING_ENTRY ")
    ]
    ring_header_fields = _heartbeat_fields(ring_headers[-1]) if ring_headers else {}
    call_trace_ring_header_fields = (
        _heartbeat_fields(call_trace_ring_headers[-1])
        if call_trace_ring_headers
        else {}
    )
    ring_entry_samples = [
        _pc_watch_entry_summary(line) for line in ring_entries[-8:]
    ]
    call_trace_ring_entry_samples = [
        _pc_watch_entry_summary(line) for line in call_trace_ring_entries[-8:]
    ]
    return {
        "seen": bool(lines),
        "line_count": len(lines),
        "last": lines[-1][:512] if lines else "",
        "samples": [line[:512] for line in lines[-8:]],
        "ring_seen": bool(ring_headers),
        "ring_count": len(ring_headers),
        "ring_entry_count": len(ring_entries),
        "last_ring": ring_headers[-1][:512] if ring_headers else "",
        "last_ring_entry": ring_entries[-1][:512] if ring_entries else "",
        "last_ring_fields": _pc_watch_fields_summary(ring_header_fields),
        "last_ring_entry_fields": (
            ring_entry_samples[-1] if ring_entry_samples else {}
        ),
        "ring_entry_samples": ring_entry_samples,
        "call_trace_ring_seen": bool(call_trace_ring_headers),
        "call_trace_ring_count": len(call_trace_ring_headers),
        "call_trace_ring_entry_count": len(call_trace_ring_entries),
        "last_call_trace_ring": (
            call_trace_ring_headers[-1][:512] if call_trace_ring_headers else ""
        ),
        "last_call_trace_ring_entry": (
            call_trace_ring_entries[-1][:512] if call_trace_ring_entries else ""
        ),
        "last_call_trace_ring_fields": _pc_watch_fields_summary(
            call_trace_ring_header_fields
        ),
        "last_call_trace_ring_entry_fields": (
            call_trace_ring_entry_samples[-1]
            if call_trace_ring_entry_samples
            else {}
        ),
        "call_trace_ring_entry_samples": call_trace_ring_entry_samples,
    }


def _pc_watch_fields_summary(fields: dict[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in fields.items():
        if key in {
            "idx",
            "age",
            "watch",
            "hit",
            "printed",
            "count",
            "fault_count",
            "entries",
            "mem_kind",
            "mem_index",
            "mem_ok",
        }:
            result[key] = _int_or_none(value)
        elif value.lower().startswith("0x"):
            result[key] = value.lower()
        else:
            result[key] = value
    return result


def _pc_watch_entry_summary(line: str) -> dict[str, Any]:
    fields = _heartbeat_fields(line)
    summary = _pc_watch_fields_summary(fields)
    summary["line"] = line[:1024]
    return summary


def _fcmp_trace_summary(text: str) -> dict[str, Any]:
    lines = re.findall(r"^LINX_FCMP_TRACE .*$", text, flags=re.MULTILINE)
    samples: list[dict[str, Any]] = []
    for line in lines[-8:]:
        fields = _heartbeat_fields(line)
        samples.append(
            {
                "line": line[:512],
                "op": fields.get("op", ""),
                "count": _decimal_or_none(fields.get("count")),
                "pc": fields.get("pc", "").lower(),
                "bpc": fields.get("bpc", "").lower(),
                "tpc": fields.get("tpc", "").lower(),
                "type": fields.get("type", ""),
                "lhs": fields.get("lhs", "").lower(),
                "rhs": fields.get("rhs", "").lower(),
                "result": _decimal_or_none(fields.get("result")),
                "fcsr": fields.get("fcsr", "").lower(),
                "lhs_f64": fields.get("lhs_f64", ""),
                "rhs_f64": fields.get("rhs_f64", ""),
                "lhs_f32": fields.get("lhs_f32", ""),
                "rhs_f32": fields.get("rhs_f32", ""),
            }
        )
    return {
        "seen": bool(lines),
        "count": len(lines),
        "last": lines[-1][:512] if lines else "",
        "samples": samples,
    }


def _tlb_fill_trace_summary(text: str) -> dict[str, Any]:
    lines = re.findall(r"^LINX_TLB_FILL_TRACE .*$", text, flags=re.MULTILINE)
    samples: list[dict[str, Any]] = []
    for line in lines[-8:]:
        fields = _heartbeat_fields(line)
        samples.append(
            {
                "line": line[:512],
                "ok": _decimal_or_none(fields.get("ok")),
                "count": _decimal_or_none(fields.get("count")),
                "access": fields.get("access", ""),
                "va": fields.get("va", "").lower(),
                "prot": fields.get("prot", "").lower(),
                "cause": fields.get("cause", "").lower(),
                "pc": fields.get("pc", "").lower(),
                "bpc": fields.get("bpc", "").lower(),
                "tpc": fields.get("tpc", "").lower(),
                "legacy_ok": _decimal_or_none(fields.get("legacy_ok")),
                "legacy_why": fields.get("legacy_why", ""),
                "legacy_desc": fields.get("legacy_desc", "").lower(),
                "legacy_prot": fields.get("legacy_prot", "").lower(),
                "legacy_cause": fields.get("legacy_cause", "").lower(),
            }
        )
    return {
        "seen": bool(lines),
        "count": len(lines),
        "last": lines[-1][:512] if lines else "",
        "samples": samples,
    }


def _mprotect_trace_summary(text: str) -> dict[str, Any]:
    lines = re.findall(r"^LINX_MPROTECT .*$", text, flags=re.MULTILINE)
    samples: list[dict[str, Any]] = []
    for line in lines[-8:]:
        fields = _heartbeat_fields(line)
        samples.append(
            {
                "line": line[:512],
                "stage": fields.get("stage", ""),
                "count": _int_or_none(fields.get("count")),
                "pid": _int_or_none(fields.get("pid")),
                "comm": fields.get("comm", ""),
                "start": fields.get("start", "").lower(),
                "end": fields.get("end", "").lower(),
                "prot": fields.get("prot", "").lower(),
                "newflags": fields.get("newflags", "").lower(),
                "error": _int_or_none(fields.get("error")),
                "trace_addr": fields.get("trace_addr", "").lower(),
                "prev_start": fields.get("prev_start", "").lower(),
                "prev_end": fields.get("prev_end", "").lower(),
                "cur_start": fields.get("cur_start", "").lower(),
                "cur_end": fields.get("cur_end", "").lower(),
                "next_start": fields.get("next_start", "").lower(),
                "next_end": fields.get("next_end", "").lower(),
                "target_start": fields.get("target_start", "").lower(),
                "target_end": fields.get("target_end", "").lower(),
                "target_flags": fields.get("target_flags", "").lower(),
            }
        )
    return {
        "seen": bool(lines),
        "count": len(lines),
        "last": lines[-1][:512] if lines else "",
        "samples": samples,
    }


def _collect_outputs_from_log(qemu_log: Path, run_dir: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    data = qemu_log.read_bytes()
    wanted = sorted({cmp_cfg["out"] for cmp_cfg in cfg.get("compares", [])})
    collected: list[str] = []
    missing: list[str] = []

    for name in wanted:
        begin = f"LINX_SPEC_FILE_BEGIN {name}".encode("utf-8")
        end = f"LINX_SPEC_FILE_END {name}".encode("utf-8")
        i = data.find(begin)
        if i < 0:
            missing.append(name)
            continue
        payload_start = data.find(b"\n", i + len(begin))
        if payload_start < 0:
            missing.append(name)
            continue
        payload_start += 1

        j = data.find(end, payload_start)
        if j < 0:
            missing.append(name)
            continue

        payload_end = j
        if payload_end >= 2 and data[payload_end - 2 : payload_end] == b"\r\n":
            payload_end -= 2
        elif payload_end >= 1 and data[payload_end - 1 : payload_end] == b"\n":
            payload_end -= 1

        payload = data[payload_start:payload_end].replace(b"\r\n", b"\n")
        out_path = run_dir / name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(payload)
        collected.append(str(out_path))

    return {"ok": not missing, "missing": missing, "collected": collected}


def _fnv1a32(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    h = 0x811C9DC5
    for b in data:
        h ^= b
        h = (
            h
            + ((h << 1) & 0xFFFFFFFF)
            + ((h << 4) & 0xFFFFFFFF)
            + ((h << 7) & 0xFFFFFFFF)
            + ((h << 8) & 0xFFFFFFFF)
            + ((h << 24) & 0xFFFFFFFF)
        ) & 0xFFFFFFFF
    return len(data), h


def _strip_async_qemu_diagnostics(text: str) -> str:
    for marker in (
        "LINX_HEARTBEAT_STALL",
        "LINX_HEARTBEAT",
        "LINX_BSTART_CACHE_STATS",
        "LINX_TLB_FILL_HOT",
        "LINX_TLB_INV_HOT",
        "LINX_TLB_FILL_TRACE",
        "LINX_FCMP_TRACE",
        "LINX_MPROTECT",
    ):
        text = re.sub(rf"{marker}[^\n]*(?:\n|$)", "", text)
    return text


def _hash_marker_candidates(text: str) -> dict[str, list[tuple[int, int]]]:
    text = _strip_async_qemu_diagnostics(text)
    pat = re.compile(r"LINX_SPEC_HASH\s+(\S+)\s+(\d+)")
    markers = list(pat.finditer(text))
    seen: dict[str, list[tuple[int, int]]] = {}

    for idx, marker in enumerate(markers):
        name = marker.group(1)
        size = int(marker.group(2), 10)
        end = markers[idx + 1].start() if idx + 1 < len(markers) else len(text)
        for sentinel in ("LINX_SPEC_PASS", "LINX_SPEC_FAIL", "LINX_REBOOT"):
            pos = text.find(sentinel, marker.end())
            if pos >= 0:
                end = min(end, pos)

        segment = text[marker.end():min(end, marker.end() + 8192)]
        for hv in re.findall(r"0x([0-9a-fA-F]+)", segment):
            seen.setdefault(name, []).append((size, int(hv, 16) & 0xFFFFFFFF))

    return seen


def _verify_hash_markers(spec_dir: Path, qemu_log: Path, bench: str, cfg: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    text = qemu_log.read_text(encoding="utf-8", errors="replace")
    seen = _hash_marker_candidates(text)

    checks: list[dict[str, Any]] = []
    all_ok = True
    for idx, cmp_cfg in enumerate(cfg.get("compares", []), start=1):
        out_name = cmp_cfg["out"]
        ref_path = spec_dir / cmp_cfg["ref"]
        ref_size, ref_hash = _fnv1a32(ref_path)
        candidates = seen.get(out_name, [])
        got = next(
            ((size, hv) for size, hv in candidates if size == ref_size and hv == ref_hash),
            None,
        )
        if got is None:
            got = next(
                ((size, hv) for size, hv in reversed(candidates) if size == ref_size),
                candidates[-1] if candidates else None,
            )
        ok = bool(got and got[0] == ref_size and got[1] == ref_hash)
        all_ok = all_ok and ok

        log_path = out_dir / f"{bench.replace('.', '_')}_hashcheck_{idx}.log"
        log_lines = [
            f"output={out_name}",
            f"reference={ref_path}",
            f"expected_size={ref_size}",
                f"expected_hash=0x{ref_hash:08x}",
        ]
        if got is None:
            log_lines.append("actual=missing")
        else:
            log_lines.append(f"actual_size={got[0]}")
            log_lines.append(f"actual_hash=0x{got[1]:08x}")
        log_lines.append(f"ok={str(ok).lower()}")
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

        checks.append(
            {
                "ok": ok,
                "method": "fnv1a32",
                "reference": str(ref_path),
                "output_name": out_name,
                "expected_size": ref_size,
                "expected_hash": f"0x{ref_hash:08x}",
                "actual_size": got[0] if got else None,
                "actual_hash": f"0x{got[1]:08x}" if got else None,
                "log": str(log_path),
            }
        )

    return {"ok": all_ok, "checks": checks}


def _run_specdiff(spec_dir: Path, run_dir: Path, bench: str, cfg: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    specperl = spec_dir / "bin" / "specperl"
    specdiff = spec_dir / "bin" / "harness" / "specdiff"
    if not specdiff.exists():
        raise SystemExit(f"error: missing specdiff under {spec_dir / 'bin'}")

    perl_cmd: list[str]
    if specperl.exists():
        try:
            probe = subprocess.run(
                [str(specperl), "-e", "print 1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            perl_cmd = [str(specperl)] if probe.returncode == 0 else []
        except OSError:
            perl_cmd = []
    else:
        perl_cmd = []

    if not perl_cmd:
        host_perl = shutil.which("perl")
        if not host_perl:
            raise SystemExit("error: could not find a runnable perl interpreter for specdiff")
        perl_cmd = [host_perl]

    checks: list[dict[str, Any]] = []
    all_ok = True
    for idx, cmp_cfg in enumerate(cfg.get("compares", []), start=1):
        ref = spec_dir / cmp_cfg["ref"]
        out = run_dir / cmp_cfg["out"]
        cmp_log = out_dir / f"{bench.replace('.', '_')}_specdiff_{idx}.log"

        cmd = [*perl_cmd, str(specdiff), *cmp_cfg["args"], str(ref), str(out)]
        proc = _run(
            cmd,
            cwd=spec_dir,
            env={**os.environ, "SPEC": str(spec_dir)},
        )
        cmp_log.write_bytes(proc.stdout)
        ok = proc.returncode == 0
        all_ok = all_ok and ok
        checks.append(
            {
                "ok": ok,
                "returncode": proc.returncode,
                "reference": str(ref),
                "output": str(out),
                "log": str(cmp_log),
            }
        )

    return {"ok": all_ok, "checks": checks}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run SPEC CPU2017 INT workloads under Linx Linux on qemu-system-linx64.")
    parser.add_argument(
        "--spec-dir",
        default=str(REPO_ROOT / "workloads" / "spec2017" / "cpu2017v118_x64_gcc12_avx2"),
    )
    parser.add_argument("--qemu", default=_default_qemu())
    parser.add_argument("--kernel", default=str(REPO_ROOT / "kernel" / "linux" / "build-linx-fixed" / "vmlinux"))
    parser.add_argument("--linux-root", default=str(REPO_ROOT / "kernel" / "linux"))
    parser.add_argument("--clang", default=str(REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang"))
    parser.add_argument("--sysroot", default=_default_musl_sysroot())
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--memory-mb", type=int, default=2048)
    parser.add_argument(
        "--stack-limit",
        default="",
        help=(
            "Set the SPEC init wrapper stack limit. Accepts bytes, K/M/G/T suffixes, "
            "'unlimited', or 'default' (default: LINX_SPEC_STACK_LIMIT_BYTES/"
            "LINX_SPEC_STACK_LIMIT env or built-in 256M)."
        ),
    )
    parser.add_argument(
        "--heartbeat-sec",
        type=float,
        default=float(os.environ.get("LINX_SPEC_HEARTBEAT_SEC", "30")),
        help="Emit host heartbeat while QEMU is running (0 to disable).",
    )
    parser.add_argument(
        "--qemu-heartbeat-interval",
        type=int,
        default=int(os.environ.get("LINX_SPEC_QEMU_HEARTBEAT_INTERVAL", "0")),
        help="Set LINX_HEARTBEAT_INTERVAL for QEMU BPC progress logging (0 disables).",
    )
    parser.add_argument(
        "--qemu-heartbeat-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_HEARTBEAT_REGS", False),
        help="Set LINX_QEMU_HEARTBEAT_REGS=1 for full GPR dumps at heartbeat sites.",
    )
    parser.add_argument(
        "--qemu-heartbeat-code-bytes",
        type=int,
        default=int(os.environ.get("LINX_SPEC_QEMU_HEARTBEAT_CODE_BYTES", "0")),
        help="Set LINX_QEMU_HEARTBEAT_CODE_BYTES for PC/BPC code-byte dumps (0 disables).",
    )
    parser.add_argument(
        "--qemu-heartbeat-same-site-warn",
        type=int,
        default=int(os.environ.get("LINX_SPEC_QEMU_HEARTBEAT_SAME_SITE_WARN", "0")),
        help="Set LINX_QEMU_HEARTBEAT_SAME_SITE_WARN to emit LINX_HEARTBEAT_STALL markers.",
    )
    parser.add_argument(
        "--qemu-frame-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_STATS", False),
        help="Set LINX_QEMU_FRAME_STATS=1 to append frame-template counters to QEMU heartbeats.",
    )
    parser.add_argument(
        "--qemu-frame-restore-host-load",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_RESTORE_HOST_LOAD", False),
        help=(
            "Set LINX_QEMU_FRAME_RESTORE_HOST_LOAD=1 to use cached host loads "
            "for frame restore slots when QEMU already has a RAM TLB entry."
        ),
    )
    parser.add_argument(
        "--qemu-frame-restore-host-verify",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRAME_RESTORE_HOST_VERIFY", False),
        help=(
            "Set LINX_QEMU_FRAME_RESTORE_HOST_VERIFY=1 to compare cached "
            "frame restore host loads against the normal soft-MMU load."
        ),
    )
    parser.add_argument(
        "--qemu-frame-restore-host-verify-limit",
        type=int,
        default=int(os.environ.get("LINX_SPEC_QEMU_FRAME_RESTORE_HOST_VERIFY_LIMIT", "0")),
        help="Set LINX_QEMU_FRAME_RESTORE_HOST_VERIFY_LIMIT for mismatch trace lines (0 uses QEMU default).",
    )
    parser.add_argument(
        "--qemu-fret-stk-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRET_STK_TRACE", False),
        help="Set LINX_QEMU_FRET_STK_TRACE=1 for FRET.STK frame-restore tracing.",
    )
    parser.add_argument(
        "--qemu-fret-stk-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FRET_STK_TRACE_REGS", False),
        help="Set LINX_QEMU_FRET_STK_TRACE_REGS=1 for GPR dumps on FRET.STK trace hits.",
    )
    parser.add_argument("--qemu-fret-stk-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_PC", ""))
    parser.add_argument("--qemu-fret-stk-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_PC_LO", ""))
    parser.add_argument("--qemu-fret-stk-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_PC_HI", ""))
    parser.add_argument("--qemu-fret-stk-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_COUNT_LO", ""))
    parser.add_argument("--qemu-fret-stk-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_COUNT_HI", ""))
    parser.add_argument("--qemu-fret-stk-trace-ra", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_RA", ""))
    parser.add_argument("--qemu-fret-stk-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_LIMIT", ""))
    parser.add_argument("--qemu-fret-stk-trace-dump-words", default=os.environ.get("LINX_SPEC_QEMU_FRET_STK_TRACE_DUMP_WORDS", ""))
    parser.add_argument(
        "--qemu-fentry-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FENTRY_TRACE", False),
        help="Set LINX_QEMU_FENTRY_TRACE=1 for FENTRY frame-save tracing.",
    )
    parser.add_argument(
        "--qemu-fentry-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FENTRY_TRACE_REGS", False),
        help="Set LINX_QEMU_FENTRY_TRACE_REGS=1 for GPR dumps on FENTRY trace hits.",
    )
    parser.add_argument("--qemu-fentry-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_PC", ""))
    parser.add_argument("--qemu-fentry-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_PC_LO", ""))
    parser.add_argument("--qemu-fentry-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_PC_HI", ""))
    parser.add_argument("--qemu-fentry-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_COUNT_LO", ""))
    parser.add_argument("--qemu-fentry-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_COUNT_HI", ""))
    parser.add_argument("--qemu-fentry-trace-ra", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_RA", ""))
    parser.add_argument("--qemu-fentry-trace-sp", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_SP", ""))
    parser.add_argument("--qemu-fentry-trace-new-sp", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_NEW_SP", ""))
    parser.add_argument("--qemu-fentry-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_LIMIT", ""))
    parser.add_argument("--qemu-fentry-trace-dump-words", default=os.environ.get("LINX_SPEC_QEMU_FENTRY_TRACE_DUMP_WORDS", ""))
    parser.add_argument(
        "--qemu-tlb-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_STATS", False),
        help="Set LINX_QEMU_TLB_STATS=1 to append TLB invalidation counters to QEMU heartbeats.",
    )
    parser.add_argument(
        "--qemu-tlb-inv-hot",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_INV_HOT", False),
        help="Set LINX_QEMU_TLB_INV_HOT=1 to emit TLBI source-PC hot-site heartbeat lines.",
    )
    parser.add_argument(
        "--qemu-tlb-fill-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_FILL_STATS", False),
        help="Set LINX_QEMU_TLB_FILL_STATS=1 to append demand page-walk counters to QEMU heartbeats.",
    )
    parser.add_argument(
        "--qemu-tlb-fill-hot",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TLB_FILL_HOT", False),
        help="Set LINX_QEMU_TLB_FILL_HOT=1 to emit hot demand page-walk heartbeat sketches.",
    )
    parser.add_argument(
        "--qemu-tb-stats",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_TB_STATS", False),
        help="Set LINX_QEMU_TB_STATS=1 to append TCG TB counters to QEMU heartbeats.",
    )
    parser.add_argument(
        "--qemu-fault-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FAULT_TRACE", False),
        help="Enable QEMU fault tracing without forcing a full GPR dump.",
    )
    parser.add_argument(
        "--qemu-fault-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_FAULT_TRACE_REGS", False),
        help="Enable QEMU fault tracing and full GPR dump on traps.",
    )
    parser.add_argument(
        "--qemu-fault-trace-limit",
        type=int,
        default=int(os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_LIMIT", "1")),
        help="Set LINX_QEMU_FAULT_TRACE_LIMIT when fault trace registers are enabled (0 disables limit).",
    )
    parser.add_argument("--qemu-fault-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_PC", ""))
    parser.add_argument("--qemu-fault-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_PC_LO", ""))
    parser.add_argument("--qemu-fault-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_PC_HI", ""))
    parser.add_argument("--qemu-fault-trace-addr", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_ADDR", ""))
    parser.add_argument("--qemu-fault-trace-addr-lo", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_ADDR_LO", ""))
    parser.add_argument("--qemu-fault-trace-addr-hi", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_ADDR_HI", ""))
    parser.add_argument("--qemu-fault-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_COUNT_LO", ""))
    parser.add_argument("--qemu-fault-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_COUNT_HI", ""))
    parser.add_argument("--qemu-fault-trace-trapnum", default=os.environ.get("LINX_SPEC_QEMU_FAULT_TRACE_TRAPNUM", ""))
    parser.add_argument(
        "--qemu-syscall-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_SYSCALL_TRACE", False),
        help="Set LINX_SYSCALL_TRACE=1 for QEMU syscall entry/return tracing.",
    )
    parser.add_argument(
        "--qemu-syscall-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_SYSCALL_TRACE_REGS", False),
        help="Set LINX_SYSCALL_TRACE_REGS=1 for syscall trace GPR dumps.",
    )
    parser.add_argument(
        "--qemu-syscall-trace-strings",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_SYSCALL_TRACE_STRINGS", False),
        help="Set LINX_SYSCALL_TRACE_STRINGS=1 to decode known pathname/string syscall arguments.",
    )
    parser.add_argument("--qemu-syscall-trace-nr", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_NR", ""))
    parser.add_argument("--qemu-syscall-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_LIMIT", ""))
    parser.add_argument("--qemu-syscall-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_PC_LO", ""))
    parser.add_argument("--qemu-syscall-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_PC_HI", ""))
    parser.add_argument("--qemu-syscall-trace-string-max", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_STRING_MAX", ""))
    parser.add_argument("--qemu-syscall-trace-dump-args", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_DUMP_ARGS", ""))
    parser.add_argument("--qemu-syscall-trace-dump-arg", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_DUMP_ARG", ""))
    parser.add_argument("--qemu-syscall-trace-dump-bytes", default=os.environ.get("LINX_SPEC_QEMU_SYSCALL_TRACE_DUMP_BYTES", ""))
    parser.add_argument(
        "--qemu-mem-trace",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE", False),
        help="Set LINX_MEM_TRACE=1 for QEMU memory access tracing.",
    )
    parser.add_argument(
        "--qemu-mem-trace-context",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE_CONTEXT", False),
        help="Set LINX_MEM_TRACE_CONTEXT=1 to add MMU context fields to memory trace lines.",
    )
    parser.add_argument(
        "--qemu-mem-trace-pre",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE_PRE", False),
        help="Set LINX_MEM_TRACE_PRE=1 to log load effective addresses before QEMU performs the load.",
    )
    parser.add_argument(
        "--qemu-mem-trace-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_MEM_TRACE_REGS", False),
        help="Set LINX_MEM_TRACE_REGS=1 to include T/U queue heads on memory trace lines.",
    )
    parser.add_argument("--qemu-mem-trace-addr", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_ADDR", ""))
    parser.add_argument("--qemu-mem-trace-size", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_SIZE", ""))
    parser.add_argument("--qemu-mem-trace-limit", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_LIMIT", ""))
    parser.add_argument("--qemu-mem-trace-access", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_ACCESS", ""))
    parser.add_argument("--qemu-mem-trace-acr", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_ACR", ""))
    parser.add_argument("--qemu-mem-trace-pc", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_PC", ""))
    parser.add_argument("--qemu-mem-trace-pc-lo", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_PC_LO", ""))
    parser.add_argument("--qemu-mem-trace-pc-hi", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_PC_HI", ""))
    parser.add_argument("--qemu-mem-trace-count-lo", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_COUNT_LO", ""))
    parser.add_argument("--qemu-mem-trace-count-hi", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_COUNT_HI", ""))
    parser.add_argument("--qemu-mem-trace-fast", default=os.environ.get("LINX_SPEC_QEMU_MEM_TRACE_FAST", ""))
    parser.add_argument("--qemu-pc-watch", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH", ""))
    parser.add_argument("--qemu-pc-watch-count-lo", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_COUNT_LO", ""))
    parser.add_argument("--qemu-pc-watch-count-hi", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_COUNT_HI", ""))
    parser.add_argument("--qemu-pc-watch-hit-limit", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_HIT_LIMIT", ""))
    parser.add_argument("--qemu-pc-watch-hit-lo", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_HIT_LO", ""))
    parser.add_argument("--qemu-pc-watch-hit-hi", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_HIT_HI", ""))
    parser.add_argument("--qemu-pc-watch-match-gpr", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_MATCH_GPR", ""))
    parser.add_argument("--qemu-pc-watch-match-value", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_MATCH_VALUE", ""))
    parser.add_argument("--qemu-pc-watch-match-mask", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_MATCH_MASK", ""))
    parser.add_argument("--qemu-pc-watch-dump-reg", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_REG", ""))
    parser.add_argument("--qemu-pc-watch-dump-regs", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_REGS", ""))
    parser.add_argument("--qemu-pc-watch-dump-offsets", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_OFFSETS", ""))
    parser.add_argument("--qemu-pc-watch-dump-ptr-offsets", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_PTR_OFFSETS", ""))
    parser.add_argument("--qemu-pc-watch-dump-words", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_WORDS", ""))
    parser.add_argument("--qemu-pc-watch-dump-width", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_WIDTH", ""))
    parser.add_argument("--qemu-pc-watch-dump-code-bytes", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_DUMP_CODE_BYTES", ""))
    parser.add_argument("--qemu-pc-watch-ring-size", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_RING_SIZE", ""))
    parser.add_argument("--qemu-pc-watch-ring-mem-reg", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_RING_MEM_REG", ""))
    parser.add_argument("--qemu-pc-watch-ring-mem-offset", default=os.environ.get("LINX_SPEC_QEMU_PC_WATCH_RING_MEM_OFFSET", ""))
    parser.add_argument(
        "--qemu-call-trace-ring-size",
        default=os.environ.get("LINX_SPEC_QEMU_CALL_TRACE_RING_SIZE", ""),
        help="Set LINX_CALL_TRACE_RING_SIZE for call-ring dumps.",
    )
    parser.add_argument(
        "--qemu-pc-watch-regs",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_REGS", False),
        help="Set LINX_DEBUG_PC_WATCH_REGS=1 for matching PC-watch hits.",
    )
    parser.add_argument(
        "--qemu-pc-watch-ring",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_RING", False),
        help="Set LINX_DEBUG_PC_WATCH_RING=1 to retain recent PC-watch hits for fault dumps.",
    )
    parser.add_argument(
        "--qemu-pc-watch-dump-call-ring",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_DUMP_CALL_RING", False),
        help=(
            "Set LINX_DEBUG_PC_WATCH_DUMP_CALL_RING=1 on matching PC-watch "
            "hits and enable LINX_CALL_TRACE_RING=1 so a caller ring exists."
        ),
    )
    parser.add_argument(
        "--qemu-call-trace-ring",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_CALL_TRACE_RING", False),
        help="Set LINX_CALL_TRACE_RING=1 without requiring a PC-watch call-ring dump.",
    )
    parser.add_argument(
        "--qemu-pc-watch-dump-phys",
        action="store_true",
        default=_env_bool("LINX_SPEC_QEMU_PC_WATCH_DUMP_PHYS", False),
        help="Set LINX_DEBUG_PC_WATCH_DUMP_PHYS=1 on matching PC-watch hits.",
    )
    parser.add_argument(
        "--guest-heartbeat-sec",
        type=int,
        default=int(os.environ.get("LINX_SPEC_GUEST_HEARTBEAT_SEC", "0")),
        help="Emit guest-side child/output heartbeats from the init wrapper while waiting (0 to disable).",
    )
    parser.add_argument(
        "--guest-proc-diagnostics",
        action="store_true",
        default=_env_bool("LINX_SPEC_GUEST_PROC_DIAGNOSTICS", False),
        help=(
            "During guest heartbeat waits, also dump /proc status, meminfo, "
            "vmstat, and pressure files. Off by default because these probes "
            "can perturb SPEC startup fault paths."
        ),
    )
    parser.add_argument(
        "--symbolize-heartbeat",
        action="store_true",
        default=_env_bool("LINX_SPEC_SYMBOLIZE_HEARTBEAT", False),
        help="Symbolize recent kernel-space QEMU heartbeat PC/BPC sites with llvm-addr2line.",
    )
    parser.add_argument(
        "--no-progress-timeout",
        type=float,
        default=float(os.environ.get("LINX_SPEC_NO_PROGRESS_TIMEOUT", "0")),
        help="Fail if QEMU emits no output for this many seconds (0 to disable).",
    )
    parser.add_argument(
        "--fail-9p-timeout",
        action="store_true",
        default=_env_bool("LINX_SPEC_FAIL_9P_TIMEOUT", False),
        help=(
            "In 9p mode, treat a per-run QEMU timeout as a gate failure. "
            "The default keeps running so full host-visible output validation can continue."
        ),
    )
    parser.add_argument(
        "--append-extra",
        default=str(os.environ.get("LINX_SPEC_APPEND_EXTRA", "")),
        help="Extra kernel cmdline appended to the built-in defaults (for example: 'norandmaps').",
    )
    parser.add_argument(
        "--dump-prefix-bytes",
        type=int,
        default=int(os.environ.get("LINX_SPEC_DUMP_PREFIX_BYTES", "0")),
        help="If >0, emit first N bytes for each verified output in initramfs mode.",
    )
    parser.add_argument(
        "--strict-hash",
        dest="strict_hash",
        action="store_true",
        help="Require initramfs hash verification to pass (default: on for initramfs).",
    )
    parser.add_argument(
        "--no-strict-hash",
        dest="strict_hash",
        action="store_false",
        help="Do not fail initramfs runs on hash mismatches/missing hash markers.",
    )
    parser.set_defaults(strict_hash=None)
    parser.add_argument("--stage", choices=["a", "b"], default="a")
    parser.add_argument("--transport", choices=["9p", "initramfs"], default="9p")
    parser.add_argument("--input-set", choices=["refrate", "test", "train"], default="refrate")
    parser.add_argument(
        "--bench",
        action="append",
        choices=sorted(ALL_BENCHES),
        help="Optional benchmark override. Repeat to run multiple.",
    )
    parser.add_argument(
        "--run-index",
        action="append",
        type=int,
        default=[],
        help=(
            "Optional 1-based SPEC command row selector for focused debug runs. "
            "Repeat to run multiple rows; default runs every row."
        ),
    )
    parser.add_argument(
        "--out-dir",
        default="",
        help="Directory for logs/json (default: <spec-dir>/tmp/linx-qemu-results).",
    )
    args = parser.parse_args(argv)
    if args.stack_limit.strip():
        os.environ["LINX_SPEC_STACK_LIMIT_BYTES"] = args.stack_limit.strip()
    if args.timeout <= 0:
        raise SystemExit("error: --timeout must be > 0")
    if args.heartbeat_sec < 0:
        raise SystemExit("error: --heartbeat-sec must be >= 0")
    if args.qemu_heartbeat_interval < 0:
        raise SystemExit("error: --qemu-heartbeat-interval must be >= 0")
    if args.qemu_heartbeat_code_bytes < 0:
        raise SystemExit("error: --qemu-heartbeat-code-bytes must be >= 0")
    if args.qemu_heartbeat_same_site_warn < 0:
        raise SystemExit("error: --qemu-heartbeat-same-site-warn must be >= 0")
    if args.qemu_fault_trace_limit < 0:
        raise SystemExit("error: --qemu-fault-trace-limit must be >= 0")
    if args.qemu_frame_restore_host_verify_limit < 0:
        raise SystemExit("error: --qemu-frame-restore-host-verify-limit must be >= 0")
    for attr in (
        "qemu_syscall_trace_limit",
        "qemu_syscall_trace_pc_lo",
        "qemu_syscall_trace_pc_hi",
        "qemu_syscall_trace_string_max",
        "qemu_syscall_trace_dump_arg",
        "qemu_syscall_trace_dump_bytes",
        "qemu_mem_trace_addr",
        "qemu_mem_trace_size",
        "qemu_mem_trace_limit",
        "qemu_mem_trace_pc",
        "qemu_mem_trace_pc_lo",
        "qemu_mem_trace_pc_hi",
        "qemu_mem_trace_count_lo",
        "qemu_mem_trace_count_hi",
        "qemu_fret_stk_trace_pc",
        "qemu_fret_stk_trace_pc_lo",
        "qemu_fret_stk_trace_pc_hi",
        "qemu_fret_stk_trace_count_lo",
        "qemu_fret_stk_trace_count_hi",
        "qemu_fret_stk_trace_ra",
        "qemu_fret_stk_trace_limit",
        "qemu_fret_stk_trace_dump_words",
        "qemu_fentry_trace_pc",
        "qemu_fentry_trace_pc_lo",
        "qemu_fentry_trace_pc_hi",
        "qemu_fentry_trace_count_lo",
        "qemu_fentry_trace_count_hi",
        "qemu_fentry_trace_ra",
        "qemu_fentry_trace_sp",
        "qemu_fentry_trace_new_sp",
        "qemu_fentry_trace_limit",
        "qemu_fentry_trace_dump_words",
    ):
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            try:
                parsed = int(value, 0)
            except ValueError as exc:
                raise SystemExit(
                    f"error: --{attr.replace('_', '-')} must be an integer"
                ) from exc
            if parsed < 0:
                raise SystemExit(f"error: --{attr.replace('_', '-')} must be >= 0")
            if attr == "qemu_syscall_trace_dump_arg" and parsed > 5:
                raise SystemExit("error: --qemu-syscall-trace-dump-arg must be <= 5")
    qemu_mem_trace_access = str(getattr(args, "qemu_mem_trace_access", "") or "").strip()
    if qemu_mem_trace_access and qemu_mem_trace_access not in {
        "load",
        "loads",
        "store",
        "stores",
        "all",
        "both",
    }:
        raise SystemExit("error: --qemu-mem-trace-access must be load, store, or all")
    qemu_mem_trace_acr = str(getattr(args, "qemu_mem_trace_acr", "") or "").strip()
    if qemu_mem_trace_acr and qemu_mem_trace_acr not in {"any", "all"}:
        try:
            parsed_acr = int(qemu_mem_trace_acr, 0)
        except ValueError as exc:
            raise SystemExit("error: --qemu-mem-trace-acr must be an integer, any, or all") from exc
        if parsed_acr < 0 or parsed_acr > 15:
            raise SystemExit("error: --qemu-mem-trace-acr must be between 0 and 15")
    for attr in (
        "qemu_pc_watch_hit_limit",
        "qemu_pc_watch_hit_lo",
        "qemu_pc_watch_hit_hi",
        "qemu_pc_watch_dump_words",
        "qemu_pc_watch_dump_width",
        "qemu_pc_watch_dump_code_bytes",
        "qemu_pc_watch_ring_size",
    ):
        value = str(getattr(args, attr, "") or "").strip()
        if value:
            try:
                parsed = int(value, 0)
            except ValueError as exc:
                raise SystemExit(
                    f"error: --{attr.replace('_', '-')} must be an integer"
                ) from exc
            if parsed < 0:
                raise SystemExit(f"error: --{attr.replace('_', '-')} must be >= 0")
    if args.guest_heartbeat_sec < 0:
        raise SystemExit("error: --guest-heartbeat-sec must be >= 0")
    if args.no_progress_timeout < 0:
        raise SystemExit("error: --no-progress-timeout must be >= 0")
    if args.dump_prefix_bytes < 0:
        raise SystemExit("error: --dump-prefix-bytes must be >= 0")
    qemu_fault_trace_filters = _qemu_fault_trace_filters_from_args(args)
    qemu_pc_watch = _qemu_pc_watch_from_args(args)
    qemu_syscall_trace = _qemu_syscall_trace_from_args(args)
    qemu_mem_trace = _qemu_mem_trace_from_args(args)
    qemu_fret_stk_trace = _qemu_fret_stk_trace_from_args(args)
    qemu_fentry_trace = _qemu_fentry_trace_from_args(args)

    spec_dir = Path(os.path.expanduser(args.spec_dir)).resolve()
    qemu = _check_exe(Path(os.path.expanduser(args.qemu)).resolve(), "qemu-system-linx64")
    kernel = _check_exe(Path(os.path.expanduser(args.kernel)).resolve(), "kernel image")
    linux_root = Path(os.path.expanduser(args.linux_root)).resolve()
    clang = _check_exe(Path(os.path.expanduser(args.clang)).resolve(), "clang")
    sysroot = Path(os.path.expanduser(args.sysroot)).resolve()

    if not (spec_dir / "benchspec" / "CPU").exists():
        raise SystemExit(f"error: invalid SPEC dir: {spec_dir}")

    out_dir = Path(os.path.expanduser(args.out_dir)).resolve() if args.out_dir else spec_dir / "tmp" / "linx-qemu-results"
    out_dir.mkdir(parents=True, exist_ok=True)

    strict_hash = bool(args.strict_hash) if args.strict_hash is not None else (args.transport == "initramfs")
    started_at_utc = _utc_now()
    start_wall = time.monotonic()

    gen_init_cpio = _find_gen_init_cpio(linux_root, out_dir)
    if args.stage == "a":
        benches = args.bench if args.bench else STAGE_A_BENCHES
    else:
        benches = args.bench if args.bench else STAGE_B_BENCHES

    summary: dict[str, Any] = {
        "schema_version": "linx-spec-qemu-v1",
        "stage": args.stage,
        "transport": args.transport,
        "input_set": args.input_set,
        "spec_dir": str(spec_dir),
        "qemu": str(qemu),
        "qemu_provenance": qemu_binary_provenance(REPO_ROOT, qemu),
        "kernel": str(kernel),
        "sysroot": str(sysroot),
        "sysroot_provenance": _sysroot_provenance(sysroot),
        "memory_mb": args.memory_mb,
        "stack_limit": _spec_stack_limit_raw() or "default",
        "stack_limit_defines": _spec_stack_limit_defines(),
        "heartbeat_sec": args.heartbeat_sec,
        "qemu_heartbeat_interval": args.qemu_heartbeat_interval,
        "qemu_heartbeat_regs": bool(args.qemu_heartbeat_regs),
        "qemu_heartbeat_code_bytes": args.qemu_heartbeat_code_bytes,
        "qemu_heartbeat_same_site_warn": args.qemu_heartbeat_same_site_warn,
        "qemu_frame_stats": bool(args.qemu_frame_stats),
        "qemu_frame_restore_host_load": bool(args.qemu_frame_restore_host_load),
        "qemu_frame_restore_host_verify": bool(args.qemu_frame_restore_host_verify),
        "qemu_frame_restore_host_verify_limit": args.qemu_frame_restore_host_verify_limit,
        "qemu_tlb_stats": bool(args.qemu_tlb_stats),
        "qemu_tlb_inv_hot": bool(args.qemu_tlb_inv_hot),
        "qemu_tlb_fill_stats": bool(args.qemu_tlb_fill_stats),
        "qemu_tlb_fill_hot": bool(args.qemu_tlb_fill_hot),
        "qemu_tb_stats": bool(args.qemu_tb_stats),
        "qemu_fret_stk_trace": qemu_fret_stk_trace,
        "qemu_fentry_trace": qemu_fentry_trace,
        "qemu_fault_trace": bool(args.qemu_fault_trace or qemu_fault_trace_filters),
        "qemu_fault_trace_regs": bool(args.qemu_fault_trace_regs),
        "qemu_fault_trace_limit": args.qemu_fault_trace_limit,
        "qemu_fault_trace_filters": qemu_fault_trace_filters,
        "qemu_pc_watch": qemu_pc_watch,
        "qemu_syscall_trace": qemu_syscall_trace,
        "qemu_mem_trace": qemu_mem_trace,
        "guest_heartbeat_sec": args.guest_heartbeat_sec,
        "guest_proc_diagnostics": bool(args.guest_proc_diagnostics),
        "symbolize_heartbeat": bool(args.symbolize_heartbeat),
        "no_progress_timeout": args.no_progress_timeout,
        "fail_9p_timeout": bool(args.fail_9p_timeout),
        "append_extra": args.append_extra,
        "dump_prefix_bytes": args.dump_prefix_bytes,
        "strict_hash": strict_hash,
        "run_indices": args.run_index,
        "started_at_utc": started_at_utc,
        "results": {},
    }

    overall_ok = True
    for bench in benches:
        cfg = _resolve_cfg(spec_dir, bench, args.input_set)
        cfg = _select_run_indices(cfg, args.run_index)
        bench_out = out_dir / bench.replace(".", "_")
        bench_out.mkdir(parents=True, exist_ok=True)

        bench_result: dict[str, Any] = {
            "ok": False,
            "bench": bench,
            "run_dir": "",
            "qemu": [],
            "run_count": len(cfg.get("runs", [])),
            "selected_run_indices": cfg.get("selected_run_indices", []),
            "specdiff": {},
        }

        try:
            run_dir = _prepare_run_dir(
                spec_dir,
                bench,
                cfg,
                preserve_symlinks=(args.transport == "9p"),
                input_set=args.input_set,
            )
            bench_result["run_dir"] = str(run_dir)
            init_static = _choose_init_static(args.transport, sysroot)
            guest_shared_runtime = _run_dir_requires_guest_shared_runtime(run_dir, cfg.get("exes", []))
            bench_result["guest_shared_runtime"] = guest_shared_runtime
            if guest_shared_runtime and not (sysroot / "lib" / "libc.so").exists():
                raise SystemExit(
                    f"error: benchmark requires shared musl guest runtime but sysroot is missing {(sysroot / 'lib' / 'libc.so')}"
                )

            qemu_ok = True
            qemu_runs: list[dict[str, Any]] = []
            hash_checks: list[dict[str, Any]] = []
            hash_ok = True
            collected_outputs = False
            collected_outputs_ok = True
            for run_idx, run_cfg in enumerate(cfg.get("runs", []), start=1):
                run_out = bench_out / f"run_{run_idx:03d}"
                run_out.mkdir(parents=True, exist_ok=True)

                init_bin = _build_init_for_run(
                    bench,
                    cfg,
                    run_cfg,
                    run_dir,
                    run_out,
                    clang,
                    sysroot,
                    args.transport,
                    args.dump_prefix_bytes,
                    args.guest_heartbeat_sec,
                    args.guest_proc_diagnostics,
                    emit_hashes=(args.transport == "initramfs"),
                )
                initramfs, initramfs_log = _build_initramfs(
                    bench,
                    run_out,
                    gen_init_cpio,
                    init_bin,
                    sysroot,
                    run_dir if args.transport == "initramfs" else None,
                    args.transport,
                    include_shared_runtime=(guest_shared_runtime or not init_static),
                )

                qemu_log = run_out / "qemu.log"
                qemu_info = _run_qemu(
                    bench,
                    qemu,
                    kernel,
                    initramfs,
                    spec_dir,
                    args.timeout,
                    qemu_log,
                    args.transport,
                    args.memory_mb,
                    args.heartbeat_sec,
                    args.qemu_heartbeat_interval,
                    args.qemu_heartbeat_regs,
                    args.qemu_heartbeat_code_bytes,
                    args.qemu_heartbeat_same_site_warn,
                    args.qemu_frame_stats,
                    args.qemu_frame_restore_host_load,
                    args.qemu_frame_restore_host_verify,
                    args.qemu_frame_restore_host_verify_limit,
                    args.qemu_tlb_stats,
                    args.qemu_tlb_inv_hot,
                    args.qemu_tlb_fill_stats,
                    args.qemu_tlb_fill_hot,
                    args.qemu_tb_stats,
                    qemu_fret_stk_trace,
                    qemu_fentry_trace,
                    args.no_progress_timeout,
                    args.append_extra,
                    args.symbolize_heartbeat,
                    args.qemu_fault_trace,
                    args.qemu_fault_trace_regs,
                    args.qemu_fault_trace_limit,
                    qemu_fault_trace_filters,
                    qemu_pc_watch,
                    qemu_syscall_trace,
                    qemu_mem_trace,
                )
                qemu_info["run_index"] = run_idx
                qemu_info["source_run_index"] = run_cfg.get("source_run_index", run_idx)
                qemu_info["configured_argv"] = list(run_cfg.get("argv", []))
                qemu_info["effective_argv"] = _effective_run_argv(run_cfg)
                qemu_info["stdout"] = run_cfg.get("stdout")
                qemu_info["stderr"] = run_cfg.get("stderr")
                qemu_info["initramfs"] = str(initramfs)
                qemu_info["initramfs_log"] = str(initramfs_log)
                qemu_runs.append(qemu_info)

                if args.transport == "9p":
                    # In 9p mode, guest outputs are validated from host-visible files.
                    # Do not gate on panic/timeout here: when /init execs a benchmark
                    # directly as PID1, Linux may terminate with "init exited" panic
                    # after the benchmark finishes. Host-side specdiff is authoritative.
                    one_ok = (
                        (not qemu_info["fail_marker"])
                        and (not args.fail_9p_timeout or not qemu_info["timed_out"])
                        and (not qemu_info.get("trap_seen", False))
                        and (not qemu_info.get("stalled", False))
                    )
                else:
                    one_ok = (
                        (not qemu_info["fail_marker"])
                        and (not qemu_info["panic_seen"])
                        and (not qemu_info.get("trap_seen", False))
                        and (not qemu_info["timed_out"])
                        and (not qemu_info.get("stalled", False))
                    )

                if one_ok and args.transport == "initramfs":
                    verify_names = set(run_cfg.get("verify_outputs", []))
                    if verify_names:
                        cmp_subset = [cmp_cfg for cmp_cfg in cfg.get("compares", []) if cmp_cfg["out"] in verify_names]
                        if not cmp_subset:
                            raise SystemExit(
                                f"error: no compare entries matched verify_outputs for {bench} run {run_idx}: {sorted(verify_names)}"
                            )
                        subset_cfg = {"compares": cmp_subset}
                        hash_info = _verify_hash_markers(spec_dir, qemu_log, bench, subset_cfg, run_out)
                        qemu_info["hashcheck"] = hash_info
                        hash_ok = hash_ok and bool(hash_info.get("ok", False))
                        for check in hash_info.get("checks", []):
                            hash_checks.append({**check, "run_index": run_idx})
                        full_dump_available = (
                            args.dump_prefix_bytes > 0
                            and all(
                                check.get("actual_size") is not None
                                and int(check["actual_size"]) <= args.dump_prefix_bytes
                                for check in hash_info.get("checks", [])
                            )
                        )
                        if full_dump_available:
                            collect_info = _collect_outputs_from_log(qemu_log, run_dir, subset_cfg)
                            qemu_info["collected_outputs"] = collect_info
                            collected_outputs = True
                            collected_outputs_ok = collected_outputs_ok and bool(collect_info.get("ok", False))
                        if strict_hash and not hash_info.get("ok", False):
                            _annotate_hash_mismatch(qemu_info, hash_info)
                            one_ok = False

                if not one_ok:
                    qemu_ok = False
                    break

            bench_result["qemu"] = qemu_runs

            if qemu_ok:
                if args.transport == "initramfs":
                    if collected_outputs and collected_outputs_ok:
                        specdiff_info = _run_specdiff(spec_dir, run_dir, bench, cfg, bench_out)
                        specdiff_info["hash_checks"] = hash_checks
                        specdiff_info["strict_hash"] = strict_hash
                        bench_result["specdiff"] = specdiff_info
                        if not specdiff_info.get("ok", False):
                            _annotate_specdiff_mismatch(qemu_runs, specdiff_info)
                        if _strict_hash_checks_ok(specdiff_info):
                            bench_result["ok"] = True
                        else:
                            bench_result["ok"] = bool(specdiff_info.get("ok", False)) and (
                                bool(hash_ok) if strict_hash else True
                            )
                    else:
                        bench_result["specdiff"] = _hash_specdiff_result(hash_ok, hash_checks, strict_hash)
                        bench_result["ok"] = bool(hash_ok) if strict_hash else True
                else:
                    specdiff_info = _run_specdiff(spec_dir, run_dir, bench, cfg, bench_out)
                    bench_result["specdiff"] = specdiff_info
                    if not specdiff_info.get("ok", False):
                        _annotate_specdiff_mismatch(qemu_runs, specdiff_info)
                    bench_result["ok"] = bool(specdiff_info.get("ok", False))
            else:
                bench_result["specdiff"] = _hash_specdiff_result(False, hash_checks, strict_hash)
                bench_result["ok"] = False

        except Exception as exc:  # pylint: disable=broad-except
            bench_result["error"] = str(exc)
            bench_result["ok"] = False

        summary["results"][bench] = bench_result
        overall_ok = overall_ok and bool(bench_result.get("ok", False))

    summary["ok"] = overall_ok
    summary["finished_at_utc"] = _utc_now()
    summary["elapsed_sec"] = round(time.monotonic() - start_wall, 3)
    summary_path = out_dir / f"stage_{args.stage}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if overall_ok:
        print(f"ok: stage-{args.stage} benchmarks passed ({summary_path})")
        return 0

    print(f"error: stage-{args.stage} benchmarks failed ({summary_path})", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
