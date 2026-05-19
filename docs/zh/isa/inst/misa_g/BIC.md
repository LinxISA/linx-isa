# BIC

## 说明

位域清除(*Bitwise Clear*)  
将源操作数的第 **M** 位开始连续 **N** 位 **置位为0**，结果写到目的寄存器中。

## 汇编语法

```
    bic SrcL, M, N, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **M**：开始清零的比特位，取值范围为：[63, 0]。该参数编码于imms字段。
- **N**：连续清零的总位数，取值范围为：[64, 1]。该参数减1后编码于imml字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![BIC](../../../figs/bitfield/svg/Instruction_32bit/BIC.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;
    integer datawidth = 64;

    bits(datawidth) operand = R[s, datawidth];

    foreach (i from 0 to (N-1) by 1 in dec) {      // i = [0, N-1]
        if (M+i <= 63) then operand[M+i] = 0;
        else operand[M+i-64] = 0;
    }

    R[d, datawidth] = operand;
```

![BIC](../../../figs/isa/inst/bic.png){ width="800" }

## 汇编索引模式

指令输出到块内t寄存器:
```asm
bic a1, m, n,           ->t             /* 单寄存器绝对索引 */
bic t#1, m, n,          ->t             /* 单寄存器相对索引 */
bic u#1, m, n,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
bic a1, m, n,           ->u             /* 单寄存器绝对索引 */
bic t#1, m, n,          ->u             /* 单寄存器相对索引 */
bic u#1, m, n,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
bic a1, m, n,           ->a3            /* 单寄存器绝对索引 */
bic t#1, m, n,          ->a3            /* 单寄存器相对索引 */
bic u#1, m, n,          ->a3            /* 单寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
