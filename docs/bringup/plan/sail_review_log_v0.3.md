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
