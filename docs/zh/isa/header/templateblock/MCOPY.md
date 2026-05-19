# MCOPY

## 说明

内存拷贝(*Block Memory Copy*)  
从源内存地址的起始位置开始拷贝若干个字节到目标内存地址中。

## 汇编语法

```asm
    MCOPY [RegSrc0, RegSrc1, RegSrc2]
```

## 汇编符号

- **RegSrc0**：
    第一层架构寄存器，用于传递目的地址。
- **RegSrc1**：
    第一层架构寄存器，用于传递源内存地址。
- **RegSrc2**：
    第一层架构寄存器，用于传递拷贝字节数。

## 编码格式

![MCOPY](../../../figs/bitfield/svg/BlockHeader_32bit/MCOPY.svg)

## 执行方式

```c
// 将 RegSrc1 指向的地址，长度为 RegSrc2 的内存块，按字节拷贝到 RegSrc0 指向的内存块中。
for (int i = 0; i < RegSrc2; i++) {
	*(uint8_t*)(RegSrc0 + i) = *(uint8_t*)(RegSrc1 + i);
}
```

## 块体指令序列

硬件实现时，可以通过模版块状态机（CT-CodeTempalte单元）来产生实际执行的指令序列。并且为了提升内存拷贝的效率，在实际的实现中最大可以以8字节为单位进行数据搬移。如下是状态机产生指令序列的方式。

首先，模板块状态机通过读取输入寄存器获取执行信息，同时初始化内部参数缓存。
```c
get RegSrc0, ->ct.dstAddr;      /* 状态机的内部缓存，用来存储目的内存地址 */
get RegSrc1, ->ct.srcAddr;      /* 状态机的内部缓存，用来存储源内存地址 */
get RegSrc2, ->ct.ldCnt;        /* 状态机的内部缓存，用来记录内存拷贝字节数 */
ct.stCnt = 0;        /* 状态机的内部缓存，用来记录已从源地址加载但未写入目的地址的字节数 */
ct.ldot = 0;         /* 状态机的内部缓存，用来记录读内存地址偏移 */
ct.stot = 0;         /* 状态机的内部缓存，用来记录写内存地址偏移 */
ct.vld = 0;          /* 状态机的内部缓存，用来记录进入第三个阶段前的阶段中，最后是否有8字节写内存，如果有则置为1 */
```

如果输入寄存器指示的拷贝字节数为0（即ct.ldCnt=0），状态机则不会继续产生内存搬运指令。但是需要生成以下指令占位，用作该模板块的块体结束的标志。

```c
generate(andi RegSrc1, 0, ->u);
generate(addi RegSrc0, 0, ->u);
```

实现方案如下：

在产生搬移指令前需要注意的是，源地址和目的地址的起始位置会有六种不同的字节对齐情况。每种场景下，我们都希望使用尽可能少的指令序列完成数据搬移，因此产生的指令序列有所不同。源和目的地址对齐情况如下所示：

![address-align](../../../figs/isa/inst/address_align.png){ width="600" }

为了更清晰地展示搬移过程，下面将整个过程分三个阶段介绍：

- 第一阶段：处理源和目的起始地址非8字节对齐情况下数据的搬移。
- 第二阶段：处理源和目的地址8字节对齐后数据的搬移，该阶段内存读写都是以8字节为单位操作的。
- 第三阶段：处理最后剩余的不足8字节的内存写。

当然，这三个阶段不一定都会执行的。如果源和目的起始地址都是8字节对齐的，那么则不需要执行第一阶段；如果第一阶段就已经将指定的所有数据加载完，则不需要执行第二阶段。如果第一阶段也已经完成数据搬移，则不需要执行第二、三阶段。因此，每个阶段都需要有条件地执行，状态机应按照执行条件严格执行。

<!-- 
![memcopy](../../../figs/uArch/memcopy.png){ width="400" }
 -->

**第一阶段**

该阶段的作用是处理源或目的起始地址的非8字节对齐部分，共分为六种场景。

展开的指令序列如下：
```c
/* 源和目的起始地址字节对齐相同的场景，分为：1.都是8字节对齐的；2.不是8字节对齐的 */
if(srcAddr[2:0] == dstAddr[2:0])
{
    /* 如果源和目的地址不是8字节对齐的，则进行非8字节对齐部分的搬移 */
    if(dstAddr[2:0] != 0)
    {
        generate(andi RegSrc0, 0xff8, ->u);  /* 将目的地址低三位置为0 */
        generate(ldi.u [u#1, 0], ->t);       /* 从目的地址前8字节对齐处加载8字节数据 */
        generate(andi RegSrc1, 0xff8, ->u);  /* 将源地址低三位置为0 */
        generate(ldi.u [u#1, 0], ->t);       /* 更新:ct.ldot+=8; ct.stCnt+=min(8-srcAddr[2:0], ct.ldCnt); ct.ldCnt-=ct.stCnt */
        generate(srli t#1, ct.srcAddr[2:0]*8, ->t);    /* 将从源地址加载的数据移至寄存器低位 */
        generate(hl.bfi t#3, t#1, dstAddr[2:0]*8, stCnt*8, ->t);    /* 将源有效数据拼接在目的有效数据高位 */
        generate(sdi.u t#1, [u#2, ct.stot]);         /* 将拼接后的数据写到目的地址，更新:ct.stot+=8, ct.stCnt=0 */
    }
    /* 如果源和目的地址是8字节对齐的，则第一阶段不需要产生指令 */
    else{}
}
/* 源地址低三位大于目的地址低三位的场景，分为：1.目的起始地址是8字节对齐的；2.目的起始地址不是8字节对齐的 */
else if(srcAddr[2:0] > dstAddr[2:0])
{
    /* 如果目的起始地址不是8字节对齐的，则需要从目的地址加载一次数据，拼接后写到目的地址 */
    if(ct.dstAddr[2:0] != 0)
    {
        generate(andi RegRrc0, 0xff8, ->u);    /* 将目的地址低三位置为0 */
        generate(andi RegSrc1, 0xff8, ->u);    /* 将源地址低三位置为0 */
        generate(ldi.u [u#1, 0], ->t);     /* 更新:ct.ldot+=8; ct.stCnt+=min(8-srcAddr[2:0], ct.ldCnt); ct.ldCnt-=ct.stCnt */
        generate(ldi.u [u#2, 0], ->t);     /* 从目的地址前8字节对齐处加载8字节数据 */

        if(ldCnt > 0)
        {
            generate(ldi.u [u#1, ct.ldot], ->t);    /* 更新:ct.ldot+=8; ct.stCnt+=min(8, ct.ldCnt); ct.ldCnt-=min(8, ct.ldCnt) */
            generate(hl.ccat t#1, t#3, shamt, ->t);  /* 拼接连续两次加载的数据并移位：shamt=64-srcAddr[2:0]*8；隐含T寄存器输出 */
            generate(addi t#2, 0, ->t);             /* 拷贝一次源内存加载的数据，用于后序hl.ccat指令索引 */
            generate(hl.bfi t#4, t#2, dstAddr[2:0]*8, N*8, ->t);    /* 将源有效数据拼接在目的有效数据高位：N=min(8-ct.dstAddr[2:0], ct.stCnt) */
            generate(sdi.u t#1, [u#2, ct.stot]);    /* 更新:ct.stot+=8; ct.stCnt-=min(8-ct.dstAddr[2:0], ct.stCnt); ct.vld=1 */
        }
        else
        {
            generate(srli t#2, ct.srcAddr[2:0]*8, ->t);    /* 将从源地址加载的数据移至寄存器低位 */
            generate(hl.bfi t#2, t#1, dstAddr[2:0]*8, N*8, ->t);    /* 将源有效数据拼接在目的有效数据高位：N=min(8-ct.dstAddr[2:0], ct.stCnt) */
            generate(sdi.u t#1, [u#2, ct.stot]);         /* 更新:ct.stot+=8; ct.stCnt-=min(8-ct.dstAddr[2:0], ct.stCnt) */
        }
    }
    /* 如果目的起始地址是8字节对齐的，则直接向目的地址搬移数据 */
    else
    {
        generate(addi RegSrc, 0, ->u);        /* 拷贝一次目的地址，保证后序store索引为u#2 */
        generate(andi RegSrc, 0xff8, ->u);    /* 将源地址低三位置为0 */
        generate(ldi.u [u#1, 0], ->t);     /* 更新:ct.ldot+=8; ct.stCnt+=min(8-srcAddr[2:0], ct.ldCnt); ct.ldCnt-=ct.stCnt */

        if(ldCnt <= 0)
            generate(srli t#1, ct.srcAddr[2:0]*8, ->t);  /* 将从源地址加载的数据移至寄存器低位 */
        else
            generate(addi zero, 0, ->t);   /* 添加一个占位指令 */
    }
}
/* 源地址低三位小于目的地址低三位的场景，分为：1.源起始地址是8字节对齐的；2.源起始地址不是8字节对齐的 */
else
{
    if(srcAddr[2:0] != 0)
    {
        generate(andi RegSrc0, 0xff8, ->u);    /* 将目的地址低三位置为0 */
        generate(ldi.u [u#1, 0], ->t);     /* 从目的地址前8字节对齐处加载8字节数据 */
        generate(andi RegSrc1, 0xff8, ->u);    /* 将源地址低三位置为0 */
        generate(ldi.u [u#1, 0], ->t);     /* 更新:ldot+=8; stCnt+=min(8-srcAddr[2:0], ldCnt); ldCnt-=stCnt */
        generate(srli t#1, srcAddr[2:0]*8, ->t);    /* 将从源地址加载的有效数据右移到低位 */
        generate(addi t#2, 0, ->t);        /* 为了后面hl.ccat索引距离固定，拷贝一次源地址加载的值 */
        generate(hl.bfi t#4, t#2, dstAddr[2:0]*8, N*8, ->t);    /* N=min(8-dstAddr[2:0], stCnt) */
        generate(sdi.u t#1, [u#2, stot]);   /* 更新:stot+=8; stCnt-=min(8-dstAddr[2:0], stCnt); vld=1 */
    }
    else
    {
        generate(andi RegSrc0, 0xff8, ->u);    /* 将目的地址低三位置为0 */
        generate(ldi.u [u#1, 0], ->t);         /* 从目的地址前8字节对齐处加载8字节数据 */
        generate(addi RegSrc1, 0, ->u);        /* 拷贝一次源地址，保证后面索引为u#2 */
        generate(ldi.u [u#1, 0], ->t);         /* 更新:ldot+=8; stCnt+=min(8-srcAddr[2:0], ldCnt); ldCnt-=stCnt */
        generate(hl.bfi t#2, t#1, dstAddr[2:0]*8, N*8, ->t);  /* N=min(8-dstAddr[2:0], stCnt) */
        generate(sdi.u t#1, [u#2, stot]);    /* 更新:stot+=8; stCnt-=min(8-dstAddr[2:0], stCnt); vld=1 */
    }
}
```

**第二阶段**

该阶段是内存拷贝的最主要部分，大量的数据拷贝都是在该阶段完成。

通过第一阶段，状态机已经处理完地址非8字节对齐部分的数据拷贝工作，因此进入第二阶段我们认为地址已经8字节对齐了。

- 进入该阶段的条件是：原地址和目的地址是8字节对齐的，并且当前还有数据没有加载回来。
- 退出该阶段的条件是：所有数据已经加载到临时T寄存器，并且未写到目的地址的数据小于8字节。
- 处在该阶段的状态时：状态机循环产生 `数据加载load`-`<数据移位concat>`-`数据写store`的指令序列。

```c
    while (ldCnt > 0)
    {
        vld = 0;    /* 每次迭代前将该轮内存写标志位置0 */
        // 加载一次8字节
        generate(ldi.u [u#1, ldot], ->t);    /* 更新:ldot+=8; stCnt+=min(8, ldCnt); ldCnt-=min(8, ldCnt) */

        // 使用上一阶段或上一次迭代加载的数据与当前迭代加载的数据进行拼接移位，得到最早应该写出的数据。
        if (srcAddr[2:0] > dstAddr[2:0]) {
            generate(hl.ccat t#1, t#3, shamt, ->t);    /* shamt = 64-(srcAddr[2:0]-dstAddr[2:0])*8 */
        }
        else if (srcAddr[2:0] < dstAddr[2:0]) {
            generate(hl.ccat t#1, t#3, shamt, ->t);    /* shamt = (dstAddr[2:0]-srcAddr[2:0])*8 */
        }

        // 如果前面加载的数据或拼接移位后待写出的数据够8个字节，则写到目的地址
        if (stCnt >= 8){
            generate(sdi.u t#1, [u#2, stot]);    /* 更新:stot+=8; stCnt-=8;vld=1 */
        }

        // 更新寻址偏移，防止offset超限
        if (ldot >= 2032) {
            generate(addi u#2, stot, ->u);    /*  更新内存写寻址偏移: stot = 0 */
            generate(addi u#2, ldot, ->u);    /*  更新内存读寻址偏移: ldot = 0 */
        }
    }
```

**第三阶段**

该阶段用于完成最后剩余的不足8个字节的数据的写内存。

进入该阶段前，状态机已经产生将数据加载到T寄存器的指令。因此在当前阶段，只需要根据剩余的字节数，产生不同的写内存指令序列即可。当然，无论使用哪条store指令，都需要从寄存器低位获取对应位宽的数据。因此如果多次从一个T寄存器中获取数据并写内存，需要提前将有效数据移至寄存器低位，因此该阶段插入了一些必要的**移位指令srli**。

```c
    if(stCnt > 0)
    {
        // 如果前一阶段的最后一步，有完整8字节的数据写出，那么剩余未写出的数据目前在t#2寄存器中且不在低位，所以需要将寄存器中有效数据右移至低位；
        // 如果前一阶段的最后一步，没有完整8字节的数据写出，那么剩余未写出的数据目前在t#1寄存器中且在低位，所以不需要移位。
        if(vld == 1){
            // if(srcAddr[2:0] < dstAddr[2:0]) imm = 64 - (dstAddr[2:0] - srcAddr[2:0]) * 8; 
            // if(srcAddr[2:0] > dstAddr[2:0]) imm = (srcAddr[2:0] - dstAddr[2:0]) * 8;
            generate(srli t#2, imm, ->t);
        }
        switch(stCnt) {
            case 1:
                generate(sbi t#1, [u#2, stot]);    /* stot += 1 */
                break;
            case 2:
                generate(shi.u t#1, [u#2, stot]);  /* stot += 2 */
                break;
            case 3:
                generate(shi.u t#1, [u#2, stot]);  /* stot += 2 */
                generate(srli t#1, 16, ->t);
                generate(sbi t#1, [u#2, stot]);    /* stot += 1 */
                break;
            case 4:
                generate(swi.u t#1, [u#2, stot]);  /* stot += 4 */
                break;
            case 5:
                generate(swi.u t#1, [u#2, stot]);  /* stot += 4 */
                generate(srli t#1, 32, ->t);
                generate(sbi t#1, [u#2, stot]);    /* stot += 1 */
                break;
            case 6:
                generate(swi.u t#1, [u#2, stot]);  /* stot += 4 */
                generate(srli t#1, 32, ->t);
                generate(shi.u t#1, [u#2, stot]);  /* stot += 2 */
                break;
            case 7:
                generate(swi.u t#1, [u#2, stot]);  /* stot += 4 */
                generate(srli t#1, 32, ->t);
                generate(shi.u t#1, [u#2, stot]);  /* stot += 2 */
                generate(srli t#1, 16, ->t);
                generate(sbi t#1, [u#2, stot]);    /* stot += 1 */
                break;
            default: break;
        }
    }
```

## 注意事项

- 源和目的地址范围之间不能有重叠部分，以8 Byte为单位。 
- 最大搬移长度65535字节，超过范围软件通过strip mining循环多次调用。
- 本块指令的跳转类型为**顺延（Fall）**。

## 备注

此指令属于模板块指令。

指令的函数原型：
```
void *memcpy(void *destination, void *source, unsigned n)
```

该模版块指令展开的微指令数计算公式为：
```c
instCount = 3 + RegSrc2 / 8 * ((|RegSrc1 - RegSrc0|) % 8 != 0 ？3 ：2) + RegSrc2 % 8;
```
