# V.RDMIN

## 说明

最小值归约(*Reduce Minimum*)<br>
对当前Group内所有Lane中源寄存器的整数比较得到最小值，结果写到目的寄存器中。如果目的寄存器是形参RO寄存器，结果需要与该寄存器中原始值比较得到较小值后再写出。

## 汇编语法

```asm
    v.rdmin SrcL<.reuse>.{T}, ->Dst.d
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器，可以索引块内的RO寄存器或T/U寄存器。
- **.d**：表示目的寄存器为64位双字宽。

## 编码格式

![V.RDMIN](../../../figs/bitfield/svg/Instruction_64bit/V.RDMIN.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth} = DecodeINT(SrcL);
integer {d, dstwidth} = DecodeDst(RegDst);
bits(64) minvalue = MAX_VALUE;  // 初始化为输入类型下最大值

// 目的寄存器是形参RO寄存器则作为初始值
if 32 <= d and d <= 35 then
    minvalue = V[d, dstwidth];

bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    if (pmask[laneid] == 1) {
        bits(64) operand = V[m, srcwidth, laneid];
        minvalue = min(minvalue, operand);
    }
}

V[d, dstwidth] = minvalue;
```

![rdmin](../../../figs/isa/inst/rdmin.png){ width = "800"}

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
