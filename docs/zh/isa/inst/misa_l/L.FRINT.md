# L.FRINT

## 说明

浮点舍入到整数(*Floating-point Round to Integral*)<br>
将源寄存器中的浮点数按指定的舍入模式舍入到最接近的整数值，结果保持浮点格式写入目的寄存器。本指令仅对浮点尾数进行舍入操作，不改变数据类型。

## 汇编语法

```asm
    l.frint SrcL.<T>, ->RegDst.d, rm, sat
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。
- **rm（rounding mode）**：舍入模式的标记符。
- **sat（saturation）**：支持饱和计算的标志。

## 编码格式

![L.FRINT](../../../figs/bitfield/svg/Instruction_64bit/L.FRINT.svg)

舍入模式rm字段编码：

| 编码 | 舍入模式 | 含义 |
|-----|----------|-----------|
| 0 | **RNONE** | No Rounding（不指定舍入模式，由硬件/实现决定默认行为）可缺省 |
| 1 | **RNE** | Round to Nearest, ties to Even（向最近偶数舍入） |
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

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)

```c
    integer {m, srcWidth} = DecodeFP(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst);

    bits(srcWidth) operand = SREG[m, 64];
    bits(64) result;
    switch (rm) {
        case RNE:  result = round_nearest_even(operand);  break;
        case RTZ:  result = round_to_zero(operand);       break;
        case RDN:  result = round_down(operand);          break;
        case RUP:  result = round_up(operand);            break;
        case RNA:  result = round_nearest_away(operand);  break;
        case RTO:  result = round_to_odd(operand);        break;
        case RHB:  result = round_hybrid(operand);        break;
        default:   result = operand;                      break;
    }

    if (sat == 1) {
        if (result >= MaxValue) result = MaxValue;
        if (result <= MinValue) result = MinValue;
    }
    SREG[d, dstWidth] = result;
```

## 注意事项

- 本指令与 [L.FCVT](L.FCVT.md) 的区别在于：L.FRINT 保持浮点类型不变，仅对尾数进行舍入；L.FCVT 在不同浮点类型之间进行完整格式转换。
- 与 [L.FCVTI](L.FCVTI.md) 的区别在于：L.FRINT 结果为浮点型整数（如 4.0）；L.FCVTI 结果为真正的整型（如 4）。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FRINT](../misa_v/V.FRINT.md)。
