# 0.57版本更新

更新日期：2026年6月1日

---

## 一、版本概述

灵犀指令集 (LinxISA) **0.57** 版本在 0.56 版本的基础上，新增 8 组向量/标量指令，覆盖整数绝对值与绝对差值计算、自然对数运算、ReLU/Leaky ReLU 激活函数以及浮点舍入到整数等场景。此外，对 Tile 形参寄存器架构进行优化，将栈空间形参 TS 与输出形参 TO1 彻底分离；并对 ACCCVT 指令进行重大增强，引入随路量化能力并重构参数模型。同时，新增 33 条 TileOp 张量指令，覆盖数据搬运/布局、逐元素幂运算、按轴 argmax/argmin、复杂操作（部分逐元素、归并排序、量化、随机数等）等领域，显著扩展了 Tile 级并行计算能力。以上变更进一步增强指令集在 AI 算子加速和数值计算领域的表达能力。

---

## 二、版本变更要点

| 序号 | 变更事项 | 变更原因与目标 |
|------|----------|----------------|
| 1 | **新增 ABS 指令**（`v.abs` / `l.abs`） | 提供单指令整数绝对值计算能力，避免编译器展开为比较+取负序列，提升整数绝对值运算的效率。 |
| 2 | **新增 ABSDIF 指令**（`v.absdif` / `l.absdif`） | 提供单指令整数绝对差值计算能力，常用于图像处理、信号处理中的距离度量等场景。 |
| 3 | **新增 FLN 指令**（`v.fln` / `l.fln`） | 提供单指令自然对数计算能力，用于指数变换、概率模型对数似然计算、归一化等场景。 |
| 4 | **新增 RELU 指令**（`v.relu` / `l.relu`） | 提供单指令整型 ReLU 激活能力，用于神经网络推理中的激活层加速。 |
| 5 | **新增 LRELU 指令**（`v.lrelu` / `l.lrelu`） | 提供单指令整型 Leaky ReLU 激活能力，在 ReLU 基础上支持负半轴的斜率参数化。 |
| 6 | **新增 FRELU 指令**（`v.frelu` / `l.frelu`） | 提供单指令浮点 ReLU 激活能力，避免浮点比较+选择的两步展开。 |
| 7 | **新增 FLRELU 指令**（`v.flrelu` / `l.flrelu`） | 提供单指令浮点 Leaky ReLU 激活能力，支持浮点负半轴斜率参数化。 |
| 8 | **新增 FRINT 指令**（`v.frint` / `l.frint`） | 提供浮点数舍入到整数值但保持浮点类型的能力。与 FCVT（跨类型格式转换）和 FCVTI（浮点转真正整数）形成清晰的指令层次：FRINT（float→float 舍入）、FCVTI（float→int 转换）、FCVT（跨精度 float→float 转换）。 |
| 9 | **TS 与 TO1 形参寄存器分离** | 原栈空间形参 TS 与第二个输出形参 TO1 共用编码槽位（编码 89），导致单输出块指令映射到 TO1 时模型处理异常。现将 TS 独立为编码 93，形参寄存器总数由 12 增至 13，栈空间与输出互不干扰。 |
| 10 | **ACCCVT 指令增强 — 随路量化、参数重构与编码简化** | 1) 新增量化参数 Tile（SrcTile），支持搬移过程中的逐行随路量化；2) 删除 DepSrc/DepDst 依赖描述符和 B.IOD 指令，简化编码格式；3) 重构 LB 参数为 ValidCol/ValidRow/Col 模型，Row 由 Size、Col 和数据位宽推导。 |
| 11 | **新增 33 条 TileOp 张量指令** | 补齐 TileOp 指令矩阵，覆盖数据搬运与布局（13 条）、逐元素幂运算（2 条）、按轴 argmax/argmin（4 条）、复杂操作（14 条）四大领域。所有新增 TileOp 统一采用输出 Tile 导向的 ValidCol/ValidRow/Col 参数模型。 |
| 12 | **新增持久化Tile寄存器（PT）及形参 TP** | 引入跨块持久化、不受 Tile 重命名影响的核内局部存储区域 PT。LTAR 中新增 TP 形参寄存器（形参总数 13→14），PT 通过 B.IOT 独立分配/释放，与调用方传入的输入输出 Tile 解耦。同步完善 LTAR 映射机制描述，明确 TP 与其他形参绑定方式的本质区别。 |
| 13 | **新增 TileInfo 硬件寄存器族** | 为每个 Tile 寄存器配备独立的 TileInfo 元数据寄存器（64-bit × 64），由硬件自动维护。当 B.IOT 输出到 Tile 时，硬件将维度、数据类型、布局等参数写入对应 TileInfo；后序块以该 Tile 为输入时，硬件从 TileInfo 自动获取元数据。TileInfo 不对软件可见，使得 TileOp 指令的 LB 参数语义统一为"仅描述输出 Tile 参数"。 |
| 14 | **CLZ → CLS 语义调整**（`cls` / `l.cls` / `v.cls`） | 将 Count Leading Zero bits（CLZ）调整为 Count Leading Sign bits（CLS），统计与符号位相同的连续位数。对于有符号数，统计前导符号位（1 或 0）；对于无符号数，统计前导零。指令助记符由 `clz`/`l.clz`/`v.clz` 改为 `cls`/`l.cls`/`v.cls`。 |
| 15 | **浮点比较指令区分为有序/无序比较** | 将浮点比较指令明确区分为有序比较（FEQ/FNE/FLT/FGE，NaN→False）和无序比较（FEQU/FNEU/FLTU/FGEU，NaN→True），替换旧版 FEQS/FNES/FLTS/FGES 命名，对齐 PTX `setp.equ` 等业界惯例。 |
| 16 | **新增 LUT 查找表指令**（`v.lutb.i2` 等 6 条） | 加速非线性运算与压缩/解压流程，通过预定义表格的索引访问代替繁复的逻辑与浮点运算，常用于图像处理、神经网络推理、MX-FP 反量化等场景。 |
| 17 | **新增 DOT 点积指令**（`v.dot` / `v.fdot` 2 条） | 提供向量单元细粒度点积运算能力，用于 4×4×4 及更小规模的矩阵乘，与 CUBE 单元的大规模矩阵乘互补。由 `vlen` 字段控制合并粒度（4-lane / 2-lane / 1-lane）。 |
| 18 | **sub-group reduce 指令扩展**（9 条） | 在原有 workgroup reduce 基础上增加 sub-group 归约能力，对原 9 条 reduce 指令统一增加 SrcR 和 imm10 参数，二者共同表示 sub-group 归约范围。 |
| 19 | **删除 B.IOD 指令** | B.IOD 为早期设计的依赖描述符指令，随着 0.57 架构演进，依赖管理已由硬件调度器自动处理，B.IOD 成为冗余。彻底删除 B.IOD 指令文档（4 个文件）、8 处交叉引用及全部编码行。 |

---

## 三、遗留问题

| 序号 | 问题描述 |
|------|----------|
| 1 | **非 TileOp 块（如 VPAR 块）写入的 Tile 寄存器，其 TileInfo 元数据如何获取。** TileOp 块通过 B.IOT 分配 Tile 时，LB 参数（ValidCol/ValidRow/Col/DataType 等）由硬件自动写入 TileInfo。VPAR 等非 TileOp 块虽然也有 B.IOT 用于绑定输出 Tile，但其 B.IOT 仅指定 Tile 寄存器和容量（Size），不携带维度、数据类型、布局等元数据。因此硬件无法在 VPAR 输出 Tile 时自动填充 TileInfo。后续 TileOp 块若以该 Tile 为输入，从 TileInfo 读取到的元数据将缺失或不准确。需明确非 TileOp 块输出 Tile 时的元数据传递机制（如在 VPAR 要求软件通过特定指令显式配置 TileInfo）。 |

---

## 四、更新详细说明

### 1. ABS — 整数绝对值

#### 1.1 指令定义

计算源寄存器中整数的绝对值。对于负数，结果为对应正数；对于非负数，结果等于原值。支持有符号整数类型。

**向量版本汇编格式：**
```asm
v.abs SrcL<.reuse>.{T}, ->RegDst.{W}, sat
```

**标量版本汇编格式：**
```asm
l.abs SrcL.<T>, ->RegDst.d, sat
```

参数说明：
- **SrcL**：源操作数。
- **T**：操作数类型，支持 `sb`, `sh`, `sw`, `sd`（有符号整数）。
- **sat**：可选的饱和计算标志。

#### 1.2 伪代码

```c
// 向量版本
for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        result = (operand < 0) ? -operand : operand;
        V[d, dstwidth, laneid] = result;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

---

### 2. ABSDIF — 整数绝对差值

#### 2.1 指令定义

计算左源寄存器和右源寄存器中整型数据的差值的绝对值。支持有符号和无符号整数类型。

**向量版本汇编格式：**
```asm
v.absdif SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}, sat
```

**标量版本汇编格式：**
```asm
l.absdif SrcL.<T>, SrcR.<T>, ->RegDst.d, sat
```

参数说明：
- **SrcL**、**SrcR**：两个源操作数。
- **T**：操作数类型，支持 `sb`, `sh`, `sw`, `sd`, `ub`, `uh`, `uw`, `ud`。
- **sat**：可选的饱和计算标志。

#### 2.2 伪代码

```c
// 向量版本
for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        diff = operand1 - operand2;
        result = (diff < 0) ? -diff : diff;
        V[d, dstwidth, laneid] = result;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

---

### 3. FLN — 自然对数

#### 3.1 指令定义

计算源寄存器中浮点数的以 e 为底的自然对数值。输入必须为正数。

**向量版本汇编格式：**
```asm
v.fln SrcL<.reuse>.{T}, ->RegDst.{W}, rm, sat
```

**标量版本汇编格式：**
```asm
l.fln SrcL.<T>, ->RegDst.d, rm, sat
```

参数说明：
- **SrcL**：源操作数。
- **T**：操作数类型，支持 `fb`, `fh`, `fs`, `fd`（BF16、FP16、FP32、FP64）。
- **rm**：舍入模式，编码同 [V.FCVT](../isa/inst/misa_v/V.FCVT.md)。
- **sat**：可选的饱和计算标志。

#### 3.2 伪代码

```c
// 向量版本
for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        result = ln(operand);
        V[d, dstwidth, laneid] = result;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

---

### 4. RELU — 整型 ReLU 激活

#### 4.1 指令定义

对源寄存器中的整型数据执行 ReLU（线性整流）激活操作：若源操作数大于等于零，则输出原值；否则输出零。

**向量版本汇编格式：**
```asm
v.relu SrcL<.reuse>.{T}, ->RegDst.{W}
```

**标量版本汇编格式：**
```asm
l.relu SrcL.<T>, ->RegDst.d
```

参数说明：
- **SrcL**：源操作数。
- **T**：操作数类型，支持 `sb`, `sh`, `sw`, `sd`（有符号整数）。

#### 4.2 伪代码

```c
// 向量版本
for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        result = (operand >= 0) ? operand : 0;
        V[d, dstwidth, laneid] = result;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

---

### 5. LRELU — 整型 Leaky ReLU 激活

#### 5.1 指令定义

对左源寄存器中的整型数据执行 Leaky ReLU（泄漏线性整流）激活操作：若左源操作数大于等于零，则输出原值；否则输出左源操作数与右源操作数的乘积。

**向量版本汇编格式：**
```asm
v.lrelu SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}, sat
```

**标量版本汇编格式：**
```asm
l.lrelu SrcL.<T>, SrcR.<T>, ->RegDst.d, sat
```

参数说明：
- **SrcL**：输入数据/特征。
- **SrcR**：负半轴斜率（leaky slope）。
- **T**：操作数类型，支持 `sb`, `sh`, `sw`, `sd`。
- **sat**：可选的饱和计算标志。

#### 5.2 伪代码

```c
// 向量版本
for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        result = (operand1 >= 0) ? operand1 : (operand1 * operand2);
        V[d, dstwidth, laneid] = result;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

---

### 6. FRELU — 浮点 ReLU 激活

#### 6.1 指令定义

对源寄存器中的浮点型数据执行 ReLU 激活操作：若源操作数大于等于零，则输出原值；否则输出浮点零。

**向量版本汇编格式：**
```asm
v.frelu SrcL<.reuse>.{T}, ->RegDst.{W}, rm, sat
```

**标量版本汇编格式：**
```asm
l.frelu SrcL.<T>, ->RegDst.d, rm, sat
```

参数说明：
- **SrcL**：源操作数。
- **T**：操作数类型，支持 `fb`, `fh`, `fs`, `fd`。
- **rm**：舍入模式，编码同 [V.FCVT](../isa/inst/misa_v/V.FCVT.md)。
- **sat**：可选的饱和计算标志。

---

### 7. FLRELU — 浮点 Leaky ReLU 激活

#### 7.1 指令定义

对左源寄存器中的浮点型数据执行 Leaky ReLU 激活操作：若左源操作数大于等于零，则输出原值；否则输出左源操作数与右源操作数的乘积。

**向量版本汇编格式：**
```asm
v.flrelu SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, ->RegDst.{W}, rm, sat
```

**标量版本汇编格式：**
```asm
l.flrelu SrcL.<T>, SrcR.<T>, ->RegDst.d, rm, sat
```

参数说明：
- **SrcL**：输入数据/特征。
- **SrcR**：负半轴斜率（leaky slope）。
- **T**：操作数类型，支持 `fb`, `fh`, `fs`, `fd`。
- **rm**：舍入模式，编码同 [V.FCVT](../isa/inst/misa_v/V.FCVT.md)。
- **sat**：可选的饱和计算标志。

---

### 8. FRINT — 浮点舍入到整数

#### 8.1 指令定义

将源寄存器中的浮点数按指定的舍入模式舍入到最接近的整数值，结果保持浮点格式。本指令仅对尾数进行舍入操作，不改变数据类型。

#### 8.2 与 FCVT / FCVTI 的关系

FRINT 与现有转换指令形成清晰的指令层次：

| 指令 | 操作 | 输入 → 输出 | 用途 |
|------|------|-------------|------|
| **FRINT** | 浮点舍入到整数 | `float` → `float` | 仅舍入尾数，类型不变 |
| **FCVTI** | 浮点转整数 | `float` → `int` | 类型转为真正整数 |
| **FCVT** | 跨精度格式转换 | `float` → `float`（不同位宽） | 完整格式转换流水线 |

#### 8.3 汇编格式

**向量版本：**
```asm
v.frint SrcL<.reuse>.{T}, ->RegDst.{W}, rm, sat
```

**标量版本：**
```asm
l.frint SrcL.<T>, ->RegDst.d, rm, sat
```

参数说明：
- **SrcL**：源操作数。
- **T**：操作数类型，支持 `fb`, `fh`, `fs`, `fd`。
- **W**：目的寄存器位宽，必须与源类型位宽一致。
- **rm**：舍入模式，编码如下：

| 编码 | 舍入模式 | 含义 |
|-----|----------|-----------|
| 0 | RNONE | No Rounding |
| 1 | RNE | Round to Nearest, ties to Even |
| 2 | RTZ | Round Toward Zero（截断） |
| 3 | RDN | Round Down（向 -∞，floor） |
| 4 | RUP | Round Up（向 +∞，ceil） |
| 5 | RNA | Round to Nearest, ties Away from Zero |
| 6 | RTO | Round to Odd |
| 7 | RHB | Hybrid Rounding |
| >7 | reserve | 保留 |

- **sat**：可选的饱和计算标志。

#### 8.4 伪代码

```c
// 向量版本
for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        switch (rm) {
            case RNE:  result = round_nearest_even(operand);  break;
            case RTZ:  result = round_to_zero(operand);       break;
            case RDN:  result = round_down(operand);          break;
            case RUP:  result = round_up(operand);            break;
            case RNA:  result = round_nearest_away(operand);  break;
            case RTO:  result = round_to_odd(operand);        break;
            case RHB:  result = round_hybrid(operand);        break;
            default:   result = operand;                      break;
        }
        V[d, dstwidth, laneid] = result;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

---

### 9. TS 与 TO1 形参寄存器分离

#### 9.1 变动原因

在 0.56 及之前版本中，栈空间 Tile 形参寄存器（TS）与第二个输出形参寄存器（TO1）共用同一编码槽位（编码 89）。当一个块指令仅有一个输出但需要使用栈空间时，该输出直接映射到 TO1，导致模型处理异常——栈空间与输出寄存器共用槽位使得二者无法同时存在，限制了单输出块指令使用栈空间的能力。

#### 9.2 变动内容

将 TS 独立为编码 **93**（原为 Reserved），与输出形参 TO1 彻底分离。

**Tile 形参寄存器汇总（13 个）**

| 寄存器 | 编码 | 类型 | 说明 |
|--------|------|------|------|
| TA ~ TH | 80 ~ 87 | 输入 | 第 1~8 个输入 Tile 寄存器形参 |
| TO | 88 | 输出 | 第 1 个输出 Tile 寄存器形参 |
| TO1 | 89 | 输出 | 第 2 个输出 Tile 寄存器形参 |
| TO2 | 90 | 输出 | 第 3 个输出 Tile 寄存器形参 |
| TO3 | 91 | 输出 | 第 4 个输出 Tile 寄存器形参 |
| TS | 93 | 栈 | 栈空间 Tile 寄存器形参（独立于输出） |

#### 9.3 影响范围

TS 独立编码后，栈空间 Tile 与输出 Tile 的寄存器槽位不再冲突。形参寄存器编码 93 新增为 TS 槽位，编码 89 恢复为单一的 TO1 槽位。块初始化时新增 STile→TS 映射，TS 可出现在输出列表的任意位置，不再受输出 Tile 数量的限制。

#### 9.4 使用示例

TS 独立后可自由放在输出列表的任意位置，不受输出 Tile 数量和顺序的限制：

```asm
# 多输出 + 栈空间 — S 可放在任意位置
VPAR xx, ->T<1KB>, S<1KB>, T<1KB>, ..., T<1KB>

# 无输出仅申请栈空间
VPAR xx, ->S<1KB>
```

---

### 10. ACCCVT 指令增强 — 随路量化、参数重构与编码简化

#### 10.1 变动原因

ACCCVT 是 CUBE 块中将 ACC 累加器结果搬移至通用 Tile 寄存器的核心指令。原有定义存在以下不足：

1. **缺少量化支持**：ACC 搬移后若需要量化（如 fp32→int8），必须额外执行量化 Pass，增加指令数和 Tile 占用。
2. **依赖描述符冗余**：DepSrc/DepDst 依赖描述符和 B.IOD 指令增加了编码复杂度，且在实际硬件调度中并非必需。
3. **参数模型不够直观**：LB0:Row、LB1:Col 的指定方式未区分有效数据区与总容量，Row 通过 LB 显式指定而非由 Tile 容量推导，编程体验不佳。

#### 10.2 变动内容

**（1）新增随路量化能力**

在 ACC 搬移流水线中增加 SrcTile 量化参数 Tile 输入，提供逐行缩放因子。处理流水线顺序为：**逐行量化 → 标量缩放 → 类型转换**，RowMax 在类型转换前的中间结果上归约。量化、缩放、类型转换、RowMax 在单条指令内融合完成。

**（2）删除 DepSrc/DepDst 及 B.IOD**

移除原有的 DepSrc0~2（源依赖描述符）、DepDst（目标依赖描述符）和 B.IOD 指令，简化编码格式。依赖管理由硬件调度器自动处理。

**（3）重构 LB 参数模型**

LB 参数从 `LB0:Row, LB1:Col` 调整为 `LB0:ValidCol, LB1:ValidRow, LB2:Col`：

| 参数 | 含义 | 说明 |
|------|------|------|
| **ValidCol** | 输出 Tile 中有效数据的列数 | 编码于 LB0 |
| **ValidRow** | 输出 Tile 中有效数据的行数 | 编码于 LB1 |
| **Col** | 输出 Tile 的总列数（含 Padding 列） | 编码于 LB2，默认等于 ValidCol |

Row（总行数）不再由 LB 显式指定，而是由输出 Tile 的 Size、Col 和数据位宽推导：

$$ Row = \frac{TileSize}{Col \times sizeof(DstType)} $$

其中 $ValidRow \le Row$，超出 ValidRow 的区域为 Padding 区域。

#### 10.3 汇编格式

```asm
ACCCVT Layout.{canon, normal}, <LB0:ValidCol, LB1:ValidRow, LB2:Col, SrcType, DstType>,
        ACC, SrcTile<.reuse>, [RegSrc],
        ->DstTile0<Size0>, DstTile1<Size1>
```

#### 10.4 编码格式对比

| 项目 | 旧编码 | 新编码 |
|------|--------|--------|
| 块头 | BSTART.CUBE ACCCVT, SrcType | BSTART.CUBE ACCCVT, SrcType |
| 布局与类型 | B.DATR Layout.{canon,normal}, DstType | B.DATR Layout.{canon,normal}, DstType |
| 依赖描述 | B.IOD DepSrc0, DepSrc1, DepSrc2, DepDst → LB0, LB1 | **已移除** |
| 维度参数 | B.DIM reg, imm, →LB0 (Row)；B.DIM reg, imm, →LB1 (Col) | B.DIM reg, imm, →LB0 (ValidCol)；B.DIM reg, imm, →LB1 (ValidRow)；B.DIM reg, imm, →LB2 (Col, 可选) |
| 量化输入 | — | B.IOT SrcTile\<.reuse\>, →DstTile0\<Size0\> |
| 输出 Tile | B.IOT SrcTile?, →DstTile0\<Size0\> | B.IOT last, →DstTile1\<Size1\>（可选） |
| 标量缩放 | B.IOR RegSrc | B.IOR RegSrc（可选） |

#### 10.5 伪代码

```c
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

---

### 11. 新增 TileOp 张量指令

#### 11.1 变动原因

结合 PTO-ISA 对标分析，当前 LinxISA 在以下 TileOp 领域存在指令空白：

1. **数据搬运与布局**：缺少 Tile 提取/插入、填充/扩展、形状重塑、转置、拼接、聚集/分散等数据操作指令。
2. **逐元素幂运算**：缺少 Tile-Tile 和 Tile-Scalar 的幂运算指令。
3. **按轴 argmax/argmin**：缺少行/列维度的 argmax/argmin 指令（返回索引而非仅返回值）。
4. **复杂操作**：缺少部分逐元素操作（partial element-wise）、归并排序、量化、随机数生成、调试打印等指令。

为保持与业界指令集的竞争力并将 LinxISA 打造为完整的 Tile 级编程模型，0.57 版本一次性补齐上述指令空白。

#### 11.2 新增指令清单

**（1）数据搬运与布局类（13 条，TMA 块类型）**

| 指令 | 功能 | 编码 (Mode.Function) |
|------|------|---------------------|
| [TPREFETCH](../isa/header/tileblock/TPREFETCH.md) | 将数据从全局内存预取到 Tile 本地缓存 | 0.3 |
| [TTRANS](../isa/header/tileblock/TTRANS.md) | 矩阵转置操作 | 0.16 |
| [TEXTRACT](../isa/header/tileblock/TEXTRACT.md) | 从源 Tile 指定偏移处提取子 Tile | 0.17 |
| [TIMG2COL](../isa/header/tileblock/TIMG2COL.md) | 图像到列变换（用于卷积工作负载） | 0.18 |
| [TINSERT](../isa/header/tileblock/TINSERT.md) | 在指定偏移处将子 Tile 插入到目标 Tile | 0.19 |
| [TFILLPAD](../isa/header/tileblock/TFILLPAD.md) | 复制 Tile 并在有效区域外使用填充值填充 | 0.20 |
| [TFILLPADEXPAND](../isa/header/tileblock/TFILLPADEXPAND.md) | 填充时允许目标大于源的填充操作 | 0.21 |
| [TRESHAPE](../isa/header/tileblock/TRESHAPE.md) | 将 Tile 重新解释为另一种形状，保留底层字节 | 0.22 |
| [TRESHAPE.MASK](../isa/header/tileblock/TRESHAPE.MASK.md) | TRESHAPE 的掩码变体，通过源/目的掩码 Tile 控制重塑过程中元素的有效性和摆放位置 | 0.23 |
| [TCONCAT](../isa/header/tileblock/TCONCAT.md) | 将两个 Tile 沿列维度水平拼接 | 0.24 |

**（2）逐元素幂运算（2 条，TEPL 块类型）**

| 指令 | 功能 | 编码 (Mode.Function) |
|------|------|---------------------|
| [TPOW](../isa/header/tileblock/TPOW.md) | 两个 Tile 的逐元素幂运算 | 0.28 |
| [TPOWS](../isa/header/tileblock/TPOWS.md) | Tile 逐元素与标量幂运算 | 1.28 |

**（3）按轴 argmax/argmin（4 条，TEPL 块类型）**

| 指令 | 功能 | 编码 (Mode.Function) |
|------|------|---------------------|
| [TROWARGMAX](../isa/header/tileblock/TROWARGMAX.md) | 获取每行最大值对应列索引 | 2.12 |
| [TROWARGMIN](../isa/header/tileblock/TROWARGMIN.md) | 获取每行最小值对应列索引 | 2.13 |
| [TCOLARGMAX](../isa/header/tileblock/TCOLARGMAX.md) | 获取每列最大值对应行索引 | 2.28 |
| [TCOLARGMIN](../isa/header/tileblock/TCOLARGMIN.md) | 获取每列最小值对应行索引 | 2.29 |

**（4）复杂操作（14 条，TEPL 块类型）**

| 指令 | 功能 | 编码 (Mode.Function) |
|------|------|---------------------|
| [TCI](../isa/header/tileblock/TCI.md) | 生成连续整数序列到目标 Tile 中 | 3.0 |
| [TTRI](../isa/header/tileblock/TTRI.md) | 生成三角（下/上）掩码 Tile | 3.1 |
| [TPARTADD](../isa/header/tileblock/TPARTADD.md) | 部分逐元素加法，对不匹配区域有实现定义的处理 | 3.3 |
| [TPARTMUL](../isa/header/tileblock/TPARTMUL.md) | 部分逐元素乘法，对不匹配区域有实现定义的处理 | 3.4 |
| [TPARTMAX](../isa/header/tileblock/TPARTMAX.md) | 部分逐元素最大值，对不匹配区域有实现定义的处理 | 3.5 |
| [TPARTMIN](../isa/header/tileblock/TPARTMIN.md) | 部分逐元素最小值，对不匹配区域有实现定义的处理 | 3.6 |
| [TPARTARGMAX](../isa/header/tileblock/TPARTARGMAX.md) | 部分逐元素最大值选择并返回对应索引（argmax） | 3.7 |
| [TPARTARGMIN](../isa/header/tileblock/TPARTARGMIN.md) | 部分逐元素最小值选择并返回对应索引（argmin） | 3.8 |
| [TRANDOM](../isa/header/tileblock/TRANDOM.md) | 使用基于计数器的密码算法生成随机数 | 3.9 |
| [TQUANT](../isa/header/tileblock/TQUANT.md) | 量化 Tile（如 FP32→FP8），生成指数/缩放/最大值输出 | 3.10 |
| [TGATHER](../isa/header/tileblock/TGATHER.md) | 使用索引 Tile 从源 Tile 中收集/选择元素 | 0.11 |
| [TGATHERB](../isa/header/tileblock/TGATHERB.md) | 使用字节偏移量收集元素 | 0.12 |
| [TSCATTER](../isa/header/tileblock/TSCATTER.md) | 使用逐元素行索引将源 Tile 的行分散到目标 Tile | 0.13 |
| [TSORT32](../isa/header/tileblock/TSORT32.md) | 对 src 每个 32 元素块与 idx 对应索引排序 | 3.14 |
| [TMRGSORT](../isa/header/tileblock/TMRGSORT.md) | 单列表多段归并排序 | 3.15 |
| [TMRGSORT4](../isa/header/tileblock/TMRGSORT4.md) | 4 个已排序列表的多列表归并排序 | 3.16 |

#### 11.3 参数模型统一

所有新增 TileOp 指令统一采用输出 Tile 导向的 LB 参数模型：

| 参数 | 含义 | 编码位置 |
|------|------|---------|
| **ValidCol** | 输出 Tile 中有效数据的列数 | LB0 |
| **ValidRow** | 输出 Tile 中有效数据的行数 | LB1 |
| **Col** | 输出 Tile 的总列数（含 Padding 列） | LB2，默认等于 ValidCol |

Row（总行数）由输出 Tile 的 Size、Col 和数据位宽推导：`Row = DstTileSize / (Col × sizeof(DataType))`。此参数模型与 ACCCVT 增强后的模型保持一致。

#### 11.4 影响范围

新增的 33 条 TileOp 指令分布于 TMA 块（13 条数据搬运/布局指令，Mode=0）和 TEPL 块（20 条计算指令，Mode=1~3），每条指令分配独立的 Mode.Function 编码。输出 Tile 导向的 ValidCol/ValidRow/Col 参数模型（LB0/LB1/LB2）与增强后的 ACCCVT 保持一致。

---

### 12. 新增持久化Tile寄存器（PT）及形参 TP

#### 12.1 变动原因

普通 Tile 寄存器受重命名机制影响，其生命周期限于单次块调用，无法跨块持久化驻留共享数据（如共享缓冲区、参数块、查找表等）。为支持跨块数据驻留，需引入一种独立于 Tile 重命名机制的持久化存储区域。

#### 12.2 变动内容

**（1）新增 PT 寄存器概念**

Persistent Tile（PT）是一种显式管理、跨块持久化的核内局部存储区域。主要属性：

- **跨块持久化**：PT 分配后可跨不同块存活，申请的块及后续块指令均可读写，直至显式释放
- **不受 Tile 重命名影响**：PT 地址空间独立管理，普通 Tile 的重命名不会覆盖 PT 区域
- **计入 Tile 容量预算**：PT 与普通 Tile 共享线程级容量池，非额外独立状态
- **显式管理**：不会自动释放，必须由软件通过指令显式释放

详见 [PT](../isa/register/common/PT.md)。

**（2）LTAR 新增 TP 形参寄存器**

在 Tile 形参寄存器列表中新增 **TP**（Tile Persistent），类型为"持久化"，存储当前线程已分配的 PT 首地址。形参总数由 13 增至 **14**：

| 寄存器 | 编码 | 类型 | 说明 |
|--------|------|------|------|
| TA ~ TH | 80 ~ 87 | 输入 | 第 1~8 个输入 Tile 寄存器形参 |
| TO | 88 | 输出 | 第 1 个输出 Tile 寄存器形参 |
| TO1 | 89 | 输出 | 第 2 个输出 Tile 寄存器形参 |
| TO2 | 90 | 输出 | 第 3 个输出 Tile 寄存器形参 |
| TO3 | 91 | 输出 | 第 4 个输出 Tile 寄存器形参 |
| **TP** | **94** | **持久化** | **持久化 Tile 寄存器形参（新增）** |
| TS | 93 | 栈 | 栈空间 Tile 寄存器形参 |

TP 的读写权限为可读写，但若 PT 未被分配则 TP 的值为未定义，访问将触发异常。

**（3）PT 的分配与释放**

PT 通过 B.IOT 指令进行分配和释放，独立于调用方传入的输入/输出 Tile 序列：

```asm
B.IOT [xx], ->PT<Size>       # 分配 Persistent Tile（有效范围 256B ~ 256KB）
B.IOT [xx], ->PT.FREE        # 释放 Persistent Tile
```

**（4）LTAR 映射机制完善**

更新 `ltar.md` 中"映射机制"一节，明确 TP 与其他形参在绑定方式上的本质区别：

- TA~TH、TO~TO3、TS 通过调用方传入的 Tile 寄存器经 B.IOT 序列绑定，硬件按操作数出现次序逐一填充
- TP 不通过调用方传入，由独立的 `B.IOT [xx], ->PT<Size>` 在 Tile 容量池中分配后填入

同时将"由块指令外部分配"修正为"由独立的 B.IOT 指令在 Tile 容量池中分配，非由调用方传入"，提升表述的精确性。

#### 12.3 影响范围

PT 作为一种新的 Tile 寄存器类别（持久化）加入 ISA 状态模型。LTAR 形参寄存器总数由 13 增至 14（新增 TP，编码 94）。B.IOT 指令新增 `PT<Size>` 分配语法和 `PT.FREE` 释放语法。PT 计入线程级 Tile 容量池，其地址空间与普通 Tile 寄存器独立管理。

---

### 13. 新增 TileInfo 硬件寄存器族

#### 13.1 变动原因

在 TileOp 指令的旧版参数模型中，LB 参数（ValidCol/ValidRow/Col）描述的是**输入 Tile** 的维度和属性。这要求软件在每条 TileOp 指令中同时维护输入和输出 Tile 的参数信息，增加了编程负担。此外，输入 Tile 的元数据（维度、数据类型、布局、容量等）在 Tile 被分配时已由硬件确定，指令中重复描述是冗余的。

为简化 TileOp 编程模型并将参数语义统一为"输出导向"，0.57 版本引入 TileInfo 硬件寄存器族，由硬件自动追踪每个 Tile 的元数据。

#### 13.2 变动内容

TileInfo 是一组硬件内部维护的 **banked 寄存器族（SSR family）**，每个 Tile 寄存器对应一个独立的 64-bit TileInfo 实例（共 64 个），用于记录该 Tile 的元数据快照。

**寄存器位域（每实例 64-bit）：**

| 位域 | 位宽 | 说明 |
|------|------|------|
| `vld` | 1 | Tile 是否已分配/有效 |
| `p` | 1 | PredicateTile 标记 |
| `Layout` | 3 | 数据存储布局（分形）类型 |
| `DataType` | 6 | 元素数据类型，编码同 BSTART |
| `size` | 4 | Tile 容量编码，编码同 B.IOT 目的寄存器容量 |
| — | 1 | 保留 |
| `validCol` | 16 | 有效数据列数 |
| `validRow` | 16 | 有效数据行数 |
| `Col` | 16 | 总列数（含 Padding） |

**生命周期：**

- **写入**：当块指令通过 B.IOT 将数据输出到一个 Tile 寄存器时，硬件自动将相关参数写入该 Tile 对应的 TileInfo。
- **读取**：当后序块指令以该 Tile 作为输入时，硬件从对应的 TileInfo 中自动获取元数据。

TileInfo **不对软件可见**（不分配 SSRID，不可通过 SSRGET/SSRSET 访问），完全由硬件自动管理。

#### 13.3 影响范围

TileInfo 引入后，TileOp 指令的 LB 参数语义统一为**"仅描述输出 Tile 参数"**。输入 Tile 的维度、数据类型、布局等信息由硬件从 TileInfo 自动获取，无需软件在指令中重复描述。此变更影响 `docs/zh/isa/header/tileblock/` 下约 68 个旧式 TileOp 指令的文档描述（需将 LB 参数从"输入Tile"更新为"输出 Tile"），新增的 0.57 TileOp 指令（TEXTRACT、TPOW 等约 20 条）已采用输出导向的参数模型，无需修改。

---

### 14. CLZ → CLS 语义调整

#### 14.1 变动原因

比特位操作指令 CLZ（Count Leading Zero bits）原语义为统计操作数指定范围内前导零的位数。为扩展符号位统计能力，将语义调整为 CLS（Count Leading Sign bits）：统计与符号位相同的连续位数。

- 对于**有符号数**，统计前导符号位位数（1 或 0）；
- 对于**无符号数**，等价于统计前导零的位数（与旧 CLZ 行为一致）。

指令助记符同步变更为 `cls`（32bit 标量）、`l.cls`（64bit 标量）、`v.cls`（64bit 向量）。

#### 14.2 语义对比

| 场景 | 旧 CLZ | 新 CLS |
|------|--------|--------|
| 正数（MSB=0） | 计数前导 0 | 计数前导 0（相同） |
| 负数（MSB=1） | 计数前导 0 | 计数前导 1 |
| 无符号数（MSB=0） | 计数前导 0 | 计数前导 0（相同） |

#### 14.3 伪代码变化

```c
// 旧 CLZ: 计数前导零
bit signbit = 0b0;  // 隐式固定比较目标

// 新 CLS: 计数与符号位相同的位
bit signbit = newoperand[M+N-1];  // 取范围的最高位作为符号位
// 循环内比较逻辑不变: if newoperand[M+i] == signbit then result++
```

#### 14.4 影响范围

指令助记符由 `clz`/`l.clz`/`v.clz` 变更为 `cls`/`l.cls`/`v.cls`。指令编码保持不变，仅语义从"计数前导零"调整为"计数前导符号位"。基础指令集、超长指令扩展、标量块和向量块的指令列表中，CLZ 条目全部替换为 CLS（含 32bit 标量 CLS、64bit 标量 L.CLS、64bit 向量 V.CLS）。

---

### 15. 浮点比较指令区分为有序/无序比较

#### 15.1 变动原因

旧版浮点比较指令 FEQS、FNES、FLTS、FGES 使用 "S" 后缀，无法清晰表达 NaN 处理语义。为明确区分 NaN 场景下的比较行为，将指令重新分类为有序比较和无序比较：

- **有序比较**（FEQ/FNE/FLT/FGE）：任一操作数为 NaN → 结果为 False（SNaN 额外触发 NV 异常）
- **无序比较**（FEQU/FNEU/FLTU/FGEU）：任一操作数为 NaN → 结果为 True（不触发异常）

后者替换旧版 "S" 后缀指令，对应 PTX `setp.equ` 等业界惯例。

#### 15.2 影响范围

浮点比较指令新增 Unordered 变体。指令助记符变更：FEQS→FEQU、FNES→FNEU、FLTS→FLTU、FGES→FGEU，覆盖标量（F.*）、64bit 标量（L.*）和 64bit 向量（V.*）三个层级。NaN 处理语义由旧版"SNaN 触发 NV 异常"明确为"有序比较 NaN→False（SNaN 额外触发 NV），无序比较 NaN→True（不触发异常）"。

---

### 16. LUT — 查找表指令

#### 16.1 变动原因

为了加速非线性运算与压缩/解压流程，灵犀指令集引入了查找表指令（LUT, Look-Up Table）机制。这类指令通过索引访问预定义表格中的数据，代替繁复的逻辑与浮点运算，从而提高性能、降低功耗，尤其适用于图像处理、神经网络推理（如替代 Sigmoid/Tanh 等激活函数）、MX-FP 反量化等场景。

#### 16.2 指令定义

LUT 指令的查找表存储于 Uniform 寄存器中（即当前 lane 可访问其他 lane 的寄存器数据），通过索引值查表获取预定义数据。新增 6 条指令：

| 指令 | 索引位宽 | 查表粒度 | 每元素结果位宽 | Dst 位宽 |
|------|---------|---------|--------------|---------|
| `v.lutb.i2` | 2-bit | byte | 8-bit | .w（每 lane 打包 4 结果） |
| `v.luth.i2` | 2-bit | halfword | 16-bit | .d（每 lane 打包 4 结果） |
| `v.lutb.i4` | 4-bit | byte | 8-bit | .h（每 lane 打包 2 结果） |
| `v.luth.i4` | 4-bit | halfword | 16-bit | .w（每 lane 打包 2 结果） |
| `v.lutb.i6` | 6-bit | byte | 8-bit | .b（每 lane 1 结果） |
| `v.luth.i6` | 6-bit | halfword | 16-bit | .h（每 lane 1 结果） |

**汇编格式：**
```asm
v.lutb.i2 SrcL.ub, SrcR.uniform, ->Dst.w
v.luth.i2 SrcL.ub, SrcR.uniform, ->Dst.d
v.lutb.i4 SrcL.ub, SrcR.uniform, ->Dst.h
v.luth.i4 SrcL.ub, SrcR.uniform, ->Dst.w
v.lutb.i6 SrcL.ub, SrcR.uniform, ->Dst.b
v.luth.i6 SrcL.ub, SrcR.uniform, ->Dst.h
```

参数说明：
- **SrcL**：表项索引寄存器，仅支持 `vt.ub` 8bit 向量格式。
- **SrcR**：查找表寄存器，必须为 Uniform 向量或标量寄存器。

#### 16.3 应用示例

micro-scaling 格式反量化（MX-FP4）：
```asm
v.lutb.i4    vt#1.ub, vu#2.uniform, ->vt.h   ; 4-bit LUT 还原基础值
v.fmul.bf16  vt#1.fh, vt#2.fh, ->vt.w        ; 应用缩放系数
```

基于 6-bit ID 查表 Sigmoid 激活函数：
```asm
v.luth.i6 vt#4.ub, vu#1.uniform, ->vt.h
```

---

### 17. DOT — 点积运算指令

#### 17.1 变动原因

灵犀指令集配有专用 CUBE Core 单元用于大规模矩阵乘法（最小粒度 16×16×16），但对于小矩阵操作（如 4×4×4），使用向量单元点积指令更为高效。点积指令在 Vector Core 执行，与 CUBE 单元的大规模矩阵乘形成互补。

#### 17.2 指令定义

新增 2 条点积指令（整型 `v.dot` + 浮点 `v.fdot`），由向量长度字段 `vlen` 控制几个 lane 执行一次点积运算：

| vlen | 合并粒度 | 说明 |
|------|---------|------|
| 00 | 4-lane 合并 | 每 4 个连续 lane 乘加后广播 |
| 01 | 2-lane 合并 | 每 2 个连续 lane 乘加后广播 |
| 10 | 1-lane | 单个 lane 内独立执行点积 |
| 11 | — | 预留 |

**汇编格式：**
```asm
v.dot SrcL.<T>, SrcR.<T>, SrcD.<T>, ->Dst.<W>
v.fdot SrcL.<T>, SrcR.<T>, SrcD.<T>, ->Dst.<W>
```

参数说明：
- **SrcL**、**SrcR**：两个源乘数向量。
- **SrcD**：累加器初始值。
- **T**：操作数类型，支持任意宽度（整型 sb/sh/sw/sd/ub/uh/uw/ud，浮点 fb/fh/fs/fd）。
- **W**：目的寄存器位宽，至少为源操作数位宽的两倍，以容纳扩展精度的累加结果。

#### 17.3 使用示例

```asm
; 4 个 int16 元素点积（vlen=00）
v.dot vt#1.sh, vt#2.sh, zero, ->vt.w

; float16 点积并累加（vlen=00）
v.fdot vt#1.fh, vt#2.fh, vt#3.fs, ->vt.w
```

---

### 18. sub-group reduce — 分组归约操作

#### 18.1 变动原因

旧版 reduce 指令仅支持 workgroup 级别的全组归约，无法在组内划分为多个子组分别归约。0.57 版本扩展归约指令，支持 sub-group（子组）范围内的独立归约操作，适用于算法优化场景（如 partial sum 的分组聚合）。

#### 18.2 指令定义

对原有 9 条 reduce 指令进行修改，统一增加 SrcR 寄存器和 imm10 立即数两个参数，二者共同表示 sub-group 归约范围。

**涉及指令（9 条）：**

| 指令 | 归约运算 | 数据类型 |
|------|---------|---------|
| `v.rdadd` | 加法 | 整型 |
| `v.rdand` | 按位与 | 整型 |
| `v.rdor` | 按位或 | 整型 |
| `v.rdxor` | 按位异或 | 整型 |
| `v.rdfadd` | 加法 | 浮点 |
| `v.rdmax` | 最大值 | 整型 |
| `v.rdmin` | 最小值 | 整型 |
| `v.rdfmax` | 最大值 | 浮点 |
| `v.rdfmin` | 最小值 | 浮点 |

以上 9 条指令均为旧版已有，0.57 版本对其统一增加 SrcR 和 imm10 参数以支持 sub-group 归约。

**汇编格式：**
```asm
v.rdadd SrcL.<T>, SrcR, imm10, ->Dst<.W>
```

参数说明：
- **SrcL**：归约源操作数。
- **SrcR**：范围寄存器（标量），与 imm10 共同指示 sub-group 归约范围。
- **imm10**：立即数范围参数，与 SrcR 共同指示 sub-group 归约范围。
- **Dst**：workgroup reduce 时可为标量或向量；sub-group reduce 时必须为向量，结果 broadcast 到子组内所有 lane。

约束：SrcR 与 imm10 共同指示的范围必须为 2 的整数次幂且不大于 Group size（64），否则行为未定义。当共同指示整个 Group 范围时按 workgroup reduce 执行。

---

### 19. 删除 B.IOD 指令

#### 19.1 变动原因

B.IOD（Block Input Output Dependency）指令为早期设计产物，用于编码 Tile 寄存器间的依赖描述符（DepSrc/DepDst）。随着 0.56→0.57 架构演进，依赖管理已由硬件调度器自动处理，B.IOD 成为冗余指令，且在 0.57 版本 ACCCVT 增强中已移除其使用。为精简指令集、降低编码复杂度，需彻底清除 B.IOD。

#### 19.2 变动内容

从指令集中彻底删除 B.IOD 指令。B.IOD 作为早期依赖描述符指令，随着硬件调度器自动管理 Tile 依赖关系而成为冗余。删除后，块头指令序列中不再包含 B.IOD 编码，ACCCVT、TLOAD、TSTORE 等指令的依赖描述符（DepSrc/DepDst）参数同步移除。

#### 19.3 影响范围

基础指令集中移除 B.IOD 条目，所有块类型（TMA/TEPL/VEC/MEM/CUBE）的块头编码表中删除 B.IOD 编码行。B.IOD 原功能由硬件调度器隐式处理。

---

## 五、总结

LinxISA 0.57 版本在指令扩充和架构优化两个维度均有重要更新：

1. **整数专用**：ABS 和 ABSDIF 提供了单指令的绝对值与绝对差值计算，消除编译器展开开销。
2. **AI 激活原语**：RELU / LRELU / FRELU / FLRELU 四组指令覆盖了整型和浮点两种数据类型的 ReLU 及带参数泄漏变体，与已有的 TileOp TPRELU/TRELU（Tile 级）和 TPRELU/TLRELU（Tile 标量级）形成互补——向量/标量指令用于寄存器级细粒度操作，TileOp 用于 Tile 级批量处理。
3. **浮点超越函数**：FLN 提供自然对数运算，完善了浮点超越函数矩阵（与已有 FEXP、FRECIP、FSQRT 并列）。
4. **浮点舍入到整数**：FRINT 填补了 float→float 舍入的指令空白，与 FCVT（格式转换）和 FCVTI（浮点转整数）构成完整的三级浮点操作体系，使编译器在映射 `llvm.floor`、`llvm.ceil`、`llvm.trunc`、`llvm.rint` 等 intrinsics 时有更简洁高效的对应。
5. **Tile 形参寄存器架构优化**：TS 与 TO1 彻底分离，栈空间形参使用独立编码 93，消除单输出块指令使用栈空间时的槽位冲突，使 TS 可放在输出列表任意位置，提升块指令的可编程性。
6. **ACCCVT 指令增强**：新增量化参数 Tile 实现随路量化，移除冗余依赖描述符，重构为 ValidCol/ValidRow/Col 参数模型，使 ACC 搬移与量化在单条指令内融合完成，减少量化 Pass 开销。
7. **TileOp 指令矩阵补齐**：新增 32 条 TileOp 指令，涵盖数据搬运/布局、幂运算、argmax/argmin、部分逐元素操作、归并排序、量化、随机数等领域，统一采用输出 Tile 导向的 ValidCol/ValidRow/Col 参数模型，与 ACCCVT 增强保持一致。
8. **持久化 Tile（PT）与 TP 形参**：引入跨块持久化的 PT 寄存器，不受 Tile 重命名影响，适用于共享缓冲区、查找表等跨块驻留场景。LTAR 新增 TP 形参，总数由 13 增至 14。PT 通过 B.IOT 独立分配/释放，与调用方传入的 Tile 序列解耦。
9. **TileInfo 硬件寄存器族**：为每个 Tile 寄存器配备独立的 TileInfo 元数据寄存器（64-bit × 64），由硬件自动维护 Tile 的维度、数据类型、布局等元数据。TileInfo 不对软件可见，使 TileOp 指令的 LB 参数语义统一为"仅描述输出 Tile 参数"，输入 Tile 参数由硬件从 TileInfo 自动获取。
10. **CLZ → CLS 语义调整**：将 Count Leading Zero bits 调整为 Count Leading Sign bits，统计与符号位相同的连续位数。指令助记符由 `clz`/`l.clz`/`v.clz` 改为 `cls`/`l.cls`/`v.cls`，伪代码中比较目标从固定的 0 改为动态取范围的最高位（符号位），扩展了符号位统计能力。
11. **浮点比较指令有序/无序区分**：将浮点比较指令明确区分为有序比较（FEQ/FNE/FLT/FGE，NaN→False）和无序比较（FEQU/FNEU/FLTU/FGEU，NaN→True），替换旧版 FEQS/FNES/FLTS/FGES 命名，对齐 PTX `setp.equ` 等业界惯例。
12. **LUT 查找表指令**：新增 6 条向量查找表指令（`v.lutb.i2` / `v.luth.i2` / `v.lutb.i4` / `v.luth.i4` / `v.lutb.i6` / `v.luth.i6`），支持 2/4/6-bit 索引查表返回 byte/halfword 数据，用于图像处理、MX-FP 反量化、激活函数加速等场景。
13. **DOT 点积指令**：新增 2 条向量点积指令（`v.dot` / `v.fdot`），由 `vlen` 字段控制合并粒度（4-lane / 2-lane / 1-lane），覆盖整型和浮点两种数据类型，用于 Vector Core 的 4×4×4 小矩阵乘法，与 CUBE 单元的大规模矩阵乘互补。
14. **sub-group reduce 指令扩展**：对原 9 条 reduce 指令统一增加 SrcR 和 imm10 参数，二者共同表示 sub-group 归约范围，在 workgroup reduce 基础上支持 sub-group 独立归约。
15. **删除 B.IOD 指令**：彻底删除早期依赖描述符指令 B.IOD，依赖管理由硬件调度器隐式处理，简化指令集编码。
