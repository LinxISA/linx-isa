#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
QEMU_ROOT="${QEMU_ROOT:-$ROOT/emulator/qemu}"
OUT_DIR="${OUT_DIR:-/tmp/linx-qemu-clean-build}"
WORKTREE_DIR="${WORKTREE_DIR:-/tmp/linx-qemu-clean-src}"
TARGET="${TARGET:-qemu-system-linx64}"
NINJA_BIN="${NINJA_BIN:-}"

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
  git -C "$QEMU_ROOT" worktree prune >/dev/null 2>&1 || true
  rm -rf "$WORKTREE_DIR" "$OUT_DIR"
}

populate_worktree_submodules() {
  git -C "$WORKTREE_DIR" submodule sync --recursive >&2
  git -C "$WORKTREE_DIR" submodule update --init --recursive >&2
}

copy_submodule_tree() {
  local src="$1"
  local dst="$2"

  mkdir -p "$dst"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete --exclude='.git' --exclude='.git/' "$src"/ "$dst"/ >&2
  else
    rm -rf "$dst"
    mkdir -p "$dst"
    (
      cd "$src"
      tar --exclude='.git' -cf - .
    ) | (
      cd "$dst"
      tar -xf -
    )
  fi
}

hydrate_worktree_submodules_from_source() {
  local rel src dst

  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    src="$QEMU_ROOT/$rel"
    dst="$WORKTREE_DIR/$rel"
    if [[ ! -e "$src" ]]; then
      continue
    fi
    copy_submodule_tree "$src" "$dst"
  done < <(git -C "$QEMU_ROOT" submodule status | awk '{print $2}')
}

hydrate_wrap_subprojects_from_source() {
  local src rel dst

  for src in "$QEMU_ROOT"/subprojects/*; do
    [[ -d "$src" ]] || continue
    [[ -f "$src/meson.build" ]] || continue
    [[ -f "$src/.meson-subproject-wrap-hash.txt" ]] || continue
    rel="subprojects/${src##*/}"
    dst="$WORKTREE_DIR/$rel"
    if [[ ! -f "$dst/meson.build" ]]; then
      echo "info: hydrating Meson wrap subproject $rel from local source tree" >&2
      copy_submodule_tree "$src" "$dst"
    fi
  done
}

have_qemu_submodule_content() {
  local tree="$1"
  [[ -f "$tree/roms/seabios/README" ]] \
    && [[ -f "$tree/roms/opensbi/README.md" ]] \
    && [[ -f "$tree/roms/edk2/BaseTools/Edk2ToolsBuild.py" ]] \
    && [[ -f "$tree/tests/lcitool/libvirt-ci/README.rst" ]]
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
  git -C "$QEMU_ROOT" worktree add --force --detach "$WORKTREE_DIR" "$HEAD_SHA" >&2
fi

CONFIGURE_ROOT="$WORKTREE_DIR"
BUILD_FINGERPRINT="$HEAD_SHA:worktree"

if ! have_qemu_submodule_content "$WORKTREE_DIR"; then
  if have_qemu_submodule_content "$QEMU_ROOT"; then
    echo "info: hydrating clean qemu worktree submodules from local source tree" >&2
    hydrate_worktree_submodules_from_source
  fi
fi

hydrate_wrap_subprojects_from_source

if ! have_qemu_submodule_content "$WORKTREE_DIR"; then
  echo "info: populating clean qemu worktree submodules" >&2
  populate_worktree_submodules
fi

if ! have_qemu_submodule_content "$WORKTREE_DIR"; then
  echo "error: clean qemu worktree lacks required nested submodules" >&2
  exit 1
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
