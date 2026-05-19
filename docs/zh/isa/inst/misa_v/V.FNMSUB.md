# V.FNMSUB

## 说明

浮点数乘减取负(*Floating-point Multiply-Sub Negative*)<br>
将第一个源寄存器和第二个源寄存器的浮点数相乘，用未舍入的积减去第三个源寄存器的浮点数，将舍入后的结果取负后写入目的寄存器。

## 汇编语法

```asm
    v.fnmsub SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, SrcA.{T}, ->RegDst.{W}, rm, sat
```

## 汇编符号

- **SrcL**：源寄存器1，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：源寄存器2，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcA**：源寄存器3，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。
- **rm（rounding mode）**：舍入模式的标记符。
- **sat（saturation）**：支持饱和计算的标志。

## 编码格式

![V.FNMSUB](../../../figs/bitfield/svg/Instruction_64bit/V.FNMSUB.svg)

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
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeFP(SrcL);
    integer {n, srctype2} = DecodeFP(SrcR);
    integer {a, srctype3} = DecodeFP(SrcA); 
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if (srctype1 != srctype2 || srctype1 != srctype3) then undefined;

    if (pmask[laneid] == 1) {
        srctype1 operand1 = V[m, srctype1, laneid];
        srctype2 operand2 = V[n, srctype2, laneid];
        srctype3 operand3 = V[a, srctype3, laneid];
        bits(64) result = - (operand1 * operand2 - operand3);
        
        if (sat == 1) {
            if (result >= MaxValue) result = MaxValue;
            if (result <= MinValue) result = MinValue;
        }
        V[d, dstwidth, laneid] = result;
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
