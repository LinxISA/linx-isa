#!/usr/bin/env python3
"""
Validate that linxisa_virt_defconfig retains SPEC/9p workflow requirements.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_OPTIONS: tuple[tuple[str, str], ...] = (
    ("CONFIG_DEVTMPFS", "y"),
    ("CONFIG_DEVTMPFS_MOUNT", "y"),
    ("CONFIG_VIRTIO_MMIO", "y"),
    ("CONFIG_VIRTIO_MMIO_CMDLINE_DEVICES", "y"),
    ("CONFIG_VIRTIO_BLK", "y"),
    ("CONFIG_NET_9P", "y"),
    ("CONFIG_NET_9P_VIRTIO", "y"),
    ("CONFIG_9P_FS", "y"),
    ("CONFIG_9P_FS_POSIX_ACL", "y"),
    ("CONFIG_9P_FS_SECURITY", "y"),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _parse_defconfig(path: Path) -> dict[str, str]:
    options: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key:
            options[key] = value
    return options


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate linxisa_virt_defconfig 9p/virtio requirements")
    ap.add_argument(
        "--defconfig",
        default="kernel/linux/arch/linx/configs/linxisa_virt_defconfig",
        help="Path to kernel defconfig to validate",
    )
    ap.add_argument(
        "--report-out",
        default="",
        help="Optional path to JSON report output",
    )
    args = ap.parse_args(argv)

    defconfig_path = Path(args.defconfig).resolve()
    if not defconfig_path.is_file():
        print(f"error: defconfig not found: {defconfig_path}", file=sys.stderr)
        return 1

    options = _parse_defconfig(defconfig_path)

    missing: list[str] = []
    mismatched: list[dict[str, str]] = []
    for key, expected in REQUIRED_OPTIONS:
        actual = options.get(key)
        if actual is None:
            missing.append(key)
            continue
        if actual != expected:
            mismatched.append({"key": key, "expected": expected, "actual": actual})

    ok = not missing and not mismatched
    report = {
        "generated_at_utc": _utc_now(),
        "defconfig": str(defconfig_path),
        "required_option_count": len(REQUIRED_OPTIONS),
        "missing": missing,
        "mismatched": mismatched,
        "result": {
            "ok": ok,
            "classification": "linxisa_virt_defconfig_spec_compatible"
            if ok
            else "linxisa_virt_defconfig_spec_incompatible",
        },
    }

    if args.report_out:
        report_path = Path(args.report_out).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if ok:
        print(
            "ok: linxisa_virt_defconfig includes required 9p/virtio options "
            f"({len(REQUIRED_OPTIONS)} checks)"
        )
        return 0

    print(
        "error: linxisa_virt_defconfig missing required SPEC/9p options "
        f"(missing={len(missing)}, mismatched={len(mismatched)})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

