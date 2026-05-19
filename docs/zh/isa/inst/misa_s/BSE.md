# BSE

发送事件(*Block Send Event*)  
将左源寄存器中的控制信息写到MSGBCR寄存器。左源寄存器里存储着消息的控制信息，包括消息地址和消息种类，0为不发消息。

本指令提交后当前块指令立即结束执行并提交，因此本指令必须是当前块内的最后一条指令。

## 汇编语法

```
	bse SrcL
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 编码格式

![BSE](../../../figs/bitfield/svg/Instruction_32bit/BSE.svg)

## 发消息汇编

用于发消息的内嵌汇编如下：
```c
static __inline__ void pushMsg(MessageControl *msgCtrl, UINT64 *data)
{
    __asm__ __volatile__(
        "BSTART.SYS FALL\n"
        "B.CATR aqrl\n"
        "ldi [%1, 0],->t\n"
        "ssrset t#1, 0x0831\n"   
        "ldi [%1, 8],->t\n"
        "ssrset t#1, 0x0832\n"
        "ldi [%1, 16],->t\n"
        "ssrset t#1, 0x0833\n"
        "ldi [%1, 24],->t\n"
        "ssrset t#1, 0x0834\n"
        "ldi [%1, 32],->t\n"
        "ssrset t#1, 0x0835\n"
        "ldi [%1, 40],->t\n"
        "ssrset t#1, 0x0836\n"
        "ldi [%1, 48],->t\n"
        "ssrset t#1, 0x0837\n"
        "ldi [%1, 56],->t\n"
        "ssrset t#1, 0x0838\n"
        "ldi [%1, 64],->t\n"
        "ssrset t#1, 0x0839\n"
        "ldi [%1, 72],->t\n"
        "ssrset t#1, 0x083a\n"
        "bse %0\n"
        :
        :"r"(msgCtrl), "r"(data)
        :"memory"
    );
}
```

## 汇编索引模式

```asm
bse a1          /* 单寄存器绝对索引 */
bse t#1         /* 单寄存器相对索引 */
bse u#1         /* 单寄存器相对索引 */
```

!!! note "注意"

    该指令不占用块内私有寄存器。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
