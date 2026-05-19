# SSRSET

## 说明

写入系统寄存器(*System Status Register Set*)  
将源寄存器中的值写到 **SSR-ID** 指示的系统寄存器中。

## 汇编语法

```
    ssrset SrcL, SSR-ID
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SSR-ID**：12位系统寄存器索引ID，默认SSR-ID[15:12]为0。映射关系请见[系统寄存器](../../register/ssr/ssrintro.md)介绍章节。

## 编码格式

![SSRSET](../../../figs/bitfield/svg/Instruction_32bit/SSRSET.svg)

SSR-ID的映射表请见[系统寄存器](../../register/ssr/ssrintro.md)介绍。

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 系统寄存器读写：[SSR\[\]](../LibPseudoCode.md)

```c
    integer s = UInt(SrcL);
    integer datawidth = 64;

    SSR[SSR-ID] = R[s, datawidth];
```

## 汇编索引模式

```asm
ssrset a1, SSR-ID     /* 单寄存器绝对索引 */
ssrset t#1, SSR-ID    /* 单寄存器相对索引 */
ssrset u#1, SSR-ID    /* 单寄存器相对索引 */
```

## 注意事项

1. 本指令不占块内私有寄存器槽位。
2. 本指令只能访问SSR-ID[15:12]为0的系统寄存器。
3. 如果访问SSR-ID[15:12]不为0的系统寄存器，需使用48bit的[HL.SSRSET](../misa_h/HL.SSRSET.md)指令。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
