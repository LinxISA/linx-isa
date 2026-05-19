# 链接器

## 常见概念

**全局符号**

- 强符号：具有唯一性，多次定义会报multiple definition错误，除非开allow-multiple-definition选项
- 弱符号：不具有唯一性，多次定义不会报错

识别规则：强符号只能有一个，一个强，多个弱，选强的，多个弱的选空间最大的

**引用**

- 强引用：引用决议时找不到会报undefined错误
- 弱引用：引用决议时找不到不会报错，给个默认值0，保证链接正确，但运行可能因为地址有误报错

**全局符号和局部符号定义及使用方式**

局部符号以“.”开头，场景及用法如下

| 场景 | 举例 | 是否在符号表 | 
|------|-------| -------| 
| lconst | lconst  .L.str | 是 |
|Pseudo Ops|.size .type .global .p2align .text等|否 |
|块体start和stop（以及块头bstart和bstop）| .LBB0_1.bstart .LBB0_1.bstop |是|
|块头符号（块间跳转）| .LBB0_1 | 是 |
|块内跳转| j .LABEL1 | 是 |
|块间跳转| bnext.cond .LBB0_3 | 是 |
|函数结束标识（算size用）|.Lfunc_end1|是|

全局符号不以“.”开头，需要在.s文件中用”.global 全局符号”格式声明，场景及用法如下

| 场景 | 举例 | 是否在符号表 | 
|------|-------| -------| 
| lconst | lconst _ZN11cSimulation5evPtrE | 是 |
|块间跳转| bnext.call _ZNK14cDisplayString8assembleEv | 是 |
|函数名| main | 是 |

除了局部符号的段名、属性、定义和函数名，其他所有场景均用于重定位，汇编器第一次重定位，链接器再次重定位。

**section**

使用命令“objdump -h .o ”可以查看.o中的sections
灵犀指令集架构复用了常规Section的用法，.text section存储块头，新增了.text.body section和.linx.attributes段，.text.body存储块体，主要是.text .text.body这两个section起作用，举例如下：

```
pflowup.o:     file format elf64-littlelinx

Sections:
Idx Name          Size      VMA               LMA               File off  Algn
  0 .text         00000142  0000000000000000  0000000000000000  00000040  2**2
                  CONTENTS, ALLOC, LOAD, RELOC, READONLY, CODE
  1 .data         00000000  0000000000000000  0000000000000000  00000182  2**0
                  CONTENTS, ALLOC, LOAD, DATA
  2 .bss          00000000  0000000000000000  0000000000000000  00000182  2**0
                  ALLOC
  3 .text.body    00000054  0000000000000000  0000000000000000  00000182  2**0
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
  4 .comment      0000005d  0000000000000000  0000000000000000  000001d6  2**0
                  CONTENTS, READONLY
  5 .note.GNU-stack 00000000  0000000000000000  0000000000000000  00000233  2**0
                  CONTENTS, READONLY
  6 .linx.attributes 00000020  0000000000000000  0000000000000000  00000233  2**0
                  CONTENTS, READONLY

```

**段条目解释表**

| 名称 | 含义 | 
|------|-------| 
| Name | 段名 | 
| Size | 段占用空间 | 
| VMA | 虚拟内存地址（可执行文件运行地址） | 
| LMA | 加载内存地址（段被加载的地址，通常等同于VMA） | 

## 链接原理 
主要流程是合并->Relax->重定位

### 合并
使用命令“ld -verbose”可以查看链接器默认的.lds链接脚本，摘取主要内容如下：

```
ENTRY(_start)
SECTIONS
{
  /* Read-only sections, merged into text segment: */
  . = SEGMENT_START("text-segment", 0x10000) + SIZEOF_HEADERS;
  .text.body    :
    {
      *(.text.body .text.body.*)
    }
  .text           :
    {
      *(.text.unlikely .text.*_unlikely .text.unlikely.*)
      *(.text.exit .text.exit.*)
      *(.text.startup .text.startup.*)
      *(.text.hot .text.hot.*)
      *(SORT(.text.sorted.*))
      *(.text .stub .text.* .gnu.linkonce.t.*)
      /* .gnu.warning sections are handled specially by elf.em.  */
      *(.gnu.warning)
    }
  }
  /DISCARD/ : { *(.note.GNU-stack) *(.gnu_debuglink) *(.gnu.lto_*) }
  ```

第一行的ENTRY(_start)制定了程序的入口为_start函数；后面的SECTION命令是链接脚本的主体，指定了各种输入段到输出段的变换，SECTIONS后面紧跟着的大括号里包含了SECTIONS变换规则

a.  . = SEGMENT_START("text-segment", 0x10000) + SIZEOF_HEADERS
  将当前虚拟地址设置成SEGMENT_START("text-segment", 0x10000) + SIZEOF_HEADERS，SIZEOF_HEADERS为输出文件的文件头大小，“.”表示当前虚拟地址
  
b. .text.body: {...}
  段转换规则，将所有输入文件中的名字为.text.body、.text.body.*的段依次合并到输出文件的 .text.body段
  
c. .text: {...}
  同上
  
d. /DISCARD/: { *(.note.GNU-stack) *(.gnu_debuglink) *(.gnu.lto_*) }
  将所有输入文件中名字为.note.GNU-stack、.gnu_debuglink、.gnu.lto_*的段丢弃，不保存到输出文件中

### relax

#### riscv_relax_delete_bytes

relax会调用riscv_relax_delete_bytes接口删除块头或者微指令，入参是段、删除起始位置段内偏移、删除量（单位Byte）。

整体流程：

- 调整段sec->size
- 传入删除内容起始地址（dst），删除截止地址（src），删除所需移动量，调用memmove接口完成删除，删除是通过移动数据将要删除的部分覆盖完成的
- 在当前段中，如果删除影响了重定位类型偏移，进行修正
- 在当前段中，如果删除影响了局部符号pc，进行修正
- 在当前段中，如果删除影响了全局符号pc，进行修正

### 重定位

块头上挂载着btext和bnext重定位，btext重定位根据符号表中同名符号以及块头pc算出来，bnext重定位根据bnext pc以及块头pc算出来

lconst，块内跳转（J .label）重定位根据标签算出偏移
