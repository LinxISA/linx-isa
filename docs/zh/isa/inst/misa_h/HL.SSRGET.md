# HL.SSRGET

## 说明

读取系统寄存器(*System Status Register Get*)  
读取 **SSR-ID** 对应系统寄存器中的值并写到目的寄存器中。

## 汇编语法

```asm
    hl.ssrget SSR-ID, ->{t, u, Rd}
```

## 汇编符号

- **SSR-ID**：24位系统寄存器索引ID，映射关系请见[系统寄存器](../../register/ssr/ssrintro.md)介绍章节。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

- 低16bit编码：

![HL.SSRGET](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SSRGET.svg)

- 高32bit编码：

![HL.SSRGET](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SSRGET.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 系统寄存器读写：[SSR\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);

    bits(datawidth) data = SSR[SSR-ID];
    R[d, datawidth] = data;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
hl.ssrget SSR-ID,           ->t 
```

指令输出到块内u寄存器：
```asm
hl.ssrget SSR-ID,           ->u
```

指令输出到全局寄存器R1-R23：
```asm
hl.ssrget SSR-ID,           ->a3
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
