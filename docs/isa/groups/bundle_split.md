# Bundle Split

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Bundle Split &nbsp;|&nbsp;
**Forms:** 71 &nbsp;|&nbsp;
**Unique mnemonics:** 61

</div>

Instructions in the **Bundle Split** group of the LinxISA v0.58.6 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BSTART](../instructions/bstart.md) | `BSTART DIRECT, <label>` | 32 | — | Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind. |
| [BSTART.FP](../instructions/bstart_fp.md) | `BSTART.FP FALL` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.GMOV](../instructions/bstart_gmov.md) | `BSTART.GMOV DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER](../instructions/bstart_mgather.md) | `BSTART.MGATHER DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.ADD](../instructions/bstart_mgather_add.md) | `BSTART.MGATHER.ADD DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.AND](../instructions/bstart_mgather_and.md) | `BSTART.MGATHER.AND DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.CAS](../instructions/bstart_mgather_cas.md) | `BSTART.MGATHER.CAS DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.DEC](../instructions/bstart_mgather_dec.md) | `BSTART.MGATHER.DEC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.EXCH](../instructions/bstart_mgather_exch.md) | `BSTART.MGATHER.EXCH DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.INC](../instructions/bstart_mgather_inc.md) | `BSTART.MGATHER.INC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.MASK](../instructions/bstart_mgather_mask.md) | `BSTART.MGATHER.MASK DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.MAX](../instructions/bstart_mgather_max.md) | `BSTART.MGATHER.MAX DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.MIN](../instructions/bstart_mgather_min.md) | `BSTART.MGATHER.MIN DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.OR](../instructions/bstart_mgather_or.md) | `BSTART.MGATHER.OR DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.XOR](../instructions/bstart_mgather_xor.md) | `BSTART.MGATHER.XOR DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MPAR](../instructions/bstart_mpar.md) | `BSTART.MPAR <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER](../instructions/bstart_mscatter.md) | `BSTART.MSCATTER DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.ADD](../instructions/bstart_mscatter_add.md) | `BSTART.MSCATTER.ADD DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.AND](../instructions/bstart_mscatter_and.md) | `BSTART.MSCATTER.AND DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.DEC](../instructions/bstart_mscatter_dec.md) | `BSTART.MSCATTER.DEC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.INC](../instructions/bstart_mscatter_inc.md) | `BSTART.MSCATTER.INC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.MASK](../instructions/bstart_mscatter_mask.md) | `BSTART.MSCATTER.MASK DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.MAX](../instructions/bstart_mscatter_max.md) | `BSTART.MSCATTER.MAX DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.MIN](../instructions/bstart_mscatter_min.md) | `BSTART.MSCATTER.MIN DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.OR](../instructions/bstart_mscatter_or.md) | `BSTART.MSCATTER.OR DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.POPC](../instructions/bstart_mscatter_popc.md) | `BSTART.MSCATTER.POPC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.XOR](../instructions/bstart_mscatter_xor.md) | `BSTART.MSCATTER.XOR DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSEQ](../instructions/bstart_mseq.md) | `BSTART.MSEQ <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.STD](../instructions/bstart_std.md) | `BSTART.STD FALL` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.SYS](../instructions/bstart_sys.md) | `BSTART.SYS FALL` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TEPL](../instructions/bstart_tepl.md) | `BSTART.TEPL Mode, Function, DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMV](../instructions/bstart_tgemv.md) | `BSTART.TGEMV DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMV.ACC](../instructions/bstart_tgemv_acc.md) | `BSTART.TGEMV.ACC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMV.BIAS](../instructions/bstart_tgemv_bias.md) | `BSTART.TGEMV.BIAS DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX](../instructions/bstart_tgemvmx.md) | `BSTART.TGEMVMX DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX.ACC](../instructions/bstart_tgemvmx_acc.md) | `BSTART.TGEMVMX.ACC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX.BIAS](../instructions/bstart_tgemvmx_bias.md) | `BSTART.TGEMVMX.BIAS DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TIMG2COL](../instructions/bstart_timg2col.md) | `BSTART.TIMG2COL DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TLOAD](../instructions/bstart_tload.md) | `BSTART.TLOAD DataType` | 32 | — | Loads a 64-bit value from memory. |
| [BSTART.TMATMUL](../instructions/bstart_tmatmul.md) | `BSTART.TMATMUL DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMATMUL.ACC](../instructions/bstart_tmatmul_acc.md) | `BSTART.TMATMUL.ACC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMATMUL.BIAS](../instructions/bstart_tmatmul_bias.md) | `BSTART.TMATMUL.BIAS DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMATMULMX](../instructions/bstart_tmatmulmx.md) | `BSTART.TMATMULMX DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMATMULMX.ACC](../instructions/bstart_tmatmulmx_acc.md) | `BSTART.TMATMULMX.ACC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMATMULMX.BIAS](../instructions/bstart_tmatmulmx_bias.md) | `BSTART.TMATMULMX.BIAS DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TMOV](../instructions/bstart_tmov.md) | `BSTART.TMOV DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TPREFETCH](../instructions/bstart_tprefetch.md) | `BSTART.TPREFETCH DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TSTORE](../instructions/bstart_tstore.md) | `BSTART.TSTORE DataType` | 32 | — | Stores a register value to memory. |
| [BSTOP](../instructions/bstop.md) | `BSTOP` | 32 | — | Block termination marker. Ends the current basic block. |
| [C.BSTART](../instructions/c_bstart.md) | `C.BSTART DIRECT, label` | 16 | — | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTOP](../instructions/c_bstop.md) | `C.BSTOP` | 16 | — | [16-bit C.] Marks the end of the current block. |
| [ERCOV](../instructions/ercov.md) | `ERCOV [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]` | 32 | — | Inventories an extension-owned execution-context recovery family rejected by PTO before operand interpretation or effects. |
| [ESAVE](../instructions/esave.md) | `ESAVE [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]` | 32 | — | Inventories an extension-owned execution-context save family rejected by PTO before operand interpretation or effects. |
| [FENTRY](../instructions/fentry.md) | `FENTRY [RegSrc0 ~ RegSrcn], sp!, uimm` | 32 | — | Creates a restartable stack frame by snapshotting and storing one inclusive callee-save register-ring range. |
| [FEXIT](../instructions/fexit.md) | `FEXIT [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Destroys a restartable stack frame and restores one inclusive callee-save register-ring range. |
| [FRET.RA](../instructions/fret_ra.md) | `FRET.RA [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Restores a restartable stack frame and returns through the pre-restore architectural return address. |
| [FRET.STK](../instructions/fret_stk.md) | `FRET.STK [ra ~ RegDstn], sp!, uimm` | 32 | — | Restores a restartable stack frame whose first stack slot supplies the validated return target. |
| [L.BSTOP](../instructions/l_bstop.md) | `L.BSTOP` | 64 | — | Commits the current bundle and transfers to its selected continuation. |
| [MCOPY](../instructions/mcopy.md) | `MCOPY [RegSrc0, RegSrc1, RegSrc2]` | 32 | — | Copies a non-overlapping byte range in restartable forward memory steps. |
| [MSET](../instructions/mset.md) | `MSET [RegSrc0=Destination, RegSrc1=FillByte, RegSrc2=LengthBytes]` | 32 | — | Fills a complete unsigned XLEN byte range with the low byte of an absolute GPR after complete access preflight. |
| [XB](../instructions/xb.md) | `XB ACR-ID, C-ID` | 32 | — | Inventories an extension-owned cross-block transfer encoding that PTO rejects before field interpretation or architectural effects. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
