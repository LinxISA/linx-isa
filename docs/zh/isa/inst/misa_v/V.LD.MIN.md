# V.LD.MIN

## 说明

内存加载双字·取最小值(*Load Doubleword Minimum*)<br>
本指令执行如下的原子操作：从左源寄存器指向的内存位置原子性地加载 64 位数据，与右源寄存器的 64 位数据进行**最大值比较**，将结果原地写回内存，并将加载的原始数据写到目的寄存器中。

本指令可以选择带有 **Load-Acquire**，**Store-Release** 语义。

## 汇编语法

```asm
v.ld.min<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL<.reuse><.ud>], SrcL<.reuse>.{T}, ->Dst.d
```

## 汇编符号

- 指令可以带有如下可选后缀：
    - **.aq**：表示带有Load-Acquire的同步语义。
    - **.rl**：表示带有Store-Release的同步语义。
    - **.f**：表示内存访问发生在远端Cache中。
    - 其他后缀（例如.aqrl）为以上基础后缀的组合形式。
- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **.ud**: 左源寄存器后缀，表示其作为 64 位操作数。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：操作数的数据类型，可选类型包括sd,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引vt/vu/vm/vn等向量寄存器。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![V.LD.MIN](../../../figs/bitfield/svg/Instruction_64bit/V.LD.MIN.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
integer {m, srcWidth1, sign1} = DecodeINT(SrcL);
integer {n, srcWidth2, sign2} = DecodeINT(SrcR); 
integer {d, dstWidth} = DecodeDst(RegDst);

// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    Atomic {
        bits(64) address = V[m, srcWidth1, laneid];
        bits(64) operand = V[n, srcWidth2, laneid];

        bits(64) oldValue = Mem[address][63:0];
        bits(64) newValue;

        if sign2 == 0 then
            newValue = (operand <(u) oldValue ? operand : oldValue);  // 无符号比较
        else 
            newValue = (operand <(s) oldValue ? operand : oldValue);  // 有符号比较

        Mem[address] = newValue;
        V[d, dstWidth, laneid] = oldValue;
    }
}
```

## 注意事项

1. 默认内存加载的数据与右源操作数的符号性相同。
2. 如果寄存器位宽不满足本指令的要求，那么硬件不保证执行结果的正确性（执行结果不可知）。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的标量版本请见[L.LD.MIN](../misa_l/L.LD.MIN.md)。
