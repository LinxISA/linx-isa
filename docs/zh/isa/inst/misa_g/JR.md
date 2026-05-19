# JR

## 说明

无条件寄存器跳转 (*Jump Register*)  
无条件跳转至源寄存器内`TPC`加左移一位的立即数偏移指示的目标地址处。

## 汇编语法

```
    jr SrcL, label
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **label**：表示跳转目标位置的程序标签。它相对于本指令TPC的偏移距离除以2后编码在simm12字段。

## 编码格式

![JR](../../../figs/bitfield/svg/Instruction_32bit/JR.svg)

## 执行方式

- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer s = UInt(SrcL);

    bits(64) curtpc = R[s, 64];
    bits(64) offset = SignExtend(simm12);
    TPC = curtpc + (offset << 1);
```


## 汇编索引模式

```asm
jr a1, label       /* 单寄存器绝对索引 */
jr t#1, label      /* 单寄存器相对索引 */
jr u#1, label      /* 单寄存器相对索引 */
```

## 汇编示例

如果需要跳转到一个symbol所在的位置，且j指令偏移的编码不足，可以使用addtpc和jr完成。

```c
label:
   ......

addtpc %tpcrel_hi(label), ->t
jr t#1, %tpcrel_lo(label)
```

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于向量Tile块、并行Tile块和访存Tile块的块体中。

<!-- !!! info 块内跳转限制

	块内跳转目前不能跳出块指令标定的范围【TPC.START】和【TPC.START + BSize * ISize】。块指令的最后一条指令为【TPC.START + BSize * ISize】所指的指令。  
    32bit编码格式下，ISize为4；16bit编码格式下，ISize为2。

!!! info 原子块指令限制

	由于原子块内不允许块内循环，因此原子块指令不允许回跳指令，块内跳转无法回跳，因此offset不能为负数。

!!! note "注意"

    如果块指令的最后一条指令是JR，那么在JR指令提交后，当前块指令提交，块内跳转不生效。 -->
