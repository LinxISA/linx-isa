#!/usr/bin/env python3
"""Run the AI workload hard-break flow through LLVM, QEMU, and LinxCoreModel."""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qemu_build_paths import default_qemu_binary


PASS_STATUSES = {"pass", "skipped", "not_applicable", "not_run"}
DIGEST_RE = re.compile(r"PTO_DIGEST\s+([A-Za-z0-9_]+)\s+0x([0-9A-Fa-f]+)")
GFSIM_BROB_RE = re.compile(
    r"Retired blocks\s+(?P<blocks>\d+)\.\s+BROB head info:\s+"
    r"(?P<head>.*?\bBPC\s+0x(?P<bpc>[0-9A-Fa-f]+).*?)(?:\n|$)"
)
GFSIM_UART_RE = re.compile(r"^linx_uart:\s*(?P<line>.*)$", re.MULTILINE)
GFSIM_FINISHER_RE = re.compile(
    r"linx_test_finisher write addr=0x10009000 val=0x(?P<value>[0-9A-Fa-f]+)\s+(?P<status>pass|fail)"
)
GFSIM_ASSERT_RE = re.compile(r"ASSERTION FAILED:\s*(?P<assertion>[^\n]+)")
FORBIDDEN_ASM_RE = re.compile(
    r"((^|[^A-Za-z0-9_])L\.|set_flag|wait_flag|TSync|B\.SET|B\.WAIT)",
    re.IGNORECASE,
)
FINISHER_PASS_LOW8 = 0x55
FINISHER_FAIL_LOW8 = 0x33
FINISHER_RESET_LOW8 = 0x77
PTO_KERNELS_REL = Path("workloads/pto_kernels")
SUPER_NPU_REL = PTO_KERNELS_REL / "benchmarks/supernpu"
LINX_TILEOP_API_REL = Path("tools/Linx-TileOP-API")
COMPONENT_LOCK_REL = Path("docs/bringup/component-lock.v0.58.json")
LINX_DIRECT_BOOT_LINK_SCRIPT = """ENTRY(_start)
PHDRS {
  text PT_LOAD FLAGS(5);
  data PT_LOAD FLAGS(6);
}
SECTIONS {
  . = 0x00010000;
  .text : { KEEP(*(.text._start)) *(.text*) } :text
  .rodata : { *(.rodata*) *(.eh_frame*) } :text
  . = ALIGN(0x1000);
  .init_array : { *(.init_array*) *(.fini_array*) } :data
  .data : { *(.sdata*) *(.data*) *(.got*) } :data
  .bss (NOLOAD) : { *(.bss*) *(.sbss*) *(.relro_padding*) *(COMMON) } :data
  . = ALIGN(16);
  .bootstack (NOLOAD) : {
    __start_init_stack = .;
    . += 0x4000;
    __end_init_stack = .;
  } :data
}
"""
LINX_MODEL_SMOKE_SOURCE = r"""extern "C" __attribute__((noreturn, section(".text._start"))) void _start(void) {
  __asm__ volatile(
      "BSTART.STD\n"
      "lui 65545, ->u\n"
      "lui 5, ->t\n"
      "addi t#1, 1365, ->t\n"
      "c.swi t#1, [u#1, 0]\n"
      "BSTOP\n"
      ::: "memory");
  while (1) {
    __asm__ volatile("" ::: "memory");
  }
}
"""
@dataclasses.dataclass
class Case:
    id: str
    kind: str
    suite: str
    tier: int
    source_paths: list[Path]
    manifest_path: Path | None
    workdir: Path
    compile_command: str | list[str] | None
    qemu_command: str | list[str] | None
    model_eligible: bool
    produces_elf: bool
    expected: str
    metadata: dict[str, Any]


@dataclasses.dataclass
class CaseState:
    case: Case
    case_dir: Path
    stages: dict[str, dict[str, Any]] = dataclasses.field(default_factory=dict)
    artifacts: dict[str, str] = dataclasses.field(default_factory=dict)
    qemu_digests: dict[str, str] = dataclasses.field(default_factory=dict)
    model_digests: dict[str, str] = dataclasses.field(default_factory=dict)
    immutable_artifacts: dict[str, dict[str, str]] = dataclasses.field(default_factory=dict)
    failure_stage: str | None = None
    failure_owner: str | None = None
    failure_evidence: str | None = None


class ArtifactIntegrityError(RuntimeError):
    """An input selected for a release flow changed or disappeared."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("ai-%Y%m%d-%H%M%S")


def default_flow_path(root: Path) -> Path:
    return root / "docs" / "bringup" / "ai_workload_bringup_flow.json"


def relpath(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", text.strip())
    text = text.strip("-._")
    return text or "case"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def capture_immutable_artifacts(paths: dict[str, Path]) -> dict[str, dict[str, str]]:
    manifest: dict[str, dict[str, str]] = {}
    for name, raw_path in sorted(paths.items()):
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise ArtifactIntegrityError(f"{name} is missing: {path}")
        manifest[name] = {"path": str(path), "sha256": sha256_file(path)}
    return manifest


def verify_immutable_artifacts(
    manifest: dict[str, dict[str, str]],
    paths: dict[str, Path],
    *,
    consumer: str,
) -> None:
    for name, raw_path in sorted(paths.items()):
        path = Path(raw_path).expanduser().resolve()
        recorded = manifest.get(name)
        if recorded is None:
            raise ArtifactIntegrityError(f"{name} has no recorded SHA-256 before {consumer}")
        if str(path) != recorded.get("path"):
            raise ArtifactIntegrityError(f"{name} path changed before {consumer}")
        if not path.is_file():
            raise ArtifactIntegrityError(f"{name} is missing before {consumer}: {path}")
        if sha256_file(path) != recorded.get("sha256"):
            raise ArtifactIntegrityError(f"{name} SHA-256 changed before {consumer}")


def verify_recorded_artifacts(
    manifest: dict[str, dict[str, str]], *, consumer: str
) -> None:
    verify_immutable_artifacts(
        manifest,
        {name: Path(row["path"]) for name, row in manifest.items()},
        consumer=consumer,
    )


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: invalid JSON {path}: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def git_output(cwd: Path, *args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(cwd), *args],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def checkout_revision(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {
            "initialized": False,
            "sha": None,
            "tree": None,
            "branch": None,
            "detached": None,
            "dirty": None,
        }
    sha = git_output(path, "rev-parse", "HEAD")
    tree = git_output(path, "rev-parse", "HEAD^{tree}") if sha else None
    branch = git_output(path, "symbolic-ref", "--quiet", "--short", "HEAD")
    status = git_output(path, "status", "--porcelain", "--untracked-files=normal")
    return {
        "initialized": sha is not None,
        "sha": sha,
        "tree": tree,
        "branch": branch,
        "detached": branch is None if sha is not None else None,
        "dirty": bool(status) if status is not None else None,
    }


def gitlink_sha(root: Path, rel: str) -> str | None:
    row = git_output(root, "ls-tree", "HEAD", "--", rel)
    if not row:
        return None
    fields = row.split(None, 3)
    if len(fields) < 3 or fields[0] != "160000" or fields[1] != "commit":
        return None
    return fields[2]


def declared_submodules(root: Path) -> dict[str, dict[str, str | None]]:
    gitmodules = root / ".gitmodules"
    if not gitmodules.is_file():
        raise SystemExit(f"error: missing submodule topology: {gitmodules}")
    try:
        output = subprocess.check_output(
            [
                "git",
                "config",
                "-f",
                str(gitmodules),
                "--get-regexp",
                r"^submodule\..*\.(path|url|branch)$",
            ],
            text=True,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"error: cannot read submodule topology: {gitmodules}") from exc
    by_name: dict[str, dict[str, str]] = {}
    for line in output.splitlines():
        key, value = line.split(None, 1)
        name_and_field = key.removeprefix("submodule.")
        name, field = name_and_field.rsplit(".", 1)
        by_name.setdefault(name, {})[field] = value.strip()
    topology: dict[str, dict[str, str | None]] = {}
    for name, fields in by_name.items():
        path = fields.get("path")
        if not path:
            raise SystemExit(f"error: submodule {name} is missing path: {gitmodules}")
        if path in topology:
            raise SystemExit(f"error: duplicate submodule path: {path}")
        topology[path] = {
            "name": name,
            "path": path,
            "url": fields.get("url"),
            "branch": fields.get("branch"),
        }
    if not topology:
        raise SystemExit(f"error: submodule topology is empty: {gitmodules}")
    return dict(sorted(topology.items()))


def load_component_lock(lock_path: Path) -> tuple[dict[str, Any] | None, str | None, str | None]:
    try:
        raw = lock_path.read_bytes()
    except FileNotFoundError:
        return None, None, f"component lock is missing: {lock_path}"
    except OSError as exc:
        return (
            None,
            None,
            f"component lock is unreadable: {lock_path}: {exc.__class__.__name__}: {exc}",
        )
    digest = hashlib.sha256(raw).hexdigest()
    try:
        lock = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, digest, f"component lock is malformed: {lock_path}: {exc}"
    if not isinstance(lock, dict):
        return None, digest, f"component lock root must be an object: {lock_path}"
    return lock, digest, None


def exact_pin_evidence(root: Path) -> dict[str, Any]:
    lock_path = root / COMPONENT_LOCK_REL
    lock, lock_digest, lock_error = load_component_lock(lock_path)
    if lock_error:
        return {
            "superproject": checkout_revision(root),
            "component_lock": {
                "path": COMPONENT_LOCK_REL.as_posix(),
                "sha256": lock_digest,
                "schema_version": None,
                "profile": None,
                "read_error": lock_error,
            },
            "topology": {
                "path": ".gitmodules",
                "sha256": (
                    sha256_file(root / ".gitmodules")
                    if (root / ".gitmodules").is_file()
                    else None
                ),
            },
            "components": {},
            "valid": False,
            "errors": [lock_error],
        }
    assert lock is not None
    entries = lock.get("components")
    if not isinstance(entries, list):
        raise SystemExit(f"error: component lock has no components array: {lock_path}")
    lock_by_path: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise SystemExit(f"error: invalid component lock entry: {lock_path}")
        rel = entry["path"]
        if rel in lock_by_path:
            raise SystemExit(f"error: duplicate component lock path: {rel}")
        lock_by_path[rel] = entry

    topology = declared_submodules(root)
    declared = sorted(topology)
    errors: list[str] = []
    for rel in sorted(set(lock_by_path) - set(declared)):
        errors.append(f"component lock path is not declared by .gitmodules: {rel}")

    components: dict[str, dict[str, Any]] = {}
    for rel in declared:
        checkout = checkout_revision(root / rel)
        expected_gitlink = gitlink_sha(root, rel)
        topology_entry = topology[rel]
        lock_entry = lock_by_path.get(rel)
        lock_commit = lock_entry.get("commit") if lock_entry else None
        lock_tree = lock_entry.get("tree") if lock_entry else None
        lock_url = lock_entry.get("url") if lock_entry else None
        lock_branch = lock_entry.get("branch") if lock_entry else None
        lock_role = lock_entry.get("role") if lock_entry else None
        components[rel] = {
            "checkout": checkout,
            "gitlink_expected_sha": expected_gitlink,
            "gitmodules_entry": topology_entry,
            "component_lock_sha": lock_commit,
            "component_lock_tree": lock_tree,
            "component_lock_entry": lock_entry,
            "matches": {
                "checkout_gitlink": bool(
                    checkout["sha"] and checkout["sha"] == expected_gitlink
                ),
                "gitlink_component_lock": bool(
                    expected_gitlink and expected_gitlink == lock_commit
                ),
                "checkout_tree_component_lock": bool(
                    checkout["tree"] and checkout["tree"] == lock_tree
                ),
                "gitmodules_url_component_lock": bool(
                    topology_entry["url"] and topology_entry["url"] == lock_url
                ),
                "gitmodules_branch_component_lock": bool(
                    topology_entry["branch"]
                    and topology_entry["branch"] == lock_branch
                ),
            },
        }
        if lock_entry is None:
            errors.append(f"missing component lock entry: {rel}")
        if expected_gitlink is None:
            errors.append(f"missing gitlink at superproject HEAD: {rel}")
        if not topology_entry["url"]:
            errors.append(f"missing .gitmodules URL: {rel}")
        if not topology_entry["branch"]:
            errors.append(f"missing .gitmodules branch: {rel}")
        if lock_entry is not None:
            if not isinstance(lock_url, str) or not lock_url:
                errors.append(f"missing component-lock URL: {rel}")
            elif topology_entry["url"] != lock_url:
                errors.append(
                    f".gitmodules/component-lock URL mismatch: {rel} "
                    f"gitmodules={topology_entry['url']} lock={lock_url}"
                )
            if not isinstance(lock_branch, str) or not lock_branch:
                errors.append(f"missing component-lock branch: {rel}")
            elif topology_entry["branch"] != lock_branch:
                errors.append(
                    f".gitmodules/component-lock branch mismatch: {rel} "
                    f"gitmodules={topology_entry['branch']} lock={lock_branch}"
                )
            if not isinstance(lock_role, str) or not lock_role.strip():
                errors.append(f"missing component-lock role: {rel}")
            if not isinstance(lock_tree, str) or not re.fullmatch(r"[0-9a-f]{40}", lock_tree):
                errors.append(f"missing or invalid component-lock tree: {rel}")
            elif checkout["tree"] is not None and checkout["tree"] != lock_tree:
                errors.append(
                    f"checkout tree/component-lock mismatch: {rel} "
                    f"checkout={checkout['tree']} lock={lock_tree}"
                )
            integration_status = lock_entry.get("integration_status")
            if integration_status is not None and integration_status != "landed":
                errors.append(
                    f"component-lock integration_status is not landed: {rel} "
                    f"status={integration_status}"
                )
        if not checkout["initialized"]:
            errors.append(f"component checkout is not initialized: {rel}")
        elif checkout["dirty"] is None:
            errors.append(f"cannot determine component dirty state: {rel}")
        elif checkout["dirty"]:
            errors.append(f"component checkout is dirty: {rel}")
        if (
            checkout["initialized"]
            and expected_gitlink is not None
            and checkout["sha"] != expected_gitlink
        ):
            errors.append(
                f"checkout/gitlink mismatch: {rel} "
                f"checkout={checkout['sha']} gitlink={expected_gitlink}"
            )
        if (
            lock_entry is not None
            and expected_gitlink is not None
            and expected_gitlink != lock_commit
        ):
            errors.append(
                f"gitlink/component-lock mismatch: {rel} "
                f"gitlink={expected_gitlink} lock={lock_commit}"
            )

    superproject = checkout_revision(root)
    if not superproject["initialized"]:
        errors.append("superproject checkout is not initialized")
    elif superproject["dirty"] is None:
        errors.append("cannot determine superproject dirty state")
    elif superproject["dirty"]:
        errors.append("superproject checkout is dirty")
    return {
        "superproject": superproject,
        "component_lock": {
            "path": COMPONENT_LOCK_REL.as_posix(),
            "sha256": lock_digest,
            "schema_version": lock.get("schema_version"),
            "profile": lock.get("profile"),
            "read_error": None,
        },
        "topology": {
            "path": ".gitmodules",
            "sha256": sha256_file(root / ".gitmodules"),
        },
        "components": components,
        "valid": not errors,
        "errors": errors,
    }


def load_flow(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if data.get("schema_version") != 1:
        raise SystemExit(f"error: unsupported flow schema_version in {path}")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise SystemExit(f"error: flow has no profiles: {path}")
    stages = data.get("stages")
    if not isinstance(stages, list) or not stages:
        raise SystemExit(f"error: flow has no stages: {path}")
    stage_ids: set[str] = set()
    for stage in stages:
        if not isinstance(stage, dict):
            raise SystemExit("error: each stage must be an object")
        stage_id = str(stage.get("id", "")).strip()
        if not stage_id:
            raise SystemExit("error: stage missing id")
        if stage_id in stage_ids:
            raise SystemExit(f"error: duplicate stage id: {stage_id}")
        stage_ids.add(stage_id)
        stage_profiles = stage.get("profiles")
        if not isinstance(stage_profiles, list) or not stage_profiles:
            raise SystemExit(f"error: stage {stage_id} missing profiles")
        invalid = sorted(str(p) for p in stage_profiles if p not in profiles)
        if invalid:
            raise SystemExit(
                f"error: stage {stage_id} has invalid profiles: {', '.join(invalid)}"
            )
    return data


def selected_stages(
    flow: dict[str, Any],
    profile: str,
    requested: list[str],
    start_at: str | None,
    stop_after: str | None,
) -> list[dict[str, Any]]:
    if profile not in flow["profiles"]:
        raise SystemExit(
            "error: invalid --profile "
            f"{profile}; choose one of {', '.join(sorted(flow['profiles']))}"
        )
    stages = [
        stage
        for stage in flow["stages"]
        if profile in {str(p) for p in stage.get("profiles", [])}
    ]
    if requested:
        wanted = set(requested)
        stages = [stage for stage in stages if stage["id"] in wanted]
        missing = sorted(wanted - {stage["id"] for stage in stages})
        if missing:
            raise SystemExit(
                "error: requested stage is not enabled for profile "
                f"{profile}: {', '.join(missing)}"
            )
    if start_at:
        ids = [stage["id"] for stage in stages]
        if start_at not in ids:
            raise SystemExit(f"error: --start-at stage not selected: {start_at}")
        stages = stages[ids.index(start_at) :]
    if stop_after:
        ids = [stage["id"] for stage in stages]
        if stop_after not in ids:
            raise SystemExit(f"error: --stop-after stage not selected: {stop_after}")
        stages = stages[: ids.index(stop_after) + 1]
    return stages


def validate_execution_stage_prefix(
    flow: dict[str, Any],
    profile: str,
    requested: list[str],
    stages: list[dict[str, Any]],
) -> None:
    """Require executable stage selections to start at the profile root."""
    enabled_ids = [
        stage["id"]
        for stage in flow["stages"]
        if profile in {str(p) for p in stage.get("profiles", [])}
    ]
    if not enabled_ids:
        raise SystemExit(f"error: profile {profile} has no enabled execution stages")
    selected_ids = [stage["id"] for stage in stages]

    def reject(label: str, stage_ids: list[str]) -> None:
        selected = set(stage_ids)
        furthest = max(
            (enabled_ids.index(stage_id) for stage_id in stage_ids if stage_id in enabled_ids),
            default=-1,
        )
        required = enabled_ids[: furthest + 1]
        missing = [stage_id for stage_id in required if stage_id not in selected]
        detail = (
            "missing prerequisite stage(s): " + ", ".join(missing)
            if missing
            else "expected canonical prefix: "
            + ", ".join(enabled_ids[: len(stage_ids)])
        )
        raise SystemExit(
            f"error: {label} must be an exact canonical stage prefix starting at "
            f"{enabled_ids[0]}; {detail}"
        )

    if requested and requested != enabled_ids[: len(requested)]:
        reject("--stage arguments", requested)
    if selected_ids != enabled_ids[: len(selected_ids)]:
        reject("execution stage selection", selected_ids)


def profile_tiers(flow: dict[str, Any], profile: str, override: list[int]) -> set[int]:
    if override:
        return set(override)
    raw = flow["profiles"][profile].get("tiers", [])
    if not isinstance(raw, list) or not raw:
        raise SystemExit(f"error: profile {profile} has no tier list")
    return {int(t) for t in raw}


def parse_compile_all_line(line: str) -> tuple[str, dict[str, str]] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    parts = [part.strip() for part in stripped.split(";") if part.strip()]
    if not parts:
        return None
    command = parts[-1]
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if not tokens:
        return None
    if tokens[0] == "run_case":
        if len(tokens) != 2 or "=" in tokens[1]:
            return None
        testcase = tokens[1]
        return f"make TESTCASE={shlex.quote(testcase)}", {"TESTCASE": testcase}
    if tokens[0] != "make":
        return None
    vars_out: dict[str, str] = {}
    for token in tokens[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        vars_out[key] = value
    testcase = vars_out.get("TESTCASE")
    if not testcase:
        return None
    return command, vars_out


def supernpu_tier(suite_rel: str, make_vars: dict[str, str]) -> int:
    testcase = make_vars.get("TESTCASE", "")
    v058_smoke = {
        "microbenchmark/vector/tadd_fp32_16x16",
        "microbenchmark/memory/tload_fp32_16x16",
        "microbenchmark/cube/tmatmul_fp16_32x64x64",
    }
    if f"{suite_rel}/{testcase}" in v058_smoke:
        return 0
    if suite_rel.startswith("microbenchmark/"):
        return 1
    if suite_rel.startswith("one-level/kernel/deepseek"):
        return 3
    if suite_rel.startswith("one-level/kernel/"):
        return 2
    raise ValueError(f"unsupported v0.58 SuperNPU manifest root: {suite_rel}")


def supernpu_test_roots(root: Path) -> list[tuple[str, Path]]:
    """Return active v0.58 SuperNPU manifest roots inside pto-kernels."""
    supernpu_root = root / SUPER_NPU_REL
    return [
        ("one-level", supernpu_root / "benchmark" / "one-level-arch" / "test"),
        ("microbenchmark", supernpu_root / "microbenchmark"),
    ]


def supernpu_elf_path(
    root: Path,
    flavor: str,
    test_root: Path,
    suite_dir: Path,
    make_vars: dict[str, str],
) -> Path:
    bench_root = root / SUPER_NPU_REL
    suite_rel = suite_dir.relative_to(test_root).as_posix()
    category_name = suite_rel.replace("/", "_")
    testcase = make_vars["TESTCASE"]
    if flavor == "microbenchmark":
        output_root = bench_root / "output" / "microbenchmark"
        return output_root / suite_rel / "elf" / category_name / f"{testcase}.elf"
    output_root = bench_root / "benchmark" / "one-level-arch" / "output"
    return output_root / suite_rel / "elf" / category_name / f"{testcase}.elf"


def supernpu_elf_dir(root: Path, flavor: str, test_root: Path, suite_dir: Path) -> Path:
    bench_root = root / SUPER_NPU_REL
    suite_rel = suite_dir.relative_to(test_root).as_posix()
    if flavor == "microbenchmark":
        return bench_root / "output" / "microbenchmark" / suite_rel / "elf"
    return bench_root / "benchmark" / "one-level-arch" / "output" / suite_rel / "elf"


def _norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def supernpu_source_keys(make_vars: dict[str, str]) -> list[str]:
    keys: list[str] = []
    for name in ("TYPE", "TESTCASE"):
        value = make_vars.get(name, "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def existing_path_with_actual_case(candidate: Path) -> Path | None:
    if not candidate.exists():
        return None
    parent = candidate.parent
    if not parent.exists():
        return candidate
    for child in parent.iterdir():
        if child.name == candidate.name:
            return child
    norm_name = _norm_key(candidate.name)
    matches = [child for child in parent.iterdir() if _norm_key(child.name) == norm_name]
    if len(matches) == 1:
        return matches[0]
    return candidate


def supernpu_source_paths(suite_dir: Path, make_vars: dict[str, str]) -> list[Path]:
    source_keys = supernpu_source_keys(make_vars)
    candidates = []
    for key in source_keys:
        candidates.extend(
            [
                suite_dir / "src" / f"{key}.cpp",
                suite_dir / key / f"{key}.cpp",
                suite_dir / f"{key}.cpp",
            ]
        )
    for candidate in candidates:
        existing = existing_path_with_actual_case(candidate)
        if existing is not None:
            return [existing]

    cpp_files = sorted(suite_dir.rglob("*.cpp"))
    for source_key in source_keys:
        norm_source_key = _norm_key(source_key)
        matching = [
            path
            for path in cpp_files
            if _norm_key(path.stem) == norm_source_key
            or _norm_key(path.stem) in norm_source_key
            or norm_source_key in _norm_key(path.stem)
        ]
        if matching:
            return [matching[0]]

    src_dir = suite_dir / "src"
    src_cpp_files = sorted(src_dir.rglob("*.cpp")) if src_dir.exists() else []
    if len(src_cpp_files) == 1:
        return [src_cpp_files[0]]

    return [suite_dir / "src" / f"{make_vars['TESTCASE']}.cpp"]


def snapshot_elf_mtimes(elf_dir: Path) -> dict[Path, float]:
    if not elf_dir.exists():
        return {}
    return {path: path.stat().st_mtime for path in elf_dir.rglob("*.elf") if path.is_file()}


def find_supernpu_elf_after_compile(
    case: Case,
    root: Path,
    before: dict[Path, float],
    *,
    elf_dir: Path | None = None,
) -> Path | None:
    expected = Path(case.metadata["elf"])
    if elf_dir is not None:
        expected = elf_dir / expected.name
    elif not expected.is_absolute():
        expected = root / expected
    if expected.exists():
        return expected

    if elf_dir is None:
        elf_dir = Path(case.metadata.get("elf_dir", ""))
        if not elf_dir.is_absolute():
            elf_dir = root / elf_dir
    if not elf_dir.exists():
        return None
    candidates = [path for path in elf_dir.rglob("*.elf") if path.is_file()]
    if not candidates:
        return None
    produced = [
        path
        for path in candidates
        if path not in before or path.stat().st_mtime > before[path]
    ]
    if produced:
        return max(produced, key=lambda path: path.stat().st_mtime)
    return max(candidates, key=lambda path: path.stat().st_mtime)


def discover_cases(root: Path) -> list[Case]:
    cases: list[Case] = []

    for flavor, test_root in supernpu_test_roots(root):
        if not test_root.exists():
            continue
        for compile_all in sorted(test_root.rglob("compile.all")):
            if "status/legacy" in compile_all.as_posix():
                continue
            suite_dir = compile_all.parent
            relative_suite = suite_dir.relative_to(test_root).as_posix()
            suite_rel = f"{flavor}/{relative_suite}"
            for line_no, line in enumerate(compile_all.read_text(encoding="utf-8").splitlines(), start=1):
                parsed = parse_compile_all_line(line)
                if parsed is None:
                    continue
                command, make_vars = parsed
                testcase = make_vars["TESTCASE"]
                sources = supernpu_source_paths(suite_dir, make_vars)
                case_vars = dict(make_vars)
                case_vars["PLAT"] = "linx"
                case_id = f"supernpu-{slug(suite_rel)}-{slug(testcase)}"
                if len(make_vars) > 1:
                    sig = "-".join(
                        f"{slug(k)}-{slug(v)}"
                        for k, v in sorted(make_vars.items())
                        if k != "TESTCASE"
                    )
                    if sig:
                        case_id = f"{case_id}-{sig}"
                cases.append(
                    Case(
                        id=case_id,
                        kind="supernpu",
                        suite=suite_rel,
                        tier=supernpu_tier(suite_rel, make_vars),
                        source_paths=sources,
                        manifest_path=compile_all,
                        workdir=suite_dir,
                        compile_command=command,
                        qemu_command=None,
                        model_eligible=True,
                        produces_elf=True,
                        expected="SuperNPUBench make/sim pass, then gfsim exit 0",
                        metadata={
                            "compile_all": relpath(root, compile_all),
                            "line": line_no,
                            "make_vars": make_vars,
                            "flavor": flavor,
                            "elf": relpath(
                                root,
                                supernpu_elf_path(
                                    root, flavor, test_root, suite_dir, make_vars
                                ),
                            ),
                            "elf_dir": relpath(
                                root,
                                supernpu_elf_dir(root, flavor, test_root, suite_dir),
                            ),
                            "elf_dir_rel": str(
                                (
                                    Path("microbenchmark") / relative_suite / "elf"
                                    if flavor == "microbenchmark"
                                    else Path(relative_suite) / "elf"
                                )
                            ),
                        },
                    )
                )
    return dedupe_cases(cases)


def dedupe_cases(cases: list[Case]) -> list[Case]:
    seen: dict[str, int] = {}
    out: list[Case] = []
    for case in cases:
        base = case.id
        count = seen.get(base, 0)
        seen[base] = count + 1
        if count:
            case.id = f"{base}-{count + 1}"
        out.append(case)
    return out


def filter_cases(
    cases: list[Case],
    tiers: set[int],
    kinds: list[str],
    patterns: list[str],
    limit: int,
) -> list[Case]:
    selected = [case for case in cases if case.tier in tiers]
    if kinds:
        wanted = set(kinds)
        selected = [case for case in selected if case.kind in wanted]
    if patterns:
        selected = [
            case
            for case in selected
            if any(case_matches_pattern(case, pattern) for pattern in patterns)
        ]
    selected.sort(key=lambda c: (c.tier, c.kind, c.suite, c.id))
    if limit > 0:
        selected = selected[:limit]
    return selected


def case_matches_pattern(case: Case, pattern: str) -> bool:
    if pattern.startswith("="):
        exact = pattern[1:]
        return exact in {case.id, case.suite, case.kind}
    return pattern in case.id or pattern in case.suite or pattern in case.kind


def unresolved_qemu_candidate(args: argparse.Namespace) -> Path:
    if args.qemu:
        return Path(args.qemu).expanduser().resolve()
    explicit = os.environ.get("QEMU")
    if explicit:
        return Path(explicit).expanduser().resolve()
    out_dir = Path(os.environ.get("QEMU_CLEAN_OUT_DIR", "/tmp/linx-qemu-clean-build"))
    return (out_dir / "qemu-system-linx64").expanduser().resolve()


def tool_paths(
    root: Path, args: argparse.Namespace, *, strict_qemu: bool = True
) -> dict[str, str]:
    llvm_bin = root / "compiler" / "llvm" / "build-linxisa-clang" / "bin"
    if args.qemu:
        qemu = Path(args.qemu).expanduser().resolve()
    elif strict_qemu:
        qemu = default_qemu_binary(root)
    else:
        qemu = unresolved_qemu_candidate(args)
    model_root = Path(args.model_root).expanduser().resolve() if args.model_root else root / "tools" / "LinxCoreModel"
    gfsim = Path(args.gfsim).expanduser().resolve() if args.gfsim else model_root / "bin" / "gfsim"
    return {
        "clang": str(Path(args.clang).expanduser().resolve() if args.clang else llvm_bin / "clang"),
        "clangxx": str(Path(args.clangxx).expanduser().resolve() if args.clangxx else llvm_bin / "clang++"),
        "lld": str(Path(args.lld).expanduser().resolve() if args.lld else llvm_bin / "ld.lld"),
        "llvm_objdump": str(
            Path(args.llvm_objdump).expanduser().resolve()
            if args.llvm_objdump
            else llvm_bin / "llvm-objdump"
        ),
        "llvm_objcopy": str(
            Path(args.llvm_objcopy).expanduser().resolve()
            if args.llvm_objcopy
            else llvm_bin / "llvm-objcopy"
        ),
        "qemu": str(qemu),
        "model_root": str(model_root),
        "gfsim": str(gfsim),
    }


def tool_manifest(paths: dict[str, str]) -> dict[str, dict[str, Any]]:
    version_args = {
        "clang": ["--version"],
        "clangxx": ["--version"],
        "lld": ["--version"],
        "llvm_objdump": ["--version"],
        "llvm_objcopy": ["--version"],
        "qemu": ["--version"],
    }

    def first_version_line(key: str, value: str) -> str | None:
        args = version_args.get(key)
        path = Path(value)
        if args is None or not executable(path):
            return None
        try:
            proc = subprocess.run(
                [str(path), *args],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        return (proc.stdout or "").splitlines()[0] if proc.stdout else None

    return {
        key: {
            "path": value,
            "exists": Path(value).exists(),
            "executable": executable(Path(value)),
            "sha256": sha256_file(Path(value)) if Path(value).is_file() else None,
            "version": first_version_line(key, value),
        }
        for key, value in paths.items()
        if key != "model_root"
    } | {
        "model_root": {
            "path": paths["model_root"],
            "exists": Path(paths["model_root"]).exists(),
            "executable": False,
            "sha256": None,
            "version": None,
        }
    }


def command_text(command: str | list[str]) -> str:
    if isinstance(command, list):
        return shlex.join(str(c) for c in command)
    return command


def run_command(
    command: str | list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
    log_path: Path,
    dry_run: bool,
) -> dict[str, Any]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = command_text(command)
    log_path.write_text(f"$ {rendered}\n", encoding="utf-8")
    row = {
        "command": rendered,
        "cwd": str(cwd),
        "log": str(log_path),
        "timeout_seconds": timeout,
        "returncode": 0,
        "status": "not_run" if dry_run else "pass",
    }
    if dry_run:
        return row

    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            shell=isinstance(command, str),
            executable="/bin/bash" if isinstance(command, str) else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout if timeout > 0 else None,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        elif not isinstance(output, str):
            output = str(output)
        log_path.write_text(f"$ {rendered}\n\n{output}", encoding="utf-8", errors="replace")
        row["status"] = "timeout"
        row["returncode"] = 124
        return row

    log_path.write_text(
        f"$ {rendered}\n\n{proc.stdout or ''}",
        encoding="utf-8",
        errors="replace",
    )
    row["returncode"] = proc.returncode
    row["status"] = "pass" if proc.returncode == 0 else "fail"
    return row


def normalize_qemu_finisher_result(result: dict[str, Any], log_path: Path) -> dict[str, Any]:
    """Treat the Linx direct-boot test finisher as a successful QEMU exit."""
    returncode = int(result.get("returncode", 0))
    finisher_low8 = returncode & 0xFF
    if result.get("status") == "fail" and finisher_low8 == FINISHER_PASS_LOW8:
        result = dict(result)
        result["status"] = "pass"
        result["finisher"] = "pass"
        with log_path.open("a", encoding="utf-8", errors="replace") as log:
            log.write(f"\n[ai-flow] guest finisher pass exit={returncode}\n")
        return result
    if result.get("status") == "fail" and finisher_low8 == FINISHER_FAIL_LOW8:
        result = dict(result)
        result["finisher"] = "fail"
    elif result.get("status") == "fail" and finisher_low8 == FINISHER_RESET_LOW8:
        result = dict(result)
        result["finisher"] = "reset"
    return result


def parse_digests(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {m.group(1): "0x" + m.group(2).upper() for m in DIGEST_RE.finditer(text)}


def append_uart_context(evidence: str, artifacts: dict[str, str]) -> str:
    uart_tail = artifacts.get("uart_tail")
    if not uart_tail:
        return evidence
    return f"{evidence}; uart tail: {uart_tail}"


def summarize_gfsim_log(status: str, log_path: Path) -> tuple[str, dict[str, str]]:
    if not log_path.exists():
        return "gfsim failed; log missing", {}

    text = log_path.read_text(encoding="utf-8", errors="replace")
    artifacts: dict[str, str] = {}
    uart_lines = [match.group("line").strip() for match in GFSIM_UART_RE.finditer(text)]
    if uart_lines:
        artifacts["uart_count"] = str(len(uart_lines))
        artifacts["uart_tail"] = " | ".join(uart_lines[-3:])

    if status == "pass":
        return append_uart_context("gfsim passed", artifacts), artifacts

    finisher = list(GFSIM_FINISHER_RE.finditer(text))
    if finisher:
        match = finisher[-1]
        value = "0x" + match.group("value").lower()
        finisher_status = match.group("status")
        artifacts["finisher_value"] = value
        artifacts["finisher_status"] = finisher_status
        return append_uart_context(f"gfsim finisher {finisher_status} ({value})", artifacts), artifacts

    assertion = GFSIM_ASSERT_RE.search(text)
    if assertion:
        reason = assertion.group("assertion").strip()
        artifacts["assertion"] = reason
        return append_uart_context(f"gfsim {status}: {reason}", artifacts), artifacts

    brob = list(GFSIM_BROB_RE.finditer(text))
    if brob:
        match = brob[-1]
        bpc = "0x" + match.group("bpc").lower()
        artifacts["last_brob_bpc"] = bpc
        artifacts["last_retired_blocks"] = match.group("blocks")
        artifacts["last_brob_head"] = match.group("head").strip()
        status_text = "timed out" if status == "timeout" else "failed"
        return append_uart_context(f"gfsim {status_text}; last BROB head BPC {bpc}", artifacts), artifacts

    if status == "timeout":
        return append_uart_context("gfsim timed out; no terminal model marker found", artifacts), artifacts
    return append_uart_context("gfsim failed; no terminal model marker found", artifacts), artifacts


def mark_failure(state: CaseState, stage_id: str, owner: str, evidence: str) -> None:
    if state.failure_stage is None:
        state.failure_stage = stage_id
        state.failure_owner = owner
        state.failure_evidence = evidence


def stage_row(
    state: CaseState,
    stage_id: str,
    status: str,
    *,
    owner: str,
    evidence: str = "",
    command: str | None = None,
    artifacts: dict[str, str] | None = None,
) -> dict[str, Any]:
    row = {
        "stage": stage_id,
        "status": status,
        "owner": owner,
        "evidence": evidence,
        "command": command,
        "artifacts": artifacts or {},
    }
    state.stages[stage_id] = row
    if status not in PASS_STATUSES:
        mark_failure(state, stage_id, owner, evidence)
    return row


def case_can_enter(state: CaseState, previous_stage: str) -> bool:
    row = state.stages.get(previous_stage)
    return row is not None and row["status"] in PASS_STATUSES


def source_contract(
    root: Path,
    states: list[CaseState],
    dry_run: bool,
    revisions: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    revision_errors = list((revisions or {}).get("errors", []))
    if revision_errors:
        for state in states:
            rows.append(
                stage_row(
                    state,
                    "source-contract",
                    "fail",
                    owner="integration",
                    evidence="exact-pin validation failed: " + "; ".join(revision_errors),
                )
            )
        return rows
    for state in states:
        case = state.case
        case_source_dir = state.case_dir / "source"
        artifacts: dict[str, str] = {}
        missing: list[str] = []
        source_rows: list[dict[str, str]] = []
        for source in case.source_paths:
            if not source.exists():
                missing.append(relpath(root, source))
                continue
            digest = sha256_file(source)
            source_rows.append({"path": relpath(root, source), "sha256": digest})
            case_source_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, case_source_dir / source.name)
        if case.manifest_path is not None:
            if not case.manifest_path.exists():
                missing.append(relpath(root, case.manifest_path))
            else:
                artifacts["manifest"] = relpath(root, case.manifest_path)
        source_manifest = state.case_dir / "source_manifest.json"
        write_json(
            source_manifest,
            {
                "case": case.id,
                "kind": case.kind,
                "suite": case.suite,
                "tier": case.tier,
                "sources": source_rows,
                "metadata": case.metadata,
                "dry_run": dry_run,
            },
        )
        artifacts["source_manifest"] = str(source_manifest)
        if missing:
            rows.append(
                stage_row(
                    state,
                    "source-contract",
                    "fail",
                    owner="benchmark",
                    evidence="missing source/manifest: " + ", ".join(missing),
                    artifacts=artifacts,
                )
            )
        else:
            rows.append(
                stage_row(
                    state,
                    "source-contract",
                    "pass",
                    owner="benchmark",
                    evidence=f"{len(source_rows)} source file(s) hashed",
                    artifacts=artifacts,
                )
            )
    return rows


def supernpu_make_command(
    case: Case,
    paths: dict[str, str],
    *,
    tileop_api_root: Path,
    target: str | None = None,
    linker_script: Path | None = None,
    obj_root: Path | None = None,
) -> str:
    vars_part = " ".join(
        f"{shlex.quote(k)}={shlex.quote(str(v))}"
        for k, v in sorted(case.metadata["make_vars"].items())
    )
    obj_root_part = f" OBJ_ROOT={shlex.quote(str(obj_root))}" if obj_root is not None else ""
    compiler_dir = shlex.quote(str(Path(paths["clang"]).parent))
    linx_compile_flags = shlex.quote("-c -target linx64-linx-none-elf -fenable-matrix -O2")
    linker_flags = "-Wl,-e,_start"
    if linker_script is not None:
        linker_flags += f" -Wl,-T,{linker_script}"
    linx_link_flags = shlex.quote(f"-target linx64-linx-none-elf -nostdlib {linker_flags}")
    prefix = (
        f"make {vars_part} PLAT=linx COMPILER_DIR={compiler_dir} "
        f"LINX_TILEOP_API_ROOT={shlex.quote(str(tileop_api_root))} "
        f"CC_O={linx_compile_flags} CC_LINK={linx_link_flags}{obj_root_part}"
    )
    if target:
        return f"{prefix} {shlex.quote(target)}"
    output_root = (
        obj_root
        if obj_root is not None
        else None
    )
    mkdir_output = f"mkdir -p {shlex.quote(str(output_root))}" if output_root else "true"
    clean = f"make{obj_root_part} clean" if obj_root_part else "make clean"
    return f"{mkdir_output} && {clean} && {prefix}"


def classify_supernpu_compile_failure(log_path: Path) -> tuple[str, str]:
    text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    if re.search(r"use of undeclared identifier '[A-Z0-9_]+_Impl'", text):
        return "benchmark", "SuperNPUBench Linx tile API implementation is not available"
    unsupported_linx_source_markers = [
        "unknown type name '__vbuf__'",
        "use of undeclared identifier 'blkv_get_",
        "Linx smoke TCOPYIN supports only unboxed tiles",
        "Linx scalar MATMUL supports only unboxed layouts",
        "Linx scalar MATMUL does not support ACC tile operands",
        "TADD not support Boxed Layout!",
    ]
    if any(marker in text for marker in unsupported_linx_source_markers):
        return "benchmark", "SuperNPUBench source uses unsupported Linx tile runtime contract"
    direct_boot_runtime_markers = [
        "undefined symbol: calloc",
        "undefined symbol: malloc",
        "undefined symbol: free",
        "undefined symbol: puts",
        "undefined symbol: printf",
        "undefined symbol: exit",
        "undefined symbol: memcpy",
        "undefined symbol: __divsf3",
        "undefined symbol: __mulsf3",
        "undefined symbol: __addsf3",
    ]
    if any(marker in text for marker in direct_boot_runtime_markers):
        return "benchmark", "SuperNPUBench source is not adapted to the Linx direct-boot runtime"
    source_markers = [
        "-mlxbc",
        "-enable-all-vector-as-tilereg",
        "bits/alltypes.h",
        "unknown target triple 'linx64v5'",
        "fatal error: 'benchmark.h' file not found",
        "unknown type name '__half'",
        "use of undeclared identifier '__fp32'",
        "use of undeclared identifier '__tf32'",
        "use of undeclared identifier '__hf32'",
        "include/c++/v1/iostream",
        "workloads/pto_kernels/benchmarks/supernpu/status/legacy/",
    ]
    if any(marker in text for marker in source_markers):
        return "benchmark", "SuperNPUBench source/toolchain manifest mismatch"
    return "compiler", "SuperNPUBench compile failed"


def classify_supernpu_missing_elf(log_path: Path, elf: Path) -> tuple[str, str]:
    owner, evidence = classify_supernpu_compile_failure(log_path)
    if owner == "benchmark":
        return owner, evidence
    return "compiler", f"expected ELF was not produced: {elf}"


def classify_avs_compile_failure(log_path: Path) -> tuple[str, str]:
    text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    source_markers = [
        "__builtin_linx_lc",
        "<<<",
        ">>>",
        "PTO kernel",
        "block_vector_kernels.hpp",
        "block_vector_compat.hpp",
    ]
    if any(marker in text for marker in source_markers):
        return "benchmark", "AVS PTO source/API contract failed under Linx clang"
    return "compiler", "AVS compile failed"


def run_obj_tool(
    tool: str,
    args: list[str],
    *,
    cwd: Path,
    out_path: Path,
    timeout: int,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("", encoding="utf-8")
        return {"status": "not_run", "command": shlex.join([tool, *args]), "output": str(out_path)}
    proc = subprocess.run(
        [tool, *args],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(proc.stdout or "", encoding="utf-8", errors="replace")
    return {
        "status": "pass" if proc.returncode == 0 else "fail",
        "returncode": proc.returncode,
        "command": shlex.join([tool, *args]),
        "output": str(out_path),
    }


def emit_elf_objdump_artifacts(
    *,
    paths: dict[str, str],
    root: Path,
    elf: Path,
    out_dir: Path,
    dry_run: bool,
) -> dict[str, str]:
    objdump = Path(paths["llvm_objdump"])
    if not (dry_run or executable(objdump)):
        return {}
    dump = run_obj_tool(
        paths["llvm_objdump"],
        ["-d", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.disasm.txt",
        timeout=120,
        dry_run=dry_run,
    )
    sym = run_obj_tool(
        paths["llvm_objdump"],
        ["-t", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.symbols.txt",
        timeout=120,
        dry_run=dry_run,
    )
    sec = run_obj_tool(
        paths["llvm_objdump"],
        ["-h", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.sections.txt",
        timeout=120,
        dry_run=dry_run,
    )
    rel = run_obj_tool(
        paths["llvm_objdump"],
        ["-r", str(elf)],
        cwd=root,
        out_path=out_dir / "objdump.relocs.txt",
        timeout=120,
        dry_run=dry_run,
    )
    return {
        "disasm": dump["output"],
        "symbols": sym["output"],
        "sections": sec["output"],
        "relocations": rel["output"],
    }


def emit_bpc_disassembly_window(
    *,
    paths: dict[str, str],
    root: Path,
    elf: Path,
    bpc: str | None,
    out_dir: Path,
    dry_run: bool,
) -> dict[str, str]:
    if not bpc:
        return {}
    try:
        bpc_addr = int(bpc, 16)
    except ValueError:
        return {}
    objdump = Path(paths["llvm_objdump"])
    if not (dry_run or executable(objdump)):
        return {}
    start = max(0, bpc_addr - 0x80)
    stop = bpc_addr + 0x80
    safe_bpc = f"0x{bpc_addr:x}"
    window = run_obj_tool(
        paths["llvm_objdump"],
        [
            "-d",
            "--no-show-raw-insn",
            f"--start-address=0x{start:x}",
            f"--stop-address=0x{stop:x}",
            str(elf),
        ],
        cwd=root,
        out_path=out_dir / f"last-bpc-{safe_bpc}.disasm.txt",
        timeout=120,
        dry_run=dry_run,
    )
    return {
        "last_brob_bpc_disasm": window["output"],
        "last_brob_bpc_window": f"0x{start:x}..0x{stop:x}",
    }


def static_check_text(text: str, *, require_entry: bool) -> tuple[bool, list[str]]:
    findings: list[str] = []
    if FORBIDDEN_ASM_RE.search(text):
        findings.append("forbidden retired pre-canonical token found")
    if require_entry and not re.search(r"(\b_start\b|\bmain\b)", text):
        findings.append("missing _start/main symbol in objdump evidence")
    return not findings, findings


def compiler_contract(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    timeout: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    env = os.environ.copy()
    env.setdefault("LINXISA_ROOT", str(root))
    for state in states:
        case = state.case
        if not case_can_enter(state, "source-contract"):
            rows.append(
                stage_row(
                    state,
                    "compiler-contract",
                    "skipped",
                    owner="compiler",
                    evidence="source contract did not pass",
                )
            )
            continue
        case_artifacts = state.case_dir / "compiler"
        log_path = case_artifacts / "compile.log"
        artifacts: dict[str, str] = {}
        if case.kind == "supernpu":
            linker_script = case_artifacts / "linx-supernpu-directboot.ld"
            linker_script.parent.mkdir(parents=True, exist_ok=True)
            linker_script.write_text(LINX_DIRECT_BOOT_LINK_SCRIPT, encoding="utf-8")
            artifacts["linker_script"] = str(linker_script)
            supernpu_output = case_artifacts / "supernpu-output"
            elf_dir = supernpu_output / case.metadata["elf_dir_rel"]
            artifacts["obj_root"] = str(supernpu_output)
            before_elves = snapshot_elf_mtimes(elf_dir)
            cmd = supernpu_make_command(
                case,
                paths,
                tileop_api_root=root / LINX_TILEOP_API_REL,
                linker_script=linker_script,
                obj_root=supernpu_output,
            )
            result = run_command(
                cmd,
                cwd=case.workdir,
                env=env,
                timeout=timeout,
                log_path=log_path,
                dry_run=dry_run,
            )
            metadata_elf = Path(case.metadata["elf"])
            elf = elf_dir / metadata_elf.name
            artifacts["log"] = str(log_path)
            artifacts["elf_source"] = str(elf)
            status = result["status"]
            evidence = "SuperNPUBench case compiled to Linx ELF"
            owner = "compiler"
            if status == "pass":
                if not dry_run:
                    actual_elf = find_supernpu_elf_after_compile(
                        case,
                        root,
                        before_elves,
                        elf_dir=elf_dir,
                    )
                    if actual_elf is not None:
                        elf = actual_elf
                        artifacts["elf_source"] = str(elf)
                if not dry_run and not elf.exists():
                    status = "fail"
                    owner, evidence = classify_supernpu_missing_elf(log_path, elf)
                else:
                    copied = case_artifacts / f"{case.id}.elf"
                    copied.parent.mkdir(parents=True, exist_ok=True)
                    if not dry_run and elf.exists():
                        shutil.copy2(elf, copied)
                        state.immutable_artifacts = capture_immutable_artifacts(
                            {
                                "compiler": Path(paths["clangxx"]),
                                "linker": Path(paths["lld"]),
                                "elf": copied,
                            }
                        )
                        identity_path = case_artifacts / "immutable-artifacts.json"
                        write_json(identity_path, state.immutable_artifacts)
                        state.artifacts["immutable_artifacts"] = str(identity_path)
                        artifacts["immutable_artifacts"] = str(identity_path)
                    state.artifacts["elf"] = str(copied)
                    artifacts["elf"] = str(copied)
                    objdump = Path(paths["llvm_objdump"])
                    if dry_run or executable(objdump):
                        dump = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-d", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.disasm.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        sym = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-t", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.symbols.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        sec = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-h", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.sections.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        rel = run_obj_tool(
                            paths["llvm_objdump"],
                            ["-r", str(copied)],
                            cwd=root,
                            out_path=case_artifacts / "objdump.relocs.txt",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        artifacts.update(
                            {
                                "disasm": dump["output"],
                                "symbols": sym["output"],
                                "sections": sec["output"],
                                "relocations": rel["output"],
                            }
                        )
                        if not dry_run:
                            text = "\n".join(
                                Path(p).read_text(encoding="utf-8", errors="replace")
                                for p in [dump["output"], sym["output"], sec["output"], rel["output"]]
                                if Path(p).exists()
                            )
                            ok, findings = static_check_text(text, require_entry=True)
                            if not ok:
                                status = "fail"
                                evidence = "; ".join(findings)
                    objcopy = Path(paths["llvm_objcopy"])
                    if dry_run or executable(objcopy):
                        raw = case_artifacts / f"{case.id}.bin"
                        objcopy_row = run_obj_tool(
                            paths["llvm_objcopy"],
                            ["-O", "binary", str(copied), str(raw)],
                            cwd=root,
                            out_path=case_artifacts / "objcopy.log",
                            timeout=120,
                            dry_run=dry_run,
                        )
                        artifacts["raw_bin"] = str(raw)
                        artifacts["objcopy_log"] = objcopy_row["output"]
            elif status == "not_run":
                copied = case_artifacts / f"{case.id}.elf"
                state.artifacts["elf"] = str(copied)
                artifacts["elf"] = str(copied)
                evidence = "dry-run compile command recorded"
                owner = "compiler"
            else:
                owner, evidence = classify_supernpu_compile_failure(log_path)
            rows.append(
                stage_row(
                    state,
                    "compiler-contract",
                    status,
                    owner=owner,
                    evidence=evidence,
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue

        rows.append(
            stage_row(
                state,
                "compiler-contract",
                "fail",
                owner="compiler",
                evidence=f"unsupported case kind: {case.kind}",
            )
        )
    return rows


def qemu_execution(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    timeout: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    env = os.environ.copy()
    env.setdefault("LINXISA_ROOT", str(root))
    env.setdefault("LINX_VIRT_TEST_FINISHER", "1")
    for state in states:
        case = state.case
        if not case_can_enter(state, "compiler-contract"):
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    "skipped",
                    owner="emulator",
                    evidence="compiler contract did not pass",
                )
            )
            continue
        if not case.produces_elf:
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    "not_applicable",
                    owner="emulator",
                    evidence="case has no standalone ELF harness yet",
                )
            )
            continue
        artifacts: dict[str, str] = {}
        case_artifacts = state.case_dir / "qemu"
        log_path = case_artifacts / "qemu.log"
        if case.kind == "supernpu":
            elf_text = state.artifacts.get("elf")
            if elf_text:
                elf = Path(elf_text)
            else:
                metadata_elf = Path(case.metadata["elf"])
                elf = metadata_elf if metadata_elf.is_absolute() else root / metadata_elf
            if not elf.exists() and not dry_run:
                rows.append(
                    stage_row(
                        state,
                        "qemu-execution",
                        "fail",
                        owner="emulator",
                        evidence="missing compiler-produced ELF for QEMU",
                    )
                )
                continue
            if not dry_run:
                try:
                    verify_recorded_artifacts(
                        state.immutable_artifacts, consumer="qemu"
                    )
                    state.immutable_artifacts.update(
                        capture_immutable_artifacts({"qemu": Path(paths["qemu"])})
                    )
                    verify_recorded_artifacts(
                        state.immutable_artifacts, consumer="qemu"
                    )
                    identity_path = case_artifacts / "immutable-artifacts.json"
                    write_json(identity_path, state.immutable_artifacts)
                    state.artifacts["immutable_artifacts"] = str(identity_path)
                except ArtifactIntegrityError as exc:
                    rows.append(
                        stage_row(
                            state,
                            "qemu-execution",
                            "fail",
                            owner="integration",
                            evidence=str(exc),
                        )
                    )
                    continue
            cmd = [
                paths["qemu"],
                "-machine",
                "virt",
                "-bios",
                "none",
                "-kernel",
                str(elf),
                "-nographic",
                "-monitor",
                "none",
            ]
            result = run_command(
                cmd,
                cwd=root,
                env=env,
                timeout=timeout,
                log_path=log_path,
                dry_run=dry_run,
            )
            result = normalize_qemu_finisher_result(result, log_path)
            artifacts.update({"log": str(log_path), "elf": str(elf)})
            if result["status"] == "pass":
                state.qemu_digests = parse_digests(log_path)
            rows.append(
                stage_row(
                    state,
                    "qemu-execution",
                    result["status"],
                    owner="emulator",
                    evidence="SuperNPUBench ELF passed QEMU" if result["status"] == "pass" else "SuperNPUBench QEMU execution failed",
                    command=result["command"],
                    artifacts=artifacts,
                )
            )
            continue
        rows.append(
            stage_row(
                state,
                "qemu-execution",
                "not_applicable",
                owner="emulator",
                evidence=f"QEMU stage not defined for kind {case.kind}",
            )
        )
    return rows


def find_smoke_elf(states: list[CaseState], override: str | None) -> Path | None:
    if override:
        return Path(override).expanduser().resolve()
    return None


def build_model_smoke_elf(
    root: Path,
    paths: dict[str, str],
    stage_dir: Path,
    env: dict[str, str],
    dry_run: bool,
    timeout: int,
) -> tuple[Path, list[dict[str, Any]]]:
    source = stage_dir / "linx-model-smoke.cpp"
    linker = stage_dir / "linx-model-smoke.ld"
    elf = stage_dir / "linx-model-smoke.elf"
    source.write_text(LINX_MODEL_SMOKE_SOURCE, encoding="utf-8")
    linker.write_text(LINX_DIRECT_BOOT_LINK_SCRIPT, encoding="utf-8")
    cmd = [
        paths["clangxx"],
        "-target",
        "linx64-linx-none-elf",
        "-O2",
        "-ffreestanding",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-exceptions",
        "-fno-rtti",
        "-nostdlib",
        str(source),
        "-Wl,-e,_start",
        f"-Wl,-T,{linker}",
        "-o",
        str(elf),
    ]
    row = run_command(
        cmd,
        cwd=root,
        env=env,
        timeout=timeout,
        log_path=stage_dir / "linx-model-smoke-compile.log",
        dry_run=dry_run,
    )
    return elf, [row]


def model_build_smoke(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    build_timeout: int,
    smoke_timeout: int,
    skip_build: bool,
    smoke_elf_override: str | None,
) -> dict[str, Any]:
    model_root = Path(paths["model_root"])
    gfsim = Path(paths["gfsim"])
    if not any(state.case.model_eligible and state.case.produces_elf for state in states):
        row = {
            "stage": "model-build-smoke",
            "status": "not_applicable",
            "owner": "model",
            "evidence": "no selected model-eligible executable cases",
            "gfsim": str(gfsim),
            "smoke_elf": None,
            "commands": [],
        }
        artifacts = {"gfsim": str(gfsim)}
        for state in states:
            state.stages["model-build-smoke"] = {
                "stage": "model-build-smoke",
                "status": "not_applicable",
                "owner": "model",
                "evidence": row["evidence"],
                "command": None,
                "commands": [],
                "artifacts": artifacts,
            }
        return row

    stage_dir = states[0].case_dir.parent / "_model" if states else root / "workloads" / "generated" / "_model"
    stage_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    rows: list[dict[str, Any]] = []
    if not dry_run and not skip_build:
        configure = run_command(
            [
                "cmake",
                "-S",
                str(model_root),
                "-B",
                str(model_root / "build"),
                "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
                "-DOPT_LEVEL=O3",
                "-DDISABLE_DEBUG_SYMBOLS=ON",
            ],
            cwd=root,
            env=env,
            timeout=build_timeout,
            log_path=stage_dir / "cmake-configure.log",
            dry_run=False,
        )
        rows.append(configure)
        if configure["status"] == "pass":
            build = run_command(
                ["cmake", "--build", str(model_root / "build"), "--target", "gfsim"],
                cwd=root,
                env=env,
                timeout=build_timeout,
                log_path=stage_dir / "cmake-build-gfsim.log",
                dry_run=False,
            )
            rows.append(build)
    elif dry_run:
        rows.append(
            {
                "status": "not_run",
                "command": (
                    f"cmake -S {model_root} -B {model_root / 'build'} "
                    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DOPT_LEVEL=O3 "
                    f"-DDISABLE_DEBUG_SYMBOLS=ON && cmake --build {model_root / 'build'} --target gfsim"
                ),
                "log": str(stage_dir / "cmake-build-gfsim.log"),
            }
        )

    smoke_elf = find_smoke_elf(states, smoke_elf_override)
    if smoke_elf is None:
        smoke_elf, smoke_compile_rows = build_model_smoke_elf(
            root,
            paths,
            stage_dir,
            env,
            dry_run,
            build_timeout,
        )
        rows.extend(smoke_compile_rows)
    else:
        smoke_compile_rows = []

    gfsim_exists = dry_run or executable(gfsim)
    smoke_row: dict[str, Any] | None = None
    if gfsim_exists and smoke_elf is not None:
        smoke_cmd = [str(gfsim), "-f", str(smoke_elf)]
        smoke_row = run_command(
            smoke_cmd,
            cwd=model_root,
            env=env,
            timeout=smoke_timeout,
            log_path=stage_dir / "gfsim-smoke.log",
            dry_run=dry_run,
        )
        rows.append(smoke_row)

    failed_build = next((row for row in rows if row.get("status") not in PASS_STATUSES), None)
    owner = "model"
    if failed_build is not None:
        status = failed_build["status"]
        owner = "compiler" if failed_build in smoke_compile_rows else "model"
        if failed_build in smoke_compile_rows:
            evidence = "model smoke ELF compile timed out" if status == "timeout" else "model smoke ELF compile failed"
        else:
            evidence = "LinxCoreModel build/smoke timed out" if status == "timeout" else "LinxCoreModel build/smoke failed"
    elif not gfsim_exists:
        status = "fail"
        evidence = f"gfsim not found or not executable: {gfsim}"
    elif smoke_elf is None:
        status = "skipped"
        evidence = "no QEMU-passing smoke ELF available yet"
    elif smoke_row and smoke_row["status"] == "not_run":
        status = "not_run"
        evidence = "dry-run model build/smoke recorded"
    else:
        status = "pass"
        evidence = "gfsim available and smoke command passed"

    row = {
        "stage": "model-build-smoke",
        "status": status,
        "owner": owner,
        "evidence": evidence,
        "gfsim": str(gfsim),
        "smoke_elf": str(smoke_elf) if smoke_elf is not None else None,
        "commands": rows,
    }
    artifacts = {
        "gfsim": str(gfsim),
        "configure_log": str(stage_dir / "cmake-configure.log"),
        "build_log": str(stage_dir / "cmake-build-gfsim.log"),
        "smoke_log": str(stage_dir / "gfsim-smoke.log"),
    }
    if smoke_elf is not None:
        artifacts["smoke_elf"] = str(smoke_elf)
    if smoke_elf_override is None:
        artifacts.update(
            {
                "smoke_source": str(stage_dir / "linx-model-smoke.cpp"),
                "smoke_linker_script": str(stage_dir / "linx-model-smoke.ld"),
                "smoke_compile_log": str(stage_dir / "linx-model-smoke-compile.log"),
            }
        )
    for state in states:
        state.stages["model-build-smoke"] = {
            "stage": "model-build-smoke",
            "status": status,
            "owner": owner,
            "evidence": evidence,
            "command": row["commands"][-1]["command"] if row["commands"] else None,
            "commands": rows,
            "artifacts": artifacts,
        }
        if status not in PASS_STATUSES:
            mark_failure(state, "model-build-smoke", owner, evidence)
    return row


def linxcoremodel_execution(
    root: Path,
    states: list[CaseState],
    paths: dict[str, str],
    dry_run: bool,
    timeout: int,
    model_stage_ok: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    model_root = Path(paths["model_root"])
    gfsim = Path(paths["gfsim"])
    env = os.environ.copy()
    for state in states:
        case = state.case
        qemu_row = state.stages.get("qemu-execution")
        if not model_stage_ok:
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "skipped",
                    owner="model",
                    evidence="model build/smoke did not pass",
                )
            )
            continue
        if not case.model_eligible or not case.produces_elf:
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "not_applicable",
                    owner="model",
                    evidence="case is not model-eligible yet",
                )
            )
            continue
        if qemu_row is None or qemu_row["status"] != "pass":
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "skipped",
                    owner="model",
                    evidence="QEMU did not pass for this case",
                )
            )
            continue
        elf = Path(state.artifacts.get("elf", ""))
        if not dry_run and not elf.exists():
            rows.append(
                stage_row(
                    state,
                    "linxcoremodel-execution",
                    "fail",
                    owner="model",
                    evidence=f"missing QEMU-passing ELF: {elf}",
                )
            )
            continue
        if not dry_run:
            try:
                verify_recorded_artifacts(
                    state.immutable_artifacts, consumer="model"
                )
                state.immutable_artifacts.update(
                    capture_immutable_artifacts({"model": gfsim})
                )
                verify_recorded_artifacts(
                    state.immutable_artifacts, consumer="model"
                )
                identity_path = state.case_dir / "model" / "immutable-artifacts.json"
                write_json(identity_path, state.immutable_artifacts)
                state.artifacts["immutable_artifacts"] = str(identity_path)
            except ArtifactIntegrityError as exc:
                rows.append(
                    stage_row(
                        state,
                        "linxcoremodel-execution",
                        "fail",
                        owner="integration",
                        evidence=str(exc),
                    )
                )
                continue
        log_path = state.case_dir / "model" / "gfsim.log"
        cmd = [str(gfsim), "-f", str(elf)]
        result = run_command(
            cmd,
            cwd=model_root,
            env=env,
            timeout=timeout,
            log_path=log_path,
            dry_run=dry_run,
        )
        if result["status"] == "pass":
            state.model_digests = parse_digests(log_path)
        evidence, diagnostics = summarize_gfsim_log(result["status"], log_path)
        artifacts = {"log": str(log_path), "elf": str(elf)}
        artifacts.update(diagnostics)
        artifacts.update(
            emit_bpc_disassembly_window(
                paths=paths,
                root=root,
                elf=elf,
                bpc=diagnostics.get("last_brob_bpc"),
                out_dir=state.case_dir / "model",
                dry_run=dry_run,
            )
        )
        rows.append(
            stage_row(
                state,
                "linxcoremodel-execution",
                result["status"],
                owner="model",
                evidence=evidence,
                command=result["command"],
                artifacts=artifacts,
            )
        )
    return rows


def differential_triage(states: list[CaseState]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for state in states:
        case = state.case
        qemu = state.qemu_digests
        model = state.model_digests
        status = "pass"
        evidence = "no digest comparison required"
        if qemu and model:
            missing = sorted(set(qemu) ^ set(model))
            mismatched = sorted(k for k in set(qemu) & set(model) if qemu[k] != model[k])
            if missing or mismatched:
                status = "fail"
                evidence = (
                    f"digest mismatch; missing={missing or []}; mismatched={mismatched or []}"
                )
                mark_failure(state, "differential-triage", "model", evidence)
            else:
                evidence = f"{len(qemu)} digest(s) matched between QEMU and model"
        elif qemu and not model:
            model_row = state.stages.get("linxcoremodel-execution", {})
            if model_row.get("status") == "pass":
                status = "fail"
                evidence = "QEMU emitted digests but model emitted none"
                mark_failure(state, "differential-triage", "model", evidence)
            else:
                status = "skipped"
                evidence = "model did not pass, digest comparison skipped"
        elif state.failure_stage:
            status = "skipped"
            evidence = f"first failure already assigned to {state.failure_owner}"
        rows.append(
            stage_row(
                state,
                "differential-triage",
                status,
                owner=state.failure_owner or "integration",
                evidence=evidence,
                artifacts={
                    "qemu_digest_count": str(len(qemu)),
                    "model_digest_count": str(len(model)),
                },
            )
        )
    return rows


def final_artifact_verification(states: list[CaseState]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for state in states:
        if not state.immutable_artifacts:
            continue
        try:
            verify_recorded_artifacts(
                state.immutable_artifacts, consumer="final verification"
            )
            status = "pass"
            evidence = "all recorded artifact SHA-256 values remain unchanged"
        except ArtifactIntegrityError as exc:
            status = "fail"
            evidence = str(exc)
        rows.append(
            stage_row(
                state,
                "immutable-artifact-final-verification",
                status,
                owner="integration",
                evidence=evidence,
                artifacts={
                    "immutable_artifacts": state.artifacts.get("immutable_artifacts", "")
                },
            )
        )
    return rows


def write_fix_packets(out_dir: Path, states: list[CaseState]) -> list[dict[str, Any]]:
    packet_dir = out_dir / "fix-packets"
    rows: list[dict[str, Any]] = []
    for state in states:
        packet_path = packet_dir / f"{state.case.id}.json"
        if not state.failure_stage:
            if packet_path.exists():
                packet_path.unlink()
            rows.append(
                stage_row(
                    state,
                    "fix-packets",
                    "not_applicable",
                    owner="integration",
                    evidence="case is green or only skipped for non-applicable stages",
                )
            )
            continue
        case = state.case
        failed_row = state.stages.get(state.failure_stage, {})
        packet = {
            "schema_version": 1,
            "generated_at_utc": utc_now(),
            "case": {
                "id": case.id,
                "kind": case.kind,
                "suite": case.suite,
                "tier": case.tier,
                "sources": [str(path) for path in case.source_paths],
                "manifest": str(case.manifest_path) if case.manifest_path else None,
                "workdir": str(case.workdir),
                "model_eligible": case.model_eligible,
                "produces_elf": case.produces_elf,
                "expected": case.expected,
                "metadata": case.metadata,
            },
            "failure": {
                "stage": state.failure_stage,
                "owner": state.failure_owner,
                "evidence": state.failure_evidence,
                "row": failed_row,
            },
            "repro": {
                "command": failed_row.get("command"),
                "cwd": str(case.workdir),
                "expected_next_boundary": next_boundary(state.failure_stage),
            },
            "artifacts": state.artifacts,
            "stage_rows": state.stages,
        }
        write_json(packet_path, packet)
        rows.append(
            stage_row(
                state,
                "fix-packets",
                "pass",
                owner="integration",
                evidence=f"fix packet emitted for {state.failure_owner}",
                artifacts={"fix_packet": str(packet_path)},
            )
        )
    return rows


def next_boundary(stage_id: str | None) -> str:
    order = [
        "source-contract",
        "compiler-contract",
        "qemu-execution",
        "model-build-smoke",
        "linxcoremodel-execution",
        "differential-triage",
    ]
    if stage_id not in order:
        return "source-contract"
    idx = order.index(stage_id)
    return order[min(idx + 1, len(order) - 1)]


def write_skill_doc_evolution(out_dir: Path, states: list[CaseState], evolve_note: str | None = None) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for state in states:
        if state.failure_owner:
            counts[state.failure_owner] = counts.get(state.failure_owner, 0) + 1
    if evolve_note:
        note = evolve_note.strip()
        if note.startswith(("updated", "no-update")):
            line = f"skill-evolve: {note}"
        else:
            line = f"skill-evolve: updated {note}"
    else:
        line = "skill-evolve: no-update (runner emitted reusable evidence; update skills only after a material repeated finding)"
    payload = {
        "stage": "skill-doc-evolution",
        "status": "pass",
        "owner": "docs-skills",
        "generated_at_utc": utc_now(),
        "skill_evolve": line,
        "failure_owner_counts": counts,
        "documentation": [
            "docs/bringup/ai_workload_bringup_flow.json",
            "tools/bringup/run_ai_workload_flow.py",
        ],
    }
    write_json(out_dir / "skill_evolution.json", payload)
    (out_dir / "skill_evolution.md").write_text(
        "# Skill And Documentation Evolution\n\n"
        f"- {line}\n"
        f"- Failure owner counts: `{json.dumps(counts, sort_keys=True)}`\n",
        encoding="utf-8",
    )
    return payload


def stage_failed(rows: list[dict[str, Any]] | dict[str, Any]) -> bool:
    if isinstance(rows, dict):
        return rows.get("status") not in PASS_STATUSES
    return any(row.get("status") not in PASS_STATUSES for row in rows)


def case_final_status(state: CaseState, emitted_stage_ids: set[str]) -> str:
    if state.failure_stage:
        return "fail"
    if "linxcoremodel-execution" not in emitted_stage_ids:
        return "pending"
    model_row = state.stages.get("linxcoremodel-execution")
    if not model_row:
        return "pending"
    return model_row.get("status", "pending")


def case_summary(state: CaseState, emitted_stage_ids: set[str]) -> dict[str, Any]:
    final_status = case_final_status(state, emitted_stage_ids)
    return {
        "id": state.case.id,
        "kind": state.case.kind,
        "suite": state.case.suite,
        "tier": state.case.tier,
        "final_status": final_status,
        "failure_stage": state.failure_stage,
        "failure_owner": state.failure_owner,
        "failure_evidence": state.failure_evidence,
        "artifacts": state.artifacts,
        "stages": state.stages,
    }


def write_manifest(
    root: Path,
    out_dir: Path,
    *,
    flow: dict[str, Any],
    profile: str,
    tiers: set[int],
    dry_run: bool,
    paths: dict[str, str],
    cases: list[Case],
    revisions: dict[str, Any],
) -> None:
    payload = {
        "schema_version": 2,
        "generated_at_utc": utc_now(),
        "flow_id": flow.get("flow_id"),
        "profile": profile,
        "tiers": sorted(tiers),
        "dry_run": dry_run,
        "repo_root": str(root),
        "tools": tool_manifest(paths),
        "revisions": revisions,
        "cases": [
            {
                "id": case.id,
                "kind": case.kind,
                "suite": case.suite,
                "tier": case.tier,
                "sources": [relpath(root, p) for p in case.source_paths],
                "manifest": relpath(root, case.manifest_path) if case.manifest_path else None,
                "model_eligible": case.model_eligible,
                "produces_elf": case.produces_elf,
                "expected": case.expected,
                "metadata": case.metadata,
            }
            for case in cases
        ],
    }
    write_json(out_dir / "manifest.json", payload)


def write_report(
    out_dir: Path,
    *,
    flow: dict[str, Any],
    profile: str,
    tiers: set[int],
    dry_run: bool,
    stages: list[dict[str, Any]],
    states: list[CaseState],
    skill_evolution: dict[str, Any] | None,
) -> None:
    emitted_stage_ids = {stage["id"] for stage in stages}
    case_summaries = [case_summary(state, emitted_stage_ids) for state in states]
    payload = {
        "schema_version": 1,
        "generated_at_utc": utc_now(),
        "flow_id": flow.get("flow_id"),
        "profile": profile,
        "tiers": sorted(tiers),
        "dry_run": dry_run,
        "ok": all(summary["final_status"] in PASS_STATUSES for summary in case_summaries),
        "stages": stages,
        "cases": case_summaries,
        "skill_evolution": skill_evolution,
    }
    write_json(out_dir / "report.json", payload)


def write_summary(
    out_dir: Path,
    states: list[CaseState],
    skill_evolution: dict[str, Any] | None,
    stages: list[dict[str, Any]],
) -> None:
    emitted_stage_ids = {stage["id"] for stage in stages}
    summaries = [case_summary(state, emitted_stage_ids) for state in states]
    total = len(states)
    failures = [s for s in states if s.failure_stage]
    pending = [summary for summary in summaries if summary["final_status"] == "pending"]
    final_green = [
        s
        for s in states
        if not s.failure_stage
        and s.stages.get("linxcoremodel-execution", {}).get("status") == "pass"
    ]
    lines = [
        "# AI Workload Bring-Up Summary",
        "",
        f"- Generated (UTC): `{utc_now()}`",
        f"- Cases selected: `{total}`",
        f"- Final model green: `{len(final_green)}`",
        f"- Failed cases: `{len(failures)}`",
        f"- Pending cases: `{len(pending)}`",
        "",
        "| Case | Kind | Tier | Final | First Owner | Evidence |",
        "|---|---:|---:|---|---|---|",
    ]
    for state, summary in zip(states, summaries, strict=True):
        evidence = (summary.get("failure_evidence") or "").replace("|", "\\|")
        lines.append(
            f"| `{state.case.id}` | `{state.case.kind}` | `{state.case.tier}` | "
            f"`{summary['final_status']}` | `{summary.get('failure_owner') or '-'}` | {evidence or '-'} |"
        )
    if skill_evolution:
        lines += ["", "## Skill Evolution", "", f"- {skill_evolution['skill_evolve']}"]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def print_stage_list(stages: list[dict[str, Any]], cases: list[Case]) -> None:
    for idx, stage in enumerate(stages, start=1):
        hard = "hard-break" if stage.get("hard_break", True) else "non-blocking"
        print(f"{idx}. {stage['id']} [{stage.get('owner', 'unknown')}/{hard}]")
        if stage.get("why"):
            print(f"   {stage['why']}")
    print()
    for case in cases:
        print(f"{case.id} [{case.kind}/tier-{case.tier}] {case.suite}")


def main(argv: list[str]) -> int:
    root = repo_root()
    ap = argparse.ArgumentParser(
        description="Run the AI workload hard-break flow through Linx LLVM, QEMU, and LinxCoreModel."
    )
    ap.add_argument("--flow", default=str(default_flow_path(root)))
    ap.add_argument("--profile", default="smoke")
    ap.add_argument("--tier", type=int, action="append", default=[], help="Override profile tiers; may repeat")
    ap.add_argument(
        "--case",
        action="append",
        default=[],
        help="Select cases whose id/suite/kind contains this text; prefix with '=' for an exact id/suite/kind match; may repeat",
    )
    ap.add_argument("--kind", action="append", choices=["supernpu"], default=[])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--stage", action="append", default=[], help="Run one stage id; may repeat")
    ap.add_argument("--start-at", default=None)
    ap.add_argument("--stop-after", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not execute toolchain/model commands; still write manifest, report, logs, and summary artifacts.",
    )
    ap.add_argument("--continue-on-fail", action="store_true")
    ap.add_argument("--run-id", default=default_run_id())
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--clang", default="")
    ap.add_argument("--clangxx", default="")
    ap.add_argument("--lld", default="")
    ap.add_argument("--llvm-objdump", default="")
    ap.add_argument("--llvm-objcopy", default="")
    ap.add_argument("--qemu", default="")
    ap.add_argument("--model-root", default="")
    ap.add_argument("--gfsim", default="")
    ap.add_argument("--model-smoke-elf", default="")
    ap.add_argument("--skip-model-build", action="store_true")
    ap.add_argument("--skill-evolve-note", default="", help="Emit `skill-evolve: update <note>` in the run closeout")
    ap.add_argument("--compile-timeout", type=int, default=900)
    ap.add_argument("--qemu-timeout", type=int, default=240)
    ap.add_argument("--model-timeout", type=int, default=600)
    ap.add_argument("--model-build-timeout", type=int, default=3600)
    args = ap.parse_args(argv)

    flow_path = Path(args.flow).resolve()
    flow = load_flow(flow_path)
    stages = selected_stages(flow, args.profile, args.stage, args.start_at, args.stop_after)
    if not args.list:
        validate_execution_stage_prefix(flow, args.profile, args.stage, stages)
    tiers = profile_tiers(flow, args.profile, args.tier)

    revisions: dict[str, Any] | None = None
    if not args.list:
        revisions = exact_pin_evidence(root)
    all_cases = discover_cases(root)
    cases = filter_cases(all_cases, tiers, args.kind, args.case, args.limit)
    if not cases:
        if revisions and revisions["errors"]:
            raise SystemExit(
                "error: exact-pin validation failed before workload discovery: "
                + "; ".join(revisions["errors"])
            )
        raise SystemExit("error: no cases selected")

    if args.list:
        print_stage_list(stages, cases)
        return 0

    assert revisions is not None
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root / "workloads" / "generated" / args.run_id / "ai-bringup"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = tool_paths(
        root,
        args,
        strict_qemu=not args.dry_run and bool(revisions["valid"]),
    )
    states = [CaseState(case=case, case_dir=out_dir / "cases" / case.id) for case in cases]
    write_manifest(
        root,
        out_dir,
        flow=flow,
        profile=args.profile,
        tiers=tiers,
        dry_run=args.dry_run,
        paths=paths,
        cases=cases,
        revisions=revisions,
    )

    stage_reports: list[dict[str, Any]] = []
    failed = False
    model_stage_status = True
    skill_evolution: dict[str, Any] | None = None

    for stage in stages:
        stage_id = stage["id"]
        print(f"== {stage_id} ({stage.get('owner', 'unknown')})")
        if stage_id == "source-contract":
            rows: list[dict[str, Any]] | dict[str, Any] = source_contract(
                root, states, args.dry_run, revisions
            )
        elif stage_id == "compiler-contract":
            rows = compiler_contract(root, states, paths, args.dry_run, args.compile_timeout)
        elif stage_id == "qemu-execution":
            rows = qemu_execution(root, states, paths, args.dry_run, args.qemu_timeout)
        elif stage_id == "model-build-smoke":
            rows = model_build_smoke(
                root,
                states,
                paths,
                args.dry_run,
                args.model_build_timeout,
                args.model_timeout,
                args.skip_model_build,
                args.model_smoke_elf or None,
            )
            model_stage_status = rows.get("status") in PASS_STATUSES
        elif stage_id == "linxcoremodel-execution":
            rows = linxcoremodel_execution(
                root,
                states,
                paths,
                args.dry_run,
                args.model_timeout,
                model_stage_status,
            )
        elif stage_id == "differential-triage":
            rows = differential_triage(states)
        elif stage_id == "fix-packets":
            rows = write_fix_packets(out_dir, states)
        elif stage_id == "skill-doc-evolution":
            skill_evolution = write_skill_doc_evolution(out_dir, states, args.skill_evolve_note or None)
            rows = skill_evolution
        else:
            raise SystemExit(f"error: unsupported stage id in flow: {stage_id}")

        stage_reports.append(
            {
                "id": stage_id,
                "owner": stage.get("owner"),
                "hard_break": bool(stage.get("hard_break", True)),
                "result": rows,
            }
        )
        write_report(
            out_dir,
            flow=flow,
            profile=args.profile,
            tiers=tiers,
            dry_run=args.dry_run,
            stages=stage_reports,
            states=states,
            skill_evolution=skill_evolution,
        )
        write_summary(out_dir, states, skill_evolution, stage_reports)
        if stage_failed(rows):
            failed = True
            if stage.get("hard_break", True) and not args.continue_on_fail:
                print(f"hard-break: stopping at stage {stage_id}")
                break

    emitted_stage_ids = {stage["id"] for stage in stage_reports}
    artifact_rows = final_artifact_verification(states)
    if artifact_rows:
        stage_reports.append(
            {
                "id": "immutable-artifact-final-verification",
                "owner": "integration",
                "hard_break": True,
                "result": artifact_rows,
            }
        )
        if stage_failed(artifact_rows):
            failed = True
        emitted_stage_ids.add("immutable-artifact-final-verification")
    if any(state.failure_stage for state in states) and "fix-packets" not in emitted_stage_ids:
        rows = write_fix_packets(out_dir, states)
        stage_reports.append(
            {
                "id": "fix-packets",
                "owner": "integration",
                "hard_break": False,
                "result": rows,
            }
        )

    if skill_evolution is None:
        skill_evolution = write_skill_doc_evolution(out_dir, states)
        stage_reports.append(
            {
                "id": "skill-doc-evolution",
                "owner": "docs-skills",
                "hard_break": False,
                "result": skill_evolution,
            }
        )

    write_report(
        out_dir,
        flow=flow,
        profile=args.profile,
        tiers=tiers,
        dry_run=args.dry_run,
        stages=stage_reports,
        states=states,
        skill_evolution=skill_evolution,
    )
    write_summary(out_dir, states, skill_evolution, stage_reports)

    print(f"manifest: {out_dir / 'manifest.json'}")
    print(f"report: {out_dir / 'report.json'}")
    print(f"summary: {out_dir / 'summary.md'}")
    if failed:
        return 1
    print("ok: AI workload flow complete" if not args.dry_run else "ok: AI workload dry-run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
