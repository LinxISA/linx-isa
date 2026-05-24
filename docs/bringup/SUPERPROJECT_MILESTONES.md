# Superproject Milestones

This page is the canonical repo-wide planning surface for LinxISA bring-up.

Legacy numbered surfaces remain in the tree as implementation history:

- `G0..G5` are no longer the canonical governance phase names.
- `M1..M6` are no longer the canonical superproject milestone names.
- `docs/bringup/phases/01_..08_*.md` remain useful domain notes, but not the
  canonical planning taxonomy.

Use named capability phases and milestone IDs instead.

## Governance Phases

- `FOUNDATION`
  Contract truth, ownership map, machine-readable reports, and basic gate wiring.
- `CORE-CLOSURE`
  Compiler, AVS compile/coverage, QEMU runtime baseline, RTL/model/trace parity.
- `LINUX-RUNTIME`
  Firmwareless Linux boot, initramfs userspace entry, BusyBox/rootfs closure.
- `HOSTED-RUNTIME`
  musl/glibc hosted ABI/runtime closure, shared-loader path, C++ runtime policy.
- `WORKLOAD-RUNTIME`
  SPEC, TSVC, PTO parity, benchmark/runtime workload execution closure.
- `PROMOTION`
  Nightly breadth, privileged/MMU/debug parity, performance discipline, release promotion.

## Milestones

### CORE-M01 Gate Truth And Ownership

Goal:
- Machine-readable gate truth, ownership, and generated markdown stay aligned.

Done means:
- gate registry, manifest, checklist ID map, and generated gate-status views are coherent
- no stale blocker prose survives without current evidence

### CORE-M02 Compiler And AVS Compile Closure

Goal:
- LLVM compile suites, active coverage, assembler surfaces, and required tools are stable.

Done means:
- active compile suites pass
- required compiler coverage gates pass
- `llvm-ar` / `llvm-nm` / `llvm-readelf` / `llvm-strip` are present and used by gates

### CORE-M03 Emulator Runtime Baseline

Goal:
- QEMU strict-system and AVS runtime suites are stable on the active v0.56 line.

Done means:
- runtime/system gates pass
- opcode/meta sync and coverage reports are current
- firmwareless boot contract is consistent across runtime harnesses

### CORE-M04 RTL / Model / Trace Parity

Goal:
- LinxCore, pyCircuit, and LinxTrace parity gates are green enough to stop being first blockers.

Done means:
- required RTL/model/trace gates pass on the active lane
- mismatch triage produces first-divergence evidence instead of broad failure summaries

### LINUX-M01 Firmwareless Userspace Entry

Goal:
- Linux reaches visible initramfs userspace under firmwareless QEMU boot.

Done means:
- trivial static initramfs control payload emits guest-visible start/pass markers
- failure, if any, is after userspace entry rather than a silent zero-output stall

### LINUX-M02 Rootfs And Hosted Userspace Closure

Goal:
- BusyBox rootfs and equivalent hosted userspace lanes reach `/sbin/init` and complete basic lifecycle.

Done means:
- BusyBox rootfs boot no longer blocks strict closure
- virtio-blk/ext2 userspace path is no longer the first Linux runtime blocker

### LIBC-M01 Static Runtime Baseline

Goal:
- musl static/runtime baseline is reproducible and aligned with the active compiler ABI model.

Done means:
- musl `M1/M2` pass on the active lane
- static runtime smoke is green or produces a precise post-userspace-entry failure
- arch headers do not hardcode stale floating-point ABI assumptions

### LIBC-M02 Hosted Shared Runtime

Goal:
- musl/glibc shared-runtime lanes are restored and reproducible.

Done means:
- shared musl/glibc loaders and `libc.so` artifacts are present and consumed successfully by hosted control lanes

### SPEC-M01 .. SPEC-M06 / SPEC-P01

Canonical plan:
- `docs/bringup/SPEC_WORKLOAD_PLAN.md`

Meaning:
- SPEC has its own planning surface because it crosses Linux, libc, workload, and xcheck concerns.

### TSVC-M01 Compile Coverage

Goal:
- compile-only TSVC strict coverage remains explicit and green as a PR-tier contract.

Done means:
- compile-only strict coverage threshold passes
- no stale runtime result is misreported as compile-only closure

### TSVC-M02 Runtime Entry

Goal:
- TSVC reaches guest-visible runtime progress and benchmark output generation on the runtime lane.

Done means:
- firmwareless TSVC runner reaches output/specdiff-eligible state

### AVS-M01 PR Closure

Goal:
- required PR-tier AVS matrix closure is stable and current.

Done means:
- required IDs pass with current evidence pack

### AVS-M02 Nightly Breadth

Goal:
- nightly-only AVS breadth expands without regressing PR-tier closure.

Done means:
- remaining nightly IDs have current execution evidence and no stale carryover blockers

### PRIV-M01 Privileged / MMU / Debug Parity

Goal:
- privileged, MMU, and debug surfaces stop being undefined future work and become executable parity gates.

Done means:
- selftests or equivalent targeted gates exist and run

### REL-M01 Strict Closure

Goal:
- `strict_cross_repo.sh` and the canonical convergence wrapper fail only on current blockers and eventually turn green without stale waivers.

Done means:
- strict closure points at the current first real blocker
- once green, the convergence report is refreshed canonically

### REL-M02 Promotion And Release Readiness

Goal:
- workload/runtime breadth, nightly evidence, and performance discipline are good enough for promotion.

Done means:
- required runtime/workload lanes are green
- promotion artifacts are reproducible
- release-grade parity work is no longer blocked by missing foundational runtime closure

## Current Active Phase

As of 2026-05-21, the active governance phase should be treated as:

- `LINUX-RUNTIME`

Reason:
- core compile/runtime baselines are largely green enough that the current first
  unresolved blockers are firmwareless Linux userspace entry and downstream
  workload runtime closure.
