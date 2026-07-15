#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
BUILD_SCRIPT = SCRIPT_DIR / "build_int_rate_linx.sh"

SUPPORTED_BENCHES = {
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
}


@dataclass
class BenchSnapshot:
    bench: str
    exe_dir: Path
    pre_names: list[str]
    backup_dir: Path


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _find_llvm_readelf() -> Path:
    cands = [
        REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "llvm-readelf",
    ]
    for cand in cands:
        if cand.is_file() and os.access(cand, os.X_OK):
            return cand
    host = shutil.which("llvm-readelf")
    if host:
        return Path(host)
    raise SystemExit("error: llvm-readelf not found; set PATH or install llvm-readelf")


def _parse_elf_header(readelf: Path, exe: Path) -> tuple[str | None, str | None, str | None]:
    proc = subprocess.run(
        [str(readelf), "-h", str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        text=True,
    )
    if proc.returncode != 0:
        return None, None, None

    machine: str | None = None
    elf_type: str | None = None
    entry: str | None = None
    for line in proc.stdout.splitlines():
        s = line.strip()
        if s.startswith("Machine:"):
            machine = s.split(":", 1)[1].strip()
        elif s.startswith("Type:"):
            m = re.search(r"Type:\s*([A-Z_]+)", s)
            elf_type = m.group(1) if m else s.split(":", 1)[1].strip()
        elif s.startswith("Entry point address:"):
            entry = s.split(":", 1)[1].strip()
    return machine, elf_type, entry


def _parse_elf_symbol(readelf: Path, exe: Path, symbol: str) -> str | None:
    proc = subprocess.run(
        [str(readelf), "-s", str(exe)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        text=True,
    )
    if proc.returncode != 0:
        return None

    for line in proc.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1] == symbol and len(parts) >= 2:
            return parts[1]
    return None


def _normalize_hex(value: str | None) -> str | None:
    if not value:
        return None
    out = value.strip().lower()
    if out.startswith("0x"):
        out = out[2:]
    out = out.lstrip("0") or "0"
    return out


def _snapshot_benches(spec_dir: Path, benches: list[str], backup_root: Path) -> list[BenchSnapshot]:
    snaps: list[BenchSnapshot] = []
    for bench in benches:
        exe_dir = spec_dir / "benchspec" / "CPU" / bench / "exe"
        exe_dir.mkdir(parents=True, exist_ok=True)
        pre_names = sorted(p.name for p in exe_dir.glob("*.mytest-m64") if p.is_file())
        bench_backup = backup_root / bench / "exe"
        bench_backup.mkdir(parents=True, exist_ok=True)
        for name in pre_names:
            shutil.copy2(exe_dir / name, bench_backup / name)
        snaps.append(BenchSnapshot(bench=bench, exe_dir=exe_dir, pre_names=pre_names, backup_dir=bench_backup))
    return snaps


def _restore_snapshots(snaps: list[BenchSnapshot]) -> bool:
    ok = True
    for snap in snaps:
        try:
            current_names = sorted(p.name for p in snap.exe_dir.glob("*.mytest-m64") if p.is_file())
            pre_set = set(snap.pre_names)

            for name in current_names:
                if name not in pre_set:
                    try:
                        (snap.exe_dir / name).unlink()
                    except OSError:
                        ok = False

            for name in snap.pre_names:
                src = snap.backup_dir / name
                dst = snap.exe_dir / name
                if src.is_file():
                    shutil.copy2(src, dst)
                else:
                    ok = False
        except OSError:
            ok = False
    return ok


def _load_build_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return obj if isinstance(obj, dict) else {}


def _collect_executables(
    spec_dir: Path,
    benches: list[str],
    build_manifest: dict[str, Any],
) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {bench: [] for bench in benches}
    bench_results = build_manifest.get("bench_results")
    if isinstance(bench_results, dict):
        for bench in benches:
            row = bench_results.get(bench)
            if not isinstance(row, dict):
                continue
            executables = row.get("executables")
            if not isinstance(executables, list):
                continue
            for entry in executables:
                if not isinstance(entry, dict):
                    continue
                if not bool(entry.get("exists", False)):
                    continue
                path = entry.get("path")
                if isinstance(path, str) and path:
                    exe_path = Path(path)
                    if exe_path.is_file():
                        out[bench].append(exe_path)

    for bench in benches:
        if out[bench]:
            continue
        exe_dir = spec_dir / "benchspec" / "CPU" / bench / "exe"
        out[bench] = sorted(p for p in exe_dir.glob("*.mytest-m64") if p.is_file())

    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Prepare phase-b static SPEC images for LinxCore xcheck.")
    ap.add_argument(
        "--spec-dir",
        default=str(REPO_ROOT / "workloads" / "spec2017" / "cpu2017v118_x64_gcc12_avx2"),
    )
    ap.add_argument("--bench", action="append", required=True, help="Benchmark to stage (repeatable).")
    ap.add_argument(
        "--out-dir",
        default=str(REPO_ROOT / "workloads" / "generated" / "spec2017" / "phaseb_static_images"),
    )
    ap.add_argument("--mode", choices=("phase-b",), default="phase-b")
    ap.add_argument("--optimize", default="", help="Pass-through optimize flags for build_int_rate_linx.sh")
    args = ap.parse_args(argv)

    if not BUILD_SCRIPT.is_file():
        raise SystemExit(f"error: missing build script: {BUILD_SCRIPT}")

    benches_raw = [b.strip() for b in args.bench if b and b.strip()]
    benches: list[str] = []
    seen: set[str] = set()
    for bench in benches_raw:
        if bench not in SUPPORTED_BENCHES:
            raise SystemExit(f"error: unsupported --bench '{bench}'")
        if bench in seen:
            continue
        seen.add(bench)
        benches.append(bench)

    spec_dir = Path(os.path.expanduser(args.spec_dir)).resolve()
    if not (spec_dir / "benchspec" / "CPU").is_dir():
        raise SystemExit(f"error: invalid SPEC dir: {spec_dir}")

    out_dir = Path(os.path.expanduser(args.out_dir)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    backup_root = out_dir / ".backups"
    backup_root.mkdir(parents=True, exist_ok=True)

    build_manifest_path = out_dir / "phaseb_build_manifest.json"
    build_log_path = out_dir / "phaseb_build.log"
    phaseb_manifest_path = out_dir / "phaseb_image_manifest.json"

    readelf = _find_llvm_readelf()

    snapshots = _snapshot_benches(spec_dir, benches, backup_root)
    restore_ok = False
    build_rc = -1
    build_exc = ""

    try:
        cmd = [
            str(BUILD_SCRIPT),
            "--spec-dir",
            str(spec_dir),
            "--mode",
            args.mode,
            "--emit-manifest",
            str(build_manifest_path),
        ]
        if args.optimize:
            cmd.extend(["--optimize", args.optimize])
        for bench in benches:
            cmd.extend(["--bench", bench])

        env = dict(os.environ)
        env["LINX_SPEC_FORCE_STATIC"] = "1"

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            env=env,
            text=True,
        )
        build_log_path.write_text(proc.stdout, encoding="utf-8")
        build_rc = proc.returncode
        if build_rc != 0:
            build_exc = f"build_int_rate_linx.sh failed with rc={build_rc}"

        build_manifest = _load_build_manifest(build_manifest_path)
        exes_by_bench = _collect_executables(spec_dir, benches, build_manifest)

        images: list[dict[str, Any]] = []
        for bench in benches:
            build_log = spec_dir / "tmp" / "linx-build-logs" / f"{bench}.log"
            bench_exes = exes_by_bench.get(bench, [])
            if not bench_exes:
                images.append(
                    {
                        "bench": bench,
                        "exe": "",
                        "elf_machine": None,
                        "elf_type": None,
                        "entry_point": None,
                        "build_log": str(build_log),
                        "status": "missing_executables",
                    }
                )
                continue

            for src_exe in bench_exes:
                staged = out_dir / bench / "exe" / src_exe.name
                staged.parent.mkdir(parents=True, exist_ok=True)
                status = "ok"
                try:
                    shutil.copy2(src_exe, staged)
                except OSError as exc:
                    status = f"copy_failed: {exc}"

                machine, elf_type, entry = (None, None, None)
                start_symbol = None
                main_symbol = None
                static_entry_ok = False
                if status == "ok":
                    machine, elf_type, entry = _parse_elf_header(readelf, staged)
                    if machine is None or elf_type is None or entry is None:
                        status = "readelf_failed"
                    else:
                        start_symbol = _parse_elf_symbol(readelf, staged, "_start")
                        main_symbol = _parse_elf_symbol(readelf, staged, "main")
                        entry_norm = _normalize_hex(entry)
                        start_norm = _normalize_hex(start_symbol)
                        main_norm = _normalize_hex(main_symbol)
                        static_entry_ok = (
                            entry_norm is not None
                            and start_norm is not None
                            and entry_norm == start_norm
                            and (main_norm is None or entry_norm != main_norm)
                        )
                        if not static_entry_ok:
                            status = "invalid_static_entry"

                if build_rc != 0 and status == "ok":
                    status = "build_failed"

                images.append(
                    {
                        "bench": bench,
                        "exe": str(staged),
                        "source_exe": str(src_exe),
                        "elf_machine": machine,
                        "elf_type": elf_type,
                        "entry_point": entry,
                        "start_symbol": start_symbol,
                        "main_symbol": main_symbol,
                        "static_entry_ok": static_entry_ok,
                        "build_log": str(build_log),
                        "status": status,
                    }
                )

        overall_ok = (build_rc == 0) and all(row.get("status") == "ok" for row in images)

        manifest = {
            "schema_version": "linx-spec-phaseb-static-images-v1",
            "generated_at_utc": _utc_now(),
            "spec_dir": str(spec_dir),
            "mode": args.mode,
            "linx_spec_force_static": True,
            "selected_benches": benches,
            "optimize": args.optimize,
            "build": {
                "returncode": build_rc,
                "log": str(build_log_path),
                "manifest": str(build_manifest_path),
                "error": build_exc or None,
            },
            "images": images,
            "overall_ok": overall_ok,
        }

        phaseb_manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        print(f"phaseb_image_manifest={phaseb_manifest_path}")
        print(f"build_log={build_log_path}")
        print(f"build_manifest={build_manifest_path}")
        print(f"overall_ok={str(overall_ok).lower()}")

        return 0 if overall_ok else 1

    finally:
        restore_ok = _restore_snapshots(snapshots)
        if not restore_ok:
            print("warn: failed to fully restore original SPEC executables", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
