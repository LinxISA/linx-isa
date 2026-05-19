# FRECIP

## 说明

浮点数倒数(*Floating-point Reciprocal Value*)  
取源寄存器中低/半/单/双精度浮点数的倒数，即用1.0除以这个浮点数后得到的近似结果，写入到目的寄存器中。

## 汇编语法

```
    frecip.<T> SrcL, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **T**：输入的浮点数精度标识，包括FB,FH,FS,FD 4种。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![FRECIP](../../../figs/bitfield/svg/Instruction_32bit/FRECIP.svg)

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
- 求浮点数倒数：[FRECIP()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);

    case SrcType of:
        when 00 then DataType = FP64;
        when 01 then DataType = FP32;
        when 10 then DataType = FP16;
        when 11 then DataType = FP8;

    DataType operand = R[m, 64];
    bits(64) result = FRECIP(operand);
    
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

!!! note "注意"

    当源操作数为0时，该指令会触发除零异常(DZ)。

## 舍入模式

当计算结果无法精确表达需要进行舍入时，计算结果的舍入模式由[CSTATE](../../register/ssr/CSTATE.md)寄存器的FRM域段决定。如果FRM字段是无效的，那么默认采用**RNE**模式对结果进行舍入。

## 备注

本指令属于[标准指令扩展](../../instset/standardInstrs.md)，只能用于浮点块指令块体中。
