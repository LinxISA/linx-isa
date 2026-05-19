# SSRSWAP

## 说明

系统寄存器交换(*System Status Register Swap*)  
该指令执行如下原子操作：读取 **SSR_ID** 指示的系统寄存器值写入目的寄存器，并将输入寄存器SrcL的值写入该系统寄存器中。

本指令保证整个执行过程是原子的。

## 汇编语法

```
    ssrswap SrcL, SSR-ID, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SSR-ID**：12位系统寄存器索引ID。本系统应根据当前特权级将SSR_ID[15:12]位补齐。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![SSRSWAP](../../../figs/bitfield/svg/Instruction_32bit/SSRSWAP.svg)

SSR-ID的映射表请见[系统寄存器](../../register/ssr/ssrintro.md)介绍。

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 系统寄存器读写：[SSR\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    Atomic {
        bits(datawidth) value_s = SSR[SSR-ID];
        bits(datawidth) value_g = R[s, datawidth];
        SSR[SSR-ID] = value_g;
        R[d, datawidth] = value_s;
    }
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
ssrswap a0, SSR-ID,           ->t        /*单寄存器绝对索引*/
ssrswap t#1, SSR-ID,           ->t        /*单寄存器相对索引*/
ssrswap u#1, SSR-ID,           ->t        /*单寄存器相对索引*/
```

指令输出到块内u寄存器：
```asm
ssrswap a0, SSR-ID,           ->u        /*单寄存器绝对索引*/
ssrswap t#1, SSR-ID,           ->u        /*单寄存器相对索引*/
ssrswap u#1, SSR-ID,           ->u        /*单寄存器相对索引*/
```

指令输出到全局寄存器R1-R23：
```asm
ssrswap a0, SSR-ID,           ->a3        /*单寄存器绝对索引*/
ssrswap t#1, SSR-ID,           ->a3        /*单寄存器相对索引*/
ssrswap u#1, SSR-ID,           ->a3        /*单寄存器相对索引*/
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
