# Phase 1: Compiler Bring-up

Compiler implementation source of truth is the LLVM submodule:

- `compiler/llvm/`

In-repo compile validation assets are centralized under AVS:

- `avs/compiler/linx-llvm/tests/`

## Current checkpoint

- Host compiler binary commonly used:
  - pinned submodule build: `compiler/llvm/build-linxisa-clang/bin/clang`
  - or an external toolchain (set `CLANG=/path/to/clang`)
- Supported bring-up target on the current Bisheng branch: `linx64-linx-none-elf`
- The checked-in compiler currently registers `linx64` / `linx64be`; older `linx32` references are archived bring-up history, not an active required gate.
- Compile test suite entrypoint: `avs/compiler/linx-llvm/tests/run.sh`

## Required invariants

- Encodings and decode assumptions must match `isa/v0.58/linxisa-v0.58.json`.
- Block ISA control-flow invariants must hold.
- PTO-common direct calls must use the atomic fused
  `BSTART.CALL <br_label>, <rt_label>, ->ra` form.
- PTO-common indirect calls must use
  `BSTART.ICALL <rt_label>, ->ra`; the target comes from the retiring
  STD/FP block's `BARG.BPCN` and does not consume `SETC.TGT` or `SETRET`.
- Linx-only long bare-call forms preserve `ra`; an optional `SETRET` or
  `C.SETRET` pairing must immediately precede the bare call.

## Execution

```bash
# Using pinned submodule build
CLANG=$PWD/compiler/llvm/build-linxisa-clang/bin/clang ./avs/compiler/linx-llvm/tests/run.sh

# Or using an external toolchain
# CLANG=/path/to/clang ./avs/compiler/linx-llvm/tests/run.sh
```
