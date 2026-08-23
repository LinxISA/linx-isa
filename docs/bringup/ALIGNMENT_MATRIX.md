# Alignment Matrix

This matrix tracks the active v0.58.3 authority. Historical v0.57 and
v0.58.1 results do not transfer to this release.

| Topic | Spec | Compiler/API | Emulator | Kernel/libc | Model/workload | Current evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Exact PTO identity | ✅ v0.58.3 lock and ELF descriptor | ✅ LLVM/LLD/TileOP/PTOAS | ✅ loader rejection matrix; QEMU `0d2f90de` | ✅ Linux/glibc/musl exact identity | ✅ model/kernels and root pins | PTO lock, leaf reviews, atomic component lock |
| ISA catalog parity | ✅ 723 mnemonics, 757 forms | ✅ LLVM 723/723 linx64 compile AVS | ✅ 723/757 decode mapping on current candidates | n/a | ✅ model authority leaf | canonical ISA and leaf reports |
| HL.LUI/HL.LIU/CSEL semantics | ✅ catalog, convention, Sail directed tests | ✅ LLVM encoding/materialization | ✅ reviewed QEMU fixes merged | ✅ clean final-LLVM vmlinux reaches userspace | n/a | Sail gate, QEMU PRs 70/72, Linux r6/r7 |
| TLSU virtual-memory access | ✅ CPU translation unless IOTCR enables I/O translation | ✅ TileOP pointer surface | ✅ QEMU PR 74 merged | ✅ mapped/faulting ACR2 integration | n/a | issue 73, PR 74, focused differential tests |
| CUBE DATR and accumulator path | ✅ per-operation DATR contracts | ✅ TileOP `bd1ecca9` emits compute Zero | ✅ accumulator/compute/publish plus TLSU | ✅ PID1/fork/exec/exit | ✅ six exact kernels pass cold boots | cold matrix SHA `3328caf9…` |
| VECTOR/CUBE first use | ✅ pre-effect retryable E_INST/EC_PERM | n/a | ✅ directed QEMU behavior | ⚠ V/C disabled pending cross-ACR EXTCTX ABI | n/a | root issue 182, Linux issue 32 |
| Full release-strict closure | ✅ policy defined | ✅ final merged pins | ✅ QEMU and six-case cold matrix | ✅ exact boot summaries | ✅ final-lock 7/7 model report | model report SHA `e7d927ba…`; proceed to final root review |
