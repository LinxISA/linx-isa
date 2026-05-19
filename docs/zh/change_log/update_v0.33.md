# 0.33版本更新

日期：2023年11月3日

指令编码设计文档网页版路径请见[LinxISA Encoding-v0.33](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255827005)

## 变动1：LD/ST新增Scale和Unscale模式

Scaled/Unscaled指的是，对右源操作数SrcR是否针对访存位宽进行移位。

- **Scaled:** Address = SrcL + SrcR << size
- **Unscaled:** Address = SrcL + SrcR

Scaled和Unscaled对`Reg+Reg`和`Reg+Imm`都适用。

- **Scaled:** Address = SrcL + imm << size
- **Unscaled:** Address = SrcL + imm

在0.33中，LD在Opcode中使用额外1bit来区别scale和unscale, 这1 bit代表要不要移位。  
这个变动的好处是，scaled表达范围更大，数据结构从 2MB（12bit）提升到 16MB (15bit) 。同时不对齐的场景下，又给软件更多的选择。  

Load类指令（Reg+imm）scaled模式编码：

![load1-v0.33](../figs/isa/version/load1-v0.33.png)

Load类指令（Reg+imm）unscaled模式编码：

![load2-v0.33](../figs/isa/version/load2-v0.33.png)

Load.a类指令（Reg+imm）scaled模式编码：

![load3-v0.33](../figs/isa/version/load3-v0.33.png)

Load.a类指令（Reg+imm）unscaled模式编码：

![load4-v0.33](../figs/isa/version/load4-v0.33.png)

1. 原有的Load/store编码上默认变成scaled，并在新的opcode空间新增unscaled的load和store。因此，只有新增编码，原有的编码不变。
2. 由于SrcL-SrcR计算地址的使用场景较少，原有ScaledLoad (Opcode = 7'b001_00X0)和ScaledStore (Opcode = 7'b001_01X0)，即Reg+Reg寻址时，右源寄存器不再支持取反操作(.neg)，保留截取低字有/无符号扩展实现（.sw和.uw）。
3. 原有 ScaledLoad (Opcode = 7'b001_00X1)和ScaledStore (Opcode = 7'b001_01X1)，即Reg+Imm寻址时，执行语义上有变化：根据访存位宽对立即数进行移位。
4. 原有prf/prf.a指令去掉(Opcode = 7'b001_00X1)的编码格式，即Reg+Imm格式，在prf.ui/prf.uia指令(Opcode = 7'b001_10X1)中实现对应执行语义。
5. prf/prf.a指令(Opcode = 7'b001_00X0)的编码中最高位3bit定义为`model`字段，用于实现预取目的cache的层级设置。

更新前：

![prefetch-v0.32](../figs/isa/version/prefetch-v0.32.png)

更新后：

![prefetch-v0.33](../figs/isa/version/prefetch-v0.33.png)

prefetch Model：000 : L1 Cache; 001 : L2 Cache; 010 : L3 Cache;

增加unscaled模式后，scaled和unscaled类型的load/store指令对立即数的移位对比如下：

| Scaled Load  |  Scaled  | Unscaled Load  |  Unscaled  |
|--------------|-------------|------------|------------|
| lh  | SrcL+simm<<1  | lh.ui  |  SrcL+simm  |
| lw  | SrcL+simm<<2  | lw.ui  |  SrcL+simm  |
| ld  | SrcL+simm<<3  | ld.ui  |  SrcL+simm  |
| lhu | SrcL+simm<<1  | lhu.ui  |  SrcL+simm  |
| lwu | SrcL+simm<<2  | lwu.ui  |  SrcL+simm  |
| lh.a  | SrcL+simm<<1  | lhu.uia  |  SrcL+simm  |
| lw.a  | SrcL+simm<<2  | lw.uia  |  SrcL+simm  |
| ld.a  | SrcL+simm<<3  | ld.uia  |  SrcL+simm  |
| lhu.a  | SrcL+simm<<1  | lhu.uia  |  SrcL+simm  |
| lwu.a  | SrcL+simm<<2  | lwu.uia  |  SrcL+simm  |

| Scaled Store  |  Scaled  | Unscaled Store  |  Unscaled  |
|--------------|-------------|------------|------------|
| sh  | SrcL+SrcR<<1  | sh.ur  |  SrcL+SrcR  |
| sw  | SrcL+SrcR<<2  | sw.ur  |  SrcL+SrcR  |
| sd  | SrcL+SrcR<<3  | sd.ur  |  SrcL+SrcR  |
| sh.a  | SrcL+SrcR<<1  | sh.ura  |  SrcL+SrcR  |
| sw.a  | SrcL+SrcR<<2  | sw.ura  |  SrcL+SrcR  |
| sd.a  | SrcL+SrcR<<3  | sd.ura  |  SrcL+SrcR  |
| sh  | SrcL+simm<<1  | sh.ui  |  SrcL+simm  |
| sw  | SrcL+simm<<2  | sw.ui  |  SrcL+simm  |
| sd  | SrcL+simm<<3  | sd.ui  |  SrcL+simm  |
| sh.a  | SrcL+simm<<1  | sh.uia  |  SrcL+simm  |
| sw.a  | SrcL+simm<<2  | sw.uia  |  SrcL+simm  |
| sd.a  | SrcL+simm<<3  | sd.uia  |  SrcL+simm  |

修改scaled模式load/store指令的汇编格式，

|     微指令    | 更新前汇编       |     更新后汇编                                                                           |
|---------------|---------------|--------------------------------------------------------------------------------------------------|
| LH     | lh \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lh \[SrcL, simm\]<, {=>, ->}RegDst> |
| LW     | lw \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lw \[SrcL, simm\]<, {=>, ->}RegDst> |
| LD     | ld \[SrcL, simm<<3\]<, {=>, ->}RegDst> | ld \[SrcL, simm\]<, {=>, ->}RegDst> |
| LBU    | lbu \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lbu \[SrcL, simm\]<, {=>, ->}RegDst> |
| LHU    | lhu \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lhu \[SrcL, simm\]<, {=>, ->}RegDst> |
| LWU    | lwu \[SrcL, simm<<3\]<, {=>, ->}RegDst> | lwu \[SrcL, simm\]<, {=>, ->}RegDst> |
| LH.A   | lh.a \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lh.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LW.A   | lw.a \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lw.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LD.A   | ld.a \[SrcL, simm<<3\]<, {=>, ->}RegDst> | ld.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LHU.A  | lhu.a \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lhu.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LWU.A  | lwu.a \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lhu.a \[SrcL, simm\]<, {=>, ->}RegDst> |

|     微指令    |      更新前汇编           |     更新后汇编                                                                    |
|---------------|------------------------|------------------------------------------------------------------------------|
| SH     | sh SrcD, \[SrcL, SrcR<{.sw,.uw}><<1\] | sh SrcD, \[SrcL, SrcR<{.sw,.uw}>\] |
| SW     | sw SrcD, \[SrcL, SrcR<{.sw,.uw}><<2\] | sw SrcD, \[SrcL, SrcR<{.sw,.uw}>\] |
| SD     | sd SrcD, \[SrcL, SrcR<{.sw,.uw}><<3\] | sd SrcD, \[SrcL, SrcR<{.sw,.uw}>\] |
| SH.A   | sh.a SrcD, \[SrcL, SrcR<{.sw,.uw}><<1\]<, {=>, ->}RegDst> | sh.a SrcD, \[SrcL, SrcR<{.sw,.uw}>\]<, {=>, ->}RegDst> |
| SW.A   | sw.a SrcD, \[SrcL, SrcR<{.sw,.uw}><<2\]<, {=>, ->}RegDst> | sw.a SrcD, \[SrcL, SrcR<{.sw,.uw}>\]<, {=>, ->}RegDst> |
| SD.A   | sd.a SrcD, \[SrcL, SrcR<{.sw,.uw}><<3\]<, {=>, ->}RegDst> | sd.a SrcD, \[SrcL, SrcR<{.sw,.uw}>\]<, {=>, ->}RegDst> |

|     微指令    |      更新前汇编           |     更新后汇编                                                                    |
|---------------|------------------------|------------------------------------------------------------------------------|
| SH     | sh SrcL, [SrcR, simm<<1] | sh SrcL, [SrcR, simm] |
| SW     | sw SrcL, [SrcR, simm<<2] | sw SrcL, [SrcR, simm] |
| SD     | sd SrcL, [SrcR, simm<<3] | sd SrcL, [SrcR, simm] |
| SH.A   | sh.a SrcL, [SrcR, simm<<1]<, {=>, ->}RegDst> | sh.a SrcL, [SrcR, simm]<, {=>, ->}RegDst> |
| SW.A   | sw.a SrcL, [SrcR, simm<<2]<, {=>, ->}RegDst> | sw.a SrcL, [SrcR, simm]<, {=>, ->}RegDst> |
| SD.A   | sd.a SrcL, [SrcR, simm<<3]<, {=>, ->}RegDst> | sd.a SrcL, [SrcR, simm]<, {=>, ->}RegDst> |

!!! note "注意"
    以上只是对指令的汇编格式的修改，指令语义并没有改变。

## 控制块类型增加BLB和BSB块指令

增加BLB指令的目的是为了提升访存效率，增加BSB指令可以降低Load/Store冲突。

具体介绍可以查看每条指令的实现。

- **BLBAR**：内存加载投机屏障(Block Load Speculation Barrier)。
- **BSBAR**：内存写入投机屏障(Block Store Speculation Barrier)。

!!! note "注意"
   一个块指令内有内存写store时，必须要增加BSB块指令。没有该块指令代表当前块没有内存写。

## JR增加立即数-复用BCOND编码

JR指令执行语义和编码变化，更新后的指令实现及编码请查看[JR](../isa/inst/misa_g/JR.md)。

对JR指令的这次变动是块内跳转的一个优化场景。如果需要跳转到一个symbol所在的位置，且j指令编码不足，那么只需要一个addtpc和jr即可完成。

```
jmp_label:
   ......
   
addtpc %top_20bit(jmp_label)
jr t#1, %bottom_12bit(jmp_label)
```

更新前则需使用三条指令完成：
```
jmp_label:
   ......
   
addtpc %top_20bit(jmp_label)
addi t#1, %bottom_12bit(jmp_label)
jr t#1
```

## 新增ADDBPCN指令和ADDBPCF指令

在CALLBLOCK下，获取当前或者下一个块头的BPC是经常使用的指令。但是由于编码限制，Next Block PC不想占用立即数域段。因此，我们新增了ADDBPCF指令。（注：使用立即数的指令的Opcode最低位必须是1）。加入该指令可以加速CALL块的访问速度。

- ADDBPCF: Add Block PC Fall Through，将当前块的顺延BPC导入到T寄存器或RegDst寄存器中。

在PGO和性能Debug下，我们需要获取到当前跳转预测预测出来的PC值。达到Branch Record的效果。

- ADDBPCN: Add Block PC Next，将当前块的预测的下个BPC导入到T寄存器或RegDst寄存器中。

增加ADDBPCN和ADDBPCF指令后，对原有ADDBPC指令的opcode做出调整：

修改前：

![ADDBPC-v0.32](../figs/isa/version/ADDBPC-v0.32.png)

修改后：

![ADDBPC-v0.33](../figs/isa/version/ADDBPC-v0.33.png)

由于编码冲突，重新调整了ADDBPC,ADDBPCN,ADDBPCF三条指令的`opcode`。

更正后编码：

![ADDBPC-v0.33-1](../figs/isa/version/ADDBPC-v0.33-1.png)

## ADD/ADDW编码调整

1. 为了避免与全0编码（非法指令）冲突，对add指令编码做出调整：指令编码高3位（func字段）由3’b000改为3’b001。

![ADD-v0.33](../figs/isa/version/ADD-v0.33.png)

2. 为了适配add指令的修改，对addw编码也做同样调整。

![ADDW-v0.33](../figs/isa/version/ADDW-v0.33.png)
