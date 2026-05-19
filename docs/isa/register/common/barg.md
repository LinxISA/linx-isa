# BARG register

BARG (full name: **Block Argument Register Group**) is a parameter register group inside a block, used to store control and status information related to block execution and jumps.

BARG consists of multiple independent fields, each field is used to store a specific category of control information (such as jump control, execution status, scheduling attributes, etc.). Each field can be set independently by the corresponding instruction; there is a one-to-one or one-to-many explicit mapping relationship between instructions and fields. The writability and update timing of the field are constrained by the instruction semantics: the relevant field can be modified only when the corresponding BARG control instruction is executed; writing to the field by non-corresponding instructions is illegal or ignored.

## Domain segment table

The BARG register contains the following field segments:

| Field segment name | Bit width | Description | Valid block type |
|------------------|-----|------------------------------------------------|-------------|
| **BPC** | 64 | The header address of the current block instruction, that is, the BPC (block pointer) of the current block instruction | All block type |
| **BPCN** | 64 | The header address of the jump target block, indicating the jump location after block instruction execution is completed | STD, FP |
| **LRA** | - | Local return address, used to record the address of return header in the separated block (multiplexed BPCN field) | MPAR, MSEQ, VPAR, VSEQ |
| **BlockType** | 5 | block type of the current block | all block type |
| **TYPE** | 2 | block instruction jump type, records the jump logic of the current block instruction.                  | STD, FP |
| **TAKEN** | 1 | Jump condition result, 1 means the condition jump is successful, 0 means the condition is not met | STD, FP |
| **AQ,RL** | 2 | Execution sequence attributes of block instruction | STD, SYS, FP, VPAR, VSEQ |
| **RegDst0** | 5 | Record the first output GGPR of the separation block | MPAR, MSEQ, VPAR, VSEQ |
| **RegDst1** | 5 | Record split block second output GGPR | MPAR, MSEQ, VPAR, VSEQ |
| **RegDst2** | 5 | Record the third output of the split block GGPR | MPAR, MSEQ, VPAR, VSEQ |
| **RegDst3** | 5 | Record the 4th output GGPR of the split block | MPAR, MSEQ, VPAR, VSEQ |

The diagram is as follows:

![barg](../../../figs/bitfield/svg/Sysregs/BARG.svg)

### 1. **BPC**Store the address (BPC) of the current block instructionheader. This field segment is set by hardware when block instruction is initialized and is used to indicate the location of the current block.

When block instruction is initialized, the address of the current BSTART is assigned to the BPC.

### 2. **BPCN**

When block instruction is initialized or executed, the header address of the jump target block is recorded in this field. Used to jump when block instruction ends and is submitted.

[SETC.TGT](../../inst/misa_g/SETC.TGT.md) command is used to set this field.

### 3. **LRA**

Initialization is performed when executing [B.TEXT](../../header/B.TEXT.md) in the separated block, and the address of the next instruction of B.TEXT is written into LRA so that it can return after executing body.

### 4. **BlockType**

Used to record the block type of the current block. This information plays a key role in exception processing. The encoding method is as follows:

| BlockType | Description |
|----------|-------------|
| 0 | INTEGER scalar BLOCK STD |
| 1 | System block SYS |
| 2 | Floating Point scalar Block FP |
| 3 | Data blocks (MPAR, MSEQ, VPAR, VSEQ, CUBE, TMA) |
| 31 | system-call blockXB |

### 5. **TYPE**

Define the jump type of block instruction. Valid values are as follows:

| Assembly | NAME | TYPE | TAKEN | BPC | BPCN |
|-----------------------|--------|---------|----------|--------------|--------------------------|
| BSTART.FALL | Postponed | 0 | 0 | Current BSTART address | Next postponed BSTART address |
| BSTART.DIRECT `label` | Direct jump | 1 | 1 | Current BSTART address | Direct jump target `label` |
| BSTART.CALL `label` | Call | 1 | 1 | Current BSTART address | Call target header address `label` |
| BSTART.COND `label` | Conditional jump | 2 | 0/1 | Current BSTART address | Fork target header address `label` |
| BSTART.IND | Indirect jump | 3 | 1 | Current BSTART address | Indirect target header address |
| BSTART.ICALL | Indirect call | 3 | 1 | Current BSTART address | Indirect target header address |
| BSTART.RET | Return | 3 | 1 | Current BSTART address | Indirect target header address |

### 6. **TAKEN**

Indicates whether the conditional jump meets the conditions:

- **1**: The conditions are met and the jump is successful.
- **0**: If the conditions are not met, execution will continue to be postponed.[setc.cond](../../blockIntro/scainstrs/setc.md) type instructions are used to set the TAKEN bit of the BARG register.

### 7. **AQ,RL**

Record the execution sequence attributes of this block and other block instruction, set by header instruction[B.ATTR](../../header/B.ATTR.md).

### 8. **RegDst0~3**

The output register number of this block is stored in the separate block, which is used to update the updated formal parameter register value in the block to the specified global register GGPR when the block is submitted.

This set of fields is configured through header instruction[B.IOR](../../header/B.IOR.md).

## Remarks

This register has the following characteristics:

* This register is readable and writable (RW).
* This register is initialized by the processor hardware **Block Scheduler** and **Branch Predictive Execution Unit**.
* Each time block instruction is submitted, the contents of the BARG register will be cleared so that it can be reinitialized the next time block instruction is executed.