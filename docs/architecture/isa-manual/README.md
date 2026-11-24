# Linx Instruction Set Architecture Manual (AsciiDoc)

This directory contains the AsciiDoc ISA manual for the **Linx Instruction Set
Architecture (Linx ISA)**. The latest stable profile is v0.58. The manual is
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

- Current stable manual release notes: `docs/releases/v0.58.3.md`
- Latest release page: https://github.com/LinxISA/linx-isa/releases/latest

## Regenerate generated sections

The current generated manual sections are derived from the v0.58 catalog:
- `isa/v0.58/linxisa-v0.58.json`

Regenerate:

```bash
make gen
```

Note: `build/` is gitignored; local build outputs are not committed to the repository.

## 0.59.2 offline HTML instruction reference

Extract the ZIP and open `index.html`. Eight functional classes, the mnemonic index and the encoding index cover 1,306 forms. Four encoding-only entries carry an explicit status notice. The Tile index covers 119 operations. [Download the Chinese HTML manual](https://github.com/LinxISA/linx-isa/releases/download/v0.59.2/linxisa-0.59.2-html.zip)

Run `make html-reference check-html-reference` in this directory with the release tags v0.59.2 and v0.59.1 available. Install the Markdown dependencies from `reference/requirements.txt`.
