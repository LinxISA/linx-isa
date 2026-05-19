# HL.SETC.LTUI

## 说明

立即数小于置位提交(*Set Commit Argument if Less Than, Unsigned Immediate*)  
无符号比较源操作数和立即数，如果源操作数小于立即数，在本块指令提交时，跳转到指定BPC。

## 汇编语法

```asm
    hl.setc.ltui SrcL, uimm
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **uimm**：无符号立即数，编码为(uimm12<< shamt)。

## 编码格式

- 低16bit编码：

![HL.SETC.LTUI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SETC.LTUI.svg)

- 高32bit编码：

![HL.SETC.LTUI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SETC.LTUI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);

    bits(64) operand = R[s, 64];
    bits(64) uimm = ZeroExtend(uimm24);
    uimm = uimm << shamt;
    BARG.TAKEN = (operand <(u) uimm ? 1 : 0);
```

## 汇编索引模式

```asm
hl.setc.ltui a1, uimm   /* 单寄存器绝对索引 */
hl.setc.ltui t#1, uimm  /* 单寄存器相对索引 */
hl.setc.ltui u#1, uimm  /* 单寄存器相对索引 */
```

## 注意事项

1. 本指令不占块内私有寄存器槽位。
2. 本指令在一个块内只能执行一次。
3. 本指令仅在条件跳转COND块内有效。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
