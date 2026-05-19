# TMATMUL.ACC

## 说明

**矩阵乘累加（MatrixA Multiply MatrixB and Accumulate）**

`TMATMUL.ACC` 用于将两个输入Tile寄存器中的 **A矩阵** 与 **B矩阵** 相乘，结果累加到ACC寄存器中 **C矩阵** 上。

```text
Matrix_C += Matrix_A * Matrix_B
```

关于矩阵运算的输入输出要求请见[矩阵数据块](../../blockIntro/cube_block/intro.md)介绍。

## 汇编语法

```asm
TMATMUL.ACC <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, ACC, ->ACC<Size>
```

## 汇编符号

- **M、N、K**：表示输入矩阵的尺寸，可分别通过`全局寄存器`、`立即数`或`全局寄存器加立即数`的形式设置。
    - **M**：表示A矩阵的行数。
    - **N**：表示B矩阵的列数。
    - **K**：表示A矩阵的列数（也是B矩阵的行数）。
- **DataTypeA**：表示A矩阵中元素数据格式。
- **DataTypeB**：表示B矩阵中元素数据格式。允许与 DataTypeA 不同，如果和 DataTypeA 相同时允许缺省。
- **SrcTile0**：存储A矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile1**：存储B矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **reuse**：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **ACC**：存储C矩阵和结果矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **Size**：指示输出Tile寄存器空间大小的立即数。容量约束请见[Tile寄存器介绍](../../register/common/tilereg.md)。

本指令 A/B矩阵支持的数据类型（DataTypeA/B）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8, U8, E4M3, E5M2, E2M3, E3M2 |
| b4  | S4x2, U4x2, E2M1x2, E1M2x2 |

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `TMATMUL.ACC, DataTypeA`
- [B.DATR](../../header/B.DATR.md) `DataTypeB`    *(注：DataTypeB 和 DataTypeA 相同时可缺省该指令)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    *(注：M)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    *(注：N)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    *(注：K)*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last, ->ACC<Size>`

注意：ACC寄存器为隐含输入。

## 执行模型

本指令执行过程通过伪代码示意如下：
```cpp
// TMATMUL_ACC: C += A x B （累加操作）
void TMATMUL_ACC(Tile __out__ C, Tile __in__ B, Tile __in__ A) {
  for (int i = 0; i < C.m; i++)
    for (int j = 0; j < C.n; j++)
      for (int k = 0; k < A.k; k++)
        C[i][j] += A[i][k] * B[k][j];
}
```

实现示意图如下:

![TMATMUL.ACC](../../../figs/isa/tileop/TMATMUL.ACC.png){ width="900" }

执行混精的CUBE运算时注意事项同[TMATMUL指令](./TMATMUL.md#execmodel)。

---

## 汇编示例

```asm
TMATMUL.ACC <LB0:100, LB1:a0, LB2:a1+10, FP32>, T#1, U#1, ACC, ->ACC<64KB>
```

- **输入输出**：
    - SrcTile0 = T#1：A 矩阵 tile。
    - SrcTile1 = U#1：B 矩阵 tile。
    - 两者未带 .reuse，表示本指令提交后可由硬件释放；若需后续复用请加 .reuse。
    - ACC：作为隐含输入与显式输出，存放 C 矩阵，容量 64KB。
- **尺寸参数**：
    - A 维度 M×K = 100 × (a1 + 10)。
    - B 维度 K×N = (a1 + 10) × a0。
    - 输出 C 维度 M×N = 100 × a0。
- **数据类型**：
    - FP32：A、B、C 的元素均为 32 位浮点；容量与对齐按 FP32 规则计算。
- **约束与一致性**：
    - 维度一致性：K (= a1 + 10) 同时匹配 A 的列与 B 的行。
    - ACC 为累加器：若需清零，请在本指令前执行清空或初始化。
    - a0、a1 的取值需满足硬件/编译期约束（合法范围、对齐/分块要求等）。
    - ACC 容量 64KB 需能容纳 C 的 FP32 布局。

---

## 备注

1. 本指令只允许输出到ACC寄存器中。
2. 本指令是一种模版块，软件只定义块头。
