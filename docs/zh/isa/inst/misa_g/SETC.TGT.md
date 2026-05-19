# SETC.TGT

## 说明

设置目标地址(*Set Commit Argument, Target*)  
在本块指令提交后，无条件设置NEXTBPC为源寄存器中块间跳转的目标地址并跳转至下一个块执行。

## 汇编语法

```
    setc.tgt SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![SETC.TGT](../../../figs/bitfield/svg/Instruction_32bit/SETC.TGT.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) value = R[s, datawidth];
    BARG[LSR_ID] = value;
```

## 汇编索引模式

```asm
setc.tgt a1       /* 单寄存器绝对索引 */
setc.tgt t#1      /* 单寄存器相对索引 */
setc.tgt u#1      /* 单寄存器相对索引 */
```

## 注意事项

1. 本指令不占私有寄存器槽位。
2. 本指令在一个块内只能执行一次。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，允许使用在不同块类型块内。
