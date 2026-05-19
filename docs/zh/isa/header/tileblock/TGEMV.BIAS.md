# TGEMV.BIAS

## 说明

**通用矩阵-向量带偏置乘法（General Matrix-Vector Multiply with Bias）**

`TGEMV.BIAS` 用于将两个输入 Tile 寄存器中的 **A向量** 与 **B矩阵** 相乘，再加上**偏置Bias矩阵**，结果写到ACC寄存器中。

实现伪代码示意如下：
```pseudocode
// 矩阵-向量乘累加操作
for n in 0..(N-1):         // 遍历N维度
  C[0, n] = 0;
  for k in 0..(K-1):       // 遍历K维度
    C[0, n] += A[0, k] × B[k, n]
  C[0, n] += Bias[0, n]    // 加偏置矩阵
```

实现示意图如下：

![TGEMV.BIAS](../../../figs/isa/tileop/TGEMV.BIAS.png){ width="800" }

---

## 汇编语法

```asm
TGEMV.BIAS <LB0:M, LB1:N, LB2:K, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, ->ACC<Size>
```

## 汇编符号

- **M、N、K**：表示输入矩阵/向量的维度，支持通过全局寄存器、立即数或全局寄存器 + 立即数三种形式进行配置。
    - **A 向量**的形状为：`1 × K`。（输入 Tile 的第一行作为 A 向量）
    - **B 矩阵**的形状为：`K × N`。
    - **结果 矩阵**和**偏置Bias矩阵**的形状为：`1 × N`。
- **DataType**：表示输入矩阵/向量中元素数据格式，支持类型见下表。
- **SrcTile0**：存储A向量的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **SrcTile1**：存储B矩阵的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **SrcTile2**：存储Bias矩阵的[Tile 寄存器](../../register/common/tilereg.md)，支持`T`/`U`/`M`/`N`队列输入。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **ACC**：存储结果矩阵的[Tile 寄存器](../../register/common/tilereg.md)类型。
- **Size**：输出Tile寄存器的空间大小（有效范围参见：[Tile寄存器](../../register/common/tilereg.md)）。

本指令支持数据类型（DataType）如下表所示：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2), HiF8, HiF4x2, E1M2x2, E2M1x2, S4x2, U4x2 |



---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) `TGEMV.BIAS, DataType`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    （注：*M*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    （注：*N*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    （注：*K*）
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, last, ->ACC<Size>`

---

## 汇编示例

```asm
TGEMV.BIAS <LB0:1, LB1:32, LB2:32, FP16>, T#1, U#1, M#1, ->ACC<256B>
```

- **输入输出**：
    - `SrcTile0 = T#1`：存放 A 向量的 tile。
    - `SrcTile1 = U#1`：存放 B 矩阵的 tile。
    - `SrcTile2 = M#1`：存放 Bias 矩阵的 tile。
    - 输入 tile 均未带 .reuse 后缀，表示本条指令提交后，硬件允许释放这些寄存器的占用。
    - `DstTile = ACC`: 存放C矩阵的 tile，分配容量为 256B。
- **尺寸参数设定**:
    - A 的维度为 `1×K = 1 × 32`，K 通过 “立即数” 设定。
    - B 的维度为 `K×N = 32 x 32`，N 通过 “立即数” 设定。
    - 结果 C 的维度为 `1×N = 1 x 32`。
- **数据类型**:
    - 输入 A、B 的元素为 16 位浮点数。
    - 输出 C 的元素为 32 位浮点数。容量计算、带宽与对齐约束以 FP32 规则为准。
- **约束与一致性**:
    - 维度一致性：K 必须与 A 的列数及 B 的行数一致。
    - M、N 的值应在硬件/编译期允许的范围内，并满足指令执行时的合法性（如非负、对齐/分块要求等）。
    - 若需要在后续指令继续复用 T#1 或 U#1 的数据，应在本指令中为相应源寄存器添加 `.reuse` 后缀，避免被硬件释放。

---

## 备注

1. 本指令只允许输出到ACC寄存器中。
2. 本指令是一种模版块，软件只定义块头。
