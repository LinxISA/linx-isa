# Universal accelerator HAC interface

The Linxblock instruction set supports accelerator calling and execution in all scenarios. The accelerator and coprocessor **HAC (Hardware Accelerated Coprocessor)** calls are encapsulated into block instruction. Programs built on acceleration blocks, custom blocks, and a large number of scalar blocks are often used for tasks such as data plane processors.


  ![custom_acc](../../figs/uArch/ACC.PNG){ width="800" }


As shown in the figure above, depending on the distance between the block processor and the accelerator, the current Linxblock instruction set supports three accelerator calling methods:

- **A. Synchronous tightly coupled accelerator interface**: Use the 32 global registers of the first layer for transfer. The tightly coupled accelerator is called as a special PE in the block instruction processor. PEs are synchronized through Block Reorder Buffer, so it is a synchronous call model.
- **B. Asynchronous tightly coupled accelerator interface**: Use system register of the system block for communication. After reading and writing system register, the current thread will return immediately without waiting for the accelerator to return data. Therefore, this is an asynchronous calling model.
- **C/D asynchronous loosely coupled accelerator interface**: Use MMU/SMMU for accelerator configuration through address mapping. This is similar to the traditional CPU-DSA interface. The difference is that multiple memory reads and writes are encapsulated into one block and performed uniformly.


In the implementation of the data plane processor based on LinxISA, the block processor interfaces with the accelerator/HAC requirements from different products.
Through the above interface, the block instruction processor has designed a private HAC bus to complete high-concurrency calling and reception of tightly coupled accelerators.
The specific design is shown in the figure below:


  ![sys_intf](../../figs/isa/arch/block-hac-sys.PNG){ width="500" }


## Synchronous tightly coupled accelerator interface

The synchronous tightly coupled accelerator uses the first layer of GPR registers for transfer and calls the accelerator through the customized header.
Each accelerator block can read a maximum of 16 GPR registers and write a maximum of 16 GPR registers. Passing extra parameters may require memory access and is passed through the block-private register.

This interface is suitable for:

- **vector Acceleration Block Vector PE**
- **Matrix acceleration block Matrix PE**
- **Encryption and decryption acceleration block SEC PE**

### Programming model

The following inline assembly shows a programming interface for a tightly coupled accelerator.
```c
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
        "battr aqrl\n"                       //Acquire and Release, 当前加速块为同步调用
        "b.cus\n"                            //定制ZXTERMZH33QXZ
        "bstop custom_stop\n"                //ZXTERMZH39QXZ结束

        ".pushsection \".text.body\",\"ax\"  \n" //ZXTERMZH40QXZ部分起始位置，提示链接器将下面ZXTERMZH40QXZ独立放置
        "custom_start:\n" //定制指令ZXTERMZH40QXZ起始
            ".word 0x10EF2812\n"    //定制指令RAW Binary
            ".word 0xBEAC123A\n"    //定制指令RAW Binary
            ".word 0xDEADBEFF\n"    //定制指令RAW Binary
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

## Asynchronous tightly coupled accelerator interface

The asynchronous tightly coupled accelerator uses system register for information transmission, and the information is transmitted to the accelerator through the **SSRGET/SSRSET** of the system block.
The system block also covers all scalar instructions, so a more complex information processing operation can be completed.

This interface is suitable for:

- **Non-memory mapped accelerator interface**: For example, accelerator configured through system register
- **Private bus RBA memory access HAC**: such as HPOE, QueueManage and other message exchanges
- **Polling Accelerator**

This interface can be used for block processor and private accelerator bus access.

### How to use

The following inline assembly demonstrates the passing of information via system register.

```c
# include <stdint.h>

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

The following shows the operation of a processor Polling.

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

## Asynchronous loosely coupled accelerator interface

### How to use

The assembly below shows an atomic block.

```c
# include <stdint.h>

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