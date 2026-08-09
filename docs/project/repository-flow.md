# LinxISA Repository Flow (v0.58)

The workspace is specification-first and submodule-first.

## Workspace Bootstrap

```bash
git submodule sync -- compiler/llvm
git submodule update --init compiler/llvm
```

Pinned ecosystem repos:

- `compiler/llvm`
- `emulator/qemu`
- `kernel/linux`
- `rtl/LinxCore`
- `tools/pyCircuit`
- `lib/glibc`
- `lib/musl`
- `workloads/pto_kernels`

## Flow

1. ISA definition in `isa/v0.58/`
2. Compiled catalog in `isa/v0.58/linxisa-v0.58.json`
3. Generated decode assets in `isa/generated/codecs/`
4. Validation in AVS (`avs/`)
5. Cross-repo alignment through submodule pinning
6. Regression gating with `tools/regression/run.sh`

Initialize only the pinned leaf needed by the task. Never use an unpinned
remote update as a shortcut; merge the leaf first and update its gitlink in a
dedicated superproject pull request.
