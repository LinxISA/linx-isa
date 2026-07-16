# ISA-LLVM-QEMU L1 Mapping Coherence

- Generated (UTC): `2026-07-16 18:26:50Z`
- Spec unique mnemonics: `711`
- QEMU evidence: `L1 decoder_source_mapping`
- L2 runtime execution: `available`
- L3 semantic oracle: `available`
- LLVM evidence is observed disassembly mnemonic breadth; it does not measure C-CodeGen or form-level coverage.
- This report does not claim runtime or semantic completeness.

| Surface | Covered | Ratio |
| --- | --- | --- |
| LLVM observed disassembly mnemonic breadth | `711/711` | `100.0%` |
| QEMU L1 decoder/source mapping | `626/711` | `87.9%` |
| QEMU AVS translation inventory | `711/711` | `100.0%` |

- Non-spec translation inventory tokens: `0`

## Inconsistency Summary

- Compiler-covered but missing from QEMU L1 mapping: `85`
- QEMU L1-mapped but missing from AVS translation inventory: `0`
- AVS translation-listed but absent from QEMU L1 mapping: `85`
- Compiler-covered but missing from AVS translation coverage: `0`

### Compiler vs QEMU L1 mapping

- `V`: `84`
- `XB`: `1`

### QEMU L1 mapping vs AVS translation


### Compiler vs AVS translation


## Missing From QEMU L1 Mapping (First 200)

- `V.LBI`
- `V.LBI.BRG`
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
- `V.LHI`
- `V.LHI.BRG`
- `V.LHI.U`
- `V.LHI.U.BRG`
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
