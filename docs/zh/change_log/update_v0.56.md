# 0.56版本更新

更新日期：2026年3月26日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.56](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101184990659)

---

## 一、版本概述

灵犀指令集 (LinxISA) **0.56.0** 版本在 0.55 版本的基础上，针对 **Tile 寄存器的使用、块操作指令的编码以及 Tile 容量模型**进行了重大更新。**0.56.1** 版本则进一步 **PTO 指令集**设计对齐，补充和调整了 **TileOp** 的定义，重点在于提升指令语义清晰度、数值控制能力以及在复杂编程模式下的灵活性和硬件效率。两个版本共同构成了 LinxISA 在 Tile 数据处理能力上的重要演进。

---

## 二、版本变更要点 

| 序号 | 变更事项                          | 变更原因与目标                | 引入版本 |
|------|-----------------------------------|-------------------------------------------------------------------|----------|
| 1 | **增加 Tile 寄存器数量 (32 -> 64)** | 通过减小单个 Tile 的默认/典型容量，增加可用 Tile 数量，旨在降低频繁小数据块访存的延迟，提升细粒度数据操作的并发性，支持更深的软件流水、双缓冲和复杂依赖链。                        | 0.56.0   |
| 2 | **调整 `B.IOT` / `B.IOTI` 指令**    | 适配新增的 32 个 Tile 寄存器编码，收敛 `B.IOT`/`B.IOTI` 双描述符模型为统一的 `B.IOT` 指令，提供统一的块操作接口，简化编程模型和工具链实现。**后续在 0.56.1 中该指令编码有进一步优化**。 | 0.56.0   |
| 3 | **Tile 容量模型改为动态上限**        | 支持软件在总容量限制下灵活配置各 Tile 的大小（256B ~ 256KB），实现“多小 Tile”与“少大 Tile”的权衡，满足不同计算阶段需求，避免静态上限模型导致的资源利用率低下。                        | 0.56.0   |
| 4 | **调整 `TCVT` 指令编码和语义**       | 1) 与 PTO 指令集中 `TCVT` 定义对齐。<br>2) 功能聚焦为 **Tile 逐元素的数据格式转换**，移除对数据存储布局（分形）变换的支持。<br>3) 增加 **舍入模式 (`RMode`)** 和 **饱和模式 (`Sat`)** 参数，增强数值控制能力。<br>4) 归属调整为 **`TEPL` 类型**块。 | 0.56.1   |
| 5 | **`TCOPY` 指令更名为 `TMOV`**        | 1) 与 PTO 指令集命名规范对齐。<br>2) 核心功能不变：用于在 **Tile 寄存器之间进行数据移动/复制**，并支持 **数据存储布局（分形）变换**。<br>3) 保留在 **`TMA` 类型**块。                               | 0.56.1   |
| 6 | **修订 `B.IOT` 指令编码 (提升灵活性)** | 1) 原编码强制要求两个源操作数 (`SrcTile0`, `SrcTile1`) 属于**同一索引距离类别**（同为“近”或“远”），限制了模板化汇编中 Tile 寄存器作为参数的自由组合。<br>2) **解除此限制**：将 `SrcTile0` 和 `SrcTile1` 字段各自独立扩展为 **6 bit**，可分别独立编码最多 64 个 Tile 寄存器 (`T#`, `U#`, `M#`, `N#` 各 16 个)。<br>3) 引入 **`function` 字段**区分输入模式 (`3b100`: 两输入, `3b101`: 单输入, `3b110`: 无输入)。<br>4 Tile Size 立即数字段 (`imm4`) 缩减为 4 bit (仍覆盖 32B ~ 512KB)。 | 0.56.1   |
| 7 | CUBE指令**支持dtypex2打包格式**以及**HiF4缩放**（HiF Microscaling） | 引入新低精度格式以适配更多模型数据需求，提升计算适配性。 |  0.56.2   |
| 8 | CUBE指令**支持混合精度输入运算** | 支持左右矩阵不同格式运算，增强算子灵活性与兼容能力。 |  0.56.2   |
| 9 | 格式转换指令**支持dtypex2格式数据的转换与量化/反量化** | 完善低精度数据的转换与量化链路，提升端到端处理效率。 | 0.56.2   |
| 10 | 更新PRED寄存器定义（每个lane改为6-bit） | 适配多元素打包类型（dtypex2, dtypex4）的设计。 |  0.56.2   |
| 11 | 浮点/整数运算指令**增加可选舍入模式和饱和计算** | 增强计算结果的可控性，完善指令定义。 |  0.56.2   |
| 12 | **新增BLOCKNUM和BLOCKID系统寄存器** | 用于多线程编程中系统调试和Trace中标识不同的执行模块。 |  0.56.2   |
| 13 | 新增TileOp指令 - **THistogram** | 为支持topk 等排序算法硬件加速，需通过THistogram指令实现高效直方图统计 |  0.56.3   |
| 14 | 增强向量数据格式支持 | 1) 新增bf16格式浮点运算支持 <br>2) 通过指令操作码显式声明打包格式（如 bf16x2），重构数据计算机制 |  0.56.3   |

---

## 三、更新详细说明

### 1. 增加 Tile 寄存器数量

#### 1.1 变动原因

原有 32 个 Tile 寄存器难以支撑更深的软件流水和复杂的 Tile 依赖链（如循环展开、双缓冲、多阶段中间结果驻留）。增加数量可减少过早回收和重复装载，并为更细粒度的调度和复杂块间表达奠定基础。

#### 1.2 变动内容

将 T/U/M/N 类型 Tile 寄存器数量从 32 个扩展到 **64 个**，每种队列的寄存器数量从 8 个扩展到 **16 个**。

**第一层架构状态 (Tile Register)**

| 寄存器名      | 解释                          | 寄存器名      | 解释                          |
|---------------|-------------------------------|---------------|-------------------------------|
| **T#1~T#8**   | T 结果队列前第 1~8 条指令结果 | **M#1~M#8**   | M 结果队列前第 1~8 条指令结果 |
| **T#9~T#16**  | T 结果队列前第 9~16 条指令结果| **M#9~M#16**  | M 结果队列前第 9~16 条指令结果|
| **U#1~U#8**   | U 结果队列前第 1~8 条指令结果 | **N#1~N#8**   | N 结果队列前第 1~8 条指令结果 |
| **U#9~U#16**  | U 结果队列前第 9~16 条指令结果| **N#9~N#16**  | N 结果队列前第 9~16 条指令结果|
| **ACC**       | 矩阵乘累加寄存器              | **S**         | 栈空间寄存器                  |

---

### 2. `B.IOT` 指令修改 (0.56.0 基础 + 0.56.1 优化)

#### 2.1 0.56.0 基础变动

* 统一使用 `B.IOT` 指令（原 `B.IOTI` 废弃）。
* 通过 **`imm5`** 立即数静态编码输出 Tile 的 **`Size`**。
* 引入 **`H` 位** 区分源 Tile 寄存器的索引距离类别（近：0~8 / 远：9~16）。
* 引入 **`L` 位** 标记是否为块内最后一条 `B.IOT` 指令。
* **SrcTile0/1 (各 3 bit + 共享 H 位):** 编码输入 Tile 索引 (0-7 或 8-15)。
* **DstTile (3 bit):** 编码输出 Tile 目标队列 (T, U, M, N, S)。

#### 2.2 0.56.1 优化变动

* **核心问题:** 原共享 `H` 位强制两个源 Tile 同属近距或同属远距类别，无法自由组合（如 `T#1`(近) + `N#13`(远)）。
* **解决方案:**
    * **独立编码：** 将 `SrcTile0` 和 `SrcTile1` 字段**各自扩展为 6 bit** (共 12 bit)，可独立编码值 0-63，对应64个Tile寄存器。
    * 移除 `H` 位概念，索引 1-16 直接对应寄存器 `T#1`-`T#16` 等
    * **输入模式：** 引入 **`function` 字段 (3 bit, 指令位 12-14)**：
        * `3b100`: 两输入有效 (`SrcTile0` 和 `SrcTile1` 均有效)
        * `3b101`: 仅 `SrcTile0` 有效
        * `3b110`: 无输入 (仅输出 `DstTile`)
        * *(移除 `S0V/S1V` 标志位)*
    * **Tile Size：** 将 `imm5` 缩减为 **`imm4` (4 bit)**，仍覆盖所需大小范围 (见下表)。

**`imm4` 编码 (0.56.1):**

| imm4 | Size  | imm4 | Size  | imm4 | Size  | imm4 | Size  |
|------|-------|------|-------|------|-------|------|-------|
| 0    | 0B    | 4    | 256B  | 8    | 4KB   | 12   | 64KB  |
| 1    | 32B   | 5    | 512B  | 9    | 8KB   | 13   | 128KB |
| 2    | 64B   | 6    | 1KB   | 10   | 16KB  | 14   | 256KB |
| 3    | 128B  | 7    | 2KB   | 11   | 32KB  | 15   | 512KB |

**优势：** 提升在模板化汇编、Tile 寄存器作为参数传递场景下的**灵活性和表达能力**，编译器/开发者无需预先确定参数寄存器的分配距离类别，可自由组合任意 `T#`/`U#`/`M#`/`N#` 寄存器 (1-16)。

例如：
```assembly
B.IOT T#1, U#4, ->T<1KB>      // OK (0.56.0 & 0.56.1)
B.IOT T#1, N#13, ->U<1KB>      // **0.56.1 OK** (0.56.0 受限：需同属近或远)
B.IOT T#14, U#2, ->T<1KB>      // **0.56.1 OK** (0.56.0 受限)
B.IOT M#15, N#9, ->T<1KB>      // **0.56.1 OK** (0.56.0 受限)
```

---

### 3. Tile 容量模型改为动态分配模型 (0.56.0)

#### 3.1 变动原因

静态上限模型（固定数量 * 固定最大容量）会高估实际需求并限制优化。动态模型允许编译器根据算法阶段在容量和数量间灵活权衡（如：10 个 4KB Tile vs 2 个 64KB Tile）。

#### 3.2 变动内容

* **单 Tile 容量范围：** **256B** 到 **256KB**。
* **单线程活跃 Tile 总容量上限：** **512KB**。
* **Tile 内部数据存储：** **物理连续**。

软件可在总容量约束下，为不同 Tile 在不同块中动态申请不同大小。

---

### 4. 调整 `TCVT` 指令 (0.56.1)

#### 4.1 变动内容

* **功能聚焦：** **仅执行 Tile 逐元素数据格式转换**。**移除**对数据存储布局（分形）变换的支持（此功能由 `TMOV` 承担）。
* **归属变更：** 指令类型调整为 **`TEPL`** (`BSTART.TEPL` 开启)，归类于 “Tile逐元素操作”。
* **新增参数：**
    * **舍入模式 (`RMode`)：** 控制转换时的舍入行为。
    * **饱和模式 (`Sat`)：** 控制结果是否限制在目标数据类型范围内。
    * **有效区域 (`ValidCol`, `ValidRow`)：** 指定源 Tile 中实际包含有效数据的区域。
    * **总列数 (`Col`)：** 指定源 Tile 的逻辑列数（可缺省，默认等于 `ValidCol`）。
    * **Padding 值 (`PadValue`)：** 指定目标 Tile 中 Padding 区域的值 (`Null`, `Zero`, `Max`, `Min`， 可缺省默认为 `Null`)。

**汇编格式：**
```assembly
TCVT <LB0:ValidCol, LB1:ValidRow, LB2:Col, SrcType, DstType, PadValue, RMode, Sat>, SrcTile<.reuse>, ->DstTile<Size>
```
编码为以下指令序列：
```assembly
BSTART.TEPL TCVT, SrcType
B.ATTR DstType, RMode, Sat    // RMode复用Layout字段；Sat复用Canon (C) 标志位
B.DIM reg, imm, ->LB0         // ValidCol
B.DIM reg, imm, ->LB1         // ValidRow
B.DIM reg, imm, ->LB2         // Col
B.IOT SrcTile<.reuse>, last, ->DstTile<Size>
```

**舍入模式 (`RMode`) 编码 (B.ATTR 复用 Layout 字段)：**

| 编码 | 舍入模式                 | 含义                                  |
|------|--------------------------|---------------------------------------|
| 0    | RNONE                    | 不指定 (由硬件/实现决定默认行为)       |
| 1    | RNE                      | 向最近偶数舍入 (最常见)               |
| 2    | RTZ                      | 向零舍入 (截断)                      |
| 3    | RDN                      | 向负无穷舍入                         |
| 4    | RUP                      | 向正无穷舍入                         |
| 5    | RNA                      | 向最近值舍入 (远离零)                |
| 6    | RTO                      | 向最近奇数舍入                       |
| 7    | RHB                      | 混合舍入模式                         |
| >7   | reserve                  | 保留                                 |

饱和标志 (`Sat`) 编码 (B.ATTR 第 25 bit `C` 位)：

| S位 | 含义         |
|-----|--------------|
| 0   | 无饱和 (默认) |
| 1   | 启用饱和      |

**汇编示例：**
```assembly
// fp32 -> fp16 ; RNE; 饱和
TCVT <LB0:50, LB1:32, LB2:64, fp32, fp16, RNE, Sat>, T#3, ->T<4KB>
// fp16 -> e2m1x2 ; RNA
TCVT <LB0:32, LB1:16, fp16, e2m1x2, RNA>, T#2, ->T<256B> // LB2(Col) 可缺省
```

---

### 5. `TCOPY` 指令更名为 `TMOV` (0.56.1)

#### 5.1 变动内容

* **更名：** `TCOPY` -> `TMOV`。
* **功能不变：** 核心功能仍是在 **Tile 寄存器之间移动/复制数据**，并支持 **数据存储布局（分形）变换** (e.g., `ND2NZ`, `NZ2ZN`)。*数据格式转换功能已移至 `TCVT`*。
* **归属不变：** 仍属于 **`TMA` 类型** (`BSTART.TMA` 开启)，Function 编码继承原 `TCOPY` 的 `2`。
* **参数细化：** 类似 `TCVT`，要求指定：
    * **变换方式 (`Layout`):** e.g., `NORM`, `NZ2ND`, `NZ2DN`, `NZ2ZN`, `ND2NZ` 等。
    * **有效区域 (`ValidCol`, `ValidRow`)**。
    * **总列数 (`Col`)**。
    * **数据类型 (`DataType`)**。
    * **Padding 值 (`PadValue`)**。

**汇编格式：**
```assembly
TMOV Layout, <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
```
编码为以下指令序列：
```assembly
BSTART.TMA TMOV, DataType
B.ATTR Layout, PadValue
B.DIM reg, imm, ->LB0      // ValidCol
B.DIM reg, imm, ->LB1      // ValidRow
B.DIM reg, imm, ->LB2      // Col
B.IOT SrcTile<.reuse>, last, ->DstTile<Size>
```

### 6. CUBE支持低精度打包数据格式（0.56.2）

#### 变动原因

低精度类型已经成为 AI 计算中不可回避的核心需求。若 ISA 只在底层编码层面支持 4-bit 数据，而不在软件可见层面提供清晰命名，编译器和程序员都很难统一理解“一个元素”和“一个打包字节”之间的关系。新增 x2 系列类型，正是为了把这种打包关系正式提升到软件语义层。

#### 变动内容

**支持低精度打包数据类型**

为了增强张量计算和数据搬运对低精度格式的支持，0.56 新增以下软件可见类型名：

- `e2m1x2`、`e1m2x2`、`hif4x2`
- `s4x2`、`u4x2`

其中 `x2` 表示一个字节内打包两个 4-bit 逻辑元素。因此，它不是普通 8-bit 标量，而是打包后的双元素类型。并且当输入元素的数据格式为`dtypex2`类型时，输入矩阵的行列参数按照实际元素个数传参。

DataType字段编码方式如下：

| DataType | 数据格式 | DataType | 数据格式 | DataType | 数据格式 | DataType | 数据格式 |
|----------|-----------|----------|-----------|----------|-----------|----------|-----------|
| 0 | FP64 | 8 | E5M2 | 16 | S64 | 24 | U64 |
| 1 | FP32 | 9 | E3M2 | 17 | S32 | 25 | U32 |
| 2 | TF32 | 10 | E2M3 | 18 | S16 | 26 | U16 |
| 3 | HF32 | 11 | **E2M1x2** | 19 | S8 | 27 | U8 |
| 4 | FP16 | 12 | **E1M2x2** | 20 | **S4x2** | 28 | **U4x2** |
| 5 | BF16 | 13 | E8M0 | 21 | reserve | 29 | reserve |
| 6 | HiF8 | 14 | **HiF4x2** | 22 | reserve | 30 | reserve |
| 7 | E4M3 | 15 | reserve | 23 | reserve | 31 | invalid | 

**支持HiF Microscaling**

HiF4数据格式的比例因子X是一种32比特的数据格式，由3个部分组成，共64个元素共享。其中，一个8位小数E6M2由所有64个元素共享，8个1位指数E1_8各由8个元素共享，16个1位指数E1_16各由4个元素共享。编码规则:

- E6M2 8 位，记作 Ea。
- E1_8 总共 8 位，其中每一位对应 1 位 Ebi（i ∈ {0,..., 7}）。
- E1_16 总共 16 位，其中每一位对应 1 位 Ecj（j ∈ {0,..., 15}）。
 
最终缩放因子可以计算为 `X = Ea * 2^(Ebi + Ecj)`（i = N/8；j = N/4）。更多详情请参考[HiF Microscaling](../isa/datatype/HiF_SCALE.md)。

### 7. CUBE支持混合精度运算（0.56.2）

#### 变更原因

在当前版本中，CUBE 指令仅支持左右矩阵使用相同精度的输入元素。随着业务对算力效率和精度灵活性的需求提升，我们在新版本中新增了混合精度输入支持，允许左右矩阵输入使用不同的精度配置。该改动能够兼顾计算性能与精度需求，为不同应用场景提供更灵活的选择。

#### 变更事项

混合精度支持：

- 新版本允许左右矩阵分别选择不同的输入精度类型（例如 FP16、BF16 等），并在硬件上完成相容转换与计算。
- 用户需在指令配置中明确指定左矩阵与右矩阵各自的输入精度，以保证计算流程正确。

指令汇编格式：
```assembly
TMATMUL <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, ->ACC<Size>
TMATMUL.ACC <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, ACC, ->ACC<Size>
TMATMUL.BIAS <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, ->ACC<Size>
```

汇编格式相比前面版本增加了DataTypeB参数，其他无改动。参数说明：

- **DataTypeA**：表示输入 A 矩阵中元素数据格式。
- **DataTypeB**：表示输入 B 矩阵中元素数据格式。（如果和 DataTypeA 相同则允许缺省）

其中，新增的DataTypeB参数编码与B.DATR指令上（以TMATMUL示意）：
```assembly
BSTART.CUBE TMATMUL DataTypeA
B.DATR DataTypeB     （注：如果和DataTypeA相同时可缺省该指令）
B.DIM reg, imm ->LB0  （注：M）
B.DIM reg, imm ->LB1  （注：N）
B.DIM reg, imm ->LB2  （注：K）
B.IOT SrcTile0<.reuse>, SrcTile1<.reuse>, last, ->ACC<Size>
```
兼容性注意事项：

- 默认配置仍为同一精度输入，以保障现有应用不受影响。
- 出于性能与数值稳定性的考虑，建议根据实际业务场景评估使用混合精度的收益与风险。

### 8. 完善格式转换指令（0.56.2）

#### 修改事项

新版本，标量/向量Convert指令的修改如下：

- 支持高精度（例如fp32, fp16等）向低精度dtypex2格式转换；
- 增加SrcR输入，用于两个高精度元素转换/量化为dtypex2格式；
- 为了适配新增SrcR，调整了SrcType字段的编码位置；
- 新增舍入模式rm字段和饱和计算sat标记位，提升计算稳定性与结果可控性。
- 新增mode字段，用于区分普通格式转换/量化/反量化等操作。

修改后，汇编格式如下（以v.fcvt和l.fcvt为例）：

v.fcvt.{st2dt} SrcL.<T>, SrcR.<T>, ->RegDst.<W>, rm, sat
l.fcvt.{st2dt} SrcL, SrcR, ->RegDst, rm, sat

汇编符号说明如下：

- st（srouce type）表示源数据格式;
- dt（destination type）表示转换后的目标数据格式。
- rm（rounding mode）舍入模式的标记符。
- sat（saturation）支持饱和计算的标志。

向量指令编码修改如下：

![v.cvt](../figs/isa/version/0.56/v.cvt.png){ width="800" }

![l.cvt](../figs/isa/version/0.56/l.cvt.png){ width="800" }

1）舍入模式rm字段

| 编码 | 舍入模式 | 含义 |
|------|---------|--------|
| 0 | RNONE | No Rounding（不指定舍入模式，由硬件/实现决定默认行为）可缺省 |
| 1 | RNE | Round to Nearest, ties to Even（向最近偶数舍入；最常见） |
| 2 | RTZ | Round Toward Zero（向零舍入，截断小数部分） |
| 3 | RDN | Round Down（向负无穷舍入） |
| 4 | RUP | Round Up（向正无穷舍入） |
| 5 | RNA | Round to Nearest, ties Away from Zero（远离零） |
| 6 | RTO | Round to Odd（向最近奇数舍入） |
| 7 | RHB | Hybrid Rounding（混合舍入模式） |
| >7 | reserve | 保留 |

2）饱和计算sat位

| sat | 含义 |
|-----|--------|
| 0 | 无饱和计算（默认） |
| 1 | 启用饱和计算 |

### 9. PRED 掩码寄存器修改（0.56.2）

新版本，为了适配一个lane中“多数据打包进向量寄存器”的设计（例如fp16x2, fp8x4等），pred改为每个lane 4-bit，内容如下：

- p0 （1-bit）：第一个元素是否有效掩码
- p1 （1-bit）：第二个元素是否有效掩码
- p2 （1-bit）：第三个元素是否有效掩码
- p3 （1-bit）：第四个元素是否有效掩码

### 10. 增加舍入模式和饱和功能（0.56.2）

新版本，以下指令增加可选的舍入模式和饱和功能：

- `l.add / l.sub / v.add / v.sub`：整数加减，仅支持饱和功能
- `l.fadd / l.fsub / l.fmul / l.fdiv / v.fadd / v.fsub / v.fmul / v.fdiv` ：浮点数加减乘除
- `l.fmadd / l.fmsub / l.fnmadd / l.fnmsub / v.fmadd / v.fmsub / v.fnmadd / v.fnmsub`：浮点数乘加乘减类三元浮点指令

舍入模式和饱和功能定义和编码方式同上面Convert指令介绍。示例：
```assembly
v.fadd vu#1.fh, vt#1.fh, ->vt.h, rtz, sat    // 使用向零舍入，并启用饱和限制
v.fmul vt#1.fh, vu#1.fh, ->vt.h, rtz        // 使用向零舍入，不使用饱和限制
v.fdiv vt#1.fh, vu#1.fh, ->vt.h, sat         // 缺省舍入模式（由实现决定舍入规则），并启用饱和限制
v.fsub vu#1.fs, vt#1.fs, ->vt.w            // 缺省舍入模式（由实现决定舍入规则），不使用饱和限制 
```

### 11. 增加系统寄存器（0.56.2）

新版本增加两个系统寄存器，分别为BLOCKNUM和BLOCKID。

- **blockid** 表示当前执行单元是第几个 block。
- **blocknum** 表示总共有多少个 block 在并行执行。

两者通常配合使用，用来描述 block 级并行任务划分。

| SSR ID | 简称 | 名称 | 解释 |
|--------|--------|-------|-------|
| 0x0050 | BLOCKNUM | 逻辑核总数寄存器（Block Number） | 该SSR由系统控制器在内核启动前配置，内核运行期间不期望进行修改。若在内核运行期间进行修改，无法保证一致性。 |
| 0x0051 | BLOCKID | 逻辑核ID寄存器（Block ID） | 用于在系统调试（System Debug）或跟踪（Trace）过程中唯一标识系统中的不同模块（Blocks）。该SSR由系统控制器在内核启动前进行配置，内核运行期间不建议修改。若在内核运行期间进行了修改，则无法保证一致性。 |

### 12. 增加Histogram指令

新版本，增加一条THistogram指令用于直方图统计，常用于基于字节的 radix 分桶/排序以计算 bucket offsets。定义如下：

#### 说明

THistogram 指令用于对源 tile 中每一行的元素按字节进行直方图统计，并将统计结果转换为前缀累计计数写入 dst tile。每个输出行对应一个输入有效行，输出列 表示一个字节的 256 种可能取值 0..255，第 k 列保存取值 0..k 的累计计数。

该指令常用于基于字节的分桶、radix sort 分阶段统计等场景。对于多字节元素，THistogram 可选择统计其中某一个字节；在统计低位字节时，可使用 idx tile 提供高位字节前缀过滤条件，使指令只统计满足指定前缀的元素。

功能概述：

- 对 src 的每个有效行独立统计。
- 每行遍历 src 的有效列元素。
- 从元素中提取指定的 Byte 字段。
- 根据 Byte 模式和 idx 提供的过滤值决定元素是否参与计数。
- 对 256 个字节取值的计数结果做前缀和。
- 将累计计数写入 dst[row, 0..255]。

THISTOGRAM 的汇编格式如下：
```assembly
THISTOGRAM <LB0:validCol, LB1:validRow, LB2:Col, SrcType, DstType, ByteId, PadValue>, SrcTile<.reuse>, IdxTile<.reuse>, ->DstTile<Size>
```

其中：

- `LB0`: validCol 指定源 SrcTile 的有效列数，即每个有效行中参与统计的元素个数。
- `LB1`: validRow 指定源 SrcTile 的有效行数，即独立生成累计计数的行数。
- `LB2`: Col 指定源 SrcTile 的总列数或 tile 列跨度。源 SrcTile 的总行数Row可通过源tile大小和Col计算得到。
- `SrcType` 指定源元素类型，当前版本仅支持 u16 或 u32。
- `DstType` 指定输出累计计数元素类型，用于描述 DstTile 中累计计数的存储类型，支持u8/u16/u32/u64。
- `ByteId` 指定要统计的目标字节，可取 Byte0、Byte1、Byte2、Byte3（u16输入时仅Byte0和Byte1有效）。
- `SrcTile` 为输入源 tile，.reuse 表示该 tile 可按复用语义保留供后续指令继续使用。
- `IdxTile` 为索引/过滤 tile。
    - idx 元素表示过滤用的字节值。
    - 对 uint16 + Byte0，idx[row,0] 保存该行高字节过滤值。
    - 对 uint32，idx 按行保存高位前缀过滤值：
        - idx[0, 0]：用于过滤 Byte3。
        - idx[1, 0]：用于过滤 Byte2。
        - idx[2, 0]：用于过滤 Byte1。
        - 当统计 Byte3 时不需要过滤，IdxTile 可作为占位操作数。
- `DstTile<Size>` 为输出 tile，Size 表示输出 tile 的目标大小配置。

其中ByteId 字段为新增内容，编码于B.DATR指令，用于指定从 SrcTile 元素中提取并统计的目标字节。

![b.datr](../figs/isa/version/0.56/b.datr.png){ width="800" }

### 13. 增强向量数据格式支持

为 增强算子兼容性 并扩展对 BF16/FP16 及其打包格式 的计算支持，本版本对向量指令系统实施以下关键优化：

#### 浮点计算指令支持bf类型操作数

为在 向量计算单元内原生支持BF16数据运算，浮点指令的源操作数新增 bf 类型标识符，与现有FP16格式形成明确区分，例如：
```assembly
v.fadd vt#1.bf, vu#1.bf, ->vt.h          ；两个bf16的数据相加
v.fadd vt#1.fh, vu#1.fh, ->vt.h          ；两个fp16的数据相加
```
bf / fh等标识编码于指令源寄存器的高3-bit。

![v.fadd](../figs/isa/version/0.56/v.fadd.png){ width="800" }

![bf](../figs/isa/version/0.56/bf.png){ width="800" }

涉及指令如下：

- V.FADD, V.FSUB, V.FMUL, V.FDIV, V.FMADD, V.FMSUB, V.FNMADD, V.FNMSUB
- V.FEQ, V.FNE, V.FLT, V.FGE, V.FEQS, V.FNES, V.FLTS, V.FGES
- V.FMAX, V.FMIN
- V.FABS, V.FSQRT, V.FRECIP, V.FEXP, V.FCLASS
- V.RDFADD, V.RDFMAX, V.RDFMIN
- L.FADD, L.FSUB, L.FMUL, L.FDIV, L.FMADD, L.FMSUB, L.FNMADD, L.FNMSUB
- L.FEQ, L.FNE, L.FLT, L.FGE, L.FEQS, L.FNES, L.FLTS, L.FGES
- L.FABS, L.FSQRT, L.FRECIP, L.FEXP, L.FCLASS
- L.FMAX, L.FMIN
- L.RDFADD, L.RDFMAX, L.RDFMIN

#### 向量指令增加vlen字段

为最大化提升 向量计算单元带宽利用率，新增 fp16x2 / bf16x2 / fp8x4 / u16x2等打包数据格式支持。原版本通过PRED寄存器的 PLEN字段记录打包信息（由v.fcvt 等指令设置），但存在限制：**Tile内存或全局内存(GM)直接加载的数据无法传递打包格式元数据**。因此，新版本将打包信息编码至指令操作码：

- 旧机制：打包信息存储于PRED.PLEN寄存器
- 新机制：打包类型通过指令操作码显式声明

向量指令增加2-bit  VLEN字段，指示输入寄存器中数据是否是多元素打包类型，具体如下：

| vlen编码 | 含义 |
|----------|--------|
| 0 | 每个Lane包含1个元素 |
| 1 | 每个Lane包含2个元素 |
| 2 | 每个Lane包含4个元素 |
| 3 | 保留 |

例如：
```assembly
v.fadd vt#1.bfx2, vu#1.bfx2, ->vt.w        ；两个bf16x2的数据相加
v.fsub vt#1.fhx2, vu#1.fhx2, ->vt.w        ；两个fp16x2的数据相减
v.add vm#2.shx2, vn#1.shx2, ->vt.w         ；两个s16x2的数据相加
v.fadd vt#1.fbx4, vu#1.fbx4, ->vt.w        ；两个fp8x4的数据相加
```

注意事项:

- 一条指令的两个源寄存器的元素数量必须相同，否则编译器报非法指令。
- 32bit操作数（例如fs / sw / uw等）不支持x2 和x4 参数，否则报非法指令。
- 64bit操作数（例如fd / sd / ud等）不支持x2 和x4 参数，否则报非法指令。

例如：
```assembly
v.fadd vt#1.fhx2, vt#2.fh, ->vt.w       ；编译期报非法指令
v.fadd vt#1.fdx2, vt#2.fdx2, ->vt.d       ；编译期报非法指令
```

#### 格式转换指令增强

扩展格式转换指令对打包数据类型的支持：

1. 新增 bf16x2 格式转换  
   - 例如 bf16 + bf16 -> bf16x2打包格式
   - 例如 bf16x2 <--> fp16x2 精度迁移
2. 新增 e5m2x4 格式转换  
   - 例如 fp16x2 + fp16x2 -> fp8(e5m2)x4 转换

#### 补充舍入模式和饱和计算

新版本以下指令增加舍入模式和饱和计算：`V.FABS` / `V.FSQRT` / `V.FRECIP` / `V.FEXP` / `L.FABS` / `L.FSQRT` / `L.FRECIP` / `L.FEXP`

---

## 四、总结

LinxISA 0.56.x 系列完成了从“资源扩容与模型重构”到“语义/编码规范化”，再到“低精度混合精度能力与专用算子补齐”的连续演进：

1. 资源层：64 Tile + 动态容量模型显著提高资源利用率和调度弹性。
2. 指令层：B.IOT、TCVT、TMOV 等完成语义收敛与 PTO 对齐，编码可组合性明显提升。
3. 数值层：舍入/饱和、dtypexN、HiF 微缩放、混合精度共同构成更完整的低精度计算体系。
4. 系统层：BLOCKNUM/BLOCKID 与后续算法 TileOp（THistogram）增强了工程可调试性和算法落地能力。

整体上，0.56.x 已将 LinxISA 在 AI/张量计算场景中的灵活性、可编程性、数值可控性与性能可扩展性提升到更成熟阶段，并保持与 PTO 指令生态的协同性。
