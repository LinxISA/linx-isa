# OPE

**Note: Priority is given to Zhu Fan for microarchitecture-related issues 00370308**<span style="background-color:#facccc;"></span>

This chapter mainly describes the overall architecture of OPE. OPE stands for Out-of-Order Process Engine. As a small core that can execute LinxISA microinstructions, it has independent instruction fetching, decoding, calculation, and memory access units, so that it can independently complete the execution of standard block microinstructions, including: ALU instructions, L/S instructions, GET/SET instructions, etc. It interacts with the following external modules:

|Module|Description|
|--|--|
| **L2 Cache**| Responsible for interacting with the L1 I/DCache in OPE to fill data |
| **BCC OOO** | Provides OPE with a series of necessary block-level information, such as: rename information, Block PC, Block ROB block tracking information, etc. |
| **LSU** | Responsible for processing memory access requests from OPE |

<span style="background-color:#facccc;">[Note] Normally the LSU is part of the CPU, but in this architecture document, we describe the LSU independently</span>

## Architecture block diagram
Structure diagram

![Architecture details](../figs/uArch/OPE_BLK.PNG){ width="800" }

Architectural details

![Architecture details](../figs/uArch/OPE_TOP.PNG){ width="800" }



## Module introduction
**OPE** can be roughly divided into the following modules

### IFU
**IFU** (Instruction Fetch Unit) is responsible for receiving the header instruction sent by the upstream and parsing the microinstruction PC from header instruction. Then the microinstruction PC is used to sequentially fetch 4 instructions from the instruction cache and send them to the decoding unit.
Similar to BFU, the entire IFU is divided into two parts, namely **ISIDE** and **BSIDE**. Among them, ISIDE is mainly responsible for reading the correct microinstructions from the instruction cache through the microinstruction PC and issuing them. BSIDE is mainly responsible for predicting the address and direction of the jump through the existing microinstruction PC, so that the microinstructions in the block can be launched efficiently.
For its specific microarchitecture, please refer to: (TODO)

### DEC and DISP
**DEC** (Decode) is responsible for parsing the instructions sent by the IFU and obtaining detailed instruction data, including instruction type, physical register number, immediate data, etc., and uses these control signals to indicate the execution of subsequent microinstructions, and guides its downstream DISP module to correctly distribute microinstructions.

**DISP** (Dispatch) is responsible for receiving the instruction data sent by DEC, and receiving the virtual register and physical register mapping information sent from PE ROB. At the same time, DISP will give priority to sending instructions to the cache that occupies less space in ISQ. There is no cache inside this module, only forwarding logic.

### PE ROB

**ROB** utilizes the unique blocking mechanism of the structured instruction set, thereby enabling the hardware to simultaneously exploit two dimensions of parallelism during program execution, namely inter-block parallelism (Block Parallelism) and intra-block parallelism (Instruction Parallelism). At the same time, it ensures the out-of-order issuance of blocks and the accurate status and correctness of the program when the micro-instructions within the block are issued out-of-order.

The PE ROB exists inside OPE, and it only needs to ensure the submission order within the block, while the submission order between blocks will be guaranteed by the superior block ROB. By implementing PE ROB in the form of a linked list, it can submit the oldest microinstructions from different blocks at the same time, thereby achieving the effect of out-of-order submission without affecting the accuracy of architectural state. At the same time, since instructions do not need to be submitted in order, the microinstruction ROB hardware resources can be released in advance, which means that the speculative depth of the ROB is greater than the actual depth, thereby releasing greater parallelism.

For specific details, please refer to [Block ISA ROB solution] (https://codehub-y.huawei.com/Graphflow/blockisa-doc/docs/backend/files?ref=master&filePath=docs%2Fbackend%2Frob.md&isFile=true)### ISQ
**ISQ** (Issue Queue) serves as the issuing unit queue and stores micro-instructions issued by DISP. The queue records the launch status and information of each instruction, including whether the operand is ready to be completed, the instruction type and other information.

In the ISQ microarchitecture, there are four types of pipelines:
 
 | Pipeline | Description |
 |--|--|
 |ALU0 ISQ|ALU0 calculation pipeline, responsible for processing basic functions such as calculation, logic, and shifting
 |ALU1 ISQ| ALU1 calculation pipeline, responsible for processing basic functions such as calculation, logic, and shifting
 |LSU ISQ|LSU memory access pipeline, responsible for processing memory read and write requests
|GSU ISQ|GSU external interaction pipeline, responsible for GET/SET/SETBPC/SETC and other instructions that require the use of GPR, BPC and other external registers

### RF
**RF** (Register File) is a 64-deep and 64-wide register file, containing 8 read ports and 4 write ports. The instruction will read its required operands through the read port, and write the calculated results of the instruction into the corresponding physical register through the write port. In order to speed up the execution of instructions, the microarchitecture arbitrates the operands with the results from the WriteBack pipeline after they are read, so as to achieve the effect of forwarding.

### EXE
**EXE** (Excution Unit) contains several computing devices, covering all computing types defined in LinxISA. Corresponding to ISQ, EXE also has four calculation pipelines, and the calculations responsible for each pipeline have been summarized in the ISQ chapter. Similarly, at the beginning of the EXE, the calculation results from the WriteBack pipeline will be obtained through the forwarding network.