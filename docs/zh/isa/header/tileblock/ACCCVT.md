# ACCCVT

## 说明

**累加器搬移与转换（Accumulator Convert）**

`ACCCVT` 将矩阵乘累加寄存器 **ACC** 中的结果矩阵搬移至通用 Tile 寄存器（**T/U/M/N**），搬移过程中支持以下随路（in-flight）操作：

1. **存储布局变换**
   将 ACC 的原生 NZ（大N小z）布局转换为目标布局（如 ND、DN 等），满足后续运算对输入布局的要求。

2. **分形规范化（Canonicalize）**
   将 ACC 的 1024 字节大分形拆分为标准的 512 字节小分形。当 ACC 结果需要作为左矩阵输入后续矩阵乘时，必须执行此操作。

3. **数据类型转换**
   将 ACC 的 32 位元素转换为目标精度（如 fp32 → fp16、fp32 → int8 等），支持浮点与整数之间的双向转换。

4. **标量缩放**
   将所有元素统一乘以一个标量缩放因子（由 GGPR 提供）。

5. **随路量化**
   使用一个独立的量化参数 Tile，对搬移数据执行逐行缩放后再做类型转换。量化与搬移在单条指令内融合完成，无需额外的量化 Pass。

6. **行最大值归约（RowMax）**
   对缩放后的每行数据计算最大值，结果写入第二个输出 Tile，常用于量化流程中的逐行绝对最大值（absmax）统计。

上述操作在硬件流水线中串联执行，顺序为：**逐行量化 → 标量缩放 → 类型转换**，RowMax 在类型转换前的中间结果上归约。

## 汇编语法

```asm
ACCCVT Layout.{canon, normal}, <LB0:ValidCol, LB1:ValidRow, LB2:Col, SrcType, DstType>,
        ACC, SrcTile<.reuse>, [RegSrc],
        ->DstTile0<Size0>, DstTile1<Size1>
```

## 汇编符号

| 参数 | 说明 | 是否可选 |
|------|------|----------|
| **Layout** | 数据存储布局变换标识。支持 `NORM`（不变）、`NZ2ND`、`NZ2DN` 等。 | 否 |
| **.canon** | 对 ACC 分形执行规范化拆分（1024B → 512B），使输出满足左矩阵输入要求。 | 是，缺省为 `.normal` |
| **.normal** | 保持 ACC 原有分形大小不变。 | 是（默认） |
| **ValidCol** | 输出 Tile 中有效数据的**列数**。可通过 `GGPR`、`立即数` 或 `GGPR + 立即数` 设置，编码于 LB0。 | 否 |
| **ValidRow** | 输出 Tile 中有效数据的**行数**。可通过 `GGPR`、`立即数` 或 `GGPR + 立即数` 设置，编码于 LB1。 | 否 |
| **Col** | 输出 Tile 的**总列数**（含 Padding 列）。缺省等于 ValidCol。可通过 `GGPR`、`立即数` 或 `GGPR + 立即数` 设置，编码于 LB2。 | 是，默认等于 ValidCol |
| **SrcType** | ACC 中源数据元素的类型。可选：`FP32`、`S32`、`U32`。 | 否 |
| **DstType** | 输出 Tile 中目标数据元素的类型。支持浮点/整数、高精度/低精度，详见下表。 | 否 |
| **ACC** | 输入累加器寄存器。 | 否 |
| **SrcTile** | 量化参数 Tile，提供逐行缩放因子。元素类型须与 SrcType 一致。省略 `.reuse` 表示指令提交后可回收该 Tile。 | 是（不使用随路量化时缺省） |
| **RegSrc** | 标量缩放因子，由 GGPR 提供。类型须与 SrcType 一致。 | 是（不缩放时缺省） |
| **DstTile0** | 第一个输出 Tile（类型 T/U/M/N），存放搬移后的主结果。 | 否 |
| **DstTile1** | 第二个输出 Tile（类型 T/U/M/N），存放每行最大值（RowMax 结果）。 | 是（不执行 RowMax 时缺省） |
| **Size0** | DstTile0 的容量，可通过立即数或 GGPR 传参。 | 否 |
| **Size1** | DstTile1 的容量，可通过立即数或 GGPR 传参。 | 是（跟随 DstTile1 缺省） |

**Row 的计算方式**：输出 Tile 的总行数 Row 不由 LB 显式指定，而是由输出 Tile 的 Size、Col 和 DstType 数据位宽推导得到：

$$ Row = \frac{TileSize}{Col \times sizeof(DstType)} $$

其中 $ValidRow \le Row$，超出 ValidRow 的行区域为 Padding 区域。

### 源数据类型（SrcType）

| SrcType | 说明 |
|---------|------|
| FP32 | 32 位单精度浮点（E8M23） |
| S32  | 32 位有符号整数 |
| U32  | 32 位无符号整数 |

### 目标数据类型（DstType）

| DstType | 说明 | DstType | 说明 |
|---------|------|---------|------|
| FP64 | 64 位双精度浮点（E11M52） | S64 | 64 位有符号整数 |
| FP32 | 32 位单精度浮点（E8M23） | S32 | 32 位有符号整数 |
| TF32 | 32 位单精度浮点（E8M10） | S16 | 16 位有符号整数 |
| HF32 | 32 位单精度浮点（E8M11） | S8  | 8 位有符号整数  |
| FP16 | 16 位半精度浮点（E5M10） | U64 | 64 位无符号整数 |
| BF16 | 16 位半精度浮点（E8M7）  | U32 | 32 位无符号整数 |
| E4M3 | 8 位低精度浮点（E4M3）   | U16 | 16 位无符号整数 |
| E5M2 | 8 位低精度浮点（E5M2）   | U8  | 8 位无符号整数  |
| E2M3 | 6 位低精度浮点（E2M3）   | E3M2| 6 位低精度浮点（E3M2） |
| E2M1 | 4 位低精度浮点（E2M1）   | E1M2| 4 位低精度浮点（E1M2） |
| E8M0 | 8 位低精度浮点（E8M0）   | HiF4| 4 位低精度浮点（E1M2） |

## 编码格式

`ACCCVT` 展开为以下微指令序列编码：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `ACCCVT, SrcType`
- [B.DATR](../../header/B.DATR.md) `Layout.{canon, normal}, DstType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0` *（注：ValidCol）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1` *（注：ValidRow）*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2` *（注：Col，等于 ValidCol 时可缺省）*
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, ->DstTile0<Size0>` *（注：不使用随路量化时 SrcTile 缺省）*
- [B.IOT](../../header/B.IOT.md) `last, ->DstTile1<Size1>` *（注：不执行 RowMax 时缺省）*
- [B.IOR](../../header/B.IOR.md) `RegSrc` *（注：不使用标量缩放时缺省）*

## 布局与数据类型

### ACC 输入格式

| 属性 | 值 |
|------|-----|
| 存储布局 | NZ（大N小z） |
| 小分形大小 | 1024 Byte |
| 元素精度 | 32 bit（FP32 / S32 / U32） |

ACC 的结果矩阵始终以 NZ 布局存储，这是 CUBE 运算单元的固定输出格式。矩阵元素在 ACC 内统一按 32 位精度存放，不论原始计算精度。

### 量化参数 Tile（SrcTile）布局

| 属性 | 要求 |
|------|------|
| 存储布局 | ND（行主序） |
| 元素类型 | 与 SrcType 一致（32 bit） |
| 行数 | 等于 ValidRow（逐行缩放），或 1（全局单因子） |
| 列数 | 1 |

量化 Tile 中每个元素 `fp[i]` 对应 ACC 结果矩阵第 i 行的缩放因子。若量化 Tile 仅有 1 行，则该因子应用于所有行。

### Canonicalize 操作

当需要将 ACC 结果作为左矩阵输入后续矩阵乘时，须通过 `.canon` 模式将 1024 字节的原生大分形拆分为两个 512 字节的标准分形：

![canonicalize](../../../figs/isa/arch/canon.png){ width="600" }

## 执行模型

```cpp
// 输入:
//   src   — ACC 寄存器中的源矩阵 (NZ, SrcType)
//   fp    — 量化参数 Tile, 逐行缩放因子 (ND, SrcType)
//   scale — 标量缩放因子 (来自 RegSrc)
// 输出:
//   dst0  — 主结果 Tile (转换后数据, DstType, 目标 Layout)
//   dst1  — RowMax 结果 Tile (每行最大值, SrcType)
//
// 处理流水线: 逐行量化 → 标量缩放 → RowMax归约 → 类型转换写入
void ACCCVT(Tile __out__ dst0, Tile __out__ dst1,
            Tile __in__ src, Tile __in__ fp, Scalar scale) {
  for (int i = 0; i < ValidRow; i++) {
    SrcType row_max = MinValue(SrcType);
    for (int j = 0; j < ValidCol; j++) {
      SrcType val = src[i][j];

      // 步骤 1: 随路量化（逐行缩放）
      if (fp.valid)  val = val * fp[i];

      // 步骤 2: 标量缩放
      if (scale.valid) val = val * scale;

      // 步骤 3: RowMax 归约（在类型转换前的中间值上计算）
      if (dst1.valid && val > row_max)  row_max = val;

      // 步骤 4: 数据类型转换并写入主输出
      dst0[i][j] = Convert(val, SrcType, DstType);
    }
    if (dst1.valid)  dst1[i][0] = row_max;
  }
}
```

数据流示意：

```text
  ACC (NZ, fp32) ────────────┐
                              ├──> [× fp[i]] ──> [× scale] ──> [Convert] ──> DstTile0 (Layout, DstType)
  SrcTile (ND, fp32) ────────┘                             │
                                                   RowMax ─┴──> DstTile1
```

## 注意事项

- **Layout 与 RowMax 的约束**：仅当布局变换为 `NZ2ND` 或 `NZ2DN` 时，RowMax 操作有效。其他布局下使能 RowMax 为未定义行为，DstTile1 中的结果不保证正确。
- **ACC 生命周期**：指令执行结束后 ACC 寄存器被释放，后续指令读取 ACC 将触发异常。
- **量化 Tile 类型一致性**：SrcTile 的元素类型必须与 SrcType 一致（均为 32 bit 精度），否则缩放结果不保证正确。
- **缩放叠加**：当 SrcTile 和 RegSrc 同时提供时，缩放因子为乘积关系（先逐行、再标量）。
- **Tile 大小约束**：DstTile0 的 Size 必须能容纳 `ValidRow × Col × sizeof(DstType)` 的数据量（含 Padding 区域）。DstTile1 的 Size 必须能容纳 `ValidRow × 1 × sizeof(SrcType)` 的数据量。

## 备注

此指令为模版块（Template Block），仅定义块头，无块体。
