# MSCATTER

## 说明

**内存分散（Scatter from Tile to Memory）**

`MSCATTER` 读取一个数据 Tile 和一个索引 Tile。索引 Tile 的每个有效元素都是相对于 GPR 基址的**字节位移**，同一坐标的数据元素写到 `BaseGPR + ByteDisplacement`。本操作只改变全局内存，不分配或发布目标 Tile。

S32 索引先符号扩展，U32 索引先零扩展，S64 与 U64 直接使用。位移不会乘以数据元素的字节数。

## 汇编语法

```asm
MSCATTER <Col, ValidRow=1, ValidCol=Col, DataType, Layout?, PEMask=AllPE>, [BaseGPR], DataTile, IndexTile
```

## 操作数

| 操作数 | 作用 |
| --- | --- |
| `BaseGPR` | 每个 PE 的 GM 基地址 |
| `DataTile` | 要写入 GM 的数据；保持不变 |
| `IndexTile` | S32、U32、S64 或 U64 字节位移；保持不变 |

两个源都必须是 Local Tile，采用同一受支持布局并具有匹配的有效形状。RowMajor、CUBE_M16 与 CUBE_M32 可用，CUBE_N8 非法。

普通传输也支持 E2M1X2、E1M2X2、HiF4X2、S4X2 与 U4X2。使用四位打包类型时，每个索引地址对应数据 Tile 中相邻的两个逻辑半字节，因而数据 Tile 的有效列数必须是索引 Tile 的两倍。

## 执行方式

模型先为所有活动通道完成地址预检，并在此阶段快照要写入的原始位。只要一个通道发生对齐、转换或权限故障，整个操作都不会产生存储事件。全部预检通过后，才按实现选择的通道顺序写入 GM。

下面的伪代码描述普通非打包类型的逻辑坐标。

```c
for (int r = 0; r < ValidRow; ++r) {
  for (int c = 0; c < ValidCol; ++c) {
    byte_offset = IndexTile[r][c];
    Memory[BaseGPR + byte_offset] = DataTile[r][c];
  }
}
```

多个活动通道可以指向同一地址。每个通道都产生一次存储，最终留下哪个值取决于实现选择的通道顺序。存在执行掩码时，未启用坐标不生成地址，也不做转换、权限检查、存储或事件记录。

## 示例

取 U32 数据 Tile `[10, 20, 30]`，U32 索引 Tile `[8, 0, 4]`，a0 中的基址为 `0x1000`。

```asm
MSCATTER <Col=4, ValidCol=3, U32>, [a0], T#1, T#2
```

执行后，`0x1008` 保存 10，`0x1000` 保存 20，`0x1004` 保存 30。索引是字节位移，所以这里使用 `8、0、4`，无需由硬件再乘以 4。

## 相关形式

`MSCATTER_MASK` 由谓词 Tile 决定哪些通道产生地址和存储。`MSCATTER_MAX/MIN/ADD/INC/DEC/AND/OR/XOR/POPC` 是索引原子归约，每个通道执行原子读改写，不返回旧值。它们不能按本页的普通覆盖存储解释。
