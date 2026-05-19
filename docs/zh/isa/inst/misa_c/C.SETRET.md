# C.SETRET

## 说明

设置返回地址(*Set Return Address*)  
立即数左移1位(低位置零)后与本指令的`TPC`相加，结果写到ra寄存器中。

本指令的标准形式请见[SETRET](../misa_g/SETRET.md)。

## 汇编语法

```
    c.setret uimm, ->ra
```

## 汇编符号

- **uimm**：5位无符号立即数，编码于uimm5域。
- **->**：用于指示目的寄存器。
- **ra**：目的寄存器，全局寄存器ra(r10)。

## 编码格式

![C.SETRET](../../../figs/bitfield/svg/Instruction_16bit/C.SETRET.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 将数据无符号扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer datawidth = 64;

    bits(datawidth) uimm = ZeroExtend(uimm5);
    bits(datawidth) result = tpc + (uimm << 1);
    R[10, datawidth] = result;
```

## 汇编索引模式

指令只能输出到ra寄存器:
```asm
    c.setret uimm, ->ra             /* 立即数操作数 */
```

!!! note "注意！"

    1. 本指令**只能写全局的ra寄存器**。
    2. 本指令仅在**CALL**和**ICALL**跳转的块内使用。

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
