#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd -P)"
TARGET="${LINX_TARGET:-linx64-unknown-linux-musl}"
SYSROOT="${LINX_SYSROOT:-$ROOT/out/libc/musl/install/phase-b}"
FORCE_STATIC="${LINX_SPEC_FORCE_STATIC:-0}"
STATIC_IMAGE_BASE="${LINX_SPEC_IMAGE_BASE:-0x40000000}"
CXX_RUNTIME_ROOT="${LINX_CXX_RUNTIME_ROOT:-$ROOT/out/cpp-runtime/musl-cxx17-spec/install}"

CLANGXX="${LINX_CLANGXX:-}"
if [[ -z "$CLANGXX" ]]; then
  cand="$ROOT/compiler/llvm/build-linxisa-clang/bin/clang++"
  if [[ -x "$cand" ]]; then
    CLANGXX="$cand"
  fi
fi
if [[ -z "$CLANGXX" || ! -x "$CLANGXX" ]]; then
  echo "error: linx_cxx.sh could not find clang++; set LINX_CLANGXX" >&2
  exit 2
fi

RUNTIME_LIB_DIRS=()
for dir in "$SYSROOT/lib" "$SYSROOT/usr/lib" "$CXX_RUNTIME_ROOT/lib"; do
  if [[ -d "$dir" ]]; then
    RUNTIME_LIB_DIRS+=("$dir")
  fi
done

resolve_runtime_archive() {
  local name="$1"
  local dir

  for dir in ${RUNTIME_LIB_DIRS[@]+"${RUNTIME_LIB_DIRS[@]}"}; do
    if [[ -f "$dir/$name" ]]; then
      printf '%s\n' "$dir/$name"
      return 0
    fi
  done

  echo "error: missing C++ runtime archive $name; run tools/build_linx_llvm_cpp_runtimes.sh --profile spec --mode phase-b or set LINX_CXX_RUNTIME_ROOT" >&2
  exit 2
}

if [[ -n "${LINX_SPEC_LINK_MODE:-}" || -n "${LINX_SPEC_COMPAT_INCLUDE:-}" ]]; then
  echo "error: legacy SPEC link/compat controls were removed; use the canonical sysroot/CRT" >&2
  exit 2
fi

BENCH_FLAGS=()
COMMON_FLAGS=(
  -DSPEC_LINUX_X64
  -DSPEC_LINUX
  -DSPEC_LP64
  -D_LIBCPP_VECTORIZE_ALGORITHMS=0
  -fno-builtin-cos
  -fno-builtin-cosf
  -fno-builtin-sin
  -fno-builtin-sinf
)
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
  *"/523.xalancbmk_r/"*)
    BENCH_FLAGS+=(
      -Dm_isPresentable=m_predicate
      -DwriteNumberedEntityReference=writeNumericCharacterReference
    )
    ;;
esac

STD_FLAGS=()
has_std=0
for arg in "$@"; do
  case "$arg" in
    -std=*)
      has_std=1
      ;;
  esac
done
if [[ "$has_std" == "0" ]]; then
  # SPEC C++ workloads are authored for pre-C++11 dialects; keep libc++ on cxx03 headers.
  STD_FLAGS+=(-std=gnu++03)
fi

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
    for required in "$SYSROOT/lib/crti.o" "$SYSROOT/lib/crtn.o" "$SYSROOT/lib/libc.a"; do
      if [[ ! -f "$required" ]]; then
        echo "error: missing static link input: $required" >&2
        exit 2
      fi
    done

    rt_archive="$SYSROOT/lib/liblinx_builtin_rt.a"
    if [[ ! -f "$rt_archive" ]]; then
      rt_archive="$SYSROOT/lib/libclang_rt.builtins-linx64.a"
    fi
    if [[ ! -f "$rt_archive" ]]; then
      echo "error: missing Linx builtins archive under $SYSROOT/lib" >&2
      exit 2
    fi

    libcxx_archive="$(resolve_runtime_archive libc++.a)"
    libcxxabi_archive="$(resolve_runtime_archive libc++abi.a)"
    libunwind_archive="$(resolve_runtime_archive libunwind.a)"

    LINK_FLAGS+=(
      -static
      -Wl,-pie
      -nostdlib
      "$crt1_obj"
      "$SYSROOT/lib/crti.o"
      -Wl,--start-group
      "$libcxx_archive"
      "$libcxxabi_archive"
      "$libunwind_archive"
      "$SYSROOT/lib/libc.a"
      "$rt_archive"
      -Wl,--end-group
      "$SYSROOT/lib/crtn.o"
      -Wl,--image-base="$STATIC_IMAGE_BASE"
    )
  else
    LINK_FLAGS+=(
      -rtlib=compiler-rt
      -unwindlib=libunwind
      -L"$SYSROOT/lib"
      -L"$SYSROOT/usr/lib"
      -L"$CXX_RUNTIME_ROOT/lib"
      -Wl,--start-group
      -lc++
      -lc++abi
      -lunwind
      -lc
      -Wl,--end-group
    )
  fi
fi

exec "$CLANGXX" \
  --target="$TARGET" \
  --sysroot="$SYSROOT" \
  -fuse-ld=lld \
  -stdlib=libc++ \
  ${COMMON_FLAGS[@]+"${COMMON_FLAGS[@]}"} \
  ${BENCH_FLAGS[@]+"${BENCH_FLAGS[@]}"} \
  ${STD_FLAGS[@]+"${STD_FLAGS[@]}"} \
  "${FILTERED_ARGS[@]}" \
  ${LINK_FLAGS[@]+"${LINK_FLAGS[@]}"}
