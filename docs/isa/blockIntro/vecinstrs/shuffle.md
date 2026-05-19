# Transformation instructions

The shuffle instruction is used in multiple lane parallel execution mode within a parallel block to move data across lanes. This operation is usually used to change the dimension order or element position of tensor.

Four types of shuffle operations are supported within parallel blocks:

| Mode | Description | Instructions involved |
|------|------|----------|
| **up** | Move data to higher ID lanes (shuffle data to upper lanes) | V.SHFL.UP, V.SHFLI.UP |
| **down** | Shuffle data to lower lanes | V.SHFL.DOWN, V.SHFLI.DOWN |
| **butterfly** | butterfly data exchange | V.SHFL.BFLY, V.SHFLI.BFLY |
| **index** | Get the data of the specified lane ID (absolute source lane id) | V.SHFL.IDX, V.SHFLI.IDX |

## Command list

Each mode provides two instructions, including a version with full register parameters and a version with immediate parameters, providing software with flexible choices.

| Microinstructions | Assembly format |
|--------------|-------------------------------------------------|
| V.SHFL.UP | `v.shfl.up   SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFL.DOWN | `v.shfl.down SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFL.BFLY | `v.shfl.bfly SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFL.IDX | `v.shfl.idx  SrcL.{T}, SrcR.{T}, SrcD.{T}, ->Dst.{W}` |
| V.SHFLI.UP | `v.shfli.up   SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}` |
| V.SHFLI.DOWN | `v.shfli.down SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}` |
| V.SHFLI.BFLY | `v.shfli.bfly SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}` |
| V.SHFLI.IDX | `v.shfli.idx  SrcL.{T}, SrcR.{T}, imm, ->Dst.{W}` |

## Command encoding

![shuffle](../../../figs/bitfield/svg/Introduction_64bit/ShuffleVector.svg)