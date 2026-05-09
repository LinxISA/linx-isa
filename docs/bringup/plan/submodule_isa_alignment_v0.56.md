# v0.56 ISA Submodule Alignment Plan

This plan tracks the submodule upgrades needed to align the implementation
stack with the canonical v0.56 ISA manual and generated encoding catalog.

## Scope

- Canonical ISA sources: `isa/v0.56/` and
  `docs/architecture/isa-manual/src/`.
- Superproject pin lane: committed submodule SHAs recorded by this repository.
- External lane: active upstream branches in the LinxISA-owned submodules.
- Closure gate: `LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 bash tools/regression/strict_cross_repo.sh`.

## Alignment Matrix

| Submodule | Upgrade target | Required v0.56 work | Gate evidence |
| --- | --- | --- | --- |
| `compiler/llvm` | Pin a committed LLVM backend update after the v0.56 opcode and register catalog is imported. | Refresh TableGen/assembler/disassembler encodings, block-boundary legality, vector memory forms, and call/return lowering against the generated catalog. | Compile AVS tests under `avs/compiler/linx-llvm/tests/` plus strict cross-repo compile lane. |
| `emulator/qemu` | Land and pin the QEMU v0.56 decode/runtime update. | Regenerate opcode metadata, align CPU state/register definitions, implement v0.56 vector and memory encoding changes, and preserve breakpoint/semihost split. | Runtime AVS under `avs/qemu/`, QEMU decode smoke tests, and strict cross-repo runtime lane. |
| `kernel/linux` | Land and pin Linux ABI/runtime updates after QEMU can boot the new contract. | Update LinxISA ABI notes, process/thread context handling, scheduler/preempt diagnostics, and rootfs scripts for v0.56 runtime assumptions. | Busybox/rootfs boot smoke, ctx-tu/ctx-tq diagnostics, and strict cross-repo runtime lane. |
| `rtl/LinxCore` | Pin the committed LinxCore opcode-catalog refresh once its local ISA-alignment edits are landed. | Align opcode catalog, decode metadata, block-fabric contracts, ROB/bookkeeping, trace schema, and cosim lockstep behavior to v0.56. | LinxCore unit tests, generated RTL safety gates, cosim lockstep smoke, and LinxTrace lint. |
| `tools/model` | Pin the committed model fixture branch after local ISA execution updates are landed. | Refresh `minst` codec generation, execution state, ELF/program loading, host syscall behavior, and JSON trace formatting for the v0.56 catalog. | Model unit/system tests plus AVS runtime smoke through `tests/checks/check_avs_runtime_smoke.py`. |
| `tools/pyCircuit` | Pin the pyCircuit PTO/manual source update after upstreaming the active branch. | Keep pyCircuit flows and PTO manual generation consistent with v0.56 block, tile, and encoding terminology. | pyCircuit C++ backend smoke, QEMU-vs-pyC comparison flow, and PTO manual generation checks. |
| `lib/glibc` | Keep current pin unless ABI changes require a libc refresh. | Validate loader/shared-lib behavior after compiler, QEMU, and kernel converge. | glibc loader smoke and strict cross-repo libc lane. |
| `lib/musl` | Keep current pin until the local toolchain script change is landed in musl. | Confirm in-repo toolchain defaults and startup assumptions against v0.56 ABI changes. | musl static hello/runtime smoke and strict cross-repo libc lane. |
| `workloads/pto_kernels` | Keep current pin until kernel catalog cleanup is committed and reviewed. | Rename legacy typed examples to v0.56-neutral kernels, update tile asm contracts, and refresh status-site manifests. | PTO kernel manifest check, tile asm contract check, and benchmark status-site build. |
| `skills/linx-skills` | Pin the latest canonical skill update for v0.56 manual navigation. | Keep bring-up agents on the v0.56 manual, encoding catalog, and submodule closure workflow. | `check_skill_change_scope.py` plus install/prune dry run when changing skills. |

## Execution Order

1. Land the superproject ISA/manual refresh and plan update as the active
   contract surface.
2. For each implementation submodule, commit and PR the local v0.56 work in the
   owning repository before repinning the superproject.
3. Repin only submodule SHAs that are pushed to their canonical upstream remote.
4. Run the PR-tier strict closure gate on the pin lane.
5. Run the same gate on the external lane before marking the repin ready for
   merge.
6. Squash-merge the superproject PR only after required checks and gate evidence
   are green.

## Current Risks

- Several implementation submodules currently contain uncommitted local edits;
  those edits cannot be represented by a superproject SHA until they are landed
  in their owning repositories.
- `compiler/llvm` reports an uninitialized local branch state in this checkout,
  so LLVM must be normalized before it can participate in closure gates.
- Full strict closure may fail until QEMU, model, LinxCore, and workloads all
  consume the regenerated v0.56 encoding catalog.
