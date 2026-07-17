#!/usr/bin/env python3
"""
Generate a form-ID Sail semantics coverage report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import Counter
from typing import Any, Dict, List


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_form_statuses(status_path: Path) -> Dict[str, Dict[str, str]]:
    status = _read_json(status_path)
    forms = status.get("forms")
    if not isinstance(forms, dict):
        raise SystemExit(f"error: {status_path} missing object field 'forms'")
    return forms


def _write_json(path: Path, obj: Any, pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pretty:
        path.write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def _relpath_in_repo(p: Path, repo_root: Path) -> str:
    try:
        rp = p.expanduser().resolve()
        rr = repo_root.resolve()
        return str(rp.relative_to(rr))
    except Exception:
        return str(p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="isa/v0.57/linxisa-v0.57.json", help="Compiled ISA catalog JSON")
    ap.add_argument(
        "--status",
        default="isa/sail/semantics_status.json",
        help="Semantic status JSON mapping stable form IDs to semantic grades",
    )
    ap.add_argument("--out", default="isa/sail/coverage.json", help="Output JSON path")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    ap.add_argument("--check", action="store_true", help="Verify --out is up-to-date without writing")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    spec = _read_json(Path(args.spec))
    form_statuses = _read_form_statuses(Path(args.status))

    insts: List[Dict[str, Any]] = list(spec.get("instructions", []))
    total_forms = len(insts)

    canonical_ids = {str(inst.get("id") or "") for inst in insts}
    missing_ids = sorted(canonical_ids - set(form_statuses))
    extra_ids = sorted(set(form_statuses) - canonical_ids)
    if missing_ids or extra_ids:
        raise SystemExit(f"error: form status mismatch: missing={missing_ids[:20]} extra={extra_ids[:20]}")

    grade_counts = Counter(str(form_statuses[form_id].get("status") or "") for form_id in canonical_ids)
    modeled = canonical_ids - {
        form_id for form_id in canonical_ids if form_statuses[form_id].get("status") == "decode-only"
    }
    modeled_mnemonics = sorted(
        {str(inst.get("mnemonic") or "") for inst in insts if str(inst.get("id") or "") in modeled}
    )

    out_obj = {
        # Keep the report deterministic: avoid embedding absolute paths.
        "spec": _relpath_in_repo(Path(args.spec), repo_root),
        "semantic_status": _relpath_in_repo(Path(args.status), repo_root),
        "total_forms": total_forms,
        "grade_counts": dict(sorted(grade_counts.items())),
        "modeled_forms": len(modeled),
        "decode_only_forms": int(grade_counts.get("decode-only", 0)),
        "modeled_mnemonics": modeled_mnemonics,
    }

    out_path = Path(args.out)
    if args.check:
        if not out_path.exists():
            print(f"error: missing {out_path} (run sail_coverage.py)", file=sys.stderr)
            return 2
        existing = _read_json(out_path)
        if _canonical(existing) != _canonical(out_obj):
            print(f"error: {out_path} is out-of-date (run sail_coverage.py)", file=sys.stderr)
            return 2
        print("OK")
        return 0

    _write_json(out_path, out_obj, pretty=bool(args.pretty))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
