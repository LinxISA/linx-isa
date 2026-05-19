# V.REV

## 说明

翻转(*Reverse*)<br>
在源操作数的每个 `M` 位范围内以 `N` 位为单位进行高低位翻转，结果写到目的寄存器中。

## 汇编语法

```asm
    v.rev SrcL<.reuse>.{T}, M, N, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指令操作数的整数类型标识，包括sh,sw,sd,uh,uw,ud。
- **M**：表示每次进行翻转操作的操作域位宽，合法取值包括：{2, 4, 8, 16, 32, 64}。该参数减1后编码于immr字段。
- **N**：表示每个操作域内进行翻转操作的单位，合法取值包括：{1, 2, 4, 8, 16, 32}。该参数编码于imml字段。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：寄存器的位宽标识，包括h,w,d等。。

!!! note "注意事项！"

    M和N的取值必须小于源寄存器位宽，否则硬件执行结果不可知。

## 编码格式

![V.REV](../../../figs/bitfield/svg/Instruction_64bit/V.REV.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)
```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srcwidth}  = DecodeINT(SrcL);
    integer {d, dstwidth} = DecodeDst(RegDst); 
    integer M = UInt(immr) + 1;
    integer N = UInt(imml);

    // 以下情况报非法指令
    if M isnot in range{2, 4, 8, 16, 32, 64} then Exception(EC_ILLEGAL);
    if N isnot in range{1, 2, 4, 8, 16, 32}  then Exception(EC_ILLEGAL);
    if M <= N                                then Exception(EC_ILLEGAL);  

    if (pmask[laneid] == 1) {
        bits(srcwidth) operand = V[m, srcwidth, laneid];
        bits(srcwidth) result;

        integer fieldnum = 64 / M;
        integer elementnum = M / N;
        integer idx = 0;
        integer ridx;
        for i = 0 to (fieldnum - 1) {
            ridx = idx + (elementnum - 1) * N;
            for j = 0 to (elementnum - 1) {
                result[ridx+(N-1): ridx] = operand[idx+(N-1) : idx];
                idx += N;
                ridx -= N;
            }
        }
        V[d, dstwidth, laneid] = result;  // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
