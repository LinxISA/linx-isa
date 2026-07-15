# Alignment Matrix

This matrix tracks cross-domain alignment at the current workspace scope.

| Topic | Spec | Compiler | Emulator | Kernel | Model | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Linx Linux libc ABI + relocation contract (`EM_LINXISA`, `R_LINX_*`, `setjmp/signal/ucontext`) | ✅ ABI guide/checklist + musl/glibc header sync | ✅ Linx32/Linx64 call/ret relocation and template AVS pass | ✅ bare-metal QEMU AVS passes on the clean pin | ❌ fresh BusyBox rootfs boot has no UART output in two 120-second attempts | ⚠ leaf checks pass; full current-pin cross-model suite not run | v0.56.5 maintenance packet and generated BusyBox report |
| Block/descriptor contracts (`B.ARG/B.IOR/B.IOT/C.B.DIMI`) | ✅ manual + generated refs | ✅ descriptor emission/tests | ✅ descriptor execution + AVS gates | ✅ userspace boot not regressed | ✅ trace-compatible bring-up subset | `bash tools/regression/run.sh` |
| ACR/IRQ/exception correctness | ✅ privileged chapter + trap table | ✅ MC symbols + encodings | ✅ strict system tests | ✅ smoke/full/virtio boots pass | ✅ qemu-vs-pyc commit diff pass | `avs/qemu/check_system_strict.sh` |
| ISA catalog parity (`v0.56`) | ✅ golden + current json | ✅ compile coverage tests | ✅ decode/execute gates | ✅ no stale active-surface refs | ✅ model-side contract checks | `python3 tools/isa/check_canonical_v056.py --root .` |
| ISA breadth tracking (spec vs QEMU implementation) | ✅ canonical spec catalog (`711` unique mnemonics, `747` forms) | ✅ compile/disasm coverage is `711/711` | ⚠ mapped QEMU coverage is `618/711` mnemonics and `621/747` forms | ❌ BusyBox/MMU closure is independently red | ⚠ implemented subsets only | `docs/bringup/gates/qemu_isa_coverage_latest.json`; `docs/bringup/gates/qemu_isa_coverage_latest.md` |
| AVS QEMU translation coverage | ✅ canonical spec catalog is the target set | ✅ per-source objects emitted by AVS compile flow | ✅ compile-only translation corpus covers `711/711` | n/a | n/a | `docs/bringup/gates/qemu_translation_coverage_latest.json`; `docs/bringup/gates/qemu_translation_coverage_latest.md` |
| ISA-LLVM-QEMU coverage coherence | ✅ canonical spec catalog is the common target set | ✅ LLVM baremetal coverage reaches `711/711` | ❌ semantic implementation remains `618/711`; translation coverage is `711/711` | n/a | n/a | `docs/bringup/gates/isa_llvm_qemu_coverage_latest.json`; `docs/bringup/gates/isa_llvm_qemu_coverage_latest.md` |
| AVS consolidation | ✅ matrix maintained in `avs/` | ✅ compile tests under `avs/compiler/linx-llvm/tests` | ✅ runtime tests under `avs/qemu` | ✅ n/a | ✅ n/a | `bash tools/ci/check_repo_layout.sh` |
