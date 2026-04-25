#!/usr/bin/env python3
"""
Validate LinxCore architecture contract docs and navigation wiring.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_TOPLEVEL_DOCS = [
    "docs/architecture/README.md",
    "docs/architecture/v0.4-architecture-contract.md",
]

CANONICAL_ARCH_DOCS = [
    "rtl/LinxCore/docs/architecture/overview.md",
    "rtl/LinxCore/docs/architecture/microarchitecture.md",
    "rtl/LinxCore/docs/architecture/interfaces.md",
    "rtl/LinxCore/docs/architecture/verification-matrix.md",
    "rtl/LinxCore/docs/architecture/module-catalog.md",
    "rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md",
]

PUBLISHED_ARCH_DOCS = [
    "docs/architecture/linxcore/overview.md",
    "docs/architecture/linxcore/microarchitecture.md",
    "docs/architecture/linxcore/interfaces.md",
    "docs/architecture/linxcore/verification-matrix.md",
    "docs/architecture/linxcore/module-catalog.md",
    "docs/architecture/linxcore/pipeline-stage-catalog.md",
]

REQUIRED_MATRIX_GATE_NAMES = [
    "Architecture::LinxCore architecture contract lint",
    "Architecture::mkdocs architecture nav/docs",
    "LinxCore::stage/connectivity lint",
    "LinxCore::opcode parity",
    "LinxCore::runner protocol",
    "LinxCore::trace schema and memory smoke",
    "LinxCore::cosim smoke",
    "Testbench::ROB bookkeeping",
    "Testbench::block struct pyc flow smoke",
    "pyCircuit::CPU C++ smoke",
    "pyCircuit::QEMU vs pyCircuit trace diff",
    "pyCircuit::interface contract gate",
    "LinxTrace::contract sync lint",
    "LinxTrace::sample trace lint",
    "LinxTrace::semver compatibility gate",
]

REQUIRED_CONTRACT_IDS = [
    "LC-ARCH-DOC-001",
    "LC-MA-PIPE-001",
    "LC-MA-HAZ-001",
    "LC-MA-BLK-001",
    "LC-MA-PRV-001",
    "LC-MA-MMU-001",
    "LC-MA-IRQ-001",
    "LC-MA-MEM-001",
    "LC-MA-FWD-001",
    "LC-IF-PYC-001",
    "LC-IF-PYC-002",
    "LC-IF-TRACE-001",
    "LC-IF-TRACE-002",
    "LC-IF-SYNC-001",
]


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _render_expected_mirror(rel: str, source_text: str) -> str:
    name = Path(rel).name
    lines = source_text.splitlines()
    header = [
        "<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->",
        f"<!-- Source: rtl/LinxCore/docs/architecture/{name} -->",
        "",
    ]
    if not lines:
        return "\n".join(header)
    first = lines[0]
    rest = lines[1:]
    note = [
        first,
        "",
        "> This published page mirrors the canonical LinxCore source in",
        f"> `rtl/LinxCore/docs/architecture/{name}`.",
        "",
    ]
    return "\n".join(header + note + rest) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate LinxCore architecture contract docs")
    ap.add_argument("--root", default=".", help="Repository root")
    ap.add_argument("--strict", action="store_true", help="Enable strict content checks")
    ap.add_argument("--require-mkdocs", action="store_true", help="Require mkdocs nav wiring")
    ap.add_argument("--out", default="", help="Optional JSON report output path")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_TOPLEVEL_DOCS + CANONICAL_ARCH_DOCS + PUBLISHED_ARCH_DOCS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required architecture doc: {rel}")

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    arch_readme = _load_text(root / "docs/architecture/README.md")
    for rel in PUBLISHED_ARCH_DOCS:
        if rel not in arch_readme and rel.replace("docs/", "") not in arch_readme:
            warnings.append(f"architecture README does not mention {rel}")
    if "rtl/LinxCore/docs/architecture/overview.md" not in arch_readme:
        warnings.append("architecture README does not mention canonical submodule LinxCore docs")

    for canonical_rel, published_rel in zip(CANONICAL_ARCH_DOCS, PUBLISHED_ARCH_DOCS):
        canonical_text = _load_text(root / canonical_rel)
        published_text = _load_text(root / published_rel)
        expected_text = _render_expected_mirror(published_rel, canonical_text)
        if published_text != expected_text:
            errors.append(f"published LinxCore mirror is out of sync: {published_rel}")

    if args.require_mkdocs:
        mkdocs_text = _load_text(root / "mkdocs.yml")
        required_nav_entries = [
            "architecture/linxcore/overview.md",
            "architecture/linxcore/microarchitecture.md",
            "architecture/linxcore/interfaces.md",
            "architecture/linxcore/verification-matrix.md",
            "architecture/linxcore/module-catalog.md",
            "architecture/linxcore/pipeline-stage-catalog.md",
        ]
        for nav_path in required_nav_entries:
            if nav_path not in mkdocs_text:
                errors.append(f"mkdocs.yml missing nav entry: {nav_path}")

    if args.strict:
        heading_requirements = {
            "rtl/LinxCore/docs/architecture/overview.md": [
                "# LinxCore v0.4 Superscalar Bring-up Overview",
                "## Scope",
                "## Normative links",
            ],
            "rtl/LinxCore/docs/architecture/microarchitecture.md": [
                "# LinxCore v0.4 Microarchitecture Contract",
                "## Baseline superscalar contract",
                "## Pipeline contract (LC-MA-PIPE-001)",
                "## Hazard and replay contract (LC-MA-HAZ-001)",
                "## Privilege/trap contract (LC-MA-PRV-001)",
                "## MMU contract (LC-MA-MMU-001)",
                "## Interrupt contract (LC-MA-IRQ-001)",
                "## Memory-ordering contract (LC-MA-MEM-001)",
            ],
            "rtl/LinxCore/docs/architecture/interfaces.md": [
                "# LinxCore External Interface Contracts",
                "## pyCircuit-LinxCore interface contract (LC-IF-PYC-001)",
                "## Required commit payload contract (LC-IF-PYC-002)",
                "## LinxTrace schema contract (LC-IF-TRACE-001)",
                "## Trace compatibility contract (LC-IF-TRACE-002)",
                "## Cross-tool synchronization contract (LC-IF-SYNC-001)",
            ],
            "rtl/LinxCore/docs/architecture/verification-matrix.md": [
                "# LinxCore v0.4 Verification Matrix",
                "## G1 contract rows (normative)",
                "## Gate-to-contract traceability (required PR gates)",
                "## PR mandatory matrix",
            ],
        }
        for rel, tokens in heading_requirements.items():
            text = _load_text(root / rel)
            for token in tokens:
                if token not in text:
                    errors.append(f"{rel} missing required token: {token}")

        v04_contract = _load_text(root / "docs/architecture/v0.4-architecture-contract.md")
        if "docs/architecture/linxcore/overview.md" not in v04_contract:
            errors.append("v0.4 architecture contract missing LinxCore overview cross-link")

        overview = _load_text(root / "rtl/LinxCore/docs/architecture/overview.md")
        if "docs/architecture/v0.4-architecture-contract.md" not in overview:
            errors.append("LinxCore overview missing v0.4 architecture contract cross-link")

        matrix_text = _load_text(root / "rtl/LinxCore/docs/architecture/verification-matrix.md")
        for gate_key in REQUIRED_MATRIX_GATE_NAMES:
            if gate_key not in matrix_text:
                errors.append(f"verification matrix missing gate key: {gate_key}")
        for contract_id in REQUIRED_CONTRACT_IDS:
            if contract_id not in matrix_text:
                errors.append(f"verification matrix missing contract id: {contract_id}")

    report = {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "checked_docs": REQUIRED_TOPLEVEL_DOCS + CANONICAL_ARCH_DOCS + PUBLISHED_ARCH_DOCS,
    }

    if args.out:
        out_path = (root / args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    for warn in warnings:
        print(f"warn: {warn}", file=sys.stderr)

    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    print("ok: LinxCore architecture contract checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
