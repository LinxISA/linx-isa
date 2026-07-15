#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any


WORKLOADS_DIR = Path(__file__).resolve().parent
REPO_ROOT = WORKLOADS_DIR.parent
GENERATED_DIR = WORKLOADS_DIR / "generated"
DEFAULT_PUBLISH_ELF_DIR = GENERATED_DIR / "elf"
PINNED_READELF = REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "llvm-readelf"

SEMANTIC_MARKERS: dict[str, dict[str, tuple[str, ...]]] = {
    "coremark": {
        "required": ("Correct operation validated. See README.md for run and reporting rules.",),
        "forbidden": ("ERROR",),
    },
    "dhrystone": {
        "required": (
            "Execution ends",
            "Final values of the variables used in the benchmark:",
            "Int_Glob:            5",
            "Bool_Glob:           1",
            "Ch_1_Glob:           A",
            "Ch_2_Glob:           B",
            "Arr_1_Glob[8]:       7",
            "Int_1_Loc:           5",
            "Int_2_Loc:           13",
            "Int_3_Loc:           7",
            "Str_1_Loc:           DHRYSTONE PROGRAM, 1'ST STRING",
            "Str_2_Loc:           DHRYSTONE PROGRAM, 2'ND STRING",
        ),
        "forbidden": (),
    },
}


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    verbose: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess[bytes]:
    if verbose:
        print("+", shlex.join(cmd), file=sys.stderr)
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=False, **kwargs)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_exe(path: Path, name: str) -> Path:
    if not path.exists():
        raise SystemExit(f"error: {name} not found: {path}")
    if not os.access(path, os.X_OK):
        raise SystemExit(f"error: {name} not executable: {path}")
    # Preserve a symlink invocation name: LLVM selects readelf/readobj output
    # personality from argv[0].  Resolving llvm-readelf to llvm-readobj changes
    # its output contract even though both paths name the same binary.
    return path.absolute()


def _resolve_cc(arg_cc: str | None) -> Path:
    raw = arg_cc or os.environ.get("CC")
    if not raw:
        raise SystemExit("error: compiler is required; set --cc or CC")
    return _check_exe(Path(os.path.expanduser(raw)), "cc")


def _resolve_readelf(arg_readelf: str | None, cc: Path) -> Path:
    raw = arg_readelf or os.environ.get("READELF")
    if raw:
        return _check_exe(Path(os.path.expanduser(raw)), "readelf")
    sibling = cc.parent / "llvm-readelf"
    for candidate in (sibling, PINNED_READELF):
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate.absolute()
    for tool in ("llvm-readelf", "readelf"):
        resolved = shutil.which(tool)
        if resolved:
            return _check_exe(Path(resolved), "readelf")
    raise SystemExit("error: llvm-readelf/readelf is required; set --readelf or READELF")


def _target_contract(target: str) -> tuple[str, str, str]:
    arch = target.split("-", 1)[0].lower()
    little_endian = "2's complement, little endian"
    contracts = {
        "linx64": ("Linx", "ELF64", little_endian),
        "linx32": ("Linx", "ELF32", little_endian),
        "x86_64": ("Advanced Micro Devices X86-64", "ELF64", little_endian),
        "aarch64": ("AArch64", "ELF64", little_endian),
        "arm64": ("AArch64", "ELF64", little_endian),
        "riscv64": ("RISC-V", "ELF64", little_endian),
        "riscv32": ("RISC-V", "ELF32", little_endian),
    }
    try:
        return contracts[arch]
    except KeyError as exc:
        raise SystemExit(f"error: unsupported target architecture for ELF verification: {arch}") from exc


def _effective_link_mode(requested: str, *, target: str, sysroot: str | None) -> str:
    if requested != "auto":
        return requested
    return "musl-static" if target.startswith(("linx64-", "linx32-")) and sysroot else "default"


def _coremark_iteration_flags(iterations: int) -> list[str]:
    # The posix port defaults to SEED_ARG, which would ignore ITERATIONS when
    # the runner supplies no guest argv.  Volatile seeding gives posix and
    # simple the same contract; ITERATIONS=0 requests upstream auto-calibration.
    return [f"-DITERATIONS={iterations}", "-DSEED_METHOD=SEED_VOLATILE"]


def _validate_run_parameters(*, coremark_iterations: int, dhrystone_runs: int, timeout: float) -> None:
    if coremark_iterations < 0:
        raise SystemExit("error: coremark iterations must be zero (auto-calibration) or positive")
    if dhrystone_runs <= 0 or timeout <= 0:
        raise SystemExit("error: dhrystone runs and timeout must be positive")


def _tool_identity(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "resolved_path": str(path.resolve()),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
    }


def _command_file_identities(command: list[str], *, tested_exe: Path) -> list[dict[str, Any]]:
    """Bind every command argument that names a real file, except the test ELF."""
    identities: list[dict[str, Any]] = []
    tested_resolved = tested_exe.resolve()
    for index, argument in enumerate(command):
        candidates = [argument]
        if "=" in argument:
            candidates.append(argument.split("=", 1)[1])
        selected: Path | None = None
        for raw in candidates:
            path = Path(os.path.expanduser(raw))
            if index == 0 and not path.exists():
                resolved = shutil.which(raw)
                if resolved:
                    path = Path(resolved)
            if not path.is_absolute():
                path = Path.cwd() / path
            if path.is_file():
                selected = path.absolute()
                break
        if selected is None or selected.resolve() == tested_resolved:
            continue
        identity = _tool_identity(selected)
        identity.update({"argument_index": index, "argument": argument})
        identities.append(identity)
    return identities


def _identity_fingerprint(identities: list[dict[str, Any]]) -> list[tuple[Any, ...]]:
    return [
        (
            item["argument_index"],
            item["argument"],
            item["path"],
            item["resolved_path"],
            item["sha256"],
            item["size_bytes"],
        )
        for item in identities
    ]


def _common_flags(*, target: str, sysroot: str | None, opt: str, extra_cflags: list[str]) -> list[str]:
    flags: list[str] = ["-target", target, opt]
    if sysroot:
        flags.append(f"--sysroot={Path(os.path.expanduser(sysroot)).resolve()}")
    flags.extend(extra_cflags)
    return flags


def _resolve_runtime_lib(*, sysroot: str | None, runtime_lib: str | None) -> Path:
    if runtime_lib:
        path = Path(os.path.expanduser(runtime_lib)).resolve()
        if not path.exists():
            raise SystemExit(f"error: runtime lib not found: {path}")
        return path
    if not sysroot:
        raise SystemExit("error: --sysroot is required for musl-static link mode")
    sysroot_path = Path(os.path.expanduser(sysroot)).resolve()
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
    sysroot_path = Path(os.path.expanduser(sysroot)).resolve()
    lib_dir = sysroot_path / "lib"
    crt1 = lib_dir / "rcrt1.o"
    if not crt1.exists():
        crt1 = lib_dir / "crt1.o"
    if not crt1.exists():
        raise SystemExit(f"error: missing static startup object under {lib_dir}")
    required = (lib_dir / "crti.o", lib_dir / "crtn.o", lib_dir / "libc.a")
    for path in required:
        if not path.exists():
            raise SystemExit(f"error: missing musl static runtime object: {path}")
    runtime = _resolve_runtime_lib(sysroot=sysroot, runtime_lib=runtime_lib)
    flags = [
        "-fuse-ld=lld",
        "-static",
        "-Wl,-pie",
        "-nostdlib",
        str(crt1),
        str(lib_dir / "crti.o"),
        str(runtime),
        str(lib_dir / "libc.a"),
        str(lib_dir / "crtn.o"),
    ]
    if image_base:
        flags.append(f"-Wl,--image-base={image_base}")
    return flags


def _invoke_build(
    *,
    name: str,
    exe: Path,
    command: list[str],
    logs_dir: Path,
    verbose: bool,
) -> dict[str, Any]:
    stdout = logs_dir / f"{name}.build.stdout.txt"
    stderr = logs_dir / f"{name}.build.stderr.txt"
    if exe.is_file() or exe.is_symlink():
        exe.unlink()
    proc = _run(command, verbose=verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout.write_bytes(proc.stdout or b"")
    stderr.write_bytes(proc.stderr or b"")
    errors: list[str] = []
    if proc.returncode != 0:
        errors.append(f"compiler exited {proc.returncode}")
    if proc.returncode == 0 and not exe.is_file():
        errors.append("compiler exited zero but did not produce the executable")
    return {
        "status": "PASS" if not errors else "FAIL",
        "command": command,
        "cwd": str(Path.cwd()),
        "exit_code": proc.returncode,
        "stdout": str(stdout),
        "stdout_sha256": _sha256(stdout),
        "stderr": str(stderr),
        "stderr_sha256": _sha256(stderr),
        "errors": errors,
    }


def _build_coremark(
    *,
    cc: Path,
    target: str,
    sysroot: str | None,
    opt: str,
    extra_cflags: list[str],
    out_dir: Path,
    logs_dir: Path,
    port: str,
    iterations: int,
    link_mode: str,
    runtime_lib: str | None,
    image_base: str | None,
    verbose: bool,
) -> tuple[Path, dict[str, Any]]:
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
    link_flags = (
        _static_link_flags(sysroot=sysroot, runtime_lib=runtime_lib, image_base=image_base)
        if link_mode == "musl-static"
        else []
    )
    command = [
        str(cc),
        *flags,
        "-std=gnu99",
        *_coremark_iteration_flags(iterations),
        '-DFLAGS_STR="external-runner"',
        "-DPERFORMANCE_RUN=1",
        f"-I{core_up}",
        f"-I{port_dir}",
        *[str(path) for path in srcs],
        *link_flags,
        "-o",
        str(exe),
    ]
    return exe, _invoke_build(name="coremark", exe=exe, command=command, logs_dir=logs_dir, verbose=verbose)


def _build_dhrystone(
    *,
    cc: Path,
    target: str,
    sysroot: str | None,
    opt: str,
    extra_cflags: list[str],
    out_dir: Path,
    logs_dir: Path,
    runs: int,
    link_mode: str,
    runtime_lib: str | None,
    image_base: str | None,
    verbose: bool,
) -> tuple[Path, dict[str, Any]]:
    upstream = WORKLOADS_DIR / "dhrystone" / "upstream"
    srcs = [upstream / "dhry_1.c", upstream / "dhry_2.c"]
    dhry_out = out_dir / "dhrystone"
    dhry_out.mkdir(parents=True, exist_ok=True)
    exe = dhry_out / "dhrystone.elf"
    flags = _common_flags(target=target, sysroot=sysroot, opt=opt, extra_cflags=extra_cflags)
    link_flags = (
        _static_link_flags(sysroot=sysroot, runtime_lib=runtime_lib, image_base=image_base)
        if link_mode == "musl-static"
        else []
    )
    command = [
        str(cc),
        *flags,
        "-std=gnu89",
        "-DTIME",
        "-Wno-implicit-int",
        "-Wno-return-type",
        "-Wno-implicit-function-declaration",
        f"-DDHRY_ITERS={runs}",
        *[str(path) for path in srcs],
        *link_flags,
        "-o",
        str(exe),
    ]
    return exe, _invoke_build(name="dhrystone", exe=exe, command=command, logs_dir=logs_dir, verbose=verbose)


def _parse_readelf_field(text: str, field: str) -> str | None:
    match = re.search(rf"^\s*{re.escape(field)}:\s*(.+?)\s*$", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def _inspect_elf(
    path: Path,
    *,
    readelf: Path,
    expected_machine: str,
    expected_class: str,
    expected_static: bool | None,
    logs_dir: Path,
    name: str,
    expected_data_encoding: str = "2's complement, little endian",
) -> dict[str, Any]:
    stdout = logs_dir / f"{name}.readelf.stdout.txt"
    stderr = logs_dir / f"{name}.readelf.stderr.txt"
    errors: list[str] = []
    sha256: str | None = None
    size_bytes: int | None = None
    magic_ok = False
    if path.is_symlink():
        errors.append("executable is a symbolic link")
    if not path.is_file():
        errors.append("executable is not a regular file")
    else:
        data = path.read_bytes()[:4]
        magic_ok = data == b"\x7fELF"
        if not magic_ok:
            errors.append("invalid ELF magic")
        sha256 = _sha256(path)
        size_bytes = path.stat().st_size
        if size_bytes == 0:
            errors.append("empty executable")
        if not os.access(path, os.X_OK):
            errors.append("executable bit is not set")

    command = [str(readelf), "--file-header", "--program-headers", "--dynamic", "--wide", str(path)]
    proc = _run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout.write_bytes(proc.stdout or b"")
    stderr.write_bytes(proc.stderr or b"")
    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    if proc.returncode != 0:
        errors.append(f"readelf exited {proc.returncode}")

    elf_class = _parse_readelf_field(text, "Class")
    data_encoding = _parse_readelf_field(text, "Data")
    elf_type = _parse_readelf_field(text, "Type")
    machine = _parse_readelf_field(text, "Machine")
    entry = _parse_readelf_field(text, "Entry point address")
    has_interp = bool(re.search(r"^\s*INTERP\s", text, flags=re.MULTILINE))
    dynamic_needed = re.findall(
        r"^\s*(?:0x[0-9a-fA-F]+)?\s*\(?NEEDED\)?\s+Shared library:\s*\[([^]]+)\]",
        text,
        flags=re.MULTILINE,
    )
    static = not has_interp and not dynamic_needed if proc.returncode == 0 else None
    if elf_class != expected_class:
        errors.append(f"ELF class mismatch: expected {expected_class}, observed {elf_class or 'unknown'}")
    if machine != expected_machine:
        errors.append(f"machine mismatch: expected {expected_machine}, observed {machine or 'unknown'}")
    if data_encoding != expected_data_encoding:
        errors.append(
            f"data encoding mismatch: expected {expected_data_encoding}, observed {data_encoding or 'unknown'}"
        )
    if entry in (None, "0x0", "0"):
        errors.append(f"invalid entry point: {entry or 'missing'}")
    if expected_static is not None and static != expected_static:
        expected = "static" if expected_static else "dynamic"
        observed = "static" if static else "dynamic"
        errors.append(f"staticity mismatch: expected {expected}, observed {observed}")
    if expected_static is True and dynamic_needed:
        errors.append(f"static executable contains DT_NEEDED entries: {', '.join(dynamic_needed)}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "path": str(path.resolve(strict=False)),
        "sha256": sha256,
        "size_bytes": size_bytes,
        "elf_magic": magic_ok,
        "elf_class": elf_class,
        "data_encoding": data_encoding,
        "type": elf_type,
        "machine": machine,
        "entry_point": entry,
        "static": static,
        "has_interp": has_interp,
        "dynamic_needed": dynamic_needed,
        "expected_machine": expected_machine,
        "expected_class": expected_class,
        "expected_data_encoding": expected_data_encoding,
        "expected_static": expected_static,
        "readelf_command": command,
        "readelf_exit_code": proc.returncode,
        "readelf_stdout": str(stdout),
        "readelf_stdout_sha256": _sha256(stdout),
        "readelf_stderr": str(stderr),
        "readelf_stderr_sha256": _sha256(stderr),
        "errors": errors,
    }


def _classify_runtime(name: str, *, exit_code: int | None, timed_out: bool, output: str) -> dict[str, Any]:
    contract = SEMANTIC_MARKERS[name]
    missing = [marker for marker in contract["required"] if marker not in output]
    forbidden = [marker for marker in contract["forbidden"] if marker in output]
    if timed_out:
        status = "TIMEOUT"
    elif exit_code != 0 or missing or forbidden:
        status = "FAIL"
    else:
        status = "PASS"
    return {
        "status": status,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "semantic_success": not missing and not forbidden,
        "required_markers": list(contract["required"]),
        "missing_markers": missing,
        "forbidden_markers": list(contract["forbidden"]),
        "observed_forbidden_markers": forbidden,
    }


def _run_with_wrapper(
    *,
    name: str,
    exe: Path,
    run_command: str,
    timeout: float,
    out_dir: Path,
    verbose: bool,
    expected_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    rendered = run_command.replace("{exe}", str(exe)) if "{exe}" in run_command else run_command
    command = shlex.split(rendered)
    if "{exe}" not in run_command:
        command.append(str(exe))
    stdout = out_dir / f"{name}.runtime.stdout.txt"
    stderr = out_dir / f"{name}.runtime.stderr.txt"
    artifact_sha256_before = _sha256(exe)
    command_file_identities_before = _command_file_identities(command, tested_exe=exe)
    timed_out = False
    exit_code: int | None
    out_data = b""
    err_data = b""
    if verbose:
        print("+", shlex.join(command), file=sys.stderr)
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        out_data, err_data = proc.communicate(timeout=timeout)
        exit_code = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        exit_code = None
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out_data, err_data = proc.communicate()
    stdout.write_bytes(out_data)
    stderr.write_bytes(err_data)
    combined = (out_data + b"\n" + err_data).decode("utf-8", errors="replace")
    evidence = _classify_runtime(name, exit_code=exit_code, timed_out=timed_out, output=combined)
    artifact_sha256_after = _sha256(exe)
    command_file_identities_after = _command_file_identities(command, tested_exe=exe)
    errors: list[str] = []
    if expected_artifact_sha256 is not None and artifact_sha256_before != expected_artifact_sha256:
        errors.append("executable no longer matches the inspected build artifact")
    if artifact_sha256_after != artifact_sha256_before:
        errors.append("executable changed while it was being run")
    if _identity_fingerprint(command_file_identities_after) != _identity_fingerprint(command_file_identities_before):
        errors.append("a command file argument changed while it was being run")
    if errors:
        evidence["status"] = "FAIL"
        evidence["semantic_success"] = False
    launcher = next(
        (item for item in command_file_identities_before if item["argument_index"] == 0),
        None,
    )
    evidence.update(
        {
            "command": command,
            "cwd": str(Path.cwd()),
            "launcher": launcher,
            "command_file_identities": command_file_identities_before,
            "command_file_identities_after": command_file_identities_after,
            "stdout": str(stdout),
            "stdout_sha256": _sha256(stdout),
            "stderr": str(stderr),
            "stderr_sha256": _sha256(stderr),
            "artifact_sha256_before": artifact_sha256_before,
            "artifact_sha256_after": artifact_sha256_after,
            "errors": errors,
        }
    )
    return evidence


def _compose_result(
    *,
    name: str,
    build: dict[str, Any],
    artifact: dict[str, Any],
    runtime: dict[str, Any] | None,
) -> dict[str, Any]:
    build_pass = build.get("status") == "PASS" and artifact.get("status") == "PASS"
    runtime_status = str(runtime.get("status")) if runtime else "NOT_RUN"
    runtime_pass = runtime_status == "PASS"
    if not build_pass:
        status = "BUILD_FAIL"
    elif runtime is None:
        status = "BUILD_ONLY"
    elif runtime_status == "PASS":
        status = "RUN_PASS"
    elif runtime_status == "TIMEOUT":
        status = "RUN_TIMEOUT"
    else:
        status = "RUN_FAIL"
    return {
        "name": name,
        "status": status,
        "build_status": "PASS" if build_pass else "FAIL",
        "build_pass": build_pass,
        "runtime_status": runtime_status,
        "runtime_pass": runtime_pass,
        "build": build,
        "artifact": artifact,
        "runtime": runtime,
    }


def _publish_executable(exe: Path, published_name: str, publish_dir: Path | None) -> Path | None:
    if publish_dir is None:
        return None
    publish_dir.mkdir(parents=True, exist_ok=True)
    destination = publish_dir / published_name
    shutil.copy2(exe, destination)
    destination.chmod(destination.stat().st_mode | 0o111)
    return destination.resolve()


def _write_report(
    path: Path,
    results: list[dict[str, Any]],
    *,
    target: str,
    cc: Path,
    readelf: Path,
    run_command: str | None,
    link_mode: str,
    build_all_pass: bool,
    runtime_all_pass: bool | None,
) -> None:
    runtime_text = "not requested" if runtime_all_pass is None else ("PASS" if runtime_all_pass else "FAIL")
    lines = [
        "# Benchmark Evidence Report",
        "",
        f"- Target: `{target}`",
        f"- Compiler: `{cc}`",
        f"- ELF inspector: `{readelf}`",
        f"- Requested gate: `{'runtime' if run_command else 'build'}`",
        f"- Effective link mode: `{link_mode}`",
        f"- Build gate: `{'PASS' if build_all_pass else 'FAIL'}`",
        f"- Runtime gate: `{runtime_text}`",
        f"- Run command template: `{run_command}`" if run_command else "- Run command template: _(not provided; build-only)_",
        "",
        "| Workload | State | Build | ELF class | Machine | Static | SHA-256 | Runtime | Exit | Semantics |",
        "|---|---|---|---|---|---:|---|---|---:|---|",
    ]
    for result in results:
        artifact = result["artifact"]
        runtime = result["runtime"] or {}
        sha = artifact.get("sha256") or "N/A"
        lines.append(
            "| `{name}` | `{state}` | {build} | `{elf_class}` | `{machine}` | {static} | `{sha}` | {runtime} | {exit_code} | {semantics} |".format(
                name=result["name"],
                state=result["status"],
                build=result["build_status"],
                elf_class=artifact.get("elf_class") or "N/A",
                machine=artifact.get("machine") or "N/A",
                static=artifact.get("static") if artifact.get("static") is not None else "N/A",
                sha=sha,
                runtime=result["runtime_status"],
                exit_code=runtime.get("exit_code") if runtime.get("exit_code") is not None else "N/A",
                semantics="PASS" if runtime.get("semantic_success") else ("N/A" if not runtime else "FAIL"),
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_json(
    path: Path,
    results: list[dict[str, Any]],
    *,
    target: str,
    cc: Path,
    readelf: Path,
    run_command: str | None,
    link_mode: str = "default",
) -> bool:
    build_all_pass = all(result["build_pass"] for result in results)
    runtime_all_pass = all(result["runtime_pass"] for result in results) if run_command else None
    requested_gate_pass = runtime_all_pass if run_command else build_all_pass
    payload = {
        "schema_version": 2,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "target": target,
        "link_mode": link_mode,
        "requested_gate": "runtime" if run_command else "build",
        "evidence_level": "runtime-pass" if runtime_all_pass else ("runtime-attempt" if run_command else "build-only"),
        "run_command_template": run_command,
        "tools": {
            "compiler": _tool_identity(cc),
            "readelf": _tool_identity(readelf),
        },
        "build_all_pass": build_all_pass,
        "runtime_all_pass": runtime_all_pass,
        "requested_gate_pass": bool(requested_gate_pass),
        # `all_pass` is deliberately runtime-only.  Build-only callers use
        # `requested_gate_pass`/the process exit code and cannot accidentally
        # promote a successful compile into a successful benchmark run.
        "all_pass": runtime_all_pass is True,
        "results": results,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return bool(requested_gate_pass)


def _not_inspected(exe: Path) -> dict[str, Any]:
    return {
        "status": "FAIL",
        "path": str(exe.resolve(strict=False)),
        "sha256": None,
        "errors": ["artifact not inspected because compilation failed"],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build and optionally run CoreMark + Dhrystone with fail-closed ELF and semantic evidence."
    )
    parser.add_argument("--cc", default=None, help="Compiler path (or set CC)")
    parser.add_argument("--readelf", default=None, help="llvm-readelf/readelf path (or set READELF)")
    parser.add_argument("--target", required=True, help="Target triple (required)")
    parser.add_argument("--sysroot", default=None, help="Optional sysroot path")
    parser.add_argument("--opt", default="-O2", help="Optimization flag (default: -O2)")
    parser.add_argument("--cflag", action="append", default=[], help="Extra C flag (repeatable)")
    parser.add_argument("--coremark-port", choices=["posix", "simple"], default="posix")
    parser.add_argument(
        "--coremark-iterations",
        type=int,
        default=0,
        help="CoreMark iteration count; 0 uses upstream auto-calibration (default)",
    )
    parser.add_argument("--dhrystone-runs", type=int, default=1000)
    parser.add_argument(
        "--link-mode",
        choices=["auto", "default", "musl-static"],
        default="auto",
        help="Link mode; auto selects musl-static for Linx targets with a sysroot",
    )
    parser.add_argument(
        "--expect-static",
        choices=["auto", "yes", "no"],
        default="auto",
        help="Fail unless staticity matches; auto requires static for musl-static mode",
    )
    parser.add_argument("--runtime-lib", default=None, help="Optional builtins archive for musl-static mode")
    parser.add_argument("--image-base", default=None, help="Optional image base passed to the linker")
    parser.add_argument(
        "--run-command",
        default=None,
        help="Optional execution wrapper. Use {exe}; otherwise the executable is appended.",
    )
    parser.add_argument("--timeout", type=float, default=120.0, help="Per-workload execution timeout seconds")
    parser.add_argument("--out-dir", default=str(GENERATED_DIR / "benchmarks"), help="Output directory")
    parser.add_argument(
        "--publish-elf-dir",
        default=str(DEFAULT_PUBLISH_ELF_DIR),
        help="Canonical ELF publish directory (use none to disable)",
    )
    parser.add_argument("--json-out", default=None, help="Machine-readable evidence path")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    _validate_run_parameters(
        coremark_iterations=args.coremark_iterations,
        dhrystone_runs=args.dhrystone_runs,
        timeout=args.timeout,
    )
    cc = _resolve_cc(args.cc)
    readelf = _resolve_readelf(args.readelf, cc)
    expected_machine, expected_class, expected_data_encoding = _target_contract(args.target)
    link_mode = _effective_link_mode(args.link_mode, target=args.target, sysroot=args.sysroot)
    if args.expect_static == "yes":
        expected_static: bool | None = True
    elif args.expect_static == "no":
        expected_static = False
    else:
        expected_static = True if link_mode == "musl-static" else None

    out_dir = Path(os.path.expanduser(args.out_dir)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    logs_dir = out_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    publish_dir = None
    if str(args.publish_elf_dir).lower() not in ("", "none", "null"):
        publish_dir = Path(os.path.expanduser(args.publish_elf_dir)).resolve()

    coremark_exe, coremark_build = _build_coremark(
        cc=cc,
        target=args.target,
        sysroot=args.sysroot,
        opt=args.opt,
        extra_cflags=args.cflag,
        out_dir=out_dir,
        logs_dir=logs_dir,
        port=args.coremark_port,
        iterations=args.coremark_iterations,
        link_mode=link_mode,
        runtime_lib=args.runtime_lib,
        image_base=args.image_base,
        verbose=args.verbose,
    )
    dhrystone_exe, dhrystone_build = _build_dhrystone(
        cc=cc,
        target=args.target,
        sysroot=args.sysroot,
        opt=args.opt,
        extra_cflags=args.cflag,
        out_dir=out_dir,
        logs_dir=logs_dir,
        runs=args.dhrystone_runs,
        link_mode=link_mode,
        runtime_lib=args.runtime_lib,
        image_base=args.image_base,
        verbose=args.verbose,
    )

    raw_results: list[tuple[str, Path, dict[str, Any]]] = [
        ("coremark", coremark_exe, coremark_build),
        ("dhrystone", dhrystone_exe, dhrystone_build),
    ]
    results: list[dict[str, Any]] = []
    published: list[Path] = []
    for name, exe, build in raw_results:
        artifact = (
            _inspect_elf(
                exe,
                readelf=readelf,
                expected_machine=expected_machine,
                expected_class=expected_class,
                expected_static=expected_static,
                logs_dir=logs_dir,
                name=name,
                expected_data_encoding=expected_data_encoding,
            )
            if build["status"] == "PASS"
            else _not_inspected(exe)
        )
        runtime = None
        if args.run_command and build["status"] == "PASS" and artifact["status"] == "PASS":
            runtime = _run_with_wrapper(
                name=name,
                exe=exe,
                run_command=args.run_command,
                timeout=args.timeout,
                out_dir=logs_dir,
                verbose=args.verbose,
                expected_artifact_sha256=artifact["sha256"],
            )
        result = _compose_result(name=name, build=build, artifact=artifact, runtime=runtime)
        if result["build_pass"]:
            published_path = _publish_executable(exe, f"{name}.elf", publish_dir)
            if published_path:
                result["published_executable"] = str(published_path)
                result["published_sha256"] = _sha256(published_path)
                published.append(published_path)
        results.append(result)

    json_out = Path(os.path.expanduser(args.json_out)).resolve() if args.json_out else out_dir / "result.json"
    json_out.parent.mkdir(parents=True, exist_ok=True)
    ok = _write_json(
        json_out,
        results,
        target=args.target,
        cc=cc,
        readelf=readelf,
        run_command=args.run_command,
        link_mode=link_mode,
    )
    payload = json.loads(json_out.read_text(encoding="utf-8"))
    report = out_dir / "report.md"
    _write_report(
        report,
        results,
        target=args.target,
        cc=cc,
        readelf=readelf,
        run_command=args.run_command,
        link_mode=link_mode,
        build_all_pass=payload["build_all_pass"],
        runtime_all_pass=payload["runtime_all_pass"],
    )
    print(f"ok: wrote {report}")
    print(f"ok: wrote {json_out}")
    for path in published:
        print(f"ok: published {path}")
    if not ok:
        print(f"error: requested {payload['requested_gate']} gate failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
