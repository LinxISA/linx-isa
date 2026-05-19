# HL.LIU

## 说明

无符号长立即数加载(*Load Unsigned Immediate*)  
将 `32位` 长立即数无符号扩展后写到目的寄存器中。

## 汇编语法

```
    hl.liu uimm, ->{t, u, Rd}
```

## 汇编符号

- **uimm**：32位立即数。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16位编码：

![HL.LIU](../../../figs/bitfield/svg/Instruction_48bit_16/HL.LIU.svg)

- 高32位编码：

![HL.LIU](../../../figs/bitfield/svg/Instruction_48bit_32/HL.LIU.svg)

## 执行方式

- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    bits(64) immediate = SignExtend(uimm32[31:0]);
    R[d, 64] = immediate;
```

## 汇编索引模式

```asm
hl.liu uimm,    ->t         /* 指令输出到块内t寄存器 */
hl.liu uimm,    ->u         /* 指令输出到块内u寄存器 */
hl.liu uimm,    ->a3        /* 指令输出到全局寄存器R1-R23 */
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
