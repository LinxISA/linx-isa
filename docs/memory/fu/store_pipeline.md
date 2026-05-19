# Store instruction pipeline

![STORE_PIPE_HW](../../figs/uArch/store_pipe_hw.png){ width="800" }

## Workflow

The main workflow of LSU’s Store command:

1. PE issues the Store command, selects a free table entry from STQ to store address, data and other information, and searches for TLB to convert virtual address (Virtual Address, VA) and physical address (Physical Address, PA). If the TLB is missing, it sends a TLB request to the MMU.

2. After the MMU returns the TLB, it re-selects the Store instruction from STQ to search for the TLB.

3. After the TLB search is completed, the Store completion mark (Resolve) is sent to the PE ROB to notify the PE ROB that the current Store instruction execution is completed.

4. Forward the data in STQ to the matching and updated Load instruction in VA

5. After the Store instruction is completed, compare it with the completed Load instruction in LDQ. If there is a consistent PA and updated Load instruction that is completed before the current Store instruction, you need to send nuke flush to ROB.

6. When multiple entries in STQ are consistent with the physical address of Load, it is necessary to put Load into sleep state, wait for the STQ of the latest entry to retire to SCB, and then reactivate and execute the previously sleeping Load.

7. Transfer the instructions in STQ to SCB according to the current commit ID (Commit ID) given by PE ROB. When there is a Load instruction with the same physical address, the data in the SCB needs to be forwarded to the Load instruction.

8. SCB needs to search for DCache Tag before writing to L1 DCache. If the Tag is missing, it needs to send a request to L2 Cache. L2 returns the data and then searches for L1 DCache again and writes the data to L1 DCache.

The flow chart is as follows:

![STORE_PIPE](../../figs/uArch/store_pipe.png){ width="800" }