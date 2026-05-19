# TMATMULMX

## 说明

**带缩放的矩阵乘法（Matrix Multiply with Scaling）**

`TMATMULMX` 用于对输入 Tile 寄存器中的 **A 数据矩阵** 与 **B 数据矩阵** 分别进行缩放处理后，执行矩阵乘运算，结果矩阵写到 ACC 寄存器中。

缩放计算：`Matrix_C = (DataMatrix_A × ScaleMatrix_A) * (DataMatrix_B × ScaleMatrix_B)`。当数据矩阵（`DataMatrix A/B`）的 DataType 为 FP16或BF16 格式时，数据矩阵不进行缩放操作，因此可缺省对应的缩放矩阵输入。

关于矩阵运算的输入输出要求请见 [矩阵数据块](../../blockIntro/cube_block/intro.md) 介绍。

## 汇编语法

```asm
TMATMULMX <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, SrcTile3<.reuse>, ->ACC<Size>
```

## 汇编符号

- **M、N、K**：表示输入矩阵的尺寸，可分别通过 `全局寄存器 `、` 立即数` 或 `全局寄存器加立即数` 的形式设置。
    - 数据矩阵A的尺寸为：`M行K列`；缩放矩阵A的行数与数据矩阵A相同，列数根据数据类型而定。
    - 数据矩阵B的尺寸为：`K行N列`；缩放矩阵A的列数与数据矩阵A相同，行数根据数据类型而定。
- **DataTypeA**：表示数据矩阵A中元素数据格式。
- **DataTypeB**：表示数据矩阵B中元素数据格式。允许与 DataTypeA 不同，如果和 DataTypeA 相同时允许缺省。
- **SrcTile0**：存储 **数据矩阵A** (Data Matrix A) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile1**：存储 **缩放矩阵A** (Scale Matrix A) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile2**：存储 **数据矩阵B** (Data Matrix B) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile3**：存储 **缩放矩阵B** (Scale Matrix B) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **reuse**：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **ACC**：存储结果矩阵的 [Tile 寄存器](../../register/common/tilereg.md) 类型。
- **Size**：指示输出 Tile 寄存器空间大小的立即数，例如 `ACC<64KB>`。

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `TMATMULMX, DataTypeA`
- [B.DATR](../../header/B.DATR.md) `DataTypeB`    *(注：DataTypeB 和 DataTypeA 相同时可缺省该指令)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    *(注：M)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    *(注：N)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    *(注：K)*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`   *(A, ScaleA)*
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, SrcTile3<.reuse>, last, ->ACC<Size>`   *(B, ScaleB)*

---

## <span id="constrain">数据布局与类型约束</span>

### 数据矩阵

数据矩阵（Data Matrix A/B/C）的分形（Fractal）必须满足如下格式：

| 数据矩阵 | 尺寸（Row x Col） | 分形格式 (Layout) | 小分形尺寸 (R0 x C0) |
| :--- | :--- | :--- | :--- |
| **Data Matrix A** | `M x K` | 大 N 小 z (`Nz`) | `16 x K0_A`，`K0_A = 32Byte / sizeof(type_A)` |
| **Data Matrix B** | `K x N` | 大 Z 小 n (`Zn`) | `K0_B x 16`，`K0_B = 32Byte / sizeof(type_B)` |

数据矩阵支持数据格式如下：

| 位宽 | 格式 | 说明 |
|------|-------|----------|
| b4  | `e2m1x2`、`e1m2x2`、`hif4x2`、`s4x2`、`u4x2` | 实际元素位宽为4-bit，但是两个元素打包存储在一个字节中。 |
| b8  | `e4m3`、`e5m2` | K 必须是 64 的倍数，避免缩放矩阵不满一个小分形 |
| b16 | `fp16`、`bf16` | 该格式输入的数据矩阵不需要缩放，无对应的缩放矩阵 |

当执行混合精度的CUBE运算时，需要特殊注意的是：

- **当数据矩阵A/B 元素的位宽比是4:1时**：由于A矩阵小分形的M维度大小与B矩阵小分形的N维度相同（都是16），A矩阵小分形K维度大小是B矩阵小分形K维度大小的1/4，因此每次CUBE都会从A矩阵中获取一个分形数据，并从B矩阵中获取1/4个分形数据以生成输出分形。
- **当数据矩阵A/B 元素的位宽比是2:1时**：由于A矩阵小分形的M维度大小与B矩阵小分形的N维度相同（都是16），A矩阵小分形K维度大小是B矩阵小分形K维度大小的1/2，因此每次CUBE都会从左矩阵中获取一个分形数据，并从B矩阵中获取1/2个分形数据以生成输出分形。
- 其他情况以此类推。

### 缩放矩阵

执行MX矩阵乘前，缩放矩阵（scale matrix）在 Tile 中的组织遵循统一的分形化存储原则：其布局既受 数据矩阵的数据类型 约束，也受 分形（fractal）最小对齐要求约束。

1. 对于 **FP4（e2m1/e1m2）** 输入，数据矩阵A的 `K0_A = 64`。在 K 维上，**每 32 个元素共享一个 E8M0 缩放因子（scale）**。为匹配该共享粒度与硬件访存组织，缩放矩阵A中 scale 的实际分形布局按 `(M, K) = 16 × 2` 组织。（E8M0格式参见[MX Microscaling](../../datatype/MX_SCALE.md)）
2. 对于 **FP8（e4m3/e5m2）** 输入，数据矩阵A的 `K0_A = 32`，且同样是 **K 维每 32 个元素共享一个 E8M0 scale**。需要注意的是，缩放矩阵的小分形对齐粒度为 32Byte，这一实现约束决定了FP8 格式下 scale matrix A 的最小分形尺寸也必须保持为 `(M, K) = 16 × 2`。因此在参数配置上，FP8 场景下的 `K0` 需满足 64 的整数倍要求，以保证分形拼接与对齐一致性。
3. 对于 **HiF4** 输入，数据矩阵A的 `K0_A = 64`。其 scale 机制为 **K 维每 64 个元素共享一组由三部分组成的缩放信息**：`E6M2`、`E1_8` 与 `E1_16`。这三部分 scale 分布在两个小分形中，每个小分形尺寸均为 `16 × 1/2`。该类型涉及更细的 scale 拆分与映射关系，具体可参见 [HiF Microscaling](../../datatype/HiF_SCALE.md) 章节。

综上，MX 的 scale 布局在架构上体现为“**类型定义的共享粒度**”与“**存储系统对齐粒度**”的联合约束：前者决定逻辑 scale 作用范围，后者决定物理分形最小组织单元。矩阵 B 的 scale 排布与 A 保持同构，实现上应按对应数据类型复用同一套规则。

缩放矩阵（Scale Matrix A/B）配置与布局规则总结如下：

| 缩放矩阵 | 分形布局 (Layout) | 数据格式 | 尺寸（Row x Col） | 小分形尺寸 (Row x Col) |
| :--- | :--- | :--- | :--- | :--- |
| **Scale Matrix A** | 大 Z 小 z (`Zz`) | `E8M0` | `M x K/32` | 32B；`16 × 2` (M, K) |
|                    | 大 Z 小 z (`Zz`) | `E6M2`、`E1_8` 与 `E1_16` | `M x K/64` | 32B；`16 × 1/2` (M, K) |
| **Scale Matrix A** | 大 N 小 n (`Nn`) | `E8M0` | `K/32 x N` | 32B；`2 × 16` (K, N) |
|                    | 大 N 小 n (`Nn`) | `E6M2`、`E1_8` 与 `E1_16` | `K/64 x N` | 32B；`1/2 x 16` (K, N) |

### 结果矩阵

| 结果矩阵 | 尺寸（Row x Col） | 分形格式 (Layout) | 小分形尺寸 (R0 x C0) | 数据格式 |
| :--- | :--- | :--- | :--- | :--- |
| **Matrix C** | `M x N` | 大 N 小 z (`Nz`) | `16 x 16` | `FP32/S32/U32` |

---

## 执行模型

本指令执行过程通过伪代码示意如下：
```cpp
// TMATMULMX: D = (ScaleA * A) * (ScaleB * B)
void TMATMULMX(Tile __out__ D, Tile __in__ A, Tile __in__ ScaleA, 
               Tile __in__ B, Tile __in__ ScaleB) {
  
  // 1. 缩放处理 (根据 DataType 决定是否跳过 A 的缩放)
  Tile A_scaled = (DataTypeA == FP16 || DataTypeA == BF16) ? A : (ScaleA * A);
  Tile B_scaled = (DataTypeB == FP16 || DataTypeB == BF16) ? B : (ScaleB * B);
  
  // 2. 矩阵乘法
  for (int i = 0; i < D.m; i++)
    for (int j = 0; j < D.n; j++) {
      D[i][j] = 0;
      for (int k = 0; k < A_scaled.k; k++)
        D[i][j] += A_scaled[i][k] * B_scaled[k][j];
    }
}
```

两个FP4输入的缩放矩阵乘 实现示意图如下：

![TMATMULMX_FP4](../../../figs/isa/tileop/TMATMULMX_FP4.png){ width="900" }

FP8 + FP4输入的缩放矩阵乘 实现示意图如下：

![TMATMULMX_FP8FP4](../../../figs/isa/tileop/TMATMULMX_FP8FP4.png){ width="900" }

两个HiF4输入的缩放矩阵乘 实现示意图如下：

![TMATMULMX_HiF4](../../../figs/isa/tileop/TMATMULMX_HiF4.png){ width="900" }

FP8 + HiF4输入的缩放矩阵乘 实现示意图如下：

![TMATMULMX_FP8HiF4](../../../figs/isa/tileop/TMATMULMX_FP8HiF4.png){ width="900" }

---

## 汇编示例

```asm
TMATMULMX <LB0:100, LB1:a0, LB2:a1+10, e4m3, e1m2x2>, T#1, U#1, M#1, N#1, ->ACC<64KB>
```

- **输入输出**：
    - `SrcTile0 = T#1`：存放 A 矩阵 (Matrix A)。
    - `SrcTile1 = U#1`：存放 A 缩放矩阵 (Scale Matrix A)。
    - `SrcTile2 = M#1`：存放 B 矩阵 (Matrix B)。
    - `SrcTile3 = N#1`：存放 B 缩放矩阵 (Scale Matrix B)。
    - `DstTile = ACC`：存放结果矩阵，分配容量为 64KB。
- **指令功能**：执行带缩放的矩阵乘法 `D = (ScaleA × A) × (ScaleB × B)`。
- **尺寸参数设定**:
    - A 的维度为 `M×K = 100 × (a1 + 10)`。
    - B 的维度为 `K×N = (a1 + 10) × a0`。
    - 结果 D 的维度为 `M×N = 100 × a0`。
- **数据类型**:
    - `DataTypeA = e4m3`，`DataTypeB = e1m2x2`。均支持缩放操作。
- **约束与一致性**:
    - **维度一致性**：K 必须与 A 的列数及 B 的行数一致。
    - **布局一致性**：SrcTile0~3 必须满足上述“分形要求”中的布局约束（如 `Nz`, `Zz`, `Nn` 等）。
    - **K 对齐约束**：若使用 `e4m3`/`e5m2` 类型，K 必须是 64 的倍数。
    - **复用约束**：若后续指令仍需使用 T#1~N#1 中的数据，必须添加 `.reuse` 后缀。

---

## 备注

1. **缩放跳过条件**：当 `DataTypeA` 或 `DataTypeB` 为 `FP16/BF16` 时，硬件将忽略对应数据矩阵的缩放操作，直接使用该矩阵作为矩阵乘输入。此时 缩放矩阵所在的输入Tile 可省略或忽略。
2. **寄存器依赖**：本指令依赖 4 个源 Tile 寄存器，请确保在执行前数据已正确加载。
3. **ACC 约束**：本指令只允许输出到 ACC 寄存器中。
4. **最小分形大小**：Scale Tile 中的最小分形大小要求为 32 字节。
