# HL.MIADD

## 说明

立即数乘加(*Multiply and Add with Immediate*)  
左源寄存器 加上 右源寄存器 与 无符号立即数的乘积，结果的`低64位`写到目的寄存器中。

## 汇编语法

```asm
    hl.miadd SrcL, SrcR, uimm, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **uimm**：19位无符号立即数，编码于uimm19字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.MIADD](../../../figs/bitfield/svg/Instruction_48bit_16/HL.MIADD.svg)

- 高32bit编码：

![HL.MIADD](../../../figs/bitfield/svg/Instruction_48bit_32/HL.MIADD.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) operand1 = R[m, 64];
    bits(64) operand2 = R[n, 64];
    bits(64) immediate = ZeroExtend(uimm19);
    bits(128) result = operand1 + operand2 * immediate;

    R[d, 64] = result[63:0];
```

## 汇编索引模式

- 指令输出到块内t寄存器

```asm
hl.miadd a1, a2, uimm,           ->t             /* 双寄存器绝对索引 */
hl.miadd a1, t#2, uimm,          ->t             /* 双寄存器混合索引 */
hl.miadd a1, u#2, uimm,          ->t             /* 双寄存器混合索引 */
hl.miadd t#1, a2, uimm,          ->t             /* 双寄存器混合索引 */
hl.miadd t#1, t#2, uimm,         ->t             /* 双寄存器相对索引 */
hl.miadd t#1, u#2, uimm,         ->t             /* 双寄存器相对索引 */
hl.miadd u#1, a2, uimm,          ->t             /* 双寄存器混合索引 */
hl.miadd u#1, t#2, uimm,         ->t             /* 双寄存器相对索引 */
hl.miadd u#1, u#2, uimm,         ->t             /* 双寄存器相对索引 */
```

- 指令输出到块内u寄存器

```asm
hl.miadd a1, a2, uimm,           ->u             /* 双寄存器绝对索引 */
hl.miadd a1, t#2, uimm,          ->u             /* 双寄存器混合索引 */
hl.miadd a1, u#2, uimm,          ->u             /* 双寄存器混合索引 */
hl.miadd t#1, a2, uimm,          ->u             /* 双寄存器混合索引 */
hl.miadd t#1, t#2, uimm,         ->u             /* 双寄存器相对索引 */
hl.miadd t#1, u#2, uimm,         ->u             /* 双寄存器相对索引 */
hl.miadd u#1, a2, uimm,          ->u             /* 双寄存器混合索引 */
hl.miadd u#1, t#2, uimm,         ->u             /* 双寄存器相对索引 */
hl.miadd u#1, u#2, uimm,         ->u             /* 双寄存器相对索引 */
```

- 指令输出到全局寄存器R1-R23

```asm
hl.miadd a1, a2, uimm,           ->a3             /* 双寄存器绝对索引 */
hl.miadd a1, t#2, uimm,          ->a3             /* 双寄存器混合索引 */
hl.miadd a1, u#2, uimm,          ->a3             /* 双寄存器混合索引 */
hl.miadd t#1, a2, uimm,          ->a3             /* 双寄存器混合索引 */
hl.miadd t#1, t#2, uimm,         ->a3             /* 双寄存器相对索引 */
hl.miadd t#1, u#2, uimm,         ->a3             /* 双寄存器相对索引 */
hl.miadd u#1, a2, uimm,          ->a3             /* 双寄存器混合索引 */
hl.miadd u#1, t#2, uimm,         ->a3             /* 双寄存器相对索引 */
hl.miadd u#1, u#2, uimm,         ->a3             /* 双寄存器相对索引 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
