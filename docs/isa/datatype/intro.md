# Overview of data format

## Overview

LinxISA provides a complete data format system covering ** high-precision floating point, low-precision floating-point, signed integer, and unsigned integer** to meet the needs of different scenarios such as scientific computing, general tensor operations, AI training, AI reasoning, data handling, and quantization/inverse quantization.

Overall, these data formats can be divided into three major categories:

1. **Floating point type**: `fp64`, `fp32`, `hf32`, `tf32`, `fp16`, `bf16`, `hif8`, `fp8(e5m2, e4m3)`, `fp6(e3m2, e2m3)`, `fp4(e1m2, e2m1)`, `hif4`
2. **signed integer type**: `s64`, `s32`, `s16`, `s8`, `s4`
3. **unsigned integer type**: `u64`, `u32`, `u16`, `u8`, `u4`

Among them:

- `s` means **signed**, which is signed integer
- `u` means **unsigned**, which is unsigned integer
- The remaining types are floating point types

Different formats make different trade-offs between bit width, numerical range, precision, hardware throughput, and storage overhead, so they are suitable for different operators and execution stages.

---

## 1. Data format classification

### 1. Floating point type

Floating point types are suitable for expressing real numbers with a large dynamic range. They usually consist of the following three parts:

- **Sign bit (Sign, S)**: indicates positive and negative
- **Exponent bit (Exponent, E)**: determines the numerical range
- **Mantissa / Fraction, M**: determines the effective precision

In LinxISA, the floating point format covers multiple precision levels from 64 bits to 4 bits:| Type | Total bit width | Bit segment form | Typical characteristics |
|------|--------|----------|----------|
| `fp64` | 64 | `1 + 11 + 52` | Double precision, highest range and accuracy |
| `fp32` | 32 | `1 + 8 + 23` | Single precision, the most versatile |
| `hf32` | 32 | `1 + 8 + 11` (aka `e8m11`) | 32-bit mixed precision, combining large dynamic range with low mantissa overhead |
| `tf32` | 32 | `1 + 8 + 10` (ie `e8m10`) | Retain a larger dynamic range and reduce the mantissa accuracy, suitable for tensor calculation |
| `fp16` | 16 | `1 + 5 + 10` | Half precision, low storage and bandwidth overhead |
| `bf16` | 16 | `1 + 8 + 7` | Keeps an exponential range close to `fp32`, with lower precision |
| `HiF8` | 8 (implementation dependent) | Non-fixed `eXmY` division | A floating point type with dynamic control of precision through point fields |
| `fp8(e5m2)` | 8 | `1 + 5 + 2` | The index range is larger and the accuracy is lower |
| `fp8(e4m3)` | 8 | `1 + 4 + 3` | The accuracy is slightly higher than `e5m2`, and the dynamic range is slightly smaller |
| `fp6(e3m2)` | 6 | `1 + 3 + 2` | Extremely low bit-width floating point, suitable for extreme compression |
| `fp6(e2m3)` | 6 | `1 + 2 + 3` | Accuracy takes precedence over `e3m2` and has a smaller range |
| `fp4(e1m2)` | 4 | `1 + 1 + 2` | Ultra-low bit width floating point, very limited representation capabilities |
| `fp4(e2m1)` | 4 | `1 + 2 + 1` | Range priority over `e1m2` |
| `hif4` | 4 | `1 + 1 + 2` | 4-bit low-precision floating-point, divided using `e1m2` |

> Note 1: `eXmY` means that the format uses `X` bit exponent and `Y` bit mantissa; plus 1 sign bit, the total bit width is obtained.
>
> Note 2: `HiF8` does not belong to the conventional floating-point format with fixed `eXmY` bit segment division, so it is not suitable to be directly integrated into the unified `S/E/M` fixed segment expression.

### 2. signed integer type

signed integer is used to represent discrete values, index offsets, quantized data, counters and control data. LinxISA is available in the following signed integer formats:

| Type | Bit width | Value range |
|------|------|----------|
| `s64` | 64 | \(-2^{63}\) to \(2^{63}-1\) |
| `s32` | 32 | \(-2^{31}\) to \(2^{31}-1\) |
| `s16` | 16 | \(-2^{15}\) to \(2^{15}-1\) |
| `s8` | 8 | \(-2^7\) to \(2^7-1\) |
| `s4` | 4 | \(-2^3\) to \(2^3-1\) |

These formats generally use two's complement representation. The smaller the bit width, the lower the storage overhead and the higher the throughput rate, but the smaller the representable range.

### 3. unsigned integer typeunsigned integer is used to represent non-negative discrete quantities, such as address offsets, masks, lengths, counts, partially quantized representations, etc.

| Type | Bit width | Value range |
|------|------|----------|
| `u64` | 64 | 0 to \(2^{64}-1\) |
| `u32` | 32 | 0 to \(2^{32}-1\) |
| `u16` | 16 | 0 to \(2^{16}-1\) |
| `u8` | 8 | 0 to \(2^8-1\) |
| `u4` | 4 | 0 to \(2^4-1\) |

The unsigned format has a larger non-negative representation range than the signed format at the same bit width, so it is often used for indexing, flag bit compression and low-bit data representation.

---

## 2. Organization of floating point format

The core difference between floating point formats is how the exponent and mantissa bits are allocated. This directly affects two abilities:

- **More exponent bits**: The dynamic range is larger, making it easier to represent very large or very small numbers.
- **More mantissa digits**: higher effective precision and more detailed values

For example:

- `bf16` and `fp16` are both 16-bit floating point, but:
    - `bf16 = 1 + 8 + 7`, wider index range
    - `fp16 = 1 + 5 + 10`, higher mantissa accuracy
- `tf32 = 1 + 8 + 10` (ie `e8m10`) can be seen as a compromise format for tensor operations:
    - Preserve a larger index range
    - Exchange fewer mantissas for higher computing efficiency
- `fp8(e5m2)` and `fp8(e4m3)` are 8-bit floating point with two different design tendencies:
    - `e5m2` focuses on dynamic range
    - `e4m3` focuses on effective accuracy
- `HiF8` is different from the regular 8-bit floating point divided by fixed `eXmY`. It is a type that dynamically controls the precision through point fields, so it should not be simply equated to a fixed `S/E/M` bit segment allocation.

For ultra-low-precision floating-point, such as 6-digit and 4-digit, the representation capability is already very limited, and it is usually not responsible for high-precision numerical expression alone, but is more suitable for:

- Weight/activation compression in neural network inference
- Intermediate approximate representation in specific operators
- Scenarios that are extremely sensitive to bandwidth, capacity, and throughput rates

---

## 3. Schematic diagram of each floating point format bit segment

The figure below shows the sign bit, exponent bit and mantissa bit of the main floating point data format of the fixed `S/E/M` bit segment division in LinxISA. Since `HiF8` adopts point domain dynamic control precision and does not belong to the fixed `eXmY` bit segment format, the figure is not included here for the time being:

![Floating-point format layout](../../figs/isa/datatype/floating_formats_overview.svg)

In order to facilitate quick understanding, here is a brief text summary:| Type | Sign bit | Exponent bit | Mantissa bit | Total |
|------|--------|--------|--------|------|
| `fp64` | 1 | 11 | 52 | 64 |
| `fp32` | 1 | 8 | 23 | 32 |
| `hf32` | 1 | 8 | 11 | 32 |
| `tf32` | 1 | 8 | 10 | 32 |
| `fp16` | 1 | 5 | 10 | 16 |
| `bf16` | 1 | 8 | 7 | 16 |
| `HiF8` | - | - | - | 8 |
| `fp8(e5m2)` | 1 | 5 | 2 | 8 |
| `fp8(e4m3)` | 1 | 4 | 3 | 8 |
| `fp6(e3m2)` | 1 | 3 | 2 | 6 |
| `fp6(e2m3)` | 1 | 2 | 3 | 6 |
| `fp4(e1m2)` | 1 | 1 | 2 | 4 |
| `fp4(e2m1)` | 1 | 2 | 1 | 4 |
| `hif4` | 1 | 1 | 2 | 4 |

> Note: For `HiF8`, only the total bit width information is retained here; its precision organization method is not given in fixed `S/E/M` segments.

---

## 4. Design trade-offs in different formats

### 1. High-precision floating point: `fp64`, `fp32`

This type of format is suitable for scenarios that require high numerical precision:

- Scientific computing
- High-precision accumulation
- Reference implementation or golden model
- Algorithms that are extremely sensitive to errors

Among them:

- `fp64` has the highest accuracy and range, but also has the highest hardware cost and bandwidth overhead.
- `fp32` is the most common general-purpose floating point format, taking into account precision, range and implementation complexity

### 2. Medium precision floating point: `hf32`, `tf32`, `fp16`, `bf16`

This type of format is commonly used for mixed-precision paths in AI training and high-performance computing:

- `fp16`: Highly storage and bandwidth efficient, suitable for high-throughput computing
- `bf16`: Large index range, less likely to overflow/underflow, suitable for training scenarios
- `tf32`: taking into account dynamic range and hardware throughput, often used in tensor core class operations
- `hf32`: It is a 32-bit hybrid design and can be regarded as the `e8m11` format, taking into account larger dynamic range and lower mantissa overhead

### 3. low-precision floating-point: `HiF8`, `fp8`, `fp6`, `fp4`, `hif4`

This type of format is mainly intended for:

- Large model reasoning
- Weight quantification
- Activate compression
- Dedicated compute paths that are extremely sensitive to throughput and storage efficiency

Their common characteristics are:

-A single element occupies very few bits
- Can significantly improve on-chip cache utilization and bandwidth efficiency
- Suitable for large-scale parallel computing
- Need to rely on more sophisticated quantization strategies, scaling factor management or hybrid accumulation mechanisms

Among them:

- `fp8` has become an important candidate format for current low-precision AI calculations
- `fp6`, `fp4`, and `hif4` further advance to ultra-low bit expression
- `hif4` is divided into `e1m2` and is a specific implementation of 4-bit super low-precision floating-point
- `HiF8` is not a simple fixed `eXmY` format, but a type that dynamically controls precision through point fields### 4. Integer format: `s*` and `u*`

Integer formats are typically used for:

- Quantized weights and activations
- Indexes and offsets
- Counters, flag bits, control fields
- Fixed point approximation calculation

Among them:

- `s8` / `u8` is common in low-precision inference
- `s4` / `u4` suitable for more aggressive compression scenarios
- `s16` / `u16` are often used for intermediate results or wider quantization representation
- `s32` / `u32`, `s64` / `u64` are commonly used for accumulation, indexing and control data

---

## 5. Understanding from an application perspective

From an application perspective, this set of data formats does not replace each other, but constitutes a set of hierarchical precision systems for different computing stages:

- **Training/Calibration/Reference Calculation**: Usually use `fp32` first, use `fp64` when necessary
- **Mixed Precision Training**: Commonly used `bf16`, `fp16`, `tf32`
- **Inference Deployment**: Commonly used `fp16`, `bf16`, `fp8`, `s8`, `u8`
- **Extreme Compression Inference**: Possible use of `fp6`, `fp4`, `hif4`, `s4`, `u4`
- **Control and Index Path**: More use of `s32`, `u32`, `s64`, `u64`

In terms of hardware implementation, the lower the format bit width, usually means:

- The same capacity of on-chip storage can accommodate more elements
- More data can be transported under the same bandwidth
- Opportunity to complete more parallel operations in the same cycle

But at the same time, it also means:

- The numerical error is larger
- The representable range may be narrower
- More complex quantization, dequantization, scaling and accumulation strategies are required to ensure final accuracy

Therefore, the choice of data format is essentially an engineering compromise between accuracy, range, throughput, bandwidth, capacity, and energy consumption.

---

## 6. Summary

The data format system in LinxISA has the following characteristics:

1. **Complete coverage**: From `fp64` to `fp4`, from `s64/u64` to `s4/u4`, the range is complete
2. **Clear hierarchy**: Supports both high-precision general computing and ultra-low-precision AI computing
3. **For mixed precision**: Provide typical mixed precision formats such as `bf16`, `tf32`, `fp8`
4. **Taking into account dedicated format extensions**: including proprietary naming formats such as `hf32`, `HiF8`, `hif4`, among which `HiF8` embodies dynamic precision control capabilities
5. **Suitable for multi-scenario deployment**: It supports not only general numerical processing, but also training, inference and quantitative calculations.

Overall, this data format system provides a foundation for LinxISA to perform precision-performance collaborative optimization under different loads.