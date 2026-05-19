# HL.CMP.ANDI

## 说明

立即数相与·比较(*Compare by And Immediate*)  
源操作数和有符号立即数执行按位与运算，结果为`非0`则将`1`写入目的寄存器，否则写入`0`。

## 汇编语法

```asm
    hl.cmp.andi SrcL, simm, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：24位有符号立即数，编码于simm24字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.CMP.ANDI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.CMP.ANDI.svg)

- 高32bit编码：

![HL.CMP.ANDI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.CMP.ANDI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);

    bits(64) operand = R[s, 64];
    bits(64) simm = SignExtend(simm24);

    bits(64) result = ((operand & simm) != 0 ? 1 : 0);
    R[d, 64] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
hl.cmp.andi a1, simm,           ->t             /* 单寄存器绝对索引 */
hl.cmp.andi t#1, simm,          ->t             /* 单寄存器相对索引 */
hl.cmp.andi u#1, simm,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
hl.cmp.andi a1, simm,           ->u             /* 单寄存器绝对索引 */
hl.cmp.andi t#1, simm,          ->u             /* 单寄存器相对索引 */
hl.cmp.andi u#1, simm,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
hl.cmp.andi a1, simm,           ->a3            /* 单寄存器绝对索引 */
hl.cmp.andi t#1, simm,          ->a3            /* 单寄存器相对索引 */
hl.cmp.andi u#1, simm,          ->a3            /* 单寄存器相对索引 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
