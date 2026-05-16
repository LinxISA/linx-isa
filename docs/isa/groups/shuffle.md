# Shuffle

<div class="insn-header">

<span class="ch-tag ch-tag-20">Ch 20</span>
&nbsp; <strong>VEC — Vector / SIMD Execution (lx64)</strong> &nbsp;|&nbsp;
**Group:** Shuffle &nbsp;|&nbsp;
**Forms:** 8 &nbsp;|&nbsp;
**Unique mnemonics:** 8

</div>

Vector lane shuffle operations.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [V.SHFL.BFLY](../instructions/v_shfl_bfly.md) | `v.shfl.bfly SrcL, SrcP, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFL.DOWN](../instructions/v_shfl_down.md) | `v.shfl.down SrcL, SrcR, SrcP, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFL.IDX](../instructions/v_shfl_idx.md) | `v.shfl.idx SrcL, SrcR, SrcP, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFL.UP](../instructions/v_shfl_up.md) | `v.shfl.up SrcL, SrcR, SrcP, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.BFLY](../instructions/v_shfli_bfly.md) | `v.shfli.bfly SrcL, imm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.DOWN](../instructions/v_shfli_down.md) | `v.shfli.down SrcL, SrcR, imm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.IDX](../instructions/v_shfli_idx.md) | `v.shfli.idx SrcL, SrcR, imm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.UP](../instructions/v_shfli_up.md) | `v.shfli.up SrcL, SrcR, imm, ->Dst` | 64 | — | [64-bit V.] Instruction from the Shuffle group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 20: VEC — Vector / SIMD Execution (lx64)](../index.md)
- [Encoding formats](../encoding.md)
