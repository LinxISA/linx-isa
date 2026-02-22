# Linx libc Bring-up Status

Canonical libc sources:

- `lib/glibc`
- `lib/musl`

## Repositories and pins

- `lib/glibc` @ `3cb936060f896ef88f888682a3159a73db1fe411`
- `lib/musl` @ `b761931e63b6cd6fdbbc7269d07ccd9e4fec20b2`

## Current policy

- Bring-up deltas live in fork history (`LinxISA/glibc`, `LinxISA/musl`).
- This repository provides orchestration, runtime smoke, and status tracking.
- Release-strict gating uses canonical artifacts from `docs/bringup/gates/latest.json`.

## Current verified state (2026-02-22)

- glibc `G1a`: ✅ pass (`configure` + `csu/subdir_lib` + startup objects)
- glibc `G1b`: ⚠️ not tested in current session
- musl `M1`: ❌ FAIL - compiler-rt build failure (adddf3.c)
- musl `M2`: ❌ FAIL - compiler-rt build failure (adddf3.c)
- musl `M3`: ❌ FAIL - compiler-rt build failure (adddf3.c)
- musl runtime `R1`: ❌ FAIL - blocked by musl build failure
- musl runtime `R2`: ❌ FAIL - blocked by musl build failure

## Blocker: musl compiler-rt build failure

The current musl build fails with:
```
error: failed to compile compiler-rt source: /Users/zhoubot/linx-isa/compiler/llvm/compiler-rt/lib/builtins/adddf3.c
```

This blocks all musl runtime gates (M1, M2, M3, R1, R2).

## Evidence pointers

- Canonical gate artifact: `docs/bringup/gates/latest.json`
- Rendered gate table: `docs/bringup/GATE_STATUS.md`
- glibc logs:
  - `out/libc/glibc/logs/summary.txt`
  - `out/libc/glibc/logs/g1b-summary.txt`
- musl logs:
  - `out/libc/musl/logs/phase-b-runtime-builtins.log`

## Notes

- Release-strict sign-off does not allow blocked waivers for required libc gates.
- Runtime numeric/benchmark parity remains outside libc bring-up scope.
