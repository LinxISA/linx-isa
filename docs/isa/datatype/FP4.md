# FP4

## Description

The data format is **4-digit low-precision floating-point number representation format**, which follows the IEEE 754-2008 standard specification.

FP4 contains two storage structures: **E2M1** and **E1M2**.

## E2M1

### Binary structure

The binary structure of FP4-E2M1 includes 1 bit sign bit, 2 bit exponent and 1 bit mantissa, abbreviated as **E2M1**. The schematic diagram is as follows:

![e2m1](../../figs/isa/datatype/e2m1.png){ width="800" }

### Value range

The exponential offset of FP4-E2M1 is 1, and the values that can be expressed are defined by the formula as follows.

1. For normalized floating point numbers:
$$
    Value = (−1)^S x 2^{E−1} x (1 + m_0 x 2^{-1})
$$

2. For denormalized floating point numbers:
$$
    Value = (−1)^S x 2^E x m_0 x 2^{-1}
$$

Among them:

- S ∈ {0,1}.
- E ∈ [0, 3], but all zeros are used for special values.
- $m_0$ is the 0th bit of the mantissa.

The value range of FP4-E2M1 is:

| Numeric value | S | Exponent | Mantissa | Expression range |
|--------|-----|------------|-------------|--------------------------|
| Zeros | 0/1 | 00 | 0 | $\pm$0 |
| Non-standard number (Subnormal) | 0/1 | 00 | 1 | $\pm$2^0 x 2^{-1} |
| Minimum specification number (Min Normal) | 0/1 | 01 | 00 | $\pm$2^0 |
| Maximum number of specifications (Max Normal) | 0/1 | 11 | 11 | $\pm$(1 + 2^{-1}) x 2^2 |
| Infinities | - | - | - | - |
| Not a number (NaN) | - | - | - | - |

## E1M2

### Binary structure

The binary structure of FP4-E1M2 includes 1 bit sign bit, 1 bit exponent and 2 bit mantissa, abbreviated as **E1M2**. The schematic diagram is as follows:

![e1m2](../../figs/isa/datatype/e1m2.png){ width="800" }

### Value range

The exponential offset of FP4-E1M2 is 1, and the values that can be expressed are defined by the formula as follows.

1. For normalized floating point numbers:
$$
    Value = (−1)^S x 2^{E−1} x (1 + \Sigma_{i=0}^1 m_i x 2^{-2+i})
$$

2. For denormalized floating point numbers:
$$
    Value = (−1)^S x 2^E x \Sigma_{i=0}^1 m_i x 2^{-2+i}
$$

Among them:

- S ∈ {0,1}.
- E ∈ [0, 1], 0 is used for special values.
- $m_i$ is the i-th bit of the mantissa, i ∈ [0, 1].

The value range of FP4-E1M2 is:| Numeric value | S | Exponent | Mantissa | Expression range |
|--------|-----|------------|-------------|--------------------------|
| Zeros | 0/1 | 0 | 00 | $\pm$0 |
|Min Subnormal | 0/1 | 0 | 01 | $\pm$2^{-2} x 2^0 |
| Max Subnormal | 0/1 | 0 | 11 | $\pm$(2^{-1} + 2^{-2}) x 2^0 |
| Minimum specification number (Min Normal) | 0/1 | 1 | 00 | $\pm$2^0 |
| Maximum number of specifications (Max Normal) | 0/1 | 1 | 11 | $\pm$(1 + 2^{-1} + 2^{-2}) x 2^0 |
| Infinities | - | - | - | - |
| Not a number (NaN) | - | - | - | - |

## Note

Overflow or underflow occurs when a value exceeds the range.