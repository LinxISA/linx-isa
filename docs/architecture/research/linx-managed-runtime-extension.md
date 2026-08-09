# LinxISA Experimental Managed Runtime Extension

Status: experimental design note

Audience: ISA, compiler, emulator, RTL, OS/runtime, JIT, interpreter, and GC
owners

## 1. Purpose

This document records research findings and an experimental LinxISA extension
proposal for managed runtimes: JVM-style virtual machines, bytecode
interpreters, JavaScript/Python/Ruby-style dynamic-language engines, and
garbage-collected JIT runtimes.

The proposed extension is named `Zdyn` in this note. `Zdyn` is not a hardware
JVM and is not a language-specific bytecode ISA. It is a small managed-runtime
assist layer for the operations that repeatedly dominate dynamic runtimes:

- tag, shape, class, and null guards;
- checked loads and fast object/property access;
- inline-cache lookup and miss routing;
- bytecode dispatch and quickened/specialized dispatch;
- deoptimization and precise frame materialization;
- allocation fast paths;
- garbage-collector write barriers, read barriers, and safepoints;
- runtime metadata lookup under ACR-controlled authority.

The design reuses existing Linx mechanisms wherever possible: block-structured
control flow, template-block restartability, Access Control Rings (ACR),
unmanaged `BSTART.SYS FALL<, fixup_label` fixup blocks, ClockHands, the 64-GPR
extension, and the DBT translation-map pattern from `linx-dbt-extension.md`.

## 2. Research Findings

The useful ISA support for dynamic languages is not a large bytecode execution
engine. The strongest recurring result from prior systems is that small,
well-placed architectural support around type checks, object access, dispatch,
and runtime barriers is easier to generalize and safer to implement than a
language-specific bytecode mode.

| Research area | Finding | Implication for LinxISA |
| --- | --- | --- |
| Inline caches and quickening | Monomorphic and polymorphic inline caches make dynamic dispatch fast by caching receiver-shape/type decisions at call or property-access sites. Quickening rewrites generic bytecodes into specialized forms after observing runtime types. | Add an inline-cache map and miss trap, not fixed language bytecodes. Keep `site_id`, receiver shape/type, target block, and metadata in runtime-owned tables. |
| Checked loads | Checked Load style support combines object access with a type/shape check and can reduce dynamic-language property access overhead. | Add `DYN.CHECKLD.*` as the highest-value data-path instruction: load plus check plus precise deopt/fixup on mismatch. |
| Interpreter dispatch | Direct-threaded dispatch and dispatch prediction reduce VM branch overhead, but indirect branches remain expensive and hard for predictors. | Add a restartable `DYN.DISPATCH` terminal template that maps bytecode PC/opcode/profile to a legal Linx block target. |
| Garbage-collector barriers | Barrier cost is workload- and collector-dependent. Store/write barriers, SATB barriers, card marks, colored-pointer read barriers, and compressed references have different costs. | Do not bake in one GC algorithm. Add barrier-profiled instructions whose exact fast path is selected by runtime profile fields. |
| Hardware bytecode engines | Historical Java bytecode hardware and ISA modes reduced some dispatch overhead but were brittle as VM designs changed. | Avoid a JVM-only instruction set. Keep the architectural contract at object, guard, dispatch, barrier, and metadata-map level. |
| Safepoints and deopt | Optimizing JITs need precise state reconstruction at guards, calls, backedges, allocation slow paths, and GC polls. | Every `Zdyn` trap must carry enough `deopt_id`, bytecode/native PC, and runtime context to reconstruct interpreter-visible state. |

Research anchors:

- Checked Load for accelerating dynamic-language object access:
  <https://homes.cs.washington.edu/~luisceze/publications/anderson-hpca2011.pdf>
- Inline Caching Meets Quickening:
  <https://publications.sba-research.org/publications/ecoop10.pdf>
- Polymorphic Inline Caches:
  <https://bibliography.selflanguage.org/_static/pics.pdf>
- Efficient Interpreters:
  <https://jilp.org/vol5/v5paper12.pdf>
- Short-circuit dispatch for virtual-machine interpreters:
  <https://channoh.github.io/pubs/isca16_scd.pdf>
- Typed architectures for dynamically typed languages:
  <https://channoh.github.io/pubs/asplos17-typed.pdf>
- Barriers: Friend or Foe:
  <https://www.steveblackburn.org/pubs/papers/wb-ismm-2004.pdf>
- OpenJDK ZGC JEP 333:
  <https://openjdk.org/jeps/333>
- OpenJDK Generational ZGC JEP 439:
  <https://openjdk.org/jeps/439>
- Python specializing adaptive interpreter PEP 659:
  <https://peps.python.org/pep-0659/>

## 3. Existing Linx Mechanisms To Reuse

### 3.1 Block-Structured Control Flow

Linx already requires every architectural control-flow target to be a legal
block start marker. `Zdyn` must preserve this rule.

Required rule:

```text
Managed-runtime dispatch, inline-cache calls, deopt returns, and barrier slow
paths must branch only to legal Linx block start markers or standalone template
blocks.
```

`Zdyn` must not add an unchecked "jump to runtime target" instruction. Any
runtime map entry that returns a native target must still validate the target as
a legal block start before transfer.

### 3.2 Template Restartability

Linx template blocks already provide restart and resume rules through
`BSTATE.Template`, `EBSTATE`, and `ACRE RRAT_RESTORE`. This is the right model
for runtime operations that may trap and retry:

- inline-cache terminal calls;
- bytecode dispatch;
- allocation fast paths;
- safepoint polls;
- deopt entries.

A `Zdyn` terminal template must not re-execute the JIT block body after a miss
or runtime trap. On `ACRE RRAT_RESTORE`, it resumes or retries only the
template operation.

### 3.3 Access Control Rings

Linx ACRs already separate execution authority. `Zdyn` should use derived ACR
states instead of defining a separate privilege hierarchy.

Managed JIT code and the runtime handler do not have the same authority:

- managed code may execute guards, barriers, checked loads, dispatch templates,
  and inline-cache lookups;
- runtime handler code may install inline-cache entries, publish generated code,
  update deopt metadata, modify GC barrier configuration, and patch dispatch
  tables.

The extension therefore defines `DYN_CODE` and `DYN_HANDLER` as ACR-scoped
states, analogous to the DBT `BT_CODE` and `BT_HANDLER` model.

### 3.4 Unmanaged FIXUP Blocks

Strict v0.57 already defines unmanaged fixup blocks as:

```text
BSTART.SYS FALL<, fixup_label
```

If a synchronous exception occurs inside such a block, the CPU routes to the
fixup target without changing ACR. This is valuable for frequent local managed
runtime slow paths:

- guard failure that can branch to a local deopt stub;
- checked-load mismatch that can branch to a local inline-cache miss stub;
- TLAB allocation failure that can branch to a local runtime call stub;
- optional barrier slow path that can branch to a local stub.

`Zdyn` should use FIXUP only for local control repair in the same privilege
context. Operations that need authority to mutate runtime maps, publish code,
or coordinate GC must use ACR service routing.

### 3.5 64-GPR Extension

Managed runtimes are register-pressure heavy. A JVM/JIT frame often keeps
thread state, heap base, bytecode PC, frame state, dispatch table, inline-cache
metadata, object temporaries, and multiple live language values at the same
time.

The 64-GPR extension from `linx-64-gpr-extension.md` is therefore the recommended
profile for `Zdyn`. It reduces environment-object spills and makes runtime
helpers less destructive to hot JIT state. Existing 5-bit ordinary instruction
formats can still access high registers through `c.gget` and `c.gset`.

### 3.6 DBT Map Pattern

The DBT proposal defines a useful pattern:

```text
runtime context + guest/runtime key -> legal native Linx block target
```

`Zdyn` should reuse that model for inline caches, dispatch targets, deopt
metadata, and code publication. The exact backing store can be a hardware cache,
runtime memory table, emulator table, or a hybrid. The architectural rule is
that only handler authority can publish trusted executable targets.

## 4. Design Principles

`Zdyn` should follow these principles:

- Reuse `BSTART.STD`, `BSTART.SYS`, template blocks, ACR, FIXUP, and ClockHands
  before adding new control-flow forms.
- Accelerate common dynamic-runtime primitives, not whole language bytecodes.
- Keep every target validated by the existing block-start safety rule.
- Make slow paths precise and restartable.
- Keep runtime policy in profiles and metadata tables, not in hard-coded
  language-specific opcodes.
- Require explicit handler authority for map mutation and generated-code
  publication.
- Make the first implementation useful in QEMU before requiring large hardware
  structures.

Non-goals:

- no dedicated JVM bytecode execution mode;
- no unchecked indirect branch;
- no overloading of `BSTART.FIXP`;
- no ad-hoc semantics in reserved TLSU/CUBE/TEPL-carrier selector space;
- no requirement that hardware understand a specific object model such as
  HotSpot, V8, CPython, or Ruby internally.

## 5. Extension Summary

The recommended `Zdyn` extension family is:

| Extension part | Purpose | First implementation |
| --- | --- | --- |
| `Zdyn.base` | Runtime context SSRs, handler vector, trap causes, map namespace, permission model | Required |
| `Zdyn.guard` | Tag, shape, class, null, bounds, and equality guards with deopt/fixup metadata | Required |
| `Zdyn.checkld` | Checked loads for object field/property access | Required |
| `Zdyn.ic` | Inline-cache probe, terminal call, map install/invalidate | Required |
| `Zdyn.dispatch` | Bytecode/opcode dispatch terminal template | Required for interpreters |
| `Zdyn.deopt` | Explicit deopt trap and deopt metadata reporting | Required |
| `Zdyn.gc` | TLAB allocation, write barriers, read barriers, card marks, safepoints | Required for GC runtimes |
| `Zdyn.gpr64` | Private `linx64dyn` 64-GPR managed-runtime profile | Recommended |
| `Zdyn.debug` | Trace/probe instructions and metadata sections | Optional |

The mandatory first subset should be small:

1. `DYNCFG`, `DYNVEC`, `DYNCTX`, and `DYNMISS_*` SSRs.
2. `DYN.GUARD.*` and `DYN.CHECKLD.*`.
3. `DYN.IC.PROBE` and restartable `DYN.CALLIC`.
4. `DYN.DISPATCH`.
5. `DYNMAP.INS`, `DYNMAP.INV`, `DYNMAP.INVCTX`, and `DYNMAP.FENCE`.
6. `DYN.TLAB.ALLOC`, `DYN.WB.ST`, `DYN.REF.LD`, and `DYN.SAFEPOINT`.

## 6. Managed Runtime ACR State

### 6.1 ACR Placement

The ISA should not hard-code one universal ACR number for managed runtimes.
Each platform profile binds a pair of comparable ACRs:

| Role | Meaning |
| --- | --- |
| `DYN_CODE_ACR` | ACR used by managed JIT or interpreter fast-path code. |
| `DYN_HANDLER_ACR` | More-privileged ACR used by runtime handlers. |

Required ordering:

```text
DYN_HANDLER_ACR p> DYN_CODE_ACR
```

Example user-mode runtime profile:

| ACR | Example role |
| --- | --- |
| `ACR1` | Host OS. |
| `ACR2` | Native host user process. |
| `ACR5` | Managed runtime handler for one process. |
| `ACR6` | Managed JIT/interpreter code for that handler. |

This example is illustrative only. A system may choose different ACRs.

### 6.2 Derived Execution States

`Zdyn` defines two derived states:

| State | Derivation | Meaning |
| --- | --- | --- |
| `DYN_CODE` | `CSTATE.ACR == DYNCFG.CodeACR` and `DYNCFG.EN = 1` | Managed fast-path code is executing. |
| `DYN_HANDLER` | `CSTATE.ACR == DYNCFG.HandlerACR` and `DYNCFG.EN = 1` | Runtime handler code is executing with metadata/map authority. |

These are architectural states derived from ACR configuration. They are not a
new ring hierarchy.

## 7. Managed Runtime SSRs

The following SSR names are provisional. They should be allocated from
ACR-scoped SSR space if the extension is promoted.

### 7.1 `DYNCFG_ACRn`

`DYNCFG_ACRn` configures managed-runtime support for one ACR pair.

| Field | Meaning |
| --- | --- |
| `EN` | Enables `Zdyn` instructions and traps for the configured runtime context. |
| `RuntimeKind` | `0=reserved`, `1=JVM`, `2=JavaScript`, `3=Python`, `4=Ruby`, `5=Wasm-gc`, others profile-defined. |
| `CodeACR` | ACR that may execute `DYN_CODE`. |
| `HandlerACR` | ACR that receives runtime service traps. |
| `Profile` | Managed runtime ABI/object profile, initially `1=linx64dyn`. |
| `GuardPolicy` | Controls guard failure routing and fixup eligibility. |
| `GCProfile` | Selects write/read barrier and reference encoding profiles. |
| `StrictTarget` | If set, runtime-map targets must carry managed-code metadata in addition to being legal block starts. |
| `MapPolicy` | `0=trap on miss`, `1=branch to software dispatcher`, others reserved. |

Only a more-privileged managing ACR may write `DYNCFG`.

### 7.2 `DYNVEC_ACRn`

`DYNVEC_ACRn` is the managed-runtime handler vector. It must point to a legal
Linx block start in `DYN_HANDLER_ACR`.

On a `Zdyn` service event, hardware vectors `BPC` to `DYNVEC_ACRn` while using
the normal `SERVICE_REQUEST` save protocol. `TRAPARG0_ACRn` should retain the
native source PC/TPC. `DYNMISS_*` registers carry managed-runtime keys.

### 7.3 `DYNCTX_ACRn`

`DYNCTX_ACRn` identifies the active managed-runtime context.

| Field | Meaning |
| --- | --- |
| `CtxID` | Runtime context ID, similar to a code-cache ASID. |
| `MapGen` | Runtime-map generation, incremented on invalidation. |
| `HeapID` | Active heap identity for GC barrier profile selection. |
| `ThreadID` | Runtime thread identity if not held in a GPR. |
| `DeoptTable` | Profile-defined pointer or selector for deopt metadata. |
| `ICRoot` | Profile-defined pointer or selector for inline-cache metadata. |
| `DispatchRoot` | Profile-defined pointer or selector for bytecode dispatch metadata. |

`DYNMAP` lookup keys include `CtxID`, `RuntimeKind`, `MapGen`, map kind, site
ID, and a profile-defined receiver key.

### 7.4 `DYNMISS_*_ACRn`

Runtime miss registers communicate service state to the handler:

| Register | Written by hardware on `Zdyn` trap |
| --- | --- |
| `DYNMISS_SITE_ACRn` | Inline-cache, dispatch, deopt, allocation, or safepoint site ID. |
| `DYNMISS_KEY0_ACRn` | Receiver shape/type, bytecode PC, allocation class, or barrier key. |
| `DYNMISS_KEY1_ACRn` | Secondary key such as opcode, source native PC, or deopt reason. |
| `DYNMISS_VALUE_ACRn` | Value or object pointer associated with the miss when available. |
| `DYNMISS_NATIVE_ACRn` | Native PC/TPC of the `Zdyn` instruction or template. |
| `DYNMISS_KIND_ACRn` | Guard fail, IC miss, dispatch miss, deopt, allocation slow path, safepoint, barrier slow path, or permission failure. |
| `DYNMISS_FLAGS_ACRn` | Runtime profile, GC profile, fixup eligibility, and context flags. |

`DYNMISS_*` state is part of the trap envelope. It must be preserved until the
handler returns or explicitly acknowledges the event.

## 8. Trap And Fixup Semantics

`Zdyn` should allocate an experimental trap class:

```text
TRAPNUM = E_DYN        # provisional; numeric allocation is unassigned
```

Suggested causes:

| Cause | Meaning |
| --- | --- |
| `EC_DYN_GUARD` | Tag, shape, class, null, bounds, or equality guard failed. |
| `EC_DYN_CHECKLD` | Checked load failed its profile-defined object/type check. |
| `EC_DYN_IC_MISS` | Inline-cache map lookup missed or found a stale generation. |
| `EC_DYN_DISPATCH_MISS` | Dispatch table entry is missing, stale, or not executable. |
| `EC_DYN_DEOPT` | Explicit or implicit deoptimization event. |
| `EC_DYN_ALLOC_SLOW` | TLAB allocation failed or requires runtime coordination. |
| `EC_DYN_BARRIER_SLOW` | GC barrier fast path cannot complete locally. |
| `EC_DYN_SAFEPOINT` | Safepoint poll requested runtime entry. |
| `EC_DYN_PERM` | Current ACR is not authorized for the operation. |
| `EC_DYN_BAD_TARGET` | Runtime map target is not a legal block start or fails managed-target validation. |
| `EC_DYN_BAD_PROFILE` | Unsupported runtime, GC, object, or ABI profile. |

### 8.1 Fixup-Eligible Failures

Some events may be handled with unmanaged FIXUP when the instruction is inside
a `BSTART.SYS FALL<, fixup_label` block:

- `EC_DYN_GUARD`;
- `EC_DYN_CHECKLD`;
- `EC_DYN_ALLOC_SLOW`;
- `EC_DYN_BARRIER_SLOW`.

FIXUP handling is allowed only if `DYNCFG.GuardPolicy` or `DYNCFG.GCProfile`
marks the event fixup-eligible. The fixup target must be a legal block start.
The failure remains precise: prior instructions in the block commit, and the
faulting instruction has no architectural side effects.

### 8.2 Handler-Required Failures

The following events must use `SERVICE_REQUEST` to `DYN_HANDLER_ACR`:

- inline-cache map installation or invalidation;
- generated-code publication;
- dispatch table mutation;
- global deoptimization;
- safepoint coordination;
- GC phase transition or global barrier configuration change;
- permission or bad-target failures.

Local FIXUP must not publish executable targets, mutate trusted metadata maps,
or change GC policy.

## 9. Guard Instructions

Guards are ordinary instructions that execute inside coupled blocks. They have
no side effect on success. On failure, they either route to FIXUP or enter the
runtime handler according to the trap rules.

Provisional forms:

```asm
DYN.GUARD.TAG    value, tag_mask, expected_tag, deopt_id
DYN.GUARD.CLASS  object, expected_class, deopt_id
DYN.GUARD.SHAPE  object, expected_shape, deopt_id
DYN.GUARD.NULL   object, deopt_id
DYN.GUARD.NNULL  object, deopt_id
DYN.GUARD.EQ     lhs, rhs, deopt_id
DYN.GUARD.BOUNDS index, length, deopt_id
```

The `deopt_id` identifies runtime metadata that reconstructs interpreter-visible
state. It may be encoded directly in 32-bit forms when small, or through a
48-bit/64-bit long form for large sites.

Success semantics:

```text
if predicate is true:
    continue
```

Failure semantics:

```text
DYNMISS_SITE   = deopt_id
DYNMISS_KEY0   = profile-defined failing key
DYNMISS_VALUE  = failing value when available
DYNMISS_NATIVE = pc/tpc of guard
DYNMISS_KIND   = guard_fail subkind

if current block is eligible unmanaged FIXUP:
    route to fixup target without ACR switch
else:
    SERVICE_REQUEST to DYNCFG.HandlerACR using DYNVEC
```

`ASSERT` is not sufficient for this role. Existing `ASSERT` has a fixed cause
and SYS-only assert semantics; dynamic runtimes need profile-specific deopt
metadata and cause codes.

## 10. Checked Loads

Checked loads are the most important data-path assist. They combine an object
access with a profile-defined check, so the common path performs one operation
instead of a guard plus a separate load.

Provisional forms:

```asm
DYN.CHECKLD.B base, simm, profile, deopt_id, ->dst
DYN.CHECKLD.H base, simm, profile, deopt_id, ->dst
DYN.CHECKLD.W base, simm, profile, deopt_id, ->dst
DYN.CHECKLD.D base, simm, profile, deopt_id, ->dst
DYN.CHECKLD.REF base, simm, profile, deopt_id, ->dst
```

`->dst` follows normal Linx destination conventions: a direct GPR destination
or a ClockHands destination such as `->t` or `->u`, as defined by the eventual
operand class.

The `profile` selects the object-model check. Examples:

| Profile | Check |
| --- | --- |
| `tag_object` | `base` has the object tag required by the runtime. |
| `shape_slot` | `base` has a cached shape and the slot offset is valid. |
| `klass_field` | `base` has the expected class and field layout generation. |
| `array_elem` | `base` is an array and index/length metadata is valid. |
| `ref_barrier` | Reference load must pass the active GC read-barrier profile. |

Success semantics:

```text
require base satisfies profile check
value = MEM[base + simm] using width/profile
apply reference decode or read barrier if profile requires it
write value to dst
```

Failure semantics are identical to guard failure, with `DYNMISS_KIND =
checkld_fail`.

`DYN.CHECKLD.*` is an ordinary instruction, not a control-flow terminator. If a
runtime wants local slow-path code, the containing block should be a
`BSTART.SYS FALL<, fixup_label` block.

## 11. Inline Cache Support

Inline caches are runtime-owned maps. They are keyed by site ID, receiver
shape/type, runtime context, and generation.

### 11.1 Inline Cache Map Entry

A `DYNMAP` inline-cache entry contains:

| Field | Meaning |
| --- | --- |
| `Valid` | Entry is visible to lookup. |
| `CtxID` | Runtime context ID from `DYNCTX`. |
| `RuntimeKind` | Runtime kind from `DYNCFG`. |
| `MapGen` | Generation from `DYNCTX`. |
| `Kind` | `IC_CALL`, `IC_LOAD`, `IC_STORE`, `DISPATCH`, `DEOPT`, `ALLOC`, or profile-defined. |
| `SiteID` | Compiler/runtime site ID. |
| `ReceiverKey` | Shape, class, hidden-class ID, map pointer, or type tag. |
| `NativePC` | Legal Linx block start for the target stub or method. |
| `Metadata` | Profile-defined method, slot, guard, or deopt metadata. |
| `Perm` | Execute and mutation permissions. |

Lookup key:

```text
DYNCTX.CtxID, DYNCFG.RuntimeKind, DYNCTX.MapGen, kind, site_id, receiver_key
```

### 11.2 Non-Terminal Probe

Provisional form:

```asm
DYN.IC.PROBE site_id, receiver, kind, ->t
```

On hit:

```text
t#1 = native target or metadata pointer
t#2 = hit flag 1
```

On miss:

```text
t#1 = 0
t#2 = 0
```

`DYN.IC.PROBE` does not transfer control and does not install map entries. It
is useful for hand-written stubs and debugging, but the terminal template below
is the recommended fast call path.

### 11.3 Terminal Inline-Cache Call

Provisional standalone template:

```asm
DYN.CALLIC site_id, receiver_reg, source_pc_reg
```

`DYN.CALLIC` is a legal block start and a terminal managed-runtime template. It
looks up the active inline-cache entry and transfers to the mapped native block
on a hit. On miss, stale entry, or bad target, it enters the handler.

Pseudocode:

```text
require DYNCFG.EN = 1
require CSTATE.ACR = DYNCFG.CodeACR

receiver_key = RuntimeShapeKey(receiver_reg, DYNCFG.Profile)
key = {DYNCTX.CtxID, DYNCFG.RuntimeKind, DYNCTX.MapGen,
       IC_CALL, site_id, receiver_key}

entry = DYNMapLookup(key)

if entry.hit and entry.generation == DYNCTX.MapGen:
    require entry.NativePC is legal block start
    if DYNCFG.StrictTarget:
        require entry.NativePC has managed-target metadata
    pc = entry.NativePC
else:
    DYNMISS_SITE   = site_id
    DYNMISS_KEY0   = receiver_key
    DYNMISS_KEY1   = source_pc_reg
    DYNMISS_VALUE  = receiver_reg
    DYNMISS_NATIVE = pc_of_this_template
    DYNMISS_KIND   = IC_MISS or stale/bad-target
    SERVICE_REQUEST to DYNCFG.HandlerACR using DYNVEC
```

Restartability:

- before the target PC is updated, `DYN.CALLIC` has no language-visible side
  effects;
- ordinary misses may report `TPL_REDO_OK=1`;
- if any internal state has advanced, `TPL_RESUME_OK=1` is required;
- `ACRE RRAT_RESTORE` retries only `DYN.CALLIC`, not the preceding JIT body.

### 11.4 Map Maintenance

Only `DYN_HANDLER` may mutate trusted runtime maps.

Provisional forms:

```asm
DYNMAP.INS kind, site_reg, key_reg, native_pc_reg, metadata_reg, perm
DYNMAP.INV kind, site_reg, key_reg
DYNMAP.INVCTX ctxid_reg
DYNMAP.FENCE
DYNMAP.PROBE kind, site_reg, key_reg, ->t
```

`DYNMAP.INS` performs:

```text
require DYNCFG.EN = 1
require CSTATE.ACR = DYNCFG.HandlerACR
require native_pc_reg points to a legal block start
require permission is allowed by DYNCFG

entry.Valid = 0
entry.CtxID = DYNCTX.CtxID
entry.RuntimeKind = DYNCFG.RuntimeKind
entry.MapGen = DYNCTX.MapGen
entry.Kind = kind
entry.SiteID = GPR[site_reg]
entry.ReceiverKey = GPR[key_reg]
entry.NativePC = GPR[native_pc_reg]
entry.Metadata = GPR[metadata_reg]
entry.Perm = perm
publish entry.Valid = 1 with release ordering
```

`DYNMAP.FENCE` orders:

- stores to generated code;
- instruction-cache synchronization;
- runtime metadata stores;
- map-entry publication;
- later `DYN.CALLIC` and `DYN.DISPATCH` lookup hits.

Open naming question: `DYNMAP` and DBT `BTMAP` may be promoted as one generic
`RTMAP` facility with separate namespaces. The semantics should remain the same
either way.

## 12. Bytecode Dispatch

Interpreters and baseline JITs need fast dispatch from bytecode PC and opcode
to a native handler block. `DYN.DISPATCH` handles this as a restartable
terminal template instead of exposing an unchecked indirect jump.

Provisional form:

```asm
DYN.DISPATCH bc_pc_reg, opcode_reg, table_reg
```

Inputs:

| Operand | Meaning |
| --- | --- |
| `bc_pc_reg` | Runtime bytecode PC or instruction index. |
| `opcode_reg` | Current bytecode opcode or quickened opcode. |
| `table_reg` | Dispatch table pointer or selector. |

Semantics:

```text
require DYNCFG.EN = 1
require CSTATE.ACR = DYNCFG.CodeACR

key = {DYNCTX.CtxID, DYNCFG.RuntimeKind, DYNCTX.MapGen,
       DISPATCH, table_reg, opcode_reg, bc_pc_reg optional by profile}

entry = DYNMapLookup(key)

if entry.hit:
    require entry.NativePC is legal block start
    pc = entry.NativePC
else:
    DYNMISS_SITE   = bc_pc_reg
    DYNMISS_KEY0   = opcode_reg
    DYNMISS_KEY1   = table_reg
    DYNMISS_NATIVE = pc_of_this_template
    DYNMISS_KIND   = DISPATCH_MISS
    SERVICE_REQUEST to DYNCFG.HandlerACR using DYNVEC
```

This form supports:

- classic interpreter dispatch;
- direct-threaded bytecode handlers;
- quickened bytecodes;
- tiered interpreter to baseline JIT transfer;
- runtime patching when bytecodes specialize or deopt.

The dispatch target must still be a legal Linx block start.

## 13. Deoptimization

Optimizing JITs must be able to leave compiled code and reconstruct an
interpreter frame. `Zdyn` supports both implicit deopt from guards and explicit
deopt.

Provisional form:

```asm
DYN.DEOPT deopt_id, reason
```

`DYN.DEOPT` is a standalone template that always enters `DYN_HANDLER_ACR`.

Trap state:

| State | Meaning |
| --- | --- |
| `DYNMISS_SITE` | `deopt_id`. |
| `DYNMISS_KEY0` | `reason`. |
| `DYNMISS_NATIVE` | Native source PC/TPC. |
| `DYNMISS_KIND` | `DEOPT`. |
| `EBARG`/`EBSTATE` | Precise native block/template snapshot for resume or unwind. |

The deopt metadata table is runtime-defined, but the ISA contract is that
`deopt_id` and the native source PC identify a complete materialization recipe:

- interpreter bytecode PC;
- expression-stack values;
- local variables;
- object/value tags;
- live GPR and ClockHands locations;
- virtual objects and scalar-replaced fields;
- pending exception or call state when applicable.

## 14. Allocation And GC Support

GC support must be profile-based. Different collectors need different barriers.
The base extension provides a set of barrier primitives selected by
`DYNCFG.GCProfile`.

### 14.1 TLAB Allocation

Provisional form:

```asm
DYN.TLAB.ALLOC size_reg, klass_reg, alloc_site, ->dst
```

Success semantics:

```text
thread = profile-defined thread register or DYNCTX.ThreadID
top = thread.tlab_top
end = thread.tlab_end
new_top = top + aligned(size_reg)

if new_top <= end:
    thread.tlab_top = new_top
    initialize object header using klass_reg and GCProfile
    dst = top encoded as runtime reference
else:
    enter fixup or DYN_HANDLER with EC_DYN_ALLOC_SLOW
```

`DYN.TLAB.ALLOC` may be implemented as a restartable template if it can perform
multiple memory operations. If it is an ordinary instruction, it must be precise
on failure and must not partially initialize an object before routing to slow
path.

### 14.2 Write Barrier Store

Provisional form:

```asm
DYN.WB.ST base, simm, value, barrier_profile
```

The instruction stores a reference or tagged value and performs the active
write barrier selected by `barrier_profile` and `DYNCFG.GCProfile`.

Profiles may include:

| Profile | Fast-path behavior |
| --- | --- |
| `card_mark` | Store value, then mark card for `base + simm`. |
| `satb_pre` | Load old reference, enqueue old reference if needed, then store. |
| `generational` | Store value, test old/new generations, mark remembered set if needed. |
| `no_barrier` | Ordinary store with runtime reference encoding. |

Ordering:

- the object field store and barrier metadata update must be ordered according
  to the collector profile;
- existing `FENCE.D` remains the architectural tool for stronger ordering when
  the collector requires it;
- atomics still use existing Linx AMO/LR/SC forms unless the GC profile defines
  an atomic barrier store variant.

### 14.3 Reference Load And Read Barrier

Provisional forms:

```asm
DYN.REF.LD base, simm, barrier_profile, ->dst
DYN.RB.FIX ref, barrier_profile, ->dst
```

`DYN.REF.LD` loads a reference and applies the profile-defined reference decode
and read barrier. `DYN.RB.FIX` applies the read barrier to an already loaded
reference.

Profiles may include:

| Profile | Fast-path behavior |
| --- | --- |
| `compressed_ref` | Decode using heap base and shift from `DYNCTX` or profile SSRs. |
| `colored_ptr` | Test color bits and strip/remap if fast path succeeds. |
| `load_barrier` | Check mark/relocation state and enter slow path if needed. |
| `plain_ref` | Return the raw reference. |

### 14.4 Card Mark And SATB Helpers

Lower-level barrier helpers are optional but useful for runtimes that want
explicit compiler scheduling:

```asm
DYN.CARD.MARK addr, card_table
DYN.SATB.ENQ old_ref, queue_reg
DYN.REF.DEC ref, profile, ->dst
DYN.REF.ENC ptr, profile, ->dst
```

These helpers are ordinary instructions. They may trap to `DYN_HANDLER` only
when the profile requires a slow path.

### 14.5 Safepoint Poll

Provisional form:

```asm
DYN.SAFEPOINT safepoint_id, poll_reg
```

Semantics:

```text
if poll_reg indicates no safepoint:
    continue
else:
    DYNMISS_SITE   = safepoint_id
    DYNMISS_VALUE  = poll_reg
    DYNMISS_NATIVE = pc/tpc of poll
    DYNMISS_KIND   = SAFEPOINT
    SERVICE_REQUEST to DYNCFG.HandlerACR using DYNVEC
```

Safepoint entry must be precise. The runtime must be able to enumerate live
references using stack maps and the active `linx64dyn` register profile.

## 15. `linx64dyn` Register Profile

`Zdyn` should recommend a private 64-GPR managed-runtime profile named
`linx64dyn`. It is not the public C ABI. It is a contract between generated
managed code, runtime stubs, handlers, the debugger, and GC stack-map tools.

Recommended assignment:

| Registers | Role |
| --- | --- |
| `r0` | `zero`. |
| `r1` | Managed/runtime stack pointer. |
| `r2..r17` | Low language value registers and helper-call arguments. |
| `r18..r31` | Hot temporaries for tags, values, array indexes, and property slots. |
| `r32` | Runtime thread pointer. |
| `r33` | Heap base or compressed-reference base. |
| `r34` | Bytecode PC, guest/source PC, or deopt source PC. |
| `r35` | Current frame/interpreter state pointer. |
| `r36` | Dispatch table pointer or selector. |
| `r37` | Inline-cache root or site metadata pointer. |
| `r38` | Current receiver shape/class key. |
| `r39` | Deopt metadata table pointer or selector. |
| `r40..r47` | JIT temporaries and barrier scratch. |
| `r48..r55` | Long-lived managed values across calls or loop backedges. |
| `r56..r63` | Handler/native bridge scratch until saved by the bridge ABI. |

Guidance:

- Public native helper functions still use the normal Linx ABI and
  `FENTRY/FEXIT/FRET.*`.
- Managed generated blocks may tail-chain to other managed blocks without
  entering the public C ABI.
- A bridge from `linx64dyn` to native C must save guest-live/runtime-live
  registers described by the stack map before calling ordinary functions.
- `DYN_HANDLER` entry must be transparent to managed code. Either hardware
  preserves GPRs on trap entry, or the handler ABI restricts early handler
  scratch use to a documented scratch subset before saving.

The 64-GPR profile is especially useful for JVM and JavaScript JITs because
thread pointer, heap base, bytecode PC, dispatch table, IC metadata, barrier
scratch, and hot language values can remain resident across blocks.

## 16. Assembly Patterns

The examples in this section use proposed `Zdyn` syntax. Existing Linx block
syntax is kept in documented form.

### 16.1 Property Load With Local FIXUP Miss

```asm
BSTART.SYS FALL<, .L_ic_miss
  DYN.GUARD.TAG   r12, 0xff, tag_object, 31
  DYN.GUARD.SHAPE r12, shape_0x18f2, 31
  DYN.CHECKLD.D   r12, 24, shape_slot, 31, ->r20
C.BSTOP

.L_ic_miss:
BSTART.SYS FALL
  ; Runtime-generated slow stub. It may call through a managed/native bridge,
  ; but it must not publish trusted map entries without handler authority.
C.BSTOP
```

The fast block handles common property access locally. A mismatch routes to the
fixup block without ACR switch because the failure does not by itself mutate a
trusted map.

### 16.2 Inline-Cache Call

```asm
BSTART.STD FALL
  ; r12 = receiver
  ; r34 = bytecode/source PC for deopt and profiling
C.BSTOP

DYN.CALLIC 0x44, r12, r34
```

On hit, `DYN.CALLIC` branches to the cached method entry after validating that
the native target is a legal Linx block start. On miss, it vectors to `DYNVEC`
so the handler can resolve the method and publish the cache entry.

### 16.3 Interpreter Dispatch

```asm
BSTART.STD FALL
  ; r34 = bytecode PC
  ; r20 = opcode
  ; r36 = dispatch table selector
C.BSTOP

DYN.DISPATCH r34, r20, r36
```

The dispatch template maps bytecode state to a legal native handler block. It
does not expose an unchecked indirect jump.

### 16.4 GC Barrier Store

```asm
BSTART.SYS FALL<, .L_barrier_slow
  ; Store r20 into [r12 + 16] with the active generational write barrier.
  DYN.WB.ST r12, 16, r20, generational
C.BSTOP

.L_barrier_slow:
BSTART.SYS FALL
  ; Local slow stub or managed/native bridge.
C.BSTOP
```

If the barrier fast path cannot complete locally, it enters the fixup slow path.
Global GC coordination still uses `DYN_HANDLER`.

### 16.5 Handler Map Publication

```asm
BSTART.SYS FALL
  ; DYN_HANDLER code has generated a target block and synchronized icache.
  ; r42 = site, r43 = receiver key, r44 = native block PC, r45 = metadata.
  DYNMAP.FENCE
  DYNMAP.INS IC_CALL, r42, r43, r44, r45, exec
  DYNMAP.FENCE
  ACRE RRAT_RESTORE
C.BSTOP
```

After `ACRE RRAT_RESTORE`, the interrupted terminal template retries and sees
the newly published entry.

## 17. Encoding Strategy

The first encoding should be conservative:

- Use 32-bit ordinary instruction forms for frequent guards, barrier helpers,
  and checked loads when operands fit existing 5-bit direct GPR/ClockHands
  classes.
- Use 48-bit `HL.*` forms for large `site_id`, `deopt_id`, profile selectors,
  or future direct 6-bit GPR operands.
- Use standalone template blocks for terminal operations that may trap and
  retry without replaying the preceding block body.
- Do not introduce `BSTART.DYN` in the first phase. Use existing `BSTART.STD`
  for ordinary managed fast-path blocks and `BSTART.SYS FALL<, fixup_label` for
  local fixup-capable blocks.

Provisional template ID allocation for `TemplateKind.class=0`:

| `TPL_ID` | Template |
| --- | --- |
| `32` | `DYN.CALLIC` |
| `33` | `DYN.DISPATCH` |
| `34` | `DYN.DEOPT` |
| `35` | `DYN.TLAB.ALLOC` if implemented as a template |
| `36` | `DYN.SAFEPOINT` if implemented as a template |
| `37..47` | Reserved for `Zdyn` experimental use. |

This keeps the currently documented template IDs `1..8` unchanged and leaves
room for DBT or other experiments to reserve their own ranges.

## 18. Security And Correctness Rules

Required rules:

- `DYN_CODE` may execute guards, checked loads, barriers, dispatch templates,
  and inline-cache terminal templates.
- Only `DYN_HANDLER` may install or invalidate trusted `DYNMAP` entries.
- Map entries must include context ID and generation.
- Stale generation entries must miss or trap.
- Every map hit target must validate as a legal Linx block start.
- `DYNMAP.FENCE` or equivalent ordering must publish generated code before a
  map entry becomes valid.
- FIXUP paths must not mutate trusted executable-target maps.
- Deopt and safepoint traps must be precise enough for runtime stack maps.
- Handler entry must preserve managed-live registers by hardware or by ABI.
- `DYN.WB.ST` and `DYN.REF.LD` must obey the active GC barrier ordering
  contract.

Bad targets must trap with `E_DYN(EC_DYN_BAD_TARGET)`. Permission failures must
trap with `E_DYN(EC_DYN_PERM)`.

## 19. Compiler Requirements

Compiler and assembler support must include:

- feature flags for `Zdyn.base`, `Zdyn.guard`, `Zdyn.checkld`, `Zdyn.ic`,
  `Zdyn.dispatch`, `Zdyn.gc`, and `Zdyn.gpr64`;
- operand classes for proposed `DYN.*` instructions;
- `deopt_id`, `site_id`, `shape`, `class`, and `barrier_profile` relocation or
  immediate policies;
- stack-map emission for `linx64dyn` registers and ClockHands;
- modeling of `DYN.CALLIC`, `DYN.DISPATCH`, `DYN.DEOPT`, and template-form
  `DYN.TLAB.ALLOC` as control-flow terminators;
- bridge lowering between managed `linx64dyn` blocks and public native Linx ABI
  functions;
- object metadata for managed-code sections and runtime maps;
- rejection of `Zdyn` instructions outside enabled target-feature profiles
  unless explicitly requested for tests.

The assembler should print proposed instructions in a way that preserves
whether an operand is an immediate profile selector, a GPR, or a ClockHands
destination. This avoids repeating the earlier ambiguity between ordinary GPR
names and T/U hand syntax.

## 20. Emulator Requirements

QEMU or another Linx emulator must:

- model `DYNCFG`, `DYNVEC`, `DYNCTX`, and `DYNMISS_*` SSRs;
- derive `DYN_CODE` and `DYN_HANDLER` from ACR state;
- implement guard/checkld success and failure behavior;
- route fixup-eligible failures through unmanaged FIXUP when inside
  `BSTART.SYS FALL<, fixup_label`;
- route handler-required events through `SERVICE_REQUEST` to `DYNVEC`;
- implement a `DYNMAP` lookup table or target cache;
- validate map hit targets using the existing legal block-start checker;
- model `DYNMAP.FENCE` publication ordering at least conservatively;
- preserve template restart state for terminal `Zdyn` templates;
- trace guard fail, IC miss, dispatch miss, map install, deopt, allocation
  slow path, barrier slow path, safepoint, bad target, and permission failure
  events.

The existing Linx target-validation path should remain the final native target
check. `Zdyn` adds runtime map lookup before target validation; it must not
replace target validation.

## 21. RTL Requirements

Hardware should implement:

- ACR-scoped runtime configuration and miss registers;
- permission checks for `DYN_CODE` and `DYN_HANDLER`;
- precise guard/checkld failure reporting;
- a restartable template sequencer for terminal `Zdyn` templates;
- a small runtime target cache for inline-cache and dispatch hits;
- legal block-start validation on target-cache hits;
- release/acquire publication ordering for `DYNMAP`;
- optional fast paths for checked loads, TLAB allocation, card marking, and
  reference decode/read barriers.

The base extension should not require hardware to understand full VM metadata
formats, walk language object layouts, or implement one GC algorithm in fixed
logic. Those details belong to runtime-selected profiles.

## 22. Validation Plan

Promotion requires tests for:

- `DYN.GUARD.TAG` success and failure;
- guard failure routed to FIXUP inside `BSTART.SYS FALL<, fixup_label`;
- guard failure routed to `DYNVEC` when no FIXUP is active;
- `DYN.CHECKLD.D` success, mismatch, and memory-fault precision;
- `DYN.IC.PROBE` hit and miss behavior;
- `DYN.CALLIC` hit to a legal block start;
- `DYN.CALLIC` miss, handler map install, `ACRE RRAT_RESTORE`, and retry;
- rejection of `DYNMAP.INS` outside `DYN_HANDLER`;
- rejection of map hit targets that are not legal block starts;
- stale generation miss after `DYNMAP.INVCTX`;
- `DYN.DISPATCH` hit, miss, and bad-target behavior;
- `DYN.DEOPT` trap state and deopt ID reporting;
- `DYN.TLAB.ALLOC` fast success and slow failure without partial object state;
- `DYN.WB.ST` card-mark and SATB profile behavior;
- `DYN.REF.LD` compressed-reference and read-barrier profiles;
- `DYN.SAFEPOINT` no-op and trap behavior;
- preservation of managed-live `linx64dyn` registers across handler entry;
- `DYNMAP.FENCE` ordering between code publication and lookup hit;
- interaction with ordinary Linx CFI traps.

## 23. Open Questions

Open choices before promotion:

- exact numeric allocation of `E_DYN` and its causes;
- exact SSR IDs for `DYNCFG`, `DYNVEC`, `DYNCTX`, and `DYNMISS_*`;
- whether `DYNMAP` should be unified with DBT `BTMAP` as a generic `RTMAP`;
- exact immediate widths for `site_id`, `deopt_id`, shape, class, and barrier
  profiles;
- whether `DYN.TLAB.ALLOC` should be an ordinary instruction, a template, or
  both;
- whether strict managed-code targets require a new marker such as `DYNENTRY`,
  or whether object/side-table metadata plus legal `BSTART.STD` is sufficient;
- how much of each GC barrier profile is architectural versus runtime-defined;
- exact native bridge ABI between `linx64dyn` managed code and public Linx ABI
  helpers;
- DWARF and stack-map numbering for ClockHands values if they are live across
  deopt points.

## 24. Recommendation

The first `Zdyn` implementation should be a focused managed-runtime assist
extension:

1. Keep normal managed JIT code as ordinary `BSTART.STD` or `BSTART.SYS`
   blocks.
2. Use `BSTART.SYS FALL<, fixup_label` for frequent local guard, checked-load,
   allocation, and barrier slow paths.
3. Use ACR service routing for authority-bearing operations: IC map mutation,
   dispatch-table mutation, code publication, deopt coordination, safepoints,
   and GC global coordination.
4. Add `DYN.GUARD.*` and `DYN.CHECKLD.*` first; they are the most direct
   dynamic-language data-path wins.
5. Add `DYN.CALLIC` and `DYN.DISPATCH` as restartable terminal templates so
   misses retry without replaying the preceding block body.
6. Add profile-based GC barrier and TLAB allocation assists, but keep collector
   policy outside fixed ISA semantics.
7. Use `linx64dyn` on top of the 64-GPR extension for high-quality JIT and
   interpreter register allocation.

This gives JVMs, interpreters, and dynamic-language JITs a common fast path
without weakening Linx block-target safety or hard-coding a single runtime
design into the ISA.
