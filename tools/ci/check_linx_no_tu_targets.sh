#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PATTERN='->[[:space:]]*([tu]([0-9]+)?)\b'

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

scan() {
  local base="$1"
  local glob="$2"
  if [[ ! -d "$base" ]]; then
    return 0
  fi
  rg -n --no-heading --glob "$glob" -- "$PATTERN" "$base" >>"$tmp" || true
}

scan "$REPO_ROOT/kernel/linux/arch/linx" "**/*.S"
scan "$REPO_ROOT/lib/glibc/sysdeps/linx" "**/*.S"
scan "$REPO_ROOT/avs/runtime/freestanding" "**/*.s"
scan "$REPO_ROOT/avs/runtime/freestanding" "**/*.S"
scan "$REPO_ROOT/avs/qemu/tests" "*.S"

if [[ -s "$tmp" ]]; then
  echo "error: found forbidden t/u register targets in handwritten assembly:" >&2
  cat "$tmp" >&2
  exit 1
fi

echo "PASS: no forbidden t/u register targets found"
