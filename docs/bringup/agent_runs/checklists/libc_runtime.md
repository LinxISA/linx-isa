# libc / Runtime Checklist

- [ ] ID: LIBC-001 Build musl sysroots for required modes (phase-b and phase-c when requested).
  Command: `MODE=phase-c lib/musl/tools/linx/build_linx64_musl.sh`
  Done means: install trees exist under `out/libc/musl/install/<mode>`.
  Status: ❌ FAIL (2026-02-22) - compiler-rt build failure: adddf3.c failed to compile

- [ ] ID: LIBC-002 Build glibc G1b shared libc gate artifacts.
  Command: `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh`
  Done means: `out/libc/glibc/logs/g1b-summary.txt` reports pass or explicit waived block.
  Status: ⚠️ NOT TESTED

- [x] ID: LIBC-003 Pass musl runtime smoke for static and shared modes.
  Command: `python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both`
  Done means: summary json for static/shared reports `ok=true`.
  Status: ⚠️ BLOCKED by LIBC-001 (musl build failure)

- [ ] ID: LIBC-004 Keep runtime status evidence updated in bring-up gate artifacts.
  Done means: gate report rows include evidence links for musl/glibc runtime checks.
  Status: ⚠️ NOT TESTED
