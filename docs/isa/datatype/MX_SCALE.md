# MXMicroscaling

## Encoding format

![E8M0](../../figs/isa/datatype/E8M0.png){ width="600" }

## Shared scaling factor mechanism

**Scale Factor X** is applied to quantitative data in block sharing mode. The specific configuration is as follows:

### Core parameters

- **Shared Range**: `k = 32` consecutive elements share the same scaling factor
- **Application Format**:
    ✅ `MX-FP4` (4-bit)
    ✅ `MX-FP6` (6-bit)
    ✅ `MX-FP8` (8-bit)

### Memory optimization principle

```plaintext
[ 元素ZXTERMZH34QXZ示意 ]
+------------+-------------------+
| Scale_X    | 32个元素          |
| (E8M0格式) | (MX-FP4/6/8格式)  |
+------------+-------------------+
```

## Data representation formula

**Scale X = 2^(E-127)**

### Encoding mapping table

| Data range | Encoding (E) | Actual represented value | Value description |
|---------------|----------|------------|------------------------|
| **Zero** | – | – | zero value |
| **Minimum** | `00000000` | 2^-127 | Minimum normalized value |
| **Maximum** | `11111110` | 2^127 | Maximum normalized value |
| **Infinity** | – | – | infinity |
| **NaN** | `11111111` | – | Not a Number (Not a Number) |

### Key description

1. **Index Range**:
    - Valid exponent range E ∈ [0, 254] (`00000000` to `11111110`)
    - All-zero encoding (`00000000`) is reserved for the smallest normalized value
    - All-one encoding (`11111111`) reserved for NaN
2. **Accuracy Characteristics**:
    - No mantissa bit (M0), all values are integer powers of 2
3. **Calculation formula description**:
    - When `E = 0`: `Scale X = 2^(-127) ≈ 5.877e-39`
    - When `E = 254`: `Scale X = 2^(127) ≈ 1.701e+38`