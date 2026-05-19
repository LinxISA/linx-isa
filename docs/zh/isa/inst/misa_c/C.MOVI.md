# C.MOVI

## 说明

立即数移动(*Move Immediate*)  
将符号扩展的立即数移动到目的寄存器中。

## 汇编语法

```c
    c.movi simm, ->{t, u, Rd}
```

## 汇编符号

- **simm**：5位有符号立即数。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23，但不包含R10(ra)。

## 编码格式

本指令与[C.SETRET](./C.SETRET.md)指令复用编码，其中RegDst域不能编码为ra。

![c.movi](../../../figs/bitfield/svg/Instruction_16bit/C.MOVI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer DataWidth = 64;

    bits(DataWidth) simm = SignExtend(simm5);

    if d != 10 then             // RegDst域不能编码为ra。
        R[d, DataWidth] = simm;
```

## 汇编索引模式

- 指令输出到块内T寄存器
```asm
    c.movi  simm,  ->t
```

- 指令输出到块内U寄存器
```asm
    c.movi  simm,  ->u
```

- 指令输出到全局R1-R23寄存器，但不包含R10(ra)
```asm
    c.movi  simm,  ->a3
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
