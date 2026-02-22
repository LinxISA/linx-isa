# Linx Standard Libraries

This directory hosts the **standard library implementations** for LinxISA:

| Library | Repository | Purpose |
|---------|------------|---------|
| **glibc** | [LinxISA/glibc](https://github.com/LinxISA/glibc) | GNU C Library |
| **musl** | [LinxISA/musl](https://github.com/LinxISA/musl) | musl libc (lightweight) |

## Quick Start

### Clone with Submodules

```bash
git clone --recurse-submodules git@github.com:LinxISA/linx-isa.git
cd linx-isa
git submodule sync --recursive
git submodule update --init --recursive
```

### Building Libraries

#### musl (Recommended for Bring-up)

```bash
# Phase-a (minimal)
MODE=phase-a lib/musl/tools/linx/build_linx64_musl.sh

# Phase-b (runtime testing)
MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh

# Phase-c (full SPEC)
MODE=phase-c lib/musl/tools/linx/build_linx64_musl.sh
```

#### glibc

```bash
# Basic build (G1a)
bash lib/glibc/tools/linx/build_linx64_glibc.sh

# Shared libc (G1b)
bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh
```

### Build Artifacts

All build outputs are written to `out/libc/`:

```
out/libc/
├── glibc/
│   └── logs/
└── musl/
    ├── install/
    │   ├── phase-a/
    │   ├── phase-b/
    │   └── phase-c/
    └── logs/
```

## Current Status

See [docs/bringup/libc_status.md](../docs/bringup/libc_status.md) for current build and runtime status.

## Development Notes

- Both libraries are maintained as git submodules pointing to LinxISA forks
- Bring-up patches are applied on top of upstream releases
- Use the top-level make targets for consistent patch application:

```bash
make libc-patch-glibc
make libc-patch-musl
make libc-build
```
