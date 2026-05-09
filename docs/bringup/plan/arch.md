# Archived v0.3 Bring-up Plan: Architecture Checklist

This page is retained only as historical bring-up planning for the retired `v0.3`
cutover. It is not a live contract surface for canonical `v0.56`.

## Live Canonical Sources

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-command-contract.md`
- `docs/architecture/linxcore/overview.md`
- `docs/architecture/linxcore/microarchitecture.md`
- `isa/v0.56/`
- `tools/bringup/check_avs_contract.py`
- `tools/bringup/check_avs_profile_closure.py`

## Historical Scope

The retired `v0.3` checklist tracked the initial bring-up of:

- block-structured execution and boundary-only control-flow,
- GSTATE/BSTATE split and block command dispatch,
- descriptor validation and decoupled body entry behavior,
- TMA, CUBE, TEPL, and SIMT/vector block-family shape,
- bridged `.brg` memory forms and RI namespace rules,
- trap envelopes and restartability for early compiler/QEMU/RTL parity.

Those topics have now been promoted into the canonical `v0.56` manual, state
catalog, and architecture-contract pages. Any remaining `v0.3` wording should be
treated as archive-only history, not as a normative source.

## Current Closure Policy

- AVS is the only live public bring-up contract.
- Tier closure is selected by `state + must_pass_in_tier`.
- Retired legacy pre-AVS contract artifacts are not part of current `v0.56`
  closure.

## Historical Note

This file stays in `docs/bringup/plan/` only to preserve planning traceability for
older bring-up discussions. It should not be cited as evidence for current
release-strict `v0.56` closure.
