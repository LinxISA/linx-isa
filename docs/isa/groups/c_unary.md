# C.UNARY

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** C.UNARY &nbsp;|&nbsp;
**Forms:** 7 &nbsp;|&nbsp;
**Unique mnemonics:** 7

</div>

16-bit compressed unary operations.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.SETC.TGT](../instructions/c_setc_tgt.md) | `c.setc.tgt srcL` | 16 | — | [16-bit C.] Sets the block-commit condition. |
| [C.SEXT.B](../instructions/c_sext_b.md) | `c.sext.b srcL, ->t` | 16 | — | C.SEXT.B - Sign-extend or zero-extend the selected scalar subword. |
| [C.SEXT.H](../instructions/c_sext_h.md) | `c.sext.h srcL, ->t` | 16 | — | C.SEXT.H - Sign-extend or zero-extend the selected scalar subword. |
| [C.SEXT.W](../instructions/c_sext_w.md) | `c.sext.w srcL, ->t` | 16 | — | C.SEXT.W - Sign-extend or zero-extend the selected scalar subword. |
| [C.ZEXT.B](../instructions/c_zext_b.md) | `c.zext.b srcL, ->t` | 16 | — | C.ZEXT.B - Sign-extend or zero-extend the selected scalar subword. |
| [C.ZEXT.H](../instructions/c_zext_h.md) | `c.zext.h srcL, ->t` | 16 | — | C.ZEXT.H - Sign-extend or zero-extend the selected scalar subword. |
| [C.ZEXT.W](../instructions/c_zext_w.md) | `c.zext.w srcL, ->t` | 16 | — | C.ZEXT.W - Sign-extend or zero-extend the selected scalar subword. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
