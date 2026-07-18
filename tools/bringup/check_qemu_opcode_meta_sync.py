#!/usr/bin/env python3
"""
Audit QEMU Linx opcode metadata vs decode source files.

Current source-of-truth decode files depend on the checked-out QEMU line.
Known supported layouts:
  - modern line:
    - target/linx/insn16.decode
    - target/linx/insn32.decode
    - target/linx/insn48.decode
    - target/linx/insn64.decode
  - older/recovered line:
    - target/linx/block16.decode
    - target/linx/block32.decode
    - target/linx/block48.decode
    - target/linx/block32_private_fvec.decode

Canonical generated opcode id/meta headers are required in strict mode. A
non-strict audit may still inspect a decode-only development line, but such a
line can never satisfy a release gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


META_RE = re.compile(
    r"\{\.op_id=(?P<op_id>\d+),.*?"
    r"\.insn_len=(?P<insn_len>\d+),.*?"
    r"\.mask=UINT64_C\((?P<mask>0x[0-9a-fA-F]+)\),\s*"
    r"\.match=UINT64_C\((?P<match>0x[0-9a-fA-F]+)\),.*?"
    r"\.mnemonic=\"(?P<mnemonic>[^\"]+)\".*?"
    r"\.source_file=\"(?P<source_file>[^\"]+)\""
)
DECODE_TOKEN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DECODE_BITS_RE = re.compile(r"^[01.]+$")
IDS_RE = re.compile(r"^\s*LINX_OP_[A-Z0-9_]+\s*=\s*(\d+),\s*$")

FormKey = tuple[str, int, int, int]


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


def _parse_decode_forms(path: Path) -> set[FormKey]:
    """Return exact decoder signatures from one Linx decodetree source."""
    width_match = re.search(r"(?:insn|block)(16|32|48|64)", path.name)
    if width_match is None:
        return set()
    raw_width = int(width_match.group(1))
    insn_len = 64 if raw_width == 48 else raw_width
    out: set[FormKey] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith(("%", "{", "}")):
            continue
        fields = line.split()
        mnemonic = fields[0]
        if not DECODE_TOKEN_RE.match(mnemonic):
            continue
        bits = "".join(part for part in fields[1:] if DECODE_BITS_RE.match(part))
        if raw_width == 48 and len(bits) == 48:
            bits = ("0" * 16) + bits
        elif len(bits) != insn_len:
            continue
        mask = 0
        match = 0
        for bit in bits:
            mask <<= 1
            match <<= 1
            if bit == "1":
                mask |= 1
                match |= 1
            elif bit == "0":
                mask |= 1
        out.add((mnemonic, insn_len, mask, match))
    return out


def _parse_meta(
    path: Path,
) -> tuple[set[int], dict[str, set[str]], dict[str, set[FormKey]]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    ids: set[int] = set()
    by_source: dict[str, set[str]] = {}
    forms_by_source: dict[str, set[FormKey]] = {}
    for item in META_RE.finditer(text):
        op_id = int(item.group("op_id"))
        mnemonic = item.group("mnemonic")
        source_file = item.group("source_file")
        ids.add(op_id)
        by_source.setdefault(source_file, set()).add(mnemonic)
        forms_by_source.setdefault(source_file, set()).add(
            (
                mnemonic,
                int(item.group("insn_len")),
                int(item.group("mask"), 0),
                int(item.group("match"), 0),
            )
        )
    return ids, by_source, forms_by_source


def _form_json(form: FormKey) -> dict[str, object]:
    _, insn_len, mask, match = form
    return {
        "insn_len": insn_len,
        "mask": f"0x{mask:x}",
        "match": f"0x{match:x}",
    }


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
    lines.append(f"- Decoder/meta form mismatch count: `{report['signature_mismatch_count']}`")
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
    if report["signature_mismatches"]:
        lines.append("### Decoder/Metadata Form Mismatches")
        for item in report["signature_mismatches"]:
            lines.append(
                f"- `{item['mnemonic']}`: decode-only `{len(item['decode_only'])}`, "
                f"meta-only `{len(item['meta_only'])}`"
            )
        lines.append("")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Audit QEMU opcode meta/id tables against live decode files")
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
    decode_file_sets = (
        ("insn16.decode", "insn32.decode", "insn48.decode", "insn64.decode"),
        ("block16.decode", "block32.decode", "block48.decode", "block32_private_fvec.decode"),
    )

    decode_files: tuple[str, ...] | None = None
    for candidate in decode_file_sets:
        if all((linx_root / name).is_file() for name in candidate):
            decode_files = candidate
            break
    if decode_files is None:
        print("error: required QEMU opcode files missing for every supported decode layout:", file=sys.stderr)
        for candidate in decode_file_sets:
            print("  - " + ", ".join(str(linx_root / name) for name in candidate), file=sys.stderr)
        return 1

    decode_patterns: set[str] = set()
    decode_forms: set[FormKey] = set()
    for name in decode_files:
        decode_patterns |= _parse_decode_patterns(linx_root / name)
        decode_forms |= _parse_decode_forms(linx_root / name)

    have_opcode_meta = meta_path.is_file() and ids_path.is_file()
    meta_ids: set[int] = set()
    ids_enum: set[int] = set()
    meta_patterns: set[str] = set()
    meta_forms: set[FormKey] = set()
    meta_internal: set[str] = set()
    meta_non_internal: set[str] = set()
    if have_opcode_meta:
        meta_ids, meta_by_source, meta_forms_by_source = _parse_meta(meta_path)
        ids_enum = _parse_ids(ids_path)
        for source_file, mnems in meta_by_source.items():
            if source_file in decode_files:
                meta_patterns |= mnems
                meta_forms |= meta_forms_by_source.get(source_file, set())
        meta_internal = set(meta_by_source.get("internal", set()))
        meta_non_internal = meta_patterns | (set().union(*[v for k, v in meta_by_source.items() if k != "internal"]) if meta_by_source else set())
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

    if have_opcode_meta:
        decode_only = sorted(decode_patterns - meta_patterns)
        meta_only = sorted(meta_patterns - decode_patterns)
        decode_only_unexpected = sorted(set(decode_only) - allow_decode_only)
        meta_only_unexpected = sorted(set(meta_only) - allow_meta_only)
        id_mismatch = sorted(meta_ids ^ ids_enum)
        signature_mismatches: list[dict[str, object]] = []
        for mnemonic in sorted(decode_patterns & meta_patterns):
            decode_for_name = {form for form in decode_forms if form[0] == mnemonic}
            meta_for_name = {form for form in meta_forms if form[0] == mnemonic}
            missing_meta_forms = sorted(decode_for_name - meta_for_name)
            stale_meta_forms = sorted(meta_for_name - decode_for_name)
            if missing_meta_forms or stale_meta_forms:
                signature_mismatches.append(
                    {
                        "mnemonic": mnemonic,
                        "decode_only": [_form_json(form) for form in missing_meta_forms],
                        "meta_only": [_form_json(form) for form in stale_meta_forms],
                    }
                )
        ok = (
            not decode_only_unexpected
            and not meta_only_unexpected
            and not signature_mismatches
            and (not args.strict or not id_mismatch)
        )
        classification = (
            "qemu_opcode_meta_sync_ok"
            if ok
            else "qemu_opcode_meta_sync_unexpected_drift"
        )
    elif args.strict:
        decode_only = sorted(decode_patterns)
        meta_only = []
        decode_only_unexpected = sorted(decode_patterns)
        meta_only_unexpected = []
        id_mismatch = []
        signature_mismatches = []
        ok = False
        classification = "qemu_opcode_meta_sync_missing_canonical_tables"
    else:
        decode_only = sorted(decode_patterns)
        meta_only = []
        decode_only_unexpected = []
        meta_only_unexpected = []
        id_mismatch = []
        signature_mismatches = []
        ok = True
        classification = "qemu_opcode_meta_sync_decode_only_line"

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "qemu_root": str(qemu_root),
        "allowlist": str(allow_path) if allow_path else "",
        "have_opcode_meta": have_opcode_meta,
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
        "signature_mismatches": signature_mismatches,
        "signature_mismatch_count": len(signature_mismatches),
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
            f"meta_only_unexpected={len(meta_only_unexpected)}, "
            f"signature_mismatch={len(signature_mismatches)})"
        )
        return 0

    print(
        "error: qemu opcode meta/id audit found unexpected drift "
        f"(decode_only_unexpected={len(decode_only_unexpected)}, "
        f"meta_only_unexpected={len(meta_only_unexpected)}, "
        f"signature_mismatch={len(signature_mismatches)})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
