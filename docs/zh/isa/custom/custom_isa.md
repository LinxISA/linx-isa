# 自定义块指令指南

灵犀块指令集层次化指令集框架下允许产品和客户定制自己的指令块。

对于自定义指令块，我们要求其维护统一的第一层架构状态，但是对于第二层架构状态可以完全自己定义，包括块内编码空间：微指令格式，编码宽度，执行方式等等。


  ![custom](../../figs/isa/arch/custom.PNG){ width="800" }


## 扩展块指令集

用户可以定义自己的一套指令集拥有自定义的编码。但是自定义指令集需要至少增加格外的两条指令：

- **GET**: 从第一层架构状态中获取寄存器，移动到块内私有寄存器中。
- **SET**: 从块内私有寄存器中移动到第一层架构状态中。

!!! info "自定义块指令限制"

	自定义块指令和其他块指令的关系为同步执行。因此，自定义块指令的内存读写与其他块指令的内存读写有保序的要求。在硬件实现上需要在相同的LSU进行保序执行。但是，自定义块指令允许有额外的私有访存接口，私有访存接口允许不和其他内存读写进行保序。

## 编译器如何支持自定义扩展块

我们可以通过c语言inline汇编即可在现有程序框架增加自定义指令块。

在不修改编译器的情况下，客户可以定制自己的块指令，并无缝内联到通用的c语言程序里面。

例如如下c语言函数中，我们可以：

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

    //定制块指令内联汇编
    __asm__ __volatile__ (

        "bstart custom_start\n"               //块头起始
        "bnext.fall\n"
        "bget %[var0], %[var1], %[var2]\n"
        "bset %[var0]\n"
        "battr atomic\n"
        "b.cus\n"                   //定制块类型
        "bstop custom_stop\n"                //块头结束

        ".pushsection \".text.body\",\"ax\"  \n" //块体部分起始位置，提示链接器将下面块体独立放置
        "custom_start:\n" //定制指令块体起始
            ".word 0x4EA32EC0\n"    //定制指令RAW Binary
            ".word 0x0001EAB0\n"    //定制指令RAW Binary
        "custom_stop:\n"//定制指令块体结束
        ".popsection\n"  //块体部分结束位置，提示链接器将上述块体独立放置

        : [var1] "=r" (var1), [var2] "=r" (var2)  //输入输出列表
        : [var0] "r" (var0)
        : "memory");

    //普通C代码
    return b[c];
}
```

如下编译指令可以直接生成带有定制块的二进制。
```
linx64-unknown-elf-gcc example_inline_block.c -o test.bin
```

!!! info "定制块编译器和汇编器"

	对于定制块指令内部需要呈现原始二进制的字节码，如上述 `.word 0x10EF2812`代表的就是一个自定义的指令集，使用了块内的私有寄存器和内存读写。这些指令是对外不可见的。需要对外可见的变量需要声明块头的`bget`和`bset`中。
    第三方用户需要对自己的指令产生独立开发一套编译器和汇编器。BlockISA编译器只负责将定制块链接到其他标量块中，并不负责第三方定制块的编译工作。

## 如何维持前后兼容性

当前代码在跑在不支持定制块指令的CPU时，块指令CPU自动会选择使用标量块指令来执行Fallback代码。

在损失性能的场景下，依然能够维护定制块指令的前后兼容。


  ![custom_fallback](../../figs/isa/arch/custom_fallback.PNG){ width="800" }


块指令为什么能够执行Fallback块体？这来自于块指令架构的独特**Fixup**设计。详情请见块指令Fixup代码设计。
