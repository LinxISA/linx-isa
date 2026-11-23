# MGATHER

## 说明

**内存聚集（Gather from Memory to Tile）**

`MGATHER` 以 GPR 中的基址为起点，把索引 Tile 的每个有效元素解释成**字节位移**，从离散的全局内存地址读取数据，并按索引 Tile 的行列顺序写入新的 Local 目标 Tile。

地址计算为 `BaseGPR + ByteDisplacement`。S32 索引先符号扩展，U32 索引先零扩展，S64 与 U64 直接使用。位移不会乘以传输元素的字节数，因此软件若持有元素下标，需要先把它换算成字节位移。

## 汇编语法

```asm
MGATHER <Col, ValidRow=1, ValidCol=Col, DataType, PadValue?, Layout?, PEMask=AllPE>, [BaseGPR], IndexTile, ->DstTile<Size>
```

## 操作数

| 操作数 | 作用 |
| --- | --- |
| `BaseGPR` | 每个 PE 的 GM 基地址 |
| `IndexTile` | S32、U32、S64 或 U64 字节位移；保持不变 |
| `DstTile` | 新分配的 Local 目标 Tile，接收读到的元素 |

目标采用块头的 `DataType`、`Layout` 和 B.DIM 形状。RowMajor、CUBE_M16 与 CUBE_M32 可用，CUBE_N8 非法。

普通传输支持非四位类型，也支持 E2M1X2、E1M2X2、HiF4X2、S4X2 与 U4X2。使用这些四位打包类型时，一个索引指向一个字节，该字节同时承载两个相邻的逻辑半字节，所以目标有效列数必须是索引有效列数的两倍。

## 执行方式

执行分为预检和发布两阶段。模型先为每个活动索引计算地址，完成对齐、转换和权限检查。任一通道失败时，不读取数据，也不发布部分目标。全部地址通过后，才读取各通道并一次性发布目标 Tile。

下面的伪代码描述普通非打包类型的逻辑坐标。CUBE 布局仍按布局映射寻址，四位打包类型按上面的“一字节两个逻辑元素”规则处理。

```c
for (int r = 0; r < ValidRow; ++r) {
  for (int c = 0; c < ValidCol; ++c) {
    byte_offset = IndexTile[r][c];
    DstTile[r][c] = Memory[BaseGPR + byte_offset];
  }
}
```

有效区域之外的物理目标元素接收 `PadValue`。省略 B.DATR 时，本操作把这些位置定义为零位。存在执行掩码时，未启用坐标不生成地址，也不做转换、权限检查或内存读取。

## 示例

取一个 `1 × 4` 的 U32 索引 Tile，内容为 `[8, 0, 8, 4]`，a0 中的基址为 `0x1000`。GM 在 `0x1000`、`0x1004`、`0x1008`、`0x100c` 处依次存放 U32 值 `1、2、3、4`。

```asm
MGATHER <Col=4, U32>, [a0], T#1, ->T<128B>
```

四个地址依次是 `0x1008、0x1000、0x1008、0x1004`，所以目标有效区域得到 `[3, 1, 3, 2]`。目标共有 32 个 U32 物理元素，其余 28 个元素由默认填充值定义为零。

## 相关形式

`MGATHER_MASK`、`MGATHER_CAS`、`MGATHER_EXCH`、`MGATHER_MAX/MIN/ADD/INC/DEC/AND/OR/XOR` 都有独立操作数和效果。掩码形式会抑制未选通道的地址生成；原子形式会更新 GM，并把每个通道观察到的旧值返回到目标 Tile。它们不能按本页的普通读取伪代码解释。
