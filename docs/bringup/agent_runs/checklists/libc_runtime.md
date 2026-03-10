# libc / Runtime Checklist

- [x] ID: LIBC-001 Build musl sysroots for required modes (phase-b and phase-c when requested).
  Command: `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh`
  Done means: the required musl install tree exists under `out/libc/musl/install/<mode>` and the summary reports `M1/M2/M3` pass.
  Status: ✅ PASS (2026-03-08) - `MODE=phase-b` musl build completes with `m1=pass`, `m2=pass`, and `m3=pass` (summary: `out/libc/musl/logs/phase-b-summary.txt`).

- [x] ID: LIBC-005 Build glibc baseline G1a artifacts in the pinned workspace.
  Command: `bash lib/glibc/tools/linx/build_linx64_glibc.sh`
  Done means: the standard Linx glibc build path completes and produces the expected build tree under `out/libc/glibc/build`.
  Status: ✅ PASS (2026-03-08) - the pinned glibc baseline build completes successfully before G1b verification, with artifacts under `out/libc/glibc/build`.

- [x] ID: LIBC-002 Build glibc G1b shared libc gate artifacts.
  Command: `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh`
  Done means: `out/libc/glibc/logs/g1b-summary.txt` reports pass or explicit waived block.
  Status: ✅ PASS (2026-03-08) - `g1b-summary.txt` reports `status: pass` and `classification: shared_libc_so_built`, with `out/libc/glibc/build/linkobj/libc.so` present.

- [x] ID: LIBC-003 Pass musl runtime smoke for static and shared modes.
  Command: `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both`
  Done means: summary json for static/shared reports `ok=true`.
  Status: ✅ PASS (2026-02-25) - phase-b combined runtime smoke passes in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/lib_musl_both.log`; summary: `avs/qemu/out/musl-smoke/summary.json`).

- [x] ID: LIBC-004 Keep runtime status evidence updated in bring-up gate artifacts.
  Done means: gate report rows include evidence links for musl/glibc runtime checks.
  Status: ✅ PASS (2026-02-25) - `docs/bringup/gates/latest.json` includes refreshed runtime evidence for run `2026-02-25-r2-pin-lanefix` (`Library::musl runtime static+shared`, `Library::glibc G1b shared libc.so`).
