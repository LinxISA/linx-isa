# Alt-Compiler SIMT ASM Gap Analysis

## Summary

This note analyzes the alternative-compiler output in `/Users/zhoubot/linx-simt.s` against:

- the source intent in `/Users/zhoubot/linx-simt.c`
- the canonical `v0.4` ISA manual
- the current LLVM Linx SIMT lowering in `compiler/llvm/llvm/lib/Target/LinxISA/LinxISASIMTAutoVectorize.cpp`
- the current QEMU Linx vector-body execution model in `emulator/qemu/target/linx/translate.c`

The main result is that the interesting gaps are mostly not raw opcode absences. The generated assembly already uses a large set of existing vector/SIMT forms. The real gaps are in the architectural SIMT contract around lane grouping, divergence, reconvergence, lane-local state, and the compiler/runtime model needed to make those forms compose into a robust GPU-style execution model.

## Workload Shape

The source in `/Users/zhoubot/linx-simt.c` is a good stress case for a real SIMT model:

- Per-thread strided iteration:
  `tid = thread_idx + thread_num * block_idx`, then `tid += thread_num * block_num` in `hashtable_insert` (`/Users/zhoubot/linx-simt.c:66-67`) and `block_base_idx += thread_num * block_num` plus `tid = block_base_idx + thread_idx` in `callee` (`/Users/zhoubot/linx-simt.c:148-152`).
- Hash and modulo-heavy address generation:
  `curr_slot = b % capacity` and `(curr_slot + 1) % capacity` (`/Users/zhoubot/linx-simt.c:97-99`, `/Users/zhoubot/linx-simt.c:120-123`, `/Users/zhoubot/linx-simt.c:183-185`, `/Users/zhoubot/linx-simt.c:206-208`).
- Divergent data-dependent loop exits:
  `while (true)` with early `break` on empty slot, found key, or full probe (`/Users/zhoubot/linx-simt.c:103-124`, `/Users/zhoubot/linx-simt.c:187-209`).
- Mixed scalar and per-lane memory activity:
  scalar setup around `capacity`, `entry_size`, and imported pointers, but per-thread key/value lookup and scattered slot traffic.

The generated assembly preserves that shape. It launches through `BSTART.MPAR VS16`, `B.DIM zero, 1024, ->lb0`, and `B.TEXT` (`/Users/zhoubot/linx-simt.s:48-55`), then lowers the body into a mix of:

- vector ALU (`v.mul`, `v.srli`, `v.xor`, `v.rem`) (`/Users/zhoubot/linx-simt.s:110-149`)
- vector memory (`v.ld`, `v.sw`, `v.sdi.u.local`, `v.lwi.u.local`) (`/Users/zhoubot/linx-simt.s:100-107`, `/Users/zhoubot/linx-simt.s:178-184`, `/Users/zhoubot/linx-simt.s:208-210`, `/Users/zhoubot/linx-simt.s:239-244`)
- mask/select operations (`v.cmp.* ->p`, `v.psel`) (`/Users/zhoubot/linx-simt.s:68-71`, `/Users/zhoubot/linx-simt.s:154-173`, `/Users/zhoubot/linx-simt.s:184-191`)
- scalar branches and jumps inside the vector body (`/Users/zhoubot/linx-simt.s:71-72`, `/Users/zhoubot/linx-simt.s:95-96`, `/Users/zhoubot/linx-simt.s:173-174`, `/Users/zhoubot/linx-simt.s:191-192`, `/Users/zhoubot/linx-simt.s:233-234`)

## Non-Gaps / Already Covered

These are not the main missing pieces:

- `BSTART.MPAR`, `B.DIM`, and `B.TEXT` already exist as first-class SIMT header/body machinery in the canonical manual (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:498-532`, `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc:40-50`).
- `p` is already a defined kernel EXEC mask, distinct from block-control predicate state (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:107-119`).
- `.local` vector memory forms already exist as canonical tile-local accesses (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:580-625`).
- `V.REM` and `V.PSEL` appearing in the asm are not, by themselves, evidence of a missing encoding. The harder problem is the execution model around them.
- QEMU already has a basic decoupled SIMT body model that enters a `B.TEXT` body and replays it over `LB/LC` state (`emulator/qemu/target/linx/translate.c:454-480`, `emulator/qemu/target/linx/translate.c:484-520`).

## Gap Inventory

### Vector ISA Design

#### Gap 1: The current SIMT model is replay-oriented and group-uniform, but this workload needs persistent per-lane liveness and divergent progress

- Classification: design gap
- Observed asm evidence:
  - The body is full of data-dependent exits and re-entry points: `b.ne` / `j` split the body into many internal blocks (`/Users/zhoubot/linx-simt.s:71-72`, `/Users/zhoubot/linx-simt.s:95-96`, `/Users/zhoubot/linx-simt.s:173-174`, `/Users/zhoubot/linx-simt.s:191-192`, `/Users/zhoubot/linx-simt.s:233-234`).
  - The compiler keeps lane state alive across those splits with `v.psel`, repeated `v.cmp.* ->p`, and many `.local` spills/reloads (`/Users/zhoubot/linx-simt.s:154-173`, `/Users/zhoubot/linx-simt.s:178-210`, `/Users/zhoubot/linx-simt.s:239-257`).
- Current canonical design:
  - The `v0.4` manual defines one scalar-uniform control-flow context per group plus EXEC mask `p` (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:121-167`).
  - SIMT bodies are defined as one-lane bodies replayed over `lc0..lc2` tuples (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:500-521`).
- Why this is a gap:
  - That contract is enough for replay-style vector loops.
  - It is not enough to express a GPU-style “some lanes are finished, some lanes are still probing” model with explicit architectural meaning.
  - The asm is forced to emulate persistent lane progress inside a model that only explicitly names a group-uniform scalar PC plus a mask.
- Impact on compiler / QEMU / RTL:
  - Compiler must aggressively if-convert and synthesize lane state in scratch.
  - QEMU can replay the body, but it has no architectural concept of per-lane continuation state to execute against.
  - RTL would have to guess whether the intended machine is “replay only” or “warp with partially completed lanes”.
- Recommended closure direction:
  - Pick one of two explicit contracts and make it architectural:
    - predication-first SIMT: restrict kernels to structured if-converted forms and say that per-lane divergence beyond mask predication is out of scope, or
    - true divergent SIMT: add first-class per-lane or per-subgroup continuation / reconvergence state.
  - Do not leave this as an implicit compiler convention.

#### Gap 2: The current predicate model (`BARG.CARG` vs `p`) is too weak for full GPU-style divergence and reconvergence

- Classification: design gap
- Observed asm evidence:
  - The body repeatedly turns vector conditions into `p`, then materializes `p` back into scalar temporaries, then branches (`/Users/zhoubot/linx-simt.s:68-71`, `/Users/zhoubot/linx-simt.s:88-96`, `/Users/zhoubot/linx-simt.s:163-173`, `/Users/zhoubot/linx-simt.s:184-191`).
  - It also uses `v.psel` to manually merge per-lane state (`/Users/zhoubot/linx-simt.s:154-160`).
- Current canonical design:
  - `v0.4` explicitly separates block-control predicate state (`BARG.CARG`) from kernel EXEC mask `p` (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:109-119`).
  - `SETC.*` does not mask vector lanes; `V.CMP.* ->p` is the normative mask producer (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:618-625`).
- Why this is a gap:
  - The current model gives a mask register, but not a full mask-control algebra for divergent execution.
  - There is no first-class architectural notion of:
    - `any` / `all` / `none` over EXEC,
    - push/pop/save/restore of EXEC subsets,
    - reconvergence point tracking,
    - branch-on-mask without scalarizing through scratch-like temporaries.
  - The asm shows exactly that missing layer.
- Impact on compiler / QEMU / RTL:
  - Compiler must translate divergent conditions into a scalarized control protocol that is not explicitly architectural.
  - Emulator and RTL can only be correct if they independently rediscover the same hidden mask protocol.
- Recommended closure direction:
  - Define a small canonical EXEC-control submodel:
    - mask query operations (`any`, `all`, `none`)
    - mask save/restore or stack operations
    - explicit convergence semantics for inner branches
  - If that is too large for `v0.4`, then codify a strict predication-only subset and ban code shapes like this from canonical lowering.

#### Gap 3: Launch geometry and group width are under-specified for alternative SIMT compilers

- Classification: design gap
- Observed asm evidence:
  - The launch wrapper uses `BSTART.MPAR VS16` with `B.DIM zero, 1024, ->lb0` and no visible `LB1` setup (`/Users/zhoubot/linx-simt.s:48-55`).
  - Inside the body, the compiler uses both `lc1` and `lc0` to reconstruct logical indices (`/Users/zhoubot/linx-simt.s:62-67`, `/Users/zhoubot/linx-simt.s:77-87`).
  - This strongly suggests an implicit strip-mining model: 1024 logical threads are being mapped onto 16-lane groups, with `lc1` acting as an implicit group index.
- Current canonical design:
  - The current 1-D canonical profile says `LB0 = lane_count`, `LB1 = group_count`, `lc0 = lane index`, `lc1 = group index` (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:159-167`, `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:517-521`).
- Why this is a gap:
  - The asm is using a different contract than the current canonical one, or at least a stricter interpretation not written down in the manual.
  - Right now the relationship among:
    - header vector size (`VS16`)
    - logical thread count (`1024`)
    - `LB0` / `LB1`
    - `lc0` / `lc1`
    - physical group width
    is not explicit enough to guarantee portability across compilers.
- Impact on compiler / QEMU / RTL:
  - Alternative compilers can generate incompatible but superficially legal kernels.
  - QEMU and RTL can disagree on how many logical iterations a body should execute and what `lc1` means.
- Recommended closure direction:
  - Add an explicit profile contract for launch strip-mining:
    - whether `VS*` is physical width, logical width, or both
    - whether `LB0` may carry total logical threads instead of lane width
    - how `lc1` is derived when only one `B.DIM` is present
  - Require canonical lowering to emit either:
    - explicit `LB0 = lane_count`, `LB1 = group_count`, or
    - a new header/profile bit that authorizes implicit strip-mining.

### Encoding / Operand Model

#### Gap 4: The operand model forces excessive scalar-vector shuttling for values that are logically lane-local but control-flow-sensitive

- Classification: design gap
- Observed asm evidence:
  - The body is full of `c.movr`, `l.ori`, `v.ori`, and scalarization of `p` into `t/u` registers (`/Users/zhoubot/linx-simt.s:76-81`, `/Users/zhoubot/linx-simt.s:88-96`, `/Users/zhoubot/linx-simt.s:164-173`, `/Users/zhoubot/linx-simt.s:211-217`, `/Users/zhoubot/linx-simt.s:245-257`).
  - This is not just normal SSA noise. It is the compiler paying an operand-model tax to move information between vector, mask, and scalar control domains.
- Current canonical design:
  - Scalar-uniform instructions operate in `GPR`/`t/u`/`p`; vector instructions operate in `vt/vu/vm/vn`; direct `v.* -> scalar` writes are illegal except for reductions or mask-producing forms (`docs/architecture/isa-manual/src/chapters/03_programming_model.adoc:123-157`).
  - Vector instructions must import scalar values via `ri*` or allowed scalar operands; direct arbitrary scalar GPR use in `V.*` forms is illegal (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:624-625`).
- Why this is a gap:
  - The current split is clean for simple vector arithmetic.
  - It is not expressive enough for SIMT control-heavy programs where lane-local values must participate in branch decisions, phi merges, and loop progress bookkeeping.
  - The asm shows the compiler constructing an ad hoc shuttle protocol instead of using first-class ISA constructs.
- Impact on compiler / QEMU / RTL:
  - Compiler generates verbose, fragile code.
  - Emulator/RTL are exposed to many more corner cases around mask/scalar/vector handoff than the ISA currently explains.
- Recommended closure direction:
  - Define a small set of first-class SIMT operand-domain crossings:
    - mask-to-scalar query
    - scalar-to-mask broadcast with explicit semantics
    - maybe one lane-local scalar temporary namespace, or explicit lane-state records
  - Keep the current clean split for non-SIMT vector code, but stop forcing SIMT control lowering through generic `movr`/`ori` patterns.

#### Gap 5: `.local` exists, but the architectural meaning of compiler-generated lane-local scratch / spill storage is under-specified

- Classification: design gap
- Observed asm evidence:
  - The body uses `.local` heavily as compiler bookkeeping storage:
    - `v.sdi.u.local ... [to1, 1800]` (`/Users/zhoubot/linx-simt.s:100-105`)
    - `v.swi.u.local ... [to1, lc0<<2, 520]` (`/Users/zhoubot/linx-simt.s:178-183`)
    - `v.ldi.u.local ... [to1, lc0<<3, 776]` (`/Users/zhoubot/linx-simt.s:196-200`)
    - `v.lwi.u.local ... [to1, lc0<<2, 520]` (`/Users/zhoubot/linx-simt.s:208-210`, `/Users/zhoubot/linx-simt.s:244-245`)
  - These offsets look like compiler-generated spill slots or lane-state records, not user-visible tile payloads.
- Current canonical design:
  - `.local` accesses are described as tile-local accesses through `TA/TB/TC/TD/TO/TS`, bounded by tile size; `TO/TS` are output/scratch bases (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:582-613`).
- Why this is a gap:
  - The manual says what `.local` addresses mean as tile references.
  - It does not define a compiler ABI for using `.local` as per-lane spill, mask-stack, recurrence, or phi-resolution storage.
  - The asm depends on exactly that unstated contract.
- Impact on compiler / QEMU / RTL:
  - Compiler has no standardized guarantee for alignment, lifetime, aliasing, or minimum scratch footprint.
  - Emulator and RTL can implement `.local` “correctly” for tile ops and still disagree with compiler-generated scratch expectations.
- Recommended closure direction:
  - Add a canonical SIMT scratch contract:
    - which tile base is the compiler scratch arena
    - lane-private addressing formula
    - alignment and sizing rules
    - whether scratch is per-group or per-kernel-instance
    - whether compiler spills may alias user-visible `.local` accesses
  - If the intent is “TS is compiler scratch”, say so explicitly and define the ABI.

### Decode / Execution Model

#### Gap 6: `B.TEXT` defines entry and termination, but not a first-class divergence/rejoin protocol inside the body

- Classification: design gap
- Observed asm evidence:
  - The kernel body contains many internal control-flow regions and repeated re-entry to the probe loop (`/Users/zhoubot/linx-simt.s:84-96`, `/Users/zhoubot/linx-simt.s:152-174`, `/Users/zhoubot/linx-simt.s:176-218`, `/Users/zhoubot/linx-simt.s:220-258`).
- Current canonical design:
  - The manual is explicit about `B.TEXT` entry legality and termination conditions (`docs/architecture/isa-manual/src/chapters/04_block_isa.adoc:523-532`, `docs/architecture/isa-manual/src/chapters/08_tile_blocks.adoc:40-50`).
  - QEMU mirrors that model by entering `cpu_body_tpc`, replaying until `linx_vec_body_next`, then returning to the header continuation (`emulator/qemu/target/linx/translate.c:454-480`, `emulator/qemu/target/linx/translate.c:484-520`).
- Why this is a gap:
  - Entry and termination are specified.
  - Rejoin semantics for partially active lanes are not.
  - The ISA leaves it unclear whether an inner body branch is:
    - only a scalar-uniform branch under current `p`,
    - a request to split EXEC and reconverge later,
    - or simply compiler-managed predication with no architectural rejoin concept.
- Impact on compiler / QEMU / RTL:
  - Compiler has to synthesize a de facto rejoin protocol.
  - Emulator/RTL can support body branches, but not know what the architectural intent is when lane subsets progress differently.
- Recommended closure direction:
  - Extend the `B.TEXT` SIMT body contract with one explicit statement:
    - either “body control flow is strictly scalar-uniform under current EXEC; no architectural reconvergence exists”
    - or “body control flow may split EXEC, and the architecture provides reconvergence state X/Y/Z”.

#### Gap 7: QEMU’s current vector-body model is a replay engine, not a semantic answer to the SIMT control-state problem

- Classification: implementation gap, but only after the design gap above is resolved
- Observed asm evidence:
  - The body expects fine-grained interaction among mask updates, branches, and state kept in `.local`.
- Current canonical implementation:
  - QEMU replays the body by stepping `LB/LC` state through `linx_vec_body_next`, then returns at body termination (`emulator/qemu/target/linx/translate.c:454-480`).
  - It treats `B.TEXT` as a decoupled header/body transfer with legality checks (`emulator/qemu/target/linx/translate.c:484-520`).
- Why this is a gap:
  - This is enough for the current replay-oriented subset.
  - It is not enough to prove correctness for a richer SIMT model with explicit divergence/rejoin state, because that state does not yet exist architecturally.
- Impact on compiler / QEMU / RTL:
  - QEMU can only ever approximate what the alternative compiler is doing unless the architecture first says what the machine is.
  - RTL validation would hit the same ambiguity.
- Recommended closure direction:
  - Do not “fix” QEMU first.
  - First freeze the SIMT control-state contract, then extend QEMU to model exactly that contract and add targeted AVS coverage for:
    - partially active loops
    - nested divergent branches
    - lane completion with surviving peers

### SIMT Compilation Model

#### Gap 8: The current LLVM SIMT lowering contract is still a correctness-first replay subset, not a full compiler contract for this class of kernels

- Classification: implementation gap with a profile-contract hole
- Observed asm evidence:
  - The alternative compiler is clearly willing to emit a control-heavy MPAR body with real in-body branching, vector compares feeding `p`, `v.psel`, `.local` spill state, and modulo-based probe loops (`/Users/zhoubot/linx-simt.s:60-258`).
- Current LLVM lowering:
  - LLVM rejects many loop shapes and defaults to `mseq` unless independence is structurally obvious (`compiler/llvm/llvm/lib/Target/LinxISA/LinxISASIMTAutoVectorize.cpp:700-860`).
  - It explicitly forces scalar-lane replay through `LB1` in the bring-up path (`compiler/llvm/llvm/lib/Target/LinxISA/LinxISASIMTAutoVectorize.cpp:1589-1649`).
  - Its inner-control-flow fallback reduces vector predicates to a scalar `any-active-lane` branch using `v.rdor ... ->t#1` (`compiler/llvm/llvm/lib/Target/LinxISA/LinxISASIMTAutoVectorize.cpp:4182-4275`).
- Why this is a gap:
  - The current implementation is not “wrong”; it is intentionally conservative.
  - But there is no stable compiler contract that says when a more aggressive MPAR lowering like the alternative compiler’s output is canonical and legal.
  - Without that contract, every compiler will invent its own SIMT lowering discipline.
- Impact on compiler / QEMU / RTL:
  - Backend portability is poor.
  - AVS cannot distinguish “legal alternative lowering” from “compiler-specific undefined behavior”.
- Recommended closure direction:
  - Write down a compiler-facing SIMT lowering profile:
    - legal branch patterns inside MPAR/MSEQ bodies
    - allowed use of `.local` scratch
    - required EXEC-mask semantics for divergent regions
    - allowed launch/group-width mappings
  - Then either expand LLVM toward that profile or explicitly keep LLVM on the replay-only subset and state that richer SIMT kernels are non-canonical for now.

## Overall Assessment

The alternative compiler is not primarily exposing missing single instructions. It is exposing that the current `v0.4` SIMT story is still a partially hardened replay model, while this hash-table kernel wants a more explicit GPU-like execution contract.

The deepest missing pieces are architectural:

- what a group is when `VS*` and `LB*` both appear
- how partially active lanes continue through inner control flow
- where compiler-generated lane-local state lives
- how masks and branches interact without relying on compiler-private conventions

Until those are frozen, LLVM, QEMU, and RTL can all make locally reasonable choices and still diverge.

## Prioritized Closure Order

1. Control-flow / reconvergence contract
2. Lane-local state / scratch model
3. Launch geometry / group-width contract
4. Compiler lowering contract
5. Emulator / decoder follow-through
