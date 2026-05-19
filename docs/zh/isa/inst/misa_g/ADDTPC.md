# ADDTPC

## 说明

TPC加高位立即数(*Add TPC with Upper immediate*)  
将 `20位` 立即数有符号扩展并左移 `12位`(低12位置零)后与当前微指令的`TPC`相加，结果写到目的寄存器。

## 汇编语法

```
    addtpc simm, ->{t, u, Rd}
```

## 汇编符号

- **simm**：20位有符号立即数，编码于simm20域。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![ADDTPC](../../../figs/bitfield/svg/Instruction_32bit/ADDTPC.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer datawidth = 64;

    bits(datawidth) simm = SignExtend(simm20);
    bits(datawidth) result = tpc + (simm << 12);
    R[d, datawidth] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
addtpc simm,    ->t         /* 指令输出到块内t寄存器 */
addtpc simm,    ->u         /* 指令输出到块内u寄存器 */
addtpc simm,    ->a3        /* 指令输出到全局寄存器R1-R23 */
```

!!! note "注意"

	此微指令可用于TPC-Relative跳转和寻址。  
    如果结果溢出，则舍弃额外的位。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
