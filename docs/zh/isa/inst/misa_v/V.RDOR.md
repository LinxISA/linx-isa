# V.RDOR

## 说明

或归约(*Reduce Or*)<br>
对当前Group内的lane进行按位或归约操作。支持两种归约模式：<br>
- **Workgroup reduce**：当 SrcR 与 imm10 共同指示整个 Group 范围时，将 Group 内所有 lane 的源寄存器值进行按位或，结果写到目的寄存器中。如果目的寄存器是形参RO寄存器，结果需要与该寄存器中原始值按位或后再写出。<br>
- **Sub-group reduce**：当 SrcR 与 imm10 共同指示子组范围时，将 Group 划分为若干子组，在每个子组内独立执行按位或归约，结果广播到该子组的所有 lane 中。

## 汇编语法

```asm
    v.rdor SrcL<.reuse>.{T}, SrcR, imm10, ->RegDst<.W>
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **SrcR**：范围寄存器（标量），与 imm10 共同指示 sub-group 归约范围。当 SrcR 与 imm10 共同指示整个 Group 范围时按 workgroup reduce 执行。
- **imm10**：立即数范围参数，与 SrcR 共同指示 sub-group 归约范围。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器。workgroup reduce 时可为标量或向量寄存器；sub-group reduce 时必须为向量寄存器，结果 broadcast 到子组内所有 lane。
- **.W**：指定目的寄存器的位宽，由数据类型隐式决定。

## 编码格式

![V.RDOR](../../../figs/bitfield/svg/Instruction_64bit/V.RDOR.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth} = DecodeINT(SrcL);
integer {d, dstwidth} = DecodeDst(RegDst);
integer subgroup_size = ComputeRange(SrcR, imm10);

// SrcR 与 imm10 共同指示整个 Group 范围时按 workgroup reduce
if (subgroup_size >= lanenum) then
    subgroup_size = lanenum;

bits(64) pmask = P;
integer num_subgroups = lanenum / subgroup_size;

for (sg_id = 0; sg_id < num_subgroups; sg_id++) {
    bits(64) result = 0;

    // 目的寄存器是形参RO寄存器则作为初始值
    if 32 <= d and d <= 35 then
        result = V[d, dstwidth];

    integer sg_start = sg_id * subgroup_size;
    integer sg_end   = sg_start + subgroup_size;

    for (laneid = sg_start; laneid < sg_end; laneid++) {
        if (pmask[laneid] == 1) {
            bits(64) operand = V[m, srcwidth, laneid];
            result |= operand;
        }
    }

    // 广播到子组内所有 lane
    for (laneid = sg_start; laneid < sg_end; laneid++) {
        if (pmask[laneid] == 1)
            V[d, dstwidth, laneid] = result;
        else
            V[d, dstwidth, laneid] = 0;
    }
}
```

![rdor](../../../figs/isa/inst/rdor.png){ width = "800"}

!!! note "注意"

    如果源寄存器位宽小于64位，那么只更新源寄存器对应的低位，不影响高位。

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
本指令为0.57版本修改，增加 SrcR 和 imm10 参数以支持 sub-group 归约。
