# 通用加速器HAC接口

灵犀块指令集支持全场景的加速器调用和执行。其中加速器和协处理器 **HAC(Hardware Accelerated Coprocessor)** 的调用被封装成块指令。基于加速块、定制块和大量标量块而构建的程序往往用于数据面处理器等任务上。


  ![custom_acc](../../figs/uArch/ACC.PNG){ width="800" }


如上图所示，根据块处理器和加速器的远近，目前灵犀块指令集支持三种加速器调用方式：

- **A.同步紧耦合加速器接口**：使用第一层的32个全局寄存器进行传递。紧耦合的加速器作为块指令处理器中的**一个特别的PE**进行调用。PE间通过Block Reorder Buffer进行同步，因此，是个同步调用模型。
- **B.异步紧耦合加速器接口**：使用系统块的系统寄存器进行通讯。在读写系统寄存器后，当前线程会立即返回，并不等待加速器返回数据。因此，这是个异步调用模型。
- **C/D异步松耦合加速器接口**：使用MMU/SMMU通过地址映射进行加速器配置。这个和传统CPU-DSA接口类似。区别在于多个内存读写被封装成一个块统一做出。


在基于灵犀指令集的数据面处理器实现中，块处理器对接了来自于不同产品的加速器/HAC需求。
块指令处理器通过以上的接口，设计了一种私有HAC总线，完成对紧耦合加速器的高并发调用和接收工作。
具体设计如下图所示：


  ![sys_intf](../../figs/isa/arch/block-hac-sys.PNG){ width="500" }


## 同步紧耦合加速器接口

同步紧耦合加速器使用第一层的GPR寄存器进行传递，通过定制块头调用加速器。
每个加速器块，最大进行16个GPR寄存器的读，最大进行16个GPR寄存器的写。多余的参数传递可能需要访存内存，经过块内私有寄存器传递。

本接口适用于：

- **向量加速块Vector PE**
- **矩阵加速块Matrix PE**
- **加解密加速块SEC PE**

### 编程模型

下面内联汇编展示了一种紧耦合加速器的编程接口。
```c
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
        "battr aqrl\n"                       //Acquire and Release, 当前加速块为同步调用
        "b.cus\n"                            //定制块类型
        "bstop custom_stop\n"                //块头结束

        ".pushsection \".text.body\",\"ax\"  \n" //块体部分起始位置，提示链接器将下面块体独立放置
        "custom_start:\n" //定制指令块体起始
            ".word 0x10EF2812\n"    //定制指令RAW Binary
            ".word 0xBEAC123A\n"    //定制指令RAW Binary
            ".word 0xDEADBEFF\n"    //定制指令RAW Binary
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

## 异步紧耦合加速器接口

异步紧耦合加速器使用系统寄存器进行信息传递，通过系统块的**SSRGET/SSRSET**进行对加速器的信息传递。
系统块还覆盖了所有的标量指令，因此，可以完成一个比较复杂的信息处理操作。

本接口适用于：

- **非内存映射类加速器接口**：例如通过系统寄存器配置的加速器
- **私有总线RBA访存HAC**：例如HPOE，QueueManage等消息交互
- **Polling加速器**

本接口可以用于块处理器和私有加速器总线的访问。

### 使用方法

以下内联汇编展示了通过系统寄存器进行信息传递。

```c
#include <stdint.h>

typedef struct {
    uint64_t                msgLen : 8;
    uint64_t                corpId : 6;
    uint64_t                corpCmd : 6;
    uint64_t                coreId : 8;
    uint64_t                rsv1 : 4;
    uint64_t                rspStatus : 4;
    uint64_t                rsv2 : 28;
} HacControlInfoGfu;

static __inline__ void pushMsg(HacControlInfoGfu *inStruType, uint64_t *data)
{
    __asm__ __volatile__(
        "bstart 1f\n"
        "b.sys\n"
        "bget %0, %1\n"
        "bstop 2f\n"
        ".pushsection .text.body\n"
        "1:\n"
        "ld	[%1, 0],->s1\n"
        "ld	[%1, 8],->s2\n"
        "ld	[%1, 16],->s3\n"
        "ld	[%1, 24],->s4\n"
        "ld [%1, 32],->s5\n"
        "ld	[%1, 40],->a3\n"
        "ld	[%1, 48],->a4\n"
        "ld	[%1, 56],->a5\n"
        "ld [%0, 0]\n"
        "setc.msg t#1\n"
        "2:\n"
        ".popsection\n"
        :
        :"r"(inStruType), "r"(data)
        :"s1", "s2", "s3", "s4", "s5", "a3", "a4", "a5", "memory"
    );
}

int main(void) {
    /* 构造需要发送给HAC的消息结构体，data[0-7]是消息净荷 */
    HacControlInfoGfu inStruType;
    inStruType.rsv1 = 0;
    inStruType.corpId = 0;
    inStruType.corpCmd = 6;
    inStruType.coreId = 0;
    inStruType.msgLen = 6;

    uint64_t data[8] = {0x12, 0x23, 0x34, 0x45, 0x56, 0x67, 0x78, 0x89};
    pushMsg(&inStruType, (uin64_t *)data);
    return 0;
}
```

下面展示了一个处理器Polling的操作。

```c
static __inline__ void popMsg(uint64_t *data)
{
    __asm__ __volatile__(
        "bstart 1f\n"
        "b.sys\n"
        "bstop 2f\n"
        ".pushsection .text.body\n"
        "1:\n"
        "addi zero, 1\n"
        "bwe t#1\n"
        "2:\n"
        "bend\n"
        ".popsection\n"
        "bstart 3f \n"
        "bget %0, s1, s2, s3, s4, s5, a3, a4, a5\n"
        "b.sys\n"
        "bstop 4f\n"
        ".pushsection .text.body\n"
        "3:\n"
        "sd s1, [%0, 0]\n"
        "addi %0, 8\n"
        "sd s2, [t#1, 0]\n"
        "addi t#2, 8\n"
        "sd s3, [t#1, 0]\n"
        "addi t#2, 8\n"
        "sd s4, [t#1, 0]\n"
        "addi t#2, 8\n"
        "sd s5, [t#1, 0]\n"
        "addi t#2, 8\n"
        "sd a3, [t#1, 0]\n"
        "addi t#2, 8\n"
        "sd a4, [t#1, 0]\n"
        "addi t#2, 8\n"
        "sd a5, [t#1, 0]\n"
        "4:\n"
        ".popsection\n"
        :
        :"r"(data)
        :"s1", "s2", "s3", "s4", "s5", "a3", "a4", "a5", "memory"
    );
}

int main(void) {
    uint64_t data[8] = {0};
    while (true) {
        popMsg((uint64_t *)data);
    }
    return 0;
}
```

## 异步松耦合加速器接口

### 使用方法

下面的汇编展示了一个原子块。

```c
#include <stdint.h>

uint64_t AtomicAddU64Rtn(uint64_t *ptr, uint64_t ullIncr)
{
    uint64_t result;
    __asm__ __volatile__(
        "bstart 1f\n"
        "bget %1, %2\n"
        "bset %0\n"
        "battr atomic.far.aq\n"
        "bstop 2f\n"
        ".pushsection .text.body\n"
        "1:\n"
        "ld [%1, 0]\n"
        "add t#1, %2,->%0\n"
        "sd t#1, [%1, 0]\n"
        "2:\n"
        ".popsection\n"
        :"=&r"(result)
        :"r"(ptr), "r"(ullIncr)
        :"memory");
    return result;
}
```
