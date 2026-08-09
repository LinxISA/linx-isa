# C.TINST

<div class="insn-header">

<span class="ch-tag ch-tag-19">Ch 19</span>
&nbsp; <strong>SYS — System Operations</strong> &nbsp;|&nbsp;
**Group:** C.TINST &nbsp;|&nbsp;
**Forms:** 6 &nbsp;|&nbsp;
**Unique mnemonics:** 6

</div>

16-bit compressed miscellaneous instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.CMP.EQI](../instructions/c_cmp_eqi.md) | `c.cmp.eqi t#1, simm, ->t` | 16 | — | C.CMP.EQI - Compare scalar operands and write the encoded boolean result. |
| [C.CMP.NEI](../instructions/c_cmp_nei.md) | `c.cmp.nei t#1, simm, ->t` | 16 | — | C.CMP.NEI - Compare scalar operands and write the encoded boolean result. |
| [C.EBREAK](../instructions/c_ebreak.md) | `c.break imm` | 16 | — | C.EBREAK - Raise the software breakpoint exception. |
| [C.SLLI](../instructions/c_slli.md) | `c.slli t#1, uimm, ->t` | 16 | — | C.SLLI - Compute this mnemonic's binary scalar operation and write the selected destination. |
| [C.SRLI](../instructions/c_srli.md) | `c.srli t#1, uimm, ->t` | 16 | — | C.SRLI - Compute this mnemonic's binary scalar operation and write the selected destination. |
| [C.SSRGET](../instructions/c_ssrget.md) | `c.ssrget SSR-ID, ->t` | 16 | — | C.SSRGET - Read the compressed-form system register. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 19: SYS — System Operations](../index.md)
- [Encoding formats](../encoding.md)
