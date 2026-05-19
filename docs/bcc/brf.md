# Block register file

There are 32 general-purpose register (Block General Purpose Register, GPR) defined in Block ISA, from R0 - R31. Each register width is 64-bit. These registers are mainly responsible for transferring data between blocks. The architectural state register is defined at the block instruction level and must be accessed through the GET/SET instruction to access the architectural state.

PRF is a 4-distributed architecture, and the block register file is divided into four block register files with a depth of 64, which are allocated to each PE. The block register file within each PE supports 1 write and 4 reads. Because the architecture determines that the SET instruction of this PE will only be written to the block register file of this PE, the writing of the SET instruction will only interact with the local block register file. For each PE's GET, the instruction will access four block register files at the same time, so the reading of the GET instruction will cause complex routing on the microarchitecture.

![Architecture BRF](../figs/uArch/BRF.png){ width="800" }