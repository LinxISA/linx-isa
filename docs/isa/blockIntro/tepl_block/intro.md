# TEPL encoding carrier

## Architectural role

TEPL is the unchanged Mode/Function encoding carrier for PTO Tile operations.
It is not an execution engine. Every legal TEPL selector is classified by the
v0.58 machine-readable catalog and is dispatched to exactly one of two engines:

| Engine | Role | Operation count |
|---|---|---:|
| **VEC** | Element-wise Tile/Tile and Tile/scalar computation | 35 |
| **SFU** | Complex functions, reductions/expands, rearrangement, and irregular computation | 52 |

TLSU and CUBE retain their own encoding families and execution engines. The
complete Tile engine inventory is therefore `VEC`, `SFU`, `TLSU`, and `CUBE`.

## Encoding and assembly

The TEPL Mode/Function encoding is unchanged. `BSTART.TEPL` is the unique
compiled decode identity. Assemblers also accept:

- `BSTART.VEC` when the selected operation is catalogued as VEC; and
- `BSTART.SFU` when the selected operation is catalogued as SFU.

Canonical disassembly emits `BSTART.VEC` or `BSTART.SFU` according to the
selected operation's engine. The aliases do not allocate new opcode space and
do not create additional decode identities.

## Classification

The seven normative semantic classes are:

| Class | Engine ownership | Count |
|---|---|---:|
| elementwise-tile-tile | VEC or SFU, as catalogued | 25 |
| tile-scalar-and-immediate | VEC | 15 |
| reduce-and-expand | SFU | 28 |
| memory-and-data-movement | TLSU | 9 |
| matrix-and-matrix-vector | CUBE | 12 |
| layout-and-rearrangement | SFU or TLSU, as catalogued | 7 |
| irregular-and-complex | SFU | 13 |

VEC is restricted to element-wise computation. Operations that require complex
hardware, including transcendental functions, reductions, expands, and
irregular processing, execute on SFU. The exact per-operation assignment is
normative in `isa/v0.58/state/pto_ops.json`; prose must not redefine it.

## Block behavior

TEPL-carried operations are header-driven Tile operations and do not contain a
SIMT body. `B.TEXT` is illegal. Their operands and descriptor requirements are
defined by the selected operation and the generated v0.58 catalog.

TEPL-carried blocks support fall-through only unless an instruction page states
a stricter rule. They operate on Tile state and do not directly replace TLSU
memory movement or CUBE matrix execution.
