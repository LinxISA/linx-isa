# Phase 1: Compiler Bring-up

Compiler implementation source of truth is the LLVM submodule:

- `compiler/llvm/`

In-repo compile validation assets are centralized under AVS:

- `avs/compiler/linx-llvm/tests/`

## Current checkpoint

- Host compiler binary commonly used:
  - pinned submodule build: `compiler/llvm/build-linxisa-clang/bin/clang`
  - or an external toolchain (set `CLANG=/path/to/clang`)
- Supported bring-up targets: `linx64-linx-none-elf`, `linx32-linx-none-elf`
- Compile test suite entrypoint: `avs/compiler/linx-llvm/tests/run.sh`

## Required invariants

- Encodings and decode assumptions must match `isa/v0.3/linxisa-v0.3.json`.
- Block ISA control-flow invariants must hold.
- Call header adjacency rule (`BSTART CALL` + `SETRET`) must hold.

## Execution

```bash
# Using pinned submodule build
CLANG=$PWD/compiler/llvm/build-linxisa-clang/bin/clang ./avs/compiler/linx-llvm/tests/run.sh

# Or using an external toolchain
# CLANG=/path/to/clang ./avs/compiler/linx-llvm/tests/run.sh
```
