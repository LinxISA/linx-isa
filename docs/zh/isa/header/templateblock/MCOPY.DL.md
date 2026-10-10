# MCOPY.DL

## 说明

内存拷贝·DL访存模式(*Block Memory Copy, DL Access Mode*)
以DL访存模式完成与 [MCOPY](MCOPY.md) 相同的内存拷贝：从源内存地址的起始位置开始拷贝若干个字节到目标内存地址中，并将完成状态写入目的寄存器。

## 汇编语法

```asm
    MCOPY.DL [RegSrc0, RegSrc1, RegSrc2], ->{t, u, Rd}
```

## 汇编符号

- **RegSrc0**：第一层架构寄存器，用于传递目的地址。
- **RegSrc1**：第一层架构寄存器，用于传递源内存地址。
- **RegSrc2**：第一层架构寄存器，用于传递拷贝字节数。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。拷贝完成状态（如已完成字节数）写入该目的寄存器。

## 编码格式

![MCOPY.DL](../../../figs/bitfield/svg/BlockHeader_32bit/MCOPY.DL.svg)

!!! note "编码说明"

    本指令与 [MCOPY](MCOPY.md) 共享 `RegSrc0/1/2` 布局，通过 `26..25` 访存模式位区分：`00`=MCOPY、`01`=MCOPY.DS、`11`=MCOPY.DL；并以 `14..12=001` 与 `11..7=RegDst` 携带目的寄存器。

## 执行方式

```c
// 以DL访存模式，将 RegSrc1 指向的地址，长度为 RegSrc2 的内存块，
// 按字节拷贝到 RegSrc0 指向的内存块中，并将完成状态写入 RegDst。
status = MCOPYWithMode(RegSrc0, RegSrc1, RegSrc2, MODE_DL);
R[RegDst] = status;
```

块体指令序列与 [MCOPY](MCOPY.md) 一致，由模版块状态机产生；仅访存模式与状态写回不同。

## 注意事项

- 源和目的地址范围之间不能有重叠部分，以8 Byte为单位。
- 最大搬移长度65535字节，超过范围软件通过strip mining循环多次调用。
- 本块指令的跳转类型为**顺延（Fall）**。

## 备注

此指令属于模板块指令。
