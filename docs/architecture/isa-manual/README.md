# Linx Instruction Set Architecture Manual (AsciiDoc)

This directory contains the AsciiDoc ISA manual for the **Linx Instruction Set
Architecture (Linx ISA)**. The latest stable profile is v0.56.5. The manual is
written in **AsciiDoc** and built to **PDF** using `asciidoctor-pdf` (via
Bundler).

The content is specific to Linx’s design (block-structured control flow, `BSTART/BSTOP`, ClockHands temporaries,
template instructions like `FENTRY`, etc).

## Build

From this directory:

```bash
make pdf
```

Outputs:
- `build/linxisa-isa-manual.pdf`

## Release artifacts

- Current stable manual release notes: `docs/releases/v0.56.5.md`
- Latest release page: https://github.com/LinxISA/linx-isa/releases/latest

## Regenerate generated sections

The current generated manual sections are derived from the v0.56 catalog:
- `isa/v0.56/linxisa-v0.56.json`

Regenerate:

```bash
make gen
```

Note: `build/` is gitignored; local build outputs are not committed to the repository.
