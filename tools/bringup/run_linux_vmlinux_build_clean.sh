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
PROVENANCE_OUT=""
PROVENANCE_OUT_EXPLICIT=0
PROVENANCE_HELPER="$ROOT/tools/bringup/linux_vmlinux_provenance.py"

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
  --provenance-out PATH
                      Mandatory vmlinux provenance output (default: <out-dir>/vmlinux.provenance.json)

Behavior:
  Reuses the same O= directory incrementally unless --fresh is selected. It
  only stashes source-tree generated/config files that would otherwise
  contaminate the in-tree build. Every successful vmlinux build atomically
  writes and verifies deterministic source/tool/config/output provenance.
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
    --provenance-out)
      PROVENANCE_OUT="$2"
      PROVENANCE_OUT_EXPLICIT=1
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
if [[ -z "$PROVENANCE_OUT" ]]; then
  PROVENANCE_OUT="$OUT_DIR/vmlinux.provenance.json"
elif [[ "$PROVENANCE_OUT" != /* ]]; then
  PROVENANCE_OUT="$ROOT/$PROVENANCE_OUT"
fi
PROVENANCE_PARENT="$(dirname "$PROVENANCE_OUT")"
mkdir -p "$PROVENANCE_PARENT"
PROVENANCE_OUT="$(cd "$PROVENANCE_PARENT" && pwd)/$(basename "$PROVENANCE_OUT")"
if [[ "$TARGET" != "vmlinux" && "$PROVENANCE_OUT_EXPLICIT" == "1" ]]; then
  echo "error: --provenance-out is only valid with --target vmlinux" >&2
  exit 2
fi
MARKER="$OUT_DIR/.linx_linux_vmlinux_build_dir"
FRESH_GENERATION_MARKER="$OUT_DIR/.linx_linux_vmlinux_fresh_generation"
EXPECTED_MARKER="$(printf 'format=1\nlinux_root=%s\n' "$LINUX_ROOT")"
if [[ "$TARGET" == "vmlinux" && -L "$OUT_DIR" ]]; then
  echo "error: vmlinux output directory must not be a symbolic link: $OUT_DIR" >&2
  exit 2
fi
if [[ "$FRESH" == "1" ]]; then
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
fi

absolute_candidate() {
  local path="$1"
  if [[ "$path" == /* ]]; then
    printf '%s\n' "$path"
  else
    printf '%s/%s\n' "$PWD" "$path"
  fi
}

# Reject lexical, symlink, and hard-link aliases before invalidating an old
# report. In particular, a malicious --provenance-out must never delete a
# compiler, build tool, source, or output that the report is meant to bind.
reserved_paths=(
  "$OUT_DIR"
  "$OUT_DIR/vmlinux"
  "$OUT_DIR/.config"
  "$MARKER"
  "$FRESH_GENERATION_MARKER"
  "${BASH_SOURCE[0]}"
  "$PROVENANCE_HELPER"
  "$CLANG_BIN"
  "$GMAKE_BIN"
  "$HOSTCC"
  "$HOSTCXX"
)
if [[ -n "$CLANG_BIN" ]]; then
  reserved_paths+=("$(dirname "$CLANG_BIN")/ld.lld")
fi
for reserved_path in "${reserved_paths[@]}"; do
  if [[ -z "$reserved_path" ]]; then
    continue
  fi
  reserved_path="$(absolute_candidate "$reserved_path")"
  if [[ "$PROVENANCE_OUT" == "$reserved_path" ]] ||
     { [[ -e "$PROVENANCE_OUT" || -L "$PROVENANCE_OUT" ]] &&
       [[ -e "$reserved_path" || -L "$reserved_path" ]] &&
       [[ "$PROVENANCE_OUT" -ef "$reserved_path" ]]; }; then
    echo "error: provenance output aliases a bound build path: $reserved_path" >&2
    exit 2
  fi
done

# The output directory is now known to be safe to own. Invalidate any prior
# claim before tool, jobs, or build validation so no failure can leave stale
# provenance. An external provenance path is never removed before this check.
if [[ "$TARGET" == "vmlinux" ]]; then
  rm -f "$PROVENANCE_OUT"
fi
if [[ "$FRESH" == "1" ]]; then
  rm -rf "$OUT_DIR"
  mkdir -p "$OUT_DIR"
  printf '%s\n' "$EXPECTED_MARKER" > "$MARKER"
  if [[ "$TARGET" == "vmlinux" ]]; then
    printf 'format=1\nlinux_root=%s\n' "$LINUX_ROOT" > "$FRESH_GENERATION_MARKER"
  fi
else
  rm -f "$FRESH_GENERATION_MARKER"
fi

if [[ -z "$CLANG_BIN" || ! -x "$CLANG_BIN" ]]; then
  echo "error: --clang must point to an executable clang" >&2
  exit 2
fi
if [[ -z "$GMAKE_BIN" || ! -x "$GMAKE_BIN" ]]; then
  echo "error: --gmake must point to an executable gmake/make" >&2
  exit 2
fi
if [[ ! -x "$HOSTCC" ]]; then
  echo "error: HOSTCC must point to an executable compiler: $HOSTCC" >&2
  exit 2
fi
if [[ ! -x "$HOSTCXX" ]]; then
  echo "error: HOSTCXX must point to an executable compiler: $HOSTCXX" >&2
  exit 2
fi
if [[ ! -f "$PROVENANCE_HELPER" ]]; then
  echo "error: vmlinux provenance helper not found: $PROVENANCE_HELPER" >&2
  exit 2
fi
if [[ -z "$JOBS" ]]; then
  JOBS="$(sysctl -n hw.ncpu 2>/dev/null || true)"
  if [[ -n "$JOBS" && "$JOBS" -gt 4 ]]; then
    JOBS=4
  fi
fi
if [[ -z "$JOBS" ]]; then
  JOBS=1
fi
if [[ ! "$JOBS" =~ ^[1-9][0-9]*$ ]]; then
  echo "error: --jobs must be a positive integer" >&2
  exit 2
fi

CLANG_BIN="$(cd "$(dirname "$CLANG_BIN")" && pwd)/$(basename "$CLANG_BIN")"
GMAKE_BIN="$(cd "$(dirname "$GMAKE_BIN")" && pwd)/$(basename "$GMAKE_BIN")"
HOSTCC="$(cd "$(dirname "$HOSTCC")" && pwd)/$(basename "$HOSTCC")"
HOSTCXX="$(cd "$(dirname "$HOSTCXX")" && pwd)/$(basename "$HOSTCXX")"
LD_LLD_BIN="$(dirname "$CLANG_BIN")/ld.lld"
provenance_temp_dir=""
pre_state=""
pre_config=""
pre_fresh_marker=""
config_command_file=""
target_command_file=""
if [[ "$TARGET" == "vmlinux" ]]; then
  if [[ ! -x "$LD_LLD_BIN" ]]; then
    echo "error: ld.lld not found beside clang: $LD_LLD_BIN" >&2
    exit 2
  fi
  provenance_temp_dir="$(mktemp -d -t linx-vmlinux-provenance.XXXXXX)"
  pre_state="$provenance_temp_dir/pre-state.json"
  pre_config="$provenance_temp_dir/pre-config.json"
  pre_fresh_marker="$provenance_temp_dir/pre-fresh-marker.json"
  config_command_file="$provenance_temp_dir/config-command.argv0"
  target_command_file="$provenance_temp_dir/target-command.argv0"
  if ! python3 "$PROVENANCE_HELPER" snapshot \
      --linux-root "$LINUX_ROOT" \
      --clang "$CLANG_BIN" \
      --ld-lld "$LD_LLD_BIN" \
      --gmake "$GMAKE_BIN" \
      --hostcc "$HOSTCC" \
      --hostcxx "$HOSTCXX" \
      --script "${BASH_SOURCE[0]}" \
      --out "$pre_state"; then
    rm -rf "$provenance_temp_dir"
    exit 2
  fi
  if [[ "$FRESH" == "1" ]]; then
    python3 "$PROVENANCE_HELPER" file-snapshot \
      --path "$FRESH_GENERATION_MARKER" \
      --label "fresh generation marker" \
      --out "$pre_fresh_marker"
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
    if [[ ! -e "$src" && ! -L "$src" ]]; then
      continue
    fi
    mkdir -p "$(dirname "$dest")"
    if [[ -e "$dest" || -L "$dest" ]]; then
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
  if [[ -n "$provenance_temp_dir" ]]; then
    rm -rf "$provenance_temp_dir"
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
  if [[ ! -e "$src" && ! -L "$src" ]]; then
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

config_command=()
if [[ "$REFRESH_DEFCONFIG" == "1" || ! -f "$OUT_DIR/.config" ]]; then
  echo "info: seeding fresh kernel config with $DEFCONFIG_TARGET + olddefconfig"
  config_command=(
    env "PATH=$(dirname "$CLANG_BIN"):$PATH"
    "${make_common[@]}"
    "$DEFCONFIG_TARGET"
    olddefconfig
  )
  if [[ "$TARGET" == "vmlinux" ]]; then
    printf '%s\0' "${config_command[@]}" > "$config_command_file"
  fi
  "${config_command[@]}"
fi

if [[ "$TARGET" == "vmlinux" ]]; then
  python3 "$PROVENANCE_HELPER" file-snapshot \
    --path "$OUT_DIR/.config" \
    --label "kernel config" \
    --out "$pre_config"
fi

target_command=(
  env "PATH=$(dirname "$CLANG_BIN"):$PATH"
  "${make_common[@]}"
  "$TARGET"
)
if [[ "$TARGET" == "vmlinux" ]]; then
  printf '%s\0' "${target_command[@]}" > "$target_command_file"
  # A successful no-op make must never certify an artifact from an earlier
  # generation. The target command must recreate this exact output.
  rm -f "$OUT_DIR/vmlinux"
fi
"${target_command[@]}"

if [[ "$TARGET" == "vmlinux" && ! -s "$OUT_DIR/vmlinux" ]]; then
  echo "error: vmlinux was not produced: $OUT_DIR/vmlinux" >&2
  exit 1
fi

if [[ "$TARGET" == "vmlinux" ]]; then
  if ! restore_paths; then
    echo "error: failed to restore Linux source after build" >&2
    exit 1
  fi
  stashed_paths=()

  collect_command=(
    python3 "$PROVENANCE_HELPER" collect
    --linux-root "$LINUX_ROOT"
    --clang "$CLANG_BIN"
    --ld-lld "$LD_LLD_BIN"
    --gmake "$GMAKE_BIN"
    --hostcc "$HOSTCC"
    --hostcxx "$HOSTCXX"
    --config "$OUT_DIR/.config"
    --vmlinux "$OUT_DIR/vmlinux"
    --script "${BASH_SOURCE[0]}"
    --pre-state "$pre_state"
    --pre-config "$pre_config"
    --out-dir "$OUT_DIR"
    --out "$PROVENANCE_OUT"
    --mode "$([[ "$FRESH" == "1" ]] && printf fresh || printf incremental)"
    --target "$TARGET"
    --arch linx
    --defconfig-target "$DEFCONFIG_TARGET"
    --jobs "$JOBS"
    --kallsyms-extra-pass "$KALLSYMS_EXTRA_PASS"
  )
  if [[ "$REFRESH_DEFCONFIG" == "1" ]]; then
    collect_command+=(--refresh-defconfig)
  fi
  if [[ "$FRESH" == "1" ]]; then
    collect_command+=(--pre-fresh-marker "$pre_fresh_marker")
  fi
  if [[ "${#config_command[@]}" -gt 0 ]]; then
    collect_command+=(--command-file "$config_command_file")
  fi
  collect_command+=(--command-file "$target_command_file")
  "${collect_command[@]}"

  trap - EXIT INT TERM
  rm -rf "$provenance_temp_dir"
fi
