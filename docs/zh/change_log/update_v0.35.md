# 0.35版本更新

日期：2023年12月11日

指令编码设计文档网页版路径请见[LinxISA Encoding-v0.35](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100261469689)

## 版本更新总体说明

1. 该版本指令集最主要的更新是增加内联块的设计。
2. LBREF块头`BTextStartOffset`字段复用为LCONST字段。
3. BLBAR块指令的编码调整。
4. addc,subc,fmadd指令编码调整。

## 增加内联块

Header Body的分层设计在面对Size较小的Block时，不仅造成了CodeSize的膨胀还阻碍了性能的进一步提升。为此，在LinxISA-0.35中，我们参考CISC指令，对于小块，直接用Header同时表达微指令+跳转的语义。这样设计带来的好处有：对于纯数据搬移的小块，Header中直接做数据搬移的效率将会更高。而对于大于2条(32bits)指令且能编码入Inline Block的小块，将获得CodeSize的收益。

### 1.块头编码

内联块指令的块头编码如下图所示：

![inlineblock-v0.35](../figs/isa/version/inlineblock-0.35.png)

### 2.块内微指令介绍

- 内联块指令集使用12bit编码空间。
- 微指令内嵌于块头，每个块头最多表达4条微指令和1条块间跳转指令。
- 如果编码少于4条微指令，空闲位置需使用inl.nop指令占位。
- 块头中bget/bset不需要显示声明。
- 块内微指令需要以`inl.`为前缀。
- 内联块可以继承前一个块T寄存器。

内联块微指令汇编格式和解释如下表：

|  Opcode  |  汇编语法                     |    解释              |
|----------|-----------------------------|---------------------|
| INL.CONST |  inl.const simm8 | 加载符号扩展的8bit有符号立即数，写到目的T寄存器 |
| INL.MOVI |  inl.movi simm4, => RegDst | 加载4bit有符号立即数，写到目的T寄存器和RegDst寄存器 |
| INL.ADDI |  inl.addi RegSrc, simm4 | 计算寄存器加立即数的值，写到目的T寄存器 |
| INL.MOVR |  inl.movr RegSrc, => RegDst | 将源寄存器的值复制到目的T寄存器和RegDst寄存器 |
| INL.LOADI |  inl.loadi [t#1, uimm5] | 从前序指令结果加带移位的立即数偏移所在地址加载对应字节的数据写到目的T寄存器 |
| INL.MOVT |  inl.movt t#l, => RegDst | 前序1-4条指令的结果写到目的T寄存器和RegDst寄存器 |
| INL.LOADR |  inl.loadr [RegSrc, t#1] | 从左源寄存器加前序指令结果的地址内存加载对应字节的数据写到目的T寄存器 |
| INL.ADD |  inl.add RegSrc, t#1, => RegDst | 左源寄存器加前序指令结果后写到目的T寄存器和RegDst寄存器 |
| INL.BINOPI |  inl.binopi t#1, simm4 | 两输入短指令，一个寄存器和一个立即数输入 |
| INL.LOADI |  inl.loadi [t#1, 0], => RegDst | 从前序指令结果对应的地址内存加载对应字节的数据写到目的T寄存器和RegDst寄存器 |
| INL.BINOP |  inl.binop RegSrc, t#1 | 两寄存器输入短指令 |
| INL.SUB |  inl.sub RegSrc, t#1, => RegDst | 左源寄存器减前序指令结果后写到目的T寄存器和RegDst寄存器 |
| INL.ALLOP |  inl.allop t#1, t#r | 包含大部分两个T寄存器输入的指令 |
| INL.MOV2NI |  inl.mov2ni simm, => RegDst | 将立即数为指数的2的N次方写到目的T寄存器和RegDst寄存器 |
| INL.STORE |  inl.store t#2, [RegSrc, t#1] | 将前序第2条指令结果的写到目的地址所在内存 |
| INL.LD |  inl.ld [RegSrc, t#1], => RegDst | 从源地址加载8字节数据写到目的T寄存器和RegDst寄存器 |

<!-- 
有关内联块的定义详见[内联块介绍](./isa/blockIntro/inline_block.md)
 -->

## 控制块指令LBREF块头增加LCONST域段

为了适配内联块中增加的inl.lconst、inl.addbpc等微指令，**LCONST**域段复用了原来LBREF块头的**BTextStartOffset**域段，即当LBREF块后面带有Inline Block时，该段用于存储32bit LCONST长立即数，可被跟随的Inline Block里面的lconst指令索引。

![LBREF-0.35](../figs/isa/version/LBREF-0.35.png)

## 指令编码修改

### 1、控制块中BLBAR指令编码调整

0.31版本更新块头的编码后，块头BInst[63:32]的高16bit用于编码块指令的输入（BGET MASK），低16bit用于编码块指令的输出(BSET MASK)。为了统一编码格式，将LoadBase0域段编码改到高16bit中BInst[51:48]位置，同时为了避免误导改称为RegPtr，该域段用于存储第一层架构寄存器ID，索引第一层架构寄存器R0-R15。

在初始版本定义中，BLBAR块头编码中block_size：2’b00表示以32byte为单位预取数据；2’b01表示以64byte为单位预取数据。但实际上硬件上预取都是以Cacheline(64byte)为单位，因此将块头编码中BlockSize域段改为固定编码2'b01。

编码更新前：

![BLBAR-0.34](../figs/isa/version/BLBAR-0.34.png)

编码更新后：

![BLBAR-0.35](../figs/isa/version/BLBAR-0.35.png)

### 2、ADDC，SUBC，FMADD指令编码及语义调整

与条件选择指令csel相同，addc，subc和fmadd也是三寄存器输入的指令。为了简化编译器实现，这些指令在当前版本取消第二个源寄存器的限制(以前版本中，指令编码中SrcR字段前的R/L固定编码为0，即SrcR只可以索引全局寄存器R0和私有寄存器R1-R15)。 csel,addc,subc和fmadd指令现在允许三个寄存器输入都是T寄存器。硬件会将第三个T寄存器拆成一条Dummy Local GPR的mov加上一条正常的三输入的指令。

例如一条`csel t#l, t#r, t#c`指令拆分后为：
```asm
addi t#c, 0, -> r0
csel  t#l, t#r, r0
```
其中r0是一个硬件定义的Local R0寄存器。

修改前的编码：

![ADDC-0.34](../figs/isa/version/ADDC-0.34.png)
![FMADD-0.34](../figs/isa/version/FMADD-0.34.png)

修改前的编码：

![ADDC-0.35](../figs/isa/version/ADDC-0.35.png)
![FMADD-0.35](../figs/isa/version/FMADD-0.35.png)

