# MCOPY.D

## 说明

内存拷贝(*Memory Copy with DMA*)<br>
从源内存地址的起始位置开始拷贝若干个字节到目标内存地址中。

本模版块指令支持带DMA的内存搬运操作。如果硬件实现不支持DMA指令，则本指令等同于[MCOPY](./MCOPY)。

## 汇编语法

```asm
    MCOPY.D [RegSrc0, RegSrc1, RegSrc2]
```

## 汇编符号

- **RegSrc0**：
    第一层架构寄存器，用于传递目的地址。
- **RegSrc1**：
    第一层架构寄存器，用于传递源内存地址。
- **RegSrc2**：
    第一层架构寄存器，用于传递拷贝字节数。

## 编码格式

![MCOPY.D](../../../figs/bitfield/svg/BlockHeader_32bit/MCOPY.D.svg)

## 执行方式

```c
// 将 RegSrc1 指向的地址，长度为 RegSrc2 的内存块，按字节拷贝到 RegSrc0 指向的内存块中。
for (int i = 0; i < RegSrc2; i++) {
	*(uint8_t*)(RegSrc0 + i) = *(uint8_t*)(RegSrc1 + i);
}
```

## 状态机工作过程

硬件实现时，可以通过模版块状态机（CT-CodeTempalte单元）来产生实际执行的指令序列。并且为了提升内存拷贝的效率，在实际的实现中最大可以 **以64字节** 为单位进行数据搬移。如下是状态机产生指令序列的方式。

首先，模板块状态机通过读取输入寄存器获取执行信息，同时初始化内部参数缓存。
```c
get RegSrc0, ->ct.dstAddr;      /* 状态机的内部缓存，用来存储目的内存地址 */
get RegSrc1, ->ct.srcAddr;      /* 状态机的内部缓存，用来存储源内存地址 */
get RegSrc2, ->ct.count;        /* 状态机的内部缓存，用来记录剩余待拷贝字节数 */
ct.offset = 0;                  /* 状态机的内部缓存，用来记录读写内存地址偏移 */
```

产生指令序列：
```c
    generate(addi RegSrc0, 0, ->u);                   /* 读取目的地址到块内私有U寄存器中 */
    generate(andi RegSrc1, 0, ->u);                   /* 读取源地址到块内私有U寄存器中 */
    // 如果拷贝字节数为0（即ct.count=0），则状态机不会继续产生内存搬运的指令。但是需要生成上面两条指令占位，用作该模板块的块体结束的标志。
    while(ct.count > 0)
    {   
        // 64字节对齐
        if(ct.srcAddr[5:0]==0 && ct.count >= 64) {
            generate(addi u#2, offset, ->u)           /* 更新目的地址 */
            generate(addi u#2, offset, ->u)           /* 更新源地址 */
            generate(dma u#1, u#2)                    /* 状态机更新：ct.count -= 64; offset = 64; ct.srcAddr += 64 */
        }
        // 8字节对齐
        else if(ct.srcAddr[2:0]==0 && ct.count >= 8) {
            generate(ldi.u [u#1, ct.offset], ->t)
            generate(sdi.u t#1, [u#2, ct.offset])     /* 状态机更新：ct.count -= 8; ct.offset += 8; ct.srcAddr += 8 */
        }
        // 4字节对齐
        else if(ct.srcAddr[1:0]==0 && ct.count >= 4) {
            generate(lwi.u [u#1, ct.offset], ->t)
            generate(swi.u t#1, [u#2, ct.offset])    /* 状态机更新：ct.count -= 4; ct.offset += 4; ct.srcAddr += 4 */
        }
        // 2字节对齐
        else if(ct.srcAddr[0]==0 && ct.count >= 2) {
            generate(lhi.u [u#1, ct.offset], ->t)
            generate(shi.u t#1, [u#2, ct.offset])    /* 状态机更新：ct.count -= 2; ct.offset += 2; ct.srcAddr += 2 */
        }
        else {
            generate(lbi.u [u#1, ct.offset], ->t)
            generate(sbi t#1, [u#2, ct.offset])      /* 状态机更新：ct.count -= 1; ct.offset += 1; ct.srcAddr += 1 */
        }
    }
```

实现示意图如下：

![memorycopy](../../../figs/isa/inst/memory_copy_diagram.svg)

## 注意事项

- 本指令要求源地址和目的地址的字节对齐情况是一致的，否则需使用[MCOPY](./MCOPY.md)指令进行内存搬运。
- 本块指令的跳转类型为**顺延（Fall）**。

## 备注

此指令属于模板块指令。

指令的函数原型：
```
void *memcpy(void *destination, void *source, unsigned n)
```
