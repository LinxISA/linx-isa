#!/usr/bin/env python3
"""Generate a focused LLVM/QEMU implementation report for 48-bit ISA forms."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _render_markdown(report: dict[str, object], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# 48-bit LLVM/QEMU Implementation Status")
    lines.append("")
    lines.append(f"- Generated (UTC): `{report['generated_at_utc']}`")
    lines.append(f"- Spec 48-bit forms: `{report['spec']['form_count']}`")
    lines.append(f"- Spec 48-bit mnemonics: `{report['spec']['mnemonic_count']}`")
    lines.append("")
    lines.append("| Surface | Covered | Ratio |")
    lines.append("| --- | --- | --- |")
    lines.append(
        f"| LLVM mnemonic coverage | `{report['llvm']['mnemonic_coverage_count']}/{report['spec']['mnemonic_count']}` | `{report['llvm']['mnemonic_coverage_ratio_percent']}%` |"
    )
    lines.append(
        f"| LLVM roundtrip-stable forms | `{report['llvm']['roundtrip_stable_form_count']}/{report['spec']['form_count']}` | `{report['llvm']['roundtrip_stable_ratio_percent']}%` |"
    )
    lines.append(
        f"| QEMU mapped forms | `{report['qemu']['mapped_form_count']}/{report['spec']['form_count']}` | `{report['qemu']['mapped_form_ratio_percent']}%` |"
    )
    lines.append(
        f"| QEMU translation mnemonics | `{report['qemu']['translation_mnemonic_coverage_count']}/{report['spec']['mnemonic_count']}` | `{report['qemu']['translation_mnemonic_coverage_ratio_percent']}%` |"
    )
    lines.append("")
    lines.append("## Missing LLVM 48-bit Mnemonics")
    lines.append("")
    if report["llvm"]["missing_mnemonics"]:
        for item in report["llvm"]["missing_mnemonics"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Missing QEMU 48-bit Forms")
    lines.append("")
    if report["qemu"]["missing_forms"]:
        for item in report["qemu"]["missing_forms"]:
            lines.append(f"- `{item['mnemonic']}`: `{item['asm']}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Missing QEMU Translation 48-bit Mnemonics")
    lines.append("")
    if report["qemu"]["translation_missing_mnemonics"]:
        for item in report["qemu"]["translation_missing_mnemonics"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## LLVM Roundtrip-Skipped 48-bit Forms")
    lines.append("")
    if report["llvm"]["roundtrip_skipped_forms"]:
        for item in report["llvm"]["roundtrip_skipped_forms"]:
            lines.append(f"- `{item['mnemonic']}`: `{item['asm']}`")
    else:
        lines.append("- None")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


_MISSING_FORM_RE = re.compile(r"^(?P<mnemonic>.+?) \[len=(?P<len>\d+) ")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", default="isa/v0.56/linxisa-v0.56.json")
    ap.add_argument(
        "--compiler-analyzer",
        default="avs/compiler/linx-llvm/tests/analyze_coverage.py",
    )
    ap.add_argument(
        "--compiler-out-dir",
        default="avs/compiler/linx-llvm/tests/out-linx64",
    )
    ap.add_argument(
        "--compiler-roundtrip-json",
        default="avs/compiler/linx-llvm/tests/out-linx64/99_spec_decode/99_spec_decode.roundtrip.json",
    )
    ap.add_argument(
        "--qemu-isa-report",
        default="docs/bringup/gates/qemu_isa_coverage_latest.json",
    )
    ap.add_argument(
        "--qemu-translation-report",
        default="docs/bringup/gates/qemu_translation_coverage_latest.json",
    )
    ap.add_argument("--report-out", default="")
    ap.add_argument("--out-md", default="")
    ap.add_argument("--require-full", action="store_true")
    args = ap.parse_args(argv)

    spec_path = Path(args.spec).resolve()
    analyzer_path = Path(args.compiler_analyzer).resolve()
    compiler_out_dir = Path(args.compiler_out_dir).resolve()
    roundtrip_path = Path(args.compiler_roundtrip_json).resolve()
    qemu_isa_report_path = Path(args.qemu_isa_report).resolve()
    qemu_translation_report_path = Path(args.qemu_translation_report).resolve()

    for path, label, is_dir in (
        (spec_path, "ISA spec", False),
        (analyzer_path, "compiler analyzer", False),
        (compiler_out_dir, "compiler out dir", True),
        (roundtrip_path, "compiler roundtrip report", False),
        (qemu_isa_report_path, "QEMU ISA report", False),
        (qemu_translation_report_path, "QEMU translation report", False),
    ):
        if is_dir and not path.is_dir():
            print(f"error: {label} not found: {path}", file=sys.stderr)
            return 1
        if not is_dir and not path.is_file():
            print(f"error: {label} not found: {path}", file=sys.stderr)
            return 1

    spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
    forms48 = [ins for ins in spec_data["instructions"] if ins.get("length_bits") == 48]
    form_count = len(forms48)
    mnemonic_set = {ins["mnemonic"] for ins in forms48}
    mnemonic_count = len(mnemonic_set)
    form_key_set = {(ins["mnemonic"], ins["asm"]) for ins in forms48}

    analyzer = _load_module(analyzer_path)
    llvm_spec = analyzer.load_isa_spec(spec_path)
    llvm_results = analyzer.analyze_coverage(llvm_spec, compiler_out_dir)
    llvm_missing_mnemonics = sorted(mnemonic_set & set(llvm_results["missing_mnemonics"]))
    llvm_mnemonic_coverage_count = mnemonic_count - len(llvm_missing_mnemonics)

    roundtrip = json.loads(roundtrip_path.read_text(encoding="utf-8"))
    skipped_indexes = {item["index"] for item in roundtrip.get("skipped_instructions", [])}
    roundtrip_skipped_forms: list[dict[str, object]] = []
    for idx, ins in enumerate(spec_data["instructions"], start=1):
        if idx not in skipped_indexes:
            continue
        if ins.get("length_bits") != 48:
            continue
        roundtrip_skipped_forms.append(
            {"index": idx, "mnemonic": ins["mnemonic"], "asm": ins["asm"]}
        )
    roundtrip_stable_form_count = form_count - len(roundtrip_skipped_forms)

    qemu_isa_report = json.loads(qemu_isa_report_path.read_text(encoding="utf-8"))
    qemu_missing_form_strings = qemu_isa_report.get("missing_spec_forms", [])
    qemu_missing_mnemonic_counter: Counter[str] = Counter()
    for item in qemu_missing_form_strings:
        if not isinstance(item, str):
            continue
        match = _MISSING_FORM_RE.match(item)
        if match is None or int(match.group("len")) != 48:
            continue
        mnemonic = match.group("mnemonic")
        qemu_missing_mnemonic_counter[mnemonic] += 1
    qemu_missing_forms = []
    remaining_by_mnemonic = Counter(qemu_missing_mnemonic_counter)
    for ins in forms48:
        mnemonic = ins["mnemonic"]
        if remaining_by_mnemonic[mnemonic] <= 0:
            continue
        qemu_missing_forms.append({"mnemonic": mnemonic, "asm": ins["asm"]})
        remaining_by_mnemonic[mnemonic] -= 1
    qemu_mapped_form_count = form_count - len(qemu_missing_forms)

    qemu_translation_report = json.loads(qemu_translation_report_path.read_text(encoding="utf-8"))
    covered_translation_mnemonics = set(qemu_translation_report.get("covered_objects_by_mnemonic", {}))

    def translation_has_mnemonic(mnemonic: str) -> bool:
        if mnemonic in covered_translation_mnemonics:
            return True
        if mnemonic.startswith("HL.BSTART") and "HL.BSTART.CALL" in covered_translation_mnemonics:
            return True
        return False

    qemu_translation_missing_mnemonics = sorted(
        mnemonic for mnemonic in mnemonic_set if not translation_has_mnemonic(mnemonic)
    )
    qemu_translation_coverage_count = mnemonic_count - len(qemu_translation_missing_mnemonics)

    ok = (
        not llvm_missing_mnemonics
        and not roundtrip_skipped_forms
        and not qemu_missing_forms
        and not qemu_translation_missing_mnemonics
    )

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "schema_version": "linx-48bit-implementation-v1",
        "spec": {
            "path": str(spec_path),
            "form_count": form_count,
            "mnemonic_count": mnemonic_count,
        },
        "llvm": {
            "compiler_analyzer": str(analyzer_path),
            "compiler_out_dir": str(compiler_out_dir),
            "roundtrip_report": str(roundtrip_path),
            "mnemonic_coverage_count": llvm_mnemonic_coverage_count,
            "mnemonic_coverage_ratio_percent": round(llvm_mnemonic_coverage_count / mnemonic_count * 100.0, 2) if mnemonic_count else 0.0,
            "missing_mnemonics": llvm_missing_mnemonics,
            "roundtrip_stable_form_count": roundtrip_stable_form_count,
            "roundtrip_stable_ratio_percent": round(roundtrip_stable_form_count / form_count * 100.0, 2) if form_count else 0.0,
            "roundtrip_skipped_forms": roundtrip_skipped_forms,
        },
        "qemu": {
            "isa_report": str(qemu_isa_report_path),
            "translation_report": str(qemu_translation_report_path),
            "mapped_form_count": qemu_mapped_form_count,
            "mapped_form_ratio_percent": round(qemu_mapped_form_count / form_count * 100.0, 2) if form_count else 0.0,
            "missing_forms": qemu_missing_forms,
            "translation_mnemonic_coverage_count": qemu_translation_coverage_count,
            "translation_mnemonic_coverage_ratio_percent": round(qemu_translation_coverage_count / mnemonic_count * 100.0, 2) if mnemonic_count else 0.0,
            "translation_missing_mnemonics": qemu_translation_missing_mnemonics,
        },
        "result": {
            "ok": ok,
            "classification": "48bit_implementation_complete" if ok else "48bit_implementation_incomplete",
        },
    }

    if args.report_out:
        report_path = Path(args.report_out).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        _render_markdown(report, Path(args.out_md).resolve())

    if args.require_full and not ok:
        print("error: 48-bit LLVM/QEMU implementation subset is incomplete", file=sys.stderr)
        return 1

    print(
        "ok: 48-bit implementation report generated "
        f"(llvm_mnemonics={llvm_mnemonic_coverage_count}/{mnemonic_count}, "
        f"llvm_forms={roundtrip_stable_form_count}/{form_count}, "
        f"qemu_forms={qemu_mapped_form_count}/{form_count}, "
        f"qemu_translation={qemu_translation_coverage_count}/{mnemonic_count})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
