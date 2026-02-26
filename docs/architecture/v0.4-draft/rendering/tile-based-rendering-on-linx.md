# v0.4 draft: Tile-based rendering on Linx (open design)

## Positioning
- Tile-based rendering is **one optional strategy** we want to support.
- We also want to support **desktop/immediate-mode** style rendering.
- Linx “tile” is **general-purpose intermediate state storage**; screen-space tiling is built on top of it when we choose the tile-based strategy.

Caveat:
- Linx “tile” (tile registers, TA/TB/TO/TS bases, TLOAD/TSTORE, etc.) may not map 1:1 onto conventional TBDR tiles.

## What we must define (Linx-specific)
1) **What is a tile?**

Chosen direction:
- A tile is **general-purpose intermediate state storage**: the shared medium for data exchange and state handoff across heterogeneous engines/blocks (shader kernels, DMA/clear, future texture/ROP/tiler engines, etc.).
- It is **not inherently a screen-space tile**; screen-space tiling is a higher-level rendering strategy built on top of this general tile storage.

2) **Tile size(s) and shapes**
   - Screen-space tile sizes (e.g. 8x8, 16x16, 32x32 pixels)?
   - Relationship to tile register sizes (512B..4KB) and data formats.

3) **Where does binning live?**

Chosen staging:
- First implementation uses **BCC / scalar-block software logic** to build tile lists/binning structures.
- Future: migrate hot paths to MPAR kernels and/or a hardened tiler/binner engine once measured.

4) **Pass structure mapping**
   - Vulkan renderpass/subpass boundaries → which blocks/engines?
   - When do we flush tile contents to global memory (`*.brg` stores)?

5) **MSAA / compression / depth formats**
   - staged bring-up: disable first
   - later: decide whether to harden ROP-like functionality

## Recommended staged approach
- First get Vulkan running (software baseline).
- Then implement a tile-based path that:
  - bins primitives to tiles in software
  - shades a tile in MPAR kernel using tile-local working set
  - resolves/writes out via `.brg`
- Only then decide what to harden.

