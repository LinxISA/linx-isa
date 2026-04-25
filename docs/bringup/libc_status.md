# Linx libc Bring-up Status

Canonical libc sources:

- `lib/glibc`
- `lib/musl`

## Repositories and pins

- `lib/glibc` @ `69493c1b395a23546cab196947d6424003a9f5ed`
- `lib/musl` @ `5b90c23dde11df89f37cf004256dff738510b469`

## Current policy

- Bring-up deltas live in fork history (`LinxISA/glibc`, `LinxISA/musl`).
- This repository provides orchestration, runtime smoke, and status tracking.
- Release-strict gating uses canonical artifacts from `docs/bringup/gates/latest.json`.

## Current status (2026-04-18)

- glibc `G1a`: pass (`configure` + `csu/subdir_lib` + startup objects)
- glibc `G1b`: pass (`out/libc/glibc/logs/g1b-summary.txt`)
- glibc dynamic runtime on Linux/QEMU: pass (`avs/qemu/out/glibc-smoke/summary.json`)
- musl runtime `R1`: pass
- musl runtime `R2`: pass

## Evidence pointers

- Canonical gate artifact: `docs/bringup/gates/latest.json`
- Rendered gate table: `docs/bringup/GATE_STATUS.md`
- glibc build logs: `out/libc/glibc/logs/summary.txt`, `out/libc/glibc/logs/g1b-summary.txt`
- musl logs: `avs/qemu/out/musl-smoke/summary.json`
- glibc runtime gate: `avs/qemu/run_glibc_smoke.py`, `avs/qemu/out/glibc-smoke/summary.json`

## Notes

- Release-strict sign-off does not allow blocked waivers for required libc gates.
- Runtime numeric/benchmark parity remains outside libc bring-up scope.
- `avs/qemu/run_glibc_smoke.py` now acts as the full in-tree glibc hello-matrix gate, not a single-binary smoke. It rebuilds one wrapper initramfs per variant and runs `entry_main`, `shared`, `startup`, and `startup_norpath`.
- Current matrix result is `4/4` pass. The repaired `shared` variant is now rebuilt as a valid `crt1`-based executable instead of reusing the stale malformed artifact that had `e_entry=0` and no `_start`.
- The decisive loader-side change for the runtime lane is still the Linx NOMMU-compatible contiguous-image PT_LOAD path in glibc, which avoids exact-address file remaps that the current Linux NOMMU lane cannot honor.
