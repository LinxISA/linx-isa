#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="${BUILD_DIR:-$ROOT/compiler/llvm/build-linxisa-clang}"
NINJA_BIN="${NINJA_BIN:-}"

usage() {
  cat <<'USAGE'
Usage: tools/bringup/run_llvm_incremental_build.sh [options] [targets...]

Options:
  --build-dir PATH   LLVM build directory (default: compiler/llvm/build-linxisa-clang)
  --ninja PATH       Ninja executable

Targets:
  Defaults to: clang llvm-mc llvm-objdump

This helper is intentionally incremental. It reuses the existing LLVM build
tree and only rebuilds the requested targets.
USAGE
}

targets=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --build-dir)
      BUILD_DIR="$2"
      shift 2
      ;;
    --ninja)
      NINJA_BIN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      targets+=("$1")
      shift
      ;;
  esac
done

if [[ -z "$NINJA_BIN" ]]; then
  for cand in "/opt/homebrew/bin/ninja" "$(command -v ninja 2>/dev/null || true)"; do
    if [[ -n "$cand" && -x "$cand" ]]; then
      NINJA_BIN="$cand"
      break
    fi
  done
fi

if [[ -z "$NINJA_BIN" || ! -x "$NINJA_BIN" ]]; then
  echo "error: ninja not found; set --ninja or NINJA_BIN" >&2
  exit 2
fi

if [[ ! -f "$BUILD_DIR/build.ninja" ]]; then
  echo "error: LLVM build directory is missing build.ninja: $BUILD_DIR" >&2
  exit 2
fi

if [[ ${#targets[@]} -eq 0 ]]; then
  targets=(clang llvm-mc llvm-objdump)
fi

echo "info: incremental LLVM build in $BUILD_DIR -> ${targets[*]}" >&2
"$NINJA_BIN" -C "$BUILD_DIR" "${targets[@]}"
