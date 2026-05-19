# 0.34版本更新

日期：2023年12月6日

指令编码设计文档网页版路径请见[LinxISA Encoding-v0.34](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100258403959)

## 版本更新总体说明

1. 增加13条浮点指令的实现。
2. load/store指令的更新：（1）地址偏移移位类（scaled）load/store指令的拆分；（2）地址偏移不移位类（unscaled）load/store指令汇编名称修改（3）增加一条空store指令。
3. 部分指令编码调整：（1）系统指令编码调整；（2）算数运算移位类指令编码调整；（3）部分模板块指令编码调整；（4）条件选择指令CSEL编码调整
4. 部分指令汇编格式修改：（1）预取指令汇编格式中增加l1/l2/l3 Cache标识符；（2）模板块指令B.MCOPY和B.MSET汇编格式去掉目的寄存器
5. CARG寄存器去除BSET/BGET/MSG域段，改为64bit寄存器。

## 修改一、增加浮点指令实现

**浮点计算类**

|     微指令    |         汇编格式                          |     描述       |
|--------------|-------------------------------------------|----------------|
|  fadd   |  fadd{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst>           |  浮点加法      |
|  fsub   |  fsub{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst>           |  浮点减法      |
|  fmul   |  fmul{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst>           |  浮点乘法      |
|  fmadd  |  fmadd{.d,.s,.h} SrcL, RSR, t#c<, {=>, ->}RegDst>      |  浮点乘加      |
|  fdiv   |  fdiv{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst>           |  浮点除法        |
|  fabs   |  fabs{.d,.s,.h} SrcL<, {=>, ->}RegDst>                 |  浮点绝对值    |
|  fsqrt  |  fsqrt{.d,.s,.h} SrcL<, {=>, ->}RegDst>                |  浮点平方根    |

**浮点转换类**

|   微指令  |     汇编格式                      |      描述    |
|----------|-----------------------------------|--------------|
|  fcvt   |  fcvt.dstT SrcL.srcT<, {=>, ->}RegDst>    |  浮点转换      |

**浮点比较类**

|     微指令    | 汇编格式         |     描述                     |
|--------------|------------------|------------------------------|
|  feq    |  feq{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst>    |  浮点相等比较         |
|  fle    |  fle{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst>    |  浮点小于等于比较     |
|  flt    |  flt{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst>    |  浮点小于比较         |

**最大最小值类**

|     微指令    | 汇编格式         |     描述                     |
|--------------|------------------|------------------------------|
|   fmax   |  fmax{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst>   |  浮点最大值     |
|   fmin   |  fmin{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst>   |  浮点最小值     |

## 修改二、Load/Store指令变动

1.对寻址偏移移位类（scaled模式）的load/store指令根据`Reg + Reg`和`Reg + Imm`两种编码格式拆分成两条指令。

- `Reg + Reg` 编码格式：保持原有的指令名称不变。
- `Reg + Imm` 编码格式：在原有的指令名称中添加 "**I**"，表明该指令是使用立即数偏移的load/store指令，增加一条指令。例如：`LB -> LBI`，`SD -> SDI`，`LW.A -> LWI.A`，`SD.A -> SDI.A`

**Load指令的修改**

| 原指令名称 | 拆分后指令名称 | 汇编示例            |   解释                                                                                |
|-----------|---------------|---------------------|---------------------------------------------------------------------------------------|
| LB | LB<br>LBI | lb [a1, a2 << shamt]<br>lbi [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + imm，默认不移位 |
| LH | LH<br>LHI | lh [a1, a2 << shamt]<br>lhi [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 1)，默认左移1位 |
| LW | LW<br>LWI | lw [a1, a2 << shamt]<br>lwi [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 2)，默认左移2位 |
| LD | LD<br>LDI | ld [a1, a2 << shamt]<br>ldi [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 3)，默认左移3位 |
| LBU | LBU<br>LBUI | lbu [a1, a2 << shamt]<br>lbui [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + imm，默认不移位 |
| LHU | LHU<br>LHUI | lhu [a1, a2 << shamt]<br>lhui [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 1)，默认左移1位 |
| LWU | LWU<br>LWUI | lwu [a1, a2 << shamt]<br>lwui [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 2)，默认左移2位 |
| LB.A | LB.A<br>LBI.A | lb.a [a1, a2 << shamt]<br>lbi.a [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + imm，默认不移位 |
| LH.A | LH.A<br>LHI.A | lh.a [a1, a2 << shamt]<br>lhi.a [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 1)，默认左移1位 |
| LW.A | LW.A<br>LWI.A | lw.a [a1, a2 << shamt]<br>lwi.a [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 2)，默认左移2位 |
| LD.A | LD.A<br>LDI.A | ld.a [a1, a2 << shamt]<br>ldi.a [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 3)，默认左移3位 |
| LBU.A | LBU.A<br>LBUI.A | lbu.a [a1, a2 << shamt]<br>lbui.a [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + imm，默认不移位 |
| LHU.A | LHU.A<br>LHUI.A | lhu.a [a1, a2 << shamt]<br>lhui.a [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 1)，默认左移1位 |
| LWU.A | LWU.A<br>LWUI.A | lwu.a [a1, a2 << shamt]<br>lwui.a [a1, imm] | 访存地址为 a1 + (a2 << shamt)，不固定移位<br>访存地址为 a1 + (imm << 2)，默认左移2位 |

**Store指令的修改**

| 原指令名称 | 拆分后指令名称 | 汇编示例            |   解释                                                                                |
|-----------|---------------|---------------------|---------------------------------------------------------------------------------------|
| SB | SB<br>SBI | sb a0, [a1, a2]<br>sbi a0, [a1, imm] | 访存地址为a1 + a2，默认不移位<br>访存地址为 a1 + imm，默认不移位 |
| SH | SH<br>SHI | sh a0, [a1, a2]<br>shi a0, [a1, imm] | 访存地址为a1 + (a2 << 1)，默认左移1位<br>访存地址为 a1 + (imm << 1)，默认左移1位 |
| SW | SW<br>SWI | sw a0, [a1, a2]<br>swi a0, [a1, imm] | 访存地址为a1 + (a2 << 2)，默认左移2位<br>访存地址为 a1 + (imm << 2)，默认左移2位 |
| SD | SD<br>SDI | sd a0, [a1, a2]<br>sdi a0, [a1, imm] | 访存地址为a1 + (a2 << 3)，默认左移3位<br>访存地址为 a1 + (imm << 3)，默认左移3位 |
| SB.A | SB.A<br>SBI.A | sb.a a0, [a1, a2]<br>sbi.a a0, [a1, imm] | 访存地址为a1 + a2，默认不移位<br>访存地址为 a1 + imm，默认不移位 |
| SH.A | SH.A<br>SHI.A | sh.a a0, [a1, a2]<br>shi.a a0, [a1, imm] | 访存地址为a1 + (a2 << 1)，默认左移1位<br>访存地址为 a1 + (imm << 1)，默认左移1位 |
| SW.A | SW.A<br>SWI.A | sw.a a0, [a1, a2]<br>swi.a a0, [a1, imm] | 访存地址为a1 + (a2 << 2)，默认左移2位<br>访存地址为 a1 + (imm << 2)，默认左移2位 |
| SD.A | SD.A<br>SDI.A | sd.a a0, [a1, a2]<br>sdi.a a0, [a1, imm] | 访存地址为a1 + (a2 << 3)，默认左移3位<br>访存地址为 a1 + (imm << 3)，默认左移3位 |

2.为了命名格式的统一，修改寻址偏移不移位类（unscaled模式）的load/store指令名称。

**Load指令的修改**

| 原指令名称 | 修改后的名称 |  汇编示例            |   解释                              |
|-----------|-------------|---------------------|-------------------------------------|
| LH.UI  | LHI.U | lhi.u [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LW.UI  | LWI.U | lwi.u [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LD.UI  | LDI.U | ldi.u [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LHU.UI  | LHUI.U | lhui.u [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LWU.UI  | LWUI.U | lwui.u [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| PRF.UI  | PRFI.U | prfi.u.l1 [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LB.UIA  | LBI.UA | lbi.ua [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LH.UIA  | LHI.UA | lhi.ua [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LW.UIA  | LWI.UA | lwi.ua [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LD.UIA  | LDI.UA | ldi.ua [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LHU.UIA  | LHUI.UA | lhui.ua [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| LWU.UIA  | LWUI.UA | lwui.ua [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| PRF.UIA  | PRFI.UA | prfi.ua.l1 [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |

**Store指令的修改**

| 原指令名称 | 修改后的名称 |  汇编示例            |   解释                              |
|-----------|-------------|---------------------|-------------------------------------|
| SH.UR  | SH.U | sh.u a0, [a1, a2]  | 访存地址为 a1 + a2，不做默认移位  |
| SW.UR  | SW.U | sw.u a0, [a1, a2]  | 访存地址为 a1 + a2，不做默认移位  |
| SD.UR  | SD.U | sd.u a0, [a1, a2]  | 访存地址为 a1 + a2，不做默认移位  |
| SH.URA  | SH.UA | sh.ua a0, [a1, a2]  | 访存地址为 a1 + a2，不做默认移位  |
| SW.URA  | SW.UA | sw.ua a0, [a1, a2]  | 访存地址为 a1 + a2，不做默认移位  |
| SD.URA  | SD.UA | sd.ua a0, [a1, a2]  | 访存地址为 a1 + a2，不做默认移位  |
| SH.UI  | SHI.U | shi.u a0, [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| SW.UI  | SWI.U | swi.u a0, [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| SD.UI  | SDI.U | sdi.u a0, [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| SH.UIA  | SHI.UA | shi.ua a0, [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| SW.UIA  | SWI.UA | swi.ua a0, [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |
| SD.UIA  | SDI.UA | sdi.ua a0, [a1, imm]  | 访存地址为 a1 + imm，不做默认移位  |

3.增加一条store指令SNOP(Store NOP)

该store指令**不写内存**，只占Store Buffer Entry（配合BSBAR内存写屏障块指令使用）。

指令编码如下：

![SN](../figs/isa/version/SN.png)

## 修改三、指令编码调整

### 系统块指令编码调整

为了方便硬件解码实现以及规范编解码格式，我们希望使用立即数的指令编码中**Opcode**域段最低位为 **1**。因此对系统指令包括SSRGET，SSRSET，SSRCRLT（及其展开指令）的编码进行了调整。

具体来讲：将Opcode从原来的 `7'b100_0000` 改为 `7'b100_0001`。

更新后的编码：

![sysinst-v0.34](../figs/isa/version/sysinst-v0.34.png)

### 移位指令编码调整

为了完善指令编解码格式的规范性，首先对移位指令的高位进行了更加明确地域段划分，同时SRA{I,W,IW}指令与SRL{I,W,IW}指令的func字段(编码的12-14bit)使用了相同的编码，并在高位的func字段进行区分，这样可以为以后版本添加移位类指令预留空间。SLL{I,W,IW}指令的func字段(编码的12-14bit)做了顺延的修改。

修改前的编码：

![shift-v0.33](../figs/isa/version/shift-0.33.png)

修改后的编码：

![shift-v0.34](../figs/isa/version/shift-0.34.png)

### 模板块指令编码调整

在当前版本中，B.MCOPY和B.MSET在执行过程中被打断时状态的保存可使用异常块来实现，因此这两条指令不需要输出寄存器的编码。所以删除了B.MCOPY和B.MSET指令编码中RegDst0- RegDst2域段，改为占位值4’b0000。

修改前的编码：

![memblock-v0.33](../figs/isa/version/memblock-0.33.png)

修改后的编码：

![memblock-v0.34](../figs/isa/version/memblock-0.34.png)

在上个版本中，模板块的立即数编码为15bit(低三位为0)，但是在指令实现时15bit的立即数无法在一条微指令中表达，因此修改了模板块的实现方式。当立即数有效位超过12bit时，使用三条指令组合的形式，拼接出块头中的长立即数。既然实现方式修改后可以处理超过12位的立即数，那么不如同时扩展立即数的范围，将块指令编码的16-31bit都编码为立即数，这样可以表达19bit的立即数，指令可使用的栈空间更大。因此，对模板块fentry, fexit, ftexit三条块指令编码的立即数域段做出调整。

修改前的编码：

![temlblock-v0.33](../figs/isa/version/temlblock-0.33.png)

修改后的编码：

![temlblock-v0.34](../figs/isa/version/temlblock-0.34.png)

块指令编码修改后，块头中立即数可表达19bit的立即数（低三位默认为0）。当块头表达的立即数有效位超过12位时，使用多条指令组合的形式拼接出块头表达的长立即数。下面以F.ENTRY指令为例说明此次修改：

- 修改前的执行方式：
```c
subi RegPtr, imm, => RegPtr

sd RegSrc0, [RegPtr, -8]
sd RegSrc1, [RegPtr, -16]
sd RegSrc2, [RegPtr, -24]
...
sd RegSrcn, [RegPtr, -8*m]
```
- 修改后的执行方式：
```c
if uimm19[18:12] != 0:
    lui {13'b0 + uimm19[18:12]}
    addi t#1, uimm19[11:0]
    sub RegPtr, t#1, => RegPtr
else:
    subi RegPtr, uimm19[11:0], => RegPtr

sd RegSrc0, [RegPtr, -8]
sd RegSrc1, [RegPtr, -16]
sd RegSrc2, [RegPtr, -24]
...
sd RegSrcn, [RegPtr, -8*m]
```

### 控制块指令编码调整

#### BLBAR块指令编码调整

BLBAR块头的编码格式中，BInst[63:32]的高16bit用于编码块指令的输入，低16bit用于编码块指令的输出。为了统一编码格式，将LoadBase0域段编码改到BInst[51:48]位置，改名为`RegPtr`，该域段用于存储第一层架构寄存器ID，索引第一层架构寄存器R0-R15。

同时，该指令预取size都是以一条Cacheline(64byte)为单位，因此将原块头编码中BlockSize域段改为固定编码**2'b01**。

编码更新前：

![BLBAR-0.33](../figs/isa/version/BLBAR-0.33.png)

编码更新后：

![BLBAR-0.34](../figs/isa/version/BLBAR-0.34.png)

#### BSBAR块指令编码调整

编码更新前：

![BSBAR-0.33](../figs/isa/version/BSBAR-0.33.png)

编码更新后：

![BSBAR-0.34](../figs/isa/version/BSBAR-0.34.png)

!!! note "注意"

    为了消除没有store指令前的BSBAR块：BSBAR 0格式的块，减少硬件BROB的占用，该指令禁止store_count为0。

### CSEL/ADDC/SUBC指令编码调整

CSEL/ADDC/SUBC指令是三输入的指令。为了简化硬件的读口设计，以前的版本中，在指令设计层面将第三个源寄存器限制为T寄存器，第二个源寄存器限制为Local GPR，第一个源寄存器没有限制。从而达到最多同时有两个T寄存器输入或最多两个Local Reg寄存器输入的目的。

在当前版本，在指令编码层面，取消了第二个源寄存器固定为Local GPR的限制，即第二个源寄存器既可以是T寄存器，也可以是Local GPR。

以前版本编码：

![bitmap-0.33](../figs/isa/version/bitmap-0.33.png)

当前版本编码：

![bitmap-0.34](../figs/isa/version/bitmap-0.34.png)

## 修改四、汇编格式的修改

1.微指令汇编格式的修改 

在前面的版本中，预取指令prf和prf.a编码格式增加了model字段，用来指示指令预取到的哪一层级的Cache，但是汇编格式上并没有做修改。为了汇编程序员能够明确指明指令预取的cache层级，因此在prf和prf.a两条指令的汇编名称后增加了 “.l1/.l2/.l3” 的后缀。而prfi.u和prfi.ua指令默认预取到L1 Cache，为了格式统一，在这两条指令的汇编名称后增加了 “.l1” 的后缀。修改后的汇编格式如下表：

|  指令  | 原汇编格式                            | 修改后的汇编格式                                 |
|-------|--------------------------------------|-------------------------------------------------|
| prf | prf [SrcL, srcR<{.sw,.uw}><<<shamt>] | prf{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw}><<<shamt>] |
| prf.a | prf [SrcL, SrcR<{.sw,.uw}><<<shamt>]<, {=>, ->}RegDst> | prf.a{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw}><<<shamt>]<, {=>, ->}RegDst> |
| prfi.u | prfi.u [SrcL, simm] | prfi.u.l1 [SrcL, simm]  |
| prfi.ua | prfi.ua [SrcL, simm]<, {=>, ->}RegDst> | prfi.ua.l1 [SrcL, simm]<, {=>, ->}RegDst> |

2.块指令汇编格式修改

同上面所讲，模板块B.MCOPY和B.MSET指令的编码中删除了RegDst0-RegDst2的字段，因此汇编格式中同样去掉RegDst0-RegDst2的表达。

B.MCOPY修改后：
```
    b.mcopy [RegSrc0, RegSrc1, RegSrc2]
```
B.MSET修改后：
```
    b.mset [RegSrc0, RegSrc1, RegSrc2]
```

## 修改五、CARG系统寄存器修改

1. CARG寄存器删除了MSG/BGET/BSET域段。
2. setc.msg指令需要使用别名指令[BSE](../isa/inst/misa_s/BSE.md)代替。
3. 块内BGET/BSET状态的保存在当前版本使用B.EXCEPTION异常块实现。
4. 块内发送的消息保存在消息缓存寄存器中。

以前版本寄存器域段：

![CARG-v0.33](../figs/isa/version/CARG-0.33.png)

当前版本寄存器域段：

![CARG-v0.34](../figs/isa/version/CARG-0.34.png)
