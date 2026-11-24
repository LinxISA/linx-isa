#!/usr/bin/env python3
"""Build the LinxISA 0.59.2 catalog from the signed 0.59.1 catalog."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "isa/v0.59/linxisa-v0.59.json"
RESERVATIONS = ROOT / "isa/v0.59/state/extension_encoding_reservations.json"
OUTPUT = ROOT / "isa/v0.59.2/linxisa-v0.59.2.json"
BASELINE_SHA256 = "490defb827d2aecd5c63fe231467d2a3416e5ce0361b65a65f507d9fab08079c"

OBSOLETE_BLOCKS = {
    "BSTART.MPAR",
    "BSTART.MSEQ",
    "C.BSTART.MPAR",
    "C.BSTART.MSEQ",
    "BSTART.VPAR",
    "BSTART.VSEQ",
    "C.BSTART.VPAR",
    "C.BSTART.VSEQ",
    "B.TEXT",
}
ENCODING_ONLY = {"DMA.FREE.L", "DMA.FREE.S", "MCOPY.DL", "MCOPY.DS"}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def render(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def _encoded_part_matches_reservation(
    part: dict[str, Any], reserved: dict[str, Any]
) -> bool:
    mask = int(reserved["mask"], 16)
    return (
        int(part["width_bits"]) == int(reserved["width_bits"])
        and int(part["mask"], 16) & mask == mask
        and int(part["match"], 16) & mask == int(reserved["match"], 16)
    )


def _status(mnemonic: str) -> tuple[str, str]:
    if mnemonic.startswith("V.") or mnemonic in OBSOLETE_BLOCKS:
        return "obsolete", "reserved-in-pto"
    if mnemonic in ENCODING_ONLY:
        return "reserved-unimplemented", "reserved-in-pto"
    return "retained", "reserved-in-pto"


def build() -> dict[str, Any]:
    if hashlib.sha256(BASELINE.read_bytes()).hexdigest() != BASELINE_SHA256:
        raise ValueError("0.59.1 baseline differs from the signed release catalog")
    document = copy.deepcopy(load(BASELINE))
    if document.get("version") != "0.59.1" or document.get("instruction_count") != 1499:
        raise ValueError("0.59.2 requires the published 0.59.1 catalog baseline")

    reservations = load(RESERVATIONS)["reservations"]
    counts = {"obsolete": 0, "retained": 0, "reserved-unimplemented": 0}
    reservation_names: set[str] = set()
    for item in document["instructions"]:
        if item.get("pto_source_form_id"):
            continue
        state, ownership = _status(str(item["mnemonic"]))
        item["architecture_status"] = {
            "state": state,
            "encoding_ownership": ownership,
        }
        if state == "obsolete":
            item["architecture_status"]["since"] = "0.59.2"
            item["architecture_status"]["replacement"] = None
        elif state == "reserved-unimplemented":
            item["architecture_status"]["execution"] = (
                "reject-before-operand-read-or-architectural-effect"
            )
        counts[state] += 1

        encoded_parts = item["encoding"]["parts"]
        matches = [
            reservation
            for reservation in reservations
            if reservation.get("status") == "reserved-in-pto"
            and len(encoded_parts) == len(reservation["encoding"])
            and all(
                _encoded_part_matches_reservation(actual, expected)
                for actual, expected in zip(
                    encoded_parts, reservation["encoding"], strict=True
                )
            )
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{item['id']}: expected one PTO reservation, found {len(matches)}"
            )
        reservation_name = matches[0]["mnemonic"]
        reservation_names.add(reservation_name)

    if counts != {
        "obsolete": 193,
        "retained": 19,
        "reserved-unimplemented": 4,
    }:
        raise ValueError(f"unexpected Linx-only status counts: {counts}")
    obsolete_reservations = {
        "V.*",
        *OBSOLETE_BLOCKS,
    }
    if (
        not obsolete_reservations <= reservation_names
        or len(obsolete_reservations) != 10
    ):
        raise ValueError("193 obsolete forms are not covered by ten PTO reservations")

    document["version"] = "0.59.2"
    document["release_status"] = {
        **document["release_status"],
        "state": "published-specification-catalog",
        "source_catalog": "isa/v0.59/linxisa-v0.59.json",
        "source_version": "0.59.1",
        "architecture_status_schema": "linxisa.instruction-status.v1",
        "linx_only_status_counts": counts,
        "obsolete_encoding_reservations": sorted(obsolete_reservations),
        "decision": "docs/architecture/linx-two-level-block-obsolescence.md",
    }
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"stale LinxISA 0.59.2 catalog: {OUTPUT}")
        print(f"LinxISA 0.59.2 catalog is current: {OUTPUT}")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
