# IEX Issue Queue

## Function

1. Emit the instructions in iq into the select array, enter the RF stage in the next shot, and write it into the exe array after completion.

![iex_iq](../../figs/model/model_detail/iex_iq.svg)

## Data structure

* **aluIQ**
Function: that is, iq of arithmetic instructions, there are 6
Implementation: vector

* **ldaIQ**
Function: that is, the iq of the load instruction, there are 4

* **staIQ**
Function: that is, the iq of the store(addr) instruction, there are 4

* **stdIQ**
Function: that is, the iq of the store(data) instruction, there are 4

* **bruIQ**
Function: that is, the iq of the branch instruction, there are 4

* **selectAluInst**
Function: As the output terminal of aluIQ, it temporarily stores the arithmetic instructions selected and transmitted in aluIQ, and at the same time, it serves as the input terminal of RF stage.
Implementation: vector

* **selectAguInst**
Function: As the output terminal of aluIQ, it temporarily stores the load command selected and transmitted in aluIQ, and at the same time, it serves as the input terminal of RF stage.

* **selectStaInst**
Function: As the output terminal of aluIQ, it temporarily stores the store(addr) instruction selected and issued in aluIQ, and at the same time, it serves as the input terminal of RF stage.

* **selectStdInst**
Function: As the output terminal of aluIQ, it temporarily stores the store(data) command selected and transmitted in aluIQ, and at the same time, it serves as the input terminal of RF stage.

* **selectBruInst**
Function: As the output terminal of aluIQ, it temporarily stores the branch instructions selected and launched in aluIQ, and at the same time, it serves as the input terminal of RF stage.

* **exeAluInst**
Function: As the output of the RF stage to temporarily store arithmetic instructions, and as the input of the EXE Stage, it assumes the function of the instruction channel from the RF stage to the EXE Stage, and serves as a carrier between the two pipeline stages.
Implementation: vector

* **exeAguInst**
Function: As the output end of the RF stage to temporarily store the load command, and as the input of the EXE Stage, it assumes the function of the command channel from the RF stage to the EXE Stage, and serves as a carrier for filming between the two pipeline sections.

* **exeStaInst**
Function: As the output end of the RF stage, it temporarily stores the store(addr) command, and as the input of the EXE Stage, it assumes the function of the command channel from the RF stage to the EXE Stage, and serves as a carrier between the two pipeline stages.

* **exeStdInst**
Function: As the output end of the RF stage, it temporarily stores the store(data) command, and as the input of the EXE Stage, it assumes the function of the command channel from the RF stage to the EXE Stage, and serves as a carrier between the two pipeline stages.

* **exeBruInst**
Function: As the output of the RF stage to temporarily store branch instructions, and as the input of the EXE Stage, it assumes the function of the instruction channel from the RF stage to the EXE Stage, and also serves as a carrier between the two pipeline stages.

## Execution process

* Call the issue function, launch the instructions in IQ, and select the instructions into the corresponding select array.
* There are **5 types of IQ**, each type of IQ contains multiple launch queues;
* There are **5 types of select** arrays, and each type of select array also contains multiple arrays;
* Each type of select array corresponds to a type of IQ. The instructions of this type of IQ can only enter the corresponding type of select array. Each IQ sends an instruction at a time, and the IQ that does not have a ready instruction will not send it.