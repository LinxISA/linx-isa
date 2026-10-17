# LinxISA 0.58.7 scalar synchronization candidate

The immutable publication baseline is PTO 0.58.7.0, commit
`de57af400cf607f03730aa522a4e9bfb160596de`. It contains 466 scalar forms,
96 command forms, and 118 Tile operations.

This candidate integrates fengzhazha's LinxISA PR #208 with the companion [PTO scalar PR #390](https://github.com/PTO-ISA/pto-spec/pull/390)
proposal pinned by `isa/v0.58/pto-scalar-proposal.lock.json`. All 473
active scalar forms, including the previously accepted PTO `SYNC.CORE`, match
the proposal exactly. DMA.FREE.S/L and MCOPY.DS/DL retain matching encodings
and operands only; they are not implemented and reject execution before effects.

The 44 atomic replacements and six new store forms are kept separate from the
published baseline. The proposal lock pins the exact PTO commit, tree, catalog
bytes, and effective scalar projection. Neither lock nor this candidate claims
that changed atomic binaries have the published release's encoding identity.

## Validation

- Golden/catalog/manifest/navigation/codec checks, opcode-extension regression,
  baseline-import verification, and scalar proposal parity pass.
- Sail 0.20.2 parser, C generation, and executable directed tests pass. The
  four resource reservations and SYNC.CORE are explicitly decode-only in this
  single-context model; coverage does not claim architectural completeness.
- English and Chinese MkDocs strict builds and documentation integrity pass.
- Independent scalar tests cover every changed atomic family, six new forms,
  subtraction underflow, narrow-store guard bytes, and rejected resource forms.

## Merge blockers

The pinned QEMU leaf still has the old atomic op5 layout. The restored exact
LR.W/LR.D check fails against it; CI now runs that check so mnemonic presence
cannot mask a raw-encoding mismatch. The [companion QEMU PR #82](https://github.com/LinxISA/qemu/pull/82) must be
reviewed and landed, with the four resource instructions remaining unsupported,
before updating the gitlink and component lock.

The PTO counterpart is a proposal, not a published release. Its ordinary
repository check is also blocked by stale release-owner projections: unchanged
PTO main has 79 TEPL operations while the frozen 0.58.7 release generator expects
78. No publication metadata or validation rule is weakened to bypass that gap.

Skill closeout: `skill-evolve: no-update` for linx-isa, linx-superproject,
and linx-qemu; this work follows their existing source and validation rules.
