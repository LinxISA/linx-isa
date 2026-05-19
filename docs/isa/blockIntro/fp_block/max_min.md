# Maximum and minimum values

Maximum and minimum instructions are used to obtain the larger or smaller value of two integer data or the larger or smaller value of two floating point data.

The FMAX instruction selects the larger value of the low-precision/half-precision/single-precision/double-precision floating-point number in the register SrcL and register SrcR to be written to the destination register queue. The operation of this instruction follows the maxNum(x,y) operation specification in the IEEE754-2008 standard.

The FMIN instruction selects the smaller value of the low-precision/half-precision/single-precision/double-precision floating point number in the register SrcL and register SrcR to be written to the destination register queue. The operation of this instruction follows the minNum(x,y) operation specification in the IEEE754-2008 standard.

## Command list

| Microinstructions | Assembly format | Description |
|-------------|--------------------------|--------------------------------------|
| MAX | max SrcL, SrcR, ->{t,u,Rd} | The larger value of the two signed integer inputs is written to the destination register |
| MAXU | maxu SrcL, SrcR, ->{t,u,Rd} | The larger value of the two unsigned integer inputs is written to the destination register |
| FMAX | fmax.{T} SrcL, SrcR, ->{t,u,Rd} | The larger value of the two floating-point inputs is written to the destination register |
| MIN | min SrcL, SrcR, ->{t,u,Rd} | The smaller value of the two signed integer inputs is written to the destination register |
| MINU | minu SrcL, SrcR, ->{t,u,Rd} | The smaller value of the two unsigned integer inputs is written to the destination register |
| FMIN | fmin.{T} SrcL, SrcR, ->{t,u,Rd} | The smaller value of the two floating-point inputs is written to the destination register |

## Command encoding

![Max-Min](../../../figs/bitfield/svg/Introduction_32bit/Max-Min.svg)