#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)

CLANG="$REPO_ROOT/compiler/llvm/build-linxisa-clang/bin/clang"
QEMU="$REPO_ROOT/emulator/qemu/build-user/qemu-linx"
SYSROOT="$REPO_ROOT/out/libc/glibc/sysroot"

if [[ -z "${BUILD_DIR:-}" ]]; then
  BUILD_DIR=$(mktemp -d -t linx-lihan-cat-glibc.XXXXXX)
  trap 'rm -rf "$BUILD_DIR"' EXIT
fi

SRC="$BUILD_DIR/lihan_cat_glibc_hello.c"
BIN="$BUILD_DIR/lihan_cat_glibc_hello"

mkdir -p "$BUILD_DIR"

cat > "$SRC" <<'EOF_C'
#include <stdio.h>

int
main(void)
{
    printf("Hello from cat-built Linx glibc: value=%d status=%s\n", 2026, "ok");
    return 0;
}
EOF_C

"$CLANG" \
  --target=linx64-unknown-linux-gnu \
  --sysroot="$SYSROOT" \
  -fuse-ld=lld \
  -rtlib=libgcc \
  -unwindlib=none \
  -O2 \
  -fPIE \
  -pie \
  -Wl,--dynamic-linker=/lib/ld.so.1 \
  -Wl,-rpath,/lib \
  -Wl,-z,now \
  -Wl,-z,relro \
  -L"$SYSROOT/lib" \
  -L"$SYSROOT/usr/lib" \
  -B"$SYSROOT/usr/lib" \
  "$SRC" \
  -o "$BIN"

echo "built: $BIN"
"$QEMU" -L "$SYSROOT" "$BIN"
