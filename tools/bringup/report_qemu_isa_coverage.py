#!/usr/bin/env python3
"""Generate or enforce a machine-readable ISA-vs-QEMU coverage snapshot."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


QEMU_MNEMONIC_RE = re.compile(r"\.mnemonic=\"([^\"]+)\"")
QEMU_META_RE = re.compile(
    r"\.insn_len=(?P<insn_len>\d+),\s+"
    r"\.mask=UINT64_C\((?P<mask>0x[0-9a-fA-F]+)\),\s+"
    r"\.match=UINT64_C\((?P<match>0x[0-9a-fA-F]+)\),\s+"
    r"\.mnemonic=\"(?P<mnemonic>[^\"]+)\""
)
DECODE_TOKEN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


SPECIAL_MAP: dict[str, str | list[str]] = {
    "bstart_call": ["BSTART CALL", "BSTART.STD"],
    "hl_bstart_std_call": "HL.BSTART CALL",
    "bstart_direct": ["BSTART", "BSTART.STD"],
    "bstart_cond": ["BSTART", "BSTART.STD"],
    "bstart_ind": ["BSTART", "BSTART.STD"],
    "bstart_icall": ["BSTART", "BSTART.STD"],
    "bstart_ret": ["BSTART", "BSTART.STD"],
    "hl_bstart_std_cond": "HL.BSTART.STD",
    "hl_bstart_std_direct": "HL.BSTART.STD",
    "hl_bstart_std_fall": "HL.BSTART.STD",
    "bstart_tma": ["BSTART.TMA", "BSTART.TMOV"],
    "bstart_tepl": [
        "BSTART.TEPL",
        "BSTART.PAR",
        "BSTART.TLOAD",
        "BSTART.TSTORE",
        "BSTART.TMATMUL",
        "BSTART.TMATMUL.ACC",
        "BSTART.ACCCVT",
    ],
    "c_bstop": "C.BSTOP",
    "c_bstart_cond": "C.BSTART",
    "c_bstart_direct": "C.BSTART",
    "c_bstart_std": "C.BSTART.STD",
    "c_bstart_std_fall": "C.BSTART.STD",
    "c_bstart_std_direct": "C.BSTART.STD",
    "c_bstart_std_cond": "C.BSTART.STD",
    "c_bstart_std_call": "C.BSTART.STD",
    "c_bstart_std_ind": "C.BSTART.STD",
    "c_bstart_std_icall": "C.BSTART.STD",
    "c_bstart_std_ret": "C.BSTART.STD",
    "c_bstart_fp": "C.BSTART.FP",
    "c_bstart_sys": "C.BSTART.SYS",
    "c_bstart_mpar": "C.BSTART.MPAR",
    "c_bstart_mseq": "C.BSTART.MSEQ",
    "c_bstart_vpar": "C.BSTART.VPAR",
    "c_bstart_vseq": "C.BSTART.VSEQ",
    "b_hint_trace": "B.HINT",
    "bstart_fp_fall": "BSTART.FP",
    "bstart_fp_direct": "BSTART.FP",
    "bstart_fp_cond": "BSTART.FP",
    "bstart_fp_call": "BSTART.FP",
    "bstart_fp_ind": "BSTART.FP",
    "bstart_fp_icall": "BSTART.FP",
    "bstart_fp_ret": "BSTART.FP",
    "bstart_sys": "BSTART.SYS",
    "bstart_fixp": "BSTART.FIXP",
    "hl_bstart_fp_fall": "HL.BSTART.FP",
    "hl_bstart_fp_direct": "HL.BSTART.FP",
    "hl_bstart_fp_cond": "HL.BSTART.FP",
    "hl_bstart_fp_call": "HL.BSTART.FP",
    "hl_ldi_po": ["HL.LDI.PO", "HL.LD.PO"],
    "hl_ldi_pr": ["HL.LDI.PR", "HL.LD.PR"],
    "hl_ldip": ["HL.LDIP", "HL.LDP"],
    "hl_lwi_po": ["HL.LWI.PO", "HL.LW.PO"],
    "hl_lwi_pr": ["HL.LWI.PR", "HL.LW.PR"],
    "hl_lwip": ["HL.LWIP", "HL.LWP"],
    "hl_lwui_po": ["HL.LWUI.PO", "HL.LWU.PO"],
    "hl_lwui_pr": ["HL.LWUI.PR", "HL.LWU.PR"],
    "hl_lwuip": ["HL.LWUIP", "HL.LWUP"],
    "hl_sdi_po": ["HL.SDI.PO", "HL.SD.PO"],
    "hl_sdi_pr": ["HL.SDI.PR", "HL.SD.PR"],
    "hl_sdi_upo": ["HL.SDI.UPO", "HL.SD.UPO"],
    "hl_sdi_upr": ["HL.SDI.UPR", "HL.SD.UPR"],
    "hl_sdip": ["HL.SDIP", "HL.SDP"],
    "hl_sdip_u": ["HL.SDIP.U", "HL.SDP.U"],
    "hl_swi_po": ["HL.SWI.PO", "HL.SW.PO"],
    "hl_swi_pr": ["HL.SWI.PR", "HL.SW.PR"],
    "hl_swi_upo": ["HL.SWI.UPO", "HL.SW.UPO"],
    "hl_swi_upr": ["HL.SWI.UPR", "HL.SW.UPR"],
    "hl_swip": ["HL.SWIP", "HL.SWP"],
    "hl_swip_u": ["HL.SWIP.U", "HL.SWP.U"],
    "b_eq": "B.EQ",
    "b_ne": "B.NE",
    "b_lt": "B.LT",
    "b_ge": "B.GE",
    "b_ltu": "B.LTU",
    "b_geu": "B.GEU",
    "assert": "ASSERT",
    "b_iod": "B.IOD",
    "bc_iall": "BC.IALL",
    "bc_iva": "BC.IVA",
    "bse": "BSE",
    "bwe": "BWE",
    "bwi": "BWI",
    "bwt": "BWT",
    "dc_iall": "DC.IALL",
    "dc_iva": "DC.IVA",
    "dc_civa": "DC.CIVA",
    "dc_cva": "DC.CVA",
    "dc_csw": "DC.CSW",
    "dc_cisw": "DC.CISW",
    "dc_isw": "DC.ISW",
    "dc_zva": "DC.ZVA",
    "ic_iall": "IC.IALL",
    "ic_iva": "IC.IVA",
    "tlb_ia": "TLB.IA",
    "tlb_iv": "TLB.IV",
    "tlb_iav": "TLB.IAV",
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


def _parse_decode_patterns(path: Path) -> set[str]:
    out: set[str] = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("%") or line.startswith("{") or line.startswith("}"):
            continue
        token = line.split()[0]
        if DECODE_TOKEN_RE.match(token):
            out.add(token)
    return out


def _load_qemu_decode_mnemonics(qemu_root: Path) -> set[str]:
    linx_dir = qemu_root / "target" / "linx"
    decode_files = ("insn16.decode", "insn32.decode", "insn48.decode", "insn64.decode")
    missing = [str(linx_dir / name) for name in decode_files if not (linx_dir / name).is_file()]
    if missing:
        raise FileNotFoundError("\n".join(missing))
    out: set[str] = set()
    for name in decode_files:
        out |= _parse_decode_patterns(linx_dir / name)
    return out


def _parse_int(value: str) -> int:
    return int(str(value), 0)


def _normalize_form_length(length_bits: int) -> int:
    return 64 if length_bits == 48 else length_bits


def _canonicalize_qemu_mnemonic(name: str, spec_set: set[str]) -> list[str]:
    norm = name.strip().lower()
    if not norm or norm.startswith("internal_"):
        return []

    special = SPECIAL_MAP.get(norm)
    if special is not None:
        candidates = [special] if isinstance(special, str) else special
        return [candidate for candidate in candidates if candidate in spec_set]

    candidate = norm.upper().replace("_", ".")
    if candidate.startswith("B.DIM."):
        candidate = "B.DIM"

    return [candidate] if candidate in spec_set else []


def _load_qemu_meta_entries(path: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = QEMU_META_RE.search(raw)
        if not match:
            continue
        mnemonic = match.group("mnemonic")
        if not mnemonic or mnemonic.startswith("internal_"):
            continue
        entries.append(
            {
                "mnemonic": mnemonic,
                "insn_len": int(match.group("insn_len")),
                "mask": _parse_int(match.group("mask")),
                "match": _parse_int(match.group("match")),
            }
        )
    return entries


def _spec_form_key(inst: dict[str, object]) -> tuple[str, int, int, int]:
    mnemonic = str(inst.get("mnemonic", "")).strip()
    enc = inst.get("encoding", {})
    raw_length_bits = int(enc.get("length_bits", inst.get("length_bits", 0)) or 0)
    length_bits = _normalize_form_length(raw_length_bits)
    parts = list(enc.get("parts", []))
    if length_bits == 64 and int(enc.get("length_bits", 0) or 0) == 64 and len(parts) == 2:
        mask = _parse_int(parts[0].get("mask", "0")) | (_parse_int(parts[1].get("mask", "0")) << 32)
        match = _parse_int(parts[0].get("match", "0")) | (_parse_int(parts[1].get("match", "0")) << 32)
    else:
        mask = _parse_int(parts[0].get("mask", "0")) if parts else 0
        match = _parse_int(parts[0].get("match", "0")) if parts else 0
    if raw_length_bits == 48:
        # QEMU decodes 48-bit instructions through a zero-extended 64-bit
        # container, so the top 16 bits are architecturally fixed to zero even
        # when the spec only records the low 48 payload bits.
        mask |= 0xFFFF000000000000
    return (mnemonic, length_bits, mask, match)


def _format_form(key: tuple[str, int, int, int]) -> str:
    mnemonic, length_bits, mask, match = key
    return f"{mnemonic} [len={length_bits} mask=0x{mask:x} match=0x{match:x}]"


def _bucket_counts(items: set[tuple[str, int, int, int]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for mnemonic, _, _, _ in items:
        prefix = _prefix(mnemonic)
        out[prefix] = out.get(prefix, 0) + 1
    return out


def _render_markdown(report: dict[str, object], out_path: Path) -> None:
    missing = report["missing_spec_mnemonics"]
    missing_forms = report["missing_spec_forms"]
    unmapped = report["unmapped_qemu_mnemonics"]
    missing_prefix = report["missing_by_prefix"]
    mapped_prefix = report["mapped_by_prefix"]
    mapped_forms_prefix = report["mapped_forms_by_prefix"]
    missing_forms_prefix = report["missing_forms_by_prefix"]
    lines: list[str] = []
    lines.append("# ISA vs QEMU Coverage Snapshot")
    lines.append("")
    lines.append(f"- Generated (UTC): `{report['generated_at_utc']}`")
    lines.append(f"- Spec unique mnemonics: `{report['spec_unique_mnemonics']}`")
    lines.append(f"- QEMU unique decode mnemonics (non-internal): `{report['qemu_unique_mnemonics']}`")
    lines.append(f"- QEMU mapped spec mnemonics: `{report['qemu_mapped_spec_mnemonics']}`")
    lines.append(
        f"- Mnemonic coverage: `{report['coverage_count']}/{report['spec_unique_mnemonics']}` "
        f"(`{report['coverage_ratio_percent']}%`)"
    )
    lines.append(f"- Spec legal forms: `{report['spec_total_forms']}`")
    lines.append(f"- QEMU mapped spec forms: `{report['form_coverage_count']}`")
    lines.append(
        f"- Form coverage: `{report['form_coverage_count']}/{report['spec_total_forms']}` "
        f"(`{report['form_coverage_ratio_percent']}%`)"
    )
    lines.append(f"- Missing spec mnemonics: `{report['missing_count']}`")
    lines.append(f"- Missing spec forms: `{report['form_missing_count']}`")
    lines.append(f"- Reserved spec forms: `{report['reserved_form_count']}`")
    lines.append(f"- Unmapped QEMU mnemonics: `{len(unmapped)}`")
    lines.append("")
    lines.append("## Mnemonic Coverage By Prefix")
    lines.append("")
    for key in sorted(mapped_prefix):
        lines.append(f"- `{key}`: `{mapped_prefix[key]}`")
    lines.append("")
    lines.append("## Missing Mnemonics By Prefix")
    lines.append("")
    for key in sorted(missing_prefix):
        lines.append(f"- `{key}`: `{missing_prefix[key]}`")
    lines.append("")
    lines.append("## Form Coverage By Prefix")
    lines.append("")
    for key in sorted(mapped_forms_prefix):
        lines.append(f"- `{key}`: `{mapped_forms_prefix[key]}`")
    lines.append("")
    lines.append("## Missing Forms By Prefix")
    lines.append("")
    for key in sorted(missing_forms_prefix):
        lines.append(f"- `{key}`: `{missing_forms_prefix[key]}`")
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
    lines.append("")
    lines.append("## Missing Spec Forms (First 200)")
    lines.append("")
    for item in missing_forms[:200]:
        lines.append(f"- `{item}`")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate ISA-vs-QEMU coverage report")
    ap.add_argument("--spec", default="isa/v0.4/linxisa-v0.4.json", help="Path to compiled ISA JSON")
    ap.add_argument(
        "--qemu-root",
        default="emulator/qemu",
        help="Path to QEMU repo root; when present, mnemonic coverage is computed from decodetree sources.",
    )
    ap.add_argument(
        "--qemu-meta",
        default="emulator/qemu/target/linx/linx_opcode_meta_gen.h",
        help="Path to QEMU Linx opcode metadata header (required for per-form coverage).",
    )
    ap.add_argument("--report-out", default="", help="Optional JSON report path")
    ap.add_argument("--out-md", default="", help="Optional Markdown summary path")
    ap.add_argument("--fail-under-count", type=int, default=0, help="Fail if mnemonic coverage is lower than this value.")
    ap.add_argument("--require-full", action="store_true", help="Fail unless mnemonic and form coverage are complete.")
    args = ap.parse_args(argv)

    spec_path = Path(args.spec).resolve()
    qemu_root = Path(args.qemu_root).resolve()
    qemu_meta_path = Path(args.qemu_meta).resolve()
    if not spec_path.is_file():
        print(f"error: ISA spec not found: {spec_path}", file=sys.stderr)
        return 1

    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(spec_data, dict) or not isinstance(spec_data.get("instructions"), list):
        print(f"error: malformed ISA spec file: {spec_path}", file=sys.stderr)
        return 1

    instructions = [inst for inst in spec_data.get("instructions", []) if str(inst.get("mnemonic", "")).strip()]
    spec_set = {str(inst.get("mnemonic", "")).strip() for inst in instructions}
    spec_forms = {_spec_form_key(inst) for inst in instructions}

    qemu_source_kind = "decode"
    qemu_meta_all: set[str] = set()
    try:
        qemu_all = _load_qemu_decode_mnemonics(qemu_root)
    except FileNotFoundError:
        if not qemu_meta_path.is_file():
            print(
                "error: neither QEMU decode sources nor metadata header are available "
                f"({qemu_root}, {qemu_meta_path})",
                file=sys.stderr,
            )
            return 1
        qemu_source_kind = "meta"
        qemu_meta_all = set(QEMU_MNEMONIC_RE.findall(qemu_meta_path.read_text(encoding="utf-8", errors="replace")))
        qemu_all = qemu_meta_all

    if not qemu_meta_path.is_file():
        print(f"error: QEMU opcode metadata header not found: {qemu_meta_path}", file=sys.stderr)
        return 1
    meta_entries = _load_qemu_meta_entries(qemu_meta_path)
    if not qemu_meta_all:
        qemu_meta_all = {str(entry["mnemonic"]) for entry in meta_entries}

    qemu_non_internal = sorted(m for m in qemu_all if m and not m.startswith("internal_"))
    mapped_pairs: dict[str, list[str]] = {}
    unmapped: list[str] = []
    for name in qemu_non_internal:
        mapped = _canonicalize_qemu_mnemonic(name, spec_set)
        if not mapped:
            unmapped.append(name)
            continue
        mapped_pairs[name] = mapped

    mapped_spec = sorted({spec_name for values in mapped_pairs.values() for spec_name in values})
    missing_spec = sorted(spec_set - set(mapped_spec))

    qemu_form_keys: set[tuple[str, int, int, int]] = set()
    for entry in meta_entries:
        mapped = _canonicalize_qemu_mnemonic(str(entry["mnemonic"]), spec_set)
        for spec_name in mapped:
            qemu_form_keys.add((spec_name, int(entry["insn_len"]), int(entry["mask"]), int(entry["match"])))

    mapped_spec_forms = sorted(spec_forms & qemu_form_keys)
    missing_spec_forms = sorted(_format_form(key) for key in (spec_forms - qemu_form_keys))

    mapped_by_prefix: dict[str, int] = {}
    for mnemonic in mapped_spec:
        p = _prefix(mnemonic)
        mapped_by_prefix[p] = mapped_by_prefix.get(p, 0) + 1

    missing_by_prefix: dict[str, int] = {}
    for mnemonic in missing_spec:
        p = _prefix(mnemonic)
        missing_by_prefix[p] = missing_by_prefix.get(p, 0) + 1

    mapped_forms_by_prefix = _bucket_counts(set(mapped_spec_forms))
    missing_forms_by_prefix = _bucket_counts(spec_forms - qemu_form_keys)

    coverage_count = len(mapped_spec)
    spec_count = len(spec_set)
    coverage_ratio = (coverage_count / spec_count) if spec_count else 0.0
    form_coverage_count = len(mapped_spec_forms)
    spec_form_count = len(spec_forms)
    form_coverage_ratio = (form_coverage_count / spec_form_count) if spec_form_count else 0.0

    ok = True
    classification = "qemu_isa_coverage_report_generated"
    if args.fail_under_count and coverage_count < args.fail_under_count:
        ok = False
        classification = "qemu_isa_coverage_below_threshold"
    if args.require_full and (coverage_count != spec_count or form_coverage_count != spec_form_count):
        ok = False
        classification = "qemu_isa_coverage_incomplete"

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "schema_version": "qemu-isa-coverage-v2",
        "spec_path": str(spec_path),
        "qemu_root": str(qemu_root),
        "qemu_meta_path": str(qemu_meta_path),
        "qemu_source_kind": qemu_source_kind,
        "qemu_meta_mnemonics": len([m for m in qemu_meta_all if m and not m.startswith("internal_")]),
        "spec_unique_mnemonics": spec_count,
        "qemu_unique_mnemonics": len(qemu_non_internal),
        "qemu_unique_forms": len(meta_entries),
        "qemu_mapped_spec_mnemonics": coverage_count,
        "qemu_mapped_spec_forms": form_coverage_count,
        "coverage_count": coverage_count,
        "missing_count": len(missing_spec),
        "coverage_ratio_percent": round(coverage_ratio * 100.0, 2),
        "spec_total_forms": spec_form_count,
        "form_coverage_count": form_coverage_count,
        "form_missing_count": len(spec_form_count and (spec_forms - qemu_form_keys) or []),
        "form_coverage_ratio_percent": round(form_coverage_ratio * 100.0, 2),
        "legal_mnemonic_count": spec_count,
        "reserved_mnemonic_count": 0,
        "legal_form_count": spec_form_count,
        "reserved_form_count": 0,
        "mapped_by_prefix": mapped_by_prefix,
        "missing_by_prefix": missing_by_prefix,
        "mapped_forms_by_prefix": mapped_forms_by_prefix,
        "missing_forms_by_prefix": missing_forms_by_prefix,
        "unmapped_qemu_mnemonics": sorted(unmapped),
        "mapped_qemu_to_spec": dict(sorted(mapped_pairs.items())),
        "missing_spec_mnemonics": missing_spec,
        "missing_spec_forms": missing_spec_forms,
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
        _render_markdown(report, Path(args.out_md).resolve())

    if ok:
        print(
            "ok: generated ISA-vs-QEMU coverage report "
            f"(mnemonics={coverage_count}/{spec_count}, forms={form_coverage_count}/{spec_form_count})"
        )
        return 0

    print(
        "error: ISA-vs-QEMU coverage below required bar "
        f"(mnemonics={coverage_count}/{spec_count}, forms={form_coverage_count}/{spec_form_count})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
