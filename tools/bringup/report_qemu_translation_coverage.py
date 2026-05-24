#!/usr/bin/env python3
"""Generate or enforce AVS QEMU translation coverage from per-source objects."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


_HEX_TOKEN_RE = re.compile(r"^[0-9a-fA-F]{2,16}$")
_OBJDUMP_INSN_RE = re.compile(r"^\s*[0-9a-fA-F]+:\s+")
_SPEC_DECODE_COMMENT_RE = re.compile(
    r"^\s*#\s+([A-Za-z][A-Za-z0-9_. ]*)\s+\([^)]+\)\s+\[\d+\]\s*$"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _prefix(value: str) -> str:
    if value.startswith("BSTART"):
        return "BSTART"
    if value.startswith("C.BSTART"):
        return "C.BSTART"
    if value.startswith("HL.BSTART"):
        return "HL.BSTART"
    if "." in value:
        return value.split(".", 1)[0]
    if " " in value:
        return value.split(" ", 1)[0]
    return value


def canonicalize_mnemonic(mnemonic: str) -> str:
    s = mnemonic.strip()
    if not s:
        return ""
    s = s.replace(" ", ".")
    s = s.rstrip(",")
    s = re.sub(r"\{[^}]*\}$", "", s)
    s = s.rstrip(",")
    m = re.match(r"^[0-9a-fA-F]{2}([A-Za-z].*)$", s)
    if m:
        candidate = m.group(1)
        if "." in candidate or candidate.startswith(
            ("BSTART", "BSTOP", "FENTRY", "FEXIT", "FRET")
        ):
            s = candidate
    s = s.upper()
    if s == "B.ATTR":
        return "B.ARG"
    if s == "BSTART.AUX":
        return "BSTART.SYS"
    if s == "C.BSTART.AUX":
        return "C.BSTART.SYS"
    return s


def derived_selector_mnemonics(mnemonic: str, operands: list[str]) -> set[str]:
    selector = canonicalize_mnemonic(mnemonic)
    if selector == "B.DATR":
        return {"B.ARG"}
    if not operands:
        return set()

    op0 = canonicalize_mnemonic(operands[0].rstrip(","))
    aliases = {
        ("BSTART.STD", "CALL"): "BSTART CALL",
        ("HL.BSTART.STD", "CALL"): "HL.BSTART CALL",
        ("BSTART.CUBE", "ACCCVT"): "BSTART.ACCCVT",
        ("BSTART.CUBE", "TMATMUL"): "BSTART.TMATMUL",
        ("BSTART.CUBE", "TMATMUL.ACC"): "BSTART.TMATMUL.ACC",
        ("BSTART.PAR", "TLOAD"): "BSTART.TLOAD",
        ("BSTART.PAR", "TSTORE"): "BSTART.TSTORE",
        ("BSTART.PAR", "TMOV"): "BSTART.TMOV",
        ("BSTART.PAR", "TMATMUL"): "BSTART.TMATMUL",
        ("BSTART.PAR", "TMATMUL.ACC"): "BSTART.TMATMUL.ACC",
        ("BSTART.PAR", "ACCCVT"): "BSTART.ACCCVT",
        ("BSTART.TMA", "TLOAD"): "BSTART.TLOAD",
        ("BSTART.TMA", "TSTORE"): "BSTART.TSTORE",
        ("BSTART.TMA", "TMOV"): "BSTART.TMOV",
        ("BSTART.TEPL", "ERCOV"): "ERCOV",
        ("BSTART.TEPL", "ESAVE"): "ESAVE",
    }
    alias = aliases.get((selector, op0))
    return {alias} if alias else set()


def extract_mnemonics_from_spec_decode_source(path: Path) -> set[str]:
    mnems: set[str] = set()
    try:
        for line in path.read_text(errors="replace").splitlines():
            m = _SPEC_DECODE_COMMENT_RE.match(line)
            if not m:
                continue
            mnem = canonicalize_mnemonic(m.group(1))
            if mnem:
                mnems.add(mnem)
    except Exception as exc:
        print(f"warning: error reading {path}: {exc}", file=sys.stderr)
    return mnems


def extract_mnemonics_from_objdump(text: str) -> tuple[set[str], set[str]]:
    emitted: set[str] = set()
    unmapped_raw: set[str] = set()
    for line in text.splitlines():
        if not _OBJDUMP_INSN_RE.match(line):
            continue
        try:
            _, rest = line.split(":", 1)
        except ValueError:
            continue
        toks = rest.strip().split()
        if not toks:
            continue
        idx = 0
        while idx < len(toks) and _HEX_TOKEN_RE.match(toks[idx]):
            idx += 1
        if idx >= len(toks):
            continue
        raw = canonicalize_mnemonic(toks[idx])
        if not raw:
            continue
        emitted.add(raw)
        emitted |= derived_selector_mnemonics(raw, toks[idx + 1 :])
    return emitted, unmapped_raw


def map_emitted_to_spec(emitted_mnem: str, spec_mnemonics: set[str]) -> str | None:
    cur = canonicalize_mnemonic(emitted_mnem)
    if not cur:
        return None
    if cur in spec_mnemonics:
        return cur
    while "." in cur:
        cur = cur.rsplit(".", 1)[0]
        if cur in spec_mnemonics:
            return cur
    return None


def close_aliases(covered_spec: set[str], spec_mnemonics: set[str]) -> None:
    for a, b in (("BSTART", "BSTART.STD"), ("C.BSTART", "C.BSTART.STD")):
        if a in spec_mnemonics and b in spec_mnemonics and (a in covered_spec or b in covered_spec):
            covered_spec.add(a)
            covered_spec.add(b)
    for a, b in (("BSTART.MPAR", "C.BSTART.MPAR"), ("BSTART.MSEQ", "C.BSTART.MSEQ")):
        if a in spec_mnemonics and b in spec_mnemonics and (a in covered_spec or b in covered_spec):
            covered_spec.add(a)
            covered_spec.add(b)
    if any(
        m in covered_spec
        for m in (
            "BSTART.TMA",
            "BSTART.CUBE",
            "BSTART.VPAR",
            "BSTART.VSEQ",
            "BSTART.MPAR",
            "BSTART.MSEQ",
        )
    ):
        if "BSTART.PAR" in spec_mnemonics:
            covered_spec.add("BSTART.PAR")
        if "BSTART.TEPL" in spec_mnemonics:
            covered_spec.add("BSTART.TEPL")


def load_spec_mnemonics(spec_path: Path) -> set[str]:
    raw = json.loads(spec_path.read_text(encoding="utf-8"))
    instructions = raw.get("instructions", [])
    return {
        canonicalize_mnemonic(inst.get("mnemonic", ""))
        for inst in instructions
        if canonicalize_mnemonic(inst.get("mnemonic", ""))
    }


def render_markdown(report: dict[str, object], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# AVS QEMU Translation Coverage")
    lines.append("")
    lines.append(f"- Generated (UTC): `{report['generated_at_utc']}`")
    lines.append(f"- Spec unique mnemonics: `{report['spec_unique_mnemonics']}`")
    lines.append(f"- AVS object files scanned: `{report['object_files_scanned']}`")
    lines.append(
        f"- Covered spec mnemonics: `{report['coverage_count']}/{report['spec_unique_mnemonics']}` "
        f"(`{report['coverage_ratio_percent']}%`)"
    )
    lines.append(f"- Missing spec mnemonics: `{report['missing_count']}`")
    lines.append("")
    lines.append("## Coverage By Prefix")
    lines.append("")
    for key in sorted(report["covered_by_prefix"]):
        lines.append(f"- `{key}`: `{report['covered_by_prefix'][key]}`")
    lines.append("")
    lines.append("## Missing By Prefix")
    lines.append("")
    for key in sorted(report["missing_by_prefix"]):
        lines.append(f"- `{key}`: `{report['missing_by_prefix'][key]}`")
    lines.append("")
    lines.append("## Top Covering Objects")
    lines.append("")
    for name, count in report["top_covering_objects"]:
        lines.append(f"- `{name}`: `{count}`")
    lines.append("")
    lines.append("## Missing Spec Mnemonics (First 200)")
    lines.append("")
    for item in report["missing_spec_mnemonics"][:200]:
        lines.append(f"- `{item}`")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate AVS QEMU translation coverage report")
    ap.add_argument("--spec", default="isa/v0.56/linxisa-v0.56.json", help="Path to compiled ISA JSON")
    ap.add_argument("--obj-dir", default="avs/qemu/out/obj", help="Directory containing per-source AVS QEMU objects")
    ap.add_argument(
        "--llvm-objdump",
        default="compiler/llvm/build-linxisa-clang/bin/llvm-objdump",
        help="Path to llvm-objdump used to disassemble AVS objects",
    )
    ap.add_argument("--report-out", default="", help="Optional JSON report path")
    ap.add_argument("--out-md", default="", help="Optional Markdown summary path")
    ap.add_argument("--require-full", action="store_true", help="Fail unless AVS translation coverage is 100%%")
    args = ap.parse_args(argv)

    spec_path = Path(args.spec).resolve()
    obj_dir = Path(args.obj_dir).resolve()
    llvm_objdump = Path(args.llvm_objdump).resolve()

    if not spec_path.is_file():
        print(f"error: ISA spec not found: {spec_path}", file=sys.stderr)
        return 1
    if not obj_dir.is_dir():
        print(f"error: AVS object directory not found: {obj_dir}", file=sys.stderr)
        return 1
    if not llvm_objdump.is_file():
        print(f"error: llvm-objdump not found: {llvm_objdump}", file=sys.stderr)
        return 1

    spec_mnemonics = load_spec_mnemonics(spec_path)
    objects = sorted(p for p in obj_dir.glob("*.o") if p.is_file())
    if not objects:
        print(f"error: no object files found under {obj_dir}", file=sys.stderr)
        return 1

    covered_spec: set[str] = set()
    covered_by_object: dict[str, list[str]] = {}
    covered_objects_by_mnemonic: dict[str, list[str]] = defaultdict(list)
    unmapped_by_object: dict[str, list[str]] = {}

    for obj in objects:
        proc = subprocess.run(
            [str(llvm_objdump), "-d", str(obj)],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
        )
        if proc.returncode != 0:
            print(f"warning: llvm-objdump failed for {obj}", file=sys.stderr)
            continue

        raw_emitted, _ = extract_mnemonics_from_objdump(proc.stdout)
        sidecar_source = obj.with_suffix(".s")
        if sidecar_source.exists():
            raw_emitted |= extract_mnemonics_from_spec_decode_source(sidecar_source)
        mapped: set[str] = set()
        unmapped: set[str] = set()
        for mnem in raw_emitted:
            hit = map_emitted_to_spec(mnem, spec_mnemonics)
            if hit is None:
                unmapped.add(mnem)
            else:
                mapped.add(hit)

        close_aliases(mapped, spec_mnemonics)
        covered_spec |= mapped
        covered_by_object[obj.name] = sorted(mapped)
        unmapped_by_object[obj.name] = sorted(unmapped)
        for mnem in mapped:
            covered_objects_by_mnemonic[mnem].append(obj.name)

    missing_spec = sorted(spec_mnemonics - covered_spec)
    covered_by_prefix: dict[str, int] = {}
    missing_by_prefix: dict[str, int] = {}
    for mnemonic in covered_spec:
        pfx = _prefix(mnemonic)
        covered_by_prefix[pfx] = covered_by_prefix.get(pfx, 0) + 1
    for mnemonic in missing_spec:
        pfx = _prefix(mnemonic)
        missing_by_prefix[pfx] = missing_by_prefix.get(pfx, 0) + 1

    coverage_count = len(covered_spec)
    spec_count = len(spec_mnemonics)
    coverage_ratio = (coverage_count / spec_count) if spec_count else 0.0
    ok = not args.require_full or coverage_count == spec_count
    classification = (
        "qemu_avs_translation_coverage_complete"
        if coverage_count == spec_count
        else "qemu_avs_translation_coverage_incomplete"
    )

    top_covering_objects = sorted(
        ((name, len(mnems)) for name, mnems in covered_by_object.items()),
        key=lambda item: item[1],
        reverse=True,
    )[:25]

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "schema_version": "qemu-avs-translation-coverage-v1",
        "spec_path": str(spec_path),
        "obj_dir": str(obj_dir),
        "llvm_objdump": str(llvm_objdump),
        "object_files_scanned": len(objects),
        "spec_unique_mnemonics": spec_count,
        "coverage_count": coverage_count,
        "missing_count": len(missing_spec),
        "coverage_ratio_percent": round(coverage_ratio * 100.0, 2),
        "covered_by_prefix": covered_by_prefix,
        "missing_by_prefix": missing_by_prefix,
        "top_covering_objects": top_covering_objects,
        "covered_by_object": covered_by_object,
        "unmapped_by_object": unmapped_by_object,
        "covered_objects_by_mnemonic": dict(sorted(covered_objects_by_mnemonic.items())),
        "missing_spec_mnemonics": missing_spec,
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
        render_markdown(report, Path(args.out_md).resolve())

    if ok:
        print(
            "ok: generated AVS QEMU translation coverage report "
            f"({coverage_count}/{spec_count})"
        )
        return 0

    print(
        "error: AVS QEMU translation coverage below required bar "
        f"({coverage_count}/{spec_count})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
