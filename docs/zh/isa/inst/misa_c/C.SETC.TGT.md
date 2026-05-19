# C.SETC.TGT

## 说明

设置目标地址(*Set Commit Argument, Target*)  
在本块指令提交后，无条件设置NEXTBPC为源寄存器中块间跳转的目标地址并跳转至下一个块执行。

本指令的标准形式请见[SETC.TGT](../misa_g/SETC.TGT.md)

## 汇编语法

```
    c.setc.tgt SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![C.SETC.TGT](../../../figs/bitfield/svg/Instruction_16bit/C.SETC.TGT.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer s = UInt(SrcL);
    BARG.TGT = R[s, 64];
```

## 汇编索引模式

```asm
    c.setc.tgt  a1               /*单寄存器绝对索引*/
    c.setc.tgt  t#1              /*单寄存器相对索引*/
    c.setc.tgt  u#1              /*单寄存器相对索引*/
```

!!! note "注意! "

    1. 本指令不占私有寄存器槽位。
    2. 本指令在一个块内只能执行一次。

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
