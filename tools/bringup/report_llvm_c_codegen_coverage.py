#!/usr/bin/env python3
"""Report ISA mnemonic breadth produced specifically by AVS C/C++ CodeGen tests."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "linx-llvm-c-codegen-coverage-v1"
MANIFEST_SCHEMA_VERSION = "linx-c-codegen-build-v1"
REACHABLE_CONTRACT_SCHEMA_VERSION = "linx-plain-c-reachable-contract-v2"
CANONICAL_TARGET = "linx64-linx-none-elf"
CANONICAL_REACHABLE_CONTRACT_PATH = Path(
    "avs/compiler/linx-llvm/tests/plain_c_reachable_contract.json"
)
# This compact pin is intentionally outside the mutable contract. Additive
# tranches require one reviewed anchor update; the minimum must never decrease.
CANONICAL_REACHABLE_CONTRACT_ANCHOR = {
    "minimum_coverage_count": 146,
    "tranche_chain_sha256": "e319dd83314027a4a7c2552516fd02e253b46b72fa877166c0166d8f03bcff09",
}
SOURCE_SUFFIXES = (".c", ".cc", ".cpp", ".cxx")
CLANG_IDENT_RE = re.compile(r'^\s*\.ident\s+"(clang version [^"]+)"', re.MULTILINE)
FULL_GIT_REVISION_RE = re.compile(r"(?<![0-9a-f])([0-9a-f]{40})(?![0-9a-f])")
SOURCE_DIRECTIVE_RE = re.compile(
    r"\b(?:asm|__asm|__asm__)\b|\b__builtin_[A-Za-z0-9_]+\b"
)
ALIAS_PAIRS = (
    ("BSTART", "BSTART.STD"),
    ("BSTART", "C.BSTART.STD"),
    ("BSTART.STD", "C.BSTART.STD"),
    ("C.BSTART", "C.BSTART.STD"),
    ("BSTART.MPAR", "C.BSTART.MPAR"),
    ("BSTART.MSEQ", "C.BSTART.MSEQ"),
)


class ProvenanceError(RuntimeError):
    """Raised when C-CodeGen artifact provenance cannot be proven."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tranche_chain_descriptor(tranches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": tranche["id"],
            "sources": sorted(tranche["sources"]),
            "baseline_alias_closure_count": tranche[
                "baseline_alias_closure_count"
            ],
            "expected_coverage_count": tranche["expected_coverage_count"],
            "new_direct_mnemonics": sorted(tranche["new_direct_mnemonics"]),
        }
        for tranche in tranches
    ]


def _tranche_chain_sha256(tranches: list[dict[str, Any]]) -> str:
    descriptor = _tranche_chain_descriptor(tranches)
    canonical = json.dumps(
        descriptor, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return _sha256_bytes(canonical)


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location("linx_c_codegen_analyzer", path)
    if spec is None or spec.loader is None:
        raise ProvenanceError(f"unable to load compiler analyzer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tool_identity(path: Path) -> str:
    return subprocess.run(
        [str(path), "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]


def _verify_compiler_identity_revision(identity: str, llvm_head: str) -> str:
    """Require the Clang build stamp to name the exact current LLVM commit."""
    revisions = FULL_GIT_REVISION_RE.findall(identity.lower())
    if len(revisions) != 1:
        raise ProvenanceError(
            "canonical Clang identity does not report exactly one full Git revision"
        )
    revision = revisions[0]
    if revision != llvm_head.lower():
        raise ProvenanceError(
            "canonical Clang revision does not match current compiler/llvm HEAD: "
            f"{revision} != {llvm_head}"
        )
    return revision


def _current_llvm_head(root: Path) -> str:
    llvm_root = root / "compiler/llvm"
    return subprocess.run(
        ["git", "-C", str(llvm_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _verify_clean_llvm_worktree(root: Path) -> None:
    """Fail closed when source state is not exactly the reported LLVM commit."""
    llvm_root = root / "compiler/llvm"
    status = subprocess.run(
        ["git", "-C", str(llvm_root), "status", "--porcelain=v1", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if status:
        changed = ", ".join(line[3:] for line in status.splitlines()[:5])
        suffix = "" if len(status.splitlines()) <= 5 else ", ..."
        raise ProvenanceError(
            "compiler/llvm worktree is dirty; coverage cannot be bound to HEAD: "
            f"{changed}{suffix}"
        )


def _expected_compile_flags(root: Path, target: str, stem: str) -> list[str]:
    flags = [
        "-target",
        target,
        "-O2",
        "-ffreestanding",
        f"-I{root / 'compiler/llvm/clang/lib/Headers'}",
        f"-I{root / 'avs/runtime/freestanding/include'}",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-asynchronous-unwind-tables",
        "-fno-unwind-tables",
        "-fno-exceptions",
        "-fno-jump-tables",
    ]
    if stem == "31_jump_tables":
        flags.remove("-fno-jump-tables")
    return flags


def _verify_build_manifest(
    *,
    root: Path,
    manifest_path: Path,
    c_source_dir: Path,
    out_dir: Path,
    clang_path: Path,
    llvm_objdump_path: Path,
    replay: bool,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ProvenanceError("build manifest has the wrong schema")
    if manifest.get("status") != "complete":
        raise ProvenanceError("build manifest is not complete")
    records = manifest.get("records")
    if not isinstance(records, list) or manifest.get("source_count") != len(records):
        raise ProvenanceError("build manifest source_count is incomplete")

    sources = _source_map(c_source_dir)
    expected_source_paths = {_relative(path, root) for path in sources.values()}
    recorded_source_paths = [record.get("source") for record in records]
    if len(recorded_source_paths) != len(set(recorded_source_paths)):
        raise ProvenanceError("build manifest contains duplicate source records")
    if set(recorded_source_paths) != expected_source_paths:
        raise ProvenanceError("build manifest source set is not exact or complete")

    target = manifest.get("target")
    if not isinstance(target, str) or not target:
        raise ProvenanceError("build manifest target is missing")
    if target != CANONICAL_TARGET:
        raise ProvenanceError(
            f"build manifest target is not canonical: {target!r} != {CANONICAL_TARGET!r}"
        )
    if manifest.get("extra_cflags") != []:
        raise ProvenanceError("build manifest contains non-canonical EXTRA_CFLAGS")
    expected_tools = {
        "clang": clang_path,
        "llvm_objdump": llvm_objdump_path,
    }
    tools = manifest.get("tools")
    if not isinstance(tools, dict):
        raise ProvenanceError("build manifest tools are missing")
    for name, path in expected_tools.items():
        entry = tools.get(name)
        if not isinstance(entry, dict):
            raise ProvenanceError(f"build manifest tool is missing: {name}")
        if entry.get("path") != _relative(path, root):
            raise ProvenanceError(f"build manifest {name} path is not canonical")
        if entry.get("sha256") != _sha256(path):
            raise ProvenanceError(f"build manifest {name} SHA does not match current tool")
        if entry.get("identity") != _tool_identity(path):
            raise ProvenanceError(f"build manifest {name} identity does not match current tool")

    records_by_source = {record["source"]: record for record in records}
    for stem, source in sorted(sources.items()):
        record = records_by_source[_relative(source, root)]
        expected_paths = {
            "source": source,
            "generated_assembly": out_dir / stem / f"{stem}.s",
            "object": out_dir / stem / f"{stem}.o",
            "objdump": out_dir / stem / f"{stem}.objdump",
        }
        for label, path in expected_paths.items():
            if record.get(label) != _relative(path, root):
                raise ProvenanceError(
                    f"build manifest {label} path mismatch for {source}"
                )
            if not path.is_file() or record.get(f"{label}_sha256") != _sha256(path):
                raise ProvenanceError(
                    f"build manifest {label} hash mismatch for {source}"
                )
        flags = record.get("compile_flags")
        if not isinstance(flags, list) or not all(isinstance(flag, str) for flag in flags):
            raise ProvenanceError(f"build manifest compile flags are invalid for {source}")
        expected_flags = _expected_compile_flags(root, target, stem)
        if flags != expected_flags:
            raise ProvenanceError(
                f"build manifest flags do not match canonical run.sh policy for {source}"
            )

        if replay:
            with tempfile.TemporaryDirectory(prefix=f"linx-c-codegen-{stem}-") as td:
                temporary = Path(td)
                replay_object = temporary / f"{stem}.o"
                subprocess.run(
                    [str(clang_path), *flags, "-c", "-o", str(replay_object), str(source)],
                    check=True,
                    capture_output=True,
                )
                if _sha256(replay_object) != record["object_sha256"]:
                    raise ProvenanceError(
                        f"recompiled object hash mismatch for {source}"
                    )
                replay_objdump = subprocess.run(
                    [
                        str(llvm_objdump_path),
                        "-d",
                        f"--triple={target}",
                        replay_object.name,
                    ],
                    cwd=temporary,
                    check=True,
                    capture_output=True,
                ).stdout
                if _sha256_bytes(replay_objdump) != record["objdump_sha256"]:
                    raise ProvenanceError(
                        f"regenerated objdump hash mismatch for {source}"
                    )
    return manifest


def _source_map(source_dir: Path) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for suffix in SOURCE_SUFFIXES:
        for path in sorted(source_dir.glob(f"*{suffix}")):
            prior = sources.get(path.stem)
            if prior is not None:
                raise ProvenanceError(
                    f"ambiguous C/C++ provenance for stem {path.stem}: {prior} and {path}"
                )
            sources[path.stem] = path
    if not sources:
        raise ProvenanceError(f"no C/C++ sources found under {source_dir}")
    return sources


def _asm_stems(asm_dir: Path) -> set[str]:
    if not asm_dir.is_dir():
        return set()
    return {
        path.stem
        for suffix in (".s", ".S")
        for path in asm_dir.glob(f"*{suffix}")
        if path.is_file()
    }


def _excluded_reason(
    top_level_name: str, artifact_name: str, asm_stems: set[str]
) -> str:
    if top_level_name in asm_stems:
        return "hand-authored assembly source; not C/C++ CodeGen"
    if "roundtrip" in artifact_name.lower():
        return "roundtrip-only artifact; not C/C++ CodeGen"
    if top_level_name == "99_spec_decode":
        return "generated ISA disassembly vector; not C/C++ CodeGen"
    return "no current C/C++ source with the same stem"


def _collect_provenance(
    root: Path,
    c_source_dir: Path,
    asm_source_dir: Path,
    out_dir: Path,
    expected_compiler_identity: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], str]:
    sources = _source_map(c_source_dir)
    asm_stems = _asm_stems(asm_source_dir)
    ambiguous = sorted(set(sources) & asm_stems)
    if ambiguous:
        raise ProvenanceError(
            "source stems exist in both C/C++ and assembly lanes: " + ", ".join(ambiguous)
        )

    included: list[dict[str, Any]] = []
    identities: set[str] = set()
    included_objdumps: set[Path] = set()
    for stem, source in sorted(sources.items()):
        artifact_dir = out_dir / stem
        generated_asm = artifact_dir / f"{stem}.s"
        object_path = artifact_dir / f"{stem}.o"
        objdump_path = artifact_dir / f"{stem}.objdump"
        required = (generated_asm, object_path, objdump_path)
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise ProvenanceError(
                f"missing artifacts for C/C++ source {source}: " + ", ".join(missing)
            )

        source_mtime = source.stat().st_mtime_ns
        for artifact in required:
            if artifact.stat().st_mtime_ns < source_mtime:
                raise ProvenanceError(
                    f"stale artifact predates source {source}: {artifact}"
                )
        if objdump_path.stat().st_mtime_ns < object_path.stat().st_mtime_ns:
            raise ProvenanceError(
                f"stale disassembly predates object {object_path}: {objdump_path}"
            )

        match = CLANG_IDENT_RE.search(generated_asm.read_text(encoding="utf-8", errors="replace"))
        if match is None:
            raise ProvenanceError(
                f"generated assembly lacks a Clang identity for C/C++ source {source}: {generated_asm}"
            )
        identity = match.group(1)
        source_directives = sorted(set(SOURCE_DIRECTIVE_RE.findall(source.read_text())))
        identities.add(identity)
        included_objdumps.add(objdump_path.resolve())
        included.append(
            {
                "source": _relative(source, root),
                "generated_assembly": _relative(generated_asm, root),
                "object": _relative(object_path, root),
                "objdump": _relative(objdump_path, root),
                "source_sha256": _sha256(source),
                "object_sha256": _sha256(object_path),
                "objdump_sha256": _sha256(objdump_path),
                "compiler_identity": identity,
                "provenance_class": (
                    "source_directed" if source_directives else "pure_c_cpp"
                ),
                "source_directives": source_directives,
            }
        )

    if len(identities) != 1:
        raise ProvenanceError(
            "C/C++ artifacts have inconsistent compiler identities: "
            + "; ".join(sorted(identities))
        )
    actual_identity = next(iter(identities))
    if expected_compiler_identity is not None and actual_identity != expected_compiler_identity:
        raise ProvenanceError(
            "artifact compiler identity does not match canonical Clang: "
            f"{actual_identity!r} != {expected_compiler_identity!r}"
        )

    excluded: list[dict[str, str]] = []
    # Only direct per-test disassemblies are candidates for this gate. Nested
    # roundtrip/probe workspaces are outside the run.sh test-directory surface.
    candidate_objdumps = sorted(
        path
        for test_dir in out_dir.iterdir()
        if test_dir.is_dir()
        for path in test_dir.glob("*.objdump")
    )
    for objdump in candidate_objdumps:
        if objdump.resolve() in included_objdumps:
            continue
        try:
            top_level = objdump.relative_to(out_dir).parts[0]
        except (ValueError, IndexError):
            top_level = objdump.parent.name
        excluded.append(
            {
                "artifact": _relative(objdump, root),
                "reason": _excluded_reason(top_level, objdump.name, asm_stems),
            }
        )
    return included, excluded, actual_identity


def _apply_alias_closure(
    direct: set[str], spec_mnemonics: set[str]
) -> tuple[set[str], list[dict[str, str]]]:
    closed = set(direct)
    additions: list[dict[str, str]] = []
    for left, right in ALIAS_PAIRS:
        if left not in spec_mnemonics or right not in spec_mnemonics:
            continue
        if left not in closed and right in closed:
            closed.add(left)
            additions.append({"observed": right, "added_alias": left})
        elif right not in closed and left in closed:
            closed.add(right)
            additions.append({"observed": left, "added_alias": right})
    return closed, additions


def _verify_reachable_contract(
    *,
    root: Path,
    contract_path: Path,
    spec_mnemonics: set[str],
    observed_by_source: dict[str, list[str]],
    included: list[dict[str, Any]],
    pure_direct: set[str],
    pure_closed: set[str],
    enforce_canonical_anchor: bool = False,
) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != REACHABLE_CONTRACT_SCHEMA_VERSION:
        raise ProvenanceError("plain-C reachable contract has the wrong schema")
    if contract.get("status") != "frozen":
        raise ProvenanceError("plain-C reachable contract is not frozen")
    if contract.get("target") != CANONICAL_TARGET:
        raise ProvenanceError("plain-C reachable contract target is not canonical")
    tranches = contract.get("tranches")
    if not isinstance(tranches, list) or not tranches:
        raise ProvenanceError("plain-C reachable contract tranches are missing")
    entries = contract.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ProvenanceError("plain-C reachable contract entries are missing")
    expected_coverage_count = contract.get("expected_coverage_count")
    if (
        not isinstance(expected_coverage_count, int)
        or expected_coverage_count <= 0
        or len(entries) != expected_coverage_count
    ):
        raise ProvenanceError("plain-C reachable contract denominator is inconsistent")

    artifacts_by_source = {item["source"]: item for item in included}
    pure_sources = {
        source
        for source, artifact in artifacts_by_source.items()
        if artifact["provenance_class"] == "pure_c_cpp"
    }

    seen: set[str] = set()
    evidence_by_mnemonic: dict[str, str] = {}
    entry_by_mnemonic: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ProvenanceError("plain-C reachable contract entry is not an object")
        mnemonic = entry.get("mnemonic")
        source = entry.get("witness_source")
        evidence_kind = entry.get("evidence_kind")
        if not isinstance(mnemonic, str) or mnemonic not in spec_mnemonics:
            raise ProvenanceError(f"plain-C reachable contract mnemonic is unknown: {mnemonic!r}")
        if mnemonic in seen:
            raise ProvenanceError(f"plain-C reachable contract mnemonic is duplicated: {mnemonic}")
        seen.add(mnemonic)
        evidence_by_mnemonic[mnemonic] = evidence_kind
        entry_by_mnemonic[mnemonic] = entry
        artifact = artifacts_by_source.get(source)
        if artifact is None or source not in observed_by_source:
            raise ProvenanceError(f"plain-C reachable contract witness is missing: {source!r}")
        if artifact["provenance_class"] != "pure_c_cpp":
            raise ProvenanceError(
                f"plain-C reachable contract witness is source-directed: {source}"
            )
        observed = set(observed_by_source[source])
        if evidence_kind == "direct":
            if "observed_mnemonic" in entry or mnemonic not in observed:
                raise ProvenanceError(
                    f"plain-C direct witness does not observe {mnemonic}: {source}"
                )
        elif evidence_kind == "alias":
            observed_mnemonic = entry.get("observed_mnemonic")
            valid_alias = any(
                {mnemonic, observed_mnemonic} == {left, right}
                for left, right in ALIAS_PAIRS
            )
            if (
                not isinstance(observed_mnemonic, str)
                or observed_mnemonic not in observed
                or not valid_alias
            ):
                raise ProvenanceError(
                    f"plain-C alias witness is invalid for {mnemonic}: {source}"
                )
        else:
            raise ProvenanceError(
                f"plain-C reachable contract evidence kind is unknown: {evidence_kind!r}"
            )
        if mnemonic not in pure_closed:
            raise ProvenanceError(f"plain-C reachable mnemonic is not currently covered: {mnemonic}")

    tranche_ids: set[str] = set()
    all_tranche_sources: set[str] = set()
    parsed_tranches: list[tuple[str, set[str], list[str], int, int]] = []
    for tranche in tranches:
        if not isinstance(tranche, dict):
            raise ProvenanceError("plain-C reachable contract tranche is not an object")
        tranche_id = tranche.get("id")
        sources = tranche.get("sources")
        new_direct = tranche.get("new_direct_mnemonics")
        baseline_count = tranche.get("baseline_alias_closure_count")
        tranche_expected = tranche.get("expected_coverage_count")
        if (
            not isinstance(tranche_id, str)
            or not tranche_id
            or tranche_id in tranche_ids
        ):
            raise ProvenanceError("plain-C tranche id is missing or duplicated")
        tranche_ids.add(tranche_id)
        if (
            not isinstance(sources, list)
            or not sources
            or not all(isinstance(source, str) for source in sources)
            or len(sources) != len(set(sources))
        ):
            raise ProvenanceError(f"plain-C tranche source set is invalid: {tranche_id}")
        source_set = set(sources)
        if source_set & all_tranche_sources:
            raise ProvenanceError("plain-C tranche sources overlap")
        all_tranche_sources.update(source_set)
        if not source_set.issubset(pure_sources):
            raise ProvenanceError("plain-C tranche source is missing or source-directed")
        if (
            not isinstance(new_direct, list)
            or not new_direct
            or not all(isinstance(mnemonic, str) for mnemonic in new_direct)
            or len(new_direct) != len(set(new_direct))
            or any(evidence_by_mnemonic.get(mnemonic) != "direct" for mnemonic in new_direct)
        ):
            raise ProvenanceError("plain-C tranche mnemonic list is unknown or duplicated")
        if (
            not isinstance(baseline_count, int)
            or baseline_count < 0
            or not isinstance(tranche_expected, int)
            or tranche_expected <= baseline_count
        ):
            raise ProvenanceError("plain-C tranche coverage counts are invalid")
        parsed_tranches.append(
            (tranche_id, source_set, new_direct, baseline_count, tranche_expected)
        )

    canonical_anchor = None
    if enforce_canonical_anchor:
        minimum_count = CANONICAL_REACHABLE_CONTRACT_ANCHOR[
            "minimum_coverage_count"
        ]
        expected_digest = CANONICAL_REACHABLE_CONTRACT_ANCHOR[
            "tranche_chain_sha256"
        ]
        actual_digest = _tranche_chain_sha256(tranches)
        if expected_coverage_count < minimum_count:
            raise ProvenanceError(
                "plain-C canonical coverage is below the non-regression minimum"
            )
        if actual_digest != expected_digest:
            raise ProvenanceError(
                "plain-C canonical tranche chain does not match the non-regression anchor"
            )
        canonical_anchor = {
            "status": "PASS",
            "minimum_coverage_count": minimum_count,
            "tranche_chain_sha256": actual_digest,
        }

    # Tranches are frozen review history, not a request to reconstruct the
    # compiler state that existed when each source was added. A later generic
    # lowering can legitimately make an older source emit a mnemonic first
    # introduced by a newer tranche. Re-deriving tranche deltas from today's
    # source-set subtraction would then invalidate sound historical evidence.
    tranche_mnemonics: set[str] = set()
    for _, _, new_direct, _, _ in parsed_tranches:
        overlap = tranche_mnemonics & set(new_direct)
        if overlap:
            raise ProvenanceError(
                "plain-C tranche mnemonic history overlaps: "
                + ", ".join(sorted(overlap))
            )
        tranche_mnemonics.update(new_direct)

    historical_covered = seen - tranche_mnemonics
    initial_closed, _ = _apply_alias_closure(historical_covered, spec_mnemonics)
    verified_tranches: list[dict[str, Any]] = []
    aggregate_new_direct: list[str] = []
    for tranche_id, sources, new_direct, baseline_count, tranche_expected in parsed_tranches:
        baseline_closed, _ = _apply_alias_closure(
            historical_covered, spec_mnemonics
        )
        if baseline_count != len(baseline_closed):
            raise ProvenanceError(
                f"plain-C tranche baseline is inconsistent: {tranche_id}"
            )
        for mnemonic in new_direct:
            if entry_by_mnemonic[mnemonic]["witness_source"] not in sources:
                raise ProvenanceError(
                    f"plain-C tranche mnemonic witness is outside tranche sources: {mnemonic}"
                )
        next_covered = historical_covered | set(new_direct)
        next_closed, _ = _apply_alias_closure(next_covered, spec_mnemonics)
        if tranche_expected != len(next_closed):
            raise ProvenanceError(
                f"plain-C tranche expected coverage is inconsistent: {tranche_id}"
            )
        verified_tranches.append(
            {
                "id": tranche_id,
                "sources": sorted(sources),
                "baseline_alias_closure_count": len(baseline_closed),
                "new_direct_mnemonics": new_direct,
                "expected_coverage_count": len(next_closed),
            }
        )
        aggregate_new_direct.extend(new_direct)
        historical_covered = next_covered

    historical_closed, _ = _apply_alias_closure(
        historical_covered, spec_mnemonics
    )
    if (
        historical_closed != seen
        or pure_closed != seen
        or not pure_direct.issubset(pure_closed)
        or len(historical_closed) != expected_coverage_count
    ):
        raise ProvenanceError(
            "plain-C contract mnemonic set differs from independent baseline plus delta"
        )
    return {
        "schema_version": contract["schema_version"],
        "path": _relative(contract_path, root),
        "sha256": _sha256(contract_path),
        "target": contract["target"],
        "status": "PASS",
        "coverage_count": expected_coverage_count,
        "coverage_denominator": expected_coverage_count,
        "missing_count": 0,
        "missing_mnemonics": [],
        "baseline_alias_closure_count": len(initial_closed),
        "new_direct_mnemonics": aggregate_new_direct,
        "tranches": verified_tranches,
        "canonical_non_regression_anchor": canonical_anchor,
    }


def build_report(
    *,
    root: Path,
    spec_path: Path,
    analyzer_path: Path,
    c_source_dir: Path,
    asm_source_dir: Path,
    out_dir: Path,
    expected_compiler_identity: str | None = None,
    clang_path: Path | None = None,
    llvm_objdump_path: Path | None = None,
    manifest_path: Path | None = None,
    reachable_contract_path: Path | None = None,
    replay_manifest: bool = False,
    llvm_source_head: str | None = None,
    llvm_source_clean: bool | None = None,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    manifest = None
    if manifest_path is not None:
        if clang_path is None or llvm_objdump_path is None:
            raise ProvenanceError("manifest verification requires canonical compiler tools")
        manifest = _verify_build_manifest(
            root=root,
            manifest_path=manifest_path,
            c_source_dir=c_source_dir,
            out_dir=out_dir,
            clang_path=clang_path,
            llvm_objdump_path=llvm_objdump_path,
            replay=replay_manifest,
        )
    included, excluded, compiler_identity = _collect_provenance(
        root,
        c_source_dir,
        asm_source_dir,
        out_dir,
        expected_compiler_identity=expected_compiler_identity,
    )
    analyzer = _load_module(analyzer_path)
    spec_data = analyzer.load_isa_spec(spec_path)
    spec_mnemonics = set(spec_data["spec_unique_mnemonics"])

    emitted: set[str] = set()
    direct: set[str] = set()
    pure_direct: set[str] = set()
    unmapped: set[str] = set()
    observed_by_source: dict[str, list[str]] = {}
    for artifact in included:
        objdump_path = root / artifact["objdump"]
        raw = set(analyzer.extract_mnemonics_from_objdump(objdump_path))
        emitted |= raw
        mapped: set[str] = set()
        for mnemonic in raw:
            hit = analyzer.map_emitted_to_spec(mnemonic, spec_mnemonics)
            if hit is None:
                unmapped.add(mnemonic)
            else:
                mapped.add(hit)
        direct |= mapped
        if artifact["provenance_class"] == "pure_c_cpp":
            pure_direct |= mapped
        observed_by_source[artifact["source"]] = sorted(mapped)

    closed, alias_additions = _apply_alias_closure(direct, spec_mnemonics)
    pure_closed, pure_alias_additions = _apply_alias_closure(pure_direct, spec_mnemonics)
    reachable_contract = None
    if reachable_contract_path is not None:
        reachable_contract = _verify_reachable_contract(
            root=root,
            contract_path=reachable_contract_path,
            spec_mnemonics=spec_mnemonics,
            observed_by_source=observed_by_source,
            included=included,
            pure_direct=pure_direct,
            pure_closed=pure_closed,
            enforce_canonical_anchor=(
                reachable_contract_path.resolve()
                == (root / CANONICAL_REACHABLE_CONTRACT_PATH).resolve()
            ),
        )
    denominator = len(spec_mnemonics)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "claim": "c_cpp_source_oriented_observed_disassembly_mnemonic_breadth",
        "status": "MEASURED",
        "threshold": None,
        "threshold_met": None,
        "metric_scope": (
            "unique v0.58.3 ISA mnemonics observed in llvm-objdump disassembly of objects "
            "whose stems match current AVS C/C++ sources; pure CodeGen excludes sources "
            "with inline asm/builtins, and explicit alias closure is separate"
        ),
        "not_measured": [
            "encoding/form acceptance",
            "hand-authored assembly coverage",
            "runtime execution or semantic correctness",
        ],
        "provenance_rule": (
            "require a complete canonical run.sh build manifest with the exact current source "
            "set, exact flags, artifact and tool hashes; recompile every source with the "
            "manifest flags and regenerate objdump before accepting source-to-object-to-"
            "disassembly provenance"
        ),
        "inputs": {
            "spec": _relative(spec_path, root),
            "spec_sha256": _sha256(spec_path),
            "compiler_analyzer": _relative(analyzer_path, root),
            "compiler_analyzer_sha256": _sha256(analyzer_path),
            "c_source_dir": _relative(c_source_dir, root),
            "compiler_out_dir": _relative(out_dir, root),
            "compiler_identity": compiler_identity,
            "llvm_source_head": llvm_source_head,
            "llvm_source_clean": llvm_source_clean,
            "clang": _relative(clang_path, root) if clang_path is not None else None,
            "clang_sha256": _sha256(clang_path) if clang_path is not None else None,
            "llvm_objdump": (
                _relative(llvm_objdump_path, root)
                if llvm_objdump_path is not None
                else None
            ),
            "llvm_objdump_sha256": (
                _sha256(llvm_objdump_path) if llvm_objdump_path is not None else None
            ),
            "build_manifest": (
                _relative(manifest_path, root) if manifest_path is not None else None
            ),
            "build_manifest_sha256": (
                _sha256(manifest_path) if manifest_path is not None else None
            ),
            "manifest_status": manifest.get("status") if manifest is not None else None,
            "target": manifest.get("target") if manifest is not None else None,
            "replay_verified_source_count": (
                manifest.get("source_count")
                if manifest is not None and replay_manifest
                else 0
            ),
            "plain_c_reachable_contract": (
                _relative(reachable_contract_path, root)
                if reachable_contract_path is not None
                else None
            ),
        },
        "spec_unique_mnemonics": denominator,
        "direct": {
            "coverage_count": len(direct),
            "coverage_denominator": denominator,
            "coverage_ratio_percent": round(len(direct) * 100.0 / denominator, 3),
            "covered_mnemonics": sorted(direct),
            "missing_count": denominator - len(direct),
            "missing_mnemonics": sorted(spec_mnemonics - direct),
        },
        "alias_closure": {
            "coverage_count": len(closed),
            "coverage_denominator": denominator,
            "coverage_ratio_percent": round(len(closed) * 100.0 / denominator, 3),
            "covered_mnemonics": sorted(closed),
            "missing_count": denominator - len(closed),
            "missing_mnemonics": sorted(spec_mnemonics - closed),
            "additions": alias_additions,
        },
        "pure_codegen": {
            "source_count": sum(
                item["provenance_class"] == "pure_c_cpp" for item in included
            ),
            "excluded_source_directed_count": sum(
                item["provenance_class"] == "source_directed" for item in included
            ),
            "excluded_source_directed_sources": [
                {
                    "source": item["source"],
                    "directives": item["source_directives"],
                }
                for item in included
                if item["provenance_class"] == "source_directed"
            ],
            "direct_coverage_count": len(pure_direct),
            "alias_closure_coverage_count": len(pure_closed),
            "coverage_denominator": denominator,
            "direct_covered_mnemonics": sorted(pure_direct),
            "alias_closure_covered_mnemonics": sorted(pure_closed),
            "missing_mnemonics_after_alias_closure": sorted(
                spec_mnemonics - pure_closed
            ),
            "alias_additions": pure_alias_additions,
        },
        "plain_c_reachable_contract": reachable_contract,
        "emitted_unique_mnemonics": len(emitted),
        "unmapped_emitted_mnemonics": sorted(unmapped),
        "included_artifact_count": len(included),
        "included_artifacts": included,
        "excluded_artifact_count": len(excluded),
        "excluded_artifacts": excluded,
        "observed_by_source": observed_by_source,
    }


def _render_markdown(report: dict[str, Any], out_path: Path) -> None:
    direct = report["direct"]
    closed = report["alias_closure"]
    pure = report["pure_codegen"]
    contract = report["plain_c_reachable_contract"]
    lines = [
        "# LLVM C/C++ CodeGen ISA Mnemonic Breadth",
        "",
        f"- Generated (UTC): `{report['generated_at_utc']}`",
        f"- Status: `{report['status']}` (no target threshold is asserted)",
        f"- Pure CodeGen direct coverage: `{pure['direct_coverage_count']}/{pure['coverage_denominator']}`",
        f"- Pure CodeGen after alias closure: `{pure['alias_closure_coverage_count']}/{pure['coverage_denominator']}`",
        f"- C/C++ source-oriented direct coverage: `{direct['coverage_count']}/{direct['coverage_denominator']}` "
        f"(`{direct['coverage_ratio_percent']}%`)",
        f"- C/C++ source-oriented after explicit alias closure: `{closed['coverage_count']}/{closed['coverage_denominator']}` "
        f"(`{closed['coverage_ratio_percent']}%`)",
        (
            f"- Frozen plain-C reachable contract: `{contract['coverage_count']}/"
            f"{contract['coverage_denominator']}` (`{contract['status']}`)"
            if contract is not None
            else "- Frozen plain-C reachable contract: `UNAVAILABLE`"
        ),
        f"- Included C/C++ artifacts: `{report['included_artifact_count']}`",
        f"- Excluded disassembly artifacts: `{report['excluded_artifact_count']}`",
        f"- Compiler identity: `{report['inputs']['compiler_identity']}`",
        "",
        "Pure CodeGen excludes C/C++ sources containing inline asm or compiler builtins. "
        "The broader source-oriented boundary includes those tests but does not relabel "
        "their source-directed instructions as compiler-selected CodeGen. Neither metric "
        "reuses generated `99_spec_decode` or hand-authored assembly-lane artifacts.",
        "",
        "## Measurement Contract",
        "",
        f"- Metric scope: {report['metric_scope']}",
        f"- Provenance rule: {report['provenance_rule']}",
        "- Not measured:",
    ]
    lines.extend(f"  - {item}" for item in report["not_measured"])
    lines.extend(["", "## Frozen Plain-C Reachability Tranches", ""])
    if contract is not None:
        anchor = contract["canonical_non_regression_anchor"]
        if anchor is not None:
            lines.append(
                "- Canonical non-regression anchor: "
                f"`{anchor['status']}`; minimum "
                f"`{anchor['minimum_coverage_count']}`; tranche-chain SHA-256 "
                f"`{anchor['tranche_chain_sha256']}`"
            )
        for tranche in contract["tranches"]:
            new_direct = ", ".join(
                f"`{mnemonic}`" for mnemonic in tranche["new_direct_mnemonics"]
            )
            lines.append(
                f"- `{tranche['id']}`: baseline "
                f"`{tranche['baseline_alias_closure_count']}` -> "
                f"`{tranche['expected_coverage_count']}`; new direct: {new_direct}"
            )
    else:
        lines.append("- Unavailable")
    lines.extend(["", "## Source-Directed C/C++ Tests Excluded from Pure CodeGen", ""])
    for item in pure["excluded_source_directed_sources"]:
        directives = ", ".join(f"`{value}`" for value in item["directives"])
        lines.append(f"- `{item['source']}`: {directives}")
    lines.extend(["", "## Explicit Alias Additions", ""])
    if closed["additions"]:
        for item in closed["additions"]:
            lines.append(f"- `{item['observed']}` -> `{item['added_alias']}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Included Artifacts", ""])
    for item in report["included_artifacts"]:
        lines.append(f"- `{item['objdump']}` <- `{item['source']}`")

    lines.extend(["", "## Excluded Artifacts", ""])
    if report["excluded_artifacts"]:
        for item in report["excluded_artifacts"]:
            lines.append(f"- `{item['artifact']}`: {item['reason']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Missing Mnemonics After Alias Closure", ""])
    for mnemonic in closed["missing_mnemonics"]:
        lines.append(f"- `{mnemonic}`")
    if not closed["missing_mnemonics"]:
        lines.append("- None")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(default_root))
    parser.add_argument("--spec", default="isa/v0.58/linxisa-v0.58.json")
    parser.add_argument(
        "--compiler-analyzer",
        default="avs/compiler/linx-llvm/tests/analyze_coverage.py",
    )
    parser.add_argument("--c-source-dir", default="avs/compiler/linx-llvm/tests/c")
    parser.add_argument("--asm-source-dir", default="avs/compiler/linx-llvm/tests/asm")
    parser.add_argument("--compiler-out-dir", default="avs/compiler/linx-llvm/tests/out")
    parser.add_argument(
        "--clang", default="compiler/llvm/build-linxisa-clang/bin/clang"
    )
    parser.add_argument(
        "--llvm-objdump",
        default="compiler/llvm/build-linxisa-clang/bin/llvm-objdump",
    )
    parser.add_argument(
        "--build-manifest",
        default="avs/compiler/linx-llvm/tests/out/c-codegen-build-manifest.json",
    )
    parser.add_argument(
        "--reachable-contract",
        default="avs/compiler/linx-llvm/tests/plain_c_reachable_contract.json",
    )
    parser.add_argument(
        "--report-out",
        default="docs/bringup/gates/llvm_c_codegen_coverage_latest.json",
    )
    parser.add_argument(
        "--out-md",
        default="docs/bringup/gates/llvm_c_codegen_coverage_latest.md",
    )
    return parser.parse_args(argv)


def _under_root(root: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    root = Path(args.repo_root).resolve()
    spec_path = _under_root(root, args.spec)
    analyzer_path = _under_root(root, args.compiler_analyzer)
    c_source_dir = _under_root(root, args.c_source_dir)
    asm_source_dir = _under_root(root, args.asm_source_dir)
    out_dir = _under_root(root, args.compiler_out_dir)
    clang_path = _under_root(root, args.clang)
    llvm_objdump_path = _under_root(root, args.llvm_objdump)
    manifest_path = _under_root(root, args.build_manifest)
    reachable_contract_path = _under_root(root, args.reachable_contract)
    report_out = _under_root(root, args.report_out)
    out_md = _under_root(root, args.out_md)

    canonical = {
        "spec": root / "isa/v0.58/linxisa-v0.58.json",
        "compiler analyzer": root / "avs/compiler/linx-llvm/tests/analyze_coverage.py",
        "C/C++ source directory": root / "avs/compiler/linx-llvm/tests/c",
        "assembly source directory": root / "avs/compiler/linx-llvm/tests/asm",
        "compiler output lane": root / "avs/compiler/linx-llvm/tests/out",
        "Clang": root / "compiler/llvm/build-linxisa-clang/bin/clang",
        "llvm-objdump": root / "compiler/llvm/build-linxisa-clang/bin/llvm-objdump",
        "build manifest": (
            root
            / "avs/compiler/linx-llvm/tests/out/c-codegen-build-manifest.json"
        ),
        "plain-C reachable contract": (
            root
            / "avs/compiler/linx-llvm/tests/plain_c_reachable_contract.json"
        ),
    }
    actual = {
        "spec": spec_path,
        "compiler analyzer": analyzer_path,
        "C/C++ source directory": c_source_dir,
        "assembly source directory": asm_source_dir,
        "compiler output lane": out_dir,
        "Clang": clang_path,
        "llvm-objdump": llvm_objdump_path,
        "build manifest": manifest_path,
        "plain-C reachable contract": reachable_contract_path,
    }
    for label, expected in canonical.items():
        if actual[label].resolve() != expected.resolve():
            print(
                f"error: {label} must use canonical lane {expected.resolve()}, got {actual[label]}",
                file=sys.stderr,
            )
            return 2
    for label, path in actual.items():
        if not path.exists():
            print(f"error: missing {label}: {path}", file=sys.stderr)
            return 2

    try:
        clang_version = _tool_identity(clang_path)
        llvm_source_head = _current_llvm_head(root)
        _verify_clean_llvm_worktree(root)
        _verify_compiler_identity_revision(clang_version, llvm_source_head)
        report = build_report(
            root=root,
            spec_path=spec_path,
            analyzer_path=analyzer_path,
            c_source_dir=c_source_dir,
            asm_source_dir=asm_source_dir,
            out_dir=out_dir,
            expected_compiler_identity=clang_version,
            clang_path=clang_path,
            llvm_objdump_path=llvm_objdump_path,
            manifest_path=manifest_path,
            reachable_contract_path=reachable_contract_path,
            replay_manifest=True,
            llvm_source_head=llvm_source_head,
            llvm_source_clean=True,
        )
    except (
        OSError,
        KeyError,
        ValueError,
        IndexError,
        subprocess.CalledProcessError,
        ProvenanceError,
    ) as error:
        print(f"error: C-CodeGen coverage provenance failed: {error}", file=sys.stderr)
        return 2

    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _render_markdown(report, out_md)
    print(
        "LLVM C/C++ mnemonic breadth: "
        f"pure CodeGen {report['pure_codegen']['direct_coverage_count']}/"
        f"{report['spec_unique_mnemonics']} direct, "
        f"{report['pure_codegen']['alias_closure_coverage_count']}/"
        f"{report['spec_unique_mnemonics']} with aliases; "
        f"source-oriented {report['direct']['coverage_count']}/"
        f"{report['spec_unique_mnemonics']} direct, "
        f"{report['alias_closure']['coverage_count']}/"
        f"{report['spec_unique_mnemonics']} with aliases"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
