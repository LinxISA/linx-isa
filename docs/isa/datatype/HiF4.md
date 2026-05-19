# HiF4

## Description

The data format is **4-digit low-precision floating-point number representation format**.

## Binary structure

The binary structure of HiF4 includes 1 bit sign bit, 1 bit exponent and 2 bit mantissa, abbreviated as **E1M2**. The encoding rules of HiF4 are the same as FP4 (E1M2), but the microscale specifications are very different.

The schematic diagram is as follows:

![e1m2](../../figs/isa/datatype/e1m2.png){ width="800" }

## Value range

The exponential offset of HiF4 is 1, and the values that can be expressed are defined by the formula as follows.

1. For normalized floating point numbers:
$$
    HiF4 Value = (−1)^S x 2^{E−1} x (1 + \Sigma_{i=0}^1 m_i x 2^{-2+i})
$$

2. For denormalized floating point numbers:
$$
    Value = (−1)^S x 2^E x \Sigma_{i=0}^1 m_i x 2^{-2+i}
$$

Among them:

- S ∈ {0,1}.
- E ∈ [0, 1], 0 is used for special values.
- $m_i$ is the i-th bit of the mantissa, i ∈ [0, 1].

The value range of HiF4 is:

| Numeric value | S | Exponent | Mantissa | Expression range |
|--------|-----|------------|-------------|--------------------------|
| Zeros | 0/1 | 0 | 00 | $\pm$0 |
|Min Subnormal | 0/1 | 0 | 01 | $\pm$2^{-2} x 2^0 |
| Max Subnormal | 0/1 | 0 | 11 | $\pm$(2^{-1} + 2^{-2}) x 2^0 |
| Minimum specification number (Min Normal) | 0/1 | 1 | 00 | $\pm$2^0 |
| Maximum number of specifications (Max Normal) | 0/1 | 1 | 11 | $\pm$(1 + 2^{-1} + 2^{-2}) x 2^0 |
| Infinities | - | - | - | - |
| Not a number (NaN) | - | - | - | - |