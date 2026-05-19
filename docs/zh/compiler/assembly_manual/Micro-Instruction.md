# 微指令
在灵犀指令集的架构定义中块指令的块体是由一系列的微指令组成，来完成具体的计算任务。微指令的汇编指令可能为如下所示形式。

```
Opcode                                                      
Opcode Operand0 
Opcode Operand0,Operand1
Opcode Operand0,Operand1,Operand2
Opcode Operand0,->{UL_GPR, LL_GPR}
Opcode Operand0,Operand1,->{UL_GPR, LL_GPR}
Opcode Operand0,Operand1,Operand2,->{UL_GPR, LL_GPR}
```

1. 微指令在具体计算时可能会有输入并且输出计算结果。在写Operand操作对象时顺序为先左源操作对象，右源操作对象，然后再输出。后文中Operand0为左源操作对象，Operand1为右源操作对象。<br>
2. 微指令的输入可能是寄存器，标签，立即数。如果输入是寄存器，可能是LL_GPR以及UL_GPR，支持使用zero代表一个值恒为0的寄存器操作数。对于系统寄存器，比如访问ebstatep(架构状态基址寄存器), tp(线程私有变量基址寄存器), gp(静态全局变量基址寄存器)等，微指令访问用系统寄存器ID。具体的寄存器操作数名字可以参见[架构和寄存器](./Architecture_Register.md)这一章节，系统寄存器的ID列表可以参见[系统寄存器](../../isa/register/ssr/ssrintro.md)这一章节。<br>
3. 微指令可能无输出，如有输出，则只能是寄存器，可能输出到{UL_GPR， LL_GPR} <br>

   - 加上`->`表明微指令有输出，可以输出到UL_GPR或者是LL_GPR <br>
   - 输出到zero寄存器，指令执行结果不起效用。<br>
   - 缺省表明无输出。<br>

下表列出了寄存器操作数的输入和输出格式：

| 输入寄存器操作数   | 输出寄存器操作数      |
|--------------------|-----------------------|
| r0  or zero        |  r0  or zero   |
| r1  or sp          |  r1  or sp     |
| r2  or a0          |  r2  or a0     |
| r3  or a1          |  r3  or a1     |
| r4  or a2          |  r4  or a2     |
| r5  or a3          |  r5  or a3     |
| r6  or a4          |  r6  or a4     |
| r7  or a5          |  r7  or a5     |
| r8  or a6          |  r8  or a6     |
| r9  or a7          |  r9  or a7     |
| r10 or ra          |  r10 or ra     |
| r11 or fp(s0)      |  r11 or fp(s0) |
| r12 or s1          |  r12 or s1     |
| r13 or s2          |  r13 or s2     |
| r14 or s3          |  r14 or s3     |
| r15 or s4          |  r15 or s4     |
| r16 or s5          |  r16 or s5     |
| r17 or s6          |  r17 or s6     |
| r18 or s7          |  r18 or s7     |
| r19 or s8          |  r19 or s8     |
| r20 or x0          |  r20 or x0     |
| r21 or x1          |  r21 or x1     |
| r22 or x2          |  r22 or x2     |
| r23 or x3          |  r23 or x3     |
| t#1~t#4            |  t             |
| u#1~u#4            |  u             |
| LB0~LB2            |  LB0~LB2       |
| LC0~LC2            |  LC0~LC2       |

**Note**：

对于LB0~LB2，LC0~LC2这些系统寄存器

- 非PAR块中需要用ssrget/ssrset才能访问。
- PAR块中，可以用SIMT块的私有微指令直接访问。
- 当前版本微指令均不支持多输出。

## 微指令输出规范：

   - 微指令的Opcode决定了该微指令是否有输出
   - 有输出的微指令输出部分不可缺省，否则汇编器会报指令格式错误

## Opcode的识别
对于Opcode的识别，首先确定其所在的块类型，进而通过对Opcode进行扩展来区分不同的指令，不同精度的浮点指令，以及原子指令的不同操作等。

- 在Opcode后面加上`w`:Opcode{w}表明进行低32bit有符号扩展<br>
- 在Opcode后面加上`u`:Opcode{u}表明进行无符号操作<br>
- 在Opcode后面加上`i`:Opcode{i}表明右源操作对象为立即数<br>
- 在Opcode后面加上`{.eq, .ne, .lt, .ge, .ltu, .geu, .and, .or}`：Opcode{.eq, .ne, .lt, .ge, .ltu, .geu, .and, .or}来表明判断成立的条件，`.eq`表示相等则判断成立，`.ne`表示不相等则判断成立，`.lt`表示有符号左源小于有符号右源则条件成立, `ge`表示有符号左源大于有符号右源则条件成立。在`.lt`和`.ge`的基础上加上`u`表明做无符号比较，`.and`和`.or`分别表示逻辑与和逻辑或，`i`表明右源操作对象为立即数的比较<br>
- 在Opcode前面加上`c.`:c.Opcode表明该指令为压缩指令，编码长度为16bit
- 浮点精度:Opcode{.fd, .fs, .fh, fb}, `.fd`代表64bit双精度浮点类型, `.fs`代表32bit单精度浮点类型, `.fh`代表16bit半精度浮点类型，`.fb`代表8bit的低精度浮点类型，仅限于浮点指令<br>
- 原子操作:Opcode{.aq, .rl, .aqrl}, `.aq`代表Acquire, `.rl`代表Release, `.aqrl`代表AcquireRelease, 仅限原子指令<br>

## Operand操作
支持对Operand的移位，地址计算，取址，算术操作，逻辑操作等操作

- Operand的类型为寄存器时，支持如下操作：<br>
    - 算术操作`Operand{.sw, .uw, .neg}` 仅限对寄存器进行， `sw`表示截取该操作数的低32bit做有符号扩展，`uw`表示截取该操作数的低32bit做无符号扩展，`neg`表示对该操作数位取反加1。<br>
    - 逻辑操作`Operand{.sw, .uw, .not}`，仅限对寄存器进行 `.not`表示对该操作数取反。<br>
    - 移位操作：`Operand1<<shamt`, 对Operand1左移shamt位。 <br>
    
- Operand为立即数和标签时，可支持常量值和立即数的取值操作，仅限整数计算类指令,访存指令,常量类指令: <br>
    - 使用绝对值：`%hi(表达式)`表示获得表达式计算结果的高20bit, `%lo(表达式)`表示获得表达式计算结果的低12bit。<br>
    - 使用相对TPC值：`%tpcrel_hi(symbol)`表示获得symbol地址相对于当前TPC的高20bit, `%got_tpcrel_hi(symbol)`表示获得symbol在GOT表上的表项地址相对于当前TPC的高20bit’,`%tpcrel_lo(label)`需要获得高位symbol地址相对于label地址的低12bit。<br>
    - 使用相对Thread Pointer的值：`%tprel_hi`表示获得TLS变量相对于Thead Pointer寄存器的高20bit，`%tprel_lo`表示获得TLS变量相对于Thead Pointer寄存器的低12bit。<br>
    - 使用相对Global Pointer的值：`%gprel_hi`表示获得全局变量相对于Global Pointer寄存器的高20bit，`gprel_lo`表示获得全局变量相对于Global Pointer寄存器的低12bit。

- 地址计算操作：`[Operand0]`或者`[Operand0,Operand1]`, 仅限对寄存器或立即数Operand做地址计算， Operand0是寄存器，Operand1可以为寄存器或立即数, 详见访存指令 <br>

可以对同一个Operand进行多个操作，如`[Operand1, Operand2.sw<<shamt]` <br>

## 寄存器类型的operand扩展设计
寄存器类型Operand增加位宽指示的设计，其目的是为了给硬件提示，从而提升SIMT块中寄存器资源的利用率。使用方式如下：

- 输出操作数标识：Operand{.b, .h, .w, .d}，`.b, .h, .w, .d`分别表示寄存器操作数宽度为8bit，16bit，32bit，64bit。该扩展设计可以叠加其他Operand的基础操作使用，比如移位，根据具体指令确定。
- 输入操作数标识：Operand{.fd, .fs, .fh, .fb, .bf, .flb, .d, .uw, .uh, .ub, .sw, .sh, .sb}，其中`.fd, .fs, .fh, .fb, .bf, .flb`用于表示寄存器操作数类型的浮点类型及相应的位宽，`.d, .uw, .uh, .ub, .sw, .sh, .sb`用于表示寄存器操作数为整型及相应的位宽。


## 块体微指令的使用
块体微指令分为两个大类：公有微指令及私有微指令，通常情况下，块指令的块体微指令是由公有微指令配合部分私有微指令组成。

- 公有微指令：表示各种类型的块指令均可以使用，具体的微指令可以参见[基础指令集](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/instset/baseInstrs/)这一章节
- 私有微指令：表示只有对应类型的块指令可以使用，具体的微指令可以参见[标量块指令集](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/std_block/intro/)、[系统块指令集](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/sys_block/intro/)、[浮点块指令集](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/fp_block/intro/)、[并行块指令集](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/simt_block/intro/)这几个章节。
- 并行块的块体微指令是全部由私有微指令组成。

