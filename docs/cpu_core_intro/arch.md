# LinxISA processor architecture design
<span style="background-color:#facccc;">**Note: Priority consultation for Block ISA microarchitecture issues Zhu Fan 00370308**</span>

To understand the design concept of BlockCore, you must first understand the Block ISA instruction set (see [Introduction to BlockISA] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc_master/docs/site/docs/) for details). To put it simply, this instruction set essentially divides the program into blocks and abstracts these program blocks into several block instruction, namely header (Block Header). A block instruction contains several micro-instructions (Micro-insts), similar to a program fragment. By utilizing information from header, the hardware can parallelize unrelated or partially related blocks to the greatest extent possible, thereby achieving better performance. For intra-block microinstructions, existing processors can also achieve optimal performance through reordering. In general, the advantage of LinxISA and BlockCore is that it provides a higher parallel level, that is, the block level, allowing the program to have a larger parallel window and achieve better performance. At the same time, the design of block instruction also provides a compiler-to-hardware interface. The meta information obtained through compilation or profiling can be included in header to instruct the execution of the hardware.

The BlockCore processor is a CPU architecture customized for Block ISA instructions. In order to support header and block-separated instructions, BlockCore is also divided into two stages, consisting of a block control core (Block Control Core, BCC) and several execution engines (Process Engine, PE). Among them, the execution object of BCC is header, while the execution object of PE is intra-block microinstructions. The forms of both have certain similarities with existing CPU cores.


## Block Control Core (BCC)

The block control core is the control module used to process header instruction. Its main function is to fetch and parse header instruction, and reasonably allocate the execution PE of the block based on the attributes of header, input/output, block size, dependencies with other blocks and other information. At the same time, in order to facilitate the execution of the block, BCC will also rename the block, register the block ROB and other operations. From an abstract point of view, BCC is equivalent to processing header as a microinstruction, except that the execution unit of the instruction is PE instead of computing devices such as ALU.

## Execution Engine (PE)

The execution engine is the execution module for the microinstructions within the block. Since each block is a program fragment, its microarchitecture is not much different from a normal CPU. It can be understood as the execution unit of the block at the block level, and as a small core at the microinstruction level.



The current overall architecture of BlockCore is as shown below. The block control core has an out-of-order one-issue structure, and the instructions it processes are 64-bit header (Block Header). The execution engine level has an out-of-order four-issue structure, and the instructions it processes are four 16-bit intra-block microinstructions (Micro-instructions).* **Block Control Core Frontend Pipeline (BCC Frontend)** includes block instruction branch prediction unit, instruction fetch unit, decoding, distribution unit, etc. Mainly responsible for fetching instructions header instruction and distributing blocks to appropriate execution engines through algorithms.
* **Block Control Core Backend Pipeline (BCC Backend)** includes general-purpose register renaming, reordering cache, emission pipeline, general-purpose register heap, block address cache, etc., and is responsible for the processing and efficient execution of block instruction.
* **Execution engine front-end pipeline (PE Frontend)** includes microinstruction branch prediction unit, instruction fetch unit, decoding, distribution unit, etc. Mainly responsible for fetching microinstructions within the instruction block and distributing them to appropriate execution units.
* **Execution engine backend pipeline (PE Backend)** includes the renaming of registers in the block, the reordering cache, the launch pipeline, the general-purpose register heap, and the computing unit, which is responsible for the efficient execution of microinstructions.
* **Load Store Unit)** is responsible for receiving memory access requests from the execution engine and executing them efficiently.

The specific architecture diagram is as follows:
![Overall architecture diagram](../figs/uArch/GFU_TOP_OVERVIEW.png){ width="800" }