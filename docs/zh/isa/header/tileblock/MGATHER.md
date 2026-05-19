# MGATHER

## 说明

**内存聚集（Gather from Memory to Tile）**

`MGATHER` 用于从离散的内存空间中聚集数据，并连续写入输出数据块（Tile）中。 

## 汇编语法

```asm
MGATHER <LB0:Col, LB1:Row, DataType>, SrcTile<.reuse>, [RegSrc], DepSrc, ->DstTile<Size>, DepDst
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **Col** | 输出Tile寄存器中数据的列数，也是输入Tile寄存器中offset的列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加立即数的方式进行设置，并存储到LB0寄存器。 | 否 |
| **Row** | 输出Tile寄存器中数据的行数，也是输入Tile寄存器中offset的行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，存储到LB1寄存器。 | 是，默认为1 |
| **DataType** | 从内存中收集的元素的数据类型/格式。 | 否 |
| **RegSrc** | 输入全局寄存器GGPR，用于存储收集数据的内存基地址baseAddress。 | 否 |
| **SrcTile** | 输入Tile 寄存器，用于存储一组基于baseAddress的偏移(offset)。 | 否 |
| **DstTile** | 输出Tile 寄存器，用于存储聚集得到的数据。 | 否 |
| **Size** | 指示输出Tile寄存器的大小。该值必须大于等于Row * Col * sizeof(DataType) | 否 |
| **DepSrc** | 表示本块指令对前序输出至D的块指令的依赖。 | 是 |
| **DepDst** | 表示本块指令对后序引用该标识的块指令的屏障。 | 是 |

其中DataType的可选类型如下表：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2), E8M0, HiF8, HiF4x2, E1M2x2, E2M1x2, S4x2, U4x2 |

---

## 编码格式

该TileOp编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `MGATHER, DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc`
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// dst：用于存储聚集数据的输出Tile
// base: 收集数据的基地址
// src: 存储离散的地址偏移的输入Tile
void MGATHER(Tile __out__ dst, Scalar __in__ base, Tile __in__ src) {
  for (int i = 0; i < row; i++)
    for (int j = 0; j < col; j++) {
      uint16_t offset = src[i][j];
      dst[i][j] = Memory[base + offset];
    }
}
```

图示如下：

![MGATHER](../../../figs/isa/tileop/MGATHER.png){ width="800" }

## 注意事项

输入数据数据块（SrcTile）中offset的存储格式必须是**uint16**格式，否则硬件不保证执行正确性。
