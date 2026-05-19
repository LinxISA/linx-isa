# V.LHU

## 说明

寄存器偏移·无符号半字加载 (*Load Unsigned Halfword with Register Offset*)<br>
本指令用于从内存或Tile寄存器中读取 `两个字节` 的数据写入目的寄存器，并且支持Group内地址连续访问和不连续访问两种寻址方式：

1. 不保证地址连续：地址由 **基址寄存器** 加 **可选移位的偏移寄存器** 计算得到。
2. 保证地址连续：地址由 **基址寄存器** 加 **可选移位的偏移寄存器** 和 **左移一位的LC0寄存器** 计算得到，并且要求基址寄存器必须是标量寄存器或者Tile类型的形参寄存器，偏移寄存器必须是标量寄存器。

## 汇编语法

```asm
v.lhu<.local> [SrcL<.reuse>.ud, <lc0<<1,> SrcR<.reuse>.{T}<<<shamt>], ->RegDst.{W}
```

## 汇编符号

- **local**：表示访问Tile寄存器的空间，缺省表示访问内存空间。
- **SrcL**：基址寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：偏移寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **lc0**：块内私有的Lane Counter 0寄存器。可选，地址连续时使用。
- **shamt**：表示偏移寄存器的左移位数，有效范围为[0, 31]。左移0位默认缺省。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **W**：寄存器的位宽标识，包括h,w,d等。

## 编码格式

![V.LHU](../../../figs/bitfield/svg/Instruction_64bit/V.LHU.svg)

其中，C和L标志位含义如下：

| C(Continuous) | 含义 | L(local) | 含义 |
|---------------|------|----------|--------|
| 0 | Group内所有lane的地址不一定连续   | 0 | 访问内存空间 |
| 1 | Group内所有lane的地址一定是连续的 | 1 | 访问Tile寄存器空间 |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)
- 转换为十进制数：[UInt()](../LibPseudoCode.md#locationA)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md#locationG)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1} = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR); 
    integer {d, dstwidth} = DecodeDst(RegDst); 
    integer shift_amount = UInt(shamt);

    if dstwidth < 16 then undefined;

    if (pmask[laneid] == 1) {
        bits(64) base = V[m, srctype1, laneid];
        bits(64) offset = V[n, srctype2, laneid];
        bits(64) address = base + (offset << shift_amount);

        if C == 1 then
            bits(64) laneoffset = V[lc0, laneid];
            address += laneoffset << 1;

        bits(16) data = Mem[address][15:0];
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
- 偏移寄存器必须是标量寄存器，否则报非法指令异常。
- 应保证该指令在[多维模式](../../blockIntro/mem_block/dimmode.md)分组的数据块内使用。

![continuels](../../../figs/isa/inst/continuels.png){ width="600" }

## 备注

1. 本指令支持地址非对齐访问。
2. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
