# SYS

<div class="insn-header">

<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Group:** SYS &nbsp;|&nbsp;
**Forms:** 35 &nbsp;|&nbsp;
**Unique mnemonics:** 35

</div>

Instructions in the **SYS** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [ACRC](../instructions/acrc.md) | `acrc rst_type` | 32 | — | Architectural control (ring call). Calls an implementation-defined ACR. |
| [ACRE](../instructions/acre.md) | `acre rra_type` | 32 | — | Architectural control (ring entry). Enters an implementation-defined ACR. |
| [ASSERT](../instructions/assert.md) | `assert SrcL` | 32 | — | Architectural assertion. Traps if the condition register is zero. |
| [BC.IALL](../instructions/bc_iall.md) | `bc.iall` | 32 | — | Branch-predictor cache invalidate all entries. |
| [BC.IVA](../instructions/bc_iva.md) | `bc.iva SrcL` | 32 | — | Branch-predictor cache invalidate by address. |
| [BSE](../instructions/bse.md) | `bse SrcL` | 32 | — | BSE publishes the SendEvent nonblocking execution-control request. |
| [BWE](../instructions/bwe.md) | `bwe SrcL` | 32 | — | BWE publishes the WaitEvent nonblocking execution-control request. |
| [BWI](../instructions/bwi.md) | `bwi SrcL` | 32 | — | BWI publishes the WaitInterrupt nonblocking execution-control request. |
| [BWT](../instructions/bwt.md) | `bwt SrcL` | 32 | — | BWT publishes the WaitTimeout nonblocking execution-control request. |
| [C.EBREAK](../instructions/c_ebreak.md) | `c.break imm` | 16 | — | C.EBREAK raises software-breakpoint trap 50 with its 5-bit immediate as cause. |
| [C.SSRGET](../instructions/c_ssrget.md) | `c.ssrget SSR-ID, ->t` | 16 | — | C.SSRGET reads the complete encoded system-register address. |
| [DC.CISW](../instructions/dc_cisw.md) | `dc.cisw SrcL` | 32 | — | Data cache clean-and-invalidate by set/way. |
| [DC.CIVA](../instructions/dc_civa.md) | `dc.civa SrcL` | 32 | — | DC.CIVA completes the data-cache clean-and-invalidate scope token maintenance operation synchronously. |
| [DC.CSW](../instructions/dc_csw.md) | `dc.csw SrcL` | 32 | — | DC.CSW completes the data-cache clean-by-set/way scope token maintenance operation synchronously. |
| [DC.CVA](../instructions/dc_cva.md) | `dc.cva SrcL` | 32 | — | DC.CVA completes the data-cache clean-by-address scope token maintenance operation synchronously. |
| [DC.IALL](../instructions/dc_iall.md) | `dc.iall` | 32 | — | DC.IALL completes the data-cache all-entry scope maintenance operation synchronously. |
| [DC.ISW](../instructions/dc_isw.md) | `dc.isw SrcL` | 32 | — | Data cache invalidate by set/way. |
| [DC.IVA](../instructions/dc_iva.md) | `dc.iva SrcL` | 32 | — | Data cache invalidate by address. |
| [DC.ZVA](../instructions/dc_zva.md) | `dc.zva SrcL` | 32 | — | DC.ZVA completes the data-cache zero-by-address scope token maintenance operation synchronously. |
| [EBREAK](../instructions/ebreak.md) | `ebreak imm` | 32 | — | Environment break instruction. Traps to the debugging or OS handler. |
| [FENCE.D](../instructions/fence_d.md) | `fence.d pred_imm, succ_imm` | 32 | — | Data memory ordering fence. |
| [FENCE.I](../instructions/fence_i.md) | `fence.i` | 32 | — | Instruction-cache fence. Synchronizes instruction fetch with prior stores. |
| [HL.SSRGET](../instructions/hl_ssrget.md) | `hl.ssrget SSR_ID, ->{t, u, Rd}` | 48 | — | HL.SSRGET reads the complete encoded system-register address. |
| [HL.SSRSET](../instructions/hl_ssrset.md) | `hl.ssrset SrcL, SSR_ID` | 48 | — | HL.SSRSET writes the complete encoded system-register address. |
| [IC.IALL](../instructions/ic_iall.md) | `ic.iall` | 32 | — | IC.IALL completes the instruction-cache all-entry scope maintenance operation synchronously. |
| [IC.IVA](../instructions/ic_iva.md) | `ic.iva SrcL` | 32 | — | IC.IVA completes the instruction-cache virtual-address scope token maintenance operation synchronously. |
| [LSRGET](../instructions/lsrget.md) | `lsrget LSR_ID, ->{t, u, Rd}` | 32 | — | LSRGET reads one assigned word from the active block BARG view. |
| [SETC.TGT](../instructions/setc_tgt.md) | `setc.tgt SrcL` | 32 | — | Sets the block-commit condition. |
| [SSRGET](../instructions/ssrget.md) | `ssrget SSR_ID, ->{t, u, Rd}` | 32 | — | SSRGET reads the complete encoded system-register address. |
| [SSRSET](../instructions/ssrset.md) | `ssrset SrcL, SSR_ID` | 32 | — | SSRSET writes the complete encoded system-register address. |
| [SSRSWAP](../instructions/ssrswap.md) | `ssrswap SrcL, SSR_ID, ->{t, u, Rd}` | 32 | — | SSRSWAP atomically swaps the complete encoded system-register address. |
| [TLB.IA](../instructions/tlb_ia.md) | `tlb.ia SrcL` | 32 | — | TLB.IA completes the 16-bit ASID token in bits 15:0 maintenance operation synchronously. |
| [TLB.IALL](../instructions/tlb_iall.md) | `tlb.iall` | 32 | — | TLB.IALL completes the all translation entries maintenance operation synchronously. |
| [TLB.IAV](../instructions/tlb_iav.md) | `tlb.iav SrcL` | 32 | — | TLB.IAV completes the canonical 48-bit virtual address with ASID scope maintenance operation synchronously. |
| [TLB.IV](../instructions/tlb_iv.md) | `tlb.iv SrcL` | 32 | — | TLB.IV completes the canonical 48-bit virtual address maintenance operation synchronously. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 19: SYS — System Operations](../index.md)
- [Encoding formats](../encoding.md)
