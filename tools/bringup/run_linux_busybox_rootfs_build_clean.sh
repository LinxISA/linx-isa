#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINUX_ROOT="${LINUX_ROOT:-$ROOT/kernel/linux}"
WORKTREE_DIR="${WORKTREE_DIR:-/tmp/linx-linux-rootfs-clean-src}"
OUT_DIR="${OUT_DIR:-/tmp/linx-linux-rootfs-clean-out}"
OBJ_DIR="${OBJ_DIR:-/tmp/linx-linux-rootfs-clean-build}"
ROOTFS_IMG="${ROOTFS_IMG:-$OUT_DIR/rootfs.ext2}"
LLVM_BUILD="${LLVM_BUILD:-$ROOT/compiler/llvm/build-linxisa-clang}"

usage() {
  cat <<'USAGE'
Usage: tools/bringup/run_linux_busybox_rootfs_build_clean.sh [options]

Options:
  --linux-root PATH   Linux source tree (default: $ROOT/kernel/linux)
  --worktree PATH     Detached clean worktree (default: /tmp/linx-linux-rootfs-clean-src)
  --out-dir PATH      Rootfs output directory (default: /tmp/linx-linux-rootfs-clean-out)
  --obj-dir PATH      Temporary O= build directory (default: /tmp/linx-linux-rootfs-clean-build)
  --rootfs-img PATH   Rootfs image path (default: <out-dir>/rootfs.ext2)
  --llvm-build PATH   LLVM build root containing clang (default: $ROOT/compiler/llvm/build-linxisa-clang)

Stdout:
  Prints the absolute path to the built rootfs image on success.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --linux-root)
      LINUX_ROOT="$2"
      shift 2
      ;;
    --worktree)
      WORKTREE_DIR="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      ROOTFS_IMG="$2/rootfs.ext2"
      shift 2
      ;;
    --obj-dir)
      OBJ_DIR="$2"
      shift 2
      ;;
    --rootfs-img)
      ROOTFS_IMG="$2"
      shift 2
      ;;
    --llvm-build)
      LLVM_BUILD="$2"
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

if [[ ! -d "$LINUX_ROOT/.git" && ! -f "$LINUX_ROOT/.git" ]]; then
  echo "error: linux root is not a git worktree: $LINUX_ROOT" >&2
  exit 2
fi
if [[ ! -x "$LLVM_BUILD/bin/clang" ]]; then
  echo "error: clang not found under LLVM_BUILD=$LLVM_BUILD" >&2
  exit 2
fi

HEAD_SHA="$(git -C "$LINUX_ROOT" rev-parse HEAD)"
MARKER="$OUT_DIR/.linx_linux_rootfs_clean_head"

reset_clean_tree() {
  git -C "$LINUX_ROOT" worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
  rm -rf "$WORKTREE_DIR" "$OBJ_DIR" "$OUT_DIR"
}

need_worktree_refresh=0
if [[ ! -d "$WORKTREE_DIR" || ! -e "$WORKTREE_DIR/.git" ]]; then
  need_worktree_refresh=1
elif [[ "$(git -C "$WORKTREE_DIR" rev-parse HEAD 2>/dev/null || true)" != "$HEAD_SHA" ]]; then
  need_worktree_refresh=1
fi

if [[ "$need_worktree_refresh" == "1" ]]; then
  echo "info: preparing clean linux rootfs worktree @ $HEAD_SHA" >&2
  reset_clean_tree
  git -C "$LINUX_ROOT" worktree add --detach "$WORKTREE_DIR" "$HEAD_SHA" >&2
fi

need_rebuild=0
if [[ ! -f "$ROOTFS_IMG" ]]; then
  need_rebuild=1
elif [[ ! -f "$MARKER" || "$(cat "$MARKER" 2>/dev/null || true)" != "$HEAD_SHA" ]]; then
  need_rebuild=1
fi

if [[ "$need_rebuild" == "1" ]]; then
  echo "info: building clean busybox rootfs in $OUT_DIR" >&2
  rm -rf "$OBJ_DIR" "$OUT_DIR"
  mkdir -p "$OBJ_DIR" "$OUT_DIR"
  O="$OBJ_DIR" LLVM_BUILD="$LLVM_BUILD" \
    bash "$WORKTREE_DIR/tools/linxisa/busybox_rootfs/build_rootfs.sh" >&2
  cp "$OBJ_DIR/linx-busybox-rootfs/rootfs.ext2" "$ROOTFS_IMG"
  printf '%s\n' "$HEAD_SHA" > "$MARKER"
fi

if [[ ! -f "$ROOTFS_IMG" ]]; then
  echo "error: built rootfs image not found: $ROOTFS_IMG" >&2
  exit 1
fi

printf '%s\n' "$ROOTFS_IMG"
