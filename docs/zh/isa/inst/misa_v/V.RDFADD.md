# V.RDFADD

## 说明

浮点加归约(*Reduce Floating-point Add*)<br>
将当前Group内所有Lane中源寄存器的浮点数相加，结果写到目的寄存器中。如果目的寄存器是形参RO寄存器，结果需要与该寄存器中原始值相加后再写出。

## 汇编语法

```asm
    v.rdfadd SrcL<.reuse>.{T}, ->Dst.d
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器，可以索引块内的RO寄存器或T/U寄存器。
- **.d**：表示目的寄存器为64位双字宽。

## 编码格式

![V.RDFADD](../../../figs/bitfield/svg/Instruction_64bit/V.RDFADD.svg)

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth} = DecodeINT(SrcL);
integer {d, dstwidth} = DecodeDst(RegDst);
bits(64) sum = 0;

// 目的寄存器是形参RO寄存器则累加
if 32 <= d and d <= 35 then
    sum = V[d, dstwidth];

bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    bits(64) operand = V[m, srcwidth, laneid];
    sum += (srctype)operand;
}

V[d, dstwidth] = sum;
```

![rdfadd](../../../figs/isa/inst/rdfadd.png){ width="800" }

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
