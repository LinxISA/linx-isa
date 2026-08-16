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

## Independent review remediation

The review requested changes for three fail-closed gaps. Follow-up model commit
`06a529db0bc55d16bfb9583bd0a6907ac1770a4b` addresses them:

1. Standalone hosted CI now checks out LinxISA commit
   `ea54153b3351c48df306a57189ffb587801b9197`, configures
   `LINXISA_AUTHORITY_ROOT`, and invokes `check-isa-codec`. Missing standalone
   authority fails closed.
2. The generator authenticates the complete catalog, PTO lock, and release
   manifest bytes before inspecting declared identities. A same-count mutation
   of a non-required `ADDI` encoding is a negative regression.
3. Release-strict validation now reopens and hashes every artifact/result,
   admits exactly `qemu`, `ref`, and `compare`, resolves result address/size
   from ELF symbols and matches the manifest, enforces exact file lengths,
   compares result bytes against golden and pairwise itself, and binds every
   comparison row to consumer-binary and result hashes.

Additional red/green cases reject missing, short, long, or mutated results;
mutated tools; arbitrary consumer names; manifest/ELF size disagreement; and
self-declared comparison hashes. The synthetic complete proof passes only when
all files, hashes, sizes, symbols, bytes, consumers, and comparison bindings
agree.

Fresh remediation verification:

- Generator authority/freshness tests: 6/6 passed.
- Root AI/provenance tests: 36/36 passed.
- Model build: no work pending after successful configure.
- Model CTest: 11/11 passed.
- Standalone copied model checkout configured with explicit immutable authority
  and passed `check-isa-codec`.
- Hosted workflow YAML parsed and contains both the exact LinxISA commit and
  the committed-output freshness invocation.
- The real release-strict command remains fail-closed at the intentionally
  absent Task 4 QEMU binary; no runtime promotion is claimed.

## Scoped re-review remediation

Follow-up model commit `5004faa` closes the remaining hosted-CI authority gap:
every job that runs authority-dependent CTest (`st` and `sanitizers`) checks
out immutable LinxISA authority commit
`ea54153b3351c48df306a57189ffb587801b9197` and configures
`LINXISA_AUTHORITY_ROOT`. A workflow regression test enforces that exact pin
for both jobs, while standalone execution without authority still fails
closed.

Release-strict ELF validation now accepts only ELF64 `ET_EXEC` artifacts with
a program-header table and at least one `PT_LOAD`. It requires
`cross_model_result` to be defined in an allocatable section at a nonzero
address, requires `cross_model_result_size` to be a positive absolute symbol,
and proves the complete result byte range is inside one loadable segment before
consulting self-declared manifest or comparison data. Explicit negatives cover
`ET_REL`, undefined result and size symbols, non-alloc sections, a patched
zero-address symbol, and a symbol range extending past its `PT_LOAD` segment.

Fresh scoped re-review verification:

- Red: the hosted-workflow regression failed for `sanitizers`; all five initial
  malformed-ELF tests failed because the validator either accepted the input
  or reached a later, unrelated check.
- Green: generator/hosted-workflow tests passed 7/7.
- Green: targeted positive plus malformed-ELF tests passed 7/7, including the
  additional undefined-size-symbol case.
- Green: root AI/provenance tests passed 42/42.
- Green: committed codec freshness passed with 765 forms, 2661 fields, 3401
  pieces, and 780 constraints; model build was current and CTest passed 11/11.
- Runtime promotion remains blocked by the absent Task 4 QEMU executable; no
  release-strict runtime PASS is claimed.
