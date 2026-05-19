# TGEMVMX.BIAS

## 说明

**通用缩放矩阵-向量带偏置乘法（General Matrix-Vector Multiply with Bias and Scaling）**

`TGEMVMX.BIAS` 用于将两个输入 Tile 寄存器中的 **A向量** 与 **B矩阵** 缩放后再相乘，再加上**偏置Bias矩阵**，结果写到ACC寄存器中。

实现伪代码示意如下：
```pseudocode
// 矩阵-向量乘操作
for n in 0..(N-1):         // 遍历N维度
  C[0, n] = 0
  for k in 0..(K-1):       // 遍历K维度
    scaled_A = A[0, k] x scale_A[0, k/32]
    scaled_B = B[k, n] x scale_B[k/32, n]
    C[0, n] += scaled_A × scaled_B
  C[0, n] += Bias[0, n]
```

实现示意图如下：

![TGEMVMX](../../../figs/isa/tileop/TGEMVMX.png){ width="800" }

本指令再将Bias 矩阵加到输出 ACC 寄存器中。

---

## 汇编语法

```asm
TGEMVMX.BIAS <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, SrcTile3<.reuse>, SrcTile4<.reuse>, ->ACC<Size>
```

## 汇编符号

- **M、N、K**：表示输入矩阵/向量的维度，支持通过全局寄存器、立即数或全局寄存器 + 立即数三种形式进行配置。
    - **A 向量**的形状为：`1 × K`。（输入 Tile 的第一行作为 A 向量）
    - **Scale A 向量**的形状为：`1 × K/32`。（A 向量K维度32个元素共享相同的缩放因子）
    - **B 矩阵**的形状为：`K × N`。
    - **Scale B 矩阵**的形状为：`K/32 × N`。（B 矩阵K维度32个元素共享相同的缩放因子）
    - **Bias 矩阵**和**结果 矩阵**的形状为：`1 × N`。
- **DataTypeA**：表示输入A向量中元素数据格式，支持类型见下表。
- **DataTypeB**：表示输入B矩阵中元素数据格式，支持类型见下表。如果和 DataTypeA 相同则允许缺省。
- **SrcTile0**：存储A向量的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **SrcTile1**：存储缩放A向量的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **SrcTile2**：存储B矩阵的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **SrcTile3**：存储缩放B矩阵的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **SrcTile4**：存储偏置Bias矩阵的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **ACC**：存储结果矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **Size**：输出Tile寄存器的空间大小（有效范围参见：[Tile寄存器](../../register/common/tilereg.md)）。

---

## 数据布局与类型约束

### 数据向量/矩阵布局 (Data Vector/Matrix Layout)
数据矩阵的分形（Fractal）必须满足如下格式：

| 参数 | 分形格式 (Layout) | 小分形尺寸 (Row x Col) | 说明 |
| :--- | :--- | :--- | :--- |
| **Vector A** | 行优先 (`Row-major`) | / | 有效数据`1 x K` |
| **Matrix B** | 大 Z 小 n (`Zn`) | `K0_B x 16` | `K0_B = C0 / sizeof(type_B)`, `C0 = 32B` |
| **Matrix C** | 大 N 小 z (`Nz`) | `16 x 16` | 结果矩阵的数据格式 (FP32/INT32/UINT32) |

### 缩放向量/矩阵布局 (Scale Vector/Matrix Layout)

| 矩阵 | 分形布局 (Layout) | 小分形尺寸 (Row x Col) | 小分形大小 | 支持类型 |
| :--- | :--- | :--- | :--- | :--- |
| **Scale Vector A** | 行优先 (`Row-major`) | / | / | `E8M0` |
| **Scale Matrix B** | 大 N 小 n (`Nn`) | `2 × 16` (K, N) | 32B | `E8M0` |

**缩放因子共享规则：**

在 K 维度上，数据向量/矩阵的每 **32 个元素** 共享同一个缩放因子。

- **若 B 矩阵元素为 FP4（e2m1x2 / e1m2x2）格式**：B 矩阵的每个小分形为 `64 × 16`，对应的缩放矩阵小分形固定为 `2 × 16`，实现一对一匹配，即 B 的每个小分形都拥有独立的缩放小分形。

- **若 B 矩阵元素为 FP8（e4m3 / e5m2）格式**：B 矩阵的每个小分形为 `32 × 16`，但缩放矩阵小分形仍为 `2 × 16`，因此两个 B 小分形共用一个缩放小分形。为确保这一映射成立，**K 维度必须是 64 的倍数**。

### 偏置向量布局 (Bias Vector Layout)

| 参数 | 分形格式 (Layout) | 形状 | 数据类型 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **Bias** | 行主序 (`Row-Major`) | `1 × N` | 与结果矩阵 C 完全匹配 | 单行向量，长度等于输出列数 N |

### 支持的数据类型组合
数据矩阵中元素的数据格式支持如下组合：

| type_A | type_B | 备注 |
| :--- | :--- | :--- |
| `e2m1` | `e2m1` | - |
| `e1m2` | `e2m1` | - |
| `e2m1` | `e1m2` | - |
| `e1m2` | `e1m2` | - |
| `e4m3` | `e4m3` | **K 必须是 64 的倍数** |
| `e4m3` | `e5m2` | **K 必须是 64 的倍数** |
| `e5m2` | `e4m3` | **K 必须是 64 的倍数** |
| `e5m2` | `e5m2` | **K 必须是 64 的倍数** |
| `e4m3` | `e2m1` | 由于 `K0_A` 是 `K0_B` 的一半，每次 CUBE 从 A 获取一个分形，从 B 获取半个分形 |
| `e4m3` | `e1m2` | 同上 |
| `e5m2` | `e2m1` | 同上 |
| `e5m2` | `e1m2` | 同上 |
| `fp16` | `e2m1` | **矩阵 A 不需要缩放**，无 Scale Matrix A 输入 |
| `fp16` | `e1m2` | **矩阵 A 不需要缩放**，无 Scale Matrix A 输入 |
| `bf16` | `e2m1` | **矩阵 A 不需要缩放**，无 Scale Matrix A 输入 |
| `bf16` | `e1m2` | **矩阵 A 不需要缩放**，无 Scale Matrix A 输入 |

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `TGEMVMX.BIAS, DataTypeA`
- [B.DATR](../../header/B.DATR.md) `DataTypeB`    （注：与DataTypeA相同时可缺省）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    （注：*M*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    （注：*N*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    （注：*K*）
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, SrcTile3<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile4<.reuse>, last, ->ACC<Size>`

---

## 汇编示例

下面给出一个 **TGEMVMX.BIAS** 汇编示例，示范如何同时传入向量 A、A 的缩放、矩阵 B 以及 B 的缩放，并累加结果矩阵 C：

```asm
TGEMVMX.BIAS <LB0:1, LB1:32, LB2:64, e3m4, e1m2X2>, T#1.reuse, U#1, M#2, N#2, T#2, ->ACC<512B>
```

- **寄存器绑定**：
    - `SrcTile0 = T#1.reuse`：存放 A 向量（`1 x 64`），标记 `.reuse`，指令提交后仍保留数据以便后续复用。
    - `SrcTile1 = U#1`：存放 A 的缩放因子（`1 × K/32 = 1 × 2` 个 E8M0 值）。
    - `SrcTile2 = M#2`：存放 B 矩阵（`64 x 32`），采用 Zn 布局。
    - `SrcTile3 = N#2`：存放 B 的缩放因子（`(K/32) × N = 2 × 32`，分形为 `2 × 16`）。
    - `SrcTile4 = T#2`：存放 Bias 矩阵（`(1 × N = 1 × 32`。
    - `DstTile = ACC<512B>`：存放累加 `1 × 32` 的 FP32 结果。
- **尺寸设定**：
    - `M = 1`：A 为单行向量。
    - `N = 32`：结果/输出宽度。
    - `K = 64`：满足 FP8/FP4 缩放共享规则，确保 `K` 为 64 的倍数，便于 B 缩放矩阵的 `2 × 16` 小分形映射。
- **数据类型与缩放**：
    - `DataTypeA = E3M4`：A 向量使用 FP8。
    - `DataTypeB = E1M2x2`：B 矩阵使用 FP4。
    - 缩放因子均为 `E8M0`，在 K 维度上每 32 个元素共享一个缩放值。  
        - scale A：`1 × (64/32) = 1 × 2` 个缩放因子。
        - scale B：`(64/32) × 32 = 2 × 32` 个缩放因子，按 Nn 布局存储。
- **注意事项**：
    - 维度一致：`K` 与 A 的列数、B 的行数一致。
    - 若计划在后续指令继续复用 `T#1` 中的 A 数据，需要 `.reuse` 修饰（示例已添加）；其他寄存器未显式声明 `.reuse`，表示当前指令执行后允许硬件释放。
    - 输出 ACC 的容量需满足 `1 × 32` 个 FP32 元素的存储需求，示例中设置为 512B（16 × 32B）。

该示例展示了 TGEMVMX.BIAS 在混合精度、分块缩放场景下的基本用法，可根据实际算子尺寸、数据类型和缩放策略进行扩展或调整。

---

## 备注

1. 本指令只允许输出到ACC寄存器中。
2. 本指令是一种模版块，软件只定义块头。
