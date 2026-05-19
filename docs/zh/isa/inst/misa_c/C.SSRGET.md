# C.SSRGET

## 说明

读取系统寄存器(*System Status Register Get*)  
读取 ***SSR-ID*** 对应系统寄存器的值并写到目的T寄存器中。

本指令的标准形式请见[SSRGET](../misa_g/SSRGET.md)。

## 汇编语法

```
    c.ssrget SSR-ID, ->t
```

## 汇编符号

- **SSR-ID**：系统寄存器索引编号。
- **->**：用于指示目的寄存器。
- **t**：目的寄存器，代表块内的T寄存器队列。

## 编码格式

![C.SSRGET](../../../figs/bitfield/svg/Instruction_16bit/C.SSRGET.svg)

其中，SSRID字段与系统寄存器映射关系如下：

| SSRID | 系统寄存器 |
|--------|--------------|
| 0 | TP |
| 1 | GP |
| 2 | EBSTATEP |
| others | 保留  |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 系统寄存器读：[SSRRD\[\]](../LibPseudoCode.md)

```c
    bits(64) data = SSRRD[SSR-ID];
    T[id] = data;
```

## 汇编索引模式

```asm
    c.ssrget SSR-ID, ->t    /* 单寄存器索引，可以索引对应的系统寄存器。 */
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
