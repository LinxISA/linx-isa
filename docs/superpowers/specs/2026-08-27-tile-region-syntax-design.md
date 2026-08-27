# Linx Tile region syntax and compiler contract

Status: **Proposed; not active in the LinxISA 0.58.3 release**

Target candidate selection: PTO architecture 0.58.4 with publication revision
0.58.4.1 at one exact PTO-SPEC head

Audience: PTO/Linx architecture, Linx LLVM, Linx-TileOP-API, and workload
implementers

## 1. Decision summary

Linx source and compiler-facing Tile syntax SHALL express a logical region on
each Tile operand:

```text
TROWMAX <4,32,4,BF16> T2[:, 4*g:4*g+4] -> T5[:, g]
TROWEXPANDMUL <2,32,2,BF16>
    T20[:, 2*i:2*i+2], T16[:, j] -> T21[:, 2*k:2*k+2]
```

A source region denotes a `B.SUBVIEW` candidate. A destination region denotes
a contribution to one `B.ASSEMBLE` generation. Each operand owns an independent
region expression; equal spelling is not implied and different induction
variables are legal.

The source language and compiler IR MUST preserve logical parent identity,
region origin and extent, assembly-generation identity, commit/publication
boundary, and execution scope when these facts cannot be reconstructed. The
compiler MUST derive raw `B.IOT`/`B.IOS` association, `SrcSelect`, `RegSrc`,
`uimm11`, SizeCode, binder continuation/group-closure controls, and
`INIT`/`LAST`. Ordinary C and C++ APIs MUST NOT require users to pass those
encoding fields.

The bracket syntax is a compiler-facing Tile IR and C++ programming-model
surface. It is not final MC assembly. Final MC remains the PTO-defined
contiguous binder-plus-modifier sequence.

## 2. Authority and version boundary

The authority order for this proposal is:

1. PTO-SPEC candidate normative ASL and accepted decisions at commit
   `9bacc7bed9c1057bf696d42e2bddb20c3fded509`.
2. The LinxISA release lock and generated v0.58 catalog.
3. Linx LLVM semantic IR and machine-lowering contracts.
4. Linx-TileOP-API source wrappers.
5. Workload usage.

The controlling PTO records are:

- [ADR-0098: range-modifier association](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/docs/status/decisions/0098-b-range-modifiers.md)
- [ADR-0106: per-PE Shared source offsets](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/docs/status/decisions/0106-shared-source-subview-per-pe.md)
- [`B.SUBVIEW` normative ASL](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/asl/block/operands/B.SUBVIEW.asl)
- [`B.ASSEMBLE` normative ASL](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/asl/block/operands/B.ASSEMBLE.asl)
- [Subview descriptor and operation applicability](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/asl/block/model/operands/subview-descriptor.asl)
- [ADR-0097: Local/Shared capacity](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/docs/status/decisions/0097-local-shared-capacity-and-cooperative-m-sharding.md)
- [ADR-0105: Shared whole-parent readiness](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/docs/status/decisions/0105-shared-whole-parent-readiness.md)
- [Local assembly generations](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/asl/block/model/operands/local-generation.asl)
- [Shared assembly generations](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/asl/block/model/operands/shared-generation.asl)
- [Portable carrier readiness, replay, and effect eligibility](https://github.com/PTO-ISA/pto-spec/blob/9bacc7bed9c1057bf696d42e2bddb20c3fded509/asl/block/model/operands/portable-carriers.asl)

The current superproject release is PTO/LinxISA 0.58.3. It does not contain
`B.SUBVIEW` or `B.ASSEMBLE`, and its pinned LLVM accepts Tile SizeCode 1 through
10. This proposal MUST remain feature-gated and MUST NOT be presented as a
0.58.3-compatible API.

PTO candidate head `9bacc7be` is a candidate selection, not a Linx-published
release boundary. Exact-head readiness and the LinxISA lock remain open. Stage
A MUST first close PTO exact-head release evidence and import one immutable
lock before Linx assigns a feature/object identity.

The candidate currently contains a SizeCode contradiction that this proposal
MUST NOT resolve locally:

- raw `B.SUBVIEW` accepts range SizeCode 1 through 12;
- raw `B.ASSEMBLE` accepts ParentSizeCode 0 through 12 subject to INIT rules;
- generated `B.IOT` destination forms and the Local single-object capacity rule
  accept 1 through 10, or 128 B through 64 KiB;
- `B.IOS` Shared destinations accept 1 through 12, or 128 B through 256 KiB;
- a checked-in Local `B.IOT` SizeCode-12 AVS still expects 256 KiB Local
  destination success.

PTO MUST reconcile the Local binder contract, capacity decision, generated
catalog, ASL helpers, and AVS before compiler implementation. Until then the
compiler rules distinguish modifier raw domain, Local binder domain, Shared
binder domain, and generation parent domain instead of using one universal
SizeCode range.

The proposed compiler feature is named `+pto0584-range` until LLVM review
assigns the final spelling. Clang builtins, LLVM intrinsics, and MC forms MUST
reject when this feature is absent. Enabling it requires the future exact PTO
0.58.4/0.58.4.1 locked identity; it MUST NOT be combined with a
`.note.pto.isa` descriptor for 0.58.3. No minimum compiler commit exists until
the MC and semantic-IR implementation PRs land.

## 3. Implementation evidence studied

### 3.1 LLVM level-one lineage

The public LLVM repository has no currently visible branch named `level-one`.
The public `bisheng-linx` import at commit
`631961c3988fb4d610034f5d9b52b38ecb279755` is the available one-level LinxV5
implementation baseline. It provides:

- Clang `tile_size`, `__in__`, and `__out__` source contracts;
- vector-valued `llvm.linx.vcall.*` and `llvm.linx.mcall.*` intrinsics whose
  input/output arity is explicit in IR;
- Tile clock-hand allocation, register reuse, Tile copies, header emission,
  and multi-output lowering in the backend;
- compiler-generated Tile input/output header operands instead of user-coded
  binder fields.

Representative evidence:

- [Block-C Tile function source](https://github.com/LinxISA/llvm-project/blob/631961c3988fb4d610034f5d9b52b38ecb279755/clang/test/LinxV5/blk-func.cpp)
- [Tile copy and clock-hand behavior](https://github.com/LinxISA/llvm-project/blob/631961c3988fb4d610034f5d9b52b38ecb279755/llvm/test/CodeGen/LinxV5/Block-C/tile-copy.ll)
- [Multiple Tile outputs](https://github.com/LinxISA/llvm-project/blob/631961c3988fb4d610034f5d9b52b38ecb279755/llvm/test/CodeGen/LinxV5/Block-C/multi-output.ll)

This lineage proves that source-level Tile input/output intent can be lowered
through SSA and compiler-generated architectural headers. It does not define
the PTO 0.58.4 range protocol and MUST NOT be copied as an encoding authority.

If a separate private or deleted `level-one` ref is intended, its exact SHA
must be added to the implementation issue before compiler work begins.

### 3.2 Current Linx LLVM

Current Linx LLVM `main` at commit
`baef2b3a47a2162ef4e0542eb715562bfdbe7a6a` has a more suitable adaptation
boundary:

- first-class `target("linx.tile")` values;
- plain-C Clang builtins using a fixed-vector frontend bridge;
- semantic Tile intrinsics for TLOAD, TSTORE, TMOV, generic Tile operations,
  typed engine wrappers, and CUBE matrix multiplication;
- SelectionDAG Tile pseudos;
- `LinxISATileSSABalance` for Tile PHI/copy identity;
- `LinxISABlockify` for source-rank inference and final `BSTART`/`B.IOT`
  construction.

Representative evidence:

- [Clang Tile builtins](https://github.com/LinxISA/llvm-project/blob/baef2b3a47a2162ef4e0542eb715562bfdbe7a6a/clang/include/clang/Basic/BuiltinsLinxISA.td)
- [Clang builtin-to-intrinsic lowering](https://github.com/LinxISA/llvm-project/blob/baef2b3a47a2162ef4e0542eb715562bfdbe7a6a/clang/lib/CodeGen/TargetBuiltins/LinxISA.cpp)
- [LLVM Tile intrinsics](https://github.com/LinxISA/llvm-project/blob/baef2b3a47a2162ef4e0542eb715562bfdbe7a6a/llvm/include/llvm/IR/IntrinsicsLinx.td)
- [Tile SSA balance](https://github.com/LinxISA/llvm-project/blob/baef2b3a47a2162ef4e0542eb715562bfdbe7a6a/llvm/lib/Target/LinxISA/LinxISATileSSABalance.cpp)
- [Tile block construction](https://github.com/LinxISA/llvm-project/blob/baef2b3a47a2162ef4e0542eb715562bfdbe7a6a/llvm/lib/Target/LinxISA/LinxISABlockify.cpp)

Current `main` has no `B.SUBVIEW`/`B.ASSEMBLE` intrinsic, MC form, machine
pseudo, or lowering pass. Its Tile intrinsics lower directly to machine
pseudos, so phase inference is not implemented today.

### 3.3 SuperNPUBench one-level implementation

The maintained workload root is
`workloads/pto_kernels/benchmarks/supernpu`; the standalone SuperNPUBench
repository is not a superproject authority.

The studied one-level workload has three relevant patterns:

1. `MultiTile<N,T>` represents a large logical result as an array of ordinary
   Tile values, and `#pragma clang loop unroll(full)` exposes each operation to
   the compiler.
2. FlashAttention and softmax carry row state in a physically padded Tile, for
   example physical `[kTm,8]` with valid shape `[kTm,1]`. This is already a
   logical-shape-versus-carrier-shape contract.
3. Matrix multiplication accumulates through explicit SSA values and
   `TMATMUL`/`TMATMUL_ACC`; it does not currently form one large architectural
   parent with range modifiers.

The workload therefore supports a compiler-derived region protocol, but it
also proves that sub-cell logical values need a padded or coalesced carrier.
It does not provide evidence that arbitrary `[:, begin:end]` rectangles map to
one contiguous PTO CELL interval.

## 4. Terminology

**Parent Tile** is the architectural Local or Shared Tile whose identity and
descriptor are retained by a region.

**Logical region** is a rank-preserving half-open selection in programmer
coordinates.

**Encoded range** is one contiguous interval in PTO CELL order. One CELL is
128 B.

**Fragment** is the Tile value consumed from or contributed to a logical
region. Its logical valid shape may be smaller than its physical carrier.

**Assembly session** is a linear compiler-visible value representing exactly
one open destination generation.

**Contribution** is one fragment written to one non-overlapping destination
region in an assembly session.

**Commit** is the semantic boundary after which the complete parent may be
consumed. For Shared state it is also the requested publication boundary;
architectural publication still occurs only when PTO readiness, collective,
fault, and retirement rules succeed.

**Scope** identifies the participating PE/execution domain when it is not
inherent in the surrounding kernel type.

## 5. Compiler-facing Tile syntax

### 5.1 Grammar

The initial grammar is:

```ebnf
tile-operation  = [ session-result-list, "=" ], mnemonic, shape-spec, operand-list,
                  [ "->", destination-list ] ;
session-result-list = session-result | "(", session-result,
                      { ",", session-result }, ")" ;
operand-list    = operand, { ",", operand } ;
operand         = tile-name, [ region ] | scalar-expression ;
destination-list = destination, { ",", destination } ;
destination     = tile-name, [ region ] | session-name, region ;
region          = "[", selector, { ",", selector }, "]" ;
selector        = ":" | expression | expression, ":", expression ;
```

Rules:

- A region MUST contain one selector per logical Tile dimension.
- `:` selects the full dimension.
- `begin:end` is half-open and has extent `end - begin`.
- A scalar selector `i` is shorthand for `i:i+1`; it does not reduce rank.
- Steps and negative indices are not part of the initial syntax.
- An omitted region selects the whole Tile.
- Whitespace is insignificant.
- Each expression is an independent compiler SSA expression. The compiler
  MUST NOT assume that `i`, `j`, and `k` are equal or that repeated spelling
  denotes the same value without normal SSA equivalence.
- Destination arity is fixed by the generated operation schema. A textual
  destination list MUST have exactly that arity.
- Names prefixed with `%` are compiler SSA values or sessions. Final PTO
  relative names such as `T#1` are allocated later and MUST NOT appear in this
  IR grammar.

The following is valid:

```text
TROWEXPANDMUL <2,32,2,BF16>
    T20[:, 2*i:2*i+2], T16[:, j] -> T21[:, 2*k:2*k+2]
```

The explicit generation form is:

```text
%s0 = TILE.ASSEMBLY.BEGIN.LOCAL %parent, <descriptor>, <scope>
%s1 = TROWMAX <4,32,4,BF16> %T2[:, 4*g:4*g+4] -> %s0[:, g]
%T5 = TILE.ASSEMBLY.COMMIT.LOCAL %s1
```

A multi-output operation advances all destination sessions atomically:

```text
(%s1, %u1) = OP ... -> %s0[region0], %u0[region1]
```

Every successor session belongs to the same Tile-operation transaction. The
operation either validates and contributes every output or contributes none;
one output MUST NOT advance independently after another output faults.

The short `-> T5[:,g]` form is permitted only for the Local implicit-session
case defined in Section 7. Shared assembly always uses the explicit form.

### 5.2 Derived byte annotations

Annotations such as `T5[:,g]<64B>` are diagnostics or disassembly comments.
They MUST be derived from dtype, logical shape, valid shape, and layout. They
MUST NOT be an independent source operand and MUST NOT override descriptor
legality.

### 5.3 Region normalization

The frontend SHALL normalize every region to:

```text
(parent identity, logical origin vector, logical extent vector,
 layout, dtype, physical shape, valid shape)
```

The compiler SHALL then prove whether the logical region maps to one contiguous
encoded CELL interval. The proof is layout-dependent. A rectangular source
region that is strided or discontiguous in the parent layout MUST NOT silently
lower to one `B.SUBVIEW`.

Legalization choices, in order, are:

1. use one direct encoded range when contiguous, aligned, and representable;
2. fuse or vectorize adjacent logical operations so they produce one actual
   representable carrier before assembly;
3. widen a source view only when the operation proves extra elements are
   masked, ignored, or filled with the operation's exact neutral value;
4. use `TEXTRACT`, `TINSERT`, or `TCONCAT` when their operation contracts make
   the transformation exact;
5. reject with a stable diagnostic.

The compiler MUST NOT merge only metadata from independent producers, change
element order, cross a descriptor boundary, read undefined padding, or invent
overlapping assembly contributions. Destination legalization smaller than one
CELL MUST first create one real CELL-sized fragment through a semantics-
preserving operation/fusion; only that fragment may be one assembly writer.

## 6. Source and destination semantics

### 6.1 Source region

For `Tsrc[region]` used as a Tile source:

- the parent Tile identity and lifetime are preserved;
- the region is a candidate `B.SUBVIEW` on the binder that supplies that
  source role;
- source zero and source one are determined within the specific binder's
  syntactic group after mapping the operation schema to Local and Shared
  binders, not by a global operation ordinal and not by the source API;
- no new architectural Tile namespace is created by the source syntax;
- operation-specific dtype, layout, shape, and definedness legality remains
  authoritative.

PTO 0.58.4 does not mean every parent descriptor is legal. Current normative
ASL derives Local subviews from Local Matrix/CUBE parents and applies the
result to any accepted Tile-operation handler. Shared source subviews use a
published non-CUBE parent and evaluate the offset independently in each
participating PE. Frontends and LLVM MUST retain these distinctions.

### 6.2 Destination region

For `Tdst[region]` used as a destination:

- `Tdst` identifies one assembly session and its parent identity;
- the producing Tile operation computes a fragment in its normal result type;
- the compiler associates that fragment with a destination contribution;
- the backend fuses the contribution into the producing binder and emits
  `B.ASSEMBLE` immediately after that binder;
- the `B.ASSEMBLE` instruction does not encode `Tdst`; the preceding
  `B.IOT`/`B.IOS` destination binding owns that identity.

The writer SizeCode is the destination binder SizeCode. `ParentSizeCode` is
encoded only for the contribution whose derived phase has `INIT=1`.

### 6.3 Applicability to Tile operations

Range machinery is generic over every accepted Tile-operation dispatch
candidate. This statement does not add missing operand roles and does not
override handler legality:

- an operation without a Tile source has no source subview role;
- an operation without a Tile destination has no assemble role;
- source/destination arity and ordering come from the operation schema;
- dtype, layout, physical shape, valid shape, and definedness rules continue to
  reject invalid combinations;
- the generated producer-effect class MUST be rollback-safe or
  atomic-auxiliary. A nonrollback-auxiliary handler is rejected before
  `B.ASSEMBLE` body or auxiliary effects.

A singleton Shared issuer may publish one complete parent without
`B.ASSEMBLE`. A multi-PE Shared producer MUST use explicit contribution ranges,
non-overlap and complete-coverage checks, matching participant metadata, and
atomic LAST publication. Until that succeeds, the prior Shared generation
remains the only consumer-visible generation.

### 6.4 Raw binder-group invariants

Final lowering MUST preserve the PTO binder-group protocol:

- each modifier belongs only to the immediately preceding contiguous
  `B.IOT`/`B.IOS` group;
- source zero, source one, and destination modifiers appear in that semantic
  order;
- an omitted role is not synthesized, a duplicate role is illegal, and an
  intervening command closes the group;
- the backend derives the binder continuation/group-closure control needed to
  keep the modifier group open;
- for `B.IOT`, `L=1` closes the effective-binding sequence but still leaves its
  immediately associated modifier group available as required by ADR-0098;
- each binder is emitted together with its own modifiers before the next binder;
  a Shared `B.IOS` source always uses binder-local `SrcSelect=0`, even when the
  Shared value is operation operand ordinal one or later;
- a `B.IOS` source-one selection MUST NOT be used as a destination substitute;
- reserved raw fields are rejected before GPR reads or carrier updates;
- a raw-legal modifier under binder `PEMode=000` retains PTO's discarded-group
  behavior and MUST NOT acquire compiler-invented side effects.

### 6.5 Offset lowering

After layout normalization, the encoded offset is measured in CELL units. The
backend SHALL decompose an affine CELL offset into
`GPR[RegSrc] + ZeroExtend(uimm11)` without truncation:

- `RegSrc` MUST be an allocated absolute GPR selector in `R0..R23`;
- `uimm11` MUST be an unsigned value in `0..2047`;
- a constant may use `R0` plus the immediate when it fits;
- a larger or dynamic value may be materialized in an allocated GPR with
  `uimm11=0`, or split when exact equivalence is proved;
- failure to represent the expression exactly is a compile-time error.

The final derived range is checked against the owning PTO rule. Current
candidate ASL bounds Shared subview and Local/Shared assembly offsets to
`0..2047` CELLs, while the Local CUBE subview descriptor has a wider parent-
geometry bound. LLVM MUST apply the selected rule and MUST NOT impose one
invented universal offset limit.

For a Shared source subview, the allocated GPR denotes each participating PE's
private GPR value. LLVM MUST NOT replace that per-PE evaluation with one common
scalar value unless it proves the two semantics equivalent.

## 7. Assembly-session semantics

An assembly session is linear SSA state:

```text
S0 = assembly.begin(parent_descriptor, scope)
S1 = assembly.write(S0, region0, fragment0)
S2 = assembly.write(S1, region1, fragment1)
...
T  = assembly.commit(Sn)
```

The following rules are normative for the compiler contract:

- `assembly.begin` MUST create one unique session identity.
- `assembly.write` MUST consume the previous session value and produce the
  next session value.
- A session MUST NOT be copied, selected, frozen, stored to memory, returned
  through an unknown ABI, passed to an unknown call, or used after it is
  consumed.
- `assembly.commit` MUST consume the final session value.
- Every executable path from `begin` MUST reach exactly one `commit`. Runtime
  abort is outside v1; a later `assembly.abort` requires a separate architecture
  contract and is not inferred from ordinary control flow.
- Contributions in one session MUST have one compatible parent descriptor and
  scope.
- Statically provable overlap or incomplete coverage MUST be rejected.
- Unknown dynamic overlap or coverage MUST retain the PTO runtime checks; the
compiler MUST NOT treat lack of proof as proof of success.

A session PHI is legal only at a structured merge of mutually exclusive
predecessors when every incoming value has the same parent identity, scope,
descriptor, generation ordinal, and compatible contribution coverage. Generic
`select`, `freeze`, cast, call, or arbitrary PHI use is illegal.

`assembly.begin`, `assembly.write`, and `assembly.commit` are side-effecting,
`convergent`, and `noduplicate`. They are not CSE-able, speculatable, clonable,
or removable as dead code. The Linx region/session verifier runs immediately
after Clang CodeGen, after the main scalar optimization pipeline, and again
before instruction selection. Any generic transform that violates linearity or
crosses a control/convergence boundary makes the module invalid.

For a purely Local, non-escaping SSA Tile, the compiler may synthesize
`begin` before the first destination-region definition and `commit` at the
first whole-parent use when dominance and post-dominance make the boundary
unique. Mutable or externally visible Shared state MUST carry an explicit
session and commit in the programming model.

`commit` is a compiler marker, not a READY instruction and not an independent
ISA command. It assigns `LAST=1` to the last contribution on each valid path.
A post-LAST consumer may be emitted, but the architecture may still wait for
required Local cells. A Shared consumer may read only after both
`whole_parent_ready` and `published` are true; an incomplete or faulted
generation leaves the prior published generation visible.

## 8. Phase inference

The compiler derives raw phase bits for each contribution:

| Semantic position | `INIT` | `LAST` | `ParentSizeCode` |
| --- | ---: | ---: | --- |
| only contribution | 1 | 1 | parent size |
| first of multiple | 1 | 0 | parent size |
| middle | 0 | 0 | 0 |
| last of multiple | 0 | 1 | 0 |

The source API MUST NOT expose `first`, `middle`, `last`, or `single` as
required arguments. A raw expert-only API may expose exact bits for MC tests
and bring-up, but it MUST live in a clearly separate namespace and MUST NOT be
used by ordinary TileOP overloads.

Inference is permitted when the contribution order is unique in the compiler
CFG. Straight-line code and fully unrolled fixed-trip loops are the initial
required cases. Structured branches are legal only when every path produces
the same session metadata and reaches one commit. V1 rejects a dynamic
contribution count or a non-unrolled loop. Versioning plus first/last loop
peeling is a future extension with separate verifier and conformance work.

The compiler MUST fail closed for session escape, irreducible or multi-exit
control flow, interleaved may-alias sessions, unproved cross-function use, or
an ambiguous commit boundary.

## 9. CELL and SizeCode constraints

PTO range offsets are in 128 B CELL units. The range-modifier raw domain uses
SizeCode 1 through 12 for power-of-two capacities from 128 B through 256 KiB.
The writer binder and parent-generation domains remain subject to the Local/
Shared split and the upstream contradiction recorded in Section 2.

Direct lowering requires:

- a contiguous parent-layout interval;
- origin aligned to one CELL;
- encoded capacity exactly representable by an assigned SizeCode;
- destination contributions that do not overlap at CELL granularity;
- complete parent CELL coverage when `LAST=1`.

A logical value smaller than 128 B is not a direct encoded range. Examples in
the motivating sequence include 64 B row fragments and 32 B conversion
results. The compiler MUST use one of the legalization strategies in Section
5.3 or reject. In particular, it MUST NOT emit multiple sub-128 B destination
writers that alias the same CELL and then claim non-overlapping coverage.

The SuperNPUBench pattern
`Tile<..., kTm, 8, ..., kTm, 1>` is the preferred initial model: the physical
carrier is representable while valid shape records the logical one-column
value.

For v1, region origin may be a dynamic affine SSA expression. Extent, dtype,
layout, physical carrier shape, valid shape, parent capacity, scope kind, and
participant mask MUST be compile-time constants. A dynamic extent is legal only
after finite compiler versioning makes every emitted path select one constant
encoded SizeCode. Otherwise it is rejected.

## 10. LLVM IR contract

### 10.1 Types

The existing Tile type remains:

```llvm
%linx.tile = type target("linx.tile")
```

The implementation SHALL add opaque Local-parent, Shared-parent, non-storable
region, and linear session types. Parent handles carry storage/generation
identity; region values are borrow tokens and are not payload Tile values:

```llvm
%linx.tile.local.parent = type target("linx.tile.local.parent")
%linx.tile.shared.parent = type target("linx.tile.shared.parent")
%linx.tile.region = type target("linx.tile.region")
%linx.tile.assembly = type target("linx.tile.assembly")
```

The alias form above follows the checked-in `%linx.tile = type
target("linx.tile")` tests. The new target extension names are not accepted
until their LLVM type registration lands; the implementation PR MUST include
an `llvm-as`/`llvm-dis` round-trip before using these declarations as test
inputs.

Verifier rules MUST reject global variables, allocas, loads, stores, ABI
parameters, ABI returns, and bitcasts of `%linx.tile.region` and
`%linx.tile.assembly`. A region token may be consumed only by the matching
region-aware Tile-operation intrinsic operand. It cannot enter a generic Tile
PHI, copy, select, freeze, call, or existing whole-Tile intrinsic. Parent types
MUST NOT be encoded as user-visible raw integers.

### 10.2 Semantic intrinsics

The exact TableGen spelling may be refined during LLVM review, but the semantic
contract SHALL be equivalent to:

```llvm
declare %linx.tile.region @llvm.linx.tile.subview.local(
    %linx.tile %parent,
    i64 %origin0, i64 %extent0,
    i64 %origin1, i64 %extent1)

declare %linx.tile.region @llvm.linx.tile.subview.shared(
    %linx.tile.shared.parent %parent,
    i64 %origin0, i64 %extent0,
    i64 %origin1, i64 %extent1,
    i32 %scope_kind, i32 %participant_mask)

declare %linx.tile.local.parent @llvm.linx.tile.parent.create.local(
    i32 %location, i32 %layout, i32 %dtype,
    i64 %physical_rows, i64 %physical_cols,
    i64 %valid_rows, i64 %valid_cols, i64 %capacity_bytes,
    i64 %cube_cell_count, i64 %cube_k_repeat)

declare %linx.tile.shared.parent @llvm.linx.tile.parent.allocate.shared(
    i32 %location, i32 %layout, i32 %dtype,
    i64 %physical_rows, i64 %physical_cols,
    i64 %valid_rows, i64 %valid_cols, i64 %capacity_bytes)

declare %linx.tile.assembly @llvm.linx.tile.assembly.begin.local(
    %linx.tile.local.parent %parent,
    i32 %scope_kind, i32 %participant_mask)

declare %linx.tile.assembly @llvm.linx.tile.assembly.begin.shared(
    %linx.tile.shared.parent %parent,
    i32 %scope_kind, i32 %participant_mask)

declare %linx.tile @llvm.linx.tileop.unary.region(
    %linx.tile.region %source,
    i32 %operation, <operation-specific semantic attributes>)

declare %linx.tile.assembly @llvm.linx.tile.assembly.write(
    %linx.tile.assembly %session, %linx.tile %fragment,
    i64 %origin0, i64 %extent0,
    i64 %origin1, i64 %extent1)

declare { %linx.tile.assembly, %linx.tile.assembly }
    @llvm.linx.tileop.<operation>.write2(
        <operation sources and semantic attributes>,
        %linx.tile.assembly %session0,
        %linx.tile.assembly %session1,
        <two normalized destination regions>)

declare %linx.tile @llvm.linx.tile.assembly.commit.local(
    %linx.tile.assembly %session)

declare %linx.tile.shared.parent @llvm.linx.tile.assembly.commit.shared(
    %linx.tile.assembly %session)
```

Rank-generic production signatures may use a descriptor aggregate or metadata,
provided origins remain ordinary SSA values, v1 extents/descriptors remain
constants, and parent/session identity is not hidden in opaque inline assembly.
Every session intrinsic, every Shared source-region intrinsic, and every
region-aware Tile-operation consumer is `convergent` and `noduplicate` and
carries the current LLVM `convergencectrl` token as an operand bundle. A Shared
subview and its consuming Tile operation MUST use the same domain. The token
supplies the opaque execution/convergence identity; it is not a C-visible
integer.

A parent descriptor is frozen by the defining TLOAD/result, `create.local`, or
`allocate.shared` intrinsic. Later subview, begin, write, and commit intrinsics
read that frozen descriptor and MUST NOT accept a caller-supplied replacement.
The verifier rejects a parent whose provenance or descriptor cannot be traced
uniquely. Local CUBE descriptors include Matrix location, CUBE layout, valid
shape, capacity, `cube_cell_count`, and `cube_k_repeat`; CELL row/column
geometry is derived by the canonical PTO layout/dtype helpers and checked
against the frozen fields.

Generated `tileop.<operation>.writeN` forms cover multi-output operation arity.
They are the single producer and directly consume all destination sessions and
regions while producing all successor sessions; there are no independently
produced fragment values that could be mistaken for separate operations. Their
struct result MUST be immediately split with one `extractvalue` per successor
session; it cannot be stored, selected, duplicated, or partially consumed. All
outputs are one operation transaction and reach MachineIR as one multi-
destination pseudo.

`begin.local` and `begin.shared` take logical descriptor fields. SizeCode is
derived later and is absent from this semantic interface. `commit.local`
returns an operation-consumable whole-parent Tile value whose defining
intrinsic carries the assembled descriptor and parent identity. It does not
perform an LLVM payload copy. `commit.shared` returns the same Shared parent
identity with a new published-generation dependency, which can feed
`subview.shared`; it does not copy Shared payload into a Local Tile.

`tile.subview` produces a semantic borrow token and MUST be folded into the
consuming region-aware Tile operation's source binder. The verifier rejects
escape or materialization as a new architectural Tile. `assembly.write` MUST be
folded into the fragment's
unique producing Tile operation when legal. If fusion is impossible, the
compiler may use an exact `TMOV`/rearrangement sequence, or it MUST diagnose the
unsupported case.

### 10.3 Pass placement

The initial implementation SHALL add an IR verifier/canonicalization pass
before instruction selection, then extend the existing machine pipeline:

1. verify and normalize regions and linear sessions;
2. infer contribution phases and prove static coverage/non-overlap;
3. select ordinary Tile operation pseudos with attached source/destination
   region metadata;
4. preserve explicit region/session pseudo operands through
   `LinxISATileSSABalance`;
5. extend `LinxISABlockify` to emit each binder followed immediately by that
   binder's contiguous `B.SUBVIEW` modifiers in binder-local source-role order
   and its destination `B.ASSEMBLE` modifier;
6. lower exact PTO 0.58.4 MC encodings.

The selected machine pseudos SHALL carry, as explicit operands rather than
discardable debug metadata:

- one normalized source-region record for each Tile source role;
- the destination session virtual register and normalized contribution region;
- Local/Shared parent kind, descriptor fields, and scope;
- the derived phase only after the session analysis succeeds.

The MachineVerifier extension MUST reject a region attached to a non-Tile role,
lost session def-use, source-role reordering, or a pseudo whose binder and
modifier group cannot be emitted atomically. `LinxISABlockify` MUST build the
binder and all contiguous modifiers as one lowering unit; it MUST diagnose
rather than schedule or split an intervening command into that group.

Operation roles come from a generated Linx Tile-operation schema keyed by the
canonical operation identity. The schema MUST identify Tile source ordinals,
scalar/descriptor operands, destination arity, engine, and operation-specific
descriptor legality, plus the generated rollback-safe/atomic/nonrollback
effect class. Operand position alone is used only after validation against that
schema.

For direct producer fusion, a fragment MUST have one `assembly.write` use and
that write's session carries the destination parent identity. A fragment with
multiple uses requires an exact materialization/copy plan; otherwise the
compiler MUST reject it. This extends the current compiler architecture. It
does not reintroduce the old LinxV5 Tile-call ABI.

### 10.4 Minimal C-to-IR shape

After the new Clang types and LLVM target extension types are registered, the
smallest plain-C path SHALL have this shape:

```c
linx_tile_t reduce_into_parent(void const *base) {
  const linx_tile_descriptor_t desc = LINX_TILE_DESC_CUBE_BF16(8, 32);
  const linx_tile_scope_t scope = LINX_TILE_SCOPE_ALL_PES;
  linx_tile_region2d_t in = {0, 4, 0, 32};
  linx_tile_region2d_t out = {0, 4, 0, 1};
  linx_tile_t src = __builtin_linx_tile_load_semantic(base, desc);
  linx_local_tile_parent_t dst = __builtin_linx_tile_parent_local(desc);
  linx_tile_region_token_t part =
      __builtin_linx_tile_subview_local(src, in);
  linx_tile_t fragment =
      __builtin_linx_sfu_trowmax_region(part);
  linx_tile_assembly_t s0 =
      __builtin_linx_tile_assembly_begin_local(dst, scope);
  linx_tile_assembly_t s1 =
      __builtin_linx_tile_assembly_write(s0, out, fragment);
  return __builtin_linx_tile_assembly_commit_local(s1);
}
```

The expected semantic IR is:

```llvm
%part = call target("linx.tile.region") @llvm.linx.tile.subview.local(...)
%fragment = call target("linx.tile") @llvm.linx.tileop.unary.region(...)
%s0 = call target("linx.tile.assembly")
    @llvm.linx.tile.assembly.begin.local(...)
%s1 = call target("linx.tile.assembly")
    @llvm.linx.tile.assembly.write(
        target("linx.tile.assembly") %s0,
        target("linx.tile") %fragment, ...)
%whole = call target("linx.tile")
    @llvm.linx.tile.assembly.commit.local(
        target("linx.tile.assembly") %s1)
```

The implementation tests MUST replace ellipses with complete declarations and
pass Clang CodeGen, `llvm-as`, `opt -passes=verify`, `llc`, integrated assembly,
and object disassembly. This design document does not claim that the unlanded
types compile in the 0.58.3 toolchain.

## 11. C and C++ programming-model contract

### 11.1 Plain C semantic surface

The first implementation is rank-2. Plain C MUST be able to reach the same
rank-2 semantic intrinsics as C++. Higher-rank regions require a later
rank-generic descriptor and are not silently flattened by this API. The rank-2
POD descriptor is:

```c
#include <stdint.h>

typedef struct {
  uint64_t row_begin;
  uint64_t row_extent;
  uint64_t col_begin;
  uint64_t col_extent;
} linx_tile_region2d_t;

typedef struct {
  uint32_t location;
  uint32_t dtype;
  uint32_t layout;
  uint32_t reserved;
  uint64_t physical_rows;
  uint64_t physical_cols;
  uint64_t valid_rows;
  uint64_t valid_cols;
  uint64_t capacity_bytes;
  uint64_t cube_cell_count;
  uint64_t cube_k_repeat;
} linx_tile_descriptor_t;

typedef enum {
  LINX_TILE_SCOPE_LOCAL_PE = 0,
  LINX_TILE_SCOPE_PE_GROUP = 1,
  LINX_TILE_SCOPE_CORE_SHARED = 2
} linx_tile_scope_kind_t;

typedef struct {
  linx_tile_scope_kind_t kind;
  uint32_t participant_mask;
} linx_tile_scope_t;
```

`uint64_t` is required in both linx32 and linx64 lanes. The dimension order is
logical row then logical column; layout linearization occurs in LLVM. In v1,
descriptor fields, region extents, scope kind, and participant mask are
required constant expressions. `participant_mask` is semantic and must map
exactly to an assigned PTO participation mode; it is not a raw PEMode field.
`location` distinguishes semantic Local Vector and Matrix locations. A Local
CUBE parent MUST use Matrix location and a CUBE layout. Its
`cube_cell_count`/`cube_k_repeat` MUST match the canonical PTO geometry derived
from dtype, layout, physical shape, and valid shape; CELL row/column geometry
is derived by the same PTO helpers. Non-CUBE descriptors set the CUBE-only
fields to zero.

Header forms such as `LINX_TILE_DESC_CUBE_BF16(rows, cols)` and
`LINX_TILE_SCOPE_ALL_PES` are compile-time constant initializers generated from
the locked PTO descriptor helpers. They are not runtime functions and cannot
override a parent descriptor after creation.

These are Clang builtin signatures, not external C functions and not linkable
ABI symbols. Clang Sema recognizes their special non-addressable types and
CodeGen lowers them directly to LLVM intrinsics. They SHALL be semantically
equivalent to:

```c
linx_local_tile_parent_t __builtin_linx_tile_parent_local(
    linx_tile_descriptor_t descriptor);

linx_shared_tile_parent_t __builtin_linx_shared_tile_allocate(
    linx_tile_descriptor_t descriptor);

linx_tile_t __builtin_linx_tile_load_semantic(
    void const *base, linx_tile_descriptor_t descriptor);

linx_tile_region_token_t __builtin_linx_tile_subview_local(
    linx_tile_t parent, linx_tile_region2d_t region);

linx_tile_region_token_t __builtin_linx_tile_subview_shared(
    linx_shared_tile_parent_t parent, linx_tile_region2d_t region,
    linx_tile_scope_t scope);

linx_tile_t __builtin_linx_sfu_trowmax_region(
    linx_tile_region_token_t source);

linx_tile_assembly_t __builtin_linx_tile_assembly_begin_local(
    linx_local_tile_parent_t parent, linx_tile_scope_t scope);

linx_tile_assembly_t __builtin_linx_tile_assembly_begin_shared(
    linx_shared_tile_parent_t parent, linx_tile_scope_t scope);

linx_tile_assembly_t __builtin_linx_tile_assembly_write(
    linx_tile_assembly_t session, linx_tile_region2d_t region,
    linx_tile_t fragment);

linx_tile_t __builtin_linx_tile_assembly_commit_local(
    linx_tile_assembly_t session);

linx_shared_tile_parent_t __builtin_linx_tile_assembly_commit_shared(
    linx_tile_assembly_t session);
```

The transition bridge for `linx_tile_t` is exactly the existing 4096-byte
frontend carrier, for example `typedef int linx_tile_t
__attribute__((vector_size(4096)))`, and uses the existing Linx Tile calling
convention/register class. It is converted by CodeGen to the semantic Tile
intrinsic surface; no memory ABI for architectural Tile payload is introduced.
The long-term surface SHOULD expose a Clang opaque Tile type.

`linx_tile_region_token_t`, `linx_tile_assembly_t`,
`linx_local_tile_parent_t`, and
`linx_shared_tile_parent_t` are builtin-only AST types. User code may bind the
returned value to an automatic variable and pass it only to the corresponding
builtin, but may not apply `sizeof`, `_Alignof`, address-of, pointer, array,
field, union, cast, varargs, `_Generic`, load/store, or external ABI operations.
A Local parent is created by `__builtin_linx_tile_parent_local`. A Shared parent
is created by `__builtin_linx_shared_tile_allocate`, which allocates and binds
one compiler-managed absolute Shared identity in the current Core. Allocation
freezes the descriptor but not a participant mask. The producer mask belongs
to each `begin.shared` generation; the consumer mask belongs to each Shared
subview/use, and neither changes Shared object identity. Later builtins read the
frozen descriptor and do not accept a replacement. Handles are function-local,
non-addressable, and non-copyable. Shared commit returns the same identity with
a new generation dependency, still subject to Shared readiness and publication
rules.

### 11.2 C++ zero-semantics wrappers

C++17 wrappers SHALL be type-safe sugar over the C/builtin/intrinsic surface,
matching the current superproject C++ baseline. A later optional layer may use
C++20 concepts, but the required API MUST NOT depend on them. The wrappers
MUST compile with exceptions and RTTI disabled and MUST NOT require dynamic
allocation.
They MUST NOT contain a separate inline-assembly implementation.

The following declarations show the required source shape; their bodies call
the Clang builtins above:

```cpp
struct all_t {};
inline constexpr all_t all{};

struct index {
  uint64_t value;
};

struct span {
  uint64_t begin;
  uint64_t extent;
};

template<class RowSelector, class ColSelector>
struct slice2d {
  RowSelector row;
  ColSelector col;
};

auto src_part = view(src)[slice2d{all, span{4 * g, 4}}];

assembly<parent_tile> dst(local_parent, descriptor, scope);
TROWMAX(dst[slice2d{all, index{g}}], src_part);
auto whole = dst.commit();
```

C++ cannot support Python colon tokens inside `operator[]`; `tile[:, a:b]` is
compiler IR/pseudo-assembly notation. The C++ API uses `all`, `index`, and
`span` values inside brackets.

The bracket operator SHOULD exist on dedicated `view` and `assembly` proxies,
not on the general Tile value, so element indexing, source views, and
destination contributions remain distinct types.

## 12. Worked lowering examples

### 12.1 Direct source subview

Compiler-facing input with an ordinary fragment destination:

```text
%f64 = TROWMAX <4,32,4,BF16> %T2[:, 4*g:4*g+4]
```

Suppose layout proof establishes that the source is one aligned 256 B interval.
The fragment result uses the operation's normal physical/valid descriptor.

The backend emits the conceptual sequence:

```text
BSTART.SFU ... TROWMAX
B.IOT ... source0=T2, destination=fragment, SizeCode=<legal Local writer code>
B.SUBVIEW SrcSelect=0, RegSrc=<allocated>, uimm11=<folded>, SubviewSizeCode=2
```

This example demonstrates source lowering only. The exact binder spelling and
fields come from the future locked PTO release.

### 12.2 Sub-CELL destination rejection

The motivating destination:

```text
%s1 = TROWMAX <4,32,4,BF16> %T2[:, 4*g:4*g+4] -> %s0[:, g]<64B>
```

MUST NOT directly emit one 128 B `B.ASSEMBLE` writer. Adjacent `g` values would
cover the same CELL even though their logical 64 B results differ. A padded
valid shape alone does not make two independent writers non-overlapping. The
compiler emits `linx.tile.region.encoding.subcell-writer` unless it performs an
exact legalization that creates one real CELL-sized fragment.

### 12.3 Legal explicit packing

Two original reduction domains remain independent. They first produce their
own logical results:

```text
%f0 = TROWMAX <4,32,4,BF16> %T2[:, 8*h:8*h+4]
%f1 = TROWMAX <4,32,4,BF16> %T2[:, 8*h+4:8*h+8]
%f128 = TILE.PACK128 %f0<64B>, %f1<64B>
%s1 = TILE.ASSEMBLY.WRITE %s0[:, 2*h:2*h+2], %f128<128B>
```

`TILE.PACK128` is compiler semantic notation, not a new PTO instruction. It
MUST lower to an assigned operation such as an exact `TINSERT` sequence, or to
another reviewed packing/rearrangement contract that creates one fully defined
128 B carrier while preserving both 64 B values. If no assigned operation and
descriptor combination can prove that result, legalization fails.

Only `%f128` is the assembly writer. The two reduction fragments do not each
claim CELL coverage. The backend therefore emits one destination binder and
one `B.ASSEMBLE` for the 128 B carrier.

The pseudo-assembly destination name/session is never repeated in
`B.ASSEMBLE`; the immediately preceding binder carries it.

## 13. Diagnostics

The compiler SHALL provide stable diagnostics for at least:

- region rank mismatch;
- negative or zero extent;
- non-affine region where the selected lowering requires affine form;
- region out of parent bounds;
- layout-discontiguous region;
- CELL misalignment;
- extent not representable by a legal SizeCode;
- sub-CELL region not legalizable;
- source/destination role mismatch;
- dtype, layout, physical-shape, or valid-shape incompatibility;
- assembly contribution overlap;
- incomplete coverage at commit;
- session copy, escape, use-after-consume, or missing commit;
- ambiguous phase inference across control flow;
- unsupported dynamic or cross-function session;
- Shared scope or participant mismatch;
- target release without PTO 0.58.4 range support.

Diagnostics MUST identify the operation, operand role, normalized region,
required alignment/extent, and selected target release.

Diagnostic ownership is:

- Clang Sema `err_linx_tile_region_*`: builtin availability, Local/Shared type
  mismatch, rank, zero/negative constant extent, forbidden session/parent type
  operations, and compile-time descriptor contradictions;
- LLVM verifier `linx.tile.region.*`: malformed region intrinsics, session
  non-linearity, escape, use-after-consume, missing/multiple commit, and schema
  role mismatch;
- region/session canonicalization `linx.tile.region.lowering.*`: affine proof,
  CFG phase inference, static overlap, and static coverage;
- ISel/Blockify `linx.tile.region.encoding.*`: CELL linearization, SizeCode,
  GPR/uimm decomposition, modifier order, and atomic binder-group emission.

A non-constant origin is accepted when the applicable layer can preserve exact
runtime PTO checks and derive an unambiguous GPR/uimm encoding. A non-constant
extent is rejected in v1 unless finite versioning converts every emitted path
to a constant descriptor and SizeCode. Otherwise the owning layer emits its
stable diagnostic.

### 13.1 Version and object compatibility

The first implementation SHALL use intrinsic schema revision
`linx.tile.region.v1` and expose C/C++ feature macro
`__LINX_PTO_0584_RANGE__` only when the exact target feature is enabled.

Objects containing region lowering MUST carry the future exact
`.note.pto.isa` identity selected by the locked PTO release. LTO and LLD MUST
fail closed on missing, 0.58.3, mixed, or mismatched identities. Region
intrinsics compiled for a 0.58.3 target receive a stable unsupported-feature
diagnostic. The compiler MUST NOT silently fall back to opaque inline assembly,
the raw expert wrapper, or a different SizeCode domain.

## 14. Validation and conformance gates

An implementation is not complete until all applicable gates pass on one exact
SHA manifest:

### PTO and MC

- exact `B.SUBVIEW` and `B.ASSEMBLE` encode/decode/objdump tests;
- reserved RegSrc, SizeCode, `INIT`/ParentSizeCode, association, ordering, and
  zero-PE-mode negative tests;
- standalone `llvm-mc` and Clang integrated-assembler coverage.

### LLVM IR and CodeGen

- verifier tests for region and linear-session rules;
- phase inference for single, first/middle/last, straight-line, branch, fixed
  loop, and rejected dynamic/escaping cases;
- source0/source1 independence and different `i`/`j`/`k` expressions;
- multi-output operations and destination-session arity;
- Shared operation ordinal versus binder-local `SrcSelect=0`;
- Tile PHI/copy preservation through `LinxISATileSSABalance`;
- legal structured session PHI plus rejected select/freeze/clone/CSE/DCE;
- `LinxISABlockify` adjacency, `B.IOT.L`, per-binder modifier grouping, and
  role-order checks;
- plain-C and C++ builtin CodeGen tests;
- LTO and LLD mixed-version fail-closed tests;
- linx32 and linx64 compile AVS coverage.

### Runtime and model

- Local generation non-overlap, full coverage, readiness, replay,
  fault/rollback, restart, and atomic publication;
- Shared collective generation, participant agreement, prior-generation
  preservation, and atomic publication;
- per-PE Shared source offsets with different GPR values;
- operation-specific descriptor legality across VEC, SFU, TLSU, and CUBE;
- complete operation × operand-role × generated effect-class matrix;
- exact sub-CELL legalization results for padded and rearranged carriers.

### Workloads

- SuperNPUBench `MultiTile` and fully unrolled patterns;
- row-max/row-sum physical `[kTm,8]`, valid `[kTm,1]` sentinels;
- FlashAttention/softmax plus final matrix multiplication;
- a negative discontiguous rectangle and overlapping assembly case;
- pin and external lanes with exact LLVM, TileOP, PTO-SPEC, QEMU, and model
  SHAs.

## 15. Implementation stages

### Stage A: architecture and MC

- resolve the Local SizeCode contract/catalog/ASL/AVS contradiction upstream;
- close PTO candidate exact-head release readiness;
- lock the resulting immutable PTO 0.58.4/0.58.4.1 source SHA in LinxISA;
- import exact command forms and feature identity;
- implement MC/parser/disassembler support and negative tests.

### Stage B: LLVM semantic IR

- add region/session types, intrinsics, verifier, and canonicalization;
- add phase/coverage analysis;
- extend machine pseudos, Tile SSA preservation, and block construction.

### Stage C: C and C++ frontend

- add plain-C builtins and CodeGen tests;
- implement C++ `view[...]` and `assembly[...]` proxies as zero-semantics
  wrappers;
- retain raw encoding wrappers only under an expert namespace.

### Stage D: workload migration

- port one bounded SuperNPUBench softmax/matmul path;
- compare direct-region lowering with the existing `MultiTile` baseline;
- expand only after compiler/QEMU/model parity is exact.

No TileOP implementation PR may be merged before Stages A and B provide a
matching compiler and object-level proof.

## 16. Open items

- Confirm whether the requested LLVM `level-one` branch is the public
  `bisheng-linx` snapshot or supply the exact alternative SHA.
- Decide the production spelling and verifier representation of the linear
  assembly-session target extension type.
- Define which Local and Shared descriptor/layout combinations Linx exposes
  from the complete PTO legality matrix.
- Freeze the first supported dynamic-loop transformation subset.
- Decide whether direct `assembly.write` without a producing Tile operation is
  represented by TMOV or rejected in the first release.
