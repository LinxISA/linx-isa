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

## 0.59.1 offline Chinese instruction reference

Download the HTML ZIP from the [0.59.1 specification release](https://github.com/LinxISA/linx-isa/releases/tag/v0.59.1), extract it and open `index.html`. Start with a functional class, then open its alphabetic mnemonic index. The instruction pages reproduce the authored Chinese MkDocs articles with their assembly examples and SVGs. Local references, including the pseudocode glossary and the compressed-extension description, are included in the archive. The LSU index uses the AGU catalog key. The release commit and source catalog hashes are on the sources page.

Run `make html-reference check-html-reference` in this directory to build and audit the site. The generator resolves `v0.59.1` to a commit, reads the tagged catalog, and compares the 578 common, 705 scoped and 216 retained Linx forms to their sources. Use a checkout containing the generator and the tag. Fetch the tag in a shallow clone before building.

The generator uses the repository’s existing MkDocs Markdown dependencies. Install the documentation environment used by CI before building the offline edition.
