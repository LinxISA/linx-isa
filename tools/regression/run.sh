#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROFILE="${LINX_BRINGUP_PROFILE:-release-strict}"
TIER="${LINX_GATE_TIER:-pr}"

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
