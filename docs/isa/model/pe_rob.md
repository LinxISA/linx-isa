# pe_rob

![pe_rob](../../figs/model/model_detail/pe_rob.svg "pe_rob")

## Data structure

* **wbAluInst**
Function: As the output end of the EXE Stage to temporarily store arithmetic instructions, and as the input of the WB Stage, it assumes the function of the instruction channel from the EXE Stage to the WB Stage, and serves as a carrier between the two pipeline stages.
Implementation: vector

* **wbAguInst**
Function: As the output end of the EXE Stage, it temporarily stores the load instruction, and as the input of the WB Stage, it is located in the data stream that writes the address in Ggpr to Lgpr.

* **wbStaInst**
Function: As the output end of the EXE Stage to temporarily store the store(addr) command, and as the input of the WB Stage, it assumes the function of the command channel from the EXE Stage to the WB Stage, and serves as a carrier for filming between the two pipeline stages.

* **wbStdInst**
Function: As the output end of the EXE Stage to temporarily store the store(data) command, and as the input of the WB Stage, it assumes the function of the command channel from the EXE Stage to the WB Stage, and serves as a carrier for filming between the two pipeline stages.

* **wbLoadInst**
Function: Receive load instructions from LSU and serve as input to WB Stage

* **wbBruInst**
Function: As the output end of the EXE Stage to temporarily store branch instructions, and as the input of the WB Stage, it assumes the function of the instruction channel from the EXE Stage to the WB Stage, and also serves as a carrier between the two pipeline stages.

## Execution process

1. For the load instruction, there are three possibilities for its src: Ggpr, Lgpr, and T register. When its src is Ggpr, an additional step is required: write the calculated address from Ggpr to Lgpr. After the load instruction ends the RF stage and obtains the address that needs to be accessed, the above additional operations can be performed in parallel while sending req to the LSU.

2. For the store instruction, the data in the source register needs to be written to the memory pointed to by the destination address, and the destination address is written to the destination T register. Therefore, only store(addr) needs to have a WB Stage, while store(data) does not have a WB Stage.

3. Wait until the instruction in rob becomes the oldest instruction before committing.