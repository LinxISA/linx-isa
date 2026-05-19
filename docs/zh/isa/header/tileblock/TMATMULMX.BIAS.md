# TMATMULMX.BIAS

## 说明

**带缩放的矩阵乘累加偏置（Matrix Multiply with Scaling and Bias）**

`TMATMULMX.BIAS` 用于对输入 Tile 寄存器中的 **A 矩阵** 与 **B 矩阵** 分别进行缩放处理后，执行矩阵乘运算，并将结果加上**偏置向量 Bias** 后写到 ACC 寄存器中。

计算公式如下：
```text
C[i, j] = Σ(k=0 to K-1) (A[i, k] * ScaleA[i, k]) × (B[k, j] * ScaleB[k, j]) + Bias[0, j]
```

支持混精度矩阵乘法，包含额外的缩放 Tile 用于量化/反量化，并支持融合偏置加法。

关于矩阵运算的输入输出要求请见 [矩阵数据块](../../blockIntro/cube_block/intro.md) 介绍。

## 汇编语法

```asm
TMATMULMX.BIAS <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, SrcTile3<.reuse>, SrcTile4<.reuse>, ->ACC<Size>
```

## 汇编符号

- **M、N、K**：表示输入矩阵的尺寸，可分别通过 `全局寄存器 `、` 立即数` 或 `全局寄存器加立即数` 的形式设置。
    - 数据矩阵A的尺寸为：`M行K列`；缩放矩阵A的行数与数据矩阵A相同，列数根据数据类型而定。
    - 数据矩阵B的尺寸为：`K行N列`；缩放矩阵A的列数与数据矩阵A相同，行数根据数据类型而定。
    - Bias矩阵的有效列数为N）。
- **DataTypeA**：表示数据矩阵A中元素数据格式。
- **DataTypeB**：表示数据矩阵B中元素数据格式。允许与 DataTypeA 不同，如果和 DataTypeA 相同时允许缺省。
- **SrcTile0**：存储 **数据矩阵A** (Data Matrix A) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile1**：存储 **缩放矩阵A** (Scale Matrix A) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile2**：存储 **数据矩阵B** (Data Matrix B) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile3**：存储 **缩放矩阵B** (Scale Matrix B) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile4**：存储 **偏置向量Bias** (Bias Vector) 的 [Tile 寄存器](../../register/common/tilereg.md)。
- **reuse**：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **ACC**：存储结果矩阵的 [Tile 寄存器](../../register/common/tilereg.md) 类型。
- **Size**：指示输出 Tile 寄存器空间大小的立即数，例如 `` `ACC<64KB>` ``。

---

## 数据布局与类型约束

### 数据矩阵与缩放矩阵

本指令对数据矩阵和缩放矩阵的要求同[TMATMULMX指令](./TMATMULMX.md#constrain)。

### 偏置向量 (Bias Vector)

| 参数 | 分形格式 (Layout) | 形状 | 数据类型 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **Bias** | 行主序 (`Row-Major`) | `1 × N` | 与结果矩阵 C 完全匹配 | 单行向量，长度等于输出列数 N |

**Bias 约束说明：**

1. **形状**：必须是 `1×N` 的单行向量。
2. **数据类型**：必须与结果矩阵 C 的数据类型完全匹配（例如：若输出为 FP32，则 Bias 必须为 FP32）。
3. **广播机制**：Bias 向量会自动广播到结果矩阵的每一行（`C[i, j] += Bias[0, j]`）。

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `MAMULBMXAC, DataTypeA`
- [B.DATR](../../header/B.DATR.md) `DataTypeB`   *(注：DataTypeB 和 DataTypeA 相同时可缺省)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    *(注：M)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    *(注：N)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    *(注：K)*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`   *(A, ScaleA)*
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, SrcTile3<.reuse>`   *(B, ScaleB)*
- [B.IOT](../../header/B.IOT.md) `SrcTile4<.reuse>, last, ->ACC<Size>`  *(Bias, Out)*

## 执行模型

本指令执行过程通过伪代码示意如下：
```cpp
// TMATMULMX.BIAS: C = (ScaleA * A) * (ScaleB * B) + Bias
void TMATMULMX_BIAS(Tile __out__ C, Tile __in__ A, Tile __in__ ScaleA, 
                    Tile __in__ B, Tile __in__ ScaleB, Tile __in__ Bias) {
  
  // 1. 缩放处理
  Tile A_scaled = (DataTypeA == FP16 || DataTypeA == BF16) ? A : (ScaleA * A);
  Tile B_scaled = ScaleB * B;
  
  // 2. 矩阵乘累加 + 偏置
  for (int i = 0; i < C.m; i++)
    for (int j = 0; j < C.n; j++) {
      C[i][j] = Bias[0][j]; // 初始化偏置
      for (int k = 0; k < A_scaled.k; k++)
        C[i][j] += A_scaled[i][k] * B_scaled[k][j];
    }
}
```

实现示意图如下：

![TMATMULMX](../../../figs/isa/tileop/TMATMULMX_FP4.png){ width="900" }

## 汇编示例

```asm
TMATMULMX.BIAS <LB0:100, LB1:a0, LB2:a1+10, e5m2, e1m2x2>, T#1, U#1, M#1, N#1, T#2, ->ACC<64KB>
```

- **输入输出**：
    - `SrcTile0 = T#1`：存放 A 矩阵。
    - `SrcTile1 = U#1`：存放 A 缩放矩阵。
    - `SrcTile2 = M#1`：存放 B 矩阵。
    - `SrcTile3 = N#1`：存放 B 缩放矩阵。
    - `SrcTile4 = T#2`：存放 **Bias 偏置向量** (1xN)。
    - `DstTile = ACC`：存放结果矩阵。
- **尺寸参数设定**:
    - A 的维度为 `M×K = 100 × (a1 + 10)`。
    - B 的维度为 `K×N = (a1 + 10) × a0`。
    - Bias 的长度为 `N = a0`。
- **约束与一致性**:
    - **Bias 类型**：T#2 中的数据类型必须与 ACC 输出类型一致（如均为 FP32）。
    - **Bias 形状**：T#2 必须配置为 1xN 的行向量布局。
    - **K 对齐**：若使用 `e4m3`/`e5m2` 类型，K 必须是 64 的倍数。
    - **复用约束**：若后续指令仍需使用 T#1~X#1 中的数据，必须添加 `.reuse` 后缀。

## 备注

1. **偏置融合**：本指令将偏置加法融合在矩阵乘过程中，无需单独执行加法指令，提高效率。
2. **Bias 初始化**：ACC 寄存器中的结果直接初始化为 Bias 值后累加，无需预先清零或加载。
3. **缩放跳过条件**：当 `DataTypeA` 为 `FP16` 或 `BF16` 时，硬件将忽略 `SrcTile1` (ScaleA) 的缩放操作。
4. **寄存器依赖**：本指令依赖 **5 个源 Tile 寄存器**，请确保在执行前数据已正确加载且布局符合约束。
5. **最小分形大小**：Scale Tile 中的最小分形大小要求为 32 字节。
