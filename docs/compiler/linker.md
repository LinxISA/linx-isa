# linker

## Common concepts

**Global symbols**

- Strong symbol: unique. Multiple definition errors will be reported unless the allow-multiple-definition option is turned on.
- Weak symbol: not unique, no error will be reported if defined multiple times

Identification rules: There can only be one strong symbol, one is strong and multiple are weak. Choose the strong one. If there are multiple weak symbols, choose the one with the largest space.

**Quote**

- Strong reference: If the resolution cannot be found, an undefined error will be reported.
- Weak reference: No error will be reported when the resolution is not found. A default value of 0 is given to ensure that the link is correct, but an error may be reported during operation due to an incorrect address.

**Definition and usage of global symbols and local symbols**

Local symbols start with ".", the scenarios and usage are as follows

| Scenario | Example | Whether in the symbol table |
|------|-------| -------|
| lconst | lconst .L.str | yes |
|Pseudo Ops|.size .type .global .p2align .text, etc.|No |
|bodystart and stop (and headerbstart and bstop)| .LBB0_1.bstart .LBB0_1.bstop |Yes|
|header symbol (jump between blocks)| .LBB0_1 | Yes |
|Jump within block| j .LABEL1 | Yes |
|Jump between blocks| bnext.cond .LBB0_3 | Yes |
|Function end identifier (used for size calculation)|.Lfunc_end1|Yes|

Global symbols do not start with "." and need to be declared in the .s file using the ".global global symbol" format. The scenarios and usage are as follows

| Scenario | Example | Whether in the symbol table |
|------|-------| -------|
| lconst | lconst _ZN11cSimulation5evPtrE | yes |
|Jump between blocks| bnext.call _ZNK14cDisplayString8assembleEv | Yes |
|Function name| main | Yes |

Except for the segment names, attributes, definitions and function names of local symbols, all other scenarios are used for relocation. The assembler relocates for the first time and the linker relocates again.

**section**

Use the command "objdump -h .o" to view the sections in .o
Linx Instruction Set Architecture reuses the usage of regular Section. The .text section stores header. The .text.body section and the .linx.attributes section are added. The .text.body stores body. Mainly, the two sections .text and .text.body work. Examples are as follows:

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

**Segment entry explanation table**

| Name | Meaning |
|------|-------|
| Name | Section name |
| Size | Segment occupied space |
| VMA | Virtual memory address (executable file running address) |
| LMA | Load memory address (the address where the segment is loaded, usually equivalent to VMA) |

## Link principle
The main process is merge->Relax->Relocation

### Merge
Use the command "ld -verbose" to view the linker's default .lds link script. The main content is as follows:

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

The ENTRY (_start) in the first line specifies the program entrance as the _start function; the following SECTION command is the main body of the link script, specifying the transformation of various input sections to output sections. The curly brackets immediately following SECTIONS contain the SECTIONS transformation rules.a. . = SEGMENT_START("text-segment", 0x10000) + SIZEOF_HEADERS
  Set the current virtual address to SEGMENT_START("text-segment", 0x10000) + SIZEOF_HEADERS, SIZEOF_HEADERS is the file header size of the output file, "." represents the current virtual address
  
b. .text.body: {...}
  Segment conversion rules, merge the segments named .text.body and .text.body.* in all input files into the .text.body segment of the output file in turn
  
c. .text: {...}
  Same as above
  
d. /DISCARD/: { *(.note.GNU-stack) *(.gnu_debuglink) *(.gnu.lto_*) }
  Discard all sections named .note.GNU-stack, .gnu_debuglink, .gnu.lto_* in all input files and do not save them in the output file.

### relax

#### riscv_relax_delete_bytes

relax will call the riscv_relax_delete_bytes interface to delete header or microinstructions. The input parameters are the segment, the offset within the segment from the deletion starting position, and the deletion amount (in Byte).

Overall process:

- Adjust segment sec->size
- Pass in the starting address of the deleted content (dst), the ending address of the deleted content (src), the required movement amount for deletion, and call the memmove interface to complete the deletion. The deletion is completed by overwriting the part to be deleted with the mobile data.
- In the current segment, if deletion affects the relocation type offset, correct it
- In the current segment, if deletion affects the local symbol pc, make corrections
- In the current segment, if deletion affects the global symbol pc, make corrections

### Relocation

header is mounted with btext and bnext relocation. The btext relocation is calculated based on the same name symbol in the symbol table and headerpc. The bnext relocation is calculated based on bnext pc and headerpc.

lconst, intra-block jump (J.label) relocation calculates offset based on label