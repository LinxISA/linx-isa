# B.GE

## 说明

大于等于时跳转(*Branch if Greater Than or Equal by Signed*)  
有符号比较两源操作数，如果左源操作数大于等于右源操作数时，跳转到当前`TPC`加上左移一位的立即数偏移指示的目标地址处；否则，顺序执行。

## 汇编语法

```
    b.ge SrcL, SrcR, label
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **label**：表示条件跳转目标位置的程序标签。它相对于本指令TPC的偏移距离除以2后编码在simm12字段。

## 编码格式

![B.GE](../../../figs/bitfield/svg/Instruction_32bit/B.GE.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) operand1 = R[m, 64];
    bits(64) operand2 = R[n, 64];
    bits(64) simm = SignExtend(simm12);
    bits(64) offset = simm << 1;
    
    TPC += (operand1 >=(s) operand2 ? offset : 4);
```

## 汇编索引模式

```asm
b.ge a1, a2, label       /* 双寄存器绝对索引 */
b.ge a1, t#2, label      /* 双寄存器混合索引 */
b.ge a1, u#2, label      /* 双寄存器混合索引 */
b.ge t#1, a2, label      /* 双寄存器混合索引 */
b.ge t#1, t#2, label     /* 双寄存器相对索引 */
b.ge t#1, u#2, label     /* 双寄存器相对索引 */
b.ge u#1, a2, label      /* 双寄存器混合索引 */
b.ge u#1, t#2, label     /* 双寄存器相对索引 */
b.ge u#1, u#2, label     /* 双寄存器相对索引 */
```

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于向量Tile块、并行Tile块和访存Tile块的块体中。

<!-- !!! info 块内跳转限制

	块内跳转目前不能跳出块指令标定的范围【TPC.START】和【TPC.START + BSize * 4】。块指令的最后一条指令为【TPC.START + BSize * 4】所指的指令。

!!! info 原子块指令限制

	由于原子块内不允许块内循环，因此原子块指令不允许回跳指令，块内跳转无法回跳，因此signed imm不能为负数。

!!! note "注意"

    如果块指令的最后一条指令是B.GE，那么该指令提交后，当前块指令提交，块内跳转不生效。 -->
