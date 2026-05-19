# V.QPUSH

## 说明

入队列(*Push to Queue*)<br>
将 右源操作数 push 到左源操作数指定的GQM队列中(默认push到队尾)，并将执行结果写入到目的寄存器。

## 汇编语法

```asm
    v.qpush SrcL<.reuse>.ud, SrcR<.reuse>.ud, ->Dst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **ud**：表示操作数为64位整型数据。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。数据编码如下：
    - [9:0] 表示写入后队列中的剩余单元数。
    - [63:62] 0表示写入成功，1表示队列满，2表示数据破坏，3保留。
- **.d**：表示目的寄存器的位宽为64位。

## 编码格式

![V.QPUSH](../../../figs/bitfield/svg/Instruction_64bit/V.QPUSH.svg)

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
        bits(64) address = V[m, srctype1, laneid];
        bits(64) operand = V[n, srctype2, laneid];
        integer remainNums, state;

        {remainNums, state} = GQM[address].push_back(operand);  // push到队尾

        bit(64) result;              //执行的结果
        result[9:0] = remainNums;    //表示写入后队列中的剩余单元数。
        result[63:62] = state;       //0表示写入成功，1表示队列满，2表示数据破坏，3保留。

        V[d, dstwidth, laneid] = result;
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
