# FEXP

## 说明

浮点数以e为底的指数值(*Floating-point Exponential Value*)  
取源寄存器中低/半/单/双精度浮点数的以e为底的指数值，写入到目的寄存器中。

## 汇编语法

```
    fexp.<T> SrcL, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **T**：输入的浮点数精度标识，包括FB,FH,FS,FD 4种。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![FEXP](../../../figs/bitfield/svg/Instruction_32bit/FEXP.svg)

SrcType域编码如下：

| SrcType | 数据格式 | 说明 |
|------|---------|------|
| 0 | FD | 64bit双精度浮点数 |
| 1 | FS | 32bit单精度浮点数 |
| 2 | FH | 16bit半精度浮点数 |
| 3 | FB | 8bit低精度浮点数 |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 求以e为底指数值：[FPExp()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);

    case SrcType of:
        when 00 then DataType = FP64;
        when 01 then DataType = FP32;
        when 10 then DataType = FP16;
        when 11 then DataType = FP8;

    DataType operand = R[m, 64];
    bits(64) result = FPExp(operand);

    R[d, 64] = result;
```

<!-- ## 汇编索引模式

```asm
fabs.h a1          /* 单寄存器绝对索引 */
fabs.h t#1         /* 单寄存器相对索引 */
fabs.s a1          /* 单精度浮点操作数，可使用.d,.s,.h */
fabs.s t#1         /* 单精度浮点操作数，可使用.d,.s,.h */
fabs.s a1,->a2     /* 指令输出到私有寄存器 */
fabs.s t#1,->a2    /* 指令输出到私有寄存器 */
fabs.d a1,=>a2     /* 指令输出到全局寄存器 */
fabs.d t#1,=>a2    /* 指令输出到全局寄存器 */
``` -->

## 备注

本指令属于[标准指令扩展](../../instset/standardInstrs.md)，只能用于浮点块指令块体中。
