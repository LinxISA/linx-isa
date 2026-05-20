# 编译器内置指令

安装器提供了一系列与架构相关的指令来方便操作，所有安装器内置的指令都以'.'开头。完整的列表请参见GNU文档，下面是部分常用的安装器内置指令。

|指令|论点|描述 |
|--|--|--|
| .align |整数 |对齐到 2 的幂（.p2align 的别名）|
| .file |“文件名” |发出文件名文件本地符号表|
| .globl |symbol_name |将 symbol_name 发送到符号表（范围 GLOBAL）|
| .local |symbol_name |将 symbol_name 发送到符号表（范围 LOCAL）|
| .comm |符号名称、大小、对齐 |将公共对象发送到 .bss 部分|
| .common |symbol_name,size,align |将公共对象发送到.bss节|
| .ident |“字符串” |为了源兼容性而接受|
| .section |[{.text,.data,.rodata,.bss}] |发出节（如果不存在，则默认为 .text）并设为当前节|
| .size |符号，符号|为了源兼容性而接受|
| .text | |发出 .text 部分（如果不存在）并设为当前|
| .data | |发出 .data 部分（如果不存在）并设为当前|
| .rodata | |发出 .rodata 部分（如果不存在）并设为当前|
| .bss | |发出 .bss 部分（如果不存在）并设为当前|
| .string |“string” |发出字符串|
| .asciz |"string" |发出字符串（.string 的别名）|
| .equ |名称、值|常量定义|
| .macro |name arg1 [, argn] |开始宏定义\要替换的argname|
| .endm | |结束宏定义|
| .type |符号，@function |为了源兼容性而接受|
| .option |{relax,norelax,push,pop} |有关更详细的说明，请参阅 .option。
| .byte |表达式 [, 表达式]* |8 位逗号分隔字|
| .2byte |表达式 [, 表达式]* |16 位逗号分隔字|
| .half |表达式 [, 表达式]* |16 位逗号分隔的单词|
| .short |表达式 [, 表达式]* |16 位逗号分隔字|
| .4byte |表达式 [, 表达式]* |32 位逗号分隔字|
| .word |表达式 [, 表达式]* |32 位逗号分隔的单词|
| .long |表达式 [, 表达式]* |32 位逗号分隔的单词|
| .8byte |表达式 [, 表达式]* |64 位逗号分隔字|
| .dword |表达式 [, 表达式]* |64 位逗号分隔字|
| .quad |表达式 [, 表达式]* |64 位逗号分隔字|
| .dtprelword |表达式 [, 表达式]* |32 位线程本地字|
| .dtpreldword |表达式 [, 表达式]* |64 位线程本地字|
| .p2align |p2,[pad_val=0],max |对齐到 2 次幂|
| .balign |b,[pad_val=0] |字节对齐|
