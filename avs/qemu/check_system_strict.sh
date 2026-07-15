#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_LOG="${OUT_LOG:-$SCRIPT_DIR/out/system_strict.log}"
RETRIES="${RETRIES:-3}"
STRICT_TIMER_IRQ_DISABLE="${STRICT_TIMER_IRQ_DISABLE:-0}"
HEARTBEAT_SEC="${HEARTBEAT_SEC:-2}"
NO_PROGRESS_TIMEOUT="${NO_PROGRESS_TIMEOUT:-0}"
mkdir -p "$(dirname "$OUT_LOG")"

if [[ -z "${QEMU:-}" || ! -x "$QEMU" ]]; then
  echo "error: strict system lane requires QEMU to name an explicit executable" >&2
  exit 2
fi
python3 - "$ROOT" "$QEMU" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "tools" / "bringup"))
from qemu_build_paths import qemu_binary_provenance

provenance = qemu_binary_provenance(root, Path(sys.argv[2]))
if not provenance["clean_build_for_head"]:
    raise SystemExit(
        "error: strict system lane requires a clean HEAD-matched QEMU build: "
        + json.dumps(provenance, sort_keys=True)
    )
PY

CMD=(
  python3 "$SCRIPT_DIR/run_tests.py"
  --qemu "$QEMU"
  --suite system
  --timeout "${TIMEOUT:-60}"
  --heartbeat-sec "$HEARTBEAT_SEC"
  --no-progress-timeout "$NO_PROGRESS_TIMEOUT"
)

if ! [[ "$RETRIES" =~ ^[0-9]+$ ]] || [[ "$RETRIES" -lt 1 ]]; then
  echo "error: RETRIES must be a positive integer (got: $RETRIES)" >&2
  exit 2
fi

LAST_RC=1
LAST_LOG=""
for attempt in $(seq 1 "$RETRIES"); do
  ATTEMPT_LOG="$OUT_LOG.attempt$attempt"
  set +e
  LINX_DISABLE_TIMER_IRQ="$STRICT_TIMER_IRQ_DISABLE" "${CMD[@]}" >"$ATTEMPT_LOG" 2>&1
  LAST_RC=$?
  set -e
  LAST_LOG="$ATTEMPT_LOG"

  if [[ "$LAST_RC" -eq 0 ]]; then
    cat "$ATTEMPT_LOG"

    if grep -q "LINX_INSN_COUNT=" "$ATTEMPT_LOG"; then
      echo "error: unexpected LINX_INSN_COUNT debug output in strict system run" >&2
      exit 1
    fi

    if grep -q "Linx: TRACE" "$ATTEMPT_LOG"; then
      echo "error: unexpected Linx trace debug output in strict system run" >&2
      exit 1
    fi

    mv "$ATTEMPT_LOG" "$OUT_LOG"
    exit 0
  fi

  if [[ "$attempt" -lt "$RETRIES" ]]; then
    echo "warn: strict system attempt $attempt/$RETRIES failed; retrying..." >&2
    tail -n 20 "$ATTEMPT_LOG" >&2 || true
    sleep 1
  fi
done

if [[ -n "$LAST_LOG" && -f "$LAST_LOG" ]]; then
  mv "$LAST_LOG" "$OUT_LOG"
  cat "$OUT_LOG"
fi
exit "$LAST_RC"
