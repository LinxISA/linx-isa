#!/usr/bin/env python3
"""Focused encoding checks for the standalone v0.57 profile."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(profile: str) -> dict:
    return json.loads((ROOT / f"isa/{profile}/linxisa-{profile}.json").read_text(encoding="utf-8"))


def _one_part(spec: dict, mnemonic: str) -> tuple[int, int]:
    inst = next(inst for inst in spec["instructions"] if inst["mnemonic"] == mnemonic)
    parts = inst["encoding"]["parts"]
    assert len(parts) == 1
    return int(parts[0]["mask"], 0), int(parts[0]["match"], 0)


def main() -> int:
    v057 = _load("v0.57")
    v057_names = {inst["mnemonic"] for inst in v057["instructions"]}

    assert {
        "BSTART.TPREFETCH",
        "BSTART.MGATHER",
        "BSTART.MSCATTER",
        "BSTART.MGATHER.MASK",
        "BSTART.MSCATTER.MASK",
        "BSTART.MGATHER.CAS",
        "BSTART.TMATMUL.BIAS",
        "BSTART.TMATMULMX",
        "BSTART.TMATMULMX.BIAS",
        "BSTART.TMATMULMX.ACC",
        "BSTART.TGEMV",
        "BSTART.TGEMV.BIAS",
        "BSTART.TGEMV.ACC",
        "BSTART.TGEMVMX",
        "BSTART.TGEMVMX.BIAS",
        "BSTART.TGEMVMX.ACC",
        "CASB",
        "CASH",
        "CASW",
        "CASD",
        "DMA",
    } <= v057_names
    assert {"BSTART.TMA", "B.IOD", "BSTART.PAR"} & v057_names == set()

    expected_tma = {
        "BSTART.TLOAD": (0x07FFFFFF, 0x00011181),
        "BSTART.TSTORE": (0x07FFFFFF, 0x00111181),
        "BSTART.TMOV": (0x07FFFFFF, 0x00211181),
        "BSTART.TPREFETCH": (0x07FFFFFF, 0x00311181),
        "BSTART.MGATHER": (0x07FFFFFF, 0x00411181),
        "BSTART.MSCATTER": (0x07FFFFFF, 0x00511181),
        "BSTART.MGATHER.MASK": (0x07FFFFFF, 0x00611181),
        "BSTART.MSCATTER.MASK": (0x07FFFFFF, 0x00711181),
        "BSTART.MGATHER.CAS": (0x07FFFFFF, 0x00811181),
    }
    for mnemonic, expected in expected_tma.items():
        assert _one_part(v057, mnemonic) == expected

    expected_pr139 = {
        "CASB": (0x0000707F, 0x0000001B),
        "CASH": (0x0000707F, 0x0000101B),
        "CASW": (0x0000707F, 0x0000201B),
        "CASD": (0x0000707F, 0x0000301B),
        "DMA": (0xFE007FFF, 0x0000700B),
    }
    for mnemonic, expected in expected_pr139.items():
        assert _one_part(v057, mnemonic) == expected

    one_part_32 = [
        (
            inst["mnemonic"],
            int(inst["encoding"]["parts"][0]["mask"], 0),
            int(inst["encoding"]["parts"][0]["match"], 0),
        )
        for inst in v057["instructions"]
        if inst["length_bits"] == 32 and len(inst["encoding"]["parts"]) == 1
    ]
    tma_base = 0x00011181
    expected_by_function = {
        0: "BSTART.TLOAD",
        1: "BSTART.TSTORE",
        2: "BSTART.TMOV",
        3: "BSTART.TPREFETCH",
        4: "BSTART.MGATHER",
        5: "BSTART.MSCATTER",
        6: "BSTART.MGATHER.MASK",
        7: "BSTART.MSCATTER.MASK",
        8: "BSTART.MGATHER.CAS",
    }
    for dtype in range(32):
        for function in range(32):
            word = (dtype << 27) | (function << 20) | tma_base
            matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
            if function in expected_by_function:
                assert matches == [expected_by_function[function]], (dtype, function, matches)
            else:
                assert matches == [], (dtype, function, matches)

    expected_cube = {
        0: "BSTART.TMATMUL",
        1: "BSTART.TMATMUL.BIAS",
        2: "BSTART.TMATMUL.ACC",
        4: "BSTART.TMATMULMX",
        5: "BSTART.TMATMULMX.BIAS",
        6: "BSTART.TMATMULMX.ACC",
        8: "BSTART.ACCCVT",
        16: "BSTART.TGEMV",
        17: "BSTART.TGEMV.BIAS",
        18: "BSTART.TGEMV.ACC",
        20: "BSTART.TGEMVMX",
        21: "BSTART.TGEMVMX.BIAS",
        22: "BSTART.TGEMVMX.ACC",
    }
    cube_base = 0x00031181
    for dtype in range(32):
        for function in range(32):
            word = (dtype << 27) | (function << 20) | cube_base
            matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
            if function in expected_cube:
                assert matches == sorted(["BSTART.CUBE", expected_cube[function]]), (dtype, function, matches)
            else:
                assert matches == ["BSTART.CUBE"], (dtype, function, matches)

    v057_tepl = {
        op["name"]: int(op["tile_opcode"])
        for op in v057["state"]["engine_ops"]["tepl"]["ops"]
    }
    expected_new_tepl = {
        "TCMP": 0x02B,
        "TSEL": 0x02C,
        "TABS": 0x02D,
        "TNOT": 0x02E,
        "TNEG": 0x02F,
        "TREM": 0x030,
        "TAXPY": 0x031,
        "TREMS": 0x032,
        "TCMPS": 0x033,
        "TSELS": 0x034,
        "TROWPROD": 0x035,
        "TROWARGMAX": 0x036,
        "TROWARGMIN": 0x037,
        "TCOLPROD": 0x038,
        "TCOLARGMAX": 0x039,
        "TCOLARGMIN": 0x03A,
        "TROWEXPANDADD": 0x03B,
        "TROWEXPANDSUB": 0x03C,
        "TROWEXPANDMUL": 0x03D,
        "TROWEXPANDDIV": 0x03E,
        "TROWEXPANDMAX": 0x03F,
        "TROWEXPANDMIN": 0x040,
        "TROWEXPANDEXPDIF": 0x041,
        "TCOLEXPANDADD": 0x042,
        "TCOLEXPANDSUB": 0x043,
        "TCOLEXPANDMUL": 0x044,
        "TCOLEXPANDDIV": 0x045,
        "TCOLEXPANDMAX": 0x046,
        "TCOLEXPANDMIN": 0x047,
        "TCOLEXPANDEXPDIF": 0x048,
        "TCI": 0x080,
        "TTRI": 0x081,
        "TFILLPAD": 0x082,
        "TQUANT": 0x083,
        "TDEQUANT": 0x084,
        "TEXTRACT": 0x085,
        "TINSERT": 0x086,
        "TCONCAT": 0x087,
        "TIMG2COL": 0x088,
        "TGATHERB": 0x089,
        "TDEINTERLEAVE": 0x08A,
        "TINTERLEAVE": 0x08B,
        "TSORT": 0x0C0,
        "TMRGSORT": 0x0C1,
        "THISTOGRAM": 0x0C2,
        "TPARTADD": 0x0C3,
        "TPARTMUL": 0x0C4,
        "TPARTMAX": 0x0C5,
        "TPARTMIN": 0x0C6,
        "TPARTARGMAX": 0x0C7,
        "TPARTARGMIN": 0x0C8,
        "TPUSH": 0x0E0,
        "TPOP": 0x0E1,
        "TALLOC": 0x0E2,
        "TFREE": 0x0E3,
    }
    for name, selector in expected_new_tepl.items():
        assert v057_tepl[name] == selector
    assert {"TFMOD", "TPOW", "TRANDOM", "TEXRACT"} & set(v057_tepl) == set()

    frame = v057["semantics_conventions"]["frame_templates_r975"]
    assert frame["step_index"]["meaning"] == "next_uncommitted_phase_one_event"
    assert frame["phase_fault_envelopes"]["phase_zero"] == {
        "bi": 0,
        "phase": 0,
        "step_index": 0,
        "dirty": 0,
        "redo_ok": 1,
        "resume_ok": 0,
        "template_effect": "none",
    }
    assert frame["phase_fault_envelopes"]["phase_one_recoverable"]["resume_ok"] == 1
    assert frame["phase_fault_envelopes"]["phase_one_recoverable"]["redo_ok"] == 0
    assert frame["phase_fault_envelopes"]["post_seal_fatal"]["resume_ok"] == 0
    assert frame["phase_fault_envelopes"]["post_seal_fatal"]["reuse_boundary"] == "platform reset only"
    assert frame["target_proof"] == {
        "actual_current_marker_proof": "required before every FRET effect",
        "coherent_marker_provenance_cache": "legal only when it proves the same target marker bytes, address-space state, code-visibility epoch, and invalidation scope as an actual current marker proof",
        "metadata_only_continuation_or_fallthrough": "non-conforming compatibility; must be rejected",
        "deferred_demand_paging": "qualified only while every FRET effect remains withheld",
        "fault_owner": "VTGT owns translation, execute-permission, marker, and CFI faults",
    }
    assert frame["seal_and_recovery"]["event_zero_seal_transaction"] == [
        "recheck_all_identities_and_generations",
        "acquire_complete_FRET_lease",
        "retire_successful_validation_rows_with_distinct_traces",
        "commit_event_zero",
        "advance_StepIndex_0_to_1",
    ]
    assert frame["seal_and_recovery"]["before_seal_invalidation"] == (
        "wins and cancels phase zero with no effect"
    )
    assert frame["seal_and_recovery"]["after_seal_invalidation"] == (
        "lease wins; producer completion waits through traps, ACRE, suspension, FINAL, or fatal release"
    )
    assert frame["seal_and_recovery"]["rollback_after_seal"] == (
        "forbidden for SP, GPR, memory, target, progress, and trace effects"
    )
    assert frame["seal_and_recovery"]["final"] == (
        "qualifies full token, performs boundary transfer/retirement, and releases lease atomically"
    )
    assert frame["seal_and_recovery"]["ebstate_recoverable_retention"] == [
        "exact TemplateOwnerID",
        "phase and StepIndex cursors",
        "sealed VLOAD state when applicable",
        "validation token",
        "retained lease",
        "complete pending InvalidationTxnID/status set",
    ]
    assert frame["seal_and_recovery"]["ebstate_retention_forbidden"] == [
        "renumber pending invalidation entries",
        "merge pending invalidation entries",
        "reacquire lease entries",
        "restore a pre-template checkpoint",
    ]
    assert frame["seal_and_recovery"]["lease_directory_suspend_rule"] == (
        "lease directory retains discoverability during suspension; a manager must resume through FINAL or choose fatal abandonment and cannot wait on its own deferred invalidation"
    )
    assert frame["seal_and_recovery"]["final_identity"] == {
        "required_matches": [
            "group",
            "checkpoint",
            "template",
            "validation",
            "lease",
            "VTGT key",
            "VLOAD key or canonical invalid",
            "visibility/share-domain",
            "FINAL RID/slot/generation",
            "final ordinal",
        ],
        "shortcut_authority_forbidden": ["queue head", "BID", "RID value", "PC", "opcode", "hash alone"],
    }
    assert frame["lease_id"] == [
        "lease_generation",
        "validation_generation",
        "validation_token_hash",
        "exact_vtgt_TemplateOwnerID",
        "exact_vload_TemplateOwnerID_or_canonical_invalid",
        "retained_target_mapping_visibility_share_domain_key",
    ]
    assert frame["invalidation"]["exact_scope_fields"] == [
        "ACR/regime/root/ASID",
        "VA/PA page or marker range",
        "TLB/code/coherence domain",
        "global/wildcard selectors",
    ]
    assert frame["invalidation"]["physical_sharing_rule"] == (
        "physical lookup/cancel/drain/release work may be shared only for transactions matching the same exact LeaseID; producer transaction bases, status, and AckID remain independent"
    )
    assert frame["invalidation"]["stale_ack_rule"] == (
        "wrong producer, sequence, operation/scope, match, directory, owner, or status-generation is rejected; identical terminal AckID retransmission is idempotent"
    )
    assert frame["invalidation"]["status_rules"] == [
        "each state transition increments status_generation",
        "matching post-seal transactions independently record DEFERRED_ACTIVE",
        "FINAL creates one RELEASED_AFTER_FINAL per pending match",
        "fatal release creates one RELEASED_AFTER_ABORT per pending match",
        "post-release admission performs a new lookup at new directory generation",
    ]
    assert frame["invalidation"]["admission_rules"] == [
        "capacity may backpressure before admission",
        "an admitted transaction cannot be dropped",
        "an admitted matching transaction cannot complete before FINAL or fatal release",
        "a manager cannot roll back or wait on its own deferred invalidation",
    ]
    assert frame["invalidation"]["terminal_rules"] == [
        "NO_MATCH after lookup at the transaction directory generation for nonmatches",
        "CANCELED_PRE_EVENT only after cancellation prevents stale event-zero seal",
        "DEFERRED_ACTIVE recorded independently for each post-seal match and is nonterminal",
        "RELEASED_AFTER_FINAL created atomically by FINAL per pending match",
        "RELEASED_AFTER_ABORT created atomically by fatal release per pending match after quiescence",
        "post-release admission performs a new lookup at the new directory generation and normally receives NO_MATCH",
    ]
    assert frame["template_integrity_fail"]["fatal_teardown_order"] == [
        "stop source-context issue, commit, wakeup, redirect, FINAL transfer, and new lease acquisition",
        "snapshot exact envelope, state, owner, token, and pending transactions",
        "advance template, row, and load generations",
        "cancel every uncommitted row and request",
        "invalidate VLOAD data, VTGT proof, token, and queued transfer",
        "obtain quiescence from every listed owner before releasing the lease",
        "atomically release the lease and create one RELEASED_AFTER_ABORT per pending matching invalidation",
        "publish the fatal record for managing-ring inspection",
    ]
    assert frame["template_integrity_fail"]["reset_reuse"] == {
        "platform_reset_only": True,
        "new_context_generation_required": True,
        "global_quiescence_before_reset": True,
        "no_pre_reset_ack_after_new_context_generation": True,
        "pre_template_state_restore": "forbidden",
    }
    assert v057["semantics_conventions"]["fixup_blocks"]["assert"]["masking"]["scope"] == (
        "ASSERT-instruction-generated ASSERT_FAIL only (other synchronous exceptions are unaffected)"
    )

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
