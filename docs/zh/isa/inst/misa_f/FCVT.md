# FCVT

## 说明

浮点数转换(*Floating-point Convert*)  
将输入寄存器中浮点型数据转换为目标类型的精度，舍入模式由系统寄存器[CSTATE](../../register/ssr/CSTATE.md)确定，结果写入到目的寄存器中。

## 汇编语法

```
    fcvt.{srcT2dstT} SrcL, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：输入寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **srcT**：表达源数据类型，范围包括FB,FH,FS,FD等。
- **dstT**：表达目标数据类型，范围同srcT。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![FCVT](../../../figs/bitfield/svg/Instruction_32bit/FCVT.svg)

SrcType和DstType域编码如下表：

| 编码 | 数据格式 | 说明 |
|------|---------|------|
| 0 | FD | 64bit双精度浮点数 |
| 1 | FS | 32bit单精度浮点数 |
| 2 | FH | 16bit半精度浮点数 |
| 3 | FB | 8bit低精度浮点数 |
| >3 | reserve | 保留 | 

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    DataType srcType, dstType;

    RoundingMode rmode;
    if SSR[CSTATE].RV == 1 then rmode = SSR[CSTATE].FRM;
    else rmode = FPRounding_TIEEVEN

    case SrcType of:
        when 0 then srcType = FP64;
        when 1 then srcType = FP32;
        when 2 then srcType = FP16;
        when 3 then srcType = FP8;

    case DstType of:
        when 0 then dstType = FP64;
        when 1 then dstType = FP32;
        when 2 then dstType = FP16;
        when 3 then dstType = FP8;
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

## 舍入模式

此指令使用的舍入模式由系统寄存器[CSTATE](../../register/ssr/CSTATE.md)的FRM字段决定，如果CSTATE中舍入模式是无效的，则使用默认的RNE模式。

## 备注

本指令属于[标准指令扩展](../../instset/standardInstrs.md)，只能用于浮点块指令块体中。
