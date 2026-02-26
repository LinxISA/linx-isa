# v0.4 draft: TAU as the hardening substrate (render-first)

## Decision direction
- **VEC** is the general-purpose kernel engine (compute shading + fallback).
- **TAU (Tile Arithmetic Unit)** is the primary target for *limited hardening*:
  - hardened shader-like operations
  - accelerator kernels that are common and ROI-positive

## Key contract: tile registers as the handoff medium
- Intermediate state passed between heterogeneous engines/blocks is stored in **tile registers**.
- TAU operations should consume/produce tiles, enabling:
  - cheap handoff (no round-trip to `.brg` unless needed)
  - clear dependency tracking via tile descriptors

## Relationship to ISA block types
- In v0.3, tile-oriented template ops are staged under `BSTART.TEPL` and conceptually map to TAU execution.
- In v0.4, we extend this idea to rendering:
  - represent hardened shader fragments as TAU-executable ops (likely TEPL-like) with well-defined tile IO.
  - keep a strict fallback path: if a shader cannot be matched/lowered, compile it to VEC MPAR kernels.

## What we still need to decide
1) **Offload granularity**
   - whole shader stage to TAU?
   - or partial offload: replace subgraphs/regions with TAU ops and run the rest on VEC?

2) **TAU op programming model** (chosen direction)
   - **Hybrid**:
     - common, stable PTOs are **header-only TEPL-like ops** (TileOp10 space)
     - complex/evolving units can use a **TAU micro-kernel** model

3) **Tile payload layout for rendering**
   - how pixels/fragments/attributes are packed into tile registers
   - how many channels and formats are supported in the first profile

4) Memory interactions
   - which ops may touch `.brg` directly (if any)
   - or require explicit TMA/DMA steps

