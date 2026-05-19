# MXFP8

MX-FP8 is a new 8-bit floating point format for artificial intelligence inference scenarios, designed for efficient, low-power, high-density large model deployment. It is a further optimization and expansion of the traditional FP8 format, integrating the concepts of "Mixed Precision" and "Adaptive Quantization" to improve model performance while reducing resource consumption.

## Structure of MX-FP8

MX-FP8 adopts a dual-channel structure and supports two sub-modes:

| Mode | Bit Allocation | Applicable Scenarios |
|------|--------|--------------|
| MX-FP8_E4M3 | Exponent 4 bits, mantissa 3 bits | General scenarios, such as NLP, vision tasks |
| MX-FP8_E5M2 | Exponent 5 bits, mantissa 2 bits | High dynamic range tasks (such as video analysis, medical imaging) |

Compared with the standard [FP8] (./FP8.md), MX-FP8 adds a dynamic index offset mechanism, which can dynamically adjust the index range according to the input data to avoid overflow.