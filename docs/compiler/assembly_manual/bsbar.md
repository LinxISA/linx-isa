# Memory write speculative barrier directive: **BSBAR**

For details of the instruction definition and microarchitecture behavior of the memory write speculation barrier BSBAR (Block Store Speculation Barrier), please see: [Instruction Manual/Control Block/BSBAR](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/inst/BSBAR/)

In assembly, `b.sbar.<oow> <N>` is a **pseudo-instruction** located in the header assembly pseudo-instruction sequence (for the header assembly description, see: [Programming Manual/Assembly Instructions/header/Overview] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/compiler/assembly_manual/block_header/)). For example:
```Linx
...
.section .text
label:
  bstart label.start
  b.sbar 1
  bget a0, a1
  bstop label.end
.section .text.body
label.start:
  sdi a0, [a1, 0]
label.end:
...
```

-----------------------

The following is the writing method of `b.sbar <N>`. At this time, the store in the block is submitted **sequentially**:

| Number of **runtime** stores in the block | Assembly representation |
|------------|------------|
| N = 0 | Mode 1: `b.sbar 0`; Mode 2: Default. **Note**: The two expressions are equivalent |
| N = [1, 63] | `b.sbar N` |
| N = [64, +∞) | `b.sbar ` |
| The value of N is uncertain | `b.sbar ` |

The following is the writing method of `b.sbar.oow <N>`. At this time, the store in the block is submitted out of order:

| Number of **runtime** stores in the block | Assembly representation |
|------------|------------|
| N = 0 | `b.sbar.oow 0` |
| N = [1, 63] | `b.sbar.oow N` |
| N = [64, +∞) | `b.sbar.oow ` |
| The value of N is uncertain | `b.sbar.oow ` |