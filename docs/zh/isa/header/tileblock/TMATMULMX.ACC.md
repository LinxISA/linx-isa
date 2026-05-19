# TMATMULMX.ACC

## 说明

**带缩放的矩阵乘累加（Matrix Multiply with Scaling and Accumulate）**

`TMATMULMX.ACC` 用于对两个输入 Tile 寄存器中的 **A 矩阵** 与 **B 矩阵** 分别进行缩放处理后，执行矩阵乘运算，并将结果**累加**到 ACC 寄存器中原有的数据上。

缩放计算：`Matrix_C = (DataMatrix_A × ScaleMatrix_A) * (DataMatrix_B × ScaleMatrix_B)`。当数据矩阵（`DataMatrix A/B`）的 DataType 为 FP16或BF16 格式时，数据矩阵不进行缩放操作，因此可缺省对应的缩放矩阵输入。

关于矩阵运算的输入输出要求请见 [矩阵数据块](../../blockIntro/cube_block/intro.md) 介绍。

## 汇编语法

```asm
TMATMULMX.ACC <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, SrcTile3<.reuse>, ACC, ->ACC<Size>
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
- **ACC**：**输入兼输出**。存储 **C 矩阵** (Matrix C) 及结果矩阵的 [Tile 寄存器](../../register/common/tilereg.md)。
    - 执行前：存放累加前的初始值。
    - 执行后：存放累加后的结果值。
- **Size**：指示输出 Tile 寄存器空间大小的立即数，例如 `ACC<64KB>`。

---

## 数据布局与类型约束

本指令对数据矩阵和缩放矩阵的要求同[TMATMULMX指令](./TMATMULMX.md#constrain)。

---

## 编码格式

本指令将拆分成以下进行编码：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `MAMULBMX.ACC, DataTypeA`
- [B.DATR](../../header/B.DATR.md) `DataTypeB`   *(注：DataTypeB 和 DataTypeA 相同时可缺省)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    *(注：M)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    *(注：N)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    *(注：K)*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`   *(A, ScaleA)*
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, SrcTile3<.reuse>, last, ACC, ->ACC<Size>`   *(B, ScaleB)*

## 执行模型

本指令执行过程通过伪代码示意如下：
```cpp
// TMATMULMX.ACC: C = (ScaleA * A) * (ScaleB * B) + C
void TMATMULMX_ACC(Tile __inout__ C, Tile __in__ A, Tile __in__ ScaleA, 
                   Tile __in__ B, Tile __in__ ScaleB) {
  
  // 1. 缩放处理
  Tile A_scaled = (DataTypeA == FP16 || DataTypeA == BF16) ? A : (ScaleA * A);
  Tile B_scaled = ScaleB * B;
  
  // 2. 矩阵乘累加
  for (int i = 0; i < C.m; i++)
    for (int j = 0; j < C.n; j++) {
      // 注意：C[i][j] 既有输入值也有输出值
      for (int k = 0; k < A_scaled.k; k++)
        C[i][j] += A_scaled[i][k] * B_scaled[k][j];
    }
}
```

实现示意图如下：

![TMATMULMX](../../../figs/isa/tileop/TMATMULMX_FP4.png){ width="900" }

## 汇编示例

```asm
TMATMULMX.ACC <LB0:100, LB1:a0, LB2:a1+10, e4m3, e5m2>, T#1, U#1, M#1, N#1, ACC, ->ACC<64KB>
```

- **输入输出**：
    - `SrcTile0 = T#1`：存放 A 矩阵。
    - `SrcTile1 = U#1`：存放 A 缩放矩阵。
    - `SrcTile2 = M#1`：存放 B 矩阵。
    - `SrcTile3 = N#1`：存放 B 缩放矩阵。
    - **`ACC`**：**既是输入也是输出**。执行前存放初始矩阵 C，执行后存放累加结果。
- **指令功能**：执行带缩放的矩阵乘累加 `C = (ScaleA × A) × (ScaleB × B) + C`。
- **尺寸参数设定**:
    - A 的维度为 `M×K = 100 × (a1 + 10)`。
    - B 的维度为 `K×N = (a1 + 10) × a0`。
    - 结果 C 的维度为 `M×N = 100 × a0`。
- **约束与一致性**:
    - **初值约束**：ACC 寄存器在执行本指令前必须已加载有效的初始数据（除非目的是覆盖，但通常 ACC 指令意味着累加）。
    - **维度一致性**：K 必须与 A 的列数及 B 的行数一致。
    - **K 对齐**：若使用 `e4m3`/`e5m2` 类型，K 必须是 64 的倍数。
    - **复用约束**：若后续指令仍需使用 T#1~W#1 中的数据，必须添加 `.reuse` 后缀。

## 备注

1. **累加语义**：与 `TMATMULMX` 不同，本指令**不会清空** ACC 寄存器中的原有数据，而是进行累加。请确保 ACC 在使用前已初始化。
2. **缩放跳过条件**：当 `DataTypeA` 为 `FP16` 或 `BF16` 时，硬件将忽略 `SrcTile1` (ScaleA) 的缩放操作。
3. **寄存器依赖**：本指令依赖 4 个源 Tile 寄存器 + 1 个 ACC 寄存器。
4. **最小分形大小**：Scale Tile 中的最小分形大小要求为 32 字节。
