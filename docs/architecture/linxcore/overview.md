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

## Core definition

LinxCore is a block-ordered heterogeneous superscalar core.

Its defining properties are:

- superscalar frontend, dispatch, issue, and commit behavior,
- out-of-order execution with precise architectural retirement,
- block-structured control flow with `BSTART` and `BSTOP` as architectural
  boundary markers,
- BID-ordered block tracking through `BROB` and block-engine paths,
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
- `TMA` remains selected through the same block model, but its memory transport
  is owned by the CSU subsystem rather than by a peer top-level engine shell.
- `CUBE` and `TAU` remain integrated engines selected through the same block
  model.
- Engine-backed work must retire, cancel, redirect, and trace through LinxCore
  rules rather than through a separate architectural domain.

This composition rule is required for consistency with:

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-command-contract.md`

## Current architecture closure slice

The current architecture-writing pass covers the promoted frontend/decode,
post-rename dispatch, and baseline issue/wakeup slice from `IFU/F0` through
`W1`.

Stage lineup in this pass:

- `F0`: PC-select stage; chooses the next fetch PC from multiple candidate PCs
  and presents a registered `F0 -> F1` boundary.
- `F1`: I-cache lookup stage; architecture-facing control remains per-thread,
  while the current physical implementation arbitrates a single I-cache read
  port across threads.
- `F2`: I-cache data staging and ECC check; forwards only ECC-clean raw cache
  data and thread/PC context.
- `F3`: variable-length stitch/assembly, static prediction, block-boundary
  annotation, and template recognition/expansion control.
- `IB`: per-thread instruction-buffer banks feeding aligned decode groups.
- `F4`: 4-slot decode window generation with continuous per-slot 64-bit view.
- `D1`: decode, contiguous-group formation, and `RID/BID/LSID` allocation.
- `D2`: rename request/translation stage and ROB-visible boundary resolution.
- `D3`: renamed-uop latch point.
- `S1`: post-rename dispatch preparation (routing and ready query).
- `S2`: actual IQ entry write.
- `P1`: IQ pick stage.
- `I1`: operand-read planning and RF read-port arbitration.
- `I2`: issue-confirm and IQ deallocation boundary.
- `E1`: first execute stage.
- `W1`: baseline late wakeup and resolve stage.

This pass is intentionally focused on architectural stage ownership and
interface shape. More detailed unit-internal execute/bypass topologies and full
commit machinery remain governed by the broader contracts in the canonical
microarchitecture page until later slices are promoted in the same style.

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
- Standalone trees such as `/Users/zhoubot/LinxCore` are development mirrors,
  not contract authority.

## Required closure target

The live closure target for this specification is:

- LinxISA `v0.56` architectural behavior,
- U + S privilege behavior,
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
