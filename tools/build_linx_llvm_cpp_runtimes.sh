#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

MODE="phase-b"
PROFILE="noeh"
TARGET="linx64-unknown-linux-musl"
LLVM_ROOT="${LLVM_ROOT:-$ROOT/compiler/llvm}"
OUT_ROOT="${OUT_ROOT:-}"
MUSL_SYSROOT=""
CACHE_FILE=""
JOBS="${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || echo 8)}"
MERGE_SYSROOT=1
ENABLE_LIBUNWIND=""

usage() {
  cat <<'EOF'
Usage: build_linx_llvm_cpp_runtimes.sh [options]

Options:
  --mode <phase-a|phase-b|phase-c>     Musl lane mode used for sysroot selection (default: phase-b)
  --profile <noeh|spec|app>    Runtime feature profile (default: noeh)
  --target <triple>            Runtime target triple (default: linx64-unknown-linux-musl)
  --llvm-root <path>           LLVM monorepo root (default: compiler/llvm in superproject)
  --out-root <path>            Runtime build/install root (default: profile-specific in out/cpp-runtime/)
  --musl-sysroot <path>        Musl sysroot to merge runtime overlay into
  --cache-file <path>          Runtime CMake cache preset
  --jobs <N>                   Parallel build jobs
  --enable-libunwind           Also build/install libunwind (requires Linx libunwind arch support)
  --no-merge-sysroot           Build/install runtime overlay but do not copy into musl sysroot
  -h, --help                   Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --llvm-root)
      LLVM_ROOT="$2"
      shift 2
      ;;
    --out-root)
      OUT_ROOT="$2"
      shift 2
      ;;
    --musl-sysroot)
      MUSL_SYSROOT="$2"
      shift 2
      ;;
    --cache-file)
      CACHE_FILE="$2"
      shift 2
      ;;
    --jobs)
      JOBS="$2"
      shift 2
      ;;
    --enable-libunwind)
      ENABLE_LIBUNWIND=1
      shift
      ;;
    --no-merge-sysroot)
      MERGE_SYSROOT=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

case "$MODE" in
  phase-a|phase-b|phase-c) ;;
  *)
    echo "error: --mode must be phase-a, phase-b, or phase-c (got '$MODE')" >&2
    exit 2
    ;;
esac

case "$PROFILE" in
  noeh|spec|app) ;;
  *)
    echo "error: --profile must be noeh, spec, or app (got '$PROFILE')" >&2
    exit 2
    ;;
esac

if [[ -z "$OUT_ROOT" ]]; then
  case "$PROFILE" in
    noeh) OUT_ROOT="$ROOT/out/cpp-runtime/musl-cxx17-noeh" ;;
    spec) OUT_ROOT="$ROOT/out/cpp-runtime/musl-cxx17-spec" ;;
    app) OUT_ROOT="$ROOT/out/cpp-runtime/musl-cxx17-app" ;;
  esac
fi

LLVM_ROOT="$(cd "$LLVM_ROOT" && pwd -P)"
OUT_ROOT="$(mkdir -p "$OUT_ROOT" && cd "$OUT_ROOT" && pwd -P)"

if [[ -z "$MUSL_SYSROOT" ]]; then
  MUSL_SYSROOT="$ROOT/out/libc/musl/install/$MODE"
fi
MUSL_SYSROOT="$(cd "$MUSL_SYSROOT" && pwd -P)"

if [[ -z "$CACHE_FILE" ]]; then
  CACHE_FILE="$LLVM_ROOT/runtimes/cmake/caches/LinxISA-musl-cxx17-noeh.cmake"
fi

if [[ ! -d "$LLVM_ROOT/llvm" ]]; then
  echo "error: invalid --llvm-root, missing '$LLVM_ROOT/llvm'" >&2
  exit 2
fi
if [[ ! -f "$CACHE_FILE" ]]; then
  echo "error: runtime cache file not found: $CACHE_FILE" >&2
  exit 2
fi
if [[ ! -d "$MUSL_SYSROOT/lib" ]]; then
  echo "error: musl sysroot missing lib dir: $MUSL_SYSROOT/lib" >&2
  echo "hint: run lib/musl/tools/linx/build_linx64_musl.sh first." >&2
  exit 2
fi
if [[ ! -d "$MUSL_SYSROOT/include" && ! -d "$MUSL_SYSROOT/usr/include" ]]; then
  echo "error: musl sysroot not ready: $MUSL_SYSROOT" >&2
  echo "hint: run lib/musl/tools/linx/build_linx64_musl.sh first." >&2
  exit 2
fi

ensure_linux_compat_headers() {
  mkdir -p "$MUSL_SYSROOT/include/linux" "$MUSL_SYSROOT/usr/include/linux"

  if [[ ! -f "$MUSL_SYSROOT/include/linux/limits.h" ]]; then
    cat >"$MUSL_SYSROOT/include/linux/limits.h" <<'EOF'
#ifndef _LINX_SPEC2017_LINUX_LIMITS_H
#define _LINX_SPEC2017_LINUX_LIMITS_H
#include <limits.h>
#endif
EOF
  fi
  install -m 644 "$MUSL_SYSROOT/include/linux/limits.h" \
    "$MUSL_SYSROOT/usr/include/linux/limits.h"

  if [[ ! -f "$MUSL_SYSROOT/include/linux/futex.h" ]]; then
    cat >"$MUSL_SYSROOT/include/linux/futex.h" <<'EOF'
#ifndef _LINX_COMPAT_LINUX_FUTEX_H
#define _LINX_COMPAT_LINUX_FUTEX_H

#define FUTEX_WAIT 0
#define FUTEX_WAKE 1
#define FUTEX_PRIVATE_FLAG 128
#define FUTEX_WAIT_PRIVATE (FUTEX_WAIT | FUTEX_PRIVATE_FLAG)
#define FUTEX_WAKE_PRIVATE (FUTEX_WAKE | FUTEX_PRIVATE_FLAG)

#endif
EOF
  fi
  install -m 644 "$MUSL_SYSROOT/include/linux/futex.h" \
    "$MUSL_SYSROOT/usr/include/linux/futex.h"
}

ensure_linux_compat_headers

CLANG="${CLANG:-}"
if [[ -z "$CLANG" ]]; then
  for cand in \
    "$ROOT/compiler/llvm/build-linxisa-clang/bin/clang" \
    "$HOME/llvm-project/build-linxisa-clang/bin/clang"
  do
    if [[ -x "$cand" ]]; then
      CLANG="$cand"
      break
    fi
  done
fi
if [[ -z "$CLANG" || ! -x "$CLANG" ]]; then
  echo "error: CLANG not found; set CLANG=/path/to/clang" >&2
  exit 2
fi

LLVM_BIN="$(cd "$(dirname "$CLANG")" && pwd -P)"
LLVM_HOST_BUILD_ROOT="${LLVM_HOST_BUILD_ROOT:-$(cd "$LLVM_BIN/.." && pwd -P)}"
CLANGXX="${CLANGXX:-$LLVM_BIN/clang++}"
LLD="${LLD:-$LLVM_BIN/ld.lld}"
AR="${AR:-$LLVM_BIN/llvm-ar}"
RANLIB="${RANLIB:-$LLVM_BIN/llvm-ranlib}"
NM="${NM:-$LLVM_BIN/llvm-nm}"
STRIP="${STRIP:-$LLVM_BIN/llvm-strip}"

for exe in "$CLANGXX" "$LLD" "$AR" "$RANLIB" "$NM" "$STRIP"; do
  if [[ ! -x "$exe" ]]; then
    echo "error: missing executable tool: $exe" >&2
    exit 2
  fi
done

LLVM_CONFIG_DIR="$LLVM_HOST_BUILD_ROOT/lib/cmake/llvm"
CLANG_CONFIG_DIR="$LLVM_HOST_BUILD_ROOT/lib/cmake/clang"
if [[ ! -f "$LLVM_CONFIG_DIR/LLVMConfig.cmake" ]]; then
  echo "error: missing LLVMConfig.cmake in host build: $LLVM_CONFIG_DIR/LLVMConfig.cmake" >&2
  exit 2
fi
if [[ ! -f "$CLANG_CONFIG_DIR/ClangConfig.cmake" ]]; then
  echo "error: missing ClangConfig.cmake in host build: $CLANG_CONFIG_DIR/ClangConfig.cmake" >&2
  exit 2
fi

BUILD_DIR="$OUT_ROOT/build/$MODE"
INSTALL_DIR="$OUT_ROOT/install"
LOG_DIR="$OUT_ROOT/logs"
SUMMARY="$OUT_ROOT/summary_${MODE}.json"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR" "$INSTALL_DIR" "$LOG_DIR"

configure_log="$LOG_DIR/configure_${MODE}.log"
build_log="$LOG_DIR/build_${MODE}.log"
install_log="$LOG_DIR/install_${MODE}.log"

RUNTIME_LIST="libcxxabi;libcxx"
LIBCXXABI_USE_LLVM_UNWINDER=OFF
LIBCXX_ENABLE_EXCEPTIONS=OFF
LIBCXXABI_ENABLE_EXCEPTIONS=OFF
LIBCXX_ENABLE_LOCALIZATION=OFF
LIBCXX_ENABLE_FILESYSTEM=OFF
LIBCXX_ENABLE_THREADS=OFF
LIBCXXABI_ENABLE_THREADS=OFF
LIBCXX_ENABLE_MONOTONIC_CLOCK=OFF
LIBCXX_STATICALLY_LINK_ABI_IN_STATIC_LIBRARY=OFF
LIBUNWIND_ENABLE_THREADS=OFF
LIBUNWIND_HAS_PTHREAD_LIB=FALSE
LIBUNWIND_HAS_DL_LIB=FALSE
LIBCXXABI_ADDITIONAL_COMPILE_FLAGS=""
CXX_EXTRA_FLAGS="-fno-exceptions"

if [[ -z "$ENABLE_LIBUNWIND" ]]; then
  if [[ "$PROFILE" == "spec" || "$PROFILE" == "app" ]]; then
    ENABLE_LIBUNWIND=1
  else
    ENABLE_LIBUNWIND=0
  fi
fi

if [[ "$PROFILE" == "spec" || "$PROFILE" == "app" ]]; then
  LIBCXX_ENABLE_EXCEPTIONS=ON
  LIBCXXABI_ENABLE_EXCEPTIONS=ON
  LIBCXX_ENABLE_LOCALIZATION=ON
  LIBCXX_ENABLE_FILESYSTEM=ON
  CXX_EXTRA_FLAGS=""
fi

if [[ "$PROFILE" == "app" ]]; then
  LIBCXX_ENABLE_THREADS=ON
  LIBCXXABI_ENABLE_THREADS=ON
  LIBCXX_ENABLE_MONOTONIC_CLOCK=ON
  LIBCXX_STATICALLY_LINK_ABI_IN_STATIC_LIBRARY=ON
  LIBUNWIND_ENABLE_THREADS=ON
  LIBUNWIND_HAS_PTHREAD_LIB=TRUE
  LIBUNWIND_HAS_DL_LIB=TRUE
  # Linx PIE link path still lacks TLS reloc support for thread_local in libc++abi.
  # Force the pthread TLS-key EH globals fallback in cxa_exception_storage.cpp.
  LIBCXXABI_ADDITIONAL_COMPILE_FLAGS="-Wno-builtin-macro-redefined -D__has_feature(x)=0"
fi

if [[ "$ENABLE_LIBUNWIND" == "1" ]]; then
  RUNTIME_LIST="libunwind;libcxxabi;libcxx"
  LIBCXXABI_USE_LLVM_UNWINDER=ON
fi

CMAKE_COMMON=(
  -G Ninja
  -C "$CACHE_FILE"
  -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON
  -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR"
  -DLLVM_DIR="$LLVM_CONFIG_DIR"
  -DClang_DIR="$CLANG_CONFIG_DIR"
  -DLLVM_BINARY_DIR="$LLVM_HOST_BUILD_ROOT"
  -DLLVM_PATH="$LLVM_ROOT/llvm"
  -DLLVM_ENABLE_RUNTIMES="$RUNTIME_LIST"
  -DLLVM_INCLUDE_TESTS=OFF
  -DLLVM_INCLUDE_DOCS=OFF
  -DLLVM_INCLUDE_BENCHMARKS=OFF
  -DHAVE_LIBRT=FALSE
  -DCMAKE_SYSTEM_NAME=Linux
  -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY
  -DCMAKE_C_COMPILER="$CLANG"
  -DCMAKE_CXX_COMPILER="$CLANGXX"
  -DCMAKE_ASM_COMPILER="$CLANG"
  -DCMAKE_C_COMPILER_TARGET="$TARGET"
  -DCMAKE_CXX_COMPILER_TARGET="$TARGET"
  -DCMAKE_ASM_COMPILER_TARGET="$TARGET"
  -DCMAKE_AR="$AR"
  -DCMAKE_RANLIB="$RANLIB"
  -DCMAKE_NM="$NM"
  -DCMAKE_STRIP="$STRIP"
  -DCMAKE_SYSROOT="$MUSL_SYSROOT"
  "-DCMAKE_C_FLAGS=--sysroot=$MUSL_SYSROOT -fuse-ld=lld"
  "-DCMAKE_CXX_FLAGS=--sysroot=$MUSL_SYSROOT -fuse-ld=lld -std=c++17 $CXX_EXTRA_FLAGS"
  "-DCMAKE_EXE_LINKER_FLAGS=--sysroot=$MUSL_SYSROOT -fuse-ld=lld"
  "-DCMAKE_SHARED_LINKER_FLAGS=--sysroot=$MUSL_SYSROOT -fuse-ld=lld"
  "-DCMAKE_MODULE_LINKER_FLAGS=--sysroot=$MUSL_SYSROOT -fuse-ld=lld"
  "-DLIBCXX_ENABLE_EXCEPTIONS=$LIBCXX_ENABLE_EXCEPTIONS"
  -DLIBCXX_ENABLE_SHARED=OFF
  -DLIBCXX_ENABLE_STATIC=ON
  -DLIBCXX_ENABLE_RTTI=ON
  -DLIBCXX_HAS_MUSL_LIBC=ON
  "-DLIBCXX_ENABLE_LOCALIZATION=$LIBCXX_ENABLE_LOCALIZATION"
  -DLIBCXX_ENABLE_WIDE_CHARACTERS=OFF
  -DLIBCXX_ENABLE_UNICODE=OFF
  "-DLIBCXX_ENABLE_FILESYSTEM=$LIBCXX_ENABLE_FILESYSTEM"
  "-DLIBCXX_ENABLE_THREADS=$LIBCXX_ENABLE_THREADS"
  "-DLIBCXX_ENABLE_MONOTONIC_CLOCK=$LIBCXX_ENABLE_MONOTONIC_CLOCK"
  "-DLIBCXX_STATICALLY_LINK_ABI_IN_STATIC_LIBRARY=$LIBCXX_STATICALLY_LINK_ABI_IN_STATIC_LIBRARY"
  "-DLIBCXXABI_ENABLE_EXCEPTIONS=$LIBCXXABI_ENABLE_EXCEPTIONS"
  -DLIBCXXABI_ENABLE_SHARED=OFF
  -DLIBCXXABI_ENABLE_STATIC=ON
  "-DLIBCXXABI_ENABLE_THREADS=$LIBCXXABI_ENABLE_THREADS"
  "-DLIBCXXABI_USE_LLVM_UNWINDER=$LIBCXXABI_USE_LLVM_UNWINDER"
  -DLIBUNWIND_ENABLE_SHARED=OFF
  -DLIBUNWIND_ENABLE_STATIC=ON
  "-DLIBUNWIND_ENABLE_THREADS=$LIBUNWIND_ENABLE_THREADS"
  "-DLIBUNWIND_HAS_DL_LIB=$LIBUNWIND_HAS_DL_LIB"
  "-DLIBUNWIND_HAS_PTHREAD_LIB=$LIBUNWIND_HAS_PTHREAD_LIB"
  "-DLIBCXXABI_ADDITIONAL_COMPILE_FLAGS=$LIBCXXABI_ADDITIONAL_COMPILE_FLAGS"
)

echo "[1/4] configure runtimes"
{
  printf '+ cmake -S %q -B %q' "$LLVM_ROOT/runtimes" "$BUILD_DIR"
  printf ' %q' "${CMAKE_COMMON[@]}"
  echo
} >"$configure_log"
cmake -S "$LLVM_ROOT/runtimes" -B "$BUILD_DIR" "${CMAKE_COMMON[@]}" >>"$configure_log" 2>&1

echo "[2/4] build runtimes (target=$TARGET)"
{
  echo "+ cmake --build $BUILD_DIR --parallel $JOBS"
} >"$build_log"
cmake --build "$BUILD_DIR" --parallel "$JOBS" >>"$build_log" 2>&1

echo "[3/4] install runtimes"
{
  echo "+ cmake --build $BUILD_DIR --target install --parallel $JOBS"
} >"$install_log"
cmake --build "$BUILD_DIR" --target install --parallel "$JOBS" >>"$install_log" 2>&1

lib_candidates=(
  "libc++.a"
  "libc++abi.a"
)
if [[ "$ENABLE_LIBUNWIND" == "1" ]]; then
  lib_candidates+=("libunwind.a")
fi

declare -a copied_libs=()
cpp_include_dir=""
clang_resource_dir="$("$CLANG" -print-resource-dir 2>/dev/null || true)"
resource_target_dir=""
resource_builtins=""
if [[ -n "$clang_resource_dir" ]]; then
  resource_target_dir="$clang_resource_dir/lib/$TARGET"
fi
if [[ "$MERGE_SYSROOT" == "1" ]]; then
  echo "[4/4] merge runtime overlay into musl sysroot"
  while IFS= read -r path; do
    cpp_include_dir="$path"
    break
  done < <(find "$INSTALL_DIR" -type d -path "*/include/c++/v1" | sort)

  if [[ -n "$cpp_include_dir" ]]; then
    mkdir -p "$MUSL_SYSROOT/include/c++"
    rm -rf "$MUSL_SYSROOT/include/c++/v1"
    cp -R "$cpp_include_dir" "$MUSL_SYSROOT/include/c++/v1"
  fi

  for lib in "${lib_candidates[@]}"; do
    src=""
    while IFS= read -r cand; do
      src="$cand"
      break
    done < <(find "$INSTALL_DIR" -type f -name "$lib" | sort)
    if [[ -z "$src" ]]; then
      echo "error: missing runtime library after install: $lib" >&2
      exit 2
    fi
    install -m 644 "$src" "$MUSL_SYSROOT/lib/$lib"
    install -m 644 "$src" "$MUSL_SYSROOT/usr/lib/$lib"
    copied_libs+=("$MUSL_SYSROOT/lib/$lib")
  done

  # Reuse musl bring-up builtins as the compiler-rt builtins compatibility
  # archive expected by clang++ when -rtlib=compiler-rt is selected.
  target_arch="${TARGET%%-*}"
  builtins_name="libclang_rt.builtins-${target_arch}.a"
  builtins_src="$ROOT/out/libc/musl/runtime/$MODE/liblinx_builtin_rt.a"
  if [[ -f "$builtins_src" ]]; then
    install -m 644 "$builtins_src" "$MUSL_SYSROOT/lib/$builtins_name"
    install -m 644 "$builtins_src" "$MUSL_SYSROOT/usr/lib/$builtins_name"
    copied_libs+=("$MUSL_SYSROOT/lib/$builtins_name")
    if [[ -n "$resource_target_dir" ]]; then
      mkdir -p "$resource_target_dir"
      resource_builtins="$resource_target_dir/libclang_rt.builtins.a"
      install -m 644 "$builtins_src" "$resource_builtins"
    fi
  fi

  ensure_linux_compat_headers
fi

python3 - <<PY
import json
from pathlib import Path

summary = {
    "schema_version": "linx-cpp-runtimes-v1",
    "mode": "${MODE}",
    "profile": "${PROFILE}",
    "target": "${TARGET}",
    "runtime_list": "${RUNTIME_LIST}".split(";"),
    "libunwind_enabled": ${ENABLE_LIBUNWIND},
    "libcxx_exceptions": "${LIBCXX_ENABLE_EXCEPTIONS}",
    "libcxxabi_exceptions": "${LIBCXXABI_ENABLE_EXCEPTIONS}",
    "libcxx_localization": "${LIBCXX_ENABLE_LOCALIZATION}",
    "libcxx_filesystem": "${LIBCXX_ENABLE_FILESYSTEM}",
    "libcxx_threads": "${LIBCXX_ENABLE_THREADS}",
    "libcxx_monotonic_clock": "${LIBCXX_ENABLE_MONOTONIC_CLOCK}",
    "libcxx_static_link_abi_in_static": "${LIBCXX_STATICALLY_LINK_ABI_IN_STATIC_LIBRARY}",
    "libcxxabi_threads": "${LIBCXXABI_ENABLE_THREADS}",
    "libcxxabi_additional_compile_flags": "${LIBCXXABI_ADDITIONAL_COMPILE_FLAGS}",
    "libunwind_threads": "${LIBUNWIND_ENABLE_THREADS}",
    "libunwind_has_pthread": "${LIBUNWIND_HAS_PTHREAD_LIB}",
    "libunwind_has_dl": "${LIBUNWIND_HAS_DL_LIB}",
    "paths": {
        "llvm_root": "${LLVM_ROOT}",
        "llvm_host_build_root": "${LLVM_HOST_BUILD_ROOT}",
        "musl_sysroot": "${MUSL_SYSROOT}",
        "out_root": "${OUT_ROOT}",
        "build_dir": "${BUILD_DIR}",
        "install_dir": "${INSTALL_DIR}",
        "cache_file": "${CACHE_FILE}",
        "clang": "${CLANG}",
        "clangxx": "${CLANGXX}",
        "lld": "${LLD}",
        "clang_resource_dir": "${clang_resource_dir}",
        "resource_target_dir": "${resource_target_dir}",
        "resource_builtins": "${resource_builtins}",
    },
    "logs": {
        "configure": "${configure_log}",
        "build": "${build_log}",
        "install": "${install_log}",
    },
    "merge_sysroot": ${MERGE_SYSROOT},
    "copied_runtime_libs": [x for x in """${copied_libs[*]}""".split() if x],
}

summary_path = Path("${SUMMARY}")
summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
print(f"ok: wrote {summary_path}")
PY

echo "ok: Linx C++ runtimes ready (mode=$MODE profile=$PROFILE target=$TARGET)"
