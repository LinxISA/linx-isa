# MSET

## 说明

内存写入(*Block Memory Set*)  
将某一块内存中的内容全部设置为指定字节的值。

## 汇编语法

```
    MSET [RegSrc0, RegSrc1, RegSrc2]
```

## 编码格式

![MSET](../../../figs/bitfield/svg/BlockHeader_32bit/MSET.svg)

## 汇编符号

- **RegSrc0**：
    第一层架构寄存器，用于传递目的内存地址。
- **RegSrc1**：
    第一层架构寄存器，用于传递内存赋值的数据。
- **RegSrc2**：
    第一层架构寄存器，用于传递内存赋值字节数。

## 执行方式

```c
// 将 RegSrc1 低字节内容，拷贝到 RegSrc0 指向的长度为 RegSrc2 的地址块中。
for (int i = 0; i < RegSrc2; i++) {
    atomic {
        *(uint8_t*)(RegSrc0 + i) = (uint8_t)RegSrc1;
    }
}
```

## 状态机执行

在硬件实现MEMSET指令时，可以不以字节为单位进行写内存操作，而需要根据目的地址的字节对齐情况使用不同粒度的写内存指令进行优化，从而达到更高的执行效率。例如如果写入内存的值为0（即对内存清零操作）且地址是64字节对齐时，硬件可以使用[dc.zva](../../inst/misa_s/DC.ZVA.md)指令对Cacheline进行清零。

### 1. 状态机初始化

首先模板块状态机读取指令输入并初始化ct.addr、ct.data、ct.count和ct.offset等内部缓存，用于根据条件产生相应的指令序列。
```c
ct.addr  = RegSrc0       /* 状态机的内部缓存，用来存储目的地址 */
ct.count = RegSrc2       /* 状态机的内部缓存，用来存储写入内存字节数 */
ct.data  = RegSrc1       /* 状态机的内部缓存，用来存储源数据 */
ct.offset = 0            /* 状态机的内部缓存，用来存储写地址的偏移 */
```
如果内存写字节数为0，则不需要产生任何指令，直接结束该模版块。

### 2. 产生指令序列

```c
    if(ct.count > 0)
    {
        generate(addi RegSrc0, 0, ->t);                       /* 读取目的地址到块内私有T寄存器中 */
        /* 如果待写入内存的值为0，则不需要低字节扩展，且可以一次最长以64byte为单位执行cacheline清零操作 */
        if(ct.data[7:0] == 0)
        {
            while(ct.count > 0)
            {
                if(ct.addr[5:0]==0 && ct.count >= 64) {
                    generate(addi t#1, offset, ->t)           /* 更新地址：offset = 64 */
                    generate(dc.zva t#1)                      /* 状态机更新：ct.count -= 64; ct.addr += 64 */
                }
                else if(ct.addr[2:0]==0 && ct.count >= 8)
                    generate(sdi.u zero, [t#1, ct.offset])    /* 状态机更新：ct.count -= 8; ct.offset += 8; ct.addr += 8 */
                else if(ct.addr[1:0]==0 && ct.count >= 4)
                    generate(swi.u zero, [t#1, ct.offset])    /* 状态机更新：ct.count -= 4; ct.offset += 4; ct.addr += 4 */
                else if(ct.addr[0]==0 && ct.count >= 2)
                    generate(shi.u zero, [t#1, ct.offset])    /* 状态机更新：ct.count -= 2; ct.offset += 2; ct.addr += 2 */
                else
                    generate(sbi zero, [t#1, ct.offset])      /* 状态机更新：ct.count -= 1; ct.offset += 1; ct.addr += 1 */
            }
        }
        else
        {
            // 首先模板块状态机会产生以下指令，将RegSrc1中最低字节数据复制7次。
            generate(hl.bfi RegSrc1, RegSrc1, 8, 8, ->u);   /* 将源数据的低 8位复制到 8至15位, 写到U寄存器队列 */
            generate(hl.bfi u#1, u#1, 16, 16, ->u);         /* 将源数据的低16位复制到16至31位, 写到U寄存器队列 */
            generate(hl.bfi u#1, u#1, 32, 32, ->u);         /* 将源数据的低32位复制到32至63位, 写到U寄存器队列 */

            while(ct.count > 0)
            {
                if(ct.addr[2:0]==0 && ct.count >= 8)
                {
                    if(ct.offset >= 2040)
                        generate(addi t#1, ct.offset, ->t);     /* offset超限，更新地址；重置ct.offset = 0 */
                    generate(sdi.u u#1, [t#1, ct.offset])       /* 状态机更新：ct.count -= 8; ct.offset += 8; ct.addr += 8 */
                }
                else if(ct.addr[1:0]==0 && ct.count >= 4)
                    generate(swi.u u#1, [t#1, ct.offset])       /* 状态机更新：ct.count -= 4; ct.offset += 4; ct.addr += 4 */
                else if(ct.addr[0]==0 && ct.count >= 2)
                    generate(shi.u u#1, [t#1, ct.offset])       /* 状态机更新：ct.count -= 2; ct.offset += 2; ct.addr += 2 */
                else
                    generate(sbi u#1, [t#1, ct.offset])         /* 状态机更新：ct.count -= 1; ct.offset += 1; ct.addr += 1 */
            }
        }
    }
```

根据目的地址ct.dstAddr的字节对齐情况，向内存地址中写入的过程如下图所示：

![BMSET-ByteAlignment](../../../figs/uArch/BMSET.PNG)

- **generate(inst)**: 状态机产生指令并向指令队列内push指令的函数。
```c
    generate(inst){
        while(1){
            if(instBuffer.notFull){
                instBuffer.push(inst);
                update ct.count, ct.offset, ct.addr;
                break;
            }
        }
    }
```

## 注意事项

- 该指令最大设置长度为2^16-1 = 65535 Byte, 超过范围软件通过strip mining循环多次调用。
- 硬件可以对内存设置过程进行加速，最长以Cacheline粒度进行赋值。
- 本块指令的跳转类型为**顺延（Fall）**。

## 备注

该指令属于模板块指令，

指令的函数原型：
```c
void *memset(void *str, int c, size_t n)
```

## 块指令数计算

该块指令展开的微指令数统计过程如下：

```c
    size_t CountNumOfInstrs(uint64 addr = RegSrc0, uint64 data = RegSrc1, uint64 size = RegSrc2)
    {
        size_t instCnt = 1;        /* 指令数：开始会产生1条拷贝寄存器值的指令 */
        if(size == 0) return instCnt;    /* size如果为0，会插入一条bstop指令 */

        if(data[7:0] == 0)
        {
            while(size > 0)
            {
                if(addr[5:0]==0 && size >= 64) instCnt += 2; size -= 64; addr += 64;
                else if(addr[2:0]==0 && size >= 8) instCnt++; size -= 8; addr += 8;
                else if(addr[1:0]==0 && size >= 4) instCnt++; size -= 4; addr += 4;
                else if(addr[0]==0 && size >= 2) instCnt++; size -= 2; addr += 2;
                else instCnt++; size--; addr++;
            }
        }
        else
        {
            instCnt += 3;
            while(size > 0)
            {
                if(addr[2:0]==0 && size >= 8) instCnt++; size -= 8; addr += 8;
                else if(addr[1:0]==0 && size >= 4) instCnt++; size -= 4; addr += 4;
                else if(addr[0]==0 && size >= 2) instCnt++; size -= 2; addr += 2;
                else instCnt++; size--; addr++;
            }
        }
        return instCnt;
    }
```
