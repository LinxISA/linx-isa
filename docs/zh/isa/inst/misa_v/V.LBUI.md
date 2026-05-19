# V.LBUI

## 说明

立即数偏移·无符号字节加载 (*Load Unsigned Byte with Immediate Offset*)<br>
本指令用于从内存或Tile寄存器中读取 `一个字节` 的数据写入目的寄存器，并且支持Group内地址连续访问和不连续访问两种寻址方式：

1. 不保证地址连续：由 **基址寄存器** 加 **有符号立即数偏移** 计算得到地址。
2. 保证地址连续：由 **基址寄存器** 加 **有符号立即数偏移** 和 **LC0寄存器** 计算得到地址，并且要求基址寄存器必须是标量寄存器或者Tile类型的形参寄存器。

## 汇编语法

```asm
v.lbui<.local> [SrcL<.reuse><.ud>, <lc0,> simm], ->RegDst.{W}
```

## 汇编符号

- **local**：表示访问Tile寄存器的空间，缺省表示访问内存空间。
- **SrcL**：基址寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **lc0**：块内私有的Lane Counter 0寄存器。可选，地址连续时使用。
- **simm**：有符号立即数偏移，该参数编码于simm24字段。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：目的寄存器的位宽标识，包括b,h,w,d等。

## 编码格式

![V.LBUI](../../../figs/bitfield/svg/Instruction_64bit/V.LBUI.svg)

其中，C和L标志位含义如下：

| C(Continuous) | 含义 | L(local) | 含义 |
|---------------|------|----------|--------|
| 0 | Group内所有lane的地址不一定连续   | 0 | 访问内存空间 |
| 1 | Group内所有lane的地址一定是连续的 | 1 | 访问Tile寄存器空间       |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)
- 将数据符号扩展：[SignExtend()](../LibPseudoCode.md#locationF)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md#locationG)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype}  = DecodeINT(SrcL);
    integer {d, dstwidth} = DecodeDst(RegDst); 

    if (pmask[laneid] == 1) {
        bits(64) base = V[m, srctype, laneid];
        bits(64) offset = SignExtend(simm24);
        bits(64) address = base + offset;

        if C == 1 then    // 连续访存
            bits(64) laneoffset = V[lc0, laneid];
            address += laneoffset;

        bits(8) data = Mem[address][7:0];
        V[d, dstwidth, laneid] = ZeroExtend(data, dstwidth);
    }
    else {
        V[d, dstwidth, laneid] = 0;  // 无效lane中默认写0
    }
}
```

## 指令约束

对于同一个Group内地址连续的使用场景，有如下约束：

- 基址寄存器必须是标量寄存器或Tile形参寄存器，否则报非法指令异常。
- 应保证该指令在[多维模式](../../blockIntro/mem_block/dimmode.md)分组的数据块内使用。

![continuels](../../../figs/isa/inst/continuels.png){ width="600" }

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
