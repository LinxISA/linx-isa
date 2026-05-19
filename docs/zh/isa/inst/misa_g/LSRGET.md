# LSRGET

## 说明

读取块内状态寄存器(*Local Status Register, Get*)  
读取LSR_ID指定的块参数寄存器[BARG](../../register/common/barg.md)某个字段的内容到目的寄存器中。

## 汇编语法

```
    lsrget LSR_ID, ->{t, u, Rd}
```

## 汇编符号

- **LSR_ID**：块参数寄存器BARG不同字段的ID值。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![LSRGET](../../../figs/bitfield/svg/Instruction_32bit/LSRGET.svg)

其中不同的LSR_ID对应的块参数寄存器如下：

| LSR_ID | BARG域段 | 说明 |
|--------|-----------|----------|
| 0 | BPC | 当前块指令的块头地址，即当前块指令的BPC。 |
| 1 | BPCN | 跳转目标块的块头地址，指示块指令执行完成后的跳转位置。  |
| 1 | LRA | 本地返回地址，用于分离块中返回块头的地址。 （复用BPCN字段）|
| 2 | Others(TYPE，TAKEN，BlockType等) | 其他参数(跳转类型, 跳转条件标志位，陷出标志位等) |
| >= 3 | 暂时保留 | 无 |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer id = UInt(LSR_ID);
    bits(64) data;

    when id == 0 then data = BARG[63:0];      // Current BPC
    when id == 1 then data = BARG[127:64];    // Next BPC 或 LRA
    when id == 2 then data = BARG[191:128];   // 其他内容
    when id >= 3 then undefined;

    R[d, 64] = data;
```

## 汇编索引模式

```asm
lsrget SSR-ID,    ->t      /* 指令输出到块内t寄存器 */
lsrget SSR-ID,    ->u      /* 指令输出到块内u寄存器 */
lsrget SSR-ID,    ->a3     /* 指令输出到全局寄存器R1-R23 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，允许使用在不同块类型块内。
