# 块内跳转指令

跳转指令用于实现在块体指令间进行跳转，跳转方式支持**PC相对跳转**和**寄存器相对跳转**。

## 指令列表

块内跳转指令列表如下：

|     微指令    | 汇编格式       |     描述                            |
|---------------|---------------|-------------------------------------|
|  B.EQ  |  b.eq srcL, srcR, label |  根据左右源操作数是否相等决定是否跳转  |
|  B.NE  |  b.ne srcL, srcR, label |  根据左右源操作数是否不等决定是否跳转  |
|  B.LT  |  b.lt srcL, srcR, label |  根据左源操作数是否小于右源操作数（有符号比较）决定是否跳转  |
|  B.GE  |  b.ge srcL, srcR, label |  根据左源操作数是否大于等于右源操作数（有符号比较）决定是否跳转  |
|  B.LTU  |  b.ltu srcL, srcR, label |  根据左源操作数是否小于右源操作数（无符号比较）决定是否跳转  |
|  B.GEU  |  b.geu srcL, srcR, label |  根据左源操作数是否大于等于右源操作数（无符号比较）决定是否跳转  |
|  B.Z  |  b.z label |  根据P寄存器的值是否是全零决定是否跳转  |
|  B.NZ  |  b.z label |  根据P寄存器的值是否是非全零决定是否跳转  |
|  JR  |  jr SrcL, label |  无条件跳转到寄存器内tpc加偏移的目标地址处  |
|  J  |  j label |  无条件跳转到当前tpc加偏移的目标地址处  |

![InnerBlockBranch32bits](../../../figs/bitfield/svg/Introduction_32bit/BranchInstruction.svg)

## 备注

1. 该类指令无目的寄存器，且不占用块内私有寄存器。
3. 该类指令作为块体的最后一条指令时，本指令提交后块指令立即提交，块内跳转不生效。
