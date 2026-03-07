#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINX_BRINGUP_PROFILE="${LINX_BRINGUP_PROFILE:-release-strict}" # dev|release-strict

echo "== LinxISA strict cross-repo gate =="
echo "profile: $LINX_BRINGUP_PROFILE"

CLANG="${CLANG:-}"
LLD="${LLD:-}"
QEMU="${QEMU:-}"
TOOLCHAIN_LANE="${TOOLCHAIN_LANE:-pin}" # external|pin|auto
# Runtime and emulator defaults pin to the in-repo submodule toolchain.
QEMU_LANE="${QEMU_LANE:-pin}" # auto|pin|external
QEMU_ROOT="${QEMU_ROOT:-}"
LINX_DISABLE_TIMER_IRQ="${LINX_DISABLE_TIMER_IRQ:-0}" # timer IRQ enabled by default
LINX_EMU_DISABLE_TIMER_IRQ="${LINX_EMU_DISABLE_TIMER_IRQ:-0}" # strict system/test coverage needs timer IRQ

RUN_GLIBC_G1="${RUN_GLIBC_G1:-1}"
GLIBC_G1_SCRIPT="${GLIBC_G1_SCRIPT:-$ROOT/lib/glibc/tools/linx/build_linx64_glibc.sh}"
RUN_GLIBC_G1B="${RUN_GLIBC_G1B-}"
GLIBC_G1B_ALLOW_BLOCKED="${GLIBC_G1B_ALLOW_BLOCKED-}"
GLIBC_G1B_SCRIPT="${GLIBC_G1B_SCRIPT:-$ROOT/lib/glibc/tools/linx/build_linx64_glibc_g1b.sh}"
ALLOW_GLIBC_G1_BLOCKED="${ALLOW_GLIBC_G1_BLOCKED-}"
RUN_MODEL_DIFF="${RUN_MODEL_DIFF-}"
RUN_CPP_GATES="${RUN_CPP_GATES-}" # 0|1
CPP_MODE="${CPP_MODE:-phase-b}"
RUN_CONSISTENCY_CHECKS="${RUN_CONSISTENCY_CHECKS:-1}" # 0|1 (nested runtime-convergence calls set 0)
RUN_AVS_MATRIX_AUDIT="${RUN_AVS_MATRIX_AUDIT-}" # 0|1
RUN_QEMU_OPCODE_SYNC_AUDIT="${RUN_QEMU_OPCODE_SYNC_AUDIT-}" # 0|1
RUN_QEMU_ISA_COVERAGE_AUDIT="${RUN_QEMU_ISA_COVERAGE_AUDIT-}" # 0|1
RUN_LINUX_DEFCONFIG_AUDIT="${RUN_LINUX_DEFCONFIG_AUDIT-}" # 0|1
MULTI_AGENT_MANIFEST="${MULTI_AGENT_MANIFEST:-$ROOT/docs/bringup/agent_runs/manifest.yaml}"
MULTI_AGENT_WAIVERS="${MULTI_AGENT_WAIVERS:-$ROOT/docs/bringup/agent_runs/waivers.yaml}"
MULTI_AGENT_CHECKLISTS_ROOT="${MULTI_AGENT_CHECKLISTS_ROOT:-$ROOT/docs/bringup/agent_runs/checklists}"
MULTI_AGENT_REPORT="${MULTI_AGENT_REPORT:-}"
MULTI_AGENT_LANE="${MULTI_AGENT_LANE:-}"
MULTI_AGENT_RUN_ID="${MULTI_AGENT_RUN_ID:-}"
MULTI_AGENT_OUT="${MULTI_AGENT_OUT:-}"
MULTI_AGENT_ACTIVE_PHASE="${MULTI_AGENT_ACTIVE_PHASE:-}"

RUN_EXTENDED_CROSS_GATES="${RUN_EXTENDED_CROSS_GATES:-0}" # 0|1
LINX_GATE_TIER="${LINX_GATE_TIER:-pr}" # pr|nightly
RUN_ARCH_DOCS_GATES="${RUN_ARCH_DOCS_GATES-}" # 0|1
RUN_LINXCORE_PR_GATES="${RUN_LINXCORE_PR_GATES-}" # 0|1
RUN_TESTBENCH_PR_GATES="${RUN_TESTBENCH_PR_GATES-}" # 0|1
RUN_PYC_PR_GATES="${RUN_PYC_PR_GATES-}" # 0|1
RUN_TRACE_PR_GATES="${RUN_TRACE_PR_GATES-}" # 0|1
RUN_LINXCORE_NIGHTLY_GATES="${RUN_LINXCORE_NIGHTLY_GATES-}" # 0|1
RUN_PYC_NIGHTLY_GATES="${RUN_PYC_NIGHTLY_GATES-}" # 0|1
RUN_TRACE_NIGHTLY_GATES="${RUN_TRACE_NIGHTLY_GATES-}" # 0|1
RUN_PERF_FLOOR_GATES="${RUN_PERF_FLOOR_GATES-}" # 0|1
PERF_MAX_REGRESSION="${PERF_MAX_REGRESSION:-10.0}"
RUN_SPEC_PR_GATES="${RUN_SPEC_PR_GATES:-0}" # 0|1
RUN_SPEC_NIGHTLY_GATES="${RUN_SPEC_NIGHTLY_GATES:-0}" # 0|1
SPEC_NIGHTLY_REPORT_ONLY="${SPEC_NIGHTLY_REPORT_ONLY:-1}" # 0|1
SPEC_INPUT_SET="${SPEC_INPUT_SET:-test}" # test|refrate

if [[ "$LINX_GATE_TIER" != "pr" && "$LINX_GATE_TIER" != "nightly" ]]; then
  echo "error: LINX_GATE_TIER must be pr|nightly (got: $LINX_GATE_TIER)" >&2
  exit 2
fi

for toggle in \
  "$RUN_SPEC_PR_GATES" \
  "$RUN_SPEC_NIGHTLY_GATES" \
  "$SPEC_NIGHTLY_REPORT_ONLY"
do
  if [[ "$toggle" != "0" && "$toggle" != "1" ]]; then
    echo "error: SPEC toggles must be 0|1 (got: $toggle)" >&2
    exit 2
  fi
done

if [[ "$SPEC_INPUT_SET" != "test" && "$SPEC_INPUT_SET" != "refrate" ]]; then
  echo "error: SPEC_INPUT_SET must be test|refrate (got: $SPEC_INPUT_SET)" >&2
  exit 2
fi

if [[ "$LINX_BRINGUP_PROFILE" == "release-strict" ]]; then
  [[ -n "$RUN_GLIBC_G1B" ]] || RUN_GLIBC_G1B=1
  [[ -n "$GLIBC_G1B_ALLOW_BLOCKED" ]] || GLIBC_G1B_ALLOW_BLOCKED=0
  [[ -n "$ALLOW_GLIBC_G1_BLOCKED" ]] || ALLOW_GLIBC_G1_BLOCKED=0
  [[ -n "$RUN_MODEL_DIFF" ]] || RUN_MODEL_DIFF=0
  [[ -n "$RUN_CPP_GATES" ]] || RUN_CPP_GATES=0
  [[ -n "$RUN_AVS_MATRIX_AUDIT" ]] || RUN_AVS_MATRIX_AUDIT=1
  [[ -n "$RUN_QEMU_OPCODE_SYNC_AUDIT" ]] || RUN_QEMU_OPCODE_SYNC_AUDIT=1
  [[ -n "$RUN_QEMU_ISA_COVERAGE_AUDIT" ]] || RUN_QEMU_ISA_COVERAGE_AUDIT=1
  [[ -n "$RUN_LINUX_DEFCONFIG_AUDIT" ]] || RUN_LINUX_DEFCONFIG_AUDIT=1
else
  [[ -n "$RUN_GLIBC_G1B" ]] || RUN_GLIBC_G1B=0
  [[ -n "$GLIBC_G1B_ALLOW_BLOCKED" ]] || GLIBC_G1B_ALLOW_BLOCKED=1
  [[ -n "$ALLOW_GLIBC_G1_BLOCKED" ]] || ALLOW_GLIBC_G1_BLOCKED=0
  [[ -n "$RUN_MODEL_DIFF" ]] || RUN_MODEL_DIFF=0
  [[ -n "$RUN_CPP_GATES" ]] || RUN_CPP_GATES=0
  [[ -n "$RUN_AVS_MATRIX_AUDIT" ]] || RUN_AVS_MATRIX_AUDIT=0
  [[ -n "$RUN_QEMU_OPCODE_SYNC_AUDIT" ]] || RUN_QEMU_OPCODE_SYNC_AUDIT=0
  [[ -n "$RUN_QEMU_ISA_COVERAGE_AUDIT" ]] || RUN_QEMU_ISA_COVERAGE_AUDIT=0
  [[ -n "$RUN_LINUX_DEFCONFIG_AUDIT" ]] || RUN_LINUX_DEFCONFIG_AUDIT=0
fi

if [[ "$RUN_EXTENDED_CROSS_GATES" == "1" ]]; then
  [[ -n "$RUN_ARCH_DOCS_GATES" ]] || RUN_ARCH_DOCS_GATES=1
  [[ -n "$RUN_LINXCORE_PR_GATES" ]] || RUN_LINXCORE_PR_GATES=1
  [[ -n "$RUN_TESTBENCH_PR_GATES" ]] || RUN_TESTBENCH_PR_GATES=1
  [[ -n "$RUN_PYC_PR_GATES" ]] || RUN_PYC_PR_GATES=1
  [[ -n "$RUN_TRACE_PR_GATES" ]] || RUN_TRACE_PR_GATES=1
  if [[ "$LINX_GATE_TIER" == "nightly" ]]; then
    [[ -n "$RUN_LINXCORE_NIGHTLY_GATES" ]] || RUN_LINXCORE_NIGHTLY_GATES=1
    [[ -n "$RUN_PYC_NIGHTLY_GATES" ]] || RUN_PYC_NIGHTLY_GATES=1
    [[ -n "$RUN_TRACE_NIGHTLY_GATES" ]] || RUN_TRACE_NIGHTLY_GATES=1
    [[ -n "$RUN_PERF_FLOOR_GATES" ]] || RUN_PERF_FLOOR_GATES=1
  else
    [[ -n "$RUN_LINXCORE_NIGHTLY_GATES" ]] || RUN_LINXCORE_NIGHTLY_GATES=0
    [[ -n "$RUN_PYC_NIGHTLY_GATES" ]] || RUN_PYC_NIGHTLY_GATES=0
    [[ -n "$RUN_TRACE_NIGHTLY_GATES" ]] || RUN_TRACE_NIGHTLY_GATES=0
    [[ -n "$RUN_PERF_FLOOR_GATES" ]] || RUN_PERF_FLOOR_GATES=0
  fi
else
  RUN_ARCH_DOCS_GATES=0
  RUN_LINXCORE_PR_GATES=0
  RUN_TESTBENCH_PR_GATES=0
  RUN_PYC_PR_GATES=0
  RUN_TRACE_PR_GATES=0
  RUN_LINXCORE_NIGHTLY_GATES=0
  RUN_PYC_NIGHTLY_GATES=0
  RUN_TRACE_NIGHTLY_GATES=0
  RUN_PERF_FLOOR_GATES=0
fi

if [[ "$LINX_BRINGUP_PROFILE" == "release-strict" ]]; then
  if [[ "$ALLOW_GLIBC_G1_BLOCKED" != "0" ]]; then
    echo "error: release-strict forbids ALLOW_GLIBC_G1_BLOCKED=$ALLOW_GLIBC_G1_BLOCKED" >&2
    exit 1
  fi
  if [[ "$GLIBC_G1B_ALLOW_BLOCKED" != "0" ]]; then
    echo "error: release-strict forbids GLIBC_G1B_ALLOW_BLOCKED=$GLIBC_G1B_ALLOW_BLOCKED" >&2
    exit 1
  fi
  if [[ "$RUN_GLIBC_G1B" != "1" ]]; then
    echo "error: release-strict requires RUN_GLIBC_G1B=1" >&2
    exit 1
  fi
fi

if [[ -n "$MULTI_AGENT_REPORT$MULTI_AGENT_LANE$MULTI_AGENT_RUN_ID$MULTI_AGENT_OUT" ]]; then
  if [[ -z "$MULTI_AGENT_REPORT" || -z "$MULTI_AGENT_LANE" || -z "$MULTI_AGENT_RUN_ID" ]]; then
    echo "error: multi-agent runtime context requires MULTI_AGENT_REPORT, MULTI_AGENT_LANE, and MULTI_AGENT_RUN_ID together" >&2
    exit 1
  fi
fi

echo
echo "-- Multi-agent static checklist gate"
STATIC_PHASE_ARGS=()
if [[ -n "$MULTI_AGENT_ACTIVE_PHASE" ]]; then
  STATIC_PHASE_ARGS+=(--active-phase "$MULTI_AGENT_ACTIVE_PHASE")
fi
python3 "$ROOT/tools/bringup/check_multi_agent_gates.py" \
  --strict-always \
  --mode static \
  --manifest "$MULTI_AGENT_MANIFEST" \
  --waivers "$MULTI_AGENT_WAIVERS" \
  --checklists-root "$MULTI_AGENT_CHECKLISTS_ROOT" \
  ${STATIC_PHASE_ARGS[@]+"${STATIC_PHASE_ARGS[@]}"}

if [[ -z "$CLANG" ]]; then
  clang_candidates=()
  case "$TOOLCHAIN_LANE" in
    external)
      clang_candidates=(
        "$HOME/llvm-project/build-linxisa-clang/bin/clang"
        "$ROOT/compiler/llvm/build-linxisa-clang/bin/clang"
      )
      ;;
    pin)
      clang_candidates=(
        "$ROOT/compiler/llvm/build-linxisa-clang/bin/clang"
        "$HOME/llvm-project/build-linxisa-clang/bin/clang"
      )
      ;;
    auto)
      clang_candidates=(
        "$HOME/llvm-project/build-linxisa-clang/bin/clang"
        "$ROOT/compiler/llvm/build-linxisa-clang/bin/clang"
      )
      ;;
    *)
      echo "error: invalid TOOLCHAIN_LANE='$TOOLCHAIN_LANE' (expected: external|pin|auto)" >&2
      exit 1
      ;;
  esac
  for cand in "${clang_candidates[@]}"; do
    if [[ -x "$cand" ]]; then
      CLANG="$cand"
      break
    fi
  done
fi
if [[ -z "$LLD" && -n "$CLANG" ]]; then
  cand="$(cd "$(dirname "$CLANG")" && pwd)/ld.lld"
  if [[ -x "$cand" ]]; then
    LLD="$cand"
  fi
fi
if [[ -z "$QEMU" ]]; then
  qemu_candidates=()
  case "$QEMU_LANE" in
    pin)
      qemu_candidates=(
        "$ROOT/emulator/qemu/build/qemu-system-linx64"
        "$ROOT/emulator/qemu/build-tci/qemu-system-linx64"
      )
      ;;
    external)
      qemu_candidates=(
        "$ROOT/emulator/qemu/build/qemu-system-linx64"
        "$ROOT/emulator/qemu/build-tci/qemu-system-linx64"
      )
      ;;
    auto)
      qemu_candidates=(
        "$ROOT/emulator/qemu/build/qemu-system-linx64"
        "$ROOT/emulator/qemu/build-tci/qemu-system-linx64"
      )
      ;;
    *)
      echo "error: invalid QEMU_LANE='$QEMU_LANE' (expected: auto|pin|external)" >&2
      exit 1
      ;;
  esac
  for cand in "${qemu_candidates[@]}"; do
    if [[ -x "$cand" ]]; then
      QEMU="$cand"
      break
    fi
  done
fi

if [[ -z "$CLANG" || ! -x "$CLANG" ]]; then
  echo "error: CLANG not found; set CLANG=/path/to/clang" >&2
  exit 1
fi
if [[ -z "$LLD" || ! -x "$LLD" ]]; then
  echo "error: LLD not found; set LLD=/path/to/ld.lld" >&2
  exit 1
fi
if [[ -z "$QEMU" || ! -x "$QEMU" ]]; then
  echo "error: QEMU not found; set QEMU=/path/to/qemu-system-linx64" >&2
  exit 1
fi
echo "info: selected TOOLCHAIN lane=$TOOLCHAIN_LANE clang=$CLANG lld=$LLD"
echo "info: selected QEMU lane=$QEMU_LANE qemu=$QEMU"
echo "info: Linux runtime IRQ policy LINX_DISABLE_TIMER_IRQ=$LINX_DISABLE_TIMER_IRQ"
echo "info: Emulator/system IRQ policy LINX_EMU_DISABLE_TIMER_IRQ=$LINX_EMU_DISABLE_TIMER_IRQ"
echo "info: release controls RUN_GLIBC_G1B=$RUN_GLIBC_G1B GLIBC_G1B_ALLOW_BLOCKED=$GLIBC_G1B_ALLOW_BLOCKED ALLOW_GLIBC_G1_BLOCKED=$ALLOW_GLIBC_G1_BLOCKED RUN_MODEL_DIFF=$RUN_MODEL_DIFF"
echo "info: C++ controls RUN_CPP_GATES=$RUN_CPP_GATES CPP_MODE=$CPP_MODE"
echo "info: maturity audits AVS=$RUN_AVS_MATRIX_AUDIT QEMU_SYNC=$RUN_QEMU_OPCODE_SYNC_AUDIT QEMU_COVERAGE=$RUN_QEMU_ISA_COVERAGE_AUDIT LINUX_DEFCONFIG=$RUN_LINUX_DEFCONFIG_AUDIT"
echo "info: extended cross gates RUN_EXTENDED_CROSS_GATES=$RUN_EXTENDED_CROSS_GATES tier=$LINX_GATE_TIER"
echo "info: extended gate toggles ARCH=$RUN_ARCH_DOCS_GATES LINXCORE=$RUN_LINXCORE_PR_GATES TESTBENCH=$RUN_TESTBENCH_PR_GATES PYC=$RUN_PYC_PR_GATES TRACE=$RUN_TRACE_PR_GATES N_LINXCORE=$RUN_LINXCORE_NIGHTLY_GATES N_PYC=$RUN_PYC_NIGHTLY_GATES N_TRACE=$RUN_TRACE_NIGHTLY_GATES PERF=$RUN_PERF_FLOOR_GATES"
echo "info: spec toggles PR=$RUN_SPEC_PR_GATES NIGHTLY=$RUN_SPEC_NIGHTLY_GATES NIGHTLY_REPORT_ONLY=$SPEC_NIGHTLY_REPORT_ONLY INPUT_SET=$SPEC_INPUT_SET"

echo
echo "-- Compiler AVS gate"
(cd "$ROOT/avs/compiler/linx-llvm/tests" && CLANG="$CLANG" ./run.sh)

if [[ "$RUN_AVS_MATRIX_AUDIT" == "1" ]]; then
  echo
  echo "-- AVS matrix status artifact audit"
  python3 "$ROOT/tools/bringup/check_avs_matrix_status.py" \
    --matrix "$ROOT/avs/linx_avs_v1_test_matrix.yaml" \
    --status "$ROOT/avs/linx_avs_v1_test_matrix_status.json" \
    --report-out "$ROOT/docs/bringup/gates/avs_matrix_status_audit.json"
fi

echo
echo "-- Handwritten asm t/u target audit"
bash "$ROOT/tools/ci/check_linx_no_tu_targets.sh"

if [[ "$RUN_CPP_GATES" == "1" ]]; then
  CLANGXX="$(cd "$(dirname "$CLANG")" && pwd)/clang++"
  if [[ ! -x "$CLANGXX" ]]; then
    echo "error: clang++ not found next to clang: $CLANGXX" >&2
    exit 1
  fi

  echo
  echo "-- C++ runtime overlay build (musl, C++17 no-EH/no-RTTI)"
  CLANG="$CLANG" CLANGXX="$CLANGXX" LLD="$LLD" \
    bash "$ROOT/tools/build_linx_llvm_cpp_runtimes.sh" --mode "$CPP_MODE"

  echo
  echo "-- C++ compile/link gate (musl, C++17 no-EH/no-RTTI)"
  (cd "$ROOT/avs/compiler/linx-llvm/tests" && \
    CLANGXX="$CLANGXX" MODE="$CPP_MODE" TARGET="linx64-unknown-linux-musl" LINK_MODE="both" ./run_cpp.sh)
fi

echo
echo "-- QEMU strict system gate"
(cd "$ROOT/avs/qemu" && LINX_DISABLE_TIMER_IRQ="$LINX_EMU_DISABLE_TIMER_IRQ" CLANG="$CLANG" LLD="$LLD" QEMU="$QEMU" ./check_system_strict.sh)

if [[ "$RUN_ARCH_DOCS_GATES" == "1" ]]; then
  echo
  echo "-- Architecture contract gates"
  python3 "$ROOT/tools/bringup/check_linxcore_arch_contract.py" --root "$ROOT" --strict
  python3 "$ROOT/tools/bringup/check_linxcore_arch_contract.py" --root "$ROOT" --strict --require-mkdocs
fi

if [[ "$RUN_LINXCORE_PR_GATES" == "1" ]]; then
  echo
  echo "-- LinxCore PR gates"
  bash "$ROOT/rtl/LinxCore/tests/test_stage_connectivity.sh"
  bash "$ROOT/rtl/LinxCore/tests/test_opcode_parity.sh"
  bash "$ROOT/rtl/LinxCore/tests/test_runner_protocol.sh"
  bash "$ROOT/rtl/LinxCore/tests/test_trace_schema_and_mem.sh"
  bash "$ROOT/rtl/LinxCore/tests/test_cosim_smoke.sh"
fi

if [[ "$RUN_TESTBENCH_PR_GATES" == "1" ]]; then
  echo
  echo "-- Testbench PR gates"
  bash "$ROOT/rtl/LinxCore/tests/test_rob_bookkeeping.sh"
  bash "$ROOT/rtl/LinxCore/tests/test_block_struct_pyc_flow.sh"
fi

if [[ "$RUN_PYC_PR_GATES" == "1" ]]; then
  echo
  echo "-- pyCircuit PR gates"
  bash "$ROOT/tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh"
  bash "$ROOT/tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh"
  python3 "$ROOT/tools/bringup/check_pycircuit_interface_contract.py" --root "$ROOT" --strict
fi

if [[ "$RUN_TRACE_PR_GATES" == "1" ]]; then
  echo
  echo "-- LinxTrace PR gates"
  python3 "$ROOT/rtl/LinxCore/tools/linxcoresight/lint_trace_contract_sync.py"
  bash "$ROOT/rtl/LinxCore/tests/test_konata_sanity.sh"
  python3 "$ROOT/tools/bringup/check_trace_semver_compat.py" --root "$ROOT" --strict
fi

if [[ "$RUN_SPEC_PR_GATES" == "1" ]]; then
  echo
  echo "-- SPEC PR gates (Stage-A xcheck)"
  SPEC_INPUT_SET="$SPEC_INPUT_SET" \
    bash "$ROOT/rtl/LinxCore/tests/test_specint_stage_a_xcheck.sh"
fi

if [[ "$RUN_QEMU_OPCODE_SYNC_AUDIT" == "1" ]]; then
  echo
  echo "-- QEMU opcode meta/id sync audit"
  python3 "$ROOT/tools/bringup/check_qemu_opcode_meta_sync.py" \
    --qemu-root "$ROOT/emulator/qemu" \
    --allowlist "$ROOT/docs/bringup/qemu_opcode_sync_allowlist.json" \
    --report-out "$ROOT/docs/bringup/gates/qemu_opcode_sync_latest.json" \
    --out-md "$ROOT/docs/bringup/gates/qemu_opcode_sync_latest.md"
fi

if [[ "$RUN_QEMU_ISA_COVERAGE_AUDIT" == "1" ]]; then
  echo
  echo "-- ISA vs QEMU coverage report"
  python3 "$ROOT/tools/bringup/report_qemu_isa_coverage.py" \
    --spec "$ROOT/isa/v0.4/linxisa-v0.4.json" \
    --qemu-meta "$ROOT/emulator/qemu/target/linx/linx_opcode_meta_gen.h" \
    --report-out "$ROOT/docs/bringup/gates/qemu_isa_coverage_latest.json" \
    --out-md "$ROOT/docs/bringup/gates/qemu_isa_coverage_latest.md"
fi

LINUX_ROOT="${LINUX_ROOT:-$ROOT/kernel/linux}"
if [[ ! -d "$LINUX_ROOT/tools/linxisa/initramfs" ]]; then
  echo "error: Linux initramfs tooling not found at $LINUX_ROOT/tools/linxisa/initramfs" >&2
  exit 1
fi
if [[ ! -f "$LINUX_ROOT/tools/linxisa/busybox_rootfs/boot.py" ]]; then
  echo "error: Linux busybox rootfs tooling not found at $LINUX_ROOT/tools/linxisa/busybox_rootfs/boot.py" >&2
  exit 1
fi

if [[ "$RUN_LINUX_DEFCONFIG_AUDIT" == "1" ]]; then
  echo
  echo "-- Linux defconfig 9p/virtio compatibility audit"
  python3 "$ROOT/tools/bringup/check_linx_virt_defconfig_spec.py" \
    --defconfig "$LINUX_ROOT/arch/linx/configs/linxisa_virt_defconfig" \
    --report-out "$ROOT/docs/bringup/gates/linxisa_virt_defconfig_audit.json"
fi

echo
echo "-- Linux initramfs smoke/full"
LINX_DISABLE_TIMER_IRQ="$LINX_DISABLE_TIMER_IRQ" QEMU="$QEMU" python3 "$LINUX_ROOT/tools/linxisa/initramfs/smoke.py"
LINX_DISABLE_TIMER_IRQ="$LINX_DISABLE_TIMER_IRQ" QEMU="$QEMU" python3 "$LINUX_ROOT/tools/linxisa/initramfs/full_boot.py"
LINX_DISABLE_TIMER_IRQ="$LINX_DISABLE_TIMER_IRQ" QEMU="$QEMU" python3 "$LINUX_ROOT/tools/linxisa/busybox_rootfs/boot.py"

echo
echo "-- musl runtime smoke (phase-b, static+shared)"
MUSL_MODE="${MUSL_MODE:-phase-b}"
MUSL_SUMMARY_DIR="${MUSL_SUMMARY_DIR:-$ROOT/avs/qemu/out/musl-smoke}"
set +e
LINX_DISABLE_TIMER_IRQ="$LINX_DISABLE_TIMER_IRQ" \
  python3 "$ROOT/avs/qemu/run_musl_smoke.py" --mode "$MUSL_MODE" --link both --qemu "$QEMU"
MUSL_COMBINED_RC=$?
set -e
if [[ "$MUSL_COMBINED_RC" -ne 0 ]]; then
  echo "note: combined musl run returned rc=$MUSL_COMBINED_RC; validating per-mode summaries." >&2
fi

for mode in static shared; do
  summary="$MUSL_SUMMARY_DIR/summary_${mode}.json"
  if [[ ! -f "$summary" ]]; then
    echo "error: missing musl ${mode} summary: $summary" >&2
    exit 1
  fi
  python3 - "$summary" "$mode" <<'PY'
import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
mode = sys.argv[2]
data = json.loads(summary_path.read_text(encoding="utf-8"))
result = data.get("result", {})
ok = bool(result.get("ok", False))
classification = str(result.get("classification", "unknown"))
if not ok:
    print(
        f"error: musl {mode} gate failed ({classification}) from {summary_path}",
        file=sys.stderr,
    )
    raise SystemExit(1)
print(f"ok: musl {mode} gate passed ({summary_path})")
PY
done

if [[ "$RUN_CPP_GATES" == "1" ]]; then
  CLANGXX="$(cd "$(dirname "$CLANG")" && pwd)/clang++"
  CPP_SUMMARY_DIR="${CPP_SUMMARY_DIR:-$ROOT/avs/qemu/out/musl-smoke-cpp}"
  echo
  echo "-- musl C++17 runtime smoke (static+shared)"
  LINX_DISABLE_TIMER_IRQ="$LINX_DISABLE_TIMER_IRQ" \
    python3 "$ROOT/avs/qemu/run_musl_smoke.py" \
      --mode "$CPP_MODE" \
      --sample cpp17_smoke \
      --link both \
      --clang "$CLANG" \
      --clangxx "$CLANGXX" \
      --lld "$LLD" \
      --qemu "$QEMU" \
      --out-dir "$CPP_SUMMARY_DIR"
fi

if [[ "$RUN_GLIBC_G1" == "1" ]]; then
  if [[ ! -x "$GLIBC_G1_SCRIPT" ]]; then
    echo "error: glibc G1 script not found: $GLIBC_G1_SCRIPT" >&2
    exit 1
  fi
  echo
  echo "-- glibc G1 build gate"
  bash "$GLIBC_G1_SCRIPT"
fi

GLIBC_SUMMARY="${GLIBC_SUMMARY:-$ROOT/out/libc/glibc/logs/summary.txt}"
if [[ ! -f "$GLIBC_SUMMARY" ]]; then
  echo "error: glibc G1 summary not found: $GLIBC_SUMMARY" >&2
  exit 1
fi

echo
echo "-- glibc G1 status"
cat "$GLIBC_SUMMARY"
if grep -Eiq "(blocked|fail|error)" "$GLIBC_SUMMARY"; then
  if [[ "$ALLOW_GLIBC_G1_BLOCKED" == "1" ]]; then
    echo "note: glibc G1 is blocked (ALLOW_GLIBC_G1_BLOCKED=1 set)." >&2
  else
    echo "error: glibc G1 is blocked; strict gate failed." >&2
    exit 1
  fi
fi

if [[ "$RUN_GLIBC_G1B" == "1" ]]; then
  if [[ ! -x "$GLIBC_G1B_SCRIPT" ]]; then
    echo "error: glibc G1b script not found: $GLIBC_G1B_SCRIPT" >&2
    exit 1
  fi
  echo
  echo "-- glibc G1b shared libc.so gate"
  GLIBC_G1B_ALLOW_BLOCKED="$GLIBC_G1B_ALLOW_BLOCKED" bash "$GLIBC_G1B_SCRIPT"

  GLIBC_G1B_SUMMARY="${GLIBC_G1B_SUMMARY:-$ROOT/out/libc/glibc/logs/g1b-summary.txt}"
  if [[ ! -f "$GLIBC_G1B_SUMMARY" ]]; then
    echo "error: glibc G1b summary not found: $GLIBC_G1B_SUMMARY" >&2
    exit 1
  fi
  echo
  echo "-- glibc G1b status"
  cat "$GLIBC_G1B_SUMMARY"

  if grep -Eiq "status:[[:space:]]*blocked" "$GLIBC_G1B_SUMMARY"; then
    if [[ "$GLIBC_G1B_ALLOW_BLOCKED" == "1" ]]; then
      echo "note: glibc G1b is blocked (GLIBC_G1B_ALLOW_BLOCKED=1 set)." >&2
    else
      echo "error: glibc G1b is blocked; strict gate failed." >&2
      exit 1
    fi
  fi
fi

if [[ "$RUN_LINXCORE_NIGHTLY_GATES" == "1" ]]; then
  echo
  echo "-- LinxCore nightly gates"
  bash "$ROOT/rtl/LinxCore/tests/test_coremark_crosscheck_1000.sh"
  bash "$ROOT/rtl/LinxCore/tests/test_cbstop_inflation_guard.sh"
fi

if [[ "$RUN_SPEC_NIGHTLY_GATES" == "1" ]]; then
  echo
  echo "-- SPEC nightly gates (full xcheck)"
  SPEC_INPUT_SET="$SPEC_INPUT_SET" \
  SPEC_NIGHTLY_REPORT_ONLY="$SPEC_NIGHTLY_REPORT_ONLY" \
    bash "$ROOT/rtl/LinxCore/tests/test_specint_full_xcheck_nightly.sh"
fi

if [[ "$RUN_PYC_NIGHTLY_GATES" == "1" ]]; then
  echo
  echo "-- pyCircuit nightly gates"
  bash "$ROOT/tools/pyCircuit/flows/scripts/run_examples.sh"
  bash "$ROOT/tools/pyCircuit/flows/scripts/run_sims.sh"
  bash "$ROOT/tools/pyCircuit/flows/scripts/run_sims_nightly.sh"
fi

if [[ "$RUN_TRACE_NIGHTLY_GATES" == "1" ]]; then
  echo
  echo "-- LinxTrace nightly gates"
  bash "$ROOT/rtl/LinxCore/tests/test_konata_dfx_pipeview.sh"
  bash "$ROOT/rtl/LinxCore/tests/test_konata_template_pipeview.sh"
fi

if [[ "$RUN_PERF_FLOOR_GATES" == "1" ]]; then
  echo
  echo "-- LinxCore performance floor gate"
  python3 "$ROOT/tools/bringup/check_linxcore_perf_floor.py" \
    --root "$ROOT" \
    --max-regression "$PERF_MAX_REGRESSION" \
    --out "$ROOT/docs/bringup/gates/linxcore_perf_floor_latest.json"
fi

if [[ "$RUN_MODEL_DIFF" == "1" ]]; then
  echo
  echo "-- QEMU vs model differential suite"
  python3 "$ROOT/tools/bringup/run_model_diff_suite.py" \
    --root "$ROOT" \
    --suite "$ROOT/avs/model/linx_model_diff_suite.yaml" \
    --profile "$LINX_BRINGUP_PROFILE" \
    --trace-schema-version "${LINX_TRACE_SCHEMA_VERSION:-1.0}" \
    --report-out "$ROOT/docs/bringup/gates/model_diff_summary.json"
fi

MULTI_AGENT_SUMMARY_PATH=""
if [[ -n "$MULTI_AGENT_REPORT" && -n "$MULTI_AGENT_LANE" && -n "$MULTI_AGENT_RUN_ID" ]]; then
  if [[ -n "$MULTI_AGENT_OUT" ]]; then
    MULTI_AGENT_SUMMARY_PATH="$MULTI_AGENT_OUT"
  else
    MULTI_AGENT_SUMMARY_PATH="$ROOT/docs/bringup/gates/logs/$MULTI_AGENT_RUN_ID/$MULTI_AGENT_LANE/multi_agent_summary.strict_cross.json"
  fi
  echo
  echo "-- Multi-agent runtime closure gate"
  RUNTIME_PHASE_ARGS=()
  if [[ -n "$MULTI_AGENT_ACTIVE_PHASE" ]]; then
    RUNTIME_PHASE_ARGS+=(--active-phase "$MULTI_AGENT_ACTIVE_PHASE")
  fi
  python3 "$ROOT/tools/bringup/check_multi_agent_gates.py" \
    --strict-always \
    --mode runtime \
    --manifest "$MULTI_AGENT_MANIFEST" \
    --waivers "$MULTI_AGENT_WAIVERS" \
    --checklists-root "$MULTI_AGENT_CHECKLISTS_ROOT" \
    --report "$MULTI_AGENT_REPORT" \
    --lane "$MULTI_AGENT_LANE" \
    --run-id "$MULTI_AGENT_RUN_ID" \
    --out "$MULTI_AGENT_SUMMARY_PATH" \
    ${RUNTIME_PHASE_ARGS[@]+"${RUNTIME_PHASE_ARGS[@]}"}
else
  echo "note: skipping multi-agent runtime closure gate (report context unavailable)"
fi

if [[ "$LINX_BRINGUP_PROFILE" == "release-strict" && "$RUN_CONSISTENCY_CHECKS" == "1" ]]; then
  echo
  echo "-- bring-up consistency/freshness checks"
  CONSISTENCY_MULTI_AGENT_ARGS=()
  CONSISTENCY_PERF_ARGS=()
  if [[ -n "$MULTI_AGENT_SUMMARY_PATH" ]]; then
    CONSISTENCY_MULTI_AGENT_ARGS+=(--multi-agent-summary "$MULTI_AGENT_SUMMARY_PATH")
  fi
  if [[ "$RUN_PERF_FLOOR_GATES" == "1" ]]; then
    CONSISTENCY_PERF_ARGS+=(
      --linxcore-perf-floor "$ROOT/docs/bringup/gates/linxcore_perf_floor_latest.json"
      --require-perf-floor-artifact
    )
  fi
  python3 "$ROOT/tools/bringup/check_gate_consistency.py" \
    --report "$ROOT/docs/bringup/gates/latest.json" \
    --progress "$ROOT/docs/bringup/PROGRESS.md" \
    --gate-status "$ROOT/docs/bringup/GATE_STATUS.md" \
    --libc-status "$ROOT/docs/bringup/libc_status.md" \
    --avs-matrix-audit "$ROOT/docs/bringup/gates/avs_matrix_status_audit.json" \
    --qemu-opcode-sync "$ROOT/docs/bringup/gates/qemu_opcode_sync_latest.json" \
    --qemu-isa-coverage "$ROOT/docs/bringup/gates/qemu_isa_coverage_latest.json" \
    --linux-defconfig-audit "$ROOT/docs/bringup/gates/linxisa_virt_defconfig_audit.json" \
    --require-maturity-artifacts \
    --profile "$LINX_BRINGUP_PROFILE" \
    --lane-policy "${LINX_LANE_POLICY:-external+pin-required}" \
    --trace-schema-version "${LINX_TRACE_SCHEMA_VERSION:-1.0}" \
    --max-age-hours "${LINX_GATE_MAX_AGE_HOURS:-24}" \
    ${CONSISTENCY_PERF_ARGS[@]+"${CONSISTENCY_PERF_ARGS[@]}"} \
    ${CONSISTENCY_MULTI_AGENT_ARGS[@]+"${CONSISTENCY_MULTI_AGENT_ARGS[@]}"}
fi

echo
echo "ok: strict cross-repo gate passed"
