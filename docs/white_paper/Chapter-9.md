# Chapter 1: Laws and concepts related to CPU
This chapter introduces the main means used to improve performance in architectural design.

- **Parallelism**: Computations without dependencies can be parallelized, exchanging space for time.
- **Frequency**: speed up the clock, increase the pipeline depth, reduce the number of pipeline logic layers at each level, and trade power consumption for time
- **Locality**: reuse instructions, reuse data, and reuse calculation results
- **Lookup Table**: Record all possible results and return directly to the table. Or record the historical results and directly look up the table and return it.
- **Customization**: Computing and data only adapt to one or several computing models, trading flexibility for time
- **Speculation execution**: Guess a result before the calculation result is transmitted, breaking data dependence

The above methods are used at all levels of the CPU architecture and microarchitecture system.

The rule of CPU performance income: income with high speculation success rate > income from table lookup > income from calculation > income with low speculation success rate

## Architecture and micro-architecture definition
Architecture is a high-level view of the system presented to users, programmers, and the system. Architecture often only shows interfaces, and related concepts are related to **API (Application Program Interface)** and **ABI (Application Binary Interace)**.

The instruction set architecture is the top-level functional interface that the CPU displays to the user. The instruction set architecture not only includes the instruction encoding format, execution model of the CPU, but also includes the format for the interaction between the CPU and other CPUs, peripherals, networks, storage, etc. on the system. The instruction set only expresses an encoding. But the instruction set architecture involves far more areas than the instruction set.

The micro-architecture is the interface defined by the implementation architecture and the specific implementation of execution model. Microarchitecture implements pipelines, logic and storage modules, interconnection networks, caches, etc.

Distinguishing between architecture and micro-architecture helps to achieve efficient layering and decoupling of software and hardware design. The complexity of microarchitecture implementation is not exposed at the architectural level as much as possible. However, the efficiency of microarchitecture can be affected through prompts and monitoring.

In terms of layered decoupling of software and hardware, CPU has always been the best. Although cores like the Linx are already executing hundreds of instructions concurrently, software engineers are still shown a programming model of sequential execution of instructions one by one. Programmers can write complex programs without understanding the hardware. The changes and evolution of CPU microarchitecture do not affect the upper-layer software. Micro-architecture improvements can automatically achieve performance improvements without changing the upper-layer software. This is also the rule we need to continue to adhere to in the CPU field.

This decoupled design allows designers at each level to optimize independently without knowing the other levels, thereby achieving overall end-to-end performance improvement. This is Iron's Law:

  ![bpu](../figs/white_paper/Chapter-1/processor_performance.png){ width="800" }


## Turing TaxTuring Tax
 
The Turing tax refers to the performance gap between a computer designed for a special purpose (Domain Specific) and a general-purpose computer.                                     

From its birth to the present, computers are basically designed based on the von Neumann architecture: Under the von Neumann architecture, only one instruction can be executed sequentially at a time.

Customized architectures in Domain Specific Architecture often obtain performance and power consumption gains on hardware by escaping the Turing tax.

Modules in the CPU that have negative benefits for PPA in order to improve versatility:

- Page table/TLB (Translation Lookaside Buffer)
- Physical Register Renaming
- Reorder Buffer
- Data Bypass/Forward Network (All-To-All Crossbar)
-Cache Tags

For DSA, if the above modules are removed, the calculation can also be completed. The performance and power consumption gains for a specific area are also objective. But the sacrifice is versatility and software flexibility.The following figure shows the main differences between CPUs compared to other programmable hardware architectures

  ![bpu](../figs/white_paper/Chapter-1/turing_tax.png){ width="800" }


Viewpoint: **Accelerator/HAC (Hardware accelerated coprocessor)** can obtain performance gains on a single business. However, in order to implement multiple services on the entire chip, after adding different types of accelerators, the overall PPAC is not as good as that of a general-purpose CPU. The cost of Turing tax will be reflected in the cost of software development and system maintenance.

## CPUarchitectural state
For the CPU, the definition of architectural stateArchitectural State is particularly important. Among them, the main functions of architectural state are:

Abstract a complete execution model for software users. This is equivalent to the software and hardware signing a contract on architectural state.
The software controls the architecture by manipulating architectural state. As long as the microarchitecture does not violate architectural state and the contract, it can be optimized privately, and executed in parallel and speculatively.
The software builds the software stack and establishes an ecosystem through the definition of architectural state
Different microarchitectures can use the same software by following the same architectural state.
The instruction set architecture imposes access restrictions on architectural state. This is reflected in the layering of EL0-EL3 on the ARM architecture. According to the definition of LinxISA, it is divided into 16 access levels AC0-AC15.

!!! info "Views"
    architectural state is essentially closely related to CPU performance. For example, any speculative execution needs to save architectural state so that it can return to a correct state in the event of an error rollback. For example, any parallel execution requires extending architectural state.

## Synchronous calls and asynchronous calls
Based on the definition of architectural state, on the parallel execution model, we extend the different processing methods of the CPU on synchronous calls and asynchronous calls:

- **Synchronous Calling**: Caller and Callee share the same architectural state. In order to speed up the performance of synchronous calls, the CPU often backs up the Caller's initial architectural state, and then transforms it into an asynchronous calling state for speculative execution. In the event of a problem or synchronization failure, it is necessary to roll back to the architectural state before the call.

- **Asynchronous call**: Caller creates a new architectural state (register and stack) for Callee. This process is called Fork. After the execution of Callee is completed, Callee's architectural state merges with Caller. This process is called Join. If nested asynchronous calls are allowed, the expansion of architectural state is unlimited. The parallel execution hardware only allows one level of asynchronous calls under the capacity limit of architectural state. This limitation creates the Master-Slave architectural design and programming model.

In the out-of-order super scalar processor, the sequential scalar instruction stream is transformed into asynchronous parallel execution of multiple code segments through jump prediction and memory access dependency prediction. The speculative state or mapping of these code segments is recorded in registers in the CPU core. These states represent states of speculation and parallel expansion. These states are reflected in the physical module of History File (x86) or MapQ+PRF (arm) in different out-of-order CPU implementations. These modules often occupy most of the area of ​​the OoO module.

## General program basic attributes
Based on the attributes of general computing programs and microarchitecture-independent, we can summarize the basic business attributes of general computing.

These attributes are generally consistent with historical research [Agerwala and Cocke 1987]:- Load instructions account for approximately 25%
- Store instructions account for approximately 15%
- ALU class scalar instructions account for 40%
- The proportion of jump instructions is 20%, of which 1/3 is a direct jump, 1/3 is a conditional Taken jump, and 1/3 is a conditional Not Taken jump.
- On average, a exception may be generated within 5-6 instructions.
 
Through the above statistical data, we draw the following conclusions:

The size of the basic block is about 5 (jumps to 20%)
The AI value (Arithmetic Intensity) of general computing is 3 (the data returned by one Load instruction can drive the operations of three instructions)
On average, five or six instructions require a architectural state record, and architectural state needs to be retained at the exception point.
When the CPU fetch width exceeds 8, it is necessary to accurately predict a jump target within the number of clock ticks. If the instruction parallelism is further improved, more than two jump targets need to be predicted continuously within one clock.
 
## Instruction parallelism wall ILP Wall
In single-threaded programs, researchers have done many studies in history on whether there is an upper limit to the degree of parallelism of instructions. These studies add different constraints on the instruction flow, thus obtaining different upper bounds on instruction parallelism.

  ![bpu](../figs/white_paper/Chapter-1/ilp_wall.png){ width="800" }


The main point of these studies is that control flow is the primary obstacle limiting instruction parallelism. If the CPU performs conditional judgment and prediction according to a linear path, the overall degree of parallelism obtained is not high, basically within 3. The actual IPC obtained by current mainstream CPUs is also within 0.5~3. If you increase CPU resources on this basis, you will not get more benefits. However, some studies [Riseman and Fostman]( https://ieeexplore.ieee.org/document/1672107) believe that parallelism also exists in control flow. After appropriately removing control flow dependencies and stack dependencies, instruction parallelism can be greatly improved. The work of [Stefanovi´c and Martonosi](https://mrmgroup.cs.princeton.edu/papers/RTAparallelism-ab.ps) further obtains the true dependency of the load store address in the memory, and can double the instruction parallelism. These ideal instruction parallelisms make it almost impossible to further liberate instruction parallelism without significantly changing existing hardware and instruction sets.

## Break through the upper limit of instruction parallelism

Recent CPU research uses Value Prediciton to break through and remove data dependencies and improve theoretical instruction parallelism. Value Prediction essentially trades off the accuracy of prediction and the cost of failed prediction. Value Prediction requires second-order prediction - whether Value Prediction has benefits to check and balance, which is essentially similar to an activation function.

!!! info "Instruction Set ILP Viewpoint"
    Instruction parallelism is actually closely related to algorithms, data structures, compilers, and instruction sets. The main method to improve instruction parallelism is speculative execution. Speculative execution is essentially an automatic parallelization operation. For example, an instruction chain becomes two instruction chains after being destroyed in the middle through speculation and prediction. The overall IPC can be doubled.

    Another method is to increase the granularity of parallelism (speculative execution) to the granularity of instruction blocks, functions, and threads. Improving the granularity of parallelism essentially turns a linear prediction path into multiple linear prediction paths and parallelizes multiple code segments. Generally speaking, the degree of instruction parallelism is improved in a higher dimension. Overall IPC = single-threaded IPC x predicted number of blocks/functions/threads that can be split. The subsequent chapters will further discuss Thread-Level Speculation.After 2004, CPU single-thread performance encountered a bottleneck. The evolution of CPUs has shifted to relying on software for explicit parallelization and distributing multi-threads/multi-processes for execution on multi-core CPUs. The main reason for this change is that the benefits obtained from the Scale Out of the CPU core are much greater than the benefits obtained from the Scale Up of the CPU core. From the perspective of the entire SOC, the overall IPC becomes single-core IPC x number of cores. However, for a single-die SOC, Cache consistency, Directory maintenance, and NOC interconnection cannot allow unlimited growth in the number of CPU cores. The next route to further improve performance is as follows: continue to invest in single-core performance improvement Scale Up, and also explore Scale Out capabilities on chiplets.