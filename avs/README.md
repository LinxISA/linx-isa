# Architecture Validation Suite (AVS)

This directory contains the canonical **Architecture Validation Suite** for LinxISA v0.3.

## Overview

The AVS validates that all implementations (compiler, emulator, RTL, kernel) conform to the ISA specification. It consists of two complementary test suites:

| Suite | Location | Type |
|-------|----------|------|
| **Runtime** | `avs/qemu/` | Execution-based tests |
| **Compile** | `avs/compiler/linx-llvm/tests/` | Code generation tests |

## Test Matrix

- **Machine-readable**: [avs/linx_avs_v1_test_matrix.yaml](linx_avs_v1_test_matrix.yaml)
- **Documentation**: [avs/matrix_v1.md](matrix_v1.md)

## Running AVS Tests

### Runtime Tests (QEMU)

```bash
cd avs/qemu
./run_tests.sh --all --timeout 10
```

### Compile Tests (LLVM)

```bash
cd avs/compiler/linx-llvm/tests
CLANG=compiler/llvm/build-linxisa-clang/bin/clang ./run.sh
```

### Strict System Tests

```bash
cd avs/qemu
LINX_DISABLE_TIMER_IRQ=0 ./check_system_strict.sh
```

## Adding New Tests

- **Runtime tests**: Add to `avs/qemu/tests/`
- **Compile tests**: Add to `avs/compiler/linx-llvm/tests/`
- **Coverage analysis**: Run `analyze_coverage.py` after adding new instructions

## Freestanding libc

AVS tests use the freestanding libc at `avs/runtime/freestanding/`. This provides minimal C runtime support without depending on full libc implementations.
