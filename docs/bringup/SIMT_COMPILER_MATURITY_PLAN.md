# Linx SIMT Compiler Maturity Plan

Status: Planning page
Last updated: 2026-03-11

This page defines the staged maturity path for the current LLVM-based Linx SIMT
compiler flow.

It is intentionally narrower than the full architecture plan. Its focus is the
current compiler implementation centered on
`compiler/llvm/llvm/lib/Target/LinxISA/LinxISASIMTAutoVectorize.cpp`, plus the
tests and execution evidence required to promote it from a bring-up subset into
a stable SIMT compiler profile.

## Current State

The current flow is functional but conservative:

- it prefers `MSEQ` unless independence is structurally obvious,
- it rejects many non-canonical loop shapes,
- it still uses scalar-lane replay through `LB1` as the main correctness-first
  fallback,
- it handles inner control flow through scalarized “any-active-lane” fallback
  patterns rather than a mature SIMT CFG model.

That is a reasonable bring-up baseline. It is not yet a mature compiler for
branch-heavy, lane-divergent SIMT kernels.

The architecture direction is now frozen in
`docs/architecture/v0.4-simt-compiler-contract.md`: canonical `v0.4` kernels
are group-granular divergent SIMT kernels driven by explicit `p` management.
The remaining work is therefore implementation maturity, not architecture
direction-finding.

## Maturity Objectives

The compiler is mature only when all of these are true:

- it targets a documented SIMT contract rather than private lowering rules,
- grouped-lane lowering has a stable canonical meaning,
- structured inner control flow has a stable lowering strategy,
- lane-local scratch and live-state lowering use a stable ABI,
- `MSEQ` and `MPAR` selection rules are explicit and testable,
- compile-time and runtime gates cover real SIMT kernels, not just simple loop
  bodies.

## Staged Plan

### S0: Freeze The Supported Subset

Goal:

- make the current compiler contract explicit before expanding it.

Work:

- document the current accepted loop subset and reject taxonomy,
- keep remarks stable and machine-readable,
- map every major reject reason to one of:
  - architecture gap,
  - compiler implementation gap,
  - intentionally unsupported canonical shape.

Required evidence:

- lit coverage for stable reject reasons,
- a short public note describing the current supported subset:
  `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`

Exit criteria:

- compiler users can tell whether a rejected loop is “not yet mature” or
  “outside canonical `v0.4`”.

### S1: Make Grouped-Lane Lowering Explicit

Status:

- partially implemented on 2026-03-09
- current landing includes:
  - explicit layout policy selection (`auto`, `scalar-replay`, `grouped`)
  - canonical single-group and strip-mined launch formation for the current
    counted unit-stride subset
  - lit coverage for grouped single-group, grouped strip-mined, and forced
    scalar replay
- still open:
  - dynamic-tripcount grouped lowering
  - grouped lowering beyond the current unit-stride / no-active-replay subset

Goal:

- stop treating grouped replay as a hidden bring-up tactic.

Work:

- align lowering with the frozen launch-geometry contract,
- implement one canonical mapping for:
  - lane count,
  - group count,
  - logical thread index,
  - `lc0/lc1` usage.

Required evidence:

- lit tests for:
  - single-lane replay,
  - grouped replay,
  - explicit strip-mined launch forms,
  - dynamic tripcount grouped lowering.

Exit criteria:

- emitted `LB*` / `lc*` usage is predictable from the written contract.

### S2: Close Structured Inner Control Flow

Status:

- partially implemented on 2026-03-09
- current landing includes:
  - direct compare-to-EXEC lowering (`V.CMP.* ->p`, `V.F* ->p`) for covered
    inner branch conditions
  - direct in-body `b.nz` / `b.z` emission instead of `v.rdor`-based
    any-active-lane branching for those covered cases
  - focused lit coverage for compare-driven inner `if/else` and nested forward
    branch regions
  - compile-path closure for break-to-exit internal branches through the
    scalar-replay active-lane path
  - QEMU runtime closure for direct body-local `p` branches, including nested
    forward branches and escape-fault containment
  - a focused runtime smoke for scalar-replay active-lane break/skip shape:
    `v.rdor ... ->t#1` scalar break gate with per-iteration
    body-store/no-store validation
  - QEMU runtime closure for scalar-replay body-local `j` else-edge/rejoin
    after a direct `->p` split, using an explicit shared rejoin at the body
    terminator
  - QEMU runtime closure for the grouped straight-line split/rejoin shape
    (`LB0>1`, `LB1=1`) using the same direct `->p` split plus body-local `j`
    else-edge and shared body terminator
  - QEMU runtime closure for grouped nested forward-CFG `j` regions with a
    shared rejoin and a common post-join tail, matching the compiler's current
    nested `if/else` lowering style more closely
  - QEMU runtime closure for the grouped straight-line backward-edge loop
    subset, using label-based body-local `j` back to the loop head
  - explicit lit coverage that the simple active-replay boundary-search loop
    now lowers under grouped strip-mined layout, with compiler-materialized
    logical-lane active state
  - QEMU runtime closure for that same compiler-generated grouped
    active-replay boundary-search shape through the dedicated `simt_autovec`
    suite, now built through the normal direct `clang -> object` pipeline
    after wiring SIMT autovec onto the Linx new-PM target callbacks, with a
    compile-phase objdump check that locks the grouped `BSTART.MSEQ/B.TEXT`
    shape instead of accepting scalar fallback
  - QEMU runtime closure for direct-`clang` grouped single-block if-converted
    diamonds and nested diamonds, matching the current standard SIMT
    compiler-style positive case where earlier scalar optimization collapses
    simple split/rejoin CFG into compare/select form before SIMT lowering
  - QEMU/runtime and compile-phase closure for a TSVC-style elemental
    min/select kernel, proving the current grouped single-block path also
    covers a branch-free compare/select source shape beyond the earlier
    diamond-only cases
  - explicit raw-`llc` lit coverage for already-if-converted `select`-SSA
    loops, so the backend-side grouped positive case does not depend only on
    front-end optimizer behavior
  - explicit raw-`llc` lit coverage for a narrow class of nested pure-value
    inner diamonds that the backend can locally if-convert to `v.csel` chains
    without architectural EXEC-mask save/restore
  - explicit raw-`llc` lit coverage for same-address store diamonds lowered as
    `v.csel + one merged store`, while different-address split/rejoin stays on
    the `exec-mask-save-restore-required` side of the boundary
  - explicit raw-`llc` lit coverage for pointer-sink store diamonds, recorded
    as a scalar-replay compile positive until grouped pointer-dispatch
    legality/addressing is promoted further
  - explicit compiler guard that unsupported exit-chain side effects reject as
    `unsupported_exit_side_effects` instead of lowering incorrectly
  - QEMU runtime closure for grouped fixed-tripcount replay with lane-local
    memory-backed active-state continuation, showing the runtime is not blocked
    on this weaker compiler-materialized form
- still open:
  - nested divergent-region mask management
  - partially-active loop continuation and explicit reconvergence discipline
  - grouped/divergent body-local control flow that requires true
    partially-active continuation or reconvergence across lane subsets
  - runtime/QEMU closure for mask-stack-like in-body branch subsets
  - a canonical scalar/group-domain carrier for `p` save/restore is still not
    available in the current assembler-visible `v0.4` surface: plain scalar
    forms only accept 5-bit regs, while canonical parsing rejects legacy
    `l.*` syntax. This blocks first-class architectural EXEC-mask save/restore
    lowering even though the SIMT contract allows it when an encoding exists.
  - existing grouped/nested QEMU runtime greens remain replay-lane evidence;
    they must not be treated as proof that architectural `p` restoration across
    divergent regions is already closed
  - TSVC-style shifted-index subscripts such as `c[i >> 1]` are still outside
    the current grouped positive subset; the direct-`clang` runtime lane is
    now covered, but the emitted object remains scalar rather than grouped
  - compiler policy now explicitly reflects that boundary: raw grouped
    split/rejoin inner CFG that would need architectural EXEC-mask
    save/restore rejects as `grouped_layout_requires_exec_mask_save_restore`
    instead of silently claiming grouped divergent closure
  - grouped positive cases remain limited to boundary-search style active
    replay and to earlier-optimized single-block vector forms; raw multi-block
    inner divergence is still not claimed closed
  - direct `clang -O2` and raw `llc` should therefore not be conflated here:
    the former may reach grouped single-block forms via earlier if-conversion,
    while the latter still exposes the stricter raw split/rejoin boundary
  - SIMT autovec remarks now expose `cf_strategy` so gates can distinguish
    `if-converted-single-block`, `if-converted-diamond`, `active-replay`, and
    `exec-mask-save-restore-required` without re-parsing assembly

Goal:

- support real structured body control flow without compiler-private semantics.

Work:

- replace ad hoc inner-CF fallback with one documented lowering discipline,
- support canonical:
  - if/else,
  - loop-carried early exit,
  - nested branch regions,
  - partially active loop continuation.

Required evidence:

- lit tests for branch-heavy SIMT kernels,
- AVS compile coverage for branch-heavy kernels,
- QEMU runtime kernels that prove the emitted shape executes correctly.

Exit criteria:

- branch-heavy kernels no longer fall back to opaque scalarization patterns
  unless that fallback is itself canonical and documented.

### S3: Freeze Lane-Local Scratch And Live-State Lowering

Goal:

- make compiler-generated `.local` state predictable and portable.

Work:

- adopt the canonical scratch ABI from the architecture plan,
- lower recurrence, exit-phi, active-lane state, and liveouts through one
  consistent state model,
- remove one-off slot conventions where possible.

Required evidence:

- lit tests for spill/reload, recurrence, exit-phi, and lane-private temporaries,
- QEMU runtime tests that use `.local` state under partial lane activity.

Exit criteria:

- compiler-generated `.local` usage can be understood and validated as an ABI,
  not reverse-engineered per test.

### S4: Mature `MSEQ` Versus `MPAR` Legality

Goal:

- make parallel mode selection explicit, safe, and reviewable.

Work:

- separate replay legality from true parallel legality,
- require explicit criteria for `MPAR`:
  - memory independence,
  - supported divergence shape,
  - allowed reduction semantics,
  - absence or containment of unsafe loop-carried state.

Required evidence:

- positive and negative lit tests for `MPAR` admission,
- stable remarks showing why a loop stayed `MSEQ` or was promoted to `MPAR`.

Exit criteria:

- `MPAR` is never selected by accident or by undocumented structural quirks.

### S5: Add Real SIMT Maturity Gates

Goal:

- validate the compiler against realistic kernels and execution evidence.

Work:

- add a dedicated SIMT kernel compile suite,
- add QEMU runtime kernels shaped like:
  - probe loops,
  - masked gather/scatter,
  - nested branches,
  - partial-lane completion,
  - launch strip-mining cases.

Required evidence:

- compile gate artifacts,
- runtime gate artifacts,
- remark artifacts for acceptance and rejection paths.

Exit criteria:

- SIMT maturity is measured by dedicated gates, not inferred indirectly from
  scalar/vector bring-up health.

## Dependency Rules

This maturity plan depends on the architecture plan in
`docs/architecture/v0.4-simt-compiler-contract-plan.md`.

Compiler implementation must stop and escalate if it reaches any of these
unfrozen questions:

- launch geometry meaning is still ambiguous,
- divergence/reconvergence semantics are not frozen,
- scratch ABI is not frozen,
- body-branch semantics are not frozen.

Those are architecture decisions, not backend-local decisions.

## Required Test Expansion

The following test layers should exist by the end of this plan:

- LLVM lit tests for header formation, `LB*` layout, branch lowering, scratch
  ABI use, and `MSEQ/MPAR` legality.
- AVS compile tests for representative SIMT kernels.
- QEMU runtime tests for grouped lanes, masked progress, and partial-lane exit.
- cross-check assembly snapshots for canonical kernel shapes.

## Relationship To Existing Maturity Plan

This page refines the SIMT/compiler portion of the broader bring-up maturity
track in `docs/bringup/MATURITY_PLAN.md`.

It does not replace the broader plan. It adds the missing depth for the `VEC`
and SIMT compiler lane so that future maturity work is not limited to generic
AVS and opcode-count growth.
