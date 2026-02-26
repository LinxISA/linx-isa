# v0.4 draft: Rendering tile conventions for PTO kernels (layout + data structures)

This document defines **initial** rendering-oriented conventions on top of the existing PTO tile type system.

Principle: **tile is generic storage** (4KB `RawTile` carrier). Rendering defines *conventions* that can evolve.

## 0) What we learned from `workloads/pto_kernels`
- A tile is ultimately a **4KB `RawTile`** carrier. On Linx backend it is opaque (vector_size(4096)).
- The `pto::Tile<Location, DType, Rows, Cols, ...>` template adds **compile-time metadata** (dtype, dims, layout).
- Current kernels often enforce the convention: `Rows*Cols*sizeof(DType) == 4096`.

Sources:
- `workloads/pto_kernels/include/pto/linx/impl/backend.hpp` (RawTile)
- `workloads/pto_kernels/kernels/add_custom.cpp` (4KB tile convention)

## 1) Canonical rendering tile profile (initial)

We pick a simple, uniform initial profile aligned with the current rendering direction:

- **Tile element grid:** `1024 x 1 = 1024` elements (single-column)
- **Tile byte size:** `4096B`
- **Layout tag:** `RowMajor`

Rationale:
- Works for `float32` channels: `1024*4B = 4096B`
- Works for packed RGBA8 as `uint32_t` per pixel: `1024*4B = 4096B`
- Keeps the data structure **list-like** and avoids binding semantics to screen-space tiling.

## 2) Data structures (recommended SoA)

### 2.1 Fragment batch (SoA)
Represent a batch of fragments/pixels as **structure-of-arrays** tiles.

Recommended minimum set:
- `pos_x`, `pos_y`, `pos_z`, `pos_w` : `Tile<Vec, float, 32, 32>` (or fewer as needed)
- `coverage` / `mask` : `Tile<Vec, uint32_t, 32, 32>` (0/1 or bitfield convention TBD)
- `color_r/g/b/a` : `Tile<Vec, float, 32, 32>` for shader output in float

Optional:
- packed output color: `Tile<Vec, uint32_t, 32, 32>` where each element is `RGBA8` packed in u32.

### 2.2 Attachments
- Color attachment (linear) can be treated as a `global_tensor<uint32_t, RowMajor<H,W>>` for RGBA8.
- Depth attachment can be `global_tensor<uint32_t, RowMajor<H,W>>` for D24S8-like packed formats, or `float`/`uint32_t` depending on profile.

(We keep formats simple in the first profile; expand later.)

## 3) Rendering-specific layouts (format conventions)

We define format conventions as **packing in tile elements**, not as a fundamental tile type:

- `RGBA8_UNORM`: 1 pixel = 1 `uint32_t` (packed little-endian RGBA).
- `RGBA16F` / `RGBA32F`: stored as 4 separate float tiles (SoA) in the first version.
- `Depth32F`: 1 depth = 1 float element.

Future (later): add explicit pack/unpack PTOs for sRGB, R11G11B10F, D24S8, etc.

## 4) Indexing convention

Define `elem = row * kTileW + col`.

For the initial `1024x1` profile, this reduces to `elem = row`.

Open item: whether `(row,col)` should correspond to:
- a screen-space micro-tile, or
- an arbitrary fragment list produced by CPU/BCC.

We will pick one as the initial bring-up convention.
