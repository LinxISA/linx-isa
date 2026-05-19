# Reorder Buffer

In Linx Instruction Set Architecture, the reorder buffer is divided into two parts: Block ROB and PE ROB. The purpose and advantages of its structure will be explained in this chapter. The details of the Block ROB and PE ROB microarchitecture will be explained in this chapter and the [PE ROB] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/backend/rob/) chapter respectively.


## Overview of out-of-order execution

Modern processor architectures usually use out-of-order execution and sequential commit computing paradigms. This paradigm refers to rearranging the execution order of the original ordered instruction list according to instruction dependencies and instruction execution cycles while ensuring consistent results, thereby achieving the purpose of improving performance. However, due to the precise interrupt (Precise Interrupt) that may arrive at any time, the hardware also needs to ensure that the hardware executes all the instructions before interrupt, and the instructions after interrupt are not executed in a precise state. Therefore, after the instructions are executed out of order, another step is added: In-order commit. The method is to cache the impact of the instructions executed out of order on the architecture in the on-chip cache. Then the hardware will sequentially change architectural state according to the order in the reordering buffer.

## Overview of reorder buffer

In the processor architecture, the reordering cache mechanism is a mechanism to achieve sequential submission of instructions and accurate exception, enabling the processor to achieve accurate exception processing and effective hardware speculative execution. The principle can be simply summarized as sequential enqueue and sequential submission (dequeue). This function is usually implemented with a FIFO.

The reordering cache will track the instructions that have been issued in the pipeline, record information such as whether the instruction has been executed, whether it is exception, etc., and sequentially submit the executed instructions, and save the instruction results to the register file or write them into the memory. Uncommitted instructions will wait in the ROB, so the depth of the ROB is the depth of hardware speculative execution. For most programs, greater speculation depth means more opportunities to exploit parallelism, thereby obtaining better performance.

## Disadvantages of existing reorder buffers

As mentioned above, in order to solve a series of problems such as accurate exception, mainstream processors have adopted the sequential submission execution paradigm. However, this paradigm requires instructions to occupy hardware resources until the instruction becomes the oldest instruction before the resources can be released sequentially. At the same time, if the execution time of the oldest instruction is too long, such as the read instruction L3 cache is missing, the instruction will always block the hardware, causing subsequent instructions to be unable to be submitted.

## Linx Instruction Set Architecture Reorder buffer overview

Different from common processor architectures, the structured reorder buffer (ROB) of the present invention utilizes the unique blocking mechanism of the structured instruction set, thereby enabling the hardware to simultaneously mine two dimensions of parallelism during program execution, namely inter-block parallelism (Block Parallelism) and intra-block parallelism (Instruction Parallelism). At the same time, it ensures the accurate status and correctness of the program when blocks are issued out of order, and when microinstructions within the blocks are issued out of order.

Corresponding to the microarchitecture level, structured ROB is divided into two levels: block ROB and microinstruction ROB. Through this layered mechanism, the hardware can decouple blocks from the sequential commit of instructions. That is, since the intra-block microinstructions will only affect the architectural state within the block when executed, and will not affect the external architectural state, the microinstruction ROB only needs to ensure the submission order within the block, while the submission order between blocks will be guaranteed by the superior block ROB. As a result, the microinstruction ROB can submit the oldest microinstructions from different blocks at the same time, thereby achieving the effect of out-of-order submission without affecting the accuracy of architectural state. At the same time, since instructions do not need to be submitted in order, the microinstruction ROB hardware resources can be released in advance, which means that the speculative depth of the ROB is greater than the actual depth, thereby releasing greater parallelism.

It should be noted that the present invention does not break the computing paradigm of sequential submission, but uses the layered mechanism of structured instruction sets to complete the submission marking of multiple blocks, resulting in the effect of out-of-order submission.

In order to ensure the correctness of the program, the hardware needs to ensure in two dimensions:

- header submitted in order
- Microinstructions within a block are committed in orderIn the microarchitecture, regular ROB is split into two levels: block ROB and microinstruction ROB. The two levels respectively ensure the sequential submission of the above-mentioned different granularities. In addition, block ROB and microinstruction ROB will provide block numbers and instruction numbers respectively. Each instruction in the program has a unique set of block numbers and instruction numbers corresponding to it, so that the hardware can track any instruction.

## Block ROB microarchitecture

Block ROB is an important module that maintains the submission order between blocks. Each item records the execution status of a block. Unlike microinstruction ROB, block ROB does not support simultaneous submission of multiple blocks. Since the submission order of microinstructions within the block is already maintained by the microinstruction ROB, the block ROB only needs to maintain the submission order of the block. Usually, the hardware implements this function through the stack, using a first-in-first-out mechanism to ensure the sequential submission of header.

### Block ROB entry structure
The implementation of the block ROB is a first-in-first-out stack with a depth of 8, and the entry and exit of the block is maintained through read and write pointers. The specific information recorded is as follows:

| Field segment | Description |
| -------- | ---------------------------------------- |
| Valid bit | Indicates that the piece is valid and occupied |
| Wrap bit | Indicates whether the block number wraps around, used to compare the old and new numbers |
| Block number | Indicates the sequence number of the block |
| Completion flag | Indicates whether all instructions in this block have completed execution |
| exception flag | Indicates whether the block encounters exception during execution |
| exception type | Indicates the exception type encountered during execution of the block |

 

### Block ROB operation
#### 1. Block entry
Whenever the upstream module delivers one or more header, the hardware will put header into the stack in order according to the write pointer instructions of the block ROB, record its block number information, and update the write pointer. At the same time, the block ROB will maintain a counter. When the counter is full, it will backpressure the upstream module to prevent the ROB from not having enough space to write new blocks.
#### 2. Block status update
If all microinstructions in the block are executed, the microinstruction ROB will report the block ROB and mark the corresponding block as completed. If exception occurs during the execution of a certain microinstruction in the block or a jump prediction error occurs, the hardware will report it to the block ROB and mark the corresponding entry as exception status. If the current oldest instruction is marked as exception, the hardware will report the exception and perform corresponding processing according to the system design.
#### 3. Block dequeue
The dequeue of block ROB must comply with the rules of block sequential submission (dequeue). The hardware will indicate the next block to be committed through a commit pointer. Every clock cycle, the hardware will query the execution status of X blocks starting from the commit pointer. The number of X is usually determined by hardware timing, implementation methods and performance indicators. If multiple consecutive blocks have been marked completed, commit them all and move the pointer to the next block to be committed.