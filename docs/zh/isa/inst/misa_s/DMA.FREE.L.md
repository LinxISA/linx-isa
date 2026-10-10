# DMA.FREE.L

## 说明

直接内存存取·释放·长(*Direct Memory Access, Free, Long*)<br>
释放由源寄存器 `SrcL` 指示的地址所关联的 长周期 DMA 传输资源（描述符与缓冲）。该指令在提交前完成释放动作。

## 汇编语法

```asm
    dma.free.l [SrcL]
```

## 汇编符号

- **SrcL**：源寄存器，用于存储被释放 DMA 资源所关联的地址。可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。

## 指令编码

![DMA.FREE.L](../../../figs/bitfield/svg/Instruction_32bit/DMA.FREE.L.svg)

!!! note "编码说明"

    本指令复用 DMA 子类槽（`14..12=111`），以 `31..25` 中的保留选择子区分变体：`0000010`=FREE.S、`0000011`=FREE.L，`24..20` 固定为 0。

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer l = UInt(SrcL);

    bits(64) address = R[l, 64];

    /* 释放与 address 关联的 长周期 DMA 传输资源 */
    DMAFree(address, Long);
```

## 备注

- 本指令属于系统块指令集，仅允许在系统块内使用。
- 本指令没有目的寄存器，不占用块内私有寄存器。
- 与 [DMA](DMA.md) 使用不同的 `31..25` 选择子，二者解码互不冲突。
