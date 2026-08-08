# BSTART CALL

<div class="insn-header">

<span class="badge-32">32-bit Base</span> **Group:** <a href="../groups/bstart.md">BSTART</a> &nbsp;|&nbsp;
<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Length:** <code>32</code> &nbsp;|&nbsp; **Decode:** <code>—</code>

</div>

## Assembly Syntax

- `BSTART.CALL <br_label>, <rt_label>, ->ra`

## Encoding

<div class="enc-diagram">

<figure>
<img src="../wavedrom/enc_bstart_call.svg" alt="BSTART CALL encoding" width="100%" />
<figcaption>Bitfield encoding diagram. MSB is on the left, LSB on the right.</figcaption>
</figure>

</div>

## Description

Atomic fused call with independent call-target and return-target fields; transfers to the call block and writes `ra`. This exact aggregate is distinct from the generic bare-call form, which preserves `ra` and requires an adjacent `SETRET` or `C.SETRET`.

## Pseudocode (informative)

```c
P = CurrentPC();
call_target = P + (SignExtend(simm12) << 1);
ra = (P + 2) + (ZeroExtend(uimm5) << 1);
AtomicCallTransfer(call_target, ra);
```

## Encoding Notes

- `Atomically closes the current bundle, computes the call target from the signed displacement and the return address from the independent unsigned displacement, writes ra, and transfers control to the call bundle.`

## Full Catalog Forms

| Assembly | Length | Decode |
|----------|--------|--------|
| `BSTART.CALL <br_label>, <rt_label>, ->ra` | 32 | — |

<div class="insn-nav">

← [BSTART](../groups/bstart.md) &nbsp;&nbsp; [Index](../index.md) &nbsp;&nbsp; [All instructions](index.md) →

</div>
