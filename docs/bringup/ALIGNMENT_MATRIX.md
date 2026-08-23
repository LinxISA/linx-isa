# Alignment Matrix

This matrix tracks the active v0.58.3 authority. Historical v0.57 and
v0.58.1 results do not transfer to this release.

| Topic | Spec | Compiler/API | Emulator | Kernel/libc | Model/workload | Current evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Exact PTO identity | ✅ v0.58.3 lock and ELF descriptor | ✅ LLVM/LLD; TileOP/PTOAS final pins pending | ✅ loader rejection matrix; final QEMU pin pending | ✅ Linux/glibc/musl exact identity | ✅ model/kernels leafs; root pins pending | PTO lock, leaf reviews, component lock after repin |
| ISA catalog parity | ✅ 723 mnemonics, 757 forms | ✅ LLVM 723/723 linx64 compile AVS | ✅ 723/757 decode mapping on current candidates | n/a | ✅ model authority leaf | canonical ISA and leaf reports |
| HL.LUI/HL.LIU/CSEL semantics | ✅ catalog, convention, Sail directed tests | ✅ LLVM encoding/materialization | ✅ reviewed QEMU fixes merged | ✅ clean final-LLVM vmlinux reaches userspace | n/a | Sail gate, QEMU PRs 70/72, Linux r6/r7 |
| TLSU virtual-memory access | ✅ CPU translation unless IOTCR enables I/O translation | ✅ TileOP pointer surface | ⏳ QEMU PR 74 | ✅ ACR2 Linux integration reaches past TLOAD | n/a | issue 73, PR 74, r7 |
| CUBE DATR and accumulator path | ✅ per-operation DATR contracts | ⏳ TileOP PR 27 emits compute Zero | ⏳ QEMU issue 75 after legal r8 preflight | ✅ PID1/fork/exec | ✅ six exact kernels compile/link | r8 summary and linked issues |
| VECTOR/CUBE first use | ✅ pre-effect retryable E_INST/EC_PERM | n/a | ✅ directed QEMU behavior | ⚠ V/C disabled pending cross-ACR EXTCTX ABI | n/a | root issue 182, Linux issue 32 |
| Full release-strict closure | ✅ policy defined | ⏳ final PTOAS/TileOP pins | ⏳ final QEMU and six-case system PASS | ⏳ final exact boot summary | ⏳ fresh final-lock model report | no promotion until every pending cell closes |
