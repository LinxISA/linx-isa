# Project Documentation

Repository-level process, governance, and navigation policies.

## Contents

- **[navigation.md](navigation.md)** - Canonical path map and forbidden paths
- **[repository-flow.md](repository-flow.md)** - Development workflow and contribution guide

## Navigation Policy

This workspace follows a strict navigation contract. See [navigation.md](navigation.md) for:

- Allowed top-level directories
- Canonical destinations for specific tasks
- Forbidden/replaced paths
- Submodule update procedures

## Quick Reference

| Task | Path |
|------|------|
| Runtime tests | `avs/qemu/` |
| Compile tests | `avs/compiler/linx-llvm/tests/` |
| Freestanding libc | `avs/runtime/freestanding/` |
| Linux libc sources | `lib/glibc/`, `lib/musl/` |
| PTO kernel headers | `workloads/pto_kernels/include/` |
| Assembly examples | `docs/reference/examples/v0.3/` |

## CI Validation

Before committing, verify repository layout:

```bash
bash tools/ci/check_repo_layout.sh
```
