# TileInfo

Tile Information Register (TileInfo) is a hardware-maintained **banked SSR family**, with one independent TileInfo instance per Tile register, recording that Tile's metadata snapshot.

TileInfo is **not software-visible** — software cannot read or write it via SSRGET/SSRSET instructions. Its lifecycle is fully managed by hardware:

- **Write**: When a block instruction outputs data to a Tile register via [B.IOT](../../header/B.IOT.md), hardware automatically writes the relevant parameters (dimensions, data type, layout, capacity, etc.) into that Tile's corresponding TileInfo.
- **Read**: When a subsequent block instruction uses that Tile as input, hardware retrieves metadata from the corresponding TileInfo, eliminating the need for software to redundantly describe input Tile parameters in the instruction.

## Register Bit Fields

Each TileInfo instance is 64-bit, with the following bit fields:

| Field | Width | Description |
|-------|-------|-------------|
| `vld` | 1 | Tile allocation/valid flag. `0` = invalid (unallocated or freed), `1` = allocated/valid. |
| `p` | 1 | PredicateTile flag. `0` = normal tile, `1` = predicate tile. |
| `Layout` | 3 | Data storage layout (fractal) type. See table below for encoding. |
| `DataType` | 6 | Element data type. Same encoding as the DataType field in [BSTART](../../header/BSTART.md). |
| `size` | 4 | Tile capacity encoding. Same encoding as the destination register capacity in [B.IOT](../../header/B.IOT.md). |
| — | 1 | Reserved. |
| `validCol` | 16 | Valid column count of the Tile. `validCol ≤ Col`. |
| `validRow` | 16 | Valid row count of the Tile. `validRow ≤ Row`, where `Row = TileSize / (Col × sizeof(DataType))`. |
| `Col` | 16 | Total column count of the Tile (including padding columns). |

## Layout Encoding

| Layout | Fractal | Description |
|--------|---------|-------------|
| 0 | ND | Row-Major |
| 1 | Zz | Big-Z little-z |
| 2 | Zn | Big-Z little-n |
| 3 | DN | Col-Major |
| 4 | Nz | Big-N little-Z |
| 5 | Nn | Big-N little-N |
| 6~7 | — | Reserved |

## Design Rationale

TileInfo is not a single 64-bit SSR, but rather a **banked SSR family** indexed by Tile number. Each of the 64 Tile registers has an independent TileInfo instance — the complete metadata for all 64 Tiles cannot fit into a single narrow register.

The introduction of TileInfo simplifies the LB parameter semantics of TileOp instructions: input Tile dimensions, data type, and layout are automatically obtained by hardware from TileInfo, so instructions only need to describe **output Tile** parameters via LB.

## Notes

TileInfo is a hardware-internal register. **No SSRID is assigned; software cannot access it.** Tile metadata is automatically maintained by hardware when B.IOT allocates/writes a Tile.
