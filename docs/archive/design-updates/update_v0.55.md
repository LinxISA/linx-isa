# 0.55 version update

Update date: November 17, 2025

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.55](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101082569709)

## 1. Update background

- exception processing and debugging: The exception/interrupt processing flow has been improved, and the debugging function support has been strengthened.
- Instruction set expansion: V.MOV instructions, scaling matrix multiplication instructions (MAMULBMX series) and DMA instructions have been added to optimize the vector processing and matrix operation capabilities.
- Register adjustment: The functions of the BARG register have been expanded, and the EBPCN register has been added, which improves the control capabilities of block instruction and the processing capabilities of exception.
- Architecture support: Added a new template block instruction based on the PTO instruction set, which provides support for the evaluation of the first layer architectural state.

## 2. Update summary

LinxISA0.55 version includes three sub-versions (0.55.0, 0.55.1, 0.55.2), each sub-version is optimized and enhanced for different functional modules. The following are the main updates in each sub-version:

### Version 0.55.0

| Category | Modifications | Description |
|------|---------|---------|
| 1. **exception processing related** | 1.1 BSTATE definitions of different block type | Used to refine the design of different block type in the current version |
| | 1.2 Update EBSTATE implementation | Adapt the design of some Tile blocks that cannot access memory |
| | 1.3 Strengthen exception processing design | Add exception storage processing of Tile block |
| | 1.4 Updated privilege level switching design | Added processing of Tile blocks during privilege level switching |
| | 1.5 Modify part of system register | Adapt the design saved and restored by the current version block instructionexception |
| | 1.6 Revised acrc/acre command definition | exception is triggered immediately after acrc/acre is submitted to achieve accurate exception |
| 2. **Software debugging related** | 2.2 Enhanced definition of EBREAK instruction | Add immediate parameters to support other debugging capabilities such as kprobe/uprobe outside GDB. The meaning of immediate data is defined by the kernel |
| | 2.2 Add the 16bit version of the C.EBREAK instruction | The 16bit version can safely replace the instruction at any address without destroying the next instruction when used for GDB debugging |

### Version 0.55.1| Category | Modifications | Description |
|------|---------|---------|
| 1. **New instruction** | V.MOV instruction | Add a new vector instruction that is not controlled by the global P-Mask and is used to fully copy the register contents in the control flow branch. |
| | Scaling matrix multiplication instructions | Added MAMULBMX, MAMULBMXAC and MAMULBMX.ACC instructions to support the micro-scaling mechanism and improve the numerical dynamic range and expression capabilities of matrix multiplication. |
| | DMA command | Added MCOPY.D command and dma command to support memory data transfer through DMA. |
| 2. **Instruction revision** | FENCE instruction | Synchronize the instruction design of version 0.43-Beta, rename FENCE.D to DSB, FENCE.I to ISB, and add the flag bit M of the DSB instruction. |
| | ESAVE and ERCOV instructions | Revised to multiple input multiple output instructions, support saving and restoring context within the block, and add saving and restoring body starting TPC. |
| 3. **Register Adjustment** | BARG Register | Expand the BPC and BPCN fields to 64 bits, add BlockType, Type, Taken, AQ, RL and other fields to improve the control capabilities of block instruction and exception processing. |
| | Newly added EBPCN register | Used to save the next block instructionBPC after exception occurs in block instruction, ensuring that the program can resume execution correctly after exception is processed. |

### Version 0.55.2

1. **New template block instruction**: The new 70+ template block instruction is designed to optimize the state management of the first-layer architecture and improve the flexibility and scalability of the instruction set.

---

## 3. Detailed description

### **1.1 BSTATE enhanced definition**

In LinxISA, the internal state of a block execution unit is called BSTATE. BSTATE is a set of registers related to block execution. Different block execution units (block type) may use different formats of BSTATE. BSTATE is divided into three parts: BARG, TPC and LPR. Among them, BARG represents the control and status register related to instruction scheduling and execution, TPC points to the address of the body instruction being executed within the block, and LPR represents the private register group of the current block. BSTATE is defined as follows:

| Name | Description |
|------|-------|
| BARG (Block Arguments Register Group) | Used to record the scheduling and execution information of block instruction in the first-layer architecture and the status information inside the block. |
| TPC (Temporal Program Counter) | Microinstruction pointer register, used to indicate the address of the microinstruction within the block being executed. |
| LPR (Local Purpose Register) | general-purpose register inside block instruction. |

**1.1.1 Definition of BARG**

BARG is a register group that evolved from the previous version of CARG. In the current design, BARG not only contains the information when block instruction is submitted, but also stores the scheduling information and execution attributes of block instruction, so renaming it BARG is more consistent with the definition.
The BARG register contains a series of different fields, each of which allows it to be set independently by the corresponding instruction. And each field is allowed to be valid under a specific block type, as follows:| Field | Bitwidth | Description | Valid block type |
|------|------|------|----------|
| BPC | 64 | BPC for current block instruction | All block type |
| BPCN | 64 | The offset of the BPC of the next block instruction in the execution logic relative to the BPC of this block. | STD, FP |
| LRA | - | The offset of the local return address in the detached block relative to the BPC of this block. (Multiple BPCN field) | MPAR, MSEQ, VPAR, VSEQ |
| BlockType | 5 | Current block's block type | All block type |
| Type | 2 | Jump method | STD, FP |
| Taken | 1 | Jump to the taken flag bit | STD, FP |
| AQ,RL | 2 | Execution sequence attributes | STD, SYS, FP, VPAR, VSEQ |
| RegDst0 | 5 | Record the first output of the split block GGPR | MPAR, MSEQ, VPAR, VSEQ |
| RegDst1 | 5 | Record the second output of the split block GGPR | MPAR, MSEQ, VPAR, VSEQ |
| RegDst2 | 5 | Record the 3rd output of the split block GGPR | MPAR, MSEQ, VPAR, VSEQ |
| RegDst3 | 5 | Record the 4th output of the split block GGPR | MPAR, MSEQ, VPAR, VSEQ |

Description:

- MPAR, MSEQ, VPAR, VARQ, etc. are defined as separate block structure, so the LRA field is valid.
- STD and FP blocks support full jump mode, so the BPCN, TYPE, and TAKEN fields are valid.
- TMA and CUBE blocks are hardened implementations of block instruction and cannot be programmed internally. So there is only BPC.
- MPAR and MSEQ blocks have AQ and RL attributes by default (see memory model MCALL mode for details).
- The RegDst0~RegDst3 fields are initialized by the B.IOR instruction in header. If the field is invalid, it is encoded as 0.

The domain segment definition of BARG is as shown in the figure below:

![barg](../figs/isa/version/0.55/barg.png)

Among them, BPCN_OFFSET and LRA_OFFSET multiplex the same field, and the storage content of this field is determined by block type.

**1.1.2 TPC definition**

TPC is used to record the address of the microinstruction executed within the block.

- For integer scalar blocks, system blocks and scalar floating point blocks, there is only one TPC within the block.
- For memory access parallel blocks and vector parallel blocks, there is an independent TPC in each parallel group.
- For memory access serial blocks and vector serial blocks, groups within the blocks are serialized, so there is only one TPC.
- For TMA and CUBE blocks, the block interior is not programmable, so there is no TPC.

**1.1.3 LPR definition**

Similarly, LPR also contains a series of registers, and the contents are different in different block type:| Register | Register bit width | Description | Valid block type |
|-------|-----------|------|------------|
| **T/U** | 64bit | scalar register | STD, SYS, FP, MPAR, MSEQ, VPAR, VSEQ |
| **RI/RO** | 64bit | Formal parameter register | MPAR, MSEQ, VPAR, VSEQ |
| **PRED(P)** | 64bit | Mask register | MPAR, MSEQ, VPAR, VSEQ |
| **LB** | 16x4 bit | Lane total counter | MPAR, MSEQ, VPAR, VSEQ |
| **LC** | 16x4 bit | Lane counter | MPAR, MSEQ, VPAR, VSEQ |
| **VT/VU/VM/VN** | 32bit x LaneNum | vector register | MPAR, MSEQ, VPAR, VSEQ |
| **Output Tile** | 512Byte ~ 32KB | Output Tile register | MPAR, MSEQ, VPAR, VSEQ, TMA, CUBE |

### **1.2 EBSTATE update definition**

The state within the block where exception occurs or is interrupt is called EBSTATE. In previous versions, EBSTATE was stored in the memory space pointed to by EBSTATEP. Since version 0.5 introduced Tile blocks and some Tile blocks do not allow access to memory, the storage method of EBSATE is adjusted as follows.

**1.2.1 EBSTATE save and restore**

In the new version, the storage methods of EBSTATE of different block type are defined as follows:| block type | Save BSTATE to EBSTATE | Restore from EBSTATE |
|--------|------------------------|----------------|
| STD, SYS, FP | Hardware saving required: <br>Save BPC to SSR:EBPC; <br>Save the rest of the information in BARG to SSR:EBARG; <br>Save TPC to SSR:ETPC; <br>Software selective saving:<br>Save scalar registers such as T/U to Memory. | Requires hardware recovery:<br>Recover BPC from SSR:EBPC; <br>Recover jump information from SSR:EBARG and wait until BARG;<br>Recover TPC from SSR:ETPC;<br>Software selective recovery:<br>Recover T/U and other scalar registers from Memory. |
| VPAR, VSEQ;<br>MPAR, MSEQ | Hardware saving required:<br>Save BPC to SSR:EBPC; <br>Save the remaining information in BARG to SSR:EBARG; <br>Record the GroupID of the Group that triggered exception in SSR: EBARG;<br>Software selective saving:<br>Save all or a certain type of Tile registers to memory by calling the TSTORE instruction;<br>Save the TPC and LPR of the Group to the Tile register by calling ESAVEtemplate block; <br>Save the contents of the Tile register output by ESAVE to memory by calling the TSTORE instruction. | Hardware recovery required:<br>Recover BPC from SSR:EBPC;<br>Recover BARG from SSR:EBARG;<br>Software selective recovery:<br>Load LPR from memory to the Tile register by calling the TLOAD instruction. <br>Restore the status of the Group by calling ERCOVtemplate block;<br>Load the contents of the Tile register back from memory by calling the TLOAD instruction. |

**1.2.2 Added system register**

In the new version, a group of system register is added for the hardware to store the exception address, block instruction internal status and block type when the hardware actively generates exception and passively generates interrupt, and updates the block type that triggered this hardware update. After the exception or interrupt processing is completed, restore from this set of registers.

EBPC and ETPC, etc.:

| SSR_ID | Register | Bit width | Description |
|--------|---------|------|------|
| 0xnf0b | EBPC | 64 | Used to record block instructionBPC and BPCN_OFFSET when exception occurs. |
| 0xnf0c | EBARG | 64 | Used to save the block instruction jump mode, block type and output register parameters when exception occurs. |
| 0xnf0d | ETPC | 64 | Microinstruction TPC used to record the occurrence of exception. |
| 0xnf0e | EBPCN | 64 | Used to record the BPC of the next block of block instruction where exception occurs. |

Among them, the format of the EBPC register is defined as follows:
 
![ebpc](../figs/isa/version/0.55/ebpc.png)

The format of the EBARG register is defined as follows:

![ebarg](../figs/isa/version/0.55/ebarg.png)

The format of the ETPC register is defined as follows:

![etpc](../figs/isa/version/0.55/etpc.png)

The format of the EBPCN register is defined as follows:

![ebpcn](../figs/isa/version/0.55/ebpcn.png)

**1.2.3 Added ESAVE and ERCOVtemplate block**As mentioned in 1.2.1 above, when exception or interrupt occurs in a Tile block such as VPAR/VSEQ/MPAR/MSEQ, the software can call ESAVEtemplate block to save the LPR content in the block to the Tile register. When exception is restored, the state of the registers in the block is restored from the Tile register by calling ERCOVtemplate block.

The two template block are defined as follows:

exception save block-ESAVE is used for vector data block or access data block. When exception or interrupt is encountered during execution, all contexts in the block are saved to the specified Tile register. ESAVE is a multi-output instruction, where:

- The first output Tile register is used to save the private registers within the exception block, including LB/LC registers, scalar registers, vector registers, mask registers, etc.
- Other output Tile registers are used to save the contents of the output Tile of the exception block itself.

In the current version, since the vector data block and memory access Tile block can have up to 4 output Tile registers, the ESAVE instruction can have up to 5 output Tile registers.

Assembly format: `ESAVE , ->DstTile0<32KB>, DstTile1<32KB>, ..., DstTile4<32KB>`

exception recovery block-ERCOV is used for vector data block or access data block. After exception or interrupt processing is completed, all context states in the block are restored from the specified Tile register.

ERCOV is a multi-input instruction where:

- The first input Tile register is used to restore the private registers within the exception block, including LB/LC registers, scalar registers, vector registers, mask registers, etc.
- Other input Tile registers are used to restore the output Tile register contents of the exception block itself.

Matching the number of output Tiles of the ESAVE instruction, the current version of the ERCOV instruction has up to 5 input Tile registers.
Assembly format: `ERCOV SrcTile0, SrcTile1, ..., SrcTile4`

The encoding of BSTART.TEPLblock instruction is as follows:
 
![bstart.tepl](../figs/isa/version/0.55/bstart.tepl.png)

Function field encoding mapping table:

| Function | TileOp | Description |
|----------|--------|--------|
| 0-29 | RESERVE | Reserved |
| 30 | **ESAVE** | exception save block, used to save the block state of the Tile block where exception occurs. |
| 31 | **ERCOV** | exception recovery block, used to restore the block state of the Tile block where exception occurred. By default, it has inheritable attributes, and the subsequent sequence block instruction can inherit the internal state of this block. |

### 1.3 exception processing

**1.3.1exception**

exception is an event that is detected synchronously in the instruction pipeline. This kind of event usually causes the pipeline to be logically unable to continue (for example, the requirements of the instruction cannot be met), and must be immediately transferred to other instruction sequences.
exception can occur synchronously during the execution of the instruction. During this process, part of the behavior of the instruction may have taken effect, may not have taken effect, or may have all taken effect. The specific situation and specific instructions are related to the type of exception. If there is no special explanation, by default the specific instruction exception occurs, then all actions required by the instruction will not take effect, and the exception instruction pointer will still stay on the instruction where exception occurred.LinxISA supports the exact exception of header instruction and body instructions. Regardless of the header instruction or body instruction exception, the exceptionblock instruction pointer EBPC always points to the block instructionBSTART where exception occurs, and ETPC always points to the address of the exception instruction. If it is body instruction exception, the processor needs to set the exception status register ECSTATE_ACRn.BI (BI means BlockI nner) is set to 1; on the contrary, if it is header instructionexception, the exception status register ECSTATE_ACRn.BI needs to be set to 0. The software can decide whether to save and restore the intra-block status of the exception block through BI information.

Special note:

- If exception occurs in the middle of a block, the hardware must ensure that the contents of all registers inside the exception block are retained and resources are not released. This ensures that the software can save the internal state of the exception block through a new block (such as ESAVEtemplate block).
- exception is not supported during CUBE block execution.
- Generating exception is not supported internally in the TMA block.

**1.3.2 Added block instructionexception type**

When scheduling is triggered, in order for the kernel (ACR1) to determine whether the user mode uses VECTOR or CUBE type block instruction, the corresponding context can be saved and scheduled. The current version adds the following control mechanisms:

- When the core (ACR1) is initialized, configure the exception enable bit in the SCONFIG_ACR1 register to 1;
- When the user mode (ACR2) process uses VECTOR or CUBE type block instruction, the corresponding exception is triggered to fall into ACR1, exception code TRAPNUM=0, CAUSE=4. The kernel performs corresponding processing:
    * Configure the exception enable bit of different block type in the ECONFIG_ACR1 register to 0 to ensure that subsequent use of VECTOR and CUBE instructions in user mode will not trigger exception;
    * Record that the current process has used VECTOR and CUBE marks TIF_VECTOR/TIF_CUBE;
    * Allocate VECTOR and CUBE block context to save address space.
- When subsequent user mode falls into the kernel again (interrupt or other exception), if scheduling is triggered, the kernel checks the prev process TIF_VECTOR/TIF_CUBE flag. If it is set, the kernel saves the prev process context.

The above is only used to briefly explain the exception processing method of VECTOR or CUBEblock instruction. The specific implementation process kernel can be adjusted and designed.

Added exception types as follows:

| TrapNum | Reason code (Cause) | exception parameter code | Trigger command |
|---------------------|-----------------|-------------|---------------|
| E_INST(0) | E_PEREM(4) | 0 | MPAR/MSEQ/VPAR/VSEQ |
| | | 1 | CUBE |

Note: The ECONFIG register is modified from the IENABLE register, and the V and C flag bits are added based on the original fields of IENABLE as the exception enable bits of the VCETOR and CUBE instructions.

Register format:![econfig](../figs/isa/version/0.55/econfig.png)

**1.3.3 Status Migration**

The operating system OS’s solution for context switching (Context Switch) on different processing units of Janus Core is designed as follows:

* **BCC Context Switch**
    *Context saving:
        1. Save EBARG to memory
        2. If context switch occurs in body, save LPR to memory
    *Context recovery:
        1. Restore EBARG from memory
        2. If context switch occurs in body, restore the status of LPR in the block
        3. Execute the ACRE instruction (if the context switch occurs in body, the ACRE parameter must be 1.
* **VECTOR/MTC Context Switch**
    *Context saving:
        1. Save EBARG to memory
        2. If context switch occurs in body, save LPR to memory:
            1. If necessary, save all Tile registers to memory: TSTORE T#1~T#8, U#1~U#8, M#1~M#8, N#1~N#8;
            2. Save the LPR to the Tile register through ESAVE, and then save the Tile register to memory through TSTORE.
    *Context recovery:
        1. If context switch occurs in body, restore LPR from memory:
            1. Load the LPR content into the Tile register through TLOAD, and then restore the LPR status through ERCOV;
            1. If necessary, restore the contents of all Tile registers from memory: TLOAD T#1~T#8; TLOAD U#1~U#8; TLOAD M#1~M#8; TLOAD N#1~N#8;
        1. Restore EBARG from memory;
        2. Execute the ACRE instruction (if the context switch occurs in body, the ACRE parameter must be 1.)
* **CUBE Context Switch for ACC**
    *Context saving:
        1. Copy the contents of the ACC register to the general Tile register: ACCCVT ACC, ->dstTile;
        2. Save the contents of the Tile register to memory: TSTORE srcTile;
    *Context recovery:
        1. Restore the contents of the Tile register from memory through the TLOAD instruction; example: TLOAD ->T
        2. Construct a matrix (identity matrix) with a main diagonal of 1 through the BSTART.VPAR block; example: VPAR ->T
        3. Restore the contents of the ACC register through the MAMULB instruction. Example: MAMULB T#2, T#1, ->ACC

### **1.4 Privilege Level (ACR) Switch**

ACR switching allows active triggering by internal or external requests from the Linx core (LxLC). The request sources are divided into exception, interrupt, system-call block instructions, ACRC and ACRE microinstructions, etc.*exception, the system switches to the target ACR state. Mainly used by the managed software to return control of the Linx core (LxLC) to the management software. The ACRC instruction belongs to the body microinstruction.
*interrupt includes external interrupt (EI) and Timerinterrupt (TI)
* The ACRE microinstruction only takes effect within the system block. Submission of this instruction will immediately submit the current block and enter the target ACR. Mainly used for management software to actively hand over control of the Linx core (LxLC) to the managed software.
* system-call block, the system switches to the target ACR state when the block is called, and returns to the ACR before the switch after the block is submitted. Mainly used for efficient invocation of critical cross-privilege level requests.

**1.4.1 SERVICE_REQUEST**

SERVICE_REQUEST can only be driven by exception or interrupt. exception are all synchronous and are called SYNC_SERVICE_REQUEST. interrupt is asynchronous and called ASYNC_SERVICE_REQUEST.
SYNC_SERVICE_REQUEST and ASYNC_SERVICE_REQUEST are collectively called traps in Linx Instruction Set Architecture, and the process of entering the trap is called falling into. SERVICE_REQUEST process is as follows:

For any SERVICE_REQUEST from ACRn to ACRm, the specific behavior is:

* If it is related to exception generated by floating point operation, set the corresponding flag bit in CSTATE.flags.
* The current SSR:CSTATE is saved to SSR:ECSTATE_ACRm. If the triggering instruction is header instruction, set SSR:ECSTATE_ACRm.BI to 0, otherwise set to 1;
* The BPC of exception block is saved to EBPC_ACRm;
* Save the BARG content of exception block to EBARG_ACRm and set EBARG_ACRm.BlockType to trigger block type.
* If the exception block is an STD, SYS or FP block, save the TPC that triggered the exception instruction to ETPC;
* If the exception block is an MPAR or VPAR block, save the GroupID that triggered the exception to the GroupID field of EBARG.
* CSTATE.I is set to 0; # interrupt enable bit
* CSTATE.ACR position is m;
* BARG reset to initial value;
* BPC is set to EVBASE_ACRm;
* For SYNC_SERVICE_REQUEST:
    * TRAPNO_ACRm.E is set to 1; # Synchronize exception flag
    * Set SSR:TRAPNO_ACRm and SSR:TRAPARG0_ACRm according to the trap code and parameters.
* For ASYNC_SERVICE_REQUEST:
    * TRAPNO_ACRm.E is set to 0;
    * Set SSR:TRAPNO_ACRm and SSR:TRAPARG0_ACRm according to interrupt type.
The above actions are completed once inside the Linx logic core (LxLC), and there will be no other actions that change the state of the Linx logic core (LxLC).

**1.4.2 ACR_ENTER**

ACR_ENTER is requested through the ACRE instruction and is fired when the instruction is submitted. For an ACR_ENTER initiated from ACRn, the specific process is:* The ACR state of Linx logic core (LxLC) switches to system registerECSTATE_ACRn.ACR. The target ACR must be comparable to the current ACRn, and ACRn p>= ECSTATE_ACRn.ACR. Otherwise this step itself triggers E_INST(EC_PARAM)exception;
* Use the contents of SSR:ECSTATE_ACRn to restore the current SSR:CSTATE state;
* Use SSR:EBPC_ACRn to restore the contents of BPC and schedule the execution of the block where BPC is located;
* According to the ACRE.RRA parameter, select whether to use the contents of SSR: EBARG_ACRn to restore BARG.
* If the block type recorded in EBARG is STD, SYS or FP, use the contents of SSR:ETPC_ACRn to resume TPC execution;

### **1.5 Partial modifications of system register**

In order to adapt to the design of the existing exception processing flow, some system register have been deleted as a whole and some fields have been modified.

1.5.1 Delete the ebv bit of CSTATE register

Before modification:

![cstate](../figs/isa/version/0.55/cstate_old.png)

After modification:

![cstate](../figs/isa/version/0.55/cstate_new.png)

**1.5.2 Modify the ebv bit of ECSTATE**

The ebv bit of ECSTATE is changed to BI, which is used to identify whether the exception block service request SERVICE_REQUEST occurs in the middle of the block. If it occurs within body, this bit is set to 1, otherwise it is cleared.

Before modification:
 
![ecstate](../figs/isa/version/0.55/ecstate_old.png)

After modification:
 
![ecstate](../figs/isa/version/0.55/ecstate_new.png)

The software can decide whether to save and restore the state in the block based on whether the BI bit of ECSTATE is set.

**1.5.3 Delete the BI flag of TRAPNO**

Duplicate with the BI definition in ECSTATE, so deleted.

![trapno](../figs/isa/version/0.55/trapno_old.png)

After modification:

![trapno](../figs/isa/version/0.55/trapno_new.png)

**1.5.4 Delete ELINK and EBSTATEP registers**

In the original design, ELINK is used to save the BPC of the exception block when the exception service request SERVICE_REQUEST processing occurs. EBSTATEP is used to store the memory pointer of EBSTATE. Under the new design, the BPC of the exception block is saved to EBPC, so ELINK is deleted. Part of EBSTATE is saved in the register and the other part of the software decides whether to save it instead of saving it uniformly in the memory, so EBSTATEP is deleted.

![ssr](../figs/isa/version/0.55/ssr.png)

### 1.6 Update ACRC and ACRE instruction definitions

**1.6.1 Enhanced definition of acrc execution semantics**

In the new version, acrc execution semantics are modified to: immediately submit the current block and initiate a system request. The request type is specified by the request_type parameter. Other definitions remain unchanged.

Constraints: The arcc instruction is an instruction with BSTOP semantics, so it must be the last microinstruction of block instruction.

After this command triggers a system request, the processing is the same as that of ordinary exception. The hardware saves the BPC to EBPC of the block where acrc is located and the TPC of acrc to ETPC. Then before returning to user mode:

- If the software is not modified, it will return to the original acrc address and re-initiate a system request. (redo syscall)
- If you expect to return to the next instruction of acrc to continue execution, then the software needs to change the addresses in EBPC and ETPC to the original value of ETPC plus 4 (that is, the instruction length of acrc).

Example:
```asm
    BSTART.SYS        <--- BPC
    B.ATTR TRAP
    ldi [a0, 8], ->t
    ldi [a0, 16], ->t
    mul t#1, t#2, ->t
    acrc SCT_SYS      <--- TPC
    BSTART.STD      <--- NextBPC       
    ...
```

How to continue execution after ACRC triggers the system call is explained as follows:| exception Save Register (SSR) | Contents saved by hardware | Software does not modify, re-initiate request | Software modify, continue execution from the next instruction of ACRC |
|-------------------------|--------------|--------------------------|----------------------------------|
| EBPC | BPC | BPC | TPC+4 |
| ETPC | TPC | TPC | TPC+4 |

**1.6.2 Modification of acre command**

The acre instruction is used to set the ACR switching requirements of the current block, immediately submit the current block and execute the ACR_ENTER process to switch the current ARC to the target ACR. The target ACR is specified by the ECSTATE register of the privilege level in which the acre instruction is executed.
The acre command has a Return Request Argument parameter, referred to as RRA, which is used to specify the status of exception when it is submitted.

Instruction assembly: `acre RRA_Type`

In the current version, the value range of RRA_Type includes:

- RRAT_DEFAULT(0): BSTATE is reset to the default state when submitted.
- RRAT_RESTORE(1): Initialize BSTATE with EBSTATE.
- Other values ​​are reserved. If other values ​​are encountered during execution, the illegal instruction exception will be triggered when submitting.

Modification point: Delete the RRAT_REDO_ECALL type when RRA_Type is 2. The software can perform the REDO_ECALL operation by modifying the values ​​of EBPC and ETPC.

Things to note:

- After this instruction is submitted, the current block instruction will be submitted immediately. Therefore, this instruction must be used as the last microinstruction of block instruction.
- block instruction where acre is located is inheritable, and the subsequent sequence block instruction can inherit the internal state of this block.

Example of using acre:
```asm
# ZXTERMZH41QXZ恢复时特权态：
ERCOV                        <- 恢复ZXTERMZH41QXZ块的块内状态
BSTART.SYS
acre RRAT_RESTORE            <- 返回指定特权级
# 返回用户态执行BPC指示的块
BSTART.xx                      # 新块继承恢复的状态
inst                           <- 从ETPC恢复的TPC指示的指令
```

### **2.1 Update EBREAK command**

The EBREAK (Exception break) instruction is used to trigger software breakpoint. This instruction requests the debugger by throwing the breakpoint exceptionE_BREAKPOINT and writes the immediate value to the low bit of the cause field of the SSR:TRAPNO register.

Assembly format: `ebreak imm`

In order to meet the needs of kernel debugging, the new version revise the ebreak instruction as follows:

- Added immediate parameter for kernel debugging, the meaning of immediate is defined by the kernel.
- Delete CMT parameters and process them in the same way as ordinary exception.
- Adjust the encoding. The modified instruction encoding is shown in the figure below.

Instruction encoding:

![ebreak](../figs/isa/version/0.55/ebreak.png)

### **2.2 Add C.EBREAK command**

Because in LinxISA, the minimum instruction length is 16 bits. Therefore, a c.break instruction is added to the new version so that the debugger can safely replace the instruction at any address without destroying the next instruction.

Assembly format: `c.ebreak imm`

The encoding format is as follows:

![c.ebreak](../figs/isa/version/0.55/c.ebreak.png)

During hardware execution, the immediate value also needs to be written to the low bits of the cause field of the SSR:TRAPNO register.

### V.MOV instruction

- **Background**: In the control flow branch, due to the limited relative index distance of the registers, an instruction that is not controlled by the global P-Mask is required to implement a full copy of the data.
- **Definition**: The assembly format is `v.mov SrcL.<T>, ->RegDst.<W>`, which implements a full copy of the input register SrcL and writes the result to the destination register RegDst.
- **Example**: Use `v.mov vt#1, ->vt` in the else branch to fully copy the register contents in the if branch.

### MAMULBMX scaling matrix multiplication instructions and micro-scaling mechanism- **Purpose**: Improve the numerical dynamic range and expressive capabilities of matrix multiplication, and support approximate operations under FP32 precision or precision compensation for low bit-width multiplication.
- **Command Type**:
    - **MAMULBMX**: Perform scaled matrix multiplication and write the result to the ACC register.
    - **MAMULBMXAC**: Perform scaled matrix multiplication and addition operations, and write the results to the ACC register.
    - **MAMULBMX.ACC**: Execute the scaled matrix multiply and accumulate operation, and write the result to the ACC register.
- **Micro-zooming mechanism**:
    - **Hardware Basics**: CUBE Core's 16×16×16 Tile-level matrix multiplication unit, the scaling unit is located in the input multiplication path of Tile A and Tile B, and the scaling factors are stored in ScaleTileA and ScaleTileB.
    - **Calculation method**:
       1. Scale the input Tile element by element:
          - Tile A: `A_scaled[i][j] = A[i][j] * ScaleA[i][j]`
          - Tile B: `B_scaled[i][j] = B[i][j] * ScaleB[i][j]`
       2. Perform scaled matrix multiplication: `ACC[M][N] += MAMULB(A_scaled[M][K], B_scaled[K][N])`
    - **Key Features**: K dimensions share scaling factors, each row of ScaleA shares a factor, and each column of ScaleB shares a factor, reducing storage and transmission overhead.

### DMA instructions

- **MCOPY.D instruction**: Added a new instruction that supports DMA copy. When the hardware does not support DMA, it is equivalent to the original MCOPY instruction.
- **dma command**: Copy 64 bytes of data from the source address to the destination address. Submit the command after the copy is completed.

### FENCE directive revision

- **FENCE.D command**: Name changed to DSB. Add the flag bit M, M=0 indicates the system default synchronization method, and M1 indicates the user-defined synchronization method.
- **FENCE.I command**: Name changed to ISB.

### Add TEPL class TileOp definition

This type of TileOp is uniformly opened by the "BSTART.TEPL" instruction, and then the specific TileOp is specified through the "Mode" and "Function" field codes. The encoding of the "BSTART.TEPL" instruction is as follows:

![bstart.tepl](../figs/isa/version/0.55/bstart.tepl.png)

The list of new TileOps is as follows:| Mode | Function | TileOp | Description |
|------|----------|--------|------|
| 0 | 0 | TADD | Element-wise addition of two Tiles. dst = src0 + src1 |
| 0 | 1 | TSUB | Element-wise subtraction of two Tiles. dst = src0 - src1 |
| 0 | 2 | TMUL | Element-wise multiplication of two Tiles. dst = src0 * src1 |
| 0 | 3 | TDIV | Element-wise division of two Tiles. dst = src0 / src1 |
| 0 | 4 | TREM | The element-wise remainder of two Tiles, with the remainder sign being the same as the divisor. dst = remainder(src0, src1) |
| 0 | 5 | TFMOD | The element-wise remainder of two Tiles, with the remainder sign being the same as the dividend. dst = fmod(src0, src1) |
| 0 | 6 | TAND | Element-wise bitwise AND of two Tiles. dst = src0 & src1 |
| 0 | 7 | TOR | Element-wise bitwise OR of two Tiles. dst = src0 | src1 |
| 0 | 8 | TXOR | Element-wise bitwise XOR of two Tiles. dst = src0 ^ src1 |
| 0 | 9 | TSHL | Element-wise left shift of two Tiles. dst = src0 << src1 |
| 0 | 10 | TSHR | Element-wise right shift of two Tiles. dst = src0 >> src1 |
| 0 | 11 | TMAX | The element-wise maximum value of two Tiles. dst = max(src0, src1) |
| 0 | 12 | TMIN | The element-wise minimum value of two Tiles. dst = min(src0, src1) |
| 0 | 13 | TCMP | Compares two Tiles and writes a packed predicate mask. dst = cmp.xx(src0, src1) |
| 0 | 14 | TPRELU | Element-wise parameterized ReLU with element-wise slope Tile. dst = (src0 > 0 ? src0 : src1 * src0) |
| 0 | 15 | TABS | The element-wise absolute value of the Tile. |
| 0 | 16 | TNOT | Element-wise bitwise negation of Tile. |
| 0 | 17 | TNEG | Element-wise negation of Tile. |
| 0 | 18 | TEXP | Element-wise exponential operation. |
| 0 | 19 | TLOG | The element-wise natural logarithm of Tile. |
| 0 | 20 | TRECIP | The element-wise reciprocal of Tile. |
| 0 | 21 | TSQRT | Element-wise square root. |
| 0 | 22 | TRSQRT | Element-wise reciprocal square root. |
| 0 | 23 | TRELU | The element-wise ReLU of the Tile. dst = src0 > 0 ? src0 : 0 |
| 0 | 24 | TADDC | Ternary element-wise addition: dst = src0 + src1 + src2. || 0 | 25 | TSUBC | Ternary element-wise subtraction: dst = src0 - src1 + src2. |
| 0 | 26 | TSEL | Use a masked Tile to select between two Tiles (element-wise selection). dst = (mask > 0 ? src0 : src1) |
| 0 | 27-31 | RESERVE| Reserved |
| 1 | 0 | TADDS | Element-wise addition of Tile with scalar. |
| 1 | 1 | TSUBS | Subtract a scalar element-wise from the Tile. |
| 1 | 2 | TMULS | Element-wise multiplication of Tile with scalar. |
| 1 | 3 | TDIVS | Element-wise division with scalar (Tile/scalar or scalar/Tile). |
| 1 | 4 | TREMS | Element-wise remainder of scalar. dst = remainder(src, scalar) |
| 1 | 5 | TFMODS | Element-wise remainder with scalar. dst = fmod(src, scalar) |
| 1 | 6 | TANDS | Element-wise bitwise AND of Tile with scalar. |
| 1 | 7 | TORS | Element-wise bitwise OR of Tile with scalar. |
| 1 | 8 | TXORS | Element-wise bitwise XOR of Tile and scalar. |
| 1 | 9 | TSHLS | Tile moves left element by element according to scalar. |
| 1 | 10 | TSHRS | Tile is shifted to the right element by element according to scalar. |
| 1 | 11 | TMAXS | Element-wise maximum value of Tile and scalar. |
| 1 | 12 | TMINS | Element-wise minimum of Tile and scalar. |
| 1 | 13 | TCMPS | Compare Tile to scalar element-by-element. |
| 1 | 14 | TLRELU | LeakyReLU with scalar slope. |
| 1 | 15-23 | RESERVE| Reserved code |
| 1 | 24 | TADDSC | With scalar fusion element-wise addition operation. dst = src0 + scalar + src1. |
| 1 | 25 | TSUBSC | With scalar fusion element-wise subtraction operation. dst = src0 - scalar + src1. |
| 1 | 26 | TSELS | Use mask tile to select between source tile and scalar (element-wise selection). dst = (mask > 0 ? src0 : scalar) |
| 1 | 27 | TEXPANDS| Broadcast scalar to the target Tile. |
| 1 | 28-31 | RESERVE| Reserved code |
| 2 | 0 | TROWSUM| Reduce each row by summing the columns. || 2 | 1 | TROWMAX| Reduce each row by taking the maximum value between columns. |
| 2 | 2 | TROWMIN| Reduce each row by taking the minimum value between columns. |
| 2 | 3 | TROWPROD| Reduce each row by multiplying across columns. |
| 2 | 4 | TROWEXPAND| Broadcasts the first element of each source row into the target row. |
| 2 | 5 | TROWEXPANDADD| Line broadcast addition: Add one per line scalarvector. |
| 2 | 6 | TROWEXPANDSUB| Row broadcast subtraction: subtract one per row of scalarvectorsrc1 from each row of src0. |
| 2 | 7 | TROWEXPANDMUL| Row broadcast multiplication: Multiply each row of src0 by one per row scalarvectorsrc1. |
| 2 | 8 | TROWEXPANDDIV| Row broadcast division: Divide each row of src0 by one per row scalarvectorsrc1. |
| 2 | 9 | TROWEXPANDMAX| Row broadcast maximum value: Take the maximum value with each row scalarvector. |
| 2 | 10 | TROWEXPANDMIN| Row broadcast minimum value: Take the minimum value with each row scalarvector. |
| 2 | 11 | TROWEXPANDEXPDIF| Row exponential difference operation: calculate exp(src0 - src1), where src1 is scalar per row. |
| 2 | 11-15 | RESERVE| Reserved encoding |
| 2 | 16 | TCOLSUM| Reduce each column by summing the rows. |
| 2 | 17 | TCOLMAX| Reduce each column by taking the maximum value between rows. |
| 2 | 18 | TCOLMIN| Reduce each column by taking the minimum value between rows. |
| 2 | 19 | TCOLPROD| Reduce each column by multiplying across rows. |
| 2 | 20 | TCOLEXPAND| Broadcasts the first element of each source column into the target column. |
| 2 | 21 | TCOLEXPANDADD| Column broadcast addition: Add each column scalarvector to each column. |
| 2 | 22 | TCOLEXPANDSUB| Column broadcast subtraction: subtract one per column scalarvector from each column. |
| 2 | 23 | TCOLEXPANDMUL| Column broadcast multiplication: Multiply each column by one per column scalarvector. |
| 2 | 24 | TCOLEXPANDDIV| Column broadcast division: Divide each column by one per column scalarvector. |
| 2 | 25 | TCOLEXPANDMAX| Column broadcast maximum value: Take the maximum value with each column scalarvector. |
| 2 | 26 | TCOLEXPANDMIN| Column broadcast minimum value: Take the minimum value with each column scalarvector. || 2 | 27 | TCOLEXPANDEXPDIF| Column exponential difference operation: calculate exp(src0 - src1), where src1 is scalar for each column. |
| 2 | 28-31 | RESERVE| Reserved encoding |
| 3 | 0-29 | RESERVE| Reserved code |
| 3 | 30 | ESAVE | exception save block, used to save the block state of the Tile block where exception occurs |
| 3 | 31 | ERCOV | exception recovery block, used to restore the intra-block state of the Tile block where exception occurred |