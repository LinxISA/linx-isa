# TRESHAPE.MASK

## 说明

**带掩码的数据块重塑（Masked Tile Reshape）**

`TRESHAPE.MASK` 是 `TRESHAPE` 的掩码变体，通过源掩码 Tile（`SrcMaskTile`）和目的掩码 Tile（`DstMaskTile`）控制重塑过程中哪些元素参与操作及其在目标中的摆放位置。掩码 Tile 中每个元素为 1 bit 的标志位，与对应 Tile 中的元素一一对应。

执行时：
- `SrcMaskTile` 指示源 Tile 中哪些位置的数据是有效的（bit=1 表示有效）；
- `DstMaskTile` 指示输出 Tile 中哪些位置需要写入数据（bit=1 表示有效位置）；
- 源有效数据按行主序顺序填充到目的有效位置中，掩码为 `0` 的位置写入 `PadValue`。

## 汇编语法

```asm
TRESHAPE.MASK <LB0:Col, LB1:Row, DataType, PadValue>, SrcTile<.reuse>, SrcMaskTile<.reuse>, DstMaskTile<.reuse>, ->DstTile<Size>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|-----|-----------|
| **Col** | 输出 Tile 的总列数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB0寄存器。 | 否 |
| **Row** | 输出 Tile 的总行数。该值可以通过全局寄存器[GGPR](../../register/common/ggpr.md)加`立即数`的方式进行设置，并存储到LB1寄存器。 | 是，默认为1 |
| **DataType** | 输入/输出 Tile 元素的数据格式。 | 否 |
| **PadValue** | 输出 Tile 中掩码为 `0` 的位置的填充值。可选类型包括：`Null`（不填充或保留随机值）、`Zero`（填充零值）、`Max`（填充当前数据格式下的最大值）、`Min`（填充当前数据格式下的最小值）。 | 是，默认 Null |
| **SrcTile** | 输入Tile 寄存器，存储待重塑的源数据。支持 `T`/`U`/`M`/`N` 队列输入（参见：[Tile 寄存器](../../register/common/tilereg.md)）。 | 否 |
| **SrcMaskTile** | 输入Tile 寄存器，存储源数据掩码。每个元素为1bit，值为 `1` 表示对应源元素有效。 | 否 |
| **DstMaskTile** | 输入Tile 寄存器，存储输出数据掩码。每个元素为1bit，值为 `1` 表示对应目标位置接收数据。 | 否 |
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

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TRESHAPE.MASK, DataType`
- [B.DATR](../../header/B.DATR.md) `PadValue` *（注：可缺省该指令）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（注：Col，输出总列数）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（注：Row，输出总行数）*
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, SrcMaskTile<.reuse>`
- [B.IOT](../../header/B.IOT.md) `DstMaskTile<.reuse>, last, ->DstTile<Size>`

---

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// dst：用于存储重塑后数据的输出Tile
// src：存储源数据的输入Tile
// src_mask：源数据掩码，1bit/元素，1=有效
// dst_mask：目标数据掩码，1bit/元素，1=有效位置
// LB0/LB1提供输出Tile的维度信息(Col, Row)
void TRESHAPE_MASK(Tile __out__ dst, Tile __in__ src, Tile __in__ src_mask,
                   Tile __in__ dst_mask) {
  // 收集源有效元素
  ElemType src_valid_elems[];
  for (int r = 0; r < src.Row; r++)
    for (int c = 0; c < src.Col; c++) {
      if (src_mask[r][c] == 1)
        src_valid_elems.append(src[r][c]);
    }

  // 按目标掩码写入
  int elem_idx = 0;
  for (int r = 0; r < Row; r++)
    for (int c = 0; c < Col; c++) {
      if (dst_mask[r][c] == 1) {
        dst[r][c] = (elem_idx < src_valid_elems.size()) ? src_valid_elems[elem_idx++] : PadValue;
      } else {
        dst[r][c] = PadValue;
      }
    }
}
```

---

## 注意事项

- **约束条件**：源有效元素数量必须等于目标有效位置数量，即 `popcount(SrcMaskTile) == popcount(DstMaskTile)`。
- 输入Tile和输出Tile的空间大小可以不相等，但有效元素的字节总数必须匹配。
- **存储布局**：重塑按行主序（RowMajor）字节顺序重新排列。
- **无数据转换**：本指令为纯数据位置重排，不执行元素级数值转换。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。
- 输入掩码Tile（SrcMaskTile 和 DstMaskTile）中每个元素为 **1 bit**，与对应 Tile 中的元素一一对应。

---

## 汇编示例

```asm
TRESHAPE.MASK <LB0:64, LB1:32, E5M2, Zero>, T#4, T#2, T#3, ->T<2KB>
```

1. **操作内容**
    - 源 Tile T#4，使用 T#2 为源掩码，T#3 为目标掩码
    - 按掩码重塑数据到输出形状 32×64
    - 输出：结果存入新的 `T` 队列 Tile 寄存器
2. **数据处理范围**
    - 输出总列数 `64`（由 `LB0:64` 指定），总行数 `32`（由 `LB1:32` 指定）
3. **掩码**
    - T#2 存储源数据的掩码，T#3 存储输出数据的掩码
4. **填充**
    - 目标掩码为 `0` 的位置填充 `Zero`
