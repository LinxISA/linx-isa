# Multiplication instructions

| Microinstructions | Assembly format | Description |
|--------------|----------------------------------|-------------------------------------------------------------|
| MUL | mul SrcL, SrcR, ->{t,u,Rd} | Two 64-bit signed multiplications, the lower 64 bits of the result are written to RegDst |
| MULU | mulu SrcL, SrcR, ->{t,u,Rd} | Two 64-bit unsigned multiplications, the lower 64 bits of the result are written to RegDst |
| MULW | mulw SrcL, SrcR, ->{t,u,Rd} | Two 32-bit signed multiplications, the result is signed-extended with the lower 32 bits and written to RegDst |
| MULUW | muluw SrcL, SrcR, ->{t,u,Rd} | Two 32-bit unsigned multiplications, the lower 32-bit unsigned extension of the result is taken and written to RegDst |
| MADD | madd SrcL, SrcR, SrcD, ->{t,u,Rd} | Two 64-bit signed multiplication, plus another 64-bit, the result is written to RegDst |
| MADDW | maddw SrcL, SrcR, SrcD, ->{t,u,Rd} | Two 32-bit signed multiplication, plus another 32-bit, the result is sign-extended with the lower 32 bits and written to RegDst |

The encoding is as follows:

![Multi-CycleALU](../../../figs/bitfield/svg/Introduction_32bit/multiInstruction.svg)


<!-- 
|  MULH   |  mulh SrcL, SrcR, ->{t,u,Rd}   |  两64位有符号乘法，高64位写到T，低64位写到RegDst  |
|  MULHU  |  mulhu SrcL, SrcR, ->{t,u,Rd}  |  两64位无符号乘法，高64位写到T，低64位写到RegDst  |
 -->