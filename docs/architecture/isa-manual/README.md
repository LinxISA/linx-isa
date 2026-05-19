# Linx Instruction Set Architecture Manual (AsciiDoc)

This directory contains the live v0.56.2 ISA manual for the **Linx Instruction Set Architecture (Linx ISA)**, written in
**AsciiDoc** and built to **PDF** using
`asciidoctor-pdf` (via Bundler).

The content is specific to Linx’s design (block-structured control flow, `BSTART/BSTOP`, ClockHands temporaries,
template instructions like `FENTRY`, etc).

The docs site also publishes a broader Markdown manual hierarchy for the standalone site. That broader hierarchy is the primary public
navigation surface, but this English AsciiDoc manual remains the normative
English manual source for architecture-visible behavior.

Related published pages:

- `docs/background/`
- `docs/compiler/`
- `docs/isa/`
- `docs/zh/` (Chinese edition)

## Build

From this directory:

```bash
make pdf
```

Outputs:
- `build/linxisa-isa-manual.pdf`

## Release artifacts

- Current release notes: `docs/releases/v0.56.2.md`
- Latest release page: https://github.com/LinxISA/linx-isa/releases/latest

## Regenerate generated sections

The manual includes generated AsciiDoc derived from the canonical spec:
- `isa/v0.56/linxisa-v0.56.json`

Regenerate:

```bash
make gen
```

Note: `build/` is gitignored; local build outputs are not committed to the repository.
