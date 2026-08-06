#!/usr/bin/env python3
"""Generate form-ID Sail semantic grades from the canonical ISA catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_STATUSES = {"decode-only", "executable-subset", "architecturally-complete"}


def _read(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def build(spec_path: Path, policy_path: Path) -> dict[str, Any]:
    spec = _read(spec_path)
    policy = _read(policy_path)
    default = str(policy.get("default_status") or "")
    overrides = policy.get("form_overrides") or {}
    if default not in VALID_STATUSES:
        raise ValueError(f"{policy_path}: invalid default_status {default!r}")
    if not isinstance(overrides, dict):
        raise ValueError(f"{policy_path}: form_overrides must be an object")

    instructions = spec.get("instructions")
    if not isinstance(instructions, list):
        raise ValueError(f"{spec_path}: instructions must be a list")
    form_ids = {str(inst.get("id") or "") for inst in instructions}
    unknown = sorted(set(overrides) - form_ids)
    if unknown:
        raise ValueError(f"{policy_path}: unknown form IDs: {unknown[:20]}")

    forms: dict[str, Any] = {}
    for inst in sorted(instructions, key=lambda item: str(item.get("id") or "")):
        form_id = str(inst.get("id") or "")
        status = str(overrides.get(form_id, default))
        if status not in VALID_STATUSES:
            raise ValueError(f"{policy_path}: invalid status {status!r} for {form_id}")
        forms[form_id] = {
            "mnemonic": str(inst.get("mnemonic") or ""),
            "status": status,
        }

    return {
        "schema_version": f"linx-sail-status-v{spec.get('version', '')}",
        "spec_version": str(spec.get("version") or ""),
        "forms": forms,
    }


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path("isa/v0.58/linxisa-v0.58.json"))
    parser.add_argument("--policy", type=Path, default=Path("isa/sail/semantics_policy.json"))
    parser.add_argument("--out", type=Path, default=Path("isa/sail/semantics_status.json"))
    parser.add_argument("--check", action="store_true", help="Compare output without writing")
    args = parser.parse_args()

    rendered = _canonical(build(args.spec, args.policy))
    if args.check:
        if not args.out.is_file() or args.out.read_text(encoding="utf-8") != rendered:
            print(f"error: {args.out} is out of date", file=sys.stderr)
            return 2
        print("OK")
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
