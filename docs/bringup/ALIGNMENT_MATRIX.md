# Alignment Matrix

This matrix separates the current v0.58.1 architecture authority from retained
v0.57 consumer-compatibility snapshots. Historical PASS counts do not transfer
to v0.58.1; LLVM, QEMU, Linux, and model rows require fresh evidence after their
respective hard-break upgrades.

| Topic | Spec | Compiler | Emulator | Kernel | Model | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Linx Linux libc ABI + relocation contract (`EM_LINXISA`, `R_LINX_*`, `setjmp/signal/ucontext`) | ✅ exact PTO ISA 0.58.1 ELF identity | ✅ Linx32/Linx64 call/ret relocation and template AVS pass | ✅ exact-identity loader matrix and strict AVS pass | ✅ fresh `vmlinux`; glibc five-variant smoke passes on the exact QEMU/Linux pins | ✅ release-strict result-memory consumers share one exact manifest | component lock; Linux provenance; glibc smoke summary; model release report |
| Block/descriptor contracts (`B.ARG/B.IOR/B.IOT/C.B.DIMI`) | ✅ manual + generated refs | ✅ descriptor emission/tests | ✅ descriptor execution + AVS gates | ✅ userspace boot not regressed | ✅ trace-compatible bring-up subset | `bash tools/regression/run.sh` |
| ACR/IRQ/exception correctness | ✅ privileged chapter + trap table | ✅ MC symbols + encodings | ✅ strict system tests | ✅ smoke/full/virtio boots pass | ✅ qemu-vs-pyc commit diff pass | `avs/qemu/check_system_strict.sh` |
| ISA catalog parity (`v0.58.1`) | ✅ golden catalog + exact PTO 0.58.1 lock | ✅ exact upgraded LLVM gitlink | ✅ exact upgraded QEMU gitlink | ✅ exact upgraded Linux gitlink | ✅ canonical model codec and provenance gates | `python3 tools/isa/check_canonical_v058.py --root .`; `python3 tools/isa/check_pto_v058_manifest.py --root .` |
| ISA breadth tracking (`v0.58.1`) | `731` legal mnemonics, `765` legal forms | exact v0.58.1 leaf checks merged | L1 `731/731` mnemonics and `765/765` forms; L2/L3 require independent runtime evidence | exact upgraded gitlink | not measured by L1 report | `docs/bringup/gates/qemu_isa_coverage_latest.json` |
| AVS QEMU translation coverage (`v0.58.1`) | current catalog | ✅ current-form assembly and 767/767 decode audit | ✅ full strict/runtime AVS; per-source translation aggregate remains separate | n/a | n/a | LLVM AVS logs and QEMU Task-4 evidence; do not reuse archived v0.57 reports |
| ISA-LLVM-QEMU coverage coherence (`v0.58.1`) | current catalog | ✅ fresh current-pin compiler breadth report | ✅ exact L1 decoder inventory | n/a | ✅ seven-case result-memory closure | `docs/bringup/gates/llvm_c_codegen_coverage_latest.json`; `docs/bringup/gates/qemu_isa_coverage_latest.json`; model release report |
| AVS consolidation | ✅ matrix maintained in `avs/` | ✅ compile tests under `avs/compiler/linx-llvm/tests` | ✅ runtime tests under `avs/qemu` | ✅ n/a | ✅ n/a | `bash tools/ci/check_repo_layout.sh` |
