# Version 0.43 update

Update date: November 25, 2024

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.43](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100752712747)

## General description of version update

The update of this version is mainly divided into two parts. The first is the update of the global register read and write semantics during the execution of block instruction, and the second is the addition of some privilege level related instructions.1. Modify block instruction execution semantics
    - To optimize register usage efficiency, the execution semantics of LinxISAblock instruction are improved. After the update, **block instruction output can directly overwrite the input value to avoid multiple sets of register status redundancy**.
2. Introduce separation block definition
    - Added Decoupled Block function to define header and body separately. **New B.IO instruction** was added to header instruction.
    - The detached block defines the input and output registers through the **B.IO instruction**, and the **B.TEXT instruction** specifies the body location, which is applicable to the **fall jump type**.
    - When block instruction is executed, the return address is recorded in CARG.LRA, allowing flexible orchestration and management of header and body.
3. system-call block design
    - system-call block** implements lightweight calls** from low-privilege ACR to high-privilege ACR, avoiding context saving overhead.
    - Key instructions: XB {ACR-ID}, {C-ID} are used to specify the calling target ACR and function ID, combined with the B.IO instruction to define headerinput/output.
    - The ACR layered mechanism supports permission management of different software roles to ensure safe invocation.
4. Add system call instructions
    - **System block renamed to auxiliary block (aux)**.
    - Added new microinstructions **acrc** and **acre** in the auxiliary block, retaining the general system call function.
5. Fixupexception self-processing mechanism
    - Added a new Fixup attribute to enable the block to automatically jump to the specified repair location to continue execution when exception occurs (such as memory access exception, assertion failure).
    - The Fixup mechanism optimizes exception processing and reduces system overhead.
6. header supplements HINT instruction encoding
    - Support software to proactively transmit block jump probability, block popularity, prefetch and other hint information to hardware.
7. Add GQM instructions (belonging to system block instruction set)
    - **Added GQM (General Queue Manager) command**, which provides cross-module asynchronous communication and supports remote access and message queue management.
    - Contains qmt, qpush and qpop instructions for queue maintenance, enqueuing and dequeuing operations, and supports the atomicity of many-to-many communication.
8. Added TLB maintenance instructions (belonging to system block instruction set)
    - **Added TLB (Translation Lookaside Buffer) maintenance instructions**, including tlb.iall, tlb.ia, tlb.iv and tlb.iav, to clean up TLB data of different levels and ranges.
    - This function enhances the system's management and control capabilities of virtual memory, effectively improving memory usage efficiency.
9. Added atomic comparison and exchange instructions (belonging to system block instruction set)
    - **Add casb, cash, casw, casd instructions** to optimize atomic comparison and exchange operations.
10. Added the instruction lsrget to read the status register in the block
    - Add an interface for reading the status in the block and saving the status when exception or interrupt.
11. Added system register and L1 GPR atomic swap instructions ssrswap
    - Supplementary function implementation to improve the exchange efficiency between system register and global registers to avoid occupying relative index registers within the block.
12. Delete BSTART.ECALL and BSTART.ERET instructions
    - Introduced XBsystem-call block and two methods of microinstructions acrc and acre system calls.
13. Delete trap command
    - The semantics are similar to the assert instruction, and LinxISA does not need to use the trap function to escape to an external debugger later.## Detailed introduction of changes

This part mainly introduces the changes in the architecture and the design of important instructions. The addition, deletion and modification of instructions are not explained in detail here.

### Modify block instruction execution semantics

After this version, in the same block instruction, the previous instruction updated a global register. Then the subsequent instruction reads the register value which is the updated value.

```asm
    BSTART.STD fall
    ldi [a0, 0], ->t
    ldi [a0, 8], ->t
    add t#1, t#2, ->a1
    sdi a1, [a0, 0]      # a1的值是上面add指令输出值
    ...
```
As shown in the assembly example above: the result of the instruction `add t#1, t#2, ->a1` is written to the global register a1, and the value of a1 read by the subsequent sdi instruction is the value updated by the add instruction.

### Separate blocks

For the execution process of the separated block, please refer to [block instruction jump] (../isa/arch/branch.md).