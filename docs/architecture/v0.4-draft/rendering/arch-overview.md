# v0.4 draft: Rendering + AI on LinxGPGPU (arch overview)

This document will host the **rendering-driven** architectural requirements that may force ISA v0.4 changes.

## Goals
- Vulkan-first graphics + compute.
- Shaders/compute compile to Linx SIMT kernel bodies, executed on a multi-core LinxGPGPU.
- Group model: 64-lane vector + 1 scalar lane controlling group-level control flow.

## Topics to fill in
- Pipeline stages expressed as kernels vs hardened engines (raster/tex/ROP/etc).
- Memory model expectations for GPU workloads (queues, barriers, caches).
- Shader compiler contract (SPIR-V/NIR lowering strategy).

