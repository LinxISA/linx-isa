#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINUX_ROOT="${LINUX_ROOT:-$ROOT/kernel/linux}"
OUT_DIR="${OUT_DIR:-/tmp/linx-linux-smp-head-build}"
CLANG_BIN="${CLANG_BIN:-$ROOT/compiler/llvm/build-linxisa-clang/bin/clang}"
GMAKE_BIN="${GMAKE_BIN:-/opt/homebrew/bin/gmake}"
JOBS="${JOBS:-4}"

usage() {
  cat <<'USAGE'
Usage: tools/bringup/run_linux_smp_head_build_clean.sh [options]

Options:
  --linux-root PATH  Linux source checkout
  --out-dir PATH     Dedicated O= directory
  --clang PATH       Linx clang executable
  --gmake PATH       GNU make executable
  --jobs N           Parallel job count
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --linux-root) LINUX_ROOT="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    --clang) CLANG_BIN="$2"; shift 2 ;;
    --gmake) GMAKE_BIN="$2"; shift 2 ;;
    --jobs) JOBS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! -d "$LINUX_ROOT" || ! -x "$CLANG_BIN" || ! -x "$GMAKE_BIN" ]]; then
  echo "error: valid --linux-root, --clang, and --gmake are required" >&2
  exit 2
fi

LINUX_ROOT="$(cd "$LINUX_ROOT" && pwd)"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
if [[ "$OUT_DIR" == "$LINUX_ROOT" || "$OUT_DIR" == "$LINUX_ROOT"/* ]]; then
  echo "error: --out-dir must be outside the Linux source tree" >&2
  exit 2
fi

TOOL_DIR="$(dirname "$CLANG_BIN")"
COMMON=(
  "$GMAKE_BIN"
  -C "$LINUX_ROOT"
  ARCH=linx
  "O=$OUT_DIR"
  "LLVM=$TOOL_DIR/"
  "CC=$CLANG_BIN --target=linx64-unknown-linux-gnu -fintegrated-as"
  HOSTCC=/usr/bin/clang
  HOSTCXX=/usr/bin/clang++
  KALLSYMS_EXTRA_PASS=128
  "-j$JOBS"
)

env "PATH=$TOOL_DIR:$PATH" "${COMMON[@]}" linx_v150_defconfig
"$LINUX_ROOT/scripts/config" --file "$OUT_DIR/.config" --enable SMP
env "PATH=$TOOL_DIR:$PATH" "${COMMON[@]}" olddefconfig

if ! grep -qx 'CONFIG_SMP=y' "$OUT_DIR/.config"; then
  echo "error: CONFIG_SMP=y was not retained by olddefconfig" >&2
  exit 1
fi

env "PATH=$TOOL_DIR:$PATH" "${COMMON[@]}" arch/linx/kernel/head.o
HEAD_OBJECT="$OUT_DIR/arch/linx/kernel/head.o"
if [[ ! -s "$HEAD_OBJECT" ]]; then
  echo "error: SMP head object was not produced: $HEAD_OBJECT" >&2
  exit 1
fi

printf '%s\n' "$HEAD_OBJECT"
