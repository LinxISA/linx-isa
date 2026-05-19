# architectural state

## **1.architectural state layered overview**

LinxISA adopts a two-layer instruction model, and its architectural state is also divided into two layers accordingly:

| Hierarchy | Name | Visibility | Features |
|--------|------|--------|--------|
| First layer | **GSTATE (Global State)** | cross-block shared | Manage global resources and support cross-block communication and jumps |
| Second layer | **BSTATE (Block State)** | block-private | Manage block-private registers, task scheduling and data processing |

This layered design improves system flexibility and hardware scheduling efficiency.

## **2. First layer architectural state (GSTATE)**

**GSTATE** is mainly used for data transfer across block instruction, maintenance of global status, and system-level operation control. It is the basis for block instruction to achieve efficient scheduling and dynamic execution. These include:

| Register | Naming | Remarks |
|--------|------|-------|
| global general-purpose register | [GGPR](./ggpr.md) | Shared by all block instruction |
| system-state register | [SSR](../ssr/ssrintro.md) | Mainly maintained by system blocks |
| Block Level Program Counter | [BPC](./bpc.md) | Each block instruction has its own BPC |
| Tile register | [Tile](./tilereg.md) | Data shared between block type and block instruction |

The uses of this set of registers include:

- Global data sharing
- Cross-block jump control
- exception processing and context saving

## **1. Second layer architectural state (BSTATE)**

**BSTATE** is the block-private state, and different block type can have different implementations. These include:

| Register | Naming | Remarks |
|--------|------|-------|
| General scalar register | [SGPR](./sgpr.md) | Stores scalar data required for general calculations |
| In-block program counter | [TPC](./tpc.md) | Track the execution position of the body instruction |
| Block parameter register | [BARG](./barg.md) | Stores block instruction jump, block type and output register information |
| General parameter register | [LGPR](./lgpr.md) | As a backup of the global register GGPR in the separate block |
| General vector register | [VGPR](./vgpr.md) | Stores vector data required for parallel computing |
| Tile formal parameter register | [LTAR](./ltar.md) | Mapping as input/outputTile register in data block |
| Iteration control register | [LOOP](./loop.md) | Controls the number of executions of block instructionbody in parallel and serial modes |
| Mask register | [PRED](./pred.md) | Stores masks for multiple execution channels of parallel computation |

The uses of this set of registers include:

- In-block data processing
- Conditional jumps and branch prediction
- body instruction parallel execution support

## **Dynamic scheduling of two layers architectural state**

### **1. Separation of global registers and private registers**The separate design of global registers and private registers ensures the independence of global data transfer and intra-block calculations. Global registers are mainly used to transfer data across blocks to ensure smooth dependencies between blocks. Private registers only take effect within the block, reducing the complexity and hardware overhead of register renaming. This separation lays the foundation for block instruction’s dynamic scheduling, ensuring block instruction’s parallel execution and effective management of cross-block data flow.

### **2. Dynamic jump and task scheduling**

**TPC** and **BARG** in the second-layer architecture provide flexible support for intra-block jumps and conditional execution. During block execution, TPC is responsible for tracking the position of the current body instruction, while BARG is used for condition judgment and target address calculation within the block. This design allows the processor to dynamically schedule tasks within a block through hardware and make jump decisions based on the status of block execution.

### **3.Dynamic submission of block instruction**

During the execution of block instruction, the hardware will dynamically track the status of each block. When the body instruction inside block instruction is completed, the processor will determine the execution location of the next block based on the jump information in the BARG register. At the same time, the private register hardware can ensure efficient management of private data flow during block submission and avoid over-reliance on global registers.

### **4. Parallel and out-of-order execution**

The design of the two-layer architectural state is particularly suitable for out-of-order execution processor architectures. The private state of block instruction can allow multiple blocks to be executed in parallel on different block engines at the same time. The hardware scheduler manages jumps between and within blocks through BPC and TPC. At the same time, by controlling conditional jumps through the BARG register, the hardware can flexibly schedule the execution order of different blocks to maximize the parallel capabilities of the processor.

---

## Architecture restriction description

Although the two-tier architecture provides great flexibility, it also has the following limitations:

| Restrictions | Description |
|--------|--------|
| The body instruction accesses R0-R23 | body instructions within the block can access the first layer R0-R23, supporting parallel calls to system services or shared variables |
| The body instruction accesses the pre-order result | The body instruction within the block can access the pre-order result and supports micro-operation level parallelism |
| system register Access Restricted | Access to system register is only allowed through the following commands:<br>• SSRGET / SSRSET<br>• C.SSRGET / HL.SSRGET<br>• HL.SSRSET |
| Output to global register | The body instruction in the block can output the result to the global register. In an integrated block, modifications can be made before the block is submitted. In separate blocks, the private register status needs to be updated to the global register after the block is submitted |

Restrictions ensure the security of system register and prevent illegal access.

---

## **Summary: Advantages of LinxISA**

| Advantages | Description |
|------|--------|
| High flexibility | Supports the separation of block-private state and global shared state |
| Strong parallel capability | Supports out-of-order execution and multi-block parallelism |
| Efficient scheduling | Hardware can dynamically manage jumps and task allocation |
| exception Security | Automatically save BSTATE to EBSTATE when interrupt |
| Good scalability | Different block type can customize BSTATE implementation |