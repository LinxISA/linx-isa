# 0.20版本更新

更新日期：2023-02-01

以下是0.20版本指令的具体变动点：

## 1.微指令结构变化

大部分微指令，可以既可以访问T寄存器，又可以访问SR寄存器。例如：

- **模式A**:两个source都是寄存器：add a0 a1。
- **模式B**:两个source是SR寄存器, 一个source是T寄存器：add t#1 a0。
- **模式C**:两个source是T寄存器：add t#1 t#2。

!!! note "注意！以下指令只支持T寄存器索引"

    MUL/DIV/REM 编码不足，只支持T寄存器索引。  
    浮点指令只支持T寄存器索引。

## 2.GET/SET语义修改

- SET重命名为SET.G, 同时更新global/local GPR。
- SGET/SSET重命名为GET/SET。
- GET/SET和SET.C/SET.TGT共享编码空间4'b0110/4'b0111。

### 2.1 新增MV (Move指令)

**MV R1, R2** 将R2移动到R1上, 本指令用于Calling Convention中寄存器迁移
**MV.G R1, R2** 将R2移动到R1上, 并广播R1, 本指令用于if-else中PHI节点的值迁移
硬件作为一条GET和SET指令同时执行本指令
MV指令作为set指令的绝对寄存器版本 **set a0/t#m a1**

### 2.2 移除ADDSP/ADDSPI指令

由于GET/SET语义修改后，ADDSP指令不太需要了。
除了影响code size以外，可以用以下两条指令代替ADD SP t#1, SET.G t#1 SP。
去掉本指令的主要原因是本指令是带有副作用的计算指令。我们希望只有SET/MV才有副作用，其他指令不能修改GPR，这样对硬件实现有好处(简化块内Rename)。

### 2.3 新增GET特殊寄存器

- GET TID: 获取线程ID
- GET CPUID: 获取CPU ID
- GET HDS: 获取当前块头的Size

## 3. CONST指令imm从11bit提升到12bit

原有立即数范围 -1024-1023
现有立即数范围 -2048-2047
原因：12bit立即数做到了和RISV的ADDI相同的水平，这样的话

`ADDI rd, rs0, imm(12bit)`

等效于如下：

```c
const imm(12bit)
addi rs0, t#1
```
如果有SET, 那么需要多出来个SET。
```c
const imm(12bit)
addi rs0, t#1
set rd, t#1
```

## 4. 新增HYPER Block种类

新版v0.20在块头上标明块内是否有跳转
新增Block属性b.hyper和块的种类并行

## 5. 新增TRAP跳转种类

告诉硬件当前块头是一个TRAP跳转类型的块，后续的硬件准备进行系统调用。
本块头用于程序结束/系统调用时候使用。

## 6. LOAD/STORE指令寻址模式优化

### Load指令寻址：

- **模式A**: Link + Imm (signed 5bit) 汇编格式：ld [t#1, 8]
```c
LB：ADDR = Link + Imm
LH：ADDR = Link + Imm<<1
LW：ADDR = Link + Imm<<2
LD：ADDR = Link + Imm<<3
LBU：ADDR = Link + Imm
LHU：ADDR = Link + Imm<<1
LWU：ADDR = Link + Imm<<2
```
注：立即数的取指范围为-16到16

- **模式B**: Register + Imm (signed 4bit) 汇编格式：ld [a0, 8]
```c
LB：ADDR = Register + Imm
LH：ADDR = Register + Imm<<1
LW：ADDR = Register + Imm<<2
LD：ADDR = Register + Imm<<3
LBU：ADDR = Register + Imm
LHU：ADDR = Register + Imm<<1
LWU：ADDR = Register + Imm<<2
```
注：立即数的取指范围为-8到8

- **模式C**: SP + Imm (signed 8bit) 汇编格式：ld [sp, 8]
```c
LB：ADDR = SP + Imm
LH：ADDR = SP + Imm<<1
LW：ADDR = SP + Imm<<2
LD：ADDR = SP + Imm<<3
LBU：ADDR = SP + Imm
LHU：ADDR = SP + Imm<<1
LWU：ADDR = SP + Imm<<2
```
注：立即数的取指范围为-128到128

- **模式D**: IP + Imm (unsigned 8bit) 汇编格式：ld [ip, 8]
```c
LW：ADDR = TPC_END + Imm<<2
LD：ADDR = TPC_END + Imm<<3
LWU：ADDR = TPC_END + Imm<<2
```
注：本指令用于访问放在块体后面的长立即数。也可以用于PC-relative load。立即数的取指范围为0到256。

使用以上寻址模式，可以高效覆盖大部分load场景，例如指针的寻址：
```
ld [a0]
ld [t#1, 8]
```
### Store指令寻址

由于16bit编码限制，Store需要额外编入data的索引，因此不能有复杂的寻址模式。

- **模式E**: [Link0 + Imm (unsigned 3bit)] = link1 汇编格式：sd [t#1, 8], t#2

SB：[ADDR = Link0]=DATA=Link1 注：store byte没有立即数编码，将ADDR写回T寄存器
SH：[ADDR = Link0]=DATA=Link1 注：store half word没有立即数编码，将ADDR写回T寄存器
SW：[ADDR = Link0 + Imm<<2]=DATA=Link1, 立即数只有3bit空间，取值0/4/8/12/16/20/24/28，并将ADDR写回T寄存器
SD：[ADDR = Link0 + Imm<<3]=DATA=Link1, 立即数只有3bit空间，取值0/8/16/24/32/40/48/56，并将ADDR写回T寄存器
举例：如果要编码 array[i] = a0+a1
```c
add a0, a1
ag.uxtw array, i
sd [t#1], t#2
```

- **模式F**: [Link + Imm (unsigned 2bit)] = register 汇编格式：sd [t#1, 8], a0

SB：[ADDR = Link0]=DATA=Reg 注：store byte没有立即数编码，将ADDR写回T寄存器
SH：[ADDR = Link0]=DATA=Reg 注：store half word没有立即数编码，将ADDR写回T寄存器
SW：[ADDR = Link0 + Imm<<2]=DATA=Reg, 立即数只有2bit空间，取值0/4/8/12，并将ADDR写回T寄存器
SD：[ADDR = Link0 + Imm<<3]=DATA=Reg, 立即数只有2bit空间，取值0/8/16/24，并将ADDR写回T寄存器
举例：如果实现一个store quard指令
```c
sd [a4], a0
sd [t#1, 4], a1
sd [t#1, 4], a2
sd [t#1, 4], a3
```

- **模式G**: [Register + Imm (unsigned 2bit)] = link 汇编格式：sd [a0, 8], t#1

SB：[ADDR = Register]=DATA=Link 注：store byte没有立即数编码。
SH：[ADDR = Register]=DATA=Link 注：store half word没有立即数编码。
SW：[ADDR = Register + Imm<<2]=DATA=Link, 立即数只有3bit空间，取值0/4/8/12/，并将ADDR写回T寄存器
SD：[ADDR = Register + Imm<<3]=DATA=Link, 立即数只有3bit空间，取值0/8/16/24/，并将ADDR写回T寄存器
举例：store quard指令的另外一种实现方法
```c
ld [s0]
sd [a0], t#1
sd [a0, 8], t#2
sd [a0, 16], t#3
sd [a0, 24], t#4
```
如果立即数过长，或者不在0/4/8/12以内，那么就得使用如下方法：
```c
const imm
ag.td a0, t#1
sd [t#1], a1
```
- **模式H**: [Register + Imm (unsigned 1bit)] = link 汇编格式：sd [a0, 8], a1

SB：[ADDR = Register]=DATA=Register 注：store byte没有立即数编码，将ADDR写回T寄存器
SH：[ADDR = Register]=DATA=Register 注：store half word没有立即数编码，将ADDR写回T寄存器
SW：[ADDR = Register + Imm<<2]=DATA=Register, 立即数只有1bit空间，取值0/4，并将ADDR写回T寄存器
SD：[ADDR = Register + Imm<<3]=DATA=Register, 立即数只有1bit空间，取值0/8，并将ADDR写回T寄存器
举例：store pair指令的一种实现方法
```c
sd [a0], a1
sd [a0,8], a2
```
两个寄存器编码已经占了8bit，Opcode为7bit，因此没有了立即数的编码空间。

为什么不能做成如下这个样子？：
```
const offset
sd [a0, t#1], a2
```
因为这条指令变成了3操作数的指令，违反了简化硬件的原则。

那寄存器编码不足怎么解决？->使用AG-address gen指令
```
const offset
ag.td a0, t#1
sd [t#1], a2
```

## AG指令寻址

为了解决在纯16bit编码空间下，Store编码空间显著不足的问题，我们引入了AG:address generation指令。

AG原名为LEA:load effective address,为了避免和x86重名，改为AG。  
AG指令专门用于复杂的寻址模式，可被Load/Store指令共同使用，但主要用于store。  
由于Store的编码空间不足，不得不引入额外的指令用于产生store的地址。  
AG主要用于array[i] = b这种访问模式。  
AG指令公式如下：

`R0 + convert(R1) << scale`

其中Convert指的是一种变换函数，有如下三种类型：

1. 如果R1类型是unsigned int, 那么先zero extend，并左移shift 2/3
2. 如果R1类型是signed int,那么先sign extend，并左移shift 2/3
3. 如果R1类型是long int，那么左移1/2/3

convert作为AG的opcode扩展，有如下模式：

- AG.TW: 等价于R0 + R1<<2 汇编格式：ag.tw a0, a1
- AG.TD: 等价于R0 + R1<<3 汇编格式：ag.td a0, a1
- AG.UXTW: 等价于R0 + ((unsigned int)R1)<<2 汇编格式：ag.uxtw a0, a1
- AG.SXTW: 等价于R0 + ((signed int)R1)<<2 汇编格式：ag.sxtw a0, a1
- AG.UXTD: 等价于R0 + ((unsigned int)R1)<<3 汇编格式：ag.uxtd a0, a1
- AG.SXTD: 等价于R0 + ((signed int)R1)<<3 汇编格式：ag.sxtd a0, a1

AG指令支持Link和Register单一和混合的三种索引模式。

### LD/ST伪指令

为了汇编可读性，我们需要引入ld/st的伪指令，在后端可以拆成AG+LD/ST的微指令序列。

load伪指令格式：

`ld [(reg0/t#m), (reg1/t#n), imm, {TW/TD/UXTW/SXTW/UXTD/SXTD}]`
例如读取array[i].field，i是int，array是64bit，field的offset是24，可写成如下伪指令

`ld [a0, a1, 24, uxtd]`
会展开成如下指令:
```c
ag.uxtw a0, a1
ld [t#1, 24]
```
store伪指令格式：

`sd [(reg0/t#m), (reg1/t#n), imm, {TW/TD/UXTW/SXTW/UXTD/SXTD}], (reg2/t#k)`
例如给array[i].field = x赋值，可写成如下伪指令

`sw [a0, a1, 24, sxtw], a3`
会展开成如下指令:
```c
ag.sxtw a0, a1
addi t#1, 24
sw [t#1], a3
```
其中ag.sxtw可以由如下指令代替：
```c
getw a1
slli t#1, 2
add a2, t#1
addi t#1, 24
sw [t#1], a3
```

# 灵犀指令集0.21更新介绍

灵犀指令集 v0.21主要解决我们在v0.20编译和模型联调实现遇到的问题，主要改动点是：

1. 部分指令的编码域段微调，目标是进一步降低Code Size。
2. 部分立即数指令只能索引前序指令结果，提升立即数的编码空间。
3. 重构了Store指令的编码，v0.20的编码和解码过于复杂。
4. 新增了SET Imm指令。
5. 参考RISCV，补齐Zba/Zbb/Zbc/Zbd扩展。

以下是指令的具体变动点：

## 1.新增Local Zero寄存器

BISA v0.21的Local GPR共定义17个寄存器，**Zero**和**R0-R15**。但Global GPR中没有Zero寄存器定义。

!!! note "注意"
    Local RA寄存器并没有去掉，只能被GET指令读取，SET类指令写出。

微指令中GET/SET中对R0的解析不同:

微指令中GET Rx能够索引R0-R15, 其中x==0时，代表索引R0(Local RA)寄存器。  
微指令中SET R0, R0代表SET Zero, RA。SET.G/SET.GL也相同。  
微指令中SET Rx, Ry. 其中Rx可索引Zero,R1-R15, Ry可索引R0,R1-R15。  
其余微指令中的R0，全部代表Zero寄存器。

上述直接索引的寄存器，都变成Zero寄存器。

## 2.索引前序指令结果

我们发现大部分指令使用T#1的频率远远高于其他T#2-T#8。对于ADDI t#l, imm类指令，没有出现非t#1的场景。

因此，我们将Link域段的编码让给立即数，在V0.21下，以下指令只能使用t#1：

ADDI,SUBI,ANDI,ORI,XORI,SRLI,SRAI,SLLI - addi t#1, imm 其中t#1不编码。

!!! info "LOAD/STORE指令"
    Store指令由于原有的编码空间不足，需要利用本设计进行重构

## 3.REG+IMM立即数编码重构

由于引入Zero寄存器，ADDI类立即数Imm没必要表达值为0的Imm，因此Imm 0被赋予更大值的数的编码。

原有指令ADDI R0, 0可作为GET来使用，BISA V0.21需要改成ADD R0, zero
原有指令ADDI R0, 0原编码需解析成ADDI R0, 16。

!!! note "注意"

    SRL/SRA/SLL的立即数编码+1在0.21中统一改成如下的映射：
    立即数编码的映射变成一一对应，对于立即数0，解码为更大的溢出的值。

本立即数映射适用于:

ADDI,SUBI,ANDI,ORI,XORI,SRLI,SRAI,SLLI  
ADDIW,SUBIW,ANDIW,ORIW,XORIW,SRLIW,SRAIW,SLLIW  
CMP.EQI,CMP.NEI,CMP.LTI,CMP.LTUI,CMP.GEI,CMP.GEUI  
SETC.EQI,SETC.NEI,SETC.LTI,SETC.LTUI,SETC.GEI,SETC.GEUI  

Load/Store类指令的立即数不适用。

## 4.补齐AG指令

0.21版AG指令补齐了所有的可能性，可统一成如下形式, 总共2x2x3x4=48种表达形式。
补齐指令的原因：将来AI类程序中使用移位1的操作较为频繁(半精度)。

`AG {LREG/TREG}, {LREG,TREG}, {DW, SW, UW} << {0,1,2,3}`

汇编写法的改进:

为了避免和ARM专利冲突，UXTW这种叫法会被攻击，因此我们重新设计了汇编写法

```c
    ag a0, a1, uw        /* 代表计算a0 + ((unsigned int)a1) */
    ag a0, a1, uw << 1   /* 代表计算a0 + ((unsigned int)a1)<<1 */
    ag a0, t#1, sw << 2  /* 代表计算a0 + ((signed int)t#1)<<2 */
    ag t#2, t#1 << 3     /* 代表计算t#2 + (t#1<<3) */
```

## 5.新增长指令编码

为了解决16bit指令编码不足的问题，BISA v0.21引入了长指令编码。长指令编码的原理和CONCAT块头类似。

- 长指令编码固定占据1/16的编码空间。
- 长指令占据一个T寄存器的位置，编码长度为32bit。
- 长指令只在**辅助块AUX**, **系统块SYS**，**浮点块FP**中出现，标准块内不出现长指令。


以下指令的编码转移到长指令空间中，也支持相对索引/绝对索引/混合索引。

- `mul a0, a1`, `mul a0, t#1`, `mul t#1, a1`, `mul t#1, t#2`, `mulh, mulhu, mulhsu, mulw ` 
- `div a0, a1`, `div a0, t#1`, `div t#1, a1`, `div t#1, t#2`, `divu, divuw`  
- `rem a0, a1`, `remu a0, t#1`, `remuw t#1, a1`, `remw t#1, t#2`, `remu, remuw`  
- `bxu a0, imml-u6, immr-u6`, `bxu t#1, imml-u6, immr-u6`  
- `bxs a0, imml-u6, immr-u6`, `bxs t#1, imml-u6, immr-u6`  

## 6.新增三操作数指令

为了降低硬件复杂度，三操作数指令的第三操作数必定是T寄存器。
BISA v0.21在辅助块中共增加两条三操作数指令：
- **SELECT**：select t#c, a0/t#1, a1/t#2  
其中t#c索引的是条件

- **BFM**：bfm t#c, a0/t#1, a1/t#2  -原BAM+BMG指令合并。  
其中t#c索引的是bitfield的mask。

a1的值和Mask覆盖得到value -- BMG
将value覆盖到a0上，写入到T寄存器 - BAM

## 7.重构了浮点编码

SPEC2006 FP例子中，浮点乘/浮点属于热点指令，需要分配绝对/相对两种编码格式。

给所有浮点指令分配绝对/相对两种编码空间已经超出了16bit编码空间。

因此在0.21中，我们只给浮点乘、加和浮点转换16bit的空间。

FADD.H,FADD.S,FADD.D分别代表半精度，单精度和全精度浮点加

FMUL.H,FMUL.S,FMUL.D分别代表半精度，单精度和全精度浮点乘

硬件会对以下组合进行指令合并成乘加指令：
```
FADD.D R0, R1
FMUL.D t#1, R3
```

FGET指令支持**64bit Integer**, **32bit signed/unsigned**, **半精度**，**单精度**，**双精度**的五种格式的相互转换。
总共24种模式转换。

- FGET.L.H: 64-bit long integer to 16-bit half float
- FGET.L.S: 64-bit long integer to 32-bit single float
- FGET.L.D: 64-bit long integer to 64-bit double
- FGET.W.H: 32-bit signed integer to 16-bit half float
- FGET.W.S: 32-bit signed integer to 32-bit single float
- FGET.W.D: 32-bit signed integer to 64-bit double
- FGET.WU.H: 32-bit unsigned integer to 16-bit half float
- FGET.WU.S: 32-bit unsigned integer to 32-bit single float
- FGET.WU.D: 32-bit unsigned integer to 64-bit double
- FGET.H.L: 16-bit half float to 64-bit long integer
- FGET.H.W: 16-bit half float to 32-bit signed integer
- FGET.H.WU: 16-bit half float to 32-bit unsigned integer
- FGET.H.S: 16-bit half float to 32-bit single float
- FGET.H.D: 16-bit half float to 64-bit double
- FGET.S.L: 32-bit single float to 64-bit long integer
- FGET.S.W: 32-bit single float to 32-bit signed integer
- FGET.S.WU: 32-bit single float to 32-bit unsigned integer
- FGET.S.H: 32-bit single float to 16-bit half float
- FGET.S.D: 32-bit single float to 64-bit double
- FGET.D.L: 64-bit double to 64-bit long integer
- FGET.D.W: 64-bit double to 32-bit signed integer
- FGET.D.WU: 64-bit double to 32-bit unsigned integer
- FGET.D.H: 64-bit double to 16-bit half float
- FGET.D.S: 64-bit double to 32-bit single float

## 7.剩余系统块和浮点块指令全部移到长立即数空间
