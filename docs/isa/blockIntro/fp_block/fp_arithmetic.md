# Floating point operations

Floating-point arithmetic instructions include basic floating-point addition, subtraction, multiplication, and division operations as well as more complex floating-point operations such as square root, reciprocal, and absolute value.

## Command list

The list of basic floating point operation instructions is as follows:

| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| FADD | fadd.{T} SrcL, SrcR, ->{t,u,Rd} | Floating point addition |
| FSUB | fsub.{T} SrcL, SrcR, ->{t,u,Rd} | Floating point subtraction |
| FMUL | fmul.{T} SrcL, SrcR, ->{t,u,Rd} | Floating point multiplication |
| FDIV | fdiv.{T} SrcL, SrcR, ->{t,u,Rd} | Floating point division |
| FMADD | fmadd.{T} SrcL, SrcR, srcA, ->{t,u,Rd} | Floating point multiply and add |
| FMSUB | fmsub.{T} SrcL, SrcR, srcA, ->{t,u,Rd} | Floating point multiplication and subtraction |
| FNMADD | fnmadd.{T} SrcL, SrcR, srcA, ->{t,u,Rd} | Floating point multiplication and addition and negation |
| FNMSUB | fnmsub.{T} SrcL, SrcR, srcA, ->{t,u,Rd} | Floating point multiplication and subtraction |

![Arithmetic](../../../figs/bitfield/svg/Introduction_32bit/FloatingPointArithmetic.svg)

The list of floating point special operation instructions is as follows:

| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| FABS | fabs.{T} SrcL, ->{t,u,Rd} | Floating point absolute value |
| FSQRT | fsqrt.{T} SrcL, ->{t,u,Rd} | Floating point square root |
| FRECIP | frecip.{T} SrcL, ->{t,u,Rd} | Floating point reciprocal |
| FCLASS | fclass.{T} SrcL, ->{t,u,Rd} | Determine the type of floating point data |

![Arithmetic](../../../figs/bitfield/svg/Introduction_32bit/FloatingPointArithmetic_1.svg)

## Rounding mode

When the calculation result cannot be expressed accurately and needs to be rounded, the rounding mode of the calculation result is determined by the FRM field segment of the [CSTATE] (../../register/ssr/CSTATE.md) register. If the FRM field is invalid, RNE (round to nearest) mode is used by default to round the result.