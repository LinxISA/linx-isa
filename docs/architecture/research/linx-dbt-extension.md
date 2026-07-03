# LinxISA Experimental Dynamic Binary Translation Extension

Status: experimental design note

Audience: ISA, privilege, compiler, emulator, RTL, OS/runtime, and binary
translator owners

## 1. Purpose

This document proposes an experimental LinxISA extension for dynamic binary
translation (DBT), with ARM/AArch64-to-LinxISA and x86-64-to-LinxISA as the
first targets.

The extension has four linked goals:

- make translated indirect branches enter a DBT handler when the guest target
  has no native translation yet;
- keep translated code inside the existing Linx block-structured control-flow
  contract;
- use the 64-GPR extension as a high-quality guest-state register substrate;
- provide a generic DBT extension family instead of separate ad-hoc ARM and x86
  target mechanisms.

The design is named `Zbt` in this note. `Zbt` is not a replacement for the
normal Linx C ABI. It is a private code-cache execution ABI and privilege
interface used by DBT runtimes.

## 2. Background Constraints

LinxISA already has several properties that are useful for DBT:

- variable-length 16-bit, 32-bit, 48-bit, and 64-bit instruction encodings;
- explicit block-start markers and block-structured control transfer;
- dynamic-target validation for `RET`, `IND`, and `ICALL`;
- `SERVICE_REQUEST` trap entry through Access Control Rings (ACR);
- `EBARG`/`EBSTATE` trap snapshots for precise resume;
- template blocks such as `FENTRY`, `FEXIT`, and `FRET.*` that are legal block
  starts and can be restarted or resumed.

The current dynamic-target rule remains mandatory:

```text
Dynamic RET/IND/ICALL targets must resolve to legal block-start markers.
```

DBT must extend that rule, not bypass it. A translated indirect branch should
not jump to arbitrary native memory. It should resolve a guest target through a
DBT translation map, then jump only to a legal Linx DBT block entry.

## 3. Design Summary

The recommended DBT extension has these pieces:

- `Zbt.base`: generic DBT context state, DBT handler trap routing, target-map
  lookup, and restartable transfer templates;
- `Zbt.gpr64`: the private `linx64bt` register profile built on the 64-GPR
  extension;
- `Zbt.cc`: lazy guest condition-code and flag materialization helpers;
- `Zbt.mem`: optional guest memory-model and address-translation assists;
- `Zbt.x86`: x86-64 profile definitions for RFLAGS, TSO, segment bases, and
  locked atomics;
- `Zbt.arm`: ARM/AArch64 profile definitions for NZCV, exclusive monitors,
  barriers, and guest privilege state.

The core mechanism is a restartable DBT terminal template:

```asm
BTXFER.IND target_reg, source_pc_reg
BTXFER.ICALL target_reg, source_pc_reg
BTXFER.RET target_reg, source_pc_reg
```

`BTXFER.*` reads a guest target PC, looks it up in the active DBT translation
map, and transfers to the mapped native Linx block on a hit. On a miss, stale
entry, or permission failure, it enters the DBT service handler through
`SERVICE_REQUEST`.

`BTXFER.*` has no guest architectural side effects other than control transfer,
so a handler can translate the missing target, install the new map entry, and
return through `ACRE RRAT_RESTORE`. The template then retries the lookup and
branches to the new native block without re-executing the translated guest block
body.

### 3.1 Concrete ISA Extension Proposal

The first `Zbt` ISA proposal should be small enough to implement in QEMU and
RTL without requiring a full hardware guest-MMU or a large hardware translation
table. The mandatory subset is:

| Extension part | Proposed architectural surface | Required in first implementation |
| --- | --- | --- |
| DBT privilege state | `DBTCFG`, `DBTVEC`, `DBTCTX`, `DBTMISS_*` SSRs | Yes |
| DBT native entries | `BSTART.BT` or `BTENTRY` block-start marker | Yes |
| DBT indirect transfer | `BTXFER.DIR`, `BTXFER.IND`, `BTXFER.ICALL`, `BTXFER.RET` | Yes |
| DBT map maintenance | `BTMAP.INS`, `BTMAP.INV`, `BTMAP.INVCTX`, `BTMAP.FENCE` | Yes |
| DBT map probe | `BTMAP.PROBE` | Optional debug/handler assist |
| Lazy flags | `BT.CC.DEF`, `BT.CC.TEST`, `BT.CC.MAT` | Recommended |
| Guest memory assists | `BT.LD`, `BT.ST`, `BT.BARRIER`, `BT.EXCL.*` | Optional profile extension |
| Direct chaining | `BT.CHAIN.*`, `BT.RSB.*` | Optional performance extension |

The base ISA-visible contract is:

```text
guest target PC + DBT context -> native Linx DBT block entry PC
```

The DBT handler publishes that mapping with `BTMAP.INS`. Translated code cannot
publish mappings; it can only query them indirectly by executing `BTXFER.*`.

#### 3.1.1 Translation Map Entry

An installed translation-map entry is architectural even if the backing storage
is implementation-defined. It contains:

| Field | Meaning |
| --- | --- |
| `Valid` | Entry is visible to `BTXFER.*` lookup. |
| `CtxID` | Translation context ID from `DBTCTX`. |
| `GuestISA` | Guest ISA from `DBTCFG`. |
| `MapGen` | Generation from `DBTCTX`. |
| `Kind` | `DIR`, `IND`, `ICALL`, `RET`, or implementation-defined slow-path kind. |
| `GuestPC` | Guest target PC. |
| `NativePC` | Native Linx block entry. |
| `NativeProfile` | Expected native DBT profile, initially `linx64bt`. |
| `Perm` | Execute and bridge permission bits. |
| `Flags` | Guest flags recipe or metadata class if needed. |

`BTXFER.*` forms the lookup key from:

```text
DBTCTX.CtxID, DBTCFG.GuestISA, DBTCTX.MapGen, branch kind, guest target PC
```

The returned `NativePC` is not trusted until it passes native target validation.
In `StrictCFI` mode it must point at `BSTART.BT` or `BTENTRY`.

#### 3.1.2 Map Installation Instruction

Provisional assembly:

```asm
BTMAP.INS kind, guest_pc_reg, native_pc_reg, profile, perm
```

`BTMAP.INS` is legal only in `BT_HANDLER` mode. It performs:

```text
require DBTCFG.EN = 1
require CSTATE.ACR = DBTCFG.HandlerACR
require native_pc_reg points to a legal DBT entry marker
require profile is supported by DBTCFG.Profile
require perm does not request authority outside DBTCFG policy

entry.Valid = 0
entry.CtxID = DBTCTX.CtxID
entry.GuestISA = DBTCFG.GuestISA
entry.MapGen = DBTCTX.MapGen
entry.Kind = kind
entry.GuestPC = GPR[guest_pc_reg]
entry.NativePC = GPR[native_pc_reg]
entry.NativeProfile = profile
entry.Perm = perm
entry.Flags = profile-defined
publish entry.Valid = 1 with release ordering
```

If any check fails, `BTMAP.INS` traps with `E_DBT(EC_DBT_PERM)`,
`E_DBT(EC_DBT_BAD_NATIVE)`, or `E_DBT(EC_DBT_BAD_GUEST)`.

#### 3.1.3 Map Invalidation Instructions

Provisional assembly:

```asm
BTMAP.INV kind, guest_pc_reg
BTMAP.INVCTX ctxid_reg
BTMAP.FENCE
BTMAP.PROBE kind, guest_pc_reg, ->t
```

`BTMAP.INV` invalidates one key in the active context. `BTMAP.INVCTX`
invalidates all entries for a context or increments the effective generation for
that context. `BTMAP.FENCE` orders code-cache stores, instruction-cache
synchronization, and map publication. `BTMAP.PROBE` is an optional handler/debug
assist that returns the native PC for a key in `t#1` and a hit flag in `t#2`, or
returns zero values on miss.

Only `BT_HANDLER` mode may execute `BTMAP.INS`, `BTMAP.INV`, `BTMAP.INVCTX`, or
`BTMAP.PROBE`. `BTMAP.FENCE` may be legal in `BT_CODE` only as a no-op or
ordering hint; it must not publish mappings outside `BT_HANDLER`.

#### 3.1.4 Miss Handler Registration Sequence

The intended indirect-branch miss path is:

```asm
; BT_CODE block computed a guest target in r42 and source PC in r34.
BTXFER.IND r42, r34

; Hardware miss path:
;   DBTMISS_TARGET = r42
;   DBTMISS_SOURCE = r34
;   DBTMISS_NATIVE = PC(BTXFER.IND)
;   DBTMISS_KIND   = IND
;   vector to DBTVEC in BT_HANDLER mode

; Handler:
;   translate guest block at DBTMISS_TARGET
;   emit native block beginning with BSTART.BT or BTENTRY
;   synchronize generated code
BTMAP.FENCE
BTMAP.INS IND, miss_target_reg, native_entry_reg, linx64bt, exec
BTMAP.FENCE
ACRE RRAT_RESTORE
```

After `ACRE RRAT_RESTORE`, the interrupted `BTXFER.IND` retries. The retry uses
the same guest target PC, now hits the new map entry, validates `NativePC`, and
branches to the translated block.

This sequence is the architectural guest-PC to translated-PC registration
contract. The mapping is not considered installed when code bytes are written;
it becomes installed only when `BTMAP.INS` publishes a valid entry.

## 4. Why A DBT Privilege Mode Is Needed

Translated code and the DBT runtime do not have the same authority.

Translated code should be allowed to:

- execute generated Linx DBT blocks;
- compute guest branch targets;
- request translation-map lookup through `BTXFER.*`;
- access guest state according to the active DBT profile.

Translated code must not be allowed to:

- install arbitrary native targets into the translation map;
- mark arbitrary native code as a valid DBT entry;
- change the DBT handler vector;
- modify DBT context identity, guest ISA identity, or memory-model policy;
- use DBT metadata SSRs as general scratch registers.

The DBT handler must have those additional powers, but it should still run below
the host OS or hypervisor. Therefore `Zbt` introduces a DBT service mode layered
on the existing ACR system.

### 4.1 ACR Placement

The ISA should not hard-code one universal ACR number for DBT. Instead, each
profile binds a pair of comparable ACRs:

| Role | Meaning |
| --- | --- |
| `BT_CODE_ACR` | ACR used by translated guest-code blocks. |
| `BT_HANDLER_ACR` | More-privileged ACR used by the DBT miss/translation handler. |

Required ordering:

```text
BT_HANDLER_ACR p> BT_CODE_ACR
```

Example user-mode DBT profile:

| ACR | Example role |
| --- | --- |
| `ACR1` | Host OS. |
| `ACR2` | Native host user process. |
| `ACR5` | DBT handler for one host process. |
| `ACR6` | Translated guest user code for that handler. |

This example is illustrative only. A system that already uses `ACR3/ACR4` for
guest OS and guest user roles may choose a different DBT pair.

### 4.2 DBT Execution State

`Zbt` defines two derived execution states:

| State | Derivation | Meaning |
| --- | --- | --- |
| `BT_CODE` | `CSTATE.ACR == BT_CODE_ACR` and `DBTCFG.EN = 1` | Generated translated blocks are executing. |
| `BT_HANDLER` | `CSTATE.ACR == BT_HANDLER_ACR` and `DBTCFG.EN = 1` | DBT runtime handler is executing with map-install authority. |

`BT_CODE` and `BT_HANDLER` are privilege modes in the architectural sense, but
they are not independent of ACR. They are ACR-scoped states selected by DBT
configuration SSRs.

## 5. DBT Privileged State

The following SSRs are provisional names. They should be allocated from the
ACR-scoped SSR space if the extension is promoted.

### 5.1 `DBTCFG_ACRn`

`DBTCFG_ACRn` configures DBT for a managed ACR pair.

| Field | Meaning |
| --- | --- |
| `EN` | Enables DBT execution and DBT traps for the configured context. |
| `GuestISA` | `0=reserved`, `1=x86-64`, `2=AArch64`, `3=AArch32`, others reserved. |
| `MemModel` | `0=Linx/native`, `1=weak guest`, `2=TSO guest`, others reserved. |
| `CodeACR` | ACR that may execute `BT_CODE`. |
| `HandlerACR` | ACR that receives DBT miss traps. |
| `Profile` | DBT ABI profile, initially `1=linx64bt`. |
| `StrictCFI` | If set, every native hit target must be a `BSTART.BT` or `BTENTRY` marker. |
| `MissPolicy` | `0=trap on miss`, `1=branch to software dispatcher block`, others reserved. |

Only a more-privileged managing ACR may write `DBTCFG`.

### 5.2 `DBTVEC_ACRn`

`DBTVEC_ACRn` is the DBT handler vector. It must point to a legal Linx block
start in `BT_HANDLER_ACR`.

On a DBT miss, hardware vectors `BPC` to `DBTVEC_ACRn`, not to the generic
`EVBASE_ACRn`, while still using the normal `SERVICE_REQUEST` save protocol.
This gives the DBT runtime a fast dedicated entry while preserving the ordinary
trap envelope.

### 5.3 `DBTCTX_ACRn`

`DBTCTX_ACRn` identifies the active translation context.

| Field | Meaning |
| --- | --- |
| `CtxID` | Translation context ID, similar to a code-cache ASID. |
| `MapGen` | Translation-map generation. Incremented on invalidation. |
| `GuestASID` | Guest address-space ID if the DBT runtime uses one. |
| `FlagsMode` | Guest condition-code profile. |
| `Endian` | Guest data endianness. |

Translation-map lookup keys include `CtxID`, `GuestISA`, `MapGen`, branch kind,
and guest target PC.

### 5.4 DBT Miss Registers

DBT miss registers communicate miss state to the handler:

| Register | Written by hardware on DBT trap |
| --- | --- |
| `DBTMISS_TARGET_ACRn` | Guest branch target PC. |
| `DBTMISS_SOURCE_ACRn` | Guest source PC or block guest PC. |
| `DBTMISS_NATIVE_ACRn` | Native PC of the `BTXFER.*` template or terminal block. |
| `DBTMISS_KIND_ACRn` | `IND`, `ICALL`, `RET`, direct-chain miss, stale mapping, or permission failure. |
| `DBTMISS_FLAGS_ACRn` | Guest ISA, flags-state kind, memory model, and context flags. |

`TRAPARG0_ACRn` should still contain the native source PC for compatibility with
the existing trap reporting style. The DBT miss registers carry the guest-level
translation key.

## 6. DBT Trap Cause

`Zbt` should allocate a new experimental trap class from the reserved TRAPNUM
space:

```text
TRAPNUM = E_DBT        # provisional; numeric allocation is unassigned
```

Suggested `E_DBT` causes:

| Cause | Meaning |
| --- | --- |
| `EC_DBT_MISS` | No translation-map entry exists for the guest target. |
| `EC_DBT_STALE` | A map entry exists but its generation does not match `DBTCTX.MapGen`. |
| `EC_DBT_PERM` | Current ACR is not authorized for the DBT operation. |
| `EC_DBT_BAD_NATIVE` | Map entry points to a non-DBT or non-block native target. |
| `EC_DBT_BAD_GUEST` | Guest target violates guest ISA alignment/canonical-address rules. |
| `EC_DBT_UNSUPPORTED` | Guest feature requires slow path or unsupported emulation. |

If the trap-number space is not available in an early bring-up profile, the
temporary fallback is:

```text
E_BLOCK(EC_DBT)
```

The promoted ISA should prefer `E_DBT`, because translation misses are not
ordinary Linx CFI failures. A DBT miss is a normal runtime event; a corrupt
native target remains a fault.

## 7. Restartable Transfer Template

### 7.1 `BTXFER.*`

`BTXFER.*` is a standalone template block. It is a legal dynamic control-flow
target, like `FENTRY/FEXIT/FRET.*`.

Assembly forms:

```asm
BTXFER.IND   target_reg, source_pc_reg
BTXFER.ICALL target_reg, source_pc_reg
BTXFER.RET   target_reg, source_pc_reg
BTXFER.DIR   target_reg, source_pc_reg
```

The `target_reg` contains the guest target PC. The `source_pc_reg` contains the
guest PC of the branch being translated. Both operands are architectural GPRs in
the active DBT profile. If the implementation supports only 5-bit direct
operands in the first phase, the assembler must require these operands in the
direct register bank or in T/U hands. A later 48-bit or 64-bit form should allow
6-bit direct GPR operands.

Pseudocode:

```text
require DBTCFG.EN = 1
require CSTATE.ACR = DBTCFG.CodeACR

key = {
    DBTCTX.CtxID,
    DBTCFG.GuestISA,
    DBTCTX.MapGen,
    kind,
    GPR[target_reg]
}

entry = DBTMapLookup(key)

if entry.hit and entry.generation == DBTCTX.MapGen:
    require entry.native_pc is legal DBT block start
    pc = entry.native_pc
else:
    DBTMISS_TARGET = GPR[target_reg]
    DBTMISS_SOURCE = GPR[source_pc_reg]
    DBTMISS_NATIVE = pc_of_this_template
    DBTMISS_KIND = kind/miss_reason
    SERVICE_REQUEST to DBTCFG.HandlerACR using DBTVEC
```

`BTXFER.*` must be restartable:

- before the native PC is updated, it has no guest-visible side effects;
- `TPL_REDO_OK` is `1` for ordinary lookup misses;
- `TPL_RESUME_OK` is `1`;
- on return from the handler, retrying the same template must not re-execute the
  translated block body.

### 7.2 Recommended Lowering Shape

A translated guest block should end by falling into a terminal transfer
template:

```asm
BSTART.BT FALL
  ; translated guest body
  ; r42 = guest indirect target
  ; r34 = guest source PC
C.BSTOP

BTXFER.IND r42, r34
```

The body may update guest registers, lazy flags, and guest PC state. If the
target is missing, only `BTXFER.IND` is retried after the handler installs the
translation. The guest body is not replayed.

### 7.3 Optional Fused Commit Form

An implementation may later add:

```asm
BSTART.BT IND
  ...
  bt.settgt r42
  bt.setsrc r34
C.BSTOP
```

In this fused form, the block commit performs the same map lookup as
`BTXFER.IND`. If it misses, the saved `EBSTATE` must indicate a commit-pending
DBT transfer so `ACRE RRAT_RESTORE` retries only the commit lookup and not the
guest block body.

The standalone `BTXFER.*` form is the recommended first implementation because
restartability is simpler and easier to validate.

## 8. Native DBT Entry Markers

Translated native blocks should begin with a DBT-specific legal block marker:

```asm
BSTART.BT FALL, profile
```

or a compressed/long alias if encoding space requires:

```asm
BTENTRY profile, guest_isa
```

The exact encoding is open. The semantic requirements are fixed:

- it is a legal Linx block start;
- it identifies the block as DBT-generated code;
- it carries or implies the DBT ABI profile;
- it may carry the guest ISA profile for validation and disassembly;
- it may be targeted by `BTXFER.*` map hits;
- ordinary non-DBT indirect control flow must not treat it as a normal C ABI
  function entry unless the object explicitly exports a bridge.

If a map entry points to `BSTART.STD` native code while `StrictCFI=1`, hardware
must trap with `E_DBT(EC_DBT_BAD_NATIVE)`.

## 9. Translation Map

The architecture should not require one hardware translation-table format in
the base extension. The minimum hardware contract is a small target cache and a
trap-on-miss interface.

A conforming implementation may use any of the following:

- hardware target cache only, filled by privileged handler instructions;
- hardware target cache plus a memory-resident map root from `DBTMAP_BASE`;
- pure software dispatcher under `MissPolicy=branch_to_dispatcher`;
- emulator-only lookup table.

The lookup key must include:

```text
CtxID, GuestISA, MapGen, branch kind, guest target PC
```

The lookup result must include:

```text
native_pc, native_profile, generation, permission bits
```

The handler is responsible for installing entries only after the target native
block has been fully generated, instruction-cache synchronized, and marked as a
legal DBT entry.

### 9.1 Map Maintenance

Privileged DBT service code maintains the map with the same operations defined
in the concrete proposal:

```asm
BTMAP.INS kind, guest_pc_reg, native_pc_reg, profile, perm
BTMAP.INV kind, guest_pc_reg
BTMAP.INVCTX ctxid_reg
BTMAP.FENCE
```

These operations are legal only in `BT_HANDLER` mode, except that
`BTMAP.FENCE` may be accepted in `BT_CODE` as an ordering hint. Early
implementations may expose map maintenance as SSR writes or emulator helper
calls, but the architectural behavior should match these instructions.

`BTMAP.FENCE` must order:

- native code-cache stores;
- instruction-cache invalidation or synchronization;
- map-entry publication;
- later `BTXFER.*` lookup hits.

Map publication is release ordered. `BTXFER.*` lookup is acquire ordered with
respect to a hit entry, so translated code cannot observe a valid map entry
before the generated native block is executable.

## 10. `linx64bt` Register Profile

`Zbt` should strongly recommend the 64-GPR extension. DBT can run without 64
GPRs, but performance will degrade because guest state must be spilled to the
environment object more often.

Recommended private register profile `linx64bt`:

| Registers | Role |
| --- | --- |
| `r0` | `zero`. |
| `r1` | Native DBT stack pointer. |
| `r2..r33` | Guest integer register bank. |
| `r34` | Guest PC/RIP source PC. |
| `r35` | Lazy flags or NZCV operation descriptor. |
| `r36` | Lazy flags source 1. |
| `r37` | Lazy flags source 2 or result. |
| `r38` | Lazy flags auxiliary value. |
| `r39` | Guest TLS, `FS/GS`, or guest thread pointer. |
| `r40` | DBT environment or vCPU pointer. |
| `r41` | Translation-map or dispatch-cache pointer. |
| `r42..r55` | DBT temporaries and guest target calculation. |
| `r56..r63` | Reserved handler/native bridge scratch. |

The profile is intentionally not the C ABI:

- translated blocks may tail-chain directly to other translated blocks;
- helper calls must go through a bridge that saves guest-live state required by
  the runtime;
- DBT miss handlers must preserve all guest-live registers, at least
  `r2..r55`, unless the active profile says the value has been committed to the
  environment object.

### 10.1 Handler Register Transparency

DBT miss entry must be register-transparent from the translated guest block's
point of view.

The first implementation can satisfy this with an ABI rule:

- hardware does not clobber GPRs on DBT trap entry;
- the handler entry may use only `r56..r63` before it has explicitly saved any
  other register;
- calls from the handler into native C runtime code must spill guest-live state
  to the environment object or a handler frame first.

An optimized implementation may add banked DBT handler GPRs or a hardware
spill mask, but software must not depend on banked registers unless the profile
advertises them.

## 11. Guest Condition-Code Support

Condition flags are a major DBT cost, especially for x86. `Zbt.cc` should
support lazy flag recipes.

Recommended generic forms:

```asm
BT.CC.DEF op, width, src1, src2, result
BT.CC.TEST cond, ->t
BT.CC.MAT mask, ->dst
```

`BT.CC.DEF` records enough information to derive guest flags later. It does not
materialize all flags immediately.

`BT.CC.TEST` evaluates one guest condition into a T hand or direct destination.
`BT.CC.MAT` materializes selected flags into an architectural GPR.

### 11.1 x86-64 Flags

For x86-64, `Zbt.x86` should cover:

- `CF`, `PF`, `AF`, `ZF`, `SF`, `OF`;
- condition-code tests for `Jcc`, `SETcc`, `CMOVcc`, and flag-consuming
  arithmetic;
- lazy recipes for add, sub, adc, sbb, logic, shift, rotate, inc, dec, compare,
  and test;
- explicit materialization for `PUSHF`, `POPF`, `LAHF`, `SAHF`, interrupts,
  and helper calls.

### 11.2 ARM/AArch64 NZCV

For ARM/AArch64, `Zbt.arm` should cover:

- `N`, `Z`, `C`, `V`;
- condition-code tests for conditional branches/selects;
- flag-producing add/sub/logical operations;
- explicit materialization when guest code reads or writes `NZCV`.

The same generic `BT.CC.*` instruction family can support both x86 and ARM by
selecting `DBTCFG.GuestISA` and `DBTCTX.FlagsMode`.

## 12. Guest Memory Model Support

ARM/AArch64 and x86-64 place different demands on the host memory model.

### 12.1 AArch64

AArch64 is a weakly ordered ISA with explicit acquire/release and barrier
operations. Linx already has fences, acquire/release atomic suffixes, and LR/SC
style operations, so `Zbt.arm` can mostly lower to existing primitives.

Recommended assists:

```asm
BT.BARRIER kind
BT.EXCL.LD width, addr, ->dst
BT.EXCL.ST width, src, addr, ->status
BT.EXCL.CLR
```

These model AArch64 exclusive monitors and barriers without forcing every DBT
runtime to hand-code monitor state in memory.

### 12.2 x86-64

x86-64 requires TSO behavior. On a weaker Linx implementation, translating x86
loads and stores only to ordinary Linx memory operations may be incorrect.

`Zbt.x86` should therefore provide one of these policies:

- `DBTCFG.MemModel = TSO`, where hardware treats DBT memory operations in the
  translated context as TSO ordered;
- explicit `BT.LD.TSO` and `BT.ST.TSO` operations;
- conservative fence insertion by the translator as a fallback profile.

The first two options are preferred for performance. The fallback profile is
valid but can be expensive on store/load-heavy x86 code.

### 12.3 Atomics

Existing Linx AMO and LR/SC operations cover many guest atomic operations. The
DBT extension should additionally plan for:

- x86 locked read-modify-write operations;
- x86 `cmpxchg8b` and `cmpxchg16b`;
- AArch64 acquire/release atomics;
- AArch64 LSE atomics if that guest profile is supported.

`cmpxchg16b` requires an eventual 128-bit compare-exchange path or a runtime
helper with precise atomicity guarantees.

## 13. Guest Address Translation

`Zbt.base` does not require hardware to walk guest page tables. The first
profile may use a runtime-managed shadow mapping and normal Linx loads/stores.

An optional `Zbt.mem` profile may add guest-VA operations:

```asm
BT.LD width, guest_addr, ->dst
BT.ST width, src, guest_addr
BT.GVA.CHECK access, guest_addr
```

These operations would report guest faults through `E_DBT` with guest fault
metadata in DBT miss/fault registers. This is useful for full-system emulation,
but it is not required for user-mode DBT of normal Linux processes.

## 14. Direct Chaining And Return Caches

The fastest DBT path is direct native chaining:

- direct guest branches are translated to direct native `BSTART.BT` transfers;
- hot indirect branches use `BTXFER.*` and hit in the DBT target cache;
- monomorphic indirect branches may be patched into a guarded direct chain;
- misses enter `DBTVEC` and return to retry the terminal template.

Recommended optional branch-cache instructions:

```asm
BT.CHAIN.CHECK target_reg, expected_guest_pc, native_pc
BT.CHAIN.PATCH source_native_pc, target_native_pc
BT.RSB.PUSH guest_return_pc, native_return_pc
BT.RSB.POP guest_return_pc, ->native_pc
```

These are optional performance features. The architectural base should remain
the simple `BTXFER.*` lookup/miss mechanism.

## 15. DBT Block Metadata

Generated code should carry metadata for debugging, profiling, invalidation,
and precise guest exception reporting.

Recommended object or side-table record:

```text
native_pc_range -> guest_pc_range
guest_isa
dbt_profile
flags_recipe_kind
map_generation
source_kind: direct, indirect, call, return, helper, slow_path
```

For AOT or persistent code-cache modes, this metadata should be emitted in a
loader-visible section such as:

```text
.linx.btmap
.linx.btunwind
.linx.btguest
```

For JIT modes, the DBT runtime can keep equivalent process-local side tables.

## 16. Security Rules

DBT must not weaken Linx CFI.

Required rules:

- only `BT_HANDLER` mode may install, invalidate, or publish translation-map
  entries;
- `BT_CODE` mode may execute `BTXFER.*` but may not write DBT control SSRs;
- every `BTXFER.*` hit must validate the native target as a legal DBT block
  start;
- map entries must include a context ID and generation;
- stale map entries must miss or trap, not silently branch;
- code-cache stores must be ordered before map publication;
- ordinary native code must not be accepted as a DBT target unless explicitly
  marked as a bridge entry;
- DBT trap entry must preserve guest-live register state by hardware or by the
  handler ABI.

If any of these checks fail, the implementation should trap with
`E_DBT(EC_DBT_PERM)` or `E_DBT(EC_DBT_BAD_NATIVE)`, not continue through a
generic indirect branch.

## 17. Interaction With Existing Linx Control Flow

The extension keeps the following Linx rules:

- `BSTART*`, `C.BSTART*`, and template blocks remain the only legal external
  control-flow targets;
- ordinary `RET`/`IND`/`ICALL` still require `setc.tgt` and legal target
  validation;
- DBT target lookup is used only by DBT transfer templates or DBT block forms;
- a native target returned by the DBT map is still checked as a legal block
  start;
- `FENTRY/FEXIT/FRET.*` remain the standard function prologue/epilogue
  mechanism for native helper functions and DBT runtime functions.

Translated guest blocks are not normal C ABI functions. They should use
`BSTART.BT` or `BTENTRY`, not `FENTRY`, unless a generated block is deliberately
exported as a native helper bridge.

## 18. Example: x86-64 Indirect Jump

Illustrative lowering:

```asm
BSTART.BT FALL, linx64bt
  ; guest rax/rbx/... are in r2..r17
  ; r40 = env pointer
  ; compute guest target from translated x86 operand
  add r12, r13, ->t
  c.gset t#1, ->r42       ; r42 = guest target PC
  ; r34 carries guest source RIP
C.BSTOP

BTXFER.IND r42, r34
```

On hit, `BTXFER.IND` branches to the native Linx block for the guest target. On
miss, hardware writes `DBTMISS_TARGET=r42`, `DBTMISS_SOURCE=r34`, and vectors to
`DBTVEC`.

The handler translates the guest block at `DBTMISS_TARGET`, emits a `BSTART.BT`
entry, publishes the map entry, and returns through `ACRE RRAT_RESTORE`.

## 19. Example: AArch64 Return

Illustrative lowering:

```asm
BSTART.BT FALL, linx64bt
  ; AArch64 x30/lr is mapped in the guest register bank.
  ; Return target is moved into r42.
  c.gget r32, ->t         ; example mapping: guest x30
  c.gset t#1, ->r42
  ; r34 carries guest source PC
C.BSTOP

BTXFER.RET r42, r34
```

A DBT implementation may add a guest return-address cache, but the architectural
fallback remains `BTXFER.RET`.

## 20. Compiler And Assembler Requirements

The compiler and assembler must:

- distinguish ordinary Linx ABI functions from `linx64bt` translated blocks;
- support `BSTART.BT` or equivalent DBT entry markers;
- support `BTXFER.*` template blocks;
- prevent DBT-only instructions from being emitted in non-DBT profiles unless
  explicitly requested;
- model `BTXFER.*` as a control-flow terminator that may trap and retry;
- preserve guest-live registers across helper bridges;
- expose target feature flags for `Zbt.base`, `Zbt.cc`, `Zbt.mem`,
  `Zbt.x86`, `Zbt.arm`, and `Zbt.gpr64`.

The disassembler should print DBT metadata when available:

```asm
BSTART.BT FALL, linx64bt, guest=x86-64, gpc=0x401000
```

## 21. Emulator Requirements

QEMU or another Linx emulator must:

- represent DBT context SSRs and DBT miss registers;
- route `BTXFER.*` misses through `SERVICE_REQUEST` to `DBTVEC`;
- implement a target map or target cache;
- validate native hit targets as legal DBT block starts;
- preserve restartability of `BTXFER.*`;
- model `BT_HANDLER` permission checks;
- expose tracing for map hit, miss, stale, install, invalidate, and bad-native
  target events;
- test demand-paged code-cache behavior and instruction-cache synchronization.

The existing `linx_check_bstart_target` path is the right conceptual hook for
native target validation. DBT should add guest-target map lookup before that
native validation step, not replace native block-start checks.

## 22. RTL Requirements

Hardware should implement:

- DBT context SSRs and permission checks;
- DBT miss trap vectoring to `DBTVEC`;
- a restartable `BTXFER.*` template sequencer;
- at minimum, a small associative or direct-mapped DBT target cache;
- legal DBT block-start validation on target-cache hits;
- code-cache publication ordering through `BTMAP.FENCE` or an equivalent fence;
- optional TSO mode or TSO load/store forms for x86 DBT;
- optional lazy condition-code evaluation helpers.

The base extension should not require hardware guest-page-table walkers or a
large hardware translation map.

## 23. Validation Plan

Before promotion, the extension needs tests for:

- DBT SSR permission failures from non-handler ACRs;
- `BTMAP.INS` rejection outside `BT_HANDLER` mode;
- `BTMAP.INS` rejection when `native_pc` is not `BSTART.BT` or `BTENTRY`;
- `BTMAP.FENCE` ordering between code-cache stores and map publication;
- `BTXFER.IND` hit to a legal `BSTART.BT`;
- `BTXFER.IND` miss, handler translation, map install, and retry;
- stale generation miss after map invalidation;
- `BTMAP.INV` and `BTMAP.INVCTX` invalidation behavior;
- bad native target detection;
- DBT trap register contents for source PC, target PC, native PC, and kind;
- no guest-body re-execution after a `BTXFER.*` miss;
- handler preservation of `linx64bt` guest-live registers;
- x86 lazy flag recipes for common arithmetic and branch conditions;
- AArch64 NZCV recipes and exclusive monitor operations;
- x86 TSO litmus tests under `DBTCFG.MemModel=TSO`;
- code-cache store, instruction-cache synchronization, and map publication
  ordering;
- interaction with ordinary Linx CFI traps and `RET`/`IND`/`ICALL` validation.

## 24. Open Questions

The following choices remain open:

- exact numeric allocation of `E_DBT`;
- exact SSR IDs for `DBTCFG`, `DBTVEC`, `DBTCTX`, and `DBTMISS_*`;
- whether DBT service mode should require banked handler GPRs in high-end
  implementations;
- whether `BTXFER.*` should have 32-bit low-register forms plus 48/64-bit
  extended-register forms;
- whether `BSTART.BT` should be a new block type or an attribute on
  `BSTART.STD`;
- whether the first hardware target cache should be architecturally visible or
  entirely implementation-defined;
- exact helper-bridge ABI between `linx64bt` blocks and native C ABI functions;
- exact object metadata names for persistent AOT code caches.

## 25. Recommendation

The first DBT extension should be generic and small:

1. Add DBT ACR service mode through `DBTCFG`, `DBTVEC`, and DBT miss registers.
2. Add legal DBT entry markers.
3. Add the restartable `BTXFER.*` terminal template.
4. Use the 64-GPR `linx64bt` profile for guest state.
5. Add lazy condition-code helpers.
6. Add TSO support for x86 either as a DBT memory mode or explicit TSO memory
   operations.

This gives ARM and x86 translators a common fast path: direct native chaining
when the target is known, a hardware-assisted DBT miss trap when an indirect
target is new, and strict Linx block-target validation for every native address
that the translator installs.

## 26. Research Anchors

The design follows established DBT implementation patterns:

- QEMU TCG uses a frontend IR, optimization passes, backend code generation,
  and direct block chaining for hot translated paths:
  <https://www.qemu.org/docs/master/devel/tcg.html>
- QEMU TCG documents the IR operations that DBT frontends lower into:
  <https://qemu.readthedocs.io/en/v9.1.3/devel/tcg-ops.html>
- QEMU MTTCG documents why memory ordering must account for the guest and host
  memory models:
  <https://www.qemu.org/docs/master/devel/multi-thread-tcg.html>
- Apple Rosetta 2 documents a production mixture of AOT and JIT translation,
  code signing, and translated code caching:
  <https://support.apple.com/guide/security/rosetta-2-on-a-mac-with-apple-silicon-secebb113be1/web>
