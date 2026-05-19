# V.SD.ADD

## 说明

存储双字·相加(*Store Doubleword Add*)<br>
本指令执行如下的原子操作：从左源寄存器指向的内存位置原子性地加载 64 位数据，与右源寄存器的 64 位数据**相加**，将结果原地写回内存。

本指令可以选择带有 **Store-Release** 语义。

## 汇编语法

```asm
v.sd.add<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL<.reuse><.ud>], SrcR<.reuse>.{T}
```

## 汇编符号

- 指令可以带有如下可选后缀：
    - **.rl**：表示带有Store-Release的同步语义。
    - **.f**：表示内存访问发生在远端Cache中。
    - **.rd**：表示执行Store Reduce操作。
    - 其他后缀（例如.rlf）为以上基础后缀的组合形式。
- **SrcL**：左源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **.ud**: 左源寄存器后缀，表示其作为 64 位操作数。
- **SrcR**：右源寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：操作数的类型标识，可选类型包括sd,ud等。

## 编码格式

![V.SD.ADD](../../../figs/bitfield/svg/Instruction_64bit/V.SD.ADD.svg)

寄存器字段的编解码方式请见[长指令编码](../../blockIntro/vecinstrs/instIntro.md)小节。

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;   // lane掩码
integer {m, srcWidth1} = DecodeINT(SrcL);
integer {n, srcWidth2} = DecodeINT(SrcR); 
integer {d, dstWidth} = DecodeDst(RegDst);

// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    Atomic {
        bits(64) address = V[m, srcWidth1, laneid];
        bits(64) operand = V[n, srcWidth2, laneid];

        bits(64) oldValue = Mem[address][63:0];
        bits(64) newValue = oldValue + operand;

        Mem[address] = newValue;
    }
}
```

## 注意事项

如果寄存器位宽不满足本指令的要求，那么硬件不保证执行结果的正确性（执行结果不可知）。

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的标量版本请见[L.SD.ADD](../misa_l/L.SD.ADD.md)。
