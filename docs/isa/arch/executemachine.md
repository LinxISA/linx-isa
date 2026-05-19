# **block instructionexecution mechanism**

block instruction is an advanced organization method in Linx Instruction Set Architecture, which is used to efficiently represent complex calculations, resource access and control processes. block instruction can be divided into two categories: Coupled Block (Coupled Block) and Decoupled Block (Decoupled Block) according to the organizational relationship between header and body. They have their own unique regulations and advantages in terms of execution mechanism, programming constraints, register access, etc. The following is a systematic explanation of the two types of organizations block instruction and execution mechanism.

---

## <span id="CoupledBlock">Coupled Block</span>

An integrated block refers to the block organization form in which header and body are closely adjacent and continuously defined in the machine instruction space. Its block instruction sequence is almost the same as the traditional instruction set sequence. header indicates the jump target and body executes the specific calculation process. It is highly compact and has low latency characteristics.

### execution mechanism

When executing a block, the processor copies the `BPC` corresponding to block instructionheader to the private PC, and initializes `TPC` to the next body instruction of `BPC`:

```asm
    BSTART     <- BPC 
    inst0      <- TPC
    inst1
    inst2
    ...
    inst[n]
    BSTOP/BSTART
```

- **BPC** always points to the starting position `BSTART` of the current block instruction.
- **TPC** points to the body instruction currently being executed, and increments the number of bytes of this instruction when the instruction is submitted.

When the TPC moves to the `BSTOP` instruction in body (or `BSTART` in the next block), it means the execution of this block ends. After block instruction is submitted, the BPC will be updated to point to the next block or target jump location.

```asm
    BSTART     <- BPC
    inst0
    inst1
    inst2
    ...
    inst[n]
    BSTOP/BSTART  <- TPC
```

### Programming constraints

- Integrated block The [B.TEXT](../header/B.TEXT.md) instruction is not allowed within the block.
- The one-piece body command can use 16/48/32/64bit encoding format.
- The integrated block body allows direct reading and writing of the global register (GGPR), and allows repeated reading and writing of the same register.
- Integrated blocks are suitable for functions, loop bodies, and parameterless block operations that require tight overall processing.

---

## <span id="DecoupledBlock">Decoupled Block</span>

The separation block achieves more flexible control flow and parameter binding by separating header (parameter transfer and call control) from body (actual calculation), and is suitable for advanced scenarios such as abstract calls, system services, and function reuse.

There are two ways for header to determine the position of body:

- **General separated block**: The pointer in header points directly to the body address.
- **system-call block**: header specifies the privilege level of body and its registry offset, which is used to implement privilege-level customized service calls.

### execution mechanism

When the detached block executes, the processor also copies `BPC` to the private PC, with `TPC` initialized to the next instruction of `BPC` and incremented on each instruction commit.

When the `B.TEXT <label>` instruction is executed, TPC jumps to the location of body and records the return address in BARG.LRA (Local Return Address) so that body can return after execution.

#### Execution process:

```asm
    BSTART                         <- BPC
    B.IOR [a0, a1, a2], [a0, a1]
    B.TEXT <body_label>            <- TPC
    BSTOP/BSTART                   <- BARG.LRA

    body_label:
    inst0
    inst1
    inst2
    ...
    inst[n]
    BSTOP
```The body instructions are executed sequentially until the TPC points to `BSTOP` of body or the next header `BSTART`, indicating that the execution of body is completed.
```asm
    body_label:
    inst0
    inst1
    inst2
    ...
    inst[n]
    BSTOP       <- TPC
```

The hardware then restores the TPC to `BARG.LRA` and continues to execute the `BSTOP` instruction after the separated block.

### Programming Constraints Description

The separated block design has strict restrictions on parameter and register access to ensure safety and correctness:

1. **Access mode restrictions**
    - If the separated block needs to access [Global Register] (../register/common/ggpr.md) (GGPR), it must be specified through the [B.IOR] (../header/B.IOR.md) instruction in header.
    - Only [Formal Parameter Register] (../register/common/lgpr.md) (RI0~RI11 and RO0~RO3) can be accessed in the separated block body, and direct access to GGPR is prohibited;
    - If the separated block needs to access the [Tile register] (../register/common/tilereg.md), it must be specified through the [B.IOT] (../header/B.IOT.md) instruction in header.
    - The separated block body needs to access the Tile register space through [Tile formal parameter register] (../register/common/ltar.md) (TA/TB/TO, etc.).

2. **Parameter matching constraints**
    - The number of `实参寄存器` specified by header (B.IOR/B.IOT) and body accessing `形参寄存器` must strictly correspond.
    - If the number of `实参寄存器` passed in by header is more than the number of `形参寄存器` in body, then the **Illegal parameter exception** will be triggered when decoding header.
    - If the number of `实参寄存器` passed in by header is less than the number of `形参寄存器` accessed by body, then the formal parameter register with a relatively large number is uninitialized, and the result after being read is undefined.

3. **Write duplicate constraints**
    - The same output parameter register (RO0-RO3) cannot be written repeatedly in the separated block body, otherwise a DoubleSetException should be triggered.

4. **Instruction Constraints**
    - Separate block body prohibits the use of 16bit and 48bit encoding instructions, and only allows the use of 32bit and 64bit encoding instructions.

---

## Summary

The Linxblock instruction architecture provides a highly abstract execution unit for the processor through two types of execution mechanism: integrated block and separate block, and efficiently supports diverse calculations and calling modes. The integrated block emphasizes compact, parameter-free direct operation of global registers; the separated block emphasizes parameterization, flexibility and multi-level access control, especially in the fields of system calls and function abstraction. The two mechanisms serve different programming and system requirements respectively, and jointly enhance the functionality and security of the instruction set architecture.