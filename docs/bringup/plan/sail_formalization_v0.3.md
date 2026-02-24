# LinxISA v0.3 — Sail formalization plan (stepwise)

This document tracks the step-by-step bring-up of the Sail model under `isa/sail/`.

Scope / constraints:

- The Sail model is a **reference** for semantics.
- Missing semantics must be **explicit** (no guessing). If a rule is unclear, we either:
  - add a clarification/convention entry, or
  - leave the instruction unimplemented and record the question in the review log.
- Coverage is tracked mechanically by:
  - `isa/sail/implemented_mnemonics.txt`
  - `isa/sail/coverage.json` (generated)

Definition-of-done per mnemonic:

- Decode/dispatch reaches an implementation point for the mnemonic (even if decode is partial/feature-gated initially).
- Execute semantics are implemented (or explicitly `unimplemented("MNEMONIC")` with a linked review log entry).
- Manual documentation impact is handled:
  - either already covered by auto-generated ISA manual sections, or
  - requires an explicit normative/non-normative note, captured as a commit in `docs/architecture/isa-manual/src/...`.

Proposed iteration loop (one PR per small slice):

1) Pick a small slice (e.g. 5–20 mnemonics in one coherent group).
2) For each mnemonic:
   - confirm semantic corner cases (trap cause/arg, sign/zero extend rules, alignment/atomicity, etc.)
   - implement Sail execute semantics
   - add/extend decode/dispatch support
3) Update `isa/sail/implemented_mnemonics.txt`.
4) Regenerate and check:
   - `python3 tools/isa/sail_coverage.py ... --check`
   - `python3 tools/isa/validate_spec.py --profile v0.3`
   - `python3 tools/isa/build_golden.py --profile v0.3 --check`
5) Record any reviewer decisions in: `docs/bringup/plan/sail_review_log_v0.3.md`

Initial prioritization (can be adjusted):

- P0: establish a maintainable decode/dispatch path (ideally generated from `isa/v0.3/linxisa-v0.3.json`).
- P1: integer core missing semantics needed for toolchain/QEMU alignment (compare + setc + branches).
- P2: loads/stores + cache maintenance (and the associated fault/partial-effect rules).
- P3: atomics.
- P4: float and vector (after integer/memory base is stable).

Current coverage snapshot:

- See `isa/sail/coverage.json` for the authoritative missing list.
