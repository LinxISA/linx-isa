# HL.LUI

## 说明

高位立即数加载(*Load Upper Immediate*)  
将符号位扩展的 `32位` 立即数左移 `32位`，将低32位置零后写到目的寄存器中。

本指令的标准版本请见[LUI](../misa_g/LUI.md)。

## 汇编语法

```
    hl.lui imm, ->{t, u, Rd}
```

## 汇编符号

- **imm**：32位立即数。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16位编码：

![HL.LUI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.LUI.svg)

- 高32位编码：

![HL.LUI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.LUI.svg)

## 执行方式

- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    R[d, 64] = imm << 32;
```

## 汇编索引模式

```asm
hl.lui imm,    ->t         /* 指令输出到块内t寄存器 */
hl.lui imm,    ->u         /* 指令输出到块内u寄存器 */
hl.lui imm,    ->a3        /* 指令输出到全局寄存器R1-R23 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
