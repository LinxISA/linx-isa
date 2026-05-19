# V.SBI.BRG

## 说明

立即数偏移·存字节·桥接表(*Store Byte with Immediate Offset by Bridge table*)<br>
本指令用于从数据寄存器中[桥接表](../../blockIntro/vecinstrs/loadStoreBridge.md)索引对应的源地址处读取 `一个字节` 并存储到目标地址指向的内存或Tile寄存器中。

支持Group内地址连续访问和不连续访问两种寻址方式：

1. 不保证地址连续：目标地址由 **基址寄存器** 加 **有符号立即数偏移** 计算得到。
2. 保证地址连续：目标地址由 **基址寄存器** 加 **有符号立即数偏移** 和 **LC0寄存器** 计算得到。并且要求基址寄存器必须是标量寄存器或者Tile类型的形参寄存器。

## 汇编语法

```asm
v.sbi.brg<.local> SrcL<.reuse>.{T}, [SrcR<.reuse><.ud>, <lc0,> simm]
```

## 汇编符号

- **local**：表示写入Tile寄存器的空间，缺省表示写入内存空间。
- **SrcL**：数据寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：基址寄存器，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **lc0**：块内私有的Lane Counter0寄存器。可选，地址连续时使用。
- **T**：指定操作数的数据类型，可选类型包括sb,sh,sw,sd,ub,uh,uw,ud等。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **simm**：有符号立即数偏移，该参数编码于simm24字段。

## 编码格式

![V.SBI.BRG](../../../figs/bitfield/svg/Instruction_64bit/V.SBI.BRG.svg)

其中，C和L标志位含义如下：

| C(Continuous) | 含义 | L(local) | 含义 |
|---------------|------|----------|--------|
| 0 | Group内所有lane的地址不一定连续   | 0 | 写入内存空间 |
| 1 | Group内所有lane的地址一定是连续的 | 1 | 写入Tile寄存器空间 |

## 执行方式

- 解码输入参数：[DecodeINT](../LibPseudoCode.md#locationL)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)
- 将数据符号扩展：[SignExtend()](../LibPseudoCode.md#locationF)

```c
bits(64) pmask = P;   // lane掩码
// lanenum表示当前Group内lane的数量
for (laneid = 0; laneid < lanenum; laneid++)
{
    integer {m, srctype1}  = DecodeINT(SrcL);
    integer {n, srctype2} = DecodeINT(SrcR);

    if (pmask[laneid] == 1) {
        bits(64) index = V[c, srctype1, laneid];
        bits(64) srcaddr = BridgeTable[index];
        
        bits(64) base = V[n, srctype2, laneid];
        bits(64) offset = SignExtend(simm24);
        bits(64) dstaddr = base + offset;
        
        if (C == 1) {
            bits(64) laneoffset = V[lc0, laneid];
            dstaddr += laneoffset;
        }
        
        Mem[dstaddr] = Mem[srcaddr][7:0];
    }
}
```

## 指令约束

对于同一个Group内地址连续的使用场景，有如下约束：

- 基址寄存器必须是标量寄存器或Tile形参寄存器，否则报非法指令异常。
- 应保证该指令在[多维模式](../../blockIntro/mem_block/dimmode.md)分组的数据块内使用。

![continuels](../../../figs/isa/inst/continuels.png){ width="600" }

关于本指令的其他使用约束请见[桥接访存指令](../../blockIntro/vecinstrs/loadStoreBridge.md#constrain)介绍。

## 备注

1. 本指令不占块内私有寄存器槽位。
2. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
