# Data format conversion

Data format conversion instructions are used to carry out format conversion tasks between floating point and integer data.

## Command list

| Microinstructions | Assembly format | Description |
|----------|----------------------------------|--------------|
| V.FCVT | `v.fcvt.{st2dt} SrcL.{T},  ->Dst.{W}` | Convert between floating point types |
| V.FCVTI | `v.fcvti.{st2dt} SrcL.{T}, ->Dst.{W}` | Convert floating point type to integer type |
| V.ICVT | `v.icvt.{st2dt} SrcL.{T},  ->Dst.{W}` | Conversion between integers |
| V.ICVTF | `v.icvtf.{st2dt} SrcL.{T}, ->Dst.{W}` | Convert integer to floating point |

- **st** represents the source operand data type, encoded in the high 3 bits of the SrcL field.
- **dt** represents the destination operand data type, encoded in the high 3 bits of the RegDst field.

## Command encoding

![FP_Convert](../../../figs/bitfield/svg/Introduction_64bit/FormatConvertVector.svg)

## Rounding mode

The rounding mode of the FCVTI instruction defaults to RTZ (round toward zero)

The rounding modes of FCVT, ICVT and ICVTF are determined by the FRM field segment in the CSTATE register. The default rounding mode is RNE (rounding to nearest). If other rounding modes need to be used, the CSTATE register can be modified through the SSRSET instruction. For details, see [CSTATE] (../../../isa/register/ssr/CSTATE.md) (public status register).

| Command | Description | Rounding Mode |
|------|--------|---------|
| V.FCVT | Conversion between floating point numbers | Controlled by [CSTATE](../../../isa/register/ssr/CSTATE.md) (FRM), default RNE |
| V.ICVTF | Signed/unsigned integer conversion to floating point | Controlled by [CSTATE](../../../isa/register/ssr/CSTATE.md) (FRM), default RNE |
| V.ICVT | Convert between integers | Wide to narrow truncation, narrow to wide expansion |
| V.FCVTI | Convert floating point to signed/unsigned integer type | Default RNE, round to nearest even number |