#!/usr/bin/env python3
"""
Generate a Sail semantics coverage report.

Coverage is computed as:
  implemented mnemonics / total instruction forms in the compiled catalog.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_implemented(status_path: Path) -> Set[str]:
    if not status_path.exists():
        return set()
    status = _read_json(status_path)
    mnemonics = status.get("mnemonics")
    if not isinstance(mnemonics, dict):
        raise SystemExit(f"error: {status_path} missing object field 'mnemonics'")
    return {name for name, state in mnemonics.items() if str(state).strip() == "implemented"}


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
    ap.add_argument("--spec", default="isa/v0.4/linxisa-v0.4.json", help="Compiled ISA catalog JSON")
    ap.add_argument(
        "--status",
        default="isa/sail/semantics_status.json",
        help="Semantic status JSON mapping mnemonics to implemented|stubbed|unimplemented",
    )
    ap.add_argument("--out", default="isa/sail/coverage.json", help="Output JSON path")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    ap.add_argument("--check", action="store_true", help="Verify --out is up-to-date without writing")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    spec = _read_json(Path(args.spec))
    implemented = _read_implemented(Path(args.status))

    insts: List[Dict[str, Any]] = list(spec.get("instructions", []))
    total_forms = len(insts)

    implemented_forms = [i for i in insts if str(i.get("mnemonic") or "") in implemented]
    missing_forms = [i for i in insts if str(i.get("mnemonic") or "") not in implemented]

    out_obj = {
        # Keep the report deterministic: avoid embedding absolute paths.
        "spec": _relpath_in_repo(Path(args.spec), repo_root),
        "semantic_status": _relpath_in_repo(Path(args.status), repo_root),
        "total_forms": total_forms,
        "implemented_forms": len(implemented_forms),
        "missing_forms": len(missing_forms),
        "implemented_mnemonics": sorted(implemented),
        "missing_mnemonics": sorted({str(i.get("mnemonic") or "") for i in missing_forms}),
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
