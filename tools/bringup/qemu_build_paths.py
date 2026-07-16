"""Shared QEMU binary selection and provenance for bring-up runners."""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any


def _qemu_head(root: Path) -> str | None:
    qemu_root = root / "emulator" / "qemu"
    try:
        return subprocess.check_output(
            ["git", "-C", str(qemu_root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _qemu_tracked_dirty(root: Path) -> bool | None:
    qemu_root = root / "emulator" / "qemu"
    try:
        status = subprocess.check_output(
            ["git", "-C", str(qemu_root), "status", "--porcelain", "--untracked-files=no"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return bool(status.strip())


def _qemu_version(binary: Path) -> str:
    try:
        output = subprocess.check_output(
            [str(binary), "--version"],
            text=True,
            stderr=subprocess.STDOUT,
            timeout=5.0,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return f"unavailable: {exc}"
    return output.splitlines()[0] if output.splitlines() else ""


def _sha256(binary: Path) -> str:
    if not binary.is_file():
        return ""
    digest = hashlib.sha256()
    with binary.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _matching_clean_qemu(root: Path, target: str = "qemu-system-linx64") -> Path | None:
    out_dir = Path(os.environ.get("QEMU_CLEAN_OUT_DIR", "/tmp/linx-qemu-clean-build"))
    binary = out_dir / target
    marker = out_dir / ".linx_qemu_clean_head"
    if not binary.is_file() or not os.access(binary, os.X_OK) or not marker.is_file():
        return None

    head = _qemu_head(root)
    if head is None:
        return None

    marker_head = marker.read_text(encoding="utf-8", errors="replace").strip().split(":", 1)[0]
    if marker_head != head:
        return None
    return binary


def default_qemu_binary(root: Path, target: str = "qemu-system-linx64") -> Path:
    explicit = os.environ.get("QEMU")
    if explicit:
        binary = Path(explicit).expanduser()
        if not binary.is_file() or not os.access(binary, os.X_OK):
            raise FileNotFoundError(f"explicit QEMU binary is not executable: {binary}")
        return binary

    clean = _matching_clean_qemu(root, target=target)
    if clean is not None:
        return clean
    out_dir = Path(os.environ.get("QEMU_CLEAN_OUT_DIR", "/tmp/linx-qemu-clean-build"))
    raise FileNotFoundError(
        "no QEMU binary was selected: set QEMU to an explicit executable or "
        f"produce a HEAD-matched clean build at {out_dir / target}"
    )


def qemu_binary_provenance(
    root: Path,
    binary: Path,
    target: str = "qemu-system-linx64",
) -> dict[str, Any]:
    """Return reproducibility metadata for a selected QEMU binary.

    The marker fields describe builds produced by run_qemu_build_clean.sh. They
    are still useful when another explicit --qemu path is used because a missing
    or mismatched marker makes stale-build evidence obvious in SPEC ledgers.
    """

    root = root.resolve()
    binary = binary.resolve()
    qemu_root = root / "emulator" / "qemu"
    head = _qemu_head(root)
    dirty = _qemu_tracked_dirty(root)
    marker_path = binary.parent / ".linx_qemu_clean_head"
    marker = ""
    marker_head = ""
    if marker_path.is_file():
        marker = marker_path.read_text(encoding="utf-8", errors="replace").strip()
        marker_head = marker.split(":", 1)[0]
    marker_matches_head = bool(marker_head and head and marker_head == head)

    try:
        relative_to_qemu = str(binary.relative_to(qemu_root.resolve()))
    except ValueError:
        relative_to_qemu = ""

    return {
        "path": str(binary),
        "sha256": _sha256(binary),
        "relative_to_qemu": relative_to_qemu,
        "version": _qemu_version(binary) if binary.is_file() else "",
        "qemu_repo_head": head or "",
        "qemu_repo_dirty_tracked": dirty,
        "clean_build_marker": marker,
        "clean_build_marker_path": str(marker_path) if marker_path.exists() else "",
        "clean_build_marker_matches_head": marker_matches_head,
        "clean_build_for_head": marker_matches_head and not bool(dirty),
        "target": target,
    }


def require_clean_qemu_binary(
    root: Path,
    binary: Path,
    target: str = "qemu-system-linx64",
) -> dict[str, Any]:
    provenance = qemu_binary_provenance(root, binary, target=target)
    if not provenance["clean_build_for_head"]:
        raise RuntimeError(
            "canonical flow requires a HEAD-matched clean QEMU build: "
            f"path={provenance['path']} head={provenance['qemu_repo_head']} "
            f"marker={provenance['clean_build_marker'] or 'missing'}"
        )
    return provenance
