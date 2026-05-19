# 块头定义

向量数据块的块头指令用于定义Group间的执行模式、块体的执行次数、输入输出的Tile寄存器和全局寄存器以及与其他块指令之间的执行依赖等信息。并且由于向量数据块只能是分离块形式的，因此块头中还需要指示块体的位置。

## 汇编格式

向量并行块的块头：
```asm
VPAR .body, <LB0:arg0, LB1:arg1, LB2:arg2, VSize, DR>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, [BGetList], DepSrc,
                                          ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList], DepDst
```
向量串行块的块头：
```asm
VSEQ .body, <LB0:arg0, LB1:arg1, LB2:arg2, VSize, DR>, SrcTile0<.reuse>, ..., SrcTile7<.reuse>, [BGetList], DepSrc,
                                          ->DstTile0<TileSize0>, ..., DstTile3<TileSize3>, [BSetList], DepDst
```

各汇编参数说明如下：

| 参数 | 说明 | 是否可选 |
|------|------|---------|
| **.body** | 块体起始位置的程序标签。 | 否 |
| **LB0** | 最内层循环上限参数，可以通过arg0（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **LB1** | 中间层循环上限参数，可以通过arg1（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **LB2** | 最外层循环上限参数，可以通过arg2（`全局寄存器`、`立即数`或`全局寄存器加立即数`）参数设置。 | 是，默认为1 |
| **VSize** | 块内使用的向量寄存器的数量，分为两档：<br> **VS16**：块内需要使用4组寄存器，每组4个。<br>**VS8**：块内需要使用2组寄存器，每组4个。 | 是，默认vs16 |
| **DR** | 指示块体[分组模式](../mem_block/dimmode.md)的参数，分为**降维模式DR**和**多维模式**两种 | 是，默认多维模式 |
| **SrcTile0, ..., SrcTile7** | 分别指示最多8个输入的Tile寄存器。 | 是 |
| **reuse** | 当本指令执行结束后相应的输入Tile寄存器不允许被释放则需要增加该标识。如无此标识，则表示允许硬件释放本寄存器。 | 是 |
| **DstTile0, ..., DstTile3** | 分别指示最多4个输出Tile寄存器类型 | 可选T, U, M或N。 | 是 |
| **TileSize0, ..., TileSize3** | 分别指示每个输出Tile寄存器的空间大小，可以通过一个 `立即数`或者`全局寄存器`传参。 | 取决于DstTile |
| **[BGetList]** | 全局寄存器[GGPR](../../register/common/ggpr.md)输入列表。 | 是 |
| **[BSetList]** | 全局寄存器[GGPR](../../register/common/ggpr.md)输出列表。 | 是 |
| **DepSrc** | 表示本块指令对前序输出至D的块指令的依赖。 | 是 |
| **DepDst** | 表示本块指令对后序引用该标识的块指令的屏障。 | 是 |

## 编码方式

一条完整向量数据块指令块头需要拆分成以下多条指令进行组合编码，其中包括：

- `BSTART.VPAR` 或 `BSTART.VSEQ` `VSize`。
- [B.CATR](../../header/B.CATR.md) `DR`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`。
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>, ->DstTile0<TileSize0>`。
- `...`
- [B.IOT](../../header/B.IOT.md) `SrcTile6<.reuse>, SrcTile7<.reuse>, last, ->DstTile3<TileSize3>`。
- [B.IOR](../../header/B.IOR.md) `RegSrc0, RegSrc1, RegSrc2, ->RegDst0`
- `...`
- [B.IOR](../../header/B.IOR.md) `RegSrc9, RegSrc10, RegSrc11, ->RegDst4`
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`。

其中，BSTART.VPAR指令的编码格式如下：

![BSTART.VPAR](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.VPAR.svg)

BSTART.VSEQ指令的编码格式如下：

![BSTART.VSEQ](../../../figs/bitfield/svg/BlockHeader_32bit/BSTART.VSEQ.svg)

其中，mode字段用于编码VSize信息。

| 编码 | VSize |
|------|-------|
| 0 | VS8 |
| 1 | VS16 |
| 2 | VS32，当前版本保留 |
| 3 | VS64，当前版本保留 |

为了降低块头指令的长度，向量数据块的BSTART提供了一种16bit 压缩版本的编码，编码方式如下：

C.BSTART.VPAR指令编码：

![C.BSTART.VPAR](../../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.VPAR.svg)

C.BSTART.VSEQ指令编码：

![C.BSTART.VSEQ](../../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.VSEQ.svg)

压缩版本的指令没有VSize字段，并且默认`VSize = VS16`。

## 汇编示例

示例1：块内使用到2组向量寄存器: vt, vu
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

示例2：块内使用到4组向量寄存器: vt, vu, vm, vn
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
