# 0.36版本更新

更新日期：2023年12月29日

指令编码设计文档网页版路径请见[LinxISA Encoding-0.36](https://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100298001623)

## 版本更新总体说明

|  变更项  |  变更内容                      |  变动原因                |
|------------|------------------------------|-------------------------------|
|  块头编码   |  BrTypeExtend：4bit->3bit；BlockOpcode：7bit->8bit。  |  降低解码复杂度。  |
|  标准块Standard Block  |  1. ECALL跳转块的BrTypeExtend: 4'b1011->3'b101；<br>2. ERET跳转块的BrTypeExtend: 4'b1100->3'b110。  |  块头编码统一调整，降低解码复杂度；预留reserve空间。  |
|  标准块stdlp  |  1. 新增标准块stdlp：BlockType：3'b001；<br>2. 没有bitmask（默认为全1），扩展BText/BNext Offset等字段长度；<br>3. 增加BranchHint域段；<br>4. IND和INDCALL块增加Likely BNextOffset用于跳转预测。  |  1. 扩展BText/BNext Offset等字段长度，用于降低lbref块的个数;<br>2. 增加BranchHint域段，用于分支，跳转预测增强。  |
|  标准超级块stdh  |  BlockType：3'b001 -> 3'b010。  |  保持和6188落地版本一致，stdlp块的BlockType定为3'b001，因此调整stdh块的BlockType为3'b010。  |
|  标准浮点块fp  |  Floating-point Block  |  1. 标准浮点块支持块内跳转指令；<br>2. 删除浮点超级块fph。  |  标准浮点块和浮点超级块合并为一种块，节省编码空间。  |
|  内联块Inline Block  |  BlockType：3'b110 -> 3'b101。  |  块头编码统一调整，降低解码复杂度。  |
|  模板块Template Block  |  1. BlockType：3'b111 -> 3'b110；<br>2. 增加SrcVld和DstVld域段；<br>3. BLBAR块由控制块类型调整为模板块；<br>4. mpush/mpop块头增加MemBitMask和signed imm字段。  |  1. 块头编码统一调整，降低解码复杂度。<br>2. BLBAR块本身为模板指令，因此调整为模板块。<br>3. mpush/mpop修改后用于不连续内存的push/pop，提升数据处理的效率。  |
|  复杂CISC块  |  新增5类CISC块：B.MOV，B.ADD，B.LJMP, B.COND,  B.CALL   |  仅用于预留编码空间。  |
|  系统块System Block   |  1. 块头编码去掉bitmask，用于长索引，长跳转的偏移；<br>2. 增加ECALL块和ERET块。<br>3. 系统块支持块内跳转指令，并删除系统超级块sysh。  |  1. 同标准块stdlp<br>2. 增加ECALL和ERET：为了保持和6188 1.0版本对齐。  |
|  控制块Control Block  |  1. LBREF块的BNextOffset域范围缩小至16bit；<br>2. 删除BSBAR块，StoreBarrier特性放在LBREF块头；<br>3. 移除BLBAR块，添加至模板块类型中。  |  StoreBarrier特性放在LBREF块头，可以大幅降低Codesize。  |
|  新增微指令  |  1. 新增比较跳转类微指令：setc.and和setc.or。  |  1. 统计发现Specint占比5%，为热点场景指令。使用该复合指令可有效降低Codesize。  |
|  删除指令  |  内联块微指令删除inl.lconst/inl.lconstu/inl.addbpc等指令。  |  统计有误，inl.lconst/inl.lconstu/inl.addbpc为虚假的热点指令，因此移除。 |
|  系统寄存器  |  1. 系统寄存器增加：CID（物理核ID）和SYSCNT（本地时间戳）;<br>2. 修改系统寄存器BREF的寄存器ID为0x000F；<br>3. 修改系统寄存器CYCLE的寄存器ID为0x0C00。   |  1. 产品OR需求；<br>2. 原BREF寄存器ID与添加的CID寄存器ID冲突。<br>3. 保持与6188落地版本一致。  |

## 变更详细介绍

### 1.块头编码统一调整

0.36版本中块头编码的BrTypeExtend字段由原来的4bit调整为3bit，BlockOpcode字段由原来的7bit调整为8bit。

0.35版本块头编码格式：

![header-v0.35](../figs/isa/version/header-0.35.png)

0.36版本块头编码格式：

![header-v0.36](../figs/isa/version/header-0.36.png)

### 2.标准块std

适配块头编码的统一调整，标准块中ECALL和ERET块的BrTypeExtend编码修改如下：

ECALL块：**4'b1011** 修改为 **3'b101**; ERET块： **4'b1100** 修改为 **3'b110**

0.35版本ECALL和ERET块编码：

![std-v0.35](../figs/isa/version/std-0.35.png)

0.36版本ECALL和ERET块编码：

![std-v0.36](../figs/isa/version/std-0.36.png)

### 3.新增标准块stdlp

标准块stdlp(Standard Block with Long Pointer)：标准块的块头块体分离，没有bitmask（默认bitmask为全1），主要用于跳转和标识块指令的范围。

- 块内微指令使用32bit编码空间。
- BTextStartOffset范围扩展至**26bit**，BNextOffset范围扩展至**25bit**，BEndOffset扩展至**10bit**。
- 其中IND和INDCALL两种跳转类型的块增加LikelyBNextOffset域，范围扩展至22bit，用于跳转预测。
- 增加BranchHint域，用于跳转信息提示，具体定义见下面表格说明。

![stdlp-v0.36](../figs/isa/version/stdlp-0.36.png)

块头BranchHint域段说明

![branchHint](../figs/isa/version/branchHint.png)

### 4.标准超级块stdh

为了保持和6188-1.0版本一致，stdlp块的BlockType定为3'b001，因此调整stdh块的BlockType为**3'b010**。

0.35版本stdh块编码：

![stdh-v0.35](../figs/isa/version/stdh-0.35.png)

0.36版本stdh块编码：

![stdh-v0.36](../figs/isa/version/stdh-0.36.png)

### 5.标准浮点块

为了节省块指令编码空间，在本版本我们选择删除标准浮点超级块fph，留下标准浮点块fp。同时定义标准浮点块内支持块内跳转指令，即在块引擎的功能上，当前版本的fp块等价于上个版本的fph块，但是仍然使用上个版本fp块的编码空间。

0.36版本fp块编码：

![fp-0.36](../figs/isa/version/fp-0.36.png)

### 6.内联块修改

内联块块指令的BlockType由**3'b110**调整为**3'b101**。

0.36版本内联块块头编码：

![inline-0.36](../figs/isa/version/inline-0.36.png)

### 7.模板块调整

- 模板块编码统一修改：
    * 模板块块指令的BlockType由3'b111 调整为 3'b110。
    * 适配块头编码统一调整：BrTypeExtend域（header[8:5]->header[7:5]）由4bit改为3bit。
    * 增加SrcVld和DstVld域段，用于快速判断块间依赖，降低硬件解码复杂度。
- FENTRY,FEXIT,FTEXIT块：增加SrcVld和DstVld的编码空间后位置与立即数高位unsigned imm[18:11]冲突，所以调整了立即数高位的位置。
- FTEXIT块的跳转类型调整为IND(Indirect)类型（3’b100 -> 3’b010），本修改用于提升硬件RAS跳转预测的准确度。
- BLBAR块由控制块类型改为模板块：
    * BlockOpcode从**4'b0001**改为**4'b0010**。
    * 统一增加SrcVld和DstVld的编码空间后，调整了prefetch_count/offset/prefetch Model等字段的编码位置。
    * MPUSH/MPOP增加MemBitMask字段用于不连续内存的push和pop；增加了Store/Load Offset（即igned imm）字段，用于地址计算的偏移。

0.35版本模板块编码：

![memblock-v0.35](../figs/isa/version/memblock-0.35.png)

0.36版本模板块编码：

![memblock-v0.36](../figs/isa/version/memblock-0.36.png)

补充修改：

#### 模板块FEXIT调整

FEXIT修改后的使用场景

场景1：函数结尾是个函数调用 f.exit+bnext.direct
```c
extern int add(int, int);
int f1(int a, int b) { 
return add(a, b);
}
```
场景2：函数结尾是个函数指针调用 f.exit+bnext.indirect
```c
extern int add(int, int); 
extern int sub(int, int); 
int f2(int a, int b, int cond) {
int (*functionPtr)(int, int);
functionPtr = cond > 0 ? add : sub;
return functionPtr(a, b); 
}
```
FEXIT指令编码调整

跳转类型由Return改为Fall，BrTypeExtend域编码对应改为3’b001。

原编码：

![fexit-0.35](../figs/isa/version/fexit-0.35.png)

更新后编码:
 
![fexit-0.36](../figs/isa/version/fexit-0.36.png)

修改FEXIT块展开的微指令序列

跳转类型由原来的Return修改为Fall类型，因此块内不需要设置CARG.TGT，即删除块内展开的setc.tgt指令。

以块指令 f.exit [ra, s0, s1, s2, s3, s4, s5], sp!, 144展开的微指令序列为示例：
```asm
addi sp, 144, => sp
ldi [sp, 136], => ra
setc.tgt  t#1 ------->去掉该指令
ldi [sp, 128], => s0
ldi [sp, 120], => s1
ldi [sp, 112], => s2
ldi [sp, 104], => s3
ldi [sp,  96], => s4
ldi [sp,  88], => s5
```

二. 模板块FTEXIT的调整

FTEXIT指令名称改为**FRET**，汇编标识为`f.ret`。

FRET(FTEXIT)调整后用于函数结尾正常return的场景：

场景1：函数结尾正常ret，且函数内部无子函数，f.ret(RA直接读)
```c
extern int symbol; 
int f3() { 
return symbol; 
}
```
场景2：函数结尾正常ret，且函数内部有子函数，f.ret(RA从栈上load)
```c
#include "stdio.h"
extern int symbol; 
int f4(int a, int b) {
printf("Linx\n"); 
return symbol;
}
```

FRET(FTEXIT)编码调整

* FRET块跳转类型由IND（indirect）改为RETURN，BrTypeExtend域编码改为3’b100。
* RegRet域段默认编码为4’b0000(对应Ra/R0寄存器)
* srcvld[1]修改为可编码的：编码为1，表示指令输入包含Ra寄存器；编码为0，表示指令输入不包含Ra寄存器。

![fret-0.35](../figs/isa/version/fret-0.35.png)

更新后编码:
 
![fret-0.36](../figs/isa/version/fret-0.36.png)

3. 汇编语法的修改

原汇编格式：`f.texit [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, RegRet, uimm19`
修改后的汇编格式：`f.ret [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, <Ra>, uimm19`

汇编格式中<Ra> : 表示Ra是否作为块指令输入是可选择的。即：

`f.ret [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, Ra, uimm19` 表示指令输入包括RegPtr和Ra寄存器，返回地址是直接读Ra寄存器获取的。
`f.ret [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, uimm19` 表示指令输入只有RegPtr寄存器，返回地址是从栈上load回来的。

FRET块微指令展开序列的调整

如果header.vld标记为1，则表示直接读Ra寄存器值作为返回地址。对应的微指令展开序列以块指令 `f.ret [s0, s1, s2], sp!, ra, 24` 为例：
```asm
setc.tgt ra
addi sp, 24, => sp
ldi [sp, 16], => s0
ldi [sp,  8], => s1
ldi [sp,  0], => s2
```
如果header.vld标记为0，则表示指令输入不包含Ra，返回地址需要从栈上load回来（此时bsetmask bit[0]需要置位）。
对应的微指令展开序列以块指令 `f.ret [ra, s0, s1, s2], sp!, 32` 为例：
```asm
addi sp, 32, => sp
ldi [sp, 24], => ra
setc.tgt t#1
ldi [sp, 16], => s0
ldi [sp,  8], => s1
ldi [sp,  0], => s2
```

模板块修改后的编码

![TEMLP](../figs/isa/version/tempb-0.36.png)

### 8.新增复杂CISC块

新增的CISC块BlockType使用**3'b110**编码空间，与模板块共用此空间。

![cisc-v0.36](../figs/isa/version/cisc-0.36.png)

### 9. 系统块修改

1. 系统块指令增加ECALL和ERET两种跳转类型块，其中ECALL块用于程序结束。
2. 系统块头编码去掉bitmask，增加长索引，长跳转偏移的编码空间。
3. 系统块块头增加BranchHint域，定义同前面标准块stdlp内描述。
4. 删除了系统超级块sysh

注：系统块不支持除FALL类型以外的块间跳转，但支持块内跳转（访问系统寄存器，自旋锁，CMO指令若需要跳转指令的场景可使用块内跳转）。

![sys-v0.36](../figs/isa/version/sys-0.36.png)

### 10.控制块编码调整

0.33版本为了降低硬件Load/Store冲突，在控制块类型中增加了BSBAR块。这样所有包含store指令的块前都需要增加BSBAR块，如果该块的跳转偏移或索引偏移不够，还需要在块前增加LBREF块来存放额外的偏移，这样就造成了code size的膨胀。

因此在0.36版本，我们删了BSBAR块指令的编码，保留了其特性并将BSBAR的特性放在LBREF块头上。LBREF具体修改如下：

1. 添加了原BSBAR块头的store_count和SpecType字段（分别使用空间Header[15:10]和Header[9:8]）
2. 缩小了BNextOffset字段的空间，由原来的23bit缩小至**16bit**。

更新前编码：

![LBREF-v0.35](../figs/isa/version/LBREF-0.35.png)

更新后编码：

![LBREF-v0.36](../figs/isa/version/LBREF-0.36.png)

### 11.新增微指令

增加一条系统块指令[DC.ZVA](../isa/inst/misa_s/DC.ZVA.md)，执行对cacheline清零操作。

### 12.删除指令

0.35版本更新并发布了内联块及其支持的120多条微指令。

但在后续的验证中，发现i**nl.lconst**, **inl.lconstu**, **inl.addbpc**为虚假的热点指令，同时硬件对这几条指令的处理相对比较复杂，因此在当前版本移除这三条指令。

### 13.系统寄存器的变更

- 为了满足产品OR需求，增加两个系统寄存器：
    * CID（物理核ID）——SSR ID为**0x0030**
    * SYSCNT（本地时间戳）——SSR ID为**0x0C01**
- 修改原有寄存器ID：
    * 原BREF寄存器与新增CID寄存器的SSR ID冲突，为了与6188落地版本保持一致，修改BREF寄存器的ID为0x000F。
    * 为了与6188落地版本保持一致，修改CYCLE寄存器的ID为**0x0C00**。
