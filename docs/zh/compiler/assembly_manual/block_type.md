# Block类型伪指令

```
b{.std, .stdc, .fp, .sys, .stdh, .stdch, .fph, .sysh, .sec}
```

用来告诉汇编器块指令的类型，当前伪指令没有操作对象。**缺省默认值是B.STD，如果存在多条块类型的描述符，以最后一条描述符为准**。这类伪指令没有操作数。

| 块指令种类 | 描述        |
|---------------------|------------|
| B.STD   | **标准块指令 Standard Block**，包括全量的标量运算, 编码为32bit定长。无块内跳转。	 |
| B.STDC  | **压缩块指令 Standard Compressed Block**，包括部分标量运算。所有微指令最多2输入，编码为16bit定长。无块内跳转。	|
| B.STDH  | **标准超级块指令 Standard Hyper Block**，标准块指令以外，再包含块内跳转指令，允许块内有控制流。	 |
| B.STDCH | **压缩超级块指令 Standard Compressed Hyper Block**，压缩块指令以外，再包含块内跳转指令，允许块内有控制流。	 |
| B.FP    | **浮点块指令 Floating-point Block**，包括最基本的浮点运算，也包括支持浮点计算的标量运算。支持半精度、单精度和双精度浮点运算。无块内跳转。 |
| B.FPH   | **浮点超级块指令 FP Hyper Block**，浮点块指令中再包含块内跳转指令。	 |
| B.SYS   | **系统块指令 System Block**，包括访问系统寄存器和系统控制以及原子操作指令。 |
| B.SYSH  | **系统超级块指令 System Hyper Block**，系统块指令中再包含块内跳转指令。	 |
| B.SEC   | **安全加解密块指令 Custom Block**，包括所有安全相关的加解密类指令。 |
