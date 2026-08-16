# LinxISA v0.58.1 Superproject Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver one verified LinxISA superproject `main` whose active leaves, documentation, Pages deployment, and retained branch history all agree with the exact released `0.58.1` authority.

**Architecture:** Execute a leaf-first corrective train from immutable root tag `v0.58.1`, repairing each producer and consumer before atomically updating root gitlinks and the component lock. Port only reviewed unique branch content, publish the Chinese MkDocs build as Pages, archive explicitly historical material, and delete stale refs only through an exact-OID read-only cleanup manifest after the integrated commit is merged.

**Tech Stack:** Git submodules and GitHub PRs, Python 3, LLVM/LLD lit, CMake/Ninja/CTest, QEMU, Linux KUnit/build scripts, glibc/musl loaders, Scala/Chisel, pyCircuit, MkDocs, GitHub Actions, JSON release manifests.

## Global Constraints

- LinxISA profile remains `v0.58`; do not create `isa/v0.58.1/`.
- Release is exactly `0.58.1` and encoding ABI is exactly `pto-isa-0.58.1-mode-function-v1`.
- Encoding projection SHA-256 is exactly `89b872d6eaf0252200bc9349d49b9346e2a69d894cdcc2dcd0fd71911c1e0b8c`.
- PTO source commit/tree are exactly `c381465b2b8e457e162a4246ee58bb9a2c5b49fd` and `463a19db3d6ba70022f18bdbca0d4b2c6ed586e4`.
- Catalog counts are exactly 474 scalar forms, 74 command forms, 109 tile operations, and 32 extension reservations.
- Tile engines are exactly `VEC`, `SFU`, `TLSU`, and `CUBE`; `TEPL` is an encoding carrier only.
- English documents remain normative; GitHub Pages publishes the Chinese `mkdocs.zh.yml` build; both builds must be strict-clean.
- Existing root and leaf tags are immutable. Do not move, delete, or retag `v0.58.1` or any existing `linxisa-v0.58.*` tag.
- Never repin a topic head. Each ordinary leaf pin must be the exact canonical merged SHA; LinxCoreModel remains the documented review-only open-PR exception.
- Never use an unpinned submodule remote update. Initialize and update only the leaf owned by the current task.
- Historical or stale evidence cannot satisfy a current gate; every promotion result must bind the exact current SHAs and non-empty artifacts.
- Tests for behavior changes are written and observed failing before production changes.
- Preserve user-owned worktrees and unrelated commits. Stage only reviewed files and gitlinks.
- Retain release branches and immutable tags; delete only exact reviewed stale refs after live OID, worktree, reachability, and replacement checks pass.

---

### Task 1: Upgrade the LLVM producer and LLD consumer to exact 0.58.1

**Files:**
- Modify: `compiler/llvm/llvm/lib/Target/LinxISA/MCTargetDesc/LinxISAMCTargetDesc.cpp`
- Modify: `compiler/llvm/lld/ELF/InputFiles.cpp`
- Modify: `compiler/llvm/lld/ELF/SyntheticSections.cpp`
- Replace from root generator: `compiler/llvm/isa/generated/codecs/linxisa_opcodes.c`
- Verify unchanged or regenerated: `compiler/llvm/isa/generated/codecs/linxisa_opcodes.h`
- Modify: `compiler/llvm/llvm/lib/Target/LinxISA/AsmParser/LinxISAAsmParser.cpp`
- Modify: `compiler/llvm/llvm/lib/Target/LinxISA/MCTargetDesc/LinxISAInstPrinter.cpp`
- Modify: `compiler/llvm/llvm/lib/Target/LinxISA/MCTargetDesc/LinxISAMCCodeEmitter.cpp`
- Modify: `compiler/llvm/llvm/lib/Target/LinxISA/Disassembler/LinxISADisassembler.cpp`
- Test: `compiler/llvm/llvm/test/MC/LinxISA/v058-pto-raw-abi.s`
- Test: `compiler/llvm/llvm/test/MC/LinxISA/v058-reject-removed-spellings.s`
- Test: `compiler/llvm/llvm/test/MC/LinxISA/fused-call-exact.s`
- Test: `compiler/llvm/llvm/test/MC/LinxISA/v0571-pto-note-owned.s`
- Test: `compiler/llvm/lld/test/ELF/linxisa-pto-identity.test`

**Interfaces:**
- Consumes: root `isa/v0.58` generated C codec and exact PTO lock.
- Produces: canonical 0.58.1 ELF note bytes and merged LLVM SHA used by every later compile/runtime task.

- [ ] **Step 1: Create a clean LLVM topic from canonical `origin/main`**

```bash
git -C compiler/llvm fetch origin --tags
git -C compiler/llvm switch -c codex/v0581-release origin/main
```

- [ ] **Step 2: Write red MC/LLD tests**

Add literal checks for `B.FPATR`, `BSTART.ICALL <rt_label>, ->ra`, `L.BSTOP`,
the dot-form `BSTART.CALL`, rejection of the four removed FP/STD CALL/ICALL
forms, and exact rejection of a descriptor whose active release is changed
from `0.58.1` to `0.58.0`. The expected descriptor is:

```json
{"encoding_abi":"pto-isa-0.58.1-mode-function-v1","encoding_projection_sha256":"89b872d6eaf0252200bc9349d49b9346e2a69d894cdcc2dcd0fd71911c1e0b8c","release":"0.58.1"}
```

- [ ] **Step 3: Run the focused lit set and confirm the new cases fail for missing/stale behavior**

```bash
compiler/llvm/build-linxisa-clang/bin/llvm-lit -sv \
  compiler/llvm/llvm/test/MC/LinxISA/v058-pto-raw-abi.s \
  compiler/llvm/llvm/test/MC/LinxISA/v058-reject-removed-spellings.s \
  compiler/llvm/llvm/test/MC/LinxISA/fused-call-exact.s \
  compiler/llvm/llvm/test/MC/LinxISA/v0571-pto-note-owned.s \
  compiler/llvm/lld/test/ELF/linxisa-pto-identity.test
```

Expected: failures identify the 0.58.0 note, missing new forms, or accepted retired forms—not a missing test tool or syntax error.

- [ ] **Step 4: Regenerate and sync the canonical codec**

```bash
python3 tools/isa/gen_c_codec.py --profile v0.58 --out-dir isa/generated/codecs --check
LLVM_PROJECT="$PWD/compiler/llvm" bash tools/isa/sync_generated_opcodes.sh
cmp isa/generated/codecs/linxisa_opcodes.c compiler/llvm/isa/generated/codecs/linxisa_opcodes.c
cmp isa/generated/codecs/linxisa_opcodes.h compiler/llvm/isa/generated/codecs/linxisa_opcodes.h
```

- [ ] **Step 5: Implement the exact note and hand-coded form support**

Keep the descriptor at 165 bytes and note at 184 bytes. Add the 32-bit
`BSTART.ICALL` rt-label/CSETRET fixup at offset 2, PC-base printing at `+2`,
and remove dead comparisons for the retired FP/STD ICALL forms. Preserve the
existing HL space-name behavior.

- [ ] **Step 6: Build required LLVM tools and run focused plus full Linx tests**

```bash
cmake --build compiler/llvm/build-linxisa-clang --target \
  clang lld llvm-mc llvm-objdump llc FileCheck yaml2obj
compiler/llvm/build-linxisa-clang/bin/llvm-lit -sv \
  compiler/llvm/llvm/test/MC/LinxISA \
  compiler/llvm/lld/test/ELF/linxisa-pto-identity.test
TARGET=linx64-linx-none-elf make -C avs/compiler/linx-llvm check
TARGET=linx32-linx-none-elf make -C avs/compiler/linx-llvm check
```

- [ ] **Step 7: Commit, push, merge normally, and record the canonical SHA**

```bash
git -C compiler/llvm add llvm lld isa/generated/codecs
git -C compiler/llvm diff --cached --check
git -C compiler/llvm commit -m "linxisa: align compiler with PTO ISA 0.58.1"
git -C compiler/llvm push -u origin codex/v0581-release
```

Merge only after hosted checks, then fetch and record the exact merged
`origin/main` SHA. Do not create or move a release tag during this task.

### Task 2: Correct PTOAS and PTO bytecode against the 0.58.1 authority

**Files:**
- Create: `compiler/ptoas/tools/pto_isa_v0_58_1_lock.json`
- Create: `compiler/ptoas/tools/pto_isa_v0_58_1_operation_contracts.json`
- Modify: `compiler/ptoas/tools/check_v058_pto_manifest.py`
- Modify: `compiler/ptoas/include/PTO/IR/PTOOps.td`
- Modify: `compiler/ptoas/lib/PTO/IR/PTO.cpp`
- Modify: `compiler/ptoas/lib/PTO/Transforms/PTOToEmitC.cpp`
- Modify: `compiler/ptoas/tools/ptobc/generated/ptobc_opcodes_v0.h`
- Modify: `compiler/ptoas/tools/ptobc/tests/opcode_coverage_check.py`
- Modify: `compiler/ptoas/tools/ptobc/MAINTENANCE.md`
- Modify: `compiler/ptoas/.github/workflows/ci.yml`
- Modify: `compiler/ptoas/.github/workflows/build_wheel.yml`
- Modify: `compiler/ptoas/.github/workflows/build_wheel_mac.yml`
- Modify: `compiler/ptoas/.github/scripts/update_pto_isa_pin.py`
- Modify: `compiler/ptoas/.github/workflows/update_pto_isa_pin.yml`
- Modify: `compiler/ptoas/docker/Dockerfile`
- Modify: `compiler/ptoas/README.md`
- Modify: `compiler/ptoas/tools/ptoas/ptoas.cpp`
- Test: `compiler/ptoas/test/lit/pto/v0581_linx_contract.pto`
- Test: `compiler/ptoas/test/lit/pto/v058_deleted_ops_rejected.pto`
- Test: `compiler/ptoas/test/lit/pto/v058_linx_target.pto`
- Test: `compiler/ptoas/test/lit/pto/v057_tileop_emitc.pto`
- Test: `compiler/ptoas/test/lit/pto/tprefetch_emitc.pto`
- Test: `compiler/ptoas/tools/ptobc/tests/ptobc_v0581_contract_encode.sh`

**Interfaces:**
- Consumes: exact root lock/catalogs and the canonical merged LLVM SHA from Task 1.
- Produces: canonical PTOAS merged SHA, exact operation contracts, bytecode arity coverage, and a checker that rejects cross-root identity drift.

- [ ] **Step 1: Preserve the reviewed release work and branch from its tip**

```bash
git -C compiler/ptoas fetch origin --tags
git -C compiler/ptoas switch codex/v058-release
git -C compiler/ptoas switch -c codex/v0581-release
```

- [ ] **Step 2: Add red identity and operation-contract tests**

The cross-root test must compare release, ABI, projection hash, source commit
and tree, content hash, release-manifest hash, hardware/numeric hashes, and all
four catalog hashes/counts. Add literal operation tests for these arities:

```text
TROWEXPAND 2
TCOLEXPAND 2
TCONCAT 3
TIMG2COL 4
TINSERT 5
TPREFETCH 5
```

and engines `TDIV`, `TDIVS`, `TREM`, `TREMS` = `SFU`.

- [ ] **Step 3: Run the checker against root and observe the real red state**

```bash
python3 compiler/ptoas/tools/check_v058_pto_manifest.py \
  --ptoas-root compiler/ptoas --linx-root .
```

Expected: nonzero with the 0.58.0 identity and the known operation role/arity
differences; the test must not false-pass by checking only profile/count.

- [ ] **Step 4: Regenerate the lock/contracts and implement hard-break IR/lowering changes**

Make TINSERT emit exact `dst,dst,insertion,row,col`; expose `posM,posK` for
TIMG2COL; expose `base,row-stride,valid-cols,valid-rows,physical-cols` for
TPREFETCH. Do not add legacy compatibility fallbacks.

- [ ] **Step 5: Make PTO bytecode regeneration reproducible**

Either add a deterministic generator invoked by the maintenance document or
record and test the exact audited schema transformation. Preserve historical
`NEW_V0580_OPCODE_ASSIGNMENTS` and `v0580_ops_v0_encode.sh`; add the separate
0.58.1 arity round trip.

- [ ] **Step 6: Bind all release automation to the canonical LLVM and explicit reviewed dependencies**

Replace the old LLVM SHA with Task 1's merged SHA. Treat
`linxisa-v0.58.1` as an ISA release tag that runs the exact manifest checker,
not as PTOAS product version `0.41`. Remove weekly implicit-HEAD behavior or
require one explicit reviewed implementation-header SHA shared by CI and
Docker. Keep PTO-SPEC commit `c381465b...` distinct from the GitCode
implementation dependency.

- [ ] **Step 7: Build and run all focused PTOAS/PTO-BC gates**

```bash
cmake --build compiler/ptoas/build
ninja -C compiler/ptoas/build check-pto
python3 compiler/ptoas/tools/check_v058_pto_manifest.py \
  --ptoas-root compiler/ptoas --linx-root .
python3 compiler/ptoas/tools/ptobc/tests/opcode_coverage_check.py \
  compiler/ptoas/include/PTO/IR/PTOOps.td \
  compiler/ptoas/tools/ptobc/generated/ptobc_opcodes_v0.h
ctest --test-dir compiler/ptoas/build --output-on-failure -R \
  'pto_isa_v0581_contract_check|ptobc_v0580_ops_v0_encode|ptobc_v0581_contract_encode|ptobc_tpartarg_v0_encode'
```

- [ ] **Step 8: Commit, push, merge, and record canonical PTOAS SHA**

```bash
git -C compiler/ptoas add -A
git -C compiler/ptoas diff --cached --check
git -C compiler/ptoas commit -m "release: align PTOAS with PTO ISA 0.58.1"
git -C compiler/ptoas push -u origin codex/v0581-release
```

Merge the full preserved release series plus corrective commits to canonical
`main` only after hosted checks.

### Task 3: Upgrade Linux, glibc, and musl fail-closed identities

**Files:**
- Modify: `kernel/linux/fs/binfmt_elf.c`
- Modify: `kernel/linux/fs/tests/binfmt_elf_kunit.c`
- Modify: `kernel/linux/Documentation/linxisa/abi.md`
- Modify: `lib/glibc/sysdeps/linx/dl-prop.h`
- Modify: `lib/glibc/tools/linx/check_pto_isa_identity.py`
- Modify: `lib/musl/ldso/dynlink.c`
- Modify: `lib/musl/tools/linx/check_pto_isa_identity.py`
- Modify: `lib/musl/tools/linx/pto_isa_identity_harness.c`

**Interfaces:**
- Consumes: exact note emitted by Task 1 and root release lock.
- Produces: merged Linux/glibc/musl SHAs that accept only exact 0.58.1 main/interpreter/dependency/dlopen closure.

- [ ] **Step 1: Create clean topics from canonical branches**

```bash
git -C kernel/linux fetch origin --tags && git -C kernel/linux switch -c codex/v0581-release origin/main
git -C lib/glibc fetch origin --tags && git -C lib/glibc switch -c codex/v0581-release origin/master
git -C lib/musl fetch origin --tags && git -C lib/musl switch -c codex/v0581-release origin/master
```

- [ ] **Step 2: Make the old-patch negatives red before replacing accepted identity**

In Linux, search active `0.58.1` and mutate the last digit to `0`; make the
conflicting descriptor explicitly `0.58.0` rather than mutating `.1` to `.1`.
Apply the same literal old-`0.58.0` negative to glibc and musl. Preserve
missing, malformed, oversized, trailing-NUL, duplicate-identical, and
duplicate-conflicting cases.

- [ ] **Step 3: Run leaf guards and observe failure against stale production constants**

```bash
python3 lib/glibc/tools/linx/check_pto_isa_identity.py
python3 lib/musl/tools/linx/check_pto_isa_identity.py
```

Expected: the new 0.58.1 expectations fail until loaders/constants change.

- [ ] **Step 4: Replace accepted descriptors with the exact canonical JSON**

```json
{"encoding_abi":"pto-isa-0.58.1-mode-function-v1","encoding_projection_sha256":"89b872d6eaf0252200bc9349d49b9346e2a69d894cdcc2dcd0fd71911c1e0b8c","release":"0.58.1"}
```

Keep compact sorted JSON, no descriptor NUL, owner `PTO\0`, type `1`, and
four-byte alignment.

- [ ] **Step 5: Run Linux compile and clean-vmlinux gates with Task 1 LLVM**

```bash
bash tools/bringup/run_linux_vmlinux_build_clean.sh --fresh --target vmlinux
```

Also build `fs/binfmt_elf.o` with `CONFIG_KUNIT=y` and
`CONFIG_BINFMT_ELF_KUNIT_TEST=y`, then verify the recorded compiler and kernel
provenance name the exact Task 1 LLVM and current Linux topic SHA.

- [ ] **Step 6: Build and run libc leaf/runtime gates**

```bash
bash lib/glibc/tools/linx/build_linx64_glibc.sh
bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh
python3 avs/qemu/run_glibc_smoke.py --qemu emulator/qemu/build/qemu-system-linx64 --timeout 30
MODE=phase-b bash lib/musl/tools/linx/build_linx64_musl.sh
QEMU=emulator/qemu/build/qemu-system-linx64 \
  python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --sample all
```

- [ ] **Step 7: Commit and merge each leaf through its canonical branch**

Use one commit series per repository, push named topics, obtain required
checks, and record the canonical merged SHAs. Do not tag or repin before those
merges exist.

### Task 4: Bring QEMU decode, DATR legality, ELF identity, and AVS coverage to 0.58.1

**Files:**
- Modify: `emulator/qemu/target/linx/tile_isa_058.h`
- Modify: `emulator/qemu/target/linx/insn16.decode`
- Modify: `emulator/qemu/target/linx/insn32.decode`
- Modify: `emulator/qemu/target/linx/insn48.decode`
- Modify: `emulator/qemu/target/linx/insn64.decode`
- Modify: `emulator/qemu/target/linx/linx_opcode_ids_gen.h`
- Modify: `emulator/qemu/target/linx/linx_opcode_meta_gen.h`
- Modify: `emulator/qemu/target/linx/translate.c`
- Modify: `emulator/qemu/target/linx/helper.c`
- Modify: `emulator/qemu/target/linx/tile_numeric_058.h`
- Modify: `emulator/qemu/target/linx/tile_cube_058.c`
- Modify: `emulator/qemu/target/linx/tile_cube_058.h`
- Modify: `emulator/qemu/target/linx/cpu.c`
- Modify: `emulator/qemu/target/linx/cpu.h`
- Modify: `emulator/qemu/hw/linx/virt.c`
- Modify: `emulator/qemu/tests/linxisa/test_v058_decode_metadata.py`
- Modify: `emulator/qemu/tests/linxisa/test_v058_pto_contract.py`
- Modify: `emulator/qemu/tests/linxisa/test_v058_review_contract.py`
- Modify: `emulator/qemu/tests/linxisa/test_v058_tile_raw_contract.py`
- Modify: `emulator/qemu/tests/linxisa/test_v058_tile_execution_coverage.py`
- Modify: `emulator/qemu/tests/linxisa/test_v058_tile_numeric_layout_contract.py`
- Modify: `emulator/qemu/tests/linxisa/test_v058_hardware_numeric_vectors.py`
- Modify: `emulator/qemu/tests/linxisa/fused_call_contract.s`
- Modify: `emulator/qemu/tests/unit/test-linx-tile-cube-numeric.c`
- Modify: `emulator/qemu/tests/unit/test-linx-tile-transaction.c`
- Modify: `emulator/qemu/tests/unit/test-linx-tile-state-dump.c`
- Modify: `emulator/qemu/tests/unit/meson.build`
- Modify: `tools/bringup/report_qemu_isa_coverage.py`
- Modify: `tools/bringup/check_tepl_encoding.py`
- Create: `tools/bringup/check_qemu_pto_v0581_contract.py`
- Create: `tools/bringup/test_check_qemu_pto_v0581_contract.py`
- Modify: `avs/qemu/run_tests.py`
- Modify: `avs/qemu/run_tests.sh`
- Modify: `avs/qemu/main.c`
- Modify: `avs/qemu/test_run_tests.py`
- Modify: `avs/qemu/README.md`
- Modify: `avs/qemu/run_callret_contract.py`
- Modify: `avs/qemu/refresh_qemu_executable_coverage.py`
- Modify: `avs/qemu/qemu_executable_coverage_manifest.json`
- Modify: AVS strict/runtime ELF identity fixtures and tests
- Regenerate: `docs/bringup/gates/qemu_isa_coverage_latest.json`
- Regenerate: `docs/bringup/gates/qemu_isa_coverage_latest.md`

**Interfaces:**
- Consumes: root 731-mnemonic/765-form catalog, Task 1 note bytes, and Task 2 operation contracts.
- Produces: canonical QEMU SHA with exact decode/execute/DATR and fail-closed ELF-note behavior plus fresh AVS evidence.

- [ ] **Step 1: Create a clean QEMU topic from canonical branch**

```bash
git -C emulator/qemu fetch origin --tags
git -C emulator/qemu switch -c codex/v0581-release origin/master
```

- [ ] **Step 2: Add red coverage, DATR, and ELF identity cases**

Require `B.FPATR`, `BSTART.CALL`, `BSTART.ICALL`, and `L.BSTOP`, all 765 exact
forms, TDIV/TDIVS/TREM/TREMS in SFU, engine counts 31 VEC/56 SFU/10 TLSU/12
CUBE, and canonical DATR masks from `isa/v0.58/state/engine_ops.json`.
Add accepted 0.58.1 plus missing, old-0.58.0, malformed, trailing-NUL,
duplicate-conflicting, and mixed-note rejection ELF cases.

- [ ] **Step 3: Run the full coverage report and prove the pinned source is red**

```bash
python3 tools/bringup/report_qemu_isa_coverage.py \
  --spec isa/v0.58/linxisa-v0.58.json \
  --qemu-root emulator/qemu \
  --qemu-meta emulator/qemu/target/linx/linx_opcode_meta_gen.h \
  --report-out /tmp/qemu-isa-coverage-red.json \
  --out-md /tmp/qemu-isa-coverage-red.md --require-full
```

Expected: current source reports 727/731 mnemonics and 749/765 forms before
the repair; the test must not consume the stale 728/766 checked-in report.

- [ ] **Step 4: Implement canonical decode/semantics/DATR and ELF note validation**

Derive legality tables from the root state instead of retaining a second
handwritten 0.58.0 catalog. Validate the canonical note in every Linx custom
ELF loader in `hw/linx/virt.c` before execution. Reuse the same compact JSON
and duplicate/conflict policy as Linux; do not accept a missing note.

- [ ] **Step 5: Build QEMU and run targeted plus full AVS gates**

```bash
bash tools/bringup/run_qemu_build_clean.sh \
  --qemu-root "$PWD/emulator/qemu" \
  --out-dir /tmp/linx-qemu-clean-build --target qemu-system-linx64
meson test -C /tmp/linx-qemu-clean-build \
  test-linx-tile-transaction test-linx-tile-cube-numeric test-linx-tile-state-dump
python3 tools/bringup/report_qemu_isa_coverage.py \
  --spec isa/v0.58/linxisa-v0.58.json \
  --qemu-root emulator/qemu \
  --qemu-meta emulator/qemu/target/linx/linx_opcode_meta_gen.h \
  --report-out docs/bringup/gates/qemu_isa_coverage_latest.json \
  --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s emulator/qemu/tests/linxisa -p 'test_v058_*.py' -v
python3 -m unittest discover -s avs/qemu -p 'test_*.py' -v
QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 \
  bash avs/qemu/check_system_strict.sh
(cd avs/qemu && QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 \
  ./run_tests.sh --all --timeout 10)
```

Run the repository-native QEMU Linx test suite and confirm all identity
negative ELFs fail before guest entry.

- [ ] **Step 6: Commit, push, merge, and record canonical QEMU SHA**

```bash
git -C emulator/qemu add -A
git -C emulator/qemu diff --cached --check
git -C emulator/qemu commit -m "linxisa: implement the PTO ISA 0.58.1 runtime contract"
git -C emulator/qemu push -u origin codex/v0581-release
```

### Task 5: Upgrade tools/model and extend exact-ELF cross-model provenance

**Files:**
- Modify: `tools/model/CMakeLists.txt`
- Modify: `tools/model/tools/isa/gen_minst_codec.py`
- Regenerate: `tools/model/include/linx/model/isa/generated_tables.hpp`
- Regenerate: `tools/model/src/isa/generated_tables.cpp`
- Modify: `tools/model/tests/fixtures/pto_v058_shared_state.json`
- Modify: `tools/model/tests/checks/check_pto_v058_shared_fixture.py`
- Modify: `tools/model/README.md`
- Modify: `tools/model/docs/isa.md`
- Modify: `tools/model/docs/architecture.md`
- Modify: `tools/bringup/run_model_diff_suite.py`
- Modify: `tools/bringup/run_ai_workload_flow.py`
- Test: `tools/bringup/test_run_ai_workload_flow.py`

**Interfaces:**
- Consumes: root 765-form catalog and exact Task 1 compiler/QEMU binaries.
- Produces: regenerated model codec, merged model SHA, and immutable ELF/tool hashes checked before every consumer.

- [ ] **Step 1: Add red generation-identity and mutation tests**

Require generator input release `0.58.1`, new forms `B.FPATR` mask `0x7fff`
match `0x2023` and `BSTART.ICALL` mask `0xf83fffff` match `0x50166001`, and
exact counts 765 forms/2661 fields/3401 pieces/780 constraints. In AI flow,
hash the ELF after link, mutate a copied byte before the second consumer, and
assert the run stops on SHA mismatch.

- [ ] **Step 2: Run red unit/generation checks**

```bash
python3 -m unittest tools.bringup.test_run_ai_workload_flow
cmake -S tools/model -B tools/model/build -G Ninja
cmake --build tools/model/build --target gen-isa-codec
```

- [ ] **Step 3: Validate authority in the generator and regenerate committed codec**

Make generation reject a lock whose release, ABI, projection hash, source,
catalog hashes, or counts differ. Add a freshness comparison target so CI
cannot pass with stale committed outputs.

- [ ] **Step 4: Bind one immutable ELF and exact tools across model consumers**

Record SHA-256 for compiler, linker, ELF, QEMU, model binary, manifest, and
golden data before execution; re-read each before its consumer starts and
after the flow. Require result memory, independent golden comparison, and
pairwise comparisons in release-strict mode; a trace-prefix fallback is not
promotion evidence.

- [ ] **Step 5: Build and run model plus differential gates**

```bash
cmake --build tools/model/build
ctest --test-dir tools/model/build --output-on-failure
python3 tools/bringup/run_model_diff_suite.py \
  --root . --suite avs/model/linx_model_diff_suite.yaml \
  --profile release-strict --trace-schema-version 1.0 \
  --report-out /tmp/linx-model-diff-v0581.json
```

- [ ] **Step 6: Commit and merge canonical model changes**

Push a topic from model `origin/main`, merge it normally, and record the
canonical merged SHA. Do not move or reuse the existing stale
`linxisa-v0.58.1` tag.

### Task 6: Upgrade the review-only LinxCoreModel projection

**Files:**
- Modify: `tools/LinxCoreModel/README.md`
- Modify: `tools/LinxCoreModel/isa/README.md`
- Modify: `tools/LinxCoreModel/tests/fixtures/pto_v058_shared_state.json`
- Modify/regenerate: `tools/LinxCoreModel/isa/codec/decodefiles/block32.decode`
- Regenerate: `tools/LinxCoreModel/isa/codec/generatedfiles/decode-inst*.cpp`
- Regenerate: `tools/LinxCoreModel/isa/codec/generatedfiles/encode-inst*.cpp`
- Test: `tools/LinxCoreModel/tests/minst_test/main.cpp`

**Interfaces:**
- Consumes: exact root catalog, Task 5 provenance contract, and Task 4 QEMU.
- Produces: one exact remotely reachable review-only LinxCoreModel PR head.

- [ ] **Step 1: Add red exact-form and fixture tests**

Use literal encodings `0x00002023` for `B.FPATR` and `0x50166001` for
`BSTART.ICALL`; reject retired `0x00006001` where the current catalog does.
Require fixture release `0.58.1` and exact lock hashes.

- [ ] **Step 2: Run the focused model test and observe missing form failures**

```bash
python3 tools/LinxCoreModel/build.py all --tests -O O3 --no-debug -j8
ctest --test-dir tools/LinxCoreModel/build --output-on-failure -R minst
```

- [ ] **Step 3: Update and regenerate the handwritten codec**

```bash
(cd tools/LinxCoreModel && sh isa/codec/build.sh)
```

Update opcode registration and semantic carriers only where the new forms
require it; do not infer encodings from archived profiles.

- [ ] **Step 4: Run the full LinxCoreModel gates and exact-ELF smoke**

```bash
python3 tools/LinxCoreModel/build.py all --tests -O O3 --no-debug -j8
ctest --test-dir tools/LinxCoreModel/build --output-on-failure
tools/LinxCoreModel/bin/gfsim -f /tmp/linx-v0581-cross-model.elf
```

- [ ] **Step 5: Push a new review-only PR head and record it**

Do not merge or tag LinxCoreModel. Preserve
`integration_status: review_only_open_pr` and record the exact remotely
reachable head and PR URL in the root component lock.

### Task 7: Upgrade pyCircuit decode and release-path validation

**Files:**
- Modify: `tools/pyCircuit/contrib/linx/flows/tools/check_pto_isa_v058_decode.py`
- Modify: `tools/pyCircuit/contrib/linx/designs/examples/linx_cpu_pyc/isa.py`
- Modify: `tools/pyCircuit/contrib/linx/designs/examples/linx_cpu_pyc/decode.py`
- Modify: `tools/pyCircuit/contrib/linx/designs/examples/linxcore_inorder/isa.py`
- Modify: `tools/pyCircuit/contrib/linx/designs/examples/linxcore_inorder/decode.py`
- Test: `tools/pyCircuit/tests/unit/test_linx_pto_decode_contract.py`

**Interfaces:**
- Consumes: exact root lock/catalog, Task 4 QEMU, and Task 5 immutable ELF hash.
- Produces: canonical merged pyCircuit SHA with no retired ICALL decode or fallback promotion path.

- [ ] **Step 1: Add red authority and exact-form tests**

Make the checker open the actual root lock/catalog and require release
`0.58.1`, `B.FPATR` `0x00002023`, `BSTART.ICALL` `0x50166001`, and rejection
of the retired `0x00006001` surface in both example decoders.

- [ ] **Step 2: Run focused red checks**

```bash
python3 tools/pyCircuit/contrib/linx/flows/tools/check_pto_isa_v058_decode.py
pytest -q tools/pyCircuit/tests/unit/test_linx_pto_decode_contract.py
```

- [ ] **Step 3: Repair both decoder copies from the canonical catalog**

Keep opcode IDs and stage behavior consistent across `linx_cpu_pyc` and
`linxcore_inorder`; remove old STD ICALL forms rather than accepting aliases.

- [ ] **Step 4: Run release-path gates without fallback**

```bash
pytest tools/pyCircuit/tests/unit -m unit
mkdocs build --config-file tools/pyCircuit/mkdocs.yml --strict
bash tools/pyCircuit/flows/scripts/run_examples.sh
PYC_GATE_RUN_ID=v0581 bash tools/pyCircuit/flows/scripts/run_semantic_regressions_v40.sh
bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh
bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh
```

Require the primary pyC path and full selected trace; reject the short-prefix
fallback as release evidence.

- [ ] **Step 5: Commit, push, merge to canonical `main`, and record the SHA**

### Task 8: Regenerate LinxCore catalogs and functional decode for 0.58.1

**Files:**
- Modify: `rtl/LinxCore/tools/generate/opcode_catalog_lib.py`
- Modify: `rtl/LinxCore/tools/generate/update_generated_linxcore.sh`
- Regenerate: `rtl/LinxCore/src/common/opcode_catalog.yaml`
- Regenerate: `rtl/LinxCore/src/common/opcode_ids_gen.py`
- Regenerate: `rtl/LinxCore/src/common/opcode_meta_gen.py`
- Regenerate: `rtl/LinxCore/chisel/src/main/scala/linxcore/backend/OooOpcodeRecipeTable.scala`
- Regenerate: `rtl/LinxCore/chisel/src/main/scala/linxcore/frontend/FrontendOpcodeDecodeTable.scala`
- Modify: `rtl/LinxCore/src/common/decode.py`
- Modify: `rtl/LinxCore/tests/test_opcode_catalog_forms.py`
- Modify: `rtl/LinxCore/tests/test_ooo_opcode_recipes.sh`

**Interfaces:**
- Consumes: exact root catalog and the canonical Task 7 pyCircuit SHA.
- Produces: canonical merged LinxCore SHA whose generated external records all say source release `0.58.1`.

- [ ] **Step 1: Add red catalog identity and functional decode tests**

Use literal encodings `0x00002023` for `B.FPATR` and `0x50166001` for
`BSTART.ICALL`; reject retired `0x00006001` where the current catalog does.
Reject any external catalog record whose `source_profile` is not `0.58.1` or
whose source lock/hash tuple differs.

- [ ] **Step 2: Run focused red checks**

```bash
python3 rtl/LinxCore/tests/test_opcode_catalog_forms.py
bash rtl/LinxCore/tests/test_ooo_opcode_recipes.sh
```

- [ ] **Step 3: Regenerate LinxCore from root authority and include frontend table generation**

```bash
LINXISA_ROOT="$PWD" LINXCORE_PYC_ROOT="$PWD/tools/pyCircuit" \
  bash rtl/LinxCore/tools/generate/update_generated_linxcore.sh
python3 rtl/LinxCore/tools/chisel/gen_frontend_decode_table.py
```

Wire the frontend generator into `update_generated_linxcore.sh` so one command
closes all committed outputs. Assert all non-internal records have
`source_profile: 0.58.1` and source release `0.58.1`.

- [ ] **Step 4: Run LinxCore focused and mandatory gates**

```bash
bash rtl/LinxCore/tests/test_opcode_parity.sh
bash rtl/LinxCore/tests/test_ooo_opcode_recipes.sh
```

Then run FrontendDecodeStageSpec, InterfaceBundlesSpec, stage connectivity,
runner protocol, cosim smoke, trace schema/memory, ROB bookkeeping, and the
block-structure pyCircuit flow named by the LinxCore skill.

- [ ] **Step 5: Commit, push, merge to canonical `main`, and record the SHA**

### Task 9: Reconcile the TileOP API canonical branch with the known-good 0.58.1 contract

**Files:**
- Modify: `tools/Linx-TileOP-API/README.md`
- Modify: `tools/Linx-TileOP-API/contracts/README.md`
- Modify: `tools/Linx-TileOP-API/contracts/linxisa-v0.58-engine-ops.json`
- Modify: `tools/Linx-TileOP-API/docs/tileop-usage/engines.md`
- Modify: `tools/Linx-TileOP-API/include/jcore/template_asm.hpp`
- Modify: `tools/Linx-TileOP-API/test/test_v058_engine_contract.py`
- Modify: `tools/Linx-TileOP-API/tools/generate_engine_docs.py`
- Modify: `tools/Linx-TileOP-API/tools/sync_linxisa_v058_contract.py`
- Modify: `tools/Linx-TileOP-API/test/run_negatives.sh`
- Modify: `tools/Linx-TileOP-API/test/verify_postprocess.sh`

**Interfaces:**
- Consumes: known-good pin `8f021d53...`, root engine catalog, and Task 1 compiler.
- Produces: repaired canonical `linx` merged SHA; never raw current `21a93e6...`.

- [ ] **Step 1: Create topic from live canonical `origin/linx` and capture known-good eight-file delta**

```bash
git -C tools/Linx-TileOP-API fetch origin --tags
git -C tools/Linx-TileOP-API switch -c codex/v0581-reconcile origin/linx
git -C tools/Linx-TileOP-API diff --binary 21a93e6c1f5bd2b67d8c1e1215d028d3556d0dd8..8f021d53d6b33ccff6babab6b80693c4fa9f6aa1 -- \
  README.md contracts docs include test tools > /tmp/tileop-v0581-reference.patch
```

- [ ] **Step 2: Add red assertions for current contract and retired surfaces**

Assert source commit/tree, catalog SHA, counts
`CUBE=12,SFU=56,TLSU=10,VEC=31`, SFU division/remainder, no raw
`BSTART.TEPL`, and no legacy `=Tr`/TMA spellings.

- [ ] **Step 3: Run `make check` and preserve the nine-failure red evidence**

```bash
make -C tools/Linx-TileOP-API check
```

- [ ] **Step 4: Semantic-port the known-good contract while preserving only verified newer additions**

Do not merge the divergent backup history. Regenerate the contract/docs from
root authority and update private/default tool scripts to require explicit
Task 1 tool paths and current targets.

- [ ] **Step 5: Run leaf compile/disassembly gates fail-fast**

```bash
make -C tools/Linx-TileOP-API check
PLAT=linx COMPILER_DIR="$PWD/compiler/llvm/build-linxisa-clang/bin" \
  bash -e tools/Linx-TileOP-API/test/tileop_api/compile.all
```

Run updated negative and postprocess gates directly; do not use
`test/run_ci.py` as sole proof because it ignores child exit status.

- [ ] **Step 6: Commit, push, merge into canonical `linx`, and record merged SHA**

### Task 10: Merge PTO kernels, verify nested SuperNPU, and archive the standalone checkout

**Files:**
- Merge existing PTO-kernels PR #11 commits into canonical repository.
- Verify: `workloads/pto_kernels/benchmarks/supernpu/SOURCE.lock.json`
- Verify: `workloads/pto_kernels/scripts/check_supernpu_v058.py`
- Verify: `workloads/pto_kernels/tests/test_supernpu_makefile_contract.py`
- Create outside repository: checksummed standalone recovery bundle and audit record.

**Interfaces:**
- Consumes: Task 1 LLVM, Task 3 sysroot, Task 4 QEMU, and Task 9 TileOP API.
- Produces: canonical PTO-kernels merged SHA, executable nested workload evidence, and no loose standalone checkout in the root workspace.

- [ ] **Step 1: Re-resolve canonical PR #11 and make it reviewable**

```bash
gh pr view 11 --repo PTO-ISA/pto-kernels --json state,isDraft,mergeable,headRefOid,baseRefOid,statusCheckRollup
```

Require head `2d87f790...`, base `15fa021e...`, clean mergeability, and all
required checks successful. Mark ready for review and merge normally; use the
actual canonical merged SHA, never topic head or the legacy `origin` fork.

- [ ] **Step 2: Run canonical leaf gates after merge**

```bash
make -C workloads/pto_kernels check
black --check workloads/pto_kernels
prospector workloads/pto_kernels
python3 workloads/pto_kernels/scripts/check_supernpu_v058.py
```

- [ ] **Step 3: Produce real compile/disassembly evidence with exact tools**

```bash
make -C workloads/pto_kernels/benchmarks/supernpu/microbenchmark/vector \
  TESTCASE=tadd_fp32_16x16 \
  COMPILER_DIR="$PWD/compiler/llvm/build-linxisa-clang/bin" \
  LINX_TILEOP_API_ROOT="$PWD/tools/Linx-TileOP-API" \
  LINX_SYSROOT="$PWD/lib/musl/build/sysroot" diss
```

Repeat the one-level and baremetal variants specified by
`test_supernpu_makefile_contract.py`, including
`LINX_BAREMETAL_HEAP_SIZE=0x10000000`.

- [ ] **Step 4: Capture and bundle the standalone checkout before removal**

```bash
git -C workloads/SuperNPUBench status --porcelain=v2 --branch
git -C workloads/SuperNPUBench show-ref
git -C workloads/SuperNPUBench worktree list --porcelain
git -C workloads/SuperNPUBench fsck --full --no-reflogs --unreachable
git -C workloads/SuperNPUBench update-ref \
  refs/archive/unreachable-v057-manual-5d08484b \
  5d08484b
git -C workloads/SuperNPUBench bundle create \
  /Users/zhoubot/.codex/archives/SuperNPUBench-standalone-20260816.bundle --all
git bundle verify /Users/zhoubot/.codex/archives/SuperNPUBench-standalone-20260816.bundle
git bundle list-heads /Users/zhoubot/.codex/archives/SuperNPUBench-standalone-20260816.bundle \
  refs/archive/unreachable-v057-manual-5d08484b
shasum -a 256 /Users/zhoubot/.codex/archives/SuperNPUBench-standalone-20260816.bundle
```

Create local archival ref
`refs/archive/unreachable-v057-manual-5d08484b` at `5d08484b` before bundling
so the bundle preserves the exact object, then verify that ref is listed by
`git bundle list-heads`. Do not delete upstream `main` or the repository.

- [ ] **Step 5: Remove only the verified loose checkout and prove the postcondition**

```bash
test ! -e workloads/SuperNPUBench
git status --porcelain --untracked-files=all
```

Use a recoverable local move to the verified archive location before final
removal; do not run a broad recursive delete against the workspace.

### Task 11: Port unique root branches, publish Chinese Pages, and update documentation

**Files:**
- Create: `docs/isa/header/B.IOS.md`
- Create: `docs/zh/isa/header/B.IOS.md`
- Modify: `docs/isa/instset/baseInstrs.md`
- Modify: `docs/zh/isa/instset/baseInstrs.md`
- Modify: `mkdocs.yml`
- Modify: `mkdocs.zh.yml`
- Create: `tools/isa/test_b_ios_documentation.py`
- Modify: `.github/workflows/ci.yml`
- Modify: `.github/workflows/pages.yml`
- Create: `tools/docs/test_pages_publish_contract.py`
- Create: `tools/docs/update_language_map.py`
- Create: `tools/docs/test_update_language_map.py`
- Modify: `tools/docs/update_translation_manifest.py`
- Modify: `docs/check_documentation.py`
- Regenerate: `docs/zh/translation-manifest.json`
- Regenerate: `docs/zh/assets/lang-map.json`
- Modify: `docs/index.md`
- Modify: `docs/zh/index.md`
- Modify: `docs/releases/v0.58.1.md`
- Modify: `docs/zh/releases/v0.58.1.md`

**Interfaces:**
- Consumes: B.IOS branch commit `5de637df...` and Dependabot commits `395e035b...`/`55defee9...`.
- Produces: bilingual B.IOS docs, strict Chinese Pages artifact, correct catalog facts, generated translation state, and GitHub Actions v7 workflows.

- [ ] **Step 1: Add red B.IOS and Pages contract tests**

The B.IOS test binds ID `b_ios_32_11ff57a2e635`, PTO source form
`b_ios_32_4ba5ef98fdaa`, mask `0xf00871ff`, match `0x00001013`, SharedTID 8
bits, PE mask 4 bits, S0..S255, zero-mask no-op, atomic descriptor/payload RMW,
and TSize 128 B through 8 KiB. The Pages test requires English strict-build to
an independent temp path and Chinese strict-build to uploaded `site/`.

- [ ] **Step 2: Run the new tests and observe missing-page/wrong-Pages failures**

```bash
python3 tools/isa/test_b_ios_documentation.py
python3 tools/docs/test_pages_publish_contract.py
```

- [ ] **Step 3: Semantic-port B.IOS, upgrade Actions, and make Pages Chinese**

Use `actions/checkout@v7` and `actions/setup-python@v7` for all twelve current
uses. Pages must execute:

```bash
python3 docs/check_documentation.py --root .
mkdocs build --strict --site-dir "${RUNNER_TEMP}/site-en"
mkdocs build --strict --config-file mkdocs.zh.yml --site-dir site
```

and upload only `site/` through `actions/upload-pages-artifact@v5`.

- [ ] **Step 4: Add deterministic language-map generation test-first**

Build symmetric pairs from mirrored Markdown, excluding `archive/**` and
`architecture/isa-manual/{.bundle,build,vendor}/**`. Make
`docs/check_documentation.py` invoke `update_language_map.py --check`.

- [ ] **Step 5: Regenerate docs and correct current facts**

```bash
python3 docs/isa/gen_isa_pages.py
python3 tools/docs/update_language_map.py
python3 tools/docs/update_translation_manifest.py
```

Set root index counts to `765` forms and `54` groups. Change the English and
Chinese release pages from the false “signed annotated” claim to “immutable
release tag”; do not alter the lightweight tag.

- [ ] **Step 6: Run strict bilingual and artifact smoke tests**

```bash
python3 tools/isa/test_b_ios_documentation.py
python3 tools/docs/test_update_language_map.py
python3 tools/docs/update_language_map.py --check
python3 tools/docs/update_translation_manifest.py --check
python3 docs/check_documentation.py --root .
mkdocs build --strict --site-dir /tmp/linx-site-en
mkdocs build --strict --config-file mkdocs.zh.yml --site-dir /tmp/linx-site-zh
test -f /tmp/linx-site-zh/isa/header/B.IOS/index.html
rg -q '灵犀指令集架构|非规范翻译' /tmp/linx-site-zh/index.html
! rg -q 'Welcome to LinxISA' /tmp/linx-site-zh/index.html
```

### Task 12: Archive legacy designs and add fail-closed branch cleanup evidence

**Files:**
- Move: `docs/superpowers/specs/2026-08-11-v058-component-release-train-design.md` to `docs/archive/v0.58/release/2026-08-11-v058-component-release-train-design.md`
- Move: `docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md` to `docs/archive/v0.58/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`
- Move: `docs/zh/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md` to `docs/zh/archive/v0.58/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`
- Create: `docs/archive/v0.58/README.md`
- Create: `docs/zh/archive/v0.58/README.md`
- Modify: `docs/bringup/README.md`
- Modify: `docs/zh/bringup/README.md`
- Create: `docs/bringup/branch_cleanup_manifest.json`
- Create: `tools/bringup/check_branch_cleanup_manifest.py`
- Create: `tools/bringup/test_branch_cleanup_manifest.py`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: exact reviewed root ref table and Task 11 doc generators.
- Produces: versioned non-normative archives and a read-only exact-OID cleanup checker with static/pre-delete/post-delete modes.

- [ ] **Step 1: Write red archive-reference and cleanup-manifest tests**

Test required manifest fields: repository, scope, ref, exact OID, action,
classification, evidence/replacement OID, required integration commit,
attached-worktree prohibition, and pre/post states. Simulate a moved delete
OID, missing retained tag, and attached delete worktree; each must fail.

- [ ] **Step 2: Run tests and observe missing checker/archive failures**

```bash
python3 tools/bringup/test_branch_cleanup_manifest.py
```

- [ ] **Step 3: Move legacy documents with archive markers and update active references**

English marker is exactly `Archive status: historical and non-normative.`;
Chinese marker is exactly `归档状态：历史资料，非规范。`. Do not move
`docs/bringup/agent_runs/checklists/*.md` or active architecture research.

- [ ] **Step 4: Implement the read-only cleanup checker**

Use `git ls-remote --heads`, `git show-ref`, `git worktree list --porcelain`,
ancestry, patch/tree equivalence, and exact replacement integration checks.
The checker never executes branch deletion.

Populate and validate these reviewed root refs at their full live OIDs before
cleanup:

```text
delete local  codex/v058-b-datr-doc-fix                  3913d7cc09cf9fb1392338a69460e1894f50949c
delete local  codex/v058-bior-resolution-sync            23745cc8556b5ae3c056ef924c5001a1fcda9142
delete local  codex/linx-l-bstop-v058                    5de637dfea660a308330aa85322c7e8dc13e5925
delete remote codex/fishtoucher-software-loop            8b6f21bf8151500c8d693fc80168bab3734355fc
delete remote codex/refresh-translation-freshness        3fc63e5fc1d1913b7c4754944df983d7bd8416c5
delete remote feat/v0.57                                 41ec8d5fabdb301982742e0e2008e72dd37de38c
delete remote dependabot/github_actions/actions/checkout-7     395e035bf27bc6f7c478f0177ad9c468a5034e7
delete remote dependabot/github_actions/actions/setup-python-7 55defee96461f729051001bfaf1fb40a79338bc4
retain local  codex/linx-058-final-release               24ac3aa117411a311590a5eb0327c6368416beb6
retain local  codex/linx-isa-0.57.1                      96860ff5c6af1c324683af3a626d1f7e8104a351
retain local  codex/v058-release-existing-repos          92425b747adafda3fa100b16b9e6861d4f5566c3
retain local  codex/v058-release-train                   da240037831ea7937652527be9893d949e786188
retain tag    v0.58.1                                    ea54153b3351c48df306a57189ffb587801b9197
```

- [ ] **Step 5: Regenerate translation state and run reference/layout checks**

```bash
python3 tools/docs/update_language_map.py
python3 tools/docs/update_translation_manifest.py
git grep -n -E \
  'docs/(superpowers/specs/2026-08-11-v058-component-release-train-design|bringup/SUPERPROJECT_BRINGUP_CHECKLIST)' \
  -- ':!docs/archive/**' ':!docs/zh/archive/**'
python3 docs/check_documentation.py --root .
bash tools/ci/check_repo_layout.sh
python3 tools/bringup/check_branch_cleanup_manifest.py \
  --manifest docs/bringup/branch_cleanup_manifest.json --mode static
```

Expected grep result: no active stale-path references.

### Task 13: Repin all leaves, run exact-SHA promotion gates, merge main, and clean refs

**Files:**
- Modify: all changed submodule gitlinks.
- Modify: `docs/bringup/component-lock.v0.58.json`
- Modify: release/current pin documentation and generated gate views.
- Modify: `skills/linx-skills/linx-linux/SKILL.md`
- Verify: `docs/bringup/gates/latest.json` and machine-readable reports.

**Interfaces:**
- Consumes: canonical merged SHAs from Tasks 1–10, review-only LinxCoreModel head, and root changes from Tasks 11–12.
- Produces: exact reviewed superproject main commit, full current-SHA evidence, and verified branch cleanup.

- [ ] **Step 1: Update gitlinks and component lock atomically**

Set each ordinary component entry to its canonical merged SHA and set
LinxCoreModel to the exact open PR head with its review-only status intact.
Do not change Mesa3D or linx-skills unless their verified tree or reusable
workflow content changed.

- [ ] **Step 2: Run topology, lock, authority, generated, and documentation gates**

```bash
bash tools/ci/check_repo_layout.sh
python3 tools/ci/check_component_lock.py --root .
python3 -m unittest tools.ci.test_component_lock
python3 tools/isa/check_canonical_v058.py
python3 tools/isa/check_pto_v058_manifest.py
python3 tools/isa/test_v058_profile.py
python3 tools/isa/test_golden_contract.py
python3 tools/isa/test_gen_c_codec.py
python3 tools/isa/test_gen_sail_decode.py
python3 tools/isa/test_gen_sail_status.py
python3 docs/check_documentation.py --root .
```

- [ ] **Step 3: Run compiler, QEMU, Linux/libc, model/RTL, TileOP, and workload gates**

Run the following from clean canonical merged checkouts:

```bash
compiler/llvm/build-linxisa-clang/bin/llvm-lit -sv \
  compiler/llvm/llvm/test/MC/LinxISA \
  compiler/llvm/lld/test/ELF/linxisa-pto-identity.test
ninja -C compiler/ptoas/build check-pto
python3 compiler/ptoas/tools/check_v058_pto_manifest.py \
  --ptoas-root compiler/ptoas --linx-root .
python3 lib/glibc/tools/linx/check_pto_isa_identity.py
python3 lib/musl/tools/linx/check_pto_isa_identity.py
bash tools/bringup/run_qemu_build_clean.sh \
  --qemu-root "$PWD/emulator/qemu" \
  --out-dir /tmp/linx-qemu-final --target qemu-system-linx64
QEMU=/tmp/linx-qemu-final/qemu-system-linx64 bash avs/qemu/check_system_strict.sh
(cd avs/qemu && QEMU=/tmp/linx-qemu-final/qemu-system-linx64 \
  ./run_tests.sh --all --timeout 10)
bash tools/bringup/run_linux_vmlinux_build_clean.sh --fresh --target vmlinux
ctest --test-dir tools/model/build --output-on-failure
pytest tools/pyCircuit/tests/unit -m unit
bash rtl/LinxCore/tests/test_opcode_parity.sh
bash rtl/LinxCore/tests/test_ooo_opcode_recipes.sh
make -C tools/Linx-TileOP-API check
make -C workloads/pto_kernels check
python3 workloads/pto_kernels/scripts/check_supernpu_v058.py
python3 -m unittest tools.bringup.test_run_ai_workload_flow
python3 tools/bringup/run_ai_workload_flow.py --profile smoke --list
```

Then run Linux smoke, full-boot, and busybox-rootfs profiles with the exact
current QEMU/kernel and run the AI workload smoke with explicit
clang/clang++/LLD/objcopy/objdump/QEMU paths. Any fallback or implicit tool
selection is a failure.

- [ ] **Step 4: Audit active release strings and evidence freshness**

```bash
rg -n '0\.58\.0|pto-isa-0\.58\.0' \
  compiler emulator kernel lib rtl tools avs docs \
  -g '!docs/archive/**' -g '!docs/zh/archive/**' -g '!avs/archive/**'
```

Classify every remaining match as historical compatibility input or fix it.
Require every mandatory report to contain exact current SHAs, non-empty
artifacts, pass status, and age within the gate policy.

- [ ] **Step 5: Commit root integration, push, review, and merge to main**

```bash
git add -A
git diff --cached --check
git commit -m "release: complete LinxISA superproject 0.58.1 alignment"
git push -u origin codex/v0581-superproject-upgrade
```

Merge only the exact reviewed commit through required checks. Do not move the
existing root `v0.58.1` tag; if a new published release is requested later,
use the next patch tag.

- [ ] **Step 6: Run cleanup checker in pre-delete mode against live refs**

```bash
python3 tools/bringup/check_branch_cleanup_manifest.py \
  --manifest docs/bringup/branch_cleanup_manifest.json --mode pre-delete
```

- [ ] **Step 7: Remove the clean attached B.IOS worktree, then delete only exact approved stale refs**

Delete local branches with `git branch -d` when ancestry permits and exact
tree-equivalent/superseded branches with `git branch -D` only after the
manifest proves their OID and replacement. Delete remote refs with explicit
full branch names only after re-running `git ls-remote`; retain all listed
release branches and tags.

- [ ] **Step 8: Fetch/prune and prove cleanup plus retained history**

```bash
git fetch --prune origin
python3 tools/bringup/check_branch_cleanup_manifest.py \
  --manifest docs/bringup/branch_cleanup_manifest.json --mode post-delete
git worktree list --porcelain
git status --short --branch
```

- [ ] **Step 9: Perform requirement-by-requirement completion audit**

For every objective clause, cite the authoritative merged file, canonical leaf
SHA, successful command/report, Pages workflow artifact, archive location, or
post-delete ref evidence. Any missing, skipped, stale, indirect, or wrong-SHA
evidence keeps the goal open.
