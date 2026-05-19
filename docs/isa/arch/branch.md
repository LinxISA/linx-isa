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
    BSTART.VEC FALL
    ...
```

### 3. Call

- Feature: Save return address to special register
- Instruction format: `BSTART.BType CALL, <label>`

Usage scenarios:
```asm
.block0: 
    BSTART.STD CALL, .block2   # 调用执行block2处程序
    setret .block1, ->ra       # 保存返回地址
    inst1
    ...
    instx
.block1: 
    BSTART.SYS FALL
    ...
.block2:
    BSTART.VEC FALL
    ...
```

Blocks with this type of jump mode have the following constraints:

- It cannot be an empty block. **The block must contain a setret instruction**.
- **setret must be placed after bstart**.

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
    BSTART.VEC FALL
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
    BSTART.VEC FALL
    ...
```

### 6. Icall (indirect call)

- Features: Dynamic function call
- Constraints: It cannot be an empty block. The block must contain a setc.tgt instruction and a setret instruction**.

Usage scenarios:
```asm
.block0: 
    BSTART.STD ICALL
    setret .block1, ->ra   # 保存返回地址
    add a0, t#1, ->t
    setc.tgt t#1           # 设置跳转目标地址
    ...
    instx
.block1:
    BSTART.SYS FALL
    ...
.block2:
    BSTART.PAR FALL
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