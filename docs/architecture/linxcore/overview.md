<!-- AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY. -->
<!-- Source: rtl/LinxCore/docs/architecture/overview.md -->

# LinxCore v0.56 Superscalar Bring-up Overview

> This published page mirrors the canonical LinxCore source in
> `rtl/LinxCore/docs/architecture/overview.md`.


## Scope

This document is the top-level specification overview for LinxCore under the
live LinxISA `v0.56` contract.

LinxCore is specified here as:

- the canonical superscalar out-of-order core for LinxISA,
- the architectural execution substrate for scalar, vector, tile, and
  accelerator-backed block work,
- the owner of precise retirement, recovery, interrupt, MMU, and trace-visible
  execution behavior,
- the machine that downstream compiler, emulator, pyCircuit, and testbench
  work must target for canonical `v0.56` behavior.

This specification is not a performance wish-list and not a historical bring-up
log. It defines the live contract the implementation must preserve.

Every architecturally visible stage in that contract must remain attached to a
named module boundary. Integration shells may compose stage modules, but they
must not erase stage ownership or hide a live stage inside undifferentiated top
glue.

## Normative links

- Base ISA architecture contract: `docs/architecture/v0.56-architecture-contract.md`
- Workload-to-engine model: `docs/architecture/v0.56-workload-engine-model.md`
- Rendering command model: `docs/architecture/v0.56-rendering-command-contract.md`
- LinxCore microarchitecture contract: `rtl/LinxCore/docs/architecture/microarchitecture.md`
- LinxCore interface contract: `rtl/LinxCore/docs/architecture/interfaces.md`
- LinxCore verification matrix: `rtl/LinxCore/docs/architecture/verification-matrix.md`

When wording diverges, the LinxISA architecture pages and the LinxCore
contract pages listed above are normative. Deep-dive implementation notes are
subordinate.

## LinxCoreModel alignment

`LinxISA/LinxCoreModel` is the most accurate executable simulator for Janus
Core behavior. LinxCore specification changes that affect architecturally
visible execution, engine completion, block recovery, ELF loading, or direct
boot workload behavior must be checked against the active model branch for the
current LinxISA line before promotion.

Current alignment point:

- Repository: `https://github.com/LinxISA/LinxCoreModel.git`
- Superproject checkout: `model/LinxCoreModel`
- Reference branch: `main`
- Reviewed commit: `793722e85c62eade9ab4e8481c9577dc5b9c98f7`
- Review date: 2026-07-10

The model is an executable reference, not a replacement for the written ISA
contract. When LinxCore docs and LinxCoreModel behavior disagree in a
Janus-Core-visible way, the discrepancy must be resolved explicitly by either:

- updating the LinxCore spec to match LinxCoreModel when the model represents
  the intended Janus Core behavior, or
- filing a model-lane fix when the model is an implementation bug relative to
  the LinxISA/LinxCore contract.

## Reference-design migration policy

The historical ARM-oriented input is preserved in Git commit
`8f6b821f75aa5170766d6ab4d37a9443b9a4f0ec`; the Linx migration draft is
preserved in commit `f72c0ee6fb21d08b2ac38d1f9918021bf6c28af3`. The live
tree does not retain either duplicate specification. The source-to-contract,
disposition, and dual-RTL ownership record is
`docs/architecture/mechanism-intake.json`.

The historical material explains why several mature out-of-order structures
exist, but it also contains missing references, contradictory widths,
unresolved flows, and AArch64-specific behavior. LinxCore therefore migrates
mechanisms only when their correctness rationale survives rebinding to
LinxISA.

The review uses four dispositions:

- **Adopt**: the mechanism solves an ISA-neutral correctness problem and fits
  the LinxCore contract directly.
- **Adapt**: the mechanism is useful, but its identity, recovery, or ordering
  fields must be rebound to Linx block semantics.
- **Parameterize**: the structure is useful, but queue counts, banking, port
  counts, or latency are implementation choices rather than architecture.
- **Reject**: the mechanism depends on ARM architectural state or conflicts
  with LinxISA.

| Reference mechanism | Why it exists | LinxCore decision |
|---|---|---|
| PC base plus offset buffer | Avoids carrying a full PC through every queue and execution pipe | Adapt for 16/32/48/64-bit instructions, semantic boundary metadata, checkpoint identity, legal-block-target validation, and full-PC trace reconstruction |
| Contiguous decode group with atomic resource admission | Prevents partial-group allocation from duplicating or reordering identities during backpressure | Adopt; reserve ROB, BROB, rename, IQ, and memory-order resources in program order without importing the reference core's fixed lane counts |
| `SMAP`/`CMAP`/free list/remap log | Removes WAR/WAW dependencies while retaining a precise committed recovery base | Adapt for scalar `P` state only; local `T/U` state uses independent local mapping queues and BID-qualified cleanup |
| Resident IQ entry with `inflight` lock | Allows cancelled speculative issues to retry without reinsertion or age loss | Adopt with Linx uop classes, `P` broadcast wakeup, and `T/U` point-to-point wakeup |
| Non-speculative ready table plus IQ-local speculative readiness | Allows load speculation without publishing cancellable state as globally ready | Adopt; wakeup at cycle `N` remains invisible to pick until cycle `N+1` |
| In-order ROB commit with later deallocation | Makes traps and side effects precise while retaining retired rows until cleanup is safe | Adapt with separate `(STID,BID_W-bit BID)` block identity, per-STID wrap-aware BROB order state, local-register sidecars, LSID watermarks, marker lifecycle, and BROB coordination |
| `LIQ`/resolved-load queue, `STQ`, `SCB`, and byte forwarding | Separates speculative memory state, replay state, and committed store drain | Adapt to Linx TSO, all-row LSID snapshots, per-STID BROB-qualified BID plus LSID ordering, and the BCC/MTC memory domain |
| Memory-disambiguation predictor | Learns recurring store/load conflicts to reduce repeated recovery | Adapt as an optional predictor; it may delay loads but must not weaken TSO or own precise nuke timing |
| Cache/TLB banking and fixed queue/port counts | Trades timing, power, and area against throughput | Parameterize; preserve translation, response identity, precise faults, and forward progress rather than ARM sizes |
| ARM grouped ROB/BranchQ BID | Compresses branch-group bookkeeping in an ARM control-flow machine | Reject; LinxCore uses one precise instruction-row identity plus a separate STID and per-STID BROB slot BID whose width is `ceil(log2(BROB_ENTRIES))` |
| ARM FSTLF, safe mode, PAC/BTI, SVE, exception levels, DMB/DSB, and exclusives | Implements ARM-specific performance or architectural behavior | Reject; re-derive any required behavior from LinxISA block control, ACR service requests, TSO, Linx fences/atomics, and engine contracts |

### Contract status language

This specification distinguishes obligation from evidence:

- **ISA requirement** is architecturally observable and mandatory even when
  an RTL owner is not yet complete.
- **LinxCore design policy** is the selected microarchitecture contract for
  this core and requires an intentional spec change to replace.
- **Reference evidence** records model behavior or a sizing point; it does not
  freeze the RTL topology.
- **Reduced-harness behavior** exists only to validate a partial path and is
  not evidence that the full owner or architectural interaction is complete.

Model parameters and unit-green Chisel helpers must not be presented as
completed full-core behavior without an integrated owner and cross-check.

## Core definition

LinxCore is a block-ordered heterogeneous superscalar core.

Its defining properties are:

- superscalar frontend, dispatch, issue, and commit behavior,
- out-of-order execution with precise architectural retirement,
- block-structured control flow with `BSTART` and `BSTOP` as architectural
  boundary markers,
- per-STID BROB-ring-ordered block tracking through `(STID,BID)`-carrying
  block-engine paths,
- one architectural recovery model for scalar, memory, template, and
  engine-backed work,
- one architectural trace model for commit and pipeline visibility.

LinxCore does not define a second hidden packet machine for engines. All
accelerator-backed work must remain subordinate to the same architectural block
stream, completion model, flush rules, and observability rules as scalar work.

## Architectural role in LinxISA

Under `v0.56`, LinxCore is the execution substrate for the multi-workload
LinxISA model.

- BCC and the block fabric provide the architectural control and submission
  path.
- `VEC` is the general programmable SIMT engine for parallel-loop work.
- `TMA` remains selected through the same block model. Architecturally it owns
  the Tile Memory Access command/completion frontend, while southbound memory
  transport terminates at the shared CSU/L2 boundary. That target CSU owner is
  not yet promoted here; `src/tma/tma.py` is the current reduced compatibility
  facade.
- `CUBE` and `TAU` remain integrated engines selected through the same block
  model.
- Engine-backed work must retire, cancel, redirect, and trace through LinxCore
  rules rather than through a separate architectural domain.

This composition rule is required for consistency with:

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-command-contract.md`

## Current architecture closure slice

The canonical pipeline taxonomy follows the ISA-neutral coordinate system from
the ARM reference while correcting the Linx-specific ownership boundaries.
There are four fetch stages (`F1..F4`) after `F0` frontend control, `F4` is the
instruction buffer, and result stages (`W1..W3`) overlay execution stages
rather than following them as a serial tail.

Stage lineup in this pass:

- `F0`: per-thread arbitration, redirect selection, and next-PC control.
- `F1`: translation and I-cache request/lookup launch.
- `F2`: fetch-return staging and integrity/ECC handling.
- `F3`: variable-length assembly, cross-line carry, and byte-stream ordering.
- `F4/IB`: final predecode/prediction and block-boundary metadata, plus the
  per-thread instruction buffer and D1 handoff. It is the fourth fetch stage,
  not a four-slot decode stage.
- `D1`: early decode, exception detection, split/fuse recognition, and group
  formation.
- `D2`: operand extraction, boundary resolution, and resource-demand
  preparation.
- `D3`: atomic resource admission, physical rename, ordering-ID acceptance,
  and dispatch-packet formation.
- `S1`: admitted-uop capture into the speculative issue-buffer boundary.
- `S2`: physical IQ allocation and write.
- `S3/IQ`: newly written row becomes resident and pick-visible.
- `P0`: optional registered candidate preselect.
- `P1`: final oldest-ready IQ pick.
- `I1`: operand-read planning and RF read-port arbitration.
- `I2`: bypass selection and issue confirmation; deallocation applies to
  non-speculative/non-cancellable transfers, while load-dependent speculative
  entries retain their IQ owner through E5 resolve.
- `E1`, `E2`, `E3`, ...: absolute execute cycles after I2.
- `W1`, `W2`, `W3`, ...: producer-relative actual
  data-bypass/result/writeback ages overlaid on E, with earlier speculative
  wakeup declared separately by E stage.
- `R0..R4`: completion intake, retirement decision, R2 commit/flush
  publication, recovery processing, and R4 restart.

Serial `IB -> F4` naming and decode helpers named `F4DecodeWindow` remain
migration work. They are implementation evidence, not alternate canonical
stage definitions.

## Specification set

The LinxCore specification is split into four contract pages:

- `overview.md`: scope, role, document boundaries, and authority rules.
- `microarchitecture.md`: execution model, detailed pipeline rules, recovery,
  memory, BID, `BROB`, and engine-composition semantics.
- `interfaces.md`: pyCircuit, commit trace, LinxTrace, block-fabric, and
  cross-tool synchronization contracts.
- `verification-matrix.md`: contract IDs, gate mapping, and required evidence.

Two structural chapters extend those contract pages and are part of the live
superscalar-core specification:

- `module-catalog.md`: canonical module families and top-level composition.
- `pipeline-stage-catalog.md`: per-stage design, ownership, and stage-to-module
  mapping.

The remaining files in this directory are implementation deep dives. They may
expand a mechanism, but they must not weaken or redefine the live contract.

## Source-of-truth model

- Canonical LinxCore contract authoring lives in `rtl/LinxCore/docs/architecture/`.
- Published superproject mirrors live in `docs/architecture/linxcore/`.
- `tools/bringup/check_linxcore_arch_contract.py` validates both the canonical
  pages and the generated mirrors.
- Standalone or out-of-superproject trees are development mirrors, not contract
  authority.

## Required closure target

The live closure target for this specification is:

- LinxISA `v0.56` architectural behavior,
- ACR service-request entry/return behavior, including `BI=1` block-state
  restoration,
- MMU and interrupt correctness,
- dual-lane reproducibility (`pin` and `external`),
- strict required-gate closure with evidence artifacts.

Phase labels may still be used operationally, but the specification itself is
gate-driven, not date-driven.

## Non-goals

This overview does not freeze:

- final frequency, area, or power targets,
- future width scaling beyond the current live contract,
- future engine additions not already covered by the LinxISA `v0.56`
  architecture contract,
- historical bring-up strategies that are no longer part of the live behavior.
