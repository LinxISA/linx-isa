# LinxISA Path Migration Map v0.4.0

This map documents the AVS-centric and submodule-first repository tidy.

## Path Changes

| Previous Canonical Path | New Canonical Path | Notes |
|---|---|---|
| `compiler/linx-llvm/` | `avs/compiler/linx-llvm/` | compile-only AVS assets moved under AVS |
| `tests/qemu/` | `avs/qemu/` | runtime AVS suites consolidated |
| `tests/scratch/` | `avs/scratch/` | scratch tests consolidated |
| `models/pyCircuit` | `tools/pyCircuit` | submodule moved to tools domain |
| `docs/validation/avs/` | `avs/` | AVS docs now top-level canonical folder |
| `toolchain/libc/` | `avs/runtime/freestanding/` | freestanding support moved under AVS runtime |
| `toolchain/pto/include/pto/` | `workloads/pto_kernels/include/` | PTO headers now come from PTO-Kernel submodule |
| `toolchain/llvm/sync_generated_opcodes.sh` | `tools/isa/sync_generated_opcodes.sh` | LLVM sync helper moved |
| `examples/assembly/v0.3/` | `docs/reference/examples/v0.3/` | sample pack consolidated into docs |
| `tools/ctuning/` | `workloads/ctuning/` | benchmark runner moved under workloads |

## Submodule Changes

| Path | URL |
|---|---|
| `compiler/llvm` | `https://github.com/LinxISA/llvm-project.git` |
| `emulator/qemu` | `https://github.com/LinxISA/qemu.git` |
| `kernel/linux` | `https://github.com/LinxISA/linux.git` |
| `rtl/LinxCore` | `https://github.com/LinxISA/LinxCore.git` |
| `tools/pyCircuit` | `https://github.com/LinxISA/pyCircuit.git` |
| `lib/glibc` | `https://github.com/LinxISA/glibc.git` |
| `lib/musl` | `https://github.com/LinxISA/musl.git` |
| `workloads/pto_kernels` | `https://github.com/LinxISA/PTO-Kernel.git` |

## Removed Paths

- `emulator/linx-qemu`
- `examples/`
- `models/`
- `toolchain/`
- `tests/`
- `docs/validation/avs/`
- `tools/ctuning/`
