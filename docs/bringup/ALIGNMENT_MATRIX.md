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
| ISA catalog parity (`v0.58`) | ✅ golden catalog + exact PTO 0.58 lock | ✅ exact upgraded LLVM gitlink | ✅ exact upgraded QEMU gitlink | ✅ exact upgraded Linux gitlink | ⚠ model consumer upgrade remains separate | `python3 tools/isa/check_canonical_v058.py --root .`; `python3 tools/isa/check_pto_v058_manifest.py --root .` |
| ISA breadth tracking (`v0.58`) | `728` legal mnemonics, `766` legal forms | exact v0.58 leaf checks merged | L1 `728/728` mnemonics and `759/766` forms; L2/L3 unavailable | exact upgraded gitlink | not measured by L1 report | `docs/bringup/gates/qemu_isa_coverage_latest.json` |
| AVS QEMU translation coverage (`v0.58`) | current catalog | fresh per-source objects required | open; v0.57 object report archived | n/a | n/a | regenerate before making a current translation claim |
| ISA-LLVM-QEMU coverage coherence (`v0.58`) | current catalog | fresh current-pin compiler artifacts required | fresh current-pin translation artifacts required | n/a | n/a | no active aggregate report until both inputs are regenerated |
| AVS consolidation | ✅ matrix maintained in `avs/` | ✅ compile tests under `avs/compiler/linx-llvm/tests` | ✅ runtime tests under `avs/qemu` | ✅ n/a | ✅ n/a | `bash tools/ci/check_repo_layout.sh` |
