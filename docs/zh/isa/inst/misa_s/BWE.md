# BWE

## 说明

等待事件(*Block Wait for Event*)  
指示处理器当前线程进入休眠状态，直到有外部事件被送到当前线程进行唤醒。

本指令提交后当前块指令立即结束执行并提交，因此本指令必须是当前块内的最后一条指令。

## 汇编语法

```
    bwe SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![BWE](../../../figs/bitfield/svg/Instruction_32bit/BWE.svg)

## 轻核子系统自定义事件

以下是轻核子系统的自定义事件，其他系统可定义自己的事件列表：

- **事件1：** HPOE事件， Hierachical Packet Order Enforcer事件，用于系统调度器的事件。
- **事件2：** RBA事件， Request Bus Arbiter事件, 用于等待和加速器调用的信号事件。
- **事件3：** L2 Cache回填事件，L2 Cache Refill事件, 用于等待数据回填Cache。

## 汇编示例

```c
static __inline__ void popMsgQm(UINT64 *data)
{
    __asm__ __volatile__(
        "BSTART.SYS FALL\n"
        "B.CATR aqrl\n"
        "ssrget 0x0831, ->t"
        "sdi t#1, [%0, 0]\n"
        "ssrget 0x0832, ->t"
        "sdi t#1, [%0, 8]\n"
        "ssrget 0x0833, ->t"
        "sdi t#1, [%0, 16]\n"
        "ssrget 0x0834, ->t"
        "sdi t#1, [%0, 24]\n"
        "ssrget 0x0835, ->t"
        "sdi t#1, [%0, 32]\n"
        "ssrget 0x0836, ->t"
        "sdi t#1, [%0, 40]\n"
        "ssrget 0x0837, ->t"
        "sdi t#1, [%0, 48]\n"
        "ssrget 0x0838, ->t"
        "sdi t#1, [%0, 56]\n"
        "ssrget 0x0839, ->t"
        "sdi t#1, [%0, 64]\n"
        "ssrget 0x083a, ->t"
        "sdi t#1, [%0, 72]\n"
        "BSTOP\n"
        :
        :"r"(data)
    );
}
```

## 汇编索引模式

```asm
bwe a1          /* 单寄存器绝对索引 */
bwe t#1         /* 单寄存器相对索引 */
bwe u#1         /* 单寄存器相对索引 */
```

!!! note "注意"

    该指令不占用块内私有寄存器。  
    该指令是一条带有休眠作用的bstop指令。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
