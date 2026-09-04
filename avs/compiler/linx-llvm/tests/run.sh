#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$ROOT/c"
ASM_DIR="$ROOT/asm"
OUT_DIR="${OUT_DIR:-$ROOT/out}"
TARGET="${TARGET:-linx64-linx-none-elf}"
STRICT_CALLRET_RELOCS="${LINX_STRICT_CALLRET_RELOCS:-0}"

CLANG="${CLANG:-}"
if [[ -z "$CLANG" ]]; then
  # The pin lane resolves only through the superproject LLVM submodule.
  DEFAULT_CLANG="$ROOT/../../../../compiler/llvm/build-linxisa-clang/bin/clang"
  if [[ -x "$DEFAULT_CLANG" ]]; then
    CLANG="$DEFAULT_CLANG"
  else
    echo "error: pinned clang not found; build compiler/llvm or set CLANG to an explicit external tool" >&2
    exit 1
  fi
fi

TOOL_DIR="$(cd "$(dirname "$CLANG")" && pwd)"
LLVMMC="${LLVMMC:-$TOOL_DIR/llvm-mc}"
OBJDUMP="${OBJDUMP:-$TOOL_DIR/llvm-objdump}"
OBJCOPY="${OBJCOPY:-$TOOL_DIR/llvm-objcopy}"
READOBJ="${READOBJ:-$TOOL_DIR/llvm-readobj}"
LLD="${LLD:-$TOOL_DIR/ld.lld}"

if [[ ! -x "$OBJDUMP" ]]; then
  echo "error: llvm-objdump not found next to clang; set OBJDUMP=..." >&2
  exit 1
fi
if [[ ! -x "$LLVMMC" ]]; then
  echo "error: llvm-mc not found next to clang; set LLVMMC=..." >&2
  exit 1
fi
if [[ ! -x "$OBJCOPY" ]]; then
  echo "error: llvm-objcopy not found next to clang; set OBJCOPY=..." >&2
  exit 1
fi
if [[ ! -x "$READOBJ" ]]; then
  echo "warning: llvm-readobj not found next to clang; relocation checks disabled" >&2
  READOBJ=""
fi
if [[ ! -x "$LLD" ]]; then
  echo "error: ld.lld not found next to clang; set LLD=..." >&2
  exit 1
fi

detect_supported_target_arches() {
  "$CLANG" --print-targets 2>/dev/null | awk '/^[[:space:]]*[A-Za-z0-9_+-]+[[:space:]]+-/{print $1}'
}

TARGET_ARCH="${TARGET%%-*}"
SUPPORTED_TARGET_ARCHES="$(detect_supported_target_arches || true)"
if [[ -n "$SUPPORTED_TARGET_ARCHES" ]] && ! grep -qx "$TARGET_ARCH" <<<"$SUPPORTED_TARGET_ARCHES"; then
  SUPPORTED_LINX_ARCHES="$(grep '^linx' <<<"$SUPPORTED_TARGET_ARCHES" || true)"
  if [[ -n "$SUPPORTED_LINX_ARCHES" ]]; then
    SUPPORTED_LINX_ARCHES="$(tr '\n' ',' <<<"$SUPPORTED_LINX_ARCHES" | sed 's/,$//' | sed 's/,/, /g')"
    echo "error: target triple '$TARGET' is not registered by $CLANG; supported Linx arches: $SUPPORTED_LINX_ARCHES" >&2
  else
    echo "error: target triple '$TARGET' is not registered by $CLANG" >&2
  fi
  exit 1
fi

REPO_ROOT="$(cd "$ROOT/../../../../" && pwd)"
LIBC_DIR="$REPO_ROOT/avs/runtime/freestanding"
LIBC_INCLUDE="$LIBC_DIR/include"
CLANG_HEADERS_DIR="$REPO_ROOT/compiler/llvm/clang/lib/Headers"
SOFTFP_SRC="$LIBC_DIR/src/softfp/softfp.c"
SOFTFP_STUBS_SRC="$ROOT/support/softfp_stubs.c"
ATOMIC_BUILTINS_SRC="$LIBC_DIR/src/atomic/atomic_builtins.c"
SUPPORT_SYMBOLS_SRC="$ROOT/support/symbols.c"

MANIFEST_HELPER="$ROOT/write_c_codegen_manifest.py"
CODEGEN_MANIFEST="$OUT_DIR/c-codegen-build-manifest.json"
mkdir -p "$OUT_DIR"
rm -f "$CODEGEN_MANIFEST"
CODEGEN_RECORDS="$(mktemp "$OUT_DIR/.c-codegen-records.XXXXXX")"
CODEGEN_MANIFEST_COMPLETE=0
cleanup_codegen_manifest() {
  rm -f "$CODEGEN_RECORDS"
  if [[ "$CODEGEN_MANIFEST_COMPLETE" != "1" ]]; then
    rm -f "$CODEGEN_MANIFEST"
  fi
}
trap cleanup_codegen_manifest EXIT
if [[ ! -f "$MANIFEST_HELPER" ]]; then
  echo "error: missing C-CodeGen manifest helper: $MANIFEST_HELPER" >&2
  exit 1
fi

RUNTIME_OUT="$OUT_DIR/_runtime"
mkdir -p "$RUNTIME_OUT"

if [[ ! -f "$SUPPORT_SYMBOLS_SRC" ]]; then
  echo "error: missing compiler test support file: $SUPPORT_SYMBOLS_SRC" >&2
  exit 1
fi

echo "[rt] building test runtime"
"$CLANG" -target "$TARGET" -O2 -ffreestanding -fno-builtin -fno-stack-protector \
  -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-exceptions -fno-jump-tables \
  "-I$CLANG_HEADERS_DIR" \
  "-I$LIBC_INCLUDE" \
  -c "$SUPPORT_SYMBOLS_SRC" -o "$RUNTIME_OUT/support_symbols.o"
"$CLANG" -target "$TARGET" -O2 -ffreestanding -fno-builtin -fno-stack-protector \
  -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-exceptions -fno-jump-tables \
  "-I$CLANG_HEADERS_DIR" \
  "-I$LIBC_INCLUDE" \
  -c "$ATOMIC_BUILTINS_SRC" -o "$RUNTIME_OUT/atomic_builtins.o"
SOFTFP_IMPL_SRC="$SOFTFP_SRC"
SOFTFP_CFLAGS=(-target "$TARGET" -O0 -ffreestanding -fno-builtin -fno-stack-protector \
  -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-exceptions -fno-jump-tables \
  "-I$CLANG_HEADERS_DIR" \
  "-I$LIBC_INCLUDE")
if [[ "$TARGET" == linx32-* ]]; then
  SOFTFP_IMPL_SRC="$SOFTFP_STUBS_SRC"
  SOFTFP_CFLAGS=(-target "$TARGET" -O2 -ffreestanding -fno-builtin -fno-stack-protector \
    -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-exceptions -fno-jump-tables \
    "-I$CLANG_HEADERS_DIR")
fi
if [[ ! -f "$SOFTFP_IMPL_SRC" ]]; then
  echo "error: missing soft-fp runtime source: $SOFTFP_IMPL_SRC" >&2
  exit 1
fi
"$CLANG" "${SOFTFP_CFLAGS[@]}" -c "$SOFTFP_IMPL_SRC" -o "$RUNTIME_OUT/softfp.o"

COMMON_FLAGS=(
  -target "$TARGET"
  -O2
  -ffreestanding
  "-I$CLANG_HEADERS_DIR"
  "-I$LIBC_INCLUDE"
  -fno-builtin
  -fno-stack-protector
  -fno-asynchronous-unwind-tables
  -fno-unwind-tables
  -fno-exceptions
  -fno-jump-tables
)

EXTRA_FLAGS=()
if [[ -n "${EXTRA_CFLAGS:-}" ]]; then
  # Allow the caller to inject additional flags, e.g. EXTRA_CFLAGS="-g -O0"
  # shellcheck disable=SC2206
  EXTRA_FLAGS=(${EXTRA_CFLAGS})
fi

FAILED=0
for SRC in "$SRC_DIR"/*.c; do
  BASE="$(basename "$SRC" .c)"

  OUT="$OUT_DIR/$BASE"
  mkdir -p "$OUT"

  echo "[cc] $BASE"
  FLAGS=("${COMMON_FLAGS[@]}")

  # Per-test flag overrides.
  #
  # Keep the suite defaulting to `-fno-jump-tables` so that the compiler tests
  # remain stable as we bring up more features. Enable jump tables selectively
  # to keep coverage of the indirect-branch path.
  case "$BASE" in
    31_jump_tables)
      TMP_FLAGS=()
      for F in "${FLAGS[@]}"; do
        if [[ "$F" == "-fno-jump-tables" ]]; then
          continue
        fi
        TMP_FLAGS+=("$F")
      done
      FLAGS=("${TMP_FLAGS[@]}")
      ;;
  esac

  if [[ ${#EXTRA_FLAGS[@]} -ne 0 ]]; then
    FLAGS+=("${EXTRA_FLAGS[@]}")
  fi

  "$CLANG" "${FLAGS[@]}" -S -o "$OUT/$BASE.s" "$SRC"
  "$CLANG" "${FLAGS[@]}" -c -o "$OUT/$BASE.o" "$SRC"

  (cd "$OUT" && "$OBJDUMP" -d --triple="$TARGET" "$BASE.o") >"$OUT/$BASE.objdump"

  RECORD_CMD=(
    python3 "$MANIFEST_HELPER" record
    --repo-root "$REPO_ROOT"
    --records-jsonl "$CODEGEN_RECORDS"
    --source "$SRC"
    --generated-assembly "$OUT/$BASE.s"
    --object "$OUT/$BASE.o"
    --objdump "$OUT/$BASE.objdump"
  )
  for F in "${FLAGS[@]}"; do
    RECORD_CMD+=("--compile-flag=$F")
  done
  "${RECORD_CMD[@]}"

  # Link a standalone ELF to resolve relocations before extracting a raw .bin.
  #
  # The compile-only tests intentionally emit ET_REL objects that may contain
  # relocations (e.g. for PC-relative branches). Extracting `.text` directly
  # from the relocatable object would leave those fixups unapplied.
  LINK_INPUTS=("$OUT/$BASE.o" "$RUNTIME_OUT/support_symbols.o")
  case "$BASE" in
    20_floating_point)
      LINK_INPUTS+=("$RUNTIME_OUT/softfp.o")
      ;;
    21_atomic|29_cache_ops)
      LINK_INPUTS+=("$RUNTIME_OUT/atomic_builtins.o")
      ;;
  esac

  "$LLD" --entry=0 -o "$OUT/$BASE.elf" "${LINK_INPUTS[@]}"
  "$OBJCOPY" --only-section=.text -O binary "$OUT/$BASE.elf" "$OUT/$BASE.bin"
  wc -c "$OUT/$BASE.bin" >"$OUT/$BASE.bin.size"

  if [[ -n "$READOBJ" ]]; then
    "$READOBJ" -r "$OUT/$BASE.o" >"$OUT/$BASE.relocs" || true
    "$READOBJ" -r "$OUT/$BASE.elf" >"$OUT/$BASE.elf.relocs" || true

    case "$BASE" in
      33_callret_*|34_callret_*|35_callret_*|36_callret_*|37_callret_*|38_callret_*|39_callret_*|40_callret_*)
        CHECK_RELOCS_CMD=(
          python3 "$ROOT/check_callret_relocs.py"
          --asm "$OUT/$BASE.s"
          --objdump "$OUT/$BASE.objdump"
          --relocs "$OUT/$BASE.relocs"
          --label "$BASE"
        )
        if [[ "$STRICT_CALLRET_RELOCS" == "1" ]]; then
          CHECK_RELOCS_CMD+=(--strict-relocs)
        fi
        "${CHECK_RELOCS_CMD[@]}"
        case "$BASE" in
          33_callret_*|34_callret_*|35_callret_*|36_callret_*|37_callret_*|38_callret_*)
            python3 "$ROOT/check_callret_templates.py" \
              --asm "$OUT/$BASE.s" \
              --label "$BASE"
            ;;
        esac
        ;;
    esac

    if grep -Eq "^\\s*0x" "$OUT/$BASE.elf.relocs"; then
      echo "error: $BASE.elf still has relocations; .bin extraction is unsafe" >&2
      exit 1
    fi
  fi

  case "$BASE" in
    20_floating_point)
      python3 "$ROOT/check_fp_extloads.py" \
        --asm "$OUT/$BASE.s" \
        --label "$BASE"
      ;;
  esac
done

if [[ $FAILED -ne 0 ]]; then
  exit 1
fi

if [[ -d "$ASM_DIR" ]]; then
  for SRC in "$ASM_DIR"/*.s; do
    [[ -e "$SRC" ]] || continue
    BASE="$(basename "$SRC" .s)"

    OUT="$OUT_DIR/$BASE"
    mkdir -p "$OUT"

    echo "[asm] $BASE"
    "$LLVMMC" -triple="$TARGET" -filetype=obj "$SRC" -o "$OUT/$BASE.o"
    "$OBJDUMP" -d --triple="$TARGET" "$OUT/$BASE.o" >"$OUT/$BASE.objdump"
    "$LLD" --entry=0 -o "$OUT/$BASE.elf" "$OUT/$BASE.o"
    "$OBJCOPY" --only-section=.text -O binary "$OUT/$BASE.elf" "$OUT/$BASE.bin"
    wc -c "$OUT/$BASE.bin" >"$OUT/$BASE.bin.size"

    case "$BASE" in
      41_v0585_isa_forms)
        python3 "$ROOT/check_required_mnemonics.py" \
          --objdump "$OUT/$BASE.objdump" \
          --label "$BASE" \
          --require B.CATR \
          --require B.DATR \
          --require B.FPATR \
          --require B.IOT \
          --require BSTART.VEC \
          --require BSTART.SFU \
          --require BSTART.CALL \
          --require BSTART.ICALL \
          --require FENTRY \
          --require FRET.STK \
          --require L.BSTOP
        ;;
    esac
  done
fi

SPEC="${SPEC:-$ROOT/../../../../isa/v0.58/linxisa-v0.58.json}"
GEN_VECTORS="$ROOT/gen_disasm_vectors.py"
ROUNDTRIP_CHECK="$ROOT/check_disasm_roundtrip.py"
SPEC_ROUNDTRIP_POLICY="${SPEC_ROUNDTRIP_POLICY:-audit}" # audit|strict

if [[ -f "$SPEC" && -f "$GEN_VECTORS" && -f "$ROUNDTRIP_CHECK" ]]; then
  BASE="99_spec_decode"
  OUT="$OUT_DIR/$BASE"
  mkdir -p "$OUT"
  echo "[gen] $BASE"

  python3 "$GEN_VECTORS" --spec "$SPEC" --out "$OUT/$BASE.s"
  "$CLANG" -target "$TARGET" -c -o "$OUT/$BASE.o" "$OUT/$BASE.s"
  "$OBJDUMP" -d --triple="$TARGET" "$OUT/$BASE.o" >"$OUT/$BASE.objdump"
  "$LLD" --entry=0 -o "$OUT/$BASE.elf" "$OUT/$BASE.o"
  "$OBJCOPY" --only-section=.text -O binary "$OUT/$BASE.elf" "$OUT/$BASE.bin"
  wc -c "$OUT/$BASE.bin" >"$OUT/$BASE.bin.size"
  python3 "$ROUNDTRIP_CHECK" \
    --input-objdump "$OUT/$BASE.objdump" \
    --asm-out "$OUT/$BASE.roundtrip.s" \
    --roundtrip-obj "$OUT/$BASE.roundtrip.o" \
    --roundtrip-objdump "$OUT/$BASE.roundtrip.objdump" \
    --report-out "$OUT/$BASE.roundtrip.json" \
    --mc "$LLVMMC" \
    --objdump "$OBJDUMP" \
    --triple "$TARGET"
  if [[ "$SPEC_ROUNDTRIP_POLICY" == "strict" ]]; then
    python3 "$ROUNDTRIP_CHECK" \
      --input-objdump "$OUT/$BASE.objdump" \
      --asm-out "$OUT/$BASE.roundtrip.strict.s" \
      --roundtrip-obj "$OUT/$BASE.roundtrip.strict.o" \
      --roundtrip-objdump "$OUT/$BASE.roundtrip.strict.objdump" \
      --report-out "$OUT/$BASE.roundtrip.strict.json" \
      --mc "$LLVMMC" \
      --objdump "$OBJDUMP" \
      --triple "$TARGET" \
      --require-all
  fi
else
  echo "warning: spec decode vectors skipped (missing $SPEC, $GEN_VECTORS, or $ROUNDTRIP_CHECK)" >&2
fi

NEG_DIR="$ROOT/neg"
if [[ -d "$NEG_DIR" ]]; then
  NEG_OUT="$OUT_DIR/_neg"
  mkdir -p "$NEG_OUT"

  echo "[neg] L.BSTART.SYS non-FALL rejection"
  if "$LLVMMC" -triple="$TARGET" -filetype=obj "$NEG_DIR/l_bstart64_invalid_sys_kind.s" -o "$NEG_OUT/l_bstart64_invalid_sys_kind.o" 2>"$NEG_OUT/l_bstart64_invalid_sys_kind.err"; then
    echo "error: invalid L.BSTART.SYS branch kind unexpectedly assembled" >&2
    exit 1
  fi
  if ! grep -Eq "branch kind does not match BSTART encoding" "$NEG_OUT/l_bstart64_invalid_sys_kind.err"; then
    echo "error: invalid L.BSTART.SYS rejection did not report a branch-kind failure" >&2
    cat "$NEG_OUT/l_bstart64_invalid_sys_kind.err" >&2
    exit 1
  fi

  echo "[neg] TEPL tileop range rejection"
  if "$LLVMMC" -triple="$TARGET" -filetype=obj "$NEG_DIR/tepl_tileop_range.s" -o /dev/null 2>"$NEG_OUT/tepl_tileop_range.err"; then
    echo "error: TEPL range negative test unexpectedly assembled" >&2
    exit 1
  fi
  if ! grep -Eq "BSTART\\.TEPL requires Mode 0\\.\\.3 and Function 0\\.\\.31|Match Instruction Error!" "$NEG_OUT/tepl_tileop_range.err"; then
    echo "error: TEPL range negative test did not report the Mode/Function range failure" >&2
    cat "$NEG_OUT/tepl_tileop_range.err" >&2
    exit 1
  fi

  echo "[neg] legacy generic BSTART.TMA rejection"
  if "$LLVMMC" -triple="$TARGET" -filetype=obj "$NEG_DIR/retired_bstart_tma.s" -o /dev/null 2>"$NEG_OUT/retired_bstart_tma.err"; then
    echo "error: legacy generic BSTART.TMA unexpectedly assembled" >&2
    exit 1
  fi
  if ! grep -Eqi "unrecognized instruction 'bstart\\.tma'" "$NEG_OUT/retired_bstart_tma.err"; then
    echo "error: legacy generic BSTART.TMA rejection did not report an unrecognized instruction" >&2
    cat "$NEG_OUT/retired_bstart_tma.err" >&2
    exit 1
  fi
fi

if [[ -n "$READOBJ" ]]; then
  BASE="98_pic_reloc"
  OUT="$OUT_DIR/$BASE"
  mkdir -p "$OUT"
  echo "[pic] $BASE"

  cat >"$OUT/foo.c" <<'C'
__attribute__((visibility("default"))) int foo(int x) { return x + 1; }
C
  cat >"$OUT/bar.c" <<'C'
extern int foo(int);
__attribute__((visibility("default"))) int bar(int x) { return foo(x) + 2; }
C

  "$CLANG" -target "$TARGET" -fPIC -c "$OUT/foo.c" -o "$OUT/foo.o"
  "$CLANG" -target "$TARGET" -fPIC -c "$OUT/bar.c" -o "$OUT/bar.o"

  "$READOBJ" -r "$OUT/bar.o" >"$OUT/bar.o.relocs"
  if ! grep -Eq "R_LINX_.*PCREL[[:space:]]+foo|R_LinxV5_.*BNEXT[[:space:]]+foo|R_LinxV5_64[[:space:]]+foo" "$OUT/bar.o.relocs"; then
    echo "error: expected a recognized Linx call/data relocation against foo in $BASE" >&2
    exit 1
  fi

  # Shared-library linking is intentionally not a hard requirement during
  # bring-up. The current Linx toolchain does not yet lower call relocations to
  # PLT/GOT forms that are linkable into ET_DYN. Keep the full dynamic-linking
  # test gated behind an explicit opt-in.
  if [[ -n "${LINX_ENABLE_SHARED_LIB_TEST:-}" ]]; then
    echo "[plt] 98_plt_shared (enabled)"
    "$LLD" -shared -o "$OUT/libfoo.so" "$OUT/foo.o"
    "$LLD" -shared -o "$OUT/libbar.so" "$OUT/bar.o" -L"$OUT" -lfoo -z now
  fi
else
  echo "warning: PIC relocation test skipped (missing llvm-readobj)" >&2
fi

COMPLETE_MANIFEST_CMD=(
  python3 "$MANIFEST_HELPER" complete
  --repo-root "$REPO_ROOT"
  --records-jsonl "$CODEGEN_RECORDS"
  --source-dir "$SRC_DIR"
  --target "$TARGET"
  --clang "$CLANG"
  --llvm-objdump "$OBJDUMP"
  --output "$CODEGEN_MANIFEST"
)
if [[ ${#EXTRA_FLAGS[@]} -ne 0 ]]; then
  for F in "${EXTRA_FLAGS[@]}"; do
    COMPLETE_MANIFEST_CMD+=("--extra-flag=$F")
  done
fi
"${COMPLETE_MANIFEST_CMD[@]}"
CODEGEN_MANIFEST_COMPLETE=1

echo "ok: outputs in $OUT_DIR"
