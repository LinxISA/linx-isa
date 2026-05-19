# 汇编器内置指令

汇编器提供一系列的架构无关的指令来以方便操作，所有的汇编器内置的指令都以'.'开头。 完整的列表请见GNU文档，下表中是部分常用的汇编器内置指令。

| Directive | Arguments | Description |
|--|--|--|
| .align	|integer	|align to power of 2 (alias for .p2align)|
| .file	|"filename"	|emit filename FILE LOCAL symbol table|
| .globl	|symbol_name	|emit symbol_name to symbol table (scope GLOBAL)|
| .local	|symbol_name	|emit symbol_name to symbol table (scope LOCAL)|
| .comm	|symbol_name,size,align	|emit common object to .bss section|
| .common	|symbol_name,size,align	|emit common object to .bss section|
| .ident	|"string"	|accepted for source compatibility|
| .section	|[{.text,.data,.rodata,.bss}]	|emit section (if not present, default .text) and make current|
| .size	|symbol, symbol	|accepted for source compatibility|
| .text		||emit .text section (if not present) and make current|
| .data		||emit .data section (if not present) and make current|
| .rodata	||emit .rodata section (if not present) and make current|
| .bss		||emit .bss section (if not present) and make current|
| .string	|"string"	|emit string|
| .asciz	|"string"	|emit string (alias for .string)|
| .equ	|name, value	|constant definition|
| .macro	|name arg1 [, argn]	|begin macro definition \argname to substitute|
| .endm		||end macro definition|
| .type	|symbol, @function	|accepted for source compatibility|
| .option	|{relax,norelax,push,pop}	|Refer to .option for a more detailed description.|
| .byte	|expression [, expression]*	|8-bit comma separated words|
| .2byte	|expression [, expression]*	|16-bit comma separated words|
| .half	|expression [, expression]*	|16-bit comma separated words|
| .short	|expression [, expression]*	|16-bit comma separated words|
| .4byte	|expression [, expression]*	|32-bit comma separated words|
| .word	|expression [, expression]*	|32-bit comma separated words|
| .long	|expression [, expression]*	|32-bit comma separated words|
| .8byte	|expression [, expression]*	|64-bit comma separated words|
| .dword	|expression [, expression]*	|64-bit comma separated words|
| .quad	|expression [, expression]*	|64-bit comma separated words|
| .dtprelword	|expression [, expression]*	|32-bit thread local word|
| .dtpreldword	|expression [, expression]*	|64-bit thread local word|
| .p2align	|p2,[pad_val=0],max	|align to power of 2|
| .balign	|b,[pad_val=0]	|byte align|
