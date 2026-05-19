# V.CSEL

## 说明

条件选择(*Conditional Select*)<br>
根据条件选择寄存器内条件，选择左源寄存器或者右源寄存器的值写入目的寄存器中。条件为**True**，选择左源寄存器；条件为**False**，选择右源寄存器。

## 汇编语法

```asm
    v.csel SrcP<.reuse>.{T}, SrcL<.reuse>.{T}, SrcR<.reuse>.{T}<.neg>, ->RegDst.{W}
```

## 汇编符号

- **SrcP**：条件选择寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。SrcR可以选择带后缀：
    - **.neg**：将右源操作数按位取反加一。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.CSEL](../../../figs/bitfield/svg/Instruction_64bit/V.CSEL.svg)

其中，SrcRType域编码如下：

|  SrcRType  |  汇编标识  |  解释                       |
|-----------|-----------|-----------------------------|
|  00  |  无   |  无格式转换                        |
|  01  |  无   |  保留（reserve）  |
|  10  |  无   |  保留（reserve）  |
|  11  |  .neg  |  negative，将操作数位取反加一  |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {c, srctype3} = DecodeINT(SrcP); 
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srctype1, laneid];
        bits(64) operand2 = V[n, srctype2, laneid];
        bits(64) condition = V[c, srctype3, laneid];

        if (SrcRType == 3)
            operand2 = Negative(operand2);

        bits(64) result = (condition != 0 ? operand1 : operand2);
        
        V[d, dstwidth, laneid] = result;  // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

当条件选择寄存器是向量寄存器时，图示如下：

![CSEL](../../../figs/isa/inst/csel1.png){ width="800" }

当条件选择寄存器是标量寄存器时，图示如下：

![CSEL](../../../figs/isa/inst/csel2.png){ width="800" }

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
