# Read request cache (Load Hit Queue, LDQ)

## Read request cache description

In this design, the microarchitecture merges LHQ and LMQ into a unified LDQ. The read request cache is built with registers to store Load instructions entering the LSU. These include:

* Load request for L1 Cache Hit
* Load request for L1 Cache Miss
*Load request of TLB Miss

## Data structure

|Field segment | Bit width | Description|
|----|----|----|
|vld | 1 | Valid bits |
|peid| 2 | Execution engine ID|
|bid | 7 |Block ID|
|rid | 7 | PE ROB ID|
|size| 3 | total size|
|pa_page1|36| PA1[47:12]|
|va_idx1|14|VA1[13:0]|
|pa_page2|36|PA2[47:12], exists when the Load instruction spans page tables|
|va_idx2|14|PA2[13:0], exists when the Load instruction is unaligned|
|tlb_hit1| 1| TLB hit1|
|tlb_hit2| 1|TLB hit2, exists when crossing a page table|
|hit1_vld|1|DCache hit1|
|hit1_way|2|DCache hit1 way|
|hit2_vld|1|DCache hit2, exists when Load instruction crosses Cacheline or page table|
|hit2_way|2|DCache hit2 way, exists when the Load instruction crosses Cacheline or page table|
|fault_vld|1|fault|
|size|2|Load data size, 0:1B, 1:2B, 2:4B, 3:8B|
|ma_type|2|Instruction non-aligned type, 0: aligned, 1: span 8B/16B, 2: span 64B, 3: span page table|
|bm1| 8| Which bytes among the 8 bytes of the instruction return data are valid|
|bm2| 8| Which bytes among the 8 bytes of data returned by the instruction are valid, exist when not aligned |
|sign|1|Whether the instruction reads a signed number|
|ldq_fsm| 4| LDQ FSM|
|total|194||
 
## LDQ operations1. Each clock cycle, LDQ will allocate a free table entry for the Load instruction input by PE to store instruction information. The Load instruction from PE will arbitrate with the instruction reselected by LDQ. Among them, LDQ reselection has a higher priority. For non-aligned Load instructions, they need to be stored in LDQ and then re-selected for execution.
2. Each clock cycle, LDQ will select the oldest TLB Miss or L1 DCache Miss entry for reselection (Repick). The Load instruction from PE and the Load instruction that did not obtain the TLB or DC TAG in LDQ will be sent to the TLB and L1 DCache arbitration together.
3. The LOAD instruction distributed by ODU needs to be written to LDQ when L0_TLB and L1 DC arbitration fails (TAG or DATA) and waits for repick to re-initiate L0_TLB and L1 DC arbitration;
4. After the M2 arbitration results, it sends a data forwarding request to STQ and SCB, and matches the address in STQ and SCB to confirm whether there is data that satisfies data forwarding;
5. If L1 DC misses, you need to request data from L2, wait for L2 to return the data, update the LDQ status, and reinitiate the L1 DC search;
6. Load UOP matches a certain STQ PA CAM, but there are multiple STQs and the current Load UOP address matches. Initiate counting and wait for the count to end before repicking the load instruction.
7. After TLB hits, L1 DC hits and LOAD data is returned, the corresponding LDQ entry state machine jumps to resolve state and sends load resolve to ROB to notify that LOAD execution is completed;
8. ODU inputs the STORE command to query LDQ. When a younger resolved load is completed before the older store, LSU determines that an ordering violation has occurred, and LDQ sends a nuke instruction to the ROB to trigger a nuke flush;
9. After receiving the commit command sent by the ROB, poll the BID and RID, and release the load resolve and older entry;
10. After receiving the FLUSH command sent by the ROB, the flush entry is younger than the flush bid/rid;

The data structure of LDQ is as follows:

Since it is a prediction table built by RAM, it has relatively high requirements on prediction bandwidth and ports, so there are certain prediction bottlenecks and area costs. The evaluation of performance requires the Linx core to be responsible.