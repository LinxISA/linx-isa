"""Bind release activation metadata to the reviewed component lock and evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = Path("isa/v0.59/release_qualification.json")
COMPONENT_LOCK = Path("docs/bringup/component-lock.v0.59.json")
PTO_LOCK = Path("isa/v0.59/pto-spec.lock.json")
REQUIRED_REPORTS = {
    "gate_consistency",
    "qemu_executable_coverage",
    "runtime_convergence_external",
    "runtime_convergence_pin",
    "sail",
    "scoped_scalar_numeric",
    "scoped_scalar_symbolic",
    "strict_cross_repo",
    "system_runtime",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qualification_reference(root: Path = ROOT) -> dict[str, str] | None:
    path = root / RECEIPT
    if not path.exists():
        return None
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict) or (
        receipt.get("schema_version"), receipt.get("profile"), receipt.get("version")
    ) != (1, "v0.59", "0.59.1"):
        raise ValueError("invalid LinxISA v0.59.1 qualification receipt")
    if not re.fullmatch(r"[0-9a-f]{40}", str(receipt.get("verification_commit", ""))):
        raise ValueError("qualification receipt must identify the verification commit")
    for key, lock in (("component_lock_sha256", COMPONENT_LOCK), ("pto_lock_sha256", PTO_LOCK)):
        if receipt.get(key) != _sha256(root / lock):
            raise ValueError(f"qualification receipt does not match {lock}")
    reports = receipt.get("reports")
    if not isinstance(reports, dict) or not REQUIRED_REPORTS <= reports.keys():
        raise ValueError("qualification receipt is missing required reports")
    for name in sorted(REQUIRED_REPORTS):
        report = reports[name]
        if (
            not isinstance(report, dict)
            or report.get("status") != "pass"
            or not re.fullmatch(r"[0-9a-f]{64}", str(report.get("sha256", "")))
        ):
            raise ValueError(f"qualification report is not a verified pass: {name}")
    return {"path": RECEIPT.as_posix(), "sha256": _sha256(path)}
