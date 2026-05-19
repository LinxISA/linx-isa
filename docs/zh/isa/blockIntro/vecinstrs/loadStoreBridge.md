# 桥接访存指令

为了降低寄存器使用开销，提升寄存器的利用率等，灵犀指令集中引入一组**桥接访存指令**（记为**Load bridge**和**Store Bridge**）。

桥接访存指令的访存位宽、地址计算方式和普通的Load、Store指令相同。区别在于：

- Load bridge的目的寄存器不再存放加载的数据，而是存放**桥接表**的一个表项索引。
- Store bridge的第一个源寄存器也不再获取数据，而是获取对应Load写入的表项索引。

**桥接表**是硬件中用于建立load与store之间建立桥接映射关系的一种信息表，每个表项包括一组global memory的地址和一组tile register的地址，以及状态位等。两组地址中的元素两两配对，建立Load的源地址与Store的目的地址之间的对应关系。在搬移数据时，实现数据快速从初始位置去到目的地，不需要在搬移单元中停留或缓冲。

示意图如下：

![bridgeTable](../../../figs/isa/arch/bridgetable.png){ width="500" }

## 使用场景

1. 从global memory Load的数据，不需要任何处理即可直接Store进Tile register（源和目的地反之亦可）；
2. 一个数据被Load指令produce之后，只有Store指令这一个consumer；

例如：
```asm
    v.ldi [vt#1.ud, 32], ->t.d 
    add t#1, a0, ->t
    v.sdi t#1.ud, [to, 32]
```
上述示例中，load产生的数据被后序的两条指令读取，因此不符合桥接访存指令使用要求。

## <span id="constrain">指令约束</span>

为了保证合理使用该类指令，我们对Load/Store bridge指令增加如下约束：

1. Load bridge和Store bridge指令必须**成对出现**，否则硬件报异常。
2. Load bridge指令的输出寄存器只能被后序的Store bridge指令读取，否则硬件报异常。

所谓Load bridge和Store bridge必须成对出现，就是要求：（1）前序有一条Load bridge指令，后序必须**有且仅有一条相同访存位宽的store bridge指令**；（2）前序没有Load bridge指令时，**不允许单独出现一条Store bridge指令**。

示例如下：
```asm
.body:
    ...
    v.ldi.brg [a0.ud, 32], ->t.d
    v.add a0.sw, vu#1.sw, ->vt.w
    v.sdi.brg t#1.ud, [to, 32]          # 合法的一对load bridge, store bridge指令
    ...
    v.ldi.brg [a0.ud, 32], ->t.d
    v.add t#1.ud, vu#1.ud, ->vt.d       # 非法读取了前序load bridge指令的输出，硬件报异常。
    v.sdi.brg t#1.ud, [to, 32]          
    ...
    v.ldi.brg [a0.ud, 32], ->t.d
    v.sdi.brg t#1.ud, [to, 16]      
    v.sdi.brg t#2.ud, [to, 32]          # 存在多个store bridge指令与前序load bridge匹配，硬件报异常。
    ...
    v.ldi.brg [a0.ud, 32], ->t.d
    bstop                               # 没有与load bridge配对的store bridge指令，硬件报异常
```

## Load Bridge指令

**寄存器-寄存器寻址**

| 指令 | 汇编格式 |
|-------|-------------|
| V.LB.BRG | `v.lb.brg<.local> [SrcL<.ud>, <lc0,> SrcR.<T><<<shamt>], ->Dst.<W>`  |
| V.LH.BRG | `v.lh.brg<.local> [SrcL<.ud>, <lc0<<1,> SrcR.<T><<<shamt>], ->Dst.<W>`  |
| V.LW.BRG | `v.lw.brg<.local> [SrcL<.ud>, <lc0<<2,> SrcR.<T><<<shamt>], ->Dst.<W>`  |
| V.LD.BRG | `v.ld.brg<.local> [SrcL<.ud>, <lc0<<3,> SrcR.<T><<<shamt>], ->Dst.<W>`  |
| V.LBU.BRG | `v.lbu.brg<.local> [SrcL<.ud>, <lc0,> SrcR.<T><<<shamt>], ->Dst.<W>`  |
| V.LHU.BRG | `v.lhu.brg<.local> [SrcL<.ud>, <lc0<<1,> SrcR.<T><<<shamt>], ->Dst.<W>`  |
| V.LWU.BRG | `v.lwu.brg<.local> [SrcL<.ud>, <lc0<<2,> SrcR.<T><<<shamt>], ->Dst.<W>`  |

指令编码如下：

![LoadBridgeRegisterOffset](../../../figs/bitfield/svg/Introduction_64bit/LoadBridgeRegisterOffsetVector.svg)

**寄存器-带缩放立即数寻址**

| 指令 | 汇编格式 |
|-------|-------------|
| V.LBI.BRG | `v.lbi.brg<.local> [SrcL<.ud>, <lc0,> simm], ->Dst.<W>`  |
| V.LHI.BRG | `v.lhi.brg<.local> [SrcL<.ud>, <lc0<<1,> simm], ->Dst.<W>`  |
| V.LWI.BRG | `v.lwi.brg<.local> [SrcL<.ud>, <lc0<<2,> simm], ->Dst.<W>`  |
| V.LDI.BRG | `v.ldi.brg<.local> [SrcL<.ud>, <lc0<<3,> simm], ->Dst.<W>`  |
| V.LBUI.BRG | `v.lbui.brg<.local> [SrcL<.ud>, <lc0,> simm], ->Dst.<W>`  |
| V.LHUI.BRG | `v.lhui.brg<.local> [SrcL<.ud>, <lc0<<1,> simm], ->Dst.<W>`  |
| V.LWUI.BRG | `v.lwui.brg<.local> [SrcL<.ud>, <lc0<<2,> simm], ->Dst.<W>`  |

指令编码如下：

![LoadBridgeImmediateOffset](../../../figs/bitfield/svg/Introduction_64bit/LoadBridgeImmediateOffsetVector.svg)

**寄存器-无缩放立即数寻址**

| 指令 | 汇编格式 |
|-------|-------------|
| V.LHI.U.BRG | `v.lhi.u.brg [SrcL<.ud>, <lc0<<1,> simm], ->Dst.<W>`  |
| V.LWI.U.BRG | `v.lwi.u.brg [SrcL<.ud>, <lc0<<2,> simm], ->Dst.<W>`  |
| V.LDI.U.BRG | `v.ldi.u.brg [SrcL<.ud>, <lc0<<3,> simm], ->Dst.<W>`  |
| V.LHUI.U.BRG | `v.lhui.u.brg [SrcL<.ud>, <lc0<<1,> simm], ->Dst.<W>`  |
| V.LWUI.U.BRG | `v.lwui.u.brg [SrcL<.ud>, <lc0<<2,> simm], ->Dst.<W>`  |

指令编码如下：

![LoadBridgeInstructionUnScaled](../../../figs/bitfield/svg/Introduction_64bit/LoadBridgeInstructionUnScaledVector.svg)

## Store Bridge指令

**寄存器-寄存器寻址**

| 指令 | 汇编格式 | 指令 | 汇编格式 |
|-------|-------------|-------|-------------|
| V.SB.BRG | `v.sb.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0,> SrcR.<T>]`  |
| V.SH.BRG | `v.sh.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<1,> SrcR.<T><<1]`  |
| V.SW.BRG | `v.sw.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<2,> SrcR.<T><<2]`  |
| V.SD.BRG | `v.sd.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<3,> SrcR.<T><<3]`  |
| V.SH.U.BRG | `v.sh.u.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<1,> SrcR.<T>]`  |
| V.SW.U.BRG | `v.sw.u.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<2,> SrcR.<T>]`  |
| V.SD.U.BRG | `v.sd.u.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<3,> SrcR.<T>]`  |

![StoreBridgeRegisterOffset](../../../figs/bitfield/svg/Introduction_64bit/StoreBridgeRegisterOffsetVector.svg)

**寄存器-立即数寻址**

| 指令 | 汇编格式 | 指令 | 汇编格式 |
|-------|-------------|-------|-------------|
| V.SBI.BRG  | `v.sbi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0,> simm]`     |
| V.SHI.BRG  | `v.shi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<1,> simm]`  |
| V.SWI.BRG  | `v.swi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<2,> simm]`  |
| V.SDI.BRG  | `v.sdi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<3,> simm]`  |
| V.SHI.U.BRG | `v.shi.u.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<1,> simm]`  |
| V.SWI.U.BRG | `v.swi.u.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<2,> simm]`  |
| V.SDI.U.BRG | `v.sdi.u.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<3,> simm]`  |

![StoreBridgeImmediateOffset](../../../figs/bitfield/svg/Introduction_64bit/StoreBridgeImmediateOffsetVector.svg)
