# V.ADD

## 说明

加(*Add*)<br>
左源寄存器中指定数据类型的操作数和可选移位的右源寄存器中指定数据类型的操作数相加，结果写入目的寄存器。

## 汇编语法

```asm
    v.add SrcL<.reuse>.{T}, SrcR<.reuse>.{T}<.neg><<<shamt>, ->RegDst.{W}, sat
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。SrcR可以选择带后缀，分别表示：
    - **.neg**：将右源操作数按位取反加一。
    - **shamt**：表示右源操作数逻辑左移位数，范围[0, 31]。左移0位默认缺省。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。
- **sat（saturation）**：支持饱和计算的标志。

## 编码格式

![V.ADD](../../../figs/bitfield/svg/Instruction_64bit/V.ADD.svg)

其中，SrcRType域编码如下：

|  SrcRType  |  汇编标识  |  解释                       |
|-----------|-----------|-----------------------------|
|  00  |  无   |  无格式转换                        |
|  01  |  无   |  保留（reserve）  |
|  10  |  无   |  保留（reserve）  |
|  11  |  .neg  |  negative，将操作数位取反加一  |

饱和计算sat位编码：

| sat | 含义 |
|------|-------|
| 0 | 无饱和计算（默认） |
| 1 | 启用饱和计算 |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 转换为十进制数：[UInt()](../LibPseudoCode.md#locationA)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)
- 对操作数位取反加一：[Negative()](../LibPseudoCode.md)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++) {
    integer {m, srcwidth0} = DecodeINT(SrcL);
    integer {n, srcwidth1} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 
    integer shift_amount = UInt(shamt);

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srcwidth0, laneid];
        bits(64) operand2 = V[n, srcwidth1, laneid];

        if SrcRType == 3 then
            operand2 = Negative(operand2);

        bits(64) result = operand1 + (operand2 << shift_amount);

        if (sat == 1) {
            if (result >= MaxValue) result = MaxValue;
            if (result <= MinValue) result = MinValue;
        }
        V[d, dstwidth, laneid] = result;  // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane结果为零
    }
}
```

## 注意事项

1. 结果忽略算数溢出。

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
