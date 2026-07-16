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
DEFCONFIG_TARGET="${DEFCONFIG_TARGET:-linx_v150_defconfig}"
KALLSYMS_EXTRA_PASS="${KALLSYMS_EXTRA_PASS:-128}"
JOBS="${JOBS:-}"
REFRESH_DEFCONFIG="${LINX_KERNEL_REFRESH_DEFCONFIG:-0}"
FRESH="${LINX_KERNEL_FRESH_BUILD:-0}"

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
  --defconfig NAME    Defconfig target for fresh O= dirs (default: linx_v150_defconfig)
  --refresh-defconfig Re-seed O=.config from the selected defconfig before building
  --fresh             Remove and recreate O= before building; O= must be outside the source tree
  --jobs N            Parallel job count for gmake/make

Behavior:
  Reuses the same O= directory incrementally unless --fresh is selected. It
  only stashes source-tree generated/config files that would otherwise
  contaminate the in-tree build.
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
    --defconfig)
      DEFCONFIG_TARGET="$2"
      shift 2
      ;;
    --refresh-defconfig)
      REFRESH_DEFCONFIG=1
      shift
      ;;
    --fresh)
      FRESH=1
      shift
      ;;
    --jobs)
      JOBS="$2"
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
if [[ ! -d "$LINUX_ROOT" ]]; then
  echo "error: linux root does not exist: $LINUX_ROOT" >&2
  exit 2
fi
LINUX_ROOT="$(cd "$LINUX_ROOT" && pwd)"
if [[ -z "$OUT_DIR" ]]; then
  OUT_DIR="$LINUX_ROOT/build-linx-fixed"
elif [[ "$OUT_DIR" != /* ]]; then
  OUT_DIR="$ROOT/$OUT_DIR"
fi
OUT_PARENT="$(dirname "$OUT_DIR")"
mkdir -p "$OUT_PARENT"
OUT_DIR="$(cd "$OUT_PARENT" && pwd)/$(basename "$OUT_DIR")"
if [[ "$FRESH" == "1" ]]; then
  MARKER="$OUT_DIR/.linx_linux_vmlinux_build_dir"
  EXPECTED_MARKER="$(printf 'format=1\nlinux_root=%s\n' "$LINUX_ROOT")"
  if [[ -L "$OUT_DIR" ]]; then
    echo "error: fresh output directory must not be a symbolic link: $OUT_DIR" >&2
    exit 2
  fi
  if [[ "$OUT_DIR" == "/" || "$OUT_DIR" == "$ROOT" ||
        "$OUT_DIR" == "$LINUX_ROOT" || "$OUT_DIR" == "$LINUX_ROOT"/* ||
        "$LINUX_ROOT" == "$OUT_DIR"/* ]]; then
    echo "error: fresh output directory must be outside the Linux source tree and its ancestors: $OUT_DIR" >&2
    exit 2
  fi
  if [[ -e "$OUT_DIR" && ! -d "$OUT_DIR" ]]; then
    echo "error: fresh output path is not a directory: $OUT_DIR" >&2
    exit 2
  fi
  if [[ -d "$OUT_DIR" && -n "$(find "$OUT_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    if [[ ! -f "$MARKER" || "$(cat "$MARKER")" != "$EXPECTED_MARKER" ]]; then
      echo "error: refusing to remove unowned non-empty output directory: $OUT_DIR" >&2
      exit 2
    fi
  fi
  rm -rf "$OUT_DIR"
  mkdir -p "$OUT_DIR"
  printf '%s\n' "$EXPECTED_MARKER" > "$MARKER"
fi
if [[ -z "$JOBS" ]]; then
  JOBS="$(sysctl -n hw.ncpu 2>/dev/null || true)"
  if [[ -n "$JOBS" && "$JOBS" -gt 4 ]]; then
    JOBS=4
  fi
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

make_common=(
  "$GMAKE_BIN"
  -C "$LINUX_ROOT"
  ARCH=linx
  "LLVM=$(dirname "$CLANG_BIN")/"
  "CC=$CLANG_BIN --target=linx64-unknown-linux-gnu -fintegrated-as"
  "HOSTCC=$HOSTCC"
  "HOSTCXX=$HOSTCXX"
  "KALLSYMS_EXTRA_PASS=$KALLSYMS_EXTRA_PASS"
  "O=$OUT_DIR"
)

if [[ -n "$JOBS" ]]; then
  make_common+=("-j$JOBS")
fi

if [[ "$REFRESH_DEFCONFIG" == "1" || ! -f "$OUT_DIR/.config" ]]; then
  echo "info: seeding fresh kernel config with $DEFCONFIG_TARGET + olddefconfig"
  env "PATH=$(dirname "$CLANG_BIN"):$PATH" \
    "${make_common[@]}" \
    "$DEFCONFIG_TARGET" \
    olddefconfig
fi

env "PATH=$(dirname "$CLANG_BIN"):$PATH" \
  "${make_common[@]}" \
  "$TARGET"

if [[ "$TARGET" == "vmlinux" && ! -s "$OUT_DIR/vmlinux" ]]; then
  echo "error: vmlinux was not produced: $OUT_DIR/vmlinux" >&2
  exit 1
fi
