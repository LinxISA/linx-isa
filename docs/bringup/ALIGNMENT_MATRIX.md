# Alignment Matrix

This matrix separates the current v0.58 architecture authority from retained
v0.57 consumer-compatibility snapshots. Historical PASS counts do not transfer
to v0.58; LLVM, QEMU, Linux, and model rows require fresh evidence after their
respective hard-break upgrades.

| Topic | Spec | Compiler | Emulator | Kernel | Model | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Linx Linux libc ABI + relocation contract (`EM_LINXISA`, `R_LINX_*`, `setjmp/signal/ucontext`) | ✅ ABI guide/checklist + musl/glibc header sync | ✅ Linx32/Linx64 call/ret relocation and template AVS pass | ✅ bare-metal QEMU AVS passes on the clean pin | ❌ fresh BusyBox rootfs boot has no UART output in two 120-second attempts | ⚠ leaf checks pass; full current-pin cross-model suite not run | v0.57 maintenance packet and generated BusyBox report |
| Block/descriptor contracts (`B.ARG/B.IOR/B.IOT/C.B.DIMI`) | ✅ manual + generated refs | ✅ descriptor emission/tests | ✅ descriptor execution + AVS gates | ✅ userspace boot not regressed | ✅ trace-compatible bring-up subset | `bash tools/regression/run.sh` |
| ACR/IRQ/exception correctness | ✅ privileged chapter + trap table | ✅ MC symbols + encodings | ✅ strict system tests | ✅ smoke/full/virtio boots pass | ✅ qemu-vs-pyc commit diff pass | `avs/qemu/check_system_strict.sh` |
| ISA catalog parity (`v0.58`) | ✅ golden catalog + exact PTO 0.58 lock | ⚠ fresh v0.58 upgrade pending | ⚠ fresh v0.58 upgrade pending | ⚠ fresh v0.58 upgrade pending | ⚠ fresh v0.58 upgrade pending | `python3 tools/isa/check_canonical_v058.py --root .`; `python3 tools/isa/check_pto_v058_manifest.py --root .` |
| ISA breadth tracking (v0.57 compatibility snapshot) | historical v0.57 target only | historical `710/710` observation only | historical L1 `624/710` mnemonics and `655/746` forms; L2/L3 `60/60` | historical pinned-lane evidence only | historical implemented subsets only | `docs/bringup/gates/qemu_isa_coverage_latest.json`; regenerate against v0.58 before making a current claim |
| AVS QEMU translation coverage (v0.57 compatibility snapshot) | historical v0.57 target only | historical per-source objects | historical `711/711` translation inventory | n/a | n/a | `docs/bringup/gates/qemu_translation_coverage_latest.json`; not v0.58 evidence |
| ISA-LLVM-QEMU coverage coherence (v0.57 compatibility snapshot) | historical v0.57 target only | historical `710/710` observation | historical L1 `624/710`; translation `710/710` | n/a | n/a | `docs/bringup/gates/isa_llvm_qemu_coverage_latest.json`; not v0.58 evidence |
| AVS consolidation | ✅ matrix maintained in `avs/` | ✅ compile tests under `avs/compiler/linx-llvm/tests` | ✅ runtime tests under `avs/qemu` | ✅ n/a | ✅ n/a | `bash tools/ci/check_repo_layout.sh` |
