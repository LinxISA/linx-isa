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

### D) Containment and safety
To preserve CFI and avoid arbitrary jumps:
- All control-flow targets inside a kernel body MUST remain within the kernel’s declared text region.
- No architectural control flow may jump **into** the middle of a kernel from outside (same as v0.3 `B.TEXT` rule).
- Kernel returns to the header continuation point via a dedicated termination mechanism (e.g. `BSTOP`/`C.BSTOP` or a v0.4-defined `KSTOP`).

### E) Calls (optional)
- v0.4 may still prohibit call/return inside kernel bodies initially (to simplify bring-up), even if branches are allowed.

## Open questions
1) How do we **declare the kernel text region** (start/end) for containment checks?
   - fixed-size in descriptor?
   - terminator scanning?
   - side-table metadata in driver/runtime?

2) How is the **lane mask** represented architecturally?
   - implicit (microarchitectural) with compiler conventions?
   - explicit register/SSR?

3) Interaction with `MPAR/MSEQ` retirement ordering and traps/restartability.

