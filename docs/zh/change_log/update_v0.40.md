# 0.40版本更新

更新日期：2024年6月5日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.40](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100421282855)

LinxISA V0.40要解决的问题:

1. V0.3X的架构扩展性问题：定长64bit块头无法扩展寄存器和其他描述信息。
2. V0.3X指令编码问题：块头块体不共用一套编码，造成硬件和编译器实现复杂度过高。
3. V0.3X codesize问题：块头导致的指令膨胀过大，与ARM相比膨胀约50%。

## 版本更新总体说明

- **架构状态/ABI变动**

|  变更内容                      |  原因                |
|------------------------------|-------------------------------|
| 1. 第一层架构寄存器UL_GPR增加至24个  | 优化寄存器分配算法，降低块指令的Spill开销，提升性能。 |
| 2. 第二层架构寄存器中删除LL_GPR  |   LL_GPR会显著增加硬件重命名复杂度。  |
| 3. 第二层架构寄存器中T寄存器索引距离减少至4 |  T#5-T#8使用率较低，且占用硬件ROB空间。  |
| 4. 第二层架构寄存器中增加U相对索引寄存器，索引距离为1-4 | 使能长距离相对索引，大幅降低copy指令数。  |
| 5. 修改寄存器映射关系：R1映射到SP, R2至R9 映射到 A0至A7, R10映射到RA  | 适配新版本的fentry,fexit,fret等模板块设计。 |

- **块指令形态**

新增一体块和分离块的架构定义。一体块可大幅消除块头开销，对于小块可以降低块头的信息冗余。

注：0.40版本仅支持一体块定义

- **块头编码重构**

块头编码完全重构，拆成多个16bit和32bit的指令描述符组合的块头。通过将64bit定长块头拆成多个块头指令组合的形式可以有效降低程序代码量并且增强块头的扩展能力。

| 块头指令  |  列表  |
|--------|-----------|
| 新增16bit块头指令 | 通用块的C.BSTART, 热点标量块的C.BSTART, C.LBREF, C.BSTOP  |
| 新增32bit块头指令 | 通用块的BSTART, 热点标量块的BSTART, LBREF, BATTR, BSTOP  |
| 模板指令改为32bit编码 | MCOPY, MSET, FENTRY, FEXIT, FRET.RA, FRET.STK (MPUSH, MPOP, BLBAR当前版本暂不支持)  |

- **删除的块指令**

删除Inline Block和BSBAR块。Inline指令设计不够高效，绝大多数的场景下Inline块内只有1-2条微指令。

- **微指令**

微指令编码完全重构，现有指令的定义不变，编码全部进行调整。微指令编码空间和块头编码空间共享，有利于反汇编及硬件解码器实现，使执行环境更安全。

升级至0.4版本后微指令编码方式调整如下：

1. 由于块头块体共同编码，因此调整原32位指令低7位Opcode域。
2. 删除LL_GPR后，输入输出寄存器域改为5bit统一编码。
3. 扩展add等指令shamt域用于支持更大范围的偏移。
4. 无寄存器输出指令不占用T寄存器槽位，减少寄存器分配。
5. 取消三输入指令的限制，对于特定的三输入指令，不再要求其中一个输入固定为块内T寄存器。
6. 位域插入指令bfi的M,N参数改为以字节为粒度进行编码。
7. cmp和setc类指令增加SrcRType域，用于扩展指令实现。
8. 由于编码格式的限制，浮点指令FCVT拆分为多条指令。
9. 跟随ABI变动，指令输入输出寄存器编码方式有所调整。

当前版本增加或删除微指令列表如下：

| 指令列表  |  原因   |
|--------|-----------|
| **新增32bit指令** |  |
| 1. addpc <br>2. cmp.and, cmp.or, cmp.andi, cmp.ori<br>3. setc.and, setc.or, setc.andi, setc.ori, setc.tgt<br>4. bic, bis, ccatw<br>5. madd, maddw<br>6. tc.iva, tc.iall<br>7. lr.b, lr.h, sc.b, sc.h, swapb, swaph  | 1. 基于编译器和模型团队的codesize分析，新增指令用于降低程序代码量。<br>2. tc.iva, tc.iall为操作系统OS内核开发需求。 |
| **新增16bit指令** |  |
| 1 movr, movi<br>2. c.add, c.sub, c.and, c.or<br>3. c.addi, c.slli, c.srli<br>4. c.setc.eq, c.setc.ne<br>5. c.lwi, c.ldi, c.swi, c.sdi<br>6. c.cmp.eqi, c.cmp.nei<br>7. sext.b, sext.h, sext.w, zext.b, zext.h, zext.w<br>8. c.ssrget, c.addpc, c.addtpc | 增加16bit 长度C扩展指令用于降低Codesize并提升性能。 |
| **命名调整指令** |  |
| 1. concat指令命名改为ccat<br>2. rev指令命名改为rev64 | 规范指令命名  |
| **当前版本暂不实现指令** | |
| 1. mulh, mulhu<br>2. load.a, load.ua类<br>3. addc, subc<br>4. casw, casd<br>5. 系统块内gqm类与Cache 维护指令 | 当前版本不支持双输出指令，gqm等系统指令定待后序版本确定 |
| **删除的微指令** | |
| 1. addbpcf, addbpcn <br>2. setc.trap, setc.msg <br>3. ssrcrlt <br>4. tlbget, tlbset, tlbi | 基于0.40版本的架构变动，部分指令不再使用，因此删除。|

## 变更详细介绍

### 一、架构状态变更

第一层架构寄存器UL_GPR增加至24个：R0至R23，增加GPR数量后在SPEC测试程序中带来的动态指令数收益如下图所示：

![spec](../figs/isa/version/spec.png)

由上图可知，增加8个GPR可以有效降低在SPEC测试程序中的动态指令数，并且块内使用两组相对索引寄存器带来的受益更高。

第二层架构寄存器修改：

1. 删除块内私有的LL_GPR；
2. 相对索引T寄存器数量减少至4个，每条指令可以索引前序4条输出至T队列的指令结果；
3. 增加4个相对索引U寄存器，每条指令可以索引前序4条输出至U队列的指令结果。

| 寄存器名 | 寄存器别名 | 解释 |
|-----------|-----------|--------|
| TR1 | T#1 | 前序第一条输出至T队列的指令结果 |
| TR2 | T#2 | 前序第二条输出至T队列的指令结果 |
| TR3 | T#3 | 前序第三条输出至T队列的指令结果 |
| TR4 | T#4 | 前序第四条输出至T队列的指令结果 |
| UR1 | U#1 | 前序第一条输出至U队列的指令结果 |
| UR2 | U#2 | 前序第二条输出至U队列的指令结果 |
| UR3 | U#3 | 前序第三条输出至U队列的指令结果 |
| UR4 | U#4 | 前序第四条输出至U队列的指令结果 |

T寄存器和U寄存器独立索引，示例如下：

```asm
ldi [a0, 0], ->t         # inst0，指令结果写到T队列
ldi [a1, 0], ->t         # inst1，指令结果写到T队列
ldi [a0, 8], ->u         # inst3，指令结果写到U队列
ldi [a1, 8], ->u         # inst4，指令结果写到U队列
addi  t#2, t#1, ->t      # 索引inst0和inst1的指令结果
sd t#1，[a2, 0]          # 指令无寄存器输出
addi u#2 u#1, ->u        # 索引inst3和inst4的指令结果
sd u#1，[a2, 8]          # 指令无寄存器输出
```
指令输出的汇编示例：

- 指令无寄存器输出：`Opcode SrcL, SrcR`
- 指令输出到T队列：`Opcode SrcL, SrcR, ->t`
- 指令输出到U队列：`Opcode SrcL, SrcR, ->u`
- 指令输出到第一层架构寄存器：`Opcode SrcL, SrcR, =>a0`

### 二、 指令编码空间变更

指令编码空间和特征如下：

块头块体统一编码, 编码长度使用16bit和32bit两种。

![编码空间](../figs/isa/arch/encoding.png)

符号说明：

- Size：指令字长，0 : 16bit指令；1 : 32bit指令。
- L/Layer：指令层级，0 : 块头指令编码空间；1-3 ：微指令编码空间
- Opcode：指令操作码

组合空间分布如下：

- Size=0 : 16bit指令
    - layer=0 : 16bit块头指令
    - layer=1 : 16bit块体微指令
- Size=1 : 32bit指令
    - layer=0 : 32bit块头指令
    - layer=1-3 : 32bit块体微指令

### 三、 块头指令变更

块头编码完全重构，引入了变长块头的概念与设计，拆成多个16bit和32bit的指令描述符组合的块头。

所谓变长块头编码，通俗的讲就是将块头中包含的全量的信息描述域拆分开来，部分域段再进行组合成为多条块描述指令，并且可以是16bit长或32bit长。因此新版本中一个块头指令是由多个16或32bit块描述符指令组合而成，块头的总编码长度是不固定的，称为变长块头。

对于一体块而言，**块头描述指令必须在块体指令前**，解码到块体指令则表示当前块头描述指令结束。

1. **新增BSTART指令**

BSTART指令语义：提交前一个块指令，并且开启当前块。BSTART是一个块指令块头中必须存在的指令，也是块指令中第一条指令。 

当前版本设计了两种BSTART指令，一种是支持全量的块类型和跳转类型的指令，用于通用场景。另一种是主要用于偏移类跳转且块类型默认为标量块的指令，也称为热点标量块。

16bit BSTART：

![v0.40bstart16](../figs/isa/version/v0.40bstart16.png)

32bit BSTART：

![v0.40bstart32](../figs/isa/version/v0.40bstart32.png)

- BlockType域：用于编码块类型。
- DCP位：一体块与分离块标志位：0代表一体块，1代表分离块（当前版本固定编码为0）
- BrType域：用于编码跳转类型：**0为无效编码**。
- PayLoad：当跳转方式为偏移类跳转时，该域用于编码跳转距离；其他跳转类型，暂时保留。 

2. 新增BATTR指令

BATTR块用于描述一个块的属性信息。编码如下：

![v0.40battr](../figs/isa/version/v0.40battr.png)

- T：块提交陷出标记 T-trap, 置为1: 表示当前块指令在提交后，产生一个陷出。
- R：块指令接力标记 R-relay，置为1：当前块的私有寄存器继承给后一个块指令，否则不继承。
- F：异常普通处理标记 F-fixup, 部分异常低特权级处理。
- H：超级块标记 H-hyper，置为1：表示支持块内跳转指令；否则不支持。
- atom：原子块标记位，指示当前块为原子块。
- far：发送当前块至多核远端执行。
- aq/rl：标识块指令之间的fence属性。

3. 新增LBREF指令

LBREF块只用于表达块间跳转偏移。该指令有16bit和32bit两种编码格式。

![lbref-0.40](../figs/isa/version/lbref-0.40.png)

跳转偏移引用指令LBREF。其编码中BNextOffset域用于与后面BSTART/C.BSTART指令中的BNextOffset拼接，组合成一个完整的BNextOffset域。

LBREF指令说明：

- 在存储逻辑上，一个块的lbref指令总是在bstart指令前。
- 一个块如果包含lbref指令，那么硬件上会将lbref作为本块的起始指令。
- 16bit和32bit的bstart与lbref指令可以自由组合使用，例如：`c.lbref + c.bstart`，`c.lbref + bstart`，`lbref + c.bstart`，`lbref + bstart`。

4. 新增BSTOP指令

最低位是0或者1，其余位编码全0为无效invalid指令，同时也作为BSTOP指令，可用于提交当前块指令。

![bstop](../figs/isa/version/bstop-0.40.png)

5. 新增模板块

引入模板块的设计用于降低CodeSize以及提升性能，模板块指令定义为一种块起始指令，用于提交前一个块指令并开启当前块。每种模板块的Opcode作为一种特殊的“BSTART”，模板块块头中描述块指令的输入输出以及其他执行要求。

![v0.40templateblock](../figs/isa/version/v0.40templateblock.png)

指令设计说明：

- **MCOPY/MSET指令**：为三寄存器输入指令，三种输入分别使用第一层架构寄存器RegSrc0，RegSrc1和RegSrc2进行传递，其中：

| 内存拷贝指令MCOPY | 内存赋值指令MSET  |
|-----------------|------------------------|
|  RegSrc0：用于传递目的内存地址 |  RegSrc0：用于传递目的内存地址 |
|  RegSrc1：用于传递源内存地址   |  RegSrc1：用来传递源数据      |
|  RegSrc2：用于传递拷贝字节数   |  RegSrc2：用于传递赋值字节数   | 

- **FENTRY指令**：该指令用于函数入口开栈，**隐含栈指针寄存器sp的输入/输出信息**。
- **FEXIT，FRET.RA，FRET.STK指令**：这三条指令用于函数出口的收栈操作，同时也**隐含着栈指针寄存器sp的输入/输出信息**。

栈空间大小编码于无符号立即数unsigned imm[14:3]中，以8 Byte为单位。压栈的寄存器信息通过SrcBegin和SrcEnd表达，SrcBegin和SrcEnd表示第一层寄存器R0-R23中一段连续的寄存器。例如将R2,R3,R4,R5,R6压栈，那么SrcBegin编码为R2，SrcEnd编码为R6。

三条收栈指令分别对应函数出口的不同场景，具体：

- FEXIT指令用于函数结尾是个函数调用（包括函数指针调用）的使用场景，跳转类型默认为Fall。<br>
- FRET.RA指令用于函数结尾正常返回且函数内部无子函数的使用场景，返回地址通过直接读取Ra寄存器获得，跳转类型默认为Return。<br>
- FRET.STK指令用于函数结尾正常返回且函数内部有子函数的使用场景，返回地址需要从栈上Load回来，跳转类型默认为Return。

汇编格式如下：

| 模板指令 | 汇编格式 | 默认跳转方式 | 注意事项 |
|-----------|-----------|-----------|-----------|
| MCOPY | b.mcopy [RegSrc0, RegSrc1, RegSrc2] | 顺延Fall Through | 源和目的地址不重叠 |
| MSET | b.mset [RegSrc0, RegSrc1, RegSrc2] | 顺延Fall Through | 无 |
| FENTRY | f.entry [RegSrc0 ~ RegSrcn], sp!, uimm | 顺延Fall Through | 隐含sp寄存器作为输入和输出  |
| FEXIT | f.exit [RegDst0 ~ RegDstn], sp!, uimm | 顺延Fall Through | 隐含sp寄存器作为输入和输出  |
| FRET.RA | f.ret.ra [RegDst0 ~ RegDstn], sp!, uimm | 返回Return |  隐含sp寄存器作为输入和输出  |
| FRET.STK | f.ret.stk [RegDst0 ~ RegDstn], sp!, uimm | 返回Return |  隐含sp寄存器作为输入和输出  |

6. 删除块指令

删除Inline Block和BSBAR块。<br>

Inline指令设计不够高效，绝大多数的场景下Inline块内只有1-2条微指令。因此删除原Inline设计并将块结构形式改成一体块（动态Inline块）

### 四、微指令变更

基于编译器团队主导的codesize分析总结与模型团队的分析数据，新增以下指令用于缩减 与 其他架构 codesize差距。

1. 增加movr/movi指令

指令编码如下：<br>

![v0.40movr&movi](../figs/isa/version/v0.40movr&movi.png)

Movr：寄存器移动，将源寄存器值移动到目的寄存器, SrcL和RegDst可重复。
Movi：立即数移动，将[-16,15]范围内的立即数移动至寄存器R1-R23或T/U队列。

2. 增加C.ADDPC指令

c.addpc指令用于CALL类型的块内记录返回地址。c.addpc是movi的别名指令, 指令编码如下：<br>

![v0.40c.adddpc](../figs/isa/version/v0.40c.adddpc.png)

c.addpc指令的输出固定为RA寄存器，立即数域作为有符号立即数。

3. 增加cmp和setc部分指令

增加cmp.{and, or, andi, ori} 和setc.{and, or, andi, ori}指令<br>

![v0.40cmp&setc-1](../figs/isa/version/v0.40cmp&setc-1.png)

cmp.and：RegDst = SrcL & SrcR<br>
cmp.or：RegDst = SrcL | SrcR<br>

![v0.40cmp&setc-2](../figs/isa/version/v0.40cmp&setc-2.png)

cmp.andi：RegDst = SrcL & simm12<br>
cmp.ori：RegDst = SrcL | simm12<br>

![v0.40cmp&setc-3](../figs/isa/version/v0.40cmp&setc-3.png)

setc.and：setc.flag = SrcL & SrcR<br>
setc.or：setc.flag = SrcL | SrcR<br>

![v0.40cmp&setc-4](../figs/isa/version/v0.40cmp&setc-4.png)

cmp.andi：setc.flag = SrcL & simm<br>
cmp.ori：setc.flag = SrcL | simm<br>

4. 增加BIC/BIS指令

大量场景下，我们需要将数据的低3位，低4位或者低5位清零，原有方法是使用左移后再右移(或多条指令组合方式实现)，增加BIC指令后可以使用一条指令实现。

![v0.40bic&bis](../figs/isa/version/v0.40bic&bis.png)

以下是编译器团队对LinxISA与ARM codesize对比分析总结中提供的对比结果：<br>

![v0.40bic&bisCause](../figs/isa/version/v0.40bic&bisCause.png)

5. 增加MADD/MADDW指令和MIADD/MISUB指令

增加乘加指令MADD/MADDW与带立即数乘加乘减指令。<br>

![v0.40madd&maddw](../figs/isa/version/v0.40madd&maddw.png)

| 指令  | 操作  |
|---------|------------|
| MADD  | RegDst = SrcD+SrcL*SrcR  |
| MADDW | RegDst = SignExtend((SrcD+SrcL*SrcR)[31:0])  |
| MIADD | RegDst = SrcL + SrcR * uimm  |
| MISUB | RegDst = SrcL - SrcR * uimm  |

以下是编译器团队对LinxISA与ARM codesize分析总结中提供的对比结果：<br>

![v0.40madd&maddwCause](../figs/isa/version/v0.40madd&maddwCause.png)

6. 增加CCATW指令

![v0.40ccatw](../figs/isa/version/v0.40ccatw.png)

语义：两源寄存器的低32bit拼接并循环移位，结果的低32bit和高32bit分别符号扩展后写到RegDst和T。

7. 增加TC.IVA/TC.IALL指令

增加该指令是为了满足操作系统OS内核开发需求, 编码如下：

![v0.40tc.iva&tc.iall](../figs/isa/version/v0.40tc.iva&tc.iall.png)

TC.IVA指令语义：将内存地址SrcL所在的缓存行副本从 Translation Cache 中无效化。<br>
TC.IALL指令语义：将Translation Cache 中所由的缓存行副本无效化。

8. 增加LR/SC/SWAP类指令

增加LR/SC/SWAP以字节和半字为单位操作的指令.<br>

![v0.40lr&sc&swap](../figs/isa/version/v0.40lr&sc&swap.png)

| ATOMIC_SIZE | LR类指令 | SC类指令 | SWAP类指令 |
|---|---|---|---|
| 0 | LR.B | SC.B | SWAPB  |
| 1 | LR.H | SC.H | SWAPH  |
| 2 | LR.W | SC.W | SWAPW  |
| 3 | LR.D | SC.D | SWAPD  |

9. 增加setc.tgt和addpc指令

在32bit公共指令空间下增加setc.tgt和addpc指令的编码。<br>

![v0.40addtpc&addpc](../figs/isa/version/v0.40addtpc&addpc.png)

addpc为addtpc的别名指令，RegDst域固定编码为RA，立即数域仅高12位有效。

![v0.40setc.tgt32](../figs/isa/version/v0.40setc.tgt32.png)

setc.tgt指令的SrcR域编码为全零。

10. 增加C扩展指令

根据指令使用热度，增加以下16bit微指令，用于降低部分场景下的Codesize以及提升性能。<br>
16bit微指令属于基础指令，可使用于任意块类型的块体中。

![v0.40Cinstruction](../figs/isa/version/v0.40Cinstruction.png)

以上指令中需要特殊注意的是C.SSRGET指令，其SSRID需要独立一套编码。编解码映射关系如下：<br>

![v0.40c.ssrget-ssrid](../figs/isa/version/v0.40c.ssrget-ssrid.png)

目前仅增加了常用的TP,GP,CP寄存器编码，其他空间暂时保留。

---

### 指令编码调整

**调整1：原指令低7位Opcode域调整**

当前版本指令编码低位7bit包含三种信息：<br>

**MInst[0]**：指令长度域Size，Size=0为16bit长度指令；Size=1表示32bit长度指令。<br>
**MInst[2:1]**：指令层级域Layer，Layer=0b01和0b10属于公共指令编码空间；Layer=0b11，属于私有指令编码空间（每种块类型私有空间）。<br>
**MInst[6:3]**：指令操作码Opcode。

**调整2：输入/输出寄存器域调整**

合并以前版本中R/L和Src域，5bit共同编码。合并以前版本中G/L和RegDst域，5bit共同编码。<br>
0.3x版本：<br>

![v0.40in&outreg-1](../figs/isa/version/v0.40in&outreg-1.png)

0.4x版本：

![v0.40in&outreg-2](../figs/isa/version/v0.40in&outreg-2.png)

**调整3：扩展shamt域**

对于add/sub/and/or/xor/load类指令，扩展其shamt域至5bit，满足程序语言中对于大型的struct，地址偏移移位超过3bit的需要。

![v0.40shamt](../figs/isa/version/v0.40shamt.png)

**调整4：无寄存器输出指令**

无寄存器输出指令不占用T寄存器槽位：<br>

setc类，块内跳转类，ssrset，ssrwr，store不更新地址类，prf类，执行控制类(trap，bwe等)，Cache管理类指令 不占用T寄存器槽位。<br>

**调整5：三输入取消限制**

CSEL等三寄存器输入指令对输入寄存器无限制，最多可以是3个GPR或3个T REG或3个S REG。

![v0.40csel](../figs/isa/version/v0.40csel.png)

**调整6：标量块内的SSRGET/SSRSET指令**

为了统一编码格式，降低解码器复杂度，调整标量块内SSRGET/SSRSET指令的SSR-ID至12bit。<br>
同时，为了适配addpc指令的调整，ssrget/ssrset指令opcode域修改：4b1100 -> 4b1111

![v0.40SSRGET&SSRSET](../figs/isa/version/v0.40SSRGET&SSRSET.png)

**调整7：系统块内的SSRGET/SSRSET指令**

系统块内的SSRGET/SSRSET指令名称修改：SSRGET改为SSRRD; SSRSET改为SSRWR。

![v0.40SSRRD&SSRWR](../figs/isa/version/v0.40SSRRD&SSRWR.png)

#### 调整8：CONCAT指令

CONCAT名称改为CCAT。<br>

![v0.40ccat](../figs/isa/version/v0.40ccat.png)

#### 调整9：BFI指令

BFI改为以Byte为粒度。<br>

原指令编码比较特殊，需要单独创建一种硬件解码实现，增加解码复杂度。因此修改其粒度为BYTE，同时修改后会使得对 字符串 的处理效果非常高效。<br>
修改指令语义为：从右源寄存器截取低N个字节，替换掉左源寄存器的第M至第M+N-1字节，结果写入目的寄存器。

![v0.40bfi](../figs/isa/version/v0.40bfi.png)

**调整10：SETC.TGT指令**

SETC.TGT增加至16bit压缩指令空间下。<br>

![v0.40setc.tgt](../figs/isa/version/v0.40setc.tgt.png)

**调整11：CMP/SETC类指令**

CMP/SETC类指令增加SrcRType域。<br>

编码如下：

![v0.40cmp&setc](../figs/isa/version/v0.40cmp&setc.png)

setc.{and, or}和cmp.{and, or}指令与其他指令的SrcRType参数不完全一致，具体如下：

| SrcRType | setc.and, setc.or, cmp.and, cmp.or  | 其他setc, cmp指令  |
|----------|-------------------------------------|-------------------|
| 0 | 无格式转换  | 无格式转换 |
| 1 | 截取SrcR寄存器低32bit有符号扩展 (.sw)  | 截取SrcR寄存器低32bit有符号扩展 (.sw) |
| 2 | 截取SrcR寄存器低32bit无符号扩展 (.uw)  | 截取SrcR寄存器低32bit无符号扩展 (.uw)  | 
| 3 | 对SrcR寄存器位取反 (.not) | 无效编码 (N/A)  |

**调整12：部分SETC类指令**

SETC类带有立即数的指令立即数偏移需要左移shamt位，具体编码如下：<br>

![v0.40setc](../figs/isa/version/v0.40setc.png)

setc类指令汇编语法中立即数不表达移位。编译器会根据给的立即数进行移位编码。具体汇编如下：

![v0.40setcasm](../figs/isa/version/v0.40setcasm.png)

**调整13：除法/求余指令**

除法指令DIV类：修改为除法结果的商写到目的寄存器。<br>
求余指令REM类：修改为除法结果的余数写到目的寄存器。

**调整14：浮点指令FCVT拆分**

为了统一解码格式，降低硬件解码复杂度，对以前版本一条FCVT指令进行拆分，结果如下：<br>

![v0.40fvt-1](../figs/isa/version/v0.40fcvt-1.png)

FCVT.H/ FCVT.S/ FCVT.D指令的SrcType:  0：uw; 1：sw; 2：sl; 3：ul<br>

FCVT.UW/ FCVT.SW/ FCVT.UL/ FCVT.SL指令的SrcType:   0：n/a; 1：h; 2：s; 3：d

![v0.40fvt-2](../figs/isa/version/v0.40fcvt-2.png)

FCVT.H/ FCVT.S/ FCVT.D指令的SrcType: 0：n/a; 1：h; 2：s; 3：d

**调整15：指令输入输出编码**

升级到0.40版本后，微指令输入输出域编码方式如下：

| 编码 | 输入寄存器域 | 输出寄存器域 |
|------|-------------|-----------------|
| 0 | R0 | 无效输出 |
| 1-23  | R1-R23  |  R1-R23  |
| 24-27 | T#1-T#4  | 保留reserve |
| 28-29 | U#1-U#2  |  保留reserve |
| 30 | U#3  | U队列  |
| 31 | U#4  | T队列  |

![v0.40src&dstasm.png](../figs/isa/version/v0.40src&dstasm.png)

**调整16：删除部分指令**

基于0.40版本的架构变动，以下指令不再使用，因此删除：

**addbpcf**, **addbpcn**, **setc.trap**, **setc.msg**, **ssrcrlt**, **tlbget**, **tlbset**, **tlbi**
