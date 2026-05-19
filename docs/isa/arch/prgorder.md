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

## 3. Look at the PO with three **real code snippets**

The following is a "header → Expand → PO" comparison of three common blocks, which does not require abstract notation at all.

### Example 1: Pure GEMM (16×16×16) and write the result back to Tile

**header (the order of appearance is L1-IPO):**

```asm
BSTART.PAR TMATMUL, FP16       ; 配置：做 FP16 的 A×B
B.DIM     rM, 128, ->M        ; M=128
B.DIM     rN, 128, ->N        ; N=128
B.DIM     rK, 256, ->K        ; K=256
B.IOT     [TA, TB], group=0, ->ACC<64KB>   ; 绑定 A/B 到 ACC
B.ARG     CD2RD                ; 结果默认行主序，无额外变换
```

**Expanded block body steps (sequential replacement):**

1. Read/prefetch the slices of A and B to the internal buffer;
2. CUBE Core performs multiplication and accumulation with a granularity of 16×16×16, and the results are accumulated into ACC;
3. Write the ACC back to the target Tile (row major order).

**Final PO (Semantic Order):**

```
BSTART.PAR → B.DIM → B.DIM → B.DIM → B.IOT → B.ARG → 
加载分片 → 乘累加到 ACC → ACC 写回 Tile
```

---

### Example 2: GEMM + TCVT conversion along the path (quantization/rearrangement before ACC→Tile)

**header：**

```asm
BSTART.PAR TMATMUL, FP16
B.DIM     zero, 64,  ->M
B.DIM     zero, 64,  ->N
B.DIM     zero, 256, ->K
B.IOT     [TA, TB], group=0, ->ACC<64KB>
B.ARG     ZZ2RD                  ; 指定 TCVT 的布局变换（例）
```

**Expanded block body (sequential replacement):**

1. Read/prefetch;
2. CUBE is multiplied and accumulated to ACC;
3. **TCVT FixPipe**: On the road of "ACC → Tile write back", **do format conversion while moving (such as inverse quantization, activation, layout transformation, etc.);
4. Write the converted data into the Tile Register.

**Final PO:**

```
ZXTERMZH39QXZ顺序 → 读取/预取 → 乘累加到 ACC → TCVT 边搬边转 → 写回 Tile
```

> The key here is: **TCVT is executed on the "ACC→Tile path"**, eliminating the round trip of "landing first and then starting another conversion".

---

### Example 3: TMATMULMX (micro scaling) + optional C Tile accumulation

**header：**

```asm
BSTART.PAR TMATMULMX, INT8
B.DIM     zero, 128, ->M
B.DIM     zero, 128, ->N
B.DIM     zero, 256, ->K
B.IOT     [TA, TSA], group=0, ->ACC<64KB>  ; A 与 ScaleA
B.IOT     [TB, TSB], group=1               ; B 与 ScaleB
; 可选：B.IOT [TC], group=2               ; 若做 +C
B.ARG     CD2RD
```

**Block body (sequential replacement):**1. Load A, ScaleA and B, ScaleB;
2. Before multiplication, press Tile broadcast scaling for A and B: `A' = A * ScaleA`, `B' = B * ScaleB`;
3. Multiply and accumulate the scaled A' and B' to ACC;
4. If there is C/ACC accumulation, perform the corresponding addition;
5. Write the ACC back to the Tile, or continue to convert it from TCVT and then write it back.

**Final PO:**

```
ZXTERMZH39QXZ顺序 → 读 A/B 与缩放 Tile → A/B 微缩放 → 乘累加到 ACC → (+C/ACC) → 写回
```

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