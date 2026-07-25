#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
PTO_KERNEL_ROOT = REPO_ROOT / "workloads" / "pto_kernels" / "kernels"
PTO_KERNEL_CATALOG = PTO_KERNEL_ROOT / "catalog.txt"
LLVM_AVS_ROOT = REPO_ROOT / "avs" / "compiler" / "linx-llvm" / "tests"
LLVM_AVS_DISASM_VECTOR_GEN = LLVM_AVS_ROOT / "gen_disasm_vectors.py"
LLVM_AVS_V057_FORMS = LLVM_AVS_ROOT / "asm" / "41_v057_isa_forms.s"
LLVM_AVS_SPEC = REPO_ROOT / "isa" / "v0.57" / "linxisa-v0.57.json"
DIRECT_BOOT_LINK_SCRIPT = """ENTRY(_start)
PHDRS {
  text PT_LOAD FLAGS(5);
  data PT_LOAD FLAGS(6);
}
SECTIONS {
  . = 0x00010000;
  .text : { *(.text*) } :text
  .rodata : { *(.rodata*) } :text
  . = ALIGN(0x1000);
  .data : { *(.data*) } :data
  .bss (NOLOAD) : { *(.bss*) *(COMMON) } :data
  . = ALIGN(16);
  .bootstack (NOLOAD) : {
    __start_init_stack = .;
    . += 0x4000;
    __end_init_stack = .;
  } :data
}
"""

FINISHER_PASS_LOW8 = 0x55
FINISHER_FAIL_LOW8 = 0x33
FINISHER_RESET_LOW8 = 0x77
SUCCESS_UART_MARKERS = (
    b"REGRESSION PASSED",
    b"TEST SUITE COMPLETE",
    b"LINX TESTS PASS",
)
TERMINAL_TEST_IDS_BY_SUITE = {
    # The final system trap continuation intentionally exits through the
    # finisher instead of returning to tests/main.c.
    "system": 0x0000110D,
}
COMPLETION_TEST_IDS_BY_SUITE = {
    "arithmetic": 0x0000A091,
    "bitwise": 0x0000B0F1,
    "loadstore": 0x0000C140,
    "branch": 0x0000D0E2,
    "move": 0x0000E141,
    "float": 0x0000F0F0,
    "atomic": 0x00007160,
    "jumptable": 0x00008002,
    "varargs": 0x00009004,
    "v057_vector": 0x000012F0,
    "v057_vector_ops": 0x00001320,
    "callret": 0x00001412,
    "runtime": 0x00002110,
    "executable_memory": 0x0000220D,
    "executable_scalar": 0x00002510,
    "executable_integer": 0x0000260F,
    "system": 0x0000110D,
    "deepseek_tilekernels": 0x00001705,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_test_events(output: bytes) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    pattern = re.compile(r"Test\s+0x([0-9a-fA-F]{1,8}):.*?\b(PASS|FAIL)\s*$")
    for line in output.decode("utf-8", errors="replace").splitlines():
        match = pattern.search(line)
        if match is None:
            continue
        test_id = f"0x{int(match.group(1), 16):08x}"
        events.append({"seq": len(events), "kind": "START", "test_id": test_id})
        if match.group(2) == "PASS":
            events.append({"seq": len(events), "kind": "PASS", "test_id": test_id})
        else:
            events.append({"seq": len(events), "kind": "FAIL", "test_id": test_id})
    return events


def _test_events_are_clean_pass(events: list[dict[str, object]]) -> bool:
    if not events or len(events) % 2:
        return False
    for index in range(0, len(events), 2):
        start, terminal = events[index : index + 2]
        if (
            start.get("seq") != index
            or terminal.get("seq") != index + 1
            or start.get("kind") != "START"
            or terminal.get("kind") != "PASS"
            or start.get("test_id") != terminal.get("test_id")
        ):
            return False
    return True


def _runtime_verdict(
    stdout: bytes,
    returncode: int,
    *,
    timed_out: bool = False,
    stalled: bool = False,
    required_test_ids: list[int] | None = None,
    terminal_test_ids: list[int] | None = None,
    suite_completion_test_ids: list[int] | None = None,
) -> dict[str, object]:
    events = _parse_test_events(stdout)
    failure = _parse_failure(stdout)
    observed_ids = {
        int(str(event["test_id"]), 16)
        for event in events
        if event["kind"] == "START"
    }
    missing_ids = sorted(set(required_test_ids or []) - observed_ids)
    missing_suite_ids = sorted(set(suite_completion_test_ids or []) - observed_ids)
    declared_terminal_ids = set(terminal_test_ids or [])
    has_fail_event = any(event["kind"] == "FAIL" for event in events)
    clean_events = not events or _test_events_are_clean_pass(events)
    terminal_event_id = (
        int(str(events[-1]["test_id"]), 16)
        if events and events[-1]["kind"] == "PASS"
        else None
    )
    success_marker = next(
        (marker for marker in SUCCESS_UART_MARKERS if marker in stdout),
        None,
    )

    pass_marker: dict[str, str] | None = None
    if (
        not failure
        and not has_fail_event
        and clean_events
        and not missing_ids
        and not missing_suite_ids
        and not timed_out
        and not stalled
    ):
        if returncode & 0xFF == FINISHER_PASS_LOW8:
            pass_marker = {"kind": "finisher_exit_low8", "value": "0x55"}
        elif returncode == 0 and success_marker is not None:
            pass_marker = {
                "kind": "uart_success_marker",
                "value": success_marker.decode("ascii", errors="replace").strip(),
            }
        elif returncode == 0 and terminal_event_id in declared_terminal_ids:
            pass_marker = {
                "kind": "terminal_test_id",
                "value": f"0x{terminal_event_id:08x}",
            }

    if failure or has_fail_event:
        status, reason = "FAIL", "guest_failure"
    elif timed_out:
        status, reason = "TIMEOUT", "timeout"
    elif stalled:
        status, reason = "STALLED", "no_progress"
    elif missing_ids:
        status, reason = "FAIL", "missing_required_test_ids"
    elif missing_suite_ids:
        status, reason = "FAIL", "missing_suite_completion_test_ids"
    elif pass_marker is not None:
        status, reason = "PASS", "clean_terminal_oracle"
    elif returncode == 0:
        status, reason = "FAIL", "missing_terminal_oracle"
    else:
        status, reason = "FAIL", "nonzero_exit"

    return {
        "status": status,
        "oracle_verdict": "PASS" if status == "PASS" else (
            "FAIL" if failure or has_fail_event or missing_ids or missing_suite_ids else "UNAVAILABLE"
        ),
        "reason": reason,
        "pass_marker": pass_marker,
        "failure": failure,
        "events": events,
        "timed_out": timed_out,
        "stalled": stalled,
        "declared_terminal_test_ids": [
            f"0x{test_id:08x}" for test_id in sorted(declared_terminal_ids)
        ],
        "declared_suite_completion_test_ids": [
            f"0x{test_id:08x}" for test_id in sorted(set(suite_completion_test_ids or []))
        ],
        "missing_required_test_ids": [f"0x{test_id:08x}" for test_id in missing_ids],
        "missing_suite_completion_test_ids": [
            f"0x{test_id:08x}" for test_id in missing_suite_ids
        ],
    }


def _parse_failure(output: bytes) -> dict[str, str] | None:
    text = output.decode("utf-8", errors="replace")
    match = re.search(
        r"Test ID:\s*(0x[0-9a-fA-F]+).*?"
        r"Expected:\s*(0x[0-9a-fA-F]+).*?"
        r"Actual:\s*(0x[0-9a-fA-F]+)",
        text,
        re.DOTALL,
    )
    if match is None:
        return None
    return {
        "test_id": f"0x{int(match.group(1), 16):08x}",
        "expected": f"0x{int(match.group(2), 16):016x}",
        "actual": f"0x{int(match.group(3), 16):016x}",
    }


def _parse_executed_pcs(trace: str) -> list[str]:
    pcs = {
        f"0x{int(match.group(1), 16):016x}"
        for match in re.finditer(r"^\s*0x([0-9a-fA-F]+):", trace, re.MULTILINE)
    }
    return sorted(pcs, key=lambda value: int(value, 16))


_TARGET_PC_WATCH_RE = re.compile(
    r"^linx_pc_watch:\s+pc=0x([0-9a-fA-F]+)\s+"
    r"hit=([0-9]+)\s+printed=([0-9]+)\s+count=([0-9]+)(?:\s|$)"
)


def _parse_target_pc_watch_packets(
    stderr: bytes, requested_pcs: list[int]
) -> list[dict[str, object]]:
    """Extract runtime helper hits, never translation-block listings."""
    requested = set(requested_pcs)
    hits: dict[int, dict[str, object]] = {}
    for line in stderr.decode("utf-8", errors="replace").splitlines():
        match = _TARGET_PC_WATCH_RE.match(line)
        if match is None:
            continue
        pc = int(match.group(1), 16)
        hit = int(match.group(2), 10)
        printed = int(match.group(3), 10)
        count = int(match.group(4), 10)
        if pc not in requested or hit < 1 or printed < 1:
            continue
        hits.setdefault(
            pc,
            {
                "pc": f"0x{pc:016x}",
                "hit": hit,
                "count": count,
                "evidence_kind": "qemu_target_pc_watch_v1",
            },
        )
    return [hits[pc] for pc in sorted(hits)]


def _parse_evidence_pcs(values: list[str]) -> list[int]:
    pcs: list[int] = []
    for value in values:
        try:
            pc = int(value, 0)
        except ValueError as exc:
            raise SystemExit(f"error: invalid --evidence-pc: {value}") from exc
        if pc < 0 or pc > 0xFFFFFFFFFFFFFFFF:
            raise SystemExit(f"error: --evidence-pc must fit uint64: {value}")
        if pc not in pcs:
            pcs.append(pc)
    if len(pcs) > 16:
        raise SystemExit("error: at most 16 --evidence-pc values are supported by QEMU")
    return pcs


def _target_pc_watch_env(pcs: list[int]) -> dict[str, str]:
    if not pcs:
        return {}
    return {
        "LINX_DEBUG_PC_WATCH": ",".join(f"0x{pc:x}" for pc in pcs),
        "LINX_DEBUG_PC_WATCH_HIT_LIMIT": "1",
        "LINX_DEBUG_PC_WATCH_PRINT": "1",
    }


def _configure_target_pc_watch_env(
    env: dict[str, str], pcs: list[int]
) -> dict[str, str]:
    debug_env = _target_pc_watch_env(pcs)
    if not debug_env:
        return debug_env
    for name in list(env):
        if name == "LINX_DEBUG_PC_WATCH" or name.startswith(
            "LINX_DEBUG_PC_WATCH_"
        ):
            env.pop(name)
    env.update(debug_env)
    return debug_env


def _repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(resolved)


def _qemu_source_sha() -> str:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT / "emulator" / "qemu"), "rev-parse", "HEAD"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"error: cannot determine QEMU source SHA: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _qemu_provenance(qemu: Path) -> dict[str, object]:
    source_root = REPO_ROOT / "emulator" / "qemu"
    status = subprocess.run(
        ["git", "-C", str(source_root), "status", "--short", "--untracked-files=no"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    diff = subprocess.run(
        ["git", "-C", str(source_root), "diff", "--binary", "HEAD"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    version = subprocess.run(
        [str(qemu), "--version"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if status.returncode != 0 or diff.returncode != 0 or version.returncode != 0:
        raise SystemExit("error: cannot capture QEMU dirty/version provenance")
    dirty = bool(status.stdout.strip())
    return {
        "version": version.stdout.splitlines()[0] if version.stdout else "unknown",
        "source_dirty": dirty,
        "patch_sha256": hashlib.sha256(diff.stdout).hexdigest() if dirty else None,
    }


def _write_execution_evidence(
    path: Path,
    *,
    selected: list[str],
    objects: list[Path],
    aggregate_object: Path,
    elf: Path,
    qemu: Path,
    completed: subprocess.CompletedProcess[bytes],
    verdict: dict[str, object],
    trace_path: Path,
    evidence_pcs: list[int],
    qemu_debug_env: dict[str, str],
) -> None:
    stdout = completed.stdout or b""
    events = verdict["events"]
    failure = verdict["failure"]
    status = verdict["status"]
    target_packets = _parse_target_pc_watch_packets(
        completed.stderr or b"", evidence_pcs
    )
    trace = (
        trace_path.read_text(encoding="utf-8", errors="replace")
        if trace_path.is_file() and not evidence_pcs
        else ""
    )
    payload = {
        "schema_version": 1,
        "status": status,
        "oracle_verdict": verdict["oracle_verdict"],
        "suites": selected,
        "required_test_ids_observed": sorted(
            {event["test_id"] for event in events if event["kind"] == "START"}
        ),
        "test_events": events,
        "pc_hits": (
            target_packets
            if evidence_pcs
            else [{"pc": pc} for pc in _parse_executed_pcs(trace)]
        ),
        "artifacts": {
            "elf": {"path": _repo_relative(elf), "sha256": _sha256(elf)},
            "object": {
                "path": _repo_relative(aggregate_object),
                "sha256": _sha256(aggregate_object),
            },
            "objects": [
                {"path": _repo_relative(obj), "sha256": _sha256(obj)} for obj in objects
            ],
        },
        "qemu": {
            "path": str(qemu),
            "binary_sha256": _sha256(qemu),
            "sha": _qemu_source_sha(),
            **_qemu_provenance(qemu),
        },
        "run": {
            "exit_code": completed.returncode,
            "timed_out": verdict["timed_out"],
            "stalled": verdict["stalled"],
            "timeout_after_fail": bool(verdict["timed_out"] and failure),
            "pass_marker": verdict["pass_marker"],
            "verdict_reason": verdict["reason"],
            "missing_required_test_ids": verdict["missing_required_test_ids"],
            "missing_suite_completion_test_ids": verdict[
                "missing_suite_completion_test_ids"
            ],
            "declared_terminal_test_ids": verdict["declared_terminal_test_ids"],
            "declared_suite_completion_test_ids": verdict[
                "declared_suite_completion_test_ids"
            ],
            "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        },
        "failure": failure,
    }
    if evidence_pcs:
        payload["pc_evidence"] = {
            "kind": "qemu_target_pc_watch_v1",
            "requested_pcs": [f"0x{pc:016x}" for pc in evidence_pcs],
            "packet_prefix": "linx_pc_watch:",
        }
        payload["qemu_debug_env"] = qemu_debug_env
    path.parent.mkdir(parents=True, exist_ok=True)
    uart_path = path.with_suffix(".uart.log")
    uart_path.write_bytes(stdout)
    payload["artifacts"]["uart"] = {
        "path": _repo_relative(uart_path),
        "sha256": _sha256(uart_path),
    }
    if evidence_pcs:
        pc_watch_path = path.with_suffix(".pc-watch.log")
        pc_watch_path.write_bytes(completed.stderr or b"")
        payload["artifacts"]["pc_watch"] = {
            "path": _repo_relative(pc_watch_path),
            "sha256": _sha256(pc_watch_path),
        }
    elif trace_path.is_file():
        payload["artifacts"]["pc_trace"] = {
            "path": _repo_relative(trace_path),
            "sha256": _sha256(trace_path),
        }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_pto_kernel_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for raw_line in PTO_KERNEL_CATALOG.read_text(encoding="utf-8").splitlines():
        entry = raw_line.strip()
        if not entry or entry.startswith("#"):
            continue
        name = Path(entry).stem
        if name in catalog:
            raise SystemExit(f"error: duplicate PTO kernel name in catalog: {name}")
        catalog[name] = entry
    return catalog


def _pto_kernel_src(name: str) -> str:
    rel_path = _load_pto_kernel_catalog().get(name)
    if rel_path is None:
        raise SystemExit(f"error: missing PTO kernel in catalog: {name}")
    return str(Path("workloads") / "pto_kernels" / "kernels" / rel_path)


PTO_TILE_KERNEL_NAMES = [
    "tload_store",
    "mamulb",
    "tmatmul_acc",
    "gemm",
    "flash_attention",
    "flash_attention_masked",
]

PTO_PARITY_KERNEL_NAMES = [
    "tload_store",
    "mamulb",
    "tmatmul_acc",
    "gemm",
    "gemm_basic",
    "gemm_demo",
    "gemm_performance",
    "add_custom",
    "relu_fp32",
    "sigmoid_fp32",
    "silu_fp32",
    "tanh_fp32",
    "softmax_fp32",
    "flash_attention",
    "flash_attention_demo",
    "flash_attention_masked",
    "fa_performance",
    "mla_attention_demo",
    "flash_attention_cube_fp16",
    "flash_attention_vec_fp32",
    "flash_attention_vec_fp16",
    "gqa_fp16",
    "sparse_attention_local_fp16",
    "rmsnorm_fp16",
    "gelu_fp32",
    "argmax_fp32",
    "gather_fp32",
    "where_fp32",
    "slice_fp32",
    "concat_fp32",
    "flatten_fp32",
    "reshape_fp32",
    "scatter_fp32",
    "squeeze_fp32",
    "unsqueeze_fp32",
    "stack_fp32",
    "split_fp32",
    "permute_nhwc_nchw_fp32",
    "transpose_large_fp32",
    "unsorted_segment_sum_fp32",
    "unique_i32",
]

DEEPSEEK_TILEKERNEL_NAMES = [
    "engram",
    "mhc",
    "moe",
    "quant",
    "transpose",
]


SUITES: dict[str, dict[str, str]] = {
    "arithmetic": {"src": "tests/01_arithmetic.c", "macro": "LINX_TEST_ENABLE_ARITHMETIC"},
    "bitwise": {"src": "tests/02_bitwise.c", "macro": "LINX_TEST_ENABLE_BITWISE"},
    "loadstore": {"src": "tests/03_loadstore.c", "macro": "LINX_TEST_ENABLE_LOADSTORE"},
    "branch": {"src": "tests/04_branch.c", "macro": "LINX_TEST_ENABLE_BRANCH"},
    "move": {"src": "tests/05_move.c", "macro": "LINX_TEST_ENABLE_MOVE"},
    "float": {"src": "tests/06_floating_point.c", "macro": "LINX_TEST_ENABLE_FLOAT"},
    "atomic": {"src": "tests/07_atomic.c", "macro": "LINX_TEST_ENABLE_ATOMIC"},
    "jumptable": {"src": "tests/08_jumptable.c", "macro": "LINX_TEST_ENABLE_JUMPTABLE"},
    "varargs": {"src": "tests/09_varargs.c", "macro": "LINX_TEST_ENABLE_VARARGS"},
    "tile": {"src": "tests/10_tile.cpp", "macro": "LINX_TEST_ENABLE_TILE"},
    "pto_parity": {"src": "tests/16_pto_kernel_parity.cpp", "macro": "LINX_TEST_ENABLE_PTO_PARITY"},
    "deepseek_tilekernels": {
        "src": "tests/17_deepseek_tilekernels.cpp",
        "macro": "LINX_TEST_ENABLE_DEEPSEEK_TILEKERNELS",
    },
    "system": {"src": "tests/11_system.c", "macro": "LINX_TEST_ENABLE_SYSTEM"},
    "v057_vector": {"src": "tests/12_v057_vector_tile.c", "macro": "LINX_TEST_ENABLE_V057_VECTOR"},
    "v057_vector_ops": {
        "src": "tests/13_v057_vector_ops_matrix.c",
        "macro": "LINX_TEST_ENABLE_V057_VECTOR_OPS",
    },
    "v057_vector_body_fault": {
        "src": "tests/18_v057_vector_body_fault.c",
        "macro": "LINX_TEST_ENABLE_V057_VECTOR_BODY_FAULT",
    },
    "translation_corpus": {
        "src": "tests/20_translation_corpus_stub.c",
        "macro": "LINX_TEST_ENABLE_TRANSLATION_CORPUS",
    },
    "simt_autovec": {
        "src": "tests/19_simt_autovec.c",
        "macro": "LINX_TEST_ENABLE_SIMT_AUTOVEC",
    },
    "callret": {"src": "tests/14_callret.c", "macro": "LINX_TEST_ENABLE_CALLRET"},
    "runtime": {"src": "tests/21_freestanding_runtime.c", "macro": "LINX_TEST_ENABLE_RUNTIME"},
    # A dedicated, single-suite executable-coverage carrier.  It deliberately
    # reuses main.c's load/store entry point so the generic runner need not grow
    # a coverage-only dispatch surface.
    "executable_memory": {
        "src": "tests/22_executable_memory.c",
        "macro": "LINX_TEST_ENABLE_LOADSTORE",
    },
    "executable_scalar": {
        "src": "tests/23_executable_scalar.c",
        "macro": "LINX_TEST_ENABLE_ARITHMETIC",
    },
    "executable_integer": {
        "src": "tests/24_executable_integer.c",
        "macro": "LINX_TEST_ENABLE_MOVE",
    },
}

COMPILE_ONLY_SUITE_SOURCE_OVERRIDE: dict[str, str] = {
    # Runtime tile stress currently relies on backend paths that are still
    # unstable for compile-only regression gating; keep a dedicated compile
    # smoke that validates PTO kernel integration.
    "tile": "tests/10_tile_compile_smoke.cpp",
}

def _extra_sources_for_suite(suite: str) -> list[str]:
    if suite == "tile":
        return [
            "avs/qemu/tests/10_tile_tma.cpp",
            "avs/qemu/tests/10_tile_cube.cpp",
            "avs/qemu/tests/10_tile_cube_asm.S",
            "avs/qemu/tests/10_tile_tepl.cpp",
            "avs/qemu/tests/10_tile_tepl_asm.S",
            "avs/qemu/tests/10_tile_integration.cpp",
            *[_pto_kernel_src(name) for name in PTO_TILE_KERNEL_NAMES],
        ]
    if suite == "atomic":
        return [
            "avs/qemu/tests/07_atomic_lr_srczero.S",
        ]
    if suite == "callret":
        return [
            "avs/qemu/tests/14_callret_templates.S",
        ]
    if suite == "runtime":
        return [
            "avs/runtime/freestanding/src/syscall.c",
            "avs/runtime/freestanding/src/stdlib/stdlib.c",
            "avs/runtime/freestanding/src/math/math.c",
        ]
    if suite == "pto_parity":
        return [_pto_kernel_src(name) for name in PTO_PARITY_KERNEL_NAMES]
    if suite == "deepseek_tilekernels":
        return [_pto_kernel_src(name) for name in DEEPSEEK_TILEKERNEL_NAMES]
    return []

LLC_PIPELINE_SUITES: set[str] = set()

EXTRA_CFLAGS_BY_SUITE: dict[str, list[str]] = {
    "pto_parity": [
        "-DPTO_USE_MIXED_TILE_SIMT=1",
    ],
    "simt_autovec": [
        "-mllvm",
        "-linx-simt-autovec=1",
        "-mllvm",
        "-linx-simt-autovec-mode=mseq",
        "-mllvm",
        "-linx-simt-autovec-layout=grouped",
        "-mllvm",
        "-linx-simt-autovec-lanes=32",
    ],
}

EXTRA_LLCFLAGS_BY_SUITE: dict[str, list[str]] = {
}

OBJDUMP_ASSERTS_BY_SUITE: dict[str, list[str]] = {
    "simt_autovec": [
        r"(?s)<search_store_index_grouped_boundary>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?B\.IOTI.*?B\.IOTI.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.sw\.brg\.local\b.*?\bv\.lw\.brg\b.*?->p.*?\bb\.nz\b.*?\bj\b.*?\bv\.sw\.brg\b",
        r"(?s)<search_store_index_split_addrs_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.psel\s+p,.*?\bv\.sw\.brg\b.*?\bv\.sw\.brg\b.*?\bv\.cmp\.ne\b",
        r"(?s)<running_sum_store>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.fadd\b.*?\bv\.sw\.brg\b.*?\bv\.sw\.brg\b",
        r"(?s)<running_sum_liveout>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.fadd\b.*?\bv\.sw\.brg\b",
        r"(?s)<reduction_sum_liveout>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?B\.IOTI.*?B\.IOTI.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.rdfadd\b.*?\bv\.sw\.brg\.local\b.*?\bv\.lw\.brg\.local\b.*?\bv\.sw\.brg\b",
        r"(?s)<copy_and_last_value_liveout>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.lw\.brg\b.*?\bv\.sw\.brg\b.*?\bv\.sw\.brg\b",
        r"(?s)<vector_nested_if_ifcvt>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.flt\b.*?\bv\.csel\b.*?\bv\.csel\b.*?\bv\.sw\.brg\b",
        r"(?s)<vector_min_select_store>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.flt\b.*?\bv\.csel\b.*?\bv\.sw\.brg\b",
        r"(?s)<vector_shifted_out_store>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+1,\s+->lb1.*?\bv\.fadd\b.*?\bv\.sw\.brg\b",
        r"(?s)<fill_i32_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.add\s+zero,\s+ri[0-9]+(?:\.sw)?,\s+->vt(?:#[0-9]+)?(?:\.w)?\b.*?\bv\.sw\.brg\b",
        r"(?s)<fill_i8_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.add\s+zero,\s+ri[0-9]+(?:\.sw)?,\s+->vt(?:#[0-9]+)?(?:\.w)?\b.*?\bv\.sb\.brg\b",
        r"(?s)<fill_i16_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.add\s+zero,\s+ri[0-9]+(?:\.sw)?,\s+->vt(?:#[0-9]+)?(?:\.w)?\b.*?\bv\.sh\.brg\b",
        r"(?s)<copy_u8_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.lbu\.brg\b.*?\bv\.sb\.brg\b",
        r"(?s)<copy_u16_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.lhu\.brg\b.*?\bv\.sh\.brg\b",
        r"(?s)<widen_i8_to_i32_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.lb\.brg\b.*?\bv\.sw\.brg\b",
        r"(?s)<widen_i16_to_i32_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.lh\.brg\b.*?\bv\.sw\.brg\b",
        r"(?s)<sign_classify_i8_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.lb\.brg\b.*?\bv\.cmp\.lt\b.*?\bv\.csel\b.*?\bv\.sw\.brg\b",
        r"(?s)<sign_classify_i16_autovec>:.*?\bBSTART\.MSEQ\b.*?\bB\.TEXT\b.*?C\.B\.DIMI\s+32,\s+->lb0.*?C\.B\.DIMI\s+2,\s+->lb1.*?\bv\.lh\.brg\b.*?\bv\.cmp\.lt\b.*?\bv\.csel\b.*?\bv\.sw\.brg\b",
    ],
}

EXPERIMENTAL_SUITES: set[str] = {
    # Requires tile builtin-enabled clang and PTO kernel headers.
    "tile",
    "pto_parity",
    # v0.57 migration keeps this behind --all-suites until the vblock body
    # symbol lowering and objdump expectations are refreshed for canonical B.IOT.
    "simt_autovec",
    # Standalone negative trap regression; not a normal smoke lane.
    "v057_vector_body_fault",
    # Compile-only per-instruction translation corpus used by coverage/reporting.
    "translation_corpus",
    # Evidence carrier: run explicitly so it never collides with the ordinary
    # loadstore suite that owns the same main.c entry point.
    "executable_memory",
    "executable_scalar",
    "executable_integer",
}

DEDICATED_EVIDENCE_SUITES: set[str] = {
    "executable_memory",
    "executable_scalar",
    "executable_integer",
}

CORE_SUITES: list[str] = [
    "arithmetic",
]


def _parse_test_id(text: str) -> int:
    try:
        value = int(text, 0)
    except ValueError as e:
        raise SystemExit(f"error: invalid --require-test-id value '{text}': {e}")
    if value < 0 or value > 0xFFFFFFFF:
        raise SystemExit(f"error: --require-test-id out of range (must fit uint32): {text}")
    return value


def _path_or_none(p: str | None) -> Path | None:
    if not p:
        return None
    return Path(os.path.expanduser(p))


def _default_clang() -> Path | None:
    env = os.environ.get("CLANG")
    if env:
        return Path(os.path.expanduser(env))
    cands = [REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "clang"]
    for cand in cands:
        if cand.exists():
            return cand
    return None


def _default_clangxx(clang: Path | None) -> Path | None:
    env = os.environ.get("CLANGXX")
    if env:
        return Path(os.path.expanduser(env))
    if clang:
        cand = clang.parent / "clang++"
        if cand.exists():
            return cand
    return None


def _default_lld(clang: Path | None) -> Path | None:
    env = os.environ.get("LLD")
    if env:
        return Path(os.path.expanduser(env))
    if clang:
        cand = clang.parent / "ld.lld"
        if cand.exists():
            return cand
    return None


def _default_llvm_objdump(clang: Path | None) -> Path | None:
    env = os.environ.get("LLVM_OBJDUMP")
    if env:
        return Path(os.path.expanduser(env))
    if clang:
        cand = clang.parent / "llvm-objdump"
        if cand.exists():
            return cand
    cands = [REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "llvm-objdump"]
    for cand in cands:
        if cand.exists():
            return cand
    return None


def _default_llc(clang: Path | None) -> Path | None:
    env = os.environ.get("LLC")
    if env:
        return Path(os.path.expanduser(env))
    if clang:
        cand = clang.parent / "llc"
        if cand.exists():
            return cand
    cands = [REPO_ROOT / "compiler" / "llvm" / "build-linxisa-clang" / "bin" / "llc"]
    for cand in cands:
        if cand.exists():
            return cand
    return None


def _clang_builtin_include_dir(clang: Path | None) -> Path | None:
    env = os.environ.get("CLANG_HEADERS_DIR")
    if env:
        cand = Path(os.path.expanduser(env))
        return cand if (cand / "stdint.h").exists() else None

    cands = [REPO_ROOT / "compiler" / "llvm" / "clang" / "lib" / "Headers"]
    if clang is not None:
        try:
            resource_dir = subprocess.run(
                [str(clang), "-print-resource-dir"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            ).stdout.strip()
        except OSError:
            resource_dir = ""
        if resource_dir:
            cands.insert(0, Path(resource_dir) / "include")

    for cand in cands:
        if (cand / "stdint.h").exists():
            return cand
    return None


def _default_qemu() -> Path | None:
    env = os.environ.get("QEMU")
    if env:
        return Path(os.path.expanduser(env))
    return None


def _check_exe(p: Path, what: str) -> None:
    if not p.exists():
        raise SystemExit(f"error: {what} not found: {p}")
    if not os.access(p, os.X_OK):
        raise SystemExit(f"error: {what} not executable: {p}")


def _run(cmd: list[str], *, verbose: bool, **kwargs) -> subprocess.CompletedProcess[bytes]:
    if verbose:
        print("+", " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd, check=False, **kwargs)


def _verify_objdump_shape(
    llvm_objdump: Path,
    obj: Path,
    *,
    suite: str,
    verbose: bool,
) -> None:
    patterns = OBJDUMP_ASSERTS_BY_SUITE.get(suite)
    if not patterns:
        return

    p = _run(
        [str(llvm_objdump), "-d", str(obj)],
        verbose=verbose,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode != 0:
        sys.stderr.buffer.write(p.stderr)
        raise SystemExit(f"error: llvm-objdump failed for {obj}")

    text = p.stdout.decode("utf-8", errors="replace")
    missing = [pat for pat in patterns if re.search(pat, text) is None]
    if missing:
        sys.stderr.write(
            f"error: missing expected objdump patterns for suite {suite}: {missing}\n"
        )
        sys.stderr.write(text)
        raise SystemExit(f"error: object shape verification failed: {obj}")


def _tail(data: bytes, max_bytes: int = 4000) -> bytes:
    if len(data) <= max_bytes:
        return data
    return data[-max_bytes:]


def _run_qemu_with_heartbeat(
    cmd: list[str],
    *,
    env: dict[str, str] | None,
    verbose: bool,
    timeout: float,
    heartbeat_sec: float,
    no_progress_timeout: float,
) -> tuple[subprocess.CompletedProcess[bytes], bool, bool]:
    if verbose:
        print("+", " ".join(cmd), file=sys.stderr)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    stdout_bytes = 0
    stderr_bytes = 0

    start = time.monotonic()
    last_activity = start
    next_heartbeat = start + heartbeat_sec if heartbeat_sec > 0 else float("inf")

    fd_kind: dict[int, str] = {}
    if proc.stdout is not None:
        fd_kind[proc.stdout.fileno()] = "stdout"
    if proc.stderr is not None:
        fd_kind[proc.stderr.fileno()] = "stderr"

    timed_out = False
    stalled = False

    while fd_kind:
        now = time.monotonic()
        elapsed = now - start
        if elapsed >= timeout:
            timed_out = True
            break

        idle = now - last_activity
        if no_progress_timeout > 0 and idle >= no_progress_timeout:
            stalled = True
            break

        wait_for = min(0.5, timeout - elapsed)
        if heartbeat_sec > 0:
            wait_for = min(wait_for, max(0.0, next_heartbeat - now))
        if no_progress_timeout > 0:
            wait_for = min(wait_for, max(0.0, no_progress_timeout - idle))

        readable, _, _ = select.select(list(fd_kind.keys()), [], [], wait_for)
        if readable:
            for fd in readable:
                kind = fd_kind.get(fd)
                if kind is None:
                    continue
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    chunk = b""
                if not chunk:
                    fd_kind.pop(fd, None)
                    continue

                if kind == "stdout":
                    stdout_chunks.append(chunk)
                    stdout_bytes += len(chunk)
                    if verbose:
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                else:
                    stderr_chunks.append(chunk)
                    stderr_bytes += len(chunk)
                    if verbose:
                        sys.stderr.buffer.write(chunk)
                        sys.stderr.buffer.flush()
                last_activity = time.monotonic()

        now = time.monotonic()
        if heartbeat_sec > 0 and now >= next_heartbeat:
            hb_elapsed = now - start
            hb_idle = now - last_activity
            sys.stderr.write(
                "LINX_QEMU_HEARTBEAT "
                f"elapsed={hb_elapsed:.1f}s "
                f"idle={hb_idle:.1f}s "
                f"stdout_bytes={stdout_bytes} "
                f"stderr_bytes={stderr_bytes}\n"
            )
            while next_heartbeat <= now:
                next_heartbeat += heartbeat_sec

        if proc.poll() is not None:
            break

    if timed_out or stalled:
        proc.kill()

    extra_out = b""
    extra_err = b""
    try:
        extra_out, extra_err = proc.communicate(timeout=1.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        extra_out, extra_err = proc.communicate()

    if extra_out:
        stdout_chunks.append(extra_out)
        if verbose:
            sys.stdout.buffer.write(extra_out)
            sys.stdout.buffer.flush()
    if extra_err:
        stderr_chunks.append(extra_err)
        if verbose:
            sys.stderr.buffer.write(extra_err)
            sys.stderr.buffer.flush()

    completed = subprocess.CompletedProcess(
        cmd,
        proc.returncode if proc.returncode is not None else -1,
        b"".join(stdout_chunks),
        b"".join(stderr_chunks),
    )
    return completed, timed_out, stalled


def _suite_selection(args: argparse.Namespace) -> list[str]:
    if args.all:
        return [s for s in SUITES.keys() if s not in EXPERIMENTAL_SUITES]

    if args.suite:
        invalid_suites = [s for s in args.suite if s not in SUITES]
        if invalid_suites:
            raise SystemExit(f"error: unsupported --suite {invalid_suites}; use --list-suites")
        return list(dict.fromkeys(args.suite))

    if args.filter:
        try:
            rx = re.compile(args.filter)
        except re.error as e:
            raise SystemExit(f"error: invalid --filter regex: {e}")
        matched: list[str] = []
        for name, meta in SUITES.items():
            if rx.search(name) or rx.search(meta["src"]):
                matched.append(name)
        if not matched:
            raise SystemExit(f"error: --filter matched no suites: {args.filter}")
        return matched

    return CORE_SUITES.copy()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compile and run LinxISA QEMU unit tests.")
    parser.add_argument("--clang", default=None, help="Path to clang (env: CLANG)")
    parser.add_argument("--clangxx", default=None, help="Path to clang++ (env: CLANGXX)")
    parser.add_argument("--lld", default=None, help="Path to ld.lld (env: LLD)")
    parser.add_argument("--llvm-objdump", default=None, help="Path to llvm-objdump (env: LLVM_OBJDUMP)")
    parser.add_argument("--llc", default=None, help="Path to llc (env: LLC)")
    parser.add_argument("--qemu", default=None, help="Path to qemu-system-linx64 (env: QEMU)")
    parser.add_argument(
        "--target",
        default="linx64-linx-none-elf",
        help="Target triple (default: linx64-linx-none-elf)",
    )
    parser.add_argument("--out-dir", default=str(SCRIPT_DIR / "out"), help="Output directory")
    parser.add_argument("--timeout", type=float, default=5.0, help="QEMU timeout in seconds")
    parser.add_argument(
        "--heartbeat-sec",
        type=float,
        default=float(os.environ.get("LINX_QEMU_HEARTBEAT_SEC", "10")),
        help="Emit heartbeat while waiting for QEMU output (0 to disable).",
    )
    parser.add_argument(
        "--no-progress-timeout",
        type=float,
        default=float(os.environ.get("LINX_QEMU_NO_PROGRESS_TIMEOUT", "0")),
        help="Fail if no QEMU stdout/stderr output is seen for this many seconds (0 to disable).",
    )
    parser.add_argument("--compile-only", action="store_true", help="Only compile/relocatable-link; do not build the direct-boot ELF or run QEMU")
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Compile and link the direct-boot ELF, then stop before QEMU.",
    )
    parser.add_argument(
        "--smoke-source-overrides",
        action="store_true",
        help="Use smoke source overrides for selected suites even when running QEMU",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--list-suites", action="store_true", help="List available suites and exit")
    parser.add_argument("--all", action="store_true", help="Enable all suites (including float/atomic)")
    parser.add_argument(
        "--all-suites",
        action="store_true",
        help="Enable all suites, including experimental ones (e.g. tile)",
    )
    parser.add_argument("--suite", action="append", help="Enable only this suite (repeatable)")
    parser.add_argument("--filter", help="Regex to select suites by name or filename")
    parser.add_argument("--qemu-arg", action="append", default=[], help="Extra QEMU arg (repeatable)")
    parser.add_argument(
        "--extra-cflag",
        action="append",
        default=[],
        help="Extra compile flag passed to every source (repeatable)",
    )
    parser.add_argument(
        "--require-test-id",
        action="append",
        default=[],
        help="Require UART evidence of test_start for this uint32 test id (hex/dec)",
    )
    parser.add_argument(
        "--evidence-out",
        default=None,
        help="Write structured runtime evidence JSON and enable bounded PC tracing.",
    )
    parser.add_argument(
        "--evidence-pc",
        action="append",
        default=[],
        help=(
            "Record an exact pre-execution QEMU PC-watch packet for this uint64 PC "
            "(repeatable; requires --evidence-out; max 16)."
        ),
    )
    args = parser.parse_args(argv)

    if args.compile_only and args.prepare_only:
        raise SystemExit("error: --compile-only and --prepare-only are mutually exclusive")
    if args.prepare_only and (args.evidence_out or args.evidence_pc):
        raise SystemExit("error: --prepare-only does not emit runtime evidence")
    if args.timeout <= 0:
        raise SystemExit("error: --timeout must be > 0")
    if args.heartbeat_sec < 0:
        raise SystemExit("error: --heartbeat-sec must be >= 0")
    if args.no_progress_timeout < 0:
        raise SystemExit("error: --no-progress-timeout must be >= 0")
    evidence_pcs = _parse_evidence_pcs(args.evidence_pc)
    if evidence_pcs and not args.evidence_out:
        raise SystemExit("error: --evidence-pc requires --evidence-out")

    if args.list_suites:
        for name, meta in SUITES.items():
            suffix = " (experimental)" if name in EXPERIMENTAL_SUITES else ""
            print(f"{name:10} {meta['src']}{suffix}")
        return 0

    clang = _path_or_none(args.clang) or _default_clang()
    if not clang:
        raise SystemExit("error: clang not found; set --clang or CLANG")
    clangxx = _path_or_none(args.clangxx) or _default_clangxx(clang)
    lld = _path_or_none(args.lld) or _default_lld(clang)
    if not lld:
        raise SystemExit("error: ld.lld not found; set --lld or LLD")
    llvm_objdump = _path_or_none(args.llvm_objdump) or _default_llvm_objdump(clang)
    llc = _path_or_none(args.llc) or _default_llc(clang)
    qemu = _path_or_none(args.qemu) or _default_qemu()
    clang_builtin_include_dir = _clang_builtin_include_dir(clang)
    if not qemu and not args.compile_only and not args.prepare_only:
        raise SystemExit("error: qemu-system-linx64 not found; set --qemu or QEMU")
    if clang_builtin_include_dir is None:
        raise SystemExit(
            "error: unable to locate clang builtin headers; "
            "set CLANG_HEADERS_DIR=/path/to/clang/lib/Headers"
        )

    _check_exe(clang, "clang")
    if clangxx:
        _check_exe(clangxx, "clang++")
    _check_exe(lld, "ld.lld")
    if llvm_objdump:
        _check_exe(llvm_objdump, "llvm-objdump")
    if llc:
        _check_exe(llc, "llc")
    if qemu:
        _check_exe(qemu, "qemu-system-linx64")
    qemu_env = os.environ.copy()
    qemu_env.setdefault("LINX_VIRT_TEST_FINISHER", "1")
    qemu_debug_env = _configure_target_pc_watch_env(qemu_env, evidence_pcs)

    selected = _suite_selection(args)
    if args.all_suites:
        selected = [s for s in SUITES.keys() if s not in DEDICATED_EVIDENCE_SUITES]
    if any(s in LLC_PIPELINE_SUITES for s in selected) and not llc:
        raise SystemExit("error: llc not found; set --llc or LLC")
    if any(s in OBJDUMP_ASSERTS_BY_SUITE for s in selected) and not llvm_objdump:
        raise SystemExit("error: llvm-objdump not found; set --llvm-objdump or LLVM_OBJDUMP")
    required_test_ids = [_parse_test_id(t) for t in args.require_test_id]

    out_dir = Path(os.path.expanduser(args.out_dir))
    obj_dir = out_dir / "obj"
    out_dir.mkdir(parents=True, exist_ok=True)
    obj_dir.mkdir(parents=True, exist_ok=True)

    generated_translation_sources: list[Path] = []
    if "translation_corpus" in selected:
        if not LLVM_AVS_DISASM_VECTOR_GEN.is_file():
            raise SystemExit(
                f"error: missing Linx disasm vector generator: {LLVM_AVS_DISASM_VECTOR_GEN}"
            )
        if not LLVM_AVS_SPEC.is_file():
            raise SystemExit(f"error: missing canonical ISA spec: {LLVM_AVS_SPEC}")
        generated_dir = out_dir / "generated"
        generated_dir.mkdir(parents=True, exist_ok=True)
        generated_spec_decode = generated_dir / "99_spec_decode_qemu.s"
        p = _run(
            [
                sys.executable,
                str(LLVM_AVS_DISASM_VECTOR_GEN),
                "--spec",
                str(LLVM_AVS_SPEC),
                "--out",
                str(generated_spec_decode),
            ],
            verbose=args.verbose,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if p.returncode != 0:
            sys.stderr.buffer.write(p.stdout)
            sys.stderr.buffer.write(p.stderr)
            raise SystemExit("error: failed to generate QEMU translation corpus")
        generated_translation_sources.append(generated_spec_decode)
        if LLVM_AVS_V057_FORMS.is_file():
            generated_translation_sources.append(LLVM_AVS_V057_FORMS)

    include_dir = SCRIPT_DIR / "lib"
    libc_include_dir = REPO_ROOT / "avs" / "runtime" / "freestanding" / "include"
    pto_kernel_include_dir: Path | None = None
    include_env = os.environ.get("PTO_KERNEL_INCLUDE")
    if include_env:
        include_candidate = Path(os.path.expanduser(include_env))
        if not include_candidate.exists():
            raise SystemExit(
                f"error: PTO_KERNEL_INCLUDE does not exist: {include_candidate}"
            )
        pto_kernel_include_dir = include_candidate
    else:
        default_include = REPO_ROOT / "workloads" / "pto_kernels" / "include"
        if default_include.exists():
            pto_kernel_include_dir = default_include
    if any(s in selected for s in ("tile", "pto_parity", "deepseek_tilekernels")) and pto_kernel_include_dir is None:
        raise SystemExit(
            "error: tile suite requires PTO headers; looked for "
            f"{REPO_ROOT / 'workloads' / 'pto_kernels' / 'include'} "
            "or set PTO_KERNEL_INCLUDE=/path/to/include"
        )
    pto_include_dir: Path | None = None
    env = os.environ.get("PTO_ISA_INCLUDE")
    if env:
        candidate = Path(os.path.expanduser(env))
        if not candidate.exists():
            raise SystemExit(f"error: PTO_ISA_INCLUDE does not exist: {candidate}")
        pto_include_dir = candidate
    sources: list[Path] = []
    seen_sources: set[Path] = set()

    def add_source(path: Path) -> None:
        if path in seen_sources:
            return
        seen_sources.add(path)
        sources.append(path)

    translation_only = args.compile_only and set(selected) == {"translation_corpus"}
    if not translation_only:
        add_source(SCRIPT_DIR / "tests" / "main.c")
        add_source(REPO_ROOT / "avs" / "runtime" / "freestanding" / "src" / "string" / "mem.c")
    for suite in selected:
        rel = SUITES[suite]["src"]
        if translation_only and suite == "translation_corpus":
            continue
        if args.compile_only or args.smoke_source_overrides:
            rel = COMPILE_ONLY_SUITE_SOURCE_OVERRIDE.get(suite, rel)
        add_source(SCRIPT_DIR / rel)
    for path in generated_translation_sources:
        add_source(path)
    for suite in selected:
        for rel in _extra_sources_for_suite(suite):
            add_source(REPO_ROOT / rel)
    softfp_suites = {
        "float",
        "v057_vector",
        "v057_vector_ops",
        "v04_vector_ops",
        "simt_autovec",
        "tile",
        "pto_parity",
        "deepseek_tilekernels",
        "runtime",
    }
    if any(s in softfp_suites for s in selected):
        add_source(REPO_ROOT / "avs" / "runtime" / "freestanding" / "src" / "softfp" / "softfp.c")
        add_source(REPO_ROOT / "avs" / "runtime" / "freestanding" / "src" / "math" / "math.c")

    suite_macro_values: dict[str, bool] = {}
    for name, meta in SUITES.items():
        macro = meta["macro"]
        suite_macro_values[macro] = suite_macro_values.get(macro, False) or name in selected
    suite_macros = [
        f"-D{macro}={'1' if enabled else '0'}"
        for macro, enabled in suite_macro_values.items()
    ]
    terminal_test_ids = [
        TERMINAL_TEST_IDS_BY_SUITE[suite]
        for suite in selected
        if suite in TERMINAL_TEST_IDS_BY_SUITE
    ]
    emit_test_logs = (
        args.verbose
        or bool(required_test_ids)
        or bool(args.evidence_out)
        or bool(terminal_test_ids)
    )
    suite_completion_test_ids = (
        [
            COMPLETION_TEST_IDS_BY_SUITE[suite]
            for suite in selected
            if suite in COMPLETION_TEST_IDS_BY_SUITE
        ]
        if emit_test_logs
        else []
    )

    common_cflags = [
        "-target",
        args.target,
        "-O2",
        "-ffreestanding",
        "-fno-function-sections",
        "-fno-data-sections",
        "-fno-builtin",
        "-fno-stack-protector",
        "-fno-asynchronous-unwind-tables",
        "-fno-unwind-tables",
        "-fno-exceptions",
        "-fno-jump-tables",
        "-nostdlib",
        f"-I{clang_builtin_include_dir}",
        f"-I{include_dir}",
        f"-I{libc_include_dir}",
        *suite_macros,
        f"-DLINX_TEST_QUIET={'0' if emit_test_logs else '1'}",
        *args.extra_cflag,
    ]
    if any(s in selected for s in ("tile", "pto_parity", "deepseek_tilekernels")):
        # Keep tile-suite bring-up deterministic: SIMT autovec currently
        # triggers a mid-end crash on migrated PTO kernels under strict v0.57.
        common_cflags += ["-mllvm", "-linx-simt-autovec=false"]
    if any(s in selected for s in ("tile", "pto_parity", "deepseek_tilekernels")):
        # Runtime policy: migrated PTO kernels run in smoke profile under QEMU.
        # Full-profile coverage remains in compile/objdump gates.
        common_cflags += ["-DPTO_QEMU_SMOKE=1"]
    if "pto_parity" in selected:
        # Keep host parity and QEMU parity on the same mixed tile/SIMT path.
        common_cflags += ["-DPTO_USE_MIXED_TILE_SIMT=1"]
    if pto_kernel_include_dir is not None:
        common_cflags.append(f"-I{pto_kernel_include_dir}")
    if pto_include_dir:
        common_cflags.append(f"-I{pto_include_dir}")
    if "pto_parity" in selected:
        parity_gen = REPO_ROOT / "workloads" / "pto_kernels" / "tools" / "generate_pto_parity_shape_header.py"
        parity_header = REPO_ROOT / "workloads" / "generated" / "pto_parity_shape_config.generated.hpp"
        if parity_gen.is_file():
            p = _run([sys.executable, str(parity_gen), "--out", str(parity_header)],
                     verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                sys.stderr.buffer.write(p.stdout)
                sys.stderr.buffer.write(p.stderr)
                raise SystemExit("error: failed to generate PTO parity shape header")
            common_cflags.append(f"-I{parity_header.parent}")

    objects: list[Path] = []
    for src in sources:
        obj = obj_dir / (src.stem + ".o")
        cflags = list(common_cflags)
        src_suite: str | None = None
        try:
            src_rel = src.relative_to(SCRIPT_DIR).as_posix()
        except ValueError:
            src_rel = None
        if src_rel is not None:
            for suite_name, meta in SUITES.items():
                if meta["src"] == src_rel:
                    src_suite = suite_name
                    break
        if src_suite is not None:
            cflags.extend(EXTRA_CFLAGS_BY_SUITE.get(src_suite, []))
        tool = clang
        if src.suffix in {".cc", ".cpp", ".cxx"}:
            if not clangxx:
                raise SystemExit("error: tile suite requires clang++; set --clangxx or CLANGXX")
            tool = clangxx
            cflags.append("-std=c++17")
        # Keep selected sources unoptimized during bring-up when backend passes
        # are still unstable under aggressive optimization.
        if src.name in {"softfp.c"}:
            cflags = [("-O0" if f == "-O2" else f) for f in cflags]
        # Jump table/indirect branch coverage requires allowing jump tables.
        if src.name == "08_jumptable.c":
            cflags = [f for f in cflags if f != "-fno-jump-tables"]
        if src_suite in LLC_PIPELINE_SUITES:
            if not llc:
                raise SystemExit("error: llc not found; set --llc or LLC")
            ir = obj_dir / (src.stem + ".ll")
            clang_cmd = [str(tool), *cflags, "-S", "-emit-llvm", str(src), "-o", str(ir)]
            p = _run(clang_cmd, verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                sys.stderr.buffer.write(p.stderr)
                raise SystemExit(f"error: IR compile failed: {src}")
            llc_cmd = [
                str(llc),
                f"-mtriple={args.target}",
                "-O2",
                "-filetype=obj",
                *EXTRA_LLCFLAGS_BY_SUITE.get(src_suite, []),
                str(ir),
                "-o",
                str(obj),
            ]
            p = _run(llc_cmd, verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                sys.stderr.buffer.write(p.stderr)
                raise SystemExit(f"error: llc failed: {src}")
        else:
            cmd = [str(tool), *cflags, "-c", str(src), "-o", str(obj)]
            p = _run(cmd, verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                sys.stderr.buffer.write(p.stderr)
                raise SystemExit(f"error: compile failed: {src}")
        if src.suffix.lower() in {".s", ".S"}:
            sidecar = obj.with_suffix(src.suffix.lower())
            shutil.copyfile(src, sidecar)
        if src_suite in OBJDUMP_ASSERTS_BY_SUITE:
            _verify_objdump_shape(
                llvm_objdump,
                obj,
                suite=src_suite,
                verbose=args.verbose,
            )
        objects.append(obj)

    out_obj = out_dir / "linx-qemu-tests.o"
    cmd = [str(lld), "-r", "-o", str(out_obj), *[str(o) for o in objects]]
    p = _run(cmd, verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.buffer.write(p.stderr)
        raise SystemExit("error: link (ld.lld -r) failed")

    print(f"ok: built {out_obj}")
    if args.compile_only:
        return 0

    directboot_linker = out_dir / "linx-qemu-tests-directboot.ld"
    directboot_elf = out_dir / "linx-qemu-tests.elf"
    directboot_linker.write_text(DIRECT_BOOT_LINK_SCRIPT, encoding="utf-8")
    cmd = [
        str(lld),
        "-T",
        str(directboot_linker),
        "-e",
        "_start",
        "-o",
        str(directboot_elf),
        str(out_obj),
    ]
    p = _run(cmd, verbose=args.verbose, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        sys.stderr.buffer.write(p.stderr)
        raise SystemExit("error: direct-boot link failed")

    print(f"ok: built {directboot_elf}")

    if args.prepare_only:
        return 0

    assert qemu is not None
    evidence_trace = out_dir / "qemu-executable-coverage-in_asm.log"
    evidence_trace_args = (
        ["-d", "in_asm", "-D", str(evidence_trace)]
        if args.evidence_out and not evidence_pcs
        else []
    )
    qemu_cmd = [
        str(qemu),
        "-machine",
        "virt",
        "-bios",
        "none",
        "-kernel",
        str(directboot_elf),
        "-nographic",
        "-monitor",
        "none",
        *evidence_trace_args,
        *args.qemu_arg,
    ]

    p, timed_out, stalled = _run_qemu_with_heartbeat(
        qemu_cmd,
        env=qemu_env,
        verbose=args.verbose,
        timeout=args.timeout,
        heartbeat_sec=args.heartbeat_sec,
        no_progress_timeout=args.no_progress_timeout,
    )

    verdict = _runtime_verdict(
        p.stdout or b"",
        p.returncode,
        timed_out=timed_out,
        stalled=stalled,
        required_test_ids=required_test_ids,
        terminal_test_ids=terminal_test_ids,
        suite_completion_test_ids=suite_completion_test_ids,
    )

    if args.evidence_out:
        _write_execution_evidence(
            Path(os.path.expanduser(args.evidence_out)),
            selected=selected,
            objects=objects,
            aggregate_object=out_obj,
            elf=directboot_elf,
            qemu=qemu,
            completed=p,
            verdict=verdict,
            trace_path=evidence_trace,
            evidence_pcs=evidence_pcs,
            qemu_debug_env=qemu_debug_env,
        )

    if verdict["reason"] == "guest_failure":
        sys.stderr.write("FAIL (guest reported a test failure)\n")
        if not args.verbose and p.stdout:
            sys.stderr.write("---- guest stdout (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stdout))
            sys.stderr.write("\n")
        return p.returncode if p.returncode > 0 else 1

    if timed_out:
        stdout = p.stdout or b""
        stderr = p.stderr or b""
        sys.stderr.write(f"error: QEMU timeout after {args.timeout:.1f}s\n")
        if stdout:
            sys.stderr.write("---- guest stdout (tail) ----\n")
            sys.stderr.buffer.write(_tail(stdout))
            sys.stderr.write("\n")
        if stderr:
            sys.stderr.write("---- qemu stderr (tail) ----\n")
            sys.stderr.buffer.write(_tail(stderr))
            sys.stderr.write("\n")
        return 124

    if stalled:
        sys.stderr.write(
            f"error: QEMU produced no output for {args.no_progress_timeout:.1f}s "
            "(no-progress timeout)\n"
        )
        if p.stdout:
            sys.stderr.write("---- guest stdout (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stdout))
            sys.stderr.write("\n")
        if p.stderr:
            sys.stderr.write("---- qemu stderr (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stderr))
            sys.stderr.write("\n")
        return 125

    finisher_low8 = p.returncode & 0xFF if p.returncode is not None else -1

    if verdict["status"] == "PASS":
        print("PASS")
        return 0

    if verdict["missing_required_test_ids"]:
        sys.stderr.write(
            "error: missing required test id marker(s) in UART output: "
            + ", ".join(verdict["missing_required_test_ids"])
            + "\n"
        )
        if not args.verbose and p.stdout:
            sys.stderr.write("---- guest stdout (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stdout))
            sys.stderr.write("\n")
        return 3

    if verdict["missing_suite_completion_test_ids"]:
        sys.stderr.write(
            "error: selected suite completion marker(s) missing from UART output: "
            + ", ".join(verdict["missing_suite_completion_test_ids"])
            + "\n"
        )
        if not args.verbose and p.stdout:
            sys.stderr.write("---- guest stdout (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stdout))
            sys.stderr.write("\n")
        return 4

    if p.returncode == 0:
        sys.stderr.write(
            "error: exit=0 without a clean finisher or UART success oracle\n"
        )
        if not args.verbose and p.stdout:
            sys.stderr.write("---- guest stdout (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stdout))
            sys.stderr.write("\n")
        return 2

    if finisher_low8 == FINISHER_FAIL_LOW8:
        sys.stderr.write(f"FAIL (guest finisher fail exit={p.returncode})\n")
    elif finisher_low8 == FINISHER_RESET_LOW8:
        sys.stderr.write(f"FAIL (guest finisher reset exit={p.returncode})\n")
    else:
        sys.stderr.write(f"FAIL (qemu exit={p.returncode})\n")
    if not args.verbose:
        if p.stdout:
            sys.stderr.write("---- guest stdout (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stdout))
            sys.stderr.write("\n")
        if p.stderr:
            sys.stderr.write("---- qemu stderr (tail) ----\n")
            sys.stderr.buffer.write(_tail(p.stderr))
            sys.stderr.write("\n")
    return p.returncode if p.returncode != 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
