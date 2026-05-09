# Archived v0.3 Bring-up Plan: Clarifications

This page is preserved only as an archive index for retired `v0.3` bring-up
decisions. It is not normative for the current canonical `v0.56` ISA contract.

## Live Canonical Sources

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/isa-manual/src/linxisa-isa-manual.adoc`
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-command-contract.md`
- `isa/v0.56/state/engine_ops.json`
- `tools/bringup/check_avs_contract.py`
- `tools/bringup/check_sail_model.py`

## Clarifications Promoted Into Canonical v0.56

The live `v0.56` contract now carries the normative form of the older bring-up
decisions that originally lived here:

- block-boundary legality and boundary-only control-flow targets,
- block-format validation and body-fetch fault reporting,
- `TPC` and body-entry terminology,
- template replay metadata and `BSTART.TEPL` selector handling,
- SIMT/vector body termination, `.brg` legality, and RI namespace usage,
- current `BSTART.TEPL` versus `BSTART.FIXP` separation.

## Historical Status

- Retired legacy pre-AVS conformance files are not part of current closure.
- `v0.3` architecture-contract pages are not live sources for `v0.56`.
- The archived migration notebook remains the only retained draft-history
  surface for this cutover.

## Usage Rule

If any wording in this archive note disagrees with canonical `v0.56` docs, state
catalogs, or validators, the canonical `v0.56` surfaces win.
