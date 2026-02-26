# v0.4 draft: SIMT kernel body control flow (group-granular)

## Context

In v0.3 strict, *decoupled bodies* are specified as **linear snippets** and MUST NOT contain any architectural control transfer instructions.

For rendering/GPGPU, we want to treat a vector block launch (e.g. `BSTART.MPAR` + descriptors) as launching a small **kernel** whose code is the body referenced by `B.TEXT`.

The kernel body must allow **full structured control flow** (if/else/loops), but control flow is evaluated at **group (warp) granularity** using the scalar-uniform lane.

## Proposed model (draft)

### A) Body is a kernel (not a linear snippet)
- `B.TEXT` selects a kernel entrypoint.
- The kernel body is a normal instruction stream (may contain branches/jumps), executed under the vector-block replay model.

### B) Control-flow granularity
- Branch/jump instructions (`B.*`, `J`, `JR`, etc.) are executed by the **scalar-uniform lane context**.
- A group maintains a **group PC** (TPC) and executes one control-flow path at a time.
- Vector lanes execute lane operations under a **lane mask** (64-bit) maintained by the kernel/runtime/compiler.

### C) Lane mask / inactive-lane behavior
- The lane mask defines which lanes are active for vector operations.
- Inactive lane behavior must be deterministic and compatible with the architectural inactive-lane policy (merge vs zero).
- The kernel/compiler is responsible for updating the lane mask around divergent regions.

Draft anchoring in existing v0.3 conventions:
- v0.3 semantics conventions already define a **vec-engine scalar-lane predicate register** named `p`, with `B.Z/B.NZ` testing `p==0` / `p!=0`.
- In v0.4, we reuse `p` as the **group EXEC mask (64-bit)**.

Draft access rule (chosen direction):
- `p` is treated as a scalar-lane 64-bit register that can be used as a **normal source/destination** in scalar-lane instructions inside the kernel body (i.e. allow `->p` destinations and `p` as an operand in scalar-lane ALU/bitwise/compare as needed).

Draft execution rule (chosen direction):
- `p` is the **EXEC mask**: for each vector instruction, lane `i` is active iff `p[i] == 1`.
- For inactive lanes, destination writeback behavior follows the architected inactive-lane policy (**merge** vs **zero**).

### D) Containment and safety
To preserve CFI and avoid arbitrary jumps:
- The kernel text region is **implicitly bounded** by terminator markers.
  - The body is considered fetchable/executable starting at `B.TEXT` entry.
  - The kernel ends on the **first terminator marker encountered** in the body stream.
  - Terminators: `BSTOP`/`C.BSTOP` and any `BSTART.*`/`C.BSTART.*` (first terminator wins; anything after is unreachable).
- In-body control-flow targets (branches/jumps) MUST NOT escape the body’s fetchable region; escaping targets fault as body-fetch faults (consistent with existing vec-engine BRU conventions).
- No architectural control flow may jump **into** the middle of a kernel from outside (same as v0.3 `B.TEXT` rule).
- Kernel returns to the header continuation point by reaching the terminator.

### E) Calls (optional)
- v0.4 may still prohibit call/return inside kernel bodies initially (to simplify bring-up), even if branches are allowed.

## Open questions
1) How do we **declare the kernel text region** (start/end) for containment checks?
   - chosen direction: **terminator markers** (first `BSTOP/C.BSTOP` or any `BSTART.*` ends the kernel)
   - (defer) fixed-size in descriptor?
   - (defer) side-table metadata in driver/runtime?

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
   - inactive lane rule (chosen): when executing `V.CMP.* ->p`, any lane that is inactive under the current EXEC mask is treated as producing **0** (bit cleared).

5) Interaction with `MPAR/MSEQ` retirement ordering and traps/restartability.

