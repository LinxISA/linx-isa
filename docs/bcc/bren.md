# Block Rename Unit (Block Rename, BREN)

The block renaming unit is a key component within OOO. It is split into multiple copies and placed in each PE Tile. It is responsible for mapping block architectural register to block physical registers. It can be used to eliminate WAW and WAR competition risk scenarios and improve out-of-order execution efficiency. The block renaming unit will process the input/output domain segment of block instruction. For the output of the block, the block renaming unit will allocate a free physical register for each output register. For the input of a block, the block renaming unit will query its internal speculative map (SMAP) to obtain its corresponding mapping. Different from other processors, the block renaming unit in Linx Instruction Set Architecture adopts a distributed structure to decouple the mapping synchronization problem between different PEs. This chapter mainly introduces the Mask Select, Rename, Physical Register File Mapping Table, Freelist and other modules.

## Architecture block diagram
![ArchitectureBREN](../figs/uArch/BREN_TOP.png){ width="800" }


## Mask Select module (Mask Select)

Different from other instruction sets, block instruction of LinxISA has multiple input/output, expressed in two 32-bit Bit Maps. The mask selection module unit is responsible for selecting the corresponding registers from these two 32-bit vector and providing them to subsequent hardware execution. The mask selection module processes input and output independently and in parallel, and each is controlled by the back pressure of the subsequent module. Currently, it supports 4 outputs per beat to allocate free physical registers, and 4 inputs per beat to query mapped physical registers. At the same time, only inputs and outputs from the same block are selected each clock cycle.


## Speculative Map Table (SMAP)

The speculative mapping table records the physical mapping of all architectural register and the latest architectural state currently seen in this PE**, refreshes the mapping relationship between architecture and physical registers in real time, and allows new input to query its latest physical register mapping. Its format is as follows:

|architectural register number|corresponds to the latest physical register number|
|-----|-----|
|G0|P2|
|G1|P4|
|...|...|
|G31|P42|

For the output of the block, it will update the physical register allocated from the Free List into SMAP every clock cycle, and the allocated mapping relationship will also be recorded in SET PRFT. For the input of the block, the hardware will obtain the mapping relationship of the physical register by querying SMAP, and the queried mapping relationship will also be recorded in GET PRFT.



## Committed Map Table (CMAP)

The latest non-speculative architectural state is recorded in the submission mapping table to provide backup for possible rollback operations in the future. It is consistent with the data format of SMAP. When an instruction is Commit, PRFT will synchronize the mapping relationship output by the instruction to CMAP. At the same time, the physical registers replaced by updates in CMAP will be recycled to Freelist for subsequent output allocation. In the initial state, CMAP will be assigned a fixed mapping, that is, P0 corresponds to G0, P1 corresponds to G1, and so on.

## Register map table (Phyiscal Register File Table, PRFT)The register map table is divided into two tables, namely GET PRFT and SET PRFT. SET PRFT contains all architectural register-physical register mapping relationships that have been allocated but have not yet been submitted. GET PRFT contains all architectural register-physical register mapping relationships that have currently been queried but have not yet been submitted. When a block is committed, its mapping is read from SET PRFT and CMAP is updated. If a Flush occurs, the mapping relationship newer than the Flush bid will be flushed in both tables, the physical registers flushed in SET PRFT will be released to Freelist, and the saved CMAP mapping relationship will be read out and help restore SMAP.

### Register map control state machine

The commit and flush pointer maintenance of the register map table is extremely error-prone. Due to the bandwidth limitations of the release map, register map table commit and flush operations require more time than BROB. To prevent mistakes, rules need to be followed: one action ends before another can begin. For the recovery operation of PRFT, the flushing and submitting behaviors cannot coexist, that is, the flushing behavior and the recovery operation coexist in the same clock cycle. For BROB, it is in a waiting state until the register map table completes the submission and flushing operations, and then performs the flushing action. 

The register map controls the working status through the state machine. When the BROB commits, the state machine enters the "Commit" state and commits the mapping relationship starting from the commit pointer until the BlockID of its mapping instruction reaches the commit BlockID of the BROB. If a Flush scenario occurs, the state machine will enter the "Rebulid" state and restore the mapping relationship to SMAP starting from the commit pointer, and at the same time release the mapping that was flushed from the allocated pointer to Freelist.

## Physical register free list (Freelist)

All physical register codes are maintained in a Freelist. Each clock cycle, the hardware will allocate up to 6 free physical registers from the free list to the Free FIFO. At the same time, the output will also select 6 free physical registers from the Free FIFO for allocation. There are two sources of free registers. One is the physical register that is flushed out of PRFT in the Flush scenario, and the other is the physical register that is replaced after being submitted from CMAP.


![PRFT_FSM](../figs/uArch/PRFT_FSM.png){ width="800" }


## Distributed renaming module

In order to avoid possible layout and routing problems, the entire BCC Backend is distributed among multiple execution engines. There are several benefits to doing this:

1. The output of each PE will only be allocated to the block physical register also located in this PE. Avoiding the routing of physical registers from global allocations.
2. Since the speculative mapping table only records the latest physical mapping of the local PE block register, rather than the global latest, it avoids the output of each PE to update a global SMAP.
3. Each clock cycle query from the PE will only access the PRFT of the local PE, thus reducing the number of interfaces on which the PRFT is accessed.

At the same time, the distributed approach also has several disadvantages:

1. The utilization of 64 registers used by a single PE is lower than the utilization of 256 registers used by all PEs.
2. When a architectural register is allocated by two PEs successively, subsequent PEs need to query the mapping from other PEs, and synchronization cannot be avoided.

For input queries, synchronization issues cannot be avoided. The micro-architecture adopts a compromise solution, that is, for the output, the global SMAP is first synchronized, and then the input will query a global latest mapping, and then store it in the GET PRFT of the corresponding PE. In this way, for each PE, its internal GET PRFT maintains the latest mapping. There are two implementation options for this method:1. Maintain a SMAP for each PE. Each time after the block output is selected, it will be transmitted to all SMAPs at the same time, and the architectural register entry corresponding to the SMAP of the PE to which the block is destined is marked as the latest, and the corresponding entries of the SMAP of other PEs are old. When subsequent block input queries SMAP, multiple mappings of the same architectural register will also be obtained from the SMAPs of multiple PEs at the same time. Then it is aggregated through a GET MERGE module to generate a latest mapping and sent to the GET PRFT of its destination PE. In this way, the micro-architecture finds a latest mapping globally and puts it into the correct PE through aggregation and synchronization. Its architecture diagram is as follows:

![BREN_DIST](../figs/uArch/BREN_DIST.png){ width="800" }

2. Maintain a global SMAP, so the latest mappings are in one SMAP, thus saving the cost of synchronization.

![BREN_DIST2](../figs/uArch/BREN_DIST2.png){ width="800" }