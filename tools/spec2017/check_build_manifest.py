#!/usr/bin/env python3
"""Attest and verify the Linx SPEC Stage-A build manifest.

This tool verifies build artifacts and their current workspace provenance.  It
does not inspect, copy, or make claims about licensed SPEC input data.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "linx-spec-build-attestation-v1"
MANIFEST_SCHEMA_VERSION = "linx-spec-build-manifest-v1"
EXPECTED_EXECUTABLES: dict[str, list[str]] = {
    "500.perlbench_r": ["perlbench_r_base.mytest-m64"],
    "502.gcc_r": ["cpugcc_r_base.mytest-m64"],
    "505.mcf_r": ["mcf_r_base.mytest-m64"],
    "520.omnetpp_r": ["omnetpp_r_base.mytest-m64"],
    "523.xalancbmk_r": ["cpuxalan_r_base.mytest-m64"],
    "525.x264_r": [
        "x264_r_base.mytest-m64",
        "ldecod_r_base.mytest-m64",
        "imagevalidate_525_base.mytest-m64",
    ],
    "531.deepsjeng_r": ["deepsjeng_r_base.mytest-m64"],
    "541.leela_r": ["leela_r_base.mytest-m64"],
    "557.xz_r": ["xz_r_base.mytest-m64"],
    "999.specrand_ir": ["specrand_ir_base.mytest-m64"],
}


class EvidenceError(RuntimeError):
    """Raised when evidence is incomplete, stale, or internally inconsistent."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_path(root: Path, raw: object, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise EvidenceError(f"missing {label} path")
    path = Path(os.path.expanduser(raw))
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def _resolve_executable_path(root: Path, raw: object, label: str) -> Path:
    """Make a tool path absolute without dereferencing argv[0]-sensitive symlinks."""
    if not isinstance(raw, str) or not raw.strip():
        raise EvidenceError(f"missing {label} path")
    path = Path(os.path.expanduser(raw))
    if not path.is_absolute():
        path = root / path
    return path.absolute()


def _canonical_lexical_path(root: Path, raw: object, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise EvidenceError(f"missing {label} path")
    expanded = os.path.expanduser(raw)
    if not os.path.isabs(expanded):
        raise EvidenceError(f"{label} must use an absolute canonical lexical path")
    if os.path.normpath(expanded) != expanded:
        raise EvidenceError(f"{label} is not a canonical lexical path: {raw}")
    return Path(expanded)


def _require_no_symlink_components(base: Path, path: Path, label: str) -> None:
    try:
        relative = path.relative_to(base)
    except ValueError as exc:
        raise EvidenceError(f"{label} escapes canonical root: {path}") from exc
    current = base
    if current.is_symlink():
        raise EvidenceError(f"{label} root is a symlink: {current}")
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise EvidenceError(f"{label} symlink component is forbidden: {current}")


def _git_output(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise EvidenceError(f"git {' '.join(args)} failed for {repo}: {proc.stderr.strip()}")
    return proc.stdout


def _git_bytes(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        timeout=30,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise EvidenceError(f"git {' '.join(args)} failed for {repo}: {stderr}")
    return proc.stdout


def _blob_identity(data: bytes) -> dict[str, object]:
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _untracked_identity(repo: Path, relative: str) -> dict[str, object]:
    if os.path.isabs(relative) or os.path.normpath(relative) != relative:
        raise EvidenceError(f"noncanonical untracked path from git status: {relative}")
    path = repo / relative
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError(f"untracked path disappeared during attestation: {relative}") from exc
    mode = stat.S_IMODE(metadata.st_mode)
    if stat.S_ISREG(metadata.st_mode):
        return {
            "path": relative,
            "kind": "file",
            "mode": f"{mode:04o}",
            "bytes": metadata.st_size,
            "sha256": _sha256(path),
        }
    if stat.S_ISLNK(metadata.st_mode):
        target = os.readlink(path)
        return {
            "path": relative,
            "kind": "symlink",
            "mode": f"{mode:04o}",
            "target_sha256": hashlib.sha256(os.fsencode(target)).hexdigest(),
        }
    raise EvidenceError(f"unsupported untracked path kind: {relative}")


def _git_identity(repo: Path) -> dict[str, object]:
    if not repo.is_dir():
        raise EvidenceError(f"missing repository: {repo}")
    head = _git_output(repo, "rev-parse", "HEAD").strip()
    status = _git_bytes(
        repo,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--ignore-submodules=none",
    )
    tokens = status.split(b"\0")
    rows: list[dict[str, str]] = []
    untracked: list[dict[str, object]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token:
            continue
        if len(token) < 4 or token[2:3] != b" ":
            raise EvidenceError(f"invalid NUL-safe git status record in {repo}")
        status_code = token[:2].decode("ascii", errors="strict")
        relative = os.fsdecode(token[3:])
        row = {"status": status_code, "path": relative}
        if "R" in status_code or "C" in status_code:
            if index >= len(tokens) or not tokens[index]:
                raise EvidenceError(f"truncated rename/copy git status record in {repo}")
            row["original_path"] = os.fsdecode(tokens[index])
            index += 1
        rows.append(row)
        if status_code == "??":
            untracked.append(_untracked_identity(repo, relative))
    unstaged = _git_bytes(
        repo, "diff", "--binary", "--no-ext-diff", "--ignore-submodules=none", "--"
    )
    staged = _git_bytes(
        repo,
        "diff",
        "--cached",
        "--binary",
        "--no-ext-diff",
        "--ignore-submodules=none",
        "--",
    )
    return {
        "path": str(repo),
        "head": head,
        "dirty_paths": rows,
        "unstaged_diff": _blob_identity(unstaged),
        "staged_diff": _blob_identity(staged),
        "untracked": untracked,
    }


def _tool_identity(path: Path, label: str) -> dict[str, str]:
    if not path.is_file() or not os.access(path, os.X_OK):
        raise EvidenceError(f"missing or non-executable {label}: {path}")
    proc = subprocess.run(
        [str(path), "--version"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise EvidenceError(f"{label} --version failed: {path}")
    identity_lines = [
        line.strip()
        for line in (proc.stdout + "\n" + proc.stderr).splitlines()
        if line.strip()
    ]
    identity = " | ".join(identity_lines[:2])
    if not identity:
        raise EvidenceError(f"{label} --version returned no identity: {path}")
    return {"path": str(path), "identity": identity, "sha256": _sha256(path)}


def _directory_identity(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_dir():
        raise EvidenceError(f"missing sysroot: {path}")
    digest = hashlib.sha256()
    digest.update(b"linx-directory-identity-v1\0")
    root_mode = stat.S_IMODE(path.lstat().st_mode)
    digest.update(b"R\0" + f"{root_mode:04o}".encode() + b"\0")
    file_count = 0
    symlink_count = 0
    entries: list[Path] = []
    for current_raw, dirs, files in os.walk(path, followlinks=False):
        current = Path(current_raw)
        kept_dirs: list[str] = []
        for name in dirs:
            entry = current / name
            entries.append(entry)
            if not entry.is_symlink():
                kept_dirs.append(name)
        dirs[:] = kept_dirs
        entries.extend(current / name for name in files)
    symlink_referents: list[dict[str, object]] = []
    for entry in sorted(entries, key=lambda item: os.fsencode(item.relative_to(path).as_posix())):
        relative = entry.relative_to(path).as_posix()
        if entry.is_symlink():
            symlink_count += 1
            link_mode = stat.S_IMODE(entry.lstat().st_mode)
            target = os.readlink(entry)
            candidate = Path(target) if os.path.isabs(target) else entry.parent / target
            candidate = Path(os.path.normpath(str(candidate)))
            try:
                candidate_relative = candidate.relative_to(path)
            except ValueError as exc:
                raise EvidenceError(f"sysroot symlink escapes sysroot: {entry}") from exc
            try:
                candidate.lstat()
            except FileNotFoundError as exc:
                raise EvidenceError(f"broken sysroot symlink: {entry}") from exc
            _require_no_symlink_components(path, candidate, "sysroot symlink target")
            referent_mode = candidate.lstat().st_mode
            if stat.S_ISDIR(referent_mode):
                raise EvidenceError(f"sysroot directory symlink is unsupported: {entry}")
            if not stat.S_ISREG(referent_mode):
                raise EvidenceError(f"unsupported sysroot symlink referent: {entry}")
            referent_sha = _sha256(candidate)
            row = {
                "path": relative,
                "mode": f"{link_mode:04o}",
                "target_sha256": hashlib.sha256(os.fsencode(target)).hexdigest(),
                "referent": candidate_relative.as_posix(),
                "kind": "file",
                "referent_sha256": referent_sha,
            }
            symlink_referents.append(row)
            digest.update(
                b"L\0"
                + os.fsencode(relative)
                + b"\0"
                + os.fsencode(target)
                + b"\0"
                + f"{link_mode:04o}".encode()
                + b"\0F\0"
                + os.fsencode(candidate_relative.as_posix())
                + b"\0"
                + referent_sha.encode()
                + b"\0"
            )
        elif entry.is_file() and not entry.is_symlink():
            file_count += 1
            digest.update(
                b"F\0"
                + os.fsencode(relative)
                + b"\0"
                + f"{entry.stat().st_mode & 0o777:o}".encode()
                + b"\0"
                + _sha256(entry).encode()
                + b"\0"
            )
        elif entry.is_dir():
            digest.update(
                b"D\0"
                + os.fsencode(relative)
                + b"\0"
                + f"{stat.S_IMODE(entry.lstat().st_mode):04o}".encode()
                + b"\0"
            )
    return {
        "path": str(path),
        "root_mode": f"{root_mode:04o}",
        "tree_sha256": digest.hexdigest(),
        "file_count": file_count,
        "symlink_count": symlink_count,
        "symlink_referents": symlink_referents,
    }


def _run_readelf(readelf: Path, option: str, elf: Path) -> str:
    proc = subprocess.run(
        [str(readelf), option, str(elf)],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise EvidenceError(f"llvm-readelf {option} failed for {elf}")
    return proc.stdout


def _field_after(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line.split(marker, 1)[1].strip()
    return None


def _symbol_value(text: str, name: str) -> str | None:
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1] == name:
            return parts[1]
    return None


def _normalize_hex(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized.startswith("0x"):
        normalized = normalized[2:]
    if not re.fullmatch(r"[0-9a-f]+", normalized):
        return None
    return normalized.lstrip("0") or "0"


def _is_linx_machine(machine: str | None) -> bool:
    if not machine:
        return False
    normalized = machine.strip().lower()
    return "linx" in normalized or "em_linxisa" in normalized


def _inspect_elf(readelf: Path, path: Path) -> dict[str, object]:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise EvidenceError(f"missing ELF: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise EvidenceError(f"ELF symlink is forbidden: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise EvidenceError(f"missing ELF: {path}")
    header = _run_readelf(readelf, "-h", path)
    programs = _run_readelf(readelf, "-l", path)
    symbols = _run_readelf(readelf, "-s", path)
    machine = _field_after(header, "Machine:")
    entry = _field_after(header, "Entry point address:")
    start = _symbol_value(symbols, "_start")
    main = _symbol_value(symbols, "main")
    has_interp = bool(re.search(r"\bINTERP\b|Requesting program interpreter", programs))
    static_entry_ok = (
        not has_interp
        and _normalize_hex(entry) is not None
        and _normalize_hex(entry) == _normalize_hex(start)
        and (_normalize_hex(main) is None or _normalize_hex(entry) != _normalize_hex(main))
    )
    return {
        "path": str(path),
        "sha256": _sha256(path),
        "machine": machine,
        "is_linx_machine": _is_linx_machine(machine),
        "entry_point": entry,
        "start_symbol": start,
        "main_symbol": main,
        "has_interp": has_interp,
        "static_entry_ok": static_entry_ok,
    }


def _manifest_paths(lines: list[str]) -> set[str]:
    paths: set[str] = set()
    for line in lines:
        match = re.match(r"^[0-9a-fA-F]{64}  (.+)$", line.rstrip("\n"))
        if match:
            paths.add(match.group(1))
    return paths


def refresh_source_drift(
    baseline: Path, post: Path, *, diff_out: Path, paths_out: Path
) -> bool:
    """Refresh drift evidence and return True exactly when manifests differ."""
    if not baseline.is_file() or not post.is_file():
        raise EvidenceError("source baseline/post manifest missing")
    baseline_lines = baseline.read_text(encoding="utf-8").splitlines(keepends=True)
    post_lines = post.read_text(encoding="utf-8").splitlines(keepends=True)
    diff_out.unlink(missing_ok=True)
    paths_out.unlink(missing_ok=True)
    if baseline_lines == post_lines:
        return False
    diff_out.parent.mkdir(parents=True, exist_ok=True)
    diff_out.write_text(
        "".join(
            difflib.unified_diff(
                baseline_lines,
                post_lines,
                fromfile=str(baseline),
                tofile=str(post),
            )
        ),
        encoding="utf-8",
    )
    changed = sorted(_manifest_paths(baseline_lines) | _manifest_paths(post_lines))
    before = {line.split("  ", 1)[1].rstrip("\n"): line for line in baseline_lines if "  " in line}
    after = {line.split("  ", 1)[1].rstrip("\n"): line for line in post_lines if "  " in line}
    changed = [path for path in changed if before.get(path) != after.get(path)]
    paths_out.write_text("".join(f"{path}\n" for path in changed), encoding="utf-8")
    return True


def _parse_source_manifest(path: Path, source_root: Path) -> list[tuple[str, str]]:
    if path.is_symlink() or not path.is_file():
        raise EvidenceError(f"source manifest is not a regular file: {path}")
    try:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"invalid source manifest encoding: {path}") from exc
    if not lines:
        raise EvidenceError(f"invalid source manifest: empty file: {path}")
    rows: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line_number, line in enumerate(lines, start=1):
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\n]+)\n", line)
        if not match:
            raise EvidenceError(f"invalid source manifest row {path}:{line_number}")
        digest, raw_source = match.groups()
        source = _canonical_lexical_path(source_root, raw_source, "source manifest entry")
        try:
            relative = source.relative_to(source_root)
        except ValueError as exc:
            raise EvidenceError(f"source manifest entry escapes source root: {source}") from exc
        if "src" not in relative.parts[:-1]:
            raise EvidenceError(f"source manifest entry is outside a src subtree: {source}")
        _require_no_symlink_components(source_root, source, "source manifest entry")
        if source.is_symlink() or not source.is_file():
            raise EvidenceError(f"source manifest entry is not a regular file: {source}")
        if raw_source in seen:
            raise EvidenceError(f"duplicate source manifest path: {raw_source}")
        seen.add(raw_source)
        rows.append((digest, raw_source))
    encoded_paths = [os.fsencode(path_text) for _, path_text in rows]
    if encoded_paths != sorted(encoded_paths):
        raise EvidenceError(f"source manifest paths are not LC_ALL=C sorted: {path}")
    return rows


def check_source_symlinks(source_root: Path) -> None:
    """Reject every symlink at or below a source subtree without following it."""
    if source_root.is_symlink() or not source_root.is_dir():
        raise EvidenceError(f"missing canonical source root: {source_root}")
    for current_raw, dirs, files in os.walk(source_root, followlinks=False):
        current = Path(current_raw)
        kept_dirs: list[str] = []
        for name in dirs:
            entry = current / name
            relative = entry.relative_to(source_root)
            if entry.is_symlink():
                if "src" in relative.parts:
                    raise EvidenceError(f"source tree symlink is forbidden: {entry}")
                continue
            kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in files:
            entry = current / name
            relative = entry.relative_to(source_root)
            if entry.is_symlink() and "src" in relative.parts[:-1]:
                raise EvidenceError(f"source tree symlink is forbidden: {entry}")


def _current_source_manifest(source_root: Path) -> tuple[bytes, int]:
    if source_root.is_symlink() or not source_root.is_dir():
        raise EvidenceError(f"missing canonical source root: {source_root}")
    check_source_symlinks(source_root)
    sources: list[Path] = []
    for current_raw, dirs, files in os.walk(source_root, followlinks=False):
        current = Path(current_raw)
        for name in files:
            source = current / name
            relative = source.relative_to(source_root)
            if "src" not in relative.parts[:-1]:
                continue
            metadata = source.lstat()
            if stat.S_ISREG(metadata.st_mode):
                sources.append(source)
    sources.sort(key=lambda item: os.fsencode(str(item)))
    rows = [f"{_sha256(source)}  {source}\n" for source in sources]
    return "".join(rows).encode("utf-8"), len(sources)


def _source_evidence(root: Path, payload: dict[str, Any]) -> tuple[dict[str, object], list[str]]:
    source = payload.get("source_immutability")
    if not isinstance(source, dict):
        raise EvidenceError("manifest missing source_immutability")
    spec_dir = _canonical_lexical_path(root, payload.get("spec_dir"), "SPEC build root")
    _require_no_symlink_components(root, spec_dir, "SPEC build root")
    log_dir = spec_dir / "tmp" / "linx-build-logs"
    baseline = _canonical_lexical_path(root, source.get("baseline_manifest"), "source baseline")
    post = _canonical_lexical_path(root, source.get("post_manifest"), "source post-build")
    expected_baseline = log_dir / "src-baseline.sha256"
    expected_post = log_dir / "src-postbuild.sha256"
    if baseline != expected_baseline or post != expected_post:
        raise EvidenceError("source baseline/post must use canonical lexical paths")
    _require_no_symlink_components(spec_dir, baseline, "source baseline")
    _require_no_symlink_components(spec_dir, post, "source post-build")
    source_root = spec_dir / "benchspec" / "CPU"
    baseline_rows = _parse_source_manifest(baseline, source_root)
    post_rows = _parse_source_manifest(post, source_root)
    if baseline.read_bytes() != post.read_bytes():
        raise EvidenceError("source manifests differ")
    if baseline_rows != post_rows:
        raise EvidenceError("source manifest rows differ")
    if source.get("manifests_match") is not True:
        raise EvidenceError("manifest does not declare matching source manifests")
    current_manifest, source_count = _current_source_manifest(source_root)
    if current_manifest != baseline.read_bytes():
        raise EvidenceError("current source tree does not match baseline/post manifests")
    drift_raw = source.get("drift_paths")
    drift = _canonical_lexical_path(root, drift_raw, "source drift") if drift_raw else None
    drift_row: dict[str, object] | None = None
    warnings: list[str] = []
    expected_drift = log_dir / "src-drift-paths.txt"
    if drift is not None and drift != expected_drift:
        raise EvidenceError("source drift evidence must use canonical lexical path")
    if drift is not None and drift.exists():
        _require_no_symlink_components(spec_dir, drift, "source drift evidence")
        if drift.is_symlink() or not drift.is_file():
            raise EvidenceError("source drift evidence is not a regular file")
        drift_row = {
            "path": str(drift),
            "sha256": _sha256(drift),
            "bytes": drift.stat().st_size,
        }
        if drift.stat().st_size:
            warnings.append(
                "legacy manifest references a non-empty stale drift-path file although baseline/post match"
            )
    return (
        {
            "baseline": {"path": str(baseline), "sha256": _sha256(baseline)},
            "post": {"path": str(post), "sha256": _sha256(post)},
            "content_equal": True,
            "current_tree_manifest_sha256": hashlib.sha256(current_manifest).hexdigest(),
            "source_file_count": source_count,
            "drift_paths": drift_row,
        },
        warnings,
    )


def _resolve_tools(root: Path, payload: dict[str, Any]) -> tuple[Path, Path, bool]:
    readelf = _resolve_executable_path(root, payload.get("llvm_readelf"), "llvm-readelf")
    clang_declared = isinstance(payload.get("clang"), str) and bool(payload.get("clang"))
    clang_raw = payload.get("clang") or os.environ.get("LINX_CLANG") or str(readelf.with_name("clang"))
    clang = _resolve_executable_path(root, clang_raw, "clang")
    return clang, readelf, clang_declared


def _validate_manifest_shape(payload: dict[str, Any]) -> None:
    if payload.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise EvidenceError("unsupported build manifest schema")
    if payload.get("overall_ok") is not True or payload.get("failed_entries") != []:
        raise EvidenceError("build manifest is not an all-pass result")
    if payload.get("force_static") is not True:
        raise EvidenceError("Stage-A attestation requires force_static=true")
    if payload.get("link_mode") != "canonical-crt":
        raise EvidenceError("Stage-A attestation requires canonical-crt")
    if payload.get("selected_benchmarks") != list(EXPECTED_EXECUTABLES):
        raise EvidenceError("Stage-A benchmark set/order is not the required exact 10")
    results = payload.get("bench_results")
    if not isinstance(results, dict) or list(results) != list(EXPECTED_EXECUTABLES):
        raise EvidenceError("bench_results is not the required exact 10")


def _elf_evidence(root: Path, payload: dict[str, Any], readelf: Path) -> list[dict[str, object]]:
    spec_dir = _canonical_lexical_path(root, payload.get("spec_dir"), "SPEC build root")
    _require_no_symlink_components(root, spec_dir, "SPEC build root")
    if spec_dir.is_symlink() or not spec_dir.is_dir():
        raise EvidenceError(f"SPEC build root is not a regular directory: {spec_dir}")
    results = payload["bench_results"]
    evidence: list[dict[str, object]] = []
    for bench, expected_names in EXPECTED_EXECUTABLES.items():
        result = results[bench]
        if not isinstance(result, dict) or result.get("build_ok") is not True:
            raise EvidenceError(f"benchmark is not build_ok: {bench}")
        rows = result.get("executables")
        if not isinstance(rows, list) or [row.get("name") for row in rows] != expected_names:
            raise EvidenceError(f"wrong executable set for {bench}")
        for row in rows:
            name = row["name"]
            expected_path = spec_dir / "benchspec" / "CPU" / bench / "exe" / name
            manifest_path = _canonical_lexical_path(root, row.get("path"), f"{bench}/{name} ELF")
            if manifest_path != expected_path:
                raise EvidenceError(f"ELF path is not the canonical lexical path: {bench}/{name}")
            _require_no_symlink_components(spec_dir, manifest_path, "ELF")
            actual = _inspect_elf(readelf, manifest_path)
            if not actual["is_linx_machine"]:
                raise EvidenceError(f"ELF is not Linx machine: {manifest_path}")
            if not actual["static_entry_ok"]:
                raise EvidenceError(f"ELF static entry check failed: {manifest_path}")
            if row.get("exists") is not True or row.get("is_linx_machine") is not True:
                raise EvidenceError(f"manifest ELF flags are not passing: {manifest_path}")
            if row.get("static_entry_ok") is not True:
                raise EvidenceError(f"manifest static entry flag is not passing: {manifest_path}")
            if _normalize_hex(row.get("entry_point")) != _normalize_hex(actual["entry_point"]):
                raise EvidenceError(f"manifest entry point changed: {manifest_path}")
            if _normalize_hex(row.get("start_symbol")) != _normalize_hex(actual["start_symbol"]):
                raise EvidenceError(f"manifest _start symbol changed: {manifest_path}")
            evidence.append({"benchmark": bench, "name": name, **actual})
    return evidence


def build_attestation(repo_root: Path, manifest_path: Path) -> dict[str, object]:
    root = repo_root.resolve()
    manifest = manifest_path.resolve()
    if not manifest.is_file():
        raise EvidenceError(f"missing build manifest: {manifest}")
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise EvidenceError(f"cannot read build manifest: {exc}") from exc
    if not isinstance(payload, dict):
        raise EvidenceError("build manifest must be a JSON object")
    _validate_manifest_shape(payload)

    clang, readelf, clang_declared = _resolve_tools(root, payload)
    sysroot_declared = isinstance(payload.get("sysroot"), str) and bool(payload.get("sysroot"))
    sysroot_raw = payload.get("sysroot") or str(
        root / "out" / "libc" / "musl" / "install" / str(payload.get("mode", "phase-b"))
    )
    sysroot = _canonical_lexical_path(root, sysroot_raw, "sysroot")
    _require_no_symlink_components(root, sysroot, "sysroot")
    source_evidence, warnings = _source_evidence(root, payload)
    if not clang_declared or not sysroot_declared:
        warnings.append(
            "legacy manifest did not bind clang/sysroot paths; attestation records current derived paths only"
        )
    elfs = _elf_evidence(root, payload, readelf)
    tools = {
        "clang": _tool_identity(clang, "clang"),
        "llvm_readelf": _tool_identity(readelf, "llvm-readelf"),
    }
    sysroot_evidence = _directory_identity(sysroot)
    # Collect repository state last so the recorded dirty-path snapshot is as
    # close as possible to serialization of the attestation.
    repositories = {
        "superproject": _git_identity(root),
        "llvm": _git_identity(root / "compiler" / "llvm"),
        "musl": _git_identity(root / "lib" / "musl"),
    }
    evidence = {
        "repositories": repositories,
        "tools": tools,
        "sysroot": sysroot_evidence,
        "source_immutability": source_evidence,
        "build_contract": {
            "mode": payload.get("mode"),
            "target": payload.get("target") or "linx64-unknown-linux-musl",
            "optimize_flags": payload.get("optimize_flags"),
            "bench_optimize_flags": payload.get("bench_optimize_flags"),
            "force_static": payload.get("force_static"),
            "link_mode": payload.get("link_mode"),
            "selected_benchmarks": payload.get("selected_benchmarks"),
        },
        "executables": elfs,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "claim": "current_workspace_stage_a_artifact_attestation",
        "constraints": [
            "does_not_attest_SPEC_input_content_or_authorization",
            "does_not_attest_test_or_train_execution",
            "legacy_build_manifests_may_not_bind_original_build_tools",
        ],
        "input": {
            "build_manifest": {
                "path": str(manifest),
                "sha256": _sha256(manifest),
                "schema_version": payload.get("schema_version"),
                "generated_at_utc": payload.get("generated_at_utc"),
            }
        },
        "evidence": evidence,
        "counts": {"benchmarks": len(EXPECTED_EXECUTABLES), "executables": len(elfs)},
        "warnings": sorted(warnings),
        "ok": True,
    }


def _first_difference(expected: object, actual: object, path: str = "$") -> str | None:
    if type(expected) is not type(actual):
        return path
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            return path
        for key in sorted(expected):
            difference = _first_difference(expected[key], actual[key], f"{path}.{key}")
            if difference:
                return difference
        return None
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return path
        for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
            difference = _first_difference(left, right, f"{path}[{index}]")
            if difference:
                return difference
        return None
    return None if expected == actual else path


def verify_attestation(repo_root: Path, attestation: dict[str, Any] | Path) -> None:
    if isinstance(attestation, Path):
        try:
            recorded = json.loads(attestation.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise EvidenceError(f"cannot read attestation: {exc}") from exc
    else:
        recorded = attestation
    if not isinstance(recorded, dict) or recorded.get("schema_version") != SCHEMA_VERSION:
        raise EvidenceError("unsupported attestation schema")
    manifest_raw = recorded.get("input", {}).get("build_manifest", {}).get("path")
    manifest = _resolve_path(repo_root, manifest_raw, "attested build manifest")
    live = build_attestation(repo_root, manifest)
    recorded_comparable = {key: value for key, value in recorded.items() if key != "generated_at_utc"}
    live_comparable = {key: value for key, value in live.items() if key != "generated_at_utc"}
    difference = _first_difference(recorded_comparable, live_comparable)
    if difference:
        raise EvidenceError(f"attestation does not match current evidence at {difference}")


def _write_attestation(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    repositories = payload["evidence"]["repositories"]
    tools = payload["evidence"]["tools"]
    lines = [
        "# SPEC Stage-A Build Attestation",
        "",
        f"- Verdict: `{'PASS' if payload['ok'] else 'FAIL'}`",
        f"- Claim: `{payload['claim']}`",
        f"- Benchmarks: `{payload['counts']['benchmarks']}`",
        f"- Executables: `{payload['counts']['executables']}`",
        f"- Superproject: `{repositories['superproject']['head']}`",
        f"- LLVM: `{repositories['llvm']['head']}`",
        f"- musl: `{repositories['musl']['head']}`",
        f"- clang: `{tools['clang']['identity']}`",
        f"- llvm-readelf: `{tools['llvm_readelf']['identity']}`",
        "",
        "This attestation does not assert SPEC input content, authorization, or test/train execution.",
    ]
    warnings = payload.get("warnings", [])
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    refresh = subparsers.add_parser("refresh-source-drift")
    refresh.add_argument("--baseline", required=True)
    refresh.add_argument("--post", required=True)
    refresh.add_argument("--diff-out", required=True)
    refresh.add_argument("--paths-out", required=True)
    symlinks = subparsers.add_parser("check-source-symlinks")
    symlinks.add_argument("--source-root", required=True)
    attest = subparsers.add_parser("attest")
    attest.add_argument("--repo-root", required=True)
    attest.add_argument("--manifest", required=True)
    attest.add_argument("--out", required=True)
    attest.add_argument("--out-md")
    verify = subparsers.add_parser("verify")
    verify.add_argument("--repo-root", required=True)
    verify.add_argument("--attestation", required=True)
    return parser


def main(argv: list[str]) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "refresh-source-drift":
            drift = refresh_source_drift(
                Path(args.baseline),
                Path(args.post),
                diff_out=Path(args.diff_out),
                paths_out=Path(args.paths_out),
            )
            if drift:
                print(f"error: source drift detected; see {args.paths_out}", file=sys.stderr)
                return 1
            print("ok: source manifests match; stale drift evidence removed")
            return 0
        if args.command == "check-source-symlinks":
            check_source_symlinks(Path(args.source_root))
            print("ok: source subtrees contain no symlinks")
            return 0
        if args.command == "attest":
            payload = build_attestation(Path(args.repo_root), Path(args.manifest))
            _write_attestation(Path(args.out), payload)
            if args.out_md:
                _write_markdown(Path(args.out_md), payload)
            print(f"ok: wrote Stage-A attestation {args.out}")
            return 0
        verify_attestation(Path(args.repo_root), Path(args.attestation))
        print("ok: Stage-A attestation matches current evidence")
        return 0
    except EvidenceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
