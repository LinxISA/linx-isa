# headerDefinition

header instruction of the vector data block is used to define the execution mode between groups, the number of executions of body, the Tile register and global register of input/output, and the execution dependencies with other block instruction. And since the vector data block can only be in the form of separate blocks, the position of body also needs to be indicated in header.

## Assembly format

header for vector parallel block:
```asm
VPAR .body, <LB0:arg0, LB1:arg1, LB2:arg2, VSize, DR>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, [BGetList], DepSrc,
                                          ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList], DepDst
```
header for vector serial block:
```asm
VSEQ .body, <LB0:arg0, LB1:arg1, LB2:arg2, VSize, DR>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, [BGetList], DepSrc,
                                          ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList], DepDst
```

Each assembly parameter is described as follows:

| Parameters | Description | Optional or not |
|------|------|---------|
| **.body** | The program label of the starting position of body. | No |
| **LB0** | The upper limit parameter of the innermost loop can be set through the arg0 (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameter. | Yes, default is 1 |
| **LB1** | The upper limit parameter of the middle layer loop can be set through the arg1 (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameter. | Yes, default is 1 |
| **LB2** | The outermost loop upper limit parameter can be set through the arg2 (`全局寄存器`, `立即数` or `全局寄存器加立即数`) parameter. | Yes, default is 1 |
| **VSize** | The number of vector registers used in the block is divided into two levels: <br> **VS16**: 4 sets of registers are required in the block, each set of 4. <br>**VS8**: 2 sets of registers are required in the block, each set of 4. | Yes, default vs16 |
| **DR** | Indicates the parameters of body [Group Mode] (../mem_block/dimmode.md), which are divided into two types: **Dimensionality Reduction Mode DR** and **Multidimensional Mode** | Yes, the default multidimensional mode |
| **SrcTile0, ..., SrcTile7** | Indicate up to 8 input Tile registers respectively. | Yes |
| **reuse** | This flag needs to be added when the corresponding input Tile register is not allowed to be released after the execution of this instruction. If there is no such mark, it means that the hardware is allowed to release this register. | Yes |
| **DstTile0, ..., DstTile3** | Indicate up to 4 output Tile register types respectively | Optional T, U, M or N. | Yes |
| **TileSize0, ..., TileSize3** | Indicates the space size of each output Tile register respectively. The parameter can be passed through a `立即数` or `全局寄存器`. | Depends on DstTile |
| **[BGetList]** | Global register [GGPR](../../register/common/ggpr.md) input list. | Yes |
| **[BSetList]** | Global register [GGPR](../../register/common/ggpr.md) output list. | Yes |
| **DepSrc** | Indicates the dependence of this block instruction on the previous block instruction output to D. | Yes |
| **DepDst** | Indicates the barrier of this block instruction to the block instruction that references this identifier in subsequent sequences. | Yes |

## Encoding method

A complete vector data block instructionheader needs to be split into the following multiple instructions for combined encoding, including:- `BSTART.VPAR` or `BSTART.VSEQ` `VSize`.
- [B.CATR](../../header/B.CATR.md) `DR`.
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`.
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`.
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`.
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile0<TileSize0>`.
- `...`
- [B.IOT](../../header/B.IOT.md) `SrcTile6<.reuse>, SrcTile7<.reuse>, last, ->DstTile3<TileSize3>`.
- [B.IOR](../../header/B.IOR.md) `RegSrc0, RegSrc1, RegSrc2, ->RegDst0`
- `...`
- [B.IOR](../../header/B.IOR.md) `RegSrc9, RegSrc10, RegSrc11, ->RegDst4`
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`.

Among them, the encoding format of the BSTART.VPAR instruction is as follows:

![BSTART.VPAR](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.VPAR.svg)

The encoding format of the BSTART.VSEQ instruction is as follows:

![BSTART.VSEQ](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.VSEQ.svg)

Among them, the mode field is used to encode VSize information.

| Encoding | VSize |
|------|-------|
| 0 | VS8 |
| 1 | VS16 |
| 2 | VS32, the current version is retained |
| 3 | VS64, the current version is retained |

In order to reduce the length of header instruction, BSTART of the vector data block provides a 16-bit compressed version of encoding. The encoding method is as follows:

C.BSTART.VPAR instruction encoding:

![C.BSTART.VPAR](../../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.VPAR.svg)

C.BSTART.VSEQ command encoding:

![C.BSTART.VSEQ](../../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.VSEQ.svg)

The compressed version of the instruction does not have a VSize field and defaults to `VSize = VS16`.

## Assembly example

Example 1: Two sets of vector registers are used in the block: vt, vu
```asm
hed:
    VPAR .foo, <LB0:64, LB1:10, VS8>, T#1.reuse, ->T<8KB>
    ...
.foo:
    v.lwi [TA, lc0<<2, 0], ->vt.w
    v.lwi [TA, lc0<<2, 4], ->vt.w
    v.mul vt#1,.sw, vt#2.sw, ->vt.w
    v.sw vt#1.sw, [TO, lc0<<2]
    ...
    v.lwi [a1, lc0<<2, 0], ->vu.w
    v.lwi [a1, lc0<<2, 4], ->vu.w
    v.add vu#1,.sw, vu#2.sw, ->vt.w
    v.sw vt#1.sw, [TO, lc0<<2]
```

Example 2: Four sets of vector registers are used in the block: vt, vu, vm, vn
```asm
hed:
    VPAR .foo, <LB0:64, LB1:10, VS8>, T#1.reuse, ->T<8KB>
    ...
.foo:
    v.lwi [TA, lc0<<2, 0], ->vt.w
    v.lwi [TA, lc0<<2, 4], ->vu.w
    v.mul vt#1,.sw, vu#1.sw, ->vt.w
    v.sw vt#1.sw, [TO, lc0<<2]
    ...
    v.lwi [a1, lc0<<2, 0], ->vm.w
    v.lwi [a1, lc0<<2, 4], ->vn.w
    v.add vm#1,.sw, vn#1.sw, ->vt.w
    v.sw vt#1.sw, [TO, lc0<<2]
```