# 0.42版本更新

更新日期： 2024年9月30日
对应DBOX上指令级定义版本[LinxISA Encoding-0.42](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100727107943)

## 版本更新总体说明

本次版本更新主要涵盖指令命名规范、长跳转偏移的优化、指令双或多输出编码方式等内容。

|  变更项  |  变更内容                      |  变动原因                |
|------------|------------------------------|-------------------------------|
|系统寄存器|补充系统寄存器CW,TR1,TR2|补充升级到0.4x版本后缺失的系统寄存器|
|指令变动|**块指令**：<br>&emsp;1. 调整指令命名<br>&emsp;2. 修改长跳转的实现<br>&emsp;3. SIMT块指令支持串行执行模式<br>**微指令**：<br>&emsp;1. 指令多输出表达和编码<br>&emsp;2. 补充SIMT块内reduce指令的输出寄存器位宽标识<br>&emsp;3. 合并pc.push和条件跳转指令实现<br>&emsp;4. 修改指令编码立即数域表达方式<br>&emsp;5. 增加b.cond指令<br>&emsp;6. J/JR指令的跳转偏移<br>&emsp;7. SIMT块内增加原子指令<br>&emsp;8. SIMT块内指令修改|**块指令**：<br>&emsp;1. 为了明确区分块头指令和微指令以及区分块头中块开始指令与其他描述指令<br>&emsp;2. BSTART指令的BNextOffset域可能不足以编码实际需要的跳转偏移<br>&emsp;3. 针对程序循环中不同的场景提供相应的软件接口，方便软件设计人员灵活的编写程序<br>**微指令**：<br>&emsp;1. 灵犀指令集后续需要引入的双/多输出指令<br>&emsp;3. 避免增加冗余寄存器<br>&emsp;5. 补充块内指令定义，保障功能完备性<br>&emsp;2&4&6. 持续优化指令集|


## 变更详细介绍

### 一、 系统寄存器

补充系统寄存器**CW**,**TR1**,**TR2**，这些是升级到0.4x版本后缺失的系统寄存器。

### 二、 指令变动

**块指令**

灵犀指令集中，为了明确区分块头指令和微指令以及区分块头中块开始指令与其他描述指令，本次版本对指令命名进行了如下的规范化调整：

- 块头指令统一使用大写表示；微指令统一使用小写。<br>
- 块头指令中块除了块开始指令外，其他块头描述指令统一使用”B.”作为前缀，便于汇编程序中区分块开始指令和其他块描述指令。<br>
- 编码宽度为16bit的压缩指令命名统一以“C.”作为前缀。

#### 调整1：块头指令的命名规范

一般情况下，内联块和分离块的块头指令中除了 BSTART 外，其他描述指令统一以 B. 作为前缀。具体修改如下：

![v0.42BlockHeaderName](../figs/isa/version/v0.42BlockHeaderName.png)

#### 调整2： 模板块指令命名修改

为配合块头指令命名的调整，同步对模板块指令的命名进行了修改，如下所示：

![v0.42templateName](../figs/isa/version/v0.42templateName.png)

#### 调整3： 压缩指令的命名修改

所有16位压缩指令统一以 “C.” 为前缀，涉及指令如下：

![v0.42comInsName](../figs/isa/version/v0.42comInsName.png)

#### 调整4： 修改长跳转的实现

0.42版本引入了 BSTART + B.NEXT 的编码组合方案解决BSTART指令的BNextOffset域可能不足以编码实际需要的跳转偏移的问题。具体说明如下：

其中：

- BSTART用于编码跳转偏移的低位部分，B.NEXT则编码高位部分。<br>
- 仅Opcode为4b0000 BSTART指令可以与B.NEXT组合使用，B.NEXT指令放在其他块头中则无效。
- B.NEXT编码紧跟在BSTART指令后。<br>
- EX：extend标志位，置0表示BSTART中跳转偏移是完整的(FF)，置1则不完整(HF)，需要等待后序的B.NEXT指令组成完整的跳转距离

BSTART编码结构

![v0.42bstartEncode](../figs/isa/version/v0.42bstartEncode.png)

B.NEXT编码结构，BnextOffset[41:17]用于编码跳转距离的高位部分，可与BSTART组合表达42位的跳转距离。

![v0.42B.NEXT](../figs/isa/version/v0.42B.NEXT.png)

B.NEXT 支持16位压缩版本 B.NEXT.C，可组合表达29位跳转距离。

![v0.42B.NEXT16](../figs/isa/version/v0.42B.NEXT16.png)

#### 调整5： SIMT块指令支持串行执行模式

**执行模式**

针对循环各个迭代之间的依赖关系的不同，指令集提供三种SIMT块执行模式的定义。

- BSTART.LOOP：所有lane之间完全串行执行。适用于循环各迭代间存在访存依赖的场景。<br>
- BSTART.VECT：同一个group内不同lane之间可以并行执行，不同 group之间需要串行执行。适用于循环中部分迭代间存在访存依赖的场景。<br>
- BSTART.SIMT：同一个group内不同lane之间可以并行执行，不同group之间也支持并行执行。适用于循环中所有迭代间都没有依赖的场景。

每种执行模式的示意图如下：

![v0.42ExcuteModeDiagram](../figs/isa/version/v0.42ExcuteModeDiagram.png)

**指令定义**

SIMT块指令的BSTART定义如下：

汇编语法：

```asm
C.BSTART.<LOOP, VECT, SIMT>
BSTART.<LOOP, VECT, SIMT>
```

SIMT块指令默认为FALL类型跳转。

编码格式：

![v0.42bstart](../figs/isa/version/v0.42bstart.png)

相比前面版本，增加了用于编码执行模式的Parallel Mode字段。其中：

- 0：用于编码LOOP模式<br>
- 1：用于编码VECT模式<br>
- 2：用于编码SIMT模式<br>
- 其他编码保留。

注意：

当前版本，暂时不支持V0.41版本中发布的LOOP块实现。指令集中暂时删除对应编码。原LOOP块编码如下：

![v0.42loop](../figs/isa/version/v0.42loop.png)

---

**微指令**

#### 调整6： 指令多输出和表达

针对灵犀指令集后续需要引入的双/多输出指令，我们在当前版本先确定了其编码方式并相应的调整了输出到全局寄存器UL_GPR的汇编表达。

单输出：

```asm
add SrcL，SrcR, ->t；   #输出至T队列
add SrcL，SrcR, ->u；   #输出至U队列
add SrcL，SrcR, ->Rx；  #输出至UL_GPR
```

多输出：

```asm
mulh SrcL, SrcR, ->tx2；        #输出到连续2个T队列
ld [SrcL, SrcR<<3], ->tx4；     #输出到连续4个T队列0
```

标量块内微指令寄存器输入输出编解码如下：

![v0.42in&outAsm](../figs/isa/version/v0.42in&outAsm.png)

注意：

- 只针对特定的Opcode允许多输出，其他单输出指令的输出寄存器（RegDst）域编码为24-29是未定义的，模型或硬件执行结果不可知。<br>
- 由于T和U两种clock hands的快慢指针属性不同，因此不支持一条指令既输出到T，又输出到U。<br>
- 块内写UL_GPR修改为通过“->”标识，块内指令读取该寄存器值为更新后的值。<br>
- 保留原有限制：“同一个块内每个UL_GPR只能写一次”。

#### 调整7：reduce指令

补充SIMT块内reduce指令的输出寄存器位宽标识。

#### 调整8： pc.push和条件跳转指令

SIMT块内的pc.push指令用于程序执行流出现分支（diverge）时，将汇聚点（reconverge）PC和线程掩码压栈。但是程序执行过程中判断是否发生diverge需要等待后面的条件跳转指令的结果，这样就需要增加一个寄存器用于临时保存汇聚点的PC。

为了避免增加该寄存器，决定在当前版本将pc.push和条件跳转指令合并为一种指令，具体修改如下：

**修改1：删除pc.push指令**

**修改2：更新条件跳转指令语义**

在标量语义的基础上，修改后SIMT块中条件跳转指令执行过程如下：

- 存在diverge（当前group中有效lane是否跳转的结果不一致）：将重汇聚点（reconvergence）信息和一侧分支的diverge信息存储到ControlStack寄存器中，并将另一侧分支的掩码及PC更新为current状态执行。
- 不存在diverge：对ControlStack寄存器无影响。并按照普通的条件跳转指令执行。

其中：

- 当前group的掩码记为cur_mask。
- 两个分支中，如果选择先执行的一侧分支的掩码记为cal_mask，则存储到ControlStack寄存器的save_mask=cur_mask &(~cal_mask)。
- 存在diverge的判断条件为：((cur_mask & cal_mask) != cur_mask) && ((cur_mask & ~cal_mask) != cur_mask)

汇编语法：

![v0.42pcpushasm1](../figs/isa/version/v0.42pcpushasm1.png)

其中：<br>
重汇聚点PC的计算为：rpc = tpc + rc_offset<<3<br>
跳转目标地址的计算为：br_pc = tpc + br_offset<<3

#### 调整9：增加一条b.cond指令

为了避免极端场景下，条件跳转指令的偏移量编码空间不足，增加一条B.COND指令<br>

汇编语法：

```asm
b.cond SrcP.<T>, SrcL.<T>, SrcR.<T>
```
其中：SrcP的值作为判断条件；SrcL用于存储跳转目标地址；SrcR用于存储重汇聚点PC。

指令语义：<br>
判断当前group下所有有效lane中SrcP的值：如果全为0或者全为1，则表示不存在diverge。<br>
**不存在diverge**：全为0则顺延执行，全为1则跳转。<br>
**存在diverge**：先将SrcR中的重汇聚点PC和当前Group 的mask push到CSTK寄存器中, 再push一侧分支PC和分支mask 。并将另一侧分支的mask及PC更新为current状态执行。

编码格式：

![v0.42b.cond](../figs/isa/version/v0.42b.cond.png)

该指令需要配合CMP类指令使用，见下面汇编示例：

```asm
addtpc %hi(rc_label),    ->t
addi t#1, %lo(rc_label), ->t        // 得到重汇聚点PC
addtpc %hi(br_label),    ->t
addi t#1, %lo(br_label), ->t        // 得到跳转目标PC
cmp.eq a0, t#1,          ->t
b.cond t#1, t#2, t#4
```

#### 调整10：J/JR指令的跳转偏移

J/JR指令的跳转偏移修改为以8字节为单位进行编码。

![v0.42jr](../figs/isa/version/v0.42jr.png)

SIMT块内JR指令执行语义为：跳转到tpc=SrcL+simm15<< 3

![v0.42j](../figs/isa/version/v0.42j.png)

SIMT块内J指令执行语义为：跳转到 tpc += simm25<<3

#### 调整11：SIMT块内增加原子指令

SIMT块内增加如下的原子指令用于实现原子操作和store reduce操作。

![v0.42automaticasm](../figs/isa/version/v0.42automaticasm.png)

- Load.op类指令在标量定义的基础上，增加了可选属性“.ne”，表示指令实现非原子操作。默认实现原子操作。<br>
- Store.op类指令在标量定义的基础上，增加了可选后缀“.rd”，表示该指令在所有lane内SrcL中地址是相同的，执行store reduce的操作。默认实现原子操作。

#### 调整12： SIMT块内指令修改

**补充sd和ud的汇编标识和编码**

- 对于数据类型转换指令，64bit整型数据与浮点型数据相互转换过程中需要区分有无符号；<br>
- 乘除法指令对于64bit宽整型数据的操作需要区分有无符号。

因此统一修改SIMT块指令的64位源操作数通过后缀“.sd”或“.ud”表示，并补充64bit有符号和无符号整型数据的编码。

![v0.42integerasm](../figs/isa/version/v0.42integerasm.png)

**指令调整**

SIMT块内指令操作的数据类型、位宽和有无符号可以通过操作数的后缀表示，因此对部分OP中带有符号信息的指令进行合并。<br>
其中包括：Reduce指令和乘除指令

![v0.42reduce1](../figs/isa/version/v0.42reduce1.png)

同时对reduce指令编码做了修改，修改后编码如下：

![v0.42reduce2](../figs/isa/version/v0.42reduce2.png)

指令编码保留原有的mul，div，rem编码。

**增加lbstop编码**

补充SIMT块体内结束指令编码并命名为lbstop，避免汇编器在生成二进制文件或者模型解码时存在歧义。

![v0.42lbstop](../figs/isa/version/v0.42lbstop.png)
