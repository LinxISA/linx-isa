# Cache Maintain

<div class="insn-header">

<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Group:** Cache Maintain &nbsp;|&nbsp;
**Forms:** 16 &nbsp;|&nbsp;
**Unique mnemonics:** 16

</div>

Cache maintenance operations (I-cache, D-cache, branch predictor).

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BC.IALL](../instructions/bc_iall.md) | `bc.iall` | 32 | — | Branch-predictor cache invalidate all entries. |
| [BC.IVA](../instructions/bc_iva.md) | `bc.iva SrcL` | 32 | — | Branch-predictor cache invalidate by address. |
| [DC.CISW](../instructions/dc_cisw.md) | `dc.cisw SrcL` | 32 | — | Data cache clean-and-invalidate by set/way. |
| [DC.CIVA](../instructions/dc_civa.md) | `dc.civa SrcL` | 32 | — | Cache maintenance operation. |
| [DC.CSW](../instructions/dc_csw.md) | `dc.csw SrcL` | 32 | — | Cache maintenance operation. |
| [DC.CVA](../instructions/dc_cva.md) | `dc.cva SrcL` | 32 | — | Cache maintenance operation. |
| [DC.IALL](../instructions/dc_iall.md) | `dc.iall` | 32 | — | Cache maintenance operation. |
| [DC.ISW](../instructions/dc_isw.md) | `dc.isw SrcL` | 32 | — | Data cache invalidate by set/way. |
| [DC.IVA](../instructions/dc_iva.md) | `dc.iva SrcL` | 32 | — | Data cache invalidate by address. |
| [DC.ZVA](../instructions/dc_zva.md) | `dc.zva SrcL` | 32 | — | Cache maintenance operation. |
| [IC.IALL](../instructions/ic_iall.md) | `ic.iall` | 32 | — | Cache maintenance operation. |
| [IC.IVA](../instructions/ic_iva.md) | `ic.iva SrcL` | 32 | — | Cache maintenance operation. |
| [TLB.IA](../instructions/tlb_ia.md) | `tlb.ia SrcL` | 32 | — | Cache maintenance operation. |
| [TLB.IALL](../instructions/tlb_iall.md) | `tlb.iall` | 32 | — | Cache maintenance operation. |
| [TLB.IAV](../instructions/tlb_iav.md) | `tlb.iav SrcL` | 32 | — | Cache maintenance operation. |
| [TLB.IV](../instructions/tlb_iv.md) | `tlb.iv SrcL` | 32 | — | Cache maintenance operation. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 19: SYS — System Operations](../index.md)
- [Encoding formats](../encoding.md)
