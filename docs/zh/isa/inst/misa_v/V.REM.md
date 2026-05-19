# V.REM

## 说明

求余数(*Remainder*)<br>
计算左源寄存器中指定数据类型的操作数除以右源寄存器中指定数据类型的操作数，结果向零舍入，`余数` 写入目的寄存器。

使用本指令应保证源操作数符号性相同，否则不保证计算结果的正确性。

## 汇编语法

```asm
    v.rem SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.REM](../../../figs/bitfield/svg/Instruction_64bit/V.REM.svg)

## 执行方式


- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    bit sign_l = SrcL[9];
    bit sign_r = SrcR[9];
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if sign_l != sign_r then undefined;

    if (pmask[laneid] == 1) {
        bits(64) operand1 = V[m, srctype1, laneid];
        bits(64) operand2 = V[n, srctype2, laneid];
        bits(64) result;

        if sign_r == 0 then   // 无符号运算
            result = operand1 % (u) operand2;
        else                  // 有符号运算
            result = operand1 % (s) operand2;
        
        V[d, dstwidth, laneid] = result;   // 根据输出寄存器位宽对结果进行截断
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

!!! note "注意"
  
    余数的符号与被除数的符号相同。  
    如果发生除法溢出情况，余数等于"0"。  
    如果发生除以零的情况，余数等于被除数。

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
