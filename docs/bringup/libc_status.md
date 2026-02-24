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

## Release-strict baseline (2026-02-17)

- glibc `G1a`: ✅ pass (`configure` + `csu/subdir_lib` + startup objects)
- glibc `G1b`: pass
- musl runtime `R2`: pass

## Evidence pointers

- Canonical gate artifact: `docs/bringup/gates/latest.json`
- Rendered gate table: `docs/bringup/GATE_STATUS.md`
- glibc logs: `docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/lib_glibc_g1b.log`
- musl logs: `docs/bringup/gates/logs/2026-02-17-r1-external-phase4b/external/lib_musl_both.log`

## Notes

- Release-strict sign-off does not allow blocked waivers for required libc gates.
- Runtime numeric/benchmark parity remains outside libc bring-up scope.
