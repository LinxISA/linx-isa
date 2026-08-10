#!/usr/bin/env python3
"""Small dependency-free contract test for the LinxISA 0.58 profile."""

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8"))
assert spec["version"] == "0.58.0"
assert sum("pto_source_form_id" in item for item in spec["instructions"]) == 573
pto_owned_instructions = [
    item
    for item in spec["instructions"]
    if item.get("pto_source_form_id") or item.get("pto_source_form_variant_of")
]
linx_only_instructions = [
    item
    for item in spec["instructions"]
    if not (item.get("pto_source_form_id") or item.get("pto_source_form_variant_of"))
]
assert len(pto_owned_instructions) == 578
assert len(linx_only_instructions) == 188
assert sum(item["mnemonic"].startswith("V.") for item in linx_only_instructions) == 184
assert {
    item["mnemonic"]
    for item in linx_only_instructions
    if not item["mnemonic"].startswith("V.")
} == {"BSTART.VPAR", "BSTART.VSEQ", "C.BSTART.VPAR", "C.BSTART.VSEQ"}
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
expected_family_counts = {"CUBE": 12, "TEPL": 87, "TLSU": 10}
expected_engine_counts = {"CUBE": 12, "SFU": 52, "TLSU": 10, "VEC": 35}
expected_classification_counts = {
    "elementwise-tile-tile": 25,
    "irregular-and-complex": 13,
    "layout-and-rearrangement": 7,
    "matrix-and-matrix-vector": 12,
    "memory-and-data-movement": 9,
    "reduce-and-expand": 28,
    "tile-scalar-and-immediate": 15,
}
assert pto_ops["family_counts"] == expected_family_counts
assert pto_ops["engine_counts"] == expected_engine_counts
assert pto_ops["classification_counts"] == expected_classification_counts
assert Counter(item["engine"] for item in pto_ops["operations"]) == Counter(expected_engine_counts)
assert Counter(item["classification"] for item in pto_ops["operations"]) == Counter(
    expected_classification_counts
)
assert all(
    item["engine"] in {"VEC", "SFU"}
    for item in pto_ops["operations"]
    if item["family"] == "TEPL"
)
assert all(
    item["engine"] == item["family"]
    for item in pto_ops["operations"]
    if item["family"] in {"TLSU", "CUBE"}
)
encoding_map = json.loads(
    (ROOT / "isa/v0.58/state/pto_encoding_map.json").read_text(encoding="utf-8")
)
assert encoding_map["family_counts"] == expected_family_counts
assert encoding_map["engine_counts"] == expected_engine_counts
assert encoding_map["classification_counts"] == expected_classification_counts
projected_classification = {
    item["name"]: (item["family"], item["classification"], item["engine"])
    for item in encoding_map["entries"]
}
assert projected_classification == {
    item["name"]: (item["family"], item["classification"], item["engine"])
    for item in pto_ops["operations"]
}
engine_ops = json.loads((ROOT / "isa/v0.58/state/engine_ops.json").read_text(encoding="utf-8"))
assert engine_ops["semantic_engine_counts"] == expected_engine_counts
legacy_scheduler_fields = {
    "dim_lb_defaults",
    "dim_lb_required",
    "dim_required",
    "dirty_rule",
    "dst_tiles",
    "engineop_state_bytes_max",
    "engineop_state_version",
    "has_index_tile",
    "phase_model",
    "redo_ok_after_start",
    "resume_ok",
    "src_tiles",
}
for item in engine_ops["tepl"]["ops"]:
    assert item["engine"] in {"VEC", "SFU"}
    assert item["classification"] in expected_classification_counts
    assert legacy_scheduler_fields.isdisjoint(item)
for family in ("tlsu", "cube"):
    expected_engine = family.upper()
    for item in engine_ops[family]["legal_aliases"]:
        assert item["engine"] == expected_engine
        assert item["classification"] in expected_classification_counts
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
sail_state = (ROOT / "isa/sail/model/state/state.sail").read_text(encoding="utf-8")
assert "tile_tlsu_required_sources" in sail_execute
assert "tile_tlsu_produces_output" in sail_execute
assert "tile_tma_" not in sail_execute
assert "PTO ISA 0.57" not in sail_execute
assert "PTO ISA 0.57" not in sail_state
assert "exec_bstart_acccvt" not in sail_execute
publish_body = sail_execute[
    sail_execute.index("function tile_effect_publish") : sail_execute.index("function tile_effect_finalize")
]
assert "selector == 0b01000" not in publish_body
assert "ACCCVT" not in sail_execute
assert "ACCCVT" not in sail_state
src0_alloc = sail_execute.index("allocate_ri_binding(src0)")
src1_alloc = sail_execute.index("allocate_ri_binding(src1)")
src2_alloc = sail_execute.index("allocate_ri_binding(src2)")
assert src0_alloc < src1_alloc < src2_alloc

bstart_tepl = [item for item in spec["instructions"] if item["mnemonic"] == "BSTART.TEPL"]
assert len(bstart_tepl) == 1
assert bstart_tepl[0]["accepted_assembly_mnemonics"] == [
    "BSTART.TEPL",
    "BSTART.VEC",
    "BSTART.SFU",
]
assert bstart_tepl[0]["canonical_assembly_by_engine"] == {
    "SFU": "BSTART.SFU",
    "VEC": "BSTART.VEC",
}
assert bstart_tepl[0]["carrier_mnemonic"] == "BSTART.TEPL"
assert {"BSTART.VEC", "BSTART.SFU"}.isdisjoint(mnemonics)
assembly_contract_pages = "\n".join(
    (ROOT / relative).read_text(encoding="utf-8")
    for relative in (
        "docs/isa/arch/branch.md",
        "docs/zh/isa/arch/branch.md",
        "docs/compiler/assembly_manual/bstop.md",
        "docs/zh/compiler/assembly_manual/bstop.md",
        "docs/architecture/isa-manual/src/chapters/04_block_isa.adoc",
    )
)
assert not re.search(
    r"BSTART\.(?:TEPL|VEC|SFU)\s+(?:FALL|DIRECT|COND|CALL)\b",
    assembly_contract_pages,
    re.IGNORECASE,
)
assert not re.search(r"BSTART\.(?:VEC|SFU)\s+Mode\b", assembly_contract_pages)
tepl_page = (ROOT / "docs/isa/instructions/bstart_tepl.md").read_text(encoding="utf-8")
tepl_fragment = (
    ROOT / "docs/architecture/isa-manual/src/generated/instructions/bstart_tepl.adoc"
).read_text(encoding="utf-8")
for syntax in (
    "BSTART.VEC TileOp, DataType",
    "BSTART.SFU TileOp, DataType",
    "BSTART.TEPL Mode, Function, DataType",
):
    assert syntax in tepl_page
    assert syntax in tepl_fragment


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
