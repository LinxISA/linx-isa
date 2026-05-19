# FCVTZ

## 说明

浮点数转换(*Floating-point Convert, rounding toward Plus infinity*)  
将输入寄存器中浮点数转换为有符号或无符号整数，使用默认的 **RTZ舍入模式**，结果写入到目的寄存器中。

## 汇编语法

```
    fcvtz.{srcT2dstT} SrcL, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：输入寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **srcT**：表达源数据类型，范围包括FB,FH,FS,FD等。
- **dstT**：表达目标数据类型，范围包括UD,UW,UH,UB,SD,SW,SH,SB。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![FCVTZ](../../../figs/bitfield/svg/Instruction_32bit/FCVTZ.svg)

SrcType字段编码如下表：

| SrcType | 数据格式 | 说明 |
|---------|---------|------|
| 0 | FD | 64bit双精度浮点数 |
| 1 | FS | 32bit单精度浮点数 |
| 2 | FH | 16bit半精度浮点数 |
| 3 | FB | 8bit低精度浮点数 |

DstType字段编码如下表：

| DstType | 数据格式 | 说明 |
|---------|---------|------|
| 0 | UD | 操作数为64bit无符号整型数据 |
| 1 | UW | 操作数为32bit无符号整型数据 |
| 2 | UH | 操作数为16bit无符号整型数据 |
| 3 | UB | 操作数为8bit无符号整型数据  |
| 4 | SD | 操作数为64bit有符号整型数据 |
| 5 | SW | 操作数为32bit有符号整型数据 |
| 6 | SH | 操作数为16bit有符号整型数据 |
| 7 | SB | 操作数为8bit有符号整型数据  |
| >7 | reserve | 保留 |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    DataType srcType, dstType;
    RoundingMode rmode = FPRounding_ZERO;

    case SrcType of:
        when 0 then srcType = FP64;
        when 1 then srcType = FP32;
        when 2 then srcType = FP16;
        when 3 then srcType = FP8;

    case DstType of:
        when 0 then dstType = UINT64;
        when 1 then dstType = UINT32;
        when 2 then dstType = UINT16;
        when 3 then dstType = UINT8;
        when 4 then dstType = INT64;
        when 5 then dstType = INT32;
        when 6 then dstType = INT16;
        when 7 then dstType = INT8;
        otherwise undefined;        # 其他编码未定义
        
    bits(64) operand = R[m, 64];
    bits(64) result = FPConvert(operand, srcType, dstType, rmode);

    R[d, 64] = result;
```

<!-- ## 汇编索引模式

```asm
fcvt.d a1.sl          /* 单寄存器绝对索引 */
fcvt.d t#1.sl         /* 单寄存器相对索引 */
fcvt.s a1.h           /* 半精度浮点数转换为单精度浮点数 */
fcvt.d t#1.s          /* 单精度浮点数转换为双精度浮点数 */
fcvt.sl a1.d           /* 双精度浮点数转换为有符号长整型 */
fcvt.d t#1.ul          /* 无符号长整型转换为双精度浮点数 */
fcvt.sl a1.uw           /* 无符号整型转换为有符号长整型 */
fcvt.d t#1.uw          /* 无符号整型转换为双精度浮点数 */
fcvt.s a1.sw,->a2     /* 指令输出到私有寄存器 */
fcvt.s t#1.sw,->a2    /* 指令输出到私有寄存器 */
fcvt.d a1.sw,=>a2     /* 指令输出到全局寄存器 */
fcvt.d t#1.sw,=>a2    /* 指令输出到全局寄存器 */ 
```-->

## 备注

本指令属于[标准指令扩展](../../instset/standardInstrs.md)，只能用于浮点块指令块体中。
