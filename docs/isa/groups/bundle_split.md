# Bundle Split

<div class="insn-header">

<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Group:** Bundle Split &nbsp;|&nbsp;
**Forms:** 60 &nbsp;|&nbsp;
**Unique mnemonics:** 41

</div>

Instructions in the **Bundle Split** group of the LinxISA v0.58.0 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BSTART](../instructions/bstart.md) | `BSTART {DIRECT, CALL}, <label>` | 32 | — | Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind. |
| [BSTART.FP](../instructions/bstart_fp.md) | `BSTART.FP FALL<, fixup_label>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.GMOV](../instructions/bstart_gmov.md) | `BSTART.GMOV DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER](../instructions/bstart_mgather.md) | `BSTART.MGATHER DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.CAS](../instructions/bstart_mgather_cas.md) | `BSTART.MGATHER.CAS DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MGATHER.MASK](../instructions/bstart_mgather_mask.md) | `BSTART.MGATHER.MASK DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MPAR](../instructions/bstart_mpar.md) | `BSTART.MPAR <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER](../instructions/bstart_mscatter.md) | `BSTART.MSCATTER DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.MASK](../instructions/bstart_mscatter_mask.md) | `BSTART.MSCATTER.MASK DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.MSEQ](../instructions/bstart_mseq.md) | `BSTART.MSEQ <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.STD](../instructions/bstart_std.md) | `BSTART.STD IND` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.SYS](../instructions/bstart_sys.md) | `BSTART.SYS FALL<, fixup_label>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TEPL](../instructions/bstart_tepl.md) | `BSTART.TEPL Mode, Function, DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMV](../instructions/bstart_tgemv.md) | `BSTART.TGEMV DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMV.ACC](../instructions/bstart_tgemv_acc.md) | `BSTART.TGEMV.ACC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMV.BIAS](../instructions/bstart_tgemv_bias.md) | `BSTART.TGEMV.BIAS DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX](../instructions/bstart_tgemvmx.md) | `BSTART.TGEMVMX DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX.ACC](../instructions/bstart_tgemvmx_acc.md) | `BSTART.TGEMVMX.ACC DataType` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX.BIAS](../instructions/bstart_tgemvmx_bias.md) | `BSTART.TGEMVMX.BIAS DataType` | 32 | — | Terminates the current block and begins the next. |
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
| [ERCOV](../instructions/ercov.md) | `ERCOV [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]` | 32 | — | Recovers the encoded execution-context range from memory. |
| [ESAVE](../instructions/esave.md) | `ESAVE [RegSrc0=BasePtr, RegSrc1=LenBytes, RegSrc2=Kind]` | 32 | — | Saves the encoded execution-context range to memory. |
| [FENTRY](../instructions/fentry.md) | `FENTRY [RegSrc0 ~ RegSrcn], sp!, uimm` | 32 | — | Atomically validates and creates a frame-template entry state. |
| [FEXIT](../instructions/fexit.md) | `FEXIT [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Atomically validates and commits a frame-template exit state. |
| [FRET.RA](../instructions/fret_ra.md) | `FRET.RA [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Restores a frame and returns through the retained return-address target. |
| [FRET.STK](../instructions/fret_stk.md) | `FRET.STK [RegDst0 ~ RegDstn], sp!, uimm` | 32 | — | Restores a frame and returns through the validated stack target. |
| [MCOPY](../instructions/mcopy.md) | `MCOPY [RegSrc0, RegSrc1, RegSrc2]` | 32 | — | Copies an encoded memory range with instruction-atomic preflight and snapshot semantics. |
| [MSET](../instructions/mset.md) | `MSET [RegSrc0, RegSrc1, RegSrc2]` | 32 | — | Fills an encoded memory range after complete access preflight. |
| [XB](../instructions/xb.md) | `XB ACR-ID, C-ID` | 32 | — | Transfers the named context value to a target virtual core block. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 0: ISA Manual](../index.md)
- [Encoding formats](../encoding.md)
