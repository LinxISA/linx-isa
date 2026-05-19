# 块内跳转

访存数据块和向量数据块内可通过[标量跳转指令](../scainstrs/branch.md)跳转到指定的位置，跳转范围不允许超出本块块体。有以下3种跳转方式提供选择：

- **无条件跳转**：直接跳转到指定位置或者跳转到相对寄存器偏移的位置。
- **条件跳转**：根据两个标量值的比较结果判断是否跳转，支持相等、不等、大于和小于等比较条件。
- **掩码跳转**：根据当前Group内[P](../../register/common/pred.md)的掩码状态判断是否跳转，支持全零跳转和非全零跳转。

## 无条件跳转

无条件跳转方式可以直接跳转到指定位置或者跳转到相对寄存器偏移的位置。

示例：
```asm
VPAR .body, T#1, T#2, ->T<16K>
...
.body:
    inst0
    inst1
    inst2
    j .bar1    # 跳转到.bar1处
    inst3
    inst4
    ...
.bar1:
    instm
    instn
.bar2:
    instx
    insty
    addtpc %tpcrel_hi(.bar2), ->t
    jr t#1, %tpcrel_lo(.bar2)     # 跳转到.bar2处
    ...
```

## 条件跳转

条件跳转方式根据两个标量值的比较结果判断是否跳转。

示例：
```asm
VPAR .body, T#1, T#2, ->T<16K>
...
.body:
    inst0
    inst1
.bar:
    inst2
    inst3
    b.eq a0, t#1, .bar    # 条件成立，跳转到.bar处
    inst4
    ...
```

## 掩码跳转

掩码跳转方式根据当前Group内[P](../../register/common/pred.md)的掩码状态判断是否跳转，

```asm
    inst0
    inst1
    l.addi p, 0, ->u         # 保存P寄存器中掩码         
    l.cmp.lt vt#1.ud, a0, ->p
    l.and p, u#1, ->p        # 根据比较结果重置P
    b.z .else                # P寄存器全0，跳转到.else位置
.if: 
    instm
    instn
    ...
.else:
    instx
    insty
    ...
.converge:
    l.addi u#1, 0, ->p       # 恢复为分支前的掩码
    ...
```

上述代码中，如果比较指令`l.cmp.lt`的结果是全零，表示所有lane都不走`if`分支，那么可通过`b.z`指令直接跳转到`else`分支执行，避免无效执行。
