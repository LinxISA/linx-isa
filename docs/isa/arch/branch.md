# Jump method

In LinxISA, flexible management of control flow is the key to achieving efficient parallel computing. block instruction provides 7 different jump methods, each method is designed for specific scenarios, and together they build a complete control flow system.

## Jump method classification

| Jump type | Function description | Target address | Usage scenarios |
|----------------|---------|----------|--------------|
| **Fall** | Execute the next block instruction sequentially | The first address of the next delayed block | Default execution process |
| **Direct** | Jump directly to the specified label position | Jump directly to the target `label` | Unconditional jump, loop control |
| **Call** | Call subroutine and save return address | Call target header address `label` | Function call, code reuse |
| **Cond** | Determine whether to jump based on the conditional judgment result | Fork target header address `label` | Conditional branch, if-else logic |
| **Ind** | Indirectly jump to the dynamically calculated target address through the register value | Indirect target header address | Jump table, dynamic scheduling |
| **Icall** | Indirectly call subroutine through register value | Indirect target header address | Function pointer, polymorphic call |
| **Ret** | Return from subroutine call to call point | Indirect target header address | Function return, call stack management |

## <span id="branch">Details</span>

### 1. Fall (delayed execution)

- Features: Default execution mode, no explicit jump instructions
- Behavior: execute the next instruction sequentially

Usage scenarios:
```asm
.block0: 
    BSTART.STD FALL
    inst0
    inst1
    ...
    instx
.block1: 
    BSTART.SYS FALL  # 执行完.block0，顺序执行.block1
    ...
```

### 2. Direct (direct jump)

- Features: Absolute address jump
- Instruction format: `BSTART.BType DIRECT, <label>`

Usage scenarios:
```asm
.block0: 
    BSTART.STD DIRECT, .block2
    inst0
    inst1
    ...
    instx
.block1: 
    BSTART.SYS FALL
    ...
.block2:
    BSTART.VPAR FALL
    ...
```

### 3. Call

- Feature: atomically retire the current block, install a direct-call BARG,
  and write the explicit return target to `ra`.
- Instruction format: `BSTART.CALL <br_label>, <rt_label>, ->ra`

Usage scenarios:
```asm
.block0: 
    BSTART.CALL .block2, .block1, ->ra
.block1: 
    BSTART.SYS FALL
    ...
.block2:
    BSTART.VPAR FALL
    ...
```

`br_label` and `rt_label` are independent PC-relative operands. The operation
does not require or permit a separate `SETRET` to supply its return target.

### 4. Cond (conditional jump)

- Features: Determine whether to jump based on the conditional judgment result of the `setc.cond` instruction in the block. If not, the execution of the next block will be postponed.
- Constraints: It cannot be an empty block. **The block must contain a setc.cond instruction**.

Usage scenarios:
```asm
.block0: 
    BSTART.STD COND, .block2   
    inst0
    setc.eq a0, t#1     # 判断a0和t#1是否相等，决定是否跳转到block2
    ...
    instx
.block1:
    BSTART.SYS FALL
    ...
.block2:
    BSTART.VPAR FALL
    ...
```

### 5. Ind (indirect jump)

- Features: The target address comes from the calculation result within the block
- Constraints: It cannot be an empty block. **The block must contain a setc.tgt instruction**.

Usage scenarios:
```asm
.block0: 
    BSTART.STD IND
    inst0
    add a0, t#1, ->t
    setc.tgt t#1       # 设置跳转目标地址
    ...
    instx
.block1:
    BSTART.SYS FALL
    ...
.block2:
    BSTART.VPAR FALL
    ...
```

### 6. Icall (indirect call)

- Features: atomically retire an active STD or FP block, snapshot that block's
  `BARG.BPCN` as the indirect call target, and write the explicit return label
  to `ra`.
- Instruction format: `BSTART.ICALL <rt_label>, ->ra`
- Constraints: the retiring block must have a valid STD/FP BARG and an aligned
  `BPCN`. The instruction does not read `SETC.TGT` and does not require a
  separate `SETRET`.

Usage scenarios:
```asm
.block0: 
    BSTART.STD DIRECT, .block2  # establishes the retiring BARG.BPCN
    ...
    instx
    BSTART.ICALL .block1, ->ra  # snapshots BPCN and writes the return target
.block1:
    BSTART.SYS FALL
    ...
.block2:
    BSTART.VPAR FALL
    ...
```

### 7. Ret (call return)

- Feature: Restore calling context
- Constraints: It cannot be an empty block. **The block must contain a setc.tgt instruction**.

Usage scenarios:
```asm
.block0: 
    BSTART.STD RET
    inst0
    setc.tgt ra           # 设置返回地址
    ...
    instx
.block1:
    BSTART.FP FALL
    ...
```

## Summary

These jump methods jointly build LinxISA's flexible and efficient control flow system, allowing programmers to implement complex jump control logic while maintaining code simplicity.

Not all types of blocks support the above seven types of block type. A certain type of block type is allowed to only support one or several jump methods, depending on the characteristics of block type.
