# v0.4 draft: Rendering state conventions (BCC config + StateTiles)

Decision (current direction):
- Small/rarely-changing state: configured by **BCC** via descriptors (`B.ARG`, possibly `B.IOR` pointers for VEC).
- Large or frequently-referenced state: placed into **tile registers** as dedicated **StateTiles**.

Rationale:
- Keeps hot-path state in tile regs for TAU ops (TAU is tile→tile only; no `.brg`).
- Keeps the command stream compact for small constants.

## Examples

### Small state (BCC-configured)
- blend enable flags
- depth/stencil compare func enums
- write masks
- small scalar constants (e.g., clear color)

### Large/hot state (StateTiles)
- descriptor tables (already materialized into tile form)
- LUTs (gamma/sRGB, etc.)
- per-draw constant buffers that are reused heavily within a pass

## Open items
- Define canonical packing for a `RenderStateTile` (fields + offsets).
- Define which state is duplicated per draw vs per pipeline vs per renderpass.
- How BCC manages lifetime/renaming of StateTiles across blocks.
