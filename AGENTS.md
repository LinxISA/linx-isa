# LinxISA Agent Navigation Contract

> **Version**: v0.5  
> **Canonical Map**: [docs/project/navigation.md](docs/project/navigation.md)

This document defines the navigation rules for AI agents and contributors working in the LinxISA superproject.

---

## Allowed Top-Level Directories

```
avs/         # Architecture Validation Suite
compiler/    # LLVM submodule
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
| Assembly examples | `docs/reference/examples/v0.3/` |

---

## Forbidden Paths

**Do not create, restore, or route new work to these paths:**

| Forbidden Path | Reason |
|---------------|--------|
| `compiler/linx-llvm` | Replaced by `compiler/llvm` submodule |
| `emulator/linx-qemu` | Replaced by `emulator/qemu` submodule |
| `examples/` | Replaced by `docs/reference/examples/` |
| `models/` | Replaced by `tools/pyCircuit/` |
| `toolchain/` | Replaced by `compiler/llvm` |
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
