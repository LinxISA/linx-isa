# MSCATTER

## 说明

**内存分散（Scatter from Memory to Tile）**

`MSCATTER` 用于将输入数据块（Tile）内的数据存储到离散的内存空间中。

## 汇编语法

```asm
MSCATTER <LB0:Col, LB1:Row, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, [RegSrc], DepSrc, ->DepDst
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|------|------------|
| **Col** | 输入Tile寄存器中数据/偏移的列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加立即数的方式进行设置，并存储到LB0寄存器。 | 否 |
| **Row** | 输入Tile寄存器中数据/偏移的行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加立即数的方式进行设置，并存储到LB1寄存器。 | 是，默认为1 |
| **DataType** | 输入Tile中数据的格式，即向内存中散布的元素的数据类型/格式。 | 否 |
| **RegSrc**   | 输入全局寄存器GGPR，用于存储分散数据的内存基地址baseAddress。 | 否 |
| **SrcTile0** | 第一个输入Tile 寄存器，用于存储源数据。 | 否 |
| **SrcTile1** | 第二个输入Tile 寄存器，用于存储偏移量（offset）。  | 否 |
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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `MSCATTER, DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc`
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// src0: 存储数据的输入Tile
// base: 表示基地址的标量
// src1: 存储偏移的输入Tile
void MSCATTER(Tile __in__ src0, Scalar __in__ base, Tile __in__ src1) {
  for (int i = 0; i < row; i++)
    for (int j = 0; j < col; j++) {
      uint16_t offset = src1[i][j];
      Memory[base + offset] = src0[i][j];
    }
}
```

实现示意图如下：

![MSCATTER](../../../figs/isa/tileop/MSCATTER.png){ width="800" }

## 注意事项

- 输入数据数据块（SrcTile1）中offset的存储格式必须是**uint16**格式，否则硬件不保证执行正确性。
- 如果多个元素映射到同一目标位置，最终值由实现定义。
