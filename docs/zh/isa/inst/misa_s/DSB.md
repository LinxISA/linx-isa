# DSB

## 说明

同步内存和I/O(*Fence Memory and I/O*)  
该指令用于同步数据流，在后序指令中的内存和 I/O 访问对外部可见之前，使这条指令之前的内存及 I/O 访问对外部可见。

## 汇编语法

	dsb pred_imm, succ_imm

## 编码格式

![DSB](../../../figs/bitfield/svg/Instruction_32bit/DSB.svg)

SUCC_IMM和PRED_IMM字段从高位到低位分别对应于如下参数。

| bit[3] |  bit[2] | bit[1] | bit[1] |
|--------|---------|--------|---------|
| 设备输入(i) | 设备输出(o) | 内存读取(r) | 内存写入(w) |

## 汇编符号

- **pred_imm**：4bit立即数，用于标识前序指令内存和 I/O 访问同步约束。
- **succ_imm**：4bit立即数，用于标识后序指令内存和 I/O 访问同步约束。

pred_imm和succ_imm可使用的汇编符号包括：w, r, rw, o, ow, or, orw, i, iw, ir, irw, io, iow, ior, iorw。

## 执行方式

```c
    Fence(pred_imm, succ_imm)
```

## 示例

```asm
    dsb ow, i       ; 将前序指令的I/O输出和内存写与后序指令的I/O输入进行排序
    dsb iorw, iorw  ; 对所有访存请求进行排序
```

!!! note "注意"

    该指令不占用块内私有寄存器。

## 约束

本指令属于系统块指令集，仅允许在系统块内使用。
