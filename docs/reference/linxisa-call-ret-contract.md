# LinxISA Precise Call/Ret Contract (linx64)

This document is normative for compiler, emulator, runtime, and Linux cross-check work.

## 1) Function Entry/Exit Forms

Normal function path:

- Entry must use `FENTRY`.
- Return must use `FRET.STK`.
- Canonical form is `FENTRY ... FRET.STK`.

Tail-transfer path:

- Entry still uses `FENTRY`.
- Tail exit uses `FEXIT`.
- Control transfer after `FEXIT` must be block-legal (direct or indirect block transfer).
- Canonical form is `FENTRY ... FEXIT`.

`FRET.RA` is valid when return target is consumed from pre-restore `ra` by design, but standard C ABI returns use `FRET.STK`.

## 2) Return-Target Semantics

- `FRET.STK`: return target comes from fixed `R10` after `R10` is restored from stack slot zero.
- `FRET.RA`: return target comes from fixed pre-restore `R10`.
- In the standard linx64 ABI, `ra` is the architectural name bound to `R10`.
- The `FRET.STK` slot-zero target load is legal only for a complete 8-byte Normal, explicitly idempotent stack access.
  Device/MMIO, mixed-type, or unspecified non-idempotent stack mappings must fault before any physical read.
- `FRET.RA` and `FRET.STK` target validation requires actual-current marker proof, or a coherent marker-provenance
  cache with the same marker bytes, address-space state, code-visibility epoch, and invalidation scope.
  Metadata-only continuation or fallthrough acceptance is non-conforming.
- `BSTART.RET` blocks must include explicit target setup:
  - `setc.tgt <src>` where `<src>` resolves to `ra` for normal returns.

Required `RET` block form:

```asm
C.BSTART.RET
c.setc.tgt ra
C.BSTOP
```

## 3) Call Header Contract

Returning call headers are architecturally fused:

- `BSTART.CALL + C.SETRET` for compressed/direct call headers.
- `BSTART.CALL + SETRET` for non-compressed forms.
- Source-level direct-call assembly should use fused `..., ra=<label>` syntax.
- Lowered object code may still spell that pair as explicit adjacent
  `setret/c.setret`.
- Object disassembly may still show the lowered `CALL` plus `setret/c.setret`
  pair after MC lowering or relaxation.

Adjacency rule for returning calls:

- `SETRET/C.SETRET` must be immediately adjacent to the corresponding `BSTART.CALL`.
- No instruction may be scheduled between call-header and setret materialization.
- Return target is the explicit label encoded by `setret`, not the lexical fall-through.

Non-returning call headers:

- `BSTART.CALL` without `SETRET` is valid only for non-returning control transfer paths.
- In this form, `ra` is preserved (no implicit return-target rewrite).
- If control eventually returns and the dynamic target is not a legal block start, dynamic target safety checks must fault.

Required fused form:

```asm
BSTART.STD CALL, callee, ra=.Lret
```

Non-fallthrough return form is valid and common:

```asm
BSTART.STD CALL, callee, ra=.Ljoin
... call block body ...
C.BSTOP

... unrelated blocks ...

.Ljoin:
C.BSTART.STD
```

Setret width selection:

- `c.setret`: short forward range only.
- `setret`: larger forward range only.
- `hl.setret`: wide signed range (forward/backward), but it is not part of the
  current compiler AVS closure surface.

Current compiler branch note:

- the Bisheng `compiler/llvm` branch emits fused `ra=` call headers in textual
  assembly and preserves the paired return-address relocation in objects;
- handwritten `ICALL` still does not accept fused `ra=` source syntax on this
  branch, so explicit adjacent `setret/c.setret` remains the portable source
  form there;
- do not assume `hl.setret` is available in portable compiler/runtime flows
  unless a dedicated MC/backend test for that branch proves it.

## 4) Indirect Target Setup Rules

Before any `RET`, `IND`, or `ICALL` block transfer, a `setc.tgt` must define the dynamic target register source in the same block.

Non-conforming sequences (`setc.tgt` missing, or non-adjacent `SETRET` in returning call headers) are contract violations and must trap in strict mode.

## 5) Dynamic Target Safety Rule

Dynamic control-flow targets from `RET`/`IND`/`ICALL` must resolve to legal block start markers (`BSTART*`, `C.BSTART*`, template block starts like `FENTRY/FEXIT/FRET.*`). Non-block targets must fault.

`FRET.RA` and `FRET.STK` perform phase-zero target validation before any frame effect. A recoverable phase-one trap resumes at the recorded next event without repeating committed SP/GPR/memory/target effects or reissuing sealed target proof. After event-zero seal, rollback is not permitted; abandonment or an exact-live target/lease/ownership contradiction enters the unmaskable template-integrity `ASSERT_FAIL` fail-stop. That fail-stop is reset-only: the managing ring may inspect the frozen source state, but cannot return to the source with `ACRE`.

## 6) Cross-Stack Validation Anchors

Cross-check against Linux Linx implementation patterns:

- `${LINUX_ROOT}/arch/linx/kernel/switch_to.S`
- `${LINUX_ROOT}/arch/linx/kernel/entry.S`

These files are treated as authoritative reference behavior for return-target setup and call/return block sequencing.
