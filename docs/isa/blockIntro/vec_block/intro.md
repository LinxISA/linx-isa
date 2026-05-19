# vector data block

## Overview

The vector data block is the core execution unit for data-level parallel computing in Linx Instruction Set Architecture. It uses **pure register-based execution model** and **hardware automatic vector technology** to provide deterministic high-performance processing capabilities for intensive computing tasks.

vector data block execution mechanism is as follows:

- Load data from Tile register to vector register
- Use multi-threads to execute vector operations in parallel
- Write the result back to the output Tile register
- Memory access is prohibited, all operations are done between registers

## execution model

vector data block adopts **Lane-Group** two-level execution level to achieve an organic combination of fine-grained parallelism and coarse-grained scheduling. The execution sequence between Groups in the vector data block can adopt parallel mode or serial mode. For details, please see the [Execution Mode] (../../arch/executemode.md) chapter. If the Group is allowed to execute in parallel mode, it needs to be defined as **vector parallel block (VPAR)**; if it must be executed in serial mode, it needs to be defined as **vector serial block (VSEQ)**.

Group level content is as follows:

| Components | Description |
|------|--------|
| Composition | Multiple vectorLane + 1 scalarLane |
| Control unit | scalarLane is responsible for branch jumps, mask management and status migration |
| P register | 64-bit mask register, controlling vectorLane execution effectiveness (1=valid, 0=invalid) |

Lane level content is as follows:

| Lane type | Register group | Function description |
|----------|---------|-------------|
| scalarLane | T/U (SGPR) | Execute control flow instructions and scalar operations |
| vectorLane | VT/VU/VM/VN (VGPR) | Execute vector calculation instructions |
| Communication mechanism | [shuffle](../../blockIntro/vecinstrs/shuffle.md) command | Realize data exchange between Lanes |

This model controls the total number of Lanes through [LB register] (../../register/common/loop.md#LB), uses RI/RO registers to manage global register context, and strictly follows the separated block execution paradigm.

![vectorblock](../../../figs/intro/vectorblock.png){ width="800" }

vector data block How to allocate body to the specified Group under different iterations, please refer to the [Group Mode] (../mem_block/dimmode.md) introduction.

## Block status BSTATE

The BSTATE of the vector data block contains the following three parts:- **[BARG](../../register/common/barg.md) register**: Control parameter register within the block, used for conditional jumps or saving and processing of execution parameters.
- **[TPC](../../register/common/tpc.md) register**: Each Group has an independent TPC, which records the instructions currently being executed by the Group.
- **LPR-Private Register Group** contains the following:
    - **[SGPR](../../register/common/sgpr.md) register**: general scalar register, used to ensure scalar data flow delivery within the block.
    - **[RI/RO](../../register/common/lgpr.md) register**: general parameter register, backup of global registers read and written in the storage block.
    - **[PRED](../../register/common/pred.md) register**: used for mask control of parallel lanes.
    - **[LB/LC](../../register/common/loop.md) register**: used for body expansion control.
    - **[VGPR](../../register/common/vgpr.md) register**: General vector register, used as a carrier for a large number of parallel vector operations within the block.
    - **[LTAR](../../register/common/ltar.md) register**: Tile formal parameter register.
    - **Output Tile**: The output Tile register has been partially updated in the block but has not been submitted to the first-level state.

In general, BARG is used to manage block-level control (mode, sequence), each Group's independent TPC is used to promote vector instruction execution, and 8 SGPRs are used to maintain efficient scalar channels; Cooperating with PRED and LB/LC to limit body iteration and expansion, with the help of a large number of vector registers VGPR, a closed execution loop of vector operation and reduction is formed.

## Core Features

The design of the vector data block follows the following core principles to enable efficient and reliable vector computational aggregation:| Level | Characteristics | Description |
|------|-------|-------|
| **Execution Control** | Hardware automatic vector | The scalar instruction stream written by the developer is automatically expanded and broadcast to all active vectorLane executions at the hardware level, greatly simplifying the programming model. |
| | Thread-level branch support | Through **scalarLane execution conditional jump**, different Groups are allowed to enter different execution paths independently according to conditions, and flexible flow control is supported. |
| | Dynamic execution mask | Through the 64-bit P register (1 valid/0 invalid), any vectorLane in the Group can be dynamically masked to achieve conditional execution and flexible data processing. |
| **Data path** | Purely register-based execution | **Access to memory space is strictly prohibited**, all data operations are completed between the Tile register, vector register (VGPR) and scalar register (SGPR), ensuring deterministic low latency. |
| | Hierarchical register architecture | scalarLane uses T/U (SGPR) registers; vectorLane uses VT/VU/VM/VN (VGPR) registers; efficient data exchange between Lanes is achieved through shuffle instructions. |
| | Restricted GGPR writing | **Only Reduce class instructions are allowed to write back to the global register (GGPR), and the output GGPR cannot be used as input to this block**, forcing the clarity of the data specification model and avoiding read and write dependency conflicts. |
| **Programming Constraints** | Separate block structure | Must **use the format** to separate header and body. Only the Fall-through jump mode is supported, which simplifies the control flow and facilitates hardware scheduling and optimization. |
| | Resource access isolation | Allows reading and writing of global registers, system register and Tile registers, but completely isolates the external memory system to form a self-contained computing unit. |

Since the vector data block adopts the structure of a separated block, it needs to comply with the definition rules of [Separated Block] (../../arch/executemachine.md#DecoupledBlock).

## Programming model and applicable scenarios

The vector data block provides developers with a programming experience of "writing scalar code and obtaining vector parallelism". Developers only need to focus on single-threaded algorithm logic, and the hardware is responsible for expanding it and efficiently executing it on multiple parallel Lanes.

Ideal application scenario:

* Computationally intensive kernel: matrix multiplication, tensor convolution, dot product and other linear algebra operations.
* Reduction and scanning operations: summation, extreme value and other results that need to be aggregated across Lanes.
* Data parallel filtering and transformation: vector conditional operation with rule branches, element-level function mapping.

Not applicable scenarios:

* Algorithms that require data exchange with global memory.
* Tasks with highly irregular control flow and huge differences across Lane branches.
* Processes with complex cross-block data dependencies that require frequent synchronization.

## block instruction constraints

**1. Access rights and prohibited items**

- The vector data block does not allow access to memory, but allows access to global registers GGPR, system registerSSR, and Tile registers and other global states.
- The load global or store global instructions are not allowed in the vector data block, otherwise the illegal instruction exception will be reported.

**2. Register read and write restrictions and Reduce related constraints**- The vector data block allows up to 8 Tile registers to be read and 4 tile registers to be written, otherwise the illegal parameter exception will be reported.
- The vector data block allows up to 12 GGPRs to be read and 4 GGPRs to be written, otherwise the illegal parameter exception will be reported.
- Only the Reduce instruction in the vector data block is allowed to write to the global register GGPR, otherwise an illegal instruction exception will be reported.
- The global register output by the Reduce instruction in the vector data block is not allowed to be used as the input of this block instruction, otherwise an illegal instruction exception will be reported.

**3.Tile register access address range constraints**
  
- The address of the **load local instruction in the vector data block cannot exceed the range** of the input/outputtile register in this block, otherwise an illegal out-of-bounds exception report will be reported.
- The **store local instruction in the vector data block cannot access the address range of the input tile register** and can only access the address of the output tile register, otherwise an illegal out-of-bounds exception report will be reported.

**4. Submission and order preserving/address coincidence rules**

- Only multiple groups are allowed to be submitted in the vector serial block in ascending order of group ids according to program order. After the last group is submitted, the vector serial block is submitted as a whole.
- The load/store local between different groups in the vector serial block allows address overlap, but needs to be modified in order according to the order of the group id. 
- The load/store local in the same group within the vector serial block is based on address preservation order, and the load/store local in different groups is in global order preservation according to address order.
- The submission within the vector parallel block needs to wait for all groups to submit. The submission of each group is defined as the submission of the last instruction in the group.
- The load/store local between different groups in the vector parallel block does not allow address overlap. If overlap occurs, the hardware does not guarantee the correctness of execution.
- The load/store local within the same group in the vector parallel block is based on address preservation order, and the addresses of different groups are not order preservation.

## Summary

The vector data block constructs a high-performance, deterministic dedicated vector computing unit through Lane-Group two-level aggregation, pure register-based execution and hardware automatic vectorization. It is particularly suitable for processing regular, intensive parallel computing tasks that do not require memory access, and is the key to achieving core computing power aggregation block instruction.