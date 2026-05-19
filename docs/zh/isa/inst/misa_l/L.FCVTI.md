# L.FCVTI

## 说明

浮点型向整型转换(*Floating-point Convert to Integer*)<br>
将源寄存器中指定类型的浮点数转换为目标类型的整数，并将转换结果写入目的寄存器。

## 汇编语法

```asm
    l.fcvti.{st2dt} SrcL.<T>, SrcR.<T>, ->RegDst.d
```

## 汇编符号

- **st**：表达源操作数的数据类型，编码于SrcType字段。
- **dt**：表达目标操作数的数据类型，编码于DstType字段。
- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。
- **rm（rounding mode）**：舍入模式的标记符。
- **sat（saturation）**：支持饱和计算的标志。

## 编码格式

![L.FCVTI](../../../figs/bitfield/svg/Instruction_64bit/L.FCVTI.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

SrcType和DstType字段编码方式如下：

| 编码 | 原格式（SrcType） | 目标格式（DstType） | 编码 | 原格式（SrcType） | 目标格式（DstType） |
|------|--------------|-------------------|------|--------------|-------------------|
| 5'b00000 | fp64   | u64     | 5'b10000 | fp16x2  | reserve |
| 5'b00001 | fp32   | u32     | 5'b10001 | bf16x2  | reserve |
| 5'b00010 | tf32   | u16     | 5'b10010 | e4m3x4  | reserve |
| 5'b00011 | hf32   | u8      | 5'b10011 | e5m2x4  | reserve |
| 5'b00100 | fp16   | u4x2    | 5'b10100 | e4m3x2  | reserve |
| 5'b00101 | bf16   | u16x2   | 5'b10101 | e5m2x2  | reserve |
| 5'b00110 | hif8   | u8x4    | 5'b10110 | e6m2x2  | reserve |
| 5'b00111 | e4m3   | reserve | 5'b10111 | reserve | reserve |
| 5'b01000 | e5m2   | s64     | 5'b11000 | reserve | reserve |
| 5'b01001 | e3m2   | s32     | 5'b11001 | reserve | reserve |
| 5'b01010 | e2m3   | s16     | 5'b11010 | reserve | reserve |
| 5'b01011 | e2m1x2 | s8      | 5'b11011 | reserve | reserve |
| 5'b01100 | e1m2x2 | s4x2    | 5'b11100 | reserve | reserve |
| 5'b01101 | hif4x2 | s16x2   | 5'b11101 | reserve | reserve |
| 5'b01110 | e8m0   | s8x4    | 5'b11110 | reserve | reserve |
| 5'b01111 | e6m2   | reserve | 5'b11111 | reserve | reserve |

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

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 数据类型转换：[FPConvert()](../LibPseudoCode.md)

```c
enum SrcDataType {
    FP64, FP32, TF32, HF32, FP16, BF16, HiF8, E4M3, 
    E5M2, E3M2, E2M3, E2M1x2, E1M2x2, HIF4x2, E8M0, E6M2,
    FP16x2, BF16x2, E4M3x4, E5M2x4, E4M3x2, E5M2x2, E6M2x2
};
enum DstDataType {
    U64, U32, U16, U8, U4, S64, S32, S16, S8, S4
};

integer {m, srcwidth} = DecodeFP(SrcL);
integer {n, srcwidth} = DecodeFP(SrcR);
integer {d, dstWidth} = DecodeDst(RegDst); 

SrcDataType srcT = SrcType;
DstDataType dstT = DstType;

bits(srcType) operand0 = SREG[m, srcType];
bits(srcType) operand1 = SREG[n, srcType];
bits(dstwidth) result;
result[dstwidth/2-1, 0]        = FPConvert((srcT)operand0, dstT);
result[dstwidth-1, dstwidth/2] = FPConvert((srcT)operand1, dstT);
SREG[d, dstWidth] = result;
```

## 转换模式

1. `单元素->单元素` 转换示例：
```asm
v.fcvti.fp162u16 t#1.fh, ->t.d
```

2. `双元素->双元素` 转换示例：
```asm
v.fcvti.bf16x22u16x2 t#1.fs, ->t.d
```

3. `四元素->四元素` 转换示例：
```asm
v.fcvti.e4m3x42u8x4 t#1.fs, ->t.d
```

4. `单元素 + 单元素 ->双元素` 转换示例：
```asm
v.fcvti.fp162u16x2 t#1.fh, t#2.fh, ->t.d
```

5. `双元素 + 双元素 ->四元素` 转换示例：
```asm
v.fcvti.bf16x22u8x4 t#1.fs, t#1.fs, ->t.d
```

## 注意事项

st与T表达的数据位宽必须保持一致，T表达输入的主格式，st表达具体格式。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FCVTI](../misa_v/V.FCVTI.md)。
