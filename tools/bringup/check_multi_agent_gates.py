#!/usr/bin/env python3
"""Strict multi-agent gate/checklist validator.

This validator has two modes:
- static: validate manifest/waiver/checklist integrity and ownership coverage metadata
- runtime: evaluate one gate-report run (lane+run-id) against strict multi-agent policy
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_GATE_STATUS = {"pass", "fail", "partial", "not_run"}
VALID_REGISTRY_PROFILES = {"dev", "release-strict"}
VALID_REGISTRY_TIERS = {"pr", "nightly"}
ID_RE = re.compile(r"\bID:\s*([A-Z0-9][A-Z0-9_-]*)\b")
GATE_KEY_RE = re.compile(r"^[^:\n]+::[^\n]+$")
FLOW_GATE_RE = re.compile(
    r"(?:^|\s)--gate(?:=|\s+)(?:'([^']+)'|\"([^\"]+)\"|([^\s]+))"
)
UTC_FMT = "%Y-%m-%d %H:%M:%SZ"

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_STATIC_FAIL = 10
EXIT_RUNTIME_FAIL = 11


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_str() -> str:
    return _utc_now().strftime(UTC_FMT)


def _load_mapping(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                f"failed to parse {path} as JSON and PyYAML is unavailable: {exc}"
            ) from exc
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must decode to an object mapping")
    return data


def _parse_utc(text: str, *, field: str) -> datetime:
    try:
        return datetime.strptime(text, UTC_FMT).replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise RuntimeError(f"invalid UTC timestamp in {field}: {text!r}") from exc


def _norm_gate_key(domain: str, gate: str) -> str:
    return f"{domain.strip()}::{gate.strip()}"


def _rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _repo_relative_path(
    value: Any,
    *,
    field: str,
    errors: list[dict[str, Any]],
) -> str | None:
    if not isinstance(value, str) or not value.strip():
        _err(errors, "E_REPO_REL_PATH", f"{field} must be a non-empty relative path", field=field)
        return None
    rel = value.strip()
    path = Path(rel)
    if path.is_absolute() or ".." in path.parts:
        _err(
            errors,
            "E_REPO_REL_PATH",
            f"{field} must stay inside the repository",
            field=field,
            path=rel,
        )
        return None
    return rel


def _err(errors: list[dict[str, Any]], code: str, message: str, **meta: Any) -> None:
    row: dict[str, Any] = {"code": code, "message": message}
    if meta:
        row.update(meta)
    errors.append(row)


def _warn(warnings: list[dict[str, Any]], code: str, message: str, **meta: Any) -> None:
    row: dict[str, Any] = {"code": code, "message": message}
    if meta:
        row.update(meta)
    warnings.append(row)


def _collect_checklist_ids(checklists_root: Path) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    found: dict[str, list[str]] = {}
    dups: dict[str, list[str]] = {}
    for md in sorted(checklists_root.glob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        ids = ID_RE.findall(text)
        found[_rel_posix(md, checklists_root)] = ids
        seen: set[str] = set()
        dup_list: list[str] = []
        for cid in ids:
            if cid in seen and cid not in dup_list:
                dup_list.append(cid)
            seen.add(cid)
        if dup_list:
            dups[_rel_posix(md, checklists_root)] = dup_list
    return found, dups


def _registry_gate_map(
    registry: dict[str, Any], *, errors: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != 1:
        _err(
            errors,
            "E_GATE_REGISTRY_VERSION",
            "gate registry schema_version must be 1",
            schema_version=registry.get("schema_version"),
        )

    owners_raw = registry.get("owners")
    owners: set[str] = set()
    if not isinstance(owners_raw, list) or not owners_raw:
        _err(
            errors,
            "E_GATE_REGISTRY_OWNERS",
            "gate registry owners must be a non-empty list",
        )
    else:
        for owner in owners_raw:
            if not isinstance(owner, str) or not owner.strip():
                _err(
                    errors,
                    "E_GATE_REGISTRY_OWNER_VALUE",
                    "gate registry owner entries must be non-empty strings",
                    owner=owner,
                )
                continue
            owner_norm = owner.strip()
            if owner_norm in owners:
                _err(
                    errors,
                    "E_GATE_REGISTRY_OWNER_DUP",
                    "gate registry owner entries must be unique",
                    owner=owner_norm,
                )
            owners.add(owner_norm)

    gates = registry.get("gates")
    if not isinstance(gates, list) or not gates:
        _err(errors, "E_GATE_REGISTRY_GATES", "gate registry gates must be a non-empty list")
        return {}

    gate_map: dict[str, dict[str, Any]] = {}
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            _err(
                errors,
                "E_GATE_REGISTRY_GATE_TYPE",
                "gate registry entry must be an object",
                index=index,
            )
            continue
        gate_key = str(gate.get("gate_key", "")).strip()
        domain = str(gate.get("domain", "")).strip()
        if not gate_key or not GATE_KEY_RE.match(gate_key):
            _err(
                errors,
                "E_GATE_REGISTRY_GATE_KEY",
                "gate registry gate_key must use Domain::Gate format",
                index=index,
                gate_key=gate_key,
            )
            continue
        if gate_key in gate_map:
            _err(
                errors,
                "E_GATE_REGISTRY_GATE_DUP",
                "gate registry gate_key must be unique",
                gate_key=gate_key,
            )
            continue
        if gate_key.split("::", 1)[0].strip() != domain:
            _err(
                errors,
                "E_GATE_REGISTRY_DOMAIN",
                "gate registry domain must match gate_key domain",
                gate_key=gate_key,
                domain=domain,
            )

        owner = gate.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            _err(
                errors,
                "E_GATE_REGISTRY_GATE_OWNER",
                "gate registry gate owner must be a non-empty string",
                gate_key=gate_key,
                owner=owner,
            )
        elif owners and owner.strip() not in owners:
            _err(
                errors,
                "E_GATE_REGISTRY_GATE_OWNER_UNKNOWN",
                "gate registry gate owner must be declared in registry owners",
                gate_key=gate_key,
                owner=owner.strip(),
            )

        command = gate.get("command")
        if not isinstance(command, str) or not command.strip():
            _err(
                errors,
                "E_GATE_REGISTRY_COMMAND",
                "gate registry command must be a non-empty string",
                gate_key=gate_key,
            )

        if not isinstance(gate.get("required"), bool):
            _err(
                errors,
                "E_GATE_REGISTRY_REQUIRED",
                "gate registry required must be a boolean",
                gate_key=gate_key,
                required=gate.get("required"),
            )

        for field in ("profiles", "tiers"):
            values = gate.get(field)
            if not isinstance(values, list) or not values:
                _err(
                    errors,
                    f"E_GATE_REGISTRY_{field.upper()}",
                    f"gate registry {field} must be a non-empty list",
                    gate_key=gate_key,
                )
                continue
            normalized: list[str] = []
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    _err(
                        errors,
                        f"E_GATE_REGISTRY_{field.upper()}_VALUE",
                        f"gate registry {field} entries must be non-empty strings",
                        gate_key=gate_key,
                        value=value,
                    )
                    continue
                normalized.append(value.strip())
            if len(normalized) != len(set(normalized)):
                _err(
                    errors,
                    f"E_GATE_REGISTRY_{field.upper()}_DUP",
                    f"gate registry {field} entries must be unique",
                    gate_key=gate_key,
                )
            valid_values = (
                VALID_REGISTRY_PROFILES if field == "profiles" else VALID_REGISTRY_TIERS
            )
            invalid_values = sorted(set(normalized) - valid_values)
            if invalid_values:
                _err(
                    errors,
                    f"E_GATE_REGISTRY_{field.upper()}_UNKNOWN",
                    f"gate registry {field} contains unsupported values",
                    gate_key=gate_key,
                    invalid_values=invalid_values,
                )

        artifacts = gate.get("artifacts")
        if not isinstance(artifacts, list):
            _err(
                errors,
                "E_GATE_REGISTRY_ARTIFACTS",
                "gate registry artifacts must be a list",
                gate_key=gate_key,
            )
        else:
            normalized_artifacts: list[str] = []
            for artifact in artifacts:
                artifact_norm = _repo_relative_path(
                    artifact,
                    field=f"gate_registry[{gate_key}].artifacts",
                    errors=errors,
                )
                if artifact_norm is not None:
                    normalized_artifacts.append(artifact_norm)
            if len(normalized_artifacts) != len(set(normalized_artifacts)):
                _err(
                    errors,
                    "E_GATE_REGISTRY_ARTIFACT_DUP",
                    "gate registry artifacts must be unique",
                    gate_key=gate_key,
                )

        freshness = gate.get("freshness_hours")
        if (
            isinstance(freshness, bool)
            or not isinstance(freshness, (int, float))
            or freshness <= 0
        ):
            _err(
                errors,
                "E_GATE_REGISTRY_FRESHNESS",
                "gate registry freshness_hours must be a positive number",
                gate_key=gate_key,
                freshness_hours=freshness,
            )

        enabled_if_env = gate.get("enabled_if_env")
        if enabled_if_env is not None and (
            not isinstance(enabled_if_env, str) or not enabled_if_env.strip()
        ):
            _err(
                errors,
                "E_GATE_REGISTRY_ENABLED_IF_ENV",
                "gate registry enabled_if_env must be a non-empty string when present",
                gate_key=gate_key,
            )
        gate_map[gate_key] = gate
    return gate_map


def _validate_phase_registry_alignment(
    phase_name: str,
    *,
    phase_gate_requirements: dict[str, dict[str, Any]],
    assignment_map: dict[str, dict[str, Any]],
    registry_gate_map: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
) -> None:
    phase_req = phase_gate_requirements.get(phase_name, {})
    phase_keys = phase_req.get("required_gate_keys", [])
    for gate_key in phase_keys:
        assignment = assignment_map.get(gate_key)
        if assignment is None:
            _err(
                errors,
                "E_PHASE_GATE_ASSIGNMENT_MISSING",
                "phase gate must exist exactly in manifest assignments",
                phase=phase_name,
                gate_key=gate_key,
            )
            continue
        registry_gate = registry_gate_map.get(gate_key)
        if registry_gate is None:
            _err(
                errors,
                "E_PHASE_GATE_NOT_REGISTERED",
                "phase gate must exist exactly in gate registry",
                phase=phase_name,
                gate_key=gate_key,
            )
            continue
        assigned_agent = str(assignment.get("agent", "")).strip()
        registry_owner = str(registry_gate.get("owner", "")).strip()
        if assigned_agent and registry_owner and assigned_agent != registry_owner:
            _err(
                errors,
                "E_PHASE_GATE_OWNER_DRIFT",
                "phase assignment agent must match gate registry owner",
                phase=phase_name,
                gate_key=gate_key,
                assignment_agent=assigned_agent,
                registry_owner=registry_owner,
            )


def _flow_gate_references(flow: dict[str, Any]) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    stages = flow.get("stages", [])
    if not isinstance(stages, list):
        return references
    for stage in stages:
        if not isinstance(stage, dict):
            continue
        stage_id = str(stage.get("id", "")).strip()
        commands = stage.get("commands", [])
        if not isinstance(commands, list):
            continue
        for command in commands:
            if not isinstance(command, dict):
                continue
            command_text = str(command.get("command", ""))
            if "run_gates.py" not in command_text:
                continue
            command_id = str(command.get("id", "")).strip()
            for match in FLOW_GATE_RE.finditer(command_text):
                gate_key = next(group for group in match.groups() if group is not None)
                references.append(
                    {
                        "stage_id": stage_id,
                        "command_id": command_id,
                        "gate_key": gate_key.strip(),
                    }
                )
    return references


def _validate_flow_gate_references(
    flow: dict[str, Any],
    registry_gate_map: dict[str, dict[str, Any]],
    *,
    errors: list[dict[str, Any]],
) -> None:
    for reference in _flow_gate_references(flow):
        if reference["gate_key"] not in registry_gate_map:
            _err(
                errors,
                "E_BENCHMARK_FLOW_GATE_UNKNOWN",
                "benchmark flow --gate reference is absent from gate registry",
                **reference,
            )


def _validate_benchmark_flow_policy(
    *,
    manifest: dict[str, Any],
    root: Path,
    agents: dict[str, Any],
    registry_gate_map: dict[str, dict[str, Any]],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    stats = {
        "enabled": False,
        "stages": 0,
    }
    policy = manifest.get("benchmark_flow_policy")
    if not isinstance(policy, dict):
        _err(errors, "E_BENCHMARK_FLOW_POLICY", "manifest.benchmark_flow_policy must be an object")
        return stats

    stats["enabled"] = True
    flow_rel = _repo_relative_path(
        policy.get("canonical_flow"),
        field="benchmark_flow_policy.canonical_flow",
        errors=errors,
    )
    runner_rel = _repo_relative_path(
        policy.get("canonical_runner"),
        field="benchmark_flow_policy.canonical_runner",
        errors=errors,
    )
    artifact_root = _repo_relative_path(
        policy.get("artifact_root"),
        field="benchmark_flow_policy.artifact_root",
        errors=errors,
    )

    if artifact_root and artifact_root != "workloads/generated":
        _err(
            errors,
            "E_BENCHMARK_FLOW_ARTIFACT_ROOT",
            "benchmark_flow_policy.artifact_root must be workloads/generated",
            artifact_root=artifact_root,
        )

    flow: dict[str, Any] = {}
    flow_stages: list[dict[str, Any]] = []
    if flow_rel:
        flow_path = root / flow_rel
        if not flow_path.exists():
            _err(
                errors,
                "E_BENCHMARK_FLOW_FILE",
                "benchmark flow file does not exist",
                path=flow_rel,
            )
        else:
            try:
                loaded_flow = json.loads(flow_path.read_text(encoding="utf-8"))
            except Exception as exc:
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_JSON",
                    f"failed to parse benchmark flow JSON: {exc}",
                    path=flow_rel,
                )
                loaded_flow = {}
            if not isinstance(loaded_flow, dict):
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_JSON",
                    "benchmark flow JSON must decode to an object",
                    path=flow_rel,
                )
                loaded_flow = {}
            flow = loaded_flow
            if flow:
                if flow.get("schema_version") != 1:
                    _err(
                        errors,
                        "E_BENCHMARK_FLOW_SCHEMA",
                        "benchmark flow schema_version must be 1",
                        path=flow_rel,
                    )
                stages_raw = flow.get("stages")
                if not isinstance(stages_raw, list) or not stages_raw:
                    _err(
                        errors,
                        "E_BENCHMARK_FLOW_STAGES",
                        "benchmark flow must declare non-empty stages",
                        path=flow_rel,
                    )
                else:
                    for stage in stages_raw:
                        if not isinstance(stage, dict):
                            _err(
                                errors,
                                "E_BENCHMARK_FLOW_STAGE",
                                "benchmark flow stage must be an object",
                                path=flow_rel,
                            )
                            continue
                        flow_stages.append(stage)

                _validate_flow_gate_references(
                    flow,
                    registry_gate_map,
                    errors=errors,
                )

    if runner_rel and not (root / runner_rel).exists():
        _err(
            errors,
            "E_BENCHMARK_FLOW_RUNNER",
            "benchmark flow runner does not exist",
            path=runner_rel,
        )

    stage_order_raw = policy.get("stage_order")
    stage_order: list[str] = []
    if not isinstance(stage_order_raw, list) or not stage_order_raw:
        _err(
            errors,
            "E_BENCHMARK_FLOW_STAGE_ORDER",
            "benchmark_flow_policy.stage_order must be a non-empty list",
        )
    else:
        seen_stage_ids: set[str] = set()
        for stage_id in stage_order_raw:
            if not isinstance(stage_id, str) or not stage_id.strip():
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_STAGE_ID",
                    "benchmark flow stage_order entries must be non-empty strings",
                    stage_id=stage_id,
                )
                continue
            norm = stage_id.strip()
            if norm in seen_stage_ids:
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_STAGE_DUP",
                    "benchmark flow stage_order entries must be unique",
                    stage_id=norm,
                )
                continue
            seen_stage_ids.add(norm)
            stage_order.append(norm)

    stage_owners_raw = policy.get("stage_owners")
    stage_owners: dict[str, str] = {}
    if not isinstance(stage_owners_raw, dict) or not stage_owners_raw:
        _err(
            errors,
            "E_BENCHMARK_FLOW_STAGE_OWNERS",
            "benchmark_flow_policy.stage_owners must be a non-empty object",
        )
    else:
        for stage_id, owner in stage_owners_raw.items():
            if not isinstance(stage_id, str) or not stage_id.strip():
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_STAGE_OWNER_KEY",
                    "benchmark flow stage owner key must be a non-empty string",
                    stage_id=stage_id,
                )
                continue
            if not isinstance(owner, str) or not owner.strip():
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_STAGE_OWNER",
                    "benchmark flow stage owner must be a non-empty string",
                    stage_id=stage_id,
                    owner=owner,
                )
                continue
            owner_norm = owner.strip()
            if owner_norm not in agents:
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_OWNER_UNKNOWN",
                    "benchmark flow stage owner must be a manifest agent",
                    stage_id=stage_id.strip(),
                    owner=owner_norm,
                )
            stage_owners[stage_id.strip()] = owner_norm

    if stage_order and stage_owners:
        missing_owners = sorted(set(stage_order) - set(stage_owners))
        extra_owners = sorted(set(stage_owners) - set(stage_order))
        if missing_owners or extra_owners:
            _err(
                errors,
                "E_BENCHMARK_FLOW_OWNER_COVERAGE",
                "benchmark_flow_policy.stage_owners must match stage_order",
                missing=missing_owners,
                extra=extra_owners,
            )

    if flow_stages:
        flow_stage_ids: list[str] = []
        seen_flow_stage_ids: set[str] = set()
        for stage in flow_stages:
            stage_id = str(stage.get("id", "")).strip()
            owner = str(stage.get("owner", "")).strip()
            if not stage_id:
                _err(errors, "E_BENCHMARK_FLOW_STAGE_ID", "flow stage missing id")
                continue
            if stage_id in seen_flow_stage_ids:
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_STAGE_DUP",
                    "flow stage ids must be unique",
                    stage_id=stage_id,
                )
                continue
            seen_flow_stage_ids.add(stage_id)
            flow_stage_ids.append(stage_id)
            if stage_owners and owner != stage_owners.get(stage_id):
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_OWNER_MISMATCH",
                    "flow stage owner must match benchmark_flow_policy.stage_owners",
                    stage_id=stage_id,
                    flow_owner=owner,
                    manifest_owner=stage_owners.get(stage_id),
                )
            if not bool(stage.get("hard_break", True)):
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_HARD_BREAK",
                    "benchmark flow stages must be hard breaks",
                    stage_id=stage_id,
                )
            commands = stage.get("commands")
            if not isinstance(commands, list) or not commands:
                _err(
                    errors,
                    "E_BENCHMARK_FLOW_COMMANDS",
                    "benchmark flow stages must declare commands",
                    stage_id=stage_id,
                )
        if stage_order and flow_stage_ids != stage_order:
            _err(
                errors,
                "E_BENCHMARK_FLOW_ORDER",
                "flow stage order must match benchmark_flow_policy.stage_order",
                manifest_order=stage_order,
                flow_order=flow_stage_ids,
            )
        stats["stages"] = len(flow_stage_ids)

    return stats


def _validate_static(
    manifest: dict[str, Any],
    waivers_doc: dict[str, Any],
    registry: dict[str, Any],
    checklists_root: Path,
    *,
    root: Path,
    strict_always: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    registry_gate_map = _registry_gate_map(registry, errors=errors)

    if manifest.get("version") != 1:
        _err(errors, "E_MANIFEST_VERSION", "manifest.version must be 1")

    policy = manifest.get("policy")
    if not isinstance(policy, dict):
        _err(errors, "E_MANIFEST_POLICY", "manifest.policy must be an object")
        policy = {}
    elif strict_always and policy.get("enforcement") != "strict_always":
        _err(
            errors,
            "E_POLICY_ENFORCEMENT",
            "manifest.policy.enforcement must be strict_always when --strict-always is set",
            enforcement=policy.get("enforcement"),
        )

    agent_scope_policy = manifest.get("agent_scope_policy")
    if agent_scope_policy is None:
        agent_scope_policy = {}
    elif not isinstance(agent_scope_policy, dict):
        _err(errors, "E_AGENT_SCOPE_POLICY", "manifest.agent_scope_policy must be an object")
        agent_scope_policy = {}

    explicit_modules_required = bool(agent_scope_policy.get("explicit_modules_required", False))
    allow_multi_module_agents = bool(agent_scope_policy.get("allow_multi_module_agents", False))

    max_modules_raw = agent_scope_policy.get("max_modules_per_agent", 1)
    if not isinstance(max_modules_raw, int) or max_modules_raw < 1:
        _err(
            errors,
            "E_SCOPE_MAX_MODULES",
            "agent_scope_policy.max_modules_per_agent must be an integer >= 1",
            value=max_modules_raw,
        )
        max_modules_per_agent = 1
    else:
        max_modules_per_agent = max_modules_raw

    allowed_modules_raw = agent_scope_policy.get("allowed_modules", [])
    allowed_modules: set[str] = set()
    if not isinstance(allowed_modules_raw, list):
        _err(errors, "E_SCOPE_ALLOWED_MODULES", "agent_scope_policy.allowed_modules must be a list")
    else:
        for module in allowed_modules_raw:
            if not isinstance(module, str) or not module.strip():
                _err(
                    errors,
                    "E_SCOPE_ALLOWED_MODULE_VALUE",
                    "allowed module must be non-empty string",
                    module=module,
                )
                continue
            allowed_modules.add(module.strip())

    canonical_skills_raw = agent_scope_policy.get("canonical_skill_names", [])
    canonical_skills: set[str] = set()
    if not isinstance(canonical_skills_raw, list):
        _err(errors, "E_SCOPE_CANONICAL_SKILLS", "agent_scope_policy.canonical_skill_names must be a list")
    else:
        for skill in canonical_skills_raw:
            if not isinstance(skill, str) or not skill.strip():
                _err(
                    errors,
                    "E_SCOPE_CANONICAL_SKILL_VALUE",
                    "canonical skill name must be non-empty string",
                    skill=skill,
                )
                continue
            canonical_skills.add(skill.strip())

    cross_module_agents_raw = agent_scope_policy.get("cross_module_agents", [])
    cross_module_agents: set[str] = set()
    if not isinstance(cross_module_agents_raw, list):
        _err(errors, "E_SCOPE_CROSS_MODULE_AGENTS", "agent_scope_policy.cross_module_agents must be a list")
    else:
        for agent in cross_module_agents_raw:
            if not isinstance(agent, str) or not agent.strip():
                _err(
                    errors,
                    "E_SCOPE_CROSS_MODULE_AGENT_VALUE",
                    "cross-module agent id must be non-empty string",
                    agent=agent,
                )
                continue
            cross_module_agents.add(agent.strip())

    domain_module_map_raw = agent_scope_policy.get("domain_module_map", {})
    domain_module_map: dict[str, set[str]] = {}
    if not isinstance(domain_module_map_raw, dict):
        _err(errors, "E_SCOPE_DOMAIN_MAP", "agent_scope_policy.domain_module_map must be an object")
    else:
        for domain, modules in domain_module_map_raw.items():
            if not isinstance(domain, str) or not domain.strip():
                _err(errors, "E_SCOPE_DOMAIN_KEY", "domain map key must be a non-empty string", domain=domain)
                continue
            if not isinstance(modules, list) or not modules:
                _err(
                    errors,
                    "E_SCOPE_DOMAIN_MODULES",
                    "domain map value must be non-empty list",
                    domain=domain,
                )
                continue
            module_set: set[str] = set()
            for module in modules:
                if not isinstance(module, str) or not module.strip():
                    _err(
                        errors,
                        "E_SCOPE_DOMAIN_MODULE_VALUE",
                        "domain map module must be non-empty string",
                        domain=domain,
                        module=module,
                    )
                    continue
                module_set.add(module.strip())
            domain_module_map[domain.strip()] = module_set

    phase_policy = manifest.get("phase_policy")
    if phase_policy is None:
        phase_policy = {}
    elif not isinstance(phase_policy, dict):
        _err(errors, "E_PHASE_POLICY", "manifest.phase_policy must be an object when present")
        phase_policy = {}

    phases_raw = phase_policy.get("phases", [])
    active_phase = str(phase_policy.get("active_phase", "")).strip()
    require_phase_bound_waivers = bool(phase_policy.get("require_phase_bound_waivers", False))

    phases: list[str] = []
    phase_set: set[str] = set()
    if phases_raw:
        if not isinstance(phases_raw, list):
            _err(errors, "E_PHASE_POLICY_PHASES", "phase_policy.phases must be a list")
        else:
            for phase in phases_raw:
                if not isinstance(phase, str) or not phase.strip():
                    _err(errors, "E_PHASE_POLICY_PHASE", "phase_policy phase entries must be non-empty strings")
                    continue
                norm = phase.strip()
                if norm in phase_set:
                    _err(errors, "E_PHASE_POLICY_DUP_PHASE", "phase_policy phase entries must be unique", phase=norm)
                    continue
                phase_set.add(norm)
                phases.append(norm)
    if active_phase:
        if active_phase not in phase_set:
            _err(
                errors,
                "E_PHASE_POLICY_ACTIVE",
                "phase_policy.active_phase must be listed in phase_policy.phases",
                active_phase=active_phase,
            )
    elif phase_set:
        _err(errors, "E_PHASE_POLICY_ACTIVE", "phase_policy.active_phase must be non-empty when phases are declared")

    agents = manifest.get("agents")
    if not isinstance(agents, dict) or not agents:
        _err(errors, "E_AGENTS", "manifest.agents must be a non-empty object")
        agents = {}

    checklists_decl = manifest.get("checklist_id_map")
    if not isinstance(checklists_decl, dict) or not checklists_decl:
        _err(errors, "E_CHECKLIST_MAP", "manifest.checklist_id_map must be a non-empty object")
        checklists_decl = {}

    if not checklists_root.exists() or not checklists_root.is_dir():
        _err(errors, "E_CHECKLIST_ROOT", f"checklists root not found: {checklists_root}")

    checklist_scan: dict[str, list[str]] = {}
    checklist_dups: dict[str, list[str]] = {}
    if checklists_root.exists() and checklists_root.is_dir():
        checklist_scan, checklist_dups = _collect_checklist_ids(checklists_root)

    for rel, dup_ids in checklist_dups.items():
        _err(
            errors,
            "E_CHECKLIST_DUPLICATE_ID",
            "checklist contains duplicate ID token(s)",
            checklist=rel,
            duplicate_ids=dup_ids,
        )

    declared_ids_global: set[str] = set()
    declared_path_ids: dict[str, set[str]] = {}
    for rel, ids in checklists_decl.items():
        if not isinstance(rel, str) or not rel.strip():
            _err(errors, "E_CHECKLIST_PATH", "checklist_id_map key must be a non-empty string", key=rel)
            continue
        if not isinstance(ids, list) or not ids:
            _err(
                errors,
                "E_CHECKLIST_IDS",
                "checklist_id_map entry must be a non-empty ID list",
                checklist=rel,
            )
            continue
        rel_norm = rel.strip()
        decl_set: set[str] = set()
        for cid in ids:
            if not isinstance(cid, str) or not cid.strip():
                _err(
                    errors,
                    "E_CHECKLIST_ID_VALUE",
                    "checklist ID must be a non-empty string",
                    checklist=rel_norm,
                    id=cid,
                )
                continue
            cid_norm = cid.strip()
            if cid_norm in declared_ids_global:
                _err(
                    errors,
                    "E_CHECKLIST_ID_REUSE",
                    "checklist ID must be globally unique",
                    id=cid_norm,
                    checklist=rel_norm,
                )
            declared_ids_global.add(cid_norm)
            decl_set.add(cid_norm)

        declared_path_ids[rel_norm] = decl_set

        expected_path = checklists_root / rel_norm
        if not expected_path.exists():
            _err(
                errors,
                "E_CHECKLIST_FILE_MISSING",
                "declared checklist file not found",
                checklist=rel_norm,
            )

        scanned = checklist_scan.get(rel_norm)
        if scanned is None:
            _err(
                errors,
                "E_CHECKLIST_SCAN_MISSING",
                "declared checklist is not present in checklist root scan",
                checklist=rel_norm,
            )
            continue

        scanned_set = set(scanned)
        if scanned_set != decl_set:
            _err(
                errors,
                "E_CHECKLIST_ID_MISMATCH",
                "declared checklist IDs do not match IDs parsed from markdown",
                checklist=rel_norm,
                declared=sorted(decl_set),
                parsed=sorted(scanned_set),
            )

    for scanned_rel in checklist_scan:
        if scanned_rel not in declared_path_ids:
            _err(
                errors,
                "E_CHECKLIST_UNDECLARED_FILE",
                "checklist file exists but is missing from checklist_id_map",
                checklist=scanned_rel,
            )

    agent_checklist: dict[str, str] = {}
    agent_modules: dict[str, set[str]] = {}
    multi_module_agent_count = 0
    for agent_id, meta in agents.items():
        if not isinstance(agent_id, str) or not agent_id.strip():
            _err(errors, "E_AGENT_KEY", "agent key must be a non-empty string", agent=agent_id)
            continue
        if not isinstance(meta, dict):
            _err(errors, "E_AGENT_META", "agent entry must be an object", agent=agent_id)
            continue
        owner = meta.get("owner")
        checklist = meta.get("checklist")
        if not isinstance(owner, str) or not owner.strip():
            _err(errors, "E_AGENT_OWNER", "agent.owner must be non-empty", agent=agent_id)
        if not isinstance(checklist, str) or not checklist.strip():
            _err(errors, "E_AGENT_CHECKLIST", "agent.checklist must be non-empty", agent=agent_id)
            continue
        checklist_norm = checklist.strip()
        agent_checklist[agent_id] = checklist_norm
        if checklist_norm not in declared_path_ids:
            _err(
                errors,
                "E_AGENT_CHECKLIST_UNKNOWN",
                "agent.checklist must reference checklist_id_map",
                agent=agent_id,
                checklist=checklist_norm,
            )

        modules = meta.get("modules")
        modules_norm: list[str] = []
        if explicit_modules_required or modules is not None:
            if not isinstance(modules, list) or not modules:
                _err(
                    errors,
                    "E_AGENT_MODULES",
                    "agent.modules must be a non-empty list when explicit_modules_required is enabled",
                    agent=agent_id,
                )
            else:
                for module in modules:
                    if not isinstance(module, str) or not module.strip():
                        _err(
                            errors,
                            "E_AGENT_MODULE_VALUE",
                            "agent module must be non-empty string",
                            agent=agent_id,
                            module=module,
                        )
                        continue
                    module_norm = module.strip()
                    modules_norm.append(module_norm)
                    if allowed_modules and module_norm not in allowed_modules:
                        _err(
                            errors,
                            "E_AGENT_MODULE_UNKNOWN",
                            "agent module must be listed in agent_scope_policy.allowed_modules",
                            agent=agent_id,
                            module=module_norm,
                        )

        if modules_norm:
            module_set = set(modules_norm)
            if len(module_set) != len(modules_norm):
                _err(
                    errors,
                    "E_AGENT_MODULE_DUP",
                    "agent.modules must not contain duplicates",
                    agent=agent_id,
                )
            agent_modules[agent_id] = module_set

            if len(module_set) > max_modules_per_agent:
                _err(
                    errors,
                    "E_AGENT_MODULE_COUNT",
                    "agent.modules exceeds max_modules_per_agent",
                    agent=agent_id,
                    modules=sorted(module_set),
                    max_modules=max_modules_per_agent,
                )

            if len(module_set) > 1:
                multi_module_agent_count += 1
                if not allow_multi_module_agents:
                    _err(
                        errors,
                        "E_AGENT_MULTI_MODULE_DISABLED",
                        "agent has multiple modules but allow_multi_module_agents is false",
                        agent=agent_id,
                        modules=sorted(module_set),
                    )
                elif agent_id not in cross_module_agents:
                    _err(
                        errors,
                        "E_AGENT_MULTI_MODULE_UNAUTHORIZED",
                        "multi-module agent must be listed in cross_module_agents",
                        agent=agent_id,
                        modules=sorted(module_set),
                    )

        skill = meta.get("skill")
        if canonical_skills or skill is not None:
            if not isinstance(skill, str) or not skill.strip():
                _err(errors, "E_AGENT_SKILL", "agent.skill must be non-empty", agent=agent_id)
            else:
                skill_norm = skill.strip()
                if re.match(r"^linx-[a-z0-9][a-z0-9-]*$", skill_norm) is None:
                    _err(
                        errors,
                        "E_AGENT_SKILL_FORMAT",
                        "agent.skill must follow canonical linx-<module> naming",
                        agent=agent_id,
                        skill=skill_norm,
                    )
                if canonical_skills and skill_norm not in canonical_skills:
                    _err(
                        errors,
                        "E_AGENT_SKILL_UNKNOWN",
                        "agent.skill must be present in canonical_skill_names",
                        agent=agent_id,
                        skill=skill_norm,
                    )

    for agent_id in sorted(cross_module_agents):
        if agent_id not in agents:
            _err(
                errors,
                "E_SCOPE_CROSS_MODULE_AGENT_UNKNOWN",
                "cross_module_agents entry is not a known agent",
                agent=agent_id,
            )

    benchmark_flow_stats = _validate_benchmark_flow_policy(
        manifest=manifest,
        root=root,
        agents=agents,
        registry_gate_map=registry_gate_map,
        errors=errors,
    )

    assignments = manifest.get("gate_assignments")
    if not isinstance(assignments, list) or not assignments:
        _err(errors, "E_ASSIGNMENTS", "manifest.gate_assignments must be a non-empty list")
        assignments = []

    assignment_map: dict[str, dict[str, Any]] = {}
    assignment_domains: set[str] = set()
    for idx, item in enumerate(assignments):
        if not isinstance(item, dict):
            _err(errors, "E_ASSIGNMENT_TYPE", "gate assignment must be an object", index=idx)
            continue

        gate_key = item.get("gate_key")
        agent = item.get("agent")
        checklist_ids = item.get("checklist_ids")

        if not isinstance(gate_key, str) or not gate_key.strip():
            _err(errors, "E_ASSIGNMENT_GATE_KEY", "gate_key must be a non-empty string", index=idx)
            continue
        gate_key = gate_key.strip()

        if not GATE_KEY_RE.match(gate_key):
            _err(
                errors,
                "E_ASSIGNMENT_GATE_KEY_FORMAT",
                "gate_key must use Domain::Gate format",
                gate_key=gate_key,
            )

        if gate_key in assignment_map:
            _err(errors, "E_ASSIGNMENT_DUP_GATE", "duplicate gate_key in assignments", gate_key=gate_key)
            continue

        if not isinstance(agent, str) or not agent.strip():
            _err(errors, "E_ASSIGNMENT_AGENT", "assignment.agent must be non-empty", gate_key=gate_key)
            continue
        agent = agent.strip()
        if agent not in agents:
            _err(
                errors,
                "E_ASSIGNMENT_AGENT_UNKNOWN",
                "assignment.agent not found in agents",
                gate_key=gate_key,
                agent=agent,
            )

        if not isinstance(checklist_ids, list) or not checklist_ids:
            _err(
                errors,
                "E_ASSIGNMENT_CHECKLIST_IDS",
                "assignment.checklist_ids must be non-empty list",
                gate_key=gate_key,
            )
            continue

        if agent in agent_checklist:
            agent_checklist_name = agent_checklist[agent]
            agent_id_set = declared_path_ids.get(agent_checklist_name, set())
        else:
            agent_checklist_name = ""
            agent_id_set = set()

        domain = gate_key.split("::", 1)[0].strip()
        assignment_domains.add(domain)
        scoped_modules = domain_module_map.get(domain)
        if scoped_modules is not None:
            modules_for_agent = agent_modules.get(agent, set())
            if not modules_for_agent:
                _err(
                    errors,
                    "E_ASSIGNMENT_AGENT_MODULES_MISSING",
                    "assignment agent is missing modules required by domain scope policy",
                    gate_key=gate_key,
                    agent=agent,
                    domain=domain,
                )
            elif modules_for_agent.isdisjoint(scoped_modules):
                _err(
                    errors,
                    "E_ASSIGNMENT_AGENT_MODULE_SCOPE",
                    "assignment agent modules do not match domain scope",
                    gate_key=gate_key,
                    agent=agent,
                    domain=domain,
                    agent_modules=sorted(modules_for_agent),
                    expected_modules=sorted(scoped_modules),
                )

        for cid in checklist_ids:
            if not isinstance(cid, str) or not cid.strip():
                _err(
                    errors,
                    "E_ASSIGNMENT_CHECKLIST_ID_VALUE",
                    "assignment checklist id must be non-empty string",
                    gate_key=gate_key,
                    id=cid,
                )
                continue
            cid_norm = cid.strip()
            if cid_norm not in declared_ids_global:
                _err(
                    errors,
                    "E_ASSIGNMENT_CHECKLIST_ID_UNKNOWN",
                    "assignment checklist id not declared in checklist_id_map",
                    gate_key=gate_key,
                    id=cid_norm,
                )
            elif cid_norm not in agent_id_set:
                _err(
                    errors,
                    "E_ASSIGNMENT_CHECKLIST_ID_WRONG_AGENT",
                    "assignment checklist id is not part of assigned agent checklist",
                    gate_key=gate_key,
                    id=cid_norm,
                    agent=agent,
                    agent_checklist=agent_checklist_name,
                )

        assignment_map[gate_key] = item

    if domain_module_map:
        missing_domains = sorted(assignment_domains - set(domain_module_map.keys()))
        if missing_domains:
            _err(
                errors,
                "E_SCOPE_DOMAIN_MAP_MISSING",
                "domain_module_map must cover all assignment domains",
                missing_domains=missing_domains,
            )

    phase_gate_requirements_raw = manifest.get("phase_gate_requirements")
    phase_gate_requirements: dict[str, dict[str, Any]] = {}
    if phase_gate_requirements_raw is None:
        phase_gate_requirements_raw = {}
    if not isinstance(phase_gate_requirements_raw, dict):
        _err(
            errors,
            "E_PHASE_GATE_REQUIREMENTS",
            "manifest.phase_gate_requirements must be an object when present",
        )
        phase_gate_requirements_raw = {}

    for phase_name, req in phase_gate_requirements_raw.items():
        if not isinstance(phase_name, str) or not phase_name.strip():
            _err(
                errors,
                "E_PHASE_GATE_REQUIREMENT_PHASE",
                "phase_gate_requirements key must be non-empty phase name",
                phase=phase_name,
            )
            continue
        phase_name_norm = phase_name.strip()
        if phase_set and phase_name_norm not in phase_set:
            _err(
                errors,
                "E_PHASE_GATE_REQUIREMENT_UNKNOWN_PHASE",
                "phase_gate_requirements phase must be listed in phase_policy.phases",
                phase=phase_name_norm,
            )

        if not isinstance(req, dict):
            _err(
                errors,
                "E_PHASE_GATE_REQUIREMENT_TYPE",
                "phase_gate_requirements phase entry must be an object",
                phase=phase_name_norm,
            )
            continue

        required_gate_keys_raw = req.get("required_gate_keys")
        if not isinstance(required_gate_keys_raw, list) or not required_gate_keys_raw:
            _err(
                errors,
                "E_PHASE_GATE_REQUIREMENT_KEYS",
                "phase_gate_requirements.required_gate_keys must be a non-empty list",
                phase=phase_name_norm,
            )
            continue

        required_gate_keys: list[str] = []
        seen_gate_keys: set[str] = set()
        for gate_key in required_gate_keys_raw:
            if not isinstance(gate_key, str) or not gate_key.strip():
                _err(
                    errors,
                    "E_PHASE_GATE_REQUIREMENT_KEY_VALUE",
                    "phase required gate key must be non-empty string",
                    phase=phase_name_norm,
                    gate_key=gate_key,
                )
                continue
            gate_key_norm = gate_key.strip()
            if gate_key_norm in seen_gate_keys:
                _err(
                    errors,
                    "E_PHASE_GATE_REQUIREMENT_KEY_DUP",
                    "phase required gate keys must be unique",
                    phase=phase_name_norm,
                    gate_key=gate_key_norm,
                )
                continue
            seen_gate_keys.add(gate_key_norm)
            if gate_key_norm not in assignment_map:
                _err(
                    errors,
                    "E_PHASE_GATE_REQUIREMENT_KEY_UNKNOWN",
                    "phase required gate key must exist in gate_assignments",
                    phase=phase_name_norm,
                    gate_key=gate_key_norm,
                )
                continue
            required_gate_keys.append(gate_key_norm)

        if required_gate_keys:
            phase_gate_requirements[phase_name_norm] = {
                "required_gate_keys": required_gate_keys,
            }

    registry_enforced_phases = {active_phase, "WORKLOAD-RUNTIME"} - {""}
    for phase_name in sorted(registry_enforced_phases):
        _validate_phase_registry_alignment(
            phase_name,
            phase_gate_requirements=phase_gate_requirements,
            assignment_map=assignment_map,
            registry_gate_map=registry_gate_map,
            errors=errors,
        )

    for gate_key in sorted(assignment_map):
        if gate_key.startswith("Workloads::") and gate_key not in registry_gate_map:
            _err(
                errors,
                "E_WORKLOAD_ASSIGNMENT_NOT_REGISTERED",
                "Workloads assignment must exist exactly in gate registry",
                gate_key=gate_key,
            )
    waivers_version = waivers_doc.get("version")
    if waivers_version != 1:
        _err(errors, "E_WAIVER_VERSION", "waivers.version must be 1", version=waivers_version)

    waivers = waivers_doc.get("waivers")
    if not isinstance(waivers, list):
        _err(errors, "E_WAIVER_LIST", "waivers.waivers must be a list")
        waivers = []

    waiver_ids: set[str] = set()
    for idx, waiver in enumerate(waivers):
        if not isinstance(waiver, dict):
            _err(errors, "E_WAIVER_TYPE", "waiver entry must be an object", index=idx)
            continue
        wid = waiver.get("id")
        domain = waiver.get("domain")
        gate = waiver.get("gate")
        owner = waiver.get("owner")
        reason = waiver.get("reason")
        issue = waiver.get("issue")
        allowed_statuses = waiver.get("allowed_statuses")
        expires_utc = waiver.get("expires_utc")
        lanes = waiver.get("lanes")
        profiles = waiver.get("profiles")
        waiver_phase = waiver.get("phase")

        if not isinstance(wid, str) or not wid.strip():
            _err(errors, "E_WAIVER_ID", "waiver.id must be non-empty", index=idx)
            continue
        wid = wid.strip()
        if wid in waiver_ids:
            _err(errors, "E_WAIVER_DUP_ID", "waiver.id must be unique", id=wid)
        waiver_ids.add(wid)

        for key_name, key_val in (
            ("domain", domain),
            ("gate", gate),
            ("owner", owner),
            ("reason", reason),
            ("issue", issue),
        ):
            if not isinstance(key_val, str) or not key_val.strip():
                _err(errors, "E_WAIVER_FIELD", f"waiver.{key_name} must be non-empty", id=wid)

        if isinstance(domain, str) and isinstance(gate, str) and domain.strip() and gate.strip():
            gate_key = _norm_gate_key(domain, gate)
            if gate_key not in assignment_map:
                _err(
                    errors,
                    "E_WAIVER_UNKNOWN_GATE",
                    "waiver references gate not present in manifest assignments",
                    id=wid,
                    gate_key=gate_key,
                )

        if not isinstance(allowed_statuses, list) or not allowed_statuses:
            _err(errors, "E_WAIVER_ALLOWED_STATUSES", "waiver.allowed_statuses must be non-empty list", id=wid)
        else:
            for st in allowed_statuses:
                if not isinstance(st, str) or st not in VALID_GATE_STATUS:
                    _err(
                        errors,
                        "E_WAIVER_ALLOWED_STATUS_VALUE",
                        "waiver.allowed_statuses includes invalid status",
                        id=wid,
                        status=st,
                    )

        if not isinstance(lanes, list) or not lanes:
            _err(errors, "E_WAIVER_LANES", "waiver.lanes must be non-empty list", id=wid)
        else:
            for lane in lanes:
                if lane not in {"pin", "external", "*"}:
                    _err(errors, "E_WAIVER_LANE_VALUE", "waiver lane must be pin|external|*", id=wid, lane=lane)

        if not isinstance(profiles, list) or not profiles:
            _err(errors, "E_WAIVER_PROFILES", "waiver.profiles must be non-empty list", id=wid)

        if require_phase_bound_waivers:
            if not isinstance(waiver_phase, str) or not waiver_phase.strip():
                _err(errors, "E_WAIVER_PHASE", "waiver.phase must be non-empty under phase-bound policy", id=wid)
            elif phase_set and waiver_phase.strip() not in phase_set:
                _err(
                    errors,
                    "E_WAIVER_PHASE_VALUE",
                    "waiver.phase must be one of phase_policy.phases",
                    id=wid,
                    phase=waiver_phase,
                )
        elif isinstance(waiver_phase, str) and waiver_phase.strip():
            if phase_set and waiver_phase.strip() not in phase_set:
                _err(
                    errors,
                    "E_WAIVER_PHASE_VALUE",
                    "waiver.phase must be one of phase_policy.phases when provided",
                    id=wid,
                    phase=waiver_phase,
                )

        if not isinstance(expires_utc, str) or not expires_utc.strip():
            _err(errors, "E_WAIVER_EXPIRES", "waiver.expires_utc must be non-empty", id=wid)
        else:
            try:
                _parse_utc(expires_utc.strip(), field=f"waiver[{wid}].expires_utc")
            except RuntimeError as exc:
                _err(errors, "E_WAIVER_EXPIRES_FORMAT", str(exc), id=wid)

    spec_policy = manifest.get("spec_policy")
    if not isinstance(spec_policy, dict):
        _err(errors, "E_SPEC_POLICY", "manifest.spec_policy must be an object")
        spec_policy = {}

    stage_a = spec_policy.get("bringup_subset")
    stage_b = spec_policy.get("promotion_required")
    excluded = spec_policy.get("excluded_benchmarks")

    if not isinstance(stage_a, list) or not stage_a:
        _err(errors, "E_SPEC_STAGE_A", "spec_policy.bringup_subset must be non-empty list")
        stage_a = []
    if not isinstance(stage_b, list) or not stage_b:
        _err(errors, "E_SPEC_STAGE_B", "spec_policy.promotion_required must be non-empty list")
        stage_b = []
    if not isinstance(excluded, list):
        _err(errors, "E_SPEC_EXCLUDED", "spec_policy.excluded_benchmarks must be list")
        excluded = []

    stage_a_set = {str(x) for x in stage_a}
    stage_b_set = {str(x) for x in stage_b}
    excluded_set = {str(x) for x in excluded}

    if not stage_a_set.issubset(stage_b_set):
        _err(
            errors,
            "E_SPEC_STAGE_SUBSET",
            "spec_policy.bringup_subset must be subset of promotion_required",
            stage_a_only=sorted(stage_a_set - stage_b_set),
        )

    if "548.exchange2_r" not in excluded_set:
        _err(
            errors,
            "E_SPEC_FORTRAN_EXCLUSION",
            "spec_policy.excluded_benchmarks must include 548.exchange2_r",
        )

    if "548.exchange2_r" in stage_b_set:
        _err(
            errors,
            "E_SPEC_FORTRAN_IN_STAGE_B",
            "548.exchange2_r must not appear in promotion_required",
        )

    required_spec_gates = {
        "SPEC::SPEC int-rate Stage A subset (qemu+specdiff)",
        "SPEC::SPEC int-rate Stage B full set (qemu+specdiff)",
        "SPEC::SPEC Fortran exclusion 548.exchange2_r",
    }
    missing_spec_gates = sorted(required_spec_gates - set(assignment_map.keys()))
    if missing_spec_gates:
        _err(
            errors,
            "E_SPEC_REQUIRED_GATES",
            "manifest missing required SPEC gate assignments",
            missing=missing_spec_gates,
        )

    stats = {
        "agents": len(agents),
        "assignments": len(assignment_map),
        "declared_checklists": len(declared_path_ids),
        "declared_checklist_ids": len(declared_ids_global),
        "waivers": len(waivers),
        "agent_scope_explicit_modules_required": explicit_modules_required,
        "agent_scope_allow_multi_module_agents": allow_multi_module_agents,
        "agent_scope_cross_module_agents": len(cross_module_agents),
        "agent_scope_multi_module_agents": multi_module_agent_count,
        "phases": len(phases),
        "active_phase": active_phase,
        "phase_gate_requirement_phases": len(phase_gate_requirements),
        "benchmark_flow_enabled": bool(benchmark_flow_stats.get("enabled", False)),
        "benchmark_flow_stages": int(benchmark_flow_stats.get("stages", 0)),
    }

    return errors, warnings, {
        "agents": agents,
        "assignments": assignment_map,
        "waivers": waivers,
        "agent_scope_policy": agent_scope_policy,
        "phase_policy": {
            "phases": phases,
            "active_phase": active_phase,
            "require_phase_bound_waivers": require_phase_bound_waivers,
        },
        "phase_gate_requirements": phase_gate_requirements,
        "registry_gates": registry_gate_map,
        "stats": stats,
    }


def _waiver_is_active(
    waiver: dict[str, Any],
    *,
    domain: str,
    gate: str,
    status: str,
    lane: str,
    profile: str,
    active_phase: str,
    now: datetime,
) -> tuple[bool, str]:
    w_domain = str(waiver.get("domain", "")).strip()
    w_gate = str(waiver.get("gate", "")).strip()
    if domain != w_domain or gate != w_gate:
        return False, "gate_mismatch"

    allowed_statuses = waiver.get("allowed_statuses", [])
    if not isinstance(allowed_statuses, list) or status not in allowed_statuses:
        return False, "status_not_allowed"

    lanes = waiver.get("lanes", [])
    if not isinstance(lanes, list) or (lane not in lanes and "*" not in lanes):
        return False, "lane_not_allowed"

    profiles = waiver.get("profiles", [])
    if not isinstance(profiles, list) or (profile not in profiles and "*" not in profiles):
        return False, "profile_not_allowed"

    waiver_phase = str(waiver.get("phase", "")).strip()
    if active_phase:
        if not waiver_phase:
            return False, "missing_phase"
        if waiver_phase != active_phase:
            return False, "phase_not_active"

    expires_raw = str(waiver.get("expires_utc", "")).strip()
    if not expires_raw:
        return False, "missing_expiry"
    try:
        expires = _parse_utc(expires_raw, field=f"waiver[{waiver.get('id', '?')}].expires_utc")
    except RuntimeError:
        return False, "invalid_expiry"

    if now > expires:
        return False, "expired"

    return True, "active"


def _run_runtime(
    report: dict[str, Any],
    *,
    lane: str,
    run_id: str,
    active_phase: str,
    assignment_map: dict[str, dict[str, Any]],
    waivers: list[dict[str, Any]],
    phase_gate_requirements: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    runs = report.get("runs")
    if not isinstance(runs, list):
        _err(errors, "E_REPORT_RUNS", "report.runs must be a list")
        return errors, warnings, {}

    selected: dict[str, Any] | None = None
    for run in runs:
        if not isinstance(run, dict):
            continue
        if str(run.get("lane", "")).strip() == lane and str(run.get("run_id", "")).strip() == run_id:
            selected = run
            break

    if selected is None:
        _err(
            errors,
            "E_REPORT_RUN_NOT_FOUND",
            "requested lane/run_id not found in report",
            lane=lane,
            run_id=run_id,
        )
        return errors, warnings, {}

    profile = str(selected.get("profile", "dev")).strip() or "dev"
    gates = selected.get("gates")
    if not isinstance(gates, list):
        _err(errors, "E_REPORT_GATES", "selected run has invalid gates list", lane=lane, run_id=run_id)
        return errors, warnings, {}

    run_gate_map: dict[str, dict[str, Any]] = {}
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        domain = str(gate.get("domain", "")).strip()
        gate_name = str(gate.get("gate", "")).strip()
        if not domain or not gate_name:
            continue
        gate_key = _norm_gate_key(domain, gate_name)
        if gate_key not in run_gate_map:
            run_gate_map[gate_key] = gate

    now = _utc_now()
    required_total = 0
    required_pass = 0
    required_waived = 0
    required_failed = 0
    waiver_hits = 0

    for gate in gates:
        if not isinstance(gate, dict):
            continue
        required = bool(gate.get("required", True))
        if not required:
            continue

        required_total += 1

        domain = str(gate.get("domain", "")).strip()
        gate_name = str(gate.get("gate", "")).strip()
        gate_key = _norm_gate_key(domain, gate_name)
        status = str(gate.get("status", "not_run")).strip()
        gate_waived = bool(gate.get("waived", False))

        if status not in VALID_GATE_STATUS:
            _err(
                errors,
                "E_RUNTIME_GATE_STATUS",
                "gate has invalid status",
                gate_key=gate_key,
                status=status,
            )
            required_failed += 1
            continue

        if gate_key not in assignment_map:
            _err(
                errors,
                "E_RUNTIME_UNASSIGNED_GATE",
                "required gate is not assigned in manifest",
                gate_key=gate_key,
                status=status,
            )
            required_failed += 1
            continue

        if status == "pass" and not gate_waived:
            required_pass += 1
            continue

        matched_waiver: dict[str, Any] | None = None
        for waiver in waivers:
            if not isinstance(waiver, dict):
                continue
            active, reason = _waiver_is_active(
                waiver,
                domain=domain,
                gate=gate_name,
                status=status,
                lane=lane,
                profile=profile,
                active_phase=active_phase,
                now=now,
            )
            if active:
                matched_waiver = waiver
                waiver_hits += 1
                break
            if reason in {"expired", "phase_not_active"} and _norm_gate_key(
                str(waiver.get("domain", "")).strip(),
                str(waiver.get("gate", "")).strip(),
            ) == gate_key:
                warn_code = "W_RUNTIME_WAIVER_EXPIRED" if reason == "expired" else "W_RUNTIME_WAIVER_PHASE"
                warn_message = (
                    "waiver exists for gate but is expired"
                    if reason == "expired"
                    else "waiver exists for gate but is outside active phase"
                )
                _warn(
                    warnings,
                    warn_code,
                    warn_message,
                    gate_key=gate_key,
                    waiver_id=waiver.get("id"),
                    active_phase=active_phase,
                )

        if matched_waiver is None:
            _err(
                errors,
                "E_RUNTIME_UNWAIVED_GATE",
                "required gate is not pass and has no active waiver",
                gate_key=gate_key,
                status=status,
                report_waived=gate_waived,
            )
            required_failed += 1
            continue

        required_waived += 1

    if required_total == 0:
        _err(
            errors,
            "E_RUNTIME_NO_REQUIRED_GATES",
            "selected run has no required gates; runtime validation cannot close run",
            lane=lane,
            run_id=run_id,
        )

    phase_required_gate_keys: list[str] = []
    phase_missing_gate_keys: list[str] = []
    phase_owner_mismatches: list[dict[str, Any]] = []
    if active_phase:
        phase_req = phase_gate_requirements.get(active_phase, {})
        if isinstance(phase_req, dict):
            req_keys_raw = phase_req.get("required_gate_keys", [])
            if isinstance(req_keys_raw, list):
                phase_required_gate_keys = [str(x).strip() for x in req_keys_raw if str(x).strip()]

    for gate_key in phase_required_gate_keys:
        gate_row = run_gate_map.get(gate_key)
        if gate_row is None:
            phase_missing_gate_keys.append(gate_key)
            continue
        expected_agent = str(assignment_map.get(gate_key, {}).get("agent", "")).strip()
        actual_owner = str(gate_row.get("owner", "")).strip()
        if expected_agent and actual_owner != expected_agent:
            phase_owner_mismatches.append(
                {
                    "gate_key": gate_key,
                    "expected_owner": expected_agent,
                    "actual_owner": actual_owner or "<empty>",
                }
            )

    if phase_missing_gate_keys:
        _err(
            errors,
            "E_RUNTIME_PHASE_REQUIRED_GATE_MISSING",
            "active-phase required gate rows are missing from selected run",
            active_phase=active_phase,
            missing_gate_keys=sorted(phase_missing_gate_keys),
        )

    if phase_owner_mismatches:
        _err(
            errors,
            "E_RUNTIME_PHASE_GATE_OWNER_MISMATCH",
            "active-phase required gate rows must use assigned agent owner tags",
            active_phase=active_phase,
            mismatches=phase_owner_mismatches,
        )

    stats = {
        "required_gates_total": required_total,
        "required_pass": required_pass,
        "required_waived": required_waived,
        "required_failed": required_failed,
        "waiver_matches": waiver_hits,
        "phase_required_gates_total": len(phase_required_gate_keys),
        "phase_required_gates_missing": len(phase_missing_gate_keys),
        "phase_required_gate_owner_mismatches": len(phase_owner_mismatches),
        "profile": profile,
        "lane": lane,
        "run_id": run_id,
        "active_phase": active_phase,
    }
    return errors, warnings, stats


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Strict multi-agent gate/checklist validator")
    ap.add_argument("--manifest", default="docs/bringup/agent_runs/manifest.yaml")
    ap.add_argument("--waivers", default="docs/bringup/agent_runs/waivers.yaml")
    ap.add_argument("--registry", default="docs/bringup/gate_registry.json")
    ap.add_argument("--checklists-root", default="docs/bringup/agent_runs/checklists")
    ap.add_argument("--strict-always", action="store_true", help="enforce strict_always policy")
    ap.add_argument("--mode", choices=["static", "runtime"], required=True)
    ap.add_argument("--report", default="docs/bringup/gates/latest.json")
    ap.add_argument("--lane", choices=["pin", "external"])
    ap.add_argument("--run-id")
    ap.add_argument("--active-phase", default="", help="Optional active phase override for waiver checks")
    ap.add_argument("--out", help="optional JSON summary output path")
    args = ap.parse_args(argv)

    root = Path(".").resolve()
    manifest_path = (root / args.manifest).resolve()
    waivers_path = (root / args.waivers).resolve()
    registry_path = (root / args.registry).resolve()
    checklists_root = (root / args.checklists_root).resolve()

    if args.mode == "runtime" and (not args.lane or not args.run_id):
        print("error: --lane and --run-id are required in runtime mode", file=sys.stderr)
        return EXIT_USAGE

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    runtime_stats: dict[str, Any] = {}

    try:
        manifest = _load_mapping(manifest_path)
    except Exception as exc:
        print(f"error: failed to load manifest: {exc}", file=sys.stderr)
        return EXIT_USAGE

    try:
        waivers_doc = _load_mapping(waivers_path)
    except Exception as exc:
        print(f"error: failed to load waivers: {exc}", file=sys.stderr)
        return EXIT_USAGE

    try:
        registry = _load_mapping(registry_path)
    except Exception as exc:
        print(f"error: failed to load gate registry: {exc}", file=sys.stderr)
        return EXIT_USAGE

    static_errors, static_warnings, state = _validate_static(
        manifest,
        waivers_doc,
        registry,
        checklists_root,
        root=root,
        strict_always=bool(args.strict_always),
    )
    errors.extend(static_errors)
    warnings.extend(static_warnings)

    if args.active_phase and not errors:
        phase_policy = state.get("phase_policy", {})
        if not isinstance(phase_policy, dict):
            phase_policy = {}
        phases = phase_policy.get("phases", [])
        active_override = str(args.active_phase).strip()
        if isinstance(phases, list):
            phase_set = {str(x).strip() for x in phases if str(x).strip()}
            if phase_set and active_override not in phase_set:
                _err(
                    errors,
                    "E_ACTIVE_PHASE_OVERRIDE",
                    "--active-phase is not listed in manifest.phase_policy.phases",
                    active_phase=active_override,
                    phases=sorted(phase_set),
                )
        if args.mode == "runtime" and not errors:
            _validate_phase_registry_alignment(
                active_override,
                phase_gate_requirements=state.get("phase_gate_requirements", {}),
                assignment_map=state.get("assignments", {}),
                registry_gate_map=state.get("registry_gates", {}),
                errors=errors,
            )

    if args.mode == "runtime" and not errors:
        report_path = (root / args.report).resolve()
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception as exc:
            _err(errors, "E_REPORT_LOAD", f"failed to load report JSON: {exc}", report=str(report_path))
            report = {}

        if not errors:
            phase_policy = state.get("phase_policy", {})
            if not isinstance(phase_policy, dict):
                phase_policy = {}
            active_phase = str(args.active_phase or phase_policy.get("active_phase", "")).strip()
            if bool(phase_policy.get("require_phase_bound_waivers", False)) and not active_phase:
                _err(
                    errors,
                    "E_RUNTIME_ACTIVE_PHASE",
                    "phase-bound waiver policy requires active phase (set manifest.phase_policy.active_phase or --active-phase)",
                )
            if not errors and active_phase:
                phases = phase_policy.get("phases", [])
                if isinstance(phases, list):
                    phase_set = {str(x).strip() for x in phases if str(x).strip()}
                    if phase_set and active_phase not in phase_set:
                        _err(
                            errors,
                            "E_RUNTIME_ACTIVE_PHASE_VALUE",
                            "active phase is not listed in manifest.phase_policy.phases",
                            active_phase=active_phase,
                            phases=sorted(phase_set),
                        )

        if not errors:
            rt_errors, rt_warnings, rt_stats = _run_runtime(
                report,
                lane=str(args.lane),
                run_id=str(args.run_id),
                active_phase=active_phase,
                assignment_map=state["assignments"],
                waivers=state["waivers"],
                phase_gate_requirements=state.get("phase_gate_requirements", {}),
            )
            errors.extend(rt_errors)
            warnings.extend(rt_warnings)
            runtime_stats = rt_stats

    summary: dict[str, Any] = {
        "ok": len(errors) == 0,
        "mode": args.mode,
        "strict_always": bool(args.strict_always),
        "checked_at_utc": _utc_now_str(),
        "manifest": str(manifest_path),
        "waivers": str(waivers_path),
        "registry": str(registry_path),
        "checklists_root": str(checklists_root),
        "errors": errors,
        "warnings": warnings,
        "static_stats": state.get("stats", {}),
    }

    if args.mode == "runtime":
        summary["report"] = str((Path(".").resolve() / args.report).resolve())
        summary["lane"] = args.lane
        summary["run_id"] = args.run_id
        summary["active_phase"] = str(args.active_phase).strip()
        summary["runtime_stats"] = runtime_stats

    if args.out:
        out_path = (Path(".").resolve() / args.out).resolve()
        _write_json(out_path, summary)

    if summary["ok"]:
        if args.mode == "static":
            print(
                "ok: multi-agent static validation passed "
                f"(agents={state['stats']['agents']}, assignments={state['stats']['assignments']})"
            )
        else:
            print(
                "ok: multi-agent runtime validation passed "
                f"(lane={args.lane}, run_id={args.run_id}, "
                f"required={runtime_stats.get('required_gates_total', 0)}, "
                f"waived={runtime_stats.get('required_waived', 0)})"
            )
        return EXIT_OK

    for item in errors:
        msg = item.get("message", "")
        code = item.get("code", "E_UNKNOWN")
        print(f"error [{code}]: {msg}", file=sys.stderr)

    if args.mode == "runtime":
        return EXIT_RUNTIME_FAIL
    return EXIT_STATIC_FAIL


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
