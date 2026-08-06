# program order（Program Order, PO）

## 1. What is program order

**Linx processor** advances the internal state according to the order of received instructions and external events: whatever instructions you give it and in what order, it will "understand and take effect" in this order.
In order to clarify the semantics of "in what order should be understood and executed", we define **program order (Program Order, PO)**:

- **PO = From a code perspective, the external performance of the hardware should be equivalent execution order**.
- The hardware may be out of order or parallel internally, but the externally visible effects (final values ​​of registers, memory, Tiles) must be consistent with the PO.

---

## 2. Expand from "header sequence" to "program order"

Linx’s **block instruction** consists of two parts:

* **header**: Configure "what to do with this piece" (data type, dimensions, input/output Tile, etc.).
* **Block**: The steps actually executed (transport/multiply and accumulate/convert/write back, etc.).

When compiling, **header** will be arranged in a **linear order** (can be understood as the order of "call points"). After that, expand each header** into its **block body steps** to get the final program order PO.

### Two expansion methods

1. **Random replacement (no internal order enforced)**
   Several actions in the block body can be parallelized or the scheduling order is not fixed, as long as the overall order of the entire block before/after other blocks remains unchanged.

2. **Sequence replacement (internal order fixed)**
   The actions in the block body have a clear sequence and must be executed step by step - for example, "first move the data, then multiply and accumulate, and finally write back."

> The block body of most matrix/vector calculation blocks is **sequential replacement**, so the final PO is usually a clear total order.

---

## 3. CUBE examples in PTO ISA 0.58

PTO ISA 0.58 has no hidden architectural ACC state and no `ACCCVT` block.
CUBE descriptors always name an explicit Local destination D. ACC forms also
name an explicit Local accumulator input C.

### Example 1: base matrix multiply

`BSTART.TMATMUL` plus its dimension, attribute, and Tile descriptors expands to
read A and B, perform the matrix product, and write D. The entire expansion
occupies the program-order position of that block.

### Example 2: conversion after matrix multiply

Format or layout conversion is a separate explicit Tile operation that reads D
after the CUBE block. There is no implicit ACC-to-Tile path. Program order is:

```
TMATMUL descriptors → read A/B → write D → conversion descriptors → read D → write converted Tile
```

### Example 3: scaled accumulation

`BSTART.TMATMULMX.ACC` reads A, row scale, B, column scale, and accumulator C,
then writes D. If D aliases C, the operation reads the old C value and writes
the new result; otherwise C and D are independent explicit Tiles.

---

## 4. The relationship between PO and “real execution” (emphasis again)

* **PO is "the order that should be expressed"**: compilers, verification and upper-level frameworks all use this to understand program semantics.
* **The hardware can be out of order/parallel internally**, but the **externally visible effect must be equivalent to PO**.
* Subsequent constraints such as **register distance calculation, memory consistency/sequence, barriers**, etc. are all based on PO.

---

## 5. From micro to macro: how to implement it into your code

* Understand **header** as the **call point** that "occupies a position on the timeline";
* **Sequential replacement**: Replace this call point with "**specific steps**";
* **Random replacement**: You only emphasize "this is a set of actions", but the internal order of the set is not important (or is determined by the scheduler);
* Arrange all the blocks in the order in which **header appears**, and then expand them one by one. What you see is the **program order** of the entire program.

---

## 6. Summary

> **program order (PO) = At the code level, header is in the order of appearance → the overall order after using block actions (sequential/random) to expand. **
> No matter how optimized the hardware is, the **externally observed behavior** must be consistent with this "sequence line".

After writing this way, when you read any piece of Linx code, you can clearly answer three things:

1. **Sequence relationship**: Who is first and who is last;
2. **Expand content**: What specific actions does a header represent?
3. **Visible semantics**: No matter how parallel the underlying layer is, the results seen externally are consistent with this order.
