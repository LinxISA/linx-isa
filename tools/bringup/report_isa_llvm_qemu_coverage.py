#!/usr/bin/env python3
"""Generate combined ISA/LLVM/QEMU L1 mapping coherence."""

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


def _partition_translation_inventory(
    spec_mnemonics: set[str],
    inventory_mnemonics: set[str],
) -> tuple[set[str], set[str], set[str]]:
    """Return spec-covered, missing-spec, and non-spec inventory mnemonics."""
    return (
        spec_mnemonics & inventory_mnemonics,
        spec_mnemonics - inventory_mnemonics,
        inventory_mnemonics - spec_mnemonics,
    )


def _validate_qemu_l1_report(report: dict[str, object]) -> str | None:
    if report.get("schema_version") != "qemu-isa-coverage-v3":
        return "expected qemu-isa-coverage-v3"
    if report.get("evidence_level") != "L1":
        return "expected evidence_level=L1"
    if report.get("claim") != "decoder_source_mapping":
        return "expected claim=decoder_source_mapping"
    evidence = report.get("evidence")
    if not isinstance(evidence, dict):
        return "missing evidence map"
    l1 = evidence.get("L1")
    if not isinstance(l1, dict) or l1.get("availability") != "available":
        return "L1 evidence is unavailable"
    if l1.get("mnemonic_count") != report.get("coverage_count"):
        return "L1 mnemonic count disagrees with compatibility count"
    if l1.get("form_count") != report.get("form_coverage_count"):
        return "L1 form count disagrees with compatibility count"
    return None


def _render_markdown(report: dict[str, object], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# ISA-LLVM-QEMU L1 Mapping Coherence")
    lines.append("")
    lines.append(f"- Generated (UTC): `{report['generated_at_utc']}`")
    lines.append(f"- Spec unique mnemonics: `{report['spec_unique_mnemonics']}`")
    lines.append("- QEMU evidence: `L1 decoder_source_mapping`")
    lines.append(
        f"- L2 runtime execution: `{report['qemu_evidence']['L2']['availability']}`"
    )
    lines.append(
        f"- L3 semantic oracle: `{report['qemu_evidence']['L3']['availability']}`"
    )
    lines.append(
        "- LLVM evidence is observed disassembly mnemonic breadth; it does not "
        "measure C-CodeGen or form-level coverage."
    )
    lines.append("- This report does not claim runtime or semantic completeness.")
    lines.append("")
    lines.append("| Surface | Covered | Ratio |")
    lines.append("| --- | --- | --- |")
    lines.append(
        f"| LLVM observed disassembly mnemonic breadth | `{report['llvm']['coverage_count']}/{report['spec_unique_mnemonics']}` | `{report['llvm']['coverage_ratio_percent']}%` |"
    )
    lines.append(
        f"| QEMU L1 decoder/source mapping | `{report['qemu_l1_mapping']['coverage_count']}/{report['spec_unique_mnemonics']}` | `{report['qemu_l1_mapping']['coverage_ratio_percent']}%` |"
    )
    lines.append(
        f"| QEMU AVS translation inventory | `{report['qemu_translation']['coverage_count']}/{report['spec_unique_mnemonics']}` | `{report['qemu_translation']['coverage_ratio_percent']}%` |"
    )
    lines.append("")
    lines.append(
        f"- Non-spec translation inventory tokens: `{report['qemu_translation']['non_spec_count']}`"
    )
    lines.append("")
    lines.append("## Inconsistency Summary")
    lines.append("")
    lines.append(
        f"- Compiler-covered but missing from QEMU L1 mapping: `{report['inconsistencies']['compiler_only_vs_qemu_l1_mapping_count']}`"
    )
    lines.append(
        f"- QEMU L1-mapped but missing from AVS translation inventory: `{report['inconsistencies']['qemu_l1_mapping_only_vs_translation_count']}`"
    )
    lines.append(
        f"- AVS translation-listed but absent from QEMU L1 mapping: `{report['inconsistencies']['translation_without_qemu_l1_mapping_count']}`"
    )
    lines.append(
        f"- Compiler-covered but missing from AVS translation coverage: `{report['inconsistencies']['compiler_only_vs_translation_count']}`"
    )
    lines.append("")
    for title, key in (
        ("Compiler vs QEMU L1 mapping", "compiler_only_vs_qemu_l1_mapping_by_prefix"),
        ("QEMU L1 mapping vs AVS translation", "qemu_l1_mapping_only_vs_translation_by_prefix"),
        ("Compiler vs AVS translation", "compiler_only_vs_translation_by_prefix"),
    ):
        lines.append(f"### {title}")
        lines.append("")
        for prefix, count in report["inconsistencies"][key]:
            lines.append(f"- `{prefix}`: `{count}`")
        lines.append("")
    lines.append("## Missing From QEMU L1 Mapping (First 200)")
    lines.append("")
    for item in report["inconsistencies"]["compiler_only_vs_qemu_l1_mapping"][:200]:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Missing From AVS Translation Coverage (First 200)")
    lines.append("")
    for item in report["inconsistencies"]["compiler_only_vs_translation"][:200]:
        lines.append(f"- `{item}`")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Generate combined ISA-LLVM-QEMU coverage report")
    ap.add_argument("--spec", default="isa/v0.58/linxisa-v0.58.json", help="Path to compiled ISA JSON")
    ap.add_argument(
        "--compiler-analyzer",
        default="avs/compiler/linx-llvm/tests/analyze_coverage.py",
        help="Path to the LLVM compiler coverage analyzer",
    )
    ap.add_argument(
        "--compiler-out-dir",
        default="avs/compiler/linx-llvm/tests/out",
        help="Directory containing the canonical run.sh compiler outputs",
    )
    ap.add_argument(
        "--qemu-isa-report",
        default="docs/bringup/gates/qemu_isa_coverage_latest.json",
        help="Path to the machine-generated ISA-vs-QEMU L1 source-mapping report",
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
        help="Fail unless LLVM, QEMU L1 mapping, and AVS translation inventory are complete and aligned",
    )
    return ap.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

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
    validation_error = _validate_qemu_l1_report(qemu_isa_report)
    if validation_error is not None:
        print(f"error: invalid QEMU L1 mapping report: {validation_error}", file=sys.stderr)
        return 1
    qemu_missing = {
        analyzer.canonicalize_mnemonic(str(mnemonic))
        for mnemonic in qemu_isa_report["missing_spec_mnemonics"]
    }
    qemu_missing.discard("")
    qemu_impl_covered = spec_mnemonics - qemu_missing

    qemu_translation_report = json.loads(qemu_translation_report_path.read_text(encoding="utf-8"))
    qemu_translation_inventory = set(
        qemu_translation_report["covered_objects_by_mnemonic"].keys()
    )
    (
        qemu_translation_covered,
        qemu_translation_missing,
        qemu_translation_extras,
    ) = _partition_translation_inventory(spec_mnemonics, qemu_translation_inventory)

    compiler_only_vs_qemu_impl = sorted(llvm_covered - qemu_impl_covered)
    qemu_impl_only_vs_translation = sorted(qemu_impl_covered - qemu_translation_covered)
    translation_without_qemu_impl = sorted(qemu_translation_covered - qemu_impl_covered)
    compiler_only_vs_translation = sorted(llvm_covered - qemu_translation_covered)

    coherent = (
        llvm_covered == spec_mnemonics
        and qemu_impl_covered == spec_mnemonics
        and qemu_translation_covered == spec_mnemonics
        and not qemu_translation_extras
        and not translation_without_qemu_impl
    )

    report: dict[str, object] = {
        "generated_at_utc": _utc_now(),
        "schema_version": "isa-llvm-qemu-l1-coherence-v3",
        "claim": "l1_mapping_coherence",
        "spec_path": str(spec_path),
        "compiler_analyzer": str(analyzer_path),
        "compiler_out_dir": str(compiler_out_dir),
        "qemu_isa_report": str(qemu_isa_report_path),
        "qemu_translation_report": str(qemu_translation_report_path),
        "spec_unique_mnemonics": len(spec_mnemonics),
        "llvm": {
            "claim": llvm_results["metric"],
            "metric_scope": llvm_results["metric_scope"],
            "not_measured": llvm_results["not_measured"],
            "coverage_count": len(llvm_covered),
            "coverage_ratio_percent": round(len(llvm_covered) / len(spec_mnemonics) * 100.0, 2) if spec_mnemonics else 0.0,
            "missing_count": len(spec_mnemonics - llvm_covered),
        },
        "qemu_l1_mapping": {
            "evidence_level": "L1",
            "claim": "decoder_source_mapping",
            "coverage_count": len(qemu_impl_covered),
            "coverage_ratio_percent": qemu_isa_report["coverage_ratio_percent"],
            "missing_count": len(spec_mnemonics - qemu_impl_covered),
        },
        "qemu_impl": {
            "deprecated_alias_for": "qemu_l1_mapping",
            "evidence_level": "L1",
            "claim": "decoder_source_mapping",
            "coverage_count": len(qemu_impl_covered),
            "coverage_ratio_percent": qemu_isa_report["coverage_ratio_percent"],
            "missing_count": len(spec_mnemonics - qemu_impl_covered),
        },
        "qemu_evidence": qemu_isa_report["evidence"],
        "qemu_translation": {
            "coverage_count": len(qemu_translation_covered),
            "coverage_ratio_percent": round(
                len(qemu_translation_covered) / len(spec_mnemonics) * 100.0,
                2,
            ) if spec_mnemonics else 0.0,
            "missing_count": len(qemu_translation_missing),
            "missing_spec_mnemonics": sorted(qemu_translation_missing),
            "inventory_count": len(qemu_translation_inventory),
            "non_spec_count": len(qemu_translation_extras),
            "non_spec_mnemonics": sorted(qemu_translation_extras),
        },
        "inconsistencies": {
            "compiler_only_vs_qemu_l1_mapping_count": len(compiler_only_vs_qemu_impl),
            "compiler_only_vs_qemu_l1_mapping": compiler_only_vs_qemu_impl,
            "compiler_only_vs_qemu_l1_mapping_by_prefix": _top_counts(_bucket_counts(set(compiler_only_vs_qemu_impl))),
            "qemu_l1_mapping_only_vs_translation_count": len(qemu_impl_only_vs_translation),
            "qemu_l1_mapping_only_vs_translation": qemu_impl_only_vs_translation,
            "qemu_l1_mapping_only_vs_translation_by_prefix": _top_counts(_bucket_counts(set(qemu_impl_only_vs_translation))),
            "translation_without_qemu_l1_mapping_count": len(translation_without_qemu_impl),
            "translation_without_qemu_l1_mapping": translation_without_qemu_impl,
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
            "translation_non_spec_count": len(qemu_translation_extras),
            "translation_non_spec_mnemonics": sorted(qemu_translation_extras),
        },
        "result": {
            "ok": coherent if args.require_coherent else True,
            "classification": "isa_llvm_qemu_l1_mapping_coherent" if coherent else "isa_llvm_qemu_l1_mapping_inconsistent",
            "runtime_execution_complete": None,
            "semantic_oracle_complete": None,
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
            "error: ISA-LLVM-QEMU L1 mapping is inconsistent "
            f"(compiler_vs_qemu_impl={len(compiler_only_vs_qemu_impl)}, "
            f"qemu_impl_vs_translation={len(qemu_impl_only_vs_translation)}, "
            f"translation_without_qemu_impl={len(translation_without_qemu_impl)})",
            file=sys.stderr,
        )
        return 1

    print(
        "ok: generated ISA-LLVM-QEMU L1 mapping coherence report "
        f"(llvm={len(llvm_covered)}/{len(spec_mnemonics)}, "
        f"qemu_impl={len(qemu_impl_covered)}/{len(spec_mnemonics)}, "
        f"qemu_translation={len(qemu_translation_covered)}/{len(spec_mnemonics)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
