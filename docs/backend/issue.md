# Issue Queue (ISQ)

The launch queue is where instructions are waiting to be issued. Since the operands required for the instructions are not ready yet, the instructions will wait in this module class. Since microinstructions are divided into three categories: **Memory Access Class (LSU)**, **Computing Class (ALU)**, and **External Communication and PC Operation Class (GSU**), the launch queue is also divided into three categories and five sub-queues, **AB ISQ**, **AM ISQ**, **LS0 ISQ**, **LS1 ISQ**, **GSU ISQ**.

When the instruction is executed, the issue queue will receive the corresponding operand wake-up signal from the downstream to inform the issue queue that the operation number has been calculated. When all source operands required for an instruction in the issue queue have been awakened, the instruction can be selected and issued. In each clock cycle, each issue queue selects an instruction that can be issued and sends it to the downstream computing unit. When there are multiple instructions in the queue that can be issued, the priority selected is the older the program sequence is, the higher it is. Most selected instructions will do a speculative execution operation (precommit) to wake up the instructions in the issue queue to improve performance.

## Introduction to launch queue

Each subqueue can receive up to 2 microinstructions of the corresponding type per clock cycle.
- GS_ISQ can receive GET/SET type instructions or SGET/SSET type instructions
- AB_ISQ can receive 1 cycle instructions such as BR/SETC.XX/ALU/STA
- AM_ISQ can receive 1 cycle instructions such as ALU/STA and 2 cycle MUL instructions
- LS0_ISQ/LS1_ISQ can receive memory access instructions such as STD/LDA

## Transmit queue field segment| Field segment | Bit width | Description |
| ---------------- | ---- | ----------------------------------------------- |
| Src0_vld | 1 | Source operand 0 valid |
| Src1_vld | 1 | Source operand 1 valid |
| Src0_tag | 6 | Source operand 0 physical register number |
| Src1_tag | 6 | Source operand 1 physical register number |
| Src0_rdy | 1 | Source operand 0 wakeup |
| Src1_rdy | 1 | Source operand 1 wakeup |
| Dst_vld | 1 | destination valid |
| Dst_tag | 1 | Destination physical register number |
| Entry Valid | 1 | This entry is valid |
| Block ROBID | 7 | The block ROBID used to record this instruction |
| PE ROBID | 7 | Microinstruction ROBID used to record this instruction |
| Load Gene Vector | 2x3 | 3-bit per source operand Load Gene Vector |
| Depend source | 2x3 | Pipeline representing data dependencies, 3-bit per source operand |
| Tracking Vector | 2x3 | Indicates the pipeline level at which data should be forwarded, 3-bit per source operand |

## Architecture block diagram


In the microarchitecture, we have two computing pipelines, so there are two ALU ISQs. Each clock cycle, the hardware can select the awakened instructions from these two ALU ISQs and send them to the downstream. LSU and GSU have only one pipeline, and only one LSU class instruction and one GSU class instruction can be selected per clock cycle. But currently their launch queue is divided into two banks. If only one Bank has an instruction that can be picked, that instruction is output. If both banks have instructions that can be picked, a polling arbiter is used to ensure that one instruction is picked every clock cycle.

## Wakeup
Wake-up logic is divided into two categories: active wake-up and passive wake-up. Among them:

* Active wake-up means that before the instruction enters the emission queue, the hardware will query the OOO module that stores the operand status for the wake-up status of the operand required for the instruction. If the operand has been awakened before, the Srcx_rdy field segment of the corresponding source operand of the instruction is set to 1 when it enters the emission queue.

* Passive wake-up means that when an operand is calculated or read, or is about to be obtained, the hardware will wake up the instruction corresponding to the operand by comparing the physical register number in the launch queue, that is, setting Srcx_rdy to 1.The timing of passive awakening is also very important:
* For instruction A completed in **single clock cycle**, it can wake up other instructions B when it is issued. This is because when instruction B needs to use the data to perform operations, the instruction A it depends on has already been calculated, and instruction B can obtain the dependent data through the forwarding network.
* For instruction A completed in **multiple clock cycles**, it will not wake up other instructions B immediately when it is issued, but will wake up the source operand of instruction B after N beats. The timing is set so that the forwarded dependent data can be received just when instruction B is issued and calculated. (For the Load instruction, the hardware will assume an execution time of 4 clock cycles, that is, Cache Hit. This solution will be explained in the Load speculative launch chapter)

## Age matrix
Age Matrix is a module used to record the old and new relationships between entries in the launch queue. It has the following rules:

1. Age matrix cache, using a separate cache to record the age of data stored in the launch queue, that is, recording the order in which an instruction is stored in the cache. Age Matrix always outputs the one-hot code in the cache that is first stored in the emission queue.
2. The Age Matrix itself does not store the content of the data. It is only responsible for recording the age of the data entering the transmission queue in order to find the oldest entry.
3. The Age matrix is ​​written at the same time as the emission queue. ISQ stores the information about the instructions themselves, and Age Matrix stores the order of instructions.
4. The wake-up signal of the instruction in ISQ is used as the unmask signal of the Age Matrix, so that the Age Matrix can find the oldest entry from the unmask entry, thereby satisfying the oldest-first principle of arbitration instructions in the launch queue.


### Age Matrix principle:
1. When a new entry x is pushed into the cache, cell[a][j] is cleared to 0 and cell[i][a] is written to 1. (The rows are written with all 0s, and the columns are written with all 1s. That is shown in blue and yellow as shown in the figure, where i represents the row and j represents the column).
2. When valid cell[i][j] = 1, it means that the valid entry I and entry j in the cache are older than entry j.
3. Calculation algorithm for the oldest entry x:
   3.1 Any cell[a][j] is either invalid or 1.
   3.2 Any cell[i][a] is either invalid or 0.

For example:
Assuming an emission queue with a depth of 8, the corresponding Age Matrix is as shown in the figure:
1~7 represents table item 1 ~ table item 7, 0~6 represents table item 0 ~ table item 6;

![AGE_MATRIX0](../figs/uArch/AGE_MATRIX0.png){ width="800" }

For example:
When the order of writing to the cache is 3, 1, 5, 4, 2, 0, 7, 6, according to the principle, each time data is written to a new table entry, the rows in the corresponding table entries are written with 0 and the columns are written with 1. After eight times, the Age Matrix as shown in the figure is obtained. You can see that the rows of table entry 3 are all 1 and the columns are all 0, so table entry 3 is the oldest.

![AGE_MATRIX1](../figs/uArch/AGE_MATRIX1.png){ width="800" }

## Data forwarding (Bypass)
Generally speaking, register forwarding in the processor is done by using the equality of read PTAG and write PTAG as an enable signal before EXE pipeline to select the correct operand. In the BlockISA microarchitecture, the microarchitecture adopts another way to judge data forwarding. In the emission queue, two additional pieces of information are maintained for each source operand:

1. **Depended Source**:
Depended Source indicates which pipe the source operand comes from. It has been recorded in OOO in the REN module when the instruction is distributed, and the signal records the pipe through which the instruction is distributed. When subsequent dependent instructions enter the issue queue, the microarchitecture will not only query the wake-up status of its source operand in the rename module, but also query the production pipeline of its source operand, and record it in the issue queue. For ease of understanding, we can regard the Depended Source information as the ordinate of the target data source.2. **Tracking Vector**:
Tracking Vector represents the pipeline level at which data should be forwarded. e.g. 3'b100 = WB1, 3'b010 = WB2, 3'b001 = W3, 3'b000 = RF. The Tracking Vector will be set through two modules. If the instruction queries OOO when it enters the launch queue and finds that the source operand has been awakened, the Tracking Vector recorded in OOO will be used directly. If the instruction is not awakened when entering ISQ, when the source operand is awakened, the Tracking Vector is set to 3'b100, which means that the data will be visible in the register file after 3 clock cycles. For ease of understanding, we can regard the Depended Source information as the abscissa of the target data source.
The Tracking vector will be activated when the source operand in the issue queue is awakened. After activation, if the instruction has not been issued, the Tracking Vector of its source operand will be shifted to the right until it is shifted to 0, which means that its source operand can be read directly from RF without forwarding. If the instruction is issued from the emission queue, the two Tracking Vectors of the instruction will no longer be shifted.

Through these two parameters (X, Y coordinates), the microarchitecture can directly select the correct source operation data, thus easing the forwarding logic. At the same time, through this approach, the microarchitecture can save unnecessary RF reading power consumption, thereby saving power consumption.