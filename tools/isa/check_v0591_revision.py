#!/usr/bin/env python3
"""Check the v0.59.1-only ISA delta against the original signed publication."""

from collections import Counter
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "d262515b55c727073997c8f4c95261909f2fe8d3"
PROFILE = "isa/v0.59"
CATALOG = f"{PROFILE}/linxisa-v0.59.json"
BLOCKS = {
    "B.TEXT",
    *(p + "BSTART." + k for p in ("", "C.") for k in ("MPAR", "MSEQ", "VPAR", "VSEQ")),
}
ENCODING_ONLY = {"DMA.FREE.L", "DMA.FREE.S", "MCOPY.DL", "MCOPY.DS"}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def bits(parts):
    width = mask = match = 0
    for p in parts:
        mask |= int(p["mask"], 16) << width
        match |= int(p["match"], 16) << width
        width += p["width_bits"]
    return width, mask, match


def verify():
    for path in ("isa/v0.57", "isa/v0.58", "isa/sail", "isa/generated"):
        if subprocess.run(
            ["git", "diff", "--quiet", BASELINE, "--", path], cwd=ROOT
        ).returncode:
            raise ValueError(
                f"prior profile or shared platform artifact differs: {path}"
            )
        if git("ls-files", "--others", "--exclude-standard", "--", path):
            raise ValueError(f"undeclared file in protected profile: {path}")
    source = json.loads(git("show", f"{BASELINE}:{CATALOG}"))
    current = json.loads((ROOT / CATALOG).read_bytes())
    if current["version"] != "0.59.1":
        raise ValueError("incorrect specification version")
    old = {r["id"]: r for r in source["instructions"]}
    retained = {
        k: v
        for k, v in old.items()
        if not v["mnemonic"].startswith("V.") and v["mnemonic"] not in BLOCKS
    }
    now = {r["id"]: r for r in current["instructions"]}
    if (len(old), len(retained), len(now), len(current["instructions"])) != (
        1499,
        1306,
        1306,
        1306,
    ) or retained != now:
        raise ValueError("retained IDs, encodings, operand fields or semantics differ")
    extensions = [x for x in now.values() if not x.get("pto_source_form_id")]
    if (
        len(extensions) != 23
        or sum(r["mnemonic"] in ENCODING_ONLY for r in extensions) != 4
    ):
        raise ValueError("extended block headers and reserved-only inventory differ")
    for basename in (
        "pto_scalar_forms",
        "pto_command_forms",
        "pto_tile_operations",
        "pto_system_registers",
        "extension_encoding_reservations",
        "pto_hardware_conformance_profile",
        "pto_hardware_numeric_vectors",
    ):
        path = f"{PROFILE}/state/{basename}.json"
        if (ROOT / path).read_bytes() != git("show", f"{BASELINE}:{path}"):
            raise ValueError(f"shared PTO input differs: {path}")
    reserves = json.loads(
        (ROOT / PROFILE / "state/extension_encoding_reservations.json").read_bytes()
    )["reservations"]
    ranges = {
        r["mnemonic"]: bits(r["encoding"])
        for r in reserves
        if r["mnemonic"] in BLOCKS | {"V.*"} and r["status"] == "reserved-in-pto"
    }
    if ranges.keys() != BLOCKS | {"V.*"}:
        raise ValueError("missing PTO encoding reservations")
    used = Counter()
    for key, row in old.items():
        width, mask, match = bits(row["encoding"]["parts"])
        for name, (rw, rm, rv) in ranges.items():
            if width != rw or (match ^ rv) & mask & rm:
                continue
            if key in now or mask & rm != rm:
                raise ValueError(f"{key}: invalid overlap with reserved range {name}")
            used[name] += 1
    if used != {"V.*": 184, **dict.fromkeys(BLOCKS, 1)}:
        raise ValueError(f"deleted forms and reservation ranges disagree: {used}")
    print(
        "OK: only v0.59.1 changes; 193 forms removed; ten full encoding ranges reserved; 1306 unchanged surviving rows."
    )


if __name__ == "__main__":
    verify()
