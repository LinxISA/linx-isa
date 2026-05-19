# Floating point operation instructions

Floating-point operations instructions include basic floating-point addition, subtraction, multiplication and division operations as well as special floating-point operations, such as square root, reciprocal, absolute value, sine and cosine, etc.

## Command list

The list of basic floating point operation instructions is as follows:

| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| V.FADD | `v.fadd SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point addition |
| V.FSUB | `v.fsub SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point subtraction |
| V.FMUL | `v.fmul SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point multiplication |
| V.FDIV | `v.fdiv SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point division |
| V.FMADD | `v.fmadd SrcL.{T}, SrcR.{T}, srcA.{T}, ->Dst.{W}` | Floating point multiply and add |
| V.FMSUB | `v.fmsub SrcL.{T}, SrcR.{T}, srcA.{T}, ->Dst.{W}` | Floating point multiplication and subtraction |
| V.FNMADD | `v.fnmadd SrcL.{T}, SrcR.{T}, srcA.{T}, ->Dst.{W}` | Floating point multiply and add negative |
| V.FNMSUB | `v.fnmsub SrcL.{T}, SrcR.{T}, srcA.{T}, ->Dst.{W}` | Floating point multiplication, subtraction and negation |

![Arithmetic](../../../figs/bitfield/svg/Introduction_64bit/Three-SourceFloatingPoint.svg)

The list of floating point special operation instructions is as follows:

| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| V.FABS | `v.fabs SrcL.{T}, ->Dst.{W}` | Floating point absolute value |
| V.FSQRT | `v.fsqrt SrcL.{T}, ->Dst.{W}` | Floating point square root |
| V.FEXP | `v.fexp SrcL.{T}, ->Dst.{W}` | Floating point exponent with base e |
| V.FRECIP | `v.frecip SrcL.{T}, ->Dst.{W}` | Floating point reciprocal |
| V.FCLASS | `v.fclass SrcL.{T}, ->Dst.H` | Determine the type of floating point data |

![Arithmetic](../../../figs/bitfield/svg/Introduction_64bit/FloatingPointArithmeticVector.svg)

## Rounding mode

When the calculation result cannot be expressed accurately and needs to be rounded, the rounding mode of the calculation result is determined by the FRM field segment of the [CSTATE] (../../register/ssr/CSTATE.md) register. If the FRM field is invalid, RNE (round to nearest) mode is used by default to round the result.