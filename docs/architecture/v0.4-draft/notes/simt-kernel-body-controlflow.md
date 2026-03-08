# v0.4 draft: SIMT kernel body control flow (group-granular)

## Context

In v0.3 strict, *decoupled bodies* are specified as **linear snippets** and MUST NOT contain any architectural control transfer instructions.

We want to treat a vector block launch (e.g. `BSTART.MPAR` / `BSTART.VPAR` + descriptors) as launching a **kernel** whose code is the body referenced by `B.TEXT`.

The kernel body must allow **structured control flow** (if/else/loops), but control flow is evaluated at **group granularity** using the scalar-uniform lane.

## Proposed model (draft)

### A) Body is a kernel (not a linear snippet)
- `B.TEXT` selects a kernel entrypoint.
- The kernel body is a normal instruction stream (may contain branches/jumps), executed under the vector-block replay model.

### B) Control-flow granularity
- Direct branch/jump instructions (`B.*`, `J`, etc.) are executed by the **scalar-uniform lane context**.
- Indirect jump (`JR`) is not part of the canonical kernel-body control-flow subset in the current bring-up contract.
- A group maintains a **group PC** (TPC) and executes one control-flow path at a time.
- Vector lanes execute lane operations under a **lane mask** (64-bit) maintained by the kernel/runtime/compiler.

### C) Lane mask / inactive-lane behavior
- The lane mask defines which lanes are active for vector operations.
- Inactive lane behavior must be deterministic and compatible with the architectural inactive-lane policy (merge vs zero).
- The kernel/compiler is responsible for updating the lane mask around divergent regions.

Draft anchoring in existing v0.3 conventions:
- v0.3 semantics conventions already define a **vec-engine scalar-lane predicate register** named `p`, with `B.Z/B.NZ` testing `p==0` / `p!=0`.
- In v0.4, we reuse `p` as the **group EXEC mask (64-bit)**.
- Kernel bodies keep this distinct from ordinary scalar conditional branching: explicit-operand scalar branch forms (`B.EQ/B.NE/B.LT/B.GE/...`) remain available for scalar control flow, while `B.Z/B.NZ` are reserved for explicit EXEC-mask tests.
- `SETC.*` / `C.SETC.*` are not part of the canonical kernel-body control-flow subset in the current bring-up contract.

Draft access rule (chosen direction):
- `p` is treated as a scalar-lane 64-bit register that can be used as a **normal source/destination** in scalar-lane instructions inside the kernel body (i.e. allow `->p` destinations and `p` as an operand in scalar-lane ALU/bitwise/compare as needed).

Draft execution rule (chosen direction):
- `p` is the **EXEC mask**: for each vector instruction, lane `i` is active iff `p[i] == 1`.
- For inactive lanes, destination writeback behavior follows the architected inactive-lane policy (**merge** vs **zero**).

### D) Entry and termination model
- `B.TEXT` provides the kernel entrypoint.
- The kernel is **not modeled as a separately declared static code region**.
- Kernel execution ends when dynamic execution reaches a terminator marker.
  - Terminators: `BSTOP`/`C.BSTOP` and any `BSTART.*`/`C.BSTART.*` (first one actually reached by execution ends the kernel).
  - If a `BSTART.*` is reached during body execution, it acts only as an implicit terminator for the current kernel; it is not executed as a nested block start.
  - Explicit direct branch/jump to `BSTOP`/`C.BSTOP` is also legal and serves as a normal early-exit path.
  - Explicit direct branch/jump to such a `BSTART.*` target is also legal and serves as an early-exit path with the same effect.
  - Falling through or fetching past valid body code without first reaching a terminator is malformed and faults as a body-fetch error rather than terminating implicitly.
- No architectural control flow may jump **into** a `B.TEXT` entry from outside; `B.TEXT` remains an engine-internal entrypoint under the existing v0.3-style safety rule.
- After reaching a terminator, execution returns to the header continuation point.
- Self-loops and other non-terminating control-flow patterns are architecturally legal; if no terminator is ever reached, the kernel simply does not return.

### E) Calls
- To keep the instruction definition unchanged and avoid introducing extra kernel-internal entry markers, v0.4 kernel bodies do **not** support in-body call/return in the current bring-up contract.
- Kernel-internal function calls are deferred/reserved for a later revision.

## Open questions
1) Do we declare a kernel text region (start/end) for containment checks?
   - chosen direction: **no separate kernel-region abstraction in the base v0.4 contract**.
   - `B.TEXT` names the entrypoint only.
   - Kernel completion is defined dynamically by reaching `BSTOP/C.BSTOP` or any `BSTART.*`/`C.BSTART.*` during execution.
   - No explicit size descriptor or side-table metadata is required.

2) How is the **lane mask** represented architecturally?
   - reuse vec-engine scalar-lane predicate register `p` as EXEC (preferred by current direction)
   - implicit (microarchitectural) with compiler conventions
   - explicit SSR or dedicated register file

3) If we reuse `p` as EXEC: what are the **read/write mechanisms**?
   - allow scalar ALU ops to write `->p` (destination form)
   - or add explicit `PSET/PGET` ops
   - or model `p` as an SSR (SSRGET/SSRSET)

4) How do we set `p` from per-lane conditions?
   - chosen direction: allow **vector compare instructions** to write an EXEC mask: `V.CMP.* ->p`
   - this is the normative vector-lane mask-generation rule, but scalar-uniform kernel instructions may also read/write `p` directly.
   - inactive lane rule (chosen): when executing `V.CMP.* ->p`, any lane that is inactive under the current EXEC mask is treated as producing **0** (bit cleared).

5) Interaction with `MPAR/MSEQ` retirement ordering and traps/restartability.

