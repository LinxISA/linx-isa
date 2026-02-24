# libc / Runtime Checklist

- [x] ID: LIBC-001 Build musl sysroots for required modes (phase-b and phase-c when requested).
  Command: `MODE=phase-c lib/musl/tools/linx/build_linx64_musl.sh`
  Done means: install trees exist under `out/libc/musl/install/<mode>`.
  Status: ✅ PASS (2026-02-23) - `MODE=phase-c` musl build completes (`M1/M2/M3` pass) in this run (log: `docs/bringup/gates/logs/2026-02-23-r2-pin-reassess/pin/lib_musl_phasec.log`).

- [ ] ID: LIBC-002 Build glibc G1b shared libc gate artifacts.
  Command: `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh`
  Done means: `out/libc/glibc/logs/g1b-summary.txt` reports pass or explicit waived block.
  Status: ❌ FAIL (2026-02-23) - `g1b-summary.txt` remains `status: blocked` (`classification: build_failed`) in run `2026-02-23-r4-pin-qemu-linux-ctxfix` (log: `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/lib_glibc_g1b.log`; base log: `out/libc/glibc/logs/03-make.log`).

- [ ] ID: LIBC-003 Pass musl runtime smoke for static and shared modes.
  Command: `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both`
  Done means: summary json for static/shared reports `ok=true`.
  Status: ❌ FAIL (2026-02-23) - combined phase-b musl smoke fails in run `2026-02-23-r4-pin-qemu-linux-ctxfix`: `shared` passes but `static` fails with runtime kernel panic signature (summary: `avs/qemu/out/musl-smoke/summary.json`; log: `docs/bringup/gates/logs/2026-02-23-r4-pin-qemu-linux-ctxfix/pin/lib_musl_both.log`).

- [x] ID: LIBC-004 Keep runtime status evidence updated in bring-up gate artifacts.
  Done means: gate report rows include evidence links for musl/glibc runtime checks.
  Status: ✅ PASS (2026-02-23) - `docs/bringup/gates/latest.json` includes refreshed `Library::musl runtime static+shared` and `Library::glibc G1b shared libc.so` rows with evidence for run `2026-02-23-r4-pin-qemu-linux-ctxfix`.
