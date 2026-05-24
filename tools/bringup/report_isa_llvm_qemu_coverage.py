#!/usr/bin/env python3
"""Generate a combined ISA-LLVM-QEMU coverage coherence report."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


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


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _bucket_counts(items: set[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        key = _prefix(item)
        out[key] = out.get(key, 0) + 1
    return out


def _top_counts(counts: dict[str, int], limit: int = 25) -> list[list[object]]:
    return [[k, v] for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]]


def _render_markdown(report: dict[str, object], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# ISA-LLVM-QEMU Coverage Coherence")
    lines.append("")
    lines.append(f"- Generated (UTC): `{report['generated_at_utc']}`")
    lines.append(f"- Spec unique mnemonics: `{report['spec_unique_mnemonics']}`")
    lines.append("")
    lines.append("| Surface | Covered | Ratio |")
    lines.append("| --- | --- | --- |")
    lines.append(
        f"| LLVM compiled coverage | `{report['llvm']['coverage_count']}/{report['spec_unique_mnemonics']}` | `{report['llvm']['coverage_ratio_percent']}%` |"
    )
    lines.append(
        f"| QEMU mapped implementation coverage | `{report['qemu_impl']['coverage_count']}/{report['spec_unique_mnemonics']}` | `{report['qemu_impl']['coverage_ratio_percent']}%` |"
    )
    lines.append(
        f"| QEMU AVS translation coverage | `{report['qemu_translation']['coverage_count']}/{report['spec_unique_mnemonics']}` | `{report['qemu_translation']['coverage_ratio_percent']}%` |"
    )
    lines.append("")
    lines.append("## Inconsistency Summary")
    lines.append("")
    lines.append(
        f"- Compiler-covered but missing from QEMU implementation: `{report['inconsistencies']['compiler_only_vs_qemu_impl_count']}`"
    )
    lines.append(
        f"- QEMU-implemented but missing from AVS translation coverage: `{report['inconsistencies']['qemu_impl_only_vs_translation_count']}`"
    )
    lines.append(
        f"- AVS translation-covered but not mapped in QEMU implementation: `{report['inconsistencies']['translation_without_qemu_impl_count']}`"
    )
    lines.append(
        f"- Compiler-covered but missing from AVS translation coverage: `{report['inconsistencies']['compiler_only_vs_translation_count']}`"
    )
    lines.append("")
    for title, key in (
        ("Compiler vs QEMU implementation", "compiler_only_vs_qemu_impl_by_prefix"),
        ("QEMU implementation vs AVS translation", "qemu_impl_only_vs_translation_by_prefix"),
        ("Compiler vs AVS translation", "compiler_only_vs_translation_by_prefix"),
    ):
        lines.append(f"### {title}")
        lines.append("")
        for prefix, count in report["inconsistencies"][key]:
            lines.append(f"- `{prefix}`: `{count}`")
        lines.append("")
    lines.append("## Missing From QEMU Implementation (First 200)")
    lines.append("")
    for item in report["inconsistencies"]["compiler_only_vs_qemu_impl"][:200]:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Missing From AVS Translation Coverage (First 200)")
    lines.append("")
    for item in report["inconsistencies"]["compiler_only_vs_translation"][:200]:
        lines.append(f"- `{item}`")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate combined ISA-LLVM-QEMU coverage report")
    ap.add_argument("--spec", default="isa/v0.56/linxisa-v0.56.json", help="Path to compiled ISA JSON")
    ap.add_argument(
        "--compiler-analyzer",
        default="avs/compiler/linx-llvm/tests/analyze_coverage.py",
        help="Path to the LLVM compiler coverage analyzer",
    )
    ap.add_argument(
        "--compiler-out-dir",
        default="avs/compiler/linx-llvm/tests/out-linx64",
        help="Directory containing the active LLVM baremetal coverage outputs",
    )
    ap.add_argument(
        "--qemu-isa-report",
        default="docs/bringup/gates/qemu_isa_coverage_latest.json",
        help="Path to the machine-generated ISA-vs-QEMU implementation coverage report",
    )
    ap.add_argument(
        "--qemu-translation-report",
        default="docs/bringup/gates/qemu_translation_coverage_latest.json",
        help="Path to the machine-generated AVS QEMU translation coverage report",
    )
    ap.add_argument("--report-out", default="", help="Optional JSON report path")
    ap.add_argument("--out-md", default="", help="Optional Markdown summary path")
    ap.add_argument(
        "--require-coherent",
        action="store_true",
        help="Fail unless LLVM, QEMU implementation, and AVS translation coverage are all complete and aligned",
    )
    args = ap.parse_args(argv)

    spec_path = Path(args.spec).resolve()
    analyzer_path = Path(args.compiler_analyzer).resolve()
    compiler_out_dir = Path(args.compiler_out_dir).resolve()
    qemu_isa_report_path = Path(args.qemu_isa_report).resolve()
    qemu_translation_report_path = Path(args.qemu_translation_report).resolve()

    for path, label in (
        (spec_path, "ISA spec"),
        (analyzer_path, "compiler analyzer"),
        (qemu_isa_report_path, "QEMU ISA coverage report"),
        (qemu_translation_report_path, "QEMU translation coverage report"),
    ):
        if not path.is_file():
            print(f"error: {label} not found: {path}", file=sys.stderr)
            return 1
    if not compiler_out_dir.is_dir():
        print(f"error: compiler out dir not found: {compiler_out_dir}", file=sys.stderr)
        return 1

    analyzer = _load_module(analyzer_path)
    spec_data = analyzer.load_isa_spec(spec_path)
    llvm_results = analyzer.analyze_coverage(spec_data, compiler_out_dir)

    spec_mnemonics = set(spec_data["spec_unique_mnemonics"])
    llvm_covered = spec_mnemonics - set(llvm_results["missing_mnemonics"])

    qemu_isa_report = json.loads(qemu_isa_report_path.read_text(encoding="utf-8"))
    qemu_impl_covered = spec_mnemonics - set(qemu_isa_report["missing_spec_mnemonics"])

    qemu_translation_report = json.loads(qemu_translation_report_path.read_text(encoding="utf-8"))
    qemu_translation_covered = set(qemu_translation_report["covered_objects_by_mnemonic"].keys())

    compiler_only_vs_qemu_impl = sorted(llvm_covered - qemu_impl_covered)
    qemu_impl_only_vs_translation = sorted(qemu_impl_covered - qemu_translation_covered)
    translation_without_qemu_impl = sorted(qemu_translation_covered - qemu_impl_covered)
    compiler_only_vs_translation = sorted(llvm_covered - qemu_translation_covered)

    coherent = (
        llvm_covered == spec_mnemonics
        and qemu_impl_covered == spec_mnemonics
        and qemu_translation_covered == spec_mnemonics
        and not translation_without_qemu_impl
    )

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "schema_version": "isa-llvm-qemu-coverage-v1",
        "spec_path": str(spec_path),
        "compiler_analyzer": str(analyzer_path),
        "compiler_out_dir": str(compiler_out_dir),
        "qemu_isa_report": str(qemu_isa_report_path),
        "qemu_translation_report": str(qemu_translation_report_path),
        "spec_unique_mnemonics": len(spec_mnemonics),
        "llvm": {
            "coverage_count": len(llvm_covered),
            "coverage_ratio_percent": round(len(llvm_covered) / len(spec_mnemonics) * 100.0, 2) if spec_mnemonics else 0.0,
            "missing_count": len(spec_mnemonics - llvm_covered),
        },
        "qemu_impl": {
            "coverage_count": len(qemu_impl_covered),
            "coverage_ratio_percent": qemu_isa_report["coverage_ratio_percent"],
            "missing_count": len(spec_mnemonics - qemu_impl_covered),
        },
        "qemu_translation": {
            "coverage_count": len(qemu_translation_covered),
            "coverage_ratio_percent": qemu_translation_report["coverage_ratio_percent"],
            "missing_count": len(spec_mnemonics - qemu_translation_covered),
        },
        "inconsistencies": {
            "compiler_only_vs_qemu_impl_count": len(compiler_only_vs_qemu_impl),
            "compiler_only_vs_qemu_impl": compiler_only_vs_qemu_impl,
            "compiler_only_vs_qemu_impl_by_prefix": _top_counts(_bucket_counts(set(compiler_only_vs_qemu_impl))),
            "qemu_impl_only_vs_translation_count": len(qemu_impl_only_vs_translation),
            "qemu_impl_only_vs_translation": qemu_impl_only_vs_translation,
            "qemu_impl_only_vs_translation_by_prefix": _top_counts(_bucket_counts(set(qemu_impl_only_vs_translation))),
            "translation_without_qemu_impl_count": len(translation_without_qemu_impl),
            "translation_without_qemu_impl": translation_without_qemu_impl,
            "compiler_only_vs_translation_count": len(compiler_only_vs_translation),
            "compiler_only_vs_translation": compiler_only_vs_translation,
            "compiler_only_vs_translation_by_prefix": _top_counts(_bucket_counts(set(compiler_only_vs_translation))),
        },
        "result": {
            "ok": coherent if args.require_coherent else True,
            "classification": "isa_llvm_qemu_coverage_coherent" if coherent else "isa_llvm_qemu_coverage_inconsistent",
        },
    }

    if args.report_out:
        report_path = Path(args.report_out).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.out_md:
        _render_markdown(report, Path(args.out_md).resolve())

    if args.require_coherent and not coherent:
        print(
            "error: ISA-LLVM-QEMU coverage is inconsistent "
            f"(compiler_vs_qemu_impl={len(compiler_only_vs_qemu_impl)}, "
            f"qemu_impl_vs_translation={len(qemu_impl_only_vs_translation)}, "
            f"translation_without_qemu_impl={len(translation_without_qemu_impl)})",
            file=sys.stderr,
        )
        return 1

    print(
        "ok: generated ISA-LLVM-QEMU coverage report "
        f"(llvm={len(llvm_covered)}/{len(spec_mnemonics)}, "
        f"qemu_impl={len(qemu_impl_covered)}/{len(spec_mnemonics)}, "
        f"qemu_translation={len(qemu_translation_covered)}/{len(spec_mnemonics)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
