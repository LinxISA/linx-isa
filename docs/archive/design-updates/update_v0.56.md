# 0.56 version update

Update date: March 26, 2026

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.56](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101184990659)

---

## 1. Version Overview

Based on version 0.55, LinxISA (LinxISA) **0.56.0** version has been significantly updated regarding the use of **Tile registers, the encoding of block operation instructions, and the Tile capacity model**. Version **0.56.1** further aligns the **PTO instruction set** design, supplements and adjusts the definition of **TileOp**, focusing on improving instruction semantic clarity, numerical control capabilities, flexibility and hardware efficiency in complex programming modes. The two versions together constitute an important evolution of LinxISA in Tile data processing capabilities.

---

## 2. Key points of version changes| Serial number | Change matters | Reasons and goals of change | Introduction version |
|------|-----------------------------------|------------------------------------------------------------------|----------|
| 1 | **Increase the number of Tile registers (32 -> 64)** | By reducing the default/typical capacity of a single Tile and increasing the number of available Tiles, it aims to reduce the latency of frequent small data block accesses, improve the concurrency of fine-grained data operations, and support deeper software pipelines, double buffering and complex dependency chains.                        | 0.56.0 |
| 2 | **Adjust the `B.IOT` / `B.IOTI` instructions** | Adapt to the newly added 32 Tile register codes, converge the `B.IOT`/`B.IOTI` dual descriptor model into the unified `B.IOT` instruction, provide a unified block operation interface, simplify the programming model and tool chain implementation. **This instruction encoding will be further optimized in 0.56.1**. | 0.56.0 |
| 3 | **Tile capacity model changed to dynamic upper limit** | Support software to flexibly configure the size of each Tile (256B ~ 256KB) under the total capacity limit to achieve the trade-off between "more small Tiles" and "few large Tiles" to meet the needs of different computing stages and avoid low resource utilization caused by the static upper limit model.                        | 0.56.0 |
| 4 | **Adjust `TCVT` instruction encoding and semantics** | 1) Align with `TCVT` definition in PTO instruction set. <br>2) The function focuses on **Tile element-by-element data format conversion**, removing support for data storage layout (fractal) transformation. <br>3) Added **rounding mode (`RMode`)** and **saturation mode (`Sat`)** parameters to enhance numerical control capabilities. <br>4) The ownership is adjusted to the **`TEPL` type** block. | 0.56.1 |
| 5 | **`TCOPY` instruction is renamed to `TMOV`** | 1) Aligned with PTO instruction set naming convention. <br>2) The core functions remain unchanged: used to move/copy data between **Tile registers** and support **data storage layout (fractal) transformation**. <br>3) Reserved in **`TMA` type** block.                               | 0.56.1 || 6 | **Revised `B.IOT` instruction encoding (improved flexibility)** | 1) The original encoding forces the two source operands (`SrcTile0`, `SrcTile1`) to belong to the same index distance category (both "near" or "far"), which limits the free combination of Tile registers as parameters in templated assembly. <br>2) **Remove this restriction**: The `SrcTile0` and `SrcTile1` fields are each independently expanded to **6 bit**, and up to 64 Tile registers can be independently encoded (16 each for `T#`, `U#`, `M#`, `N#`). <br>3) Introduce **`function` field** to distinguish input modes (`3b100`: two inputs, `3b101`: single input, `3b110`: no input). <br>4 Tile Size immediate field (`imm4`) is reduced to 4 bit (still covering 32B ~ 512KB). | 0.56.1 |
| 7 | The CUBE command **supports dtypex2 packaging format** and **HiF4 scaling** (HiF Microscaling) | Introduces a new low-precision format to adapt to more model data requirements and improve computing adaptability. | 0.56.2 |
| 8 | CUBE instruction** supports mixed-precision input operations** | Supports left and right matrix operations in different formats, enhancing operator flexibility and compatibility. | 0.56.2 |
| 9 | Format conversion instructions** support the conversion and quantization/dequantization of dtypex2 format data** | Improve the conversion and quantification link of low-precision data to improve end-to-end processing efficiency. | 0.56.2 |
| 10 | Update PRED register definition (changed to 6-bit for each lane) | Adapt to the design of multi-element packing type (dtypex2, dtypex4). | 0.56.2 |
| 11 | Floating point/integer operation instructions **Add optional rounding mode and saturation calculation** | Enhance the controllability of calculation results and improve the instruction definition. | 0.56.2 |
| 12 | **Added BLOCKNUM and BLOCKIDsystem register** | Used for system debugging in multi-thread programming and identifying different execution modules in Trace. | 0.56.2 |
| 13 | New TileOp instruction - **THistogram** | In order to support hardware acceleration of sorting algorithms such as topk, the THistogram instruction needs to be used to achieve efficient histogram statistics | 0.56.3 |
| 14 | Enhanced vector data format support | 1) Added bf16 format floating point operation support <br> 2) Explicitly declare the packaging format (such as bf16x2) through the instruction opcode and reconstruct the data calculation mechanism | 0.56.3 |

---

## 3. Update details

### 1. Increase the number of Tile registers

#### 1.1 Reasons for changes

The original 32 Tile registers are difficult to support deeper software pipelines and complex Tile dependency chains (such as loop unrolling, double buffering, and multi-stage intermediate result retention). Increasing the number reduces premature collections and duplicate loads, and sets the stage for more fine-grained scheduling and complex inter-block expression.

#### 1.2 Changes

Expand the number of T/U/M/N type Tile registers from 32 to **64**, and the number of registers for each queue from 8 to **16**.

**First layer architectural state (Tile Register)**| Register name | Explanation | Register name | Explanation |
|------------------|----------------------------------|------------------|--------------------------------|
| **T#1~T#8** | The results of the 1st~8th instructions before the T result queue | **M#1~M#8** | The results of the 1st~8th instructions before the M result queue |
| **T#9~T#16** | T The result of the 9th~16th instruction before the queue | **M#9~M#16** | M The result of the 9th~16th instruction before the queue|
| **U#1~U#8** | The results of the 1st~8th instructions before the U result queue | **N#1~N#8** | The results of the 1st~8th instructions before the N result queue |
| **U#9~U#16** | The results of the 9th~16th instructions before the U result queue | **N#9~N#16** | The results of the 9th~16th instructions before the N result queue|
| **ACC** | Matrix multiply-accumulate register | **S** | Stack space register |

---

### 2. `B.IOT` instruction modification (0.56.0 basic + 0.56.1 optimization)

#### 2.1 0.56.0 Base changes

* Use the `B.IOT` instruction uniformly (the original `B.IOTI` is obsolete).
* Output Tile's **`Size`** via **`imm5`** immediate static encoding.
* Introduced **`H` bit** to distinguish the index distance category of the source Tile register (near: 0~8 / far: 9~16).
* Introduced **`L` bit** to mark whether it is the last `B.IOT` instruction in the block.
* **SrcTile0/1 (3 bits each + shared H bit):** Encoded input Tile index (0-7 or 8-15).
* **DstTile (3 bit):** Encoded output Tile target queue (T, U, M, N, S).

#### 2.2 0.56.1 Optimization changes* **Core problem:** The original shared `H` bit forces the two source Tiles to belong to the same near or far category and cannot be freely combined (such as `T#1` (near) + `N#13` (far)).
* **Solution:**
    * **Independent encoding:** Extend the `SrcTile0` and `SrcTile1` fields** to 6 bits** each (12 bits in total), and can independently encode values 0-63, corresponding to 64 Tile registers.
    * Remove the `H` bit concept, indexes 1-16 directly correspond to registers `T#1`-`T#16`, etc.
    * **Input mode:** Introduced **`function` field (3 bit, command bits 12-14)**:
        * `3b100`: Both inputs are valid (both `SrcTile0` and `SrcTile1` are valid)
        * `3b101`: Only valid for `SrcTile0`
        * `3b110`: No input (only output `DstTile`)
        * *(Remove `S0V/S1V` flag)*
    * **Tile Size:** Reduce `imm5` to **`imm4` (4 bit)**, still covering the required size range (see table below).

**`imm4` encoding (0.56.1):**

| imm4 | Size | imm4 | Size | imm4 | Size | imm4 | Size |
|------|-------|------|-------|------|-------|------|-------|
| 0 | 0B | 4 | 256B | 8 | 4KB | 12 | 64KB |
| 1 | 32B | 5 | 512B | 9 | 8KB | 13 | 128KB |
| 2 | 64B | 6 | 1KB | 10 | 16KB | 14 | 256KB |
| 3 | 128B | 7 | 2KB | 11 | 32KB | 15 | 512KB |

**Advantages:** Improved **flexibility and expressiveness** in scenarios where templated assembly and Tile registers are passed as parameters. Compilers/developers do not need to predetermine the allocation distance category of parameter registers and can freely combine any `T#`/`U#`/`M#`/`N#` registers (1-16).

For example:
```assembly
B.IOT T#1, U#4, ->T<1KB>      // OK (0.56.0 & 0.56.1)
B.IOT T#1, N#13, ->U<1KB>      // **0.56.1 OK** (0.56.0 受限：需同属近或远)
B.IOT T#14, U#2, ->T<1KB>      // **0.56.1 OK** (0.56.0 受限)
B.IOT M#15, N#9, ->T<1KB>      // **0.56.1 OK** (0.56.0 受限)
```

---

### 3. Tile capacity model changed to dynamic allocation model (0.56.0)

#### 3.1 Reasons for changes

A static capped model (fixed quantity * fixed maximum capacity) overestimates actual demand and limits optimization. The dynamic model allows the compiler to flexibly trade off capacity and number based on algorithm stages (e.g. 10 4KB Tiles vs 2 64KB Tiles).

#### 3.2 Changes

* **Single Tile capacity range:** **256B** to **256KB**.
* **Single-threaded active Tile total capacity limit:** **512KB**.
* **Tile internal data storage:** **Physically contiguous**.

The software can dynamically apply for different sizes in different blocks for different Tiles under the total capacity constraint.

---

### 4. Adjust `TCVT` command (0.56.1)

#### 4.1 Changes* **Feature Focus:** **Only perform Tile element-by-element data format conversion**. **Removed** support for data storage layout (fractal) transformations (this feature is assumed by `TMOV`).
* **Official changes:** The command type is adjusted to **`TEPL`** (`BSTART.TEPL` is turned on), classified under "Tile element-by-element operation".
* **New parameters:**
    * **Rounding Mode (`RMode`):** Controls rounding behavior when converting.
    * **Saturation Mode (`Sat`):** Controls whether the results are limited to the target data type range.
    * **Valid area (`ValidCol`, `ValidRow`):** Specifies the area in the source Tile that actually contains valid data.
    * **Total number of columns (`Col`):** Specifies the number of logical columns of the source Tile (optional, default equals `ValidCol`).
    * **Padding value (`PadValue`): ** Specify the value of the Padding area in the target Tile (`Null`, `Zero`, `Max`, `Min`, the default is `Null`).

**Assembly format:**
```assembly
TCVT <LB0:ValidCol, LB1:ValidRow, LB2:Col, SrcType, DstType, PadValue, RMode, Sat>, SrcTile<.reuse>, ->DstTile<Size>
```
Encoded as the following sequence of instructions:
```assembly
BSTART.TEPL TCVT, SrcType
B.ATTR DstType, RMode, Sat    // RMode复用Layout字段；Sat复用Canon (C) 标志位
B.DIM reg, imm, ->LB0         // ValidCol
B.DIM reg, imm, ->LB1         // ValidRow
B.DIM reg, imm, ->LB2         // Col
B.IOT SrcTile<.reuse>, last, ->DstTile<Size>
```

**Rounding mode (`RMode`) encoding (B.ATTR multiplexed Layout field):**

| Encoding | Rounding mode | Meaning |
|------|--------------------------|---------------------------------------|
| 0 | RNONE | Not specified (default behavior determined by hardware/implementation) |
| 1 | RNE | Round to nearest even number (most common) |
| 2 | RTZ | Round toward zero (truncation) |
| 3 | RDN | Round toward negative infinity |
| 4 | RUP | Round toward positive infinity |
| 5 | RNA | Round toward nearest value (away from zero) |
| 6 | RTO | Round to nearest odd number |
| 7 | RHB | Mixed Rounding Mode |
| >7 | reserve | reserve |

Saturation flag (`Sat`) encoding (B.ATTR bit 25 `C`):

| S bit | Meaning |
|-----|--------------|
| 0 | No saturation (default) |
| 1 | Enable saturation |

**Assembly example:**
```assembly
// fp32 -> fp16 ; RNE; 饱和
TCVT <LB0:50, LB1:32, LB2:64, fp32, fp16, RNE, Sat>, T#3, ->T<4KB>
// fp16 -> e2m1x2 ; RNA
TCVT <LB0:32, LB1:16, fp16, e2m1x2, RNA>, T#2, ->T<256B> // LB2(Col) 可缺省
```

---### 5. `TCOPY` instruction renamed to `TMOV` (0.56.1)

#### 5.1 Changes

* **Name changed:** `TCOPY` -> `TMOV`.
* **Function remains unchanged:** The core function is still to move/copy data between **Tile registers** and support **data storage layout (fractal) transformation** (e.g., `ND2NZ`, `NZ2ZN`). *Data format conversion functionality has been moved to `TCVT`*.
* **The ownership remains unchanged:** Still belongs to the **`TMA` type** (`BSTART.TMA` is turned on), and the Function code inherits the `2` of the original `TCOPY`.
* **Parameter refinement:** Similar to `TCVT`, it is required to specify:
    * **Conversion method (`Layout`):** e.g., `NORM`, `NZ2ND`, `NZ2DN`, `NZ2ZN`, `ND2NZ`, etc.
    * **Valid area (`ValidCol`, `ValidRow`)**.
    * **Total number of columns (`Col`)**.
    * **data type (`DataType`)**.
    * **Padding value (`PadValue`)**.

**Assembly format:**
```assembly
TMOV Layout, <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, SrcTile<.reuse>, ->DstTile<Size>
```
Encoded as the following sequence of instructions:
```assembly
BSTART.TMA TMOV, DataType
B.ATTR Layout, PadValue
B.DIM reg, imm, ->LB0      // ValidCol
B.DIM reg, imm, ->LB1      // ValidRow
B.DIM reg, imm, ->LB2      // Col
B.IOT SrcTile<.reuse>, last, ->DstTile<Size>
```

### 6. CUBE supports low-precision packed data format (0.56.2)

#### Reason for change

Low-precision types have become an unavoidable core requirement in AI computing. If ISA only supports 4-bit data at the underlying encoding level and does not provide clear naming at the software visible level, it will be difficult for compilers and programmers to uniformly understand the relationship between "an element" and "a packed byte". The new x2 series type is added to officially upgrade this packaging relationship to the software semantic layer.

#### Changes

**Support low-precision packaging data type**

In order to enhance tensor calculation and data handling support for low-precision formats, 0.56 adds the following software visible type names:

- `e2m1x2`, `e1m2x2`, `hif4x2`
- `s4x2`, `u4x2`

Among them, `x2` represents two 4-bit logical elements packed into one byte. Therefore, it is not a regular 8-bit scalar, but a packed two-element type. And when the data format of the input element is `dtypex2` type, the row and column parameters of the input matrix are passed according to the actual number of elements.

The DataType field is encoded as follows:| DataType | Data Format | DataType | Data Format | DataType | Data Format | DataType | Data Format |
|----------|-----------|----------|-----------|----------|-----------|----------|-----------|
| 0 | FP64 | 8 | E5M2 | 16 | S64 | 24 | U64 |
| 1 | FP32 | 9 | E3M2 | 17 | S32 | 25 | U32 |
| 2 | TF32 | 10 | E2M3 | 18 | S16 | 26 | U16 |
| 3 | HF32 | 11 | **E2M1x2** | 19 | S8 | 27 | U8 |
| 4 | FP16 | 12 | **E1M2x2** | 20 | **S4x2** | 28 | **U4x2** |
| 5 | BF16 | 13 | E8M0 | 21 | reserve | 29 | reserve |
| 6 | HiF8 | 14 | **HiF4x2** | 22 | reserve | 30 | reserve |
| 7 | E4M3 | 15 | reserve | 23 | reserve | 31 | invalid |

**Support HiF Microscaling**

The scale factor X of the HiF4 data format is a 32-bit data format consisting of 3 parts and a total of 64 elements shared. Among them, an 8-bit decimal E6M2 is shared by all 64 elements, the 8 1-bit exponents E1_8 are each shared by 8 elements, and the 16 1-bit exponents E1_16 are each shared by 4 elements. Encoding rules:

- E6M2 8-bit, denoted as Ea.
- E1_8 has a total of 8 bits, each of which corresponds to 1 bit of Ebi (i ∈ {0,..., 7}).
- E1_16 has a total of 16 bits, each of which corresponds to 1 bit Ecj (j ∈ {0,..., 15}).
 
The final scaling factor can be calculated as `X = Ea * 2^(Ebi + Ecj)` (i = N/8; j = N/4). Please refer to [HiF Microscaling](../isa/datatype/HiF_SCALE.md) for more details.

### 7. CUBE supports mixed precision operations (0.56.2)

#### Reason for change

In the current version, the CUBE instruction only supports input elements with the same precision for the left and right matrices. As business demands for computing power efficiency and accuracy flexibility increase, we have added mixed-precision input support in the new version, allowing the left and right matrix input to use different precision configurations. This change can take into account computing performance and accuracy requirements, providing more flexible options for different application scenarios.

#### Changes

Mixed precision support:

- The new version allows the left and right matrices to select different input precision types (such as FP16, BF16, etc.), and complete compatible conversion and calculation on hardware.
- The user needs to clearly specify the input precision of the left matrix and the right matrix in the command configuration to ensure the correct calculation process.

Instruction assembly format:
```assembly
TMATMUL <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, ->ACC<Size>
TMATMUL.ACC <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, ACC, ->ACC<Size>
TMATMUL.BIAS <LB0:M, LB1:N, LB2:K, DataTypeA, DataTypeB> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, ->ACC<Size>
```

Compared with the previous version, the assembly format adds the DataTypeB parameter, but there are no other changes. Parameter description:

- **DataTypeA**: Indicates the data format of the elements in the input A matrix.
- **DataTypeB**: Indicates the data format of the elements in the input B matrix. (Default is allowed if same as DataTypeA)

Among them, the newly added DataTypeB parameter encoding and B.DATR instruction (indicated by TMATMUL):
```assembly
BSTART.CUBE TMATMUL DataTypeA
B.DATR DataTypeB     （注：如果和DataTypeA相同时可缺省该指令）
B.DIM reg, imm ->LB0  （注：M）
B.DIM reg, imm ->LB1  （注：N）
B.DIM reg, imm ->LB2  （注：K）
B.IOT SrcTile0<.reuse>, SrcTile1<.reuse>, last, ->ACC<Size>
```
Compatibility Notes:

- The default configuration is still the same precision input to ensure that existing applications are not affected.
- For performance and numerical stability considerations, it is recommended to evaluate the benefits and risks of using mixed precision based on actual business scenarios.

### 8. Improve the format conversion command (0.56.2)

#### Modification matters

In the new version, the modifications to the scalar/vectorConvert instruction are as follows:- Supports conversion from high-precision (such as fp32, fp16, etc.) to low-precision dtypex2 format;
- Added SrcR input for converting/quantizing two high-precision elements into dtypex2 format;
- In order to adapt to the new SrcR, the encoding position of the SrcType field has been adjusted;
- Added rounding mode rm field and saturated calculation sat flag bit to improve calculation stability and result controllability.
- Added mode field to distinguish operations such as normal format conversion/quantization/inverse quantization.

After modification, the assembly format is as follows (taking v.fcvt and l.fcvt as examples):

v.fcvt.{st2dt} SrcL.<T>, SrcR.<T>, ->RegDst.<W>, rm, sat
l.fcvt.{st2dt} SrcL, SrcR, ->RegDst, rm, sat

The assembly symbols are explained as follows:

- st (srouce type) indicates the source data format;
- dt (destination type) represents the converted target data format.
- rm (rounding mode) rounding mode marker.
- sat (saturation) Flag to support saturation calculations.

The vector instruction encoding is modified as follows:

![v.cvt](../figs/isa/version/0.56/v.cvt.png){ width="800" }

![l.cvt](../figs/isa/version/0.56/l.cvt.png){ width="800" }

1) Rounding mode rm field

| Encoding | Rounding mode | Meaning |
|------|---------|--------|
| 0 | RNONE | No Rounding (no rounding mode specified, default behavior determined by hardware/implementation) can be defaulted |
| 1 | RNE | Round to Nearest, ties to Even (round to nearest even number; most common) |
| 2 | RTZ | Round Toward Zero (round towards zero, truncate the decimal part) |
| 3 | RDN | Round Down (rounding towards negative infinity) |
| 4 | RUP | Round Up (rounding towards positive infinity) |
| 5 | RNA | Round to Nearest, ties Away from Zero (away from zero) |
| 6 | RTO | Round to Odd (round to the nearest odd number) |
| 7 | RHB | Hybrid Rounding (Hybrid Rounding Mode) |
| >7 | reserve | reserve |

2) Saturation calculation sat bit

| sat | meaning |
|-----|--------|
| 0 | No saturation calculation (default) |
| 1 | Enable saturation calculation |

### 9. PRED mask register modification (0.56.2)

In the new version, in order to adapt to the design of "multiple data packed into vector registers" in one lane (such as fp16x2, fp8x4, etc.), pred is changed to 4-bit per lane, as follows:

- p0 (1-bit): whether the first element is a valid mask
- p1 (1-bit): whether the second element is a valid mask
- p2 (1-bit): whether the third element is a valid mask
- p3 (1-bit): Whether the fourth element is a valid mask

### 10. Add rounding mode and saturation function (0.56.2)

In the new version, the following instructions add optional rounding mode and saturation function:

- `l.add / l.sub / v.add / v.sub`: Integer addition and subtraction, only supports saturation function
- `l.fadd / l.fsub / l.fmul / l.fdiv / v.fadd / v.fsub / v.fmul / v.fdiv`: Floating point addition, subtraction, multiplication and division
- `l.fmadd / l.fmsub / l.fnmadd / l.fnmsub / v.fmadd / v.fmsub / v.fnmadd / v.fnmsub`: Floating point multiplication, addition, multiplication and subtraction ternary floating point instructions

The rounding mode and saturation function definition and encoding methods are the same as those introduced by the Convert command above. Example:
```assembly
v.fadd vu#1.fh, vt#1.fh, ->vt.h, rtz, sat    // 使用向零舍入，并启用饱和限制
v.fmul vt#1.fh, vu#1.fh, ->vt.h, rtz        // 使用向零舍入，不使用饱和限制
v.fdiv vt#1.fh, vu#1.fh, ->vt.h, sat         // 缺省舍入模式（由实现决定舍入规则），并启用饱和限制
v.fsub vu#1.fs, vt#1.fs, ->vt.w            // 缺省舍入模式（由实现决定舍入规则），不使用饱和限制 
```

### 11. Add system register (0.56.2)

The new version adds two system register, namely BLOCKNUM and BLOCKID.- **blockid** indicates which block the current execution unit is.
- **blocknum** indicates how many blocks are executing in parallel.

The two are often used together to describe block-level parallel task division.

| SSR ID | Abbreviation | Name | Explanation |
|--------|--------|-------|-------|
| 0x0050 | BLOCKNUM | Logical core total register (Block Number) | This SSR is configured by the system controller before the kernel starts and is not expected to be modified while the kernel is running. If modifications are made while the kernel is running, consistency cannot be guaranteed. |
| 0x0051 | BLOCKID | Logic core ID register (Block ID) | Used to uniquely identify different modules (Blocks) in the system during system debugging (System Debug) or tracing (Trace). This SSR is configured by the system controller before the kernel starts, and it is not recommended to modify it while the kernel is running. If modifications are made while the kernel is running, consistency is not guaranteed. |

### 12. Add Histogram command

The new version adds a THistogram instruction for histogram statistics, which is often used for byte-based radix bucketing/sorting to calculate bucket offsets. The definition is as follows:

#### Description

The THistogram instruction is used to perform histogram statistics by bytes on the elements of each row in the source tile, and convert the statistical results into prefix cumulative counts and write them into the dst tile. Each output row corresponds to an input valid row, the output column represents 256 possible values ​​of a byte, 0..255, and the kth column holds the cumulative count of values ​​0..k.

This command is commonly used in scenarios such as byte-based bucketing and radix sort staged statistics. For multi-byte elements, THistogram can choose to count one of the bytes; when counting low-order bytes, you can use idx tile to provide high-order byte prefix filtering conditions, so that the instruction only counts elements that meet the specified prefix.

Function overview:

- Count each valid line of src independently.
- Iterate over the valid column elements of src for each row.
- Extracts the specified Byte field from the element.
- Determine whether the element participates in counting based on the Byte mode and the filter value provided by idx.
- Perform a prefix sum on the counting results of 256 byte values.
- Write cumulative count to dst[row, 0..255].

The assembly format of THISTOGRAM is as follows:
```assembly
THISTOGRAM <LB0:validCol, LB1:validRow, LB2:Col, SrcType, DstType, ByteId, PadValue>, SrcTile<.reuse>, IdxTile<.reuse>, ->DstTile<Size>
```

Among them:- `LB0`: validCol specifies the number of valid columns of the source SrcTile, that is, the number of elements participating in statistics in each valid row.
- `LB1`: validRow specifies the number of valid rows in the source SrcTile, that is, the number of rows that independently generate a cumulative count.
- `LB2`: Col specifies the total number of columns or tile column span of the source SrcTile. The total row count of the source SrcTile Row can be calculated from the source tile size and Col.
- `SrcType` specifies the source element type, the current version only supports u16 or u32.
- `DstType` specifies the output cumulative count element type, which is used to describe the storage type of the cumulative count in DstTile, supporting u8/u16/u32/u64.
- `ByteId` specifies the target byte to be counted, which can be Byte0, Byte1, Byte2, Byte3 (only Byte0 and Byte1 are valid when u16 is input).
- `SrcTile` is the input source tile, and .reuse means that the tile can be retained for subsequent use by subsequent instructions according to reuse semantics.
- `IdxTile` is the index/filter tile.
    - The idx element represents the byte value used for filtering.
    - For uint16 + Byte0, idx[row,0] saves the high byte filter value of the row.
    - For uint32, idx stores high-order prefix filtered values row by row:
        - idx[0, 0]: used to filter Byte3.
        - idx[1, 0]: used to filter Byte2.
        - idx[2, 0]: used to filter Byte1.
        - No filtering is required when counting Byte3, IdxTile can be used as a placeholder operand.
- `DstTile<Size>` is the output tile, and Size represents the target size configuration of the output tile.

The ByteId field is a new content, encoded in the B.DATR instruction, used to specify the target bytes extracted and counted from the SrcTile element.

![b.datr](../figs/isa/version/0.56/b.datr.png){ width="800" }

### 13. Enhanced vector data format support

In order to enhance operator compatibility and expand calculation support for BF16/FP16 and its packaging format, this version implements the following key optimizations for the vector instruction system:

#### Floating point calculation instructions support bf type operands

In order to natively support BF16 data operations in the vector computing unit, the source operand of the floating point instruction has a new bf type identifier, which is clearly distinguished from the existing FP16 format, for example:
```assembly
v.fadd vt#1.bf, vu#1.bf, ->vt.h          ；两个bf16的数据相加
v.fadd vt#1.fh, vu#1.fh, ->vt.h          ；两个fp16的数据相加
```
Identifiers such as bf/fh are encoded in the high 3-bits of the instruction source register.

![v.fadd](../figs/isa/version/0.56/v.fadd.png){ width="800" }

![bf](../figs/isa/version/0.56/bf.png){ width="800" }

The instructions involved are as follows:- V.FADD, V.FSUB, V.FMUL, V.FDIV, V.FMADD, V.FMSUB, V.FNMADD, V.FNMSUB
- V.FEQ, V.FNE, V.FLT, V.FGE, V.FEQS, V.FNES, V.FLTS, V.FGES
- V.FMAX, V.FMIN
- V.FABS, V.FSQRT, V.FRECIP, V.FEXP, V.FCLASS
- V.RDFADD, V.RDFMAX, V.RDFMIN
- L.FADD, L.FSUB, L.FMUL, L.FDIV, L.FMADD, L.FMSUB, L.FNMADD, L.FNMSUB
- L.FEQ, L.FNE, L.FLT, L.FGE, L.FEQS, L.FNES, L.FLTS, L.FGES
- L.FABS, L.FSQRT, L.FRECIP, L.FEXP, L.FCLASS
- L.FMAX, L.FMIN
- L.RDFADD, L.RDFMAX, L.RDFMIN

#### vector instruction adds vlen field

In order to maximize the bandwidth utilization of the vector computing unit, new support for packaged data formats such as fp16x2 / bf16x2 / fp8x4 / u16x2 has been added. The original version records packaging information through the PLEN field of the PRED register (set by instructions such as v.fcvt), but there are limitations: **Data loaded directly from Tile memory or global memory (GM) cannot pass packaging format metadata**. Therefore, the new version encodes packing information into the instruction opcode:

- Old mechanism: Packing information is stored in the PRED.PLEN register
- New mechanism: packed types are explicitly declared via instruction opcodes

The vector instruction adds a 2-bit VLEN field to indicate whether the data in the input register is a multi-element packed type, as follows:

| vlen encoding | meaning |
|----------|--------|
| 0 | Each Lane contains 1 element |
| 1 | Each Lane contains 2 elements |
| 2 | Each Lane contains 4 elements |
| 3 | Reserved |

For example:
```assembly
v.fadd vt#1.bfx2, vu#1.bfx2, ->vt.w        ；两个bf16x2的数据相加
v.fsub vt#1.fhx2, vu#1.fhx2, ->vt.w        ；两个fp16x2的数据相减
v.add vm#2.shx2, vn#1.shx2, ->vt.w         ；两个s16x2的数据相加
v.fadd vt#1.fbx4, vu#1.fbx4, ->vt.w        ；两个fp8x4的数据相加
```

Things to note:

- The number of elements in the two source registers of an instruction must be the same, otherwise the compiler reports an illegal instruction.
- 32bit operands (such as fs/sw/uw, etc.) do not support x2 and x4 parameters, otherwise an illegal instruction will be reported.
- 64bit operands (such as fd/sd/ud, etc.) do not support x2 and x4 parameters, otherwise an illegal instruction will be reported.

For example:
```assembly
v.fadd vt#1.fhx2, vt#2.fh, ->vt.w       ；编译期报非法指令
v.fadd vt#1.fdx2, vt#2.fdx2, ->vt.d       ；编译期报非法指令
```

#### Format conversion command enhancement

Extended format conversion instructions support for packaging data type:

1. Added bf16x2 format conversion
   - For example bf16 + bf16 -> bf16x2 packaging format
   - For example, bf16x2 <--> fp16x2 precision migration
2. Added e5m2x4 format conversion
   - For example, fp16x2 + fp16x2 -> fp8(e5m2)x4 conversion

#### Supplementary rounding mode and saturation calculation

The following instructions in the new version add rounding mode and saturation calculation: `V.FABS` / `V.FSQRT` / `V.FRECIP` / `V.FEXP` / `L.FABS` / `L.FSQRT` / `L.FRECIP` / `L.FEXP`

---

## 4. Summary

The LinxISA 0.56.x series has completed the continuous evolution from "resource expansion and model reconstruction" to "semantics/encoding standardization" to "low-precision mixed-precision capabilities and dedicated operator completion":1. Resource layer: 64 Tile + dynamic capacity model significantly improves resource utilization and scheduling flexibility.
2. Instruction layer: B.IOT, TCVT, TMOV, etc. have completed semantic convergence and PTO alignment, and the coding composability has been significantly improved.
3. Numerical layer: rounding/saturation, dtypexN, HiF micro-scaling, and mixed precision together form a more complete low-precision calculation system.
4. System layer: BLOCKNUM/BLOCKID and subsequent algorithm TileOp (THistogram) enhance project debuggability and algorithm implementation capabilities.

Overall, 0.56.x has improved the flexibility, programmability, numerical controllability and performance scalability of LinxISA in AI/tensor computing scenarios to a more mature stage, while maintaining synergy with the PTO instruction ecosystem.