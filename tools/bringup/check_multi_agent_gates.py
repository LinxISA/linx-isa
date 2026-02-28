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
ID_RE = re.compile(r"\bID:\s*([A-Z0-9][A-Z0-9_-]*)\b")
GATE_KEY_RE = re.compile(r"^[^:\n]+::[^\n]+$")
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


def _validate_static(
    manifest: dict[str, Any],
    waivers_doc: dict[str, Any],
    checklists_root: Path,
    *,
    strict_always: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

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

    stage_a = spec_policy.get("stage_a_subset")
    stage_b = spec_policy.get("stage_b_required")
    excluded = spec_policy.get("excluded_benchmarks")

    if not isinstance(stage_a, list) or not stage_a:
        _err(errors, "E_SPEC_STAGE_A", "spec_policy.stage_a_subset must be non-empty list")
        stage_a = []
    if not isinstance(stage_b, list) or not stage_b:
        _err(errors, "E_SPEC_STAGE_B", "spec_policy.stage_b_required must be non-empty list")
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
            "spec_policy.stage_a_subset must be subset of stage_b_required",
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
            "548.exchange2_r must not appear in stage_b_required",
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
    }

    return errors, warnings, {
        "agents": agents,
        "assignments": assignment_map,
        "waivers": waivers,
        "agent_scope_policy": agent_scope_policy,
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
    assignment_map: dict[str, dict[str, Any]],
    waivers: list[dict[str, Any]],
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
                now=now,
            )
            if active:
                matched_waiver = waiver
                waiver_hits += 1
                break
            if reason == "expired" and _norm_gate_key(
                str(waiver.get("domain", "")).strip(),
                str(waiver.get("gate", "")).strip(),
            ) == gate_key:
                _warn(
                    warnings,
                    "W_RUNTIME_WAIVER_EXPIRED",
                    "waiver exists for gate but is expired",
                    gate_key=gate_key,
                    waiver_id=waiver.get("id"),
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

    stats = {
        "required_gates_total": required_total,
        "required_pass": required_pass,
        "required_waived": required_waived,
        "required_failed": required_failed,
        "waiver_matches": waiver_hits,
        "profile": profile,
        "lane": lane,
        "run_id": run_id,
    }
    return errors, warnings, stats


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Strict multi-agent gate/checklist validator")
    ap.add_argument("--manifest", default="docs/bringup/agent_runs/manifest.yaml")
    ap.add_argument("--waivers", default="docs/bringup/agent_runs/waivers.yaml")
    ap.add_argument("--checklists-root", default="docs/bringup/agent_runs/checklists")
    ap.add_argument("--strict-always", action="store_true", help="enforce strict_always policy")
    ap.add_argument("--mode", choices=["static", "runtime"], required=True)
    ap.add_argument("--report", default="docs/bringup/gates/latest.json")
    ap.add_argument("--lane", choices=["pin", "external"])
    ap.add_argument("--run-id")
    ap.add_argument("--out", help="optional JSON summary output path")
    args = ap.parse_args(argv)

    root = Path(".").resolve()
    manifest_path = (root / args.manifest).resolve()
    waivers_path = (root / args.waivers).resolve()
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

    static_errors, static_warnings, state = _validate_static(
        manifest,
        waivers_doc,
        checklists_root,
        strict_always=bool(args.strict_always),
    )
    errors.extend(static_errors)
    warnings.extend(static_warnings)

    if args.mode == "runtime" and not errors:
        report_path = (root / args.report).resolve()
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except Exception as exc:
            _err(errors, "E_REPORT_LOAD", f"failed to load report JSON: {exc}", report=str(report_path))
            report = {}

        if not errors:
            rt_errors, rt_warnings, rt_stats = _run_runtime(
                report,
                lane=str(args.lane),
                run_id=str(args.run_id),
                assignment_map=state["assignments"],
                waivers=state["waivers"],
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
        "checklists_root": str(checklists_root),
        "errors": errors,
        "warnings": warnings,
        "static_stats": state.get("stats", {}),
    }

    if args.mode == "runtime":
        summary["report"] = str((Path(".").resolve() / args.report).resolve())
        summary["lane"] = args.lane
        summary["run_id"] = args.run_id
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
