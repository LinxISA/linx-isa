# Rendering and Vulkan Bring-up

This document defines the live bring-up plan for rendering-capable userspace on
canonical `v0.56` systems.

The initial goal is not immediate hardware acceleration. The first closure
target is a reproducible software-backed graphics and Vulkan stack running under
the Linx QEMU environment, with explicit gates that can later be replaced or
supplemented by LinxGPGPU-backed execution.

## Scope

- emulator-first rendering bring-up,
- Mesa-based userspace stack assembly,
- headless validation before presentation-path work,
- software-backed OpenGL and Vulkan baselines,
- later handoff from software backends to Linx kernel execution.

This page is normative for rendering bring-up ordering and stage criteria. It
does not freeze final hardware acceleration architecture.

## Current Policy

- Start with software backends before hardware acceleration.
- Prefer host-side cross-builds of Mesa and related userspace artifacts.
- Use a deterministic install prefix inside the target rootfs: `/opt/mesa`.
- Bring up headless and offscreen paths before X11, Wayland, or DRM scanout.
- Use software rendering as a correctness scaffold, not as the end-state
  graphics implementation.

## Mesa Software Scaffolding Policy

Mesa software backends are the canonical early rendering scaffold for `v0.56`
bring-up under QEMU.

Their purpose is to:

- validate that Linx Linux, libc, the loader, and userspace runtime can host a
  real rendering stack,
- validate userspace packaging, driver discovery, and WSI or headless plumbing
  before Linx-specific acceleration is introduced,
- produce repeatable rendering traces and workload-characterization evidence
  before hardening choices are made.

This scaffold is a bring-up baseline and reference path. It is not the intended
final acceleration architecture.

### Backend Roles

- `softpipe` is the preferred first OpenGL backend because it has the simplest
  dependency path and the lowest bring-up complexity.
- `llvmpipe` is the preferred higher-feature software reference backend once
  the LLVM dependency path is stable inside the bring-up environment.
- `lavapipe` is the first required Vulkan backend for headless Vulkan closure.

The backend progression is therefore:

1. `softpipe` for first OpenGL/offscreen correctness.
2. `llvmpipe` for higher-feature software reference and shader-behavior
   comparison where needed.
3. `lavapipe` for Vulkan device and headless workload closure.
4. selective replacement of software execution paths with Linx-executed shader
   or kernel paths while preserving the same validation signals.

## Backend Sequence

Rendering userspace is brought up in this order:

1. Mesa build and runtime integration.
2. OpenGL offscreen validation using `softpipe`.
3. Vulkan device validation using `lavapipe`.
4. Optional presentation-path validation such as `vkcube` or equivalent.
5. Replacement of selected software execution paths with Linx shader-kernel
   execution while preserving the same correctness gates.

`llvmpipe` is a valid supplemental reference backend once the LLVM dependency
path is stable, but it is not the first hard gate.

## Stage Gates

### Stage Zero: Platform Sanity

Goal:

- the emulator boots Linux userspace reliably enough to host dynamic rendering
  binaries.

Required checks:

- `uname -a` runs,
- the dynamic loader and libc operate correctly,
- at least one scripting or shell environment is usable,
- the rootfs has space for Mesa libraries, helper tools, and validation
  binaries.

Required artifacts:

- reproducible emulator launch parameters,
- reproducible rootfs/sysroot reference,
- recorded toolchain provenance for the Mesa build used by the run.

### Stage One: Mesa Build Integration

Goal:

- Mesa builds for Linx and installs into the target prefix used by QEMU runs.

Required policy:

- use Meson and Ninja unless replaced by an explicitly documented equivalent,
- prefer host-side cross compilation,
- stage the install into `/opt/mesa` within the target filesystem view.

Required checks:

- the required Mesa libraries are present under the target prefix,
- the runtime loader can discover and load those libraries under QEMU,
- headless context creation dependencies are present for the chosen software
  backend.

### Stage Two: OpenGL Offscreen First Pixels

Goal:

- a minimal OpenGL program renders offscreen in the emulator and produces a
  deterministic result.

Recommended shape:

- use EGL surfaceless or pbuffer execution first,
- render a trivial triangle or quad,
- read back the rendered image or checksum it.

Required checks:

- the program exits successfully,
- the output image or checksum is deterministic across repeated runs of the
  same artifact set,
- the validation result is machine-readable.

`softpipe` is the preferred first backend for this stage because it minimizes
dependency complexity.

### Stage Two-B: Software Reference Characterization

Goal:

- capture workload-shape evidence from a live rendering stack before Linx
  execution replacement or hardening decisions.

Required policy:

- keep `softpipe` as the minimal correctness reference,
- use `llvmpipe` as an optional higher-feature software reference once the LLVM
  path is stable,
- keep characterization runs headless where possible so results stay
  reproducible in the emulator.

Recommended workload classes:

- minimal OpenGL micro-scenes,
- shader-heavy scenes,
- texture-heavy scenes,
- simple benchmark-style scenes comparable to `glmark2` or `vkmark` subsets.

Required outputs:

- machine-readable pass or fail summaries,
- captured backend identity and configuration,
- deterministic image or checksum results for the selected scenes,
- workload-characterization metrics recorded with each run.

### Stage Three: Vulkan First Device

Goal:

- Vulkan userspace runs under QEMU with a software ICD and passes a minimal
  headless validation path.

Required backend:

- Mesa `lavapipe` is the baseline software Vulkan implementation for this
  stage.

Required checks:

- `vulkaninfo` runs and enumerates a device,
- a minimal headless Vulkan sample creates an instance and device,
- the sample executes at least one compute or graphics workload,
- results are copied back and validated through deterministic correctness
  checks.

This stage closes the first “Vulkan runs under emulator” milestone.

### Stage Four: Optional Presentation Path

Goal:

- presentation-capable rendering paths run once the headless baseline is
  stable.

Examples:

- `vkcube`,
- a minimal present demo,
- equivalent Wayland, X11, or DRM validation programs.

This stage is optional for early closure and must not block headless Vulkan
bring-up.

### Stage Five: Linx Execution Replacement

Goal:

- start replacing software execution paths with Linx shader-kernel execution
  while preserving the same user-visible correctness checks.

Required policy:

- keep software backends available as reference paths during bring-up,
- compare Linx-executed paths against software-backed outputs,
- do not drop the software baseline until the replacement path is validated on
  the same workloads.

Examples of later replacement work:

- compile selected shaders into `MPAR` kernels,
- route kernel launches through the canonical rendering command contract,
- preserve image or checksum-based validation from earlier stages.

## Measurement Requirements

Collect these metrics from the first working rendering runs onward:

- shader count and approximate size,
- shader categories such as vertex, fragment, compute, or equivalent pipeline
  stage proxies where available,
- compiler or IR instruction-mix proxies where available,
- bytes read and written per workload when measurable,
- texture sample counts and dominant formats once textured scenes are running,
- depth, stencil, and blend usage when the scene exercises those paths,
- backend identity and configuration for every captured result.

These metrics are required to support later hardening decisions and workload
selection.

## Non-goals for Early Closure

These are intentionally deferred:

- presentation-stack completeness,
- high-performance graphics,
- final Linx Vulkan driver architecture,
- fixed-function hardening decisions,
- full OpenGL conformance.

## Relationship to Other Canonical Pages

- Architectural submission ownership is defined in
  `docs/architecture/v0.56-rendering-command-contract.md`.
- Shader-kernel semantics remain defined by the ISA contract, manual, and
  `isa/v0.56/state/` canonical state files.
- Workload and gate closure status remain tracked through AVS and the bring-up
  status pages.
