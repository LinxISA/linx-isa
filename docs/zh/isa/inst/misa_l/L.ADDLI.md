# L.ADDLI

## 说明

加立即数(*Add Immediate*)  
将源寄存器值和无符号立即数相加，忽略算数溢出，结果写到目的寄存器中。

## 汇编语法

```
    l.addli SrcL, uimm, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，只可以索引前序最近一条输出至T队列或U队列的指令结果。
- **uimm**：32位立即数，编码于uimm字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![L.ADDLI](../../../figs/bitfield/svg/Instruction_64bit/L.ADDLI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 系统寄存器读写：[SSR\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);

    bits(64) immediate = ZeroExtend(uimm);
    bits(64) result = operand + immediate;

    R[d, 64] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
l.addli a1, uimm,           ->t             /* 单寄存器绝对索引 */
l.addli t#1, uimm,          ->t             /* 单寄存器相对索引 */
l.addli u#1, uimm,          ->t             /* 单寄存器相对索引 */
```
指令输出到块内u寄存器：
```asm
l.addli a1, uimm,           ->u             /* 单寄存器绝对索引 */
l.addli t#1, uimm,          ->u             /* 单寄存器相对索引 */
l.addli u#1, uimm,          ->u             /* 单寄存器相对索引 */
```
指令输出到全局寄存器R1-R23：
```asm
l.addli a1, uimm,           ->a3            /* 单寄存器绝对索引 */
l.addli t#1, uimm,          ->a3            /* 单寄存器相对索引 */
l.addli u#1, uimm,          ->a3            /* 单寄存器相对索引 */
```

## 汇编示例

加载64bit长立即数（例：0xAAAABBBBCCCCDDDD）
```asm
hl.lui 0xAAAABBBB, ->t            # 加载立即数高32bit
l.addli t#1, 0xCCCCDDDD, ->t      # 加载立即数低32bit
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于任意类型的块指令块体中。
