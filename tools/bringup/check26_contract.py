#!/usr/bin/env python3
"""
Validate strict LinxISA 26-check bring-up contract.

This gate validates:
  - exactly 26 checks, IDs 1..26
  - each check has non-empty clauses/owners/tests
  - required canonical patterns exist in canonical source artifacts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


def _load_contract(path: Path) -> Dict[str, Any]:
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
        raise RuntimeError(f"{path} must decode to a mapping object")
    return data


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return path.read_text(encoding="latin-1", errors="replace")


def _validate_contract_shape(contract: Dict[str, Any], root: Path) -> List[str]:
    errors: List[str] = []
    checks = contract.get("checks")
    if not isinstance(checks, list):
        return ["contract.checks must be a list"]
    if len(checks) != 26:
        errors.append(f"contract must contain exactly 26 checks, got {len(checks)}")
    ids: List[int] = []
    for idx, chk in enumerate(checks):
        if not isinstance(chk, dict):
            errors.append(f"check[{idx}] must be a mapping")
            continue
        cid = chk.get("id")
        if not isinstance(cid, int):
            errors.append(f"check[{idx}] has non-integer id: {cid!r}")
            continue
        ids.append(cid)

        for key in ("title",):
            v = chk.get(key)
            if not isinstance(v, str) or not v.strip():
                errors.append(f"check[{cid}] missing non-empty {key}")

        for key in ("clauses", "owners", "tests"):
            v = chk.get(key)
            if not isinstance(v, list) or not v:
                errors.append(f"check[{cid}] missing non-empty {key} list")
                continue
            for ent in v:
                if not isinstance(ent, str) or not ent.strip():
                    errors.append(f"check[{cid}] has invalid {key} entry: {ent!r}")

        owners = chk.get("owners")
        if isinstance(owners, list):
            for owner in owners:
                if not isinstance(owner, str):
                    continue
                if owner.startswith("/"):
                    p = Path(owner)
                else:
                    p = root / owner
                if owner.startswith("qemu/") or owner.startswith("linux/") or owner.startswith("llvm/"):
                    continue
                # Absolute owner paths are treated as external lanes/tools and are not
                # required to exist within the current repo checkout.
                if p.is_absolute():
                    continue
                if not p.exists():
                    errors.append(f"check[{cid}] owner path does not exist: {owner}")

    if ids:
        expect = list(range(1, 27))
        if sorted(ids) != expect:
            errors.append(f"check IDs must be contiguous 1..26, got {sorted(ids)}")
    return errors


def _collect_canonical_texts(contract: Dict[str, Any], root: Path) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    texts: List[str] = []
    canon = contract.get("canonical_paths")
    if not isinstance(canon, list) or not canon:
        return [], ["contract.canonical_paths must be a non-empty list"]
    for p in canon:
        if not isinstance(p, str) or not p.strip():
            errors.append(f"invalid canonical path entry: {p!r}")
            continue
        full = root / p
        if not full.exists():
            errors.append(f"canonical path missing: {p}")
            continue
        texts.append(_read_text(full))
    return texts, errors


def _validate_patterns(contract: Dict[str, Any], corpus: Sequence[str]) -> List[str]:
    errors: List[str] = []
    checks = contract.get("checks")
    if not isinstance(checks, list):
        return errors
    haystack = "\n".join(corpus)
    for chk in checks:
        if not isinstance(chk, dict):
            continue
        cid = chk.get("id")
        patterns = chk.get("patterns", [])
        if patterns is None:
            patterns = []
        if not isinstance(patterns, list):
            errors.append(f"check[{cid}] patterns must be a list when present")
            continue
        for pat in patterns:
            if not isinstance(pat, str) or not pat.strip():
                errors.append(f"check[{cid}] invalid pattern: {pat!r}")
                continue
            if re.search(re.escape(pat), haystack) is None:
                errors.append(f"check[{cid}] missing required canonical pattern: {pat!r}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="LinxISA repo root")
    ap.add_argument(
        "--contract",
        default="docs/bringup/check26_contract.yaml",
        help="Path to check26 contract file",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    contract_path = (root / args.contract).resolve()
    if not contract_path.exists():
        print(f"error: missing contract file: {contract_path}", file=sys.stderr)
        return 2

    try:
        contract = _load_contract(contract_path)
    except Exception as exc:
        print(f"error: failed to load contract: {exc}", file=sys.stderr)
        return 2

    errors: List[str] = []
    errors.extend(_validate_contract_shape(contract, root))
    corpus, canon_errors = _collect_canonical_texts(contract, root)
    errors.extend(canon_errors)
    if not canon_errors:
        errors.extend(_validate_patterns(contract, corpus))

    if errors:
        for err in errors[:200]:
            print(err, file=sys.stderr)
        if len(errors) > 200:
            print(f"... {len(errors) - 200} more", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

