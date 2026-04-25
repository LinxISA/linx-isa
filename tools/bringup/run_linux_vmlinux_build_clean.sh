#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINUX_ROOT="${LINUX_ROOT:-$ROOT/kernel/linux}"
OUT_DIR=""
CLANG_BIN="${CLANG_BIN:-}"
GMAKE_BIN="${GMAKE_BIN:-}"
HOSTCC="${HOSTCC:-/usr/bin/clang}"
HOSTCXX="${HOSTCXX:-/usr/bin/clang++}"
TARGET="${TARGET:-vmlinux}"

usage() {
  cat <<'USAGE'
Usage: tools/bringup/run_linux_vmlinux_build_clean.sh [options]

Options:
  --linux-root PATH   Linux source tree (default: $ROOT/kernel/linux)
  --out-dir PATH      Kernel O= directory (default: <linux-root>/build-linx-fixed)
  --clang PATH        Clang executable for CC
  --gmake PATH        gmake/make executable
  --hostcc PATH       Host C compiler (default: /usr/bin/clang)
  --hostcxx PATH      Host C++ compiler (default: /usr/bin/clang++)
  --target NAME       Make target (default: vmlinux)
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --linux-root)
      LINUX_ROOT="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --clang)
      CLANG_BIN="$2"
      shift 2
      ;;
    --gmake)
      GMAKE_BIN="$2"
      shift 2
      ;;
    --hostcc)
      HOSTCC="$2"
      shift 2
      ;;
    --hostcxx)
      HOSTCXX="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$CLANG_BIN" || ! -x "$CLANG_BIN" ]]; then
  echo "error: --clang must point to an executable clang" >&2
  exit 2
fi
if [[ -z "$GMAKE_BIN" || ! -x "$GMAKE_BIN" ]]; then
  echo "error: --gmake must point to an executable gmake/make" >&2
  exit 2
fi
if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$LINUX_ROOT/build-linx-fixed"
fi

stash_dir="$(mktemp -d -t linx-linux-src-stash.XXXXXX)"
stashed_paths=()

restore_paths() {
  local restore_rc=0
  local idx
  for (( idx=${#stashed_paths[@]}-1 ; idx>=0 ; idx-- )); do
    local rel="${stashed_paths[$idx]}"
    local src="$stash_dir/$rel"
    local dest="$LINUX_ROOT/$rel"
    if [[ ! -e "$src" ]]; then
      continue
    fi
    mkdir -p "$(dirname "$dest")"
    if [[ -e "$dest" ]]; then
      echo "error: restore collision for $dest; preserved stashed copy at $src" >&2
      restore_rc=1
      continue
    fi
    mv "$src" "$dest"
  done
  rmdir "$stash_dir" 2>/dev/null || true
  return "$restore_rc"
}

cleanup() {
  local rc=$?
  if ! restore_paths; then
    rc=1
  fi
  exit "$rc"
}
trap cleanup EXIT INT TERM

paths=(
  ".config"
  "include/config"
  "include/generated"
  "arch/linx/include/generated"
)

for rel in "${paths[@]}"; do
  src="$LINUX_ROOT/$rel"
  if [[ ! -e "$src" ]]; then
    continue
  fi
  mkdir -p "$(dirname "$stash_dir/$rel")"
  mv "$src" "$stash_dir/$rel"
  stashed_paths+=("$rel")
  echo "info: stashed $src"
done

env "PATH=$(dirname "$CLANG_BIN"):$PATH" \
  "$GMAKE_BIN" \
  -C "$LINUX_ROOT" \
  ARCH=linx \
  LLVM="$(dirname "$CLANG_BIN")/" \
  "CC=$CLANG_BIN --target=linx64-unknown-linux-gnu -fintegrated-as" \
  "HOSTCC=$HOSTCC" \
  "HOSTCXX=$HOSTCXX" \
  "O=$OUT_DIR" \
  "$TARGET"
