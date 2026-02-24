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
- Immediate offsets are **halfword-scaled**: `target = base + (SignExtend(simm) << 1)`.
- `JR SrcL, label` also uses halfword-scaled immediate: `target = SrcL + (SignExtend(simm12) << 1)`.
- `JR` does **not** force 2-byte alignment; odd targets are permitted and are handled by the normal fetch/alignment-fault machinery.

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
