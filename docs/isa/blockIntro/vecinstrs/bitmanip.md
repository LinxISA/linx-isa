# Bit manipulation instructions

Bit operation instructions are used to perform efficient local bit field processing and statistics on 8/16/32/64-bit scalar elements in each execution channel (Lane). This type of instructions uses bits as the basic unit and covers common operations such as endian flipping, bit counting, bit segment extraction and expansion, and bit segment clearing/setting. It is suitable for scenarios such as accelerated encoding and decoding, cryptography, image/signal processing, and bit-level protocol analysis.

## Command list

| Microinstructions | Assembly format | Supported register width | Description |
|---------------|---------------|----------------|---------------------------------------------|
| V.BXU | `v.bxu  SrcL.{T}, M, N, ->Dst.{W}` | Continuously intercept the `N` bits starting from the `M` bit of the source operand without sign extension |
| V.BXS | `v.bxs  SrcL.{T}, M, N, ->Dst.{W}` | Continuously intercept the `N` bits starting from the `M` bit of the source operand and sign extend |
| V.BIC | `v.bic  SrcL.{T}, M, N, ->Dst.{W}` | Set the consecutive `N` bits starting from the `M` bit of the source operand to 0 |
| V.BIS | `v.bis  SrcL.{T}, M, N, ->Dst.{W}` | Set the consecutive `N` bits starting from the `M` bit of the source operand to 1 |
| V.CTZ | `v.ctz  SrcL.{T}, M, N, ->Dst.{W}` | Count the number of 0s after the first 1 in the `N` bit of the source operand starting from the `M` bit |
| V.CLZ | `v.clz  SrcL.{T}, M, N, ->Dst.{W}` | Count the number of 0s before the first 1 in the `N` bit of the source operand starting from the `M` bit |
| V.BCNT | `v.bcnt SrcL.{T}, M, N, ->Dst.{W}` | The number of consecutive `N` bits starting from the `M` bit of the count source operand is 1 |
| V.REV | `v.rev  SrcL.{T}, M, N, ->Dst.{W}` | Toggle in units of `N` bits within the range of `M` bits of the source operand |

## Command encoding

![BitOperation](../../../figs/bitfield/svg/Introduction_64bit/BitManipulationVector.svg)

## Note on usage and boundaries

- The caller should ensure that the values of M and N do not cross the bounds; out-of-bounds behavior is undefined.
- For counting instructions (CLZ/CTZ/BCNT), statistics are only performed within the specified N-bit window, regardless of bits outside the window.
- For instructions (BIC/BIS) that modify bit fields, only the specified bit fields are affected, and the remaining bits are retained at their original values.
- Does not involve cross-channel data dependency and synchronization.