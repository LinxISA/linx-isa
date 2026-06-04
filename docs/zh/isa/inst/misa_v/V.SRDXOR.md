# V.SRDXOR

## 说明

子组按位异或归约（*Sub-group Reduce Bitwise XOR*）<br>
将当前Group内的lane划分为若干子组（sub-group），在每个子组内对源寄存器的整数值执行按位异或归约，结果广播（broadcast）到该子组的所有lane中。子组大小由SrcR标量寄存器指定。

## 汇编语法

```asm
    v.srdxor SrcL<.reuse>.{T}, SrcR<.reuse>, ->RegDst<.W>
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **SrcR**：范围寄存器，仅支持标量寄存器，用于指示子组大小（sub-group size）。当SrcR为zero寄存器时，表示按整个Group范围执行归约操作。SrcR指示的范围必须为2的整数次幂且不允许大于Group size（64），否则执行行为未定义。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器。当执行workgroup归约（SrcR=0）时，支持标量寄存器或向量寄存器；当执行子组归约时，必须为向量寄存器，结果广播到子组内所有lane。
- **.W**：指定目的寄存器的位宽，由数据类型隐式决定。

## 编码格式

（待补充）

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth} = DecodeINT(SrcL);
integer {d, dstwidth} = DecodeDst(RegDst);
integer subgroup_size = V[srcr_reg, 64];

if (subgroup_size == 0) then
    subgroup_size = lanenum;

bits(64) pmask = P;
integer num_subgroups = lanenum / subgroup_size;

for (sg_id = 0; sg_id < num_subgroups; sg_id++) {
    bits(64) result = 0;

    if 32 <= d and d <= 35 then
        result = V[d, dstwidth];

    integer sg_start = sg_id * subgroup_size;
    integer sg_end   = sg_start + subgroup_size;

    for (laneid = sg_start; laneid < sg_end; laneid++) {
        if (pmask[laneid] == 1) {
            bits(64) operand = V[m, srcwidth, laneid];
            result ^= operand;
        }
    }

    for (laneid = sg_start; laneid < sg_end; laneid++) {
        if (pmask[laneid] == 1)
            V[d, dstwidth, laneid] = result;
        else
            V[d, dstwidth, laneid] = 0;
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
本指令为0.57版本新增的子组归约指令，旧版V.RDXOR（无范围参数）仍被保留。
