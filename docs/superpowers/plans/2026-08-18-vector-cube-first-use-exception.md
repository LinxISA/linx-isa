# VECTOR/CUBE First-Use Exception Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an executable unreleased-main contract for precise VECTOR/CUBE first-use exceptions without publishing or renumbering the existing release.

**Architecture:** `isa/v0.58/state/system_registers.json` owns numeric trap/register state, while `isa/v0.58/semantics_conventions.json` owns trigger ordering and restart behavior. The golden catalog, Sail model, generated AsciiDoc, bilingual Markdown, and consumer-requirement packet are projections of those two sources. This plan intentionally stops at the ISA authority boundary; QEMU, Linux, and LinxCore implementation changes require separate leaf plans after the exact context layout and consumer packet merge.

**Tech Stack:** JSON, Python 3.11+, Sail 0.20.2, AsciiDoc, Markdown, MkDocs Material, unittest.

## Global Constraints

- `TRAPNO.E=1` means synchronous exception; `TRAPNO.E=0` means asynchronous interrupt.
- This change fixes only the first-use `E_INST=0` envelope. Existing PTO EBREAK trap 50 and current ASSERT, E_DATA, E_BLOCK, syscall, and debug trap numbers remain unchanged.
- First-use delivery is exactly `E=1`, `ARGV=1`, `TRAPNUM=E_INST(0)`, `CAUSE=EC_PERM(4)`, `BI=0`.
- `TRAPARG0=0` identifies VECTOR and `TRAPARG0=1` identifies CUBE.
- First-use `EC_PERM` is encoded as raw `CAUSE=4`; other E_INST producers keep their existing profile-specific cause format.
- Active sources must use `EC_PERM`; `E_PEREM` remains only in archived historical text.
- `ECONFIG.V=bit32`, `ECONFIG.C=bit33`, and reset is `0x0000000300000008`.
- VECTOR trigger forms are `BSTART.MPAR/MSEQ/VPAR/VSEQ` plus their compressed forms. `BSTART.VEC/SFU` on the TEPL carrier are excluded.
- CUBE trigger membership is derived from the canonical CUBE family, not a handwritten downstream mnemonic list.
- The first-use check occurs after legal decode/permission checks and before BARG/BSTATE mutation, resource allocation, queue insertion, memory issue, or other architectural effect.
- Active text uses `TLSU`; `TMA` may appear only in explicit historical-compatibility explanations.
- No new instruction encoding, dependency, or top-level directory is introduced.
- LinxISA version/status, release manifest, release navigation, and immutable `v0.58.1` tag remain unchanged.
- `isa/v0.58/pto-spec.lock.json` remains byte-identical; the PTO ELF descriptor and ABI remain unchanged.

---

## File and Interface Map

### Machine authority

- `isa/v0.58/state/system_registers.json`: ECONFIG layout/reset, TRAPNO.E polarity, and the exact first-use trap envelope.
- `isa/v0.58/semantics_conventions.json`: trigger set, ordering, precision, retry, internal-exception boundary, ESAVE progress contract.
- `isa/v0.58/linxisa-v0.58.json`: generated compiled projection; never hand-edit.

### Validation and generators

- `tools/isa/test_first_use_exception_contract.py`: exact source/compiled contract regression.
- `tools/isa/validate_spec.py`: fail-closed structural and cross-field validation.
- `tools/isa/gen_ssr_adoc.py`: generated TRAPNO, CAUSE, and ECONFIG tables.
- `tools/isa/test_first_use_exception_documentation.py`: bilingual and generated-document closure.

### Sail

- `isa/sail/model/state/state.sail`: trap envelope, ECONFIG reset/fields, observable trap state.
- `isa/sail/model/execute/execute.sail`: pre-allocation VECTOR/CUBE checks.
- `isa/sail/tests/directed.sail`: exact trap, no-effect, retry, and selective-bit cases.

### Documentation

- `docs/architecture/isa-manual/src/chapters/10_system_and_privilege.adoc`: normative English architecture chapter.
- `docs/architecture/isa-manual/src/generated/trapno_encoding.adoc`: generated trap/cause projection.
- `docs/architecture/isa-manual/src/generated/system_registers_ssr.adoc`: generated SSR projection.
- `docs/isa/exception/exception.md` and `docs/zh/isa/exception/exception.md`: bilingual exception semantics.
- `docs/isa/register/ssr/TRAPNO.md` and `docs/zh/isa/register/ssr/TRAPNO.md`: bilingual wire encoding.
- `docs/isa/register/ssr/ECONFIG.md` and `docs/zh/isa/register/ssr/ECONFIG.md`: bilingual field/reset/task-switch rules.
- `docs/bringup/first-use-exception-consumer-requirements.json`: machine-readable downstream packet.
- `docs/bringup/FIRST_USE_EXCEPTION_CONSUMER_REQUIREMENTS.md`: reviewer-facing packet view.
- `docs/zh/translation-manifest.json`: regenerated translation freshness metadata.

---

### Task 0: Preserve the current release identity

**Files:**
- Verify only: `isa/v0.58/meta.json`
- Verify only: `isa/v0.58/release_manifest.json`
- Verify only: `isa/v0.58/pto-spec.lock.json`
- Verify only: `tools/isa/test_v058_profile.py`
- Verify only: `tools/isa/check_canonical_v058.py`

**Interfaces:**
- Preserves: LinxISA version `0.58.1`, stable status, immutable tag, and exact PTO 0.58.1 identity
- Produces: no release artifact and no release commit

- [ ] **Step 1: Record the identity baseline**

```bash
test "$(python3 -c 'import json; print(json.load(open("isa/v0.58/meta.json"))["version"])')" = 0.58.1
test "$(python3 -c 'import json; print(json.load(open("isa/v0.58/release_manifest.json"))["version"])')" = 0.58.1
test "$(shasum -a 256 isa/v0.58/pto-spec.lock.json | awk '{print $1}')" = \
  fec69d22b2757ebb8da3876b16e1d5845af188f107f06d05422af15513309dfd
```

- [ ] **Step 2: Keep release files unchanged throughout implementation**

At every commit boundary, require `git diff origin/main -- isa/v0.58/meta.json isa/v0.58/release_manifest.json isa/v0.58/pto-spec.lock.json` to be empty. Do not create release notes, change MkDocs release navigation, or create/move a tag.

---

### Task 1: Freeze the first-use TRAPNO envelope and ECONFIG source contract

**Files:**
- Create: `tools/isa/test_first_use_exception_contract.py`
- Modify: `isa/v0.58/state/system_registers.json`
- Modify: `tools/isa/validate_spec.py`
- Regenerate: `isa/v0.58/linxisa-v0.58.json`

**Interfaces:**
- Produces: `state.system_registers.trapno_encoding.first_use_exception`
- Produces: `state.system_registers.econfig_contract`
- Consumes: no new interfaces

- [ ] **Step 1: Write a failing exact-contract test**

Create `tools/isa/test_first_use_exception_contract.py` with helpers that load both the source state and compiled catalog:

```python
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "isa/v0.58/state/system_registers.json"
COMPILED = ROOT / "isa/v0.58/linxisa-v0.58.json"

EXPECTED_FIRST_USE = {
    "e": 1,
    "argv": 1,
    "trapnum": "E_INST",
    "trapnum_value": 0,
    "cause": "EC_PERM",
    "cause_value": 4,
    "bi": 0,
    "traparg0": {"VECTOR": 0, "CUBE": 1},
}
```

Add tests asserting:

```python
self.assertEqual(source["trapno_encoding"]["first_use_exception"], EXPECTED_FIRST_USE)
self.assertEqual(source["econfig_contract"]["reset_value"], "0x0000000300000008")
self.assertEqual(source["econfig_contract"]["fields"]["V"]["bit"], 32)
self.assertEqual(source["econfig_contract"]["fields"]["C"]["bit"], 33)
self.assertEqual(compiled["state"]["system_registers"], source)
```

- [ ] **Step 2: Run the test and capture the red boundary**

Run:

```bash
python3 -m unittest tools.isa.test_first_use_exception_contract -v
```

Expected: FAIL because `first_use_exception` and `econfig_contract` do not exist.

- [ ] **Step 3: Add the scoped first-use exception envelope**

Keep `bringup_trapnums` byte-for-byte unchanged. Add under `trapno_encoding`:

```json
"first_use_exception": {
  "e": 1,
  "argv": 1,
  "trapnum": "E_INST",
  "trapnum_value": 0,
  "cause": "EC_PERM",
  "cause_value": 4,
  "bi": 0,
  "traparg0": {
    "VECTOR": 0,
    "CUBE": 1
  }
}
```

Correct the `E` field description to synchronous exception `1`, asynchronous interrupt `0`.

- [ ] **Step 4: Add the complete ECONFIG machine definition**

Add top-level `econfig_contract` under `system_registers`:

```json
"econfig_contract": {
  "width_bits": 64,
  "reset_value": "0x0000000300000008",
  "per_hardware_thread": true,
  "fields": {
    "E": {"bit": 0, "description": "External interrupt enable."},
    "T": {"bit": 1, "description": "Timer interrupt enable."},
    "S": {"bit": 2, "description": "Software interrupt enable."},
    "A": {"bit": 3, "description": "ASSERT instruction exception enable."},
    "V": {"bit": 32, "description": "VECTOR first-use exception enable."},
    "C": {"bit": 33, "description": "CUBE first-use exception enable."}
  },
  "reserved_ranges": [[4, 31], [34, 63]],
  "reserved_write": "must-zero",
  "reserved_read": "zero"
}
```

- [ ] **Step 5: Make `validate_spec.py` fail closed**

Add:

```python
def _validate_first_use_register_contract(spec: dict[str, Any], errors: list[str]) -> None:
    sysregs = ((spec.get("state") or {}).get("system_registers") or {})
    trap = sysregs.get("trapno_encoding") or {}
    if trap.get("first_use_exception") != EXPECTED_FIRST_USE:
        errors.append("v0.58: first-use exception envelope mismatch")
    econfig = sysregs.get("econfig_contract") or {}
    if econfig.get("reset_value") != "0x0000000300000008":
        errors.append("v0.58: ECONFIG reset must be 0x0000000300000008")
```

Call it for the current v0.58.1 development profile before instruction iteration. Also validate exact reserved ranges, exact V/C bits, absence of active `E_PEREM` keys, and that `bringup_trapnums` is unchanged from the baseline.

- [ ] **Step 6: Regenerate the compiled catalog**

Run:

```bash
python3 tools/isa/build_golden.py --profile v0.58
```

Expected: only machine-derived outputs change; hand-authored opcodes remain unchanged.

- [ ] **Step 7: Run focused and canonical tests**

```bash
python3 -m unittest tools.isa.test_first_use_exception_contract -v
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/test_golden_contract.py
```

Expected: PASS.

- [ ] **Step 8: Commit the numeric authority**

```bash
git add isa/v0.58/state/system_registers.json isa/v0.58/linxisa-v0.58.json \
  tools/isa/validate_spec.py tools/isa/test_first_use_exception_contract.py
git commit -m "isa: define first-use trap envelope and ECONFIG layout"
```

---

### Task 2: Add the executable first-use semantics contract

**Files:**
- Modify: `isa/v0.58/semantics_conventions.json`
- Modify: `tools/isa/test_first_use_exception_contract.py`
- Regenerate: `isa/v0.58/linxisa-v0.58.json`

**Interfaces:**
- Consumes: Task 1 trap/cause and ECONFIG schema
- Produces: `state.semantics_conventions.extension_first_use`

- [ ] **Step 1: Add red tests for the semantic envelope**

Extend the test with exact assertions:

```python
first_use = conventions["extension_first_use"]
self.assertEqual(first_use["source_acr"], 2)
self.assertEqual(first_use["manager_acr"], 1)
self.assertEqual(first_use["trap"], {
    "e": 1, "argv": 1, "trapnum": "E_INST", "trapnum_value": 0,
    "cause": "EC_PERM", "cause_value": 4, "bi": 0,
})
self.assertEqual(first_use["kinds"], {"VECTOR": 0, "CUBE": 1})
self.assertEqual(first_use["vector_headers"], [
    "BSTART.MPAR", "BSTART.MSEQ", "BSTART.VPAR", "BSTART.VSEQ",
    "C.BSTART.MPAR", "C.BSTART.MSEQ", "C.BSTART.VPAR", "C.BSTART.VSEQ",
])
self.assertNotIn("BSTART.VEC", first_use["vector_headers"])
self.assertNotIn("BSTART.SFU", first_use["vector_headers"])
```

- [ ] **Step 2: Run the focused test and verify failure**

```bash
python3 -m unittest tools.isa.test_first_use_exception_contract -v
```

Expected: FAIL at missing `extension_first_use`.

- [ ] **Step 3: Add `extension_first_use` to semantic conventions**

Add this shape:

```json
"extension_first_use": {
  "source_acr": 2,
  "manager_acr": 1,
  "trap": {
    "e": 1,
    "argv": 1,
    "trapnum": "E_INST",
    "trapnum_value": 0,
    "cause": "EC_PERM",
    "cause_value": 4,
    "bi": 0
  },
  "kinds": {"VECTOR": 0, "CUBE": 1},
  "econfig_bits": {"VECTOR": "V", "CUBE": "C"},
  "vector_headers": [
    "BSTART.MPAR", "BSTART.MSEQ", "BSTART.VPAR", "BSTART.VSEQ",
    "C.BSTART.MPAR", "C.BSTART.MSEQ", "C.BSTART.VPAR", "C.BSTART.VSEQ"
  ],
  "cube_membership": "state.pto_ops.operations entries with family=CUBE and engine=CUBE",
  "ordering": ["legal-decode", "acr-permission", "first-use", "resource-allocation", "effects"],
  "retry_pc": "faulting block-header PC",
  "zero_effects": ["BARG", "BSTATE", "queues", "memory-requests", "completion-state"],
  "internal_exception_boundary": {
    "VECTOR": "recoverable-internal-exceptions-allowed",
    "CUBE": "no-extension-owned-recoverable-internal-exceptions",
    "TLSU": "no-extension-owned-recoverable-internal-exceptions; memory faults are E_DATA"
  },
  "esave_forward_progress": "dedicated-path-or-reserved-capacity-required"
}
```

- [ ] **Step 4: Cross-check catalog membership in the test**

Build the active mnemonic set from `compiled["instructions"]`. Assert every `vector_headers` entry exists. Load `state.pto_ops.operations`, select exactly the rows with `family=CUBE` and `engine=CUBE`, assert the set contains `12` operations, cross-check `state.engine_ops.semantic_engine_counts.CUBE == 12`, and assert the convention derives CUBE membership rather than embedding a second name list.

- [ ] **Step 5: Regenerate and run focused tests**

```bash
python3 tools/isa/build_golden.py --profile v0.58
python3 -m unittest tools.isa.test_first_use_exception_contract -v
python3 tools/isa/validate_spec.py --profile v0.58
```

Expected: PASS.

- [ ] **Step 6: Commit the semantic contract**

```bash
git add isa/v0.58/semantics_conventions.json isa/v0.58/linxisa-v0.58.json \
  tools/isa/test_first_use_exception_contract.py
git commit -m "isa: define precise VECTOR and CUBE first-use traps"
```

---

### Task 3: Make the Sail model executable

**Files:**
- Modify: `isa/sail/model/state/state.sail`
- Modify: `isa/sail/model/execute/execute.sail`
- Modify: `isa/sail/tests/directed.sail`

**Interfaces:**
- Consumes: `extension_first_use` values from Tasks 1-2
- Produces: `trapnum_e_inst()`, `trap_extension_first_use(kind)`, `exec_vector_bstart()`, CUBE pre-admission check

- [ ] **Step 1: Write directed red cases**

Add a reset helper that sets ACR2, manager ECONFIG, BARG/tile state, and observable trap registers. Add assertions for:

```sail
reset_first_use_case(0x0000_0000_0000_1000);
ssr_econfig_acr1 = 0x0000_0003_0000_0008;
exec_bstart_mpar();
assert(last_trapnum == 0x00);
assert(last_cause == 0x000004);
assert(last_traparg0 == 0x0000_0000_0000_0000);
assert(last_e == 0b1);
assert(last_argv == 0b1);
assert(last_bi == 0b0);
assert(not_bool(barg_valid));
assert(barg_commit_seqno == 0x0000_0000_0000_0000);
```

Add matching CUBE, disabled-bit retry, and selective V/C cases.

- [ ] **Step 2: Run directed tests and verify the red boundary**

```bash
eval "$(opam env)"
sail -o /tmp/linx-first-use-directed isa/sail/tests/directed.sail
```

Expected: FAIL because `last_e`, `last_argv`, and first-use execution helpers do not exist.

- [ ] **Step 3: Add a scoped Sail first-use trap helper**

Keep existing E_DATA, E_BLOCK, ASSERT, breakpoint, syscall, debug, and generic illegal-instruction helpers unchanged. Add:

```sail
function trapnum_e_inst() -> bits(6) = { sail_zeros(6) }
function trap_extension_first_use(kind : bits(1)) -> unit = {
  raise_trap_full(
    0b1, 0b1, trapnum_e_inst(),
    sail_zero_extend(0x04, 24),
    sail_zero_extend(kind, 64), 0b0
  )
}
```

Do not route any pre-existing producer through this helper.

- [ ] **Step 4: Record E/ARGV and correct ECONFIG reset**

Add observable registers:

```sail
register last_e : bits(1) = 0b0
register last_argv : bits(1) = 0b0
```

Add `raise_sync_trap(argv, trapnum, cause, traparg0, bi)` that records `last_e=1`. Preserve existing `raise_trap` call sites through a wrapper while migrating architecture-sensitive paths explicitly.

Set all ECONFIG reset declarations to `0x0000_0003_0000_0008`. Mask reserved bits on SSR writes with `0x0000_0003_0000_000F`.

- [ ] **Step 5: Add first-use helpers**

```sail
function first_use_enabled(kind : bits(1)) -> bool = {
  current_acr_id() == 0x2 &
  (if kind == 0b0 then ssr_econfig_acr1[32] == 0b1
   else ssr_econfig_acr1[33] == 0b1)
}

function trap_extension_first_use(kind : bits(1)) -> unit = {
  trap_e_inst(0x04, sail_zero_extend(kind, 64), 0b1)
}
```

- [ ] **Step 6: Gate VECTOR before generic block transition**

Add:

```sail
function exec_vector_bstart() -> unit = {
  if first_use_enabled(0b0) then trap_extension_first_use(0b0)
  else exec_bstart()
}
```

Route all eight normal/compressed MPAR/MSEQ/VPAR/VSEQ entry functions through it.

- [ ] **Step 7: Gate CUBE before resource allocation**

For generic `exec_bstart_cube()` and `exec_tile_bstart(family, selector)`, test `family==0b10` before calling `exec_bstart_transition()` or `tile_effect_begin()`. On a trap, leave `tile_effect_pending`, descriptor state, BARG, and commit counters unchanged.

- [ ] **Step 8: Run Sail and generator gates**

```bash
eval "$(opam env)"
python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend
python3 tools/isa/sail_coverage.py --check
python3 tools/isa/gen_sail_decode.py --check
python3 tools/isa/gen_sail_status.py --check
```

Expected: parser, directed semantics, decode freshness, C backend, and coverage pass.

- [ ] **Step 9: Commit Sail semantics**

```bash
git add isa/sail/model/state/state.sail isa/sail/model/execute/execute.sail isa/sail/tests/directed.sail
git commit -m "sail: execute VECTOR and CUBE first-use exceptions"
```

---

### Task 4: Generate and publish the bilingual normative documentation

**Files:**
- Modify: `tools/isa/gen_ssr_adoc.py`
- Modify: `docs/architecture/isa-manual/src/chapters/10_system_and_privilege.adoc`
- Regenerate: `docs/architecture/isa-manual/src/generated/trapno_encoding.adoc`
- Regenerate: `docs/architecture/isa-manual/src/generated/system_registers_ssr.adoc`
- Modify: `docs/isa/exception/exception.md`
- Modify: `docs/zh/isa/exception/exception.md`
- Modify: `docs/isa/register/ssr/TRAPNO.md`
- Modify: `docs/zh/isa/register/ssr/TRAPNO.md`
- Modify: `docs/isa/register/ssr/ECONFIG.md`
- Modify: `docs/zh/isa/register/ssr/ECONFIG.md`
- Create: `tools/isa/test_first_use_exception_documentation.py`
- Regenerate: `docs/zh/translation-manifest.json`

**Interfaces:**
- Consumes: Tasks 1-3 machine contract
- Produces: one English and one Chinese normative explanation with generated numeric tables

- [ ] **Step 1: Write documentation closure tests**

Assert both language trees contain the exact strings and no active `E_PEREM`:

```python
for path in (EN_EXCEPTION, ZH_EXCEPTION, EN_ECONFIG, ZH_ECONFIG):
    text = path.read_text(encoding="utf-8")
    self.assertIn("E_INST", text)
    self.assertIn("EC_PERM", text)
    self.assertNotIn("E_PEREM", text)
self.assertIn("bit 32", EN_ECONFIG.read_text())
self.assertIn("位 32", ZH_ECONFIG.read_text())
```

Also assert the generated AsciiDoc contains `E_INST |0`, `EC_PERM |4`, ECONFIG reset, and V/C rows.

- [ ] **Step 2: Run the documentation test red**

```bash
python3 -m unittest tools.isa.test_first_use_exception_documentation -v
```

Expected: FAIL on the current generated table and placeholder ECONFIG image.

- [ ] **Step 3: Extend `gen_ssr_adoc.py`**

Keep the existing generated bring-up trap table unchanged. Extend `gen_trapno_encoding()` with one generated `first_use_exception` table and add `gen_econfig_contract()` to `system_registers_ssr.adoc` with field, bit, reset, and reserved behavior rows.

The generator must not contain numeric E_INST/ECONFIG constants; it reads them from JSON.

- [ ] **Step 4: Rewrite the manual trap section**

Keep all existing non-first-use trap-number descriptions intact. Correct `TRAPNO.E` polarity and add the precise `E_INST(0)/EC_PERM(4)` first-use envelope and trigger ordering in a separate subsection.

- [ ] **Step 5: Rewrite bilingual exception pages**

Insert the approved block-execution constraints and first-use sections. Include the exact `NEVER_USED`, `SAVED_NOT_RESTORED`, and `LIVE` context-state table. Separate normative architecture rules from the Linux `TIF_VECTOR/TIF_CUBE` example. Use TLSU in active prose and explain memory-system `E_DATA` separately.

- [ ] **Step 6: Replace the placeholder ECONFIG diagram with tables**

Remove the placeholder SVG reference from both ECONFIG pages. Render the exact bit table, reset value, per-thread scope, manager ACR rule, selective clear behavior, and context-switch rewrite requirement directly in Markdown.

- [ ] **Step 7: Regenerate AsciiDoc and translation metadata**

```bash
python3 tools/isa/gen_ssr_adoc.py --profile v0.58
python3 tools/docs/update_translation_manifest.py
```

- [ ] **Step 8: Run documentation validation**

```bash
python3 -m unittest tools.isa.test_first_use_exception_documentation -v
python3 tools/isa/gen_ssr_adoc.py --profile v0.58 --check
python3 tools/docs/update_translation_manifest.py --check
python3 docs/check_documentation.py --root .
mkdocs build --strict --site-dir /tmp/linx-first-use-en
mkdocs build --strict --config-file mkdocs.zh.yml --site-dir /tmp/linx-first-use-zh
```

Expected: PASS.

- [ ] **Step 9: Commit normative documentation**

```bash
git add tools/isa/gen_ssr_adoc.py tools/isa/test_first_use_exception_documentation.py \
  docs/architecture/isa-manual/src/chapters/10_system_and_privilege.adoc \
  docs/architecture/isa-manual/src/generated/trapno_encoding.adoc \
  docs/architecture/isa-manual/src/generated/system_registers_ssr.adoc \
  docs/isa/exception/exception.md docs/zh/isa/exception/exception.md \
  docs/isa/register/ssr/TRAPNO.md docs/zh/isa/register/ssr/TRAPNO.md \
  docs/isa/register/ssr/ECONFIG.md docs/zh/isa/register/ssr/ECONFIG.md \
  docs/zh/translation-manifest.json
git commit -m "docs: specify first-use exception and ECONFIG contracts"
```

---

### Task 5: Publish a fail-closed downstream consumer packet

**Files:**
- Create: `docs/bringup/first-use-exception-consumer-requirements.json`
- Create: `docs/bringup/FIRST_USE_EXCEPTION_CONSUMER_REQUIREMENTS.md`
- Create: `tools/bringup/check_first_use_exception_requirements.py`
- Create: `tools/bringup/test_first_use_exception_requirements.py`
- Modify: `docs/bringup/README.md`

**Interfaces:**
- Consumes: exact machine contract from Tasks 1-4
- Produces: versioned QEMU/Linux/LinxCore/Sail implementation requirements without mutating leaf code

- [ ] **Step 1: Write a failing requirements-schema test**

Require this top-level shape:

```json
{
  "schema": "linx-first-use-exception-consumers-v1",
  "source_profile": "0.58.1-unreleased-main",
  "contract": {
    "trapnum": 0,
    "cause": 4,
    "vector_arg0": 0,
    "cube_arg0": 1,
    "econfig_v_bit": 32,
    "econfig_c_bit": 33
  },
  "consumers": []
}
```

The test requires exactly `emulator/qemu`, `kernel/linux`, `rtl/LinxCore`, and `tools/model`, with `status="required"` and exact owned file lists.

- [ ] **Step 2: Run the red test**

```bash
python3 -m unittest tools.bringup.test_first_use_exception_requirements -v
```

Expected: FAIL because the packet/checker does not exist.

- [ ] **Step 3: Create the JSON packet**

Record, for each consumer:

- required trigger point;
- exact no-effect boundary;
- exact trap fields;
- state/reset/migration additions;
- positive, negative, retry, and task-switch test requirements;
- `implementation_status: "required-not-implemented"`.

Do not record a topic SHA or claim runtime support.

- [ ] **Step 4: Implement the packet checker**

`check_first_use_exception_requirements.py` loads the packet and current compiled ISA, proves every numeric field matches the machine authority, proves the consumer set is exact, and rejects `implemented/pass` status without an exact merged commit plus evidence URL.

- [ ] **Step 5: Write the Markdown view**

Summarize ownership:

- QEMU: block-header admission, ECONFIG storage/migration, exact trap/retry tests.
- Linux: three-state task context, selective V/C programming, save/restore hooks.
- LinxCore: pre-allocation trap and ESAVE forward-progress proof.
- tools/model: trace-visible exact trap/no-effect behavior.

The Linux row must name all three required states (`NEVER_USED`, `SAVED_NOT_RESTORED`, `LIVE`) and reject a design that uses only one `TIF_*` bit to distinguish allocation from residency.

- [ ] **Step 6: Run checker and tests**

```bash
python3 tools/bringup/check_first_use_exception_requirements.py --root .
python3 -m unittest tools.bringup.test_first_use_exception_requirements -v
```

Expected: PASS while truthfully reporting all leaf implementations as required-not-implemented.

- [ ] **Step 7: Commit the consumer packet**

```bash
git add docs/bringup/first-use-exception-consumer-requirements.json \
  docs/bringup/FIRST_USE_EXCEPTION_CONSUMER_REQUIREMENTS.md docs/bringup/README.md \
  tools/bringup/check_first_use_exception_requirements.py \
  tools/bringup/test_first_use_exception_requirements.py
git commit -m "bringup: publish first-use exception consumer requirements"
```

---

### Task 6: Run full release gates and integrate the ISA contract

**Files:**
- Modify only if a gate exposes a defect in Tasks 1-5
- Review range: `origin/main..HEAD`

**Interfaces:**
- Consumes: all prior tasks
- Produces: reviewed canonical superproject commit and immutable evidence

- [ ] **Step 1: Run mandatory ISA gates**

```bash
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/test_v058_profile.py
python3 tools/isa/check_pto_v058_manifest.py --root .
python3 tools/isa/check_canonical_v058.py --root .
python3 tools/isa/check_agent_navigation.py --root .
python3 tools/isa/gen_qemu_codec.py --check
python3 tools/isa/gen_c_codec.py --check
python3 tools/isa/gen_sail_decode.py --check
python3 tools/isa/gen_sail_status.py --check
```

- [ ] **Step 2: Run executable Sail gates**

```bash
eval "$(opam env)"
python3 tools/bringup/check_sail_model.py --require-parser --require-c-backend
python3 tools/isa/sail_coverage.py --check
```

- [ ] **Step 3: Run contract and documentation tests**

```bash
python3 -m unittest \
  tools.isa.test_first_use_exception_contract \
  tools.isa.test_first_use_exception_documentation \
  tools.bringup.test_first_use_exception_requirements -v
python3 tools/bringup/check_first_use_exception_requirements.py --root .
python3 docs/check_documentation.py --root .
python3 tools/docs/update_translation_manifest.py --check
bash tools/ci/check_repo_layout.sh
```

- [ ] **Step 4: Run lint and diff checks**

```bash
git ls-files -z '*.py' | xargs -0 ruff check --config ruff.toml --force-exclude
git ls-files -z '*.sh' | xargs -0 shellcheck -x -S error
git diff --check origin/main..HEAD
```

- [ ] **Step 5: Perform inline exact-range review**

Inspect every changed machine field, generated projection, Sail branch, bilingual paragraph, and consumer status. Reject:

- numeric values duplicated outside machine authority;
- active `E_PEREM` spelling;
- `BSTART.VEC/SFU` in the VECTOR trigger list;
- claims that QEMU/Linux/LinxCore already implement the feature;
- any first-use path that calls `exec_bstart_transition()` or `tile_effect_begin()` before trapping.
- any change to existing non-first-use trap numbers, including PTO EBREAK trap 50 or current ASSERT/E_DATA/E_BLOCK values.

- [ ] **Step 6: Push and open the architecture PR**

```bash
git push -u origin codex/first-use-exception
gh pr create --repo LinxISA/linx-isa --base main \
  --head codex/first-use-exception \
  --title "isa: add VECTOR and CUBE first-use exceptions"
```

- [ ] **Step 7: Require exact-head hosted checks**

Confirm guards, AVS/Sail, docs, lint, model, and final guard all pass on the exact reviewed head. A skipped, stale-head, or missing job is not a pass.

- [ ] **Step 8: Squash merge and verify tree identity**

```bash
gh pr merge <PR> --repo LinxISA/linx-isa --squash --delete-branch=false
git fetch origin main
test "$(git rev-parse <reviewed-head>^{tree})" = "$(git rev-parse origin/main^{tree})"
git diff --quiet <reviewed-head> origin/main
```

- [ ] **Step 9: Delete the merged topic and retain the design/plan history in main**

Delete only the exact merged local/upstream topic with force-with-lease. Keep release/tag branches unchanged, and verify `v0.58.1` still resolves to its immutable commit. Re-run the three new contract checks against canonical `origin/main`.

---

## Separate Follow-On Plans

After this plan merges, create one leaf plan per consumer from the machine-readable packet:

1. QEMU executable delivery and migration.
2. Linux task allocation/save/restore and ECONFIG programming.
3. LinxCore pre-allocation trap plus ESAVE resource proof.
4. tools/model trace parity and superproject repin.

Those plans may begin only after the canonical ISA PR merge SHA is available. They must pin the merged authority commit, not this topic head.
