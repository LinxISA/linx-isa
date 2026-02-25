# LinxISA v0.3 — Sail formalization review log

This log captures *review decisions* and open questions made while implementing the v0.3 Sail model.

Format:

- Each entry has: date, topic, question, decision, rationale, and follow-ups.
- Keep it technical and reference canonical sources when possible.

---

## 2026-02-24 — Kickoff

Topic: stepwise Sail formalization for ~670 missing mnemonics (per `isa/sail/coverage.json`).

Decision:
- Proceed in small PR slices.
- Ask one focused semantic question per slice when ambiguity is encountered.

Follow-ups:
- Choose the first slice and confirm any corner-case semantics that must be fixed in conventions.

---

## 2026-02-25 — SETC.*I immediate shift semantics

Topic: `SETC.*I` forms encode an implicit `shamt` field but assembly syntax prints only `simm/uimm`.

Question:
- How should strict v0.3 interpret the encoded `shamt` for `SETC.*I`?

Decision (Kevin):
- **A)** Treat it as an immediate left shift: `imm = (SignExtend(simm) << shamt)` (or `ZeroExtend(uimm) << shamt`).

Rationale:
- Encoding clearly dedicates bits[11:7] (in 32-bit SETC.*I) to `shamt`, suggesting a widened immediate encoding scheme.

Follow-ups:
- Document this convention in `isa/v0.3/semantics_conventions.json`.
- Update auto-generated pseudocode for SETC.*I in the ISA manual generator.
- Implement the corresponding Sail semantics.

---

## 2026-02-25 — Restricted SrcRType handling for CMP/SETC

Topic: `CMP.{EQ,NE,LT,GE,LTU,GEU}` and `SETC.{EQ,NE,LT,GE,LTU,GEU}` assembly syntax only allows `{.sw,.uw}`, but encoding still carries a 2-bit `SrcRType`.

Question:
- What should strict v0.3 do when `SrcRType=11` appears for these restricted forms?

Decision (Kevin):
- Treat `SrcRType=11` as **equivalent to `00` (no modifier)**.

Rationale:
- Keeps strict profile deterministic without introducing extra illegal encodings for legacy streams.

Follow-ups:
- Record in `isa/v0.3/semantics_conventions.json` under `srcrtype.restricted_forms`.
- Update Sail semantics for the restricted CMP/SETC forms to sanitize 11→00.

---

## 2026-02-25 — BRU control-transfer legality in scalar blocks

Topic:
- BRU control-transfer instructions (`B.*`, `J`, `JR`, and related direct control-transfer forms) are not legal payload instructions in coupled scalar blocks.
- They are only executed on the **vec engine scalar lane**; if encountered in a scalar block, strict profile must trap.

Decision (Kevin):
- Misuse in scalar block raises **ILLEGAL_INST**: `TRAPNUM=4`.

Open details:
- Whether `TRAPARG0` should be populated (and with which PC) is still TBD.

---

## 2026-02-25 — Vec engine scalar-lane BRU PC domain

Topic:
- When BRU control-transfer instructions execute on the vec engine scalar lane, which PC domain do they update?

Decision (Kevin):
- Update **TPC** (body-local PC), not the architectural global PC.

Follow-ups:
- Define the immediate/label target computation relative to TPC (byte vs halfword scaling) for `B.*`/`J`/`JR`.

Decision (Kevin):
- Base for PC-relative targets is the **current instruction TPC**.
- Immediate offsets are **halfword-scaled**: `target = base + (SignExtend(simm) << 1)`.
- `JR SrcL, label` reads `SrcL` from the **vec engine scalar-lane GPR file** (not ClockHands `t/u` queues).
- `B.EQ/B.NE/B.LT/B.GE/B.LTU/B.GEU` read `SrcL/SrcR` from the **vec engine scalar-lane GPR file**.
- Signed/unsigned compare uses full 64-bit width (signed for LT/GE, unsigned for LTU/GEU).
- Equality compare (EQ/NE) is full 64-bit width.
- `JR SrcL, label` also uses halfword-scaled immediate: `target = SrcL + (SignExtend(simm12) << 1)`.
- `JR` does **not** force 2-byte alignment; odd targets are permitted and are handled by the normal fetch/alignment-fault machinery.
- If the resulting `TPC` is misaligned at fetch/execute time, it is reported as `E_BLOCK(EC_BFETCH)` (TRAPNUM=5) with `TRAPARG0` = faulting `TPC`.
- `JR` encoding includes a `SrcZero` field; strict v0.3 **ignores it** (treat as 0). If the computed target ends up at VA=0, subsequent fetch will fault (body-fetch error).
- If `JR` targets an address that is not a valid vec-body fetch location (out-of-body / unmapped / otherwise not fetchable), report as `E_BLOCK(EC_BFETCH)`.
- No explicit architectural body-range boundary is defined; "fetchable" is defined operationally (if fetch fails => `EC_BFETCH`).

---

## 2026-02-25 — B.Z / B.NZ predicate source

Topic:
- `B.Z`/`B.NZ` have no source operands; they branch based on a predicate value.

Decision (Kevin):
- They read the **predicate register `p`** (vec engine predicate domain) and test whether it is all-zero vs non-zero:
  - `B.Z` taken iff `p == 0`
  - `B.NZ` taken iff `p != 0`

Notes:
- `B.Z`/`B.NZ` are vec-engine-only (scalar blocks executing them trap with `TRAPNUM=4`).
- Any mirroring of `p` into architectural BARG/EBARG is vec-engine/profile-defined; scalar-only components must not assume it.

---

## 2026-02-25 — Floating-point min/max NaN behavior

Topic:
- `FMAX/FMIN` NaN handling semantics.

Decision (Kevin):
- IEEE/ARM-style `maxNum/minNum` behavior:
  - if exactly one operand is NaN: return the non-NaN operand
  - if both operands are NaN: return canonical qNaN
  - signed zeros: FMAX returns +0 when both are zeros; FMIN returns -0 iff either operand is -0.

---

## 2026-02-25 — CSEL SrcRType handling

Topic:
- `CSEL` assembly syntax allows `SrcR<.neg>` but encoding includes 2-bit `SrcRType`.

Decision (Kevin):
- Treat `SrcRType=11` as `.neg`; treat all other values as `00` (no modifier).

Notes:
- This mirrors the "restricted SrcRType" philosophy used elsewhere: prefer deterministic sanitization over new traps.

---

## 2026-02-25 — Immediate materialization (LUI / HL.LUI / HL.LIS / HL.LIU)

Topic:
- Define constant materialization semantics for LUI and HL immediate-load forms.

Decision:
- Follow RTL decode conventions:
  - `LUI imm20` materializes `SignExtend(imm20) << 12`.
  - `HL.LUI imm32` materializes `SignExtend(imm32)` (no `<< 12`).
  - `HL.LIS simm32` materializes `SignExtend(imm32)`.
  - `HL.LIU uimm32` materializes `ZeroExtend(imm32)`.

---

## 2026-02-25 — Prefetch (PRF/PRFI)

Topic:
- Define architectural semantics for prefetch/hint instructions and whether they may fault.

Decision (Kevin):
- Prefetch is a **non-faulting hint**: address translation, permission, and alignment errors are suppressed (no trap).
- `HL.PRF.A` / `HL.PRFI.UA` additionally return the computed effective address:
  - `Rd = EA`

---

## 2026-02-25 — DIV/REM edge cases (ARM-like semantics)

Topic:
- Define non-trapping behavior for divide-by-zero and signed overflow for DIV/REM families.

Decision (Kevin):
- Follow ARM-style behavior (non-trapping, defined results):
  - If divisor == 0:
    * DIV/DIVU/DIVW/DIVUW => quotient = 0
    * REM/REMU/REMW/REMUW => remainder = dividend
  - If signed overflow (MIN_INT / -1):
    * DIV/DIVW => quotient = MIN_INT
    * REM/REMW => remainder = 0
  - Division rounds toward zero; remainder computed as `a - q*b`.
- For *W variants, writeback is **sign-extend from bit 31** to 64-bit for ALL of DIVW/DIVUW/REMW/REMUW.
- For HL DIV/REM two-destination forms: `Dst0 = quotient`, `Dst1 = remainder`.
- For HL MUL/MULU two-destination forms: `Dst0 = low64(full_product)`, `Dst1 = high64(full_product)`.
- For HL MADD/MADDW two-destination forms: treat as 128-bit accumulator `acc = (SrcL*SrcR + SrcD)` (signed multiply/add), then `Dst0 = low64(acc)`, `Dst1 = high64(acc)`.
