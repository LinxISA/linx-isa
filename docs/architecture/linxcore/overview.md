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
- Workload-to-engine model: `docs/architecture/v0.4-workload-engine-model.md`
- Rendering command model: `docs/architecture/v0.4-rendering-command-contract.md`
- LinxCore microarchitecture contract: `docs/architecture/linxcore/microarchitecture.md`
- LinxCore interface contract: `docs/architecture/linxcore/interfaces.md`
- LinxCore gate traceability matrix: `docs/architecture/linxcore/verification-matrix.md`

## Source-of-truth model

- Canonical governance + architecture contract: `linx-isa` superproject docs
- Canonical implementation lane: pinned submodules in `linx-isa`
- Standalone trees (for example `/Users/zhoubot/LinxCore`) are mirror lanes, not contract authority

## Execution Composition

LinxCore is the block-ordered execution substrate for the current `v0.4`
multi-workload model.

- BCC and the block fabric remain the architectural control and orchestration
  path.
- `VEC`, `TMA`, `CUBE`, and `TAU` are integrated engines within that same
  block/BID-ordered machine.
- Engine-backed work does not define a separate retirement or command language;
  it remains subordinate to the same recovery, completion, and observability
  rules described by the live architecture contract.

## Current architecture closure slice

The current architecture-writing pass covers the promoted frontend/decode,
post-rename dispatch, and baseline issue/wakeup slice from `IFU/F0` through
`W1`.

Stage lineup in this pass:

- `F0`: PC-select stage; chooses the next fetch PC from multiple candidate PCs
  and presents a registered `F0->F1` boundary.
- `F1`: I-cache lookup stage; architecture-facing control remains per-thread,
  while the current physical implementation arbitrates a single I-cache read
  port across threads.
- `F2`: I-cache data staging and ECC check; forwards only ECC-clean raw cache
  data and thread/PC context.
- `F3`: variable-length stitch/assembly, static prediction, block-boundary
  annotation, and template recognition/expansion control.
- `IB`: per-thread instruction-buffer banks feeding aligned decode groups.
- `D1`: decode, contiguous-group formation, and `RID/BID/LSID` allocation.
- `D2`: rename request/translation stage.
- `D3`: renamed-uop latch point.
- `S1`: post-rename dispatch preparation (routing + ready query).
- `S2`: actual `IQ` entry write.
- `P1`: `IQ` pick stage.
- `I1`: operand-read planning and RF read-port arbitration.
- `I2`: issue-confirm / `IQ` deallocation boundary.
- `E1`: first execute stage.
- `W1`: baseline late wakeup / resolve stage.

This pass is intentionally focused on architectural stage ownership and
interface shape. More detailed unit-internal execute/bypass topologies and
full commit machinery still remain under the later bring-up contracts until
those contracts are promoted in the same style.

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
