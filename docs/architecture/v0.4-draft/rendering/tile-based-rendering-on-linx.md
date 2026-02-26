# v0.4 draft: Tile-based rendering on Linx (open design)

## Decision
- Prefer **tile-based rendering** overall.
- Caveat: Linx “tile” (tile registers, TA/TB/TO/TS bases, TLOAD/TSTORE, etc.) may not map 1:1 onto conventional TBDR tiles.

## What we must define (Linx-specific)
1) **What is a tile?**
   - Is a tile primarily a *working-set region* for color/depth/stencil?
   - Or a generic accelerator-local scratchpad (not necessarily screen tiles)?

2) **Tile size(s) and shapes**
   - Screen-space tile sizes (e.g. 8x8, 16x16, 32x32 pixels)?
   - Relationship to tile register sizes (512B..4KB) and data formats.

3) **Where does binning live?**
   - software binning in MPAR kernels?
   - later: harden a binning/tiler engine?

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

