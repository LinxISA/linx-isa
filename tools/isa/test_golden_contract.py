#!/usr/bin/env python3
"""Focused regression checks for the standalone v0.57 ISA contract."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_validate_spec():
    path = ROOT / "tools/isa/validate_spec.py"
    spec = importlib.util.spec_from_file_location("validate_spec", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _assert_rejected(base_spec: dict, mutate) -> None:
    candidate = copy.deepcopy(base_spec)
    mutate(candidate["semantics_conventions"]["frame_templates_r975"])
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "candidate.json"
        path.write_text(json.dumps(candidate, sort_keys=True), encoding="utf-8")
        errors = _load_validate_spec().validate(str(path))
    assert errors, "mutated frame_templates_r975 contract was accepted"


def _delete(mapping: dict, key: str) -> None:
    del mapping[key]


def _weaken(mapping: dict, key: str) -> None:
    value = mapping[key]
    if isinstance(value, str):
        mapping[key] = value + "; after lookup, status and AckID may coalesce"
    elif isinstance(value, list):
        del value[-1]
    elif isinstance(value, dict):
        first_key = next(iter(value))
        del value[first_key]
    elif isinstance(value, bool):
        mapping[key] = not value
    else:
        raise AssertionError(f"unsupported mutation target {key}: {value!r}")


def _mutate_identity_array(frame: dict, path: tuple[str, ...], index: int = 0) -> None:
    target = frame
    for key in path[:-1]:
        target = target[key]
    values = target[path[-1]]
    values[index] = f"{values[index]}_weakened"


def main() -> int:
    spec = json.loads((ROOT / "isa/v0.57/linxisa-v0.57.json").read_text(encoding="utf-8"))
    instructions = spec["instructions"]
    mnemonics = {str(inst["mnemonic"]) for inst in instructions}
    assert spec["version"] == "0.57.1"
    assert "B.IOD" not in mnemonics
    assert "BSTART.PAR" not in mnemonics
    assert {
        "B.IOR",
        "B.IOT",
        "BSTART.TEPL",
        "B.CATR",
        "B.DATR",
        "L.BSTART.FP",
        "L.BSTART.STD",
        "L.BSTART.SYS",
    } <= mnemonics

    long_bstarts = [inst for inst in instructions if str(inst["mnemonic"]).startswith("L.BSTART.")]
    assert len(long_bstarts) == 9
    assert {inst["length_bits"] for inst in long_bstarts} == {64}
    assert {inst["asm"].split()[1] for inst in long_bstarts} >= {"FALL<,", "DIRECT,", "COND,", "CALL,"}

    retired = {entry["retired_mnemonic"]: entry for entry in spec["retired_encodings"]["entries"]}
    assert retired["B.IOD"]["disposition"] == "reserved"
    assert retired["BSTART.PAR"]["disposition"] == "reserved"
    assert "replacement_mnemonic" not in retired["BSTART.PAR"]

    exact_calls = [
        inst
        for inst in instructions
        if inst["mnemonic"] in {"BSTART CALL", "HL.BSTART CALL"}
    ]
    assert len(exact_calls) == 2
    for call in exact_calls:
        note = str(call.get("note") or "")
        assert "Atomic fused CALL" in note
        assert "independently relocatable" in note
        assert [role["role"] for role in call["operand_roles"]] == [
            "call_target",
            "return_target",
            "link_destination",
        ]
        assert call["semantic_contract"]["atomic"] is True

    generic_long_calls = [
        inst
        for inst in instructions
        if str(inst["mnemonic"]).startswith("L.BSTART.") and " CALL," in inst["asm"]
    ]
    assert len(generic_long_calls) == 2
    for call in generic_long_calls:
        note = str(call.get("note") or "")
        assert "preserves ra" in note
        assert "SETRET or C.SETRET" in note

    form_ids = [str(inst["id"]) for inst in instructions]
    assert len(form_ids) == len(set(form_ids)) == int(spec["instruction_count"])
    assert all(inst.get("uop_big_kind") and inst.get("uop_class") for inst in instructions)
    assert spec["field_definitions"]["fields"]
    assert spec["semantics_conventions"]

    field_source = json.loads(
        (ROOT / "isa/v0.57/encoding/fields.json").read_text(encoding="utf-8")
    )
    assert spec["field_definitions"] == field_source
    for name, definition in field_source["fields"].items():
        assert definition["widths"] == sorted(set(definition["widths"])), name
        if definition["namespace"] == "immediate":
            assert isinstance(definition["signed"], bool), name
            assert isinstance(definition["scale"], int) and definition["scale"] > 0, name
        if definition["namespace"] == "selector":
            assert isinstance(definition["reserved_values"], list), name
    assert field_source["fields"]["reserve"]["allowed_values"] == [0]
    assert field_source["fields"]["reserve"]["documented_only"] is True
    assert "TileOpcode" not in field_source["fields"]
    assert field_source["fields"]["Mode"]["widths"] == [2]
    assert field_source["fields"]["Function"]["widths"] == [5]

    tma = spec["state"]["engine_ops"]["tma"]
    assert tma["function_field_bits"] == [0, 4]
    assert tma["kind"] == "function_u5"
    assert {
        (entry["function"], entry["mnemonic"])
        for entry in tma["legal_aliases"]
    } == {
        (0, "BSTART.TLOAD"),
        (1, "BSTART.TSTORE"),
        (2, "BSTART.TMOV"),
        (3, "BSTART.TPREFETCH"),
        (4, "BSTART.MGATHER"),
        (5, "BSTART.MSCATTER"),
        (6, "BSTART.MGATHER.MASK"),
        (7, "BSTART.MSCATTER.MASK"),
        (8, "BSTART.MGATHER.CAS"),
    }
    assert tma["reserved_behavior"] == "illegal_instruction"
    assert tma["reserved_function_range"] == [9, 31]
    assert "BSTART.TMA" not in mnemonics
    exact_tma = {
        inst["mnemonic"]: inst["encoding"]["parts"][0]
        for inst in instructions
        if inst["mnemonic"] in {
            "BSTART.TLOAD",
            "BSTART.TSTORE",
            "BSTART.TMOV",
            "BSTART.TPREFETCH",
        }
    }
    assert {
        name: (int(part["mask"], 0), int(part["match"], 0))
        for name, part in exact_tma.items()
    } == {
        "BSTART.TLOAD": (0x07FFFFFF, 0x00011181),
        "BSTART.TSTORE": (0x07FFFFFF, 0x00111181),
        "BSTART.TMOV": (0x07FFFFFF, 0x00211181),
        "BSTART.TPREFETCH": (0x07FFFFFF, 0x00311181),
    }

    observed_fields = {
        field["name"]
        for inst in instructions
        for part in inst["encoding"]["parts"]
        for field in part.get("fields", [])
    }
    assert "reserve" not in observed_fields
    b_catr = next(inst for inst in instructions if inst["mnemonic"] == "B.CATR")
    assert (
        int(b_catr["encoding"]["parts"][0]["mask"], 0),
        int(b_catr["encoding"]["parts"][0]["match"], 0),
    ) == (0xFBF07FFF, 0x00000023)
    trace_hint = next(inst for inst in instructions if inst["asm"] == "B.HINT TRACE.{begin, end}")
    assert int(trace_hint["encoding"]["parts"][0]["mask"], 0) == 0xFFFF7FFF

    status = json.loads((ROOT / "isa/sail/semantics_status.json").read_text(encoding="utf-8"))
    assert set(form_ids) == set(status["forms"])
    assert {
        entry["status"] for entry in status["forms"].values()
    } <= {"decode-only", "executable-subset", "architecturally-complete"}

    frame = spec["semantics_conventions"]["frame_templates_r975"]
    assert frame["applies_to"] == ["FENTRY", "FEXIT", "FRET.RA", "FRET.STK"]
    assert frame["arithmetic"]["kind"] == "immediate_only"
    assert frame["register_ring"] == {
        "inclusive_range": [2, 23],
        "allows_singleton": True,
        "allows_full_ring": True,
        "allows_wrap": True,
    }
    assert frame["legality"]["fret_ra_target"] == "fixed pre-restore R10"
    assert frame["legality"]["fret_stk_target"] == "fixed R10 restored from slot zero"
    assert frame["legality"]["fret_stk_stack_slot_zero"]["required_memory_type"] == "Normal"
    assert frame["legality"]["fret_stk_stack_slot_zero"]["requires_idempotent"] is True
    assert "before any cache, fabric, device, or MMIO physical read" in frame["legality"]["fret_stk_stack_slot_zero"]["device_mmio_or_mixed_or_non_idempotent"]

    assert frame["forms"]["FENTRY"]["d3_total_rows"] == "N+3"
    assert frame["forms"]["FENTRY"]["examples"] == {"N=1": 4, "N=22": 25}
    assert frame["forms"]["FEXIT"]["d3_total_rows"] == "N+3"
    assert frame["forms"]["FRET.RA"]["d3_total_rows"] == "N+5"
    assert frame["forms"]["FRET.STK"]["d3_total_rows"] == "N+6"
    assert frame["forms"]["FRET.STK"]["examples"] == {"N=1": 7, "N=22": 28}
    assert frame["forms"]["malformed"] == {
        "ordinals": ["0=VFORM_TRAP"],
        "d3_total_rows": 1,
        "final_row_present": False,
    }
    assert frame["d3_ownership"]["hidden_parent_row"] is False
    assert frame["d3_ownership"]["private_validator"] is False
    assert frame["d3_ownership"]["rowless_validator"] is False
    assert "Device/MMIO" in frame["vload"]["forbidden_memory_zero_read"]
    assert frame["vload"]["post_seal_replacement"] == "forbidden; enters template_integrity_fail FatalReason=2"
    assert frame["seal_and_recovery"]["rollback_after_seal"] == "forbidden for SP, GPR, memory, target, progress, and trace effects"
    assert frame["template_integrity_fail"]["trapnum"] == "ASSERT_FAIL (52)"
    assert frame["template_integrity_fail"]["maskable_by_ECONFIG3"] is False
    assert frame["template_integrity_fail"]["fixup_allowed"] is False
    assert frame["template_integrity_fail"]["acre_continuation_allowed"] is False
    assert frame["template_integrity_fail"]["fatal_reasons"]["4"] == "exact-live ownership/generation/lease/FINAL contradiction"
    assert set(frame["template_owner_id"]["field_groups"]) == {"placement", "group", "row", "memory"}
    assert frame["template_owner_id"]["exact_live_post_seal_contradiction"] == "template_integrity_fail FatalReason=4"
    assert frame["template_owner_id"]["field_groups"]["placement"] == [
        "lxcpu_id",
        "lxcpu_context_generation",
        "pe_id",
        "stid",
        "engine_local_tid",
    ]
    assert frame["lease_id"] == [
        "lease_generation",
        "validation_generation",
        "validation_token_hash",
        "exact_vtgt_TemplateOwnerID",
        "exact_vload_TemplateOwnerID_or_canonical_invalid",
        "retained_target_mapping_visibility_share_domain_key",
    ]
    assert frame["invalidation"]["producer_bases_coalesce"] is False
    assert frame["invalidation"]["txn_base_fields"] == [
        "producer_domain",
        "producer_kind",
        "producer_lxcpu_id",
        "producer_context_generation",
        "producer_pe_id",
        "producer_stid_valid",
        "producer_stid",
        "producer_tid_valid",
        "producer_engine_local_tid",
        "producer_endpoint_id",
        "transaction_sequence_value",
        "transaction_sequence_wrap_or_generation",
        "architectural_operation",
        "exact_operation_scope",
    ]
    assert frame["invalidation"]["txn_id_fields"] == [
        "complete InvalidationTxnBase",
        "matched_LeaseID_or_explicit_NO_LEASE",
        "lease_directory_generation_at_lookup",
        "status_generation",
    ]
    assert frame["invalidation"]["ack_id_fields"] == [
        "complete InvalidationTxnID",
        "exact_lease_owner_TemplateOwnerID_or_canonical_invalid",
        "terminal_kind",
    ]
    assert frame["invalidation"]["terminal_kinds"] == [
        "NO_MATCH",
        "CANCELED_PRE_EVENT",
        "RELEASED_AFTER_FINAL",
        "RELEASED_AFTER_ABORT",
    ]
    assert frame["invalidation"]["nonterminal_kinds"] == ["DEFERRED_ACTIVE"]

    producers = spec["semantics_conventions"]["fixup_blocks"]["assert_fail_producers"]
    assert producers["instruction_assert"]["ecconfig_maskable"] is True
    assert producers["instruction_assert"]["local_fixup"] == "existing instruction behavior"
    assert producers["template_integrity_fail"]["ecconfig_maskable"] is False
    assert producers["template_integrity_fail"]["local_fixup"] == "forbidden"

    _assert_rejected(
        spec,
        lambda frame: frame["template_owner_id"]["field_groups"]["placement"].remove(
            "lxcpu_context_generation"
        ),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["template_owner_id"]["field_groups"]["placement"].insert(
            1, "spurious_context_generation"
        ),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["template_owner_id"]["field_groups"]["placement"].reverse(),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["template_owner_id"]["field_groups"]["placement"].__setitem__(
            1, "context_generation"
        ),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["invalidation"]["txn_base_fields"].remove(
            "transaction_sequence_wrap_or_generation"
        ),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["invalidation"]["txn_base_fields"].insert(
            11, "transaction_sequence_epoch"
        ),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["invalidation"]["txn_base_fields"].__setitem__(
            slice(10, 12),
            list(reversed(frame["invalidation"]["txn_base_fields"][10:12])),
        ),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["invalidation"]["txn_base_fields"].__setitem__(
            11, "transaction_wrap"
        ),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["lease_id"].remove("validation_token_hash"),
    )
    _assert_rejected(
        spec,
        lambda frame: frame["invalidation"]["ack_id_fields"].append("ack_generation"),
    )
    for key in frame["target_proof"]:
        _assert_rejected(spec, lambda frame, key=key: _delete(frame["target_proof"], key))
        _assert_rejected(spec, lambda frame, key=key: _weaken(frame["target_proof"], key))

    for key in (
        "ebstate_recoverable_retention",
        "ebstate_retention_forbidden",
        "lease_directory_suspend_rule",
        "final_identity",
    ):
        _assert_rejected(spec, lambda frame, key=key: _delete(frame["seal_and_recovery"], key))
        _assert_rejected(spec, lambda frame, key=key: _weaken(frame["seal_and_recovery"], key))

    for key in (
        "fatal_teardown_order",
        "reset_reuse",
    ):
        _assert_rejected(spec, lambda frame, key=key: _delete(frame["template_integrity_fail"], key))
        _assert_rejected(spec, lambda frame, key=key: _weaken(frame["template_integrity_fail"], key))

    for key in (
        "exact_scope_fields",
        "physical_sharing_rule",
        "stale_ack_rule",
        "status_rules",
        "admission_rules",
        "terminal_rules",
        "terminal_kinds",
        "nonterminal_kinds",
    ):
        _assert_rejected(spec, lambda frame, key=key: _delete(frame["invalidation"], key))
        _assert_rejected(spec, lambda frame, key=key: _weaken(frame["invalidation"], key))

    for group in ("placement", "group", "row", "memory"):
        _assert_rejected(
            spec,
            lambda frame, group=group: _mutate_identity_array(
                frame, ("template_owner_id", "field_groups", group)
            ),
        )
    for path in (
        ("lease_id",),
        ("invalidation", "txn_base_fields"),
        ("invalidation", "txn_id_fields"),
        ("invalidation", "ack_id_fields"),
    ):
        _assert_rejected(spec, lambda frame, path=path: _mutate_identity_array(frame, path))
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
