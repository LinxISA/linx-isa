# 跳转方式

在灵犀指令集中，控制流的灵活管理是实现高效并行计算的关键。块指令提供了7种不同的跳转方式，每种方式针对特定场景设计，共同构建了完整的控制流体系。

## 跳转方式分类

| 跳转类型    | 功能描述 | 目标地址 | 使用场景 |
|------------|---------|-----------|--------------|
| **Fall**   | 顺序执行下一条块指令 | 下个顺延块首地址     | 默认执行流程 |
| **Direct** | 直接跳转到指定标签位置 | 直接跳转目标 `label` | 无条件跳转、循环控制 |
| **Call**   | 调用子程序并保存返回地址 | 调用目标块头地址 `label` | 函数调用、代码复用 |
| **Cond**   | 根据条件判断结果决定是否跳转 | 岔路目标块头地址 `label` | 条件分支、if-else逻辑 |
| **Ind**    | 通过寄存器值间接跳转到动态计算的目标地址 | 间接目标块头地址 | 跳转表、动态调度 |
| **Icall**  | 通过寄存器值间接调用子程序 | 间接目标块头地址 | 函数指针、多态调用 |
| **Ret**    | 从子程序调用返回到调用点  | 间接目标块头地址 | 函数返回、调用栈管理 |

## <span id="branch">详细说明</span>

### 1. Fall（顺延执行）

- 特点：默认执行模式，无显式跳转指令
- 行为：顺序执行下一条指令

使用场景：
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

### 2. Direct（直接跳转）

- 特点：绝对地址跳转
- 指令格式：`BSTART.BType DIRECT, <label>`

使用场景：
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

### 3. Call（调用）

- 特点：保存返回地址到专用寄存器
- 指令格式：`BSTART.BType CALL, <label>`

使用场景：
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

该类型跳转方式的块有如下约束：

- 不能是空块，**块内必须包含一条setret指令**。
- **setret必须放在bstart的后面**。

### 4. Cond（条件跳转）

- 特点：基于块内`setc.cond`指令条件判断结果决定是否跳转，不跳转则顺延执行下个块。
- 约束：不能是空块，**块内必须包含一条setc.cond指令**。

使用场景：
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

### 5. Ind（间接跳转）

- 特点：目标地址来自块内计算结果
- 约束：不能是空块，**块内必须包含一条setc.tgt指令**。

使用场景：
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

### 6. Icall（间接调用）

- 特点：动态函数调用
- 约束：不能是空块，**块内必须包含一条setc.tgt指令和一条setret指令**。

使用场景：
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

### 7. Ret（调用返回）

- 特点：恢复调用上下文
- 约束：不能是空块，**块内必须包含一条setc.tgt指令**。

使用场景：
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

## 总结

这些跳转方式共同构建了灵犀指令集灵活高效的控制流系统，使程序员能够在保持代码简洁性的同时实现复杂的跳转控制逻辑。

并不是所有类型的块都支持以上7种块类型，允许某种块类型仅支持一种或几种跳转方式，具体根据块类型特点而定。
