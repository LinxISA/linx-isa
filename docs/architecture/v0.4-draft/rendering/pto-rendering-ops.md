# v0.4 draft: PTO (Parallel Tile Ops) for rendering

## Context / goal
We want the full rendering pipeline to be decomposable into small, composable **PTO** units.

Architecture direction:
- **VEC**: compute shading + fallback for anything not hardened.
- **TAU**: the primary hardening substrate.
- **Tile registers**: the universal intermediate-state storage used for state handoff between heterogeneous engines/blocks.
- **BCC/CPU**: builds the pipeline in software first (command lowering, scaffolding), then we selectively replace hot regions with TAU PTOs.

This document proposes a rendering-oriented PTO catalog (names + signatures + staging plan). It is a *planning* doc, not a frozen spec.

---

## 0) PTO design rules (so it composes)

1) **Tile-in / tile-out, minimal side effects**
- A PTO consumes 0–N input tiles and produces 0–M output tiles.
- Avoid hidden global memory side effects; if needed, make memory actions explicit via TMA/DMA blocks.

2) **Explicit parameters via descriptors**
- Small constants/state via `B.ARG`.
- Larger state tables via `B.IOR` pointers (`ri*`) referencing `.brg` memory (for example descriptor tables, LUTs).

3) **I/O arity stays small**
- Prefer ops with <=3 input tiles and 1 output tile (aligns with strict-v0.3 header constraints).
- If more are needed, compose ops (or define v0.4 header extension later).

4) **Fallback equivalence**
- Every PTO should have a reference implementation as a **VEC MPAR kernel** (functional equivalence gate).

---

## 1) Common tile payload conventions (rendering)

We treat tiles as generic storage; rendering defines *conventions* for what a tile contains.

Recommended early conventions (simple and composable):
- **Color tile**: RGBA vectors for a micro-batch of fragments/pixels (exact packing TBD).
- **Depth tile**: depth values for the same micro-batch.
- **Stencil/coverage tile**: 8-bit stencil and/or 1-bit coverage mask packed in a tile.
- **Attribute tiles**: varyings/intermediate values (N tiles as needed).

Important: the “micro-batch” does not have to be a screen-space tile; it can be any batch chosen by BCC.

---

## 2) PTO families for rendering

### A) Tile utility & packing (high ROI, low risk)
These are foundational and likely needed regardless of pipeline mode.

- **PTO.TCLEAR**: fill a tile with a constant pattern (zero, one, imm32, imm64).
  - in: none or optional mask tile
  - out: one tile
  - params: fill value, element type, stride/packing mode

- **PTO.TPACK / PTO.TUNPACK**: convert between tile internal layout and a canonical vector layout.
  - in: one tile
  - out: one tile
  - params: packing mode (RGBA8, RGBA16F, R11G11B10F, etc.)

- **PTO.TCVT**: datatype conversion (F16↔F32, UNORM↔F32, sRGB encode/decode as separate ops).
  - in: one tile
  - out: one tile
  - params: conversion mode, rounding/sat

- **PTO.TSWZ**: channel swizzle / replicate / mask.
  - in: one tile
  - out: one tile
  - params: swizzle map, write mask

### B) Fragment/ROP-like ops (prime hardening candidates)
These capture operations that are ubiquitous in desktop rendering.

- **PTO.DEPTH_TEST**: compare depth vs existing depth, produce pass mask and optional updated depth.
  - in: depth_in, depth_buf (and optional stencil)
  - out: pass_mask, depth_out (optional)
  - params: func (LESS/LEQUAL/…), write_enable

- **PTO.STENCIL_TEST_OP**: stencil compare + update (separate from depth initially).
  - in: stencil_in, stencil_buf, pass_mask(optional)
  - out: stencil_out, new_pass_mask
  - params: func, ref, read_mask, write_mask, ops (fail/zfail/zpass)

- **PTO.BLEND**: blend src color with dst color under a mask.
  - in: src_color, dst_color, pass_mask
  - out: out_color
  - params: blend factors, blend ops, color write mask

- **PTO.LOGIC_OP** (optional): bitwise logic blend.
  - in: src_color, dst_color
  - out: out_color
  - params: op (AND/OR/XOR/...)

### C) Interpolation & derivatives (shader support helpers)
- **PTO.INTERP_LINEAR**: barycentric interpolation for varyings.
  - in: v0, v1, v2, bary_coords (or edge eqs)
  - out: varying_tile
  - params: perspective/linear mode

- **PTO.DERIV_QUAD**: compute dFdx/dFdy-like derivatives on a quad layout.
  - in: value_tile
  - out: ddx_tile, ddy_tile
  - params: quad layout policy

### D) Texture sampling (later; depends on memory + cache policy)
Texture is expensive but high ROI. We stage it later because it pulls in memory hierarchy and format tables.

- **PTO.TEX2D_SAMPLE** (staged): sample a 2D texture for a batch of coordinates.
  - in: uv_tile, lod_tile(optional)
  - out: texel_tile
  - params: filter mode, address mode
  - resources: descriptors via `B.IOR` pointer(s) to `.brg` tables (image/sampler state)

Note: even if texture is ultimately a hardened engine, PTO is a good *programming surface*.

### E) Rasterization setup (CPU-first; optional TAU later)
Given the current direction (software first), these start on CPU/BCC and move later.

- **PTO.TRI_SETUP**: edge equations / barycentric setup.
- **PTO.COVERAGE**: coverage mask generation.

---

## 3) MVP recommendation (what to harden first)
If we want a small set that unlocks big wins while keeping the rest on VEC fallback:

**Tier-0 (plumbing):**
- TCLEAR, TPACK/TUNPACK, TCVT, TSWZ

**Tier-1 (desktop must-have):**
- DEPTH_TEST (+ writeback)
- BLEND
- STENCIL_TEST_OP (if needed for target apps)

Texture can be Tier-2 unless your target apps are texture-dominated.

---

## 4) Open questions (to answer next)
1) What is the **first supported render path** we target in Vulkan terms?
   - simplest: single color attachment, optional depth, no MSAA
2) Which PTO arity constraints do we enforce in v0.4?
3) Tile payload packing for color/depth/mask: define one “canonical” packing for the first profile.
