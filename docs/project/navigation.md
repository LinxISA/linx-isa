# LinxISA Navigation Guide (v0.58)

This is the canonical navigation contract for contributors and agents.

## Top-level map

- `README.md` — workspace overview
- `AGENTS.md` — agent-facing routing and guardrails
- `avs/` — architectural verification suite
- `compiler/` — compiler-side submodules (`compiler/llvm`, `compiler/ptoas`)
- `emulator/` — upstream QEMU submodule (`emulator/qemu`)
- `kernel/` — upstream Linux submodule (`kernel/linux`)
- `rtl/` — LinxCore submodule (`rtl/LinxCore`) + rtl notes
- `tools/` — generators, regression, models, and the Linx TileOP API submodule
- `workloads/` — benchmark runners + generated artifacts + PTO kernels submodule
- `isa/` — ISA source of truth and generated catalogs
- `docs/` — architecture, bring-up, migration, project references
- `lib/` — glibc/musl fork submodules

## Canonical test locations

- Runtime AVS suites: `avs/qemu/`
- Compile AVS suites: `avs/compiler/linx-llvm/tests/`
- AVS matrix/docs: `avs/`

## Canonical ISA contract

- Machine-readable authority: `isa/v0.58/linxisa-v0.58.json`
- Stable architecture overview: `docs/architecture/v0.58-architecture-contract.md`
- Generated instruction reference: `docs/isa/`
- Historical profiles and archived narrative are non-normative and are not
  valid agent-routing targets.

## Canonical toolchain support locations

- Freestanding libc support used by AVS/tests: `avs/runtime/freestanding/`
- Linux libc source forks: `lib/glibc/`, `lib/musl/`
- PTO assembler fork: `compiler/ptoas/`
- PTO kernels and maintained SuperNPU workloads (submodule): `workloads/pto_kernels/`
- SuperNPU active root: `workloads/pto_kernels/benchmarks/supernpu/`
- Linx v0.58 TileOP API include root: `tools/Linx-TileOP-API/include/`
- LLVM opcode sync helper: `tools/isa/sync_generated_opcodes.sh`

## Benchmark locations

- CoreMark upstream: `workloads/coremark/upstream/`
- Dhrystone upstream: `workloads/dhrystone/upstream/`
- AI workload hard-break flow: `tools/bringup/run_ai_workload_flow.py`
- AI workload flow contract: `docs/bringup/ai_workload_bringup_flow.json`
- PolyBench source cache: `workloads/third_party/PolyBenchC/`
- ctuning runner: `workloads/ctuning/`

## Removed / forbidden paths

Do not add or revive these paths:

- `compiler/linx-llvm`
- `emulator/linx-qemu`
- `examples/`
- `models/`
- `toolchain/`
- `tests/`
- `docs/validation/avs/`
- `tools/ctuning/`
- `tools/libc/`
- `tools/glibc/`
- `workloads/benchmarks/`
- `workloads/examples/`
- `workloads/SuperNPUBench/`
- `spec/`

CI guard: `tools/ci/check_repo_layout.sh`

## Submodule policy

When implementation repos change:

1. Merge in the upstream ecosystem repo first.
2. Update submodule SHA in this workspace.
3. Keep `.gitmodules` URLs aligned to the owning organization and
   `docs/bringup/component-lock.v0.58.json`.
4. Validate with:

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```
