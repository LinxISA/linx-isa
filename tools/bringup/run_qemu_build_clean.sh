#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QEMU_ROOT="${QEMU_ROOT:-$ROOT/emulator/qemu}"
OUT_DIR="${OUT_DIR:-/tmp/linx-qemu-clean-build}"
WORKTREE_DIR="${WORKTREE_DIR:-/tmp/linx-qemu-clean-src}"
TARGET="${TARGET:-qemu-system-linx64}"
NINJA_BIN="${NINJA_BIN:-}"
ALLOW_DIRTY_SOURCE_FALLBACK="${LINX_QEMU_ALLOW_DIRTY_SOURCE_FALLBACK:-0}"

usage() {
  cat <<'USAGE'
Usage: tools/bringup/run_qemu_build_clean.sh [options]

Options:
  --qemu-root PATH     QEMU source tree (default: $ROOT/emulator/qemu)
  --out-dir PATH       Clean build directory (default: /tmp/linx-qemu-clean-build)
  --worktree PATH      Detached clean worktree (default: /tmp/linx-qemu-clean-src)
  --target NAME        Build target (default: qemu-system-linx64)
  --ninja PATH         Ninja executable

Behavior:
  Reuses the same out-dir incrementally once configured. This is the preferred
  reproducible QEMU build path for bring-up iterations.

Stdout:
  Prints the absolute path to the requested built target on success.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --qemu-root)
      QEMU_ROOT="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --worktree)
      WORKTREE_DIR="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
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
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$QEMU_ROOT/.git" && ! -f "$QEMU_ROOT/.git" ]]; then
  echo "error: qemu root is not a git worktree: $QEMU_ROOT" >&2
  exit 2
fi

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

HEAD_SHA="$(git -C "$QEMU_ROOT" rev-parse HEAD)"
MARKER="$OUT_DIR/.linx_qemu_clean_head"
TARGET_PATH="$OUT_DIR/$TARGET"

reset_clean_tree() {
  git -C "$QEMU_ROOT" worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
  rm -rf "$WORKTREE_DIR" "$OUT_DIR"
}

tree_is_clean() {
  local tree="$1"
  [[ -z "$(git -C "$tree" status --porcelain --untracked-files=no)" ]]
}

have_qemu_submodule_content() {
  local tree="$1"
  [[ -f "$tree/capstone/CMakeLists.txt" ]] \
    && [[ -f "$tree/dtc/meson.build" ]] \
    && [[ -f "$tree/tests/fp/berkeley-softfloat-3/README.html" ]]
}

need_worktree_refresh=0
if [[ ! -d "$WORKTREE_DIR" || ! -e "$WORKTREE_DIR/.git" ]]; then
  need_worktree_refresh=1
elif [[ "$(git -C "$WORKTREE_DIR" rev-parse HEAD 2>/dev/null || true)" != "$HEAD_SHA" ]]; then
  need_worktree_refresh=1
fi

if [[ "$need_worktree_refresh" == "1" ]]; then
  echo "info: preparing clean qemu worktree @ $HEAD_SHA" >&2
  reset_clean_tree
  git -C "$QEMU_ROOT" worktree add --detach "$WORKTREE_DIR" "$HEAD_SHA" >&2
fi

CONFIGURE_ROOT="$WORKTREE_DIR"
CONFIGURE_SUBMODULE_MODE="validate"
BUILD_FINGERPRINT="$HEAD_SHA:worktree"

if ! have_qemu_submodule_content "$WORKTREE_DIR"; then
  if [[ "$ALLOW_DIRTY_SOURCE_FALLBACK" == "1" ]] && have_qemu_submodule_content "$QEMU_ROOT"; then
    echo "info: clean qemu worktree lacks populated nested submodules; using dirty source tree fallback" >&2
    CONFIGURE_ROOT="$QEMU_ROOT"
    CONFIGURE_SUBMODULE_MODE="ignore"
    BUILD_FINGERPRINT="$HEAD_SHA:dirty-source"
  elif tree_is_clean "$QEMU_ROOT" && have_qemu_submodule_content "$QEMU_ROOT"; then
    echo "info: clean qemu worktree lacks populated nested submodules; using clean source tree fallback" >&2
    CONFIGURE_ROOT="$QEMU_ROOT"
    CONFIGURE_SUBMODULE_MODE="ignore"
    BUILD_FINGERPRINT="$HEAD_SHA:source"
  else
    echo "error: clean qemu worktree lacks populated nested submodules and source tree fallback is unavailable" >&2
    exit 1
  fi
fi

need_configure=0
if [[ ! -f "$OUT_DIR/build.ninja" ]]; then
  need_configure=1
elif [[ ! -f "$MARKER" || "$(cat "$MARKER" 2>/dev/null || true)" != "$BUILD_FINGERPRINT" ]]; then
  need_configure=1
fi

if [[ "$need_configure" == "1" ]]; then
  echo "info: configuring clean qemu build in $OUT_DIR" >&2
  rm -rf "$OUT_DIR"
  mkdir -p "$OUT_DIR"
  (
    cd "$OUT_DIR"
    LINX_MODEL_INCLUDE="$ROOT/tools/model/include" \
      "$CONFIGURE_ROOT/configure" \
      --with-git-submodules="$CONFIGURE_SUBMODULE_MODE" \
      --target-list=linx64-softmmu \
      --enable-plugins \
      --disable-docs \
      --disable-werror >&2
  )
  printf '%s\n' "$BUILD_FINGERPRINT" > "$MARKER"
fi

echo "info: building $TARGET in $OUT_DIR" >&2
"$NINJA_BIN" -C "$OUT_DIR" "$TARGET" >&2

if [[ ! -x "$TARGET_PATH" ]]; then
  echo "error: built target not found: $TARGET_PATH" >&2
  exit 1
fi

printf '%s\n' "$TARGET_PATH"
