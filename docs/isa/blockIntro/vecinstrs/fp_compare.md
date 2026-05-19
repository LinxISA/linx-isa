# Floating point comparison class

Each opcode of the floating point comparison instruction represents a different comparison condition. The comparison conditions include: equality comparison, inequality comparison, greater than or equal comparison and less than comparison.

Floating point comparison instructions are divided into **Quiet Compare** and **Signaling Compare** from the perspective of triggering floating point exceptions:

- **Silent comparison**: If any operand is SNaN, invalid operand floating point exception is triggered.
- **Sending Comparison**: If any operand is NaN, invalid operand floating point exception is triggered.

The floating point comparison instruction compares two inputs based on the conditions defined by this instruction and outputs 0 or 1. **If any operand is NaN, the output result is 0**.

## Command list

| Microinstruction | Assembly format | Description | Whether QNaN triggers exception |
|--------------|------------------|------------------------------------------|--------------------------------|
| V.FEQ | `v.feq SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point equality silent comparison | No |
| V.FNE | `v.fne SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point inequality silent comparison | No |
| V.FLT | `v.flt SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point less than silent comparison | No |
| V.FGE | `v.fge SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point greater than or equal to silent comparison | No |
| V.FEQS | `v.feqs SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point equality signal comparison | Yes |
| V.FNES | `v.fnes SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point unequal signal comparison | Yes |
| V.FLTS | `v.flts SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point less than signal comparison | Yes |
| V.FGES | `v.fges SrcL.{T}, SrcR.{T}, ->Dst.{W}` | Floating point greater than or equal to signal comparison | Yes |

## Command encoding

![FP_Compare](../../../figs/bitfield/svg/Introduction_64bit/Two-SourceFloatingPointVector.svg)