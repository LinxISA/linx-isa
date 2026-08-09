# LinxISA Assembly Sample Pack (v0.57.1)

> Historical, non-normative archive. Do not use these examples for current assembly or toolchain decisions.

Canonical public assembly examples generated from the locked PTO ISA 0.57.1
kernel surface.

## Layout

- `curated/`: reviewed hand-curated scalar/disassembly examples.
- `generated/`: deterministic compiler outputs from
  `workloads/pto_kernels/tools/examples/`.
- `index.yaml`: exact source and toolchain provenance.

## Canonical tile example

```asm
BSTART.TLOAD INT32
B.DIM        a3, 0, ->lb0
B.DIM        a3, 0, ->lb1
B.DIM        a3, 0, ->lb2
B.IOR        [a6,a7],[]
B.IOT        last, ->t<4KB>
```

The 0.57.1 examples contain no `B.ARG`, generic `BSTART.TMA` or
`BSTART.CUBE`, `MAMULB`, or deleted D-class operation. Regenerate them with the
LLVM and PTO-Kernel commits recorded in `index.yaml`.
