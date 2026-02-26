# v0.4 draft: LinxGPGPU core architecture (render-first)

This document is the working architectural spec for a **GPU-SM-like core** (“LinxGPGPU core”), scaling out to many cores to form a GPGPU suitable for rendering + compute.

## 1) System philosophy
- **Limited hardening**: only high-ROI units become fixed-function engines.
- **VEC/SIMT kernel fallback**: everything must be runnable as MPAR kernels.
- **BCC scheduling + heterogeneous blocks**: the machine is a composition of blocks targeting different engines, with out-of-order execution allowed but retired/visible under LinxCore’s block/BID rules.

## 2) Execution model (kernel body)
### 2.1 Group/warp
- One group ≈ NVIDIA warp.
- Group composition:
  - 64 vector lanes
  - 1 scalar-uniform lane (controls group-level control flow)
- `p` is the **EXEC mask** (64-bit).

### 2.2 Control flow in kernel body
- Kernel body is a normal instruction stream (branches/loops allowed).
- Control-flow instructions update body-local `TPC` and are evaluated at **group granularity** using the scalar-uniform lane.
- Kernel terminates on the first terminator marker (`BSTOP/C.BSTOP` or any `BSTART.*`).

### 2.3 EXEC mask rules
- Vector instructions are implicitly predicated by `p` (lane active iff `p[lane]==1`).
- `V.CMP.* ->p` is used to generate masks.
  - Inactive lanes during `V.CMP.* ->p` produce 0 bits.

## 3) Unified 64-bit kernel encoding and l/v derivation
Design direction:
- Kernel-body instructions use a **unified 64-bit encoding space**.
- `l.*` vs `v.*` is **derived from register-class usage** (no dedicated mode bit).
  - Any-operand rule: if any operand references per-lane regs (`vt/vu/vm/vn`), treat as `v.*`.
  - Otherwise treat as `l.*`.
- Mixed-class semantics (initial): scalar/group-domain src operands (`t/u/ri/p/TA/TB/TO/TS/...`) are **broadcast** to all active lanes when executing `v.*`.
- `v.*` writing scalar/group-domain destinations is not allowed; use explicit reductions (`V.RD*`) or other explicit cross-lane ops.

## 4) Global memory access inside kernels
- Kernel global memory accesses go through the **bridged path** (`*.brg`).
  - vector lanes: `v.*.brg`
  - scalar lane (uniform): `l.*.brg`
- Normal BCC scalar memory issue is closed while in MCALL-like MPAR/MSEQ mode; `l.*.brg` is treated as part of the bridged/MTC-like domain.

## 5) Hardware partitioning (core + engines)
### 5.1 Per-core units (SM-like)
- Wave/group scheduler: issues 64-lane groups.
- Scalar lane pipeline (control + address + mask ops).
- Vector ALU pipelines for per-lane ops.
- `.brg` memory interface + coalescing.
- Tile/local storage interfaces (`TA/TB/TO/TS` + tile regs) for tile-oriented stages.

### 5.2 Chip-level engines (limited hardening, optional)
- CP / submission engine (block command ingestion).
- DMA/BLT/Clear engine.
- Optional future engines: texture/sampler, raster/tiler/binning, ROP.

## 6) Open items to decide next
- Rendering pipeline style: **tile-based preferred** (note: Linx tile semantics may differ from conventional TBDR; we must specify the exact meaning of a “tile” in Linx terms).
- Vulkan command buffer mapping: **BCC-led expansion** (command buffers are lowered/expanded into Linx blocks by BCC/runtime rather than a heavy on-GPU CP parser).
- Memory/cache/coherence policy for `.brg` vs CPU.
