# Linx Instruction Set Architecture Manual (AsciiDoc)

This directory contains the live v0.4 ISA manual for the **Linx Instruction Set Architecture (Linx ISA)**, written in
**AsciiDoc** and built to **PDF** using
`asciidoctor-pdf` (via Bundler).

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

- Current release notes: `docs/releases/v0.4.0.md`
- Latest release page: https://github.com/LinxISA/linx-isa/releases/latest

## Regenerate generated sections

The manual includes generated AsciiDoc derived from the canonical spec:
- `isa/v0.4/linxisa-v0.4.json`

Regenerate:

```bash
make gen
```

Note: `build/` is gitignored; local build outputs are not committed to the repository.
