# Maximum and minimum value instructions

Maximum and minimum instructions are used to obtain the larger or smaller value of two integer data or the larger or smaller value of two floating point data.

Among them, the larger value of the low-precision/half-precision/single-precision/double-precision floating point number in the FMAX instruction selection register SrcL and register SrcR is written into the destination register queue. The operation of this instruction follows the maxNum(x,y) operation specification in the IEEE754-2008 standard. The FMIN instruction selects the smaller value of the low-precision/half-precision/single-precision/double-precision floating point number in the register SrcL and register SrcR to be written to the destination register queue. The operation of this instruction follows the minNum(x,y) operation specification in the IEEE754-2008 standard.

## Command list

| Microinstructions | Assembly format | Description |
|-------------|--------------------------|--------------------------------------|
| V.MAX | `v.max SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Write the larger value of the two integer inputs to the destination register |
| V.MIN | `v.min SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Write the smaller value of the two integer inputs to the destination register |
| V.FMAX | `v.fmax SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Write the larger value of the two floating-point inputs to the destination register |
| V.FMIN | `v.fmin SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Write the smaller value of the two floating-point inputs to the destination register |

## Command encoding

![Max-Min](../../../figs/bitfield/svg/Introduction_64bit/CompareInstructionVector.svg)