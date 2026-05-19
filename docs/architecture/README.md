# Architecture Docs

Architecture-facing documentation lives under `docs/architecture/`.

## Canonical contract pages

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/v0.56-hardening-policy.md`
- `docs/architecture/v0.56-simt-compiler-contract.md`
- `docs/architecture/v0.56-simt-compiler-contract-plan.md` (planning page; not itself normative)
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-kernel-authoring.md`
- `docs/architecture/v0.56-rendering-pto-contract.md`
- `docs/architecture/v0.56-rendering-command-contract.md`
- published LinxCore pages:
  - `docs/architecture/linxcore/overview.md`
  - `docs/architecture/linxcore/microarchitecture.md`
  - `docs/architecture/linxcore/interfaces.md`
  - `docs/architecture/linxcore/verification-matrix.md`
  - `docs/architecture/linxcore/module-catalog.md`
  - `docs/architecture/linxcore/pipeline-stage-catalog.md`
- LinxCore source material:
  - `rtl/LinxCore/docs/architecture/`

## ISA manual

- `docs/architecture/isa-manual/`
  - AsciiDoc ISA manual source and generated PDF.

## Published bilingual manual surface

The published docs site now has a broader manual hierarchy than the AsciiDoc
manual alone:

- ISA/publication pages under `docs/background/`, `docs/compiler/`,
  and the expanded `docs/isa/` tree,
- a Chinese edition under `docs/zh/` with path parity,
- the existing generated `docs/isa/groups/` and `docs/isa/instructions/`
  retained as appendix/reference rather than the primary manual home.

The normative rule does not change: architecture-affecting behavior is still
owned by the English v0.56 contract pages and the English AsciiDoc manual.
The broader manual pages are the primary published narrative surface,
but they must stay synchronized with those normative sources.

## Governance notes

- LinxArch pages are the canonical architecture contract for bring-up and gates.
- LinxCore contract authoring lives in `rtl/LinxCore/docs/architecture/`; the
  superproject `docs/architecture/linxcore/` pages are published copies.
- Implementation-specific deep dives in submodules must link back to these
  contract pages.
- Any architecture-affecting change must update LinxArch first, then implementation.
- Archived pre-v0.56 material, pre-canonical draft notes, and research notes are retained for history only and must not be used as the live contract.
- Planning pages may live alongside canonical pages when they define the staged path to the next contract freeze; they must state clearly whether they are normative.
