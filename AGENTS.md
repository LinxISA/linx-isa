# LinxISA Agent Navigation Contract

> **Version**: v0.5  
> **Canonical Map**: [docs/project/navigation.md](docs/project/navigation.md)

This document defines the navigation rules for AI agents and contributors working in the LinxISA superproject.

---

## Bring-up Workflow Entry Points

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
| Assembly examples | `docs/reference/examples/v0.57/` |

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

## Submodule Bump Workflow

```bash
# Sync all submodules
git submodule sync --recursive

# Initialize all submodules
git submodule update --init --recursive

# Pull latest from upstream remotes
git submodule update --remote \
    compiler/llvm \
    compiler/ptoas \
    emulator/qemu \
    kernel/linux \
    rtl/LinxCore \
    tools/pyCircuit \
    lib/glibc \
    lib/musl \
    workloads/pto_kernels

# Verify repository layout
bash tools/ci/check_repo_layout.sh
```

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
