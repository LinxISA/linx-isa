# Task 4 — QEMU / AVS PTO ISA 0.58.1 report

## Status

The QEMU-owned implementation and its targeted, native, strict-system, full
AVS, and superproject-wide TEPL consistency gates are green.

## Git provenance

- Canonical QEMU base: `c667cdec93ba4ee48bf09c2649c16949e219c95c`
  (`origin/master`, release tag `linxisa-v0.58.4` preserved).
- Local topic: `codex/v0581-release`.
- QEMU implementation commit:
  `0075536c6266a7bb7e15e9f60dd1c5d7701c2471`.
- No branch or tag was deleted, and nothing was pushed.

## Red evidence captured before implementation

- Decoder-source coverage: 727/731 mnemonics and 749/765 exact forms.
- Missing mnemonics: `B.FPATR`, `BSTART.CALL`, `BSTART.ICALL`, `L.BSTOP`.
- DATR legality differed from the canonical table for 87 entries.
- Numeric-vector table contained 75 vectors instead of the official 104.
- The Linx ELF loader had no fail-closed PTO ISA identity validation.
- The initial exact-contract, DATR, engine-count, numeric-vector, retired-form,
  and ELF-identity tests failed on those gaps.

The source coverage red artifact is `/tmp/qemu-isa-coverage-red.json`; it
records 727/731 mnemonics and 749/765 forms from the pinned pre-repair source.

## Implemented contract

- Added exact decode/execute metadata for the four missing mnemonics and all
  765 legal forms, with bidirectional checks rejecting retired forms.
- Bound the 109 PTO operations to the canonical engine/DATR state:
  31 VEC, 56 SFU, 10 TLSU, and 12 CUBE operations.
- Installed all 104 official numeric vectors. Canonical vector payload SHA-256:
  `59c96cc2f45f8e8f3eebb8230338b21ec3a77a99e8fb5e1c7c7b391819a6aa81`.
- Added fail-closed ELF note validation in `hw/linx/virt.c` before loader state
  mutation. Exact 0.58.1 and identical duplicate notes are accepted; missing,
  old, malformed, trailing-NUL, conflicting duplicate, and mixed notes are
  rejected before guest entry.
- Corrected `BSTART.ICALL` to snapshot the pre-bound BARG target before the
  boundary reset; the native call/return contract caught the original error.
- Updated migration state for FPATR state (VMState v20, minimum v19).
- Routed active AVS generation to `isa/v0.58/linxisa-v0.58.json`, removed the
  handwritten v0.57 suites from the active runner, and marked the audited
  v0.57.1 executable-evidence ledger explicitly archival.
- Added exact root contract and ELF identity fixture checks and regenerated the
  checked-in QEMU ISA coverage report.

## Green verification evidence

- `python3 tools/bringup/check_qemu_pto_v0581_contract.py`:
  731/731 mnemonics, 765/765 forms, 109 operations, 104 numeric vectors.
- `python3 tools/bringup/report_qemu_isa_coverage.py ... --require-full`:
  731/731 mnemonics and 765/765 exact forms; refreshed JSON and Markdown gates.
- `bash tools/bringup/run_qemu_build_clean.sh ... /tmp/linx-qemu-clean-build`:
  clean `qemu-system-linx64` build from QEMU commit `0075536c...`.
- `meson test -C /tmp/linx-qemu-clean-build test-linx-tile-transaction
  test-linx-tile-cube-numeric test-linx-tile-state-dump`: all 29 subtests pass
  (12 transaction, 14 numeric, 3 state-dump).
- QEMU Linx Python suite: 64 tests pass.
- Root exact-contract checker suite: 3 tests pass.
- AVS Python suite: 95 tests pass, including the active-release routing,
  identity-fixture, and archival-ledger assertions.
- `python3 avs/qemu/run_elf_identity_contract.py ...`: canonical and identical
  duplicate identities accepted; all six negative identities rejected before
  guest entry.
- `QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64 bash
  avs/qemu/check_system_strict.sh`: PASS.
- `(cd avs/qemu && QEMU=/tmp/linx-qemu-clean-build/qemu-system-linx64
  ./run_tests.sh --all --timeout 10)`: PASS.
- `LLVM_MC=... QEMU_BIN=... bash
  emulator/qemu/scripts/linxisa/run-fused-call-contract.sh`: PASS.
- QEMU topic worktree is clean.

## Integrated TEPL gate

After Task 1 installed LLVM commit
`cc9d100e9e83bbedd79e17465e6a0771b25b9bd9`,
`python3 tools/bringup/check_tepl_encoding.py --root .` reports 87 canonical
TEPL operations and `OK`. The prior TDIV/TDIVS/TREM/TREMS VEC/SFU mismatch is
resolved.

## Skill closeout

The existing Linx QEMU, ISA, and superproject skills already describe the
required exact-contract, fail-closed identity, clean-build, and cross-repo gate
workflow. Skill evolution result: `no-update`.
