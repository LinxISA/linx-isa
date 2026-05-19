# TMATMUL

## 说明

**矩阵乘法（Matrix Multiply）**

`TMATMUL` 用于将两个输入Tile寄存器中的 **A矩阵** 与 **B矩阵** 相乘，结果矩阵写到ACC寄存器中。

```text
Matrix_C = Matrix_A * Matrix_B
```
对任意行 i、列 j，有:
```c
C[i, j] = sum_k(A[i, k] × B[k, j])
```

关于矩阵运算的输入输出要求请见[矩阵数据块](../../blockIntro/cube_block/intro.md)介绍。

## 汇编语法

```asm
TMATMUL <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, ->ACC<Size>
```

## 汇编符号

- **M、N、K**：表示输入矩阵的尺寸，可分别通过`全局寄存器`、`立即数`或`全局寄存器加立即数`的形式设置。
    - A矩阵的尺寸为：`M行K列`；
    - B矩阵的尺寸为：`K行N列`。
- **DataTypeA**：表示A矩阵中元素数据格式。
- **DataTypeB**：表示B矩阵中元素数据格式。允许与 DataTypeA 不同，如果和 DataTypeA 相同时允许缺省。
- **SrcTile0**：存储A矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile1**：存储B矩阵的[Tile 寄存器](../../register/common/tilereg.md)。
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

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `TMATMUL, DataTypeA`
- [B.DATR](../../header/B.DATR.md) `DataTypeB`    *(注：DataTypeB 和 DataTypeA 相同时可缺省该指令)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    *(注：M)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    *(注：N)*
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    *(注：K)*
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, last, ->ACC<Size>`

---

## <span id="execmodel">执行模型</span>

本指令执行过程通过伪代码示意如下：
```cpp
// TMATMUL: C = A x B
void TMATMUL(Tile __out__ C, Tile __in__ B, Tile __in__ A) {
  for (int i = 0; i < C.m; i++)
    for (int j = 0; j < C.n; j++) {
      C[i][j] = 0;
      for (int k = 0; k < A.k; k++)
        C[i][j] += A[i][k] * B[k][j];
    }
}
```

实现示意图如下：

![TMATMUL](../../../figs/isa/tileop/TMATMUL.png){ width="800" }

执行混合精度的CUBE运算时，需要特殊注意的是：

- **当左右矩阵元素的位宽比是4:1时**：由于左矩阵小分形的M维度大小与右矩阵小分形的N维度相同（都是16），左矩阵小分形K维度大小是右矩阵小分形K维度大小的1/4，因此每次CUBE都会从左矩阵中获取一个分形数据，并从右矩阵中获取1/4个分形数据以生成输出分形。
- **当左右矩阵元素的位宽比是2:1时**：由于左矩阵小分形的M维度大小与右矩阵小分形的N维度相同（都是16），左矩阵小分形K维度大小是右矩阵小分形K维度大小的1/2，因此每次CUBE都会从左矩阵中获取一个分形数据，并从右矩阵中获取1/2个分形数据以生成输出分形。
- 其他情况以此类推。

![TMATMUL_HYBRID](../../../figs/isa/tileop/TMATMUL_HYBRID.png){ width="900" }

---

## 汇编示例

示例1：fp16 x fp8(e5m2)
```asm
TMATMUL <LB0:32, LB1:64, LB2:16, fp16, e5m2> T#1.reuse, M#1, ->ACC<8KB>
```

- 输入左矩阵：
    - 寄存器：SrcTile0 = T#1，添加了 `.reuse` 标记，表示本指令提交后保留该寄存器。
    - 形状尺寸（M x K）：32 x 16
    - 数据格式：fp16
- 输入右矩阵：
    - 寄存器：SrcTile1 = M#1，没有 `.reuse` 标记，表示本指令提交后可释放该寄存器。
    - 形状尺寸（K x N）：16 x 64
    - 数据格式：e5m2
- 输出结果矩阵：
    - 寄存器：DstTile = ACC，申请空间 8KB。
    - 形状尺寸（M x N）：32 x 64
    - 数据格式：fp32, 输入统一转换为fp32精度进行CUBE运算。


示例2：TMATMUL的e1m2x2输入
```asm
TMATMUL <LB0:32, LB1:32, LB2:64, e1m2x2>, T#1.reuse, U#1, ->ACC<4KB>
```

- 输入左矩阵：
    - 寄存器：SrcTile0 = T#1，添加了 `.reuse` 标记，表示本指令提交后保留该寄存器。
    - 形状尺寸（M x K）：32 x 64
    - 数据格式：e1m2x2
- 输入右矩阵：
    - 寄存器：SrcTile1 = U#1，没有 `.reuse` 标记，表示本指令提交后可释放该寄存器。
    - 形状尺寸（K x N）：64 x 32
    - 数据格式：e1m2x2
- 输出结果矩阵：
    - 寄存器：DstTile = ACC，申请空间 4KB。
    - 形状尺寸（M x N）：32 x 32
    - 数据格式：fp32, 输入统一转换为fp32精度进行CUBE运算。

---

## 备注

1. 本指令只允许输出到ACC寄存器中。
2. 本指令是一种模版块，软件只定义块头。
