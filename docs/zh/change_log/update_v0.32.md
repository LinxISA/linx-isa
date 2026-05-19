# 0.32版本更新

日期：2023年9月28日

指令编码设计文档网页版路径请见[LinxISA Encoding-v0.32](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255827005)

v0.32版本最主要的变动是对store指令的改动。

## 指令实现变化

### Store指令变动

1. 由于硬件解码器的DecodeType解码类型不匹配，需要对Store指令(sb/sh/sw/sd)的**opcode**做出调整：  
    - Reg + Reg格式: opcode 7'b0010110  -> 7'b0010100  /* RegDst字段改为全零 */
    - Reg + imm格式: opcode 7'b0010111  -> 7'b0010101
2. 为了简化Store指令的硬件寄存器的写口，降低硬件实现复杂度。修改sb/sh/sw/sd等指令的执行操作为：不输出目的地址，即不写T寄存器和RegDst寄存器。
3. 为了提升内存连续写的效率，新增sb.a/sh.a/sw.a/sd.a指令，在对应的sb/sh/sw/sd功能基础上，增加写地址到目的T和RegDst寄存器的操作。

![store-v0.33](../figs/isa/version/store-v0.32.png)

### 指令操作数增加TP/GP/CP

在v0.32，每条微指令的源寄存器都可以去索引系统寄存器中的TP/GP/CP寄存器。

- 为了提升硬件访问私有变量的效率，增加了微指令索引TP寄存器的操作。
- 为了提升硬件访问全局变量的效率，增加了微指令索引GP寄存器的操作。
- 为了提升硬件做状态迁移的效率，增加了微指令索引CP寄存器的操作。

### bit位操作指令变动

#### 为了提升字符串库处理的效率，比特位操作指令新增

- ctzw：在最低有效字内计数尾随零。  
- clz：在整个64bit内计数前导零。  
- clzw：在最低有效字内计数前导零。  

#### 为了降低硬件实现复杂度。对比特位操作指令bfi编码更新：改为两输入指令，M/N在指令编码中表达。

更新前：

![bfi-v32](../figs/isa/version/bfi-v32.png)

更新后：

![bfi-v64](../figs/isa/version/bfi-v64.png)

!!! info "编码的变化带来指令实现的部分变化"

    更新后G/L字段和RegDst字段的被M字段占用，因此结果只写到T寄存器。  
    更新前为三输入指令，为了简化硬件实现，限制了SrcR只能索引块内私有寄存器。更新为两输入后，去掉了该限制，SrcR可以索引T寄存器以及新添加的TP/GP/CP系统寄存器

#### 为了适配bfi编码的修改，对bxu和concat编码有所更新：

更新前：

![bxu_concat-v32](../figs/isa/version/bxu_concat-v32.png)

更新后：

![bxu_concat-v64](../figs/isa/version/bxu_concat-v64.png)

#### bxu/bxs/bfi指令实现加入卷绕情况的处理实现。

加入卷绕，可以通过这些指令对操作数实现循环移位操作（ror, rol）。

修改后的指令实现请查看：[bxu](../isa/inst/misa_g/BXU.md)，[bxs](../isa/inst/misa_g/BXS.md)，bfi。
