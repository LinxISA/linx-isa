In an executable file, there is at least one **.text** segment to store code and **.data** segment to store data.

The section names of some sections in the LinxISA assembler cannot be changed, and these sections have fixed attributes.

| Section name | Attributes |
|------------|------------|
| .text | Executable code segment |
| .data | Readable and writable data segment |
| .rodata | Read-only data segment |
| .bss | Uninitialized static data |


block instruction of LinxISA contains two parts: header and optional microinstructions. Where header and microinstructions are placed will directly affect the location of header and microinstructions in the final generated binary file. In an assembly file, the contents placed in the same section are placed in consecutive positions in the final generated binary.

In an a.s, header is placed in the text section, and the body is placed in the .text.body section. In the final generated binary file, header1 and header2 are placed continuously in space, and microinstruction 2 and microinstruction 1 are placed continuously.
```
.text
  ZXTERMZH39QXZ1
.pushSection    .text.body
  微指令2
.popSection
  ZXTERMZH39QXZ2
.pushSection    .text.body
  微指令1
.popSection

```

In an a.s, header is placed in the text section, and the body is placed in the .text.body section. In the final generated binary file, header1, header2, and header3 are placed continuously in space, and microinstruction 1, microinstruction 2, and microinstruction 3 are placed continuously.
```
.text
  ZXTERMZH39QXZ1
  ZXTERMZH39QXZ2
.pushSection    .text.body
  微指令1
  微指令2
.popSection
  ZXTERMZH39QXZ3
.pushSection    .text.body
  微指令3
.popSection

```

If the segment in a.s is in the following form, put header and body in the .text segment. In the final generated binary file, the order of placement becomes header1, microinstruction 2, header2, microinstruction 1.
```
.text
  ZXTERMZH39QXZ1
  微指令2
  ZXTERMZH39QXZ2
  微指令1
  ...
```
Regarding the problem of different placement of sections in binary files caused by sections with the same name in different assembly files, or sections with different names, and the alignment problem of LinxISAheader, please see the following chapters.