# LinxISA v0.58 Component Release Train Design

> Archive status: historical v0.58.0/v0.58.1 release-train design. This file is
> non-normative and must not be used to infer current v0.58.3 component pins,
> identities, semantics, or release gates.

## 1. Objective

Upgrade every component governed by `docs/bringup/component-lock.v0.58.json`
to one coherent LinxISA/PTO ISA 0.58 contract, verify the exact integrated
component set, publish each governed leaf as `linxisa-v0.58.0`, and publish the
corrective superproject release as `v0.58.1`.

The existing mutable lightweight `v0.58` tag is historical and must never move
again. The new releases use signed annotated tags and immutable exact commit
identities.

## 2. Scope

The release train contains the fourteen leaf gitlinks in the v0.58 component
lock:

1. `compiler/llvm`
2. `compiler/ptoas`
3. `emulator/qemu`
4. `kernel/linux`
5. `lib/glibc`
6. `lib/mesa3d`
7. `lib/musl`
8. `rtl/LinxCore`
9. `skills/linx-skills`
10. `tools/Linx-TileOP-API`
11. `tools/LinxCoreModel`
12. `tools/model`
13. `tools/pyCircuit`
14. `workloads/pto_kernels`

The removed standalone `PTO-ISA/SuperNPUBench` repository is not a release
train leaf. No code, tag, or release is pushed there. Existing issue
`PTO-ISA/SuperNPUBench#41` is the tracking surface; the maintained workload is
changed and verified only through
`workloads/pto_kernels/benchmarks/supernpu`.

## 3. Fixed Contract

All leaves consume one identity:

- LinxISA profile: `v0.58`
- PTO release: `0.58.0`
- Encoding ABI: `pto-isa-0.58.0-mode-function-v1`
- Encoding projection SHA-256:
  `0cad2272ada8f53fc8354e22568099fe8d6bd4b7832c837260cd370b0fc76ffa`
- PTO common Tile operations: 109
- Execution engines: `VEC`, `TLSU`, `CUBE`, and `SFU`
- `TEPL`: encoding carrier only
- Shared binding: 32-bit `B.IOS`, absolute `S0..S255`
- TSize: codes `1..7` represent 128 B through 8 KiB per selected PE
- Zero PE mask: strict no-effect operation
- Retired active spellings include `C.B.IOS`, `B.IOD`, `BSTART.PAR`, and the
  superseded v0.57 selector surface

The `.note.pto.isa` wire identity is exactly one allocatable `SHT_NOTE`
section, four-byte aligned, with owner bytes `PTO\0`, type `1`, and canonical
compact JSON without a trailing NUL. Producers, LLD, Linux, glibc, and musl
must agree byte-for-byte and reject missing, old, malformed, conflicting, or
mixed identities.

## 4. Release Architecture

The release is a leaf-first train with one integration proof:

```text
ISA/PTO lock
  -> LLVM + PTOAS
  -> QEMU + Linux + glibc + musl + Linx-TileOP-API
  -> tools/model
  -> LinxCoreModel + pyCircuit
  -> LinxCore
  -> pto-kernels and nested SuperNPU
  -> linx-skills
  -> superproject exact repin and v0.58.1
```

Independent leaves may be implemented in separate branches, but this session
executes them inline and sequentially at dependency boundaries. Every leaf is
merged before its SHA is eligible for the component lock. Topic heads and
uncommitted worktrees are never release identities.

## 5. Leaf Responsibilities

### 5.1 Producers

LLVM must provide the canonical 0.58 MC/codegen surface, unique Shared TMOV
selection, generated metadata, and the canonical ELF identity. PTOAS must
replace its 0.57.1/120-operation lock with the 0.58/109-operation contract and
provide parser, printer, encoder, decoder, allocation, bytecode, and handoff
coverage.

### 5.2 Runtime and loaders

QEMU consumes the merged v0.58 implementation and proves decode, execution,
snapshot stability, and cross-model results. Linux releases from its governed
`main` branch, not the unrelated GitHub-default `master` history. glibc and
musl upgrade their fail-closed dynamic-loader identities to 0.58 and exercise
main executable, interpreter, dependency, and `dlopen` closure.

### 5.3 Models and RTL

`tools/model` is the first architectural oracle for Shared allocation and
effect rules. LinxCoreModel and pyCircuit then implement their cycle/interface
surfaces. LinxCore consumes the stable catalog and model fixtures and proves
RTL-visible allocation, rename, atomic update, reset, and trace parity. Orphan
topic gitlinks for LinxCore and LinxCoreModel are replaced by merged commits.

### 5.4 API, workloads, and skills

Linx-TileOP-API exposes only the active API and must prove generated object and
disassembly behavior with the exact LLVM SHA. PTO-kernels consumes that API,
contains the maintained SuperNPU tree, and runs clean compile, disassembly,
runtime, and cross-model checks. linx-skills is updated last so its commands,
paths, and stop conditions match the delivered repositories.

Mesa3D receives the same release tag only after confirming that its current
pin neither emits nor consumes a conflicting LinxISA/PTO identity and that its
existing checks pass against the final sysroot/toolchain surface.

## 6. Verification Contract

Each leaf must pass its repository-native tests plus the v0.58 acceptance
matrix that exercises its owned contract. A leaf is not ready when any required
result is failed, pending, skipped, waived, stale, missing-tool, dirty, or
missing an exact SHA.

The integrated candidate additionally proves:

- repository topology and component-lock/gitlink equality;
- v0.58 golden, spec, PTO lock, canonical, generated codec, Sail, and docs
  closure;
- LLVM/PTOAS object round trips and negative spelling tests;
- QEMU strict/runtime and coverage gates;
- Linux clean build, initramfs/rootfs boot, and ELF identity enforcement;
- glibc and musl static/shared hosted runtime;
- QEMU/model/pyCircuit/LinxCoreModel/LinxCore differential evidence;
- fresh nested SuperNPU and representative benchmark runtime evidence;
- identical required gate-key sets for clean `pin` and `external` lanes;
- a non-empty `docs/bringup/gates/latest.json` less than 24 hours old;
- a complete, clean SHA manifest for the superproject and all leaves.

Before the candidate can pass, the superproject gate registry and phase policy
must be fail-closed: `LINUX-RUNTIME` and `PROMOTION` have explicit required
gate sets, Linux gates cannot be silently filtered, the v0.58 canonical
freshness input references the v0.58 manifest, and SHA mismatch or omission is
fatal.

## 7. Merge and Release Transaction

1. Implement and review a leaf on a dedicated branch/worktree.
2. Run the leaf acceptance matrix and hosted checks.
3. Merge through a PR without bypassing required checks.
4. Record the merged commit and tree.
5. Repin only that leaf in the superproject integration branch.
6. After all leaves land, run the complete exact-SHA integration matrix.
7. Freeze the candidate superproject commit, tree, component-lock digest, and
   fourteen leaf SHAs.
8. Create signed annotated `linxisa-v0.58.0` tags at the frozen leaf commits.
9. Create draft GitHub Releases, attach provenance/checksum evidence, and
   verify tag-to-commit-to-tree resolution.
10. Publish leaf releases in dependency order. Stop on the first failure.
11. Merge the exact reviewed superproject tree and rerun final-main checks.
12. Create signed annotated `v0.58.1`, verify the remote object, upload the
    manual/catalog/lock/evidence bundle and checksums, and publish the root
    release last.

Tags are never moved or deleted as a repair mechanism. A post-tag defect uses a
new patch version.

## 8. SuperNPUBench Handling

`PTO-ISA/SuperNPUBench#41` is reused rather than creating a duplicate issue.
Before workload implementation starts, add one comment containing:

- the selected exact LinxISA, LLVM, PTOAS, TileOP, QEMU, model, and pto-kernels
  commits;
- the dependency and release-train order;
- the compile/disassembly/runtime/cross-model matrix;
- the explicit rule that this release train makes no direct repository push,
  tag, or release in SuperNPUBench;
- links to evidence produced from the nested maintained copy.

## 9. Safety, Failure, and Recovery

Stop immediately if a required gate is not a fresh pass, a reviewed and merged
tree differ, a branch/default-branch ambiguity remains, a component identity
changes after validation, or a merge needs administrative bypass.

Before tags exist, fix the leaf and rerun all dependent validation. After a
leaf tag exists but before the root release, keep the leaf tag immutable and
use a new patch tag if its identity is invalid. After publication, mark a bad
release superseded, land a normal corrective PR, and publish a new patch
release; never rewrite release history.

The user's original dirty checkout remains untouched. All implementation and
verification work occurs in isolated worktrees.

## 10. Completion Criteria

The objective is complete only when all fourteen leaf releases exist at the
verified exact commits, the nested SuperNPU issue carries current evidence,
the superproject component lock and gitlinks match those releases, all required
current-SHA gates pass, and `v0.58.1` is published at the proven final tree.
