# B.IOT

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bundle_input_output.md">Bundle Input & Output</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>`
- `B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>`
- `B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>`
- `B.IOT SrcTile0, mask=PE_MASK, <last>, ->DstTile<SizeCode>`
- `B.IOT SrcTile0.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>`
- `B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>`
- `B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>`
- `B.IOT mask=PE_MASK, <last>, ->DstTile<SizeCode>`
- `B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>`
- `B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>`
- `B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>`
- `B.IOT SrcTile0.reuse, mask=PE_MASK, <last>`
- `B.IOT SrcTile0, mask=PE_MASK, <last>`

## Encoding

<div class="enc-diagram">

<figure id="encoding-b_iot_32_0175e009f69e">
<img src="../wavedrom/enc_b_iot_32_0175e009f69e.svg" alt="B.IOT encoding form b_iot_32_0175e009f69e" width="100%" />
<figcaption><code>b_iot_32_0175e009f69e</code> — <code>B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_15bc51973d26">
<img src="../wavedrom/enc_b_iot_32_15bc51973d26.svg" alt="B.IOT encoding form b_iot_32_15bc51973d26" width="100%" />
<figcaption><code>b_iot_32_15bc51973d26</code> — <code>B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_2d213eb811c7">
<img src="../wavedrom/enc_b_iot_32_2d213eb811c7.svg" alt="B.IOT encoding form b_iot_32_2d213eb811c7" width="100%" />
<figcaption><code>b_iot_32_2d213eb811c7</code> — <code>B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_2f60297debcb">
<img src="../wavedrom/enc_b_iot_32_2f60297debcb.svg" alt="B.IOT encoding form b_iot_32_2f60297debcb" width="100%" />
<figcaption><code>b_iot_32_2f60297debcb</code> — <code>B.IOT SrcTile0, mask=PE_MASK, <last>, ->DstTile<SizeCode></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_3bc48b48fea2">
<img src="../wavedrom/enc_b_iot_32_3bc48b48fea2.svg" alt="B.IOT encoding form b_iot_32_3bc48b48fea2" width="100%" />
<figcaption><code>b_iot_32_3bc48b48fea2</code> — <code>B.IOT SrcTile0.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_610b3e49f01c">
<img src="../wavedrom/enc_b_iot_32_610b3e49f01c.svg" alt="B.IOT encoding form b_iot_32_610b3e49f01c" width="100%" />
<figcaption><code>b_iot_32_610b3e49f01c</code> — <code>B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_6d3f0819f3ed">
<img src="../wavedrom/enc_b_iot_32_6d3f0819f3ed.svg" alt="B.IOT encoding form b_iot_32_6d3f0819f3ed" width="100%" />
<figcaption><code>b_iot_32_6d3f0819f3ed</code> — <code>B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_7d0899202df1">
<img src="../wavedrom/enc_b_iot_32_7d0899202df1.svg" alt="B.IOT encoding form b_iot_32_7d0899202df1" width="100%" />
<figcaption><code>b_iot_32_7d0899202df1</code> — <code>B.IOT mask=PE_MASK, <last>, ->DstTile<SizeCode></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_ba693fbfdca5">
<img src="../wavedrom/enc_b_iot_32_ba693fbfdca5.svg" alt="B.IOT encoding form b_iot_32_ba693fbfdca5" width="100%" />
<figcaption><code>b_iot_32_ba693fbfdca5</code> — <code>B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_bf660153d171">
<img src="../wavedrom/enc_b_iot_32_bf660153d171.svg" alt="B.IOT encoding form b_iot_32_bf660153d171" width="100%" />
<figcaption><code>b_iot_32_bf660153d171</code> — <code>B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_cd6ec8181a49">
<img src="../wavedrom/enc_b_iot_32_cd6ec8181a49.svg" alt="B.IOT encoding form b_iot_32_cd6ec8181a49" width="100%" />
<figcaption><code>b_iot_32_cd6ec8181a49</code> — <code>B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_e0f1463d6a7e">
<img src="../wavedrom/enc_b_iot_32_e0f1463d6a7e.svg" alt="B.IOT encoding form b_iot_32_e0f1463d6a7e" width="100%" />
<figcaption><code>b_iot_32_e0f1463d6a7e</code> — <code>B.IOT SrcTile0.reuse, mask=PE_MASK, <last></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

<figure id="encoding-b_iot_32_ed562ab5801f">
<img src="../wavedrom/enc_b_iot_32_ed562ab5801f.svg" alt="B.IOT encoding form b_iot_32_ed562ab5801f" width="100%" />
<figcaption><code>b_iot_32_ed562ab5801f</code> — <code>B.IOT SrcTile0, mask=PE_MASK, <last></code>. MSB is on the left, LSB is on the right.</figcaption>
</figure>

</div>

## Description

Bind ordered relative Local Tile sources and renamed destinations; each T/U/M/N #1 source names the newest published generation of that hand.

## Pseudocode (informative)

```c
// Execute B.IOT as defined by the Bundle Input & Output semantics.
```

## Encoding Notes

- `Bind ordered relative Local Tile sources and renamed destinations; each T/U/M/N #1 source names the newest published generation of that hand.`

## Full Catalog Forms

| Form ID | Assembly | Length | Decode | Encoding |
|---------|----------|--------|--------|----------|
| `b_iot_32_0175e009f69e` | `B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_0175e009f69e.svg) |
| `b_iot_32_15bc51973d26` | `B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_15bc51973d26.svg) |
| `b_iot_32_2d213eb811c7` | `B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_2d213eb811c7.svg) |
| `b_iot_32_2f60297debcb` | `B.IOT SrcTile0, mask=PE_MASK, <last>, ->DstTile<SizeCode>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_2f60297debcb.svg) |
| `b_iot_32_3bc48b48fea2` | `B.IOT SrcTile0.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_3bc48b48fea2.svg) |
| `b_iot_32_610b3e49f01c` | `B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_610b3e49f01c.svg) |
| `b_iot_32_6d3f0819f3ed` | `B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_6d3f0819f3ed.svg) |
| `b_iot_32_7d0899202df1` | `B.IOT mask=PE_MASK, <last>, ->DstTile<SizeCode>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_7d0899202df1.svg) |
| `b_iot_32_ba693fbfdca5` | `B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_ba693fbfdca5.svg) |
| `b_iot_32_bf660153d171` | `B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_bf660153d171.svg) |
| `b_iot_32_cd6ec8181a49` | `B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_cd6ec8181a49.svg) |
| `b_iot_32_e0f1463d6a7e` | `B.IOT SrcTile0.reuse, mask=PE_MASK, <last>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_e0f1463d6a7e.svg) |
| `b_iot_32_ed562ab5801f` | `B.IOT SrcTile0, mask=PE_MASK, <last>` | 32 | — | [SVG](../wavedrom/enc_b_iot_32_ed562ab5801f.svg) |

<div class="insn-nav">

← [Bundle Input & Output](../groups/bundle_input_output.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
