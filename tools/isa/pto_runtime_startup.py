#!/usr/bin/env python3
"""Project the exact PTO four-PE runtime-startup ABI into LinxISA."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "isa/v0.58"
LOCK_PATH = PROFILE / "pto-runtime-startup.lock.json"
STATE_PATH = PROFILE / "state/pto_runtime_startup.json"

SOURCE_REPOSITORY = "https://github.com/PTO-ISA/pto-spec.git"
SOURCE_COMMIT = "2209562859a89be80b73ea926f5d60b9d018faae"
SOURCE_TREE = "9dc9e0aa528f381d74d0396c503b0682aa936b00"
SOURCE_PULL_REQUEST = "https://github.com/PTO-ISA/pto-spec/pull/417"

CLAUSES = {
    "asl/arch/state/kernel-lifecycle.asl": (
        "PTO-ARCH-KERNEL-LIFECYCLE-001",
        "PTO-ARCH-RUNTIME-STARTUP-ABI-001",
        "PTO-ARCH-RUNTIME-STARTUP-LIFETIME-001",
        "PTO-ARCH-RUNTIME-STARTUP-ADAPTATION-001",
    ),
    "asl/arch/state/core-synchronization.asl": (
        "PTO-ARCH-CORE-SYNCHRONIZATION-001",
    ),
    "asl/scalar/model/sys/semantics.asl": (
        "PTO-THREAD-ID-PE-IDENTITY-001",
    ),
}
CATALOGS = {
    "spec/catalog/scalar-forms.json": ("forms", "mnemonic", "SYNC.CORE"),
    "spec/catalog/system-registers.json": ("registers", "name", "THREAD_ID"),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def render(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def canonical_sha256(value: object) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    )


def git_bytes(repository: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
    ).stdout


def git_text(repository: Path, *arguments: str) -> str:
    return git_bytes(repository, *arguments).decode().strip()


def extract_clause(source: bytes, clause_id: str) -> bytes:
    marker = re.escape(clause_id.encode())
    pattern = re.compile(
        rb"^// NDF-BEGIN: " + marker + rb"\n.*?^// NDF-END: " + marker + rb"\n",
        re.MULTILINE | re.DOTALL,
    )
    matches = pattern.findall(source)
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one NDF region for {clause_id}, found {len(matches)}"
        )
    return matches[0]


def load_frozen_sources(
    source_root: Path,
    *,
    commit: str = SOURCE_COMMIT,
    tree: str = SOURCE_TREE,
) -> dict[str, bytes]:
    source_root = source_root.resolve()
    try:
        actual_tree = git_text(source_root, "rev-parse", f"{commit}^{{tree}}")
    except subprocess.CalledProcessError as error:
        raise ValueError(f"PTO source commit is unavailable: {commit}") from error
    if actual_tree != tree:
        raise ValueError(
            f"PTO source tree mismatch: expected {tree}, observed {actual_tree}"
        )

    sources: dict[str, bytes] = {}
    for path in (*CLAUSES, *CATALOGS):
        try:
            sources[path] = git_bytes(source_root, "show", f"{commit}:{path}")
        except subprocess.CalledProcessError as error:
            raise ValueError(f"PTO source blob is unavailable: {commit}:{path}") from error
    return sources


def build_documents(source_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    sources = load_frozen_sources(source_root)
    projected_clauses: list[dict[str, object]] = []
    source_records: dict[str, object] = {}
    for path, clause_ids in CLAUSES.items():
        source = sources[path]
        clause_records = []
        for clause_id in clause_ids:
            region = extract_clause(source, clause_id)
            record = {
                "id": clause_id,
                "sha256": sha256_bytes(region),
                "source_path": path,
                "text": region.decode(),
            }
            projected_clauses.append(record)
            clause_records.append({"id": clause_id, "sha256": record["sha256"]})
        source_records[path] = {
            "sha256": sha256_bytes(source),
            "clauses": clause_records,
        }

    catalog_bindings = {}
    for path, (list_key, identity_key, identity_value) in CATALOGS.items():
        source = sources[path]
        document = json.loads(source)
        matches = [
            row for row in document.get(list_key, [])
            if row.get(identity_key) == identity_value
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected exactly one {identity_value} catalog record, found {len(matches)}"
            )
        record = matches[0]
        catalog_bindings[identity_value] = record
        source_records[path] = {
            "sha256": sha256_bytes(source),
            "binding": {
                identity_key: identity_value,
                "sha256": canonical_sha256(record),
            },
        }

    state = {
        "source_lock": "isa/v0.58/pto-runtime-startup.lock.json",
        "status": "required-downstream-adaptation",
        "source_mode": "immutable-git-objects",
        "pto_runtime_startup": {
            "clauses": projected_clauses,
            "interface_bindings": catalog_bindings,
            "contract_state": "required-downstream-adaptation",
            "execution_support": {
                "sail": "decode-only-single-context",
                "four_pe_runtime_startup": "unsupported",
            },
        },
    }
    state_bytes = render(state).encode()
    lock = {
        "$schema": "https://docs.openclaw.ai/schemas/linxisa/pto_runtime_startup_lock.v1.json",
        "status": "required-downstream-adaptation",
        "source": {
            "repository": SOURCE_REPOSITORY,
            "commit": SOURCE_COMMIT,
            "tree": SOURCE_TREE,
            "pull_request": SOURCE_PULL_REQUEST,
            "mode": "immutable-git-objects",
        },
        "sources": source_records,
        "projection": {
            "path": "isa/v0.58/state/pto_runtime_startup.json",
            "sha256": sha256_bytes(state_bytes),
        },
        "existing_catalog_binding": {
            "lock": "isa/v0.58/pto-scalar-proposal.lock.json",
            "unchanged": True,
        },
    }
    return lock, state


def nested_records(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nested_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_records(child)


def validate_linx_bindings(root: Path, state: dict[str, object]) -> list[str]:
    errors = []
    system_path = root / "isa/v0.58/state/system_registers.json"
    scalar_path = root / "isa/v0.58/state/pto_scalar_forms.json"
    if not system_path.is_file() or not scalar_path.is_file():
        return ["missing Linx system-register or PTO scalar-form state"]
    systems = json.loads(system_path.read_text(encoding="utf-8"))
    records = list(nested_records(systems))
    base = systems.get("ssr", {}).get("base", [])
    identity_addresses = [row for row in base if int(row.get("id", "-1"), 0) == 0x26]
    if len(identity_addresses) != 1 or identity_addresses[0].get("name") != "THREAD_ID":
        errors.append("0x0026 must uniquely name THREAD_ID")
    thread_ids = [row for row in records if row.get("name") == "THREAD_ID"]
    if len(thread_ids) != 1:
        errors.append(f"expected one Linx THREAD_ID entry, found {len(thread_ids)}")
    elif {
        "id": thread_ids[0].get("id"),
        "access": thread_ids[0].get("access"),
        "width_bits": thread_ids[0].get("width_bits"),
    } != {"id": "0x0026", "access": "RO", "width_bits": 64}:
        errors.append("Linx THREAD_ID must be RO 0x0026 with XLEN=64")
    if any(
        int(row[key], 0) == 0x802
        for row in records for key in ("id", "idx") if key in row
    ):
        errors.append("retired 0x0802 PE identity alias must remain unassigned")

    scalar = json.loads(scalar_path.read_text(encoding="utf-8"))
    sync_forms = [row for row in scalar.get("forms", []) if row.get("mnemonic") == "SYNC.CORE"]
    expected = state["pto_runtime_startup"]["interface_bindings"]["SYNC.CORE"]
    if sync_forms != [expected]:
        errors.append("Linx SYNC.CORE form differs from the frozen PTO binding")
    upstream_thread = state["pto_runtime_startup"]["interface_bindings"]["THREAD_ID"]
    if upstream_thread != {
        "access": "RO", "address": "0x0026", "name": "THREAD_ID", "scope": "base"
    }:
        errors.append("frozen PTO THREAD_ID binding is not canonical RO 0x0026")
    return errors


def expected_outputs(source_root: Path) -> dict[Path, str]:
    lock, state = build_documents(source_root)
    return {LOCK_PATH: render(lock), STATE_PATH: render(state)}


def check_outputs(root: Path, outputs: dict[Path, str]) -> list[str]:
    errors = []
    for canonical_path, expected in outputs.items():
        path = root / canonical_path.relative_to(ROOT)
        if not path.is_file():
            errors.append(f"missing generated PTO runtime-startup projection: {path}")
        elif path.read_text(encoding="utf-8") != expected:
            errors.append(f"stale generated PTO runtime-startup projection: {path}")
    try:
        state = json.loads(outputs[STATE_PATH])
        errors.extend(validate_linx_bindings(root, state))
    except (KeyError, json.JSONDecodeError) as error:
        errors.append(f"invalid expected PTO runtime-startup state: {error}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source-root", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    arguments = parser.parse_args()

    try:
        outputs = expected_outputs(arguments.source_root)
        if arguments.write:
            for canonical_path, text in outputs.items():
                path = arguments.root.resolve() / canonical_path.relative_to(ROOT)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            print("wrote exact PTO runtime-startup lock and state projection")
            return 0
        errors = check_outputs(arguments.root.resolve(), outputs)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(f"error: {error}")
        return 1
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("OK: exact PTO runtime-startup projection is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
