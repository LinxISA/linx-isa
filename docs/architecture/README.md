# Architecture Docs

Architecture-facing documentation lives under `docs/architecture/`.

## Canonical contract pages

- `docs/architecture/v0.4-architecture-contract.md`
- `docs/architecture/v0.4-hardening-policy.md`
- `docs/architecture/v0.4-workload-engine-model.md`
- `docs/architecture/v0.4-rendering-kernel-authoring.md`
- `docs/architecture/v0.4-rendering-pto-contract.md`
- `docs/architecture/v0.4-rendering-command-contract.md`
- `docs/architecture/linxcore/overview.md`
- `docs/architecture/linxcore/microarchitecture.md`
- `docs/architecture/linxcore/interfaces.md`
- `docs/architecture/linxcore/verification-matrix.md`

## ISA manual

- `docs/architecture/isa-manual/`
  - AsciiDoc ISA manual source and generated PDF.

## Governance notes

- LinxArch pages are the canonical architecture contract for bring-up and gates.
- Implementation-specific deep dives in submodules must link back to these pages.
- Any architecture-affecting change must update LinxArch first, then implementation.
- Archived material (`v0.3`, pre-canonical draft notes, research notes) is retained for history only and must not be used as the live contract.
