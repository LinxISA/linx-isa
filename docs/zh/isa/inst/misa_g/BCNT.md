# BCNT

## 说明

计数置位位数(*Count set Bits*)  
计数源操作数的第 **M** 位开始连续 **N** 位的范围内 **置位为1** 的位数，结果写到目的寄存器中。

## 汇编语法

```
    bcnt SrcL, M, N, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **M**：开始置一的比特位，取值范围为：[63, 0]。该参数编码于imms字段。
- **N**：连续置一的总位数，取值范围为：[64, 1]。该参数减1后编码于imml字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![BCNT](../../../figs/bitfield/svg/Instruction_32bit/BCNT.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;

    bits(64)  operand = R[s, 64];
    bits(64)  result = 0;
    bits(128) newoperand = (operand << 64) | operand; 

    foreach (i from 0 to (N-1) by 1 in dec) {
        if newoperand[M+i] == 1 then result++;
    }
    R[d, 64] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
bcnt a1, m, n,           ->t             /* 单寄存器绝对索引 */
bcnt t#1, m, n,          ->t             /* 单寄存器相对索引 */
bcnt u#1, m, n,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
bcnt a1, m, n,           ->u             /* 单寄存器绝对索引 */
bcnt t#1, m, n,          ->u             /* 单寄存器相对索引 */
bcnt u#1, m, n,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
bcnt a1, m, n,           ->a3            /* 单寄存器绝对索引 */
bcnt t#1, m, n,          ->a3            /* 单寄存器相对索引 */
bcnt u#1, m, n,          ->a3            /* 单寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
