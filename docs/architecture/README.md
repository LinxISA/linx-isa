# Architecture Docs

Architecture-facing documentation lives under `docs/architecture/`.

## Canonical contract pages

- `docs/architecture/v0.4-architecture-contract.md`
- `docs/architecture/v0.4-hardening-policy.md`
- `docs/architecture/v0.4-simt-compiler-contract.md`
- `docs/architecture/v0.4-simt-compiler-contract-plan.md` (planning page; not itself normative)
- `docs/architecture/v0.4-workload-engine-model.md`
- `docs/architecture/v0.4-rendering-kernel-authoring.md`
- `docs/architecture/v0.4-rendering-pto-contract.md`
- `docs/architecture/v0.4-rendering-command-contract.md`
- published LinxCore mirrors:
  - `docs/architecture/linxcore/overview.md`
  - `docs/architecture/linxcore/microarchitecture.md`
  - `docs/architecture/linxcore/interfaces.md`
  - `docs/architecture/linxcore/verification-matrix.md`
  - `docs/architecture/linxcore/module-catalog.md`
  - `docs/architecture/linxcore/pipeline-stage-catalog.md`
- canonical LinxCore authoring source:
  - `rtl/LinxCore/docs/architecture/overview.md`
  - `rtl/LinxCore/docs/architecture/microarchitecture.md`
  - `rtl/LinxCore/docs/architecture/interfaces.md`
  - `rtl/LinxCore/docs/architecture/verification-matrix.md`
  - `rtl/LinxCore/docs/architecture/module-catalog.md`
  - `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`

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
- Archived material (`v0.3`, pre-canonical draft notes, research notes) is retained for history only and must not be used as the live contract.
- Planning pages may live alongside canonical pages when they define the staged path to the next contract freeze; they must state clearly whether they are normative.
