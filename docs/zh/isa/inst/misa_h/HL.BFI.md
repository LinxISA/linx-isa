# HL.BFI

## 说明

位域插入(*Bit Field Insert*)  
从右源寄存器中取出低 **N** 位，替换掉左源寄存器值的第 **M** 位至第 **M+N-1** 位，结果写到目的寄存器中。

## 汇编语法

```asm
    hl.bfi SrcL, SrcR, M, N, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **M**：从左源寄存器中开始替换的起始位，范围为：0-63。该参数编码于imms字段。
- **N**：从右源寄存器中连续截取的位数，范围为：1-64。该参数减1后编码于imml字段。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.BFI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.BFI.svg)

- 高32bit编码：

![HL.BFI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.BFI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer M = UInt(imms);
    integer N = UInt(imml) + 1;

    bits(64) operand1 = R[m, 64];
    bits(64) operand2 = R[n, 64];
    bits(128) result = 0;

    result[63:0] = operand1[63:0];
    result[M+N-1 : M] = operand2[N-1 : 0];

    /* M+N > 64 时出现卷绕 */
    if M+N > 64 then result[M+N-65 : 0] = result[M+N-1 : 64];

    R[d, 64] = result[63:0];
```

当 `M+N <= 64` 时：

![HL.BFI](../../../figs/isa/inst/bfi1.png){ width="800" }

当 `M+N > 64` 时：

![HL.BFI](../../../figs/isa/inst/bfi2.png){ width="800" }

当 `N == 64` 时：

![HL.BFI](../../../figs/isa/inst/bfi3.png){ width="800" }

此时，可以看到该指令对源操作数实现了循环移位效果。因此，bfi指令可以用于对数据进行循环移位。

## 使用方法

假如要修改变量A中区间[M, M+N-1]修改为变量B的低 N bits，那么需要如下汇编操作：

```
hl.bfi A, B, M, N     ;将B的低N bits截取出来，并和A的M bit以及高位合并
```

## 汇编索引模式

- 指令输出到块内t寄存器

```asm
hl.bfi a1, a2, m, n,   ->t             /* 双寄存器绝对索引 */
hl.bfi a1, t#2, m, n,  ->t             /* 双寄存器混合索引 */
hl.bfi a1, u#2, m, n,  ->t             /* 双寄存器混合索引 */
hl.bfi t#1, a2, m, n,  ->t             /* 双寄存器混合索引 */
hl.bfi t#1, t#2, m, n, ->t             /* 双寄存器相对索引 */
hl.bfi t#1, u#2, m, n, ->t             /* 双寄存器相对索引 */
hl.bfi u#1, a2, m, n,  ->t             /* 双寄存器混合索引 */
hl.bfi u#1, t#2, m, n, ->t             /* 双寄存器相对索引 */
hl.bfi u#1, u#2, m, n, ->t             /* 双寄存器相对索引 */
```

- 指令输出到块内u寄存器

```asm
hl.bfi a1, a2, m, n,   ->u             /* 双寄存器绝对索引 */
hl.bfi a1, t#2, m, n,  ->u             /* 双寄存器混合索引 */
hl.bfi a1, u#2, m, n,  ->u             /* 双寄存器混合索引 */
hl.bfi t#1, a2, m, n,  ->u             /* 双寄存器混合索引 */
hl.bfi t#1, t#2, m, n, ->u             /* 双寄存器相对索引 */
hl.bfi t#1, u#2, m, n, ->u             /* 双寄存器相对索引 */
hl.bfi u#1, a2, m, n,  ->u             /* 双寄存器混合索引 */
hl.bfi u#1, t#2, m, n, ->u             /* 双寄存器相对索引 */
hl.bfi u#1, u#2, m, n, ->u             /* 双寄存器相对索引 */
```

- 指令输出到全局寄存器R1-R23

```asm
hl.bfi a1, a2, m, n,   ->a3             /* 双寄存器绝对索引 */
hl.bfi a1, t#2, m, n,  ->a3             /* 双寄存器混合索引 */
hl.bfi a1, u#2, m, n,  ->a3             /* 双寄存器混合索引 */
hl.bfi t#1, a2, m, n,  ->a3             /* 双寄存器混合索引 */
hl.bfi t#1, t#2, m, n, ->a3             /* 双寄存器相对索引 */
hl.bfi t#1, u#2, m, n, ->a3             /* 双寄存器相对索引 */
hl.bfi u#1, a2, m, n,  ->a3             /* 双寄存器混合索引 */
hl.bfi u#1, t#2, m, n, ->a3             /* 双寄存器相对索引 */
hl.bfi u#1, u#2, m, n, ->a3             /* 双寄存器相对索引 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，且**仅允许在标量块内使用**。
