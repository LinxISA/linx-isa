#!/usr/bin/env python3
"""Build a source-backed review candidate for active v0.58.3 QEMU evidence."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import refresh_qemu_executable_coverage as refresh
import report_qemu_executable_coverage as reporter


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "avs/qemu/qemu_executable_coverage_v0583_candidate.json"
ARCHIVE = ROOT / "avs/qemu/qemu_executable_coverage_manifest.json"
ADDITIONAL = (
    ROOT / "avs/qemu/qemu_executable_setc_imm_manifest.json",
    ROOT / "avs/qemu/qemu_executable_maddw_bfi_mi_manifest.json",
)
SPEC = ROOT / "isa/v0.58/linxisa-v0.58.json"

STATIC_KEYS = (
    "form_id",
    "mnemonic",
    "form_key",
    "suite",
    "suite_completion_test_id",
    "test_id",
    "reachability",
    "oracle",
    "max_level",
    "test_contract",
    "failure_attribution",
)

TILE_ROWS = (
    {
        "form_id": "bstart_tload_32_5178a1794614",
        "suite": "tile_v0583_tlsu",
        "test_id": "0x00002a01",
        "symbol": "linx_v0583_tlsu_copy",
        "source": "avs/qemu/tests/28_v0583_tile_tlsu.c",
        "test_symbol": "run_tile_v0583_tlsu_tests",
        "object": "28_v0583_tile_tlsu_carrier.o",
        "oracle": {
            "kind": "differential",
            "expected": "(uint32_t)input[i]",
        },
    },
    {
        "form_id": "b_iot_32_ba693fbfdca5",
        "suite": "tile_v0583_vec",
        "test_id": "0x00002b01",
        "symbol": "linx_v0583_vec_add",
        "source": "avs/qemu/tests/29_v0583_tile_vec.c",
        "test_symbol": "run_tile_v0583_vec_tests",
        "object": "29_v0583_tile_vec_carrier.o",
        "oracle": {"kind": "exact_value", "expected": "0x40400000"},
    },
    {
        "form_id": "b_iot_32_2f60297debcb",
        "suite": "tile_v0583_sfu",
        "test_id": "0x00002c01",
        "symbol": "linx_v0583_sfu_exp",
        "source": "avs/qemu/tests/30_v0583_tile_sfu.c",
        "test_symbol": "run_tile_v0583_sfu_tests",
        "object": "30_v0583_tile_sfu_carrier.o",
        "oracle": {"kind": "exact_value", "expected": "0x3f800000"},
    },
    {
        "form_id": "bstart_tmatmul_32_3bb582723869",
        "suite": "tile_v0583_cube",
        "test_id": "0x00002d01",
        "symbol": "linx_v0583_cube_matmul",
        "source": "avs/qemu/tests/31_v0583_tile_cube.c",
        "test_symbol": "run_tile_v0583_cube_tests",
        "object": "31_v0583_tile_cube_carrier.o",
        "oracle": {
            "kind": "differential",
            "expected": "(uint32_t)rhs[i]",
        },
    },
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def static_entry(entry: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in STATIC_KEYS if key not in entry]
    if missing:
        raise ValueError(f"{entry.get('form_id')}: missing static fields {missing}")
    result = {key: copy.deepcopy(entry[key]) for key in STATIC_KEYS}
    symbol = entry.get("instruction", {}).get("symbol")
    if not isinstance(symbol, str) or not symbol:
        raise ValueError(f"{entry.get('form_id')}: missing instruction symbol")
    result.update(
        {
            "elf": f"template/{entry['suite']}/linx-qemu-tests.elf",
            "object": (
                f"template/{entry['suite']}/obj/"
                f"{Path(str(entry['object'])).name}"
            ),
            "instruction": {"symbol": symbol, "pc": "0x0", "occurrence": 0},
        }
    )
    return result


def tile_entry(row: dict[str, Any], forms: dict[str, dict[str, Any]]) -> dict[str, Any]:
    form = forms[row["form_id"]]
    source = row["source"]
    symbol = row["symbol"]
    return {
        "form_id": row["form_id"],
        "mnemonic": form["mnemonic"],
        "form_key": {
            "length_bits": form["length_bits"],
            "mask": f"0x{form['mask']:0{(form['length_bits'] + 3) // 4}x}",
            "match": f"0x{form['match']:0{(form['length_bits'] + 3) // 4}x}",
        },
        "suite": row["suite"],
        "suite_completion_test_id": row["test_id"],
        "test_id": row["test_id"],
        "elf": f"template/{row['suite']}/linx-qemu-tests.elf",
        "object": f"template/{row['suite']}/obj/{row['object']}",
        "instruction": {"symbol": symbol, "pc": "0x0", "occurrence": 0},
        "reachability": {
            "source": source,
            "test_symbol": row["test_symbol"],
            "target_symbol": symbol,
        },
        "oracle": {
            **row["oracle"],
            "source": source,
            "locator": row["test_symbol"],
        },
        "max_level": "L3",
        "test_contract": "valid",
        "failure_attribution": "none",
    }


def validate_source_mapping(entry: dict[str, Any]) -> None:
    reachability = entry["reachability"]
    source_path = ROOT / reachability["source"]
    source = source_path.read_text(encoding="utf-8")
    body = reporter._function_body(source, reachability["test_symbol"])
    if body is None or reachability["target_symbol"] not in body:
        raise ValueError(f"{entry['form_id']}: target is not source-reachable")
    oracle = entry["oracle"]
    oracle_source = (ROOT / oracle["source"]).read_text(encoding="utf-8")
    oracle_body = reporter._function_body(oracle_source, oracle["locator"])
    if oracle_body is None:
        raise ValueError(f"{entry['form_id']}: oracle locator is absent")
    test_id = int(str(entry["test_id"]), 0)
    if oracle["kind"] == "differential":
        bound = reporter._differential_assertion_binds(
            oracle_body, oracle_source, oracle["expected"], test_id
        )
    else:
        bound = reporter._assertion_binds(
            oracle_body, oracle_source, int(str(oracle["expected"]), 0), test_id
        )
    if not bound:
        raise ValueError(f"{entry['form_id']}: oracle is not source-bound")


def build() -> dict[str, Any]:
    spec = load(SPEC)
    forms = reporter._spec_forms(spec)
    archive = load(ARCHIVE)
    if archive.get("active_release") is not False:
        raise ValueError("historical source manifest must remain archival")
    evidence = [
        static_entry(entry)
        for entry in archive["evidence"]
        if entry.get("suite") in refresh.SUITE_ORDER
    ]
    for path in ADDITIONAL:
        evidence.extend(static_entry(entry) for entry in load(path)["evidence"])
    evidence.extend(tile_entry(row, forms) for row in TILE_ROWS)
    candidate = {
        "schema_version": 4,
        "release": refresh.ACTIVE_RELEASE,
        "active_release": True,
        "template_status": "review-candidate-source-backed",
        "availability": {"L2": "available", "L3": "available"},
        "evidence": evidence,
        "producer": {
            "builder": "tools/bringup/build_qemu_executable_coverage_v0583_candidate.py",
            "policy": (
                "Static mappings only. Dynamic QEMU, binary and run evidence "
                "must be produced by refresh_qemu_executable_coverage.py."
            ),
        },
    }
    rebinds = refresh._rebind_manifest_forms(candidate, spec)
    candidate["producer"]["identity_rebinds"] = rebinds
    grouped = refresh._suite_entries(candidate)
    if set(grouped) != set(refresh.SUITE_ORDER):
        raise ValueError("candidate does not cover every refresh suite")
    for entry in candidate["evidence"]:
        validate_source_mapping(entry)
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"v0.58.3 executable template build failed: {error}") from error
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale v0.58.3 executable template: {OUTPUT}")
        print("v0.58.3 executable coverage candidate is current")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
