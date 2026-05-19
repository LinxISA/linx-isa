# SSRGET

## 说明

读取系统寄存器(*System Status Register Get*)  
读取 **SSR-ID** 对应系统寄存器中的值并写到目的寄存器中。

## 汇编语法

```
    ssrget SSR-ID, ->{t, u, Rd}
```

## 汇编符号

- **SSR-ID**：12位系统寄存器索引ID，默认SSR-ID[15:12]为0。映射关系请见[系统寄存器](../../register/ssr/ssrintro.md)介绍章节。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![SSRGET](../../../figs/bitfield/svg/Instruction_32bit/SSRGET.svg)

SSR-ID的映射表请见[系统寄存器](../../register/ssr/ssrintro.md)介绍。

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
ssrget SSR-ID,           ->t 
```

指令输出到块内u寄存器：
```asm
ssrget SSR-ID,           ->u
```

指令输出到全局寄存器R1-R23：
```asm
ssrget SSR-ID,           ->a3
```

## 注意事项

1. 本指令只能访问SSR-ID[15:12]为0的系统寄存器。
2. 如果访问SSR-ID[15:12]不为0的系统寄存器，需使用48bit的[HL.SSRGET](../misa_h/HL.SSRGET.md)指令。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
