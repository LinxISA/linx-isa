#!/usr/bin/env python3
"""Run Linx bring-up gates from the canonical registry."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_PROFILES = {"dev", "release-strict"}
VALID_TIERS = {"pr", "nightly"}
REQUIRED_GATE_KEYS = {
    "gate_key",
    "domain",
    "owner",
    "command",
    "profiles",
    "tiers",
    "required",
    "artifacts",
    "freshness_hours",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def truthy_env(name: str) -> bool:
    value = os.environ.get(name, "").strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def load_registry(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: invalid gate registry JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"error: registry must be a JSON object: {path}")
    if data.get("schema_version") != 1:
        raise SystemExit(f"error: registry schema_version must be 1: {path}")
    owners = data.get("owners")
    if not isinstance(owners, list) or not all(isinstance(o, str) and o for o in owners):
        raise SystemExit("error: registry.owners must be a non-empty string list")
    gates = data.get("gates")
    if not isinstance(gates, list):
        raise SystemExit("error: registry.gates must be a list")
    seen: set[str] = set()
    owner_set = set(owners)
    for idx, gate in enumerate(gates):
        if not isinstance(gate, dict):
            raise SystemExit(f"error: registry gate #{idx} must be an object")
        missing = sorted(REQUIRED_GATE_KEYS - gate.keys())
        if missing:
            raise SystemExit(f"error: registry gate #{idx} missing keys: {', '.join(missing)}")
        gate_key = str(gate.get("gate_key", "")).strip()
        if "::" not in gate_key:
            raise SystemExit(f"error: invalid gate_key for gate #{idx}: {gate_key!r}")
        if gate_key in seen:
            raise SystemExit(f"error: duplicate gate_key: {gate_key}")
        seen.add(gate_key)
        owner = str(gate.get("owner", "")).strip()
        if owner not in owner_set:
            raise SystemExit(f"error: unknown owner for {gate_key}: {owner!r}")
        for field, valid in (("profiles", VALID_PROFILES), ("tiers", VALID_TIERS)):
            values = gate.get(field)
            if not isinstance(values, list) or not values:
                raise SystemExit(f"error: {gate_key}.{field} must be a non-empty list")
            bad = sorted(str(v) for v in values if v not in valid)
            if bad:
                raise SystemExit(f"error: {gate_key}.{field} has invalid values: {', '.join(bad)}")
        if not isinstance(gate.get("required"), bool):
            raise SystemExit(f"error: {gate_key}.required must be boolean")
        if not isinstance(gate.get("artifacts"), list):
            raise SystemExit(f"error: {gate_key}.artifacts must be a list")
        if not isinstance(gate.get("freshness_hours"), (int, float)):
            raise SystemExit(f"error: {gate_key}.freshness_hours must be numeric")
    return data


def default_registry(root: Path) -> Path:
    return root / "docs" / "bringup" / "gate_registry.json"


def resolve_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_tool(root: Path, rel: str) -> str:
    path = root / rel
    return str(path) if path.exists() else ""


def prepare_env(root: Path, profile: str, tier: str) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("ROOT", str(root))
    env.setdefault("LINXISA_ROOT", str(root))
    env.setdefault("LINX_BRINGUP_PROFILE", profile)
    env.setdefault("LINX_GATE_TIER", tier)
    env.setdefault("LINUX_ROOT", str(root / "kernel" / "linux"))
    env.setdefault("TOOLCHAIN_LANE", "pin")
    env.setdefault("QEMU_LANE", "pin")
    env.setdefault("LINX_DISABLE_TIMER_IRQ", "0")
    env.setdefault("LINX_EMU_DISABLE_TIMER_IRQ", "0")
    env.setdefault("CLANG", default_tool(root, "compiler/llvm/build-linxisa-clang/bin/clang"))
    env.setdefault("LLD", default_tool(root, "compiler/llvm/build-linxisa-clang/bin/ld.lld"))
    env.setdefault("QEMU", default_tool(root, "emulator/qemu/build/qemu-system-linx64"))
    if tier == "nightly":
        env.setdefault("QEMU_ISA_COVERAGE_REQUIRE_FULL", "1")
        env.setdefault("RUN_BUSYBOX_ROOTFS_GATE", "1")
    else:
        env.setdefault("QEMU_ISA_COVERAGE_REQUIRE_FULL", "0")
    if profile == "release-strict":
        env.setdefault("RUN_LINUX_DEFCONFIG_AUDIT", "1")
        env.setdefault("RUN_PTO_PARITY_GATE", "1")
    else:
        env.setdefault("RUN_LINUX_DEFCONFIG_AUDIT", "0")
        env.setdefault("RUN_PTO_PARITY_GATE", "0")
    return env


def gate_enabled(gate: dict[str, Any], profile: str, tier: str, include_optional: bool) -> bool:
    if profile not in gate["profiles"] or tier not in gate["tiers"]:
        return False
    env_flag = str(gate.get("enabled_if_env", "")).strip()
    if env_flag and not truthy_env(env_flag):
        return False
    if not bool(gate["required"]) and not include_optional:
        return False
    return True


def select_gates(
    registry: dict[str, Any],
    *,
    profile: str,
    tier: str,
    gate_filter: list[str],
    domain_filter: list[str],
    include_optional: bool,
) -> list[dict[str, Any]]:
    gates = [
        gate
        for gate in registry["gates"]
        if gate_enabled(gate, profile, tier, include_optional)
    ]
    if gate_filter:
        wanted = set(gate_filter)
        gates = [gate for gate in gates if gate["gate_key"] in wanted]
        missing = sorted(wanted - {gate["gate_key"] for gate in gates})
        if missing:
            raise SystemExit("error: selected gate not enabled or not found: " + ", ".join(missing))
    if domain_filter:
        wanted_domains = set(domain_filter)
        gates = [gate for gate in gates if gate["domain"] in wanted_domains]
        if not gates:
            raise SystemExit("error: no enabled gates match selected domain(s)")
    return gates


def list_gates(gates: list[dict[str, Any]]) -> None:
    for gate in gates:
        req = "required" if gate["required"] else "optional"
        print(f"{gate['gate_key']} [{gate['domain']}/{gate['owner']}/{req}]")


def run_gate(gate: dict[str, Any], env: dict[str, str], dry_run: bool) -> dict[str, Any]:
    print()
    print(f"-- {gate['gate_key']}")
    if dry_run:
        print(gate["command"])
        status = "not_run"
        rc = 0
    else:
        proc = subprocess.run(
            gate["command"],
            cwd=env["ROOT"],
            env=env,
            shell=True,
            executable="/bin/bash",
        )
        rc = proc.returncode
        status = "pass" if rc == 0 else "fail"
    artifact_state = check_artifacts(Path(env["ROOT"]), gate)
    if (
        not dry_run
        and status == "pass"
        and truthy_env("LINX_GATE_ENFORCE_FRESHNESS")
        and not artifact_state["ok"]
    ):
        status = "fail"
        rc = 1
    return {
        "gate_key": gate["gate_key"],
        "domain": gate["domain"],
        "owner": gate["owner"],
        "command": gate["command"],
        "required": bool(gate["required"]),
        "status": status,
        "returncode": rc,
        "artifacts": gate["artifacts"],
        "artifact_state": artifact_state,
        "freshness_hours": gate["freshness_hours"],
    }


def check_artifacts(root: Path, gate: dict[str, Any]) -> dict[str, Any]:
    max_age = float(gate.get("freshness_hours", 0))
    now = datetime.now(timezone.utc).timestamp()
    rows: list[dict[str, Any]] = []
    ok = True
    for raw in gate.get("artifacts", []):
        rel = str(raw)
        path = (root / rel).resolve()
        if not path.exists():
            rows.append({"path": rel, "status": "missing"})
            ok = False
            continue
        age_hours = (now - path.stat().st_mtime) / 3600.0
        stale = max_age > 0 and age_hours > max_age
        rows.append(
            {
                "path": rel,
                "status": "stale" if stale else "fresh",
                "age_hours": round(age_hours, 3),
                "freshness_hours": max_age,
            }
        )
        if stale:
            ok = False
    return {"ok": ok, "artifacts": rows}


def write_report(path: Path, profile: str, tier: str, dry_run: bool, rows: list[dict[str, Any]]) -> None:
    report = {
        "schema_version": 1,
        "generated_at_utc": utc_now(),
        "profile": profile,
        "tier": tier,
        "dry_run": dry_run,
        "result": {
            "ok": all(row["status"] in {"pass", "not_run"} or not row["required"] for row in rows),
            "gate_count": len(rows),
        },
        "gates": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"report: {path}")


def main(argv: list[str]) -> int:
    root = resolve_root()
    ap = argparse.ArgumentParser(description="Run Linx bring-up gates from docs/bringup/gate_registry.json")
    ap.add_argument("--registry", default=str(default_registry(root)))
    ap.add_argument("--profile", choices=sorted(VALID_PROFILES), default=os.environ.get("LINX_BRINGUP_PROFILE", "release-strict"))
    ap.add_argument("--tier", choices=sorted(VALID_TIERS), default=os.environ.get("LINX_GATE_TIER", "pr"))
    ap.add_argument("--gate", action="append", default=[], help="Run one enabled gate by exact gate_key; may repeat")
    ap.add_argument("--domain", action="append", default=[], help="Run enabled gates by domain; may repeat")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list", action="store_true", help="List selected gates and exit")
    ap.add_argument("--include-optional", action="store_true", help="Include optional gates selected for the profile/tier")
    ap.add_argument("--report-out", default="", help="Write a JSON run report")
    args = ap.parse_args(argv)

    registry = load_registry(Path(args.registry).resolve())
    env = prepare_env(root, args.profile, args.tier)
    os.environ.update(env)
    gates = select_gates(
        registry,
        profile=args.profile,
        tier=args.tier,
        gate_filter=args.gate,
        domain_filter=args.domain,
        include_optional=args.include_optional,
    )
    if args.list:
        list_gates(gates)
        return 0
    if not gates:
        raise SystemExit("error: no gates selected")

    rows: list[dict[str, Any]] = []
    failed_required = False
    for gate in gates:
        row = run_gate(gate, env, args.dry_run)
        rows.append(row)
        if row["returncode"] != 0 and row["required"]:
            failed_required = True
            break
    if args.report_out:
        write_report(Path(args.report_out).resolve(), args.profile, args.tier, args.dry_run, rows)
    if failed_required:
        return 1
    print()
    print("ok: selected gates complete" if not args.dry_run else "ok: selected gates listed in dry-run mode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
