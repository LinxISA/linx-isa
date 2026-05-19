# 0.30版本更新

日期：2023年8月18日

指令编码设计文档网页版路径请见[LinxISA Encoding-v0.30](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255877291)

### 32bit编码格式变化

v0.30对32bit编码格式进行了重构，重构原因：

- 目前BISA微指令的编码并不是最优，CodeSize和取指FootPrint过大。
- BISA即将正式商用，需要尽快定下来一个最优的且通用指令编码，之后就不会再进行大的变动。
- BISA要升级至1.0，需要预留指令空间，提前布局32bit编码空间。

编码格式变化：

- 在一种编码格式中源寄存器可以表达为T寄存器或块内私有寄存器（标志位判断）。
- 增加额外的目的寄存器，可以是块内私有寄存器也可以是共享架构寄存器（标志位判断）。
- 提升了立即数的编码空间。

### 指令实现变化

- 大部分指令与set/set.g指令合并，结果有选择更新到目的寄存器，且结果默认写到T寄存器的设计不变。
- 乘法指令将结果高位和低位分别写到目的T寄存器和目的寄存器。
- 除法/求余指令将商和余数分别写到目的T寄存器和目的寄存器。
- load类指令将加载的数据和访问地址分别写到目的T寄存器和目的寄存器。

### 新增指令

#### 块内跳转类

- b.eq：相等时跳转
- b.ne：不等时跳转
- b.lt：小于时跳转（有符号比较）
- b.ge：大于等于时跳转（有符号比较）
- b.ltu：小于时跳转（无符号比较）
- b.geu：大于等于时跳转（无符号比较）

#### 整数通用计算类：

- addc: 带进位加法；
- subc: 借位减法；

#### 访存类

- PRF：预取内存（先将包含访问地址的内存块取到高速缓存中）。

#### 比特位操作类

- ctz：计数寄存器中最低有效位后面跟随的零的个数；
- concat：拼接(循环移位)

#### 浮点计算类

- fmadd：浮点乘加指令；
- fabs：求浮点绝对值；

#### 立即数类

- lui：高位立即数加载。

#### 块输入输出类

- bend：用于作为结束块指令执行的指令。属于标准块内输入输出指令。

#### 系统指令类

- BSE：当前块提交后，将自定义事件信息发给外部系统。
- BC.IVA：在Block Header Cache中无效SrcL的内存地址所对应的虚拟地址。
- BC.IALL：Block Cache中无效掉所有的Cacheline。
- IC.IVA：在Instruction Cache中无效SrcL的内存地址所对应的虚拟地址。
- IC.IALL：在Instruction Cache中无效掉所有的Cacheline。
- DC.IVA：在Data Cache中无效SrcL的内存地址所对应的虚拟地址。
- DC.CVA：在Data Cache中将SrcL的内存地址所对应的虚拟地址写回到下一级告诉缓存或主处理器中。
- DC.CIVA：在Data Cache中将SrcL的内存地址所对应的虚拟地址写回到下一级告诉缓存或主处理器中，并标记对应Cacheline无效。
- DC.ISW：Data Cache 中无效SrcL中所表明的Set/Way对应的Cacheline。
- DC.CSW：在Data Cache中将SrcL中所表明的Set/Way对应的Cacheline写回到下一级告诉缓存或主处理器中。
- DC.CISW：在Data Cache中将SrcL中所表明的Set/Way对应的Cacheline写回到下一级告诉缓存或主处理器中，并标记对应Cacheline无效。
- TLBGET：特权级:读取页表并设置对应SSR寄存器。
- TLBSET：特权级:读取SSR寄存器并设置对应页表。
- TLBI：在TLB中将Src存储的ASID对应的页表清除。
- FENCE.D：数据屏障。
- FENCE.I：指令屏障。

### 其他变动

- 访存指令等增加`基址寄存器+变址寄存器`寻址模式；
- sel指令改为**csel**（条件选择指令）
- 浮点指令合并（例：fdiv.h,fdiv.s,fdiv.d 改为一条指令 fdiv），实现一条指令完成不同精度操作数的相同操作。
- fget指令增加了64位无符号长整型与[半/单/双]精度浮点数之间的转换，同时fget指令名称改为**fcvt**。
- 系统块内微指令：保留SSRGET,SSRSET,lr.d,lr.w,sc.d,sc.w；trap,wfe,wfi,fence,fence.i合并为SSRCRLT指令。
- 提交参数寄存器CARG.FLAG域段改为1bit标志位。setc.eq类指令对CARG.FLAG置位。
- 在标准块内支持ssrget指令，即标准块内实现对系统寄存器的只读。
- 乘法指令的变动：

以前版本使用mul,mulh,mulhsu,mulhu,mulw；v0.30使用mul,mulu,mulw,muluw,mulh,mulhu。同时mul/mulu指令目的T寄存器和RegDst寄存器输出改为一致（乘法结果保留低位）。
