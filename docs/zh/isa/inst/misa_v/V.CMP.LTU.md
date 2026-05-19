# V.CMP.LTU

## 说明

无符号小于比较(*Compare if Less Than by Unsigned*)<br>
无符号比较左源寄存器中指定数据类型的操作数和右源寄存器中指定数据类型的操作数，若左源操作数小于右源操作数则将`1`写入目的寄存器，否则写入`0`。

如果目的寄存器是P寄存器，本指令是一条向量指令，每个lane写P寄存器中对应的1bit。

## 汇编语法

```asm
    v.cmp.ltu SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，索引范围同SrcL。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括ub,uh,uw,ud。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.CMP.LTU](../../../figs/bitfield/svg/Instruction_64bit/V.CMP.LTU.svg)

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)
```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srctype1, laneid];
        bits(64) operand2 = V[n, srctype2, laneid];
        bits(64) result = (operand1 <(u) operand2 ? 1 : 0);
        
        V[d, dstwidth, laneid] = result;  // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
