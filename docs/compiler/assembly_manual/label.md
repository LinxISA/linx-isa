Labels need to start from the first character of a line. If the line has no labels, you need to start the line with a space or tab delimiter. If there is a label, the assembler considers the label to be equal to the address in the object file of the corresponding instruction. Tags can be used as targets for branches or loads and stores. If the current line has only a label, the assembler assumes that the address represented by the label is equal to the address of the next line of instructions in the current section.

In the following example, .Ltmp0_std is a label, and header instruction*BSTART.STD* is assembled in such a way that the offset in the instruction encoding points to the position of the label .Ltmp0_std, which means the start of the next block instruction.


header：
```
...
...
.text
BSTART.STD COND, .Ltmp0_std 
addi zero,32, ->t           /* 当前ZXTERMZH32QXZ的第一条微指令  */
sll t#1, a0,  ->t
sra t#1,t#2,  ->t
addi zero,32, ->t
sll t#2, t#1, ->t
srli t#1,30,  ->t
add a1,t#1,   ->a3
...
.Ltmp0_std
BSTART.STD FALL
...
BSTOP
...
...
```

There are two types of tags: tags used only inside the file and tags used outside the file.

- Tags used only within the file: This tag only takes effect within the current file. Other files can use tags with the same name. It is agreed that the tag used internally in the file is a string starting with '.L'
- Label used outside the file: it can be any string that does not coincide with the assembler keyword, and the name cannot be repeated.