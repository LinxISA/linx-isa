# LinxISA constraint

In order to ensure the correctness and safety of program execution, LinxISA imposes a series of necessary restrictions and constraints on specific instructions and under specific environments or conditions. These constraints may involve the order of execution of instructions, selection of operands, memory access methods, etc.

## **1 block instruction constraint**| Classification | Constraints |
|-------|-------------|
| A1 | In LinxISA, all execution logic is executed in order according to the program sequence. The microarchitecture allows out-of-order execution, but when committing, the order of program state and memory access is preserved. Each microinstruction guarantees the same address order for memory access. |
| A2 | block instruction only expresses the level and scope (Scope) of architectural state. There is no limit to the number of microinstructions inside block instruction and the number of executions. Some types of block instruction cannot be programmed internally and cannot be disassembled (such as matrix Tile blocks). |
| **block type** | LinxISA is divided into integer scalar blocks, system blocks, floating point scalar blocks and a series of Tile blocks according to program attributes and functions. Different block instruction have different types of instructions and execution model has different types. |
| A3 | **Integer scalar block** (BSTART.STD): General and complete scalar integer operation instructions, no floating point instructions. Used for basic control flow and back-end calculation operations. Features are as follows: |
| A3.1 | The integer scalar block supports full jump mode (Fall, Direct, Call, Cond, Ind, Icall, Ret) |
| A3.2 | The integer scalar block allows access to global registers GGPR, system registerSSR and memory global states. Access to Tile registers is not allowed. |
| A3.3 | The integer scalar block only supports the one-piece block form |
| A3.4 | The integer scalar block does not support intra-block jumps |
| A4 | **System block** (BSTART.SYS): Provides system configuration-related operations and privilege level switching functions. The system block has a unique order-preserving execution function. The characteristics are as follows: |
| A4.1 | System blocks only support Fall jump mode |
| A4.2 | The system block allows access to global registers GGPR, system registerSSR and memory and other global states. Access to Tile registers is not allowed. |
| A4.3 | System blocks only support one block form |
| A4.4 | System blocks do not support intra-block jumps |
| A5 | **Floating point scalar block** (BSTART.FP): Has traditional floating point computing capabilities such as FP32 and FP64. The characteristics are as follows: |
| A5.1 | Floating point scalar block supports full jump mode (Fall, Direct, Call, Cond, Ind, Icall, Ret) |
| A5.2 | The floating point scalar block allows access to global state such as the global register GGPR, system registerSSR and memory. Access to Tile registers is not allowed. |
| A5.3 | Floating point scalar block only supports one block form |
| A5.4 | Floating point scalar block does not support intra-block jumps |
| A6 | **vector Serial Block** (BSTART.VSEQ): Provides vector computing capabilities. Split into multiple groups for execution, and memory access between groups must be executed in order. The characteristics are as follows: |
| A6.1 | vector serial block only supports block structure in separated block form |
| A6.2 | vector serial block only supports Fall jump mode |
| A6.3 | The vector serial block allows access to global registers GGPR, system registerSSR, and Tile registers and other global states. Access to memory is not allowed. |
| A6.4 | vector does not allow load global or store global instructions in the serial block, otherwise an illegal instruction exception will be reported. || A6.5 | The vector serial block allows up to 8 Tile registers to be read and 4 tile registers to be written. |
| A6.6 | vector serial block allows up to 12 GGPRs for reading and 4 GGPRs for writing |
| A6.7 | Only the Reduce instruction in the vector serial block allows writing to the global register GGPR |
| A6.8 | The global register output by the Reduce instruction in the vector serial block is not allowed to be used as the input of this block instruction, otherwise an illegal instruction exception will be reported |
| A6.9 | The address of the load local instruction in the vector serial block cannot exceed the range of the input/outputtile register of this block, otherwise an illegal out-of-bounds exception report will be reported. |
| A6.10 | The store local instruction in the vector serial block cannot access the address range of the tile register pointed to by TA/TB/TC, but can only access the address range of the tile register pointed to by TO/TS, otherwise an illegal out-of-bounds exception report will be reported. |
| A6.11 | Only multiple groups are allowed to be submitted in the vector serial block in ascending order of group ids according to program order. After the last group is submitted, the vector serial block is submitted as a whole. |
| A6.12 | The load/store local between different groups in the vector serial block allows address overlap, but needs to be modified in order according to the order of the group id. |
| A6.13 | vector The load/store local in the same group within the vector serial block is based on address order preservation, and the load/store local in different groups is in global order preservation according to the address order. |
| A7 | **vector parallel block** (BSTART.PAR): Provides vector computing capabilities. Split into multiple groups for execution, and memory access between groups does not require order-preserving execution. The characteristics are as follows: |
| A7.1 | vector parallel block only supports block structure in split block form |
| A7.2 | vector parallel block only supports Fall jump mode |
| A7.3 | The vector parallel block allows access to global registers GGPR, system registerSSR, and Tile registers and other global states. Access to memory is not allowed. |
| A7.4 | The load global or store global instructions are not allowed in the vector parallel block, otherwise an illegal instruction exception will be reported. |
| A7.5 | The vector parallel block allows up to 8 Tile registers to be read and 4 tile registers to be written. |
| A7.6 | The vector parallel block allows up to 12 GGPRs for reading and 4 GGPRs for writing |
| A7.7 | Only the Reduce instruction in the vector parallel block allows writing to the global register GGPR |
| A7.8 | The global register output by the Reduce instruction in the vector parallel block is not allowed to be used as the input of this parallel block instruction, otherwise an illegal instruction exception will be reported |
| A7.9 | The address of the load local instruction in the vector parallel block cannot exceed the range of the input/outputtile register of this block, otherwise an illegal out-of-bounds exception report will be reported. |
| A7.10 | The store local instruction in the vector parallel block cannot access the address range of the tile register pointed to by TA/TB/TC, but can only access the address range of the tile register pointed to by TO/TS, otherwise an illegal out-of-bounds exception report will be reported. || A7.11 | The load/store local between different groups in the vector parallel block does not allow address overlap. If overlap occurs, the hardware does not guarantee the correctness of execution. |
| A7.12 | vector The load/store local within the same group in the parallel block is based on address preservation order, and the addresses of different groups are not order preservation. |
| A7.13 | The submission within the vector parallel block needs to wait for all groups to submit. The submission of each group is defined as the submission of the last instruction in this group. |
| A8 | **Memory Access Parallel Block** (BSTART.MTC): Provides data movement capabilities between shared memory and Tile registers. Split into multiple Groups for execution, and Groups can access DDR externally. |
| A8.1 | Memory access parallel block only supports block structure in the form of separated blocks |
| A8.2 | Memory access parallel block only supports Fall jump mode |
| A8.3 | The memory access parallel block allows access to global registers GGPR, system registerSSR and memory, as well as global states such as Tile registers. |
| A8.4 | The memory access parallel block allows up to 8 Tile registers to be read and 4 tile registers to be written. |
| A8.5 | The memory access parallel block allows up to 12 GGPRs for reading and 4 GGPRs for writing |
| A8.6 | Only the Reduce instruction in the memory access parallel block is allowed to write the global register GGPR |
| A8.7 | The global register output by the Reduce instruction in the parallel block is not allowed to be used as the input of this parallel block instruction, otherwise an illegal instruction exception will be reported |
| A8.8 | The address of the load local instruction in the parallel block cannot exceed the range of the input/outputtile register of this block, otherwise an illegal out-of-bounds exception report will be reported. |
| A8.9 | The store local instruction in the parallel block cannot access the address range of the tile register pointed by TA/TB/TC, but can only access the address range of the tile register pointed by TO/TS, otherwise an illegal out-of-bounds exception report will be reported. |
| A8.10 | The load/store local between different groups in the memory access parallel block does not allow address overlap. If overlap occurs, the hardware does not guarantee the correctness of execution. |
| A8.11 | The load/store local in the same group in the parallel block is based on address preservation order, and the addresses of different groups are not order preservation. |
| A8.12 | The load/store global between different groups in the parallel block does not allow address overlap. If overlap occurs, the hardware does not guarantee the correctness of execution. |
| A8.13 | The load/store global between different groups in the memory access parallel block is not allowed to overlap with the load/store address of the scalar block. If there is overlap, the hardware does not guarantee the correctness of execution. |
| A8.14 | There are no synchronization operations such as DMB/DSB in the memory access parallel block. If synchronization requires forced cutting of blocks, synchronization is performed through the system block. |
| A8.15 | The load/store global in the same group in the parallel block is based on address preservation order, and the addresses of different groups are not order preservation. |
| A8.16 | The load/store global instructions to access parallel blocks can access non-cacheable and device IO address spaces, and the access sequence between groups is not guaranteed. |
| A8.17 | The load/store global atomic instructions to access parallel blocks allow atomic access to memory, but do not guarantee the order of atomic accesses between groups. |
| A8.18 | The commit within the memory access parallel block needs to wait for all groups to commit. The commit of each group is defined as the commit of the last instruction in this group. |
| A9 | **Matrix Tile block** (BSTART.CUBE): Provides matrix operation capabilities, splits the matrix into N fractals, and performs an operation on each fractal. The characteristics are as follows: |
| A9.1 | The matrix Tile block cannot be programmed inside and cannot be disassembled || A9.2 | Matrix Tile blocks only support Fall jump mode |
| A9.3 | The matrix Tile block allows access to the global register GGPR and the Tile register, but does not allow access to memory and system registerSSR. |
| A9.4 | Matrix Tile block allows up to 8 Tile registers to be read and 4 tile registers to be written in one block |
| A9.5 | The matrix Tile block only allows output to the ACC register |
| A9.6 | After the data in the ACC register of the matrix Tile block is moved out, the ACC register is immediately released, and subsequent instructions are not allowed to read. |
| A9.7 | The data type elements in the ACC register of the matrix Tile block can only be FP32, S32 and U32. Other data type report illegal instructions exception. |
| A9.8 | The left matrix input by the matrix Tile block must be stored in the layout of Nz (big N and small z), and the size of a fractal is fixed at 512 bytes. |
| A9.9 | The right matrix input by the matrix Tile block must be stored in a Zn (large Z small n) layout, and the size of a fractal is fixed at 512 bytes. |
| A9.10 | The size of a fractal of the accumulation matrix of a matrix Tile block is fixed to 1024 bytes. |
| **block structure** | LinxISA is divided into separate blocks (template block is a special separate block) and integrated blocks according to the structure of block instruction. |
| A10 | **Separate block constraints** (Separate blocks: header and body are stored separately) |
| A10.1 | The GGPR accessed within the separated block must be expressed through the B.IOR instruction, and the output register is not allowed to be repeated |
| A10.2 | Tile registers accessed within separate blocks must be expressed through the B.IOT instruction |
| A10.3 | The Tile register must be accessed through formal parameters in the separated block |
| A10.4 | Only the block-private registers (Local GPR and relative index registers, etc.) can be accessed within the separated block, and GGPR cannot be accessed directly |
| A10.5 | The same Local GPR (RO0-RO3) cannot be written repeatedly in the separated block, otherwise it will trigger repeated setting of exception. |
| A10.6 | 16bit and 48bit encoded instructions are not allowed in the separated block body, otherwise the illegal instruction exception will be reported. |
| A10.7 | The integer scalar block, floating point scalar block and system block do not support the separated block form |
| A11 | **template block constraints** (template block: software only defines header, body is generated by hardware) |
| A11.1 | When template block generates instructions, the number of instructions generated is determined after obtaining the input |
| A11.2 | The Index of the instruction generated by template block corresponds to the TPC. For a specified Index, a certain instruction will be generated |
| A11.3 | The range of memory access instructions generated by template block is certain, ensuring that nuke flush will not be generated within the template |
| A11.4 | There must be no overlap between the source address and destination address range of the MCOPY instruction, in units of 8 Byte |
| A12 | **One block constraint** (one block: header and body continuous storage) |
| A12.1 | vector block, memory access block and matrix operation block do not support integrated block form |
| A12.2 | The B.TEXT instruction is not allowed within a block |
| A12.3 | Supports 16/48/32/64bit encoded instructions in one block |
| A12.4 | Repeated reading and writing of the same GGPR is allowed within a single block || **Jump method** | In LinxISA, the jump methods between block instruction include the following methods. Some instructions in the blocks of some jump methods need to exist to ensure the correct execution of the program. |
| A13 | CALL: It cannot be an empty block and must contain a setret. The setret must be placed after bstart |
| A14 | COND: It cannot be an empty block and must contain a setc.cond |
| A15 | IND: It cannot be an empty block and must contain a setc.tgt |
| A16 | ICALL: It cannot be an empty block and must contain a setc.tgt and a setret. The setret must be placed after bstart |
| A17 | RET: It cannot be an empty block and must contain a setc.tgt |
| A18 | FALL: Only FALL block supports Fixup jump |

## **2 Register Constraints**| Serial number | Constraints |
|-------|-----------|
| **Register** | In LinxISA, the Tile register is a register, not memory. The attributes of the register are: |
| B1 | Atomicity: During the calculation process, block instruction's writing to Tile Register is atomic. There is no way for multiple block instruction to write a Tile Register at the same time. |
| B2 | Exclusivity: During the calculation process, block instruction has exclusive rights to its own Destination Tile Register. Subsequent block instruction cannot be read until the current block instruction is submitted. |
| B3 | Idempotence: A Tile register can only be assigned once and cannot be overwritten repeatedly. |
| B4 | Directness: The Tile register cannot obtain a pointer, nor can it be directly accessed through a pointer. |
| **Tile Reg** | The constraints of the Tile register are as follows: |
| B5 | Once a Tile register is assigned and committed by the Producer block, it becomes read-only. Subsequent block instruction cannot modify its value. Therefore, Tile Register can be copied to multiple physical entities without consistency issues. |
| B6 | A Tile register has only one Producerblock instruction, but there can be 0 to multiple Consumerblock instruction. |
| B7 | The Reuse flag of the Tile register is recorded on the input of the consumer instruction. After the consumer instruction is submitted, the input register resources can be released. |
| B8 | The capacity of a Tile register Size must be an integer multiple of the minimum fractal size of the matrix (i.e. 512 bytes). The current size of Tile Reg is between 512B and 32KB. |
| B9 | The addresses assigned by the Tile register cannot overlap. |
| B10 | The ACC register in the Tile register can only be written by the matrix Tile block, other blocks are not allowed to write |
| **GGPR** | The constraints of the global register GGPR are as follows: |
| B11 | Global registers do not need to be marked with reuse information, and they are all reused by default |
| B12 | GGPR cannot be accessed in the separated block, otherwise an illegal instruction exception will be reported |
| **T/U** | The constraints of the scalar register (t/u) include: |
| B13 | scalar registers do not need to be marked with reuse information, and they are reuse by default |
| **VT/VU/VM/VN** | The constraints of the vector register (vt/vu/vm/vn) are as follows: |
| B14 | The reuse of the vector register is recorded on the input register of the consumer instruction. After the consumer instruction is submitted, the input register resources can be released. |
| B15 | After the vector register is released, if there is a subsequent instruction to read the register, the hardware should generate exception. |
| B16 | The producer and consumer of the vector register must ensure that they use the same bit width |
| **LB/LC** | The constraints of the lb/lc register are as follows: |
| B17 | The upper limit of LB/LC register bit width is 16 bits. |
| B18 | The LB register can only be written by the B.DIM instruction, and other instructions can only read it. |
| B19 | The LC register is read-only and does not allow instructions to write. Its value is assigned by the hardware based on lane_id. |
| **PRED** | The usage constraints of P register are as follows: |
| B20 | When the P register is compared and written by the cmp instruction, it is a vector operation, and each lane is written with 1 bit. |
| B21 | When the P register is written by other instructions, it is a scalar operation. |

## **3 Microinstruction Constraints**| Serial number | Constraints |
|---------|----------|
| | **General operation instructions** |
| C1 | The destination register of the c.movi instruction cannot be the r10 register, otherwise an illegal instruction exception will be reported |
| | **Control flow instructions** |
| C2 | c.setret, the setret instruction can only write to the r10 register, otherwise an illegal instruction exception will be reported |
| C3 | c.setret, the setret instruction is only used within the CALL/ICALL block, and there is only one in a block |
| C4 | The setc.tgt instruction is only valid within the IND/ICALL/RET block, and there is only one |
| C5 | setc.cond instructions are only valid within the COND block, and there is only one in a block |
| | **Memory access operation instructions** |
| C6 | Ordinary load/store memory access instructions support address non-aligned access |
| | **SSR access command** |
| C7 | The ssrget/ssrset command can only access system register with SSR_ID[15:12] equal to 0, otherwise you need to use the hl.ssrget/hl.ssrset command |
| | **Bit operation instructions** |
| C8 | The legal value of the M parameter of the rev/l.rev instruction is {2,4,8,16,32,64}, and the legal value of the N parameter is {1,2,4,8,16,32}, and M must be greater than N, otherwise the illegal parameter exception will be reported. |
| C9 | The values of the M and N parameters of the l.bxu instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| C10 | The values of the M and N parameters of the l.bxs instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| C11 | The values of the M and N parameters of the l.bic instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| C12 | The values of the M and N parameters of the l.bis instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| C13 | The values of the M and N parameters of the l.clz instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| C14 | The values of the M and N parameters of the l.ctz instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| C15 | The values of the M and N parameters of the l.bcnt instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| C16 | The values of the M and N parameters of the l.rev instruction must be smaller than the source register bit width, otherwise the hardware execution result is unknown. |
| | **Double output command** |
| C17 | If the two destination registers of the hl.mul instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C18 | If the two destination registers of the hl.mulu instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C19 | If the two destination registers of the hl.madd instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C20 | If the two destination registers of the hl.maddw instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C21 | If the two destination registers of the hl.div instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C22 | If the two destination registers of the hl.divu instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C23 | If the two destination registers of the hl.divw instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C24 | If the two destination registers of the hl.divuw instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C25 | If the two destination registers of the hl.rem instruction are the same, the execution result is unknown (the hardware determines which result is retained). || C26 | If the two destination registers of the hl.remu instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C27 | If the two destination registers of the hl.remw instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C28 | If the two destination registers of the hl.remuw instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C29 | If the two destination registers of the hl.load pair class instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C30 | If the two destination registers of hl.load pre-index instructions are the same, the execution result is unknown (the hardware determines which result is retained). |
| C31 | If the two destination registers of hl.load post-index instructions are the same, the execution result is unknown (the hardware determines which result is retained). |
| C32 | If the two destination registers of the hl.ccat instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C33 | If the two destination registers of the hl.ccatw instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| C34 | If the two destination registers of the hl.qpop instruction are the same, the execution result is unknown (the hardware determines which result is retained). |
| | **Atomic Operation Instructions** |
| C35 | The memory access address of the atomic instruction must be aligned according to the memory access bit width, otherwise the trigger address will not be aligned exception |
| C35.1 | The memory access address of the ld.op/sd.op instructions (including the vector version) must be 8-byte aligned |
| C35.2 | The memory access address of the lw.op/sw.op instruction (including the vector version) must be 4-byte aligned |
| C35.3 | The memory access address of the swapd instruction must be 8-byte aligned |
| C35.4 | The memory access address of the swapw instruction must be 4-byte aligned |
| C35.5 | The memory access address of the swaph instruction must be 2-byte aligned |
| C35.6 | The memory access address of the hl.casd instruction must be 8-byte aligned |
| C35.7 | The memory access address of the hl.casw instruction must be 4-byte aligned |
| C35.8 | The memory access address of the hl.cash instruction must be 2-byte aligned |
| C35.9 | The memory access address of the l.casdp instruction must be 8-byte aligned |
| C35.10 | The memory access address of the l.caswp instruction must be 4-byte aligned |
| C35.11 | The memory access address of the l.cashp instruction must be 2-byte aligned |
| C36 | The load reserve and conditional store (lr/sc) instruction memory access address must be aligned according to the memory access bit width, otherwise the trigger address will not be aligned exception |
| C36.1 | The memory access address of lr.d/sc.d instructions must be 8-byte aligned |
| C36.2 | The memory access address of the lr.w/sc.w instruction must be 4-byte aligned |
| C36.3 | The memory access address of the lr.h/sc.h instruction must be 2-byte aligned |
| | **Execution control instructions** |
| C37 | The implementation of the barrier instruction isb will not process the instruction data prefetched into Icache and Bcache, that is, there is no need to re-fetch instructions from memory |
| C38 | If the acrc/acre command is called repeatedly in the same block, or if acrc and acre are used at the same time, the command behind program order will overwrite the request of the previous command |
| C39 | The bwe instruction is a bstop instruction, so it must be the last instruction within the block. There can be at most one bwe instruction in a system block. |
| C40 | The bse instruction is a bstop instruction, so it must be the last instruction within the block. There can be at most one bse instruction in a system block. |
| C41 | The bwt instruction is a bstop instruction, so it must be the last instruction within the block. There can be at most one bwt instruction within a system block. || C42 | The bwi instruction is a bstop instruction, so it must be the last instruction within the block. There can be at most one bwi instruction in a system block. |
| | **GQM Directive** |
| C43 | The memory access instruction is not allowed to access the GQM queue memory block |
| C44 | The maximum space of GQM queue is 2^10 bytes |
| | **Floating Point Instructions** |
| C45 | When the divisor of the fdiv/l.fdiv instruction is 0 and the dividend is a finite non-zero data, division by zero exception is generated |
| C46 | When the divisor and dividend of the fdiv/l.fdiv instruction are both 0 or infinity, this instruction triggers an illegal operation exception |
| C47 | When the input of the fsqrt/l.sqrt instruction is a negative number, the instruction triggers an illegal operation NVexception |
| C48 | When the source operand of the frecip/l.frecip instruction is 0, this instruction will trigger division by zero exception |