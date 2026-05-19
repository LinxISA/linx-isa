# L.ICVT

## 说明

整型转换(*Integer Convert*)<br>
将源寄存器中指定类型的整数转换为目标类型的整数，并将转换结果写入目的寄存器中。

## 汇编语法

```asm
    l.icvt.{st2dt} SrcL.<T>, SrcR.<T>, ->RegDst.d
```

## 汇编符号

- **st**：指定源操作数的数据类型，编码于SrcType字段。
- **dt**：指定目标操作数的数据类型，编码于DstType字段。
- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。
- **rm（rounding mode）**：舍入模式的标记符。
- **sat（saturation）**：支持饱和计算的标志。

## 编码格式

![L.ICVT](../../../figs/bitfield/svg/Instruction_64bit/L.ICVT.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

SrcType和DstType字段编码方式如下：

| 编码 | 原格式（SrcType） | 目标格式（DstType） |
|----------|---------|-----------------|
| 5'b00000 | u64     | u64     |
| 5'b00001 | u32     | u32     |
| 5'b00010 | u16     | u16     |
| 5'b00011 | u8      | u8      |
| 5'b00100 | u4x2    | u4x2    |
| 5'b00101 | u16x2   | u16x2   |
| 5'b00110 | u8x4    | u8x4    |
| 5'b00111 | reserve | reserve |
| 5'b01000 | s64     | s64     |
| 5'b01001 | s32     | s32     |
| 5'b01010 | s16     | s16     |
| 5'b01011 | s8      | s8      |
| 5'b01100 | s4x2    | s4x2    |
| 5'b01101 | s16x2   | s16x2   |
| 5'b01110 | s8x4    | s8x4    |
| 5'b01111 | reserve | reserve |
| others | reserve   | reserve |

舍入模式rm字段编码：

| 编码 | 舍入模式 | 含义 |
|-----|----------|-----------|
| 0 | **RNONE** | No Rounding（不指定舍入模式，由硬件/实现决定默认行为）可缺省 |
| 1 | **RNE** | Round to Nearest, ties to Even（向最近偶数舍入；最常见） |
| 2 | **RTZ** | Round Toward Zero（向零舍入，截断小数部分） |
| 3 | **RDN** | Round Down（向负无穷舍入） |
| 4 | **RUP** | Round Up（向正无穷舍入） |
| 5 | **RNA** | Round to Nearest, ties Away from Zero（远离零） |
| 6 | **RTO** | Round to Odd（向最近奇数舍入） |
| 7 | **RHB** | Hybrid Rounding（混合舍入模式） |
| >7 | reserve | 保留 |

饱和计算sat位编码：

| sat | 含义 |
|------|-------|
| 0 | 无饱和计算（默认） |
| 1 | 启用饱和计算 |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 数据类型转换：[Convert()](../LibPseudoCode.md)

```c
enum DataType {
    U64, U32, U16, U8, U4x2, U16x2, U8x4,
    S64, S32, S16, S8, S4x2, S16x2, S8x4
};

integer {m, srcwidth} = DecodeINT(SrcL);
integer {n, srcwidth} = DecodeINT(SrcR);
integer {d, dstWidth} = DecodeDst(RegDst);

DataType srcT = SrcType;
DataType dstT = DstType;

bits(srcwidth) operand0 = SREG[m, srcwidth];
bits(srcwidth) operand1 = SREG[n, srcwidth];
bits(dstwidth) result;
result[dstwidth/2-1, 0]        = FPConvert((srcT)operand0, dstT);
result[dstwidth-1, dstwidth/2] = FPConvert((srcT)operand1, dstT);

SREG[d, dstWidth] = result;
```

| 源数据格式 | 目标数据格式 | 位宽变化 | 处理方式 |
|-----------|-------------|----------|--------------------------|
| 有符号数  |  有符号数/无符号数  | 64 > 64 | 截断，结果作为有符号数/无符号数  |
| 有符号数  |  有符号数/无符号数  | 64 = 64 | 空操作NOP/最高有效位改为数值位  |
| 有符号数  |  有符号数/无符号数  | 64 < 64 | 符号位扩展，结果作为有符号数/无符号数  |
| 无符号数  |  有符号数/无符号数  | 64 > 64 | 截断，结果作为有符号数/无符号数  |
| 无符号数  |  有符号数/无符号数  | 64 = 64 | 最高有效位作为符号位/空操作NOP  |
| 无符号数  |  有符号数/无符号数  | 64 < 64 | 零扩展，结果作为有符号数/无符号数  |

## 转换模式

1. `单元素->单元素` 转换示例：
```asm
l.icvt.u82u16 t#1.ub, ->t.d
```

2. `双元素->双元素` 转换示例：
```asm
l.icvtf.u16x22s16x2 t#1.uw, ->t.d
```

3. `四元素->四元素` 转换示例：
```asm
l.icvtf.u8x42s8x4 t#1.uw, ->t.d
```

4. `单元素 + 单元素 ->双元素` 转换示例：
```asm
l.icvtf.u162s16x2 t#1.uh, t#2.uh, ->t.d
```

5. `双元素 + 双元素 ->四元素` 转换示例：
```asm
l.icvtf.u16x22u8x4 t#1.uw, t#1.uw, ->t.d
```

## 注意事项

st与T表达的数据位宽必须保持一致，T表达输入的主格式，st表达具体格式。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.ICVT](../misa_v/V.ICVT.md)。
