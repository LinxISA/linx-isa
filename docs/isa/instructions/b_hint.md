# B.HINT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_hint.md">Bundle Hint</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-00">Ch 00</span>
&nbsp; <strong>ISA Manual</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.HINT TRACE.{begin, end}`
- `B.HINT {BR.{likely, unlikely}, TEMP.{hot, warm, cool, none}, PRFSIZE}`

## Encoding

<div class="enc-diagram">

<figure id="encoding-b_hint_32_67e2ad8dd981">
<img src="../wavedrom/enc_b_hint_32_67e2ad8dd981.svg" alt="B.HINT encoding form b_hint_32_67e2ad8dd981" width="100%" />
<figcaption><code>b_hint_32_67e2ad8dd981</code> — <code>B.HINT TRACE.{begin, end}</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_hint_32_b3e8a4e77930">
<img src="../wavedrom/enc_b_hint_32_b3e8a4e77930.svg" alt="B.HINT encoding form b_hint_32_b3e8a4e77930" width="100%" />
<figcaption><code>b_hint_32_b3e8a4e77930</code> — <code>B.HINT {BR.{likely, unlikely}, TEMP.{hot, warm, cool, none}, PRFSIZE}</code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

Records non-functional branch, temperature, prefetch-size, or trace guidance.

## Pseudocode (informative)

```c
// Execute B.HINT as defined by the Bundle Hint semantics.
```

## Encoding Notes

- `Records non-functional branch, temperature, prefetch-size, or trace guidance.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `b_hint_32_67e2ad8dd981` | `B.HINT TRACE.{begin, end}` | 32 | — | [SVG](../wavedrom/enc_b_hint_32_67e2ad8dd981.svg) |
| `b_hint_32_b3e8a4e77930` | `B.HINT {BR.{likely, unlikely}, TEMP.{hot, warm, cool, none}, PRFSIZE}` | 32 | — | [SVG](../wavedrom/enc_b_hint_32_b3e8a4e77930.svg) |

<div class="insn-nav">

← [Bundle Hint](../groups/bundle_hint.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
