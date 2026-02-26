# v0.4 draft: Rendering + AI on LinxGPGPU (arch overview)

This document will host the **rendering-driven** architectural requirements that may force ISA v0.4 changes.

## Goals
- Vulkan-first graphics + compute.
- Shaders/compute compile to Linx SIMT kernel bodies, executed on a multi-core LinxGPGPU.
- Group model: 64-lane vector + 1 scalar lane controlling group-level control flow.
- Default kernel launch form: `BSTART.MPAR`.
- Kernel global memory access: allowed via `*.brg` (bridged path).

## Topics to fill in
- Pipeline stages expressed as kernels vs hardened engines (raster/tex/ROP/etc).
- Memory model expectations for GPU workloads (queues, barriers, caches).
- Shader compiler contract (SPIR-V/NIR lowering strategy).

## Draft memory-mode rule for shader kernels (MCALL-like)

Carry forward the v0.3 staged memory-channel model into the v0.4 shader-kernel story:
- Treat `BSTART.MPAR/MSEQ` shader kernels as entering a **MCALL-like** mode.
- Entry boundary: acquire-style ordering before MTC-only execution begins.
- Exit boundary: release-style ordering before subsequent scalar blocks execute.
- While active: **BCC scalar memory issue is closed** (no normal scalar `load/store/atomic/fence`).
  - Global memory traffic is via the bridged path (`*.brg`):
    - vector lanes: `v.*.brg`
    - scalar lane (uniform): `l.*.brg` (v0.4 draft requirement / alias family)
- Non-speculative start: do not begin side-effecting execution until declared input dependencies (`B.IOT/B.IOTI`) are resolved.

