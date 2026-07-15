# ISA-LLVM-QEMU Coverage Coherence

- Generated (UTC): `2026-07-15 10:37:55Z`
- Spec unique mnemonics: `711`

| Surface | Covered | Ratio |
| --- | --- | --- |
| LLVM compiled coverage | `711/711` | `100.0%` |
| QEMU mapped implementation coverage | `618/711` | `86.92%` |
| QEMU AVS translation coverage | `711/711` | `100.0%` |

## Inconsistency Summary

- Compiler-covered but missing from QEMU implementation: `93`
- QEMU-implemented but missing from AVS translation coverage: `0`
- AVS translation-covered but not mapped in QEMU implementation: `93`
- Compiler-covered but missing from AVS translation coverage: `0`

### Compiler vs QEMU implementation

- `V`: `90`
- `B`: `1`
- `C`: `1`
- `XB`: `1`

### QEMU implementation vs AVS translation


### Compiler vs AVS translation


## Missing From QEMU Implementation (First 200)

- `B.DIM`
- `C.SETRET`
- `V.LB`
- `V.LBI`
- `V.LBI.BRG`
- `V.LBU`
- `V.LBUI`
- `V.LBUI.BRG`
- `V.LD`
- `V.LD.ADD`
- `V.LD.AND`
- `V.LD.BRG`
- `V.LD.MAX`
- `V.LD.MIN`
- `V.LD.OR`
- `V.LD.XOR`
- `V.LDI`
- `V.LDI.BRG`
- `V.LDI.U`
- `V.LDI.U.BRG`
- `V.LH`
- `V.LHI`
- `V.LHI.BRG`
- `V.LHI.U`
- `V.LHI.U.BRG`
- `V.LHU`
- `V.LHUI`
- `V.LHUI.BRG`
- `V.LHUI.U`
- `V.LHUI.U.BRG`
- `V.LW.ADD`
- `V.LW.AND`
- `V.LW.MAX`
- `V.LW.MIN`
- `V.LW.OR`
- `V.LW.XOR`
- `V.LWI`
- `V.LWI.BRG`
- `V.LWI.U`
- `V.LWI.U.BRG`
- `V.LWU`
- `V.LWU.BRG`
- `V.LWUI`
- `V.LWUI.BRG`
- `V.LWUI.U`
- `V.LWUI.U.BRG`
- `V.QPOP`
- `V.QPUSH`
- `V.SB`
- `V.SBI`
- `V.SBI.BRG`
- `V.SD`
- `V.SD.ADD`
- `V.SD.AND`
- `V.SD.BRG`
- `V.SD.MAX`
- `V.SD.MIN`
- `V.SD.OR`
- `V.SD.U`
- `V.SD.U.BRG`
- `V.SD.XOR`
- `V.SDI`
- `V.SDI.BRG`
- `V.SDI.U`
- `V.SDI.U.BRG`
- `V.SH`
- `V.SH.U`
- `V.SH.U.BRG`
- `V.SHFL.BFLY`
- `V.SHFL.DOWN`
- `V.SHFL.IDX`
- `V.SHFL.UP`
- `V.SHFLI.BFLY`
- `V.SHFLI.DOWN`
- `V.SHFLI.IDX`
- `V.SHFLI.UP`
- `V.SHI`
- `V.SHI.BRG`
- `V.SHI.U`
- `V.SHI.U.BRG`
- `V.SW.ADD`
- `V.SW.AND`
- `V.SW.MAX`
- `V.SW.MIN`
- `V.SW.OR`
- `V.SW.U`
- `V.SW.U.BRG`
- `V.SW.XOR`
- `V.SWI`
- `V.SWI.BRG`
- `V.SWI.U`
- `V.SWI.U.BRG`
- `XB`

## Missing From AVS Translation Coverage (First 200)
