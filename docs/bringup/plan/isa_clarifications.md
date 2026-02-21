# LinxISA v0.3 — Clarifications & Decisions (Bring-up)

This document summarizes clarifications agreed during bring-up work. It is a **non-normative index** into the canonical
spec and contract docs.

Canonical spec sources:

- ISA manual (v0.3): `docs/architecture/isa-manual/src/linxisa-isa-manual.adoc`
- Architecture contract: `docs/architecture/v0.3-architecture-contract.md`
- Bring-up gates: `docs/bringup/check26_contract.yaml` and scripts under `tools/bringup/`

---

## 1) Block boundary markers and “outside blocks”

- `BSTART.*` / `BSTOP` are **block boundary markers** for block init/commit.
- “No architectural instructions outside blocks” is interpreted as:
  - no **architectural state-modifying payload** instructions outside block execution; boundary markers/descriptors can
    appear as packaging/control.

See:
- `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`
- `docs/architecture/v0.3-architecture-contract.md`

---

## 2) CFI / illegal targets

- Control-flow targets must land on legal block start markers.
- Architectural control-flow to engine-internal entrypoints (e.g. decoupled body entry, SIMT body entry) is illegal and
  reported as `E_BLOCK(EC_CFI)` with `EC_CFI_KIND=CFI_BAD_TARGET`.

### 2.1) `E_BLOCK(EC_CFI)` encoding

- `EC_CFI = 0x1` within `E_BLOCK`.
- `EC_CFI_KIND` is carried in `TRAPNO.CAUSE[3:0]`:
  - `0x1`: `CFI_BAD_TARGET`
  - `0x3`: `CFI_MISSING_NEXT_MARKER`
  - other values reserved.
- `TRAPNO.CAUSE[7:4]` reserved and must be 0.

### 2.2) CFI reporting

- `TRAPARG0` = source PC/TPC of the triggering control-flow instruction (or boundary marker).
- `BI=0`.
- CFI is precise.

See:
- `docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc`
- `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`
- `docs/bringup/plan/arch.md`

---

## 3) Block-format validation failures

### 3.1) `E_BLOCK(EC_BLOCKFMT)` encoding

- `EC_BLOCKFMT = 0x2` within `E_BLOCK`.

### 3.2) Missing/invalid descriptor reporting

- `TRAPARG0[7:0] = MissingDescFamily`:
  - `1=B.DIM`, `2=B.TEXT`, `3=B.ARG`, `4=B.IOR`, `5=B.IOT/B.IOTI`
- `TRAPARG0[15:8]=MissingDetail`:
  - `0x00` missing
  - `0x01` invalid/out-of-range
  - `0x02` illegal combination
  - `0x03..0xFF` op/template-specific

Other rules:

- Multiple missing families: report exactly one; priority order:
  1. `B.ARG`
  2. `B.TEXT`
  3. `B.IOT/B.IOTI`
  4. `B.IOR`
  5. `B.DIM`
- Must be detected during **header validation** before side effects.
- `BI=0`, precise.
- Applies to all block headers (scalar + tile/vector).
- Malformed `BSTART.*` / `BSTOP` instruction encodings remain `E_INST(EC_ILLEGAL)`.

See:
- `docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc`
- `docs/architecture/isa-manual/src/chapters/07_tile_blocks.adoc`

---

## 4) Body fetch faults (`EC_BFETCH`)

### 4.1) `E_BLOCK(EC_BFETCH)` encoding

- `EC_BFETCH = 0x3` within `E_BLOCK`.

### 4.2) Split policy (MMU vs non-MMU)

- MMU translation/access faults during body fetch/execute => `E_DATA` (trap context indicates `BI=1` body context).
- Non-MMU body fetch faults (e.g. misaligned body entry) => `E_BLOCK(EC_BFETCH)`.

### 4.3) Reporting

- For `E_BLOCK(EC_BFETCH)`, `TRAPARG0` = faulting body-fetch VA.
- `BI=1`.
- Non-MMU `EC_BFETCH` misalignment faults are **fatal** (non-restartable).

### 4.4) Alignment

- Decoupled `BodyTPC` (legacy name for body-entry `TPC`) must be 2-byte aligned.
- SIMT `B.TEXT` targets must be 2-byte aligned.

See:
- `docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc`
- `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`
- `docs/architecture/isa-manual/src/chapters/07_tile_blocks.adoc`

---

## 5) Program counters terminology

- `TPC` is **Temporary PC** (not Thread PC).
- `BodyTPC` is legacy/prose naming for body-entry `TPC`.

See:
- `docs/architecture/isa-manual/src/chapters/02_programming_model.adoc`
- `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`

---

## 6) Template replay flags / IDs

- `EBARG_TPLFLAGS` bitfields standardized; `TPL_PHASE` meanings standardized.
- Marker-template `TPL_ID` mnemonic enum defined in `06_templates.adoc`.
- `TPL_ID_PRESENT` must be 1 for marker templates and TEPL.

See:
- `docs/architecture/isa-manual/src/chapters/09_system_and_privilege.adoc`
- `docs/architecture/isa-manual/src/chapters/06_templates.adoc`

---

## 7) SIMT bodies terminators

- SIMT out-of-line body streams may terminate on `BSTOP` or `BSTART`; first terminator wins.
- `BSTART` terminator is a **terminator trigger only**, not an in-body successor.

See:
- `docs/architecture/isa-manual/src/chapters/04_block_isa.adoc`
- `docs/architecture/isa-manual/src/chapters/07_tile_blocks.adoc`

---

## 8) Tile/vector block chapter

A new chapter documents per-block mandatory descriptor contracts:

- `07_tile_blocks.adoc`

---

## 9) TEPL encoding, maps, and status

- Canonical TEPL map is published in manual (`04_block_isa.adoc`), and additionally mirrored in:
  - `isa/v0.3/state/engine_ops.json` (authoritative semantic catalog seed)
  - `docs/bringup/tepl_status.yaml` (bring-up status; per-op gate list)
- Gate tooling (manual run for now): `tools/bringup/check_tepl_encoding.py`

Recent changes:

- `TCOLEXPAND` moved to `0x0C0` (legacy `0x027` non-canonical).
- Added `TROWEXPAND=0x0C1`.

---

## Notes

This file is updated as decisions land. If anything here conflicts with the canonical manual/contract, the manual/contract
wins; please file an issue to reconcile.
