# VECTOR/CUBE First-Use PTO/QEMU Synchronization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the LinxISA first-use exception authority with an exact PTO profile-hook provenance record, an executable QEMU implementation, and a refreshed model authority pin without creating a release.

**Architecture:** PTO-SPEC owns a portable, disabled-by-default profile hook while LinxISA owns concrete trap numbers, ECONFIG bits, and ACR routing. QEMU checks the Linx profile at runtime before block resource allocation or effects. LinxISA records the merged PTO hook commit/hash separately from the immutable PTO 0.58.1 release lock, then repins merged QEMU and model leaves atomically.

**Tech Stack:** ASL1/ASLRef, JSON profile metadata, Python contract tests, QEMU TCG/C helpers and migration state, Sail/LinxISA generators, GitHub pull requests.

## Global Constraints

- Do not create or move any release tag.
- Keep `isa/v0.58/pto-spec.lock.json` and the `.note.pto.isa` descriptor byte-identical.
- Keep LinxISA version `0.58.1` and codec shape `765/2661/3401/780` unchanged.
- First use is exact `E=1`, `ARGV=1`, `E_INST=0`, `EC_PERM=4`, `BI=0`, with `TRAPARG0=0` for VECTOR and `1` for CUBE.
- VECTOR triggers are exactly MPAR/MSEQ/VPAR/VSEQ and their four compressed forms; TEPL VEC/SFU aliases do not trigger.
- CUBE membership is derived from canonical PTO operation rows with `family=CUBE` and `engine=CUBE`.
- First-use validation occurs after legal decode/target/ACR permission and before resource allocation or effects.
- Work leaf-first: merge PTO-SPEC, QEMU, and model before changing superproject gitlinks.

---

### Task 1: Add the portable PTO first-use profile hook

**Files:**
- Create: `PTO-SPEC/asl/arch/profile/extension-first-use.asl`
- Create: `PTO-SPEC/docs/arch/profile/extension-first-use.md`
- Create: `PTO-SPEC/tests/asl/arch/profile/extension-first-use/arch-static-extension-first-use-contract-001.asl`
- Create: `PTO-SPEC/tests/asl/arch/profile/extension-first-use/arch-exec-extension-first-use-default-001.asl`
- Create: `PTO-SPEC/docs/status/decisions/0068-extension-first-use-profile-hook.md`
- Modify: `PTO-SPEC/spec/profile-hooks.json`
- Modify: PTO generated source order, release inputs, manifest, documentation navigation, and traceability files selected by repository generators

**Interfaces:**
- Consumes: existing `AccessControlRing`, trap-context state, and `PTO-REQ-FAULT-001`.
- Produces: `ExtensionFirstUseKind`, `ExtensionFirstUseEnabled(kind)`, and `RaiseExtensionFirstUse(kind, source, manager)` profile surfaces plus an exact machine-readable hook row.

- [ ] **Step 1: Create a PTO issue and isolated topic**

Create a GitHub issue that names PTO-SPEC `652e9b5bbee2ffea8917f9caa8c6e87be99fe05c` as baseline, cites `PTO-REQ-FAULT-001`, states portable default disabled, and records no release impact. Create `codex/extension-first-use-profile-hook` from live `origin/main` in a dedicated worktree.

- [ ] **Step 2: Write the failing static hook test**

The static ASL point must reference the new enum and both profile functions, assert VECTOR and CUBE have distinct values, and fail before production sources exist.

Run:

```bash
python3 scripts/print-asl-test-matrix --refresh
python3 scripts/run-asl-test --id arch-static-extension-first-use-contract-001
```

Expected: FAIL because `ExtensionFirstUseKind` and the profile functions are undefined.

- [ ] **Step 3: Write the failing executable portable-default test**

Reset the reference profile, call `ExtensionFirstUseEnabled` for both kinds, and assert both return `FALSE` without changing `_ACRTrap*`, BARG, queues, memory-event state, or fault state.

Run:

```bash
python3 scripts/run-asl-test --id arch-exec-extension-first-use-default-001
```

Expected: FAIL because the portable default does not exist.

- [ ] **Step 4: Implement the minimal portable hook**

Define a two-value enum and disabled-by-default `impdef readonly` enable query. Define an `impdef` raise hook whose portable implementation returns `FALSE` and performs no effects. Put concrete trap numbers, ECONFIG positions, and Linx ACR routing outside PTO portable semantics.

- [ ] **Step 5: Register the profile hook and decision**

Add a `spec/profile-hooks.json` row with domain `extension-first-use`, portable default `disabled/no architectural effects`, requirement `PTO-REQ-FAULT-001`, target obligations matching the approved design, and both test IDs. Record the accepted profile boundary in decision 0068 and regenerate the exact Markdown/source-order/manifest/traceability projections with repository scripts.

- [ ] **Step 6: Verify GREEN and repository closure**

Run:

```bash
python3 scripts/print-asl-test-matrix --refresh
python3 scripts/run-asl-test --id arch-static-extension-first-use-contract-001
python3 scripts/run-asl-test --id arch-exec-extension-first-use-default-001
make pr-check
make repo-check
git diff --check
```

Expected: both focused tests and both repository gates PASS; no release tag or version changes.

- [ ] **Step 7: Commit, push, open PR, and merge exact head**

Commit `arch: add extension first-use profile hook`, open a PTO-SPEC PR to `main`, require hosted checks, squash-merge, and record merged commit, tree, hook path, and hook SHA-256.

---

### Task 2: Implement exact QEMU first-use traps with TDD

**Files:**
- Create: `emulator/qemu/tests/linxisa/test_first_use_exception.py`
- Create: `emulator/qemu/tests/linxisa/first_use_exception.S`
- Create: `emulator/qemu/scripts/linxisa/run-first-use-exception.sh`
- Modify: `emulator/qemu/target/linx/helper.h`
- Modify: `emulator/qemu/target/linx/helper.c`
- Modify: `emulator/qemu/target/linx/translate.c`
- Modify: `emulator/qemu/target/linx/cpu.c`
- Modify: `emulator/qemu/tests/linxisa/test_v058_review_contract.py`

**Interfaces:**
- Consumes: LinxISA compiled first-use contract and the merged PTO profile-hook identity from Task 1.
- Produces: runtime helper `linx_extension_first_use` that returns normally when disabled/inapplicable and raises the exact synchronous exception when enabled.

- [ ] **Step 1: Create a clean QEMU topic from canonical master**

Fetch `origin/master`, verify the checked-out base equals canonical master, then create `codex/first-use-exception` without committing on detached HEAD.

- [ ] **Step 2: Write static RED tests for ECONFIG and trigger coverage**

The Python contract must require reset `0x0000000300000008`, allowed mask `0x000000030000000f`, eight VECTOR opcode IDs, CUBE catalog-derived classification, no TEPL VEC/SFU inclusion, helper call before `linx_block_begin`, and migration coverage through banked `ssr_acr`.

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest emulator/qemu/tests/linxisa/test_first_use_exception.py -v
```

Expected: FAIL on missing helper/reset/masking/trigger implementation.

- [ ] **Step 3: Write executable RED trap tests**

Build one ACR2 fixture that sets ACR1 ECONFIG.V/C, executes each covered header, records ACR1 TRAPNO/TRAPARG0/ECSTATE plus BARG/queue/tile sentinel state, clears only the triggering bit, retries, and exits through the finisher. Include invalid-target, ACR0/ACR1, and TEPL negative cases.

Run:

```bash
QEMU=/tmp/linx-qemu-first-use-red/qemu-system-linx64 \
  bash emulator/qemu/scripts/linxisa/run-first-use-exception.sh
```

Expected: FAIL because covered headers execute without first-use traps.

- [ ] **Step 4: Implement ECONFIG reset and write masking**

Initialize every ACR bank at reset with `0x0000000300000008`. In `linx_ssr_write`, mask ECONFIG writes with `0x000000030000000f`; reads use the existing banked SSR path. Retain `ssr_acr` VMState and add focused assertions proving the state is migrated.

- [ ] **Step 5: Implement the pre-effect helper**

Add `DEF_HELPER_3(linx_extension_first_use, void, env, i32, i64)` where arguments are kind and instruction PC. The helper returns unless source ACR is 2 and the corresponding ACR1 V/C bit is set. On trap it sets pending cause `4`, argument `0/1`, preserves the original header PC for retry, and raises the synchronous instruction-exception path before any generated header state mutation.

- [ ] **Step 6: Wire exactly eight VECTOR headers and catalog-bound CUBE headers**

Emit the helper immediately after decode/target legality checks and before `linx_block_begin` in MPAR/MSEQ/VPAR/VSEQ and their compressed decoders. In the tile header path, call it only when canonical block type/family is CUBE; use a generated/static contract check against the twelve LinxISA CUBE rows. Do not call it for TEPL VEC/SFU.

- [ ] **Step 7: Verify focused GREEN**

Run the Python contract, clean QEMU build, native unit tests, and executable runner. Expected: exact envelope for both kinds, no state changes on trap, independent bit clearing, retry success, and all negative cases PASS.

- [ ] **Step 8: Run QEMU regression gates**

Run sequentially:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s emulator/qemu/tests/linxisa -p 'test_*.py' -v
meson test -C /tmp/linx-qemu-first-use-build \
  test-linx-tile-transaction test-linx-tile-cube-numeric test-linx-tile-state-dump
QEMU=/tmp/linx-qemu-first-use-build/qemu-system-linx64 \
  bash avs/qemu/check_system_strict.sh
cd avs/qemu && QEMU=/tmp/linx-qemu-first-use-build/qemu-system-linx64 \
  ./run_tests.sh --all --timeout 10
```

Expected: all PASS with no shared-output race.

- [ ] **Step 9: Commit, push, open PR, and merge exact head**

Commit `linxisa: implement VECTOR and CUBE first-use traps`, open a QEMU PR to `master`, require hosted/focused evidence, squash-merge, and record merged commit/tree.

---

### Task 3: Refresh linx-model authority without changing codecs

**Files:**
- Modify: `tools/model/tools/isa/gen_minst_codec.py`
- Modify: `tools/model/docs/isa.md`
- Modify: `tools/model/tests/checks/test_gen_minst_codec.py`

**Interfaces:**
- Consumes: final PR #178 compiled catalog bytes before gitlink repin.
- Produces: exact new catalog SHA authentication with byte-identical generated codec tables and unchanged counts.

- [ ] **Step 1: Create model topic from canonical main**

Create `codex/first-use-authority` from live `origin/main`.

- [ ] **Step 2: Capture RED freshness failure**

Run the existing generator check against the PR worktree. Expected: FAIL with old catalog hash `c1750250...` versus the new catalog hash.

- [ ] **Step 3: Update exact authority hash and tests**

Replace only `EXPECTED_CATALOG_CONTENT_SHA256` and the documented value. Extend the authority mutation test to show a first-use numeric mutation fails content authentication. Do not change `EXPECTED_CODEC_COUNTS`, generated tables, lock hash, release-manifest hash, or PTO identity.

- [ ] **Step 4: Verify codec parity and model tests**

Run:

```bash
cmake -S tools/model -B /tmp/linx-model-first-use -G Ninja \
  -DLINXISA_AUTHORITY_ROOT="$PWD"
cmake --build /tmp/linx-model-first-use
ctest --test-dir /tmp/linx-model-first-use --output-on-failure
git diff --exit-code -- tools/model/include/linx/model/isa/generated_tables.hpp \
  tools/model/src/isa/generated_tables.cpp
```

Expected: all model tests PASS and generated tables are unchanged.

- [ ] **Step 5: Commit, push, open PR, and merge exact head**

Commit `test: authenticate first-use ISA authority`, merge to model `main`, and record merged commit/tree.

---

### Task 4: Bind PTO, QEMU, and model into LinxISA PR #178

**Files:**
- Create: `isa/v0.58/pto-profile-hooks.lock.json`
- Create: `tools/isa/check_pto_profile_hooks.py`
- Create: `tools/isa/test_pto_profile_hooks.py`
- Modify: `isa/v0.58/semantics_conventions.json`
- Modify: `isa/v0.58/linxisa-v0.58.json`
- Modify: `docs/bringup/component-lock.v0.58.json`
- Modify gitlinks: `emulator/qemu`, `tools/model`
- Modify: `.github/workflows/ci.yml` to invoke the new exact hook checker in the guards job

**Interfaces:**
- Consumes: merged PTO hook commit/tree/hash, merged QEMU commit/tree, merged model commit/tree.
- Produces: one exact superproject tree whose machine contract, PTO hook, QEMU, and model pins agree.

- [ ] **Step 1: Write RED PTO hook lock tests**

The test must fail when the lock is missing, repository/commit/tree/path/hash/profile ID differs, local trap mapping differs, or the existing common PTO lock changes.

Run:

```bash
python3 -m unittest tools.isa.test_pto_profile_hooks -v
```

Expected: FAIL because the lock/checker does not exist.

- [ ] **Step 2: Add the exact merged hook lock and checker**

Record the canonical PTO merged commit/tree/path/hash. Compute a deterministic SHA-256 over the concrete Linx mapping in `semantics_conventions.json`. The checker fetches no remote state; it validates only the checked-in lock, current machine contract, and an optional explicit PTO checkout used by CI/local verification.

- [ ] **Step 3: Repin merged QEMU and model leaves atomically**

Update the two gitlinks to canonical merged commits and update only their component-lock rows. Never pin topic heads.

- [ ] **Step 4: Regenerate LinxISA projections**

Run the golden builder, Sail status/coverage, SSR/manual generators, language map, and translation manifest. Confirm release/version/PTO common lock/ELF identity files have no diff.

- [ ] **Step 5: Run full local gates**

Run the mandatory LinxISA gate pack, new PTO hook tests, Sail parser/C backend, model build/CTest, QEMU focused tests, QEMU strict AVS and full AVS sequentially, component-lock tests, documentation checks, ruff, shellcheck, and `git diff --check`.

- [ ] **Step 6: Push exact PR head and require hosted checks**

Push `codex/first-use-exception`, update the PR description with merged leaf provenance, mark ready only after every required check is green on the exact head.

- [ ] **Step 7: Squash-merge PR #178 and prove identity**

Capture the reviewed head/tree, squash-merge, fetch `origin/main`, and prove the merge commit tree equals the reviewed PR head tree. Re-run focused contract and component-lock checks on canonical main.

- [ ] **Step 8: Delete merged topics safely**

Delete only the merged LinxISA, QEMU, model, and PTO topic branches after live reachability/tree checks. Preserve all release/tag branches and immutable tags.

---

## Plan self-review

- Spec coverage: PTO hook, QEMU runtime/migration, model freshness, root lock/repin, hosted merge, and cleanup are each owned by one task.
- Placeholders: none; every behavior change names its RED and GREEN test surface.
- Type consistency: `ExtensionFirstUseKind`, `ExtensionFirstUseEnabled`, `RaiseExtensionFirstUse`, and QEMU `linx_extension_first_use` are defined once and consumed consistently.
- Release boundary: common PTO lock, ELF identity, versions, and tags remain unchanged.
