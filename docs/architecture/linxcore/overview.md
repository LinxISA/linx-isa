# LinxCore v0.4 Superscalar Bring-up Overview

## Scope

This document defines the architecture closure target for LinxCore under the strict v0.4 bring-up program.

Closure target:

- v0.4 architectural closure
- U + S privilege behavior
- MMU + interrupts enabled and validated
- dual-lane reproducibility (`pin` and `external`)
- strict required gates with evidence artifacts

## Normative links

- Base ISA architecture contract: `docs/architecture/v0.4-architecture-contract.md`
- LinxCore microarchitecture contract: `docs/architecture/linxcore/microarchitecture.md`
- LinxCore interface contract: `docs/architecture/linxcore/interfaces.md`
- LinxCore gate traceability matrix: `docs/architecture/linxcore/verification-matrix.md`

## Source-of-truth model

- Canonical governance + architecture contract: `linx-isa` superproject docs
- Canonical implementation lane: pinned submodules in `linx-isa`
- Standalone trees (for example `/Users/zhoubot/LinxCore`) are mirror lanes, not contract authority

## Program phases (gate-based)

- G0: governance and gate wiring
- G1: architecture contract completion
- G2: LinxCore superscalar functional closure
- G3: pyCircuit API + flow hardening
- G4: testbench + LinxTrace hard closure
- G5: integrated dual-lane closure + continuous repin

Phase transitions are gate-driven, not date-driven.

## Mandatory closure outcomes

- Required-gate matrix is complete and blocking
- Multi-agent ownership is explicit and validated by static/runtime gate checks
- LinxArch contract pages and implementation gates stay synchronized
- Waivers are explicit, issue-linked, phase-bound, and expiry-enforced
