# LinxISA v0.3 SIMT / Vector Block Model (research notes)

> Purpose: capture what LinxISA already specifies about SIMT-style execution so our AI+render GPGPU design builds on it (instead of reinventing a GPU model).

## 1) SIMT is expressed as *block types* (not a separate ISA mode)

The ISA defines **SIMT-style vector blocks**:
- `BSTART.MSEQ` / `BSTART.MPAR`
- `BSTART.VSEQ` / `BSTART.VPAR`

Key rule: a vector block body specifies **one-lane semantics**, and hardware **replays** it over a lane space.

Sources:
- `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (SIMT-style vector blocks)
- `docs/architecture/isa-manual/src/chapters/07_tile_blocks.adoc` (SIMT vector blocks)

## 2) Lane space + counters (LB0–LB2, lc0–lc2)

Bring-up model (strict v0.3):
- `LB0..LB2` are written by header `B.DIM`.
- Hardware exposes lane counters `lc0..lc2` to the body, init `0`.
- Body executes for each tuple `(lc0,lc1,lc2)`:
  - `lc0: 0..LB0-1` (fastest)
  - `lc1: 0..max(LB1,1)-1`
  - `lc2: 0..max(LB2,1)-1`

Commit semantics:
- `MSEQ`/`VSEQ`: lexicographic commit order.
- `MPAR`/`VPAR`: conceptually parallel; commit may interleave but must be observationally valid.

Source: `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`

## 3) “Group model”: scalar-uniform context per group

Strict v0.3 defines a canonical 1-D lowering:
- `LB0` = **lane_count** (lanes per group)
- `LB1` = **group_count**
- linear lane index: `lc0 + lc1 * lane_count`

Important: **scalar instructions inside vector bodies are uniform per group**:
- one scalar-uniform execution context per group replay
- scalar instructions execute once per group; vector instructions operate in the lane domain

Source: `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` and `docs/architecture/isa-manual/src/chapters/02_programming_model.adoc`

## 4) Predicates: block-control vs lane values

Two distinct predicate domains:
- Block-control predicate (`BARG.CARG`) from `SETC.*` for block-level control.
- Vector-lane predicate values produced by `V.CMP.*` / `V.F*` compares, consumed by `V.CSEL` etc.

Lane predicate truth: `value != 0`.

Source: `docs/architecture/isa-manual/src/chapters/02_programming_model.adoc` and `isa/v0.3/state/architectural_state.json`

## 5) Memory model separation + bridged global memory

Architectural constraint (v0.3 strict):
- **Vector PE has no direct main-memory access**.
- Scalar pipe and TMA/tile channel perform memory accesses.

Vector memory naming:
- `.local` forms: tile/local direction (base is tile bases `TA/TB/TO/TS`)
- `.brg` forms: bridged global memory (base must be `ri*` imported via `B.IOR`)

Hard restriction:
- `VSEQ/VPAR` blocks **MUST NOT** use `.brg` ops (tile-only vector execution).
- `MSEQ/MPAR` are the vector families intended to use the bridged path.

Sources:
- `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (bridge naming + restrictions)
- `docs/bringup/plan/arch.md` (vector-memory separation)
- `isa/v0.3/state/memory_model.json` (MTC includes bridged MSEQ/MPAR)

## 6) Implications for our “shader→SIMT→VEC” plan

What LinxISA already gives us:
- A standardized SIMT replay model (lane_count/group_count).
- Lane IDs (`lc*`) usable for subgroup ops, addressing, etc.
- Reduction (`V.RD*`) and shuffle (`V.SHFL*`) operations suitable for subgroup programming.

What we still must decide/design:
- **lane_count policy** for our GPGPU core (e.g. LB0=8/16/32/64). ISA allows variable; hardware+compiler should pick a sweet spot.
- How to compile GPU-style divergent control flow given the strict separation of predicate domains and the “scalar-uniform per group” rule.
  - Likely needs aggressive if-conversion/predication, or an ISA/profile extension for per-lane control flow (exec-mask style).
- How to map graphics shader stages onto `MSEQ/MPAR` vs tile-only `VSEQ/VPAR`.

