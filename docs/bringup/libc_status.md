# Linx libc Bring-up Status

Canonical libc sources:

- `lib/glibc`
- `lib/musl`

## Repositories and pins

- `lib/glibc` @ `6dd1cee38fef1e9cf2caf71554cb68975e7e9f90`
- `lib/musl` @ `a16cd1b589382141452dbf5408448a51e9b90273`

## Release policy

- Bring-up deltas live in the `LinxISA/glibc` and `LinxISA/musl` fork
  histories.
- The superproject owns orchestration, full-system runtime smoke, and
  release-status reporting.
- Required libc gates cannot use blocked waivers in the release-strict
  profile.
- The canonical result is the matching `external` and `pin` lane pair in
  `docs/bringup/gates/latest.json`.

## v0.57 status (2026-07-18)

- glibc `G1a`: pass (`configure`, `csu/subdir_lib`, and startup objects).
- glibc `G1b`: pass (`libc.so` shared-library closure).
- glibc full-system dynamic hello: pass under the clean v0.57 QEMU and Linux
  pins.
- musl `M1`: pass with the Linx64 ABI headers.
- musl `M2`: pass in `phase-b`.
- musl `M3`: pass in the current `phase-b` build/runtime lane.
- musl runtime `R2`: pass for all static and shared smoke samples.

The release-strict run `2026-07-18-v057-release` proves the same libc results
in both the external-tool and pinned-tool lanes with zero waivers.

## Evidence

- Canonical gate artifact: `docs/bringup/gates/latest.json`
- Rendered gate table: `docs/bringup/GATE_STATUS.md`
- glibc build logs:
  `out/libc/glibc/logs/summary.txt`,
  `out/libc/glibc/logs/g1b-summary.txt`
- glibc runtime summary: `avs/qemu/out/glibc-smoke/summary.json`
- musl build summary: `out/libc/musl/logs/phase-b-summary.txt`
- musl runtime summaries:
  `avs/qemu/out/musl-smoke/summary.json`,
  `avs/qemu/out/musl-smoke/summary_static.json`,
  `avs/qemu/out/musl-smoke/summary_shared.json`
- Per-lane release logs:
  `docs/bringup/gates/logs/2026-07-18-v057-release/external/`,
  `docs/bringup/gates/logs/2026-07-18-v057-release/pin/`
