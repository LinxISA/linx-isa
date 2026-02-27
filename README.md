<p align="center">
  <img src="docs/architecture/isa-manual/src/images/linxisa-logo.svg" alt="LinxISA logo" width="220" />
</p>

<h1 align="center">LinxISA: Block-Structured Instruction Set Architecture</h1>

<p align="center">
  <a href="https://github.com/LinxISA/linx-isa/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/LinxISA/linx-isa/ci.yml?branch=main" alt="CI Status"></a>
  <a href="https://github.com/LinxISA/linx-isa/releases"><img src="https://img.shields.io/github/v/release/LinxISA/linx-isa?include_prereleases" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/LinxISA/linx-isa" alt="License"></a>
</p>

---

## What is LinxISA?

**LinxISA** is a block-structured instruction set architecture (ISA) designed for high-performance computing. Unlike traditional scalar ISAs, LinxISA organizes instructions into **blocks** that execute as atomic units, enabling:

- **Explicit block boundaries** with mandatory control-flow integrity
- **Two-layer state model** (global + block-local state)
- **Vector/tile extensions** for SIMD-style parallelism
- **Template blocks** for function prologues/epilogues and accelerator operations

This repository serves as the **superproject** that pins together all ecosystem components: compiler (LLVM), emulator (QEMU), Linux kernel, RTL (LinxCore), and standard libraries (glibc, musl).

---

## Quick Start

### Clone with Submodules

```bash
git clone --recurse-submodules git@github.com:LinxISA/linx-isa.git
cd linx-isa
git submodule sync --recursive
git submodule update --init --recursive
```

### Run Validation Gates

```bash
# ISA contract validation (mandatory)
python3 tools/bringup/check26_contract.py --root .

# Full regression suite
bash tools/regression/run.sh
```

---

## Repository Structure

```
linx-isa/
├── avs/                    # Architecture Validation Suite
│   ├── qemu/              # Runtime AVS tests (QEMU)
│   ├── compiler/          # Compile-only AVS tests (LLVM)
│   └── runtime/           # Freestanding libc support
│
├── compiler/              # LLVM submodule (linx-isa target)
├── emulator/              # QEMU submodule (linx-isa emulation)
├── kernel/                # Linux kernel submodule
├── rtl/                   # LinxCore RTL submodule
├── lib/                   # Standard libraries (glibc, musl)
│   ├── glibc/
│   └── musl/
│
├── tools/                 # Build scripts, generators, regression
│   ├── bringup/          # Bring-up orchestration
│   ├── regression/       # Test runners
│   └── pyCircuit/        # ISA model (submodule)
│
├── workloads/             # Benchmarks and kernels
│   └── pto_kernels/     # PTO accelerator kernels (submodule)
│
├── isa/                   # ISA specification sources
│   ├── v0.3/            # v0.3 ISA definition
│   └── generated/        # Generated encodings/decoders
│
└── docs/                  # Architecture & bring-up documentation
    ├── architecture/      # ISA manual and references
    ├── bringup/          # Bring-up status and gates
    ├── reference/        # Examples and guides
    └── project/          # Navigation and policies
```

---

## Submodules

| Submodule | Repository | Purpose |
|-----------|------------|---------|
| `compiler/llvm` | [LinxISA/llvm-project](https://github.com/LinxISA/llvm-project) | LLVM-based compiler for Linx |
| `emulator/qemu` | [LinxISA/qemu](https://github.com/LinxISA/qemu) | QEMU-based emulator |
| `kernel/linux` | [LinxISA/linux](https://github.com/LinxISA/linux) | Linux kernel port |
| `rtl/LinxCore` | [LinxISA/LinxCore](https://github.com/LinxISA/LinxCore) | RTL implementation |
| `tools/pyCircuit` | [LinxISA/pyCircuit](https://github.com/LinxISA/pyCircuit) | ISA reference model |
| `lib/glibc` | [LinxISA/glibc](https://github.com/LinxISA/glibc) | GNU C Library port |
| `lib/musl` | [LinxISA/musl](https://github.com/LinxISA/musl) | musl libc port |
| `workloads/pto_kernels` | [LinxISA/PTO-Kernel](https://github.com/LinxISA/PTO-Kernel) | PTO accelerator kernels |

### Updating Submodules

```bash
# Sync and update all submodules
git submodule sync --recursive
git submodule update --init --recursive

# Pull latest from upstream
git submodule update --remote compiler/llvm emulator/qemu kernel/linux rtl/LinxCore tools/pyCircuit lib/glibc lib/musl workloads/pto_kernels

# Verify layout
bash tools/ci/check_repo_layout.sh
```

---

## Validation & Testing

### Core Gates

| Gate | Command | Description |
|------|---------|-------------|
| **check26 Contract** | `python3 tools/bringup/check26_contract.py --root .` | ISA specification compliance |
| **Compiler AVS** | `cd avs/compiler/linx-llvm/tests && ./run.sh` | LLVM code generation tests |
| **QEMU Runtime** | `cd avs/qemu && ./run_tests.sh --all` | Emulator execution tests |
| **Linux Boot** | `python3 kernel/linux/tools/linxisa/initramfs/smoke.py` | Kernel boot validation |

### Regression Suites

```bash
# Main regression (fast)
bash tools/regression/run.sh

# Full stack (includes Linux boot)
bash tools/regression/full_stack.sh

# Strict cross-repo (release gates)
bash tools/regression/strict_cross_repo.sh
```

---

## Documentation

- **Website**: https://linxisa.github.io/
- **[Getting Started](docs/bringup/GETTING_STARTED.md)** - Onboarding guide
- **[Architecture Contract](docs/architecture/v0.3-architecture-contract.md)** - ISA v0.3 specification
- **[Bring-up Progress](docs/bringup/PROGRESS.md)** - Current status tracking
- **[Navigation Guide](docs/project/navigation.md)** - Repository layout policy
- **[ISA Manual](docs/architecture/isa-manual/README.md)** - Complete ISA documentation

---

## Versioning

- **ISA Version**: v0.3 (current)
- **Repository**: This superproject pins specific commits of all ecosystem repos
- **Release Notes**: See [docs/releases/](docs/releases/) for version history

---

## Contributing

1. Follow the [navigation policy](docs/project/navigation.md)
2. Implement changes in the relevant submodule first
3. Run validation gates locally before submitting
4. Update submodule SHAs in this workspace
5. Ensure `tools/ci/check_repo_layout.sh` passes

---

## License

See [LICENSE](LICENSE) file for details.
