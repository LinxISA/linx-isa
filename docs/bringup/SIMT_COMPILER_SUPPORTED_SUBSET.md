# Linx SIMT Compiler Supported Subset

Last updated: 2026-03-11

This page documents the **current implemented subset** of the LLVM Linx SIMT
lowering centered on
`compiler/llvm/llvm/lib/Target/LinxISA/LinxISASIMTAutoVectorize.cpp`.

It is an implementation-status page, not the architectural contract. The live
architecture direction is defined by
`docs/architecture/v0.4-simt-compiler-contract.md`.

## Purpose

This page answers two practical questions:

- which loop shapes the current pass is actually prepared to lower,
- how to interpret the current reject reasons emitted in SIMT autovec remarks.

It exists so users do not have to reverse-engineer backend behavior from
assembly or from the pass source.

The JSON remarks now also expose a compiler-facing control-flow classification
field, `cf_strategy`, so standard SIMT lowering techniques can be tracked
without inferring them from assembly alone. The current values in active use
are:

- `if-converted-single-block`: simple diamonds or nested diamonds collapsed
  into compare/select form before SIMT lowering
- `if-converted-diamond`: raw nested pure-value inner diamond regions that the
  backend can locally collapse into compare/select form without architectural
  `p` save/restore
- `active-replay`: replay-driven continued progress using compiler-materialized
  lane state instead of first-class EXEC-mask restoration
- `exec-mask-save-restore-required`: grouped split/rejoin would require
  architectural `p` save/restore, so grouped lowering is not claimed closed

## Current Lowering Posture

The current pass is still a correctness-first bring-up implementation.

Its default posture is:

- prefer `MSEQ` unless independence is structurally obvious,
- keep the accepted loop subset narrow,
- prefer canonical grouped layout for counted, unit-stride loops with a static
  divisible tripcount,
- fall back to scalar-lane replay through `LB1` when grouped layout is not yet
  safe or not yet implemented,
- scalarize difficult inner control flow through an `any-active-lane` fallback
  rather than a mature divergent-SIMT lowering.

This means the pass is currently best understood as:

- a usable SIMT kernel generator for a narrow canonical loop subset,
- plus an experimental bridge toward the newly frozen divergent `v0.4` SIMT
  contract.

## Current Accepted Loop Shape

The current pass is intended for loops with these properties:

- innermost loop only,
- loop-simplify form with stable preheader/header/latch structure,
- no unsupported calls,
- no Linx tile/CUBE/TEPL intrinsic loop bodies,
- tripcount expressible through the current ScalarEvolution-based expansion,
- affine-enough memory/indexing for the lowering path in use,
- at least one meaningful loop-side effect:
  - store, or
  - supported recurrence/reduction/liveout path, or
  - active-replay-driven exit behavior.

The strongest current success case is:

- counted innermost loops,
- simple affine loads/stores,
- no unsupported inner CFG,
- no complicated pointer-phi or liveout shapes,
- no volatile/atomic memory.

## Current Mode Policy

The pass currently exposes three policy modes:

- `mseq`: always choose `MSEQ`
- `mpar-safe`: allow `MPAR` when the loop looks dependence-safe
- `auto`: correctness-first default; prefer `MSEQ` unless the loop is
  structurally independent

In practice today:

- `MSEQ` is the stable default for complex loops,
- `MPAR` is currently realistic only for simple, store-free or obviously safe
  loops,
- many branch-heavy or state-heavy kernels are still lowered through replay-like
  grouped execution rather than a mature divergent-SIMT strategy.

The pass also now exposes an explicit layout policy:

- `auto`: prefer canonical grouped layout when the current implementation can
  prove a safe static mapping
- `scalar-replay`: force the conservative `LB0=1`, `LB1=tripcount` replay path
- `grouped`: require canonical grouped lowering and reject the loop if the
  current implementation cannot satisfy it

## Current Grouped-Replay Fallback

The current implementation still relies heavily on grouped replay for
correctness:

- `LB1` is still the main replay/group dimension in the conservative path,
- scalar replay is still used for dynamic tripcounts, active-replay loops, and
  memory shapes outside the current grouped subset,
- grouped lanes now have an explicit canonical lowering path:
  - single-group: `LB0=tripcount`, `LB1=1`
  - strip-mined: `LB0=lanes-per-group`, `LB1=group-count`
- the logical thread index remains `lc0 + lc1 * LB0` when the grouped layout
  uses more than one group.

This is implementation status, not the final intended `v0.4` SIMT contract.

## Current Inner Control-Flow Behavior

The pass can now emit the first canonical branch-on-`p` form for structured
inner control flow:

- vector compare-driven branch conditions may lower as `V.CMP.* ->p` or
  `V.F* ->p`,
- branch transfer may then lower directly as in-body `b.nz` / `b.z`,
- this removes the old `v.rdor ... ->t#1` “any-active-lane” bridge for the
  covered compare-driven cases,
- covered acyclic inner CFG now includes single-level and nested forward
  compare-driven branches with direct body-local labels.
- break-to-exit internal branches are classified as inner CFG and lower through
  the scalar-replay active-lane path instead of being treated as plain latch
  exits.

What is still not mature:

- full mask save/restore discipline across nested divergent regions,
- general partially-active loop continuation and reconvergence,
- runtime closure beyond the current forward-only nested branch subset.

Current runtime evidence now covers one additional scalar-replay active-lane
shape:

- a body-local `v.rdor ... ->t#1` bridge feeding a scalar `b.ne`,
- with one lane set proving the body executes and writes the replay body result
  when the reduced condition does not fire,
- and a second lane set proving the scalar break/skip path suppresses the
  current scalar-replay iteration's body store when the reduced condition
  fires.
- a scalar-replay `if/else` body shape using direct `->p` branch transfer plus
  body-local `j` else-edge/rejoin, with per-iteration result checks proving
  both the taken true path and the jumped false path return to the shared body
  terminator correctly.
- a grouped `if/else` body shape (`LB0=4`, `LB1=1`) using the same direct
  `->p` split plus body-local `j` else-edge/rejoin, with per-lane result
  checks proving the current replay model also closes the grouped straight-line
  split/rejoin case.
- a grouped nested `if/else` body shape with multiple body-local `j` edges,
  a shared rejoin, and a common post-join tail store, proving the current
  replay model also closes straight-line grouped continued progress after the
  first split/rejoin.
- a grouped backward-edge body loop with label-based `j` back to the loop head,
  proving the current replay model also closes straight-line grouped
  backward-edge progress when each lane can complete independently.
- a grouped fixed-tripcount replay body with lane-local memory-backed active
  state, proving the current runtime can carry per-lane continued progress when
  the compiler/materialization explicitly stores that state outside `p`.

Direct `->p` branch transfer remains covered by the existing dedicated
`v0.3 MSEQ body b.nz/b.z on p` and nested-branch runtime regressions.

The compiler-side boundary has moved as well: simple active-replay loops with a
derived max tripcount and unit-stride memory now lower under grouped layout,
with the active bit materialized as logical-lane state in compiler scratch.
This is covered in lit by `search_store_index_grouped_boundary`, which now
lowers as grouped strip-mined `LB0=32, LB1=2` instead of falling back to scalar
replay.

That compiler shape is also runtime-covered now through the dedicated
`simt_autovec` QEMU suite, built through the normal direct `clang -> object`
pipeline. Its compile phase now also checks the emitted object shape directly
for `BSTART.MSEQ`, `B.TEXT`, grouped `LB0/LB1`, `.brg` memory ops, and body
local `p`-branch/jump control flow. The guarded positive cases are:

- grouped active-replay search with a hit in the first strip-mined group,
- grouped active-replay search with a hit in the tail group,
- grouped active-replay miss returning `-1`,
- direct-`clang` grouped single-block inner-diamond if-conversion lowering,
  materialized as `V.FLT` plus `V.CSEL`,
- direct-`clang` grouped single-block nested-diamond if-conversion lowering,
  materialized as compare/select chains without body-local split/rejoin CFG.
- direct-`clang` grouped same-address store-diamond lowering, validated at
  runtime from branch-store source shape rather than only from pre-if-converted
  value SSA.
- direct-`clang` grouped TSVC-style elemental min/select store lowering,
  validated at runtime and compile phase from a branch-free `min(a[i], b[i])`
  source shape that lands as grouped `v.flt + v.csel + v.sw.brg`.
- compiler-lit coverage now also locks the TSVC split explicitly:
  `vector_min_select_store` is a grouped `if-converted-single-block` positive,
  while `vector_shift_half_index` remains an explicit scalar/reject boundary
  (`non_float_store_value`) rather than a grouped positive.
- an additional TSVC-style affine positive is now locked as well:
  constant shifted-output stores (`a[i + 32] = a[i] + b[i]`) lower as
  `grouped-single-group`, while stride-controlled loops (`i += inc`) remain
  scalar-replay rather than entering the grouped subset.
- the dynamic-offset variant (`a[i + M] = a[i] + b[i]`) is also now locked as
  scalar-replay: it stays within the vblock path, but with lane-count `1`
  rather than grouped launch geometry.
- TSVC-style control-flow kernels are now split more explicitly as well:
  a simple masked update of the current destination value is still rejected as
  `unsupported_value_expr:select`, while nested dual-update/dual-store control
  flow lands on the `exec-mask-save-restore-required` side of the boundary.
- more TSVC control-flow detail is now locked too: independent-condition
  dual-store kernels and dependent-condition dual-update kernels both remain on
  the `unsupported_value_expr:select` boundary. In other words, current grouped
  single-block if-conversion handles one selected result well, but not a
  multi-result masked update pack.

Those extra positives line up with a standard SIMT compiler technique: when
earlier scalar optimization can if-convert a simple diamond into predicate and
select form, the grouped kernel can stay within the current canonical `v0.4`
body contract (`BSTART.MSEQ`, `B.TEXT`, grouped `LB0/LB1`, vector compare, and
select) without needing first-class EXEC-mask save/restore or split/rejoin
reconvergence.

That positive lane is now covered in both ways:

- direct `clang -O2` on branchy source that earlier scalar passes if-convert,
- raw `llc` on already-if-converted `select`-SSA IR, which is the backend-side
  canonical proof for the standard SIMT if-conversion technique.
- raw `llc` on a narrow class of nested structured inner diamond regions whose
  side blocks are pure speculative value producers and whose intermediate
  bridges are PHI-only merge blocks; the backend now locally if-converts that
  shape into `v.csel` chains and reports it as
  `cf_strategy = if-converted-diamond`.
- raw `llc` on a narrow class of same-address store diamonds; when both sides
  only compute a value and store to the same lane-varying destination, the
  backend now locally rewrites that shape to `v.csel` plus one merged store,
  rather than treating it as a true EXEC-mask reconvergence problem.
- raw `llc` on pointer-sink diamonds where the value path is locally
  if-converted but the final store still dispatches through the existing
  pointer-PHI sink mechanism; this is currently compiler-covered as a
  scalar-replay positive, not a grouped positive.
- direct `clang` on a TSVC-style shifted-half-index address pattern
  (`a[i] = b[i] + c[i >> 1]`) currently remains a scalar boundary case: it is
  runtime-covered in `simt_autovec`, but the emitted object is still a scalar
  counted loop rather than a grouped `BSTART.MSEQ/B.TEXT` body.

One additional compiler boundary is now explicit: exit-chain side effects such
as `store *out = i` in the break block are rejected with
`unsupported_exit_side_effects` instead of being silently dropped.

The earlier two-stage `clang -emit-llvm` plus `llc` workaround is no longer
needed: the Linx target now registers SIMT autovec on the new pass-manager
`clang` pipeline, and the direct `clang -> object` path emits the same grouped
`BSTART.MSEQ/B.TEXT` shape as the `llc` lane for this function class.

What is still not claimed closed here:

- grouped/divergent body-local control flow that requires true partially-active
  continuation or reconvergence through architectural mask discipline rather
  than compiler-materialized logical-lane memory state,
- mask save/restore or mask-stack-like nested reconvergence behavior,
- backward-edge in-body control-flow that depends on divergent lane-subset
  continuation rather than per-lane replay.

One concrete blocker is now pinned down at the ISA/encoding boundary. The
canonical SIMT docs allow compiler/runtime save/restore of `p` when the operand
encoding permits it, but the current canonical toolchain surface has no usable
carrier for that operation:

- plain scalar `add p, zero, ->t` / `add t, zero, ->p` fails because the
  scalar form only carries 5-bit register fields,
- canonical `v0.4` parsing rejects `l.add ...` legacy syntax,
- so there is currently no accepted canonical asm shape for group-domain
  `p` save/restore through a scalar carrier.

This is now locked by the MC regression
`compiler/llvm/llvm/test/MC/LinxISA/simt-p-save-restore-gap.s`.

Related runtime caveat: the current grouped/nested QEMU regressions in
`v03_vector` are still evidence for the replay-oriented execution lane, not for
full architectural EXEC-mask restoration. Those tests exercise grouped body CFG
under the current replay model, but they do not prove a first-class
save/restore carrier for `p` or true subset-mask reconvergence.

The compiler now treats raw multi-block inner-CFG as a hard grouped-layout
boundary unless earlier optimization has already collapsed that region into a
single-block vector form (for example `v.csel` on a compare result). In the
current compiler surface:

- grouped fixed-tripcount active-replay search/boundary loops remain supported,
- optimizer-if-converted single-block inner conditionals may still lower as
  grouped vector bodies,
- a narrow raw nested inner-diamond subset may also lower as grouped vector
  bodies when side regions are side-effect-free speculative value producers
  and intermediate bridge blocks are PHI-only merges,
- a narrow same-address store-diamond subset may also lower as grouped vector
  bodies when both arms only differ in the stored value and the store address
  expression is the same on both sides,
- in practice this means direct `clang -O2` can still produce grouped
  single-block SIMT bodies for simple diamonds after scalar/CFG optimization,
  while raw multi-block `llc` IR only escapes the stricter split/rejoin
  boundary for that local-if-conversion subset,
- but raw in-loop split/rejoin CFG that would need first-class EXEC-mask
  save/restore falls back to scalar replay in `auto`, and forced `grouped`
  rejects with `grouped_layout_requires_exec_mask_save_restore`.
- different-address store split/rejoin regions remain on the reject side of
  that boundary; they are not locally if-converted and still require a real
  architectural EXEC-mask save/restore story.

This grouped rejection boundary is locked by
`compiler/llvm/llvm/test/CodeGen/LinxISA/autovec_grouped_exec_mask_save_restore_reject.ll`.

## Reject Taxonomy

The current reject reasons are grouped below by intent.

### Structural Preconditions

These mean the loop shape is outside the basic entry requirements of the pass:

- `function_already_lowered`
- `not_innermost_loop`
- `not_loop_simplify`
- `missing_preheader_or_header`
- `preheader_not_simple_branch`
- `missing_loop_latch`
- `no_exit_block`
- `no_unique_exit`
- `missing_terminator`

Interpretation:

- the pass expects a stable canonical loop CFG before it can even start SIMT
  lowering.

### Unsupported Semantic Content

These mean the loop contains constructs intentionally excluded from the current
implementation:

- `contains_call`
- `linx_tile_intrinsic_loop`
- `volatile_or_atomic_load`
- `volatile_or_atomic_store`

Interpretation:

- these are outside the current generic SIMT autovec slice and should not be
  treated as accidental regressions.

### Tripcount And Canonicalization Failures

These mean the pass could not derive a usable tripcount or induction model:

- `no_tripcount_expr`
- `tripcount_expand_failed`
- `tripcount_non_integer`
- `grouped_layout_requires_static_tripcount`

Interpretation:

- the loop may still be legal under the architecture contract, but the current
  implementation cannot lower it yet.

### Side-Effect / Progress Requirements

These mean the loop body does not match the current definition of “worth
lowering” or “safely lowerable”:

- `no_store_in_loop`

Interpretation:

- this is an implementation filter, not a statement that pure compute loops are
  architecturally invalid.

### Branch And Terminator Limits

These mean the pass hit control-flow forms it cannot yet lower cleanly:

- `unsupported_branch_condition`
- `unsupported_branch_fcmp_condition`
- `unsupported_branch_i1_condition`
- `unsupported_branch_predicate`
- `unsupported_terminator`
- `unsupported_switch_condition`
- `unsupported_switch_case`
- `unsupported_inner_backedge`
- `unsupported_inner_cycle`

Interpretation:

- these are the main current blockers for branch-heavy divergent kernels.

### Store / Addressing Limits

These mean memory lowering could not keep the current affine/supported form:

- `non_affine_store_address`
- `unsupported_store_stride`
- `non_float_store_value`
- `grouped_layout_requires_unit_stride_memory`

Interpretation:

- these are current implementation limits in memory-form selection and address
  reconstruction.

### Layout-Policy Limits

These mean the chosen launch layout policy could not be satisfied:

- `grouped_layout_requires_masked_lane_state`
- `grouped_layout_unavailable`

Interpretation:

- these are not generic loop-shape failures; they are explicit signals that the
  loop fell outside the currently implemented canonical grouped subset.

### PHI / Liveout / Pointer-PHI Limits

These mean state carried across edges or out of the loop exceeded the current
lowering model:

- `value_live_out_unsupported_type`
- `unsupported_liveout_value`
- `liveout_bind_exhausted`
- `liveout_store_emit_failed`
- `invalid_exit_phi_plan`
- `exit_phi_bind_exhausted`
- `exit_phi_init_not_dominating`
- `exit_phi_no_init_incoming`
- `exit_phi_store_emit_failed`
- `exit_phi_unsupported_type`
- `exit_phi_value_emit_failed`
- `invalid_phi_edge`
- `missing_phi_incoming`
- `missing_phi_reg`
- `unsupported_inner_phi_type`
- `invalid_ptr_phi_plan`
- `missing_ptr_phi_edge`
- `missing_ptr_phi_plan`
- `ptr_phi_bind_exhausted`
- `ptr_phi_sel_emit_failed`
- `unsupported_ptr_phi_incoming`
- `unsupported_ptr_phi_store_gep`
- `unsupported_ptr_phi_store_index`
- `unsupported_ptr_phi_variant_incoming`
- `phi_incoming_addrec_emit_failed`
- `phi_incoming_emit_failed`

Interpretation:

- these are state-model maturity gaps, not ISA conflicts.

### Recurrence And Induction Limits

These mean loop-carried state exists but the current implementation could not
represent it safely:

- `invalid_recurrence_init`
- `invalid_recurrence_init_cast`
- `invalid_recurrence_liveout_cast`
- `invalid_recurrence_plan`
- `invalid_recurrence_slot_type`
- `recurrence_bind_exhausted`
- `recurrence_store_emit_failed`
- `recurrence_update_not_emitted`
- `invalid_f32_induction_plan`
- `f32_induction_not_emitted`
- `f32_induction_step_emit_failed`
- `f32_induction_store_emit_failed`

Interpretation:

- these are central to the next maturity slice for lane-local live state.

### Reduction And Resource Limits

These mean the loop hit finite implementation limits rather than semantic
ambiguity:

- `too_many_reductions`
- `unsupported_reduction_value`
- `reduction_bind_exhausted`
- `vector_reg_exhausted`
- `active_bind_exhausted`

Interpretation:

- these are backend resource/model limits that should shrink over time.

### Emission / Internal Lowering Failures

These mean the pass conceptually accepted the loop shape but failed while
materializing the lowering:

- `active_cond_emit_failed`
- `active_load_failed`
- `active_store_emit_failed`

Interpretation:

- these should generally be treated as compiler bugs, not unsupported user code
  shapes.

## How To Read The Remarks

The pass already emits machine-readable remarks including:

- `status`
- `reason`
- selected mode
- `lane_count`
- `group_count`
- `force_scalar_lane`
- recurrence / memory / tripcount metadata

Recommended interpretation:

- `reject` + structural or semantic-content reason:
  loop is outside the current supported subset.
- `reject` + state-model or control-flow reason:
  loop is a maturity gap candidate.
- `reject` + emit-failed reason:
  likely compiler bug or incomplete lowering path.

## Current “Supported” Means

For now, a kernel should be considered within the supported subset when it:

- lowers without a reject remark,
- produces a stable `MSEQ` or explicitly justified `MPAR` header,
- does not rely on undocumented scratch/layout conventions beyond the current
  emitted address expressions,
- runs correctly in the corresponding QEMU/runtime lane when such a gate
  exists.

## Relationship To Other Pages

- Architecture contract:
  `docs/architecture/v0.4-simt-compiler-contract.md`
- Architecture planning:
  `docs/architecture/v0.4-simt-compiler-contract-plan.md`
- Compiler maturity roadmap:
  `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

This page should be updated whenever the pass support boundary changes in a way
that users or downstream validation must understand.
