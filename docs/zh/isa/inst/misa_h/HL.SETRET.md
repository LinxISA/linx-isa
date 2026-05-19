# HL.SETRET

## 说明

设置返回地址(*Set Return Address*)  
立即数左移1位(低位置零)后与当前指令的`TPC`相加，结果写到ra寄存器中。

## 汇编语法

```asm
    hl.setret uimm, ->ra
```

## 汇编符号

- **uimm**：32位无符号立即数，编码于imm32域。
- **->**：用于指示目的寄存器。
- **ra**：目的寄存器，全局寄存器ra(r10)。

## 编码格式

- 低16bit编码：

![HL.SETRET](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SETRET.svg)

- 高32bit编码：

![HL.SETRET](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SETRET.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 将数据无符号扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    bits(64) uimm = ZeroExtend(imm32);
    bits(64) result = tpc + (uimm << 1);
    R[10, 64] = result;
```

## 汇编索引模式

```asm
    hl.setret uimm,    ->ra         /* 只能写到全局的ra寄存器 */
```

!!! note "注意！"

    1. 该指令**只能写全局的ra寄存器**。
    2. 该指令仅在**CALL**和**ICALL**跳转的块内使用。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，，允许使用在不同块类型块内。
