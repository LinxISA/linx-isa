# PTO golden synchronization

PTO-SPEC is the sole authority. The active design consumes development golden
`f0a876e449a95d26841c5ee7affb4c905ebc5f5b`, not a mixture of the old published
commands and a downstream scalar amendment. The golden includes 473 scalar
forms, 105 command forms, 119 Tile operations, and 50 encoding reservations.

`tools/isa/import_pto_golden.py` verifies exact commit/tree and upstream file
bytes, then projects all common catalogs. `check_pto_scalar_proposal.py` checks
full scalar/command/Tile/reservation equality and the active encoding identity.
The historical filenames remain entry points; no independent scalar amendment
source remains. `gen_pto_binder_pages.py` generates English/Chinese B.IOT and
B.IOS references from the pinned PTO owning ASL contract, including independent
.reuse/last-use semantics.

The current development ELF identity has release `0.58.7`, ABI
`pto-isa-0.58.7-mode-function-v1`, and encoding projection
`a5f78ecd707bde4a014542158ea257c783796b95fa4fbcce37742e41fee6a881`.
It is not the published 0.58.7.0 identity; old objects must reject. The immutable
publication lock and its frozen 466/96/118 inventory remain historical evidence.

## Downstream work

- [PTO-SPEC #390](https://github.com/PTO-ISA/pto-spec/pull/390) owns scalar
  definitions, development identity, and source traceability.
- [QEMU #82](https://github.com/LinxISA/qemu/pull/82) synchronizes scalar
  masks, rejects removed fused32 CALL, checks frame legality before effects,
  and rejects unsupported resource/header/synchronization forms.
- [PTOAS #9](https://github.com/LinxISA/PTOAS/pull/9) pins the same golden and
  rejects retired names through shared verification. Name presence is not
  semantic conformance: 94 names are present, 25 golden operations are absent,
  and 87 retained operation catalogs changed since its previous source.
- LLVM and the model catalog consumer are updated in their owning PRs; exact
  checked revisions and validation evidence accompany those PRs.

## Implementation boundaries

DMA.FREE.S/L and MCOPY.DS/DL are encoding-only, NOT IMPLEMENTED, in both golden
and consumers. No successful no-op, identity address, or resource behavior is
invented. New binder lifetime modes, nonzero ExecutionMask controls, and
SYNC.CORE are decoded but explicitly unsupported in the staged Sail/QEMU
subsets. This does not narrow the PTO architecture or claim full conformance.

Leaf revisions are promoted to superproject gitlinks only after their own
review and gates; old default pins remain a visible integration dependency.

Skill closeout: `skill-evolve: no-update` for linx-isa, linx-superproject,
linx-compiler, and linx-qemu; the current-source authority and exact-pin rules
already govern this synchronization.
