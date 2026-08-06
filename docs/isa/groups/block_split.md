# Block Split

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** Block Split &nbsp;|&nbsp;
**Forms:** 2 &nbsp;|&nbsp;
**Unique mnemonics:** 2

</div>

Block structural instructions (BSTART, BSTOP, FENTRY, etc.).

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BSTART.VPAR](../instructions/bstart_vpar.md) | `BSTART.VPAR <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |
| [BSTART.VSEQ](../instructions/bstart_vseq.md) | `BSTART.VSEQ <VS8, VS16>` | 32 | — | Terminates the current block and begins the next. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
