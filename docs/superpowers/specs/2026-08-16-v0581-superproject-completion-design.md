# LinxISA v0.58.1 Superproject Completion Design

## 1. Objective

Complete the LinxISA superproject upgrade to release `0.58.1` as one coherent,
leaf-first integration. The delivered superproject must use the released
LinxISA/PTO identity in every component that emits, consumes, validates, or
documents that identity; publish the Chinese ISA documentation as GitHub
Pages; preserve useful unique branch content; archive explicitly historical
design material; and remove stale local and upstream branches only after their
content is proven integrated or superseded.

This is a corrective completion train on top of superproject commit
`ea54153b3351c48df306a57189ffb587801b9197` and tag `v0.58.1`. The existing
tag is immutable. The train does not move or replace `v0.58.1`; it brings the
superproject and leaf repositories into agreement with the identity already
released by that tag and lands the result on `main` through normal reviewed
commits.

## 2. Authoritative Release Contract

All active implementations and current documentation consume this exact
identity from `isa/v0.58/pto-spec.lock.json` and
`isa/v0.58/release_manifest.json`:

- LinxISA profile: `v0.58`
- LinxISA release: `0.58.1`
- PTO release: `0.58.1`
- Encoding ABI: `pto-isa-0.58.1-mode-function-v1`
- Encoding projection SHA-256:
  `89b872d6eaf0252200bc9349d49b9346e2a69d894cdcc2dcd0fd71911c1e0b8c`
- PTO source commit: `c381465b2b8e457e162a4246ee58bb9a2c5b49fd`
- PTO source tree: `463a19db3d6ba70022f18bdbca0d4b2c6ed586e4`
- PTO lock content SHA-256:
  `693e8c0734b48598ac35ffe7fe6f2a01037788fba30ebe026895808d23139f2c`
- Tile operations: `109`
- Command forms: `74`
- Scalar forms: `474`
- Extension encoding reservations: `32`
- Execution engines: exactly `VEC`, `SFU`, `TLSU`, and `CUBE`
- `TEPL`: Mode/Function encoding carrier, not an execution engine
- Shared binding: 32-bit `B.IOS`, absolute `S0..S255`, 8-bit SharedTID,
  4-bit PE mask, and a zero PE mask with no effect

The profile directory remains `isa/v0.58/`. A new `isa/v0.58.1/` directory is
not introduced. Historical profiles and archived documents are non-normative
and never serve as active generator or validation input.

## 3. Why the Existing Root Tag Is Not Sufficient

The root release manifest and PTO lock already describe `0.58.1`, but several
governed leaf pins still embed the earlier `0.58.0` release identity:

- LLVM/LLD and MC descriptor metadata
- PTOAS release lock and cross-root checker
- Linux ELF loader documentation and enforcement
- glibc and musl loader identity
- LinxCore generated catalog source profile
- `tools/model` documentation and fixtures

A root-only gitlink or documentation update would preserve a mixed release.
Conversely, merging every historical branch wholesale would restore obsolete
v0.57 generated sources, spellings, evidence, and pins. The selected solution
therefore ports only reviewed unique content and regenerates each affected
leaf from the current `0.58.1` authority.

## 4. Integration Architecture

The train is leaf-first and fail-closed:

```text
LinxISA/PTO 0.58.1 authority
  -> LLVM and PTOAS producers/checkers
  -> Linux, glibc, and musl loaders
  -> QEMU and AVS decode/runtime coverage
  -> model, LinxCoreModel, pyCircuit, and LinxCore projections
  -> TileOP API and PTO kernels/nested SuperNPU
  -> documentation, Chinese Pages, and skills
  -> exact superproject component lock and gitlinks
  -> full current-SHA integration gates
  -> main merge and stale-ref cleanup
```

Each leaf is changed and verified in its own repository before the
superproject records its SHA. A leaf SHA is eligible for the final component
lock only when its worktree is clean, its commit is remotely reachable on the
canonical repository, and all mandatory owned gates pass. Topic branches,
uncommitted worktrees, empty evidence, and stale generated reports are not
release identities.

## 5. Component Responsibilities

### 5.1 LLVM and PTOAS

LLVM remains on the current descendant implementation; it is not downgraded to
an older tag whose name happens to contain `0.58.1`. Its MC producer, LLD
consumer, note fixtures, generated descriptors, and negative identity tests
must encode the exact current release identity.

PTOAS preserves the useful work on `codex/v058-release`, including LLVM 23,
nanobind, build isolation, and CPython linking. Its `0.58.0` lock is regenerated
from the root `0.58.1` authority. The cross-root checker must compare release,
ABI, projection hash, source commit/tree, release-manifest hash, catalog
hashes, and catalog counts. A mismatched-release regression must fail before
the checker is fixed and pass afterward. Wheel automation must recognize
`linxisa-v0.58.1` without routing it through the package-version comparison.

### 5.2 Linux, glibc, and musl

The kernel and both hosted libc loaders consume the same canonical ELF note
bytes and reject missing, old, malformed, conflicting, or mixed identities.
Their documentation and fixtures must say `0.58.1`; no active loader path may
retain `0.58.0` as an accepted current identity. Linux is upgraded from its
governed branch, not from an unrelated default history.

### 5.3 QEMU and AVS

QEMU keeps its current descendant implementation and regenerates or audits
decode/execute/catalog projections against the current manifest. Its Linx ELF
loaders must validate the exact canonical `.note.pto.isa` identity before
execution, because the released documentation already promises fail-closed
QEMU enforcement and the current pin does not implement it. AVS adds positive
`0.58.1` ELF-note coverage plus missing, old-`0.58.0`, malformed, trailing-NUL,
duplicate-conflicting, and mixed-identity rejection cases. AVS compile,
runtime, strict decode, retired-spelling, B.IOS, and executable-coverage tests
must exercise the delivered QEMU and compiler SHAs. Historical evidence stays
under versioned archives and cannot satisfy a current gate.

### 5.4 Models, pyCircuit, and LinxCore

`tools/model`, LinxCoreModel, pyCircuit, and LinxCore consume the same catalog
and release identity. Generated catalog metadata must use source profile
`0.58.1`. Cross-model validation uses one ELF and independent golden data and
records exact executable and component hashes. LinxCore changes are limited to
the release projection and owned conformance behavior; unrelated backend work
is not pulled into the train.

### 5.5 TileOP API and PTO Kernels

The released TileOP API pin `8f021d53d6b33ccff6babab6b80693c4fa9f6aa1`
is the known-good `0.58.1` baseline. Canonical `origin/linx` is a
non-descendant that retains obsolete selector and constraint surfaces and
fails the release contract suite; it must not be pinned directly. Reconcile
canonical `linx` by porting its still-desired additions onto the known-good
release baseline, or by repairing it on a reviewed topic branch until
`make check` passes without waivers, then pin the canonical merged SHA.

PTO kernels merges the two reviewed commits on `codex/v058-release` into
canonical `pto-isa/main`, never the divergent legacy `origin` fork, then
validates the current startup syntax, sysroot/triple contract, TLOAD/TSTORE
migration, heap behavior, formatting/lint rules, and retired TCOPYIN/OUT
rejection. The maintained SuperNPU source remains
`workloads/pto_kernels/benchmarks/supernpu`.

The standalone `workloads/SuperNPUBench` checkout is not a superproject leaf.
Its upstream tree is already represented by the nested `SOURCE.lock`; its only
unique local commit is an obsolete private v0.57 path change and is not
ported. The standalone checkout is removed from the active workspace only
after nested-source identity is verified. Non-ancestral backup refs are
preserved by archival tags before any branch deletion.

### 5.6 Related Leaves

Mesa3D, linx-skills, and other governed leaves are repinned only when their
current tree is compatible with the exact final toolchain and lock. Skills are
updated only for reusable commands, invariants, or stop conditions introduced
by this train; release-specific prose alone does not justify a skill change.

## 6. Branch Integration and Retention

### 6.1 Unique content to integrate

- `codex/linx-l-bstop-v058`: port the bilingual B.IOS pages, navigation,
  language map, translation freshness record, and catalog-bound regression.
- `origin/dependabot/github_actions/actions/checkout-7`: reapply the six
  `actions/checkout@v6` to `@v7` changes on current `main`.
- `origin/dependabot/github_actions/actions/setup-python-7`: reapply the six
  `actions/setup-python@v6` to `@v7` changes on current `main`.
- `workloads/pto_kernels` `codex/v058-release`: merge both reviewed commits
  into canonical `pto-isa/main`.
- `compiler/ptoas` `codex/v058-release`: preserve useful implementation work
  while correcting the release contract before merge.

### 6.2 Release refs to retain

- `codex/linx-058-final-release`
- `codex/linx-isa-0.57.1`, because no `v0.57.1` tag preserves its individual
  22-commit review history
- `codex/v058-release-existing-repos`
- `codex/v058-release-train`
- immutable release tags, including `v0.58.1`

### 6.3 Stale refs to delete after verification

- local `codex/v058-b-datr-doc-fix`
- local `codex/v058-bior-resolution-sync`
- local `codex/linx-l-bstop-v058` after its commit is integrated
- remote `codex/fishtoucher-software-loop`
- remote `codex/refresh-translation-freshness`
- remote `feat/v0.57`
- the two Dependabot branches after their changes are integrated and checks
  pass
- component-local historical branches proven ancestral, tree-equivalent, or
  superseded, excluding retained release branches and archival tags

Deletion is an end-of-train transaction. Immediately before deletion, every
target SHA and classification is re-resolved from the live remote. A ref is not
deleted if it moved after review, contains an unpreserved commit, is a default
branch, is protected, or is still attached to a worktree.

## 7. Documentation and Pages

The English source remains normative. The Chinese tree remains a maintained
translation and must clearly preserve that status. Both sites are built in CI,
but GitHub Pages publishes the Chinese configuration from `mkdocs.zh.yml`.
The Pages artifact must have a Chinese home page and Chinese ISA navigation;
it must not accidentally publish the English `mkdocs.yml` build.

The B.IOS detailed page is added in both languages and linked through both
navigation trees and the language map. Translation freshness is regenerated
from current English sources and checked. Generated ISA manual, encoding,
catalog, and release pages are refreshed only from `isa/v0.58` authority.

Explicitly historical design/checklist material moves into established
versioned archives with all references updated. Active architecture research,
current release specifications, and normative contracts are not moved merely
because they predate this train. The earlier
`docs/archive/v0.58/release/2026-08-11-v058-component-release-train-design.md` is
archived as a completed 0.58.0/initial-0.58.1 release design after this new
design becomes the current record.

## 8. Verification Contract

Every changed leaf runs repository-native tests and its owned release gates.
The final superproject candidate additionally proves:

- repository topology and allowed paths;
- every gitlink equals the component lock SHA;
- every governed worktree is clean and remotely reachable;
- v0.58 golden, canonical, PTO lock, catalog, opcode, generated codec, Sail,
  and manual closure;
- exact `0.58.1` identity across LLVM, PTOAS, Linux, glibc, musl, model, and
  generated RTL/catalog fixtures;
- LLVM/PTOAS assembly, object, note, link, and negative mismatch behavior;
- QEMU strict decode, runtime, snapshot, retired-spelling, and executable
  coverage gates;
- Linux build and boot evidence plus fail-closed ELF identity behavior;
- glibc and musl static/shared runtime coverage;
- QEMU/model/pyCircuit/LinxCoreModel/LinxCore differential evidence using the
  same ELF bytes;
- PTO-kernel and nested SuperNPU compile/disassembly/runtime checks;
- English and Chinese MkDocs strict builds;
- the Pages workflow packages the Chinese build;
- translation freshness, navigation, language-map, and B.IOS tests;
- no active source or current document retains `0.58.0` where `0.58.1` is
  required;
- fresh, non-empty, exact-SHA release evidence for every mandatory gate.

A skipped, waived, stale, pending, empty, dirty, wrong-SHA, or missing-tool
result is not a pass. When an environment cannot run a mandatory hosted or
hardware gate locally, the exact reviewed commit must receive the required
hosted result before merge or branch deletion.

## 9. Commit, Merge, and Cleanup Transaction

1. Commit this design and the implementation plan on the isolated integration
   branch.
2. Upgrade and test each leaf in dependency order, using tests before behavior
   changes and one reviewed commit series per leaf.
3. Push leaf branches, merge through normal repository policy, and record the
   canonical merged SHA.
4. Repin the superproject only to canonical reachable leaf SHAs and refresh the
   component lock atomically.
5. Port root unique branches, publish Chinese Pages configuration, update
   documents, and move legacy designs.
6. Run the full current-SHA integration matrix and obtain required hosted
   checks.
7. Merge the exact reviewed superproject commit to `main` without moving the
   existing `v0.58.1` tag.
8. Re-resolve and delete only the stale refs enumerated by the live cleanup
   manifest. Remove attached worktrees before deleting their branches.
9. Fetch with prune and prove that retained release refs remain and deleted
   refs no longer resolve locally or remotely.

## 10. Completion Criteria

The work is complete only when:

1. all active identity producers and consumers agree with the exact `0.58.1`
   authority;
2. AVS, QEMU, LLVM, Linux, libc, models, LinxCore, TileOP API, PTO kernels, and
   related governed submodules are pinned to verified canonical commits;
3. unique branch work is present on `main` and no useful commit is discarded;
4. GitHub Pages publishes the Chinese ISA site while both languages build;
5. current documents and generated views match the final pins and authority;
6. explicitly historical designs are archived and no active reference is
   broken;
7. all mandatory local and hosted gates pass for the exact merged SHAs;
8. retained release branches and tags remain reachable; and
9. every approved stale local and upstream branch has been removed and its
   absence verified.
