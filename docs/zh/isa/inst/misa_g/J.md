# J

## 说明

块内无条件跳转 (*Jump*)  
无条件地跳转到当前指令`TPC`加上左移一位的立即数偏移指示的目标地址处。

## 汇编语法

```
    j label
```

## 汇编符号

- **label**：表示跳转目标位置的程序标签。它相对于本指令TPC的偏移距离除以2后编码在simm22字段。

## 编码格式

![J](../../../figs/bitfield/svg/Instruction_32bit/J.svg)

## 执行方式

- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
	bits(64) offset = SignExtend(simm22);
    TPC += (offset << 1);
```

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于向量Tile块、并行Tile块和访存Tile块的块体中。

<!-- 
!!! info 块内跳转限制

	块内跳转目前不能跳出块指令标定的范围【TPC.START】和【TPC.START + BSize * ISize】。块指令的最后一条指令为【TPC.START + BSize * ISize】所指的指令。  
	32bit编码格式下，ISize为4；16bit编码格式下，ISize为2。

!!! info 原子块指令限制

	由于原子块内不允许块内循环，因此原子块指令不允许回跳指令，块内跳转无法回跳，因此offset不能为负数。

!!! note "注意"

	如果块指令的最后一条指令是J，那么在J指令提交后，当前块指令提交，块内跳转不生效。
 -->
