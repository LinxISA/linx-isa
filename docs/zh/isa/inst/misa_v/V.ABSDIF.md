# V.ABSDIF

## 说明

整数绝对差值(*Integer Absolute Difference*)<br>
计算左源寄存器和右源寄存器中整型数据的差值的绝对值，并将结果写入目的寄存器。

`vlen` 字段控制指令对 lane 内多个元素的同时操作能力，允许单条指令在一个 lane 内并行处理多个数据元素。

## 汇编语法

```asm
    v.absdif SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}, sat
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb, sh, sw, sd, ub, uh, uw, ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。
- **sat（saturation）**：支持饱和计算的标志。

## 编码格式

![V.ABSDIF](../../../figs/bitfield/svg/Instruction_64bit/V.ABSDIF.svg)


`vlen` 字段控制指令对 lane 内多个元素的同时操作能力，允许单条指令在一个 lane 内并行处理多个数据元素。

饱和计算sat位编码：

| sat | 含义 |
|------|-------|
| 0 | 无饱和计算（默认） |
| 1 | 启用饱和计算 |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量

// vlen 控制每个 lane 内的有效元素数量
// vlen=0: 1 元素/lane, vlen=1: 2 元素/lane, vlen=2: 4 元素/lane
integer elem_per_lane = (vlen == 0) ? 1 : (vlen == 1) ? 2 : (vlen == 2) ? 4 : 1;
integer elem_width = srcwidth / elem_per_lane;

for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR);
    integer {d, dstwidth} = DecodeDst(RegDst);

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srctype1, laneid];
        bits(64) operand2 = V[n, srctype2, laneid];
        bits(64) diff = operand1 - operand2;
        bits(64) result = (diff < 0) ? -diff : diff;

        if (sat == 1) {
            if (result >= MaxValue) result = MaxValue;
            if (result <= MinValue) result = MinValue;
        }
        V[d, dstwidth, laneid] = result;
    }
    else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
