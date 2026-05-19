# CTZ

## 说明

计数尾随零位(*Count Trailing Zero bits*)  
从源操作数的 `M` 位开始连续 `N` 位的范围内，从低位至高位计数遇到第一个`1`之前二进制`0`的位数，将计数结果写到目的寄存器中。

## 汇编语法

```
    ctz SrcL, M, N, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **M**：计数范围的起始位，取值范围为：[63, 0]。该参数编码于imms字段。
- **N**：计数范围的总位数，取值范围为：[64, 1]。该参数减1后编码于imml字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![CTZ](../../../figs/bitfield/svg/Instruction_32bit/CTZ.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;

    bits(64) operand = R[s, 64];
    bits(128) newoperand = (operand << 64) | operand;

    bits(64) result = 0;
    foreach (i from 0 to (N-1) by 1 in dec) {
        if newoperand[M+i] == 0 then result++;
        else break;
    }

    R[d, 64] = result;
```

![ctz](../../../figs/isa/inst/ctz.png){ width="800" }

## 汇编索引模式

指令输出到块内t寄存器:
```asm
ctz a1,  m, n,    ->t             /* 单寄存器绝对索引 */
ctz t#1, m, n,    ->t             /* 单寄存器相对索引 */
ctz u#1, m, n,    ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
ctz a1,  m, n,    ->u             /* 单寄存器绝对索引 */
ctz t#1, m, n,    ->u             /* 单寄存器相对索引 */
ctz u#1, m, n,    ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
ctz a1,  m, n,    ->a3            /* 单寄存器绝对索引 */
ctz t#1, m, n,    ->a3            /* 单寄存器相对索引 */
ctz u#1, m, n,    ->a3            /* 单寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
