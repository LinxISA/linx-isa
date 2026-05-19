The assembly file is compiled and encoded to generate a binary object file, and the required binary object files are linked to generate the final binary executable file. <br>

The simplest link command is as follows:<br>
```
ld.lld  tmp.o -o tmp.out
```
Or use the clang command directly:
```
clang --target=linx64v4-linux-musl  tmp.o -o tmp.out
```

Use the default linker script and do not link any libraries or start functions. For linker usage, please refer to: https://lld.llvm.org/. <br>

## How the segments in the assembly file affect the layout of the final binary content

From the above discussion, in the same assembly file, the contents in the same segment are spatially continuous in the final generated binary (binary is used to represent the binary executable file in the following text). The arrangement of sections with different names in the same assembly file and sections in different assembly files is determined by the link order and link script. <br>

Sections with different names in the same assembly file:<br>

- When the position of the section is not specified in the linker script, it will be sorted according to the lexicographic order of the section name<br>
- When the order of specific sections of a specific file is specified in the linker script, the specified sections are arranged in the order specified by the linker script<br>

Segments in different assembly files:<br>

- When the order of specific sections of a specific file is not specified in the linker script (the current default linker script), the order in which sections in different assembly files are arranged in the binary follows the linker order. In the link command, one file is written before another file, which will be placed at the front position in the binary<br>
- Specify the order of specific sections of a specific file in the link script, and the specified sections are arranged in the order specified by the link script<br>


Therefore, for LinxISA, the currently supported integrated blocks and separated blocks have different binary arrangement requirements:
- For one-piece blocks, there is no additional arrangement operation for header and body
- For separate blocks, if you want to change the arrangement of header and microinstruction content in the binary, you need to:
	1. Distinguish segments in the assembly file as needed.
	2. Change the linker script to arrange the segments as needed.


The following introduces three binary arrangement schemes in the form of separated blocks.
### Scheme 1 (ELF arrangement): header in the entire binary is in a continuous area, and the microinstructions are in another continuous area.

- In all assembly files, place header in section A and microinstructions in section B. <br>
- In the linker script, place section A in the output section A-OUT and section B in the output section B-OUT. <br>

Features: Different sections of the same file are not continuous, but sections of the same name in different files are continuous and arranged according to the link script. The distance between header is the smallest, and the distance between header microinstructions is the largest.

### Option 2 (.o arrangement): header and the microinstructions in the same assembly file are in a continuous area, and header and the microinstructions in another assembly file are in another continuous area.

- In the assembly file, put header in section A and the microinstructions in section B. <br>
- In the link script, the A and B sections in the same assembly file are placed in the same output section AB-OUT in order. <br>

Features: Different segments of the same file are continuous, and different files are arranged in link order. The distance between header inside the file is small, and the distance between header microinstructions is small.

### Option 3 (Function Arrangement): The header and microinstructions of the same function are in a continuous area, and the header and microinstructions of another function are in another continuous area.

- Place the header of function A in section A, and the microinstructions of function A in section A.body. Place the header of function B in section B, and the microinstructions of function B in section B.body. Other functions follow the same rules and so on. <br>
- In the link script, place the sections in the same output section AB-OUT in the order of A, A.body, B, B.body. <br>

Features: Different sections of the same file are arranged according to the order in the link script, and different files are arranged according to the link order. header microinstructions are the smallest apart.

The comparison between different solutions is shown in the table below:<br>| Scheme | header distance between files | header distance within files | header distance within functions | header distance between microinstructions |
| ---------- | ---------- | ---------- | ---------- | ---------- |
| Option 1 | Minimum | Minimum | Equal | Maximum |
| Option 2 | Maximum | Minimum | Equal | Less than Option 1, Greater than Option 3 |
| Option 3 | Greater than Option 1, less than Option 2 | Maximum | Equal | Minimum |


The syntax of link scripts is not explained in detail in this article. Please refer to https://ftp.gnu.org/old-gnu/Manuals/ld-2.9.1/html_chapter/ld_3.html

### Function Alignment

Linx Instruction Set Architecture defines header and body. In order to support the alternate arrangement of header and body at the plan three function or plan two file level during the link stage, the assembly needs to ensure that the start of each function is 8byte aligned. The ‘.align 3’ alignment command needs to be added before each header. <br>
 
header：<br>
```
.section .text	 
.align 3	     //保证main函数的header是8B对齐
main：
    BSTART.SIMT FALL 
    B.TEXT main.bstart
    BSTOP
```

Microinstructions:<br>

```
.section .text.body
main.bstart:
    addi zero,0, ->t
    ...
    lbstop
```