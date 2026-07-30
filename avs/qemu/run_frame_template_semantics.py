#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import selectors
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
SRC = SCRIPT_DIR / "tests" / "16_frame_template_semantics.S"
SCHEMA = "linx.qemu.frame_template_semantics.v2"
FINISHER_ADDR = 0x10009000
PASS_VALUE = 0x5555
PASS_LOW8 = PASS_VALUE & 0xFF
EXPECTED_DYNAMIC_ENVS = [None, "64"]
FRET_STK_DYNAMIC_CONFIGS = [
    {
        "label": "default-fallback",
        "env": {
            "LINX_FRET_STK_TRACE": "1",
        },
        "expected": {
            "restore_host_loads": 0,
            "restore_fallback_loads": 1,
            "host_verify_loads": 0,
            "slot0_physical_reads": 1,
            "slot0_physical_reads_proven": 1,
            "physical_restore_reads": 1,
            "status": "pass",
        },
    },
    {
        "label": "cached-host",
        "env": {
            "LINX_FRET_STK_TRACE": "1",
            "LINX_QEMU_FRAME_RESTORE_HOST_LOAD": "1",
        },
        "expected": {
            "restore_host_loads": 1,
            "restore_fallback_loads": 0,
            "host_verify_loads": 0,
            "slot0_physical_reads": 1,
            "slot0_physical_reads_proven": 1,
            "physical_restore_reads": 1,
            "status": "pass",
        },
    },
    {
        "label": "cached-host-verify",
        "env": {
            "LINX_FRET_STK_TRACE": "1",
            "LINX_QEMU_FRAME_RESTORE_HOST_LOAD": "1",
            "LINX_QEMU_FRAME_RESTORE_HOST_VERIFY": "1",
        },
        "expected": {
            "restore_host_loads": 1,
            "restore_fallback_loads": 0,
            "host_verify_loads": 0,
            "slot0_physical_reads": 1,
            "slot0_physical_reads_proven": 1,
            "physical_restore_reads": 1,
            "status": "pass",
        },
    },
]
U64_MASK = (1 << 64) - 1
GPR_NAMES = (
    "zero", "sp", "a0", "a1", "a2", "a3", "a4", "a5",
    "a6", "a7", "ra", "s0", "s1", "s2", "s3", "s4",
    "s5", "s6", "s7", "s8", "x0", "x1", "x2", "x3",
)


@dataclass(frozen=True)
class Case:
    case_id: str
    kind: str
    requirement: str
    case_number: int | None = None
    current_blocker: str | None = None


RAW_GUEST_ENCODINGS = {
    "valid_singleton_ra_terminal": {
        "fentry_word": "0x04a50041",
        "fexit_word": "0x04a51041",
        "intent": "FENTRY/FEXIT [ra ~ ra], sp!, 16",
    },
    "valid_wrap_r22_ra_terminal": {
        "fentry_word": "0x16ab0041",
        "fexit_word": "0x16ab1041",
        "intent": "FENTRY/FEXIT [x2 ~ ra], sp!, 88",
    },
    "valid_full_r2_s12_terminal": {
        "fentry_word": "0x2d710041",
        "fexit_word": "0x2d711041",
        "intent": "FENTRY/FEXIT [r2 ~ r23], sp!, 176",
    },
    "fret_ra_pre_restore_target": {
        "fret_ra_word": "0x04a52041",
        "intent": "setup block; FRET.RA [ra ~ ra], sp!, 16",
    },
    "fret_stk_retained_slot0_target": {
        "fentry_word": "0x04a50041",
        "fret_stk_word": "0x04a53041",
        "intent": "FRET.STK [ra ~ ra], sp!, 16 with slot0 target retention",
    },
}
EXPECTED_FENTRY_STACKSIZE = {
    "valid_singleton_ra_terminal": 16,
    "valid_wrap_r22_ra_terminal": 88,
    "valid_full_r2_s12_terminal": 176,
}
FENTRY_DYNAMIC_CASES = {
    "valid_singleton_ra_terminal",
    "valid_wrap_r22_ra_terminal",
    "valid_full_r2_s12_terminal",
}
FRET_RA_CASE_ID = "fret_ra_pre_restore_target"
FRET_RA_PRE_MARKER = "LINX_FRET_RA_PRE_TARGET case=4"
FRET_RA_RESTORED_MARKER = "LINX_FRET_RA_RESTORED_TARGET case=4"
FRET_STK_CASE_ID = "fret_stk_retained_slot0_target"
FRET_STK_RETAINED_MARKER = "LINX_FRET_STK_RETAINED_TARGET case=5"


MANIFEST = [
    Case("valid_singleton_ra_terminal", "dynamic", "Compile and execute FENTRY/FEXIT [ra ~ ra], sp!, 16.", 1),
    Case("valid_wrap_r22_ra_terminal", "dynamic", "Compile and execute legal inclusive wrap range [x2 ~ ra], sp!, 88.", 2),
    Case("valid_full_r2_s12_terminal", "dynamic", "Compile and execute the full accepted R2..R23 register ring.", 3),
    Case(
        "encoded_f_environment_invariance",
        "semantic",
        "Same guest bytes must prove encoded F only under unset and malicious LINX_CALLFRAME_SIZE.",
    ),
    Case(
        "high_end_slot_addresses",
        "semantic",
        "Machine-readable state must prove slots use C - 8*(i+1).",
    ),
    Case(
        "fret_ra_pre_restore_target",
        "dynamic",
        "FRET.RA must publish pre-restore R10 even when slot0 differs.",
        4,
    ),
    Case(
        "fret_stk_retained_slot0_target",
        "dynamic",
        "FRET.STK must use the retained slot-zero target and not reread slot0.",
        5,
    ),
    Case(
        "malformed_admission_zero_effect",
        "required-red",
        "Bad endpoint/alignment/F<N/target cases must prove zero SP/GPR/memory/target effect.",
        current_blocker="bad_target_zero_effect_oracle_missing",
    ),
    Case(
        "phase_one_every_event_resume",
        "required-red",
        "Every phase-one event fault must retain earlier effects and resume at exact StepIndex.",
        current_blocker="phase_one_resume_oracle_missing",
    ),
    Case(
        "device_mmio_vload_zero_read",
        "required-red",
        "Device/MMIO FRET.STK VLOAD must produce zero physical read and phase-zero fault.",
        current_blocker="device_mmio_vload_zero_read_oracle_missing",
    ),
]


def _slot_sequence(pre_sp: int, registers: list[str], values: list[int]) -> list[dict[str, Any]]:
    return [
        {
            "index": index,
            "register": reg,
            "address": pre_sp - 8 * (index + 1),
            "value": values[index],
        }
        for index, reg in enumerate(registers)
    ]


def _decode_fentry_word(raw_word: str) -> dict[str, Any]:
    """Decode the accepted v0.57 FENTRY fields without consulting trace rows."""
    try:
        word = int(raw_word, 0)
    except (TypeError, ValueError) as exc:
        raise TerminalEvidenceError(f"invalid raw FENTRY word: {raw_word!r}") from exc
    if word & 0x707F != 0x0041:
        raise TerminalEvidenceError(f"raw word is not a 32-bit FENTRY: {raw_word}")
    begin_index = (word >> 15) & 0x1F
    end_index = (word >> 20) & 0x1F
    stacksize = ((((word >> 7) & 0x1F) << 10) | ((word >> 25) & 0x7F)) << 3
    if not (2 <= begin_index <= 23 and 2 <= end_index <= 23):
        raise TerminalEvidenceError(f"raw FENTRY endpoint outside R2..R23: {raw_word}")
    register_indices: list[int] = []
    current = begin_index
    for _ in range(22):
        register_indices.append(current)
        if current == end_index:
            break
        current = 2 if current == 23 else current + 1
    else:
        raise TerminalEvidenceError(f"raw FENTRY ring does not terminate: {raw_word}")
    save_count = len(register_indices)
    legal_min_frame = 8 * save_count
    return {
        "raw_fentry_word": f"0x{word:08x}",
        "begin_index": begin_index,
        "end_index": end_index,
        "begin": GPR_NAMES[begin_index],
        "end": GPR_NAMES[end_index],
        "stacksize": stacksize,
        "register_indices": register_indices,
        "registers": [GPR_NAMES[index] for index in register_indices],
        "save_count": save_count,
        "legal_min_frame": legal_min_frame,
        "legal": stacksize >= legal_min_frame,
    }


def _case_fentry_decode(case: Case) -> dict[str, Any]:
    decoded = _decode_fentry_word(RAW_GUEST_ENCODINGS[case.case_id]["fentry_word"])
    if not decoded["legal"]:
        raise TerminalEvidenceError(
            f"{case.case_id}: raw FENTRY frame {decoded['stacksize']} is smaller than "
            f"8*N ({decoded['legal_min_frame']})"
        )
    return decoded


def _semantic_observations() -> dict[str, dict[str, Any]]:
    singleton_regs = ["ra"]
    wrap_regs = list(_decode_fentry_word("0x16ab0041")["registers"])
    full_regs = list(_decode_fentry_word("0x2d710041")["registers"])
    cases = {
        "valid_singleton_ra_terminal": (0x800000, 16, singleton_regs, [0x1111222233334444]),
        "valid_wrap_r22_ra_terminal": (
            0x801000,
            88,
            wrap_regs,
            [0x2200000000000000 + i for i in range(len(wrap_regs))],
        ),
        "valid_full_r2_s12_terminal": (
            0x802000,
            176,
            full_regs,
            [0x4400000000000000 + i for i in range(len(full_regs))],
        ),
    }
    env_records = []
    high_end_cases = []
    for case_id, (pre_sp, frame_bytes, regs, values) in cases.items():
        slots = _slot_sequence(pre_sp, regs, values)
        for env in EXPECTED_DYNAMIC_ENVS:
            env_records.append(
                {
                    "case_id": case_id,
                    "environment": {"LINX_CALLFRAME_SIZE": env},
                    "initial_state": {"sp": pre_sp, "register_values": dict(zip(regs, values, strict=True))},
                    "ordered_events": [
                        {"step_index": 0, "event": "SP_SUB", "old_sp": pre_sp, "new_sp": pre_sp - frame_bytes},
                        *[
                            {
                                "step_index": index + 1,
                                "event": "STORE_i",
                                "slot": slot,
                            }
                            for index, slot in enumerate(slots)
                        ],
                    ],
                    "final_state": {"sp": pre_sp - frame_bytes, "target": None},
                }
            )
        high_end_cases.append(
            {
                "case_id": case_id,
                "initial_state": {"sp": pre_sp},
                "ordered_slots": slots,
                "final_state": {"sp": pre_sp - frame_bytes},
            }
        )
    return {
        "encoded_f_environment_invariance": {
            "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
            "record_kind": "encoded_f_environment_invariance",
            "raw_guest_identity": RAW_GUEST_ENCODINGS,
            "records": env_records,
        },
        "high_end_slot_addresses": {
            "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
            "record_kind": "high_end_slot_addresses",
            "records": high_end_cases,
        },
        "fret_ra_pre_restore_target": {
            "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
            "record_kind": "fret_ra_pre_restore_target",
            "raw_word": "0x04a52041",
            "initial_state": {
                "pre_ra_symbol": "fret_ra_pre_restore_target",
                "slot0_symbol": "fret_ra_restored_target",
                "distinct_targets": True,
            },
            "ordered_events": [
                {"step_index": 0, "event": "SET_PRE_RA", "symbol": "fret_ra_pre_restore_target"},
                {"step_index": 1, "event": "STORE_SLOT0", "symbol": "fret_ra_restored_target"},
                {"step_index": 2, "event": "FRET_RA", "raw_word": "0x04a52041"},
                {"step_index": 3, "event": "REACH_PRE_RESTORE_MARKER"},
                {"step_index": 4, "event": "VERIFY_POST_RA_WITH_EXPLICIT_RET"},
                {"step_index": 5, "event": "REACH_RESTORED_RA_MARKER"},
            ],
            "final_state": {"terminal": "pass"},
        },
        "fret_stk_retained_slot0_target": {
            "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
            "record_kind": "fret_stk_retained_slot0_target",
            "raw_word": "0x04a53041",
            "initial_state": {"sp": 0x820000, "r10": 0x1111000011110000, "slot0": 0x2222000022220000},
            "ordered_events": [
                {"step_index": 0, "event": "VLOAD", "address": 0x81FFF8, "physical_read_count": 1, "value": 0x2222000022220000},
                {"step_index": 1, "event": "VTGT", "source": "retained_slot0", "value": 0x2222000022220000},
                {"step_index": 2, "event": "SP_ADD", "old_sp": 0x820000, "new_sp": 0x820010},
                {"step_index": 3, "event": "RESTORE_R10", "value": 0x2222000022220000, "additional_physical_reads": 0},
                {"step_index": 4, "event": "TARGET_PUBLISH", "target": 0x2222000022220000},
            ],
            "final_state": {"sp": 0x820010, "r10": 0x2222000022220000, "published_target": 0x2222000022220000},
        },
        "malformed_admission_zero_effect": {
            "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
            "record_kind": "malformed_admission_zero_effect",
            "records": [
                {
                    "malformed_form": form,
                    "raw_word": raw,
                    "initial_state": {"sp": 0x830000, "r10": 0x1234, "memory_digest": "sha256:before-a"},
                    "fault": {"phase": 0, "step_index": 0, "bi": 0, "dirty": 0, "redo": 1, "resume": 0, "cause": cause},
                    "final_state": {"sp": 0x830000, "r10": 0x1234, "memory_digest": "sha256:before-a", "target": None},
                }
                for form, raw, cause in [
                    ("bad_endpoint", "0x00210041", "E_INST/ENDPOINT"),
                    ("bad_alignment", "0x04a50141", "E_INST/ALIGNMENT"),
                    ("insufficient_f_wrap_11_frame_32", "0x08ab0041", "E_INST/F_TOO_SMALL"),
                    ("non_r10_fret_stk", "0x04b53041", "E_INST/FRET_STK_BEGIN"),
                ]
            ],
        },
        "phase_one_every_event_resume": {
            "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
            "record_kind": "phase_one_every_event_resume",
            "records": [
                {
                    "form": form,
                    "faulting_event": event,
                    "initial_state": {"sp": 0x840000, "memory_digest": "sha256:phase-one-before"},
                    "prior_effects": prior,
                    "fault": {"phase": 1, "step_index": step, "bi": 1, "dirty": 1, "redo": 0, "resume": 1},
                    "resume_events": [{"step_index": step, "event": event}, {"step_index": step + 1, "event": "FINAL"}],
                    "final_state": {"memory_digest": "sha256:phase-one-after"},
                }
                for form, event, step, prior in [
                    ("FENTRY", "STORE_i", 2, [{"event": "SP_SUB", "sp": 0x83FFF0}]),
                    ("FEXIT", "LOAD_i", 2, [{"event": "SP_ADD", "sp": 0x840010}]),
                    ("FRET.RA", "LOAD_i", 4, [{"event": "TARGET_PUBLISH", "target": 0x9000}, {"event": "SP_ADD", "sp": 0x840010}]),
                    ("FRET.STK", "RESTORE_R10", 4, [{"event": "SP_ADD", "sp": 0x840010}]),
                ]
            ],
        },
        "device_mmio_vload_zero_read": {
            "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
            "record_kind": "device_mmio_vload_zero_read",
            "raw_word": "0x04a53041",
            "initial_state": {"sp": 0x850000, "slot0_va": 0x10009000, "physical_read_counter": 17},
            "classification": {"address": 0x10009000, "range": "0x10009000..0x10009007", "type": "Device/MMIO"},
            "ordered_events": [],
            "fault": {"phase": 0, "step_index": 0, "cause": "E_DATA/MMU_PERM", "physical_read_counter": 17},
            "final_state": {"sp": 0x850000, "physical_read_counter": 17, "template_effects": []},
        },
    }


EXPECTED_SEMANTIC_OBSERVATIONS = _semantic_observations()
EXPECTED_CURRENT_BLOCKER_ROWS = [
    {
        "id": case.current_blocker,
        "case": case.case_id,
        "status": "required-red",
        "reason": case.requirement,
    }
    for case in MANIFEST
    if case.current_blocker is not None
]
EXPECTED_CURRENT_BLOCKERS = {row["id"] for row in EXPECTED_CURRENT_BLOCKER_ROWS}


class TerminalEvidenceError(ValueError):
    pass


def _default_clang() -> Path:
    return REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang"


def _default_lld() -> Path:
    return REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "ld.lld"


def _default_qemu() -> Path:
    return REPO_ROOT / "emulator" / "qemu" / "build-linx" / "qemu-system-linx64"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _check_exe(path: Path, what: str) -> Path:
    if not path.exists():
        raise SystemExit(f"error: {what} not found: {path}")
    if not os.access(path, os.X_OK):
        raise SystemExit(f"error: {what} is not executable: {path}")
    return path


def _run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, check=False, **kwargs)


def _case_by_id() -> dict[str, Case]:
    return {case.case_id: case for case in MANIFEST}


def _terminal_token(case: Case) -> str:
    assert case.case_number is not None
    return (
        f"LINX_FRAME_TEMPLATE case={case.case_number} status=PASS "
        f"finisher_addr=0x{FINISHER_ADDR:08x} finisher_value=0x{PASS_VALUE:08x}"
    )


def _terminal_trace_line() -> str:
    return f"linx_virt_exit_write value=0x{PASS_VALUE:x}"


TOKEN_RE = re.compile(
    r"^LINX_FRAME_TEMPLATE case=(?P<case>[0-9]+) status=PASS "
    r"finisher_addr=(?P<addr>0x[0-9a-fA-F]+) finisher_value=(?P<value>0x[0-9a-fA-F]+)$",
    re.MULTILINE,
)
TRACE_RE = re.compile(r"linx_virt_exit_write value=(?P<value>0x[0-9a-fA-F]+)")
FENTRY_TRACE_RE = re.compile(
    r"^LINX_FENTRY_TRACE count=(?P<count>[0-9]+)"
    r" pc=(?P<pc>0x[0-9a-fA-F]+) next_pc=(?P<next_pc>0x[0-9a-fA-F]+)"
    r" old_sp=(?P<old_sp>0x[0-9a-fA-F]+) new_sp=(?P<new_sp>0x[0-9a-fA-F]+)"
    r" stacksize=(?P<stacksize>[0-9]+) callframe=(?P<callframe>[0-9]+)"
    r" begin=(?P<begin>[^ ]+) end=(?P<end>[^ ]+) save_count=(?P<save_count>[0-9]+)",
    re.MULTILINE,
)
FENTRY_SLOT_RE = re.compile(
    r"^LINX_FENTRY_SLOT count=(?P<count>[0-9]+)"
    r" pc=(?P<pc>0x[0-9a-fA-F]+) reg=(?P<reg>[^ ]+)"
    r" addr=(?P<addr>0x[0-9a-fA-F]+) value=(?P<value>0x[0-9a-fA-F]+)"
    r" mmu=(?P<mmu>[0-9]+) mmu_readback=(?P<mmu_readback>0x[0-9a-fA-F]+)"
    r" host=(?P<host>[^ ]+) host_readback=(?P<host_readback>0x[0-9a-fA-F]+)"
    r" debug_read_ok=(?P<debug_read_ok>[01]) debug_readback=(?P<debug_readback>0x[0-9a-fA-F]+)$",
    re.MULTILINE,
)
FRET_RA_PRE_MARKER_RE = re.compile(r"^LINX_FRET_RA_PRE_TARGET case=(?P<case>[0-9]+)$", re.MULTILINE)
FRET_RA_RESTORED_MARKER_RE = re.compile(
    r"^LINX_FRET_RA_RESTORED_TARGET case=(?P<case>[0-9]+)$",
    re.MULTILINE,
)
FRET_STK_RETAINED_MARKER_RE = re.compile(
    r"^LINX_FRET_STK_RETAINED_TARGET case=(?P<case>[0-9]+)$",
    re.MULTILINE,
)
FRET_STK_TRACE_PREFIX = "LINX_FRET_STK_TRACE "
FRET_STK_SLOT_PREFIX = "LINX_FRET_STK_SLOT "
FRET_STK_PUBLISH_PREFIX = "LINX_FRET_STK_PUBLISH "


def _parse_trace_kv_line(line: str, prefix: str) -> dict[str, str]:
    if not line.startswith(prefix):
        raise TerminalEvidenceError(f"trace line missing prefix {prefix.strip()}")
    values: dict[str, str] = {}
    for token in line[len(prefix):].split():
        if "=" not in token:
            raise TerminalEvidenceError(f"malformed trace token: {token!r}")
        key, value = token.split("=", 1)
        if key in values:
            raise TerminalEvidenceError(f"duplicate trace field: {key}")
        values[key] = value
    return values


def _int_field(fields: dict[str, str], key: str, *, base: int = 0) -> int:
    if key not in fields:
        raise TerminalEvidenceError(f"missing trace field: {key}")
    try:
        return int(fields[key], base)
    except ValueError as exc:
        raise TerminalEvidenceError(f"invalid integer trace field: {key}={fields[key]!r}") from exc


def _require_fields(fields: dict[str, str], keys: tuple[str, ...], *, label: str) -> None:
    missing = [key for key in keys if key not in fields]
    if missing:
        raise TerminalEvidenceError(f"{label}: missing fields: {', '.join(missing)}")


def _parse_terminal_evidence(text: str, case: Case) -> dict[str, Any]:
    token_matches = list(TOKEN_RE.finditer(text))
    trace_matches = list(TRACE_RE.finditer(text))
    if len(token_matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one terminal token")
    if len(trace_matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one finisher trace event")
    token = token_matches[0]
    trace = trace_matches[0]
    terminal_case = int(token.group("case"))
    addr = int(token.group("addr"), 16)
    value = int(token.group("value"), 16)
    trace_value = int(trace.group("value"), 16)
    if terminal_case != case.case_number:
        raise TerminalEvidenceError(f"{case.case_id}: terminal case id mismatch")
    if addr != FINISHER_ADDR:
        raise TerminalEvidenceError(f"{case.case_id}: finisher address mismatch")
    if value != PASS_VALUE:
        raise TerminalEvidenceError(f"{case.case_id}: finisher value mismatch")
    if trace_value != PASS_VALUE:
        raise TerminalEvidenceError(f"{case.case_id}: qemu finisher trace value mismatch")
    return {
        "case_id": case.case_id,
        "case_number": case.case_number,
        "token": token.group(0),
        "terminal_pass_low8": True,
        "terminal_case_id": terminal_case,
        "finisher_addr": addr,
        "finisher_value": value,
        "qemu_trace_event": "linx_virt_exit_write",
    }


def _parse_fentry_trace_evidence(text: str, case: Case, env_value: str | None) -> dict[str, Any]:
    matches = list(FENTRY_TRACE_RE.finditer(text))
    if len(matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one FENTRY trace record")
    match = matches[0]
    old_sp = int(match.group("old_sp"), 16)
    new_sp = int(match.group("new_sp"), 16)
    stacksize = int(match.group("stacksize"))
    callframe = int(match.group("callframe"))
    instruction_count = int(match.group("count"))
    next_pc = int(match.group("next_pc"), 16)
    save_count = int(match.group("save_count"))
    decoded = _case_fentry_decode(case)
    delta = (old_sp - new_sp) & U64_MASK
    if stacksize != decoded["stacksize"]:
        raise TerminalEvidenceError(f"{case.case_id}: FENTRY stacksize mismatch")
    if match.group("begin") != decoded["begin"] or match.group("end") != decoded["end"]:
        raise TerminalEvidenceError(f"{case.case_id}: FENTRY begin/end mismatch with raw encoding")
    if save_count != decoded["save_count"]:
        raise TerminalEvidenceError(f"{case.case_id}: FENTRY save_count mismatch with raw encoding")
    if callframe != 0:
        raise TerminalEvidenceError(f"{case.case_id}: FENTRY callframe must be zero")
    if new_sp != ((old_sp - stacksize) & U64_MASK):
        raise TerminalEvidenceError(f"{case.case_id}: FENTRY SP delta mismatch")
    pc = int(match.group("pc"), 16)
    if next_pc != ((pc + 4) & U64_MASK):
        raise TerminalEvidenceError(f"{case.case_id}: FENTRY next PC mismatch")
    return {
        "case_id": case.case_id,
        "raw_fentry_word": decoded["raw_fentry_word"],
        "env": {"LINX_CALLFRAME_SIZE": env_value},
        "instruction_count": instruction_count,
        "pc": pc,
        "next_pc": next_pc,
        "old_sp": old_sp,
        "new_sp": new_sp,
        "stacksize": stacksize,
        "delta": delta,
        "callframe": callframe,
        "begin_index": decoded["begin_index"],
        "end_index": decoded["end_index"],
        "begin": decoded["begin"],
        "end": decoded["end"],
        "save_count": save_count,
        "legal_min_frame": decoded["legal_min_frame"],
    }


def _parse_fentry_slot_evidence(
    text: str,
    case: Case,
    fentry_trace: dict[str, Any],
) -> list[dict[str, Any]]:
    matches = list(FENTRY_SLOT_RE.finditer(text))
    if not matches:
        raise TerminalEvidenceError(f"{case.case_id}: expected FENTRY slot trace records")
    old_sp = fentry_trace.get("old_sp")
    pc = fentry_trace.get("pc")
    instruction_count = fentry_trace.get("instruction_count")
    decoded = _case_fentry_decode(case)
    if not isinstance(old_sp, int) or not isinstance(pc, int) or not isinstance(instruction_count, int):
        raise TerminalEvidenceError(f"{case.case_id}: FENTRY trace must bind old SP and PC before slots")
    if len(matches) != decoded["save_count"]:
        raise TerminalEvidenceError(
            f"{case.case_id}: expected exactly {decoded['save_count']} FENTRY slot trace records"
        )
    slots: list[dict[str, Any]] = []
    seen_addresses: set[int] = set()
    for index, match in enumerate(matches):
        addr = int(match.group("addr"), 16)
        value = int(match.group("value"), 16)
        mmu_readback = int(match.group("mmu_readback"), 16)
        host_readback = int(match.group("host_readback"), 16)
        debug_read_ok = int(match.group("debug_read_ok"))
        debug_readback = int(match.group("debug_readback"), 16)
        expected_addr = (old_sp - 8 * (index + 1)) & U64_MASK
        if int(match.group("count")) != instruction_count:
            raise TerminalEvidenceError(f"{case.case_id}: FENTRY slot instruction count mismatch")
        if int(match.group("pc"), 16) != pc:
            raise TerminalEvidenceError(f"{case.case_id}: FENTRY slot PC mismatch")
        if match.group("reg") != decoded["registers"][index]:
            raise TerminalEvidenceError(f"{case.case_id}: FENTRY slot register/order mismatch")
        if addr != expected_addr:
            raise TerminalEvidenceError(f"{case.case_id}: FENTRY slot address mismatch")
        if addr in seen_addresses:
            raise TerminalEvidenceError(f"{case.case_id}: duplicate FENTRY slot address")
        seen_addresses.add(addr)
        if mmu_readback != value:
            raise TerminalEvidenceError(f"{case.case_id}: FENTRY slot MMU readback mismatch")
        if debug_read_ok != 1 or debug_readback != value:
            raise TerminalEvidenceError(f"{case.case_id}: FENTRY slot debug readback mismatch")
        if match.group("host") == "(nil)" and host_readback != 0:
            raise TerminalEvidenceError(f"{case.case_id}: nil-host FENTRY slot readback must be zero")
        if match.group("host") != "(nil)" and host_readback != value:
            raise TerminalEvidenceError(f"{case.case_id}: FENTRY slot host readback mismatch")
        slots.append(
            {
                "index": index,
                "case_id": case.case_id,
                "instruction_count": instruction_count,
                "pc": pc,
                "pre_sp": old_sp,
                "register": match.group("reg"),
                "address": addr,
                "value": value,
                "memory_effect": {
                    "mmu": int(match.group("mmu")),
                    "mmu_readback": mmu_readback,
                    "host": match.group("host"),
                    "host_readback": host_readback,
                    "debug_read_ok": True,
                    "debug_readback": debug_readback,
                },
            }
        )
    return slots


def _parse_fentry_evidence(text: str, case: Case, env_value: str | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fentry_trace = _parse_fentry_trace_evidence(text, case, env_value)
    return fentry_trace, _parse_fentry_slot_evidence(text, case, fentry_trace)


def _parse_fret_ra_evidence(text: str, case: Case, env_value: str | None) -> dict[str, Any]:
    pre_matches = list(FRET_RA_PRE_MARKER_RE.finditer(text))
    restored_matches = list(FRET_RA_RESTORED_MARKER_RE.finditer(text))
    if len(pre_matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one pre-restore marker")
    if len(restored_matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one restored-target marker")
    if int(pre_matches[0].group("case")) != case.case_number:
        raise TerminalEvidenceError(f"{case.case_id}: pre-restore marker case mismatch")
    if int(restored_matches[0].group("case")) != case.case_number:
        raise TerminalEvidenceError(f"{case.case_id}: restored-target marker case mismatch")
    if pre_matches[0].start() > restored_matches[0].start():
        raise TerminalEvidenceError(f"{case.case_id}: restored target reached before pre-restore target")
    terminal_matches = list(TOKEN_RE.finditer(text))
    if len(terminal_matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: terminal record missing for FRET.RA evidence")
    if restored_matches[0].start() > terminal_matches[0].start():
        raise TerminalEvidenceError(f"{case.case_id}: terminal appeared before restored-target check")
    return {
        "case_id": case.case_id,
        "raw_fret_ra_word": RAW_GUEST_ENCODINGS[case.case_id]["fret_ra_word"],
        "env": {"LINX_CALLFRAME_SIZE": env_value},
        "pre_ra_symbol": "fret_ra_pre_restore_target",
        "slot0_symbol": "fret_ra_restored_target",
        "distinct_pre_ra_and_slot0": True,
        "sp_delta": 16,
        "reached_marker": FRET_RA_PRE_MARKER,
        "post_ra_check": "explicit_ret_reached_restored_target",
        "restored_marker": FRET_RA_RESTORED_MARKER,
        "terminal_after_restored_marker": True,
    }


def _parse_fret_stk_evidence(
    text: str,
    case: Case,
    config: dict[str, Any],
) -> dict[str, Any]:
    trace_lines = [line for line in text.splitlines() if line.startswith(FRET_STK_TRACE_PREFIX)]
    slot_lines = [line for line in text.splitlines() if line.startswith(FRET_STK_SLOT_PREFIX)]
    publish_lines = [line for line in text.splitlines() if line.startswith(FRET_STK_PUBLISH_PREFIX)]
    marker_matches = list(FRET_STK_RETAINED_MARKER_RE.finditer(text))
    terminal_matches = list(TOKEN_RE.finditer(text))
    if len(trace_lines) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one FRET.STK pre-commit row")
    if len(slot_lines) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one FRET.STK slot row")
    if len(publish_lines) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one FRET.STK publish row")
    if len(marker_matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: expected exactly one retained-target marker")
    if len(terminal_matches) != 1:
        raise TerminalEvidenceError(f"{case.case_id}: terminal record missing for FRET.STK evidence")
    if int(marker_matches[0].group("case")) != case.case_number:
        raise TerminalEvidenceError(f"{case.case_id}: retained-target marker case mismatch")
    if marker_matches[0].start() > terminal_matches[0].start():
        raise TerminalEvidenceError(f"{case.case_id}: terminal appeared before retained-target marker")

    trace = _parse_trace_kv_line(trace_lines[0], FRET_STK_TRACE_PREFIX)
    slot = _parse_trace_kv_line(slot_lines[0], FRET_STK_SLOT_PREFIX)
    publish = _parse_trace_kv_line(publish_lines[0], FRET_STK_PUBLISH_PREFIX)
    _require_fields(
        trace,
        (
            "count", "pc", "next_pc", "old_sp", "new_sp", "stacksize",
            "callframe", "restore_base", "begin", "end", "restore_count",
            "restore_host_loads", "restore_fallback_loads", "host_verify_loads",
            "executed_restore_loads", "physical_restore_reads", "slot0_addr",
            "slot0_value", "slot0_loads", "slot0_physical_reads",
            "slot0_physical_reads_proven", "retained_target", "incoming_ra",
            "restored_ra",
        ),
        label=case.case_id,
    )
    _require_fields(slot, ("count", "pc", "reg", "addr", "value"), label=case.case_id)
    _require_fields(
        publish,
        (
            "count", "pc", "slot0_addr", "slot0_value", "slot0_loads",
            "additional_slot0_loads", "slot0_physical_reads",
            "slot0_physical_reads_proven", "additional_slot0_physical_reads",
            "executed_restore_loads", "host_verify_loads", "retained_target",
            "committed_r10", "published_target",
        ),
        label=case.case_id,
    )
    count = _int_field(trace, "count")
    pc = _int_field(trace, "pc")
    old_sp = _int_field(trace, "old_sp")
    new_sp = _int_field(trace, "new_sp")
    stacksize = _int_field(trace, "stacksize")
    slot0_addr = _int_field(trace, "slot0_addr")
    slot0_value = _int_field(trace, "slot0_value")
    retained_target = _int_field(trace, "retained_target")
    restored_ra = _int_field(trace, "restored_ra")
    expected = config["expected"]
    trace_ints = {
        "restore_count": _int_field(trace, "restore_count"),
        "restore_host_loads": _int_field(trace, "restore_host_loads"),
        "restore_fallback_loads": _int_field(trace, "restore_fallback_loads"),
        "host_verify_loads": _int_field(trace, "host_verify_loads"),
        "executed_restore_loads": _int_field(trace, "executed_restore_loads"),
        "physical_restore_reads": _int_field(trace, "physical_restore_reads"),
        "slot0_loads": _int_field(trace, "slot0_loads"),
        "slot0_physical_reads": _int_field(trace, "slot0_physical_reads"),
        "slot0_physical_reads_proven": _int_field(trace, "slot0_physical_reads_proven"),
    }
    if trace["begin"] != "ra" or trace["end"] != "ra":
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK begin/end must be ra")
    if stacksize != 16 or _int_field(trace, "callframe") != 0 or _int_field(trace, "restore_base") != 0:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK frame fields mismatch")
    if new_sp != ((old_sp + 16) & U64_MASK):
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK SP delta mismatch")
    if _int_field(trace, "next_pc") != ((pc + 4) & U64_MASK):
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK next PC mismatch")
    if slot0_addr != ((new_sp - 8) & U64_MASK):
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK slot0 address mismatch")
    if retained_target != slot0_value or restored_ra != slot0_value:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK retained/restored target mismatch")
    if _int_field(slot, "count") != count or _int_field(slot, "pc") != pc:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK slot row key mismatch")
    if slot["reg"] != "ra":
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK slot register mismatch")
    if _int_field(slot, "addr") != slot0_addr or _int_field(slot, "value") != slot0_value:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK slot address/value mismatch")
    if _int_field(publish, "count") != count or _int_field(publish, "pc") != pc:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK publish row key mismatch")
    for field in (
        "slot0_addr", "slot0_value", "slot0_loads", "slot0_physical_reads",
        "slot0_physical_reads_proven", "executed_restore_loads",
        "host_verify_loads", "retained_target",
    ):
        if _int_field(publish, field) != (slot0_addr if field == "slot0_addr" else slot0_value if field == "slot0_value" else retained_target if field == "retained_target" else trace_ints[field]):
            raise TerminalEvidenceError(f"{case.case_id}: FRET.STK publish {field} mismatch")
    if _int_field(publish, "additional_slot0_loads") != 0:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK additional logical slot0 read")
    if _int_field(publish, "additional_slot0_physical_reads") != 0:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK additional physical slot0 read")
    if _int_field(publish, "committed_r10") != slot0_value:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK committed R10 mismatch")
    if _int_field(publish, "published_target") != slot0_value:
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK published target mismatch")
    for field, value in expected.items():
        if field in {"status", "product_blocker"}:
            continue
        if trace_ints.get(field) != value:
            raise TerminalEvidenceError(f"{case.case_id}: FRET.STK {field} mismatch for {config['label']}")
    product_blocker = None
    if trace_ints["physical_restore_reads"] == 2 or trace_ints["slot0_physical_reads_proven"] == 0:
        product_blocker = "fret_stk_host_verify_double_read"
    if product_blocker != expected.get("product_blocker"):
        raise TerminalEvidenceError(f"{case.case_id}: FRET.STK product blocker mismatch for {config['label']}")
    return {
        "case_id": case.case_id,
        "raw_fentry_word": RAW_GUEST_ENCODINGS[case.case_id]["fentry_word"],
        "raw_fret_stk_word": RAW_GUEST_ENCODINGS[case.case_id]["fret_stk_word"],
        "configuration": {
            "label": config["label"],
            "env": copy.deepcopy(config["env"]),
        },
        "instruction_count": count,
        "pc": pc,
        "next_pc": _int_field(trace, "next_pc"),
        "old_sp": old_sp,
        "new_sp": new_sp,
        "sp_delta": (new_sp - old_sp) & U64_MASK,
        "stacksize": stacksize,
        "restore_base": _int_field(trace, "restore_base"),
        "begin": trace["begin"],
        "end": trace["end"],
        "restore_count": trace_ints["restore_count"],
        "restore_host_loads": trace_ints["restore_host_loads"],
        "restore_fallback_loads": trace_ints["restore_fallback_loads"],
        "host_verify_loads": trace_ints["host_verify_loads"],
        "executed_restore_loads": trace_ints["executed_restore_loads"],
        "physical_restore_reads": trace_ints["physical_restore_reads"],
        "slot0_addr": slot0_addr,
        "slot0_value": slot0_value,
        "slot0_loads": trace_ints["slot0_loads"],
        "slot0_physical_reads": trace_ints["slot0_physical_reads"],
        "slot0_physical_reads_proven": bool(trace_ints["slot0_physical_reads_proven"]),
        "additional_slot0_loads": 0,
        "additional_slot0_physical_reads": 0,
        "retained_target": retained_target,
        "restored_ra": restored_ra,
        "committed_r10": _int_field(publish, "committed_r10"),
        "published_target": _int_field(publish, "published_target"),
        "reached_marker": FRET_STK_RETAINED_MARKER,
        "terminal_after_marker": True,
        "status": expected["status"],
        **({"product_blocker": product_blocker} if product_blocker else {}),
    }


def _fentry_invariance_observation(dynamic_observations: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    for item in dynamic_observations:
        if item["id"] not in FENTRY_DYNAMIC_CASES:
            continue
        case = _case_by_id()[item["id"]]
        runs = item.get("runs", [])
        records.append(
            {
                "case_id": case.case_id,
                "raw_fentry_word": RAW_GUEST_ENCODINGS[case.case_id]["fentry_word"],
                "runs": [copy.deepcopy(run.get("fentry_trace")) for run in runs],
            }
        )
    return {
        "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
        "record_kind": "encoded_f_environment_invariance",
        "records": records,
    }


def _high_end_slot_observation(dynamic_observations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
        "record_kind": "high_end_slot_addresses",
        "records": [
            {
                "case_id": item.get("id"),
                "raw_fentry_word": RAW_GUEST_ENCODINGS[item["id"]]["fentry_word"],
                "runs": [
                    {
                        "environment": copy.deepcopy(run.get("env")),
                        "qemu_log": run.get("qemu_log"),
                        "qemu_log_sha256": run.get("qemu_log_sha256"),
                        "pre_sp": run.get("fentry_trace", {}).get("old_sp"),
                        "slots": copy.deepcopy(run.get("fentry_slots")),
                    }
                    for run in item.get("runs", [])
                    if isinstance(run, dict)
                ],
            }
            for item in dynamic_observations
            if isinstance(item, dict) and item.get("id") in FENTRY_DYNAMIC_CASES
        ],
    }


def _fret_ra_observation(dynamic_observations: list[dict[str, Any]]) -> dict[str, Any]:
    for item in dynamic_observations:
        if item.get("id") == FRET_RA_CASE_ID:
            return {
                "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
                "record_kind": FRET_RA_CASE_ID,
                "runs": [
                    {
                        "environment": copy.deepcopy(run.get("env")),
                        "qemu_log": run.get("qemu_log"),
                        "qemu_log_sha256": run.get("qemu_log_sha256"),
                        "fret_ra": copy.deepcopy(run.get("fret_ra")),
                    }
                    for run in item.get("runs", [])
                    if isinstance(run, dict)
                ],
            }
    return {
        "schema": "linx.qemu.frame_template_semantics.semantic_record.v2",
        "record_kind": FRET_RA_CASE_ID,
        "runs": [],
    }


def _terminal_evidence_complete(text: str, case: Case) -> bool:
    try:
        _parse_terminal_evidence(text, case)
    except TerminalEvidenceError:
        return False
    return True


def _manifest_dict() -> list[dict[str, Any]]:
    return [
        {
            "id": case.case_id,
            "kind": case.kind,
            "requirement": case.requirement,
            **({"case_number": case.case_number} if case.case_number is not None else {}),
            **(
                {"raw_encoding": copy.deepcopy(RAW_GUEST_ENCODINGS[case.case_id])}
                if case.kind == "dynamic"
                else {}
            ),
            **(
                {"expected_observation": copy.deepcopy(EXPECTED_SEMANTIC_OBSERVATIONS[case.case_id])}
                if case.kind == "required-red"
                else {}
            ),
            **({"current_blocker": case.current_blocker} if case.current_blocker is not None else {}),
        }
        for case in MANIFEST
    ]


def _compile_case(*, clang: Path, lld: Path, target: str, out_dir: Path, case: Case) -> tuple[Path | None, dict[str, Any]]:
    assert case.case_number is not None
    case_dir = out_dir / case.case_id
    case_dir.mkdir(parents=True, exist_ok=True)
    obj = case_dir / f"{case.case_id}.o"
    kernel = case_dir / f"{case.case_id}.kernel.o"
    compile_log = case_dir / "compile.log"
    commands = [
        [
            str(clang),
            "-target",
            target,
            "-O2",
            "-ffreestanding",
            "-fno-builtin",
            "-fno-stack-protector",
            "-fno-asynchronous-unwind-tables",
            "-fno-unwind-tables",
            "-fno-exceptions",
            "-fno-jump-tables",
            "-nostdlib",
            f"-DCASE={case.case_number}",
            "-c",
            str(SRC),
            "-o",
            str(obj),
        ],
        [str(lld), "-r", "-o", str(kernel), str(obj)],
    ]
    with compile_log.open("w", encoding="utf-8") as stream:
        for cmd in commands:
            stream.write("+ " + shlex.join(cmd) + "\n")
            proc = _run(cmd, stdout=stream, stderr=subprocess.STDOUT)
            if proc.returncode != 0:
                return None, {
                    "status": "compile-fail",
                    "compile_log": str(compile_log),
                    "compile_log_sha256": _sha256(compile_log),
                    "command": cmd,
                    "returncode": proc.returncode,
                }
    return kernel, {
        "status": "compiled",
        "compile_log": str(compile_log),
        "compile_log_sha256": _sha256(compile_log),
        "kernel": str(kernel),
        "kernel_sha256": _sha256(kernel),
    }


def _terminate_after_evidence(proc: subprocess.Popen[bytes], *, grace_seconds: float) -> dict[str, Any]:
    already_exited = proc.poll()
    if already_exited is not None:
        return {
            "status": "exited_after_terminal",
            "requested": False,
            "returncode": already_exited,
        }
    proc.terminate()
    try:
        proc.wait(timeout=grace_seconds)
        return {
            "status": "controlled",
            "requested": True,
            "returncode": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=grace_seconds)
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "requested": True,
                "returncode": proc.returncode,
            }
        return {
            "status": "forced",
            "requested": True,
            "returncode": proc.returncode,
        }


def _stream_qemu_until_terminal(
    cmd: list[str],
    *,
    env: dict[str, str],
    timeout: float,
    case: Case,
) -> tuple[bytes, dict[str, Any]]:
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert proc.stdout is not None
    os.set_blocking(proc.stdout.fileno(), False)
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    chunks: list[bytes] = []
    terminal_observed = False
    timed_out = False
    premature_exit = False
    termination = {
        "status": "not_attempted",
        "requested": False,
        "returncode": None,
    }
    try:
        while True:
            text = b"".join(chunks).decode("utf-8", errors="replace")
            if _terminal_evidence_complete(text, case):
                terminal_observed = True
                termination = _terminate_after_evidence(proc, grace_seconds=1.0)
                break
            if proc.poll() is not None:
                remaining = proc.stdout.read()
                if remaining:
                    chunks.append(remaining)
                    text = b"".join(chunks).decode("utf-8", errors="replace")
                    if _terminal_evidence_complete(text, case):
                        terminal_observed = True
                        termination = _terminate_after_evidence(proc, grace_seconds=1.0)
                        break
                premature_exit = True
                termination = {
                    "status": "premature_exit",
                    "requested": False,
                    "returncode": proc.returncode,
                }
                break
            remaining_seconds = deadline - time.monotonic()
            if remaining_seconds <= 0:
                timed_out = True
                termination = _terminate_after_evidence(proc, grace_seconds=1.0)
                if termination["status"] == "exited_after_terminal":
                    termination["status"] = "timeout_before_terminal"
                break
            events = selector.select(timeout=min(0.05, remaining_seconds))
            for key, _ in events:
                chunk = key.fileobj.read()
                if chunk:
                    chunks.append(chunk)
        try:
            tail = proc.stdout.read()
        except BlockingIOError:
            tail = None
        if tail:
            chunks.append(tail)
    finally:
        selector.close()
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=1.0)
    return b"".join(chunks), {
        "terminal_observed": terminal_observed,
        "timed_out": timed_out,
        "premature_exit": premature_exit,
        "termination": termination,
        "returncode": proc.returncode,
    }


def _run_case(
    *,
    qemu: Path,
    out_dir: Path,
    case: Case,
    kernel: Path,
    env_value: str | None,
    timeout: float,
    fret_stk_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    label = fret_stk_config["label"] if fret_stk_config else ("env_unset" if env_value is None else f"env_{env_value}")
    qemu_log = out_dir / case.case_id / f"qemu-{label}.log"
    terminal_trace = out_dir / case.case_id / f"terminal-{label}.log"
    env = os.environ.copy()
    env["LINX_VIRT_TEST_FINISHER"] = "1"
    if fret_stk_config:
        env.pop("LINX_CALLFRAME_SIZE", None)
        env.update(fret_stk_config["env"])
    else:
        env["LINX_FENTRY_TRACE"] = "1"
        if env_value is None:
            env.pop("LINX_CALLFRAME_SIZE", None)
        else:
            env["LINX_CALLFRAME_SIZE"] = env_value
    cmd = [
        str(qemu),
        "-machine",
        "virt",
        "-kernel",
        str(kernel),
        "-nographic",
        "-monitor",
        "none",
        "-no-reboot",
        "-bios",
        "none",
        "-trace",
        "linx_virt_exit_write",
        "-d",
        "guest_errors",
    ]
    output, lifecycle = _stream_qemu_until_terminal(cmd, env=env, timeout=timeout, case=case)
    timed_out = lifecycle["timed_out"]
    returncode = lifecycle["returncode"]
    qemu_log.write_bytes(output)
    text = output.decode("utf-8", errors="replace")
    generic_fault = any(
        needle in text
        for needle in (
            "invalid branch target",
            "branch target violation",
            "block fault @",
            "EBREAK trap imm=",
            "decode32 failed",
        )
    )
    terminal: dict[str, Any] | None = None
    fentry_trace: dict[str, Any] | None = None
    fentry_slots: list[dict[str, Any]] | None = None
    fret_ra: dict[str, Any] | None = None
    fret_stk: dict[str, Any] | None = None
    terminal_error = None
    if text:
        try:
            terminal = _parse_terminal_evidence(text, case)
            if case.case_id == FRET_RA_CASE_ID:
                fret_ra = _parse_fret_ra_evidence(text, case, env_value)
            elif case.case_id == FRET_STK_CASE_ID:
                assert fret_stk_config is not None
                fret_stk = _parse_fret_stk_evidence(text, case, fret_stk_config)
            else:
                fentry_trace, fentry_slots = _parse_fentry_evidence(text, case, env_value)
        except TerminalEvidenceError as exc:
            terminal_error = str(exc)
    else:
        terminal_error = f"{case.case_id}: empty qemu output is not terminal evidence"
    terminal_trace.write_text(
        "\n".join(
            line
            for line in text.splitlines()
            if (
                line.startswith("LINX_FRAME_TEMPLATE ")
                or line.startswith("LINX_FENTRY_TRACE ")
                or line.startswith("LINX_FENTRY_SLOT ")
                or line.startswith("LINX_FRET_RA_PRE_TARGET ")
                or line.startswith("LINX_FRET_RA_RESTORED_TARGET ")
                or line.startswith("LINX_FRET_STK_TRACE ")
                or line.startswith("LINX_FRET_STK_SLOT ")
                or line.startswith("LINX_FRET_STK_PUBLISH ")
                or line.startswith("LINX_FRET_STK_RETAINED_TARGET ")
                or "linx_virt_exit_write value=" in line
            )
        )
        + "\n",
        encoding="utf-8",
    )
    termination_status = lifecycle["termination"]["status"]
    status = (
        "pass"
        if (
            terminal
            and ((fentry_trace and fentry_slots) or fret_ra or fret_stk)
            and lifecycle["terminal_observed"]
            and not timed_out
            and not lifecycle["premature_exit"]
            and termination_status in {"controlled", "exited_after_terminal"}
            and not generic_fault
        )
        else "fail"
    )
    if timed_out:
        status = "timeout"
    run_obs: dict[str, Any] = {
        "env": (
            {"LINX_CALLFRAME_SIZE": env_value}
            if fret_stk_config is None
            else copy.deepcopy(fret_stk_config["env"])
        ),
        **({"configuration": fret_stk_config["label"]} if fret_stk_config else {}),
        "status": status,
        "returncode": returncode,
        "timed_out": timed_out,
        "terminal_observed": lifecycle["terminal_observed"],
        "premature_exit": lifecycle["premature_exit"],
        "collector_termination": lifecycle["termination"],
        "generic_fault_seen": generic_fault,
        "qemu_log": str(qemu_log),
        "qemu_log_sha256": _sha256(qemu_log),
        "terminal_trace": str(terminal_trace),
        "terminal_trace_sha256": _sha256(terminal_trace),
    }
    if terminal is not None:
        run_obs["terminal"] = terminal
    if fentry_trace is not None:
        run_obs["fentry_trace"] = fentry_trace
    if fentry_slots is not None:
        run_obs["fentry_slots"] = fentry_slots
    if fret_ra is not None:
        run_obs["fret_ra"] = fret_ra
    if fret_stk is not None:
        run_obs["fret_stk"] = fret_stk
        run_obs["status"] = fret_stk["status"]
        if "product_blocker" in fret_stk:
            run_obs["product_blocker"] = fret_stk["product_blocker"]
    if terminal_error is not None:
        run_obs["terminal_error"] = terminal_error
    return run_obs


def _artifact_errors(path_value: Any, hash_value: Any, label: str) -> list[str]:
    if not isinstance(path_value, str) or not path_value:
        return [f"{label}: artifact path missing"]
    if not _valid_sha256(hash_value):
        return [f"{label}: artifact hash missing"]
    path = Path(path_value)
    if not path.exists():
        return [f"{label}: artifact does not exist: {path}"]
    actual = _sha256(path)
    if actual != hash_value:
        return [f"{label}: artifact digest mismatch: {path}"]
    return []


def _validate_dynamic_observation(
    item: dict[str, Any],
    case: Case,
    seen_artifacts: set[str],
    *,
    mode: str,
) -> list[str]:
    errors: list[str] = []
    item_id = item.get("id")
    if item.get("kind") != "dynamic":
        errors.append(f"{item_id}: dynamic observation kind mismatch")
    compile_obs = item.get("compile")
    if not isinstance(compile_obs, dict):
        errors.append(f"{item_id}: compile observation missing")
    else:
        if compile_obs.get("status") != "compiled":
            errors.append(f"{item_id}: compile status must be compiled")
        errors.extend(_artifact_errors(compile_obs.get("compile_log"), compile_obs.get("compile_log_sha256"), f"{item_id}: compile log"))
        errors.extend(_artifact_errors(compile_obs.get("kernel"), compile_obs.get("kernel_sha256"), f"{item_id}: kernel"))
    runs = item.get("runs")
    if case.case_id == FRET_STK_CASE_ID:
        expected_env_values: list[Any] = [config["env"] for config in FRET_STK_DYNAMIC_CONFIGS]
        expected_run_count = len(FRET_STK_DYNAMIC_CONFIGS)
    else:
        expected_env_values = [{"LINX_CALLFRAME_SIZE": value} for value in EXPECTED_DYNAMIC_ENVS]
        expected_run_count = len(EXPECTED_DYNAMIC_ENVS)
    if not isinstance(runs, list) or len(runs) != expected_run_count:
        return errors + [f"{item_id}: must include exact dynamic run matrix"]
    env_values = [run.get("env") if isinstance(run, dict) else object() for run in runs]
    if env_values != expected_env_values:
        errors.append(f"{item_id}: environment values must match exact dynamic matrix")
    fentry_tuples: list[tuple[Any, ...]] = []
    for run_index, run in enumerate(runs):
        if not isinstance(run, dict):
            errors.append(f"{item_id}: run entry must be an object")
            continue
        label = f"{item_id}: run {run.get('env')}"
        if run.get("timed_out"):
            errors.append(f"{label}: timeout is not evidence")
        if not run.get("terminal_observed"):
            errors.append(f"{label}: observed terminal state missing")
        if run.get("premature_exit"):
            errors.append(f"{label}: process exited before terminal evidence")
        termination = run.get("collector_termination")
        if not isinstance(termination, dict):
            errors.append(f"{label}: collector termination record missing")
        elif termination.get("status") not in {"controlled", "exited_after_terminal"}:
            errors.append(f"{label}: collector termination did not complete after evidence")
        if run.get("generic_fault_seen"):
            errors.append(f"{label}: generic fault is not conformance")
        expected_fret_stk_config = (
            FRET_STK_DYNAMIC_CONFIGS[run_index]
            if case.case_id == FRET_STK_CASE_ID
            else None
        )
        expected_status = (
            expected_fret_stk_config["expected"]["status"]
            if expected_fret_stk_config
            else "pass"
        )
        if run.get("status") != expected_status:
            errors.append(f"{label}: run status must be {expected_status}")
        qemu_log = run.get("qemu_log")
        trace_log = run.get("terminal_trace")
        errors.extend(_artifact_errors(qemu_log, run.get("qemu_log_sha256"), f"{label}: qemu log"))
        errors.extend(_artifact_errors(trace_log, run.get("terminal_trace_sha256"), f"{label}: terminal trace"))
        for artifact in (qemu_log, trace_log):
            if isinstance(artifact, str):
                if artifact in seen_artifacts:
                    errors.append(f"{label}: duplicate artifact path: {artifact}")
                seen_artifacts.add(artifact)
        terminal = run.get("terminal")
        fentry_trace = run.get("fentry_trace")
        fentry_slots = run.get("fentry_slots")
        fret_ra = run.get("fret_ra")
        fret_stk = run.get("fret_stk")
        if not isinstance(terminal, dict):
            errors.append(f"{label}: terminal evidence missing")
        else:
            expected_terminal = {
                "case_id": case.case_id,
                "case_number": case.case_number,
                "token": _terminal_token(case),
                "terminal_pass_low8": True,
                "terminal_case_id": case.case_number,
                "finisher_addr": FINISHER_ADDR,
                "finisher_value": PASS_VALUE,
                "qemu_trace_event": "linx_virt_exit_write",
            }
            if terminal != expected_terminal:
                errors.append(f"{label}: terminal record mismatch")
        if case.case_id == FRET_RA_CASE_ID:
            expected_fret_ra = {
                "case_id": case.case_id,
                "raw_fret_ra_word": RAW_GUEST_ENCODINGS[case.case_id]["fret_ra_word"],
                "env": {"LINX_CALLFRAME_SIZE": run.get("env", {}).get("LINX_CALLFRAME_SIZE")},
                "pre_ra_symbol": "fret_ra_pre_restore_target",
                "slot0_symbol": "fret_ra_restored_target",
                "distinct_pre_ra_and_slot0": True,
                "sp_delta": 16,
                "reached_marker": FRET_RA_PRE_MARKER,
                "post_ra_check": "explicit_ret_reached_restored_target",
                "restored_marker": FRET_RA_RESTORED_MARKER,
                "terminal_after_restored_marker": True,
            }
            if fret_ra != expected_fret_ra:
                errors.append(f"{label}: FRET.RA evidence mismatch")
            if fentry_trace is not None or fentry_slots is not None:
                errors.append(f"{label}: FRET.RA case must not report FENTRY slot evidence")
            if isinstance(qemu_log, str) and Path(qemu_log).exists():
                try:
                    qemu_text = Path(qemu_log).read_text(encoding="utf-8", errors="replace")
                    parsed = _parse_terminal_evidence(qemu_text, case)
                    if parsed != terminal:
                        errors.append(f"{label}: terminal case id mismatch in qemu log")
                    parsed_fret_ra = _parse_fret_ra_evidence(
                        qemu_text,
                        case,
                        run.get("env", {}).get("LINX_CALLFRAME_SIZE"),
                    )
                    if parsed_fret_ra != fret_ra:
                        errors.append(f"{label}: FRET.RA trace mismatch in qemu log")
                except TerminalEvidenceError as exc:
                    errors.append(f"{label}: {exc}")
            continue
        if case.case_id == FRET_STK_CASE_ID:
            if run.get("configuration") != expected_fret_stk_config["label"]:
                errors.append(f"{label}: FRET.STK configuration label mismatch")
            if fentry_trace is not None or fentry_slots is not None or fret_ra is not None:
                errors.append(f"{label}: FRET.STK case must not report FENTRY/FRET.RA evidence")
            if not isinstance(fret_stk, dict):
                errors.append(f"{label}: FRET.STK evidence missing")
            elif isinstance(qemu_log, str) and Path(qemu_log).exists():
                try:
                    qemu_text = Path(qemu_log).read_text(encoding="utf-8", errors="replace")
                    parsed = _parse_terminal_evidence(qemu_text, case)
                    if parsed != terminal:
                        errors.append(f"{label}: terminal case id mismatch in qemu log")
                    parsed_fret_stk = _parse_fret_stk_evidence(
                        qemu_text,
                        case,
                        expected_fret_stk_config,
                    )
                    if parsed_fret_stk != fret_stk:
                        errors.append(f"{label}: FRET.STK trace mismatch in qemu log")
                except TerminalEvidenceError as exc:
                    errors.append(f"{label}: {exc}")
            if isinstance(fret_stk, dict):
                expected_blocker = expected_fret_stk_config["expected"].get("product_blocker")
                if fret_stk.get("status") != expected_status:
                    errors.append(f"{label}: FRET.STK evidence status mismatch")
                if fret_stk.get("product_blocker") != expected_blocker:
                    errors.append(f"{label}: FRET.STK product blocker mismatch")
                for key, value in expected_fret_stk_config["expected"].items():
                    if key in {"status", "product_blocker"}:
                        continue
                    observed_value = fret_stk.get(key)
                    if key == "slot0_physical_reads_proven":
                        observed_value = int(bool(observed_value))
                    if observed_value != value:
                        errors.append(f"{label}: FRET.STK {key} mismatch")
                slot0_value = fret_stk.get("slot0_value")
                for key in ("retained_target", "restored_ra", "committed_r10", "published_target"):
                    if fret_stk.get(key) != slot0_value:
                        errors.append(f"{label}: FRET.STK {key} must equal slot0 value")
                if fret_stk.get("sp_delta") != 16:
                    errors.append(f"{label}: FRET.STK SP delta mismatch")
                if fret_stk.get("reached_marker") != FRET_STK_RETAINED_MARKER:
                    errors.append(f"{label}: FRET.STK retained marker missing")
                if fret_stk.get("terminal_after_marker") is not True:
                    errors.append(f"{label}: FRET.STK terminal must follow marker")
            continue
        if not isinstance(fentry_trace, dict):
            errors.append(f"{label}: FENTRY trace evidence missing")
        else:
            expected_env_value = run.get("env", {}).get("LINX_CALLFRAME_SIZE")
            decoded = _case_fentry_decode(case)
            if fentry_trace.get("case_id") != case.case_id:
                errors.append(f"{label}: FENTRY trace case id mismatch")
            if fentry_trace.get("raw_fentry_word") != decoded["raw_fentry_word"]:
                errors.append(f"{label}: FENTRY raw instruction mismatch")
            if fentry_trace.get("env") != {"LINX_CALLFRAME_SIZE": expected_env_value}:
                errors.append(f"{label}: FENTRY environment binding mismatch")
            for field in (
                "instruction_count", "pc", "next_pc", "old_sp", "new_sp",
                "stacksize", "delta", "callframe", "begin_index", "end_index",
                "save_count", "legal_min_frame",
            ):
                if not isinstance(fentry_trace.get(field), int):
                    errors.append(f"{label}: FENTRY {field} missing")
            for field in (
                "begin_index", "end_index", "begin", "end", "stacksize",
                "save_count", "legal_min_frame",
            ):
                if fentry_trace.get(field) != decoded[field]:
                    errors.append(f"{label}: FENTRY {field} mismatch with raw encoding")
            if fentry_trace.get("callframe") != 0:
                errors.append(f"{label}: FENTRY callframe must be zero")
            old_sp = fentry_trace.get("old_sp")
            new_sp = fentry_trace.get("new_sp")
            stacksize = fentry_trace.get("stacksize")
            if isinstance(old_sp, int) and isinstance(new_sp, int) and isinstance(stacksize, int):
                expected_new_sp = (old_sp - stacksize) & U64_MASK
                if new_sp != expected_new_sp:
                    errors.append(f"{label}: FENTRY SP delta mismatch")
                if fentry_trace.get("delta") != ((old_sp - new_sp) & U64_MASK):
                    errors.append(f"{label}: FENTRY delta field mismatch")
            if stacksize != decoded["stacksize"]:
                errors.append(f"{label}: FENTRY stacksize mismatch")
            fentry_tuples.append(
                (
                    fentry_trace.get("raw_fentry_word"),
                    fentry_trace.get("instruction_count"),
                    fentry_trace.get("pc"),
                    fentry_trace.get("next_pc"),
                    fentry_trace.get("old_sp"),
                    fentry_trace.get("new_sp"),
                    fentry_trace.get("stacksize"),
                    fentry_trace.get("delta"),
                    fentry_trace.get("callframe"),
                    fentry_trace.get("begin_index"),
                    fentry_trace.get("end_index"),
                    fentry_trace.get("begin"),
                    fentry_trace.get("end"),
                    fentry_trace.get("save_count"),
                    fentry_trace.get("legal_min_frame"),
                )
            )
        if not isinstance(fentry_slots, list) or not fentry_slots:
            errors.append(f"{label}: FENTRY slot evidence missing")
        elif len(fentry_slots) != _case_fentry_decode(case)["save_count"]:
            errors.append(f"{label}: FENTRY exact slot count mismatch")
        if isinstance(qemu_log, str) and Path(qemu_log).exists():
            try:
                qemu_text = Path(qemu_log).read_text(encoding="utf-8", errors="replace")
                parsed = _parse_terminal_evidence(qemu_text, case)
                if parsed != terminal:
                    errors.append(f"{label}: terminal case id mismatch in qemu log")
                parsed_fentry, parsed_slots = _parse_fentry_evidence(
                    qemu_text,
                    case,
                    run.get("env", {}).get("LINX_CALLFRAME_SIZE"),
                )
                if parsed_fentry != fentry_trace:
                    errors.append(f"{label}: FENTRY trace mismatch in qemu log")
                if parsed_slots != fentry_slots:
                    errors.append(f"{label}: FENTRY slot trace mismatch in qemu log")
            except TerminalEvidenceError as exc:
                errors.append(f"{label}: {exc}")
    if len(fentry_tuples) == 2 and fentry_tuples[0] != fentry_tuples[1]:
        errors.append(f"{item_id}: FENTRY state tuple must be identical for unset and 64")
    return errors


def _validate_semantic_observation(
    item: dict[str, Any],
    *,
    mode: str,
    dynamic_observations: list[dict[str, Any]],
) -> list[str]:
    item_id = item.get("id")
    expected = EXPECTED_SEMANTIC_OBSERVATIONS.get(item_id)
    if expected is None:
        return [f"{item_id}: unknown semantic observation"]
    if item.get("kind") != "semantic":
        return [f"{item_id}: semantic observation kind mismatch"]
    if item_id == "encoded_f_environment_invariance":
        expected_observed = _fentry_invariance_observation(dynamic_observations)
        if item.get("status") != "pass":
            return [f"{item_id}: encoded-F observation must pass from QEMU trace evidence"]
        if "current_blocker" in item:
            return [f"{item_id}: encoded-F blocker must be removed"]
        if item.get("observed") != expected_observed:
            return [f"{item_id}: encoded-F observed state mismatch"]
        return []
    if item_id == "high_end_slot_addresses":
        expected_observed = _high_end_slot_observation(dynamic_observations)
        if item.get("status") != "pass":
            return [f"{item_id}: high-end slot observation must pass from QEMU slot trace evidence"]
        if "current_blocker" in item:
            return [f"{item_id}: slot-address blocker must be removed"]
        if item.get("observed") != expected_observed:
            return [f"{item_id}: high-end slot observed state mismatch"]
        return []
    if mode == "current-red":
        if item.get("status") != "blocked":
            return [f"{item_id}: current-red semantic rows must be explicitly blocked"]
        if item.get("current_blocker") != _case_by_id()[item_id].current_blocker:
            return [f"{item_id}: semantic blocker mismatch"]
        if item.get("expected_observation") != expected:
            return [f"{item_id}: semantic expected observation mismatch"]
        return []
    if item.get("status") != "pass":
        return [f"{item_id}: future-green semantic status must be pass"]
    if item.get("observed") != expected:
        return [f"{item_id}: semantic observation mismatch"]
    return []


def _validate_report(report: dict[str, Any], *, mode: str) -> list[str]:
    errors: list[str] = []
    if mode not in {"current-red", "future-green"}:
        errors.append(f"unknown mode: {mode}")
    if report.get("schema") != SCHEMA:
        errors.append("schema mismatch")
    if report.get("mode") != mode:
        errors.append("report mode mismatch")
    if report.get("source") != str(SRC):
        errors.append("source path mismatch")
    if report.get("source_sha256") != _sha256(SRC):
        errors.append("source digest mismatch")
    manifest = report.get("manifest")
    if manifest != _manifest_dict():
        errors.append("manifest must match exact expected object")
    observations = report.get("observations")
    if not isinstance(observations, list):
        errors.append("observations missing")
    else:
        observation_keys = [(item.get("id"), item.get("kind")) for item in observations if isinstance(item, dict)]
        expected_keys = [
            (case.case_id, "dynamic")
            for case in MANIFEST
            if case.kind == "dynamic"
        ] + [
            (case.case_id, "semantic")
            for case in MANIFEST
            if case.kind != "dynamic"
        ]
        if observation_keys != expected_keys:
            errors.append("complete dynamic+semantic observation ID set/order mismatch")
        if len(observation_keys) != len(set(observation_keys)):
            errors.append("duplicate observation IDs")
        seen_artifacts: set[str] = set()
        dynamic_observations = [
            item
            for item in observations
            if (
                isinstance(item, dict)
                and item.get("id") in _case_by_id()
                and _case_by_id()[item["id"]].kind == "dynamic"
            )
        ]
        for item in observations:
            if not isinstance(item, dict):
                errors.append("observation entry must be an object")
                continue
            case = _case_by_id().get(item.get("id"))
            if case is None:
                errors.append(f"{item.get('id')}: unknown observation id")
                continue
            if case.kind == "dynamic":
                errors.extend(_validate_dynamic_observation(item, case, seen_artifacts, mode=mode))
            else:
                errors.extend(
                    _validate_semantic_observation(
                        item,
                        mode=mode,
                        dynamic_observations=dynamic_observations,
                    )
                )
    blockers = report.get("current_blockers")
    if not isinstance(blockers, list):
        errors.append("current blockers missing")
    else:
        blocker_ids = [item.get("id") for item in blockers if isinstance(item, dict)]
        if len(blocker_ids) != len(set(blocker_ids)):
            errors.append("duplicate current blocker")
        expected = EXPECTED_CURRENT_BLOCKER_ROWS if mode == "current-red" else []
        if blockers != expected:
            errors.append("current blocker rows must match exact expected object")
    return errors


def _normalize_ingested_report(report: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(report)
    if normalized.get("source") == str(SRC):
        normalized["source_sha256"] = _sha256(SRC)
    normalized["manifest"] = _manifest_dict()
    for item in normalized.get("observations", []):
        if not isinstance(item, dict) or item.get("kind") != "dynamic":
            continue
        case = _case_by_id().get(item.get("id"))
        if case is None:
            continue
        for run in item.get("runs", []):
            if not isinstance(run, dict):
                continue
            qemu_log = run.get("qemu_log")
            if not isinstance(qemu_log, str) or not Path(qemu_log).exists():
                continue
            try:
                text = Path(qemu_log).read_text(encoding="utf-8", errors="replace")
                terminal = _parse_terminal_evidence(text, case)
            except TerminalEvidenceError:
                continue
            run.setdefault("terminal", terminal)
            if case.case_id == FRET_RA_CASE_ID:
                try:
                    fret_ra = _parse_fret_ra_evidence(
                        text,
                        case,
                        run.get("env", {}).get("LINX_CALLFRAME_SIZE"),
                    )
                except TerminalEvidenceError:
                    continue
                run.setdefault("fret_ra", fret_ra)
            elif case.case_id == FRET_STK_CASE_ID:
                config = next(
                    (
                        item
                        for item in FRET_STK_DYNAMIC_CONFIGS
                        if item["label"] == run.get("configuration") or item["env"] == run.get("env")
                    ),
                    None,
                )
                if config is None:
                    continue
                try:
                    fret_stk = _parse_fret_stk_evidence(text, case, config)
                except TerminalEvidenceError:
                    continue
                run.setdefault("configuration", config["label"])
                run.setdefault("env", copy.deepcopy(config["env"]))
                run.setdefault("fret_stk", fret_stk)
                run.setdefault("status", fret_stk["status"])
                if "product_blocker" in fret_stk:
                    run.setdefault("product_blocker", fret_stk["product_blocker"])
            else:
                try:
                    fentry_trace, fentry_slots = _parse_fentry_evidence(
                        text,
                        case,
                        run.get("env", {}).get("LINX_CALLFRAME_SIZE"),
                    )
                except TerminalEvidenceError:
                    continue
                run.setdefault("fentry_trace", fentry_trace)
                run.setdefault("fentry_slots", fentry_slots)
            run.setdefault("terminal_observed", True)
            run.setdefault("timed_out", False)
            run.setdefault("premature_exit", False)
            run.setdefault(
                "collector_termination",
                {
                    "status": "exited_after_terminal",
                    "requested": False,
                    "returncode": run.get("returncode"),
                },
            )
    dynamic_observations = [
        item
        for item in normalized.get("observations", [])
        if isinstance(item, dict)
        and item.get("id") in _case_by_id()
        and _case_by_id()[item["id"]].kind == "dynamic"
    ]
    for item in normalized.get("observations", []):
        if not isinstance(item, dict) or item.get("id") not in {
            "encoded_f_environment_invariance",
            "high_end_slot_addresses",
        }:
            continue
        item["kind"] = "semantic"
        item["status"] = "pass"
        item.pop("current_blocker", None)
        item.pop("expected_observation", None)
        if item.get("id") == "encoded_f_environment_invariance":
            item["observed"] = _fentry_invariance_observation(dynamic_observations)
        else:
            item["observed"] = _high_end_slot_observation(dynamic_observations)
    return normalized


def _semantic_rows_for_current_red(dynamic_observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": "encoded_f_environment_invariance",
            "kind": "semantic",
            "status": "pass",
            "observed": _fentry_invariance_observation(dynamic_observations),
        },
        {
            "id": "high_end_slot_addresses",
            "kind": "semantic",
            "status": "pass",
            "observed": _high_end_slot_observation(dynamic_observations),
        },
        *[
            {
                "id": case.case_id,
                "kind": "semantic",
                "status": "blocked",
                "current_blocker": case.current_blocker,
                "expected_observation": copy.deepcopy(EXPECTED_SEMANTIC_OBSERVATIONS[case.case_id]),
            }
            for case in MANIFEST
            if case.kind == "required-red"
        ],
    ]


def _semantic_rows_for_future_green(dynamic_observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": "encoded_f_environment_invariance",
            "kind": "semantic",
            "status": "pass",
            "observed": _fentry_invariance_observation(dynamic_observations),
        },
        {
            "id": "high_end_slot_addresses",
            "kind": "semantic",
            "status": "pass",
            "observed": _high_end_slot_observation(dynamic_observations),
        },
        *[
            {
                "id": case.case_id,
                "kind": "semantic",
                "status": "pass",
                "observed": copy.deepcopy(EXPECTED_SEMANTIC_OBSERVATIONS[case.case_id]),
                "evidence_class": "contract-expected-future-state",
            }
            for case in MANIFEST
            if case.kind == "required-red"
        ],
    ]


def _load_future_semantics(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("error: --semantic-observations must point to a JSON list")
    return payload


def _write_report(
    out_dir: Path,
    report: dict[str, Any],
    errors: list[str],
    report_out: Path | None = None,
) -> Path:
    report = dict(report)
    report["verdict"] = "pass" if not errors else "fail"
    report["errors"] = errors
    report_path = report_out or out_dir / "frame-template-semantics-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"report: {report_path}")
    print(f"verdict: {report['verdict']}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    return report_path


def _self_test() -> int:
    import test_run_frame_template_semantics
    import unittest

    suite = unittest.defaultTestLoader.loadTestsFromModule(test_run_frame_template_semantics)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        return 1
    print("self-test: PASS")
    return 0


def run(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Verify Linx frame-template QEMU semantics.")
    parser.add_argument("--clang", default=str(_default_clang()))
    parser.add_argument("--lld", default=str(_default_lld()))
    parser.add_argument("--qemu", default=str(_default_qemu()))
    parser.add_argument("--target", default="linx64-linx-none-elf")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--out-dir", default=str(SCRIPT_DIR / "out" / "frame-template-semantics"))
    parser.add_argument("--expect-current-red", action="store_true")
    parser.add_argument("--future-green", action="store_true")
    parser.add_argument("--semantic-observations")
    parser.add_argument("--ingest-report")
    parser.add_argument("--report-out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()
    mode = "future-green" if args.future_green else "current-red"
    if not args.expect_current_red and not args.future_green:
        mode = "future-green"
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_out = Path(args.report_out) if args.report_out else None

    if args.ingest_report:
        report = _normalize_ingested_report(json.loads(Path(args.ingest_report).read_text(encoding="utf-8")))
        errors = _validate_report(report, mode=mode)
        _write_report(out_dir, report, errors, report_out)
        return 1 if errors else 0

    clang = _check_exe(Path(args.clang), "clang")
    lld = _check_exe(Path(args.lld), "ld.lld")
    qemu = _check_exe(Path(args.qemu), "qemu-system-linx64")

    observations: list[dict[str, Any]] = []
    for case in MANIFEST:
        if case.kind != "dynamic":
            continue
        kernel, compile_obs = _compile_case(clang=clang, lld=lld, target=args.target, out_dir=out_dir, case=case)
        obs: dict[str, Any] = {"id": case.case_id, "kind": "dynamic", "compile": compile_obs, "runs": []}
        if kernel is not None:
            if case.case_id == FRET_STK_CASE_ID:
                for config in FRET_STK_DYNAMIC_CONFIGS:
                    obs["runs"].append(
                        _run_case(
                            qemu=qemu,
                            out_dir=out_dir,
                            case=case,
                            kernel=kernel,
                            env_value=None,
                            timeout=args.timeout,
                            fret_stk_config=config,
                        )
                    )
            else:
                for env_value in EXPECTED_DYNAMIC_ENVS:
                    obs["runs"].append(
                        _run_case(
                            qemu=qemu,
                            out_dir=out_dir,
                            case=case,
                            kernel=kernel,
                            env_value=env_value,
                            timeout=args.timeout,
                        )
                    )
        observations.append(obs)

    if mode == "future-green":
        if args.semantic_observations:
            observations.extend(_load_future_semantics(Path(args.semantic_observations)))
        else:
            observations.extend(_semantic_rows_for_future_green(observations))
        current_blockers: list[dict[str, Any]] = []
    else:
        observations.extend(_semantic_rows_for_current_red(observations))
        current_blockers = EXPECTED_CURRENT_BLOCKER_ROWS

    report = {
        "schema": SCHEMA,
        "mode": mode,
        "source": str(SRC),
        "source_sha256": _sha256(SRC),
        "manifest": _manifest_dict(),
        "observations": observations,
        "current_blockers": current_blockers,
    }
    errors = _validate_report(report, mode=mode)
    _write_report(out_dir, report, errors, report_out)
    return 1 if errors else 0


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
