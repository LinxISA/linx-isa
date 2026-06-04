# TRESHAPE

## 说明

**数据块重塑（Tile Reshape）**

`TRESHAPE` 将源 Tile 中由源 Tile 自身 ValidRow/ValidCol 指定的有效区域，重塑为 LB0/LB1/LB2 指定的新行列形状，保留底层字节不变。源和目标的元素总数必须匹配（`sizeof(SrcElem) × SrcValidRow × SrcValidCol == sizeof(DstElem) × ValidRow × ValidCol`）。

## 汇编语法

```asm
TRESHAPE <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **ValidCol** | 输出 Tile 中有效元素的列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB0寄存器。 | 否 |
| **ValidRow** | 输出 Tile 中有效元素的行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB1寄存器。 | 是，默认为1 |
| **Col** | 输出 Tile 的总列数（包含无效列）。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB2寄存器。 | 是，默认等于ValidCol |
| **Row** | 输出 Tile 的总行数（包含无效行）。该值由硬件通过 `DstTileSize / (Col * sizeof(DataType))` 计算得到，无需软件显式设置。 | 否（硬件推导） |
| **DataType** | 输入/输出 Tile 元素的数据格式。 | 否 |
| **PadValue** | 输出 Tile 中位于有效区域之外的填充值。可选类型包括：`Null`（不填充或保留随机值）、`Zero`（填充零值）、`Max`（填充当前数据格式下的最大值）、`Min`（填充当前数据格式下的最小值）。 | 是，默认 Null |
| **SrcTile** | 输入Tile 寄存器，存储待重塑的源数据。支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。 | 否 |
| **DstTile** | 输出Tile 寄存器，存储重塑后的数据。支持 `T`/`U`/`M`/`N` 队列输出。 | 否 |
| **Size** | 指示输出Tile寄存器的大小。该值等于 `Row * Col * sizeof(DataType)`。有效范围参见：[Tile 寄存器](../../register/common/tilereg.md)。 | 否 |

其中DataType的可选类型如下表：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2) |

---

## 编码格式

该TileOp编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TRESHAPE, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` *（注：可缺省该指令）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（注：ValidCol，输出有效列数）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（注：ValidRow，输出有效行数）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` *（注：Col，输出总列数，可缺省该指令）*
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, last, ->DstTile<Size>`

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// dst：用于存储重塑后数据的输出Tile
// src：存储源数据的输入Tile
// LB0/LB1/LB2提供输出Tile的维度信息(ValidCol, ValidRow, Col)
void TRESHAPE(Tile __out__ dst, Tile __in__ src) {
  // 元素总数守恒：源有效区域 == 目标有效区域
  assert(sizeof(SrcElem) * src.ValidRow * src.ValidCol == sizeof(DstElem) * ValidRow * ValidCol);

  uint8_t* src_bytes = &src;

  // 将源有效区域的字节按行主序重排到目标有效区域
  for (int r = 0; r < ValidRow; r++)
    for (int c = 0; c < ValidCol; c++) {
      int flat_idx = r * ValidCol + c;
      dst[r][c] = reinterpret<DstElem*>(src_bytes)[flat_idx];
    }

  // 填充输出无效区域
  for (int r = 0; r < Row; r++)
    for (int c = 0; c < Col; c++) {
      if (r >= ValidRow || c >= ValidCol)
        dst[r][c] = PadValue;
    }
}
```

---

## 注意事项

- **约束条件**：`sizeof(SrcElem) × SrcValidRow × SrcValidCol == sizeof(DstElem) × ValidRow × ValidCol`，即源和目标的有效区域元素总数必须守恒。
- 输入Tile和输出Tile的空间大小可以不相等（取决于目标形状），但有效区域的字节总数必须相等。
- **存储布局**：重塑按行主序（RowMajor）字节顺序重新排列。
- **无数据转换**：本指令为纯形状重解释，不执行元素级数值转换。如需类型转换，请使用 [TCVT](./TCVT.md)。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TRESHAPE <LB0:28, LB1:16, LB2:32, FP16, Zero>, T#2, ->T<1KB>
```

1. **操作内容**
    - 源 Tile T#2 的有效区域重塑为 16×28 的输出形状
    - 输出：结果存入新的 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 输出有效列数 `28`（由 `LB0:28` 指定），有效行数 `16`（由 `LB1:16` 指定）
    - 输出总列数 `32`（由 `LB2:32` 指定），总行数由 Size 推导
3. **数据格式**
    - 使用 `FP16` 格式
4. **填充**
    - 目标无效区域填充 `Zero`
