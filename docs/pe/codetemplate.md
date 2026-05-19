# Code Template
Code Template (CT) is a microinstruction generator customized for template block and specific instructions defined in LinxISA. Currently defined, it mainly undertakes the following tasks:
- **Microinstruction Template**
	- MSGBuffer request delivery
	- MSGBuffer reply delivery

- **block instruction Template**
	- **B.MCOPY**: Copy the specified size of the target memory to the target address at byte granularity
	- **B.MSET**: Assign the target memory to the specified value (bytes)
	- **B.MPUSH**: Continuously writes the specified register list to the target memory address and updates the register pointer
	- **B.MPOP**: Continuously read data from the target memory address and write it into the destination register list, and update the register pointer
	- **F.ENTRY**: Continuously write the specified register list to the target memory address
	- **F.EXIT**: Continuously read data from the target memory address and write it into the destination register list, and use the ra register to update CARG.TGT
	- **F.RET**: Continuously read data from the target memory address and write it into the destination register list, and use the RegRet register to update CARG.TGT

- **exception Template**
	- exception context save
	- exception context recovery

- **Call Block Template**
	- Automatically save return address

## Code Template Custom Instructions

Currently, most of the instructions generated in the Code Template are microinstructions defined in LinxISA. At the same time, we also defined some instructions related to microarchitecture:


- **Clear LSMAP**: Clear all mapping relationships of this block in Local Smap so that subsequent accesses to GPR point to the Global register.
- **Set RA**: Calculate the return address of the CALL type block and store it in the Global R1 register

## Code Template implementation

Note: This chapter only describes the implementation of Code Template. The specific code generation and hardware coordination of each function are not reflected in this chapter.

Code Template will be implemented through state machines. The state machine enters the corresponding template state through specific event triggers, takes over the front-end instruction fetch unit and generates corresponding micro-instructions. After the command is generated, Code Template will return the source of the command to the front end. At this point, Code Template has completed a code generation work.

**Code Template Status**:

- **Idle**: Initial state, Code Template is idle and can receive specific event requests
- **Setup [x]**: In the ready state, Code Template has received the generation request, but it has not yet reached the correct time to generate instructions. It waits for the target event to occur and takes over the front end.
- **CodeGen[x]**: Generated state, Code Template takes over the front-end and generates a series of instructions, and jumps back to the initial state at the end

It should be noted that Setup and CodeGen are a set of states, and each subdivided scenario corresponds to a set of independent Setup & CodeGen state machines (different scenarios are marked by [x]). At the same time, the conditions for the Idle state to jump to different scenarios are also different. The jump conditions for all states are listed below:

- **template block Scenario**:
	- Idle -> Setup: Block Control Core front end (BDecode) resolves to template block
	- Setup -> CodeGen: The required registers or parameters for template block are ready, and the previous block will be parsed.
	- CodeGen -> Idle: Instruction generation completed- **exception Scenario**:
	- Idle -> Setup: The oldest instruction of the current oldest block reports exception, and the type is Debug or recoverable exception
	- Setup -> CodeGen: When the current exceptionFlush is completed
	- CodeGen -> Idle: Instruction generation completed

- **Setc.msg microinstruction scenario**:
	- Idle -> Setup: When the PE front end (Decode) parses the setc.msg microinstruction
	- Setup -> CodeGen: The required parameters are prepared and the current block is parsed to the last instruction
	- CodeGen -> Idle: Instruction generation completed

- **Call Block Scenario**:
	- Idle -> Setup: Block Control Core front end (BDecode) parses to Call block
	- Setup -> CodeGen: The previous block will be parsed
	- CodeGen -> Idle: Instruction generation completed