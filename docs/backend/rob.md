# Linx Instruction Set Architecture ROB (Reorder buffer) introduction

In the processor architecture, ROB is a mechanism to achieve sequential submission of instructions and accurate exception, enabling the processor to achieve precise exception processing and effective hardware speculative execution. The principle can be simply summarized as sequential enqueue and sequential submission (dequeue). This function is usually implemented with a FIFO.

ROB will track the instructions that have been issued in the pipeline, record whether the instructions have been executed, whether exception and other information, and submit the executed instructions in sequence, and save the instruction results to the register file or write them into the memory. Uncommitted instructions will wait in the ROB, so the depth of the ROB is the depth of hardware speculative execution. For most programs, greater speculation depth means more opportunities to exploit parallelism, thereby obtaining better performance.

In order to solve a series of problems such as precise exception, mainstream processors have adopted the sequential submission execution paradigm. However, this paradigm requires instructions to occupy hardware resources until the instruction becomes the oldest instruction before the resources can be released sequentially. At the same time, if the execution time of the oldest instruction is too long, such as the read instruction L3 cache is missing, the instruction will always block the hardware, causing subsequent instructions to be unable to be submitted.

Different from common processor architectures, the ROB in Linx Instruction Set Architecture utilizes the unique blocking mechanism of the structured instruction set, thereby enabling the hardware to simultaneously exploit two dimensions of parallelism during program execution, namely inter-block parallelism (Block Parallelism) and intra-block parallelism (Instruction Parallelism). At the same time, it ensures the accurate status and correctness of the program when blocks are issued out of order, and when microinstructions within the blocks are issued out of order.

Corresponding to the microarchitecture level, structured ROB is divided into two levels: block ROB and microinstruction ROB. Through this layered mechanism, the hardware can decouple blocks from the sequential commit of instructions. That is, since the intra-block microinstructions will only affect the architectural state within the block when executed, and will not affect the external architectural state, the microinstruction ROB only needs to ensure the submission order within the block, while the submission order between blocks will be guaranteed by the superior block ROB. As a result, the microinstruction ROB can submit the oldest microinstructions from different blocks at the same time, thereby achieving the effect of out-of-order submission without affecting the accuracy of architectural state. At the same time, since instructions do not need to be submitted in order, the microinstruction ROB hardware resources can be released in advance, which means that the speculative depth of the ROB is greater than the actual depth, thereby releasing greater parallelism.

It should be noted that this design does not break the computing paradigm of sequential submission, but uses the layered mechanism of the structured instruction set to complete the submission marking of multiple blocks, resulting in the effect of out-of-order submission.

# PE ROB
The microinstruction ROB is a key module that ensures that microinstructions belonging to the same block are submitted sequentially. It only needs to ensure the execution order within the block, and does not need to ensure that the programs between blocks are also submitted in order. The order submission between blocks will be guaranteed by the superior block ROB. If some microinstructions in multiple blocks have been completed, the microinstructions in these blocks can be submitted in order. When all instructions in a block are submitted, the corresponding entry in the superior block ROB is marked as completed.

Based on the above rules, the most reasonable implementation is to implement the microinstruction ROB as a linked list structure, and have an additional BICT (Block Instruction Commit Tracker) module record the execution of each block.

## Microinstruction ROB table entry structure

![PEROB](../figs/uArch/PE_ROB_FIG.png)

As shown in the figure above, the microinstruction ROB is composed of M slices. Each slice is a block of a ROB and contains K instructions. Each slice can be connected at will through the head and tail pointers to form a linked list structure, which can store a total of M*K instructions. Each slice has the following domain segments:| Field segment | Description |
| ----------- | --------------------------------------------------------------- |
| Valid bit | Indicates that the piece is valid and occupied |
| Wrap bit | Indicates whether the block number wraps around, used to compare the old and new numbers |
| Head and tail pointers | Indicate the connection relationship of the piece. Only the same block will have pointer connections |
| Block number | Indicates the sequential number of the block to which the slice belongs |
| slice number | indicates the sequence number of the slice in the block it belongs to |
| Block start mark | Indicates that the slice is the first slice of the block |
| Block end mark | Indicates that the slice is the last slice of the block |
| Instruction status *K | Each slice can store the status of K instructions. The status includes complete, exception, exception type and other information |


## BICT (Block Instruction Commit Tracker) structure
Since the superior block ROB maintains N header, at most N blocks in the microinstruction ROB are executed at the same time. During execution, each block will be submitted in sequence, and the microinstruction ROB will process submissions from multiple blocks at the same time. In order to ensure the correctness when multiple blocks are submitted at the same time, the hardware also needs to maintain a tracking module BICT to track the submission progress of each block.
BICT is a stack with a depth of N. Each item in it records the execution status of the corresponding block. It has the following field segments:

| Field segment | Description |
|---------------------|---------------------------------|
| Valid bit | Indicates that the entry is valid and occupied |
| Block number | Indicates the block number corresponding to this entry |
| The oldest slice pointer of the block | Indicates the position of the oldest slice of the block in the microinstruction ROB |

 ## Microinstruction ROB operation
### Command entry
When the upstream module provides a new block, the microinstruction ROB will select a block from the currently free slice, record the currently entered multiple or one microinstruction information into the slice, and mark the fragment as the starting point of the block. In addition, each slice also maintains a write pointer. If the instruction does not fill the K instruction slots, the instruction write pointer of the slice is updated to the next instruction slot to facilitate subsequent continuous writes with the same block instruction. At the same time, the microinstruction ROB will maintain a counter. When the counter is full, it will backpressure the upstream module to prevent the microinstruction ROB from not having enough space to write new blocks.
When the instruction provided by the upstream module belongs to the same block as the instruction entered in the previous clock cycle, the instruction information can be continued to be written to the slice written in the previous clock cycle. If the number of currently entered instructions exceeds the recording capacity of the current slice, you need to apply for a new free slice to write instructions that exceed the capacity, and update the instruction write pointer of the slice at the same time. In addition, the hardware will also update the head pointer of this slice to the number of the previous slice, and update the tail pointer of the previous slice to the number of this slice.
### Command update
When the instruction execution is completed, the status of the instruction in the microinstruction ROB will be updated according to the instruction number. If the instruction is executed normally and completed, the instruction will be updated to the completion status. If the instruction encounters exception during execution, the hardware will update the exception and exception type status of the instruction.
### Command dequeue
For each instruction in the microinstruction ROB, it can be dequeued as long as it is the last instruction of its block and is marked as a normal completion status. However, since each slice can only be occupied by one block, as long as all the instructions in the slice are not completed, other blocks cannot occupy the block in advance. At the same time, for simplicity of design, the microinstruction ROB can choose to kick out a slice at the same time, that is, bind K instructions together and queue them up. At the same time, the microinstruction ROB does not need to guarantee the sequential submission of blocks, so the hardware allows multiple slices to be kicked out at the same time.
When all instructions of a block have been dequeued (that is, when a slice with an end mark is dequeued), the microinstruction ROB will notify the superior block ROB of a signal that the block has been completed.
### Command to flush out
When encountering an external exception or interrupt, the microinstruction ROB will find instructions younger than the number and flush them out based on the block number and instruction number of the flush instruction provided by the upstream. At the same time, according to the flushing situation, the valid bit of each slice, the instruction write pointer, and the valid bit of each block in BICT are updated in time.