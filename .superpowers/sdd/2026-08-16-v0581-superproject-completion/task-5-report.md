# Task 5 — tools/model 0.58.1 codec and immutable provenance

## Outcome

- Model topic: `codex/v0581-release` from `origin/main`.
- Local model commit: `2ce598232f70f96b2ff7a59d58a634876c21e35b`.
- The pre-existing `linxisa-v0.58.1` tag remains unchanged at `69e926b`.
- The committed codec now contains 765 forms, 2661 fields, 3401 pieces, and
  780 constraints, including `B.FPATR` mask/match `0x7fff/0x2023` and
  `BSTART.ICALL` mask/match `0xf83fffff/0x50166001`.
- Generation fails closed on any drift in the exact PTO ISA 0.58.1 release,
  ABI, projection hash, source commit/tree, catalog hashes/counts, release
  manifest cardinalities, codec cardinalities, or required new forms.
- `check-isa-codec` regenerates into a temporary directory and byte-compares
  the committed output.
- AI workload consumers record and re-check SHA-256 identities for compiler,
  linker, copied ELF, QEMU, and model binary before each consumer and after the
  flow. The model differential runner independently records the same available
  tool/ELF/manifest inputs around its consumers.
- `release-strict` rejects trace-only output and requires immutable hashes for
  compiler, linker, ELF, QEMU, model, manifest, and independent golden data,
  plus each model's result memory, all golden comparisons, and all pairwise
  comparisons.

## Red evidence

- Generator identity tests failed because `validate_authority`, `--lock`,
  `--release-manifest`, and `--check` did not exist.
- AI mutation tests failed because no immutable-artifact capture/verification
  API existed.
- The original shared-state fixture failed the new exact identity check because
  it named PTO ISA `0.58.0` and source commit
  `8a77c9f0eab36cc41051519366ff163171f81463`.
- Freshness check failed on the old committed source table.
- First regenerated CTest run exposed the stale 766-form expectation and stale
  CASB/CASD/DMA UIDs; those tests were updated to the exact catalog.

## Green evidence

- `python3 -m unittest tools.bringup.test_run_ai_workload_flow -v` — 31/31
  passed.
- `python3 -m unittest tools/model/tests/checks/test_gen_minst_codec.py -v` —
  3/3 passed, including seven authority mutations and stale-output rejection.
- `cmake --build tools/model/build --target check-isa-codec` — passed with
  `765 forms, 2661 fields, 3401 pieces, 780 constraints`.
- `cmake --build tools/model/build` — passed.
- `ctest --test-dir tools/model/build --output-on-failure` — 11/11 passed.
- `QEMU=/usr/bin/true python3 tools/bringup/run_ai_workload_flow.py --profile
  smoke --limit 1 --dry-run --qemu /usr/bin/true --gfsim /usr/bin/true
  --out-dir /tmp/linx-ai-v0581-provenance-dryrun` — passed as a dry-run path
  check.

## Remaining release-strict blocker

The required command currently stops before execution because Task 4 has not
yet produced the expected QEMU binary:

```text
error: provenance artifact qemu is missing: .../emulator/qemu/build-linx/qemu-system-linx64
```

Even after that binary exists, the current suite is still trace-oriented and
does not yet publish independently generated golden bytes or architecture-
visible `result.bin` files for QEMU and the model. The new release-strict gate
will continue to reject that evidence until Task 4 supplies the QEMU dump
surface and the suite supplies golden/result-memory/pairwise artifacts. No
release-strict PASS is claimed.

## Skill evolution

- `skill-evolve: no-update linx-model (Task 5 changed codec/provenance
  implementation, not reusable queue/module semantics)`
- `skill-evolve: no-update linx-isa (no normative authority change)`
- `skill-evolve: no-update linx-superproject (no topology/governance change)`
