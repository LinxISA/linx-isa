# MAX

## 说明

有符号最大值(*Maximum*)  
有符号比较左源操作数和右源操作数，将较大值写入到目的寄存器中。

## 汇编语法

```
    max SrcL, SrcR, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![MAX](../../../figs/bitfield/svg/Instruction_32bit/MAX.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    
    bits(64) operand1 = R[m, 64];
    bits(64) operand2 = R[n, 64];

    bits(64) result = (operand1 >(s) operand2 ? operand1 : operand2);
    R[d, 64] = result;
```

<!-- ## 汇编索引模式

```asm
max.h a1, a2           /* 双寄存器绝对索引 */
max.h t#1, a2          /* 双寄存器相对绝对索引 */
max.h a1, t#2          /* 双寄存器相对绝对索引 */
max.h t#1, t#2         /* 双寄存器相对索引 */
max.s a1, a2           /* 单精度浮点操作数，可使用.d,.s,.h */
max.s t#1, a2          /* 单精度浮点操作数，可使用.d,.s,.h */
max.s a1, t#2          /* 单精度浮点操作数，可使用.d,.s,.h */
max.s t#1, t#2         /* 单精度浮点操作数，可使用.d,.s,.h */
max.s a1, a2,->a1      /* 指令输出到私有寄存器 */
max.s t#1, a2,->a1     /* 指令输出到私有寄存器 */
max.s a1, t#2,->a1     /* 指令输出到私有寄存器 */
max.s t#1, t#2,->a1    /* 指令输出到私有寄存器 */
max.d a1, a2,=>a1      /* 指令输出到全局寄存器 */
max.d t#1, a2,=>a1     /* 指令输出到全局寄存器 */
max.d a1, t#2,=>a1     /* 指令输出到全局寄存器 */
max.d t#1, t#2,=>a1    /* 指令输出到全局寄存器 */
``` -->

## 备注

本指令属于[标准指令扩展](../../instset/standardInstrs.md)，只能用于浮点块指令块体中。
