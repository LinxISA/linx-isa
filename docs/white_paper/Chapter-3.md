# Chapter 3: Parallelism and Granularity

Author: Zhou Ruoyu 532827

CPUs with different instruction set architectures process calculations at different granularities. The figure below shows that a general calculation will be split into about 9 different granularities. Programs expressed at different levels of granularity can obtain corresponding levels of parallelism.


  ![bpu](../figs/white_paper/Chapter-3/best_instr.png){ width="800" }


Theoretically, a hierarchical scheduling model can be constructed at each level of granularity. Below we list the scheduling entities at each level:

- **Process**: The scheduling entity is the operating system
- **Thread**: The scheduling entity is the operating system or hardware thread
- **Function**: Function Flow Task Scheduler/Runtime Depending on the granularity, it can be a software scheduler or a hardened scheduler
- **SCF**: Structured Control Flow is a self-created granularity in the BlockISA concept. This will be expanded later.
- **exception point**: Scheduling granularity in Reorder Buffer
- **Microinstruction**: Scheduling granularity is in Issue Queue or Reservation Station

Among these granularities, the two granularities that are easily overlooked are **SCF** and **exception points**:

## Structured Control Flow:

Refers to a Single-Entry-Single-Exit code form. SCF represents a collection of code with a series of jumps inside. But for SCF jump predictor, as long as the Entry is Taken, then its Exit must be Taken. Exit represents the convergence point of jumps. SCF essentially represents a collection of control flow graphs with a higher granularity than jumps. Yale Patt calls this form [Wish Branch](https://ieeexplore.ieee.org/document/1540947), which is called [Structured Control Flow](https://medium.com/leaningtech/solving-the-structured-control-flow-problem-once-and-for-all-5123117b1ee2) on the compiler.

SCF theory lays the foundation for the design of the WebAssembly instruction set.

## Exception Point:

The CPU will use the point where exception/Flush will be generated as the dividing line to recombine the instruction stream into a Reorder Buffer Group. From the perspective of the CPU and the entire system, the instruction granularity based on ROB Group is the optimal instruction granularity. Because if exception and Flush will not be generated inside the instruction stream, then the CPU does not need to reserve architectural state internally for a ROB Group.

## Instruction-Level Parallelism

The ARMv8 instruction set has a total of 1070 instructions, 53 formats, and 6,000 pages of instruction manual. x86 also has more than 1,300 instructions. The Loongson architecture proposes more instructions and integrates multiple instruction sets. However, most of these instructions are compound instructions designed for specific scenarios. But if these instructions are broken down into microcode, they are nothing more than simple operations, memory reading and writing, compare, and branch combined together. If we only express microcode and use a unified compression format, then the instruction set we design will be very simple.

Divide various operations into the smallest microinstructions. Since these microinstructions are thin enough, they can be reused in general operations, special operations, and various scenarios, because everyone is essentially these basic operations. If it is not broken down carefully, these operations and instructions cannot be reused. This will cause a split in the instruction set. Just like DNA/RNA can be broken down into A, T, C, G base sequences. All various proteins can be broken down into the same 20 amino acids. By breaking any instruction into these microcodes, we can reuse complex instructions at the microcode level.From a first-principles perspective, any general-purpose operation can be broken down into basic microinstructions. The CPU ultimately obtains the degree of parallelism on these microinstructions. However, the current physical implementation cannot directly break up the instruction flow and schedule a large number of these microcode instructions in a fine-grained manner at one level. However, by only splitting the calculation into the smallest pieces, the organizational structure information of the original software system is lost. The CPU still needs to perform hierarchical scheduling while maintaining the original semantics, and these disassembled microinstructions can be combined into a whole for execution.

Therefore, we hope to describe the organizational structure, scope, connection relationship, parallelism, etc. of these microinstructions through block instruction. This information is passed to the microarchitecture through block instructionISA. Organize information such as a template to build these micro-instructions into complex compound instructions, vector operations, micro-thread operations, etc. Each microarchitecture handles this organized information differently, but the information given is enough to allow these microinstructions to be optimized to the best in the microarchitecture. The hardware merges Fusion according to the template, which is actually the same effect as designing more than a thousand instructions in the ARM/x86 instruction set.

## Memory-Level Parallelism



## Block Parallelism Block Parallelism

In the BlockISA instruction set, we define a new type of instruction granularity, called block granularity. The definition of a block is a series of instruction sequences, which need to follow the semantics of **Single-Entry-Single-Exit**, which is the SCF granularity described above.


  ![bpu](../figs/white_paper/Chapter-3/block_header.png){ width="800" }


The compiler extracts the overall external input, output, and exit jumps of these instruction sequences and constructs them into a header.

The program based on this abstraction is uniformly composed of Block Header, as shown in the figure below.


  ![bpu](../figs/white_paper/Chapter-3/block_header.png){ width="800" }


Since the Block Header format is fixed, it can be efficiently scheduled and speculatively executed by dedicated hardware. We build a dual-level scheduling module through Block granularity, which can effectively reduce the implementation complexity of the CPU. Achieving a larger instruction window at low cost and obtaining higher performance gains.

Under hierarchical scheduling, the final block parallelism will still be broken down into microinstruction parallelism. Therefore, block parallelism does not essentially require the source program to increase the degree of parallelism, but requires that the source program needs to be recompiled according to a hierarchical writing method. As shown in the figure below, the hierarchical scheduling enabled by BlockISA:


  ![bpu](../figs/white_paper/Chapter-3/sch_unit.png){ width="800" }


## Function Parallelism

In Function Flow, we define a new type of function definition. Function represents a stateless or stateful task.

(To be continued)