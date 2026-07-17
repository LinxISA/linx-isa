# LinxISA Experimental 64-GPR Extension

Status: experimental design note

Audience: ISA, compiler, emulator, RTL, ABI, unwinder, and runtime owners

## 1. Purpose

This document defines an experimental extension that raises the first-layer
general-purpose register file from 24 architectural GPRs to 64 architectural
GPRs while preserving the existing variable-length LinxISA instruction model.

The extension has three linked parts:

- a 64-entry first-layer GPR architectural state;
- explicit handle-transfer instructions for ordinary access to high GPRs;
- count-mode function template blocks that encode ABI save depth rather than
  physical register ranges.

The design keeps `FENTRY`, `FEXIT`, `FRET.RA`, and `FRET.STK` as the mandatory
function prologue/epilogue mechanism. A 64-GPR function does not synthesize
ordinary load/store save sequences for ABI callee saves unless it is outside the
standard ABI path, such as a naked function or trap entry.

## 2. Current Constraint

The current v0.57 frame-template encoding is a 32-bit instruction family:

```text
31..25 = uimm[9:3]
24..20 = SrcEnd/DstEnd
19..15 = SrcBegin/DstBegin
14..12 = type
11..7  = uimm[14:10]
6..4   = 3'b100
3..1   = 3'b000
0      = 1
```

The existing `type` assignments are:

| Type | Form | Meaning |
| --- | --- | --- |
| `000` | `FENTRY` | Save a register range and allocate stack frame. |
| `001` | `FEXIT` | Restore a register range and deallocate stack frame before tail/fall-through transfer. |
| `010` | `FRET.RA` | Restore a register range, deallocate stack frame, and return through pre-restore `ra`. |
| `011` | `FRET.STK` | Restore a register range, deallocate stack frame, and return through restored `ra`. |

The current `SrcBegin/SrcEnd` or `DstBegin/DstEnd` fields are 5-bit register
encodings. The architectural GPR range is `R0..R23`; encodings `24..31` are
already used by `t#1..t#4` and `u#1..u#4` queue references in ordinary operand
contexts. Therefore the current range form cannot be widened to 64 GPRs by
reinterpreting the existing 5-bit fields.

## 3. Design Goals

The 64-GPR extension has the following goals:

- preserve old 24-GPR binaries and existing range-mode frame templates;
- make 64 architectural GPRs visible to the ABI, debugger, unwinder, compiler,
  emulator, and RTL;
- keep existing 16-bit and 32-bit instruction density for common operations;
- avoid adding 6-bit GPR fields to every existing instruction format;
- make function entry and exit compact even when callee-saved registers live in
  the high register bank;
- make prologue/epilogue restart semantics independent of ordinary instruction
  scheduling;
- encode enough ABI identity in the instruction stream for hardware and tools
  to expand frame templates without consulting compiler-private policy.

## 4. Non-Goals

This extension does not redefine tile registers, T/U/M/N tile hands, vector
state, system registers, or block-private RI/RO registers.

This extension does not remove the existing 24-GPR ABI. Old range-mode
`FENTRY/FEXIT/FRET.*` forms remain valid for legacy code.

This extension does not require all ordinary ALU, load, store, branch, or SETC
formats to grow direct 6-bit GPR operands. Existing 5-bit operand fields remain
the dense direct encoding surface.

## 5. Architectural GPR State

The extended first-layer architectural GPR file contains 64 64-bit registers:

```text
GPR64[0..63]
```

The following registers are fixed:

| Register | ABI name | Role |
| --- | --- | --- |
| `r0` | `zero` | Constant zero. Writes are discarded. |
| `r1` | `sp` | Stack pointer. Preserved by callees through balanced frame templates. |

All other registers are general architectural GPRs whose ABI names are selected
by the active ABI profile.

### 5.1 Direct Operand Encoding

Existing ordinary instruction fields remain 5-bit fields.

In an existing 5-bit GPR operand context:

- codes `0..23` name direct architectural GPRs `r0..r23`;
- codes `24..27` name `t#1..t#4`;
- codes `28..31` name `u#1..u#4`.

Therefore, textual `r24..r63` are not legal operands for existing 5-bit ordinary
instruction forms. They are legal only in operand classes that explicitly accept
an extended GPR immediate or extended ABI register operand.

### 5.2 High-GPR Handle Access

Ordinary access to `r24..r63` uses dedicated compressed handle-transfer
instructions. These instructions move values between the architectural GPR file
and the T/U hand queues:

```asm
c.gget r42, ->t
c.gget r42, ->u
c.gset t#1, ->r42
c.gset u#1, ->r42
```

`c.gget` copies an extended architectural GPR value into the selected hand.
`c.gset` copies the most recent selected hand value into an extended
architectural GPR.

The source or destination `rN` operand in these forms is a 6-bit architectural
GPR index. It is not the existing 5-bit ordinary operand class. The assembler
must reject `t#1`/`u#1` aliases in the extended-GPR index position.

Template blocks are the exception: `FENTRY/FEXIT/FRET.*` may read or write all
64 architectural GPRs directly through template microcode and do not require
`c.gget` or `c.gset` for frame saves/restores.

## 6. ABI Profile Model

The 64-GPR extension encodes an ABI profile in count-mode frame templates.

An ABI profile defines:

- architectural GPR names;
- caller-saved and callee-saved sets;
- argument and return registers;
- stack alignment;
- frame-template save schedule;
- DWARF register numbering;
- ELF attributes or other object metadata needed to prevent incompatible links.

The frame-template instruction stream carries a small `profile` field. The
profile identifies which architectural save schedule is used by `save_count`.
Hardware, QEMU, disassemblers, unwinders, and the compiler must use the same
profile table.

## 7. Recommended 64-GPR ABI Profile

This document recommends ABI profile `1`, named `linx64gpr64`.

### 7.1 Register Assignment

| Registers | ABI names | Convention |
| --- | --- | --- |
| `r0` | `zero` | Constant zero. |
| `r1` | `sp` | Stack pointer. |
| `r2..r17` | `a0..a15` | Argument and return registers, caller-saved. |
| `r18` | `ra` | Return address, caller-saved but saved by frame template when needed by the callee. |
| `r19..r47` | `x0..x28` | Caller-saved temporaries. |
| `r48..r63` | `s0..s15` | Callee-saved registers. |

Rationale:

- the low direct bank retains the current dense operand style for the most
  frequent ABI registers;
- argument registers fit within the low directly encodable bank;
- the high register bank is primarily used for longer-lived values and
  callee-saved allocation pressure;
- prologue/epilogue cost is handled by count-mode templates instead of by
  direct high-register instruction encodings.

### 7.2 Calling Convention

For the C ABI under profile `1`:

- integer and pointer return values use `a0`, then `a1` if needed;
- integer and pointer arguments use `a0..a15`, then the stack;
- `a0..a15`, `ra`, and `x0..x28` are caller-saved;
- `s0..s15` and `sp` are callee-saved;
- stack alignment is 16 bytes at public function call boundaries;
- stack-passed arguments are addressed relative to the callee stack after
  `FENTRY` allocation using the existing frame-lowering rule.

The frame pointer, when required, should use the first scheduled saved register
allocated by the compiler. Under the recommended profile this is `s0`.

## 8. ABI Save Schedule

Count-mode frame templates do not encode physical register IDs. They encode how
many entries of an architectural ABI save schedule are active.

For profile `1`, the save schedule is:

| Schedule index | Register | ABI name | Reason |
| --- | --- | --- | --- |
| 0 | `r18` | `ra` | Return target for non-leaf calls and `FRET.STK`. |
| 1 | `r48` | `s0` | First callee-saved register; preferred frame pointer. |
| 2 | `r49` | `s1` | Callee-saved. |
| 3 | `r50` | `s2` | Callee-saved. |
| 4 | `r51` | `s3` | Callee-saved. |
| 5 | `r52` | `s4` | Callee-saved. |
| 6 | `r53` | `s5` | Callee-saved. |
| 7 | `r54` | `s6` | Callee-saved. |
| 8 | `r55` | `s7` | Callee-saved. |
| 9 | `r56` | `s8` | Callee-saved. |
| 10 | `r57` | `s9` | Callee-saved. |
| 11 | `r58` | `s10` | Callee-saved. |
| 12 | `r59` | `s11` | Callee-saved. |
| 13 | `r60` | `s12` | Callee-saved. |
| 14 | `r61` | `s13` | Callee-saved. |
| 15 | `r62` | `s14` | Callee-saved. |
| 16 | `r63` | `s15` | Callee-saved. |

If `save_count = N`, the template saves or restores entries
`SaveSched[0]` through `SaveSched[N - 1]`.

For profile `1`, valid `save_count` values are `0..17`. Larger values are
reserved and must trap as illegal instruction or fail assembly until assigned.

The compiler register allocator should prefer lower schedule indices for
callee-saved allocation. If it uses schedule entry `K`, it should emit
`save_count >= K + 1`. This intentionally preserves the current Linx design
choice where template prologues may save a prefix of the callee-saved schedule
rather than an arbitrary sparse set.

## 9. Count-Mode Frame Template Encoding

The count-mode forms reuse the existing frame-template opcode family and the
currently unused type values `100..111`.

```text
31..25 = uimm[9:3]
24..21 = profile
20..15 = save_count
14..12 = type
11..7  = uimm[14:10]
6..4   = 3'b100
3..1   = 3'b000
0      = 1
```

`uimm` is the frame size in bytes with bits `2..0` implicitly zero. Therefore
the encoded frame size is 8-byte aligned and currently uses the same 15-bit
range as legacy frame templates.

The count-mode `type` assignments are:

| Type | Form | Assembly |
| --- | --- | --- |
| `100` | Count-mode entry | `FENTRY.C profile, save_count, sp!, uimm` |
| `101` | Count-mode tail/fall-through exit | `FEXIT.C profile, save_count, sp!, uimm` |
| `110` | Count-mode return through pre-restore RA | `FRET.C.RA profile, save_count, sp!, uimm` |
| `111` | Count-mode return through restored RA | `FRET.C.STK profile, save_count, sp!, uimm` |

The `.C` suffix means "count mode", not compressed instruction length. These
forms are 32-bit template-block instructions.

Assemblers may also accept ABI-profile aliases:

```asm
FENTRY.G64  save_count, sp!, uimm
FEXIT.G64   save_count, sp!, uimm
FRET.G64.RA save_count, sp!, uimm
FRET.G64.STK save_count, sp!, uimm
```

These aliases encode `profile = 1`.

## 10. Template Semantics

The count-mode template semantics are defined by:

```text
Sched = AbiProfile[profile].SaveSched
Regs  = Sched[0 .. save_count - 1]
```

If `save_count` exceeds the length of `Sched`, the instruction is illegal.
If `profile` is reserved or unsupported, the instruction is illegal.

### 10.1 `FENTRY.C`

`FENTRY.C profile, save_count, sp!, frame_size` performs:

```text
old_sp = sp
new_sp = old_sp - frame_size
probe save slots for Regs before committing sp
sp = new_sp
for i in 0 .. save_count - 1:
    MEM64[sp + frame_size - 8 * (i + 1)] = GPR64[Regs[i]]
next_pc = fall-through block address
```

The probe-before-commit rule is required. If a save slot faults, the template
must be restartable from the original architectural state and must not subtract
the frame twice.

`FENTRY.C` is a legal block-start marker and must appear as a standalone
template block. It is not wrapped in `BSTART/BSTOP`.

### 10.2 `FEXIT.C`

`FEXIT.C profile, save_count, sp!, frame_size` performs:

```text
old_sp = sp
new_sp = old_sp + frame_size
for i in 0 .. save_count - 1:
    temp[i] = MEM64[new_sp - 8 * (i + 1)]
sp = new_sp
for i in 0 .. save_count - 1:
    GPR64[Regs[i]] = temp[i]
next_pc = fall-through block address
```

`FEXIT.C` is used for tail-transfer and other function-exit paths that do not
return through `FRET.*`. The control transfer following `FEXIT.C` must still
satisfy the block-structured dynamic-target rules.

### 10.3 `FRET.C.STK`

`FRET.C.STK profile, save_count, sp!, frame_size` performs the same restore
sequence as `FEXIT.C`, then reads the return target from restored `ra`:

```text
target = GPR64[ra]
check target is a legal block start
pc = target
```

For the standard C ABI, normal returns use `FRET.C.STK`.

If `save_count = 0`, `ra` is not restored by the template. In that case
`FRET.C.STK` uses the current architectural `ra` value. Compilers should use
this only when the function is leaf-safe and `ra` has not been clobbered.

### 10.4 `FRET.C.RA`

`FRET.C.RA profile, save_count, sp!, frame_size` captures `ra` before restore,
then performs the restore sequence:

```text
target = GPR64[ra]
restore Regs
check target is a legal block start
pc = target
```

`FRET.C.RA` is valid when the return target is intentionally consumed from
pre-restore `ra`. Standard C ABI lowering should prefer `FRET.C.STK`.

## 11. Stack Frame Layout

For a count-mode frame with `frame_size = F` and `save_count = N`, the save
area occupies the high end of the allocated frame:

```text
old_sp
  -8     SaveSched[0]
  -16    SaveSched[1]
  ...
  -8*N   SaveSched[N - 1]
new_sp = old_sp - F
```

Equivalently, after `FENTRY.C` commits `sp = new_sp`, schedule entry `i` is
stored at:

```text
sp + F - 8 * (i + 1)
```

The compiler must reserve at least `8 * save_count` bytes inside `frame_size`.
If local objects or outgoing argument areas overlap the save area, the program
is malformed.

Large frames that exceed the 15-bit template immediate are still represented by
one count-mode template plus additional ordinary stack adjustment chunks, using
the same split strategy as the current backend.

## 12. Always-Template Function Rule

Under profile `1`, every ABI-visible function must use the count-mode template
forms for entry and exit:

```asm
FENTRY.C profile, save_count, sp!, frame_size
...
FRET.C.STK profile, save_count, sp!, frame_size
```

or, for tail-transfer exit paths:

```asm
FENTRY.C profile, save_count, sp!, frame_size
...
FEXIT.C profile, save_count, sp!, frame_size
```

A zero-frame leaf function still uses:

```asm
FENTRY.C 1, 0, sp!, 0
...
FRET.C.STK 1, 0, sp!, 0
```

Toolchains may optimize textual display with aliases, but object code must keep
the template block markers so dynamic control-flow target validation,
unwinding, tracing, and hardware block boundaries remain canonical.

Exceptions to this rule are limited to explicitly marked non-ABI code, such as:

- naked functions;
- privileged trap entry/exit code with its own architectural contract;
- boot code before the ABI environment is established;
- hand-written tests that intentionally check illegal or nonstandard sequences.

## 13. Object and Linker Metadata

Object files using the 64-GPR extension must carry an ABI attribute that records:

- GPR count: `64`;
- frame-template mode: `count`;
- ABI profile: `1` for `linx64gpr64`;
- stack alignment: `16`;
- high-GPR handle-transfer support: required.

The linker must reject objects with incompatible GPR count, incompatible
template mode, or incompatible ABI profile unless an explicit transition ABI is
defined.

Recommended ELF attribute names are provisional:

```text
Tag_Linx_GPR_Count = 64
Tag_Linx_Frame_Template = count
Tag_Linx_ABI_Profile = linx64gpr64
Tag_Linx_High_GPR_Access = c.gget_c.gset
```

## 14. DWARF and Unwind Semantics

DWARF register numbers should match architectural GPR indices for `r0..r63`
unless the existing ABI already reserves a different public numbering scheme.

For count-mode frame templates, unwinders reconstruct callee-saved locations
from:

```text
profile
save_count
frame_size
canonical frame address
```

For profile `1`, entry `i` in `SaveSched` is saved at CFA offset:

```text
-8 * (i + 1)
```

where CFA is the caller stack pointer value before `FENTRY.C`.

The compiler may emit explicit CFI for each saved schedule entry, or an
ABI-aware unwinder may decode the count-mode template directly. The architectural
contract is the same in both cases.

## 15. Compiler Requirements

The compiler backend must:

- define 64 architectural GPRs and keep existing `t#`/`u#` queue references out
  of the architectural GPR class;
- add distinct operand classes for 5-bit ordinary GPR operands and 6-bit
  extended-GPR immediate operands;
- lower high-GPR ordinary uses through `c.gget` and `c.gset` when no direct
  instruction form exists;
- allocate arguments preferentially in `a0..a15`;
- allocate callee-saved registers according to the save schedule order;
- compute `save_count` as one plus the highest used save-schedule index;
- force `save_count >= 1` when a non-leaf or frame-bearing function must restore
  `ra` through `FRET.C.STK`;
- reserve stack slots for the complete save-count prefix, not only for sparse
  callee-saved registers actually used;
- emit count-mode `FENTRY.C` and matching `FEXIT.C` or `FRET.C.*`;
- model all restored registers as restored by the template, not by ordinary
  spill/reload pseudo-instructions;
- reject mixing range-mode and count-mode frame templates in one ABI-visible
  function.

Register allocation cost should prefer caller-saved low registers for short
live ranges and use high callee-saved registers for values that survive calls.
This aligns with caller/callee partition research: caller-saved registers avoid
unnecessary prologue cost for short-lived values, while a moderate callee-saved
bank reduces repeated spill traffic for long-lived values across calls.

## 16. Emulator Requirements

The emulator must:

- expand `LINX_GPR_COUNT` and architectural state storage to 64 GPRs;
- preserve existing `tq` and `uq` queue state as separate state, not as aliases
  of `r24..r31`;
- decode type `100..111` as count-mode frame templates;
- interpret `profile` and `save_count` through the architectural save schedule;
- reject unsupported profiles and out-of-range save counts;
- preserve restartable template behavior and probe-before-commit save semantics;
- update trace and disassembly paths to distinguish `r24..r63` from `t#`/`u#`
  queue references;
- keep legacy range-mode `FENTRY/FEXIT/FRET.*` behavior unchanged.

## 17. RTL Requirements

The code template unit must:

- support 64 GPR read/write ports or an internal sequencer capable of addressing
  all 64 GPR entries;
- add count-mode decode for frame-template type values `100..111`;
- map `(profile, save_count)` to an ordered save/restore sequence;
- preserve standalone template-block behavior;
- preserve restartability across page faults or memory exceptions;
- expose illegal-profile and illegal-save-count traps;
- keep old range-mode expansion for legacy code.

If hardware stores the save schedule in microcode or ROM, that table is
architectural for each supported profile and must be versioned with the ISA.

## 18. Assembler and Disassembler Requirements

The assembler must:

- parse `FENTRY.C`, `FEXIT.C`, `FRET.C.RA`, and `FRET.C.STK`;
- parse profile aliases such as `FENTRY.G64` only when the target enables
  profile `1`;
- reject `save_count` values larger than the selected profile's schedule length;
- reject high-GPR names in existing 5-bit operand contexts;
- accept high-GPR names only in extended-GPR operand contexts and diagnostics.

The disassembler should prefer profile aliases when an ABI profile is known:

```asm
FENTRY.G64 5, sp!, 128
```

When the profile is not known, the disassembler should print the explicit form:

```asm
FENTRY.C 1, 5, sp!, 128
```

## 19. Compatibility

Range-mode and count-mode frame templates are binary-distinct because they use
different `type` values.

Legacy mode:

```asm
FENTRY [ra ~ s2], sp!, 256
FRET.STK [ra ~ s2], sp!, 256
```

64-GPR count mode:

```asm
FENTRY.C 1, 4, sp!, 256
FRET.C.STK 1, 4, sp!, 256
```

For profile `1`, `save_count = 4` saves and restores:

```text
ra, s0, s1, s2
```

The two forms are not ABI-compatible unless a transition shim preserves both
calling conventions.

## 20. Examples

### 20.1 Leaf Function

```asm
FENTRY.C 1, 0, sp!, 0
  add a0, a1, ->a0
FRET.C.STK 1, 0, sp!, 0
```

### 20.2 Non-Leaf Function Saving RA Only

```asm
FENTRY.C 1, 1, sp!, 32
  BSTART.STD CALL, callee, ra=.Lret
  C.BSTOP

.Lret:
  add a0, a1, ->a0
FRET.C.STK 1, 1, sp!, 32
```

`save_count = 1` saves only `ra`.

### 20.3 Function Using High Callee-Saved Registers

```asm
FENTRY.C 1, 3, sp!, 64
  c.gget r48, ->t
  add t#1, a0, ->t
  c.gset t#1, ->r48
  c.gget r49, ->u
  add u#1, a1, ->u
  c.gset u#1, ->r49
FRET.C.STK 1, 3, sp!, 64
```

`save_count = 3` saves and restores `ra`, `s0`/`r48`, and `s1`/`r49`.

### 20.4 Tail Transfer

```asm
FENTRY.C 1, 2, sp!, 48
  c.gget r48, ->t
  add t#1, a0, ->a0
FEXIT.C 1, 2, sp!, 48
  BSTART.STD DIRECT, target
  C.BSTOP
```

The `FEXIT.C` restores the frame state. The following block transfer remains
responsible for satisfying the block-structured control-flow contract.

## 21. Validation Plan

The extension requires the following tests before promotion from experimental:

- assembler round-trip for all count-mode template forms;
- disassembler round-trip with and without ABI-profile aliases;
- illegal profile decode tests;
- illegal save-count tests;
- `save_count = 0` leaf return tests;
- `save_count = 1` non-leaf `ra` save/restore tests;
- high callee-saved register save/restore tests for `r48`, `r63`;
- page-fault restart test for `FENTRY.C` save-slot probing;
- `FRET.C.STK` target-safety tests using restored `ra`;
- `FRET.C.RA` target-safety tests using pre-restore `ra`;
- mixed range/count-mode ABI rejection tests;
- linker ABI attribute compatibility tests;
- DWARF unwind tests for all saved schedule entries;
- QEMU and RTL co-simulation for count-mode expansion order.

## 22. Open Questions

The following decisions remain open:

- whether profile `0` should be reserved for legacy range mode or defined as a
  24-GPR count-mode ABI;
- whether `r18` remains `ra` in the final 64-GPR ABI or `ra` moves to improve
  other encoding patterns;
- whether `FENTRY.C 1, 0, sp!, 0` should be mandatory for all leaf functions or
  only for externally visible leaf functions;
- whether high-GPR handle transfers need both T and U hand destinations in the
  first implementation step;
- whether `save_count` should remain 6 bits or be reduced to 5 bits to expose
  one more profile or flag bit;
- the exact ELF attribute numbers and GNU property names;
- the exact privileged trap/interrupt convention for preserving 64 GPRs.

## 23. Summary

The 64-GPR extension should encode the ABI into frame-template instructions by
using `profile + save_count`, not physical register ranges. The profile selects
an architectural save schedule; `save_count` saves or restores the first N
entries of that schedule.

This keeps `FENTRY/FEXIT/FRET.*` as the single canonical prologue/epilogue
mechanism, avoids adding 6-bit operands to every ordinary instruction, gives
hardware a deterministic template expansion, and lets the ABI grow to 64 GPRs
without breaking existing range-mode binaries.
