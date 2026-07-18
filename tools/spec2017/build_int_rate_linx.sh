#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
SPEC_DIR="${SPEC_DIR:-$ROOT/workloads/spec2017/cpu2017v118_x64_gcc12_avx2}"
MODE="${MODE:-phase-b}"
JOBS="${JOBS:-$(sysctl -n hw.ncpu 2>/dev/null || echo 8)}"
OPTIMIZE_FLAGS="${OPTIMIZE_FLAGS:--O0 -fno-vectorize -fno-slp-vectorize}"
REEXTRACT=0
BUILD_RUNTIMES=0
EMIT_MANIFEST=""
FORCE_STATIC="${LINX_SPEC_FORCE_STATIC:-0}"
CLI_BENCHES=()
BENCH_OPTIMIZE_OVERRIDES=()

usage() {
  cat <<EOF
Usage: build_int_rate_linx.sh [options]

Options:
  --spec-dir <path>      SPEC bundle root (default: $SPEC_DIR)
  --mode <phase-a|phase-b|phase-c>   Sysroot mode for wrappers (default: $MODE)
  --jobs <N>             Parallel jobs for gmake (default: $JOBS)
  --optimize <flags>     Optimization flags override (default: "$OPTIMIZE_FLAGS")
  --bench-optimize <bench=flags>
                         Per-benchmark optimization flags override (repeatable).
                         Environment alternative: LINX_SPEC_BENCH_OPTIMIZE
                         with semicolon-separated bench=flags entries.
  --bench <name>         Benchmark to build (repeatable). Overrides LINX_SPEC_BENCHES.
  --emit-manifest <path> Write build/readelf evidence manifest JSON to <path>
  --reextract            Re-extract SPEC zip and refresh baseline manifest
  --build-runtimes       Build/merge spec-profile libc++ runtimes before gmake
  --force-static         Build phase-b style static PIE executables
  --shared-runtime       Build hosted shared-runtime executables
  -h, --help             Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --spec-dir)
      SPEC_DIR="$2"
      shift 2
      ;;
    --mode)
      MODE="$2"
      shift 2
      ;;
    --jobs)
      JOBS="$2"
      shift 2
      ;;
    --optimize)
      OPTIMIZE_FLAGS="$2"
      shift 2
      ;;
    --bench-optimize)
      BENCH_OPTIMIZE_OVERRIDES+=("$2")
      shift 2
      ;;
    --bench)
      CLI_BENCHES+=("$2")
      shift 2
      ;;
    --emit-manifest)
      EMIT_MANIFEST="$2"
      shift 2
      ;;
    --reextract)
      REEXTRACT=1
      shift
      ;;
    --build-runtimes)
      BUILD_RUNTIMES=1
      shift
      ;;
    --force-static)
      FORCE_STATIC=1
      shift
      ;;
    --shared-runtime)
      FORCE_STATIC=0
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

if [[ -n "${LINX_SPEC_BENCH_OPTIMIZE:-}" ]]; then
  while IFS= read -r entry; do
    [[ -n "$entry" ]] || continue
    BENCH_OPTIMIZE_OVERRIDES+=("$entry")
  done < <(printf '%s\n' "$LINX_SPEC_BENCH_OPTIMIZE" | tr ';' '\n' | sed '/^$/d')
fi

case "$MODE" in
  phase-a|phase-b|phase-c) ;;
  *)
    echo "error: --mode must be phase-a, phase-b, or phase-c (got '$MODE')" >&2
    exit 2
    ;;
esac

if [[ "$REEXTRACT" == "1" ]]; then
  "$ROOT/tools/spec2017/reextract_cpu2017.sh"
fi

SPEC_DIR="$(cd "$SPEC_DIR" && pwd -P)"
if [[ ! -d "$SPEC_DIR/benchspec/CPU" ]]; then
  echo "error: invalid SPEC dir: $SPEC_DIR" >&2
  exit 2
fi

if [[ "$BUILD_RUNTIMES" == "1" ]]; then
  runtime_profile="${LINX_RUNTIME_PROFILE:-spec}"
  "$ROOT/tools/build_linx_llvm_cpp_runtimes.sh" --profile "$runtime_profile" --mode "$MODE"
fi

LOG_DIR="$SPEC_DIR/tmp/linx-build-logs"
mkdir -p "$LOG_DIR"
BASELINE_MANIFEST="$LOG_DIR/src-baseline.sha256"
POST_MANIFEST="$LOG_DIR/src-postbuild.sha256"
DRIFT_DIFF="$LOG_DIR/src-drift.diff"
DRIFT_PATHS="$LOG_DIR/src-drift-paths.txt"
SOURCE_ROOT="$SPEC_DIR/benchspec/CPU"

python3 "$ROOT/tools/spec2017/check_build_manifest.py" check-source-symlinks \
  --source-root "$SOURCE_ROOT"

if [[ ! -f "$BASELINE_MANIFEST" ]]; then
  find "$SOURCE_ROOT" -type f -path '*/src/*' -print0 \
    | LC_ALL=C sort -z \
    | xargs -0 shasum -a 256 > "$BASELINE_MANIFEST"
fi

CC_WRAPPER="$ROOT/tools/spec2017/linx_cc.sh"
CXX_WRAPPER="$ROOT/tools/spec2017/linx_cxx.sh"
chmod +x "$CC_WRAPPER" "$CXX_WRAPPER" "$ROOT/tools/spec2017/reextract_cpu2017.sh"

export LINX_SYSROOT="${LINX_SYSROOT:-$ROOT/out/libc/musl/install/$MODE}"
if [[ -n "${LINX_SPEC_LINK_MODE:-}" || -n "${LINX_SPEC_COMPAT_INCLUDE:-}" ]]; then
  echo "error: legacy SPEC link/compat controls were removed; use the canonical sysroot/CRT" >&2
  exit 2
fi
export LINX_SPEC_FORCE_STATIC="$FORCE_STATIC"

MAKE_BIN="${MAKE:-make}"
if [[ -z "${MAKE:-}" && "$(uname -s)" == "Darwin" ]] && command -v gmake >/dev/null 2>&1; then
  MAKE_BIN="gmake"
fi
if ! command -v "$MAKE_BIN" >/dev/null 2>&1; then
  echo "error: make tool not found: $MAKE_BIN" >&2
  exit 2
fi

LLVM_READELF="${LLVM_READELF:-}"
if [[ -z "$LLVM_READELF" ]]; then
  cand="$ROOT/compiler/llvm/build-linxisa-clang/bin/llvm-readelf"
  if [[ -x "$cand" ]]; then
    LLVM_READELF="$cand"
  fi
fi
if [[ -z "$LLVM_READELF" ]] && command -v llvm-readelf >/dev/null 2>&1; then
  LLVM_READELF="$(command -v llvm-readelf)"
fi
if [[ -z "$LLVM_READELF" || ! -x "$LLVM_READELF" ]]; then
  echo "error: llvm-readelf not found; set LLVM_READELF=/path/to/llvm-readelf" >&2
  exit 2
fi

LINX_CLANG_RESOLVED="${LINX_CLANG:-$ROOT/compiler/llvm/build-linxisa-clang/bin/clang}"
if [[ ! -x "$LINX_CLANG_RESOLVED" ]]; then
  echo "error: clang not found; set LINX_CLANG=/path/to/clang" >&2
  exit 2
fi

expected_exes() {
  case "$1" in
    500.perlbench_r) echo "perlbench_r_base.mytest-m64" ;;
    502.gcc_r) echo "cpugcc_r_base.mytest-m64" ;;
    505.mcf_r) echo "mcf_r_base.mytest-m64" ;;
    520.omnetpp_r) echo "omnetpp_r_base.mytest-m64" ;;
    523.xalancbmk_r) echo "cpuxalan_r_base.mytest-m64" ;;
    525.x264_r) echo "x264_r_base.mytest-m64 ldecod_r_base.mytest-m64 imagevalidate_525_base.mytest-m64" ;;
    531.deepsjeng_r) echo "deepsjeng_r_base.mytest-m64" ;;
    541.leela_r) echo "leela_r_base.mytest-m64" ;;
    557.xz_r) echo "xz_r_base.mytest-m64" ;;
    999.specrand_ir) echo "specrand_ir_base.mytest-m64" ;;
    *) echo "" ;;
  esac
}

is_supported_bench() {
  case "$1" in
    500.perlbench_r|502.gcc_r|505.mcf_r|520.omnetpp_r|523.xalancbmk_r|525.x264_r|531.deepsjeng_r|541.leela_r|557.xz_r|999.specrand_ir)
      return 0
      ;;
  esac
  return 1
}

bench_optimize_flags() {
  local bench="$1"
  local result="$OPTIMIZE_FLAGS"
  local entry
  local key
  local value

  for entry in ${BENCH_OPTIMIZE_OVERRIDES[@]+"${BENCH_OPTIMIZE_OVERRIDES[@]}"}; do
    key="${entry%%=*}"
    value="${entry#*=}"
    if [[ "$entry" == "$key" || -z "$key" || -z "$value" ]]; then
      echo "error: malformed --bench-optimize entry '$entry' (expected bench=flags)" >&2
      exit 2
    fi
    if ! is_supported_bench "$key"; then
      echo "error: unsupported --bench-optimize benchmark '$key'" >&2
      exit 2
    fi
    if [[ "$key" == "$bench" ]]; then
      result="$value"
    fi
  done

  printf '%s\n' "$result"
}

candidate_exe_names() {
  local bench="$1"
  local expected="$2"
  local raw="${expected%_base.mytest-m64}"

  printf '%s\n' "$expected"
  printf '%s\n' "$raw"

  case "$bench:$raw" in
    502.gcc_r:cpugcc_r)
      printf '%s\n' "cpugcc"
      ;;
    523.xalancbmk_r:cpuxalan_r)
      printf '%s\n' "cpuxalan"
      printf '%s\n' "xalancbmk_r"
      ;;
    525.x264_r:imagevalidate_525)
      printf '%s\n' "imagevalidate"
      ;;
    541.leela_r:leela_r)
      printf '%s\n' "leela"
      ;;
  esac
}

stage_expected_exe() {
  local bench="$1"
  local build_dir="$2"
  local exe_dir="$3"
  local expected="$4"
  local log_file="$5"
  local cand

  while IFS= read -r cand; do
    [[ -n "$cand" ]] || continue
    if [[ -f "$build_dir/$cand" ]]; then
      mkdir -p "$exe_dir"
      cp -f "$build_dir/$cand" "$exe_dir/$expected"
      chmod +x "$exe_dir/$expected" || true
      echo "info: staged executable for $bench: $build_dir/$cand -> $exe_dir/$expected" >>"$log_file"
      return 0
    fi
  done < <(candidate_exe_names "$bench" "$expected")

  return 1
}

normalize_elf_hex() {
  local value="$1"

  value="${value#0x}"
  value="${value#0X}"
  value="$(printf '%s' "$value" | tr 'A-F' 'a-f' | sed -E 's/^0+//')"
  if [[ -z "$value" ]]; then
    value="0"
  fi
  printf '%s\n' "$value"
}

read_symbol_value() {
  local exe="$1"
  local symbol="$2"

  "$LLVM_READELF" -s "$exe" 2>/dev/null \
    | awk -v sym="$symbol" '$NF == sym { print $2; exit }'
}

validate_static_entry() {
  local exe="$1"
  local bench="$2"
  local log_file="$3"
  local entry
  local start_value
  local main_value
  local entry_norm
  local start_norm
  local main_norm

  entry="$("$LLVM_READELF" -h "$exe" 2>/dev/null \
    | awk '/Entry point address:/ { print $4; exit }')"
  if [[ -z "$entry" ]]; then
    echo "error: could not read ELF entry for $bench: $exe" >>"$log_file"
    return 1
  fi

  start_value="$(read_symbol_value "$exe" _start)"
  if [[ -z "$start_value" ]]; then
    echo "error: forced-static executable for $bench lacks _start symbol: $exe" >>"$log_file"
    "$LLVM_READELF" -h "$exe" >>"$log_file" 2>&1 || true
    return 1
  fi

  entry_norm="$(normalize_elf_hex "$entry")"
  start_norm="$(normalize_elf_hex "$start_value")"
  if [[ "$entry_norm" != "$start_norm" ]]; then
    main_value="$(read_symbol_value "$exe" main)"
    main_norm=""
    if [[ -n "$main_value" ]]; then
      main_norm="$(normalize_elf_hex "$main_value")"
    fi
    if [[ -n "$main_norm" && "$entry_norm" == "$main_norm" ]]; then
      echo "error: forced-static executable for $bench enters at main instead of _start: $exe" >>"$log_file"
    else
      echo "error: forced-static executable for $bench entry 0x$entry_norm does not match _start 0x$start_norm: $exe" >>"$log_file"
    fi
    "$LLVM_READELF" -h -s "$exe" >>"$log_file" 2>&1 || true
    return 1
  fi

  return 0
}

build_benchmark() {
  local bench="$1"
  local build_dir="$SPEC_DIR/benchspec/CPU/$bench/build/build_base_mytest-m64.0000"
  local exe_dir="$SPEC_DIR/benchspec/CPU/$bench/exe"
  local log_file="$LOG_DIR/${bench}.log"
  local expected
  local bench_optimize

  expected="$(expected_exes "$bench")"
  bench_optimize="$(bench_optimize_flags "$bench")"

  if [[ ! -d "$build_dir" ]]; then
    echo "error: missing build dir for $bench: $build_dir" >"$log_file"
    return 1
  fi

  {
    echo "[bench] $bench"
    echo "[build_dir] $build_dir"
    echo "[mode] $MODE"
    echo "[optimize] $bench_optimize"
    if [[ "$bench_optimize" != "$OPTIMIZE_FLAGS" ]]; then
      echo "[global_optimize] $OPTIMIZE_FLAGS"
    fi
    echo "[cc] $CC_WRAPPER"
    echo "[cxx] $CXX_WRAPPER"
    echo "[sysroot] $LINX_SYSROOT"
    echo "[link_mode] canonical-crt"
    echo "[force_static] $LINX_SPEC_FORCE_STATIC"
    echo "[readelf] $LLVM_READELF"
    echo
    cd "$build_dir"
    for exe in $expected; do
      rm -f "$exe_dir/$exe"
    done

    bench_targets=("")
    if [[ "$bench" == "525.x264_r" ]]; then
      bench_targets=("x264_r" "ldecod_r" "imagevalidate_525")
    fi
    link_driver="$CC_WRAPPER"
    case "$bench" in
      520.omnetpp_r|523.xalancbmk_r|541.leela_r)
        link_driver="$CXX_WRAPPER"
        ;;
    esac

    for bench_target in "${bench_targets[@]}"; do
      target_args=()
      if [[ -n "$bench_target" ]]; then
        target_args=(TARGET="$bench_target")
      fi

      "$MAKE_BIN" \
        SPEC="$SPEC_DIR" \
        CC="$CC_WRAPPER" \
        CXX="$CXX_WRAPPER" \
        LD="$link_driver" \
        CLD="$link_driver" \
        CXXLD="$CXX_WRAPPER" \
        FC=false \
        SPECLANG= \
        OPTIMIZE="$bench_optimize" \
        EXTRA_OPTIMIZE= \
        EXTRA_COPTIMIZE= \
        EXTRA_CXXOPTIMIZE= \
        PORTABILITY= \
        EXTRA_PORTABILITY= \
        ${target_args[@]+"${target_args[@]}"} \
        clean || true

      "$MAKE_BIN" -j"$JOBS" \
        SPEC="$SPEC_DIR" \
        CC="$CC_WRAPPER" \
        CXX="$CXX_WRAPPER" \
        LD="$link_driver" \
        CLD="$link_driver" \
        CXXLD="$CXX_WRAPPER" \
        FC=false \
        SPECLANG= \
        OPTIMIZE="$bench_optimize" \
        EXTRA_OPTIMIZE= \
        EXTRA_COPTIMIZE= \
        EXTRA_CXXOPTIMIZE= \
        PORTABILITY= \
        EXTRA_PORTABILITY= \
        ${target_args[@]+"${target_args[@]}"}
    done
  } >"$log_file" 2>&1

  for exe in $expected; do
    if [[ ! -f "$exe_dir/$exe" ]]; then
      stage_expected_exe "$bench" "$build_dir" "$exe_dir" "$exe" "$log_file" || true
    fi
    if [[ ! -f "$exe_dir/$exe" ]]; then
      echo "error: missing expected executable for $bench: $exe_dir/$exe" >>"$log_file"
      return 1
    fi
    machine_line="$("$LLVM_READELF" -h "$exe_dir/$exe" 2>/dev/null \
      | awk -F'Machine:' '/Machine:/ { print $2; exit }')"
    if [[ "$machine_line" != *Linx* && "$machine_line" != *EM_LINXISA* ]]; then
      echo "error: non-Linx executable for $bench: $exe_dir/$exe" >>"$log_file"
      "$LLVM_READELF" -h "$exe_dir/$exe" >>"$log_file" 2>&1 || true
      return 1
    fi
    if [[ "$FORCE_STATIC" == "1" ]]; then
      if ! validate_static_entry "$exe_dir/$exe" "$bench" "$log_file"; then
        return 1
      fi
    fi
  done

  return 0
}

benchmarks=()
if [[ ${#CLI_BENCHES[@]} -gt 0 ]]; then
  for bench in "${CLI_BENCHES[@]}"; do
    if ! is_supported_bench "$bench"; then
      echo "error: unsupported --bench '$bench'" >&2
      exit 2
    fi
    already_added=0
    for added in ${benchmarks[@]+"${benchmarks[@]}"}; do
      if [[ "$added" == "$bench" ]]; then
        already_added=1
        break
      fi
    done
    if [[ "$already_added" == "0" ]]; then
      benchmarks+=("$bench")
    fi
  done
elif [[ -n "${LINX_SPEC_BENCHES:-}" ]]; then
  while IFS= read -r bench; do
    [[ -n "$bench" ]] || continue
    if ! is_supported_bench "$bench"; then
      echo "error: unsupported LINX_SPEC_BENCHES entry '$bench'" >&2
      exit 2
    fi
    benchmarks+=("$bench")
  done < <(printf '%s\n' "$LINX_SPEC_BENCHES" | tr ', ' '\n\n' | sed '/^$/d')
else
  benchmarks=(
    "500.perlbench_r"
    "502.gcc_r"
    "505.mcf_r"
    "520.omnetpp_r"
    "523.xalancbmk_r"
    "525.x264_r"
    "531.deepsjeng_r"
    "541.leela_r"
    "557.xz_r"
    "999.specrand_ir"
  )
fi

echo "skip: 548.exchange2_r (Fortran/toolchain out-of-scope)" >"$LOG_DIR/548.exchange2_r.log"

failed=()
for bench in "${benchmarks[@]}"; do
  if ! build_benchmark "$bench"; then
    failed+=("$bench")
  fi
done

python3 "$ROOT/tools/spec2017/check_build_manifest.py" check-source-symlinks \
  --source-root "$SOURCE_ROOT"

find "$SOURCE_ROOT" -type f -path '*/src/*' -print0 \
  | LC_ALL=C sort -z \
  | xargs -0 shasum -a 256 > "$POST_MANIFEST"

if ! python3 "$ROOT/tools/spec2017/check_build_manifest.py" refresh-source-drift \
  --baseline "$BASELINE_MANIFEST" \
  --post "$POST_MANIFEST" \
  --diff-out "$DRIFT_DIFF" \
  --paths-out "$DRIFT_PATHS"
then
  failed+=("__src_drift__")
fi

BENCH_OPTIMIZE_MANIFEST="$LOG_DIR/bench-optimize.tsv"
: >"$BENCH_OPTIMIZE_MANIFEST"
for bench in "${benchmarks[@]}"; do
  printf '%s\t%s\n' "$bench" "$(bench_optimize_flags "$bench")" >>"$BENCH_OPTIMIZE_MANIFEST"
done

if [[ -n "$EMIT_MANIFEST" ]]; then
  manifest_out="$EMIT_MANIFEST"
  if [[ "$manifest_out" != /* ]]; then
    manifest_out="$ROOT/$manifest_out"
  fi
  mkdir -p "$(dirname "$manifest_out")"

  benchmarks_csv="$(IFS=,; echo "${benchmarks[*]-}")"
  failed_csv="$(IFS=,; echo "${failed[*]-}")"
  python3 - "$manifest_out" "$SPEC_DIR" "$MODE" "$OPTIMIZE_FLAGS" "$BENCH_OPTIMIZE_MANIFEST" "canonical-crt" "$LINX_SPEC_FORCE_STATIC" "$LLVM_READELF" "$LINX_CLANG_RESOLVED" "$LINX_SYSROOT" "${LINX_TARGET:-linx64-unknown-linux-musl}" "$LOG_DIR" "$BASELINE_MANIFEST" "$POST_MANIFEST" "$DRIFT_PATHS" "$benchmarks_csv" "$failed_csv" <<'PY'
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

manifest_out = Path(sys.argv[1]).resolve()
spec_dir = Path(sys.argv[2]).resolve()
mode = sys.argv[3]
optimize_flags = sys.argv[4]
bench_optimize_manifest = Path(sys.argv[5]).resolve()
link_mode = sys.argv[6]
force_static = sys.argv[7] == "1"
llvm_readelf = Path(sys.argv[8])
clang = Path(sys.argv[9]).resolve()
sysroot = Path(sys.argv[10]).resolve()
target = sys.argv[11]
log_dir = Path(sys.argv[12]).resolve()
baseline_manifest = Path(sys.argv[13]).resolve()
post_manifest = Path(sys.argv[14]).resolve()
drift_paths = Path(sys.argv[15]).resolve()
benchmarks = [x for x in sys.argv[16].split(",") if x]
failed = {x for x in sys.argv[17].split(",") if x}

bench_optimize_flags = {}
if bench_optimize_manifest.exists():
    for line in bench_optimize_manifest.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        bench, flags = line.split("\t", 1)
        bench_optimize_flags[bench] = flags

expected = {
    "500.perlbench_r": ["perlbench_r_base.mytest-m64"],
    "502.gcc_r": ["cpugcc_r_base.mytest-m64"],
    "505.mcf_r": ["mcf_r_base.mytest-m64"],
    "520.omnetpp_r": ["omnetpp_r_base.mytest-m64"],
    "523.xalancbmk_r": ["cpuxalan_r_base.mytest-m64"],
    "525.x264_r": [
        "x264_r_base.mytest-m64",
        "ldecod_r_base.mytest-m64",
        "imagevalidate_525_base.mytest-m64",
    ],
    "531.deepsjeng_r": ["deepsjeng_r_base.mytest-m64"],
    "541.leela_r": ["leela_r_base.mytest-m64"],
    "557.xz_r": ["xz_r_base.mytest-m64"],
    "999.specrand_ir": ["specrand_ir_base.mytest-m64"],
}

def _readelf_machine(path: Path):
    try:
        out = subprocess.check_output(
            [str(llvm_readelf), "-h", str(path)],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except Exception:
        return None
    for line in out.splitlines():
        if "Machine:" in line:
            return line.split("Machine:", 1)[1].strip()
    return None

def _readelf_entry(path: Path):
    try:
        out = subprocess.check_output(
            [str(llvm_readelf), "-h", str(path)],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except Exception:
        return None
    for line in out.splitlines():
        if "Entry point address:" in line:
            return line.split(":", 1)[1].strip()
    return None

def _readelf_symbol(path: Path, name: str):
    try:
        out = subprocess.check_output(
            [str(llvm_readelf), "-s", str(path)],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except Exception:
        return None
    for line in out.splitlines():
        parts = line.split()
        if parts and parts[-1] == name and len(parts) >= 2:
            return parts[1]
    return None

def _normalize_hex(value):
    if not value:
        return None
    value = str(value).strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    value = value.lstrip("0") or "0"
    return value

def _is_linx_machine(machine):
    if not machine:
        return False
    normalized = machine.strip().lower()
    return ("linx" in normalized) or ("em_linxisa" in normalized)

bench_results: dict[str, object] = {}
for bench in benchmarks:
    exes = expected.get(bench, [])
    exe_results = []
    all_exists = True
    all_linx = True
    for exe in exes:
        exe_path = spec_dir / "benchspec" / "CPU" / bench / "exe" / exe
        exists = exe_path.exists()
        machine = _readelf_machine(exe_path) if exists else None
        entry = _readelf_entry(exe_path) if exists else None
        start_symbol = _readelf_symbol(exe_path, "_start") if exists else None
        main_symbol = _readelf_symbol(exe_path, "main") if exists else None
        is_linx = _is_linx_machine(machine)
        static_entry_ok = (
            (not force_static)
            or (
                _normalize_hex(entry) is not None
                and _normalize_hex(entry) == _normalize_hex(start_symbol)
                and (
                    _normalize_hex(main_symbol) is None
                    or _normalize_hex(entry) != _normalize_hex(main_symbol)
                )
            )
        )
        all_exists = all_exists and exists
        all_linx = all_linx and is_linx
        exe_results.append(
            {
                "name": exe,
                "path": str(exe_path),
                "exists": exists,
                "machine": machine,
                "is_linx_machine": is_linx,
                "entry_point": entry,
                "start_symbol": start_symbol,
                "main_symbol": main_symbol,
                "static_entry_ok": static_entry_ok,
            }
        )
    build_ok = bench not in failed
    bench_results[bench] = {
        "build_ok": build_ok,
        "all_expected_exes_present": all_exists,
        "all_expected_exes_linx_machine": all_linx,
        "optimize_flags": bench_optimize_flags.get(bench, optimize_flags),
        "uses_global_optimize_flags": bench_optimize_flags.get(bench, optimize_flags) == optimize_flags,
        "log": str(log_dir / f"{bench}.log"),
        "executables": exe_results,
    }

source_immutability = {
    "baseline_manifest": str(baseline_manifest),
    "post_manifest": str(post_manifest),
    "manifests_match": "__src_drift__" not in failed,
    "drift_paths": str(drift_paths) if drift_paths.exists() else None,
}

manifest = {
    "schema_version": "linx-spec-build-manifest-v1",
    "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
    "spec_dir": str(spec_dir),
    "mode": mode,
    "optimize_flags": optimize_flags,
    "bench_optimize_flags": {bench: bench_optimize_flags.get(bench, optimize_flags) for bench in benchmarks},
    "link_mode": link_mode,
    "force_static": force_static,
    "target": target,
    "sysroot": str(sysroot),
    "clang": str(clang),
    "llvm_readelf": str(llvm_readelf),
    "selected_benchmarks": benchmarks,
    "bench_results": bench_results,
    "fortran_exclusion": {
        "benchmark": "548.exchange2_r",
        "excluded": True,
        "reason": "Fortran/toolchain out-of-scope",
        "evidence_log": str(log_dir / "548.exchange2_r.log"),
    },
    "source_immutability": source_immutability,
    "failed_entries": sorted(failed),
    "overall_ok": len(failed) == 0,
}
manifest_out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
  echo "ok: wrote manifest $manifest_out"
fi

if [[ ${#failed[@]} -gt 0 ]]; then
  printf 'failed benchmarks/checks:\n' >&2
  printf '  - %s\n' "${failed[@]}" >&2
  exit 1
fi

echo "ok: all selected INT C/C++ benchmarks built"
echo "ok: logs under $LOG_DIR"
echo "ok: source immutability check passed"
