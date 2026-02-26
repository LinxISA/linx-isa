# v0.4 draft: LinxGPGPU core architecture (render-first)

This document is the working architectural spec for a **GPU-SM-like core** (“LinxGPGPU core”), scaling out to many cores to form a GPGPU suitable for rendering + compute.

## 1) System philosophy
- **CPU (BCC) + Shader Core** as the primary composition model:
  - CPU/BCC performs command lowering, orchestration, and software fallbacks.
  - Shader core runs kernels (MPAR) for the parallel parts.
- **Limited hardening**: only high-ROI units become fixed-function engines.
- **VEC/SIMT kernel fallback**: everything must be runnable as MPAR kernels.
- **Heterogeneous blocks + out-of-order**: the machine is a composition of blocks targeting different engines, allowed to run out-of-order, but retiring/visibility is managed by LinxCore block/BID rules.
- **Tile is general intermediate state storage** for cross-engine communication; rendering may be tile-based *or* immediate-mode.

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

### 5.1 Core roles
- **VEC (shader core)**: runs MPAR kernels for compute shading and serves as the **fallback path** for any feature not supported by hardening.
- **TAU (tile arithmetic unit)**: is the primary substrate for **hardening** “shader-like” operations and other accelerators.
  - TAU/accelerators communicate via **tile registers** (general intermediate state storage).
  - Hardening should be expressed as TAU-facing operations so state handoff stays in tiles.

### 5.2 Engine set (current LinxCore decomposition)
- BCC + block fabric dispatch to engines by block type.
- Engines include: **TMA**, **CUBE**, **VEC**, **TAU** (plus DMA/clear as needed).

### 5.3 State handoff
- The primary inter-engine handoff medium is the **tile register file**.
- BCC orchestrates pipelines by issuing heterogeneous blocks whose inputs/outputs are tiles.

## 6) Open items to decide next
- Rendering pipeline modes: support both **immediate-mode (desktop-style)** and **tile-based** approaches.
  - Linx “tile” remains **general-purpose intermediate state storage**; screen-space tiling is an optional strategy.
- What work is on **CPU/BCC** vs **shader core** in each pipeline mode (stage-by-stage split).
- If/when we introduce binning: stage-1 binning can be built by **BCC scalar-block software logic**; later migrate to MPAR kernels / hardened binner if ROI proves out.
- Vulkan command buffer mapping: **BCC-led expansion** (command buffers are lowered/expanded into Linx blocks by BCC/runtime rather than a heavy on-GPU CP parser).
- Memory/cache/coherence policy for `.brg` vs CPU.
