#!/usr/bin/env python3
"""
Generate a machine-readable ISA-vs-QEMU coverage snapshot.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


QEMU_MNEMONIC_RE = re.compile(r"\.mnemonic=\"([^\"]+)\"")


SPECIAL_MAP: dict[str, str] = {
    "bstart_call": "BSTART CALL",
    "hl_bstart_std_call": "HL.BSTART CALL",
    "bstart_direct": "BSTART",
    "bstart_cond": "BSTART",
    "bstart_ind": "BSTART",
    "bstart_icall": "BSTART",
    "bstart_ret": "BSTART",
    "hl_bstart_std_cond": "HL.BSTART.STD",
    "hl_bstart_std_direct": "HL.BSTART.STD",
    "hl_bstart_std_fall": "HL.BSTART.STD",
    "bstart_par_tload": "BSTART.TLOAD",
    "bstart_par_tstore": "BSTART.TSTORE",
    "bstart_par_mamulb": "BSTART.TMATMUL",
    "bstart_par_mamulb_acc": "BSTART.TMATMUL.ACC",
    "bstart_par_acccvt": "BSTART.ACCCVT",
    "bstart_par_vcall": "BSTART.PAR",
    "bstart_par_compat163": "BSTART.PAR",
    "c_bstop": "C.BSTOP",
    "c_bstart_cond": "C.BSTART.STD",
    "c_bstart_direct": "C.BSTART.STD",
    "b_hint_trace": "B.HINT",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _prefix(value: str) -> str:
    if value.startswith("BSTART"):
        return "BSTART"
    if "." in value:
        return value.split(".", 1)[0]
    if " " in value:
        return value.split(" ", 1)[0]
    return value


def _canonicalize_qemu_mnemonic(name: str, spec_set: set[str]) -> str | None:
    norm = name.strip().lower()
    if not norm or norm.startswith("internal_"):
        return None

    special = SPECIAL_MAP.get(norm)
    if special is not None:
        return special if special in spec_set else None

    candidate = norm.upper().replace("_", ".")
    if candidate.startswith("B.DIM."):
        candidate = "B.DIM"

    return candidate if candidate in spec_set else None


def _render_markdown(report: dict[str, object], out_path: Path) -> None:
    missing = report["missing_spec_mnemonics"]
    unmapped = report["unmapped_qemu_mnemonics"]
    missing_prefix = report["missing_by_prefix"]
    mapped_prefix = report["mapped_by_prefix"]
    lines: list[str] = []
    lines.append("# ISA vs QEMU Coverage Snapshot")
    lines.append("")
    lines.append(f"- Generated (UTC): `{report['generated_at_utc']}`")
    lines.append(f"- Spec unique mnemonics: `{report['spec_unique_mnemonics']}`")
    lines.append(f"- QEMU unique decode mnemonics (non-internal): `{report['qemu_unique_mnemonics']}`")
    lines.append(f"- QEMU mapped spec mnemonics: `{report['qemu_mapped_spec_mnemonics']}`")
    lines.append(
        f"- Coverage: `{report['coverage_count']}/{report['spec_unique_mnemonics']}` "
        f"(`{report['coverage_ratio_percent']}%`)"
    )
    lines.append(f"- Missing spec mnemonics: `{report['missing_count']}`")
    lines.append(f"- Unmapped QEMU mnemonics: `{len(unmapped)}`")
    lines.append("")
    lines.append("## Coverage By Prefix")
    lines.append("")
    for key in sorted(mapped_prefix):
        lines.append(f"- `{key}`: `{mapped_prefix[key]}`")
    lines.append("")
    lines.append("## Missing By Prefix")
    lines.append("")
    for key in sorted(missing_prefix):
        lines.append(f"- `{key}`: `{missing_prefix[key]}`")
    lines.append("")
    lines.append("## Unmapped QEMU Mnemonics")
    lines.append("")
    if unmapped:
        for item in unmapped:
            lines.append(f"- `{item}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Missing Spec Mnemonics (First 200)")
    lines.append("")
    for item in missing[:200]:
        lines.append(f"- `{item}`")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate ISA-vs-QEMU coverage report")
    ap.add_argument(
        "--spec",
        default="isa/v0.3/linxisa-v0.3.json",
        help="Path to compiled ISA JSON",
    )
    ap.add_argument(
        "--qemu-meta",
        default="emulator/qemu/target/linx/linx_opcode_meta_gen.h",
        help="Path to QEMU Linx opcode metadata header",
    )
    ap.add_argument(
        "--report-out",
        default="",
        help="Optional JSON report path",
    )
    ap.add_argument(
        "--out-md",
        default="",
        help="Optional Markdown summary path",
    )
    args = ap.parse_args(argv)

    spec_path = Path(args.spec).resolve()
    qemu_meta_path = Path(args.qemu_meta).resolve()
    if not spec_path.is_file():
        print(f"error: ISA spec not found: {spec_path}", file=sys.stderr)
        return 1
    if not qemu_meta_path.is_file():
        print(f"error: QEMU metadata file not found: {qemu_meta_path}", file=sys.stderr)
        return 1

    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(spec_data, dict) or not isinstance(spec_data.get("instructions"), list):
        print(f"error: malformed ISA spec file: {spec_path}", file=sys.stderr)
        return 1

    spec_set = {
        str(inst.get("mnemonic", "")).strip()
        for inst in spec_data.get("instructions", [])
        if str(inst.get("mnemonic", "")).strip()
    }

    qemu_all = set(QEMU_MNEMONIC_RE.findall(qemu_meta_path.read_text(encoding="utf-8", errors="replace")))
    qemu_non_internal = sorted(m for m in qemu_all if m and not m.startswith("internal_"))
    mapped_pairs: dict[str, str] = {}
    unmapped: list[str] = []
    for name in qemu_non_internal:
        mapped = _canonicalize_qemu_mnemonic(name, spec_set)
        if mapped is None:
            unmapped.append(name)
            continue
        mapped_pairs[name] = mapped

    mapped_spec = sorted(set(mapped_pairs.values()))
    missing_spec = sorted(spec_set - set(mapped_spec))

    mapped_by_prefix: dict[str, int] = {}
    for mnemonic in mapped_spec:
        p = _prefix(mnemonic)
        mapped_by_prefix[p] = mapped_by_prefix.get(p, 0) + 1

    missing_by_prefix: dict[str, int] = {}
    for mnemonic in missing_spec:
        p = _prefix(mnemonic)
        missing_by_prefix[p] = missing_by_prefix.get(p, 0) + 1

    coverage_count = len(mapped_spec)
    spec_count = len(spec_set)
    coverage_ratio = (coverage_count / spec_count) if spec_count else 0.0

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "spec_path": str(spec_path),
        "qemu_meta_path": str(qemu_meta_path),
        "spec_unique_mnemonics": spec_count,
        "qemu_unique_mnemonics": len(qemu_non_internal),
        "qemu_mapped_spec_mnemonics": coverage_count,
        "coverage_count": coverage_count,
        "missing_count": len(missing_spec),
        "coverage_ratio_percent": round(coverage_ratio * 100.0, 2),
        "mapped_by_prefix": mapped_by_prefix,
        "missing_by_prefix": missing_by_prefix,
        "unmapped_qemu_mnemonics": sorted(unmapped),
        "mapped_qemu_to_spec": dict(sorted(mapped_pairs.items())),
        "missing_spec_mnemonics": missing_spec,
        "result": {
            "ok": True,
            "classification": "qemu_isa_coverage_report_generated",
        },
    }

    if args.report_out:
        report_path = Path(args.report_out).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.out_md:
        _render_markdown(report, Path(args.out_md).resolve())

    print(
        "ok: generated ISA-vs-QEMU coverage report "
        f"(coverage={coverage_count}/{spec_count}, missing={len(missing_spec)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

