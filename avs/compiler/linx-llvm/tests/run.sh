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
  # Default: prefer the in-workspace LLVM submodule build, then fallback to sibling checkout.
  DEFAULT_CLANG="$ROOT/../../../../compiler/llvm/build-linxisa-clang/bin/clang"
  if [[ -x "$DEFAULT_CLANG" ]]; then
    CLANG="$DEFAULT_CLANG"
  else
    FALLBACK_CLANG="$ROOT/../../../../../llvm-project/build-linxisa-clang/bin/clang"
    if [[ -x "$FALLBACK_CLANG" ]]; then
      CLANG="$FALLBACK_CLANG"
    else
      echo "error: set CLANG=/path/to/clang (built with Linx target)" >&2
      exit 1
    fi
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

mkdir -p "$OUT_DIR"

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

  "$OBJDUMP" -d --triple="$TARGET" "$OUT/$BASE.o" >"$OUT/$BASE.objdump"

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
      41_v056_isa_forms)
        python3 "$ROOT/check_required_mnemonics.py" \
          --objdump "$OUT/$BASE.objdump" \
          --label "$BASE" \
          --require B.ARG \
          --require B.DIM \
          --require B.IOR \
          --require B.IOT \
          --require BSTART.ACCCVT \
          --require BSTART.CUBE \
          --require BSTART.FIXP \
          --require BSTART.TLOAD \
          --require BSTART.TMATMUL \
          --require BSTART.TMATMUL.ACC \
          --require BSTART.TMOV \
          --require BSTART.TSTORE \
          --require BSTART.VPAR \
          --require BSTART.VSEQ \
          --require C.BSTART.MPAR \
          --require C.BSTART.MSEQ \
          --require C.BSTART.SYS \
          --require C.BSTART.VPAR \
          --require C.BSTART.VSEQ \
          --require C.SSRGET \
          --require ERCOV \
          --require ESAVE \
          --require FENTRY \
          --require FRET.STK \
          --require HL.CASW.AQRLF \
          --require HL.CASD.AQRLF
        ;;
    esac
  done
fi

SPEC="${SPEC:-$ROOT/../../../../isa/v0.56/linxisa-v0.56.json}"
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

  echo "[asm] simt bstop spelling"
  if ! "$LLVMMC" -triple="$TARGET" -filetype=obj "$NEG_DIR/legacy_alias_l_bstop.s" -o "$NEG_OUT/legacy_alias_l_bstop.o" 2>"$NEG_OUT/legacy_alias_l_bstop.err"; then
    echo "error: L.BSTOP spelling did not assemble" >&2
    cat "$NEG_OUT/legacy_alias_l_bstop.err" >&2
    exit 1
  fi
  "$OBJDUMP" -d --triple="$TARGET" "$NEG_OUT/legacy_alias_l_bstop.o" >"$NEG_OUT/legacy_alias_l_bstop.objdump"
  if ! grep -Eq "\\bL\\.BSTOP\\b" "$NEG_OUT/legacy_alias_l_bstop.objdump"; then
    echo "error: L.BSTOP spelling did not disassemble as expected" >&2
    cat "$NEG_OUT/legacy_alias_l_bstop.objdump" >&2
    exit 1
  fi

  echo "[neg] TEPL tileop range rejection"
  if "$LLVMMC" -triple="$TARGET" -filetype=obj "$NEG_DIR/tepl_tileop_range.s" -o /dev/null 2>"$NEG_OUT/tepl_tileop_range.err"; then
    echo "error: TEPL range negative test unexpectedly assembled" >&2
    exit 1
  fi
  if ! grep -Eq "TileOp10 must be in range 0\\.\\.1023|TileOpcode must be in range 0\\.\\.1023|Match Instruction Error!" "$NEG_OUT/tepl_tileop_range.err"; then
    echo "error: TEPL range negative test did not report a range/match failure" >&2
    cat "$NEG_OUT/tepl_tileop_range.err" >&2
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
  if ! grep -Eq "R_LINX_.*PCREL[[:space:]]+foo|R_LinxV5_.*BNEXT[[:space:]]+foo" "$OUT/bar.o.relocs"; then
    echo "error: expected a PC-relative/call relocation against foo in $BASE" >&2
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

echo "ok: outputs in $OUT_DIR"
