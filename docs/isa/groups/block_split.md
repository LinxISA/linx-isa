# Block Split

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Block Split &nbsp;|&nbsp;
**Forms:** 45 &nbsp;|&nbsp;
**Unique mnemonics:** 31

</div>

Block structural instructions (BSTART, BSTOP, FENTRY, etc.).

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BSTART](../instructions/bstart.md) | `BSTART {DIRECT, CALL}, <label>` | 32 | — | Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind. |
| [BSTART.ACCCVT](../instructions/bstart_acccvt.md) | `BSTART.ACCCVT DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.CUBE](../instructions/bstart_cube.md) | `BSTART.CUBE Function, DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.FIXP](../instructions/bstart_fixp.md) | `BSTART.FIXP TileOp, DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.FP](../instructions/bstart_fp.md) | `BSTART.FP RET` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MPAR](../instructions/bstart_mpar.md) | `BSTART.MPAR <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSEQ](../instructions/bstart_mseq.md) | `BSTART.MSEQ <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.PAR](../instructions/bstart_par.md) | `BSTART.PAR TileOpcode, DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.STD](../instructions/bstart_std.md) | `BSTART.STD COND, <label>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.SYS](../instructions/bstart_sys.md) | `BSTART.SYS FALL<, fixup_label>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TEPL](../instructions/bstart_tepl.md) | `BSTART.TEPL TileOpcode, DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TLOAD](../instructions/bstart_tload.md) | `BSTART.TLOAD DataType` | 32 | — | Loads a 64-bit value from memory. |
| [BSTART.TMA](../instructions/bstart_tma.md) | `BSTART.TMA Function, DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMATMUL](../instructions/bstart_tmatmul.md) | `BSTART.TMATMUL DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMATMUL.ACC](../instructions/bstart_tmatmul_acc.md) | `BSTART.TMATMUL.ACC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMOV](../instructions/bstart_tmov.md) | `BSTART.TMOV DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TSTORE](../instructions/bstart_tstore.md) | `BSTART.TSTORE DataType` | 32 | — | Stores a register value to memory. |
| [BSTART.VPAR](../instructions/bstart_vpar.md) | `BSTART.VPAR <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.VSEQ](../instructions/bstart_vseq.md) | `BSTART.VSEQ <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTOP](../instructions/bstop.md) | `BSTOP` | 32 | — | Block termination marker. Ends the current basic block. |
| [C.BSTART](../instructions/c_bstart.md) | `C.BSTART COND,  label` | 16 | — | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTOP](../instructions/c_bstop.md) | `C.BSTOP` | 16 | — | [16-bit C.] Marks the end of the current block. |
| [ERCOV](../instructions/ercov.md) | `ERCOV [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]` | 32 | — | Instruction from the Block Split group. |
| [ESAVE](../instructions/esave.md) | `ESAVE [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]` | 32 | — | Instruction from the Block Split group. |
| [FENTRY](../instructions/fentry.md) | `FENTRY [RegSrc0 ~ RegSrcn], sp!, uimm` | 32 | — | Instruction from the Block Split group. |
| [FEXIT](../instructions/fexit.md) | `FEXIT [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Instruction from the Block Split group. |
| [FRET.RA](../instructions/fret_ra.md) | `FRET.RA [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Instruction from the Block Split group. |
| [FRET.STK](../instructions/fret_stk.md) | `FRET.STK [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Instruction from the Block Split group. |
| [MCOPY](../instructions/mcopy.md) | `MCOPY [RegSrc0, RegSrc1, RegSrc2]` | 32 | — | Instruction from the Block Split group. |
| [MSET](../instructions/mset.md) | `MSET [RegSrc0, RegSrc1, RegSrc2]` | 32 | — | Instruction from the Block Split group. |
| [XB](../instructions/xb.md) | `XB ACR-ID, C-ID` | 32 | — | Instruction from the Block Split group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
