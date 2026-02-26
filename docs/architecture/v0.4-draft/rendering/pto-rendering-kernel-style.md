# v0.4 draft: Rendering PTO kernel writing style (recommended)

This is a practical coding style guide for writing rendering-related kernels in `workloads/pto_kernels`.

## 1) Keep the same conventions as existing PTO kernels
- Use `Tile<Location::Vec, T, 32, 32, ...>` and enforce `tile_bytes == 4096`.
- Use `global_tensor<T, RowMajor<H,W>>` + `global_iterator<...>` for linear buffers.
- Prefer SoA: one tile per channel.

Example pattern (from `add_custom.cpp`):
- create iterators
- nested loops over tile rows/cols
- `TLOAD` tiles → do ops → `TSTORE`

## 2) Rendering kernel signatures
Stage kernels should take:
- pointers to global buffers (vertex buffers, index buffers, attachments)
- pointers to descriptor/state tables (via `.brg` pointers in `ri*` when lowered to Linx)
- optional scratch pointers

In the early software-first phase, CPU/BCC can marshal these pointers.

## 3) Shading kernels (VEC) vs hardened ops (TAU)
- VEC kernels: implement shading/compute and serve as fallback.
- TAU PTOs:
  - TEPL/TileOp10 for stable primitives
  - TAU micro-kernels for complex units
  - **tile→tile only** (no direct `.brg`), by current v0.4 direction

## 4) What to avoid early
- Don’t bind tile meaning to a single rendering pipeline (tile-based only).
- Don’t overfit to a single pixel format; keep pack/unpack explicit.
- Don’t introduce hidden global memory effects inside TAU PTOs.
