# Jump within block

The memory access data block and the vector data block can jump to the specified location through the [scalar jump command] (../scainstrs/branch.md), and the jump range is not allowed to exceed this block body. There are the following 3 jump methods to choose from:

- **Unconditional jump**: Jump directly to the specified location or jump to a relative register offset.
- **Conditional jump**: Determine whether to jump based on the comparison results of two scalar values. It supports comparison conditions such as equality, inequality, greater than and less than.
- **Mask Jump**: Determine whether to jump based on the mask status of [P](../../register/common/pred.md) in the current Group. All-zero jumps and non-all-zero jumps are supported.

## Unconditional jump

The unconditional jump method can jump directly to a specified location or jump to a relative register offset location.

Example:
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

## Conditional jump

The conditional jump method determines whether to jump based on the comparison results of two scalar values.

Example:
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

## Mask jump

The mask jump method determines whether to jump based on the mask status of [P](../../register/common/pred.md) in the current Group.

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

In the above code, if the result of the comparison instruction `l.cmp.lt` is all zeros, which means that all lanes do not take the `if` branch, then the `b.z` instruction can be used to directly jump to the `else` branch for execution to avoid invalid execution.