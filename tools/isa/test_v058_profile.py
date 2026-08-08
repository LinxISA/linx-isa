#!/usr/bin/env python3
"""Small dependency-free contract test for the LinxISA 0.58 profile."""

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parents[2]
spec = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8"))
assert spec["version"] == "0.58.0"
assert sum("pto_source_form_id" in item for item in spec["instructions"]) == 573
mnemonics = {item["mnemonic"] for item in spec["instructions"]}
assert {"B.IOS", "BSTART.GMOV", "BSTART.VPAR", "BSTART.VSEQ", "V.QPOP", "V.QPUSH"} <= mnemonics
assert {"B.IOD", "BSTART.PAR", "C.B.IOS"}.isdisjoint(mnemonics)
b_ios = [item for item in spec["instructions"] if item["mnemonic"] == "B.IOS"]
assert len(b_ios) == 1
b_ios_part = b_ios[0]["encoding"]["parts"][0]
assert (int(b_ios_part["mask"], 0), int(b_ios_part["match"], 0)) == (
    0xF00871FF,
    0x00001013,
)
assert spec["retired_encodings"]["entries"] == []
pto_ops = json.loads((ROOT / "isa/v0.58/state/pto_ops.json").read_text(encoding="utf-8"))
tfma = [item for item in pto_ops["operations"] if item["name"] == "TFMA"]
assert len(tfma) == 1
assert (tfma[0]["mode"], tfma[0]["function"], tfma[0]["selector"]) == (0, 28, "0x01C")
shared = json.loads((ROOT / "isa/v0.58/state/shared_tile_registers.json").read_text(encoding="utf-8"))
assert shared["register_count"] == 256
assert shared["register_names"]["first"] == "S0"
assert shared["register_names"]["last"] == "S255"
assert shared["tsize_bytes"] == [None, 128, 256, 512, 1024, 2048, 4096, 8192]
assert shared["pe_mask"]["owner"] == "B.IOS"
assert shared["gm_access"]["base_selector"] == "B.IOR.RegSrc0"
assert shared["gm_access"]["row_stride_selector"] == "B.IOR.RegSrc1"
b_ios_page = (ROOT / "docs/isa/instructions/b_ios.md").read_text(encoding="utf-8")
b_ior_page = (ROOT / "docs/isa/instructions/b_ior.md").read_text(encoding="utf-8")
assert "## Description\n\nBinds one ordered absolute core-private Shared register" in b_ios_page
assert "## Description\n\nBind up to three absolute GPR inputs" in b_ior_page
dma = next(item for item in spec["instructions"] if item["mnemonic"] == "DMA")
assert "64-byte" in dma["note"]
assert "overlap has memmove semantics" in dma["note"]
assert "64-bit" not in dma["note"]
for mnemonic in ("BSTART CALL", "HL.BSTART CALL"):
    call = next(item for item in spec["instructions"] if item["mnemonic"] == mnemonic)
    assert "independent unsigned displacement" in call["note"]
    assert "writes ra" in call["note"]
sail_execute = (ROOT / "isa/sail/model/execute/execute.sail").read_text(encoding="utf-8")
src0_alloc = sail_execute.index("allocate_ri_binding(src0)")
src1_alloc = sail_execute.index("allocate_ri_binding(src1)")
src2_alloc = sail_execute.index("allocate_ri_binding(src2)")
assert src0_alloc < src1_alloc < src2_alloc


def instruction_slug(mnemonic: str) -> str:
    slug = re.sub(r"\.+", "_", mnemonic.strip().lower())
    slug = re.sub(r"[^a-z0-9_]+", "_", slug)
    return re.sub(r"_+", "_", slug).strip("_") or "x"


common_mnemonics: set[str] = set()
for item in spec["instructions"]:
    if "pto_source_form_id" not in item:
        continue
    note = " ".join(str(item.get("note") or "").split())
    assert note
    common_mnemonics.add(item["mnemonic"])
for mnemonic in common_mnemonics:
    page = (ROOT / "docs/isa/instructions" / f"{instruction_slug(mnemonic)}.md").read_text(encoding="utf-8")
    description = page.split("## Description\n\n", 1)[1].split("\n\n## Pseudocode", 1)[0].strip()
    assert description
    assert "Instruction from the " not in description, mnemonic
print("OK")
