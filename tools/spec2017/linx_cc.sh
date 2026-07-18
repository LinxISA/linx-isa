#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"
TARGET="${LINX_TARGET:-linx64-unknown-linux-musl}"
SYSROOT="${LINX_SYSROOT:-$ROOT/out/libc/musl/install/phase-b}"
FORCE_STATIC="${LINX_SPEC_FORCE_STATIC:-0}"
STATIC_IMAGE_BASE="${LINX_SPEC_IMAGE_BASE:-0x40000000}"

CLANG="${LINX_CLANG:-}"
if [[ -z "$CLANG" ]]; then
  cand="$ROOT/compiler/llvm/build-linxisa-clang/bin/clang"
  if [[ -x "$cand" ]]; then
    CLANG="$cand"
  fi
fi
if [[ -z "$CLANG" || ! -x "$CLANG" ]]; then
  echo "error: linx_cc.sh could not find clang; set LINX_CLANG" >&2
  exit 2
fi

if [[ -n "${LINX_SPEC_LINK_MODE:-}" || -n "${LINX_SPEC_COMPAT_INCLUDE:-}" ]]; then
  echo "error: legacy SPEC link/compat controls were removed; use the canonical sysroot/CRT" >&2
  exit 2
fi

BENCH_FLAGS=()
COMMON_FLAGS=(
  -DSPEC_LINUX_X64
  -DSPEC_LP64
  -fno-builtin-cos
  -fno-builtin-cosf
  -fno-builtin-sin
  -fno-builtin-sinf
)
case "$PWD" in
  *"/500.perlbench_r/"*)
    BENCH_FLAGS+=(
      -D_GNU_SOURCE
      -D_FILE_OFFSET_BITS=64
      -D_LARGEFILE_SOURCE
      -D_LARGE_FILES
      -DSPEC_NO_USE_STDIO_PTR
      -DSPEC_NO_USE_STDIO_BASE
      -include fcntl.h
      -include unistd.h
      -include sys/types.h
      -include sys/stat.h
    )
    ;;
esac

case "$PWD" in
  *"/502.gcc_r/"*)
    BENCH_FLAGS+=(
      -DSPEC_GCC_VARIADIC_FUNCTIONS_MISMATCH_WORKAROUND
    )
    ;;
esac

case "$PWD" in
  *"/520.omnetpp_r/"*)
    BENCH_FLAGS+=(
      -Dstat64=stat
      -Dfstat64=fstat
      -Dlstat64=lstat
      -Dftello64=ftello
      -Dfseeko64=fseeko
    )
    ;;
esac

case "$PWD" in
  *"/525.x264_r/"*)
    BENCH_FLAGS+=(
      -include string.h
    )
    ;;
esac

LINK_FLAGS=()
is_link=1
for arg in "$@"; do
  case "$arg" in
    -c|-S|-E|-M|-MM|-fsyntax-only)
      is_link=0
      ;;
  esac
done
FILTERED_ARGS=("$@")
if [[ "$is_link" == "1" && "$FORCE_STATIC" == "1" ]]; then
  FILTERED_ARGS=()
  for arg in "$@"; do
    case "$arg" in
      -lm)
        # The phase-b Linx musl sysroot currently folds libm into libc.a and
        # does not install a separate libm.a. SPEC makefiles still add -lm.
        if [[ ! -f "$SYSROOT/lib/libm.a" && ! -f "$SYSROOT/usr/lib/libm.a" ]]; then
          continue
        fi
        ;;
    esac
    FILTERED_ARGS+=("$arg")
  done
fi
if [[ "$is_link" == "1" ]]; then
  if [[ "$FORCE_STATIC" == "1" ]]; then
    crt1_obj="$SYSROOT/lib/rcrt1.o"
    if [[ ! -f "$crt1_obj" ]]; then
      crt1_obj="$SYSROOT/lib/crt1.o"
    fi
    if [[ ! -f "$crt1_obj" ]]; then
      echo "error: missing static startup object (rcrt1.o/crt1.o) under $SYSROOT/lib" >&2
      exit 2
    fi

    rt_archive="$SYSROOT/lib/liblinx_builtin_rt.a"
    if [[ ! -f "$rt_archive" ]]; then
      rt_archive="$SYSROOT/lib/libclang_rt.builtins-linx64.a"
    fi
    if [[ ! -f "$rt_archive" ]]; then
      echo "error: missing Linx builtins archive under $SYSROOT/lib" >&2
      exit 2
    fi

    LINK_FLAGS+=(
      -static
      -Wl,-pie
      -nostdlib
      "$crt1_obj"
      "$SYSROOT/lib/crti.o"
      "$rt_archive"
      "$SYSROOT/lib/libc.a"
      "$SYSROOT/lib/crtn.o"
      -Wl,--image-base="$STATIC_IMAGE_BASE"
    )
  else
    LINK_FLAGS+=(
      -rtlib=compiler-rt
    )
  fi
fi

exec "$CLANG" \
  --target="$TARGET" \
  --sysroot="$SYSROOT" \
  -fuse-ld=lld \
  ${COMMON_FLAGS[@]+"${COMMON_FLAGS[@]}"} \
  ${BENCH_FLAGS[@]+"${BENCH_FLAGS[@]}"} \
  "${FILTERED_ARGS[@]}" \
  ${LINK_FLAGS[@]+"${LINK_FLAGS[@]}"}
