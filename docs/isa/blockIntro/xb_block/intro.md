# system-call block

system-call block is a special type of definition block method, designed to achieve efficient calls across privilege levels and modules. Its design supports the separate definition of callers and implementers, and is suitable for modular calls in operating systems, embedded systems, and security-sensitive scenarios.

## Architecture composition

system-call block consists of two parts:

- **Caller Definition**: Located at the call initiator, use the XB instruction to specify the call target (target ACR and function ID).
- **Implementation definition**: Located at the target module or privilege level, including the remaining parts of header (through CAC_TABLE table entries) and the body instruction implementation.

The caller and implementer can be distributed across processors or privilege-level contexts.

---

## XB directives and CAC_TABLE

The XB instruction is used to trigger system-call block execution, and its core mechanism relies on the CAC_TABLE table in the [XBINFO](../../register/ssr/XBINFO.md) register.

- The XBINFO register stores the base address of CAC_TABLE, and each ACR maintains an independent table.
- The C-ID parameter of the XB instruction is used as an index to access the 32-byte definition entry in CAC_TABLE.
- This entry defines a complete header (including B.IOR, B.TEXT and other instructions) or points to the address of a separated body.

CAC_TABLE does not contain commit instructions and is only used to define block attributes and parameter bindings.

---

## header definition and command support

The CAC_TABLE table entry defines the header attribute through the following instructions:

- B.CATR: Set block attributes (such as execution mode, permission flags).
- B.IOR: Define input/output register (RI/RO) for parameter transfer and return value.
- B.TEXT: Specify the location of body in memory (separated block mode).

---

## Block execution process

The execution process of system-call block is as follows:

1. Registration: The software registers the body command sequence and permission information into CAC_TABLE, through B.TEXT or directly embedding the command.
2. Call: The caller executes the XB instruction and uses ACR-ID and C-ID to locate the target body.
3. Execute:
    - If it is a block mode (CAC_TABLE embedded instruction), the instruction sequence is directly loaded and executed.
    - If it is separated block mode (CAC_TABLE points to the external PC address), obtain the body address through B.TEXT and jump to execution.

The schematic diagram is as follows:

![XB](../../../figs/isa/arch/XB.png)

Distinguish between integrated block and separated block modes:

| Features | One-Block Mode | Split-Block Mode |
|------|-------------------|------------------|
| CAC_TABLE content | Directly embed instruction sequence | Store bodyPC address |
| Instruction acquisition method | No need to access memory, direct loading | Need to jump through B.TEXT |
| Applicable scenarios | High-frequency, small body (such as template functions, context switching) | Larger, independent modules (such as system calls, complex algorithms) |
| Performance | High (reduce memory access latency) | General |

In all modes, the B.IOR instruction is used to define the input/output register to ensure cross-module data consistency.

execution mechanism diagram:
```
XB 指令
   ↓
获取ID → 查找 CAC_TABLE[128]
   ↓
判断表项类型：
   ├─ 一体块模式：加载嵌入指令 → 执行
   └─ 分离块模式：获取 B.TEXT 地址 → 跳转执行
```

## Permissions and security control

- The target ACR called by the XB instruction must have a privilege level no lower than the current ACR.
- If the permissions are insufficient, trigger E_INST(EC_PERM) exception to ensure system security.

## Usage scenarios and examples

**Scenario 1: Cross-module system call (split block mode)**
Purpose: Module A calls the file reading function of module B.
```assembly
; 调用方（模块 A）
XB ACR1, 20        ; 调用目标 ACR1，功能 ID 20

; 实现方（模块 B）
CAC_TABLE[20] = DECOUPLED {
   B.IOR [R1], [R2]   ; 输入：文件描述符在 R1，输出：数据地址在 R2
   B.TEXT BLOCK_B_FILE_READ    ; 指向ZXTERMZH40QXZ PC
}
```**Scenario 2: Lightweight task scheduling (one-block mode)**
Purpose: Quickly perform context switching.
```assembly
; 调用方（调度器）
XB ACR0, 5         ; 调用任务切换功能，ID 5

; 实现方（ACR0）
CAC_TABLE[5] = COUPLED {
   PUSH R3        ; 保存当前状态
   POP R4         ; 恢复新任务状态
}
```

**Scenario 3: Permission control template call (separated block mode)**
Purpose: Low-privilege modules call high-privilege encryption functions.
```assembly
; 调用方（低特权模块）
XB ACR2, 8         ; 调用加密功能，ID 8

; 实现方（ACR2）
CAC_TABLE[8] = DECOUPLED {
   B.IOR [R5], [R6]   ; 输入：数据在 R5，输出：密文在 R6
   B.TEXT BLOCK_ENCRYPT
}
```

**Scenario 4: Hardware Access Path (One-Block Mode)**
Purpose: High frequency GPIO operation.
```assembly
; 调用方
XB ACR1, 10        ; 调用 GPIO 功能，ID 10

; 实现方
CAC_TABLE[10] = COUPLED {
    WRITE_GPIO R7   ; 执行 GPIO 控制
    READ_GPIO R8    ; 读取 GPIO 状态
}
```

## Design advantages

- Flexibility: Supports two modes: integrated block and separated block, adapting to different performance and complexity requirements.
- Security: The permission control mechanism prevents unauthorized calls.
- Efficiency: One-block mode reduces memory access overhead and improves high-frequency calling performance.
- Modularization: The caller and the implementer are decoupled to facilitate system maintenance and upgrades.