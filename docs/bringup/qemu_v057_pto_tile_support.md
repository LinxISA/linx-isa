# QEMU v0.57 PTO Tile execution status

This page records the LinxISA superproject evidence for the v0.57 PTO Tile
execution work in `emulator/qemu`. It supports the QEMU subtask tracked by
[LinxISA/SuperScalarModel#31](https://github.com/LinxISA/SuperScalarModel/issues/31).

The authoritative operation identities and selectors come from
`isa/v0.57/state/pto_encoding_map.json`. Detailed execution semantics were
cross-checked against the DavinciOO intrinsic workbook and operation pages,
with `pto-isa/docs/isa/tile/` as a secondary reference.

## Status summary

| Family | v0.57 workbook operations | QEMU execution paths | Remaining fail-closed |
| --- | ---: | ---: | ---: |
| TMA | 6 | 6 | 0 |
| CUBE | 8 | 4 | 4 |
| TEPL | 97 | 82 | 15 |
| Total | 111 | 92 | 19 |

An execution path means QEMU performs a defined operation on Tile, ACC, or
memory state. It does not imply that every dtype, layout, shape, rounding mode,
exception, or target-specific profile is complete. Unsupported tuples and
selectors are rejected instead of passing through a write-zero fallback.

The QEMU-local operation list and profile limits are documented in
`emulator/qemu/docs/linxisa/pto-v057-tile-support.md`.

## Implemented groups

TMA has execution paths for:

```text
TLOAD TSTORE TMOV TPREFETCH MGATHER MSCATTER
```

CUBE has execution paths for:

```text
TMATMUL TMATMUL_ACC TGEMV TGEMV_ACC
```

TEPL has 82 executable selectors covering:

- base and scalar elementwise arithmetic and logic;
- packed comparison and selection;
- row/column sum, min, max, product, argmin, and argmax;
- row/column expand and expanded binary operations;
- transpose, reshape, gather/scatter, concat, gather-by-byte, and extraction;
- sequence and triangular generation, fill padding, and dequantization;
- partial add, multiply, minimum, and maximum.

Important implemented profiles include row-packed U32 predicates for
`TCMP/TCMPS`, matching consumption by `TSEL/TSELS`; persistent rectangular
Tile shape metadata; and S8/S16 dequantization with per-row FP32 scale and
offset:

```text
dst[r,c] = (src[r,c] - offset[r]) * scale[r]
```

## Deliberately unsupported operations

The remaining CUBE operations are `TMATMUL_BIAS`, `TGEMV_BIAS`, `TMATMUL_MX`,
and `TGEMV_MX`. Their extra bias/scale Tile roles and mixed-precision
reconstruction profiles are not represented by the current QEMU collector.

The remaining TEPL operations are:

```text
TAXPY TQUANT TINSERT TIMG2COL TDEINTERLEAVE TINTERLEAVE
TSORT TMRGSORT THISTOGRAM TPARTARGMAX TPARTARGMIN
TPUSH TPOP TALLOC TFREE
```

They remain fail-closed for concrete contract reasons:

- `TAXPY` and `TINSERT` require an existing destination to be read and
  preserved, while the current TEPL output is a fresh allocation.
- `TQUANT` has distinct INT8, MXFP8, and MXFP4 metadata, output, and packing
  profiles that the current header/collector cannot uniquely bind.
- `TDEINTERLEAVE`, `TINTERLEAVE`, `TSORT`, `TPARTARGMAX`, and `TPARTARGMIN`
  require compound or multiple outputs.
- `TIMG2COL`, `TMRGSORT`, and `THISTOGRAM` lack a closed configuration,
  variable-operand, or attribute contract in the current decoder path.
- `TPUSH`, `TPOP`, `TALLOC`, and `TFREE` require a Pipe/control ABI rather than
  an ordinary TEPL numeric operation.

`TQUANT` selector `0x083` is therefore decoded but rejected by the executable
selector gate before the destination is modified. QEMU does not guess one
quantization formula and report it as general v0.57 support.

## AVS organization

Tests are separated by PTO family:

| Family | Sources |
| --- | --- |
| TMA | `avs/qemu/tests/10_tile_tma.cpp` |
| CUBE | `avs/qemu/tests/10_tile_cube.cpp`, `10_tile_cube_gemv.S` |
| TEPL | `avs/qemu/tests/10_tile_tepl.cpp`, `10_tile_tepl_*.S` |
| Cross-family | `avs/qemu/tests/10_tile_integration.cpp` |

Recent exact-value evidence includes:

| AVS ID | Coverage |
| --- | --- |
| `0x000A0013` | TCMP packed predicates and compare modes |
| `0x000A0015` | signed S8/S16 lanes |
| `0x000A0016` | FP16/BF16 raw-bit arithmetic |
| `0x000A0017` | persistent rectangular Tile shape |
| `0x000A001D` | row/column expanded binary operations |
| `0x000A001E` | TFILLPAD Zero/Max/Min |
| `0x000A001F` | partial binary operations |
| `0x000A0020` | reshape, concat, and gather-by-byte |
| `0x000A0021` | TCI and TTRI |
| `0x000A0022` | plain TEXTRACT |
| `0x000A0023` | S8/S16 to FP32 TDEQUANT |
| `0x000A0024` | S32 TGEMV and TGEMV_ACC |

The focused regression command is:

```bash
QEMU=$PWD/emulator/qemu/build/qemu-system-linx64 \
  python3 avs/qemu/run_tests.py --suite tile --timeout 40
```

At this snapshot, the QEMU incremental build, focused Tile suite, and
`tools/isa/check_pto_v057_manifest.py` pass. The full `--all` run still has an
unrelated known liveness blocker at DeepSeek test `0x00001702`, so focused Tile
success must not be reported as a complete AVS pass.

The illegal-instruction expected-trap harness is also not a stable negative L3
oracle on this baseline: it may re-enter the test entry rather than return to
the continuation. Unsupported selectors are implemented as fail-closed, but
negative runtime evidence remains pending that harness repair.

## Cross-model handoff

This change closes the QEMU implementation and reference-result side of issue
#31 for the defined subset. The next repository-level work is:

1. implement the same defined selector/profile subset in `gfrun`;
2. run the same ELF/input data through QEMU and gfrun and compare result memory;
3. use the resulting gfrun behavior as one side of the gfrun/gfsim regression;
4. retain the 19 fail-closed operations in the report until their ISA-visible
   operand and profile contracts are closed.
