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
B.IOS S<SharedTID>, mask=<PE_MASK>
```

Destination binding:

```asm
B.IOS mask=<PE_MASK>, ->S<SharedTID><TSize>
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
| 18:15 | `PE_MASK` | Four-PE participation mask |
| 14:12 | fixed `001` | Function selector |
| 11:9 | `TSize` | Source/destination selector and per-PE destination size |
| 8:0 | fixed `000010011` | Minor encoding |

The 32-bit decode identity is mask `0xf00871ff`, match `0x00001013`. Its PTO
source form is `b_ios_32_4ba5ef98fdaa`; the standalone Linx catalog form is
`b_ios_32_11ff57a2e635`.

All 256 `SharedTID` values and all 16 `PE_MASK` values are assigned. The three
`TSize` bits are fully assigned as follows, so this form has no unassigned
`TSize` code:

| `TSize` | Form | Per-PE destination capacity |
| --- | --- | --- |
| 0 | Source binding | Not applicable; no destination allocation |
| 1 | Destination binding | 128 B |
| 2 | Destination binding | 256 B |
| 3 | Destination binding | 512 B |
| 4 | Destination binding | 1 KiB |
| 5 | Destination binding | 2 KiB |
| 6 | Destination binding | 4 KiB |
| 7 | Destination binding | 8 KiB |

Fixed-bit mismatches do not decode as `B.IOS`.

## Operation

`PE_MASK` is a predicate over the four fixed PE quarters. Multiple set bits
are legal. `PE_MASK=0000` is a strict no-op: it performs no binding,
allocation, register read, descriptor update, payload update, or faulting
access. For a nonzero mask, each set bit enables the corresponding PE quarter.
The aggregate storage selected by a destination is therefore the per-PE
capacity multiplied by the number of set bits.

For a source binding (`TSize=0`), the selected PEs read the named Shared
register. The read does not modify its descriptor. Reading an uninitialized
Shared register produces an undefined value, like reading an undefined scalar
register.

For a destination binding (`TSize=1` through `TSize=7`), the selected Shared
architectural register receives a fresh allocation and its descriptor is
updated. A Shared write atomically updates descriptor and payload state as one
read-modify-write operation. The architecture imposes no ordering between PEs
beyond that atomic property; software must avoid conflicting offsets.

The capacity in the table is always per PE. Descriptor rows and columns are
powers of two. Rows are derived from `TSize`, the column count, and the element
size; valid rows and columns must not exceed the allocated shape. Matrix
operations obey the same shape rule.

## Examples

Bind `S7` as a source for PE quarters 2 and 3:

```asm
B.IOS S7, mask=0011
```

Allocate 128 B per participating PE in `S23`; four participating PEs select
512 B in aggregate:

```asm
B.IOS mask=1111, ->S23<128B>
```

Suppress the binding completely:

```asm
B.IOS S7, mask=0000
```

`B.IOT` remains the distinct Local tile binding instruction. It does not bind
the Shared `S0` through `S255` bank.
