# TMATMUL.BIAS

## 说明

**带偏置矩阵乘（Matrix Multiply with Bias）**

`TMATMUL.BIAS` 用于将前两个输入Tile寄存器中的 **A矩阵** 与 **B矩阵** 相乘，再加上第三个输入Tile寄存器中的 **Bias矩阵**，结果矩阵写到ACC寄存器中。

```text
Matrix_C = Matrix_A * Matrix_B + Matrix_Bias
```
Bias 为 1×N 向量，对应按列广播：对任意行 i、列 j，有:
```c
C[i, j] = sum_k(A[i, k] × B[k, j]) + Bias[0, j]
```

关于矩阵运算的输入输出要求请见[矩阵数据块](../../blockIntro/cube_block/intro.md)介绍。

## 汇编语法

```asm
TMATMUL.BIAS <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, ->ACC<Size>
```

## 汇编符号

- **M、N、K**：表示输入矩阵的尺寸，可分别通过`全局寄存器`、`立即数`或`全局寄存器加立即数`的形式设置。
    - A矩阵的尺寸为：`M行K列`；
    - B矩阵的尺寸为：`K行N列`；
    - Bias矩阵的尺寸为：`1行N列`。
- **DataTypeA**：表示A矩阵中元素数据格式。
- **DataTypeB**：表示B矩阵中元素数据格式。允许与 DataTypeA 不同，如果和 DataTypeA 相同时允许缺省。
- **SrcTile0**：存储A矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile1**：存储B矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile2**：存储Bias矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **reuse**：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **ACC**：存储结果矩阵的[Tile 寄存器](../../register/common/tilereg.md)类型。
- **Size**：指示输出Tile寄存器空间大小的立即数。容量约束请见[Tile寄存器介绍](../../register/common/tilereg.md)。

本指令 A/B矩阵支持的数据类型（DataTypeA/B）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8, U8, E4M3, E5M2, E2M3, E3M2 |
| b4  | S4x2, U4x2, E2M1x2, E1M2x2 |

Bias 矩阵特点：

- 形状：`1×N`（单行，列数与输出矩阵列数相同）。
- 数据类型：必须与结果矩阵 C 的数据类型完全匹配。
- 布局：必须是行主序（row-major）。

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `TMATMUL.BIAS, DataTypeA`
- [B.DATR](../../header/B.DATR.md) `DataTypeB`    *(注：DataTypeB 和 DataTypeA 相同时可缺省该指令)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    *(注：M)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    *(注：N)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    *(注：K)*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, last, ->ACC<Size>`

---

## 执行模型

本指令执行过程通过伪代码示意如下：
```cpp
// TMATMUL.BIAS: D = A x B + Bias
// Bias: 1 x n, A: m x k, B: k x n, D: m x n
// 将 A x B 的结果加到 Bias 上，存入 D
void TMATMUL.BIAS(Tile __out__ D, Tile __in__ A, Tile __in__ B, Tile __in__ Bias) {
  for (int i = 0; i < D.m; i++)
    for (int j = 0; j < D.n; j++)
      for (int k = 0; k < A.k; k++)
        D[i][j] = A[i][k] * B[k][j] + Bias[0][j];
}
```

执行混精的CUBE运算时注意事项同[TMATMUL指令](./TMATMUL.md#execmodel)。

---

## 汇编示例

```asm
TMATMUL.BIAS <LB0:100, LB1:a0, LB2:a1+10, FP32>, T#1, U#1, N#1, ->ACC<64KB>
```

- **输入/输出含义**:
    - SrcTile0 = T#1：存放 A 矩阵的 tile。
    - SrcTile1 = U#1：存放 B 矩阵的 tile。
    - SrcTile2 = N#1：存放 Bias 矩阵的 tile（形状 1×N，按列广播到输出的每一行）。
    - 以上三个源寄存器均未带 `.reuse` 后缀，表示本条指令提交后，硬件可释放这些寄存器的占用。
    - DstTile = ACC：存放结果矩阵 C 的 tile，容量配置为 64KB。
- **尺寸参数设定**:
    - M = LB0:100，表示 A 的行数为 100。
    - N = LB1:a0，表示 B 的列数为 a0（同时也是 Bias 的列数与 C 的列数）。
    - K = LB2:a1+10，表示 A 的列数与 B 的行数为 (a1 + 10)。
    - 因此各矩阵维度为：
    - A：`M×K = 100 × (a1 + 10)`
    - B：`K×N = (a1 + 10) × a0`
    - Bias：`1×N = 1 × a0`（按列广播）
    - C：`M×N = 100 × a0`
- **数据类型**:
    - FP32：A、B、Bias、C 的元素类型均为 32 位浮点（E8M23）。容量计算、带宽与对齐约束按 FP32 规则执行。
    - 注意：Bias 的数据类型必须与输出 C 完全一致（此处为 FP32）。
- **约束与一致性**:
    - 维度一致性：
        - K 一致：A 的列数与 B 的行数均为 a1 + 10。
        - N 一致：B 的列数、Bias 的列数与 C 的列数均为 a0。
        - Bias 形状固定为 1×N，并按列广播到 C 的每一行。
    - 数据类型一致性：
        - A、B、Bias、C 必须使用本条指令给定的 DataType（此处为 FP32）。
    - 布局要求（Bias）：
        - Bias 必须为行主序（row-major），长度为 N 的单行向量。
    - ACC 容量要求：
        - `输出 C 的字节数 = M × N × sizeof(FP32) = 100 × a0 × 4`。
        - 需满足 100 × a0 × 4 ≤ 64KB。
        - 若 a0 超出该范围，应增大 ACC 容量或分块输出。
    - 参数取值合法性：
        - a0、a1 应在硬件/编译期允许范围内（非负，满足分块/对齐要求等）。
        - 若硬件对 M、N、K 有分块粒度或倍数要求（例如需为某个 tile 大小的倍数），需确保 100、a0、a1+10 满足相应粒度。
    - 复用控制：
        - 如果后续指令仍要使用 T#1/U#1/N#1 的内容，请在本条指令的对应源寄存器后添加 `.reuse` 后缀，避免被硬件释放。

---

## 备注

1. 本指令只允许输出到ACC寄存器中。
2. 本指令是一种模版块，软件只定义块头。
