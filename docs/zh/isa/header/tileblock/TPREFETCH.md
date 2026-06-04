# TPREFETCH

## 说明

**数据块预取（Tile Prefetch）**

`TPREFETCH` 将全局内存中的数据预取到 Tile 本地缓存（UB），作为提示指令，硬件可选择性忽略。与 `TLOAD` 不同，本指令不分配 Tile 寄存器，仅将数据从 GM 搬运到本地缓存。

实现伪代码示意如下：
```pseudocode
// 预取操作（硬件提示）
prefetch_gm_to_ub(src_addr, size)   // 将 GM 数据预取到 UB 缓存
```

---

## 汇编语法

```asm
TPREFETCH Layout, <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, [RegSrc], [RegOff]
```

## 汇编符号

- **Layout**：源数据的存储布局，如 `ND`、`NZ` 等。
- **ValidCol**：预取数据有效元素的列数。该参数可以通过以下 3 种形式配置到 LB0 寄存器中：
    - **reg**：通过全局寄存器 [GGPR](../../register/common/ggpr.md) 设置。
    - **imm**: 使用立即数设置。
    - **reg+imm**：通过全局寄存器加立即数的形式设置。
- **ValidRow**：预取数据有效元素的行数（可缺省，默认值：`1`）。该参数配置到 LB1 寄存器中，配置方式同上。
- **Col**：预取数据的总列数（可缺省，默认值：等于 `ValidCol`）。该参数配置到 LB2 寄存器中，配置方式同上。
- **Row**：预取数据的总行数，通过公式计算：`Row = (ValidRow × Col × sizeof(DataType)) / (Col × sizeof(DataType))`。
- **DataType**：预取数据元素的数据格式，支持类型见下表。
- **RegSrc**：源内存基地址，由 GGPR 提供。
- **RegOff**：源内存偏移量，由 GGPR 提供（可缺省）。

本指令支持的数据格式（DataType）如下表所示：

| Datatype | 说明 | Datatype | 说明 |
|----------|------|----------|-------|
| FP64 | 64 位双精度浮点数（E11M52） | S64 | 64 位有符号整型数据 |
| FP32 | 32 位单精度浮点数（E8M23） | S32 | 32 位有符号整型数据 |
| TF32 | 32 位单精度浮点数（E8M10） | S16 | 16 位有符号整型数据 |
| HF32 | 32 位单精度浮点数（E8M11） | S8 | 8 位有符号整型数据 |
| FP16 | 16 位半精度浮点数（E5M10） | U64 | 64 位无符号整型数据 |
| BF16 | 16 位半精度浮点数（E8M7） | U32 | 32 位无符号整型数据 |
| E4M3 | 8 位低精度浮点数（E4M3） | U16 | 16 位无符号整型数据 |
| E5M2 | 8 位低精度浮点数（E5M2） | U8 | 8 位无符号整型数据 |

---

## 编码格式

该 TileOp 模版块编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TPREFETCH, DataType`
- [B.DATR](../../header/B.DATR.md) `Layout`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`   （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`   （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`   （注：*Col*）
- [B.IOR](../../header/B.IOR.md) `RegSrc`
- [B.IOR](../../header/B.IOR.md) `RegOff`   （注：*可选*）

## 约束条件

- **硬件行为**：本指令为优化提示，硬件可选择忽略。不影响程序语义正确性，仅影响性能。
- **有效边界**：`ValidRow <= Row`，`ValidCol <= Col`
- **存储布局**：必须是行主序（RowMajor）。
- **尺寸范围**：Tile 的行列/有效行列等参数大小均必须小于等于 16 bit。

---

## 汇编示例

```asm
TPREFETCH ND, <LB0:64, LB1:32, FP16>, [a0]
```

1. **操作内容**
    - 将 `a0` 指向的全局内存数据预取到 UB 缓存
2. **数据处理范围**
    - 有效列数 `64`（由 `LB0:64` 指定）
    - 有效行数 `32`（由 `LB1:32` 指定）
3. **数据格式**
    - 使用 `16 位半精度浮点数`（`FP16`）格式
4. **特性**
    - 本指令为纯提示指令，不分配 Tile 寄存器，不产生输出

---

## 备注

此指令是 TileOp 模版块，软件只定义块头。
