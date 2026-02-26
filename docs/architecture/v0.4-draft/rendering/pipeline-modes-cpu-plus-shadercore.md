# v0.4 draft: Rendering pipeline modes (CPU + Shader Core)

## Goal
Support both:
- **desktop / immediate-mode** rendering pipelines
- **tile-based** rendering pipelines

The architectural direction is **CPU (BCC) + shader core** composition:
- CPU/BCC builds and schedules work (command buffer lowering, binning/raster tasks, software fallbacks).
- Shader core runs MPAR kernels for parallel stages (shading/compute and selected raster stages if desired).

## Common building blocks
- **Tiles**: general-purpose intermediate state storage for cross-engine communication and shared working sets.
- **`.brg`**: bridged global memory accesses for both scalar-uniform (`l.*.brg`) and vector-lane (`v.*.brg`).
- **Blocks**: heterogeneous blocks can target shader core kernels, DMA/clear, and future hardened engines.

## Mode A: Immediate-mode (desktop style)
Concept:
- Process primitives in submission order (or reordered batches).
- Typical stages (software or kernels):
  - command expansion + state setup (CPU/BCC)
  - vertex shading (shader core)
  - primitive assembly + rasterization (CPU/BCC first; later kernels/engine)
  - fragment shading (shader core)
  - depth/stencil/blend/writeback (CPU/BCC first; later engine)

Benefits:
- simpler mental model; aligns with many desktop workloads.

Risks:
- bandwidth pressure (frequent `.brg` traffic)
- software raster/ROP may dominate until hardened.

## Mode B: Tile-based
Concept:
- Build tile lists, process one tile’s working set largely in local tile storage, then write back.

Staging:
- Start with CPU/BCC software binning/raster scaffolding.
- Gradually move hot loops to kernels or hardened engines.

## Open question (to be decided next)
- In the first accelerated prototype beyond pure software, what is the **minimum shader-core responsibility**?
  - shading only (VS/FS/CS)
  - shading + some rasterization
  - shading + ROP-like ops
