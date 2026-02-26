# Alignment Matrix

This matrix tracks cross-domain alignment at the current workspace scope.

| Topic | Spec | Compiler | Emulator | Kernel | Model | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Linx Linux libc ABI + relocation contract (`EM_LINXISA`, `R_LINX_*`, `setjmp/signal/ucontext`) | ✅ ABI guide/checklist + musl/glibc header sync | ✅ workspace clang call/ret relocation+template gates pass (`FENTRY/FRET.STK` vs musttail `FENTRY/FEXIT`) | ✅ strict lane runtime gates pass (musl runtime + glibc G1b + strict system + model-diff) | ✅ smoke/full/busybox/virtio-disk boot gates pass | ✅ qemu-vs-pyc commit diff pass | `docs/bringup/gates/latest.json`; `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/lib_musl_both.log`; `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/lib_glibc_g1b.log`; `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/model_diff_suite.log` |
| Block/descriptor contracts (`B.ARG/B.IOR/B.IOT/C.B.DIMI`) | ✅ manual + generated refs | ✅ descriptor emission/tests | ✅ descriptor execution + AVS gates | ✅ userspace boot not regressed | ✅ trace-compatible bring-up subset | `bash tools/regression/run.sh` |
| ACR/IRQ/exception correctness | ✅ privileged chapter + trap table | ✅ MC symbols + encodings | ✅ strict system tests | ✅ smoke/full/virtio boots pass | ✅ qemu-vs-pyc commit diff pass | `avs/qemu/check_system_strict.sh` |
| ISA catalog parity (`v0.3`) | ✅ golden + current json | ✅ compile coverage tests | ✅ decode/execute gates | ✅ no legacy refs in runtime scripts | ✅ model-side contract checks | `python3 tools/isa/check_no_legacy_v03.py --root .` |
| ISA breadth tracking (spec vs QEMU implementation) | ✅ canonical spec catalog (`710` unique mnemonics) | ✅ compile/disasm coverage remains 100% for implemented toolchain surface | ⚠ mapped QEMU coverage is `311/710` (gap tracked as artifact, not waived) | ✅ kernel runtime closure remains green while breadth expands incrementally | ✅ model suite remains required and passing for implemented subsets | `docs/bringup/gates/qemu_isa_coverage_latest.json`; `docs/bringup/gates/qemu_isa_coverage_latest.md` |
| AVS consolidation | ✅ matrix maintained in `avs/` | ✅ compile tests under `avs/compiler/linx-llvm/tests` | ✅ runtime tests under `avs/qemu` | ✅ n/a | ✅ n/a | `bash tools/ci/check_repo_layout.sh` |
