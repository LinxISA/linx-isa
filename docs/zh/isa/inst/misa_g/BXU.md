# BXU

## 说明

无符号位提取(*Bit eXtract Unsigned*)  
从源操作数的第 `M` 位开始连续截取 `N` 位，无符号扩展后写到目的寄存器中。

## 汇编语法

```
    bxu SrcL, M, N, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **M**：开始截取的比特位，取值范围为：[63, 0]。该参数编码于imms字段。
- **N**：连续截取的总位数，取值范围为：[64, 1]。该参数减1后编码于imml字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![BXU](../../../figs/bitfield/svg/Instruction_32bit/BXU.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;
    integer datawidth = 64;

    bits(datawidth) operand = R[s, datawidth];
    bits(datawidth) operand_t;

    if (N + M <= 64) then
        operand_t[N-1 : 0] = operand[N+M-1 : M];
    else
        operand_t[63-M : 0] = operand[63 : M];
        operand_t[N-1 : 64-M] = operand[M+N-65 : 0];

    bits(datawidth) result = ZeroExtend(operand_t[N-1:0]);

    R[d, datawidth] = result;
```

- 当 **M+N <= 64** 时：

![bxu1](../../../figs/isa/inst/bxu1.png){ width="800" }

- 当 **M+N > 64** 且 **N < 64** 时：

![bxu2](../../../figs/isa/inst/bxu2.png){ width="500" }

- 当 **M+N > 64** 且 **N == 64** 时：

![bxu3](../../../figs/isa/inst/bxu3.png){ width="500" }

## 汇编索引模式

指令输出到块内t寄存器:
```asm
bxu a1, m, n,           ->t             /* 单寄存器绝对索引 */
bxu t#1, m, n,          ->t             /* 单寄存器相对索引 */
bxu u#1, m, n,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
bxu a1, m, n,           ->u             /* 单寄存器绝对索引 */
bxu t#1, m, n,          ->u             /* 单寄存器相对索引 */
bxu u#1, m, n,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
bxu a1, m, n,           ->a3            /* 单寄存器绝对索引 */
bxu t#1, m, n,          ->a3            /* 单寄存器相对索引 */
bxu u#1, m, n,          ->a3            /* 单寄存器相对索引 */
```

## 汇编举例

由上面 **M > 0** 且 **N == 64** 时的实现可以看到，该指令对操作数实现了循环移位。

bxu指令实现循环移位的方式如下：

- **实现循环左移rol**
```c
bxu SrcL, M, 64, ->{t, u, Rd}    /* M = 64 - shamt */
```
此时需将 M 设置为XLEN(即64)减去循环左移的位数后的值。

- **实现循环右移ror**
```c
bxu SrcL, M, 64, ->{t, u, Rd}    /* M = shamt */
```
此时需将 M 设置为循环右移的位数。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
