# GGPR

## Description

The general-purpose register in the first layer architectural state is called GGPR (Global General Purpose Register), which is a global register set used for data transfer across block instruction. These registers are shared between block instruction and are the medium for global data access and communication.

The first layer of general-purpose register is named **R[n]**, and n takes the value 0, 1, 2, 3, 4, ..., 23. The bit width of this set of registers is uniformly 64bit.

The main uses of the general-purpose register group include:

- **Transfer data across blocks**: Each block instruction can directly read or write global registers, which are used to transfer data between different block instructions, avoiding frequent memory accesses.
- **Data storage optimization**: Long-lived data (such as global variables, function parameters) can remain valid through global registers, and the compiler will prioritize allocating these data to GGPR to reduce unnecessary memory reading and writing overhead.
- **input/output operation**: The input and output of block instruction can be passed through GGPR, supporting parallel execution of instructions and improving hardware execution efficiency.

Among them, general-purpose register adopts the standard ABI interface for naming and use, including zero register, stack pointer register, function parameter register, sub-function register and parent function saving register, etc. The specific uses of each register are as follows:| register name | alias | explanation | register name | alias | explanation |
|----------|----------|-------------|---------|-----------|----------------|
| R0 | Zero | Zero register, always 0 | R12 | S1 | Subfunction register 1 |
| R1 | SP | Stack pointer register | R13 | S2 | Subfunction register 2 |
| R2 | A0 | Function parameter 0 | R14 | S3 | Sub-function register 3 |
| R3 | A1 | Function parameter 1 | R15 | S4 | Sub-function register 4 |
| R4 | A2 | Function parameter 2 | R16 | S5 | Sub-function register 5 |
| R5 | A3 | Function parameter 3 | R17 | S6 | Sub-function register 6 |
| R6 | A4 | Function parameter 4 | R18 | S7 | Sub-function register 7 |
| R7 | A5 | Function parameter 5 | R19 | S8 | Sub-function register 8 |
| R8 | A6 | Function parameter 6 | R20 | X0 | Parent function save register 0 |
| R9 | A7 | Function parameter 7 | R21 | X1 | Parent function save register 1 |
| R10 | RA | Return address register | R22 | X2 | Parent function save register 2 |
| R11 | FP(S0) | Stack frame register/sub-function register 0 | R23 | X3 | Parent function save register 3 |

The function of these registers is similar to the register set in the traditional architecture, but in LinxISA, they are optimized for cross-block data transfer of block instruction, ensuring efficient management of data in jumps and function calls between blocks.

## Access properties

This set of registers are both readable and writable (RW).