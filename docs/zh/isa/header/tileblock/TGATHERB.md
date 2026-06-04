# TGATHERB

## 说明

**数据块按字节偏移聚集（Tile Gather by Byte Offset）**

`TGATHERB` 使用字节偏移量索引 Tile，从源 Tile 的基地址开始按字节偏移收集元素，结果写入输出 Tile 中。

实现伪代码示意如下：
```pseudocode
// 按字节偏移聚集操作
src_ptr = byte_address_of(src[0, 0])                    // 获取源 Tile 的字节基地址
for r in 0..(ValidRow-1):                              // 遍历所有行
  for c in 0..(ValidCol-1):                            // 遍历所有列
    offset = offsetTile[r, c]                             // 获取字节偏移量
    dst[r, c] = *(src_ptr + offset)                       // 从基址+偏移处读取元素
```

---

## 汇编语法

```asm
TGATHERB <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, OffTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

- **ValidCol**：输出 Tile 中有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：输出 Tile 中有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：输出 Tile 的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：输出 Tile 的总行数，通过公式计算：`Row = DstTileSize / (Col × sizeof(DataType))`。
- **DataType**：输入/输出 Tile 元素的数据格式，支持类型见下表。
- **SrcTile**：输入 Tile 寄存器，作为字节读取的基址，支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **OffTile**：偏移量 Tile 寄存器，元素类型为 `U32`，存储相对于 `SrcTile` 基址的字节偏移量。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：输出 Tile 寄存器，支持 `T`/`U`/`M`/`N` 队列输出。
- **Size**：输出 Tile 寄存器的空间大小（有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)）。
- **PadValue**：输出 Tile 无效区域的填充值，可选：`Null`、`Zero`、`Max`、`Min`（可缺省，默认值：`Null`）。编码到 [B.DATR](../../header/B.DATR.md) 中。

本指令支持数据类型（DataType）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2) |

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `TGATHERB, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, OffTile<.reuse>, last, ->DstTile<Size>`

## 约束条件

- **偏移范围**：偏移量必须在 `SrcTile` 的有效字节范围内，不执行边界检查，越界访问结果由硬件实现定义。
- **合法读取**：从 `SrcTile + offset` 处读取的元素必须保证为合法 `DataType` 值，否则行为未定义。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **数据类型**：`SrcTile::DataType == DstTile::DataType`；`OffTile::DataType == U32`。
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TGATHERB <LB0:16, LB1:8, FP16>, T#1.reuse, U#2, ->T<256B>
```

1. **操作内容**
    - 使用 `U#2` 中的字节偏移量从 `T#1` 基址处聚集 8×16 个 FP16 元素
    - 输出：结果存入 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 输出有效列数 `16`
    - 输出有效行数 `8`
3. **数据格式**
    - 值使用 `16 位半精度浮点数`（`FP16`）
    - 偏移量使用 `U32`

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
