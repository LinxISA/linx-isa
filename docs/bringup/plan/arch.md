# LinxISA v0.3 — Architecture Features & Constraints Checklist (Bring-up)

This document is a **bring-up checklist** for the *architectural* features and hard constraints that implementations (LLVM/QEMU/RTL/Linux/libc) must satisfy for LinxISA **v0.3**.

It is intended to be **precise and test-aligned**. The authoritative contract is `docs/architecture/v0.3-architecture-contract.md`, and the normative conformance gate is `check26` (`docs/bringup/check26_contract.yaml`).

## Scope / Canonical Inputs

- ISA profile: **v0.3 only**
- Canonical compiled catalog: `isa/v0.3/linxisa-v0.3.json`
- Canonical “golden” sources: `isa/v0.3/`
- Manual chapters referenced by the check26 contract:
  - `docs/architecture/isa-manual/src/chapters/02_programming_model.adoc`
  - `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`
  - `docs/architecture/isa-manual/src/chapters/08_memory_operations.adoc`
  - `docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc`

## How to Use This

- Treat each checkbox as a **must-hold invariant** for any bring-up milestone claiming “v0.3 architectural compliance”.
- For each item, record:
  - **Evidence** (test name + log path, waveform, trace, or diff)
  - **Owner** (domain / person)
  - **Status** (pass/fail/waived + justification)

---

## A. ISA Model: Block-Structured Execution (Non-Negotiable)

- [ ] **Block-structured ISA**: execution is fundamentally block-based. Blocks are **initiated and committed** via **block start/stop markers**.
  - Notes:
    - `BSTART.*` / `BSTOP` are treated as **markers** for block init/commit (not “normal” in-block payload instructions).
    - The contract statement “no architectural instructions outside blocks” is interpreted here as: **there must be no instructions that modify architectural state outside block execution** (boundary markers/descriptors are allowed to exist as a control/packaging mechanism).
- [ ] **Two-layer architectural state model** exists and is respected:
  - [ ] **GSTATE** (first-layer, global architectural state)
  - [ ] **BSTATE** (second-layer, per-block local architectural state)
- [ ] **All computation is in blocks**:
  - [ ] There are **no architectural state-modifying payload instructions** outside block execution.
  - [ ] **Empty blocks are legal.** For bring-up, treat the following as valid “empty block” scenarios (i.e., no architecturally meaningful payload work beyond boundary/control mechanics):
  - [ ] Coupled form with header descriptors only and no body payload ops.
  - [ ] Coupled form where the block end is the implicit boundary at the next block start marker (no explicit `BSTOP`).
  - [ ] Decoupled form using `B.TEXT` where the referenced body is empty.
  - [ ] Template marker blocks (`FENTRY`/`FEXIT`/`FRET.*`) with no additional payload.
  - [ ] Blocks containing only boundary-event instructions (e.g. `ACRC`, `EBREAK`) and no other payload.
  - [ ] Vector blocks with `DIM` implying zero iterations (where permitted by the profile/spec).
- [ ] **Commit-time control-flow visibility**:
  - [ ] Block computes its next target during execution.
  - [ ] Architectural PC is updated **at block commit**.
- [ ] **Boundary-only branch target safety / CFI**:
  - [ ] Control-flow targets **must land on legal block boundaries**.
  - [ ] Any *architectural* control-flow transfer to a **non-boundary** (e.g. mid-block / `BodyTPC`) is **illegal** and MUST raise a dedicated control-flow-integrity exception: `E_BLOCK(EC_CFI)`.
    - Bring-up cause encoding: `EC_CFI=0x1` in `E_BLOCK`, with `EC_CFI_KIND` in `TRAPNO.CAUSE[3:0]` (see System/Privilege chapter for the normative mapping).
    - Bring-up reporting requirement: `TRAPARG0` = source PC/TPC of the control-flow instruction (or boundary marker that triggered the violation); `ECSTATE.BI=0`.

## B. Architectural State: GSTATE Composition

- [ ] **24 GPRs** are architecturally exposed in the global layer.
- [ ] **32 tile registers** are architecturally exposed.
- [ ] **SSR state** (system register model) exists and is integrated into the architectural state.
  - Reference: `isa/v0.3/state/system_registers.json`

## C. Architectural State: BSTATE Composition

- [ ] **BSTATE is block-type dependent**.
- [ ] Local states for these categories are architecturally defined and consistent:
  - [ ] scalar-local state
  - [ ] vector/tile-local state
  - [ ] template-local state

## D. Machine Model: BCC / PEs / Retirement

- [ ] **BCC schedules block commands**.
- [ ] **Heterogeneous PEs** model:
  - [ ] PEs share the first-layer architectural state.
  - [ ] Each PE owns its second-layer local state.
- [ ] **OoO issue, in-order retirement**:
  - [ ] Block issue may be out-of-order.
  - [ ] Block retirement/resolve must be **in program order** via a **block reorder buffer (BROB)**.
- [ ] **Second-layer consume/execute/resolve contract**:
  - [ ] PE executes only after receiving a valid block command.
  - [ ] PE returns liveouts/status to BROB for in-order resolve.

## E. Block Boundary Instruction Set & Events

- [ ] Block lifecycle boundaries are implemented and semantically correct:
  - [ ] `BSTART.*` / `C.BSTART.*` start a block.
  - [ ] `BSTOP` / `C.BSTOP` terminates a block.
- [ ] Boundary events/instructions are implemented and have correct semantics:
  - [ ] `BWE` / `BWI`
  - [ ] `ACRC` / `ACRE`
  - [ ] `EBREAK`

## F. Header Descriptors (Normative)

- [ ] Header descriptors are implemented and interpreted normatively:
  - [ ] `B.ARG`
  - [ ] `B.ATTR`
  - [ ] `B.IOR`
  - [ ] `B.IOT`
- [ ] `B.IOD` exists only as **obsolete compatibility** descriptor (do not rely on it as normative).

## G. Coupled vs Decoupled Blocks

- [ ] **Coupled blocks** (header + body) work.
- [ ] **Decoupled blocks** work:
  - [ ] Header uses `B.TEXT` to point to the body.
  - [ ] Header/body execution context separation is architecturally respected.

## H. Variable-Length Interpretation / Queues

- [ ] A block can be interpreted as a **variable-length macro instruction**.
- [ ] Internal T/U queue behavior follows the architected constrained producer–consumer flow (no illegal reordering/overrun).

## I. Templates (TEPL + Save/Restore)

- [ ] Template blocks are treated as architected contracts (not “micro-optimizations”).
- [ ] Template body generation models are allowed (ROM/FSM/engine), but:
  - [ ] Behavior must remain **architecturally equivalent**.
- [ ] Template save/restore contract is implemented:
  - [ ] `ESAVE` saves second-layer state for recovery.
  - [ ] `ERCOV` restores second-layer state from saved context.
- [ ] **TEPL extension + FP hint semantics**:
  - [ ] `BSTART.TEPL` provides a generic accelerator block type.
  - [ ] `BSTART.FP` is **hint-only** for mixed scalar/FP typing (must not change correctness).

## J. Vector / Tile Execution Semantics

### J1. MSEQ / MPAR

- [ ] `BSTART.MSEQ` semantics:
  - [ ] Vector body expresses **one-lane semantics**.
  - [ ] `DIM` controls repeated execution and ordered commit.
- [ ] `BSTART.MPAR` semantics:
  - [ ] Lanes execute in parallel.
  - [ ] Commit/resolve semantics differ from MSEQ and match the spec.

### J2. VPAR / VSEQ (Tile-only vectors)

- [ ] `BSTART.VPAR` / `BSTART.VSEQ`:
  - [ ] Do **not** directly access main memory.
  - [ ] May execute speculatively (within architected constraints).

### J3. Tile Architectural Bounds

These are **hard architectural constraints** for v0.3 bring-up (software may rely on them; invalid runtime values must be rejected per the spec / treated as illegal).

- [ ] Architectural tile register count is **32**.
- [ ] Tile size bounds (tile size is **variable per binding/allocation**, selected via tile-size descriptors):
  - [ ] min **512 B**
  - [ ] max **4 KiB**
- [ ] Architectural tile capacity is **128 KiB**.
- [ ] Tile renaming is allowed, but must preserve architectural semantics.

### J4. Clockhand Allocation Invariants (Compiler)

- [ ] Compiler preserves **relative tile distance** across control-flow joins.
- [ ] If not provable, compiler must **spill/reload** (no silent corruption).

## K. Block-Command Packing / Dispatch

- [ ] Header descriptors pack the block-command fields correctly.
- [ ] `BSTOP` dispatches the block command to the selected PE.

## L. Memory Model & Memory-System Constraints

- [ ] Ordering model is architectural **TSO** (applies to the architectural ordering domain; implementations may be stronger, but software must not depend on stronger-than-TSO behavior).
  - In Linx terms, a **memory operation** includes: load, store, atomic RMW, or fence.
  - Ordering/visibility primitives to explicitly cover during bring-up:
    - [ ] Atomic qualifiers: `.aq` / `.rl` / `.aqrl`
    - [ ] `FENCE.D pred_imm, succ_imm`
    - [ ] `FENCE.I`
- [ ] Vector-memory separation is respected:
  - [ ] Vector PE has **no direct main-memory access**.
  - [ ] Scalar pipe and TMA perform main-memory accesses.
- [ ] Shared MMU/TLB model:
  - [ ] Scalar and tile accesses share the MMU/TLB path.
  - [ ] `TLOAD` / `TSTORE` faults are **restartable** (ranged tile faults).
- [ ] Bridged memory path for `MSEQ`/`MPAR`:
  - [ ] Memory flow is bridged through tile/TMA path.
  - [ ] Barriers/fences/atomics constrain conflicts between bridged memory actions (TSO-preserving).

## M. Tile Alias Mapping & Per-Family Header Contracts

### M1. Vector bridge load/store forms

- [ ] Bridge loads/stores use the correct forms:
  - [ ] `load.local` / `store.local`
  - [ ] `load.brg` / `store.brg`

### M2. Vector body argument namespace & base registers

- [ ] Vector body uses `ri0..rin` argument namespace.
- [ ] Vector body uses these base registers consistently:
  - [ ] `TA` / `TB` as inputs
  - [ ] `TO` / `TS` as output/scratch bases
- [ ] Vector blocks may mix scalar and vector instructions **in the block body** for the applicable vector families (MSEQ/MPAR and VSEQ/VPAR).
  - Note: `BSTART.TEPL` blocks do not have a normal architected block body (template expansion / engine execution), so “mixing in the body” is not applicable there.

### M3. TMA / TLOAD / TSTORE / TMOV (Function field)

- [ ] In strict v0.3, `BSTART.TMA` uses the **Function** field.
- [ ] Mappings:
  - [ ] `BSTART.TLOAD`  -> `Function = 0`
  - [ ] `BSTART.TSTORE` -> `Function = 1`
  - [ ] `BSTART.TMOV`   -> `Function = 2`
- [ ] `Function = 3..31` is **reserved** in strict v0.3 and treated as **architecturally illegal / UNPREDICTABLE**: software must not generate it, and implementations must not assign ad-hoc semantics (do not repurpose).
- [ ] TMOV destination allocation is **queue-push only** (no illegal random-access destination semantics).
- [ ] Header requirements:
  - [ ] `BSTART.TLOAD/TSTORE` require layout from `B.ARG`.
  - [ ] Stride/base must come from `B.IOR`.

### M4. CUBE / MATMUL family

- [ ] `BSTART.CUBE` uses a Function selector and maps these operations:
  - [ ] `TMATMUL`
  - [ ] `TMATMUL.ACC`
  - [ ] `ACCCVT`
- [ ] `TMATMUL` / `TMATMUL.ACC` bind `LB0/LB1/LB2` as `m/n/k`.
- [ ] `ACCCVT` requires quantization arguments via `B.ARG` and `B.IOR`.

### M5. TEPL selector space

- [ ] `BSTART.TEPL` carries the PTO template-op selector `TileOp10`.
- [ ] Unassigned `TileOp10` space is **reserved** for future extension (do not allocate ad-hoc meanings).
- [ ] TVEC is represented by `BSTART.VPAR` / `BSTART.VSEQ`.

---

## N. Privilege, Traps, and Restartability (System Model)

- [ ] Privileged state and trap envelopes follow the v0.3 SSR/TRAPNO model.
- [ ] Trap behavior is consistent across compiler-emitted code, QEMU, and RTL (no “implementation-defined” divergence).

---

## Reference: Normative Gate(s)

- Run the contract gate:

```bash
python3 tools/bringup/check26_contract.py --root .
```

- The contract definition is in `docs/bringup/check26_contract.yaml`.
