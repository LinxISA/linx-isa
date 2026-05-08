#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROFILE="${LINX_BRINGUP_PROFILE:-release-strict}"
TIER="${LINX_GATE_TIER:-pr}"

# Keep the historical strict-cross entrypoint as the heavier compatibility
# lane while delegating gate selection/execution to the canonical registry.
export RUN_LINUX_DEFCONFIG_AUDIT="${RUN_LINUX_DEFCONFIG_AUDIT:-1}"
export RUN_LINUX_BOOT_GATES="${RUN_LINUX_BOOT_GATES:-1}"
export RUN_PTO_PARITY_GATE="${RUN_PTO_PARITY_GATE:-1}"

ARGS=(
  --profile "$PROFILE"
  --tier "$TIER"
)

if [[ "${LINX_GATE_DRY_RUN:-0}" == "1" ]]; then
  ARGS+=(--dry-run)
fi

if [[ -n "${LINX_GATE_REPORT_OUT:-}" ]]; then
  ARGS+=(--report-out "$LINX_GATE_REPORT_OUT")
fi

if [[ "${LINX_GATE_INCLUDE_OPTIONAL:-0}" == "1" ]]; then
  ARGS+=(--include-optional)
fi

exec python3 "$ROOT/tools/bringup/run_gates.py" "${ARGS[@]}" "$@"
