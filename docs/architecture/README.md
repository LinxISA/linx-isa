# Architecture Docs

Architecture-facing documentation lives under `docs/architecture/`.

## Canonical contract pages

- v0.58 canonical page:
  - `docs/architecture/v0.58-architecture-contract.md`
- machine-readable authority:
  - `isa/v0.58/linxisa-v0.58.json`
- generated encoding and instruction reference:
  - `docs/isa/encoding.md`
  - `docs/isa/instructions/`
- published LinxCore mirrors:
  - `docs/architecture/linxcore/overview.md`
  - `docs/architecture/linxcore/microarchitecture.md`
  - `docs/architecture/linxcore/interfaces.md`
  - `docs/architecture/linxcore/verification-matrix.md`
  - `docs/architecture/linxcore/module-catalog.md`
  - `docs/architecture/linxcore/pipeline-stage-catalog.md`
  - `docs/architecture/linxcore/ifu.md`
- canonical LinxCore authoring source:
  - `rtl/LinxCore/docs/architecture/overview.md`
  - `rtl/LinxCore/docs/architecture/microarchitecture.md`
  - `rtl/LinxCore/docs/architecture/interfaces.md`
  - `rtl/LinxCore/docs/architecture/verification-matrix.md`
  - `rtl/LinxCore/docs/architecture/module-catalog.md`
  - `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`
  - `rtl/LinxCore/docs/architecture/ifu.md`

## ISA manual

- `docs/architecture/isa-manual/`
  - AsciiDoc ISA manual source and generated PDF.

## Governance notes

- LinxArch pages are the canonical architecture contract for bring-up and gates.
- LinxCore contract authoring lives in `rtl/LinxCore/docs/architecture/`; the
  superproject `docs/architecture/linxcore/` pages are generated publication
  mirrors.
- Implementation-specific deep dives in submodules must link back to these
  contract pages.
- Any architecture-affecting change must update LinxArch first, then implementation.
- v0.58 is the sole active profile; its sources must not revive retired
  compatibility spellings or archived raw fragments.
- Historical profiles, archived narratives, pre-canonical drafts, and research
  notes are context only and must not be used as the live contract or an agent
  entry point.
- Planning pages may live alongside canonical pages when they define the staged path to a future contract freeze; they must state clearly whether they are normative.
