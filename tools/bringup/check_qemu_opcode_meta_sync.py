#!/usr/bin/env python3
"""
Audit QEMU Linx opcode metadata vs decode source files.

This is an anti-drift check for:
  - target/linx/linx_opcode_ids_gen.h
  - target/linx/linx_opcode_meta_gen.h
against:
  - target/linx/insn16.decode
  - target/linx/insn32.decode
  - target/linx/insn48.decode
  - target/linx/insn64.decode
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


META_RE = re.compile(r"\{\.op_id=(\d+),.*?\.mnemonic=\"([^\"]+)\".*?\.source_file=\"([^\"]+)\"")
DECODE_TOKEN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
IDS_RE = re.compile(r"^\s*LINX_OP_[A-Z0-9_]+\s*=\s*(\d+),\s*$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _parse_decode_patterns(path: Path) -> set[str]:
    out: set[str] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("%") or line.startswith("{") or line.startswith("}"):
            continue
        token = line.split()[0]
        if not DECODE_TOKEN_RE.match(token):
            continue
        out.add(token)
    return out


def _parse_meta(path: Path) -> tuple[set[int], dict[str, set[str]]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    ids: set[int] = set()
    by_source: dict[str, set[str]] = {}
    for op_id_s, mnemonic, source_file in META_RE.findall(text):
        op_id = int(op_id_s)
        ids.add(op_id)
        by_source.setdefault(source_file, set()).add(mnemonic)
    return ids, by_source


def _parse_ids(path: Path) -> set[int]:
    ids: set[int] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = IDS_RE.match(raw)
        if not m:
            continue
        ids.add(int(m.group(1)))
    return ids


def _load_allowlist(path: Path | None) -> tuple[set[str], set[str]]:
    if path is None:
        return set(), set()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"error: allowlist must be a JSON object: {path}")
    decode_only = set(str(x) for x in data.get("decode_only_allow", []))
    meta_only = set(str(x) for x in data.get("meta_only_allow", []))
    return decode_only, meta_only


def _render_md(report: dict[str, object], out_md: Path) -> None:
    lines: list[str] = []
    lines.append("# QEMU Opcode Sync Audit")
    lines.append("")
    lines.append(f"- Generated (UTC): `{report['generated_at_utc']}`")
    lines.append(f"- Result: `{report['result']['classification']}`")
    lines.append(f"- OK: `{str(report['result']['ok']).lower()}`")
    lines.append(f"- Decode forms (unique): `{report['decode_unique_patterns']}`")
    lines.append(f"- Meta mnemonics (unique, non-internal): `{report['meta_unique_non_internal']}`")
    lines.append("")
    lines.append("## Drift Summary")
    lines.append("")
    lines.append(f"- Decode-only (unexpected): `{report['decode_only_unexpected_count']}`")
    lines.append(f"- Meta-only (unexpected): `{report['meta_only_unexpected_count']}`")
    lines.append(f"- Enum/meta op-id mismatch count: `{report['id_mismatch_count']}`")
    lines.append("")
    if report["decode_only_unexpected"]:
        lines.append("### Decode-only Unexpected")
        for item in report["decode_only_unexpected"]:
            lines.append(f"- `{item}`")
        lines.append("")
    if report["meta_only_unexpected"]:
        lines.append("### Meta-only Unexpected")
        for item in report["meta_only_unexpected"]:
            lines.append(f"- `{item}`")
        lines.append("")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Audit QEMU opcode meta/id tables against decode files")
    ap.add_argument("--qemu-root", default="emulator/qemu", help="Path to QEMU repo root")
    ap.add_argument(
        "--allowlist",
        default="docs/bringup/qemu_opcode_sync_allowlist.json",
        help="JSON allowlist for known decode/meta drift",
    )
    ap.add_argument("--report-out", default="", help="Optional JSON report path")
    ap.add_argument("--out-md", default="", help="Optional Markdown report path")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any unexpected drift or enum/meta id mismatch",
    )
    args = ap.parse_args(argv)

    qemu_root = Path(args.qemu_root).resolve()
    linx_root = qemu_root / "target" / "linx"
    ids_path = linx_root / "linx_opcode_ids_gen.h"
    meta_path = linx_root / "linx_opcode_meta_gen.h"
    decode_files = ("insn16.decode", "insn32.decode", "insn48.decode", "insn64.decode")

    missing_inputs = [str(p) for p in [ids_path, meta_path] if not p.is_file()]
    for name in decode_files:
        path = linx_root / name
        if not path.is_file():
            missing_inputs.append(str(path))
    if missing_inputs:
        print("error: required QEMU opcode files missing:", file=sys.stderr)
        for item in missing_inputs:
            print(f"  - {item}", file=sys.stderr)
        return 1

    decode_patterns: set[str] = set()
    for name in decode_files:
        decode_patterns |= _parse_decode_patterns(linx_root / name)

    meta_ids, meta_by_source = _parse_meta(meta_path)
    ids_enum = _parse_ids(ids_path)
    meta_patterns: set[str] = set()
    for source_file, mnems in meta_by_source.items():
        if source_file in decode_files:
            meta_patterns |= mnems

    meta_internal = set(meta_by_source.get("internal", set()))
    meta_non_internal = meta_patterns | (set().union(*[v for k, v in meta_by_source.items() if k != "internal"]) if meta_by_source else set())
    # Remove internal pseudo names from public sync counts.
    meta_non_internal -= {m for m in meta_non_internal if m.startswith("internal_")}

    allow_decode_only: set[str] = set()
    allow_meta_only: set[str] = set()
    if args.allowlist:
        allow_path = Path(args.allowlist).resolve()
        if not allow_path.is_file():
            print(f"error: allowlist not found: {allow_path}", file=sys.stderr)
            return 1
        allow_decode_only, allow_meta_only = _load_allowlist(allow_path)
    else:
        allow_path = None

    decode_only = sorted(decode_patterns - meta_patterns)
    meta_only = sorted(meta_patterns - decode_patterns)
    decode_only_unexpected = sorted(set(decode_only) - allow_decode_only)
    meta_only_unexpected = sorted(set(meta_only) - allow_meta_only)

    id_mismatch = sorted(meta_ids ^ ids_enum)

    ok = not decode_only_unexpected and not meta_only_unexpected and (not args.strict or not id_mismatch)
    classification = (
        "qemu_opcode_meta_sync_ok"
        if ok
        else "qemu_opcode_meta_sync_unexpected_drift"
    )

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "qemu_root": str(qemu_root),
        "allowlist": str(allow_path) if allow_path else "",
        "decode_unique_patterns": len(decode_patterns),
        "meta_unique_decode_patterns": len(meta_patterns),
        "meta_unique_non_internal": len(meta_non_internal),
        "meta_internal_names": sorted(meta_internal),
        "decode_only": decode_only,
        "meta_only": meta_only,
        "decode_only_unexpected": decode_only_unexpected,
        "meta_only_unexpected": meta_only_unexpected,
        "decode_only_unexpected_count": len(decode_only_unexpected),
        "meta_only_unexpected_count": len(meta_only_unexpected),
        "id_mismatch": id_mismatch,
        "id_mismatch_count": len(id_mismatch),
        "result": {
            "ok": ok,
            "classification": classification,
        },
    }

    if args.report_out:
        report_path = Path(args.report_out).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.out_md:
        _render_md(report, Path(args.out_md).resolve())

    if ok:
        print(
            "ok: qemu opcode meta/id audit passed "
            f"(decode_only_unexpected={len(decode_only_unexpected)}, "
            f"meta_only_unexpected={len(meta_only_unexpected)})"
        )
        return 0

    print(
        "error: qemu opcode meta/id audit found unexpected drift "
        f"(decode_only_unexpected={len(decode_only_unexpected)}, "
        f"meta_only_unexpected={len(meta_only_unexpected)})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

