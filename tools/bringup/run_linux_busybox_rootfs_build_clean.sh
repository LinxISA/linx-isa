#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CALLER_PWD="$PWD"
LINUX_ROOT="${LINUX_ROOT:-$ROOT/kernel/linux}"
WORKTREE_DIR="${WORKTREE_DIR:-/tmp/linx-linux-rootfs-clean-src}"
OUT_DIR="${OUT_DIR:-/tmp/linx-linux-rootfs-clean-out}"
OBJ_DIR="${OBJ_DIR:-/tmp/linx-linux-rootfs-clean-build}"
ROOTFS_IMG="${ROOTFS_IMG:-$OUT_DIR/rootfs.ext2}"
LLVM_BUILD="${LLVM_BUILD:-$ROOT/compiler/llvm/build-linxisa-clang}"

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    echo "error: sha256sum or shasum is required" >&2
    return 2
  fi
}

abs_path() {
  local candidate component separator
  local -a path_parts normalized_parts
  case "$1" in
    /*) candidate="$1" ;;
    *) candidate="$CALLER_PWD/$1" ;;
  esac

  IFS='/' read -r -a path_parts <<< "$candidate"
  normalized_parts=()
  for component in "${path_parts[@]}"; do
    case "$component" in
      ''|.) ;;
      ..)
        if [[ "${#normalized_parts[@]}" -gt 0 ]]; then
          unset "normalized_parts[$((${#normalized_parts[@]} - 1))]"
        fi
        ;;
      *) normalized_parts[${#normalized_parts[@]}]="$component" ;;
    esac
  done

  printf '/'
  separator=''
  for component in "${normalized_parts[@]}"; do
    printf '%s%s' "$separator" "$component"
    separator='/'
  done
  printf '\n'
}

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

LINUX_ROOT="$(abs_path "$LINUX_ROOT")"
WORKTREE_DIR="$(abs_path "$WORKTREE_DIR")"
OUT_DIR="$(abs_path "$OUT_DIR")"
OBJ_DIR="$(abs_path "$OBJ_DIR")"
ROOTFS_IMG="$(abs_path "$ROOTFS_IMG")"
LLVM_BUILD="$(abs_path "$LLVM_BUILD")"

if [[ ! -d "$LINUX_ROOT/.git" && ! -f "$LINUX_ROOT/.git" ]]; then
  echo "error: linux root is not a git worktree: $LINUX_ROOT" >&2
  exit 2
fi
if [[ ! -x "$LLVM_BUILD/bin/clang" ]]; then
  echo "error: clang not found under LLVM_BUILD=$LLVM_BUILD" >&2
  exit 2
fi
if [[ ! -x "$LLVM_BUILD/bin/ld.lld" ]]; then
  echo "error: ld.lld not found under LLVM_BUILD=$LLVM_BUILD" >&2
  exit 2
fi

HEAD_SHA="$(git -C "$LINUX_ROOT" rev-parse HEAD)"
MARKER="$OUT_DIR/.linx_linux_rootfs_clean_head"
PRISTINE_IMG="$OUT_DIR/rootfs.pristine.ext2"
CLANG_SHA="$(sha256_file "$LLVM_BUILD/bin/clang")"
LD_LLD_SHA="$(sha256_file "$LLVM_BUILD/bin/ld.lld")"
EXPECTED_MARKER="$(printf 'format=2\nlinux_head=%s\nclang_sha256=%s\nld_lld_sha256=%s\n' \
  "$HEAD_SHA" "$CLANG_SHA" "$LD_LLD_SHA")"

if [[ "$ROOTFS_IMG" == "$PRISTINE_IMG" ]]; then
  echo "error: rootfs work image must differ from pristine cache: $PRISTINE_IMG" >&2
  exit 2
fi

reset_clean_tree() {
  git -C "$LINUX_ROOT" worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || true
  git -C "$LINUX_ROOT" worktree prune >/dev/null 2>&1 || true
  rm -rf "$WORKTREE_DIR" "$OBJ_DIR"
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
if [[ ! -f "$PRISTINE_IMG" ]]; then
  need_rebuild=1
elif [[ ! -f "$MARKER" || "$(cat "$MARKER" 2>/dev/null || true)" != "$EXPECTED_MARKER" ]]; then
  need_rebuild=1
fi

if [[ "$need_rebuild" == "1" ]]; then
  echo "info: building clean busybox rootfs in $OUT_DIR" >&2
  rm -rf "$OBJ_DIR"
  mkdir -p "$OBJ_DIR" "$OUT_DIR"
  O="$OBJ_DIR" LLVM_BUILD="$LLVM_BUILD" \
    bash "$WORKTREE_DIR/tools/linxisa/busybox_rootfs/build_rootfs.sh" >&2
  if [[ ! -f "$OBJ_DIR/linx-busybox-rootfs/rootfs.ext2" ]]; then
    echo "error: built rootfs image not found under object directory" >&2
    exit 1
  fi
  rm -f "$PRISTINE_IMG.tmp" "$MARKER.tmp"
  cp "$OBJ_DIR/linx-busybox-rootfs/rootfs.ext2" "$PRISTINE_IMG.tmp"
  mv "$PRISTINE_IMG.tmp" "$PRISTINE_IMG"
  printf '%s\n' "$EXPECTED_MARKER" > "$MARKER.tmp"
  mv "$MARKER.tmp" "$MARKER"
fi

mkdir -p "$(dirname "$ROOTFS_IMG")"
rm -f "$ROOTFS_IMG.tmp"
cp "$PRISTINE_IMG" "$ROOTFS_IMG.tmp"
mv "$ROOTFS_IMG.tmp" "$ROOTFS_IMG"

printf '%s\n' "$ROOTFS_IMG"
