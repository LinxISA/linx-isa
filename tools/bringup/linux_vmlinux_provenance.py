#!/usr/bin/env python3
"""Collect and verify deterministic provenance for a Linx Linux vmlinux build."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "linx-linux-vmlinux-build-provenance-v1"
HEX_CHARS = frozenset("0123456789abcdef")


class ProvenanceError(RuntimeError):
    """Raised when build provenance cannot be collected or verified."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _absolute(path: str | Path) -> Path:
    return Path(path).expanduser().absolute()


def _require_regular(path: Path, label: str, *, executable: bool = False) -> Path:
    path = _absolute(path)
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise ProvenanceError(f"missing {label}: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ProvenanceError(f"{label} must be a non-symlink regular file: {path}")
    if metadata.st_size <= 0:
        raise ProvenanceError(f"{label} must be nonempty: {path}")
    if executable and not os.access(path, os.X_OK):
        raise ProvenanceError(f"{label} is not executable: {path}")
    return path


def _file_identity(path: Path, label: str) -> dict[str, Any]:
    path = _require_regular(path, label)
    return {
        "path": str(path),
        "sha256": _sha256_file(path),
        "size_bytes": path.stat().st_size,
    }


def _tool_identity(path: Path, label: str) -> dict[str, Any]:
    requested = _absolute(path)
    if not requested.exists() or not os.access(requested, os.X_OK):
        raise ProvenanceError(f"missing or non-executable {label}: {requested}")
    resolved = requested.resolve(strict=True)
    _require_regular(resolved, label, executable=True)
    try:
        proc = subprocess.run(
            [str(requested), "--version"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProvenanceError(f"cannot identify {label} {requested}: {exc}") from exc
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if proc.returncode != 0 or not lines:
        raise ProvenanceError(f"{label} --version did not succeed with output: {requested}")
    return {
        "path": str(requested),
        "resolved_path": str(resolved),
        "version": lines[0],
        "sha256": _sha256_file(resolved),
        "size_bytes": resolved.stat().st_size,
    }


def _git(repo: Path, *args: str, text: bool = False) -> bytes | str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
        timeout=30,
    )
    if proc.returncode != 0:
        stderr = proc.stderr if text else proc.stderr.decode("utf-8", errors="replace")
        raise ProvenanceError(f"git {' '.join(args)} failed for {repo}: {stderr.strip()}")
    return proc.stdout


def _untracked_identity(repo: Path, relative: str) -> dict[str, Any]:
    if os.path.isabs(relative) or os.path.normpath(relative) != relative:
        raise ProvenanceError(f"noncanonical untracked path: {relative}")
    path = repo / relative
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise ProvenanceError(f"untracked path disappeared: {relative}") from exc
    mode = f"{stat.S_IMODE(metadata.st_mode):04o}"
    if stat.S_ISREG(metadata.st_mode):
        return {
            "path": relative,
            "kind": "file",
            "mode": mode,
            "bytes": metadata.st_size,
            "sha256": _sha256_file(path),
        }
    if stat.S_ISLNK(metadata.st_mode):
        target = os.readlink(path)
        return {
            "path": relative,
            "kind": "symlink",
            "mode": mode,
            "target_sha256": _sha256_bytes(os.fsencode(target)),
        }
    raise ProvenanceError(f"unsupported untracked path kind: {relative}")


def _source_identity(repo: Path) -> dict[str, Any]:
    repo = _absolute(repo)
    if not repo.is_dir():
        raise ProvenanceError(f"missing Linux source repository: {repo}")
    head = str(_git(repo, "rev-parse", "HEAD", text=True)).strip()
    raw_status = bytes(
        _git(
            repo,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--ignore-submodules=none",
        )
    )
    tokens = raw_status.split(b"\0")
    rows: list[dict[str, str]] = []
    untracked: list[dict[str, Any]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token:
            continue
        if len(token) < 4 or token[2:3] != b" ":
            raise ProvenanceError(f"invalid NUL-safe git status record in {repo}")
        code = token[:2].decode("ascii", errors="strict")
        relative = os.fsdecode(token[3:])
        row = {"status": code, "path": relative}
        if "R" in code or "C" in code:
            if index >= len(tokens) or not tokens[index]:
                raise ProvenanceError(f"truncated rename/copy status record in {repo}")
            row["original_path"] = os.fsdecode(tokens[index])
            index += 1
        rows.append(row)
        if code == "??":
            untracked.append(_untracked_identity(repo, relative))
    rows.sort(key=lambda row: (row["path"], row["status"], row.get("original_path", "")))
    untracked.sort(key=lambda row: row["path"])
    unstaged = bytes(
        _git(repo, "diff", "--binary", "--no-ext-diff", "--ignore-submodules=none", "--")
    )
    staged = bytes(
        _git(
            repo,
            "diff",
            "--cached",
            "--binary",
            "--no-ext-diff",
            "--ignore-submodules=none",
            "--",
        )
    )
    return {
        "path": str(repo),
        "head": head,
        "clean": not rows,
        "dirty_paths": rows,
        "staged_diff": {"sha256": _sha256_bytes(staged), "bytes": len(staged)},
        "unstaged_diff": {"sha256": _sha256_bytes(unstaged), "bytes": len(unstaged)},
        "untracked": untracked,
    }


def _snapshot(
    linux_root: Path,
    clang: Path,
    ld_lld: Path,
    gmake: Path,
    hostcc: Path,
    hostcxx: Path,
    script: Path,
) -> dict[str, Any]:
    return {
        "source": _source_identity(linux_root),
        "tools": {
            "clang": _tool_identity(clang, "clang"),
            "ld_lld": _tool_identity(ld_lld, "ld.lld"),
            "gmake": _tool_identity(gmake, "gmake"),
            "hostcc": _tool_identity(hostcc, "HOSTCC"),
            "hostcxx": _tool_identity(hostcxx, "HOSTCXX"),
        },
        "script": _file_identity(script, "build script"),
        "provenance_helper": _file_identity(
            Path(__file__).resolve(), "provenance helper"
        ),
    }


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceError(f"cannot read {label} {path}: {exc}") from exc


def _read_nul_argv(path: Path) -> list[str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProvenanceError(f"cannot read command argv {path}: {exc}") from exc
    if not raw or not raw.endswith(b"\0"):
        raise ProvenanceError(f"command argv must be nonempty and NUL terminated: {path}")
    return [os.fsdecode(item) for item in raw[:-1].split(b"\0")]


def _assert_distinct(paths: dict[str, Path]) -> None:
    resolved: dict[Path, str] = {}
    for label, path in paths.items():
        candidate = _absolute(path).resolve(strict=False)
        prior = resolved.get(candidate)
        if prior is not None:
            raise ProvenanceError(f"{label} aliases {prior}: {candidate}")
        resolved[candidate] = label


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path = _absolute(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def _require_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ProvenanceError(f"{label} keys do not match schema")
    return value


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX_CHARS


def _validate_file_record(record: Any, label: str, *, tool: bool = False) -> dict[str, Any]:
    keys = {"path", "sha256", "size_bytes"}
    if tool:
        keys |= {"resolved_path", "version"}
    row = _require_keys(record, keys, label)
    if not isinstance(row["path"], str) or not row["path"].startswith("/"):
        raise ProvenanceError(f"{label} path is not absolute")
    if not _valid_sha(row["sha256"]) or not isinstance(row["size_bytes"], int) or row["size_bytes"] <= 0:
        raise ProvenanceError(f"{label} identity is malformed")
    if tool and (
        not isinstance(row["resolved_path"], str)
        or not row["resolved_path"].startswith("/")
        or not isinstance(row["version"], str)
        or not row["version"]
    ):
        raise ProvenanceError(f"{label} tool identity is malformed")
    return row


def collect(args: argparse.Namespace) -> dict[str, Any]:
    linux_root = _absolute(args.linux_root)
    clang = _absolute(args.clang)
    ld_lld = _absolute(args.ld_lld)
    gmake = _absolute(args.gmake)
    hostcc = _absolute(args.hostcc)
    hostcxx = _absolute(args.hostcxx)
    config = _absolute(args.config)
    vmlinux = _absolute(args.vmlinux)
    script = _absolute(args.script)
    output = _absolute(args.out)
    out_dir = _absolute(args.out_dir)
    fresh_marker = out_dir / ".linx_linux_vmlinux_fresh_generation"
    _assert_distinct(
        {
            "provenance output": output,
            "config": config,
            "vmlinux": vmlinux,
            "script": script,
            "clang": clang,
            "ld.lld": ld_lld,
            "gmake": gmake,
            "HOSTCC": hostcc,
            "HOSTCXX": hostcxx,
            "fresh generation marker": fresh_marker,
        }
    )
    before = _load_json(_absolute(args.pre_state), "pre-build state")
    after = _snapshot(linux_root, clang, ld_lld, gmake, hostcc, hostcxx, script)
    if before != after:
        raise ProvenanceError("Linux source, toolchain, or build script changed during build")
    config_before = _load_json(_absolute(args.pre_config), "pre-target kernel config")
    config_after = _file_identity(config, "kernel config")
    if config_before != config_after:
        raise ProvenanceError("kernel config changed while building the target")
    source = dict(after["source"])
    source["pre_post_equal"] = True
    commands = [_read_nul_argv(_absolute(path)) for path in args.command_file]
    if not commands:
        raise ProvenanceError("at least one executed build command is required")
    fresh_generation: dict[str, Any] | None
    if args.mode == "fresh":
        fresh_generation = _file_identity(fresh_marker, "fresh generation marker")
        recorded_fresh_generation = _load_json(
            _absolute(args.pre_fresh_marker), "pre-build fresh generation marker"
        )
        if fresh_generation != recorded_fresh_generation:
            raise ProvenanceError("fresh generation marker changed during build")
    else:
        if fresh_marker.exists() or fresh_marker.is_symlink():
            raise ProvenanceError("incremental build must not retain a fresh generation marker")
        fresh_generation = None
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "claim": "vmlinux_build_output_provenance",
        "constraints": ["trusted_parent_manifest_must_bind_report_sha256"],
        "ok": True,
        "source": source,
        "tools": after["tools"],
        "inputs": {
            "config": config_after,
            "script": after["script"],
            "provenance_helper": after["provenance_helper"],
            "fresh_generation": fresh_generation,
        },
        "build": {
            "mode": args.mode,
            "target": args.target,
            "arch": args.arch,
            "defconfig_target": args.defconfig_target,
            "refresh_defconfig": args.refresh_defconfig,
            "jobs": args.jobs,
            "kallsyms_extra_pass": args.kallsyms_extra_pass,
            "out_dir": str(out_dir),
            "commands": commands,
        },
        "output": _file_identity(vmlinux, "vmlinux"),
    }
    _atomic_write_json(output, payload)
    try:
        verify_payload(output)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return payload


def verify_payload(
    path: Path,
    *,
    require_clean_source: bool = False,
    require_fresh: bool = False,
    require_linux_head: str = "",
    require_clang_sha: str = "",
    require_ld_lld_sha: str = "",
) -> dict[str, Any]:
    path = _absolute(path)
    _require_regular(path, "provenance")
    payload = _load_json(path, "provenance")
    top = _require_keys(
        payload,
        {"schema_version", "generated_at_utc", "claim", "constraints", "ok", "source", "tools", "inputs", "build", "output"},
        "provenance",
    )
    if top["schema_version"] != SCHEMA_VERSION or top["claim"] != "vmlinux_build_output_provenance" or top["ok"] is not True:
        raise ProvenanceError("unsupported or non-passing provenance claim")
    if not isinstance(top["generated_at_utc"], str) or not top["generated_at_utc"].endswith("Z"):
        raise ProvenanceError("provenance timestamp is malformed")
    if top["constraints"] != ["trusted_parent_manifest_must_bind_report_sha256"]:
        raise ProvenanceError("provenance tamper-resistance constraint is missing")
    source = _require_keys(
        top["source"],
        {"path", "head", "clean", "dirty_paths", "staged_diff", "unstaged_diff", "untracked", "pre_post_equal"},
        "source",
    )
    tools = _require_keys(
        top["tools"], {"clang", "ld_lld", "gmake", "hostcc", "hostcxx"}, "tools"
    )
    inputs = _require_keys(
        top["inputs"],
        {"config", "script", "provenance_helper", "fresh_generation"},
        "inputs",
    )
    build = _require_keys(
        top["build"],
        {"mode", "target", "arch", "defconfig_target", "refresh_defconfig", "jobs", "kallsyms_extra_pass", "out_dir", "commands"},
        "build",
    )
    if source["pre_post_equal"] is not True:
        raise ProvenanceError("source pre/post equality is not proven")
    if (
        not isinstance(source["path"], str)
        or not source["path"].startswith("/")
        or not isinstance(source["head"], str)
        or len(source["head"]) not in {40, 64}
        or not set(source["head"]) <= HEX_CHARS
        or not isinstance(source["clean"], bool)
        or not isinstance(source["dirty_paths"], list)
        or not isinstance(source["untracked"], list)
    ):
        raise ProvenanceError("source identity is malformed")
    for diff_name in ("staged_diff", "unstaged_diff"):
        diff = _require_keys(source[diff_name], {"sha256", "bytes"}, diff_name)
        if not _valid_sha(diff["sha256"]) or not isinstance(diff["bytes"], int) or diff["bytes"] < 0:
            raise ProvenanceError(f"{diff_name} identity is malformed")
    live_source = _source_identity(Path(source["path"]))
    expected_source = {key: value for key, value in source.items() if key != "pre_post_equal"}
    if live_source != expected_source:
        raise ProvenanceError("current Linux source identity differs from provenance")
    for name, label in (
        ("clang", "clang"),
        ("ld_lld", "ld.lld"),
        ("gmake", "gmake"),
        ("hostcc", "HOSTCC"),
        ("hostcxx", "HOSTCXX"),
    ):
        recorded = _validate_file_record(tools[name], label, tool=True)
        if _tool_identity(Path(recorded["path"]), label) != recorded:
            raise ProvenanceError(f"current {label} identity differs from provenance")
    for name, label in (
        ("config", "kernel config"),
        ("script", "build script"),
        ("provenance_helper", "provenance helper"),
    ):
        recorded = _validate_file_record(inputs[name], label)
        if _file_identity(Path(recorded["path"]), label) != recorded:
            raise ProvenanceError(f"current {label} identity differs from provenance")
    output = _validate_file_record(top["output"], "vmlinux")
    if _file_identity(Path(output["path"]), "vmlinux") != output:
        raise ProvenanceError("current vmlinux identity differs from provenance")
    if build["mode"] not in {"fresh", "incremental"} or build["target"] != "vmlinux":
        raise ProvenanceError("unsupported build mode or target")
    if (
        build["arch"] != "linx"
        or not isinstance(build["defconfig_target"], str)
        or not build["defconfig_target"]
        or not isinstance(build["refresh_defconfig"], bool)
        or not isinstance(build["jobs"], int)
        or build["jobs"] <= 0
        or not isinstance(build["kallsyms_extra_pass"], str)
        or not isinstance(build["out_dir"], str)
        or not build["out_dir"].startswith("/")
    ):
        raise ProvenanceError("build contract is malformed")
    if not isinstance(build["commands"], list) or not build["commands"] or not all(
        isinstance(command, list) and command and all(isinstance(arg, str) for arg in command)
        for command in build["commands"]
    ):
        raise ProvenanceError("build commands are malformed")
    if len(build["commands"]) not in {1, 2}:
        raise ProvenanceError("build command count is unsupported")
    if build["refresh_defconfig"] and len(build["commands"]) != 2:
        raise ProvenanceError("refreshed defconfig is missing its command evidence")
    out_dir = _absolute(build["out_dir"])
    if Path(inputs["config"]["path"]) != out_dir / ".config":
        raise ProvenanceError("kernel config path is outside the recorded output directory")
    if Path(output["path"]) != out_dir / "vmlinux":
        raise ProvenanceError("vmlinux path is outside the recorded output directory")
    fresh_marker_path = out_dir / ".linx_linux_vmlinux_fresh_generation"
    fresh_generation = inputs["fresh_generation"]
    if build["mode"] == "fresh":
        marker = _validate_file_record(fresh_generation, "fresh generation marker")
        if Path(marker["path"]) != fresh_marker_path:
            raise ProvenanceError("fresh generation marker path does not match output directory")
        if _file_identity(fresh_marker_path, "fresh generation marker") != marker:
            raise ProvenanceError("fresh generation marker identity differs from provenance")
    else:
        if fresh_generation is not None:
            raise ProvenanceError("incremental provenance must not claim a fresh generation")
        if fresh_marker_path.exists() or fresh_marker_path.is_symlink():
            raise ProvenanceError("incremental output retains a fresh generation marker")

    common_command = [
        tools["gmake"]["path"],
        "-C",
        source["path"],
        f"ARCH={build['arch']}",
        f"LLVM={Path(tools['clang']['path']).parent}/",
        (
            f"CC={tools['clang']['path']} "
            "--target=linx64-unknown-linux-gnu -fintegrated-as"
        ),
        f"HOSTCC={tools['hostcc']['path']}",
        f"HOSTCXX={tools['hostcxx']['path']}",
        f"KALLSYMS_EXTRA_PASS={build['kallsyms_extra_pass']}",
        f"O={out_dir}",
        f"-j{build['jobs']}",
    ]

    def require_exact_command(command: list[str], targets: list[str], label: str) -> None:
        if len(command) < 2 or command[0] != "env" or not command[1].startswith("PATH="):
            raise ProvenanceError(f"{label} command environment is malformed")
        expected = common_command + targets
        if command[2:] != expected:
            raise ProvenanceError(f"{label} command metadata does not match provenance")

    if build["mode"] == "fresh" and len(build["commands"]) != 2:
        raise ProvenanceError("fresh build is missing configuration command evidence")
    if len(build["commands"]) == 2:
        require_exact_command(
            build["commands"][0],
            [build["defconfig_target"], "olddefconfig"],
            "configuration",
        )
    require_exact_command(build["commands"][-1], [build["target"]], "target")
    if require_clean_source and source["clean"] is not True:
        raise ProvenanceError("promotion requires a clean Linux source")
    if require_fresh and build["mode"] != "fresh":
        raise ProvenanceError("promotion requires a fresh Linux build")
    if require_linux_head and source["head"] != require_linux_head:
        raise ProvenanceError("Linux HEAD does not match the required SHA")
    if require_clang_sha and tools["clang"]["sha256"] != require_clang_sha:
        raise ProvenanceError("clang SHA-256 does not match the required value")
    if require_ld_lld_sha and tools["ld_lld"]["sha256"] != require_ld_lld_sha:
        raise ProvenanceError("ld.lld SHA-256 does not match the required value")
    return payload


def _write_snapshot(path: Path, payload: dict[str, Any]) -> None:
    _atomic_write_json(path, payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot = subparsers.add_parser("snapshot")
    snapshot.add_argument("--linux-root", required=True)
    snapshot.add_argument("--clang", required=True)
    snapshot.add_argument("--ld-lld", required=True)
    snapshot.add_argument("--gmake", required=True)
    snapshot.add_argument("--hostcc", required=True)
    snapshot.add_argument("--hostcxx", required=True)
    snapshot.add_argument("--script", required=True)
    snapshot.add_argument("--out", required=True)

    file_snapshot = subparsers.add_parser("file-snapshot")
    file_snapshot.add_argument("--path", required=True)
    file_snapshot.add_argument("--label", required=True)
    file_snapshot.add_argument("--out", required=True)

    collect_parser = subparsers.add_parser("collect")
    for option in (
        "linux-root",
        "clang",
        "ld-lld",
        "gmake",
        "hostcc",
        "hostcxx",
        "config",
        "vmlinux",
        "script",
        "pre-state",
        "pre-config",
        "out-dir",
        "out",
    ):
        collect_parser.add_argument(f"--{option}", required=True)
    collect_parser.add_argument("--mode", choices=("fresh", "incremental"), required=True)
    collect_parser.add_argument("--target", required=True)
    collect_parser.add_argument("--arch", required=True)
    collect_parser.add_argument("--defconfig-target", required=True)
    collect_parser.add_argument("--refresh-defconfig", action="store_true")
    collect_parser.add_argument("--jobs", type=int, required=True)
    collect_parser.add_argument("--kallsyms-extra-pass", required=True)
    collect_parser.add_argument("--command-file", action="append", default=[], required=True)
    collect_parser.add_argument("--pre-fresh-marker", default="")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--provenance", required=True)
    verify_parser.add_argument("--require-clean-source", action="store_true")
    verify_parser.add_argument("--require-fresh", action="store_true")
    verify_parser.add_argument("--require-linux-head", default="")
    verify_parser.add_argument("--require-clang-sha", default="")
    verify_parser.add_argument("--require-ld-lld-sha", default="")
    return parser


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            _write_snapshot(
                _absolute(args.out),
                _snapshot(
                    _absolute(args.linux_root),
                    _absolute(args.clang),
                    _absolute(args.ld_lld),
                    _absolute(args.gmake),
                    _absolute(args.hostcc),
                    _absolute(args.hostcxx),
                    _absolute(args.script),
                ),
            )
            return 0
        if args.command == "file-snapshot":
            _write_snapshot(
                _absolute(args.out),
                _file_identity(_absolute(args.path), args.label),
            )
            return 0
        if args.command == "collect":
            collect(args)
            print(f"ok: wrote and verified vmlinux provenance {args.out}")
            return 0
        verify_payload(
            _absolute(args.provenance),
            require_clean_source=args.require_clean_source,
            require_fresh=args.require_fresh,
            require_linux_head=args.require_linux_head,
            require_clang_sha=args.require_clang_sha,
            require_ld_lld_sha=args.require_ld_lld_sha,
        )
        print("ok: vmlinux provenance matches current evidence")
        return 0
    except (ProvenanceError, OSError, subprocess.SubprocessError, KeyError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
