# B.IOS

## Purpose

`B.IOS` binds one absolute Shared tile register for a block operation. Each
core owns a private bank named `S0` through `S255`; all four PEs in that core
can access every entry in the bank. The same `Sx` name in another core denotes
a different register. Shared register allocation is a compiler responsibility,
while hardware may rename the selected architectural register.

The machine-readable instruction catalog remains the encoding authority. This
page explains that record and does not define an alternate encoding.

## Assembly syntax

Source binding:

```asm
B.IOS S<SharedTID>, mask=<PEMode>
```

Destination binding:

```asm
B.IOS mask=<PEMode>, ->S<SharedTID><SizeCode>
```

`SharedTID` is an absolute integer in the range 0 through 255. Canonical
assembly therefore uses `S0` through `S255`; relative spellings such as `S#1`
are not accepted.

## Encoding

![B.IOS encoding](../wavedrom/enc_b_ios.svg)

| Bits | Field | Meaning |
| --- | --- | --- |
| 31:28 | fixed `0000` | Major encoding |
| 27:20 | `SharedTID` | Absolute Shared register index, 0 through 255 |
| 19 | fixed `0` | Reserved fixed bit; any other value is not `B.IOS` |
| 18:15 | `SizeCode` | Source/destination role and per-PE destination capacity |
| 14:12 | fixed `001` | Function selector |
| 11:9 | `PEMode` | Fixed four-PE participation mode |
| 8:0 | fixed `000010011` | Minor encoding |

The 32-bit decode identity is mask `0xf00871ff`, match `0x00001013`. Its PTO
source form is `b_ios_32_4ba5ef98fdaa`; the standalone Linx catalog form is
`b_ios_32_0f62f62d6a81`.

All 256 `SharedTID` values and all eight `PEMode` values are assigned.
`PEMode` decodes as follows:

| `PEMode` | Semantic mask |
| --- | --- |
| 0 | `0000` (none) |
| 1 | `1000` (PE0) |
| 2 | `0100` (PE1) |
| 3 | `0010` (PE2) |
| 4 | `0001` (PE3) |
| 5 | `1100` (PE0+PE1) |
| 6 | `1110` (PE0+PE1+PE2) |
| 7 | `1111` (all four PEs) |

The four-bit `SizeCode` field is assigned as follows:

| `SizeCode` | Form | Per-PE destination capacity |
| --- | --- | --- |
| 0 | Source binding | Not applicable; no destination allocation |
| 1 | Destination binding | 128 B |
| 2 | Destination binding | 256 B |
| 3 | Destination binding | 512 B |
| 4 | Destination binding | 1 KiB |
| 5 | Destination binding | 2 KiB |
| 6 | Destination binding | 4 KiB |
| 7 | Destination binding | 8 KiB |
| 8 | Destination binding | 16 KiB |
| 9 | Destination binding | 32 KiB |
| 10 | Destination binding | 64 KiB |
| 11 | Destination binding | 128 KiB |
| 12 | Destination binding | 256 KiB |
| 13..15 | Reserved | Illegal instruction |

Fixed-bit mismatches do not decode as `B.IOS`.

## Operation

`PEMode` selects one fixed participation mask from the table above.
`PEMode=000` is a strict no-effect path: it performs no binding,
allocation, register read, descriptor update, payload update, or faulting
access. For a nonzero mask, each set bit enables the corresponding PE quarter.
The aggregate storage selected by a destination is therefore the per-PE
capacity multiplied by the number of set bits.

For a source binding (`SizeCode=0`), the selected PEs read the named Shared
register. The read does not modify its descriptor. Reading an uninitialized
Shared register produces an undefined value, like reading an undefined scalar
register.

For a destination binding (`SizeCode=1` through `SizeCode=12`), the selected Shared
architectural register receives a fresh allocation and its descriptor is
updated. A Shared write atomically updates descriptor and payload state as one
read-modify-write operation. The architecture imposes no ordering between PEs
beyond that atomic property; software must avoid conflicting offsets.

The capacity in the table is always per PE. Descriptor rows and columns are
powers of two. Rows are derived from `SizeCode`, the column count, and the element
size; valid rows and columns must not exceed the allocated shape. Matrix
operations obey the same shape rule.

## Examples

Bind `S7` as a source for PE0 and PE1:

```asm
B.IOS S7, mask=101
```

Allocate 128 B per participating PE in `S23`; four participating PEs select
512 B in aggregate:

```asm
B.IOS mask=111, ->S23<128B>
```

Suppress the binding completely:

```asm
B.IOS S7, mask=000
```

`B.IOT` remains the distinct Local tile binding instruction. It does not bind
the Shared `S0` through `S255` bank.
