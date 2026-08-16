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

The PTO-common returning call is one fused architectural instruction:

- `BSTART.CALL <br_label>, <rt_label>, ->ra` encodes the branch target and
  return target together and writes `ra` atomically.
- It does not consume an adjacent `SETRET`/`C.SETRET`, and disassembly must not
  rewrite it into the deleted `BSTART.STD CALL` or `BSTART.FP CALL` spellings.
- `br_label` and `rt_label` are independent PC-relative operands; the return
  target is never inferred from lexical fall-through.

Required form:

```asm
BSTART.CALL callee, .Lret, ->ra
```

Non-fallthrough return form is valid and common:

```asm
BSTART.CALL callee, .Ljoin, ->ra

... unrelated blocks ...

.Ljoin:
C.BSTART.STD FALL
```

Linx additionally retains long bare-call forms such as
`L.BSTART.STD CALL, <label>` and `HL.BSTART.FP CALL, <label>`. A bare call
preserves `ra`. When software deliberately pairs one with `SETRET` or
`C.SETRET`, the return-address instruction must immediately precede the bare
call; this Linx-only pair is not an alternative spelling of `BSTART.CALL`.

## 4) Indirect Target Setup Rules

`RET` and `IND` block transfers require `setc.tgt` to define the dynamic target
register source in the same block.

`BSTART.ICALL <rt_label>, ->ra` is different: it retires the active STD or FP
block, snapshots that block's `BARG.BPCN` as the indirect target, and writes
the explicit return label to `ra`. It does not read `SETC.TGT` and does not
consume a separate `SETRET`.

Missing target state, misaligned targets, or malformed long bare-call pairs
are contract violations and must trap before architectural effects.

## 5) Dynamic Target Safety Rule

Dynamic control-flow targets from `RET`/`IND`/`ICALL` must resolve to legal block start markers (`BSTART*`, `C.BSTART*`, template block starts like `FENTRY/FEXIT/FRET.*`). Non-block targets must fault.

`FRET.RA` and `FRET.STK` perform phase-zero target validation before any frame effect. A recoverable phase-one trap resumes at the recorded next event without repeating committed SP/GPR/memory/target effects or reissuing sealed target proof. After event-zero seal, rollback is not permitted; abandonment or an exact-live target/lease/ownership contradiction enters the unmaskable template-integrity `ASSERT_FAIL` fail-stop. That fail-stop is reset-only: the managing ring may inspect the frozen source state, but cannot return to the source with `ACRE`.

## 6) Cross-Stack Validation Anchors

Cross-check against Linux Linx implementation patterns:

- `${LINUX_ROOT}/arch/linx/kernel/switch_to.S`
- `${LINUX_ROOT}/arch/linx/kernel/entry.S`

These files are treated as authoritative reference behavior for return-target setup and call/return block sequencing.
