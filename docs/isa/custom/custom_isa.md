# Customize block instruction Guide

Linxblock instruction set hierarchical instruction set framework allows products and customers to customize their own instruction blocks.

For custom instruction blocks, we require them to maintain a unified first layer architectural state, but for the second layer architectural state, you can completely define it yourself, including the encoding space within the block: microinstruction format, encoding width, execution method, etc.


  ![custom](../../figs/isa/arch/custom.PNG){ width="800" }


## Extended block instruction set

Users can define their own set of instructions with custom encoding. However, a custom instruction set requires adding at least two additional instructions:

- **GET**: Get the register from the first layer architectural state and move it to the block-private register.
- **SET**: Move from the block-private register to the first layer architectural state.

!!! info "Customized block instruction limit"

	The relationship between custom block instruction and other block instruction is synchronous execution. Therefore, the memory reading and writing of the custom block instruction must be order-preserving compared to the memory reading and writing of other block instruction. In terms of hardware implementation, order-preserving execution needs to be performed on the same LSU. However, the custom block instruction allows additional private memory access interfaces, and the private memory access interface does not allow order preservation with other memory reads and writes.

## How the compiler supports custom extension blocks

We can add custom instruction blocks to the existing program framework through inline assembly in C language.

Without modifying the compiler, customers can customize their own block instruction and seamlessly inline it into common C language programs.

For example, in the following C language function, we can:

```c
int foo(long c)
{
    c = c + 1;
    return c;
}

int example_inline_block(int a, char *b, long c)
{
    //普通C代码
    int var1 = b[a];
    //预处理函数
    int var2 = foo(c);
    int var0 = 0;

    //定制ZXTERMZH32QXZ内联汇编
    __asm__ __volatile__ (

        "bstart custom_start\n"               //ZXTERMZH39QXZ起始
        "bnext.fall\n"
        "bget %[var0], %[var1], %[var2]\n"
        "bset %[var0]\n"
        "battr atomic\n"
        "b.cus\n"                   //定制ZXTERMZH33QXZ
        "bstop custom_stop\n"                //ZXTERMZH39QXZ结束

        ".pushsection \".text.body\",\"ax\"  \n" //ZXTERMZH40QXZ部分起始位置，提示链接器将下面ZXTERMZH40QXZ独立放置
        "custom_start:\n" //定制指令ZXTERMZH40QXZ起始
            ".word 0x4EA32EC0\n"    //定制指令RAW Binary
            ".word 0x0001EAB0\n"    //定制指令RAW Binary
        "custom_stop:\n"//定制指令ZXTERMZH40QXZ结束
        ".popsection\n"  //ZXTERMZH40QXZ部分结束位置，提示链接器将上述ZXTERMZH40QXZ独立放置

        : [var1] "=r" (var1), [var2] "=r" (var2)  //ZXTERMZH22QXZ列表
        : [var0] "r" (var0)
        : "memory");

    //普通C代码
    return b[c];
}
```

The following compilation instructions can directly generate binaries with custom blocks.
```
linx64-unknown-elf-gcc example_inline_block.c -o test.bin
```

!!! info "Custom block compiler and assembler"

	For customized block instruction, the original binary bytecode needs to be presented internally. As mentioned above, `.word 0x10EF2812` represents a customized instruction set, using private registers and memory reading and writing within the block. These instructions are not visible to the outside world. Variables that need to be visible to the outside need to be declared in `bget` and `bset` of header.
    Third-party users need to independently develop a set of compilers and assemblers to generate their own instructions. The BlockISA compiler is only responsible for linking customized blocks to other scalar blocks, and is not responsible for compiling third-party customized blocks.

## How to maintain forward and backward compatibility

When the current code is running on a CPU that does not support customized block instruction, the block instructionCPU will automatically choose to use scalarblock instruction to execute the Fallback code.

In the scenario of loss of performance, the front and rear compatibility of the customized block instruction can still be maintained.


  ![custom_fallback](../../figs/isa/arch/custom_fallback.PNG){ width="800" }


Why can block instruction execute Fallbackbody? This comes from the unique **Fixup** design of the block instruction architecture. Please see the block instructionFixup code design for details.