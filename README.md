# linxisa

<p align="center">
  <img src="docs/architecture/isa-manual/src/images/linxisa-logo.svg" alt="LinxISA logo (灵犀)" width="180" />
</p>

LinxISA is a new instruction-set architecture (ISA) in the spirit of RISC-style ISAs, with a repository layout intended
to keep **specification**, **software**, and **hardware** implementations consistent.

## Naming

- Official ISA name: **LinxISA** (Linx Instruction Set Architecture)
- Short name: **Linx**
- LLVM/MC arch names: `linx32`, `linx64`

## Branding

- Official logo asset (SVG): `docs/architecture/isa-manual/src/images/linxisa-logo.svg`
- Design intent: preserve the original **灵犀**-inspired silhouette and add subtle semiconductor-style detailing (routed traces, pads/vias) for technical ISA branding.

## Source of truth

The ISA definition is centralized under `isa/`:
- Golden sources (authoritative, current): `isa/golden/v0.3/**`
- Compiled, machine-readable catalog (checked in, current): `isa/spec/current/linxisa-v0.3.json`
- Legacy catalogs (kept for reference): `isa/spec/current/linxisa-v0.2.json`, `isa/spec/current/linxisa-v0.1.json`

All implementations in this repo (compiler, emulator, C++ models, RTL) should reference the formal catalog to avoid
decode/encode drift.

## ISA manual (PDF)

A draft ISA manual (AsciiDoc → PDF) lives in:

- `docs/architecture/isa-manual/`

Build:

```bash
cd docs/architecture/isa-manual
make pdf
```

## Bring-up plan and progress

Canonical bring-up hierarchy and progress tracking live in:

- `docs/bringup/README.md`
- `docs/bringup/PROGRESS.md`

Current execution roadmap:

1. `docs/bringup/phases/04_rtl.md` (agile pyCircuit RTL/model loop)
2. `docs/bringup/phases/05_fpga_zybo_z7.md` (ZYBO Z7-20 platform bring-up)
3. `docs/bringup/phases/06_linux_on_janus.md` (Linux to BusyBox shell on Janus)

## Regression

Run the repo's end-to-end regression (compiler compile-only tests + coverage + QEMU runtime tests):

```bash
bash tools/regression/run.sh
```

Override tool locations as needed:

```bash
export CLANG=~/llvm-project/build-linxisa-clang/bin/clang
export LLD=~/llvm-project/build-linxisa-clang/bin/ld.lld
export QEMU=~/qemu/build-tci/qemu-system-linx64
bash tools/regression/run.sh
```

## Repository layout (initial)

- `isa/`: ISA specification and generated catalogs
- `tools/isa/`: spec extraction/validation tools
- `compiler/`: compiler/backend work (planned)
- `toolchain/`: assembler/linker/runtime tooling (planned)
- `emulator/`: reference emulator (planned)
- `models/`: C++ core models / reference models (planned)
- `rtl/`: RTL implementation (planned)
- `docs/`: design notes and development docs (architecture, bring-up, reference, project)
- `tests/`: QEMU runtime tests and scratch tests
- `workloads/`: benchmarks, examples, and generated codegen/runtime reports

## Target flow

1. C source → 2. compiler → 3. LinxISA encoding/spec → 4. emulator → 5. RTL (simulation/FPGA/ASIC)
