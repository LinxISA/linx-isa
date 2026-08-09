# LinxISA Agent Navigation Contract

> **Version**: v0.58
> **Canonical Map**: [docs/project/navigation.md](docs/project/navigation.md)

This document defines the navigation rules for AI agents and contributors working in the LinxISA superproject.

---

## Bring-up Workflow Entry Points

- Start every architecture lookup from `isa/v0.58/linxisa-v0.58.json`, then
  use `docs/architecture/v0.58-architecture-contract.md` for narrative context.
- The Tile execution engines are exactly `VEC`, `SFU`, `TLSU`, and `CUBE`.
  `VEC` is element-wise only; `SFU` owns complex operations. `TEPL` is the
  unchanged Mode/Function encoding carrier for VEC/SFU, not an engine.
- Historical profiles and archived documents are non-normative and MUST NOT be
  used to infer current encodings or semantics.
- Start benchmark/QEMU/Linux bring-up from `docs/bringup/BENCHMARK_QEMU_LINUX_FLOW.md`.
- Treat `docs/bringup/benchmark_qemu_linux_flow.json` as the machine-readable hard-break stage order.
- Use `tools/bringup/run_benchmark_linux_flow.py` for PR, Linux, and nightly benchmark profiles.
- Use `docs/bringup/agent_runs/manifest.yaml` for stage ownership and handoff routing.
- Put new benchmark artifacts under `workloads/generated/<run-id>/`; do not create ad-hoc `workloads/generated-*` sibling directories.
- Treat generated markdown status pages as views. When they disagree with JSON reports or fresh runner output, the machine-readable report wins.

---

## Allowed Top-Level Directories

```
avs/         # Architecture Validation Suite
compiler/    # LLVM + PTOAS submodules
emulator/    # QEMU submodule
kernel/      # Linux kernel submodule
rtl/         # LinxCore RTL submodule
tools/       # Build scripts, generators, regression
workloads/   # Benchmarks and kernels
isa/         # ISA specification sources
docs/        # Architecture and bring-up documentation
lib/         # Standard libraries (glibc, musl)
```

---

## Canonical Destinations

| Task | Path |
|------|------|
| Runtime AVS tests | `avs/qemu/` |
| Compile AVS tests | `avs/compiler/linx-llvm/tests/` |
| Freestanding libc | `avs/runtime/freestanding/` |
| pyCircuit model | `tools/pyCircuit/` (submodule) |
| PTO kernels | `workloads/pto_kernels/` (submodule) |
| Assembly guidance | `docs/reference/linxisa-assembly-agent-guide.md` |

---

## Forbidden Paths

**Do not create, restore, or route new work to these paths:**

| Forbidden Path | Reason |
|---------------|--------|
| `compiler/linx-llvm` | Replaced by `compiler/llvm` submodule |
| `emulator/linx-qemu` | Replaced by `emulator/qemu` submodule |
| `examples/` | Replaced by `docs/reference/examples/` |
| `models/` | Replaced by `tools/pyCircuit/` |
| `toolchain/` | Replaced by `compiler/llvm` and `compiler/ptoas` |
| `tests/` | Replaced by `avs/` |
| `docs/validation/avs/` | Deprecated |
| `tools/ctuning/` | Deprecated |
| `tools/libc/` | Deprecated |
| `tools/glibc/` | Deprecated |
| `workloads/benchmarks/` | Replaced by workload-specific directories |
| `workloads/examples/` | Deprecated |
| `spec/` | Replaced by `workloads/spec2017/` (gitignored) |

---

## Submodule Workflow

```bash
# Initialize only the pinned leaf required by the current task.
git submodule sync -- compiler/llvm
git submodule update --init compiler/llvm

# Verify repository layout
bash tools/ci/check_repo_layout.sh
```

Never use an unpinned remote update as an agent shortcut. Merge and verify the
leaf repository first, then update its gitlink in a dedicated superproject PR.

---

## Rule: No Random Folders

Do not introduce new top-level directories. Place all new files in the canonical domains listed above.

---

## Enforcement

The repository layout is validated by:

```bash
bash tools/ci/check_repo_layout.sh
```

This CI check prevents non-compliant paths from being committed.
