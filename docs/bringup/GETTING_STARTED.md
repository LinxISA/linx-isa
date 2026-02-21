# LinxISA Bring-up Getting Started

This guide is the entry point for contributors joining the LinxISA bring-up workspace.

## 1. Prerequisites

### Platform notes

- **Linux**: supported (recommended).
- **macOS**: supported for most compiler/emulator/tooling work.
- **Windows**:
  - supported **via WSL2** (recommended),
  - native Windows can be used for editing + some tooling, but most gates expect a POSIX shell.

### Required

- `git`
- `python3`
- A POSIX shell to run `*.sh` gates (Linux/macOS, or Windows+WSL2)
- `clang` + `ld.lld` for Linx cross builds (either from the pinned LLVM submodule build, or an external toolchain)

### Recommended

- `gh` (GitHub CLI)

## 2. Clone with Submodules

```bash
git clone --recurse-submodules git@github.com:LinxISA/linx-isa.git
cd linx-isa
git submodule sync --recursive
git submodule update --init --recursive
```

Submodule map:

- `compiler/llvm` -> `LinxISA/llvm-project`
- `emulator/qemu` -> `LinxISA/qemu`
- `kernel/linux` -> `LinxISA/linux`
- `rtl/LinxCore` -> `LinxISA/LinxCore`
- `tools/pyCircuit` -> `LinxISA/pyCircuit`
- `lib/glibc` -> `LinxISA/glibc`
- `lib/musl` -> `LinxISA/musl`
- `workloads/pto_kernels` -> `LinxISA/PTO-Kernel`

## 3. Validate Baseline

From repo root:

```bash
bash tools/regression/run.sh
```

Optional overrides:

```bash
# Tool paths can come from:
# - pinned submodules (recommended for reproducibility)
# - external installs (recommended for day-to-day dev if you already have them)
#
# If you built the pinned submodules:
export CLANG=$PWD/compiler/llvm/build-linxisa-clang/bin/clang
export LLD=$PWD/compiler/llvm/build-linxisa-clang/bin/ld.lld
export QEMU=$PWD/emulator/qemu/build/qemu-system-linx64

# Or point to external toolchains:
# export CLANG=/path/to/clang
# export LLD=/path/to/ld.lld
# export QEMU=/path/to/qemu-system-linx64

bash tools/regression/run.sh
```

Run contract gate:

```bash
python3 tools/bringup/check26_contract.py --root .
```

## 4. Daily Workflow

1. Pick a scope under `docs/bringup/phases/`.
2. Implement in the relevant submodule/repo first.
3. Run AVS + regression gates locally.
4. Merge upstream in ecosystem repos.
5. Bump submodule SHAs in `linx-isa`.

Submodule bump command:

```bash
git submodule update --remote compiler/llvm emulator/qemu kernel/linux rtl/LinxCore tools/pyCircuit lib/glibc lib/musl workloads/pto_kernels
git add .gitmodules compiler/llvm emulator/qemu kernel/linux rtl/LinxCore tools/pyCircuit lib/glibc lib/musl workloads/pto_kernels
git commit -m "chore(submodules): bump ecosystem revisions"
```

## 5. Canonical Paths

- AVS runtime tests: `avs/qemu/`
- AVS compile tests: `avs/compiler/linx-llvm/tests/`
- Freestanding libc support used by AVS: `avs/runtime/freestanding/`
- Linux libc source forks: `lib/glibc/`, `lib/musl/`
- PTO kernel headers: `workloads/pto_kernels/include/`
- Assembly sample pack: `docs/reference/examples/v0.3/`

## 6. Coordination References

- Bring-up progress: `docs/bringup/PROGRESS.md`
- Contract checkpoint: `docs/bringup/CHECK26_CONTRACT.md`
- Migration map: `docs/migration/path-map-v0.4.0.md`
- Navigation guide: `docs/project/navigation.md`
