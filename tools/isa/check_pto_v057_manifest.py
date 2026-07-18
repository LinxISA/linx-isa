#!/usr/bin/env python3
"""Validate the normalized PTO 0.57 inventory and its Linx encoding map."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = "0387b39f108599f2469c2e2374a46ea4b832a96fee7bf7aa5d7cc575fdc7864a"
EXPORT_SHA256 = "4c75f961e8f2f63e35bce51dec21c97f75c50e2189a0f8c83f95577403984d21"
EXPECTED_NAMES = """
TADD TSUB TMUL TMAX TMIN TAND TOR TXOR TSHL TSHR TCMP TSEL TABS TNOT TNEG TRELU
TDIV TREM TSQRT TLOG TRECIP TEXP TRSQRT TADDS TAXPY TSUBS TMULS TDIVS TMINS TMAXS
TREMS TANDS TORS TXORS TCMPS TSELS TSHLS TSHRS TROWSUM TROWPROD TROWMAX TROWMIN
TROWARGMAX TROWARGMIN TCOLSUM TCOLPROD TCOLMAX TCOLMIN TCOLARGMAX TCOLARGMIN
TROWEXPAND TROWEXPANDADD TROWEXPANDSUB TROWEXPANDMUL TROWEXPANDDIV TROWEXPANDMAX
TROWEXPANDMIN TROWEXPANDEXPDIF TCOLEXPAND TCOLEXPANDADD TCOLEXPANDSUB TCOLEXPANDMUL
TCOLEXPANDDIV TCOLEXPANDMAX TCOLEXPANDMIN TCOLEXPANDEXPDIF TMATMUL TMATMUL_BIAS
TMATMUL_ACC TMATMUL_MX TGEMV TGEMV_BIAS TGEMV_ACC TGEMV_MX TLOAD TSTORE TPREFETCH
MGATHER MSCATTER TEXPANDS TCI TTRI TFILLPAD TCVT TQUANT TDEQUANT TEXTRACT TINSERT
TGATHER TSCATTER TCONCAT TTRANS TIMG2COL TMOV TGATHERB TDEINTERLEAVE TINTERLEAVE
TRESHAPE TSORT TMRGSORT THISTOGRAM TPARTADD TPARTMUL TPARTMAX TPARTMIN TPARTARGMAX
TPARTARGMIN TPUSH TPOP TALLOC TFREE
""".split()

EXPECTED_TMA = {
    "TLOAD": ("BSTART.TLOAD", 0),
    "TSTORE": ("BSTART.TSTORE", 1),
    "TMOV": ("BSTART.TMOV", 2),
    "TPREFETCH": ("BSTART.TPREFETCH", 3),
    "MGATHER": ("BSTART.MGATHER", 4),
    "MSCATTER": ("BSTART.MSCATTER", 5),
}
EXPECTED_CUBE = {
    "TMATMUL": ("BSTART.TMATMUL", 0),
    "TMATMUL_BIAS": ("BSTART.TMATMUL.BIAS", 1),
    "TMATMUL_ACC": ("BSTART.TMATMUL.ACC", 2),
    "TMATMUL_MX": ("BSTART.TMATMULMX", 4),
    "TGEMV": ("BSTART.TGEMV", 16),
    "TGEMV_BIAS": ("BSTART.TGEMV.BIAS", 17),
    "TGEMV_ACC": ("BSTART.TGEMV.ACC", 18),
    "TGEMV_MX": ("BSTART.TGEMVMX", 20),
}
EXPECTED_SUPPLEMENTAL = {
    ("BSTART.MGATHER.MASK", "TMA", 6),
    ("BSTART.MSCATTER.MASK", "TMA", 7),
    ("BSTART.MGATHER.CAS", "TMA", 8),
}
REJECTED_NAMES = {
    "TEXRACT",
    "TFILL/TEXPANDS",
    "TFMOD",
    "TFMODS",
    "TLRELU？",
    "TPOW",
    "TPOWS",
    "TPRELU？",
    "TRANDOM",
}


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    ops_path = root / "isa/v0.57/state/pto_ops.json"
    map_path = root / "isa/v0.57/state/pto_encoding_map.json"
    engine_path = root / "isa/v0.57/state/engine_ops.json"
    for path in (ops_path, map_path, engine_path):
        if not path.is_file():
            errors.append(f"missing required v0.57 PTO state file: {path}")
    if errors:
        return errors

    inventory = _load(ops_path)
    encoding_map = _load(map_path)
    engine = _load(engine_path)
    for label, document in (("inventory", inventory), ("encoding map", encoding_map)):
        if document.get("profile") != "v0.57":
            errors.append(f"{label}: profile must be v0.57")
        if document.get("version") != "0.57.0":
            errors.append(f"{label}: version must be 0.57.0")
        source = document.get("source", {})
        if source.get("original_sha256") != SOURCE_SHA256:
            errors.append(f"{label}: original workbook SHA-256 mismatch")
        if source.get("review_export_sha256") != EXPORT_SHA256:
            errors.append(f"{label}: review export SHA-256 mismatch")

    operations = inventory.get("operations")
    entries = encoding_map.get("entries")
    if not isinstance(operations, list) or not isinstance(entries, list):
        return errors + ["PTO operations and encoding entries must be lists"]
    names = [str(operation.get("name") or "") for operation in operations]
    if names != EXPECTED_NAMES:
        errors.append("PTO inventory names/order do not match the frozen 111-row workbook")
    if len(names) != len(set(names)):
        errors.append("PTO inventory contains duplicate names")
    if [operation.get("source_row") for operation in operations] != list(range(2, 113)):
        errors.append("PTO inventory source rows must be exactly 2..112")
    if inventory.get("operation_count") != 111 or encoding_map.get("entry_count") != 111:
        errors.append("PTO inventory and encoding map must each contain 111 workbook rows")

    by_name = {operation["name"]: operation for operation in operations}
    map_by_name = {entry["pto_name"]: entry for entry in entries}
    if set(map_by_name) != set(by_name) or len(map_by_name) != len(entries):
        errors.append("PTO encoding map must contain each inventory operation exactly once")

    tepl_by_name = {
        str(operation["name"]): int(operation["tile_opcode"])
        for operation in engine.get("tepl", {}).get("ops", [])
    }
    tma_state = {
        (entry["mnemonic"], int(entry["function"]))
        for entry in engine.get("tma", {}).get("legal_aliases", [])
    }
    cube_state = {
        (entry["mnemonic"], int(entry["function"]))
        for entry in engine.get("cube", {}).get("legal_aliases", [])
    }
    seen_tepl: dict[int, str] = {}
    family_counts = {"TEPL": 0, "TMA": 0, "CUBE": 0}
    for name in names:
        operation = by_name[name]
        entry = map_by_name.get(name, {})
        disposition = operation.get("disposition", {})
        family = disposition.get("family")
        if family not in family_counts:
            errors.append(f"{name}: invalid disposition family {family!r}")
            continue
        family_counts[family] += 1
        if entry.get("canonical_name") != operation.get("canonical_name"):
            errors.append(f"{name}: encoding map disagrees with canonical_name")
        for key in ("canonical_name", "family", "encoding_mnemonic", "selector", "function"):
            if key in disposition and entry.get(key) != disposition.get(key):
                errors.append(f"{name}: encoding map disagrees with inventory field {key}")

        if name in EXPECTED_TMA:
            mnemonic, function = EXPECTED_TMA[name]
            if disposition != {
                "family": "TMA",
                "function": function,
                "encoding_mnemonic": mnemonic,
            }:
                errors.append(f"{name}: incorrect TMA disposition")
            if (mnemonic, function) not in tma_state:
                errors.append(f"{name}: TMA disposition missing from engine state")
        elif name in EXPECTED_CUBE:
            mnemonic, function = EXPECTED_CUBE[name]
            if disposition != {
                "family": "CUBE",
                "function": function,
                "encoding_mnemonic": mnemonic,
            }:
                errors.append(f"{name}: incorrect CUBE disposition")
            if (mnemonic, function) not in cube_state:
                errors.append(f"{name}: CUBE disposition missing from engine state")
        else:
            canonical = "TTRANSPOSE" if name == "TTRANS" else name
            selector = tepl_by_name.get(canonical)
            rendered = None if selector is None else f"0x{selector:03X}"
            if disposition != {
                "family": "TEPL",
                "selector": rendered,
                "encoding_mnemonic": "BSTART.TEPL",
            }:
                errors.append(f"{name}: incorrect TEPL disposition")
            if selector is not None:
                previous = seen_tepl.get(selector)
                if previous is not None and previous != canonical:
                    errors.append(
                        f"TEPL selector 0x{selector:03X} is shared by {previous} and {canonical}"
                    )
                seen_tepl[selector] = canonical

    expected_counts = {"TEPL": 97, "TMA": 6, "CUBE": 8}
    if family_counts != expected_counts:
        errors.append(f"PTO family counts mismatch: {family_counts}")
    if inventory.get("family_counts") != expected_counts:
        errors.append("PTO inventory family_counts field is stale")
    if encoding_map.get("family_counts") != expected_counts:
        errors.append("PTO encoding map family_counts field is stale")

    supplemental = {
        (
            entry.get("canonical_name"),
            entry.get("family"),
            entry.get("function"),
        )
        for entry in encoding_map.get("supplemental_entries", [])
    }
    if supplemental != EXPECTED_SUPPLEMENTAL:
        errors.append("supplemental PR #123/#133 TMA mappings are incomplete")

    all_names = set(names) | {
        str(entry.get("canonical_name") or "") for entry in entries
    }
    leaked = sorted(REJECTED_NAMES & all_names)
    if leaked:
        errors.append(f"review-only or typo PTO names leaked into v0.57: {leaked}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
